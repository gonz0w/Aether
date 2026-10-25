// SPDX-License-Identifier: BSD-2-Clause
//! Current ownership of one ABI9 paired connection; no transport protocol policy.
#![allow(dead_code)]
use super::service_owner::{Error, Fault, Identity, Phase};
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Role { Runner, Backend, Command }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Terminal { pub detail: u64, pub kind: u64 }
#[derive(Clone, Copy)]
pub struct Key<'a> { owner: &'a Identity, generation: u64 }
/// Known errors have no effects; Unknown errors close the owner against replay.
/// Successful channel creation returns both endpoints; launch transfers exactly
/// the request reader and reply writer. Terminal observations are side-effect free.
pub trait Backend {
    type Reader: Copy;
    type Writer: Copy;
    type Worker: Copy;
    type Error: Copy;
    fn channel(&mut self) -> Result<(Self::Reader, Self::Writer), Fault<Self::Error>>;
    fn launch(&mut self, role: Role, request: Self::Reader, reply: Self::Writer) -> Result<Self::Worker, Fault<Self::Error>>;
    fn observe(&mut self, worker: Self::Worker) -> Result<Option<Terminal>, Fault<Self::Error>>;
    fn stop(&mut self, worker: Self::Worker) -> Result<(), Fault<Self::Error>>;
    fn close_reader(&mut self, reader: Self::Reader) -> Result<(), Fault<Self::Error>>;
    fn close_writer(&mut self, writer: Self::Writer) -> Result<(), Fault<Self::Error>>;
    fn reclaim(&mut self, worker: Self::Worker) -> Result<(), Fault<Self::Error>>;
}
pub struct Connection<'a, B: Backend> {
    owner: &'a Identity, role: Role, generation: u64, remaining: u64, phase: Phase,
    readers: [Option<B::Reader>; 2], writers: [Option<B::Writer>; 2],
    worker: Option<B::Worker>, terminal: Option<Terminal>, stop_sent: bool,
    first: Option<Fault<B::Error>>, latest: Option<Fault<B::Error>>,
}
impl<'a, B: Backend> Connection<'a, B> {
    pub fn new(owner: &'a mut Identity, role: Role, attempts: u64) -> Self {
        Self { owner, role, generation: 0, remaining: attempts, phase: Phase::Idle,
            readers: [None; 2], writers: [None; 2], worker: None, terminal: None, stop_sent: false,
            first: None, latest: None }
    }
    pub fn key(&self) -> Key<'a> { Key { owner: self.owner, generation: self.generation } }
    pub fn phase(&self) -> Phase { self.phase }
    pub fn resources(&self) -> ([bool; 2], [bool; 2], bool) {
        (self.readers.map(|x| x.is_some()), self.writers.map(|x| x.is_some()), self.worker.is_some())
    }
    pub fn errors(&self) -> (Option<Fault<B::Error>>, Option<Fault<B::Error>>) { (self.first, self.latest) }
    fn validate(&self, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        if !core::ptr::eq(self.owner, key.owner) || key.generation != self.generation || self.generation == 0 { return Err(Error::Invalid); }
        if self.phase == Phase::Unknown { return Err(Error::Closed); }
        Ok(())
    }
    fn failed(&mut self, fault: Fault<B::Error>) -> Error<B::Error> {
        if self.first.is_none() { self.first = Some(fault); }
        self.latest = Some(fault);
        if matches!(fault, Fault::Unknown(_)) { self.phase = Phase::Unknown; }
        Error::Backend(fault)
    }
    pub fn start(&mut self, backend: &mut B) -> Result<(), Error<B::Error>> {
        if self.phase == Phase::Unknown { return Err(Error::Closed); }
        if self.phase != Phase::Idle { return Err(Error::Busy); }
        if self.remaining == 0 || self.generation == u64::MAX { return Err(Error::Exhausted); }
        self.remaining -= 1; self.generation += 1; self.first = None; self.latest = None; self.terminal = None; self.stop_sent = false;
        self.phase = Phase::Cleanup;
        for i in 0..2 {
            let (reader, writer) = backend.channel().map_err(|e| self.failed(e))?;
            self.readers[i] = Some(reader); self.writers[i] = Some(writer);
        }
        let worker = backend.launch(self.role, self.readers[0].unwrap(), self.writers[1].unwrap()).map_err(|e| self.failed(e))?;
        self.worker = Some(worker); self.readers[0] = None; self.writers[1] = None;
        self.phase = Phase::Live;
        Ok(())
    }
    /// Borrowed handles for protocol I/O only; this owner retains close/reclaim responsibility.
    pub fn handles(&self, key: &Key<'_>) -> Result<(B::Reader, B::Writer, B::Worker), Error<B::Error>> {
        self.validate(key)?;
        if self.phase != Phase::Live || self.terminal.is_some() { return Err(Error::Busy); }
        Ok((self.readers[1].ok_or(Error::Invalid)?, self.writers[0].ok_or(Error::Invalid)?, self.worker.ok_or(Error::Invalid)?))
    }
    pub fn observe(&mut self, backend: &mut B, key: &Key<'_>) -> Result<Option<Terminal>, Error<B::Error>> {
        self.validate(key)?;
        if self.terminal.is_none() {
            let worker = self.worker.ok_or(Error::Invalid)?;
            self.terminal = backend.observe(worker).map_err(|e| self.failed(e))?;
        }
        Ok(self.terminal)
    }
    /// Caller must first retire clients/references and complete backend readback.
    /// This explicit operation sends EOF; observation itself never closes a handle.
    pub fn backend_eof(&mut self, backend: &mut B, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        self.validate(key)?;
        if self.role != Role::Backend || self.worker.is_none() || !matches!(self.phase, Phase::Live | Phase::Stopping) { return Err(Error::Invalid); }
        self.phase = Phase::Stopping;
        self.close_writer(backend, 0)
    }
    pub fn request_stop(&mut self, backend: &mut B, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        self.validate(key)?;
        if !matches!(self.phase, Phase::Live | Phase::Stopping) { return Err(Error::Invalid); }
        if self.stop_sent { return Ok(()); }
        if self.observe(backend, key)?.is_none() {
            backend.stop(self.worker.ok_or(Error::Invalid)?).map_err(|e| self.failed(e))?;
            self.stop_sent = true;
        }
        self.phase = Phase::Stopping;
        Ok(())
    }
    fn close_writer(&mut self, backend: &mut B, i: usize) -> Result<(), Error<B::Error>> {
        if let Some(writer) = self.writers[i] {
            backend.close_writer(writer).map_err(|e| self.failed(e))?; self.writers[i] = None;
        }
        Ok(())
    }
    /// Caller authorizes cleanup only after protocol-owned references are settled.
    pub fn cleanup(&mut self, backend: &mut B, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        self.validate(key)?;
        if self.phase == Phase::Idle { return Err(Error::Invalid); }
        if self.worker.is_some() && self.observe(backend, key)?.is_none() { return Err(Error::Busy); }
        self.phase = Phase::Cleanup;
        for i in 0..2 {
            self.close_writer(backend, i)?;
            if let Some(reader) = self.readers[i] {
                backend.close_reader(reader).map_err(|e| self.failed(e))?; self.readers[i] = None;
            }
        }
        if let Some(worker) = self.worker {
            backend.reclaim(worker).map_err(|e| self.failed(e))?; self.worker = None;
        }
        self.phase = Phase::Idle;
        Ok(())
    }
}
