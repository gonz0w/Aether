// SPDX-License-Identifier: BSD-2-Clause
//! Actual entry tests use the bridge and a typed C provider, never native I/O.
use super::*;
use filesystem_service::{message, put, word};
use std::{cell::RefCell, collections::VecDeque, vec::Vec};
const READER: u64 = 0x10001;
const WRITER: u64 = 0x20002;
unsafe extern "C" {
    fn home_reset(mode: u32);
    fn home_count(index: u32) -> u32;
    #[cfg(fs_home_probe_three)]
    fn home_clock(seconds: u64, nanos: u64, after: u32);
    fn home_validate(result: *const HomeResult, protocol: *mut i32) -> i32;
}
#[derive(Default)]
struct State {
    #[cfg(fs_af09_drain)]
    diagnostic: Vec<([u8; 8], usize, usize)>,
    #[cfg(fs_af09_drain)]
    diagnostic_return: Option<i64>,
    input: VecDeque<u8>,
    received: usize,
    output: Vec<u8>,
    closes: Vec<u64>,
    close_errors: [i64; 2],
    published: usize,
    publish_error: i64,
    #[cfg(fs_home_probe_three)]
    advance_clock_on_ready: bool,
    fail_after: Option<usize>,
}
std::thread_local! { static STATE: RefCell<State> = RefCell::new(State::default()); }
pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64) -> i64 {
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        match op {
            #[cfg(fs_af09_drain)]
            0x10001 => {
                assert_eq!((endpoint, length), (1, 8));
                // SAFETY: actual endpoint supplies a live initialized record8.
                let bytes = unsafe { core::slice::from_raw_parts(pointer as *const u8, 8) };
                let record = bytes.try_into().unwrap();
                let received = s.received;
                let sent = s.output.len();
                s.diagnostic.push((record, received, sent));
                s.diagnostic_return.unwrap_or(8)
            }
            0x20004 => {
                #[cfg(fs_home_probe_three)]
                if s.advance_clock_on_ready {
                    // SAFETY: host-only UTC fixture setter, no live context mutation.
                    unsafe { home_clock(1791290100, 0, 0) };
                }
                s.published += 1;
                s.publish_error
            }
            0x24001 => {
                assert_eq!(endpoint, READER);
                let n = (length as usize).min(s.input.len());
                // SAFETY: actual Framed retains an initialized writable chunk.
                let bytes = unsafe { core::slice::from_raw_parts_mut(pointer as *mut u8, n) };
                for byte in bytes {
                    *byte = s.input.pop_front().unwrap();
                }
                s.received += n;
                n as i64
            }
            0x24002 => {
                assert_eq!(endpoint, WRITER);
                if s.fail_after.is_some_and(|n| s.output.len() >= n) {
                    return -32;
                }
                let n =
                    (length as usize).min(s.fail_after.map_or(usize::MAX, |n| n - s.output.len()));
                // SAFETY: actual Framed provides an initialized readable chunk.
                s.output.extend_from_slice(unsafe {
                    core::slice::from_raw_parts(pointer as *const u8, n)
                });
                n as i64
            }
            0x24003 => {
                let index = s.closes.len();
                s.closes.push(endpoint);
                s.close_errors[index]
            }
            0x24004 | 0x1fffe => 0,
            _ => panic!("unexpected trap"),
        }
    })
}
fn reset(mode: u32) {
    // SAFETY: serial fixture, prior entry has returned.
    unsafe { home_reset(mode) };
    STATE.with(|s| *s.borrow_mut() = State::default());
}
fn count(i: u32) -> u32 {
    // SAFETY: scalar fixture query.
    unsafe { home_count(i) }
}
fn invoke(out: &mut HomeResult) -> i32 {
    let mut marker = 0u64;
    // SAFETY: live exclusive independent output/SPA marker and fixed C dataset.
    unsafe {
        aether_fs_home_run(
            (&mut marker as *mut u64).cast(),
            c"testpool_zstd/x86_64".as_ptr().cast(),
            20,
            READER,
            WRITER,
            1000,
            1000,
            out,
            320,
        )
    }
}
#[test]
fn bootstrap_retains_both_receipts_then_activates_and_closes() {
    reset(0);
    command(4, None);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 0);
    assert_eq!((out.phase, out.mutation_attempts, out.flags), (0, 2, 47));
    assert_eq!((out.mkdir.provider, out.create.provider), (1, 1));
    assert_eq!(
        (out.mkdir.provider_txg, out.create.provider_txg),
        (788, 789)
    );
    assert_eq!((out.service.ready, out.service.stop), (1, 0));
    assert_eq!(
        (count(0), count(1), count(2), count(3), count(4)),
        (3, 3, 2, 2, 0)
    );
    STATE.with(|s| {
        let s = s.borrow();
        assert_eq!(s.closes, [READER, WRITER]);
        assert_eq!(s.output.len(), 192);
        assert_eq!(s.published, 1);
    });
}
#[test]
fn first_unassigned_has_no_order_or_activation_and_no_replay() {
    reset(1);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 5);
    assert_eq!((out.phase, out.mutation_attempts, out.flags), (4, 1, 44));
    assert_eq!(
        (out.mkdir.provider_error, out.mkdir.provider_state),
        (17, 0)
    );
    assert_eq!(out.create, BootstrapReceipt::default());
    let before = out;
    assert_eq!(invoke(&mut out), 22);
    assert_eq!(out, before);
    assert_eq!(count(2), 1);
}
#[test]
fn create_failures_preserve_first_obligation_and_original_typed_result() {
    for mode in 2..=6 {
        reset(mode);
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 5);
        assert_eq!((out.phase, out.mutation_attempts), (6, 2));
        assert_ne!(out.flags & 2, 0, "HOME_ORDER_MONOTONIC");
        assert_eq!(out.mkdir.provider_txg, 788, "HOME_FIRST_RECEIPT");
        assert_eq!(out.mkdir.returned, 1);
        if mode == 5 {
            assert_eq!(out.create.provider, 1, "HOME_TYPED_NEGATIVE");
            assert_eq!(out.create.provider_error, -1);
            assert_eq!(out.create.error_kind, 9);
        }
        assert_eq!(count(2), 2);
    }
}
#[test]
fn publication_and_both_greeting_losses_retain_bootstrap_and_reply_status() {
    for at in [0, 64, 128] {
        reset(0);
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            if at == 128 {
                s.publish_error = -13;
            } else {
                s.fail_after = Some(at);
            }
        });
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 5);
        assert_eq!(out.phase, 0);
        assert_eq!(out.mutation_attempts, 2);
        assert_eq!((out.service.ready, out.service.stop), (0, 2));
        assert_ne!(out.flags & 2, 0);
    }
}
#[test]
fn malformed_initial_output_is_never_reset_or_acquired() {
    reset(0);
    let mut out = HomeResult::initial();
    out.create.returned = 1;
    let before = out;
    assert_eq!(invoke(&mut out), 22);
    assert_eq!(out, before);
    assert_eq!(count(0), 0);
}
#[test]
fn scalar_preflight_returns_explicit_canonical_handback() {
    reset(0);
    let mut out = HomeResult::initial();
    let mut marker = 0u64;
    // SAFETY: independent initialized trusted storage, deliberately invalid tokens.
    let code = unsafe {
        aether_fs_home_run(
            (&mut marker as *mut u64).cast(),
            c"testpool_zstd/x86_64".as_ptr().cast(),
            20,
            0,
            WRITER,
            1000,
            1000,
            &mut out,
            320,
        )
    };
    assert_eq!(code, 22);
    assert_eq!((out.flags, out.phase, out.error_kind), (32, 1, 1));
    assert!(out.canonical_unaccepted());
    assert_eq!(count(0), 0);
}

fn command(op: u64, name: Option<&[u8]>) {
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        let mut frame = message(READER, op);
        put(&mut frame, 3, if op == 4 { 0 } else { 2 });
        if let Some(name) = name {
            put(&mut frame, 4, if op == 1 { 3 } else { 0 });
            put(&mut frame, 5, name.len() as u64);
            s.input.extend(frame);
            let mut body = [0; 64];
            body[..name.len()].copy_from_slice(name);
            s.input.extend(body);
        } else {
            s.input.extend(frame);
        }
    });
}
#[test]
fn tenth_mutation_is_rejected_before_provider_effects() {
    reset(0);
    for i in 0..8 {
        command(7, Some(&[b'a' + i]));
    }
    command(4, None);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 0);
    assert_eq!(out.mutation_attempts, 9, "HOME_MUTATION_QUOTA");
    assert_eq!(count(2), 9, "HOME_MUTATION_QUOTA");
    STATE.with(|s| {
        let s = s.borrow();
        let denied: &[u8] = &s.output[128 + 7 * 64..128 + 8 * 64];
        assert_ne!(word(denied.try_into().unwrap(), 1), 0);
    });
}
#[test]
fn request_97_is_not_received_or_dispatched() {
    reset(0);
    for _ in 0..97 {
        command(6, None);
    }
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 5);
    assert_eq!(
        (out.service.stop, out.service.requests),
        (3, 96),
        "HOME_REQUEST_QUOTA"
    );
    STATE.with(|s| assert_eq!(s.borrow().received, 96 * 64, "HOME_REQUEST_QUOTA"));
}
#[test]
fn temporary_probe_handle_is_released_before_full_capacity_delegation() {
    reset(0);
    for _ in 0..13 {
        command(1, Some(b"probe"));
    }
    command(4, None);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 0);
    STATE.with(|s| {
        let s = s.borrow();
        for i in 0..12 {
            let frame = (&s.output[128 + i * 64..128 + (i + 1) * 64])
                .try_into()
                .unwrap();
            assert_eq!(word(frame, 1), 0, "HOME_TEMPORARY_RELEASE");
        }
        let frame = (&s.output[128 + 12 * 64..128 + 13 * 64])
            .try_into()
            .unwrap();
        assert_ne!(word(frame, 1), 0);
    });
}
#[test]
fn clock_refresh_and_identity_failures_keep_the_correct_phase() {
    for (mode, phase, attempts) in [
        (7, 4, 0),
        (8, 6, 1),
        (9, 6, 2),
        (10, 5, 1),
        (14, 5, 1),
        (11, 7, 2),
        (12, 7, 2),
    ] {
        reset(mode);
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 5);
        assert_eq!((out.phase, out.mutation_attempts), (phase, attempts));
        if mode == 9 {
            assert_eq!(out.create.provider_error, 0);
            assert_eq!(out.create.returned, 2);
            assert_eq!(out.create.error_kind, 15);
            assert_eq!(out.create.provider_txg, 789);
        }
        if mode == 10 {
            assert_eq!(count(2), 1, "HOME_ROOT_BEFORE_CREATE");
        }
    }
    reset(13);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 5);
    assert_eq!((out.phase, out.service.stop, out.service.error), (0, 2, -5));
    STATE.with(|s| assert_eq!(s.borrow().published, 0));
}

#[test]
fn typed_lost_observation_flattens_uncertainty_and_requires_ordering() {
    let mut receipt = BootstrapReceipt::default();
    let observed = NamespaceObservation {
        result: Err(Error::Uncertain),
        provider: Some(Err(filesystem_bridge::policy::Lost)),
    };
    assert_eq!(retain(&mut receipt, observed), Err(Error::Uncertain));
    assert_eq!(
        (receipt.provider, receipt.returned, receipt.error_kind),
        (2, 2, 14),
        "HOME_LOST_UNCERTAINTY"
    );
    assert!(receipt.requires_ordering());
    assert!(receipt.valid());
}

#[test]
fn both_actual_endpoint_closes_are_retained_on_bootstrap_and_loop_failure() {
    for mode in [0, 1] {
        reset(mode);
        STATE.with(|s| s.borrow_mut().close_errors = [-13, -32]);
        command(4, None);
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 5);
        assert_eq!(
            [out.service.reader_close, out.service.writer_close],
            [-13, -32]
        );
        assert_ne!(out.flags & CLOSE_ATTEMPTED, 0);
        STATE.with(|s| assert_eq!(s.borrow().closes, [READER, WRITER]));
    }
}
#[test]
fn output_extent_rejection_preserves_caller_storage_without_acquisition() {
    reset(0);
    let mut out = HomeResult::initial();
    let before = out;
    // SAFETY: storage is aligned and live; deliberately wrong byte extent rejects before dereference.
    let code = unsafe {
        aether_fs_home_run(
            core::ptr::null_mut(),
            core::ptr::null(),
            0,
            READER,
            WRITER,
            1000,
            1000,
            &mut out,
            136,
        )
    };
    assert_eq!(code, 22);
    assert_eq!(out, before);
    assert_eq!(count(0), 0);
}

#[test]
fn all_native_normal_outcomes_satisfy_the_carrier_phase_and_receipt_matrix() {
    for mode in 0..=14 {
        reset(mode);
        command(4, None);
        let mut out = HomeResult::initial();
        let _ = invoke(&mut out);
        assert!(out.valid(), "HOME_CANONICAL_RESULT: {mode}: {out:?}");
    }
}

fn validate_with_c(out: &HomeResult, protocol_expected: i32, order_expected: i32) {
    // SAFETY: the integer-only 320-byte carrier is fully initialized and has
    // no padding; copying its bytes retains an independent comparison snapshot.
    let before = unsafe { *core::ptr::from_ref(out).cast::<[u8; 320]>() };
    let mut protocol = 0;
    // SAFETY: actual Rust carrier is initialized, aligned and immutable; the
    // independently compiled C consumer borrows it only through this call.
    let order = unsafe { home_validate(out, &mut protocol) };
    assert_eq!(
        (protocol, order),
        (protocol_expected, order_expected),
        "HOME_RUST_C_CARRIER: {out:?}"
    );
    // SAFETY: same initialized live immutable carrier remains borrowed here.
    let after = unsafe { &*core::ptr::from_ref(out).cast::<[u8; 320]>() };
    assert_eq!(*after, before, "HOME_C_CONSUMER_PRESERVES_BYTES");
}
#[test]
fn actual_service_malformed_completion_retains_unknown_diagnostic() {
    reset(15);
    command(7, Some(b"broken"));
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 5);
    assert_eq!(
        (
            out.phase,
            out.mutation_attempts,
            out.service.ready,
            out.service.requests
        ),
        (0, 3, 1, 1)
    );
    assert_eq!(
        (
            out.service.stop,
            out.service.error,
            out.service.txg,
            out.service.bytes_staged,
            out.service.state
        ),
        (5, -5, 0, 0, 3),
        "HOME_SERVICE_UNKNOWN"
    );
    STATE.with(|s| {
        let s = s.borrow();
        let reply = (&s.output[128..192]).try_into().unwrap();
        assert_eq!(word(reply, 1) as i64, -5);
        assert_eq!(word(reply, 6), 3);
    });
    assert!(out.valid(), "HOME_SERVICE_UNKNOWN");
}
#[test]
fn actual_entry_bytes_are_consumed_by_the_c_carrier_validator() {
    // CALLBACK16 is trusted host fixture setup representing the already-entered
    // launch callback. The production entry and C consumer run unchanged.
    for (mode, loss, protocol, order) in [
        (0, false, 0, 1),
        (1, false, 0, 0),
        (5, false, 1, 1),
        (6, false, 1, 1),
        (0, true, 0, 1),
        (15, false, 0, 1),
    ] {
        reset(mode);
        if mode == 15 {
            command(7, Some(b"broken"));
        } else {
            command(4, None);
        }
        if loss {
            STATE.with(|s| s.borrow_mut().fail_after = Some(64));
        }
        let mut out = HomeResult::initial();
        out.flags = CALLBACK;
        let _ = invoke(&mut out);
        assert_ne!(out.flags & ENTRY, 0);
        validate_with_c(&out, protocol, order);
    }
}
#[test]
fn typed_lost_converter_bytes_are_consumed_by_c_without_a_native_lost_hook() {
    // The existing real bridge never returns typed Lost. This separate converter
    // fixture exercises that diagnostic layer and the actual C consumer only.
    let mut out = HomeResult::initial();
    out.flags = CALLBACK | ENTRY | ACCEPTED | CLOSE_ATTEMPTED | ORDERED;
    out.phase = 4;
    out.error_kind = 14;
    out.mutation_attempts = 1;
    let _ = retain(
        &mut out.mkdir,
        NamespaceObservation {
            result: Err(Error::Uncertain),
            provider: Some(Err(filesystem_bridge::policy::Lost)),
        },
    );
    validate_with_c(&out, 0, 1);
}
#[test]
fn carrier_rejects_impossible_loop_progress_and_accepts_only_failure_unknown() {
    reset(0);
    command(4, None);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 0);
    assert!(out.valid());
    for index in 0..7 {
        let mut bad = out;
        match index {
            0 => bad.service.ready = 0,
            1 => bad.mutation_attempts = 4,
            2 => bad.service.stop = 3,
            3 => bad.service.state = 99,
            4 => bad.service.bytes_staged = 4097,
            5 => bad.service.state = 3,
            _ => {
                bad.service.state = 3;
                bad.service.stop = 5;
                bad.service.error = 0;
            }
        };
        assert!(!bad.valid(), "HOME_LOOP_CARRIER_INVARIANTS: {index}");
    }
}

#[test]
fn rust_and_c_enforce_service_progress_states_without_erasing_committed_txg_zero() {
    reset(0);
    command(4, None);
    let mut base = HomeResult::initial();
    base.flags = CALLBACK;
    assert_eq!(invoke(&mut base), 0);
    for (state, txg, requests, attempts, stop, error) in [
        (0, 0, 1, 2, 0, 0),
        (1, 0, 1, 3, 5, -5),
        (1, 0, 1, 3, 2, -32),
        (2, 790, 2, 3, 0, 0),
    ] {
        let mut out = base;
        out.service.state = state;
        out.service.txg = txg;
        out.service.requests = requests;
        out.mutation_attempts = attempts;
        out.service.stop = stop;
        out.service.error = error;
        assert!(out.valid(), "HOME_SERVICE_PROGRESS_VALID: {out:?}");
        validate_with_c(&out, 0, 1);
    }
    for index in 0..8 {
        let mut out = base;
        match index {
            0 => out.service.txg = 1,
            1 => out.service.bytes_staged = 1,
            2 => out.service.state = 2,
            3 => {
                out.service.state = 1;
                out.service.error = -5;
            }
            4 => {
                out.service.state = 1;
                out.service.stop = 5;
            }
            5 => {
                out.service.state = 1;
                out.service.stop = 5;
                out.service.error = -5;
                out.service.ready = 0;
                out.service.requests = 0;
            }
            6 => {
                out.service.state = 2;
                out.service.txg = 790;
                out.service.ready = 0;
                out.service.requests = 0;
            }
            _ => {
                out.service.state = 2;
                out.service.txg = 790;
                out.service.requests = 0;
            }
        }
        assert!(
            !out.valid(),
            "HOME_SERVICE_PROGRESS_INVALID: {index}: {out:?}"
        );
        validate_with_c(&out, 1, 1);
    }
}

#[cfg(fs_home_probe_three)]
#[test]
fn selected_clock_accepts_only_the_half_open_window_before_first_effect() {
    for (seconds, allowed) in [
        (1791290039, false),
        (1791290040, true),
        (1791290099, true),
        (1791290100, false),
    ] {
        reset(0);
        command(4, None);
        // SAFETY: serial host fixture setter before entry owns any context.
        unsafe { home_clock(seconds, 999999999, 0) };
        let mut out = HomeResult::initial();
        let code = invoke(&mut out);
        if allowed {
            assert_eq!(code, 0, "HOME_CLOCK_WINDOW");
            assert_eq!(out.mutation_attempts, 2);
        } else {
            assert_eq!(
                (
                    code,
                    out.phase,
                    out.error_kind,
                    out.mutation_attempts,
                    out.mkdir.provider
                ),
                (5, 4, 11, 0, 0),
                "HOME_CLOCK_WINDOW"
            );
            assert_eq!(count(2), 0);
            STATE.with(|s| assert_eq!(s.borrow().published, 0));
        }
    }
}
#[cfg(fs_home_probe_three)]
#[test]
fn selected_clock_rechecks_second_bootstrap_readiness_and_request_mutation() {
    for (after, phase, attempts) in [(1, 6, 1), (2, 0, 2)] {
        reset(0);
        command(4, None);
        // SAFETY: serial typed host UTC; the existing provider attempt count
        // selects a later observation without a production clock counter.
        unsafe { home_clock(1791290100, 0, after) };
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 5, "HOME_CLOCK_RECHECK");
        assert_eq!(
            (out.phase, out.mutation_attempts),
            (phase, attempts),
            "HOME_CLOCK_RECHECK"
        );
        assert_ne!(out.flags & ORDERED, 0);
        STATE.with(|s| assert_eq!(s.borrow().published, 0));
        if after == 1 {
            assert_eq!((out.create.provider, out.create.error_kind), (0, 11));
        } else {
            assert_eq!((out.service.stop, out.service.error), (2, -5));
        }
    }
    reset(0);
    command(7, Some(b"late"));
    command(4, None);
    STATE.with(|s| s.borrow_mut().advance_clock_on_ready = true);
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 0);
    assert_eq!(
        (out.mutation_attempts, count(2), out.service.requests),
        (2, 2, 2),
        "HOME_CLOCK_REQUEST_BEFORE_EFFECT"
    );
    STATE.with(|s| {
        let s = s.borrow();
        assert_eq!(s.published, 1);
        let reply = (&s.output[128..192]).try_into().unwrap();
        assert_eq!(word(reply, 1) as i64, -5);
    });
}

#[cfg(fs_af09_drain)]
fn drain_requests() {
    command(1, Some(b"probe"));
    let mut close = message(READER, 3);
    put(&mut close, 3, 3);
    STATE.with(|s| s.borrow_mut().input.extend(close));
    command(4, None);
}

#[cfg(fs_af09_drain)]
#[test]
fn actual_disconnect_counts_are_once_before_ack_after_dispatch() {
    reset(0);
    drain_requests();
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 0);
    assert_eq!((out.mutation_attempts, out.service.requests), (2, 3));
    STATE.with(|s| {
        let s = s.borrow();
        assert_eq!(s.diagnostic.len(), 1, "AF09_DRAIN_COUNTER_ORDER");
        assert_eq!(s.diagnostic[0], ([1, 1, 2, 0, 3, 0, 0, 0], 256, 256));
        assert_eq!(s.output.len(), 320);
        assert_eq!(s.closes, [READER, WRITER]);
    });
}

#[cfg(fs_af09_drain)]
#[test]
fn actual_counter_values_are_not_fixed_success_literals() {
    for mutate in [false, true] {
        reset(0);
        if mutate {
            command(7, Some(b"x"));
        }
        command(4, None);
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 0);
        let (mutations, requests) = if mutate { (3, 2) } else { (2, 1) };
        assert_eq!(
            (out.mutation_attempts, out.service.requests),
            (mutations, requests)
        );
        STATE.with(|s| {
            let s = s.borrow();
            assert_eq!(s.diagnostic.len(), 1);
            assert_eq!(
                s.diagnostic[0].0,
                [1, 1, mutations as u8, 0, requests as u8, 0, 0, 0]
            );
        });
    }
}

#[cfg(fs_af09_drain)]
#[test]
fn counter_output_failure_never_sends_ack_and_attempts_both_closes() {
    for returned in [-28, -13, -110, 0, 1, 7, 9, i64::MAX] {
        reset(0);
        drain_requests();
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            s.diagnostic_return = Some(returned);
            s.close_errors = [-9, -13];
        });
        let mut out = HomeResult::initial();
        assert_eq!(invoke(&mut out), 5);
        assert_eq!(out.service.error, if returned < 0 { returned } else { -5 });
        assert_eq!(
            (out.service.reader_close, out.service.writer_close),
            (-9, -13)
        );
        STATE.with(|s| {
            let s = s.borrow();
            assert_eq!(s.diagnostic.len(), 1, "AF09_DRAIN_NO_ACK_RETRY");
            assert_eq!(
                (s.received, s.output.len()),
                (256, 256),
                "AF09_DRAIN_NO_ACK_RETRY"
            );
            assert_eq!(s.closes, [READER, WRITER]);
        });
    }
}

#[cfg(fs_af09_drain)]
#[test]
fn rejected_disconnect_has_no_counter_record() {
    reset(0);
    let mut invalid = message(READER, 4);
    invalid[24] = 1;
    STATE.with(|s| s.borrow_mut().input.extend(invalid));
    let mut out = HomeResult::initial();
    assert_eq!(invoke(&mut out), 5);
    STATE.with(|s| {
        let s = s.borrow();
        assert!(s.diagnostic.is_empty());
        assert_eq!(s.closes, [READER, WRITER]);
    });
}

#[cfg(fs_af09_drain)]
#[test]
fn endpoint_record_checks_u16_conversion_and_preserves_actual_bytes() {
    for (mutations, requests) in [(0, 0), (258, 772), (65535, 65535)] {
        reset(0);
        let mut endpoints = Endpoints {
            reader: READER,
            writer: WRITER,
            closed: false,
            flags: None,
        };
        assert_eq!(Io::af09_counts(&mut endpoints, mutations, requests), Ok(()));
        let m = (mutations as u16).to_le_bytes();
        let r = (requests as u16).to_le_bytes();
        STATE.with(|s| {
            assert_eq!(
                s.borrow().diagnostic[0].0,
                [1, 1, m[0], m[1], r[0], r[1], 0, 0]
            )
        });
        assert_eq!(endpoints.close(), [0, 0]);
    }
    for (mutations, requests) in [(65536, 0), (0, 65536), (u64::MAX, u64::MAX)] {
        reset(0);
        let mut endpoints = Endpoints {
            reader: READER,
            writer: WRITER,
            closed: false,
            flags: None,
        };
        assert_eq!(
            Io::af09_counts(&mut endpoints, mutations, requests),
            Err(-75)
        );
        STATE.with(|s| assert!(s.borrow().diagnostic.is_empty()));
        assert_eq!(endpoints.close(), [0, 0]);
    }
}
