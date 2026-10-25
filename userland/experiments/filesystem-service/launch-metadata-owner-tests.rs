// SPDX-License-Identifier: BSD-2-Clause
//! Typed FFI doubles for the actual executable owner, no host kernel claims.
use super::*;
use std::{cell::RefCell, vec::Vec};
#[derive(Default)]
struct Input {
    mode: u8,
    closes: Vec<u64>,
    calls: usize,
    serves: usize,
    missing_phase: u64,
    bad_provision: bool,
}
std::thread_local! {static INPUT:RefCell<Input>=RefCell::new(Input::default());}
fn state() -> LaunchState {
    LaunchState {
        version: 1,
        bytes: 136,
        reader: 0x10001,
        writer: 0x20002,
        ..LaunchState::default()
    }
}
fn reset(mode: u8) {
    INPUT.with(|s| {
        *s.borrow_mut() = Input {
            mode,
            ..Input::default()
        }
    });
}
pub unsafe fn getauxval(tag: usize) -> usize {
    match tag {
        0xa004 => 0x10001,
        0xa005 => 0x20002,
        _ => panic!("BOOTSTRAP_TAG"),
    }
}
pub unsafe fn close(endpoint: u64) -> i64 {
    INPUT.with(|s| {
        s.borrow_mut().closes.push(endpoint);
        if s.borrow().mode == 9 {
            -13
        } else {
            0
        }
    })
}
pub unsafe fn aether_fs_engine_run(grant: u64, p: *mut LaunchState) -> i32 {
    assert_eq!(grant, 0xf101, "BLOCK_SCOPE");
    // SAFETY: owner retains this exclusive initialized output through the call.
    let s = unsafe { &mut *p };
    let mode = INPUT.with(|s| {
        s.borrow_mut().calls += 1;
        s.borrow().mode
    });
    if mode == 1 || mode == 9 {
        s.engine_error = 12;
        return 12;
    }
    s.phases = 63;
    // SAFETY: static nonnull opaque fixture sentinel, never dereferenced as SPA.
    let error = unsafe { aether_fs_launch_serve(core::ptr::dangling_mut::<c_void>(), s) };
    s.phases = FINISHED;
    s.phases &= !INPUT.with(|s| s.borrow().missing_phase);
    match mode {
        2 => {
            s.phases &= !1024;
            s.engine_error = 5;
            5
        }
        3 => {
            s.phases &= !4096;
            0
        }
        4 => {
            s.service.error = -32;
            0
        }
        5 => {
            s.service.reader_close = -13;
            0
        }
        12 => {
            s.service.writer_close = -13;
            0
        }
        6 => {
            s.service.ready = 0;
            0
        }
        7 => {
            s.service.stop = 1;
            0
        }
        8 => {
            s.version = 2;
            0
        }
        13 => {
            s.engine_error = 5;
            0
        }
        14 => {
            s.bytes = 135;
            0
        }
        15 | 16 => {
            s.service.state = if mode == 15 { 3 } else { 1 };
            s.service.txg = 788;
            0
        }
        17 => {
            s.service.state = 2;
            s.service.txg = 0;
            0
        }
        18 => {
            s.service.state = 0;
            s.service.txg = 788;
            0
        }
        19 => {
            s.service.state = 2;
            s.service.txg = 788;
            s.service.bytes_staged = 4097;
            0
        }
        20 => {
            s.service.requests = 0;
            0
        }
        21 => {
            s.phases |= 8192;
            0
        }
        22 => -32,
        23 => 256,
        24 => 13,
        _ => error,
    }
}
#[allow(
    clippy::too_many_arguments,
    reason = "Mirrors the trusted nine-argument AF07 service ABI."
)]
pub unsafe fn aether_fs_metadata_run(
    spa: *mut c_void,
    name: *const u8,
    length: usize,
    reader: u64,
    writer: u64,
    rights: u64,
    uid: u64,
    gid: u64,
    out: *mut ServiceResult,
) -> i32 {
    assert!(!spa.is_null());
    if (reader, writer, rights, uid, gid) != (0x10001, 0x20002, 31, 1000, 1000) {
        INPUT.with(|s| s.borrow_mut().bad_provision = true);
        return 22;
    }
    // SAFETY: actual owner provides this immutable terminated slice.
    assert_eq!(
        unsafe { core::slice::from_raw_parts(name, length + 1) },
        b"testpool_zstd/x86_64\0"
    );
    // SAFETY: actual owner provides exclusive initialized separate result.
    let result = unsafe { &mut *out };
    result.ready = 1;
    let mode = INPUT.with(|s| {
        s.borrow_mut().serves += 1;
        s.borrow().mode
    });
    if mode == 10 {
        result.stop = 2;
        result.error = -32;
        result.txg = 900;
        result.state = 2;
        return 5;
    }
    result.requests = if mode == 11 { 1000 } else { 1 };
    result.txg = if mode == 11 { 999 } else { 0 };
    result.state = if mode == 11 { 2 } else { 0 };
    0
}
#[test]
fn clean_readonly_and_many_requests_are_not_fixture_workloads() {
    for mode in [0, 11] {
        reset(mode);
        let mut s = state();
        assert_eq!(run(&mut s), 0);
        INPUT.with(|i| {
            let i = i.borrow();
            assert_eq!((i.calls, i.serves), (1, 1));
            assert!(i.closes.is_empty());
        });
    }
    reset(0);
    assert_eq!(filesystem_main(), 0);
}
#[test]
fn startup_failure_closes_exact_pair_once_and_retains_failure() {
    for mode in [1, 9] {
        reset(mode);
        let mut s = state();
        assert_eq!(run(&mut s), 12);
        assert_eq!(s.engine_error, 12);
        INPUT.with(|i| {
            let i = i.borrow();
            assert_eq!(i.closes, [0x10001, 0x20002]);
            assert_eq!((i.calls, i.serves), (1, 0));
        });
        if mode == 9 {
            assert_eq!(s.startup_reader_close, -13);
            assert_eq!(s.startup_writer_close, -13);
        }
    }
}
#[test]
fn bad_bootstrap_cannot_start_engine_or_close_same_token_twice() {
    for (reader, writer) in [
        (0, 0x20002),
        (0x10001, 0),
        (0x10001, 0x10001),
        (0x10001, 0x10002),
        (0x10002, 0x20001),
        (u64::MAX, 0x20002),
    ] {
        reset(0);
        let mut s = state();
        s.reader = reader;
        s.writer = writer;
        assert_eq!(run(&mut s), 22);
        INPUT.with(|i| {
            let i = i.borrow();
            assert_eq!(i.calls, 0);
            assert_eq!(i.serves, 0);
            assert_eq!(
                i.closes.len(),
                usize::from(reader != 0) + usize::from(writer != 0 && reader != writer)
            );
        });
    }
}
#[test]
fn no_error_normalization_or_false_cleanup_ready_or_disconnect() {
    for mode in [2, 3, 4, 5, 6, 7, 8, 12] {
        reset(mode);
        assert_eq!(run(&mut state()), 5);
        INPUT.with(|i| {
            let i = i.borrow();
            assert_eq!((i.calls, i.serves), (1, 1));
            assert!(i.closes.is_empty());
        });
    }
    reset(10);
    let mut s = state();
    assert_eq!(run(&mut s), 5);
    assert_eq!((s.service.error, s.service.txg), (-32, 900));
    assert_eq!(s.phases, FINISHED);
}
#[test]
fn callback_rejects_wrong_context_before_acquiring_endpoints() {
    reset(0);
    let mut s = state();
    // SAFETY: rejected null or initialized fixture borrow; no real SPA dereference.
    unsafe {
        assert_eq!(aether_fs_launch_serve(core::ptr::null_mut(), &mut s), 22);
        assert_eq!(
            aether_fs_launch_serve(core::ptr::dangling_mut(), core::ptr::null_mut()),
            22
        );
        assert_eq!(
            aether_fs_launch_serve(core::ptr::dangling_mut(), &mut s),
            22
        );
    }
    INPUT.with(|i| assert_eq!(i.borrow().serves, 0));
}

#[test]
fn every_cleanup_phase_and_unknown_phase_is_required_for_success() {
    for bit in 0..13 {
        reset(0);
        INPUT.with(|s| s.borrow_mut().missing_phase = 1 << bit);
        assert_eq!(run(&mut state()), 5, "MISSING_CLEANUP_PHASE");
        INPUT.with(|s| assert!(s.borrow().closes.is_empty()));
    }
    reset(21);
    assert_eq!(run(&mut state()), 5);
}

#[test]
fn impossible_success_progress_and_unreported_engine_errors_stay_failed() {
    for mode in 13..=20 {
        reset(mode);
        assert_eq!(run(&mut state()), 5, "FALSE_CLEAN_SUCCESS");
    }
    for (mode, expected) in [(22, 5), (23, 5), (24, 13)] {
        reset(mode);
        assert_eq!(run(&mut state()), expected);
    }
}

#[test]
fn callback_validates_version_extent_and_binding_before_service() {
    for invalid in 0..4 {
        reset(0);
        let mut s = state();
        s.phases = 63;
        match invalid {
            0 => s.version = 2,
            1 => s.bytes = 135,
            2 => s.writer = s.reader,
            _ => s.reader = 0,
        }
        // SAFETY: separate valid initialized state and unused opaque SPA marker;
        // callback must reject before passing either to the service.
        assert_eq!(
            unsafe { aether_fs_launch_serve(core::ptr::dangling_mut(), &mut s) },
            22
        );
        INPUT.with(|i| assert_eq!(i.borrow().serves, 0));
    }
    reset(0);
    assert_eq!(filesystem_main(), 0);
    INPUT.with(|i| assert!(!i.borrow().bad_provision));
}
