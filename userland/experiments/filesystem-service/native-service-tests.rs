// SPDX-License-Identifier: BSD-2-Clause
//! Host-only typed C fixture plus injected channel; never native authentication.
use super::*;
use filesystem_service::{message, put, Message};
use std::{cell::RefCell, collections::VecDeque, vec::Vec};
const READER: u64 = 0x10001;
const WRITER: u64 = 0x20002;
unsafe extern "C" {
    fn fixture_reset(mode: u32);
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
                // SAFETY: production Framed caller owns this exclusive initialized
                // writable chunk; test substitutes synchronous copy with no retain.
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
                // SAFETY: production caller owns initialized live chunk through call.
                let bytes = unsafe { core::slice::from_raw_parts(pointer as *const u8, count) };
                s.output.extend_from_slice(bytes);
                count as i64
            }
            0x24003 => {
                // SAFETY: serial test uses fixed valid fixture counter index1.
                assert_eq!(unsafe { fixture_count(1) }, 1);
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
fn reset(mode: u32, frames: &[Message]) {
    // SAFETY: tests serial; prior call has returned with sole context consumed.
    unsafe { fixture_reset(mode) };
    STATE.with(|s| {
        *s.borrow_mut() = State {
            input: frames.iter().flatten().copied().collect(),
            ..State::default()
        }
    });
}
fn count(index: u32) -> u32 {
    // SAFETY: in-range counter index with no concurrent C fixture operation.
    unsafe { fixture_count(index) }
}
fn lookup() -> Message {
    let mut m = message(READER, 1);
    put(&mut m, 3, 1);
    put(&mut m, 4, 7);
    put(&mut m, 5, 4);
    m[48..52].copy_from_slice(b"file");
    m
}
fn write() -> Message {
    let mut m = message(READER, 5);
    put(&mut m, 3, 2);
    put(&mut m, 4, 4);
    put(&mut m, 5, 2);
    m[48..50].copy_from_slice(b"EF");
    m
}
fn invoke(rights: u64) -> (i32, ServiceResult) {
    let mut marker = 0u64;
    let mut out = ServiceResult::default();
    // SAFETY: distinct live host SPA marker and result, exact static dataset;
    // typed C fixture substitutes SPA, test trap substitutes retained bindings.
    let code = unsafe {
        aether_fs_service_run(
            (&mut marker as *mut u64).cast(),
            c"testpool_zstd/x86_64".as_ptr().cast(),
            20,
            READER,
            WRITER,
            rights,
            &mut out,
        )
    };
    (code, out)
}

#[test]
fn c_fixture_through_native_entry_preserves_write_and_cleanup() {
    reset(0, &[lookup(), write(), message(READER, 4)]);
    let (code, out) = invoke(7);
    assert_eq!(code, 0);
    assert_eq!((out.ready, out.requests, out.stop, out.error), (1, 3, 0, 0));
    assert_eq!((out.txg, out.bytes_staged, out.state), (788, 2, 2));
    assert_eq!((count(0), count(1), count(5)), (1, 1, 1));
    STATE.with(|s| {
        let s = s.borrow();
        assert_eq!(s.close, [READER, WRITER]);
        assert_eq!(s.output.len(), 256);
    });
}

#[test]
fn native_entry_reply_loss_keeps_progress_and_both_close_errors() {
    reset(0, &[lookup(), write(), write()]);
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        s.fail_after = Some(128);
        s.close_error = true;
    });
    let (code, out) = invoke(7);
    assert_eq!(code, 5);
    assert_eq!((out.requests, out.stop, out.error), (2, 2, -32));
    assert_eq!((out.reader_close, out.writer_close), (-5, -5));
    assert_eq!((out.txg, out.bytes_staged, out.state), (788, 2, 2));
    assert_eq!(count(5), 1);
    STATE.with(|s| assert_eq!(s.borrow().close, [READER, WRITER]));
}

#[test]
fn native_entry_consumes_owned_open_error_before_endpoints() {
    reset(1, &[]);
    let (code, out) = invoke(7);
    assert_eq!(code, 5);
    assert_eq!((out.ready, out.stop, out.error), (0, 4, -5));
    assert_eq!((count(0), count(1)), (1, 1));
    STATE.with(|s| {
        let s = s.borrow();
        assert!(s.output.is_empty());
        assert_eq!(s.close, [READER, WRITER]);
    });
}

#[test]
fn native_entry_invalid_rights_do_not_acquire_or_publish() {
    for rights in [0, 8, 256, u64::MAX] {
        reset(0, &[]);
        let (code, out) = invoke(rights);
        assert_eq!(code, 22);
        assert_eq!((out.ready, out.stop, out.error), (0, 4, -22));
        assert_eq!((out.reader_close, out.writer_close), (-9, -9));
        assert_eq!(count(0), 0);
        STATE.with(|s| assert!(s.borrow().close.is_empty()));
    }
}
