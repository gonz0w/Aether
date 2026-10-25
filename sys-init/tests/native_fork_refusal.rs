// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity};
use fixture::{Fault, Harness};
use fork_gate::{GateError, Owner, Phase};
use fork_streams::{SessionPipe, State};
use std::panic::{AssertUnwindSafe, catch_unwind};
fn native(slot: u32) -> NativeIdentity {
    NativeIdentity::admitted(slot, 1, 0xb0000100 | (slot as u64 + 1)).unwrap()
}
#[test]
fn native_refusal_preserves_supervisor_result_and_original_errno_without_replay() {
    for raw in [Ok(0), Ok(-11), Ok(1), Err(-32), Err(-11)] {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let mut files = h.fds.take().unwrap();
        let parent = files.admitted_shell(native(1), 7).unwrap();
        let streams = State::new([None; 3], [SessionPipe::new(), SessionPipe::new()]).unwrap();
        let mut owner = Owner::new(files, streams);
        let mut calls = 0;
        assert_eq!(
            owner.resolve_native_refusal(7, -12, |_| {
                calls += 1;
                raw
            }),
            Err(GateError::Mismatch)
        );
        let plan = Plan {
            identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
            shell: 1,
            parent: 7,
            generation: 77,
            bindings: [Binding::default(); 16],
            sources: [Source::default(); 7],
            history: [0; 2],
        };
        owner.begin(7, |_, _| ()).unwrap();
        assert!(
            owner
                .copy(7, parent, native(2), 9, &plan, |_| CopyAttempt::Refused(
                    -12
                ))
                .unwrap()
                .is_err()
        );
        assert_eq!(
            owner.resolve_native_refusal(8, -12, |_| {
                calls += 1;
                raw
            }),
            Err(GateError::Mismatch)
        );
        assert_eq!(calls, 0);
        assert_eq!(
            owner.resolve_native_refusal(7, -12, |_| {
                calls += 1;
                raw
            }),
            Ok(raw)
        );
        assert_eq!(calls, 1);
        assert_eq!(
            owner.resolve_native_refusal(7, -12, |_| {
                calls += 1;
                raw
            }),
            Err(GateError::Mismatch)
        );
        assert_eq!(calls, 1);
        if raw == Ok(0) {
            assert_eq!(owner.phase(), Phase::RefusalSettled { error: -12 });
            assert_eq!(owner.cleanup(), None);
            assert_eq!(owner.refusal_delivered(7, -11), Err(GateError::Mismatch));
            owner.refusal_delivered(7, -12).unwrap();
            assert_eq!(owner.phase(), Phase::Idle);
            owner
                .admit(|files, _| assert_eq!(files.current(native(1)), Ok(parent)))
                .unwrap();
        } else {
            assert_eq!(owner.phase(), Phase::Retired);
            assert_eq!(owner.cleanup(), Some([-9, -5]));
            assert_eq!(owner.admit(|_, _| ()), Err(GateError::Closed));
        }
        owner.retire();
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut files = h.fds.take().unwrap();
    let parent = files.admitted_shell(native(1), 7).unwrap();
    let mut owner = Owner::new(
        files,
        State::new([None; 3], [SessionPipe::new(), SessionPipe::new()]).unwrap(),
    );
    let plan = Plan {
        identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
        shell: 1,
        parent: 7,
        generation: 77,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [0; 2],
    };
    owner.begin(7, |_, _| ()).unwrap();
    assert!(
        owner
            .copy(7, parent, native(2), 9, &plan, |_| CopyAttempt::Refused(
                -12
            ))
            .unwrap()
            .is_err()
    );
    assert!(
        catch_unwind(AssertUnwindSafe(|| {
            let _ = owner.resolve_native_refusal(7, -12, |_| panic!("unknown cancellation"));
        }))
        .is_err()
    );
    assert_eq!(owner.phase(), Phase::Resolving);
    assert_eq!(owner.admit(|_, _| ()), Err(GateError::Closed));
    owner.retire();
    drop(owner);
}
