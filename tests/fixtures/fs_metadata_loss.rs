// SPDX-License-Identifier: BSD-2-Clause
//! Actual fixed loss methods; explicit fragmented transport, never native proof.
use std::{cell::RefCell, collections::VecDeque};
struct Connection {
    request: u64,
    send: u64,
    receive: u64,
}
#[derive(Default)]
struct State {
    input: VecDeque<[u8; 64]>,
    output: Vec<[u8; 64]>,
    prefix: [u8; 16],
    offset: usize,
    closed: usize,
    waits: usize,
    stalled: bool,
    fault: u8,
}
std::thread_local! {static STATE:RefCell<State>=RefCell::new(State::default());}
fn check(ok: bool) {
    assert!(ok, "AF07_METADATA_LOSS_CHECK");
}
fn get(b: &[u8; 64], i: usize) -> u64 {
    u64::from_le_bytes(b[i * 8..i * 8 + 8].try_into().unwrap())
}
fn put(b: &mut [u8; 64], i: usize, v: u64) {
    b[i * 8..i * 8 + 8].copy_from_slice(&v.to_le_bytes());
}
fn call(op: u64, endpoint: u64, _: u64, _: u64, _: u64) -> (i64, u64) {
    assert_eq!((op, endpoint), (0x24003, 22));
    STATE.with(|s| s.borrow_mut().closed += 1);
    (0, 0)
}
mod channel {
    use super::*;
    pub fn frame(endpoint: u64, bytes: &mut [u8; 64], writing: bool) -> Result<(), i64> {
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            assert_eq!(s.closed, 0);
            if writing {
                assert_eq!(endpoint, 11);
                s.output.push(*bytes);
                Ok(())
            } else {
                assert_eq!(endpoint, 22);
                *bytes = s.input.pop_front().ok_or(-5)?;
                Ok(())
            }
        })
    }
    pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64, _: u64) -> (i64, u64) {
        assert_eq!(endpoint, 22);
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            assert_eq!(s.closed, 0);
            if op == 0x24004 {
                assert!(s.stalled);
                s.stalled = false;
                s.waits += 1;
                return (if s.fault == 4 { -4 } else { 0 }, 0);
            }
            assert_eq!(op, 0x24001);
            assert_eq!(length as usize, 16 - s.offset);
            match s.fault {
                1 => return (0, 0),
                2 => return (17, 0),
                3 => return (-13, 0),
                4 | 5 => {
                    s.stalled = true;
                    return (-11, 0);
                }
                _ => (),
            }
            if s.stalled {
                return (-11, 0);
            }
            let count = (length as usize).min(7);
            // SAFETY: the actual method supplies a live exclusive initialized
            // suffix; count<=length and this model retains neither pointer.
            unsafe {
                std::ptr::copy_nonoverlapping(
                    s.prefix[s.offset..].as_ptr(),
                    pointer as *mut u8,
                    count,
                );
            }
            s.offset += count;
            s.stalled = true;
            (count as i64, 0)
        })
    }
}
impl Connection {
    fn directory_message(&self, op: u64, token: u64) -> [u8; 64] {
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(b"AFSRPC07");
        put(&mut raw, 1, op);
        put(&mut raw, 2, self.request);
        put(&mut raw, 3, token);
        raw
    }
    fn directory_send(&self, raw: &mut [u8; 64], _: u8, _: u8) {
        // Stage0 intentionally closes the receiver before sending the request.
        STATE.with(|s| s.borrow_mut().output.push(*raw));
        assert_eq!(self.send, 11);
    }
    fn directory_receive(&self, raw: &mut [u8; 64], error: u8) {
        check(channel::frame(self.receive, raw, false).is_ok());
        check(
            get(raw, 0) == u64::from_le_bytes(*b"AFSRPC07")
                && get(raw, 1) == u64::from(error)
                && get(raw, 2) == self.request,
        );
    }
    // LOSS_METHODS
}
fn setup(stage: u8) -> Connection {
    let c = Connection {
        request: 77,
        send: 11,
        receive: 22,
    };
    let mut s = State::default();
    if stage != 0 {
        let mut header = c.directory_message(0, 0);
        put(&mut header, 5, 112);
        s.input.push_back(header);
        if stage == 2 {
            let mut frame = [0; 64];
            for (i, value) in [5, 0o040755, 4, 0, 0, 0x840800000144, 1621447687, 7]
                .into_iter()
                .enumerate()
            {
                put(&mut frame, i, value);
            }
            s.input.push_back(frame);
        }
        let words: [u64; 2] = if stage == 1 {
            [5, 0o040755]
        } else {
            [1791290041, 7]
        };
        s.prefix[..8].copy_from_slice(&words[0].to_le_bytes());
        s.prefix[8..].copy_from_slice(&words[1].to_le_bytes());
    }
    STATE.with(|v| *v.borrow_mut() = s);
    c
}
#[test]
fn exact_loss_points_and_fragmented_prefix_never_replay() {
    for stage in 0..=2 {
        setup(stage).metadata_loss(stage);
        STATE.with(|s| {
            let s = s.borrow();
            assert_eq!(s.closed, 1, "AF07_METADATA_LOSS_ORACLE");
            assert_eq!(s.output.len(), 1);
            assert_eq!(get(&s.output[0], 1), 12);
            assert_eq!(get(&s.output[0], 2), 77);
            assert_eq!(get(&s.output[0], 3), 1);
            assert_eq!(s.offset, if stage == 0 { 0 } else { 16 });
            assert_eq!(s.waits, if stage == 0 { 0 } else { 2 });
            assert!(s.input.is_empty());
        });
    }
    let c = setup(3);
    assert!(
        std::panic::catch_unwind(|| c.metadata_loss(3)).is_err(),
        "AF07_METADATA_LOSS_ORACLE: invalid stage accepted"
    );
}
#[test]
fn corrupted_headers_and_prefixes_cannot_qualify_a_loss_point() {
    for mode in 0..5 {
        let c = setup(if mode == 3 { 2 } else { 1 });
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            match mode {
                0 => put(&mut s.input[0], 5, 111),
                1 => put(&mut s.input[0], 6, 1),
                2 => s.prefix[0] ^= 1,
                3 => put(&mut s.input[1], 2, 99),
                _ => s.fault = 3,
            }
        });
        assert!(
            std::panic::catch_unwind(|| c.metadata_loss(if mode == 3 { 2 } else { 1 })).is_err(),
            "AF07_METADATA_LOSS_ORACLE: corruption accepted"
        );
    }
}
#[test]
fn eof_bad_counts_errno_readiness_and_budget_are_checked() {
    for (fault, error) in [(1, -5), (2, -5), (3, -13), (4, -4), (5, -110)] {
        let c = setup(1);
        STATE.with(|s| s.borrow_mut().fault = fault);
        assert_eq!(c.metadata_prefix(&mut [0; 16]), Err(error));
        STATE.with(|s| assert_eq!(s.borrow().closed, 0));
    }
}
