// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use std::{cell::RefCell, vec::Vec};
#[derive(Default)]
struct State {
    mode: u32,
    attempts: Option<u64>,
    requests: Option<u64>,
    corrupt: u8,
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
    state.home.mutation_attempts = STATE.with(|s| {
        s.borrow().attempts.unwrap_or(if cfg!(fs_home_cold_reopen) {
            0
        } else if cfg!(fs_home_terminfo_seven) {
            7
        } else if cfg!(fs_home_terminfo_six) {
            6
        } else if cfg!(fs_home_probe_three) {
            3
        } else {
            2
        })
    });
    state.phases = 8191;
    #[cfg(not(fs_home_cold_reopen))]
    {
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
    }
    state.home.service.ready = 1;
    state.home.service.requests = STATE.with(|s| {
        s.borrow()
            .requests
            .unwrap_or(if cfg!(any(fs_home_terminfo_six, fs_home_terminfo_seven)) {
                13
            } else if cfg!(fs_af09_drain) {
                3
            } else {
                2
            })
    });
    if mode == 5 {
        state.home.flags &= !ORDERED;
    }
    #[cfg(fs_home_cold_reopen)]
    {
        state.home.flags &= !ORDERED;
    }
    match STATE.with(|s| s.borrow().corrupt) {
        0 => {}
        1 => state.home.create.returned_error = 5,
        2 => {
            state.home.create.returned = 0;
            state.home.create.provider_state = 3;
        }
        3 => state.home.create.provider = 2,
        4 => state.home.phase = 9,
        5 => state.home.error_kind = 10,
        6 => state.home.service.reader_close = -9,
        7 => state.home.service.writer_close = -5,
        8 => state.home.service.ready = 0,
        9 => state.home.service.stop = 2,
        10 => state.home.service.error = -5,
        11 => {
            state.home.service.state = 2;
            state.home.service.txg = 0;
        }
        12 => state.home.service.bytes_staged = 1,
        13 => {
            if cfg!(fs_home_cold_reopen) {
                state.home.flags |= ORDERED;
            } else {
                state.home.flags &= !ORDERED;
            }
        }
        14 => state.phases = FINISHED - 1,
        15 => state.engine_error = 5,
        16 => state.home.service.state = 3,
        17 => state.home.create.returned_staged = 4097,
        18 => state.home.version = 2,
        19 => state.bytes = 383,
        20 => {
            state.home.service.state = 2;
            state.home.service.txg = 800;
            state.home.service.bytes_staged = 4096;
        }
        _ => panic!("invalid test corruption"),
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

#[cfg(not(any(fs_home_cold_reopen, fs_home_terminfo_six, fs_home_terminfo_seven)))]
#[test]
fn fixed_home_probe_requires_three_attempts_only_when_selected() {
    for attempts in [2, 3, 4, 6] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                requests: if attempts == 6 { Some(13) } else { None },
                ..State::default()
            }
        });
        let mut state = state();
        state.phases = 0;
        // The engine stub's field is varied below through its ordinary test mode.
        STATE.with(|s| s.borrow_mut().attempts = Some(attempts));
        assert_eq!(
            run(&mut state),
            if (cfg!(fs_home_probe_three) && attempts != 3)
                || (cfg!(fs_af09_drain) && attempts != 2)
            {
                5
            } else {
                0
            },
            "HOME_PROBE_THREE"
        );
    }
}

#[cfg(fs_af09_drain)]
#[test]
fn drain_two_mutations_three_requests_are_exact() {
    for attempts in [0, 1, 2, 3, 4, 9, u64::MAX] {
        for requests in [0, 1, 2, 3, 4, 96, u64::MAX] {
            STATE.with(|s| {
                *s.borrow_mut() = State {
                    mode: 4,
                    attempts: Some(attempts),
                    requests: Some(requests),
                    ..State::default()
                }
            });
            let mut selected = state();
            selected.phases = 0;
            assert_eq!(
                run(&mut selected),
                if (attempts, requests) == (2, 3) { 0 } else { 5 },
                "AF09_DRAIN_LAUNCH_COUNT"
            );
        }
    }
}

#[cfg(fs_home_terminfo_six)]
#[test]
fn terminfo_six_requires_exact_count_and_complete_clean_result() {
    for (attempts, expected) in [(3, 5), (5, 5), (6, 0), (7, 5), (9, 5)] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                attempts: Some(attempts),
                requests: Some(13),
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(run(&mut selected), expected, "HOME_TERMINFO_SIX");
    }
}

#[cfg(any(fs_home_terminfo_six, fs_home_terminfo_seven))]
#[test]
fn terminfo_six_keeps_all_clean_result_and_resource_checks() {
    let attempts = if cfg!(fs_home_terminfo_seven) { 7 } else { 6 };
    for corrupt in 1..=20 {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                attempts: Some(attempts),
                requests: Some(13),
                corrupt,
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(
            run(&mut selected),
            if corrupt == 20 { 0 } else { 5 },
            "HOME_TERMINFO_CLEAN:{corrupt}"
        );
    }
    for (requests, expected) in [(0, 5), (3, 5), (4, 0), (13, 0), (96, 0), (97, 5)] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                attempts: Some(attempts),
                requests: Some(requests),
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(
            run(&mut selected),
            if attempts > 2 + requests { 5 } else { expected },
            "HOME_TERMINFO_REQUEST_CAP"
        );
    }
}

#[cfg(fs_home_terminfo_seven)]
#[test]
fn terminfo_seven_requires_exact_count_and_complete_clean_result() {
    for (attempts, expected) in [(3, 5), (5, 5), (6, 5), (7, 0), (8, 5), (9, 5)] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                attempts: Some(attempts),
                requests: Some(18),
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(run(&mut selected), expected, "HOME_TERMINFO_SEVEN");
    }
}

#[cfg(fs_home_cold_reopen)]
#[test]
fn cold_reopen_requires_exact_zero_and_all_completion_obligations() {
    for attempts in [0, 1, 2, 7, 9, u64::MAX] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                attempts: Some(attempts),
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(
            run(&mut selected),
            if attempts == 0 { 0 } else { 5 },
            "COLD_LAUNCH_COUNT"
        );
    }
    for corrupt in 1..=20 {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                corrupt,
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(run(&mut selected), 5, "COLD_LAUNCH_COMPLETE:{corrupt}");
    }
    for requests in [0, 1, 4, 20, 96, 97, u64::MAX] {
        STATE.with(|s| {
            *s.borrow_mut() = State {
                mode: 4,
                requests: Some(requests),
                ..State::default()
            }
        });
        let mut selected = state();
        selected.phases = 0;
        assert_eq!(
            run(&mut selected),
            if (1..=96).contains(&requests) { 0 } else { 5 }
        );
    }
}
