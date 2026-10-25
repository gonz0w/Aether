// SPDX-License-Identifier: BSD-2-Clause
//! Fixed started dependency and reverse shutdown; no journal or graph engine.
use super::service_owner::{Backend, Error, Identity, Phase, Service};
pub struct Pair<'a, B: Backend> {
    provider: Service<'a, B>, dependent: Service<'a, B>, closing: bool,
}
impl<'a, B: Backend> Pair<'a, B> {
    pub fn new(provider: &'a mut Identity, dependent: &'a mut Identity,
        provider_attempts: u64, dependent_attempts: u64) -> Self {
        Self { provider: Service::new(provider, 0, provider_attempts),
            dependent: Service::new(dependent, 1, dependent_attempts), closing: false }
    }
    pub fn phases(&self) -> (Phase, Phase) { (self.provider.phase(), self.dependent.phase()) }
    pub fn start_provider(&mut self, backend: &mut B) -> Result<(), Error<B::Error>> {
        if self.closing { return Err(Error::Closed); }
        if self.dependent.phase() != Phase::Idle { return Err(Error::Busy); }
        self.provider.start(backend)
    }
    pub fn provider_running(&mut self, backend: &mut B) -> Result<bool, Error<B::Error>> {
        if self.provider.phase() == Phase::Idle { return Ok(false); }
        self.provider.running(backend, &self.provider.key())
    }
    pub fn start_dependent(&mut self, backend: &mut B) -> Result<(), Error<B::Error>> {
        if self.closing { return Err(Error::Closed); }
        if !self.provider_running(backend)? { return Err(Error::Busy); }
        self.dependent.start(backend)
    }
    pub fn restart_provider(&mut self, backend: &mut B) -> Result<(), Error<B::Error>> {
        if self.closing { return Err(Error::Closed); }
        if self.dependent.phase() != Phase::Idle { return Err(Error::Busy); }
        self.provider.request_stop(backend, &self.provider.key())?;
        self.provider.cleanup(backend, &self.provider.key())?;
        self.provider.start(backend)
    }
    pub fn shutdown(&mut self, backend: &mut B) -> Result<(), Error<B::Error>> {
        self.closing = true;
        if self.dependent.phase() != Phase::Idle {
            self.dependent.request_stop(backend, &self.dependent.key())?;
            self.dependent.cleanup(backend, &self.dependent.key())?;
        }
        if self.provider.phase() != Phase::Idle {
            self.provider.request_stop(backend, &self.provider.key())?;
            self.provider.cleanup(backend, &self.provider.key())?;
        }
        Ok(())
    }
}
