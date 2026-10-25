// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity};
use fixture::{Fault, Harness};
use fork_gate::{ForkStreams, GateError, Owner, Phase};
use fork_streams::{Caller, Outcome, SessionPipe, State};
fn id(slot: u32, epoch: u32) -> Identity {
    Identity::admitted(
        slot,
        epoch,
        0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
fn native_id(slot: u32, epoch: u32) -> NativeIdentity {
    NativeIdentity::admitted(
        slot,
        epoch,
        0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
fn console() -> [Option<Source>; 3] {
    core::array::from_fn(|i| {
        Some(Source {
            reference: 0x10101 + i as u32,
            selector: i as u32,
            rights: if i == 0 { 1 } else { 2 },
            bound: 16,
        })
    })
}
fn frame(op: u32, generation: u32, end: u32, data: &[u8]) -> [u8; 32] {
    let mut raw = [0; 32];
    for (at, word) in [
        (0, op),
        (4, 0x78000000 | generation << 8 | end),
        (8, end + 2),
        (12, data.len() as u32),
    ] {
        raw[at..at + 4].copy_from_slice(&word.to_le_bytes());
    }
    if op == 2 {
        raw[16..16 + data.len()].copy_from_slice(data);
    }
    raw
}
fn result(outcome: Outcome) -> i32 {
    match outcome {
        Outcome::Reply(raw) => i32::from_le_bytes(raw[..4].try_into().unwrap()),
        Outcome::Pending => panic!("expected complete reply"),
    }
}
fn create(pipe: &mut SessionPipe) {
    let mut raw = [0; 32];
    raw[..4].copy_from_slice(&82u32.to_le_bytes());
    raw[4..8].copy_from_slice(&0x76050001u32.to_le_bytes());
    raw[8..12].copy_from_slice(&1u32.to_le_bytes());
    assert_eq!(result(pipe.request(Caller::Parent, &raw)), 0);
}
fn state(open: bool) -> State {
    let mut pipes = [SessionPipe::new(), SessionPipe::new()];
    if open {
        for p in &mut pipes {
            create(p);
        }
    }
    State::new(console(), pipes).unwrap()
}
fn plan(open: bool, file: bool) -> Plan {
    let mut p = Plan {
        identity: id(1, 1),
        shell: 1,
        parent: 7,
        generation: 1,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: if open { [1; 2] } else { [0; 2] },
    };
    for (i, source) in console().iter().enumerate() {
        p.bindings[i] = Binding {
            kind: 1,
            selector: i as u8,
            cloexec: (i % 2) as u8,
        };
        p.sources[i] = source.unwrap();
    }
    if open {
        for i in 3..7 {
            p.bindings[i] = Binding {
                kind: 2,
                selector: i as u8,
                cloexec: (i % 2) as u8,
            };
            p.sources[i] = Source {
                reference: 0x79000000
                    | (((i - 3) / 2) as u32) << 16
                    | 1 << 8
                    | (((i - 3) % 2 + 1) as u32),
                selector: i as u32,
                rights: if i % 2 == 1 { 1 } else { 2 },
                bound: 16,
            };
        }
        // Alias a CLOEXEC reader; fork preserves it.
        p.bindings[12] = p.bindings[3];
    }
    if file {
        p.bindings[15] = Binding {
            kind: 3,
            selector: filesystem_remote_descriptors::FIRST_FILE_FD as u8,
            cloexec: 1,
        };
    }
    p
}
fn harness() -> Harness {
    Harness::new(Fault::None, [-9, -5])
}
#[test]
fn gate_checks_actual_pipes_before_copy_then_holders_control_eof() {
    let mut h = harness();
    let mut files = h.fds.take().unwrap();
    let parent = files.admitted_shell(native_id(1, 1), 7).unwrap();
    assert_eq!(
        files.open_read(parent, b"file", true),
        Ok(filesystem_remote_descriptors::FIRST_FILE_FD)
    );
    let p = plan(true, true);
    let mut scratch = [0; 304];
    fd_startup::encode(&p, &mut scratch).unwrap();
    let mut g = Owner::new(files, state(true));
    g.begin(1, |_, s| s.validate_fork(&p)).unwrap().unwrap();
    assert_eq!(h.storage.lock().unwrap().lookups, 1);
    let before = h.opcodes();
    let child = g
        .copy(1, parent, native_id(2, 1), 9, &p, |s| {
            // Reserve actual reader/writer holders before the simulated native copy.
            for object in 0..2 {
                s.pipe_mut(object)
                    .unwrap()
                    .stage_participant(1, 1, [true; 2])
                    .unwrap();
                assert_eq!(
                    result(s.pipe_mut(object).unwrap().request(
                        Caller::Participant {
                            slot: 1,
                            generation: 1
                        },
                        &frame(2, 1, 2, b"z")
                    )),
                    -13
                );
            }
            CopyAttempt::Copied {
                identity: native_id(2, 1),
                parent_pid: 9,
            }
        })
        .unwrap()
        .unwrap();
    assert_eq!(h.opcodes(), before);
    assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
    g.context_ready(1, 10).unwrap();
    g.parent_delivered(1, 10).unwrap();
    g.admit(|f, s| {
        for object in 0..2 {
            let pipe = s.pipe_mut(object).unwrap();

            assert_eq!(
                result(pipe.request(
                    Caller::Participant {
                        slot: 1,
                        generation: 1
                    },
                    &frame(2, 1, 2, b"z")
                )),
                1
            );
            assert_eq!(
                result(pipe.request(Caller::Parent, &frame(3, 1, 2, &[]))),
                0
            );
            assert_eq!(
                result(pipe.request(Caller::Parent, &frame(1, 1, 1, b"x"))),
                1
            );
            assert_eq!(
                pipe.request(Caller::Parent, &frame(1, 1, 1, b"x")),
                Outcome::Pending
            );
            pipe.confirmed_terminal(Caller::Participant {
                slot: 1,
                generation: 1,
            })
            .unwrap();
            assert_eq!(
                result(pipe.request(Caller::Parent, &frame(1, 1, 1, b"x"))),
                0
            );
            assert_eq!(
                result(pipe.request(Caller::Parent, &frame(3, 1, 1, &[]))),
                0
            );
            assert!(pipe.retire_if_idle([false; 4]));
        }
        f.close(child, filesystem_remote_descriptors::FIRST_FILE_FD)
            .unwrap();
        f.close(parent, filesystem_remote_descriptors::FIRST_FILE_FD)
            .unwrap();
        f.settled(child).unwrap();
        f.settled(parent).unwrap();
        f.disconnect().unwrap();
    })
    .unwrap();
    drop(g);
    drop(h);
}
#[test]
fn all_source_fields_holdings_and_history_mismatches_deny_without_copy() {
    // Every field of every live source, omitted live endpoint, extra alias-domain
    // confusion, and both history words. Source references never confer authority.
    for mode in 0..40 {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let parent = f.admitted_shell(native_id(1, 1), 7).unwrap();
        let mut p = plan(true, false);
        match mode {
            0..=27 => {
                let src = &mut p.sources[mode / 4];
                match mode % 4 {
                    0 => src.reference ^= 1,
                    1 => src.selector ^= 1,
                    2 => src.rights ^= 3,
                    _ => src.bound ^= 1,
                }
            }
            28..=34 => {
                let i = mode - 28;
                p.bindings[i] = Binding::default();
                if i == 3 {
                    p.bindings[12] = Binding::default();
                }
                p.sources[i] = Source::default();
            }
            35..=36 => p.history[mode - 35] ^= 1,
            37 => {
                p.bindings[3].kind = 3;
                p.bindings[12] = Binding::default();
                p.sources[3] = Source::default();
            }
            38 => p.sources.swap(3, 5),
            _ => p.sources[3].reference = 0x78000101,
        }
        let mut g = Owner::new(f, state(true));
        g.begin(1, |_, _| ()).unwrap();
        let mut called = false;
        let r = g.copy(1, parent, native_id(2, 1), 9, &p, |_| {
            called = true;
            CopyAttempt::Unknown(-5)
        });
        assert!(matches!(
            r,
            Err(GateError::Streams(_)) | Err(GateError::Mismatch)
        ));
        assert!(!called);
        assert_eq!(g.phase(), Phase::Rejected);
        assert_eq!(g.cleanup(), None);
        assert!(h.opcodes().is_empty());
        assert_eq!(h.local.lock().unwrap().closes, 0);
        assert_eq!(
            g.copy(
                1,
                parent,
                native_id(2, 1),
                9,
                &plan(true, false),
                |_| panic!("retry")
            ),
            Err(GateError::Closed)
        );
        g.retire();
        drop(g);
        drop(h);
    }
}
#[test]
fn validation_is_read_only_and_retains_inactive_history_and_closed_console() {
    let mut s = state(true);
    let original = plan(true, false);
    s.validate_fork(&original).unwrap();
    for object in 0..2 {
        let pipe = s.pipe_mut(object).unwrap();
        assert_eq!(
            result(pipe.request(Caller::Parent, &frame(2, 1, 2, b"q"))),
            1
        );
        let baseline = pipe.clone();
        let mut wrong = plan(true, false);
        wrong.history[object] = 0;
        assert_eq!(s.validate_fork(&wrong), Err(-9));
        assert_eq!(*s.pipe_mut(object).unwrap(), baseline);
    }
    for object in 0..2 {
        let pipe = s.pipe_mut(object).unwrap();
        for end in 1..=2 {
            assert_eq!(
                result(pipe.request(Caller::Parent, &frame(3, 1, end, &[]))),
                0
            );
        }
        assert!(pipe.retire_if_idle([false; 4]));
    }
    let mut empty = plan(false, false);
    empty.history = [1; 2];
    s.validate_fork(&empty).unwrap();
    assert_eq!(s.validate_fork(&plan(false, false)), Err(-9));
    // History survives even when no source is emitted. A new pipe increments it.
    create(s.pipe_mut(0).unwrap());
    assert_eq!(s.validate_fork(&empty), Err(-9));
    let mut no_pipe = state(false);
    no_pipe.console_closed(1).unwrap();
    let mut closed = plan(false, false);
    closed.bindings[1] = Binding::default();
    closed.sources[1] = Source::default();
    no_pipe.validate_fork(&closed).unwrap();
    assert_eq!(no_pipe.validate_fork(&plan(false, false)), Err(-9));
    assert_eq!(no_pipe.console_closed(1), Err(-9));
    assert_eq!(no_pipe.console_closed(3), Err(-9));
    assert!(
        State::new(
            [Some(Source::default()), None, None],
            [SessionPipe::new(), SessionPipe::new()]
        )
        .is_err()
    );
}
#[test]
fn known_refusal_releases_staging_but_unknown_keeps_real_holders() {
    for unknown in [false, true] {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let parent = f.admitted_shell(native_id(1, 1), 7).unwrap();
        let p = plan(true, false);
        let mut g = Owner::new(f, state(true));
        g.begin(1, |_, _| ()).unwrap();
        g.copy(1, parent, native_id(2, 1), 9, &p, |s| {
            for object in 0..2 {
                s.pipe_mut(object)
                    .unwrap()
                    .stage_participant(1, 1, [true; 2])
                    .unwrap();
            }
            if unknown {
                CopyAttempt::Unknown(-5)
            } else {
                CopyAttempt::Refused(-12)
            }
        })
        .unwrap()
        .unwrap_err();
        if unknown {
            assert_eq!(g.phase(), Phase::Retired);
            g.retired_streams(|s| {
                let pipe = s.pipe_mut(0).unwrap();
                assert_eq!(
                    result(pipe.request(Caller::Parent, &frame(3, 1, 2, &[]))),
                    0
                );
                assert_eq!(
                    pipe.request(Caller::Parent, &frame(1, 1, 1, b"x")),
                    Outcome::Pending
                );
                // Only confirmed termination settles unknown child obligations.
                pipe.confirmed_terminal(Caller::Participant {
                    slot: 1,
                    generation: 1,
                })
                .unwrap();
                assert_eq!(
                    result(pipe.request(Caller::Parent, &frame(1, 1, 1, b"x"))),
                    0
                );
            })
            .unwrap();
        } else {
            g.resolve_refusal(1, -12, |s| {
                for object in 0..2 {
                    s.pipe_mut(object)
                        .unwrap()
                        .finish_participant_copy(1, 1, false)
                        .unwrap();
                }
                Ok(-11) // injected authenticated thaw observation
            })
            .unwrap()
            .unwrap();
            g.refusal_delivered(1, -12).unwrap();
            g.admit(|_, s| {
                s.validate_fork(&p).unwrap();
                // Refusal consumed no child epoch; this exact reservation is reusable.
                s.pipe_mut(0)
                    .unwrap()
                    .stage_participant(1, 1, [true; 2])
                    .unwrap();
            })
            .unwrap();
        }
        g.retire();
        drop(g);
        drop(h);
    }
}
#[test]
fn terminated_parent_is_not_empty_and_no_readers_produce_epipe() {
    let mut s = state(true);
    let pipe = s.pipe_mut(0).unwrap();
    assert_eq!(
        result(pipe.request(Caller::Parent, &frame(3, 1, 1, &[]))),
        0
    );
    assert_eq!(
        result(pipe.request(Caller::Parent, &frame(2, 1, 2, b"x"))),
        -32
    );
    assert_eq!(
        result(pipe.request(Caller::Parent, &frame(3, 1, 2, &[]))),
        0
    );
    assert!(pipe.retire_if_idle([false; 4]));
    pipe.confirmed_terminal(Caller::Parent).unwrap();
    let mut p = plan(true, false);
    p.bindings[3] = Binding::default();
    p.bindings[4] = Binding::default();
    p.bindings[12] = Binding::default();
    p.sources[3] = Source::default();
    p.sources[4] = Source::default();
    assert_eq!(s.validate_fork(&p), Err(-13));
}
#[test]
fn missing_staged_holders_cannot_publish_parent_success() {
    for partial in [false, true] {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let parent = f.admitted_shell(native_id(1, 1), 7).unwrap();
        let p = plan(true, false);
        let mut g = Owner::new(f, state(true));
        g.begin(1, |_, _| ()).unwrap();
        g.copy(1, parent, native_id(2, 1), 9, &p, |s| {
            if partial {
                s.pipe_mut(0)
                    .unwrap()
                    .stage_participant(1, 1, [true; 2])
                    .unwrap();
            }
            CopyAttempt::Copied {
                identity: native_id(2, 1),
                parent_pid: 9,
            }
        })
        .unwrap()
        .unwrap();
        assert_eq!(g.context_ready(1, 10), Err(GateError::Streams(-9)));
        assert_eq!(g.phase(), Phase::Retired);
        assert_eq!(g.parent_delivered(1, 10), Err(GateError::Mismatch));
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(g.cleanup(), Some([-9, -5]));
        drop(g);
        drop(h);
    }
}

fn tagged(op: u32, object: u32, generation: u32, end: u32, data: &[u8]) -> [u8; 32] {
    let mut raw = frame(op, generation, end, data);
    raw[4..8].copy_from_slice(&(0x79000000 | object << 16 | generation << 8 | end).to_le_bytes());
    raw[8..12].copy_from_slice(&(3 + object * 2 + end - 1).to_le_bytes());
    raw
}
#[test]
fn tagged_factory_routes_both_owned_objects_and_preserves_pending_eof_and_epipe() {
    let mut s = state(false);
    let mut factory = [0; 32];
    factory[0] = 82;
    factory[4..8].copy_from_slice(&0x76050001u32.to_le_bytes());
    factory[8] = 1;
    for object in 0..2 {
        let Outcome::Reply(raw) =
            s.request(Caller::Parent, &factory, |_, _| panic!("pipe is not UART"))
        else {
            panic!("factory")
        };
        assert_eq!(
            u32::from_le_bytes(raw[8..12].try_into().unwrap()),
            0x79000101 | object << 16
        );
        assert_eq!(
            u32::from_le_bytes(raw[16..20].try_into().unwrap()),
            3 + object * 2
        );
    }
    assert_eq!(
        result(s.request(Caller::Parent, &factory, |_, _| panic!())),
        -23
    );
    for object in 0..2 {
        let read = tagged(1, object, 1, 1, &[0; 2]);
        assert!(matches!(
            s.request(Caller::Parent, &read, |_, _| panic!()),
            Outcome::Pending
        ));
        assert_eq!(
            result(s.request(
                Caller::Parent,
                &tagged(2, object, 1, 2, b"ab"),
                |_, _| panic!()
            )),
            2
        );
        let Outcome::Reply(raw) = s.request(Caller::Parent, &read, |_, _| panic!()) else {
            panic!()
        };
        assert_eq!(&raw[16..18], b"ab");
        let mut forged = read;
        forged[6] ^= 1;
        assert_eq!(
            result(s.request(Caller::Parent, &forged, |_, _| panic!())),
            -13
        );
        assert_eq!(
            result(s.request(
                Caller::Parent,
                &tagged(3, object, 1, 2, b""),
                |_, _| panic!()
            )),
            0
        );
        assert_eq!(result(s.request(Caller::Parent, &read, |_, _| panic!())), 0);
        assert_eq!(
            result(s.request(
                Caller::Parent,
                &tagged(3, object, 1, 1, b""),
                |_, _| panic!()
            )),
            0
        );
    }
    s.retire_idle([true, false, false, false]);
    assert_eq!(
        result(s.request(Caller::Parent, &factory, |_, _| panic!())),
        -23
    );
    s.retire_idle([false; 4]);
    let Outcome::Reply(raw) = s.request(Caller::Parent, &factory, |_, _| panic!()) else {
        panic!()
    };
    assert_eq!(raw[4], 2);
    assert_eq!(
        result(s.request(
            Caller::Parent,
            &tagged(1, 0, 1, 1, &[0; 1]),
            |_, _| panic!()
        )),
        -9
    );
}
#[test]
fn staged_console_and_pipe_holders_activate_refuse_and_terminate_atomically() {
    let mut s = state(true);
    let p = plan(true, false);
    s.stage_child(10, &p).unwrap();
    let child = Caller::Participant {
        slot: 1,
        generation: 1,
    };
    let source = console()[1].unwrap().reference;
    let mut console = [0; 32];
    console[0] = 2;
    console[4..8].copy_from_slice(&source.to_le_bytes());
    console[8] = 1;
    console[12] = 2;
    console[16..18].copy_from_slice(b"ab");
    assert_eq!(
        result(s.request(child, &console, |_, _| panic!("staged I/O forbidden"))),
        -13
    );
    s.cancel_stage(10).unwrap();
    s.stage_child(10, &p).unwrap();
    s.child_ready(10).unwrap();
    assert_eq!(s.cancel_stage(10), Err(-9));
    let mut calls = 0;
    assert_eq!(
        result(s.request(child, &console, |write, bytes| {
            assert!(write);
            assert_eq!(bytes, b"ab");
            calls += 1;
            2
        })),
        2
    );
    assert_eq!(calls, 1);
    assert!(matches!(
        s.request(child, &console, |_, _| -11),
        Outcome::Pending
    ));
    assert_eq!(result(s.request(child, &console, |_, _| -32)), -32);
    let mut close = console;
    close[0] = 3;
    close[12] = 0;
    close[16..].fill(0);
    assert_eq!(result(s.request(child, &close, |_, _| panic!())), 0);
    assert_eq!(result(s.request(child, &console, |_, _| panic!())), -13);
    assert_eq!(result(s.request(Caller::Parent, &console, |_, _| 2)), 2);
    s.confirmed_terminal(child).unwrap();
    assert_eq!(
        result(s.request(child, &tagged(2, 0, 1, 2, b"a"), |_, _| panic!())),
        -13
    );
    assert_eq!(s.confirmed_terminal(child), Err(-9));
    s.stage_child(17, &p).unwrap();
    s.child_ready(17).unwrap();
    assert_eq!(result(s.request(child, &console, |_, _| panic!())), -13);
    let replacement = Caller::Participant {
        slot: 1,
        generation: 2,
    };
    assert_eq!(result(s.request(replacement, &console, |_, _| 2)), 2);
}
