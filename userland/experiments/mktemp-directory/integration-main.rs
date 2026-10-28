// SPDX-License-Identifier: BSD-2-Clause
//! Host-only real Toybox/Client/service/Zpl composition; no native launch claim.
use core::{
    ffi::{c_char, c_void},
    ptr, slice,
};
use mktemp_namespace::*;
use std::{cell::Cell, ffi::CString, io::Write};
#[path = "namespace-tests.rs"]
mod qualification;
use qualification::fixture::Actual;

#[repr(C)]
struct Timespec {
    seconds: i64,
    nanoseconds: i64,
}
type Applet = unsafe extern "C" fn(i32, *mut *mut c_char) -> i32;
#[repr(C)]
struct Observations {
    state: *mut c_void,
    monotonic: Option<unsafe extern "C" fn(*mut c_void, *mut Timespec) -> i32>,
    thread_identity: Option<unsafe extern "C" fn(*mut c_void) -> i64>,
    before_exit: Option<unsafe extern "C" fn(*mut c_void, *const Run, u32) -> i32>,
}
unsafe extern "C" {
    fn amk_target_run(
        bootstrap: *const Bootstrap,
        argc: i32,
        argv: *mut *mut c_char,
        envp: *mut *mut c_char,
        observations: *const Observations,
        applet: Option<Applet>,
        out: *mut Run,
    ) -> i32;
    fn amk_toybox_main(argc: i32, argv: *mut *mut c_char) -> i32;
    fn pthread_threadid_np(thread: *mut c_void, out: *mut u64) -> i32;
    fn _NSGetEnviron() -> *mut *mut *mut c_char;
    fn close(fd: i32) -> i32;
}
std::thread_local! { static IDENTITY: Cell<i64> = const { Cell::new(0) }; }
#[derive(Clone, Copy, PartialEq, Eq)]
enum Case {
    Success,
    Collision,
    OutputFailure,
    FinalizerFailure,
    InvalidClock,
}
impl Case {
    fn name(self) -> &'static str {
        match self {
            Self::Success => "success",
            Self::Collision => "collision",
            Self::OutputFailure => "output-failure",
            Self::FinalizerFailure => "finalizer-failure",
            Self::InvalidClock => "invalid-clock",
        }
    }
}
struct Observation {
    actual: Option<Actual>,
    case: Case,
    expected_path: String,
    environ_installed: bool,
    observed: bool,
}
unsafe extern "C" fn monotonic(state: *mut c_void, out: *mut Timespec) -> i32 {
    // SAFETY: live disjoint observation state, initialized output from C.
    let case = unsafe { (*state.cast::<Observation>()).case };
    unsafe {
        out.write(Timespec {
            seconds: 1,
            nanoseconds: if case == Case::InvalidClock {
                1_000_000_000
            } else {
                2
            },
        })
    };
    0
}
unsafe extern "C" fn identity(_state: *mut c_void) -> i64 {
    IDENTITY.with(Cell::get)
}
fn expected_leaf(identity: i64) -> Vec<u8> {
    // Independent collision setup from the retained musl naming formula. This
    // prepares a known existing victim; acceptance tests actual EEXIST/no replay,
    // not a second implementation's assertion of helper correctness.
    let mut seed = 3u64.wrapping_add((identity as u64).wrapping_mul(65537));
    let mut name = b"t.".to_vec();
    for _ in 0..6 {
        name.push((65 + (seed & 15) + (seed & 16) * 2) as u8);
        seed >>= 5;
    }
    name
}
unsafe extern "C" fn before_exit(state: *mut c_void, report: *const Run, status: u32) -> i32 {
    // SAFETY: C has consumed/disposed Client, completed ALL Wire callbacks and
    // cleared its TLS borrow before this HOST observer. Only now may the raw base
    // form an ancestor &mut Observation and take/move Actual/Wire for join. No
    // later Wire callback is permitted. Copy typed initialized scalar records;
    // never inspect padding, reenter, unwind or retain report.
    let observation = unsafe { &mut *state.cast::<Observation>() };
    if observation.observed || report.is_null() {
        return 1;
    }
    observation.observed = true;
    let report = unsafe { report.read() };
    let Some(actual) = observation.actual.take() else {
        return 1;
    };
    let baseline = actual.baseline_attempts;
    let namespace_closes = actual.wire.closes;
    let mkdir_headers = actual
        .wire
        .sent
        .iter()
        .filter(|frame| {
            &frame[..8] == filesystem_service::MAGIC && filesystem_service::word(frame, 1) == 10
        })
        .count();
    let joined = actual.try_finish();
    let (service, attempts, opens, closes) = match joined {
        Ok(value) => value,
        Err(()) => {
            let _ = writeln!(
                std::io::stderr(),
                "AMK_INTEGRATION {{\"case\":\"{}\",\"validated\":false,\"fixture_join_failed\":true}}",
                observation.case.name()
            );
            return 1;
        }
    };
    let delta = attempts.checked_sub(baseline);
    let common = observation.environ_installed
        && namespace_closes == 1
        && opens == closes
        && service.ready
        && service.cleanup == [0, 0]
        && report.phase == 3
        && report.reserved_zero == 0
        && report.admission.phase == 3
        && report.admission.endpoints_accepted == 1
        && report.finalization.phase == 1
        && report.finalization.cleanup_present == 1
        && status == report.final_status;
    let case_ok = match observation.case {
        Case::Success => {
            report.mutation.outcome == 3
                && report.mutation.progress == 2
                && report.mutation.txg > 0
                && report.mutation.errno_value == 0
                && (report.command_status, report.final_status) == (0, 0)
                && report.finalization.cleanup_uncertain == 0
                && delta == Some(1)
                && mkdir_headers == 1
                && service.stop == filesystem_service::Stop::Disconnected
        }
        Case::Collision => {
            (
                report.mutation.outcome,
                report.mutation.progress,
                report.mutation.errno_value,
            ) == (1, 0, 17)
                && report.command_status != 0
                && report.final_status != 0
                && report.finalization.disconnect_attempted == 0
                && delta == Some(1)
                && mkdir_headers == 1
        }
        Case::OutputFailure => {
            report.mutation.outcome == 3
                && report.mutation.progress == 2
                && report.mutation.txg > 0
                && report.command_status != 0
                && report.final_status != 0
                && delta == Some(1)
                && mkdir_headers == 1
        }
        Case::FinalizerFailure => {
            report.mutation.outcome == 3
                && report.mutation.progress == 2
                && (report.command_status, report.final_status) == (0, 1)
                && report.finalization.writer_close == -5
                && report.finalization.cleanup_uncertain == 1
                && delta == Some(1)
                && mkdir_headers == 1
        }
        Case::InvalidClock => {
            (report.mutation.outcome, report.mutation.progress) == (0, 4)
                && report.command_status != 0
                && report.final_status != 0
                && delta == Some(0)
                && mkdir_headers == 0
        }
    };
    let valid = common && case_ok;
    let result = writeln!(
        std::io::stderr(),
        concat!(
            "AMK_INTEGRATION {{\"case\":\"{}\",\"validated\":{},",
            "\"expected_path\":\"{}\",\"actual_C_environ_installed\":{},",
            "\"command_status\":{},\"final_status\":{},\"outcome\":{},\"progress\":{},\"txg\":{},\"mutation_errno\":{},",
            "\"provider_baseline_attempts\":{},\"provider_total_attempts\":{},\"candidate_attempt_delta\":{},",
            "\"mkdir_headers\":{},\"namespace_closes\":{},\"provider_opens\":{},\"provider_closes\":{},",
            "\"disconnect_attempted\":{},\"raw_reader_close\":{},\"raw_writer_close\":{},\"native\":false}}"
        ),
        observation.case.name(),
        valid,
        observation.expected_path,
        observation.environ_installed,
        report.command_status,
        report.final_status,
        report.mutation.outcome,
        report.mutation.progress,
        report.mutation.txg,
        report.mutation.errno_value,
        baseline,
        attempts,
        delta.map_or(-1, i64::from),
        mkdir_headers,
        namespace_closes,
        opens,
        closes,
        report.finalization.disconnect_attempted,
        report.finalization.reader_close,
        report.finalization.writer_close
    );
    i32::from(!valid || result.is_err())
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let case = match args.as_slice() {
        [_, name] => match name.as_str() {
            "success" => Case::Success,
            "collision" => Case::Collision,
            "output-failure" => Case::OutputFailure,
            "finalizer-failure" => Case::FinalizerFailure,
            "invalid-clock" => Case::InvalidClock,
            _ => std::process::exit(64),
        },
        _ => std::process::exit(64),
    };
    let mut id = 0u64;
    // SAFETY: Darwin host-only current-thread query, initialized scalar output.
    if unsafe { pthread_threadid_np(ptr::null_mut(), &mut id) } != 0
        || id == 0
        || id > i64::MAX as u64
    {
        std::process::exit(65);
    }
    IDENTITY.with(|slot| slot.set(id as i64));
    let leaf = expected_leaf(id as i64);
    let expected_path = match String::from_utf8([b"/home/".as_slice(), leaf.as_slice()].concat()) {
        Ok(path) => path,
        Err(_) => std::process::exit(65),
    };
    // Install the actual libc environment BEFORE starting the fixture thread.
    // This is an isolated host child, and every fixture thread agrees not to
    // read/mutate environ. Stable storage lives through terminal real _exit.
    let env = CString::new("LC_ALL=C").expect("constant has no NUL");
    let mut envp = [env.as_ptr().cast_mut(), ptr::null_mut()];
    let environment = unsafe { _NSGetEnviron() };
    if environment.is_null() {
        std::process::exit(65);
    }
    let previous = unsafe { environment.read() };
    unsafe { environment.write(envp.as_mut_ptr()) };
    let actual = Actual::start_named(if case == Case::Collision {
        Some(leaf)
    } else {
        None
    });
    let mut observation = Box::new(Observation {
        actual: Some(actual),
        case,
        expected_path,
        environ_installed: true,
        observed: false,
    });
    if case == Case::FinalizerFailure
        && let Some(actual) = observation.actual.as_mut()
    {
        actual.wire.close_values = [0, -5];
    }
    // Export one raw base AFTER all ordinary initialization. The allocation
    // deliberately lives until this isolated process exits; terminal _exit does
    // not run Rust Drop. No later Box/ancestor borrow may invalidate the derived
    // Wire callback pointer while Client can still call it.
    let observation = Box::into_raw(observation);
    // SAFETY: project only the actual field through the raw allocation base.
    // This short field borrow ends here, before C can invoke any callback.
    let mut bootstrap = unsafe {
        let actual = ptr::addr_of_mut!((*observation).actual);
        (*actual)
            .as_mut()
            .expect("present fixture")
            .wire
            .bootstrap()
    };
    bootstrap.parent_prefix = b"/home/".as_ptr();
    let observers = Observations {
        state: observation.cast(),
        monotonic: Some(monotonic),
        thread_identity: Some(identity),
        before_exit: Some(before_exit),
    };
    let mut argv0 = b"mktemp\0".to_vec();
    let mut option = b"-d\0".to_vec();
    let mut template = b"/home/t.XXXXXX\0".to_vec();
    let mut argv = [
        argv0.as_mut_ptr().cast(),
        option.as_mut_ptr().cast(),
        template.as_mut_ptr().cast(),
        ptr::null_mut(),
    ];
    let mut report = Run::default();
    if case == Case::OutputFailure {
        // Fault only this isolated host fixture's stdout, after setup. Real
        // upstream stdio/flush must observe the error; no output-success stub.
        if unsafe { close(1) } != 0 {
            std::process::exit(65);
        }
    }
    // SAFETY: boxed observation/actual callback state and disjoint arguments,
    // prefix and report stay stable; no Rust references span foreign execution.
    let returned = unsafe {
        amk_target_run(
            &bootstrap,
            3,
            argv.as_mut_ptr(),
            envp.as_mut_ptr(),
            &observers,
            Some(amk_toybox_main),
            &mut report,
        )
    };
    // Actual upstream applet normally terminal-exits. Unexpected return is a
    // failed closure, never accepted as a shortcut around callbacks/finalization.
    // Keep the raw Observation allocation alive on this failed-process exit path;
    // do not reconstruct/free it without proving no callback can remain retained.
    unsafe { environment.write(previous) };
    let _ = writeln!(
        std::io::stderr(),
        "AMK_INTEGRATION {{\"case\":\"{}\",\"validated\":false,\"unexpected_return\":{}}}",
        case.name(),
        returned
    );
    std::process::exit(1);
}
