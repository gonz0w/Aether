// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use std::{cell::RefCell, vec::Vec};
#[derive(Default)]
struct State {
    mode: u32,
    calls: usize,
    closes: Vec<u64>,
}
std::thread_local! {static STATE:RefCell<State>=RefCell::new(State::default());}
pub unsafe fn getauxval(_tag: usize) -> usize {
    0
}
pub unsafe fn close(token: u64) -> i64 {
    STATE.with(|s| s.borrow_mut().closes.push(token));
    0
}
pub unsafe fn aether_fs_home_engine_run(_grant: u64, state: *mut HomeLaunchState) -> i32 {
    // SAFETY: run supplies live exclusive initialized state for this synchronous stub.
    let state = unsafe { &mut *state };
    let mode = STATE.with(|s| s.borrow().mode);
    if mode == 0 {
        return 5;
    }
    state.phases = 32;
    state.home.flags = CALLBACK;
    if mode == 1 {
        return 5;
    }
    state.home.flags |= ENTRY;
    state.home.phase = 1;
    state.home.error_kind = 1;
    if mode == 2 {
        return 22;
    }
    if mode == 3 {
        state.home.flags |= ACCEPTED;
        return 5;
    }
    if mode == 6 {
        state.home.bytes = 136;
        return 5;
    }
    state.home.phase = 0;
    state.home.error_kind = 0;
    state.home.flags = 63;
    state.home.mutation_attempts = 2;
    state.phases = 8191;
    state.home.mkdir = BootstrapReceipt {
        provider: 1,
        returned: 1,
        returned_txg: 788,
        returned_state: 2,
        provider_txg: 788,
        provider_state: 2,
        ..BootstrapReceipt::default()
    };
    state.home.create = BootstrapReceipt {
        returned_txg: 789,
        provider_txg: 789,
        ..state.home.mkdir
    };
    state.home.service.ready = 1;
    state.home.service.requests = 1;
    if mode == 5 {
        state.home.flags &= !ORDERED;
    }
    0
}
#[allow(clippy::too_many_arguments)]
pub unsafe fn aether_fs_home_run(
    _spa: *mut c_void,
    _dataset: *const u8,
    _length: usize,
    _reader: u64,
    _writer: u64,
    _uid: u64,
    _gid: u64,
    out: *mut HomeResult,
    bytes: usize,
) -> i32 {
    assert_eq!(bytes, 320);
    STATE.with(|s| s.borrow_mut().calls += 1);
    // SAFETY: real callback gives aligned initialized exclusive carrier.
    let out = unsafe { &mut *out };
    assert_eq!(out.flags, 16);
    out.flags |= 32 | 4 | 8;
    5
}
fn state() -> HomeLaunchState {
    HomeLaunchState {
        version: 1,
        bytes: 384,
        reader: 0x10001,
        writer: 0x20002,
        phases: 32,
        home: HomeResult::initial(),
        ..HomeLaunchState::default()
    }
}
#[test]
fn callback_latches_before_entry_and_reentry_never_resets_evidence() {
    STATE.with(|s| *s.borrow_mut() = State::default());
    let mut s = state();
    // SAFETY: separate initialized live state and nonnull host SPA substitute.
    assert_eq!(
        unsafe { aether_fs_home_launch_serve(core::ptr::dangling_mut(), &mut s) },
        5
    );
    let before = s.home;
    // SAFETY: same exclusive storage; reentry deliberately rejected.
    assert_eq!(
        unsafe { aether_fs_home_launch_serve(core::ptr::dangling_mut(), &mut s) },
        22
    );
    assert_eq!(s.home, before);
    STATE.with(|s| assert_eq!(s.borrow().calls, 1));
}
#[test]
fn malformed_callback_cannot_transfer_or_reset() {
    let mut s = state();
    s.home.mkdir.provider = 2;
    let before = s.home;
    // SAFETY: live state, malformed protocol carrier intentionally rejected.
    assert_eq!(
        unsafe { aether_fs_home_launch_serve(core::ptr::dangling_mut(), &mut s) },
        22
    );
    assert_eq!(s.home, before);
}

#[test]
fn launch_requires_complete_valid_evidence_and_only_closes_proven_handback() {
    for (mode, code, closes) in [
        (0, 5, 2),
        (1, 5, 0),
        (2, 22, 2),
        (3, 5, 0),
        (4, 0, 0),
        (5, 5, 0),
        (6, 5, 0),
    ] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode,
                ..State::default()
            }
        });
        let mut state = state();
        state.phases = 0;
        assert_eq!(run(&mut state), code, "HOME_LAUNCH_VALIDATION");
        STATE.with(|s| assert_eq!(s.borrow().closes.len(), closes, "HOME_LAUNCH_HANDBACK"));
    }
}

#[test]
fn malformed_launch_prefix_cannot_enter_callback() {
    for index in 0..4 {
        let mut state = state();
        match index {
            0 => state.phases |= 8192,
            1 => state.engine_error = 5,
            2 => state.startup_reader_close = -9,
            _ => state.startup_writer_close = -9,
        };
        // SAFETY: live initialized exclusive state with deliberately contradictory prefix.
        assert_eq!(
            unsafe { aether_fs_home_launch_serve(core::ptr::dangling_mut(), &mut state) },
            22
        );
        assert!(state.home.canonical_initial(false));
    }
}
