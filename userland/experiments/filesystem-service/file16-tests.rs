// SPDX-License-Identifier: BSD-2-Clause
use super::*;
#[path = "process-fd-fixture.rs"]
mod fixture;
use fixture::{Fault, Harness};

fn identity(slot: u32, epoch: u32) -> NativeIdentity {
    NativeIdentity::admitted(
        slot,
        epoch,
        0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
fn shell<T: Channel>(files: &mut ProcessFiles<T>) -> Process {
    files.admitted_shell(identity(1, 1), 7).unwrap()
}
fn confirmed(child: NativeIdentity) -> CopyAttempt<i32> {
    CopyAttempt::Copied {
        identity: child,
        parent_pid: 9,
    }
}
fn closes(h: &Harness) -> usize {
    h.opcodes().iter().filter(|&&op| op == 3).count()
}
fn sent(h: &Harness) -> usize {
    h.local.lock().unwrap().sent.len()
}

#[test]
fn thirteen_descriptions_sixteen_aliases_and_full_table_exact_replacement() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    assert_eq!(super::super::FIRST_FILE_FD, 0);
    assert_eq!(f.files.descriptions.len(), 13);
    for fd in 0..13 {
        assert_eq!(f.open_read(p, b"file", true), Ok(fd));
    }
    let before = sent(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.open_read(p, b"file", false),
        Err(ProcessError::Files(Failure::Full))
    );
    for fd in 13..16 {
        assert_eq!(f.duplicate(p, 12, 0, true), Ok(fd));
    }
    assert_eq!(f.file_view_v1(p), Ok((0xffff, 0xffff)));
    assert_eq!(
        f.duplicate(p, 12, 0, false),
        Err(ProcessError::Files(Failure::Full))
    );
    assert_eq!(
        f.open_read(p, b"file", false),
        Err(ProcessError::Files(Failure::Full))
    );
    assert_eq!(sent(&h), before);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.replace(p, 15, 0), Ok(0));
    assert_eq!(f.file_view_v1(p), Ok((0xffff, 0xfffe)));
    assert_eq!(f.replace(p, 15, 15), Ok(15));
    assert_eq!(f.file_view_v1(p), Ok((0xffff, 0xfffe)));
    let mut out = [0xa5; MAX_READ];
    assert_eq!(f.read(p, 15, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(f.read(p, 0, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
    assert!(out[2..].iter().all(|&v| v == 0));
    assert_eq!(f.read(p, 1, 1, &mut out), Ok(1));
    assert_eq!(out[0], b'a');
    assert_eq!(closes(&h), 1);
    assert_eq!(h.storage.lock().unwrap().lookups, 13);
    assert_eq!(h.storage.lock().unwrap().reads, 3);
}

#[test]
fn low_alias_flags_and_inherited_victim_last_close_are_view_local() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    assert_eq!(f.open_read(p, b"file", true), Ok(0));
    assert_eq!(f.open_read(p, b"alias", true), Ok(1));
    assert_eq!(f.replace(p, 0, 2), Ok(2));
    f.set_close_on_exec(p, 2, true).unwrap();
    let mut children = std::vec::Vec::new();
    for slot in 2..=4 {
        children.push(f.inherited_child(p, identity(slot, 1), 9).unwrap());
    }
    assert_eq!(f.replace(p, 0, 1), Ok(1));
    assert_eq!(closes(&h), 0);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.replace(p, 0, 2), Ok(2));
    assert_eq!(f.file_view_v1(p), Ok((7, 1)));
    for child in &children {
        assert_eq!(f.file_view_v1(*child), Ok((7, 7)));
    }
    f.set_close_on_exec(children[0], 0, false).unwrap();
    assert_eq!(f.file_view_v1(p), Ok((7, 1)));
    assert_eq!(f.file_view_v1(children[0]), Ok((7, 6)));
    f.seek(p, 2, Seek::Set(2)).unwrap();
    assert_eq!(f.position(children[2], 0), Ok(2));
    assert_eq!(f.position(children[2], 1), Ok(0));
    f.close(children[0], 1).unwrap();
    f.close(children[1], 1).unwrap();
    assert_eq!(closes(&h), 0);
    h.fds.as_mut().unwrap().close(children[2], 1).unwrap();
    assert_eq!(closes(&h), 1);
    let f = h.fds.as_mut().unwrap();
    f.commit_exec_close(p).unwrap();
    assert_eq!(f.file_view_v1(p), Ok((6, 0)));
    assert_eq!(f.position(p, 1), Ok(2));
    f.settled(p).unwrap();
    for child in children {
        f.settled(child).unwrap();
    }
    assert_eq!(closes(&h), 2);
}

#[test]
fn exact_keys_invalid_indices_and_failed_open_have_no_source_effects() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    assert_eq!(
        f.open_read(p, b"missing", false),
        Err(ProcessError::Files(Failure::Source(
            filesystem_client::Error::Remote(-2)
        )))
    );
    assert_eq!(f.open_read(p, b"file", true), Ok(0));
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.settled(child).unwrap();
    let replacement = f.inherited_child(p, identity(2, 2), 9).unwrap();
    let before = sent(&h);
    let f = h.fds.as_mut().unwrap();
    for stale in [
        child,
        Process {
            service_epoch: 1,
            ..p
        },
        Process {
            identity: NativeIdentity {
                pid: 99,
                ..p.identity
            },
            ..p
        },
    ] {
        assert_eq!(f.replace(stale, 0, 1), Err(ProcessError::Stale));
    }
    for (from, to) in [(-1, 0), (16, 0), (1, 0), (0, -1), (0, 16)] {
        assert_eq!(
            f.replace(p, from, to),
            Err(ProcessError::Files(Failure::BadFd))
        );
    }
    for minimum in [-1, 16] {
        assert_eq!(
            f.duplicate(p, 0, minimum, false),
            Err(ProcessError::Files(Failure::Invalid))
        );
    }
    assert_eq!(f.file_view_v1(p), Ok((1, 1)));
    assert_eq!(f.file_view_v1(replacement), Ok((1, 1)));
    assert_eq!(f.position(p, 0), Ok(0));
    assert_eq!(sent(&h), before);
}

#[test]
fn failed_last_victim_close_retires_all_views_and_never_replays() {
    let mut h = Harness::new(Fault::Close, [-9, -5]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", false).unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.open_read(p, b"alias", false).unwrap();
    assert!(matches!(
        f.replace(p, 0, 1),
        Err(ProcessError::Files(Failure::Source(_)))
    ));
    assert_eq!(f.cleanup(), Some([-9, -5]));
    let before = sent(&h);
    let f = h.fds.as_mut().unwrap();
    for key in [p, child] {
        assert_eq!(
            f.file_view_v1(key),
            Err(ProcessError::Files(Failure::Retired))
        );
        assert_eq!(
            f.replace(key, 0, 1),
            Err(ProcessError::Files(Failure::Retired))
        );
    }
    assert_eq!(sent(&h), before);
    assert_eq!(closes(&h), 1);
    assert_eq!(h.local.lock().unwrap().closes, 1);
}

#[test]
fn read_errors_overflow_and_invalid_count_preserve_zeroed_output() {
    for fault in [Fault::None, Fault::ReadBody, Fault::Count] {
        let mut h = Harness::new(fault, [0; 2]);
        let f = h.fds.as_mut().unwrap();
        let p = shell(f);
        f.open_read(p, b"file", false).unwrap();
        let mut out = [0xa5; MAX_READ];
        assert_eq!(
            f.read(p, -1, 1, &mut out),
            Err(ProcessError::Files(Failure::BadFd))
        );
        assert_eq!(out, [0; MAX_READ]);
        assert_eq!(f.seek(p, 0, Seek::Set(i64::MAX)), Ok(i64::MAX as u64));
        assert_eq!(
            f.read(p, 0, 1, &mut out),
            Err(ProcessError::Files(Failure::Overflow))
        );
        assert_eq!(f.position(p, 0), Ok(i64::MAX as u64));
        assert_eq!(f.seek(p, 0, Seek::End(0)), Ok(6));
        f.seek(p, 0, Seek::Set(0)).unwrap();
        if fault == Fault::None {
            h.storage.lock().unwrap().deny_read = true;
            assert_eq!(
                f.read(p, 0, 2, &mut out),
                Err(ProcessError::Files(Failure::Source(
                    filesystem_client::Error::Remote(-13)
                )))
            );
            assert_eq!(f.position(p, 0), Ok(0));
            assert_eq!(f.cleanup(), None);
        } else {
            assert!(matches!(
                f.read(p, 0, 2, &mut out),
                Err(ProcessError::Files(Failure::Source(_)))
            ));
            assert_eq!(
                f.file_view_v1(p),
                Err(ProcessError::Files(Failure::Retired))
            );
        }
        assert_eq!(out, [0; MAX_READ]);
    }
}

#[test]
fn serialized_copy_requires_exact_observation_and_retires_unknown() {
    for unexpected in [false, true] {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let f = h.fds.as_mut().unwrap();
        let p = shell(f);
        f.open_read(p, b"file", true).unwrap();
        let result = f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || {
            if unexpected {
                confirmed(identity(3, 1))
            } else {
                CopyAttempt::Unknown(-32)
            }
        });
        if unexpected {
            assert!(matches!(result, Err(CopyInheritanceError::Unbound { .. })));
        } else {
            assert_eq!(result, Err(CopyInheritanceError::Unknown(-32)));
        }
        assert_eq!(
            f.validate_binding(p),
            Err(ProcessError::Files(Failure::Retired))
        );
        assert_eq!(f.cleanup(), Some([-9, -5]));
        assert_eq!(
            f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || -> CopyAttempt<i32> {
                panic!("no replay")
            }),
            Err(CopyInheritanceError::BeforeCopy(ProcessError::Files(
                Failure::Retired
            )))
        );
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}

#[test]
fn copy_then_parent_mutation_preserves_child_and_generation_history() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", true).unwrap();
    f.seek(p, 0, Seek::Set(4)).unwrap();
    assert_eq!(
        f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || CopyAttempt::Refused(-11)),
        Err(CopyInheritanceError::Refused(-11))
    );
    assert_eq!(f.file_view_v1(p), Ok((1, 1)));
    let child = f
        .copy_inherit_serialized_v1(p, identity(2, 1), 9, || confirmed(identity(2, 1)))
        .unwrap();
    f.close(p, 0).unwrap();
    assert_eq!(f.open_read(p, b"alias", false), Ok(0));
    assert_eq!(f.position(child, 0), Ok(4));
    assert_eq!(f.position(p, 0), Ok(0));
    f.commit_exec_close(child).unwrap();
    assert_eq!(f.file_view_v1(child), Ok((0, 0)));
    f.settled(child).unwrap();
    assert_eq!(
        f.inherited_child(p, identity(2, 1), 9),
        Err(ProcessError::Generation)
    );
    assert!(f.inherited_child(p, identity(2, 2), 9).is_ok());
    assert_eq!(closes(&h), 1);
}

#[test]
fn disconnect_requires_every_live_view_and_source_closes_once() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", false).unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.settled(p).unwrap();
    assert_eq!(f.admitted_shell(identity(1, 2), 7), Err(ProcessError::Busy));
    assert_eq!(f.disconnect(), Err(ProcessError::Busy));
    f.settled(child).unwrap();
    assert_eq!(f.disconnect(), Ok([-9, -5]));
    assert_eq!(h.local.lock().unwrap().closes, 1);
    assert_eq!(closes(&h), 1);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 4).count(), 1);
}

#[test]
fn high_aliases_close_on_exec_and_poisoned_views_do_not_escape_settlement() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.open_read(p, b"file", true).unwrap();
    assert_eq!(f.duplicate(p, 0, 15, true), Ok(15));
    assert_eq!(f.file_view_v1(p), Ok((0x8001, 0x8001)));
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.commit_exec_close(child).unwrap();
    assert_eq!(f.file_view_v1(child), Ok((0, 0)));
    assert_eq!(f.file_view_v1(p), Ok((0x8001, 0x8001)));
    f.settled(child).unwrap();
    let next = f.inherited_child(p, identity(2, 2), 9).unwrap();
    assert_eq!(f.file_view_v1(next), Ok((0x8001, 0x8001)));
    f.settled(next).unwrap();
    f.settled(p).unwrap();
    assert_eq!(closes(&h), 1);
}

#[cfg(all(fs_cwd, not(fs_cwd_wire)))]
#[path = "process-cwd-tests.rs"]
mod cwd_tests;
