// SPDX-License-Identifier: BSD-2-Clause
//! One current service attempt; no event journal or native authority in this core.
#![allow(dead_code)]
#[derive(Debug)]
pub struct Identity { _private: u8 }
impl Identity { pub fn new() -> Self { Self { _private: 0 } } }
#[derive(Clone, Copy, Debug)]
pub struct Key<'a> { owner: &'a Identity, generation: u64 }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Fault<E> { Known(E), Unknown(E) }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error<E> { Invalid, Busy, Exhausted, Closed, Backend(Fault<E>) }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Phase { Idle, Live, Cleanup, Unknown, Stopping }
/// Known failure guarantees that this operation did not consume/transfer resources.
/// Unknown may have executed and must never be automatically replayed.
pub trait Backend {
    type Reader: Copy;
    type Writer: Copy;
    type Worker: Copy;
    type Error: Copy;
    fn channel(&mut self) -> Result<(Self::Reader, Self::Writer), Fault<Self::Error>>;
    fn launch(&mut self, slot: u8, writer: Self::Writer) -> Result<Self::Worker, Fault<Self::Error>>;
    fn stop(&mut self, worker: Self::Worker) -> Result<(), Fault<Self::Error>>;
    fn terminal(&mut self, worker: Self::Worker) -> Result<bool, Fault<Self::Error>>;
    fn close_reader(&mut self, reader: Self::Reader) -> Result<(), Fault<Self::Error>>;
    fn close_writer(&mut self, writer: Self::Writer) -> Result<(), Fault<Self::Error>>;
    fn reclaim(&mut self, worker: Self::Worker) -> Result<(), Fault<Self::Error>>;
}
pub struct Service<'a, B: Backend> {
    owner: &'a Identity, generation: u64, remaining: u64, phase: Phase, slot: u8,
    reader: Option<B::Reader>, writer: Option<B::Writer>, worker: Option<B::Worker>,
    first: Option<Fault<B::Error>>, latest: Option<Fault<B::Error>>,
}
impl<'a, B: Backend> Service<'a, B> {
    pub fn new(owner: &'a mut Identity, slot: u8, attempts: u64) -> Self {
        Self { owner, slot, generation: 0, remaining: attempts, phase: Phase::Idle,
            reader: None, writer: None, worker: None, first: None, latest: None }
    }
    pub fn key(&self) -> Key<'a> { Key { owner: self.owner, generation: self.generation } }
    pub fn phase(&self) -> Phase { self.phase }
    pub fn generation(&self) -> u64 { self.generation }
    pub fn resources(&self) -> (bool, bool, bool) {
        (self.reader.is_some(), self.writer.is_some(), self.worker.is_some())
    }
    pub fn errors(&self) -> (Option<Fault<B::Error>>, Option<Fault<B::Error>>) {
        (self.first, self.latest)
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
        self.generation += 1; self.remaining -= 1; self.first = None; self.latest = None;
        let (reader, writer) = backend.channel().map_err(|e| self.failed(e))?;
        self.reader = Some(reader); self.writer = Some(writer); self.phase = Phase::Cleanup;
        let worker = backend.launch(self.slot, writer).map_err(|e| self.failed(e))?;
        self.worker = Some(worker); self.writer = None; self.phase = Phase::Live;
        Ok(())
    }
    fn validate(&self, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        if !core::ptr::eq(self.owner, key.owner) || key.generation != self.generation || self.generation == 0 {
            return Err(Error::Invalid);
        }
        if self.phase == Phase::Unknown { return Err(Error::Closed); }
        Ok(())
    }
    pub fn running(&mut self, backend: &mut B, key: &Key<'_>) -> Result<bool, Error<B::Error>> {
        self.validate(key)?;
        if self.phase != Phase::Live { return Ok(false); }
        let worker = self.worker.ok_or(Error::Invalid)?;
        if backend.terminal(worker).map_err(|e| self.failed(e))? {
            self.phase = Phase::Cleanup;
            return Ok(false);
        }
        Ok(true)
    }
    pub fn request_stop(&mut self, backend: &mut B, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        self.validate(key)?;
        match self.phase {
            Phase::Idle => return Err(Error::Invalid),
            Phase::Stopping | Phase::Cleanup => return Ok(()),
            _ => (),
        }
        if !self.running(backend, key)? { return Ok(()); }
        backend.stop(self.worker.ok_or(Error::Invalid)?).map_err(|e| self.failed(e))?;
        self.phase = Phase::Stopping;
        Ok(())
    }
    pub fn cleanup(&mut self, backend: &mut B, key: &Key<'_>) -> Result<(), Error<B::Error>> {
        if !core::ptr::eq(self.owner, key.owner) || key.generation != self.generation || self.generation == 0 {
            return Err(Error::Invalid);
        }
        if self.phase == Phase::Unknown { return Err(Error::Closed); }
        if self.phase == Phase::Idle { return Err(Error::Invalid); }
        if let Some(worker) = self.worker {
            if !backend.terminal(worker).map_err(|e| self.failed(e))? { return Err(Error::Busy); }
        }
        self.phase = Phase::Cleanup;
        if let Some(writer) = self.writer {
            backend.close_writer(writer).map_err(|e| self.failed(e))?; self.writer = None;
        }
        if let Some(reader) = self.reader {
            backend.close_reader(reader).map_err(|e| self.failed(e))?; self.reader = None;
        }
        if let Some(worker) = self.worker {
            backend.reclaim(worker).map_err(|e| self.failed(e))?; self.worker = None;
        }
        self.phase = Phase::Idle;
        Ok(())
    }
}
