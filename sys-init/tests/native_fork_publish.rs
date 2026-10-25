// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use af07_transport::Kernel;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity, Process};
use fixture::{Fault, Harness, Pipe};
use fork_gate::{GateError, Owner, Phase};
use fork_streams::{SessionPipe, State};
use fork_transport::{Publication, PublishError};
use std::panic::{AssertUnwindSafe, catch_unwind};

fn native(slot: u32) -> NativeIdentity {
    NativeIdentity::admitted(slot, 1, 0xb0000100 | (slot as u64 + 1)).unwrap()
}
fn prepared() -> (Harness, Owner<Pipe, State>, Plan, Process) {
    let mut harness = Harness::new(Fault::None, [-9, -5]);
    let mut files = harness.fds.take().unwrap();
    let parent = files.admitted_shell(native(1), 7).unwrap();
    assert_eq!(
        files.open_read(parent, b"file", true),
        Ok(filesystem_remote_descriptors::FIRST_FILE_FD)
    );
    let mut plan = Plan {
        identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
        shell: 1,
        parent: 7,
        generation: 1,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [0; 2],
    };
    plan.bindings[15] = Binding {
        kind: 3,
        selector: filesystem_remote_descriptors::FIRST_FILE_FD as u8,
        cloexec: 1,
    };
    let state = State::new([None; 3], [SessionPipe::new(), SessionPipe::new()]).unwrap();
    let mut owner = Owner::new(files, state);
    owner.begin(7, |_, _| ()).unwrap();
    (harness, owner, plan, parent)
}
fn bound(stage_second: bool) -> (Harness, Owner<Pipe, State>, Plan, Process) {
    let (harness, mut owner, mut plan, parent) = prepared();
    let child = owner
        .copy(7, parent, native(2), 9, &plan, |streams| {
            for object in 0..if stage_second { 2 } else { 1 } {
                streams
                    .pipe_mut(object)
                    .unwrap()
                    .stage_participant(1, 1, [false; 2])
                    .unwrap();
            }
            CopyAttempt::Copied {
                identity: native(2),
                parent_pid: 9,
            }
        })
        .unwrap()
        .unwrap();
    plan.identity = Identity::admitted(2, 1, 0xb0000103).unwrap();
    plan.parent = 9;
    // Fresh child channel generation assigned by this fixture's trusted owner.
    plan.generation = 2;
    (harness, owner, plan, child)
}
fn request(plan: &Plan) -> Publication<'_> {
    Publication {
        sequence: 7,
        startup: plan,
        child_writer: 71,
        child_reader: 72,
        parent_writer: 73,
    }
}
struct Wire {
    startup: Vec<u8>,
    parent: Vec<u8>,
    ready: [u8; 32],
    read: usize,
    stop: Option<(u64, usize)>,
    panic_at: Option<(u64, usize)>,
    error: i64,
    wait: i64,
    eagain: bool,
    calls: usize,
    waits: usize,
    refused: bool,
}
impl Wire {
    fn new() -> Self {
        let mut ready = [0; 32];
        ready[..8].copy_from_slice(b"AEFKC001");
        ready[8..16].copy_from_slice(&7u64.to_le_bytes());
        ready[16..24].copy_from_slice(&10u64.to_le_bytes());
        Self {
            startup: Vec::new(),
            parent: Vec::new(),
            ready,
            read: 0,
            stop: None,
            panic_at: None,
            error: 0,
            wait: 0,
            eagain: false,
            calls: 0,
            waits: 0,
            refused: false,
        }
    }
}
impl Kernel for Wire {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        assert!(!bytes.is_empty() && bytes.len() <= 16);
        let position = match (endpoint, writing) {
            (71, true) => {
                assert!(self.parent.is_empty());
                self.startup.len()
            }
            (72, false) => {
                assert_eq!(self.startup.len(), 304);
                assert!(self.parent.is_empty());
                self.read
            }
            (73, true) => {
                assert_eq!(self.read, if self.refused { 0 } else { 32 });
                if self.refused {
                    assert!(self.startup.is_empty());
                }
                self.parent.len()
            }
            _ => panic!("wrong endpoint direction"),
        };
        assert_ne!(
            self.panic_at,
            Some((endpoint, position)),
            "transport unwind"
        );
        self.calls += 1;
        if self.eagain && self.calls % 2 == 1 {
            return -11;
        }
        if self.stop == Some((endpoint, position)) {
            return self.error;
        }
        let mut n = bytes.len().min(7);
        if let Some((ep, at)) = self.stop
            && ep == endpoint
        {
            n = n.min(at - position);
        }
        if writing {
            if endpoint == 71 {
                self.startup.extend_from_slice(&bytes[..n]);
            } else {
                self.parent.extend_from_slice(&bytes[..n]);
            }
        } else {
            bytes[..n].copy_from_slice(&self.ready[position..position + n]);
            self.read += n;
        }
        n as i64
    }
    fn wait(&mut self, endpoint: u64) -> i64 {
        assert!((71..=73).contains(&endpoint));
        self.waits += 1;
        self.wait
    }
    fn close(&mut self, _: u64) -> i64 {
        panic!("publication must not close native endpoints")
    }
}

#[test]
fn short_eagain_startup_ready_parent_delivery_then_shared_file_continuation() {
    let (h, mut owner, plan, child) = bound(true);
    let mut wire = Wire::new();
    wire.eagain = true;
    let mut scratch = [0xa5; 304];
    let mut budget = 1000;
    assert_eq!(
        fork_transport::publish(
            &mut owner,
            &mut wire,
            request(&plan),
            &mut budget,
            &mut scratch
        ),
        Ok(())
    );
    assert_eq!(owner.phase(), Phase::Idle);
    assert_eq!(owner.cleanup(), None);
    assert!(wire.waits > 0);
    let mut expected = [0; 304];
    fd_startup::encode(&plan, &mut expected).unwrap();
    assert_eq!(wire.startup, expected);
    assert_eq!(wire.parent, fork_frames::disposition(7, 10).unwrap());
    assert_eq!(scratch, [0; 304]);
    owner
        .admit(|files, _| {
            let parent = files.current(native(1)).unwrap();
            let mut data = [0; 4096];
            assert_eq!(
                files.read(
                    parent,
                    filesystem_remote_descriptors::FIRST_FILE_FD,
                    2,
                    &mut data
                ),
                Ok(2)
            );
            assert_eq!(&data[..2], b"ab");
            assert_eq!(
                files.read(
                    child,
                    filesystem_remote_descriptors::FIRST_FILE_FD,
                    2,
                    &mut data
                ),
                Ok(2)
            );
            assert_eq!(&data[..2], b"cd");
            assert_eq!(
                files.file_view_v1(child),
                Ok((
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                ))
            );
        })
        .unwrap();
    owner.retire();
    drop(owner);
    assert_eq!(h.local.lock().unwrap().closes, 1);
}

#[test]
fn every_incomplete_delivery_retires_without_negative_reply_or_native_close() {
    for (endpoint, length) in [(71, 304), (72, 32), (73, 32)] {
        for prefix in 0..length {
            let (h, mut owner, plan, _) = bound(true);
            let mut wire = Wire::new();
            wire.stop = Some((endpoint, prefix));
            let mut scratch = [0xa5; 304];
            assert_eq!(
                fork_transport::publish(
                    &mut owner,
                    &mut wire,
                    request(&plan),
                    &mut 1000,
                    &mut scratch
                ),
                Err(PublishError::Transport(-5))
            );
            assert_eq!(owner.phase(), Phase::Retired);
            assert_eq!(owner.cleanup(), Some([-9, -5]));
            assert_eq!(owner.admit(|_, _| ()), Err(GateError::Closed));
            assert_eq!(scratch, [0; 304]);
            if endpoint != 73 {
                assert!(wire.parent.is_empty());
            } else {
                assert_eq!(
                    wire.parent,
                    fork_frames::disposition(7, 10).unwrap()[..prefix]
                );
            }
            drop(owner);
            assert_eq!(h.local.lock().unwrap().closes, 1);
        }
    }
}

#[test]
fn stale_ready_and_activation_failure_never_publish_parent_success() {
    for corrupt in [0, 8, 16, 24, 31, 32] {
        let (h, mut owner, plan, _) = bound(corrupt != 32);
        let mut wire = Wire::new();
        if corrupt < 32 {
            wire.ready[corrupt] ^= 1;
        }
        let mut scratch = [0xa5; 304];
        let result = fork_transport::publish(
            &mut owner,
            &mut wire,
            request(&plan),
            &mut 1000,
            &mut scratch,
        );
        assert!(
            result.is_err(),
            "malformed ready or failed activation must not publish success"
        );
        let error = result.unwrap_err();
        if corrupt == 32 {
            assert!(matches!(
                error,
                PublishError::Activation(GateError::Streams(-9))
            ));
        } else {
            assert_eq!(error, PublishError::Ready);
        }
        assert!(wire.parent.is_empty());
        assert_eq!(owner.phase(), Phase::Retired);
        assert_eq!(scratch, [0; 304]);
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}

#[test]
fn wrong_admission_and_routes_do_not_perform_transport() {
    for case in 0..13 {
        let (h, mut owner, mut plan, _) = bound(true);
        match case {
            9 => plan.identity.memory ^= 1,
            10 => plan.generation = 0,
            11 => plan.bindings[15].cloexec = 2,
            12 => plan.sources[0].reference = 1,
            _ => (),
        }
        let mut request = request(&plan);
        match case {
            0 => request.sequence = 8,
            1 => {
                owner.context_ready(7, 10).unwrap();
            }
            2 => request.child_writer = 0,
            3 => request.child_reader = 0,
            4 => request.parent_writer = 0,
            5 => request.child_reader = request.child_writer,
            6 => request.parent_writer = request.child_reader,
            7 => {
                owner.context_ready(7, 10).unwrap();
                owner.parent_delivered(7, 10).unwrap();
            }
            8 => request.parent_writer = request.child_writer,
            9..=12 => (),
            _ => unreachable!(),
        }
        let before = owner.phase();
        let mut wire = Wire::new();
        let mut scratch = [0xa5; 304];
        let error =
            fork_transport::publish(&mut owner, &mut wire, request, &mut 1000, &mut scratch)
                .unwrap_err();
        if case < 2 || case == 7 {
            assert_eq!(error, PublishError::Admission(GateError::Mismatch));
            assert_eq!(owner.phase(), before);
        } else {
            assert_eq!(owner.phase(), Phase::Retired);
        }
        assert_eq!(wire.calls, 0);
        assert_eq!(scratch, [0; 304]);
        owner.retire();
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}

#[test]
fn known_refusal_waits_for_settlement_and_complete_original_errno_delivery() {
    for error in [-4095, -12, -1] {
        let (h, mut owner, plan, parent) = prepared();
        owner
            .copy(7, parent, native(2), 9, &plan, |_| {
                CopyAttempt::Refused(error)
            })
            .unwrap()
            .unwrap_err();
        let mut wire = Wire::new();
        wire.refused = true;
        wire.eagain = true;
        let mut scratch = [0xa5; 304];
        assert_eq!(
            fork_transport::refuse(&mut owner, &mut wire, 7, error, 73, &mut 1000, &mut scratch),
            Err(PublishError::Admission(GateError::Mismatch))
        );
        assert_eq!(wire.calls, 0);
        assert_eq!(owner.phase(), Phase::Refused { error });
        // Injected known raw thaw, not a native execution claim.
        owner
            .resolve_refusal(7, error, |_| Ok(-11))
            .unwrap()
            .unwrap();
        assert_eq!(
            fork_transport::refuse(&mut owner, &mut wire, 7, error, 73, &mut 1000, &mut scratch),
            Ok(())
        );
        assert_eq!(owner.phase(), Phase::Idle);
        assert_eq!(wire.parent, fork_frames::disposition(7, error).unwrap());
        assert!(wire.waits > 0);
        assert_eq!(scratch, [0; 304]);
        owner
            .admit(|files, _| {
                assert_eq!(
                    files.position(parent, filesystem_remote_descriptors::FIRST_FILE_FD),
                    Ok(0)
                );
                assert_eq!(
                    files.file_view_v1(parent),
                    Ok((
                        1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                        1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                    ))
                );
            })
            .unwrap();
        owner.retire();
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}

#[test]
fn partial_or_unwound_refusal_delivery_never_reopens_or_thaws_again() {
    for prefix in 0..34 {
        let (h, mut owner, plan, parent) = prepared();
        owner
            .copy(7, parent, native(2), 9, &plan, |_| {
                CopyAttempt::Refused(-12)
            })
            .unwrap()
            .unwrap_err();
        owner.resolve_refusal(7, -12, |_| Ok(-11)).unwrap().unwrap();
        let mut wire = Wire::new();
        wire.refused = true;
        if prefix < 32 {
            wire.stop = Some((73, prefix));
        } else if prefix == 32 {
            wire.panic_at = Some((73, 0));
        } else {
            wire.stop = Some((73, 0));
            wire.error = -32;
        }
        let mut scratch = [0xa5; 304];
        let result = catch_unwind(AssertUnwindSafe(|| {
            fork_transport::refuse(&mut owner, &mut wire, 7, -12, 73, &mut 1000, &mut scratch)
        }));
        if prefix == 32 {
            assert!(result.is_err());
            assert_eq!(owner.phase(), Phase::RefusalSettled { error: -12 });
        } else {
            assert_eq!(
                result.unwrap(),
                Err(PublishError::Transport(if prefix == 33 { -32 } else { -5 }))
            );
            assert_eq!(owner.phase(), Phase::Retired);
            assert_eq!(
                wire.parent,
                fork_frames::disposition(7, -12).unwrap()[..if prefix < 32 { prefix } else { 0 }]
            );
        }
        assert_eq!(owner.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(scratch, [0; 304]);
        owner.retire();
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}

#[test]
fn raw_transport_wait_overcount_and_budget_errors_remain_fail_closed() {
    for (raw, eagain, wait, budget) in [
        (-32, false, 0, 1000),
        (17, false, 0, 1000),
        (0, true, -7, 1000),
        (0, true, 1, 1000),
        (0, true, 0, 1),
        (0, false, 0, 0),
    ] {
        let (h, mut owner, plan, _) = bound(true);
        let mut wire = Wire::new();
        wire.stop = Some((71, 0));
        wire.error = raw;
        wire.eagain = eagain;
        wire.wait = wait;
        let mut scratch = [0xa5; 304];
        let expected = if budget < 2 {
            -110
        } else if eagain {
            if wait < 0 { wait } else { -5 }
        } else if raw < 0 {
            raw
        } else {
            -5
        };
        assert_eq!(
            fork_transport::publish(
                &mut owner,
                &mut wire,
                request(&plan),
                &mut { budget },
                &mut scratch
            ),
            Err(PublishError::Transport(expected))
        );
        assert_eq!(owner.phase(), Phase::Retired);
        assert_eq!(scratch, [0; 304]);
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}

#[test]
fn unwinding_during_each_phase_keeps_gate_closed_and_clears_scratch() {
    for endpoint in [71, 72, 73] {
        let (h, mut owner, plan, _) = bound(true);
        let mut wire = Wire::new();
        wire.panic_at = Some((endpoint, 0));
        let mut scratch = [0xa5; 304];
        assert!(
            catch_unwind(AssertUnwindSafe(|| fork_transport::publish(
                &mut owner,
                &mut wire,
                request(&plan),
                &mut 1000,
                &mut scratch
            )))
            .is_err()
        );
        assert_eq!(
            owner.phase(),
            if endpoint == 73 {
                Phase::Ready { pid: 10 }
            } else {
                Phase::Bound { pid: 10 }
            }
        );
        assert_eq!(owner.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(scratch, [0; 304]);
        owner.retire();
        drop(owner);
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}
