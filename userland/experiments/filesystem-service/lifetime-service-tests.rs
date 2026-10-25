// SPDX-License-Identifier: BSD-2-Clause
//! Actual Rust entry and typed C context fixture; no native authentication claim.
use super::*;
use filesystem_service::{message, put, word, Message};
use std::{cell::RefCell, collections::VecDeque, vec::Vec};
const READER: u64 = 0x10001;
const WRITER: u64 = 0x20002;
unsafe extern "C" {
    fn lifetime_reset(mode: u32, retirement: u32, reopen: u32);
    fn lifetime_retire_count() -> u32;
    fn fixture_count(index: u32) -> u32;
}
#[derive(Default)]
struct State {
    input: VecDeque<u8>,
    output: Vec<u8>,
    close: Vec<u64>,
    fail_after: Option<usize>,
    close_error: bool,
}
std::thread_local! { static STATE: RefCell<State> = RefCell::new(State::default()); }
pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64) -> i64 {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        match op {
            0x24001 => {
                assert_eq!(endpoint, READER);
                assert!(length <= 16);
                if s.input.is_empty() {
                    return 0;
                }
                let count = (length as usize).min(7).min(s.input.len());
                // SAFETY: real Framed caller retains exclusive live output chunk.
                let bytes = unsafe { core::slice::from_raw_parts_mut(pointer as *mut u8, count) };
                for b in bytes {
                    *b = s.input.pop_front().unwrap();
                }
                count as i64
            }
            0x24002 => {
                assert_eq!(endpoint, WRITER);
                assert!(length <= 16);
                if s.fail_after.is_some_and(|limit| s.output.len() >= limit) {
                    return -32;
                }
                let count = (length as usize).min(7);
                // SAFETY: real Framed caller owns this initialized readable chunk.
                let bytes = unsafe { core::slice::from_raw_parts(pointer as *const u8, count) };
                s.output.extend_from_slice(bytes);
                count as i64
            }
            0x24003 => {
                // SAFETY: serial fixture, valid fixed counter indexes. Every owned
                // success/error context must be consumed before endpoint closure.
                assert_eq!(unsafe { fixture_count(1) }, unsafe { fixture_count(0) });
                s.close.push(endpoint);
                if s.close_error {
                    -5
                } else {
                    0
                }
            }
            0x1fffe => 0,
            _ => panic!("unexpected trap"),
        }
    })
}
fn reset(mode: u32, retire: u32, reopen: u32, frames: &[Message]) {
    // SAFETY: serial test; prior entry returned with all owned contexts consumed.
    unsafe { lifetime_reset(mode, retire, reopen) };
    STATE.with(|s| {
        *s.borrow_mut() = State {
            input: frames.iter().flatten().copied().collect(),
            ..State::default()
        }
    });
}
fn count(index: u32) -> u32 {
    // SAFETY: serial fixture, valid fixed counter index.
    unsafe { fixture_count(index) }
}
fn retired() -> u32 {
    // SAFETY: serial scalar observer, no mutable borrow or native call in flight.
    unsafe { lifetime_retire_count() }
}
fn lookup(rights: u64) -> Message {
    let mut m = message(READER, 1);
    put(&mut m, 3, 1);
    put(&mut m, 4, rights);
    put(&mut m, 5, 4);
    m[48..52].copy_from_slice(b"zstd");
    m
}
fn write(index: usize) -> Message {
    let mut m = message(READER, 5);
    put(&mut m, 3, 2);
    put(&mut m, 4, (37 + index * 16) as u64);
    put(&mut m, 5, 16);
    for (i, b) in m[48..].iter_mut().enumerate() {
        *b = ((index * 16 + i) as u8).wrapping_mul(17).wrapping_add(91);
    }
    m
}
fn frames(writes: usize) -> Vec<Message> {
    let mut frames = std::vec![lookup(4), lookup(2)];
    for index in 0..writes {
        frames.push(write(index));
        let mut read = message(READER, 2);
        put(&mut read, 3, 3);
        put(&mut read, 4, (37 + index * 16) as u64);
        put(&mut read, 5, 16);
        frames.push(read);
    }
    frames
}
fn disconnect(frames: &mut Vec<Message>) {
    frames.push(message(READER, 4));
}
fn invoke() -> (i32, ServiceResult) {
    let mut marker = 0u64;
    let mut out = ServiceResult::default();
    // SAFETY: separate live host SPA marker/result, immutable retained dataset;
    // actual Rust entry with typed C substitution and retained test channels.
    let code = unsafe {
        aether_fs_service_run(
            (&mut marker as *mut u64).cast(),
            c"testpool_zstd/x86_64".as_ptr().cast(),
            20,
            READER,
            WRITER,
            7,
            &mut out,
        )
    };
    STATE.with(|s| assert_eq!(s.borrow().close, [READER, WRITER]));
    (code, out)
}
#[test]
fn eight_fresh_contexts_retire_once_and_ninth_write_is_denied() {
    let mut input = frames(8);
    input.push(write(8));
    disconnect(&mut input);
    reset(0, 0, 0, &input);
    let (code, out) = invoke();
    assert_eq!((code, out.stop, out.requests, out.error), (0, 0, 20, 0));
    assert_eq!((out.txg, out.bytes_staged, out.state), (795, 16, 2));
    assert_eq!((count(0), count(1), count(5), retired()), (9, 9, 8, 8));
    STATE.with(|s| {
        let state = s.borrow();
        let (replies, tail) = state.output.as_chunks::<64>();
        assert!(tail.is_empty());
        assert_eq!(replies.len(), 21);
        for index in 0..8 {
            let wrote = &replies[3 + index * 2];
            assert_eq!(
                (
                    word(wrote, 1),
                    word(wrote, 4),
                    word(wrote, 5),
                    word(wrote, 6)
                ),
                (0, 788 + index as u64, 16, 2)
            );
            let read = replies[4 + index * 2];
            assert_eq!(&read[48..], &write(index)[48..]);
        }
        let ninth = &replies[19];
        assert_eq!(word(ninth, 1) as i64, -28);
    });
}
#[test]
fn failed_retirement_or_owned_reopen_keeps_synced_progress_and_stops() {
    for at in [1, 8] {
        let input = frames(8);
        reset(0, at, 0, &input);
        let (code, out) = invoke();
        assert_eq!((code, out.stop, out.error), (5, 5, -5));
        assert_eq!(
            (out.txg, out.bytes_staged, out.state),
            (787 + u64::from(at), 16, 2)
        );
        assert_eq!((count(0), count(1), count(5), retired()), (at, at, at, at));
        reset(0, 0, at + 1, &input);
        let (code, out) = invoke();
        assert_eq!((code, out.stop, out.error), (5, 5, -5));
        assert_eq!(
            (out.txg, out.bytes_staged, out.state),
            (787 + u64::from(at), 16, 2)
        );
        assert_eq!(
            (count(0), count(1), count(5), retired()),
            (at + 1, at + 1, at, at)
        );
    }
}
#[test]
fn failed_c_write_and_verification_never_retire_or_reopen() {
    for (mode, state) in [(7, 1), (8, 3), (5, 2), (6, 2)] {
        reset(mode, 0, 0, &frames(8));
        let (code, out) = invoke();
        assert_eq!((code, out.stop, out.error), (5, 5, -5));
        assert_eq!(out.state, state);
        if mode != 8 {
            assert_eq!((out.txg, out.bytes_staged), (788, 16));
        }
        assert_eq!((count(0), count(1), count(5), retired()), (1, 1, 1, 0));
    }
}
#[test]
fn known_unassigned_error_does_not_restore_call_budget() {
    let mut input = frames(2);
    disconnect(&mut input);
    reset(15, 0, 0, &input);
    let (code, out) = invoke();
    assert_eq!((code, out.stop, out.txg, out.state), (0, 0, 0, 0));
    assert_eq!((count(0), count(1), count(5), retired()), (1, 1, 1, 0));
}
#[test]
fn lost_reply_after_first_or_last_write_keeps_actual_progress_without_replay() {
    for at in [1, 8] {
        reset(0, 0, 0, &frames(8));
        STATE.with(|s| s.borrow_mut().fail_after = Some((3 + (at - 1) * 2) * 64));
        let (code, out) = invoke();
        assert_eq!((code, out.stop, out.error), (5, 2, -32));
        assert_eq!(
            (out.txg, out.bytes_staged, out.state),
            (787 + at as u64, 16, 2)
        );
        assert_eq!(
            (count(0), count(1), count(5), retired()),
            (at as u32 + 1, at as u32 + 1, at as u32, at as u32)
        );
    }
}
#[test]
fn partial_input_after_first_or_last_write_never_dispatches() {
    for at in [1, 8] {
        reset(0, 0, 0, &frames(at));
        STATE.with(|s| s.borrow_mut().input.extend(&message(READER, 4)[..16]));
        let (code, out) = invoke();
        assert_eq!((code, out.stop, out.error), (5, 1, -5));
        assert_eq!(out.requests, 2 + at as u64 * 2);
        assert_eq!(
            (out.txg, out.bytes_staged, out.state),
            (787 + at as u64, 16, 2)
        );
        assert_eq!(
            (count(0), count(1), count(5), retired()),
            (at as u32 + 1, at as u32 + 1, at as u32, at as u32)
        );
    }
}
#[test]
fn both_endpoint_cleanup_errors_survive_after_consuming_last_context() {
    let mut input = frames(8);
    disconnect(&mut input);
    reset(0, 0, 0, &input);
    STATE.with(|s| s.borrow_mut().close_error = true);
    let (code, out) = invoke();
    assert_eq!((code, out.stop, out.error), (5, 0, -5));
    assert_eq!((out.reader_close, out.writer_close), (-5, -5));
    assert_eq!((out.txg, out.bytes_staged, out.state), (795, 16, 2));
    assert_eq!((count(0), count(1), count(5), retired()), (9, 9, 8, 8));
}
