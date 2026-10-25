// SPDX-License-Identifier: BSD-2-Clause
//! Synchronous ABI 14 transport. Native authority is enforced on every call.
use core::arch::asm;

pub const SECTOR: usize = 512;
pub const MAX_TRANSFER: usize = 4096;
#[derive(Debug, PartialEq, Eq)]
pub enum Cause {
    Native(i64),
    InvalidRequest,
    UnsupportedMetadata,
    UnexpectedCompletion,
    Unavailable,
}
#[derive(Debug, PartialEq, Eq)]
pub struct Error {
    pub cause: Cause,
    /// Confirmed transferred prefix, not a durability or atomicity guarantee.
    pub completed: usize,
}
pub struct Block {
    selector: u64,
    sectors: u64,
    rights: u64,
    available: bool,
}
fn trap(op: u64, selector: u64, a: u64, b: u64, c: u64) -> i64 {
    let result;
    // Synchronous ABI: no pointer is retained. Callers keep their borrowed slices
    // live; no nomem/readonly option permits reordering across the interrupt.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") selector,
             in("rsi") a, inlateout("rdx") b => _, in("r10") c,
             lateout("rcx") _, lateout("r8") _, lateout("r9") _);
    }
    result
}
impl Block {
    /// A selector alone grants nothing: query verifies the invoking task's binding.
    pub fn open(selector: u64) -> Result<Self, Cause> {
        let mut info = [0u64; 4];
        let n = trap(0x27006, selector, info.as_mut_ptr() as u64, 32, 0);
        if n < 0 {
            return Err(Cause::Native(n));
        }
        if n != 0 {
            return Err(Cause::UnexpectedCompletion);
        }
        if info[0] != SECTOR as u64
            || info[1] == 0
            || info[1] > u64::MAX / SECTOR as u64
            || info[2] == 0
            || info[2] & !7 != 0
            || info[3] != 0
        {
            return Err(Cause::UnsupportedMetadata);
        }
        Ok(Self {
            selector,
            sectors: info[1],
            rights: info[2],
            available: true,
        })
    }
    pub fn size_bytes(&self) -> u64 {
        self.sectors * SECTOR as u64
    }
    pub fn rights(&self) -> u64 {
        self.rights
    }
    fn validate(&self, offset: u64, length: usize, right: u64) -> Result<(), Error> {
        let cause = if !self.available {
            Some(Cause::Unavailable)
        } else if self.rights & right == 0 {
            Some(Cause::Native(-13))
        } else if length == 0
            || length > MAX_TRANSFER
            || length % SECTOR != 0
            || offset % SECTOR as u64 != 0
            || offset > self.size_bytes()
            || length as u64 > self.size_bytes() - offset
        {
            Some(Cause::InvalidRequest)
        } else {
            None
        };
        match cause {
            Some(cause) => Err(Error {
                cause,
                completed: 0,
            }),
            None => Ok(()),
        }
    }
    fn completion(&mut self, result: i64, expected: i64, completed: usize) -> Result<(), Error> {
        if result == expected {
            return Ok(());
        }
        let cause = if result < 0 {
            Cause::Native(result)
        } else {
            self.available = false;
            Cause::UnexpectedCompletion
        };
        Err(Error { cause, completed })
    }
    pub fn read(&mut self, offset: u64, bytes: &mut [u8]) -> Result<(), Error> {
        self.validate(offset, bytes.len(), 1)?;
        for (i, sector) in bytes.chunks_exact_mut(SECTOR).enumerate() {
            let n = trap(
                0x27000,
                self.selector,
                offset / SECTOR as u64 + i as u64,
                sector.as_mut_ptr() as u64,
                SECTOR as u64,
            );
            self.completion(n, SECTOR as i64, i * SECTOR)?;
        }
        Ok(())
    }
    pub fn write(&mut self, offset: u64, bytes: &[u8]) -> Result<(), Error> {
        self.validate(offset, bytes.len(), 2)?;
        for (i, sector) in bytes.chunks_exact(SECTOR).enumerate() {
            let n = trap(
                0x27001,
                self.selector,
                offset / SECTOR as u64 + i as u64,
                sector.as_ptr() as u64,
                SECTOR as u64,
            );
            self.completion(n, SECTOR as i64, i * SECTOR)?;
        }
        Ok(())
    }
    pub fn flush(&mut self) -> Result<(), Error> {
        if !self.available {
            return Err(Error {
                cause: Cause::Unavailable,
                completed: 0,
            });
        }
        let n = trap(0x27002, self.selector, 0, 0, 0);
        self.completion(n, 0, 0)
    }
    /// Explicit consuming close, with no destructor I/O or automatic retry.
    pub fn close(mut self) -> Result<(), Error> {
        if !self.available {
            return Err(Error {
                cause: Cause::Unavailable,
                completed: 0,
            });
        }
        let n = trap(0x27004, self.selector, 0, 0, 0);
        self.available = false;
        self.completion(n, 0, 0)
    }
}
