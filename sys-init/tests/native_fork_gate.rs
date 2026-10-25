// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{
    CopyAttempt, CopyInheritanceError, NativeIdentity, ProcessError,
};
use fixture::{Fault, Harness};
use fork_gate::{ForkStreams, GateError, Owner, Phase};
use std::panic::{AssertUnwindSafe, catch_unwind};
#[derive(Default)]
struct Streams {
    staged: usize,
    dispatched: usize,
    panic_ready: bool,
}
// Deliberate stream double: this suite tests FILE/admission mechanics only.
impl ForkStreams for Streams {
    fn validate_fork(&self, _: &Plan) -> Result<(), i32> {
        Ok(())
    }
    fn child_ready(&mut self, _: u32) -> Result<(), i32> {
        assert!(!self.panic_ready, "activation");
        Ok(())
    }
}
fn snapshot(bindings: [Binding; 16]) -> Plan {
    Plan {
        identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
        shell: 1,
        parent: 7,
        generation: 1,
        bindings,
        sources: [Source::default(); 7],
        history: [0; 2],
    }
}
fn harness() -> Harness {
    let fault = match std::env::var("FORK_TEST_FAULT").as_deref() {
        Ok("body") => Fault::ReadBody,
        Ok("count") => Fault::Count,
        Ok("close") => Fault::Close,
        _ => Fault::None,
    };
    Harness::new(fault, [-9, -5])
}
fn identity(slot: u32, epoch: u32) -> NativeIdentity {
    NativeIdentity::admitted(
        slot,
        epoch,
        0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
#[test]
fn successful_copy_gates_capture_publication_ready_and_parent_reply() {
    let mut h = harness();
    let mut files = h.fds.take().unwrap();
    let parent = files.admitted_shell(identity(1, 1), 7).unwrap();
    let fd = files.open_read(parent, b"file", true).unwrap();
    let mut owner = Owner::new(files, Streams::default());
    assert_eq!(
        owner.copy(
            1,
            parent,
            identity(2, 1),
            9,
            &snapshot(map(Some((fd, true)))),
            |_| { CopyAttempt::Unknown(-5) }
        ),
        Err(GateError::Closed)
    );
    owner
        .begin(1, |f, s| {
            assert_eq!(f.position(parent, fd), Ok(0));
            assert_eq!(
                f.file_view_v1(parent),
                Ok((
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                ))
            );
            s.staged = 1;
        })
        .unwrap();
    assert_eq!(
        owner.admit(|_, s| s.dispatched += 1),
        Err(GateError::Closed)
    );
    let child = owner
        .copy(
            1,
            parent,
            identity(2, 1),
            9,
            &snapshot(map(Some((fd, true)))),
            |s| {
                assert_eq!(s.staged, 1);
                CopyAttempt::Copied {
                    identity: identity(2, 1),
                    parent_pid: 9,
                }
            },
        )
        .unwrap()
        .unwrap();
    assert_eq!(owner.phase(), Phase::Bound { pid: 10 });
    assert_eq!(
        owner.admit(|f, _| f.close(parent, fd)),
        Err(GateError::Closed)
    );
    assert_eq!(owner.parent_delivered(1, 10), Err(GateError::Mismatch));
    assert_eq!(owner.context_ready(2, 10), Err(GateError::Mismatch));
    assert_eq!(owner.context_ready(1, 11), Err(GateError::Mismatch));
    owner.context_ready(1, 10).unwrap();
    assert_eq!(
        owner.admit(|_, s| s.dispatched += 1),
        Err(GateError::Closed)
    );
    owner.parent_delivered(1, 10).unwrap();
    owner
        .admit(|f, s| {
            s.dispatched += 1;
            let mut out = [0; 4096];
            assert_eq!(f.read(parent, fd, 2, &mut out), Ok(2));
            assert_eq!(&out[..2], b"ab");
            assert_eq!(f.read(child, fd, 2, &mut out), Ok(2));
            assert_eq!(&out[..2], b"cd");
            assert_eq!(
                f.file_view_v1(parent),
                Ok((
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                ))
            );
            assert_eq!(
                f.file_view_v1(child),
                Ok((
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                ))
            );
            assert_eq!(f.position(parent, fd), Ok(4));
            f.set_close_on_exec(child, fd, false).unwrap();
            assert_eq!(
                f.file_view_v1(parent),
                Ok((
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                ))
            );
            assert_eq!(
                f.file_view_v1(child),
                Ok((1u16 << filesystem_remote_descriptors::FIRST_FILE_FD, 0))
            );
            f.close(parent, fd).unwrap();
            assert_eq!(f.position(child, fd), Ok(4));
            f.close(child, fd).unwrap();
            f.settled(child).unwrap();
            f.settled(parent).unwrap();
            assert_eq!(f.disconnect(), Ok([-9, -5]));
            assert_eq!(s.dispatched, 1);
        })
        .unwrap();
    assert_eq!(owner.phase(), Phase::Retired);
    assert_eq!(owner.cleanup(), Some([-9, -5]));
    assert_eq!(h.opcodes(), [1, 2, 2, 3, 4]);
    assert_eq!(h.storage.lock().unwrap().lookups, 1);
    drop(owner);
    drop(h);
}
#[test]
fn refusal_requires_resolution_delivery_and_does_not_consume_child_epoch() {
    let mut h = harness();
    let mut f = h.fds.take().unwrap();
    let p = f.admitted_shell(identity(1, 1), 7).unwrap();
    let mut g = Owner::new(f, Streams::default());
    g.begin(3, |_, s| s.staged = 1).unwrap();
    assert_eq!(
        g.copy(3, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
            CopyAttempt::Refused(-12)
        })
        .unwrap(),
        Err(CopyInheritanceError::Refused(-12))
    );
    assert_eq!(g.refusal_delivered(3, -12), Err(GateError::Mismatch));
    assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
    assert_eq!(
        g.resolve_refusal(3, -13, |_| Ok(-11)),
        Err(GateError::Mismatch)
    );
    assert_eq!(
        g.resolve_refusal(3, -12, |s| {
            s.staged = 0;
            Ok(-11)
        }),
        Ok(Ok(-11))
    );
    assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
    g.refusal_delivered(3, -12).unwrap();
    assert_eq!(g.begin(3, |_, _| ()), Err(GateError::Sequence));
    g.begin(4, |_, _| ()).unwrap();
    let child = g
        .copy(4, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
            CopyAttempt::Copied {
                identity: identity(2, 1),
                parent_pid: 9,
            }
        })
        .unwrap()
        .unwrap();
    g.context_ready(4, 10).unwrap();
    g.parent_delivered(4, 10).unwrap();
    g.admit(|f, _| {
        assert_eq!(f.current(identity(2, 1)), Ok(child));
        f.settled(child).unwrap();
        f.settled(p).unwrap();
        f.disconnect().unwrap();
    })
    .unwrap();
    drop(g);
    drop(h);
}
#[test]
fn unknown_unbound_and_preflight_retire_without_normal_admissions() {
    for mode in 0..4 {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let p = f.admitted_shell(identity(1, 1), 7).unwrap();
        let mut g = Owner::new(f, Streams::default());
        g.begin(1, |_, s| s.staged = 1).unwrap();
        let mut called = false;
        let target = if mode == 3 {
            identity(2, 2)
        } else {
            identity(2, 1)
        };
        let r = g
            .copy(1, p, target, 9, &snapshot(map(None)), |_| {
                called = true;
                match mode {
                    0 => CopyAttempt::Unknown(-4),
                    1 => CopyAttempt::Copied {
                        identity: identity(3, 1),
                        parent_pid: 9,
                    },
                    _ => CopyAttempt::Refused(0),
                }
            })
            .unwrap();
        match mode {
            0 => assert_eq!(r, Err(CopyInheritanceError::Unknown(-4))),
            1 => assert!(matches!(r, Err(CopyInheritanceError::Unbound { .. }))),
            2 => assert_eq!(r, Err(CopyInheritanceError::Refused(0))),
            _ => assert_eq!(
                r,
                Err(CopyInheritanceError::BeforeCopy(ProcessError::Generation))
            ),
        }
        assert_eq!(called, mode != 3);
        assert_eq!(g.phase(), Phase::Retired);
        assert_eq!(g.cleanup(), Some([-9, -5]));
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(g.refusal_delivered(1, -4), Err(GateError::Mismatch));
        g.retired_streams(|s| {
            assert_eq!(s.staged, 1);
            s.staged = 0;
        })
        .unwrap();
        assert_eq!(h.local.lock().unwrap().closes, 1);
        drop(g);
        drop(h);
    }
}
#[test]
fn failed_refusal_resolution_and_lost_handshake_never_reopen() {
    for mode in 0..3 {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let p = f.admitted_shell(identity(1, 1), 7).unwrap();
        let mut g = Owner::new(f, Streams::default());
        g.begin(1, |_, _| ()).unwrap();
        if mode < 2 {
            g.copy(1, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
                CopyAttempt::Refused(-12)
            })
            .unwrap()
            .unwrap_err();
            let raw = if mode == 0 { Ok(-12) } else { Err(-5) };
            assert_eq!(g.resolve_refusal(1, -12, |_| raw), Ok(raw));
        } else {
            g.copy(1, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
                CopyAttempt::Copied {
                    identity: identity(2, 1),
                    parent_pid: 9,
                }
            })
            .unwrap()
            .unwrap();
            g.context_ready(1, 10).unwrap();
            g.retire();
        }
        assert_eq!(g.phase(), Phase::Retired);
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(g.cleanup(), Some([-9, -5]));
        drop(g);
        drop(h);
    }
}
#[test]
fn unwinds_keep_capture_copy_dispatch_and_resolution_closed() {
    for mode in 0..5 {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let p = f.admitted_shell(identity(1, 1), 7).unwrap();
        let mut g = Owner::new(f, Streams::default());
        let result = catch_unwind(AssertUnwindSafe(|| match mode {
            0 => {
                let _: Result<(), _> = g.begin(1, |_, _| panic!("capture"));
            }
            1 => {
                g.begin(1, |_, _| ()).unwrap();
                let _ = g.copy(1, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
                    panic!("copy")
                });
            }
            2 => {
                let _: Result<(), _> = g.admit(|_, _| panic!("dispatch"));
            }
            3 => {
                g.begin(1, |_, _| ()).unwrap();
                g.copy(1, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
                    CopyAttempt::Refused(-12)
                })
                .unwrap()
                .unwrap_err();
                let _ = g.resolve_refusal(1, -12, |_| panic!("resolve"));
            }
            _ => {
                g.begin(1, |_, s| s.panic_ready = true).unwrap();
                g.copy(1, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
                    CopyAttempt::Copied {
                        identity: identity(2, 1),
                        parent_pid: 9,
                    }
                })
                .unwrap()
                .unwrap();
                let _ = g.context_ready(1, 10);
            }
        }));
        assert!(result.is_err());
        assert_ne!(g.phase(), Phase::Idle);
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        g.retire();
        assert_eq!(g.cleanup(), Some([-9, -5]));
        drop(g);
        drop(h);
    }
}
#[test]
fn final_sequence_is_usable_once_and_never_resets() {
    let mut h = harness();
    let mut f = h.fds.take().unwrap();
    let p = f.admitted_shell(identity(1, 1), 7).unwrap();
    let mut g = Owner::new(f, Streams::default());
    assert_eq!(g.begin(0, |_, _| ()), Err(GateError::Sequence));
    g.begin(u64::MAX, |_, _| ()).unwrap();
    g.copy(u64::MAX, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
        CopyAttempt::Refused(-28)
    })
    .unwrap()
    .unwrap_err();
    g.resolve_refusal(u64::MAX, -28, |_| Ok(-11))
        .unwrap()
        .unwrap();
    g.refusal_delivered(u64::MAX, -28).unwrap();
    assert_eq!(g.sequence(), u64::MAX);
    assert_eq!(g.begin(u64::MAX, |_, _| ()), Err(GateError::Sequence));
    assert_eq!(g.begin(1, |_, _| ()), Err(GateError::Sequence));
    drop(g);
    drop(h);
}

fn map(file: Option<(i32, bool)>) -> [Binding; 16] {
    let mut bindings = [Binding::default(); 16];
    // Stream selector3 is a separate domain from remote FILE3.
    bindings[3] = Binding {
        kind: 2,
        selector: 3,
        cloexec: 0,
    };
    if let Some((selector, flag)) = file {
        bindings[5] = Binding {
            kind: 3,
            selector: u8::try_from(selector).unwrap(),
            cloexec: u8::from(flag),
        };
    }
    bindings
}
#[test]
fn file_view_denials_have_no_copy_source_or_flag_effects() {
    for mode in 0..8 {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let p = f.admitted_shell(identity(1, 1), 7).unwrap();
        let fd = f.open_read(p, b"file", true).unwrap();
        assert_eq!(fd, filesystem_remote_descriptors::FIRST_FILE_FD);
        let baseline = h.opcodes();
        let mut bindings = map(Some((fd, true)));
        match mode {
            0 => bindings[5] = Binding::default(), // omitted
            1 => bindings[5].cloexec = 0,
            2 => {
                bindings[6] = Binding {
                    kind: 3,
                    selector: 15,
                    cloexec: 0,
                }
            }
            3 => bindings[6] = bindings[5], // duplicate remote selector
            4 => bindings[5].selector = 2,  // reserved low bit
            5 => bindings[5].cloexec = 2,
            6 => bindings[6].cloexec = 1, // flags on hole
            _ => bindings[5].kind = 4,
        }
        let mut g = Owner::new(f, Streams::default());
        g.begin(1, |f, _| {
            assert_eq!(
                f.file_view_v1(p),
                Ok((
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                    1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                ))
            );
            assert_eq!(f.position(p, fd), Ok(0));
        })
        .unwrap();
        let mut called = false;
        assert_eq!(
            g.copy(1, p, identity(2, 1), 9, &snapshot(bindings), |_| {
                called = true;
                CopyAttempt::Unknown(-5)
            }),
            Err(GateError::Mismatch)
        );
        assert!(!called);
        assert_eq!(g.phase(), Phase::Rejected);
        assert_eq!(g.cleanup(), None);
        assert_eq!(h.opcodes(), baseline);
        assert_eq!(h.local.lock().unwrap().closes, 0);
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(
            g.copy(
                1,
                p,
                identity(2, 1),
                9,
                &snapshot(map(Some((fd, true)))),
                |_| { panic!("rejected transaction cannot retry") }
            ),
            Err(GateError::Closed)
        );
        g.retire();
        drop(g);
        drop(h);
    }
}
#[test]
fn stale_and_retired_file_views_never_become_empty_success() {
    for retired in [false, true] {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let p = f.admitted_shell(identity(1, 1), 7).unwrap();
        if !retired {
            f.settled(p).unwrap();
        }
        let mut g = Owner::new(f, Streams::default());
        g.begin(1, |f, _| {
            if retired {
                f.abort();
            }
        })
        .unwrap();
        let mut called = false;
        let result = g.copy(1, p, identity(2, 1), 9, &snapshot(map(None)), |_| {
            called = true;
            CopyAttempt::Unknown(-5)
        });
        assert!(matches!(result, Err(GateError::FileView(_))));
        assert!(!called);
        assert_eq!(g.phase(), Phase::Rejected);
        assert!(h.opcodes().is_empty());
        assert_eq!(h.local.lock().unwrap().closes, usize::from(retired));
        g.retire();
        drop(g);
        drop(h);
    }
}
#[test]
fn every_remote_file_bit_survives_reordered_map_and_inheritance() {
    let first = filesystem_remote_descriptors::FIRST_FILE_FD;
    for flagged in first..=15 {
        let mut h = harness();
        let mut f = h.fds.take().unwrap();
        let p = f.admitted_shell(identity(1, 1), 7).unwrap();
        let fd = f.open_read(p, b"file", flagged == first).unwrap();
        for next in first + 1..=15 {
            assert_eq!(f.duplicate(p, fd, next, next == flagged), Ok(next));
        }
        let mut bindings = [Binding::default(); 16];
        for (slot, binding) in bindings[..(16 - first as usize)].iter_mut().enumerate() {
            let remote = 15 - slot as u8;
            *binding = Binding {
                kind: 3,
                selector: remote,
                cloexec: u8::from(i32::from(remote) == flagged),
            };
        }
        if first == 3 {
            bindings[15] = Binding {
                kind: 2,
                selector: 3,
                cloexec: 0,
            };
        }
        let baseline = h.opcodes();
        let expected = (u16::MAX << first, 1u16 << flagged);
        let mut g = Owner::new(f, Streams::default());
        g.begin(1, |f, _| {
            assert_eq!(f.file_view_v1(p), Ok(expected));
            assert_eq!(f.position(p, 15), Ok(0));
        })
        .unwrap();
        let child = g
            .copy(1, p, identity(2, 1), 9, &snapshot(bindings), |_| {
                CopyAttempt::Copied {
                    identity: identity(2, 1),
                    parent_pid: 9,
                }
            })
            .unwrap()
            .unwrap();
        assert_eq!(h.opcodes(), baseline);
        assert_eq!(h.local.lock().unwrap().closes, 0);
        g.context_ready(1, 10).unwrap();
        g.parent_delivered(1, 10).unwrap();
        g.admit(|f, _| {
            assert_eq!(f.file_view_v1(p), Ok(expected));
            assert_eq!(f.file_view_v1(child), Ok(expected));
            assert_eq!(f.position(p, 15), Ok(0));
            assert_eq!(f.position(child, 15), Ok(0));
            for fd in first..=15 {
                f.close(child, fd).unwrap();
                f.close(p, fd).unwrap();
            }
            f.settled(child).unwrap();
            f.settled(p).unwrap();
            f.disconnect().unwrap();
        })
        .unwrap();
        drop(g);
        drop(h);
    }
}
