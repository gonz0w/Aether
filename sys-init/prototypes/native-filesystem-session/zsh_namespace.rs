// SPDX-License-Identifier: BSD-2-Clause
//! Private synchronous loan of the existing budget and physical-close journal.
//! Raw pointers are armed only inside Runtime's exclusive filesystem call. The
//! borrowed disjoint fields outlive the call, never move during it, and are not
//! accessed through another path until disarm. Client/Framed retain no buffer.
//! Every constructor/call result disarms; close disarms itself even on failure.
//! Unarmed I/O fails before a native call. This is no persistent Runtime pointer.
use super::{AppControl, Bound, End};
use core::ptr;
use filesystem_readonly::Error;
use filesystem_service::{
    Channel, Message,
    channel::{Framed, Io},
};

pub(super) struct Namespace<K: AppControl> {
    kernel: K,
    reader: u64,
    writer: u64,
    bound: *mut Bound,
    ends: *mut [End; 8],
    requests: *mut u32,
    prepaid: *mut [u64; 2],
    body_frames: usize,
    cleanup: Option<[i64; 2]>,
}
impl<K: AppControl> Namespace<K> {
    pub(super) fn new(kernel: K, reader: u64, writer: u64) -> Self {
        Self {
            kernel,
            reader,
            writer,
            bound: ptr::null_mut(),
            ends: ptr::null_mut(),
            requests: ptr::null_mut(),
            prepaid: ptr::null_mut(),
            body_frames: 0,
            cleanup: None,
        }
    }
    /// # Safety
    /// The caller exclusively loans these four disjoint Runtime fields until
    /// disarm or close. No callback reentry, move, unwind, or pointer escape is
    /// allowed. Constructor failure drops the channel while the loans are live.
    pub(super) unsafe fn arm(
        &mut self,
        bound: &mut Bound,
        ends: &mut [End; 8],
        requests: &mut u32,
        prepaid: &mut [u64; 2],
    ) -> Result<(), Error> {
        if self.cleanup.is_some() || !self.bound.is_null() {
            return Err(Error::Closed);
        }
        self.bound = bound;
        self.ends = ends;
        self.requests = requests;
        self.prepaid = prepaid;
        Ok(())
    }
    pub(super) fn disarm(&mut self) {
        self.bound = ptr::null_mut();
        self.ends = ptr::null_mut();
        self.requests = ptr::null_mut();
        self.prepaid = ptr::null_mut();
    }
    fn before(&mut self) -> Result<(), i64> {
        if self.bound.is_null() || self.cleanup.is_some() {
            return Err(-9);
        }
        // SAFETY: arm's exclusive scoped loan remains live; only this method
        // accesses Bound during this synchronous namespace operation.
        unsafe { (&mut *self.bound).before(&mut self.kernel) }
    }
    pub(super) fn verify_disconnect(&mut self, engine: u64) -> Result<(), Error> {
        loop {
            self.before().map_err(Error::Transport)?;
            // SAFETY: before() validated the live, exclusive arm loan. No
            // Runtime access or disarm occurs before this synchronous query.
            #[cfg(native_zsh_operator)]
            let sequence = unsafe { (&*self.bound).sequence };
            let state = self.kernel.ctl(0x20001, engine, 0);
            if state.0 > 0 {
                if state.0 != 1 || state.2 != 1 {
                    return Err(Error::Protocol);
                }
                break;
            }
            if state.0 < 0 {
                return Err(Error::Transport(state.0));
            }
            if self.bound.is_null() {
                return Err(Error::Closed);
            }
            // SAFETY: original exclusive loan; no enclosing Runtime path is
            // used during verification. Park keeps the same deadline/sequence.
            unsafe {
                let bound = &mut *self.bound;
                bound.before(&mut self.kernel).map_err(Error::Transport)?;
                #[cfg(not(native_zsh_operator))]
                let sequence = bound.sequence;
                let parked = self.kernel.park_events(sequence, Some(bound.deadline));
                #[cfg(native_zsh_operator)]
                bound.wake(parked, sequence).map_err(Error::Transport)?;
                if parked.0 != 0 {
                    return Err(Error::Transport(if parked.0 < 0 { parked.0 } else { -5 }));
                }
            }
        }
        self.before().map_err(Error::Transport)?;
        let mut byte = [0];
        let read = self.kernel.transfer(self.reader, &mut byte, false);
        self.before().map_err(Error::Transport)?;
        let write = self.kernel.transfer(self.writer, &mut byte, true);
        if read != 0 || write != -32 {
            return Err(Error::Protocol);
        }
        self.before().map_err(Error::Transport)?;
        Ok(())
    }
    fn frame(&mut self, frame: &mut Message, writing: bool) -> Result<(), i64> {
        // Framed borrows this Io only for this call; no workspace is retained.
        if writing {
            Framed(self).send(frame)
        } else {
            Framed(self).receive(frame)
        }
    }
}
impl<K: AppControl> Io for &mut Namespace<K> {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        if let Err(error) = self.before() {
            return error;
        }
        self.kernel.transfer(
            if writing { self.writer } else { self.reader },
            bytes,
            writing,
        )
    }
    fn wait(&mut self, _writing: bool) -> i64 {
        if let Err(error) = self.before() {
            return error;
        }
        self.kernel.ctl(0x1fffe, 0, 0).0
    }
    fn close(&mut self) -> [i64; 2] {
        Channel::close(*self)
    }
}
impl<K: AppControl> Channel for Namespace<K> {
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        if self.bound.is_null() || self.cleanup.is_some() {
            return Err(-9);
        }
        if self.body_frames != 0 {
            self.body_frames -= 1;
        } else {
            let word = |i: usize| u64::from_le_bytes(frame[i * 8..i * 8 + 8].try_into().unwrap());
            let opcode = word(1);
            if frame[..8] != *b"AFSRPC09" || !(1..=11).contains(&opcode) {
                return Err(-22);
            }
            // SAFETY: same scoped exclusive loan as before(); body assembly is
            // local and serialized. Count complete-operation attempts, not frames.
            let count = unsafe { &mut *self.requests };
            if *count >= 96 || (*count >= 95 && opcode != 4) {
                return Err(-28);
            }
            *count += 1;
            let body = match opcode {
                1 | 5 => word(5),
                7..=11 => {
                    let n = word(5);
                    (n & 0xffffffff) + (n >> 32)
                }
                _ => 0,
            };
            if body > 4096 {
                return Err(-22);
            }
            self.body_frames = (body as usize).div_ceil(64);
        }
        let mut copy = *frame;
        self.frame(&mut copy, true)
    }
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        self.frame(frame, false)
    }
    fn close(&mut self) -> [i64; 2] {
        if let Some(cleanup) = self.cleanup {
            return cleanup;
        }
        if self.bound.is_null() {
            return [-9; 2];
        }
        // SAFETY: exclusive scoped journal/credit loans; each close is marked
        // before its leaf call. Credits were debited from the ordinary allowance
        // before app admission, preserving the existing containment reserve.
        let results = unsafe {
            let ends = &mut *self.ends;
            let prepaid = &mut *self.prepaid;
            [self.reader, self.writer].map(|cap| {
                let Some(end) = ends.iter_mut().find(|end| end.cap == cap && end.owned) else {
                    return -9;
                };
                if end.attempted {
                    return end.status;
                }
                let Some(credit) = prepaid.iter_mut().find(|value| **value == cap) else {
                    return -5;
                };
                *credit = 0;
                end.attempted = true;
                end.status = self.kernel.close(cap);
                end.status
            })
        };
        self.cleanup = Some(results);
        self.disarm();
        results
    }
}
