// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Owned counterpart endpoints for the pinned AF07 Client/Framed, not authority.
use filesystem_service::channel::Io;

pub trait Kernel {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64;
    fn wait(&mut self, endpoint: u64) -> i64;
    fn close(&mut self, endpoint: u64) -> i64;
}

pub struct Endpoints<K: Kernel> {
    kernel: K,
    reader: u64,
    writer: u64,
    cleanup: Option<[i64; 2]>,
}
impl<K: Kernel> Endpoints<K> {
    /// Caller supplies actual owned live endpoints, never frame-derived labels.
    /// On shape rejection the caller retains both endpoints and the returned K.
    pub fn new(kernel: K, reader: u64, writer: u64) -> Result<Self, K> {
        if reader == 0 || writer == 0 || reader == writer {
            return Err(kernel);
        }
        Ok(Self {
            kernel,
            reader,
            writer,
            cleanup: None,
        })
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.cleanup
    }
}
impl<K: Kernel> Io for Endpoints<K> {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        if self.cleanup.is_some() {
            return -9;
        }
        if bytes.is_empty() || bytes.len() > 16 {
            return -22;
        }
        let endpoint = if writing { self.writer } else { self.reader };
        self.kernel.transfer(endpoint, bytes, writing)
    }
    fn wait(&mut self, writing: bool) -> i64 {
        if self.cleanup.is_some() {
            return -9;
        }
        self.kernel
            .wait(if writing { self.writer } else { self.reader })
    }
    fn close(&mut self) -> [i64; 2] {
        if let Some(results) = self.cleanup {
            return results;
        }
        // Never short-circuit the second obligation or infer success from ack.
        let results = [
            self.kernel.close(self.reader),
            self.kernel.close(self.writer),
        ];
        self.cleanup = Some(results);
        results
    }
}
impl<K: Kernel> Drop for Endpoints<K> {
    fn drop(&mut self) {
        let _ = self.close();
    }
}

#[cfg(target_os = "none")]
#[path = "af07_native.rs"]
pub mod native;

#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "af07_transport_tests.rs"]
mod tests;
