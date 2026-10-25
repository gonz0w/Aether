// SPDX-License-Identifier: BSD-2-Clause
//! Bounded short-transfer assembly; native holder checks remain in the kernel.
use crate::{Channel, Message, FRAME};

pub const POLLS: usize = 100_000;

pub trait Io {
    /// Transfer at most16 bytes, returning a count or negative native error.
    /// The slice is borrowed only for this synchronous call.
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64;
    #[cfg(not(fs_wait))]
    fn yield_now(&mut self);
    /// Scalar readiness hint on the same endpoint; no borrowed buffer retained.
    #[cfg(fs_wait)]
    fn wait(&mut self, writing: bool) -> i64;
    fn close(&mut self) -> [i64; 2];
}

pub struct Framed<I: Io>(pub I);

impl<I: Io> Framed<I> {
    fn frame(&mut self, bytes: &mut Message, writing: bool) -> Result<(), i64> {
        let mut offset = 0;
        for _ in 0..POLLS {
            let length = (FRAME - offset).min(16);
            let count = self
                .0
                .transfer(writing, &mut bytes[offset..offset + length]);
            if count == -11 {
                #[cfg(not(fs_wait))]
                self.0.yield_now();
                #[cfg(fs_wait)]
                {
                    let status = self.0.wait(writing);
                    if status != 0 {
                        bytes.fill(0);
                        return Err(if status < 0 { status } else { -5 });
                    }
                }
            } else if count <= 0 || count as u64 > length as u64 {
                bytes.fill(0);
                return Err(if count < 0 { count } else { -5 });
            } else {
                offset += count as usize;
                if offset == FRAME {
                    return Ok(());
                }
            }
        }
        bytes.fill(0);
        Err(-110)
    }
}

impl<I: Io> Channel for Framed<I> {
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        frame.fill(0);
        self.frame(frame, false)
    }

    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        // Never give a transfer implementation mutable access to caller state.
        let mut copy = *frame;
        self.frame(&mut copy, true)
    }

    fn close(&mut self) -> [i64; 2] {
        self.0.close()
    }
}
