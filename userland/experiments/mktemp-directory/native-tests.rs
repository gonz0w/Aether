// SPDX-License-Identifier: BSD-2-Clause
//! Actual selected adapter bodies; only raw kernel observations are substituted.
use super::*;
use std::{
    cell::RefCell,
    collections::VecDeque,
    sync::{Mutex, MutexGuard},
    vec::Vec,
};

const CAPS: [u64; 4] = [0xd10a0101, 0xd10b0102, 0xd1000101, 0xd1010102];
static SERIAL: Mutex<()> = Mutex::new(());
#[derive(Default)]
struct Fixture {
    now: i64,
    calls: Vec<(u64, [u64; 6])>,
    reads: VecDeque<i64>,
    writes: VecDeque<i64>,
    close_errors: [i64; 4],
    restore_error: i64,
    fatal: Option<&'static str>,
    terminal_returns: bool,
    process_bytes: VecDeque<u8>,
    request: Vec<u8>,
    streams: Option<fork_streams::State>,
    serial_results: VecDeque<i64>,
    delivered: Vec<(u32, Vec<u8>)>,
}
std::thread_local! { static FIXTURE: RefCell<Fixture> = RefCell::new(Fixture::default()); }

fn setup() -> MutexGuard<'static, ()> {
    let lock = SERIAL.lock().unwrap();
    // SAFETY: tests serialize the selected single-context storage. No callback
    // or borrowed Context/FD object exists at this reset boundary.
    unsafe {
        *STATE.budget.get() = Budget {
            left: TOTAL - RESERVE,
            deadline: 0,
            last: 0,
            clock: 0,
            initialized: false,
            error: 0,
        };
        *STATE.ledger.get() = Ledger {
            ends: [End::default(); 4],
            reserve: RESERVE,
            failed: false,
            terminal: false,
        };
        *STATE.transport.get() = Transport {
            reader: 0,
            writer: 0,
        };
    }
    STATE.admission.store(false, Ordering::Release);
    STATE.io_busy.store(false, Ordering::Release);
    STATE.finished.store(false, Ordering::Release);
    FIXTURE.with(|f| {
        *f.borrow_mut() = Fixture {
            now: 100,
            ..Fixture::default()
        }
    });
    lock
}
fn record() -> [u8; 64] {
    let mut bytes = [0; 64];
    bytes[..8].copy_from_slice(b"AENAP001");
    for (offset, value) in [
        (8, 64),
        (16, 0x3600000100000001),
        (24, CAPS[0]),
        (32, CAPS[1]),
        (40, CAPS[1] & !255 | 1),
    ] {
        bytes[offset..offset + 8].copy_from_slice(&value.to_le_bytes());
    }
    bytes[48..56].copy_from_slice(b"/home/\0\0");
    bytes
}
fn initialize(bytes: &[u8; 64]) -> (i64, Bootstrap) {
    let mut output = Bootstrap {
        io: Callbacks {
            state: ptr::null_mut(),
            transfer: None,
            wait: None,
            close: None,
        },
        epoch: 0,
        parent_prefix: ptr::null(),
        parent_prefix_length: 0,
    };
    let result = unsafe {
        amk_native_initialize(
            bytes.as_ptr(),
            RECORD,
            0x40000102,
            CAPS[2],
            CAPS[3],
            &mut output,
        )
    };
    (result, output)
}
fn accepted() -> Bootstrap {
    let (status, output) = initialize(&record());
    assert_eq!(status, 0, "NATIVE_ADMISSION");
    output
}
fn closes() -> Vec<u64> {
    FIXTURE.with(|f| {
        f.borrow()
            .calls
            .iter()
            .filter(|(op, _)| *op == 0x24003)
            .map(|(_, a)| a[0])
            .collect()
    })
}
pub fn raw(op: u64, args: [u64; 6]) -> i64 {
    if op == 0x100e7 {
        let fatal = FIXTURE.with(|f| f.borrow().fatal);
        if let Some(name) = fatal {
            fatal_oracle(name, args[0]);
            if FIXTURE.with(|f| f.borrow().terminal_returns) {
                return 0;
            }
            std::println!("AMK_FATAL_PASS {name}");
            std::process::exit(0);
        }
        return -5;
    }
    FIXTURE.with(|f| {
        let mut f = f.borrow_mut();
        f.calls.push((op, args));
        match op {
            0x28012 => f.now,
            0x24001 if args[0] == CAPS[2] && f.streams.is_some() => {
                let count = (args[2] as usize).min(f.process_bytes.len());
                if count == 0 {
                    return -11;
                }
                // SAFETY: actual C transport passed initialized exclusive read
                // output, <=16 bytes, valid throughout this synchronous leaf.
                let output = unsafe { core::slice::from_raw_parts_mut(args[1] as *mut u8, count) };
                for byte in output {
                    *byte = f.process_bytes.pop_front().unwrap();
                }
                count as i64
            }
            0x24002 if args[0] == CAPS[3] && f.streams.is_some() => {
                // SAFETY: actual C transport lends a stable initialized write
                // input, <=16 bytes, until this synchronous raw leaf returns.
                let input =
                    unsafe { core::slice::from_raw_parts(args[1] as *const u8, args[2] as usize) };
                f.request.extend_from_slice(input);
                if f.request.len() == 32 {
                    let frame: [u8; 32] = f.request.as_slice().try_into().unwrap();
                    f.request.clear();
                    let selector = u32::from_le_bytes(frame[8..12].try_into().unwrap());
                    let serial = if u32::from_le_bytes(frame[..4].try_into().unwrap()) == 2 {
                        f.serial_results.pop_front()
                    } else {
                        None
                    };
                    let mut state = f.streams.take().unwrap();
                    let result =
                        state.request(fork_streams::Caller::Parent, &frame, |writing, bytes| {
                            assert!(writing, "STDIO_NO_STDIN");
                            let count = serial.unwrap_or(bytes.len() as i64);
                            if count > 0 && count as usize <= bytes.len() {
                                f.delivered
                                    .push((selector, bytes[..count as usize].to_vec()));
                            }
                            count
                        });
                    f.streams = Some(state);
                    match result {
                        fork_streams::Outcome::Reply(bytes) => f.process_bytes.extend(bytes),
                        fork_streams::Outcome::Pending => {
                            panic!("stdio fixture has no Pending selection")
                        }
                    }
                }
                args[2] as i64
            }
            0x24001 => f.reads.pop_front().unwrap_or(-11),
            0x24002 => f.writes.pop_front().unwrap_or(args[2] as i64),
            0x24003 => CAPS
                .iter()
                .position(|cap| *cap == args[0])
                .map_or(-13, |i| f.close_errors[i]),
            0x1000e if args[0] == 2 => f.restore_error,
            0x1000e => 0,
            0x10027 => 9,
            0x1006e => 7,
            0x1fffe => 0,
            _ => -38,
        }
    })
}

#[test]
fn invalid_bootstrap_never_accepts_or_closes_labels() {
    let _serial = setup();
    let original = record();
    for index in [0, 8, 16, 24, 32, 40, 48, 56] {
        let mut bytes = original;
        bytes[index] ^= 1;
        assert_eq!(initialize(&bytes).0, -22, "NATIVE_BOOTSTRAP_NO_EFFECT");
        assert!(!STATE.admission.load(Ordering::Acquire));
    }
    assert!(FIXTURE.with(|f| f.borrow().calls.is_empty()));
    assert!(closes().is_empty());
}
#[test]
fn admission_uses_actual_clock_and_caches_all_four_close_results() {
    let _serial = setup();
    let bootstrap = accepted();
    assert_eq!(bootstrap.epoch, CAPS[1] & !255 | 1);
    assert_eq!(bootstrap.parent_prefix_length, 6);
    assert_eq!(
        unsafe { core::slice::from_raw_parts(bootstrap.parent_prefix, 6) },
        b"/home/"
    );
    assert_eq!(unsafe { (*STATE.budget.get()).deadline }, 5_000_000_100);
    FIXTURE.with(|f| f.borrow_mut().close_errors = [-5, 0, -9, -32]);
    let mut first = Receipt::default();
    assert_eq!(unsafe { amk_native_finish_raw(&mut first) }, -5);
    let mut second = Receipt::default();
    assert_eq!(unsafe { amk_native_finish_raw(&mut second) }, -5);
    assert_eq!(first.status, [-5, 0, -9, -32]);
    assert_eq!(first.status, second.status);
    assert_eq!(first.attempted, 15);
    assert_eq!(closes(), CAPS, "NATIVE_CLOSE_ONCE");
    assert_eq!(unsafe { (*STATE.ledger.get()).reserve }, 1);
}
#[test]
fn clock_failure_after_admission_still_owns_cleanup() {
    let _serial = setup();
    FIXTURE.with(|f| f.borrow_mut().now = -38);
    assert_eq!(initialize(&record()).0, -38);
    let mut receipt = Receipt::default();
    assert_eq!(unsafe { amk_native_finish_raw(&mut receipt) }, -38);
    assert_eq!(receipt.owned, 15);
    assert_eq!(closes(), CAPS);
}
#[test]
fn continuous_progress_expires_one_absolute_deadline() {
    let _serial = setup();
    let bootstrap = accepted();
    let mut bytes = [0u8; 1];
    let transfer = bootstrap.io.transfer.unwrap();
    assert_eq!(
        unsafe { transfer(bootstrap.io.state, 1, bytes.as_mut_ptr(), 1) },
        1
    );
    FIXTURE.with(|f| f.borrow_mut().now = 5_000_000_100);
    assert_eq!(
        unsafe { transfer(bootstrap.io.state, 1, bytes.as_mut_ptr(), 1) },
        -110,
        "NATIVE_FIXED_DEADLINE"
    );
    assert_eq!(unsafe { (*STATE.budget.get()).deadline }, 5_000_000_100);
    assert_eq!(
        FIXTURE.with(|f| f
            .borrow()
            .calls
            .iter()
            .filter(|(op, _)| *op == 0x24002)
            .count()),
        1
    );
    let mut receipt = Receipt::default();
    assert_eq!(unsafe { amk_native_finish_raw(&mut receipt) }, -110);
    assert_eq!(closes(), CAPS);
}
#[test]
fn clock_regression_fails_without_renewal() {
    let _serial = setup();
    let _bootstrap = accepted();
    FIXTURE.with(|f| f.borrow_mut().now = 99);
    assert_eq!(amk_native_clock(), -5, "NATIVE_CLOCK_REGRESSION");
    assert_eq!(amk_native_clock(), -5);
}
#[test]
fn admission_clock_overflow_preserves_owned_cleanup() {
    let _serial = setup();
    FIXTURE.with(|f| f.borrow_mut().now = i64::MAX - 1);
    assert_eq!(initialize(&record()).0, -75, "NATIVE_CLOCK_OVERFLOW");
    let mut receipt = Receipt::default();
    assert_eq!(unsafe { amk_native_finish_raw(&mut receipt) }, -75);
    assert_eq!(closes(), CAPS);
}
#[test]
fn namespace_and_stdio_spend_the_same_selected_budget() {
    let _serial = setup();
    let bootstrap = accepted();
    let before = unsafe { (*STATE.budget.get()).left };
    let mut byte = [0u8];
    assert_eq!(
        unsafe { bootstrap.io.transfer.unwrap()(bootstrap.io.state, 1, byte.as_mut_ptr(), 1) },
        1
    );
    assert_eq!(amk_native_call(ptr::null_mut(), 0x10027, 0, 0, 0, 0), 9);
    assert_eq!(
        unsafe { (*STATE.budget.get()).left },
        before - 4,
        "NATIVE_SHARED_BUDGET"
    );
}
#[test]
fn native_wait_yields_without_fabricating_eof() {
    let _serial = setup();
    let bootstrap = accepted();
    assert_eq!(
        unsafe { bootstrap.io.wait.unwrap()(bootstrap.io.state, 0) },
        0
    );
    assert!(FIXTURE.with(|f| f.borrow().calls.iter().any(|(op, _)| *op == 0x1fffe)));
    assert!(!FIXTURE.with(|f| f.borrow().calls.iter().any(|(op, _)| *op == 0x24004)));
    FIXTURE.with(|f| {
        f.borrow_mut().reads.push_back(-5);
    });
    assert_eq!(
        unsafe { amk_native_verify(bootstrap.io.state) },
        -5,
        "NATIVE_REAL_EOF_EPIPE"
    );
}
#[test]
fn actual_eof_then_epipe_required_under_shared_bounds() {
    let _serial = setup();
    let bootstrap = accepted();
    FIXTURE.with(|f| {
        let mut f = f.borrow_mut();
        f.reads.extend([-11, 0]);
        f.writes.extend([-11, -32]);
    });
    assert_eq!(
        unsafe { amk_native_verify(bootstrap.io.state) },
        0,
        "NATIVE_REAL_EOF_EPIPE"
    );
    let operations = FIXTURE.with(|f| {
        f.borrow()
            .calls
            .iter()
            .filter(|(op, _)| matches!(op, 0x24001 | 0x24002))
            .map(|(op, _)| *op)
            .collect::<Vec<_>>()
    });
    assert_eq!(operations, [0x24001, 0x24001, 0x24002, 0x24002]);
}
#[test]
fn descriptor_call_rejects_foreign_caps_and_unknown_operations_before_effects() {
    let _serial = setup();
    let _bootstrap = accepted();
    let before = FIXTURE.with(|f| f.borrow().calls.len());
    assert_eq!(
        amk_native_call(ptr::null_mut(), 0x24003, 0xdead, 0, 0, 0),
        -13
    );
    assert_eq!(
        amk_native_call(ptr::null_mut(), 0x24001, CAPS[0], 0, 1, 0),
        -13
    );
    assert_eq!(
        amk_native_call(ptr::null_mut(), 0x24002, CAPS[1], 0, 1, 0),
        -13
    );
    assert_eq!(amk_native_call(ptr::null_mut(), 0x26000, 0, 0, 0, 0), -38);
    assert_eq!(
        FIXTURE.with(|f| f.borrow().calls.len()),
        before,
        "NATIVE_CAP_SCOPE"
    );
}
#[test]
fn output_after_raw_finish_has_no_trap() {
    let _serial = setup();
    let bootstrap = accepted();
    let mut receipt = Receipt::default();
    assert_eq!(unsafe { amk_native_finish_raw(&mut receipt) }, 0);
    let before = FIXTURE.with(|f| f.borrow().calls.len());
    let mut byte = [0u8];
    assert_eq!(
        unsafe { bootstrap.io.transfer.unwrap()(bootstrap.io.state, 1, byte.as_mut_ptr(), 1) },
        -9
    );
    assert_eq!(
        FIXTURE.with(|f| f.borrow().calls.len()),
        before,
        "NATIVE_FINISHED_NO_IO"
    );
}

fn fatal_check(condition: bool, marker: &str) {
    if !condition {
        std::eprintln!("AMK_FATAL_ASSERT {marker}");
        std::process::exit(79);
    }
}
fn fatal_oracle(name: &str, status: u64) {
    fatal_check(status == 125, "STATUS125");
    let observed = closes();
    fatal_check(
        observed.len() == 4
            && CAPS
                .iter()
                .all(|cap| observed.iter().filter(|v| *v == cap).count() == 1),
        "FOUR_DISTINCT_CLOSES",
    );
    let ledger = unsafe { *STATE.ledger.get() };
    fatal_check(
        ledger.reserve == 0 && ledger.terminal && ledger.failed,
        "EXACT_FIVE_RESERVE",
    );
    fatal_check(
        ledger.ends.iter().all(|end| end.attempted),
        "NO_LOST_RECEIPT",
    );
    FIXTURE.with(|f| {
        let f = f.borrow();
        fatal_check(
            ledger
                .ends
                .iter()
                .enumerate()
                .all(|(i, end)| end.result == f.close_errors[i]),
            "CLOSE_ERRORS_RETAINED",
        );
    });
    if name.contains("deadline") || name.contains("budget") {
        let calls = FIXTURE.with(|f| f.borrow().calls.clone());
        let first_close = calls.iter().position(|(op, _)| *op == 0x24003).unwrap();
        fatal_check(
            calls[first_close..].iter().all(|(op, _)| *op == 0x24003),
            "NO_POST_EXPIRY_FORWARD_CALL",
        );
    }
}
pub fn fault() -> ! {
    if let Some(name) = FIXTURE.with(|f| f.borrow().fatal) {
        let attempted = closes();
        fatal_check(
            !attempted
                .iter()
                .any(|cap| attempted.iter().filter(|v| *v == cap).count() > 1),
            "PRIOR_CLOSE_REPLAY",
        );
        fatal_check(
            FIXTURE.with(|f| f.borrow().terminal_returns),
            "UNEXPECTED_FAULT",
        );
        fatal_oracle(name, 125);
        std::println!("AMK_FATAL_PASS {name}");
        std::process::exit(0);
    }
    std::process::abort()
}
#[unsafe(no_mangle)]
extern "C" fn amk_test_before_leave(kind: u32) {
    match kind {
        0 => unsafe {
            (*STATE.budget.get()).left = 0;
        },
        1 => FIXTURE.with(|f| f.borrow_mut().now = 5_000_000_100),
        _ => FIXTURE.with(|f| f.borrow_mut().restore_error = -5),
    }
}
unsafe extern "C" {
    fn amk_test_actual_fd_leave(kind: u32);
}
unsafe extern "C" {
    fn amk_native_test_reset();
    fn amk_native_fd_start(memory: u64, input: u64, output: u64) -> i64;
    fn amk_native_test_finish() -> i32;
    fn amk_test_actual_stdio_case(kind: u32) -> i32;
}
fn start_stdio() {
    let identity = abi29_dispatch_core::startup::Identity::admitted(1, 1, 0xb0000102).unwrap();
    let console = [
        None,
        Some(fd_startup::Source {
            reference: 0x7a010001,
            selector: 1,
            rights: 2,
            bound: 16,
        }),
        Some(fd_startup::Source {
            reference: 0x7a020001,
            selector: 2,
            rights: 2,
            bound: 16,
        }),
    ];
    let mut plan = fd_startup::Plan {
        identity,
        shell: 1,
        parent: 7,
        generation: 1,
        bindings: [fd_startup::Binding::default(); 16],
        sources: [fd_startup::Source::default(); 7],
        history: [0; 2],
    };
    for fd in [1, 2] {
        plan.bindings[fd] = fd_startup::Binding {
            kind: 1,
            selector: fd as u8,
            cloexec: 0,
        };
        plan.sources[fd] = console[fd].unwrap();
    }
    let mut greeting = [0u8; fd_startup::BYTES];
    fd_startup::encode(&plan, &mut greeting).unwrap();
    FIXTURE.with(|f| {
        let mut f = f.borrow_mut();
        f.process_bytes.extend(greeting);
        f.streams = Some(
            fork_streams::State::new(
                console,
                [
                    fork_streams::SessionPipe::new(),
                    fork_streams::SessionPipe::new(),
                ],
            )
            .unwrap(),
        );
    });
    // SAFETY: no foreign borrow is live before this test-only reset; the prior
    // test finalized any admitted context. Actual C startup consumes this exact
    // Rust-produced record through the selected raw callback.
    unsafe {
        amk_native_test_reset();
    }
    assert_eq!(
        unsafe { amk_native_fd_start(identity.memory, CAPS[2], CAPS[3]) },
        0,
        "STDIO_MATCHED_304_STARTUP"
    );
}
#[test]
fn actual_stdio_partial_vectors_route_fd1_and_fd2() {
    let _serial = setup();
    let _bootstrap = accepted();
    start_stdio();
    FIXTURE.with(|f| f.borrow_mut().serial_results.push_back(7));
    assert_eq!(
        unsafe { amk_test_actual_stdio_case(0) },
        0,
        "STDIO_PARTIAL_VECTORS"
    );
    assert_eq!(
        unsafe { amk_test_actual_stdio_case(1) },
        0,
        "STDIO_DISTINCT_STDERR"
    );
    FIXTURE.with(|f| {
        let f = f.borrow();
        for selector in [1, 2] {
            let bytes = f
                .delivered
                .iter()
                .filter(|(source, _)| *source == selector)
                .flat_map(|(_, bytes)| bytes.clone())
                .collect::<Vec<_>>();
            assert_eq!(bytes, b"abc0123456789ABCDEFGHIJ", "STDIO_CONFIRMED_PREFIX");
        }
    });
    assert_eq!(unsafe { amk_native_test_finish() }, 0);
}
#[test]
fn actual_stdio_zero_progress_sets_f_err_and_errno() {
    let _serial = setup();
    let _bootstrap = accepted();
    start_stdio();
    FIXTURE.with(|f| f.borrow_mut().serial_results.push_back(0));
    assert_eq!(
        unsafe { amk_test_actual_stdio_case(4) },
        0,
        "STDIO_ZERO_REJECT"
    );
    FIXTURE.with(|f| f.borrow_mut().serial_results.push_back(0));
    assert_eq!(
        unsafe { amk_test_actual_stdio_case(2) },
        0,
        "STDIO_ZERO_F_ERR"
    );
    assert!(FIXTURE.with(|f| f.borrow().delivered.is_empty()));
    assert_eq!(unsafe { amk_native_test_finish() }, 0);
}
#[test]
fn actual_stdio_partial_error_keeps_progress_and_stderr_error() {
    let _serial = setup();
    let _bootstrap = accepted();
    start_stdio();
    FIXTURE.with(|f| f.borrow_mut().serial_results.extend([7, -32]));
    assert_eq!(
        unsafe { amk_test_actual_stdio_case(3) },
        0,
        "STDIO_PARTIAL_F_ERR"
    );
    let bytes = FIXTURE.with(|f| {
        f.borrow()
            .delivered
            .iter()
            .flat_map(|(_, bytes)| bytes.clone())
            .collect::<Vec<_>>()
    });
    assert_eq!(bytes, b"abc0123");
    assert_eq!(unsafe { amk_native_test_finish() }, 0);
}
fn leave_case(name: &'static str, kind: u32, errors: [i64; 4], prior: bool, returns: bool) {
    let _serial = setup();
    let _bootstrap = accepted();
    FIXTURE.with(|f| {
        let mut f = f.borrow_mut();
        f.fatal = Some(name);
        f.close_errors = errors;
        f.terminal_returns = returns;
    });
    if prior {
        assert_eq!(close_raw(CAPS[0]), errors[0]);
        assert_eq!(close_raw(CAPS[2]), errors[2]);
    }
    unsafe {
        amk_test_actual_fd_leave(kind);
    }
    fatal_check(false, "FATAL_PATH_RETURNED");
}
// These cases terminate their containing host process. The reviewed runner must
// dispatch each exact case alone and require its semantic marker plus EXIT0.
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_expired_budget_closes_live_namespace() {
    leave_case(
        "fd_leave_expired_budget_closes_live_namespace",
        0,
        [0; 4],
        false,
        false,
    );
}
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_expired_deadline_closes_live_namespace() {
    leave_case(
        "fd_leave_expired_deadline_closes_live_namespace",
        1,
        [0; 4],
        false,
        false,
    );
}
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_kernel_restore_error_closes_both_pairs() {
    leave_case(
        "fd_leave_kernel_restore_error_closes_both_pairs",
        2,
        [0; 4],
        false,
        false,
    );
}
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_process_input_close_error_preserved_without_retry() {
    leave_case(
        "fd_leave_process_input_close_error_preserved_without_retry",
        2,
        [0, 0, -5, 0],
        false,
        false,
    );
}
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_process_output_close_error_preserved_without_retry() {
    leave_case(
        "fd_leave_process_output_close_error_preserved_without_retry",
        2,
        [0, 0, 0, -9],
        false,
        false,
    );
}
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_exact_five_reserve_and_prior_closes() {
    leave_case(
        "fd_leave_exact_five_reserve_and_prior_closes",
        2,
        [-5, -32, -9, -13],
        true,
        false,
    );
}
#[test]
#[ignore = "isolated terminating host case"]
fn fd_leave_terminal_return_faults_without_reentry() {
    leave_case(
        "fd_leave_terminal_return_faults_without_reentry",
        2,
        [0; 4],
        false,
        true,
    );
}
