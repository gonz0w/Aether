// SPDX-License-Identifier: BSD-2-Clause
#[cfg(not(test))]
use super::{check, copies::transfer_once};
#[cfg(test)]
use tests::{check, transfer_once};

// The authenticated caller retains this state until both exec requests and
// their replies complete. Each poll borrows its frame for just one native trap.
pub(super) struct ExecRequest {
    frame: [u8; 32],
    used: usize,
    phase: u8, // denied request/reply, allowed request/reply, complete
}

impl ExecRequest {
    pub(super) fn new() -> Self {
        Self {
            frame: [0; 32],
            used: 0,
            phase: if cfg!(pipeline_dash_parent) { 2 } else { 0 },
        }
    }

    #[cfg(pipeline_exec_overlap)]
    pub(super) fn partial_denial(&self) -> bool {
        self.phase == 1 && self.used == 7
    }

    #[cfg(pipeline_exec_io)]
    pub(super) fn awaiting(&self) -> bool {
        (self.phase == 0 || self.phase == 2) && self.used == 0
    }

    #[cfg(pipeline_exec_io)]
    pub(super) fn accept(&mut self, generation: u32, slot: usize, frame: [u8; 32]) {
        check(self.awaiting(), 2746);
        self.frame = frame;
        self.finish(generation, slot, false);
    }

    #[inline(never)]
    pub(super) fn poll(&mut self, generation: u32, slot: usize, reader: u64, writer: u64) -> bool {
        if self.phase == 4 {
            return true;
        }
        let write = self.phase & 1 != 0;
        self.used += transfer_once(
            if write { writer } else { reader },
            self.frame[self.used..].as_mut_ptr() as u64,
            32 - self.used,
            write,
        );
        if self.used != 32 {
            return false;
        }
        self.finish(generation, slot, write)
    }

    fn finish(&mut self, generation: u32, slot: usize, write: bool) -> bool {
        if !write {
            check(
                self.frame[..4] == 84u32.to_le_bytes()
                    && self.frame[4..8]
                        == (if self.phase == 0 { 0xffffu32 } else { 0xc002 }).to_le_bytes()
                    && self.frame[8..12] == (slot as u32).to_le_bytes()
                    && self.frame[12..16] == generation.to_le_bytes()
                    && self.frame[16..]
                        == if cfg!(pipeline_shell_early) {
                            if slot == 2 {
                                [2, 0, 0, 0, b'p', b'u', b'm', b'p', 4, 0, 0, 0, 1, 0, 0, 0]
                            } else {
                                [2, 0, 0, 0, b'o', b'n', b'e', 0, 4, 0, 0, 0, 1, 0, 0, 0]
                            }
                        } else if cfg!(pipeline_dash_parent) {
                            [2, 0, 0, 0, b'c', b'o', b'p', b'y', 4, 0, 0, 0, 1, 0, 0, 0]
                        } else if cfg!(pipeline_helper_args) {
                            [2, 0, 0, 0, b'c', b'o', b'p', b'y', 0, 0, 0, 0, 0, 0, 0, 0]
                        } else {
                            [0; 16]
                        },
                2746,
            );
        }
        self.frame = [0; 32];
        if self.phase == 0 {
            self.frame[..4].copy_from_slice(
                &(if cfg!(pipeline_exec_errno) {
                    -22i32
                } else {
                    -13i32
                })
                .to_le_bytes(),
            );
        }
        self.used = 0;
        self.phase += 1;
        self.phase == 4
    }
}

#[cfg(test)]
mod tests {
    use super::ExecRequest;
    use std::{cell::RefCell, collections::VecDeque};

    struct Transport {
        frames: VecDeque<(bool, [u8; 32])>,
        offset: usize,
        calls: usize,
        fragment: usize,
        bytes: usize,
    }
    std::thread_local! { static TRANSPORT: RefCell<Option<Transport>> = const { RefCell::new(None) }; }

    pub fn check(ok: bool, reason: u64) {
        assert!(ok, "rejection {reason}");
    }
    pub fn transfer_once(channel: u64, pointer: u64, remaining: usize, write: bool) -> usize {
        TRANSPORT.with(|cell| {
            let mut borrowed = cell.borrow_mut();
            let t = borrowed.as_mut().unwrap();
            t.calls += 1;
            assert_eq!(channel, if write { 12 } else { 11 });
            if t.calls % 3 == 0 {
                return 0;
            }
            let (expected_write, frame) = t.frames.front().unwrap();
            assert_eq!(write, *expected_write);
            assert_eq!(remaining, 32 - t.offset);
            let count = remaining.min(t.fragment).min(if write { 7 } else { 16 });
            // The polling caller lends its live 32-byte frame for this synchronous
            // mock. Offset and remaining checks above bound the accessed prefix.
            unsafe {
                let buffer = std::slice::from_raw_parts_mut(pointer as *mut u8, count);
                if write {
                    assert_eq!(buffer, &frame[t.offset..t.offset + count]);
                } else {
                    buffer.copy_from_slice(&frame[t.offset..t.offset + count]);
                }
            }
            t.offset += count;
            t.bytes += count;
            if t.offset == 32 {
                t.frames.pop_front();
                t.offset = 0;
            }
            count
        })
    }

    fn setup(fragment: usize, corrupt: Option<(usize, usize)>) {
        let mut frames = VecDeque::new();
        let images: &[u32] = if cfg!(pipeline_dash_parent) {
            &[0xc002]
        } else {
            &[0xffff, 0xc002]
        };
        for (index, &image) in images.iter().enumerate() {
            let mut request = [0; 32];
            for (chunk, value) in request.chunks_exact_mut(4).zip([84, image, 3, 2]) {
                chunk.copy_from_slice(&value.to_le_bytes());
            }
            if cfg!(pipeline_dash_parent) {
                request[16..]
                    .copy_from_slice(&[2, 0, 0, 0, b'c', b'o', b'p', b'y', 4, 0, 0, 0, 1, 0, 0, 0]);
            }
            if cfg!(pipeline_shell_early) {
                request[20..24].copy_from_slice(b"one\0");
            }
            if let Some((which, byte)) = corrupt {
                if which == index {
                    request[byte] ^= 1;
                }
            }
            frames.push_back((false, request));
            let mut reply = [0; 32];
            if image == 0xffff {
                reply[..4].copy_from_slice(&(-13i32).to_le_bytes());
            }
            frames.push_back((true, reply));
        }
        TRANSPORT.with(|cell| {
            *cell.borrow_mut() = Some(Transport {
                frames,
                offset: 0,
                calls: 0,
                fragment,
                bytes: 0,
            })
        });
    }
    fn observed() -> (usize, usize) {
        TRANSPORT.with(|cell| {
            let t = cell.borrow();
            let t = t.as_ref().unwrap();
            (t.calls, t.bytes)
        })
    }

    #[test]
    fn fragmented_handshake_returns_after_one_operation_and_completes_once() {
        for fragment in 1..=16 {
            setup(fragment, None);
            let mut request = ExecRequest::new();
            let mut done = false;
            for _ in 0..300 {
                let before = observed();
                done = request.poll(2, 3, 11, 12);
                let after = observed();
                assert_eq!(after.0, before.0 + 1);
                assert_eq!(
                    done,
                    after.1 == if cfg!(pipeline_dash_parent) { 64 } else { 128 }
                );
                if done {
                    break;
                }
            }
            assert!(done);
            let before = observed();
            assert!(request.poll(2, 3, 11, 12));
            assert_eq!(observed(), before);
        }
    }

    #[test]
    fn malformed_requests_never_advance_to_their_reply() {
        for which in 0..if cfg!(pipeline_dash_parent) { 1 } else { 2 } {
            for byte in [0, 4, 8, 12, 16, 20, 24, 28, 31] {
                setup(3, Some((which, byte)));
                let result = std::panic::catch_unwind(|| {
                    let mut request = ExecRequest::new();
                    for _ in 0..300 {
                        assert!(!request.poll(2, 3, 11, 12));
                    }
                });
                let panic = result.expect_err("malformed request accepted");
                let message = panic
                    .downcast_ref::<String>()
                    .map(String::as_str)
                    .or_else(|| panic.downcast_ref::<&str>().copied())
                    .unwrap();
                assert_eq!(message, "rejection 2746");
                assert_eq!(observed().1, if which == 0 { 32 } else { 96 });
            }
        }
    }
}
