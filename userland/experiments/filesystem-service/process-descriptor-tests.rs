// SPDX-License-Identifier: BSD-2-Clause
use super::*;
#[path = "process-fd-fixture.rs"]
mod fixture;
use super::super::MAX_FDS;
use fixture::{Fault, Harness};
fn identity(slot: u32, epoch: u32) -> NativeIdentity {
    NativeIdentity::admitted(
        slot,
        epoch,
        0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
fn shell<T: Channel>(f: &mut ProcessFiles<T>) -> Process {
    f.admitted_shell(identity(1, 1), 7).unwrap()
}
#[test]
fn copied_views_share_offsets_and_last_close_across_all_four_processes() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", false).unwrap();
    let mut children = std::vec::Vec::new();
    for slot in 2..=4 {
        children.push(f.inherited_child(p, identity(slot, 1), 9).unwrap());
    }
    assert_eq!(f.open_read(children[0], b"alias", false), Ok(4));
    let mut out = [0x77; MAX_READ];
    assert_eq!(f.read(p, fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(f.read(children[0], fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
    assert_eq!(f.position(children[1], fd), Ok(4));
    assert_eq!(f.position(children[0], 4), Ok(0));
    f.close(p, fd).unwrap();
    f.close(children[0], fd).unwrap();
    f.close(children[1], fd).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 0);
    h.fds.as_mut().unwrap().close(children[2], fd).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 1);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 1).count(), 2);
    let storage = h.storage.clone();
    drop(h);
    assert_eq!(storage.lock().unwrap().drops, 1);
}
#[test]
fn copied_flags_change_per_process_and_failed_open_preserves_parent() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", true).unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.set_close_on_exec(child, fd, false).unwrap();
    assert_eq!(
        f.open_read(p, b"missing", true),
        Err(ProcessError::Files(Failure::Source(
            filesystem_client::Error::Remote(-2)
        )))
    );
    assert_eq!(f.position(p, fd), Ok(0));
    assert_eq!(f.position(child, fd), Ok(0));
    f.commit_exec_close(child).unwrap();
    assert_eq!(f.position(child, fd), Ok(0));
    f.commit_exec_close(p).unwrap();
    assert_eq!(f.position(p, fd), Err(ProcessError::Files(Failure::BadFd)));
    let mut out = [0x77; MAX_READ];
    assert_eq!(f.read(child, fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 0);
}
#[test]
fn stale_identity_epochs_parents_and_keys_never_select_replacement_view() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.admitted_shell(identity(1, 1), 14),
        Err(ProcessError::Identity(-9))
    );
    let p = shell(f);
    let fd = f.open_read(p, b"file", false).unwrap();
    assert_eq!(
        f.inherited_child(p, identity(2, 1), 7),
        Err(ProcessError::Identity(-9))
    );
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    assert_eq!(
        f.current(NativeIdentity {
            pid: 99,
            ..identity(2, 1)
        }),
        Err(ProcessError::Stale)
    );
    let foreign = Process {
        service_epoch: 90,
        ..child
    };
    let mut out = [0x77; MAX_READ];
    assert_eq!(f.read(foreign, fd, 1, &mut out), Err(ProcessError::Stale));
    assert_eq!(out, [0; MAX_READ]);
    f.settled(child).unwrap();
    let replacement = f.inherited_child(p, identity(2, 2), 9).unwrap();
    assert_eq!(f.position(child, fd), Err(ProcessError::Stale));
    assert_eq!(f.current(identity(2, 1)), Err(ProcessError::Stale));
    assert_eq!(f.position(replacement, fd), Ok(0));
    assert_eq!(
        f.inherited_child(replacement, identity(3, 1), 10),
        Err(ProcessError::Stale)
    );
}
#[test]
fn generation_history_never_resets_and_shell_waits_for_all_views() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    assert_eq!(
        f.inherited_child(p, identity(2, 2), 9),
        Err(ProcessError::Generation)
    );
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    assert_eq!(
        f.inherited_child(p, identity(2, 1), 9),
        Err(ProcessError::Busy)
    );
    f.settled(p).unwrap();
    assert_eq!(f.admitted_shell(identity(1, 2), 7), Err(ProcessError::Busy));
    f.settled(child).unwrap();
    let next = f.admitted_shell(identity(1, 2), 7);
    assert_eq!(next.as_ref().map(|_| ()), Ok(()));
    let p2 = next.unwrap();
    assert_eq!(
        f.inherited_child(p2, identity(2, 1), 16),
        Err(ProcessError::Generation)
    );
    for generation in 2..=15 {
        let c = f.inherited_child(p2, identity(2, generation), 16).unwrap();
        f.settled(c).unwrap();
    }
    assert_eq!(
        f.inherited_child(p2, identity(2, 15), 16),
        Err(ProcessError::Generation)
    );
    assert!(f
        .inherited_child(
            p2,
            NativeIdentity {
                epoch: 16,
                ..identity(2, 15)
            },
            16
        )
        .is_err());
    f.settled(p2).unwrap();
    let p3 = f.admitted_shell(identity(1, 3), 7).unwrap();
    f.settled(p3).unwrap();
    assert!(f
        .admitted_shell(
            NativeIdentity {
                epoch: 4,
                ..identity(1, 3)
            },
            7
        )
        .is_err());
}
#[test]
fn inheritance_at_capacity_uses_no_new_handles_and_process_close_is_local() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    for expected in 3..MAX_FDS {
        assert_eq!(f.open_read(p, b"file", false), Ok(expected));
    }
    let c = f.inherited_child(p, identity(2, 1), 9).unwrap();
    assert_eq!(
        f.open_read(c, b"alias", false),
        Err(ProcessError::Files(Failure::Full))
    );
    assert_eq!(
        f.duplicate(c, 3, 0, false),
        Err(ProcessError::Files(Failure::Full))
    );
    f.close(c, 3).unwrap();
    assert_eq!(f.position(p, 3), Ok(0));
    assert_eq!(
        f.open_read(c, b"alias", false),
        Err(ProcessError::Files(Failure::Full))
    );
    f.close(p, 3).unwrap();
    assert_eq!(f.open_read(c, b"alias", false), Ok(3));
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 1).count(), 14);
}
#[test]
fn busy_disconnect_preserves_live_views_and_settlement_closes_only_last_alias() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", false).unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    assert_eq!(f.disconnect(), Err(ProcessError::Busy));
    assert_eq!(f.cleanup(), None);
    f.settled(p).unwrap();
    assert_eq!(f.position(child, fd), Ok(0));
    f.settled(child).unwrap();
    assert_eq!(f.disconnect(), Ok([-9, -5]));
    assert_eq!(f.cleanup(), Some([-9, -5]));
    assert_eq!(
        f.current(identity(2, 1)),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 1);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 4).count(), 1);
}
#[test]
fn read_loss_and_unknown_final_close_retire_without_releasing_native_ledger() {
    for fault in [Fault::ReadBody, Fault::Close] {
        let mut h = Harness::new(fault, [-9, -5]);
        let f = h.fds.as_mut().unwrap();
        let p = shell(f);
        let fd = f.open_read(p, b"file", false).unwrap();
        let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
        if fault == Fault::ReadBody {
            let mut out = [0x77; MAX_READ];
            assert_eq!(
                f.read(child, fd, 2, &mut out),
                Err(ProcessError::Files(Failure::Source(
                    filesystem_client::Error::Transport(-32)
                )))
            );
            assert_eq!(out, [0; MAX_READ]);
        } else {
            f.settled(p).unwrap();
            assert_eq!(
                f.settled(child),
                Err(ProcessError::Files(Failure::Source(
                    filesystem_client::Error::Transport(-32)
                )))
            );
        }
        assert_eq!(
            f.current(identity(2, 1)),
            Err(ProcessError::Files(Failure::Retired))
        );
        assert!(f.records[1].process.is_some());
        assert_eq!(f.cleanup(), Some([-9, -5]));
        assert_eq!(
            f.admitted_shell(identity(1, 2), 7),
            Err(ProcessError::Files(Failure::Retired))
        );
        assert!(!h.opcodes().contains(&4));
    }
}
#[test]
fn every_non_native_admission_field_rejects_without_publishing_view() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    for bad in [
        NativeIdentity {
            handle: 0,
            ..identity(1, 1)
        },
        NativeIdentity {
            pid: 8,
            ..identity(1, 1)
        },
        NativeIdentity {
            memory: 0,
            ..identity(1, 1)
        },
        NativeIdentity {
            slot: 5,
            ..identity(1, 1)
        },
    ] {
        assert!(f.admitted_shell(bad, 7).is_err());
        assert!(f.records.iter().all(|r| r.process.is_none()));
    }
    let p = shell(f);
    let fd = f.open_read(p, b"file", false).unwrap();
    let before = h.local.lock().unwrap().sent.len();
    for bad in [
        NativeIdentity {
            handle: 0,
            ..identity(2, 1)
        },
        NativeIdentity {
            pid: 9,
            ..identity(2, 1)
        },
        NativeIdentity {
            memory: 0,
            ..identity(2, 1)
        },
    ] {
        assert!(f.inherited_child(p, bad, 9).is_err());
        assert!(f.records[1].process.is_none());
        assert_eq!(f.position(p, fd), Ok(0));
    }
    assert_eq!(h.local.lock().unwrap().sent.len(), before);
}

fn confirmed(child: NativeIdentity) -> CopyAttempt<i32> {
    CopyAttempt::Copied {
        identity: child,
        parent_pid: 9,
    }
}
#[test]
fn serialized_copy_publishes_before_queued_parent_fd_mutations() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", true).unwrap();
    f.seek(p, fd, Seek::Set(2)).unwrap();
    let pending = std::cell::Cell::new(false);
    let child = f
        .copy_inherit_serialized_v1(p, identity(2, 1), 9, || {
            // Simulated native parent resumption queues work; no ledger borrow.
            pending.set(true);
            confirmed(identity(2, 1))
        })
        .unwrap();
    assert!(pending.get());
    // Owner dispatches queued close/open only after the local child view exists.
    f.close(p, fd).unwrap();
    assert_eq!(f.open_read(p, b"alias", false), Ok(fd));
    assert_eq!(f.position(p, fd), Ok(0));
    assert_eq!(f.position(child, fd), Ok(2));
    let mut out = [0; MAX_READ];
    assert_eq!(f.read(child, fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
    // Copied cloexec remains true even though the replacement parent FD is false.
    f.commit_exec_close(child).unwrap();
    assert_eq!(
        f.position(child, fd),
        Err(ProcessError::Files(Failure::BadFd))
    );
    assert_eq!(f.position(p, fd), Ok(0));
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 1).count(), 2);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 1);
}
#[test]
fn serialized_copy_shares_offsets_but_separates_flags_and_last_close() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", true).unwrap();
    let child = f
        .copy_inherit_serialized_v1(p, identity(2, 1), 9, || confirmed(identity(2, 1)))
        .unwrap();
    f.set_close_on_exec(p, fd, false).unwrap();
    f.seek(p, fd, Seek::Set(3)).unwrap();
    assert_eq!(f.position(child, fd), Ok(3));
    f.commit_exec_close(p).unwrap();
    assert_eq!(f.position(p, fd), Ok(3));
    f.close(p, fd).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 0);
    h.fds.as_mut().unwrap().commit_exec_close(child).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 1);
}
#[test]
fn serialized_preflight_never_calls_copy_for_bad_or_busy_target() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let c = f.inherited_child(p, identity(2, 1), 9).unwrap();
    let foreign = Process {
        service_epoch: 99,
        ..p
    };
    for (parent, child, pid) in [
        (p, identity(2, 1), 9),
        (p, identity(3, 2), 9),
        (p, identity(3, 1), 7),
        (foreign, identity(3, 1), 9),
        (c, identity(3, 1), 10),
        (
            p,
            NativeIdentity {
                memory: 0,
                ..identity(3, 1)
            },
            9,
        ),
    ] {
        let result = f.copy_inherit_serialized_v1(parent, child, pid, || -> CopyAttempt<i32> {
            panic!("preflight must reject before native effects")
        });
        assert!(matches!(result, Err(CopyInheritanceError::BeforeCopy(_))));
    }
    assert_eq!(f.validate_binding(p), Ok(()));
    assert_eq!(f.validate_binding(c), Ok(()));
    assert!(f.records[2].process.is_none());
}
#[test]
fn serialized_known_refusal_preserves_parent_and_next_generation() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", true).unwrap();
    f.seek(p, fd, Seek::Set(4)).unwrap();
    for error in [-11, -12, -13] {
        assert_eq!(
            f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || CopyAttempt::Refused(error)),
            Err(CopyInheritanceError::Refused(error))
        );
        assert_eq!(f.position(p, fd), Ok(4));
        assert_eq!(f.cleanup(), None);
        assert!(f.records[1].process.is_none());
        assert_eq!(f.records[1].last_generation, 0);
    }
    let c = f
        .copy_inherit_serialized_v1(p, identity(2, 1), 9, || confirmed(identity(2, 1)))
        .unwrap();
    f.commit_exec_close(p).unwrap();
    assert_eq!(f.position(c, fd), Ok(4));
    f.commit_exec_close(c).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 1).count(), 1);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 1);
}
#[test]
fn serialized_unknown_retires_once_without_native_rollback_or_replay() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", false).unwrap();
    assert_eq!(
        f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || CopyAttempt::Unknown(-32)),
        Err(CopyInheritanceError::Unknown(-32))
    );
    assert_eq!(
        f.validate_binding(p),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(f.cleanup(), Some([-9, -5]));
    assert!(f.records[0].process.is_some());
    assert!(f.records[1].process.is_none());
    assert_eq!(
        f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || -> CopyAttempt<i32> {
            panic!("no replay")
        }),
        Err(CopyInheritanceError::BeforeCopy(ProcessError::Files(
            Failure::Retired
        )))
    );
    assert_eq!(h.local.lock().unwrap().closes, 1);
    assert!(!h.opcodes().contains(&3));
    assert!(!h.opcodes().contains(&4));
}
#[test]
fn serialized_unexpected_confirmed_child_retains_observation_and_retires() {
    for (actual, parent_pid) in [
        (identity(3, 1), 9),
        (identity(2, 2), 9),
        (
            NativeIdentity {
                handle: 0,
                ..identity(2, 1)
            },
            9,
        ),
        (identity(2, 1), 7),
    ] {
        let mut h = Harness::new(Fault::None, [0; 2]);
        let f = h.fds.as_mut().unwrap();
        let p = shell(f);
        let result =
            f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || CopyAttempt::<i32>::Copied {
                identity: actual,
                parent_pid,
            });
        assert_eq!(
            result,
            Err(CopyInheritanceError::Unbound {
                identity: actual,
                parent_pid,
                error: ProcessError::Stale
            })
        );
        assert_eq!(
            f.validate_binding(p),
            Err(ProcessError::Files(Failure::Retired))
        );
        assert!(f.records[0].process.is_some());
        assert!(f.records[1..].iter().all(|r| r.process.is_none()));
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}
#[test]
fn serialized_callback_unwind_closes_admission_and_keeps_process_occupancy() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        let _ = f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || -> CopyAttempt<i32> {
            panic!("unknown native copy outcome")
        });
    }));
    assert!(result.is_err());
    assert_eq!(
        f.validate_binding(p),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert!(f.records[0].process.is_some());
    assert!(f.records[1].process.is_none());
    assert_eq!(h.local.lock().unwrap().closes, 1);
}
#[test]
fn serialized_full_table_inherits_all_child_slots_without_new_source_handles() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    for fd in 3..MAX_FDS {
        assert_eq!(f.open_read(p, b"file", fd % 2 == 0), Ok(fd));
    }
    for slot in 2..=4 {
        let child = f
            .copy_inherit_serialized_v1(p, identity(slot, 1), 9, || confirmed(identity(slot, 1)))
            .unwrap();
        for fd in 3..MAX_FDS {
            assert_eq!(f.position(child, fd), Ok(0));
        }
    }
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 1).count(), 13);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 0);
}

#[test]
fn file_view_v1_exports_empty_full_holey_and_each_cloexec_bit_without_io() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    assert_eq!(f.file_view_v1(p), Ok((0, 0)));
    for fd in 3..MAX_FDS {
        assert_eq!(f.open_read(p, b"file", false), Ok(fd));
    }
    let sent = h.local.lock().unwrap().sent.len();
    for fd in 3..MAX_FDS {
        f.set_close_on_exec(p, fd, true).unwrap();
        assert_eq!(f.file_view_v1(p), Ok((0xfff8, 1 << fd)));
        f.set_close_on_exec(p, fd, false).unwrap();
    }
    assert_eq!(h.local.lock().unwrap().sent.len(), sent);
    assert_eq!(h.local.lock().unwrap().closes, 0);
    for fd in 3..MAX_FDS {
        if fd % 2 == 0 {
            f.close(p, fd).unwrap();
        } else {
            f.set_close_on_exec(p, fd, true).unwrap();
        }
    }
    let sent = h.local.lock().unwrap().sent.len();
    assert_eq!(f.file_view_v1(p), Ok((0xaaa8, 0xaaa8)));
    for fd in (3..MAX_FDS).step_by(2) {
        assert_eq!(f.position(p, fd), Ok(0));
    }
    assert_eq!(h.local.lock().unwrap().sent.len(), sent);
}

#[test]
fn file_view_v1_distinguishes_flags_at_shared_positions_in_all_views() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let fd = f.open_read(p, b"file", true).unwrap();
    assert_eq!(f.duplicate(p, fd, 15, false), Ok(15));
    f.seek(p, fd, Seek::Set(4)).unwrap();
    for slot in 2..=4 {
        let c = f.inherited_child(p, identity(slot, 1), 9).unwrap();
        f.set_close_on_exec(c, fd, false).unwrap();
        f.set_close_on_exec(c, 15, true).unwrap();
        let sent = h.local.lock().unwrap().sent.len();
        assert_eq!(f.position(c, fd), f.position(p, fd));
        assert_eq!(f.file_view_v1(c), Ok((0x8008, 0x8000)));
        assert_eq!(f.file_view_v1(p), Ok((0x8008, 8)));
        assert_eq!(h.local.lock().unwrap().sent.len(), sent);
    }
    assert_eq!(h.local.lock().unwrap().closes, 0);
}

#[test]
fn file_view_v1_rejects_foreign_stale_and_reused_process_keys_without_io() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", true).unwrap();
    let c = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.settled(c).unwrap();
    let replacement = f.inherited_child(p, identity(2, 2), 9).unwrap();
    let sent = h.local.lock().unwrap().sent.len();
    for key in [
        c,
        Process {
            service_epoch: 1,
            ..p
        },
        Process {
            identity: identity(3, 1),
            ..p
        },
        Process {
            identity: NativeIdentity {
                pid: 99,
                ..p.identity
            },
            ..p
        },
        Process {
            identity: NativeIdentity {
                slot: 0,
                ..p.identity
            },
            ..p
        },
        Process {
            identity: NativeIdentity {
                slot: 5,
                ..p.identity
            },
            ..p
        },
    ] {
        assert_eq!(f.file_view_v1(key), Err(ProcessError::Stale));
    }
    assert_eq!(f.file_view_v1(replacement), Ok((8, 8)));
    assert_eq!(f.file_view_v1(p), Ok((8, 8)));
    assert_eq!(h.local.lock().unwrap().sent.len(), sent);
    assert_eq!(h.local.lock().unwrap().closes, 0);
}

#[test]
fn file_view_v1_exact_comparison_rejects_every_bit_difference_without_parent_change() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", false).unwrap();
    f.duplicate(p, 3, 15, true).unwrap();
    f.seek(p, 3, Seek::Set(5)).unwrap();
    let sent = h.local.lock().unwrap().sent.len();
    let actual = f.file_view_v1(p).unwrap();
    assert_eq!(actual, (0x8008, 0x8000));
    // Consumer-side exact comparison includes unused low bits and flags on holes.
    for bit in 0..16 {
        assert_ne!(actual, (actual.0 ^ (1 << bit), actual.1));
        assert_ne!(actual, (actual.0, actual.1 ^ (1 << bit)));
    }
    assert_eq!(f.file_view_v1(p), Ok(actual));
    assert_eq!(f.position(p, 3), Ok(5));
    assert_eq!(f.position(p, 15), Ok(5));
    assert_eq!(h.local.lock().unwrap().sent.len(), sent);
    assert_eq!(h.local.lock().unwrap().closes, 0);
}

#[test]
fn file_view_v1_preserves_known_denial_and_refusal_but_rejects_unknown() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", true).unwrap();
    assert!(f.open_read(p, b"missing", false).is_err());
    let sent = h.local.lock().unwrap().sent.len();
    assert_eq!(f.file_view_v1(p), Ok((8, 8)));
    assert_eq!(h.local.lock().unwrap().sent.len(), sent);
    assert_eq!(
        f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || CopyAttempt::Refused(-11)),
        Err(CopyInheritanceError::Refused(-11))
    );
    assert_eq!(f.file_view_v1(p), Ok((8, 8)));
    let c = f
        .copy_inherit_serialized_v1(p, identity(2, 1), 9, || confirmed(identity(2, 1)))
        .unwrap();
    assert_eq!(f.file_view_v1(c), Ok((8, 8)));
    assert_eq!(
        f.copy_inherit_serialized_v1(p, identity(3, 1), 9, || CopyAttempt::Unknown(-32)),
        Err(CopyInheritanceError::Unknown(-32))
    );
    let sent = h.local.lock().unwrap().sent.len();
    for key in [p, c] {
        assert_eq!(
            f.file_view_v1(key),
            Err(ProcessError::Files(Failure::Retired))
        );
    }
    assert_eq!(h.local.lock().unwrap().sent.len(), sent);
    assert_eq!(h.local.lock().unwrap().closes, 1);
    assert_eq!(f.cleanup(), Some([-9, -5]));
}

#[test]
fn every_description_survives_full_occupancy_inheritance_and_flagged_close() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let mut flags = 0u16;
    for fd in 3..16 {
        let cloexec = fd % 2 == 0;
        assert_eq!(f.open_read(p, b"file", cloexec), Ok(fd));
        if cloexec {
            flags |= 1 << fd;
        }
    }
    assert_eq!(f.file_view_v1(p), Ok((0xfff8, flags)));
    assert_eq!(
        f.open_read(p, b"file", false),
        Err(ProcessError::Files(Failure::Full))
    );
    let c = f
        .copy_inherit_serialized_v1(p, identity(4, 1), 9, || confirmed(identity(4, 1)))
        .unwrap();
    for fd in 3..16 {
        f.close(p, fd).unwrap();
    }
    let closes = h
        .local
        .lock()
        .unwrap()
        .sent
        .iter()
        .filter(|f| filesystem_service::word(f, 1) == 3)
        .count();
    assert_eq!(closes, 0);
    assert_eq!(f.file_view_v1(c), Ok((0xfff8, flags)));
    let mut bytes = [0xa5; MAX_READ];
    for fd in 3..16 {
        assert_eq!(f.read(c, fd, 2, &mut bytes), Ok(2));
        assert_eq!(&bytes[..2], b"ab");
        assert_eq!(f.position(c, fd), Ok(2));
    }
    f.commit_exec_close(c).unwrap();
    assert_eq!(f.file_view_v1(c), Ok((0xfff8 & !flags, 0)));
    for fd in (3..16).step_by(2) {
        assert_eq!(f.read(c, fd, 2, &mut bytes), Ok(2));
        assert_eq!(&bytes[..2], b"cd");
    }
    f.settled(c).unwrap();
    f.settled(p).unwrap();
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 13);
}

#[test]
fn checked_disconnect_requires_empty_views_and_verification_before_raw_close() {
    for verification in [Ok(()), Err(filesystem_client::Error::Transport(-32))] {
        for closes in [[0; 2], [-9, -5]] {
            let mut h = Harness::new(Fault::None, closes);
            let observed = h.local.clone();
            let f = h.fds.as_mut().unwrap();
            let p = shell(f);
            assert_eq!(
                f.disconnect_checked(|_| panic!("live views must prevent verification")),
                Err(ProcessError::Busy)
            );
            f.settled(p).unwrap();
            let mut calls = 0;
            let outcome = f.disconnect_checked(|_| {
                let prior = observed.lock().unwrap().closes;
                assert_eq!(prior, 0);
                calls += 1;
                verification
            });
            assert_eq!(calls, 1);
            assert_eq!(
                outcome,
                verification
                    .map(|_| closes)
                    .map_err(|e| ProcessError::Files(Failure::Source(e)))
            );
            assert_eq!(f.cleanup(), Some(closes));
            assert!(f
                .disconnect_checked(|_| panic!("never repeat verification"))
                .is_err());
            let state = observed.lock().unwrap();
            assert_eq!(state.closes, 1);
            assert_eq!(
                state
                    .sent
                    .iter()
                    .filter(|f| filesystem_service::word(f, 1) == 4)
                    .count(),
                1
            );
        }
    }
}

#[cfg(fs_replace)]
#[path = "replace-tests.rs"]
mod replacement_tests;

#[cfg(all(fs_cwd, not(fs_cwd_wire)))]
#[path = "process-cwd-tests.rs"]
mod cwd_tests;
