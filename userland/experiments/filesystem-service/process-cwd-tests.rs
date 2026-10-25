// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_client::Error as SourceError;
use filesystem_service::{word, MAGIC};
use std::{vec, vec::Vec};

fn sent_len(h: &Harness) -> usize {
    h.local.lock().unwrap().sent.len()
}
fn rows(h: &Harness, opcode: u64) -> Vec<filesystem_service::Message> {
    h.local
        .lock()
        .unwrap()
        .sent
        .iter()
        .filter(|row| row[..8] == MAGIC[..] && word(row, 1) == opcode)
        .copied()
        .collect()
}
fn close_tokens(h: &Harness) -> Vec<u64> {
    rows(h, 3).iter().map(|row| word(row, 3)).collect()
}
fn source(error: SourceError) -> ProcessError {
    ProcessError::Files(Failure::Source(error))
}

#[test]
fn root_admission_and_relative_reads_use_exact_retained_directory() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    assert!(f.records.iter().all(|record| record.cwd.is_none()));
    f.change_directory(p, b"dir/dir").unwrap();
    let cwd = f.records[0].cwd;
    assert!(cwd.is_some());
    let fd = f.open_read(p, b"file", false).unwrap();
    let mut out = [0; MAX_READ];
    assert_eq!(f.read(p, fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    f.close(p, fd).unwrap();
    assert_eq!(f.records[0].cwd, cwd);
    let lookups = rows(&h, 1);
    assert_eq!(
        lookups
            .iter()
            .map(|row| (word(row, 3), word(row, 4)))
            .collect::<Vec<_>>(),
        vec![(1, 3), (2, 3), (3, 2)]
    );
    assert_eq!(close_tokens(&h), vec![2, 4]);
    let f = h.fds.as_mut().unwrap();
    f.settled(p).unwrap();
    assert!(f.records[0].cwd.is_none());
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(close_tokens(&h), vec![2, 4, 3]);
}

#[test]
fn inherited_directory_is_shared_until_final_reference_and_chdir_is_local() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let original = f.records[0].cwd;
    let mut children = Vec::new();
    for slot in 2..=4 {
        let child = f.inherited_child(p, identity(slot, 1), 9).unwrap();
        assert_eq!(f.records[slot as usize - 1].cwd, original);
        children.push(child);
    }
    f.change_directory(children[0], b"dir").unwrap();
    assert_ne!(f.records[1].cwd, original);
    assert_eq!(f.records[0].cwd, original);
    assert_eq!(f.records[2].cwd, original);
    assert_eq!(close_tokens(&h), Vec::<u64>::new());
    let f = h.fds.as_mut().unwrap();
    f.change_directory(p, b"/").unwrap();
    assert!(f.records[0].cwd.is_none());
    assert_eq!(close_tokens(&h), Vec::<u64>::new());
    let f = h.fds.as_mut().unwrap();
    f.settled(children[1]).unwrap();
    f.settled(children[2]).unwrap();
    assert_eq!(close_tokens(&h), vec![2]);
    let f = h.fds.as_mut().unwrap();
    let fd = f.open_read(children[0], b"file", false).unwrap();
    f.close(children[0], fd).unwrap();
    f.settled(children[0]).unwrap();
    f.settled(p).unwrap();
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(close_tokens(&h), vec![2, 4, 3]);
}

#[test]
fn successful_exec_closes_flagged_files_but_preserves_cwd_and_absolute_root() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let cwd = f.records[0].cwd;
    f.open_read(p, b"file", true).unwrap();
    f.commit_exec_close(p).unwrap();
    assert_eq!(f.file_view_v1(p), Ok((0, 0)));
    assert_eq!(f.records[0].cwd, cwd);
    f.open_read(p, b"/file", false).unwrap();
    f.open_read(p, b"file", false).unwrap();
    let bases = rows(&h, 1)
        .iter()
        .map(|row| word(row, 3))
        .collect::<Vec<_>>();
    assert_eq!(bases, vec![1, 2, 1, 2]);
    h.fds.as_mut().unwrap().settled(p).unwrap();
    assert_eq!(close_tokens(&h), vec![3, 4, 5, 2]);
}

#[test]
fn canonical_denials_and_known_errors_preserve_current_directory() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let cwd = f.records[0].cwd;
    let before = sent_len(&h);
    let f = h.fds.as_mut().unwrap();
    for name in [
        b"".as_slice(),
        b"..",
        b"dir/../dir",
        b"dir/./dir",
        b"//dir",
        b"dir/",
        b"a\0b",
        &[b'a'; 256],
    ] {
        assert!(f.change_directory(p, name).is_err());
        assert_eq!(f.records[0].cwd, cwd);
    }
    f.change_directory(p, b".").unwrap();
    assert_eq!(f.records[0].cwd, cwd);
    assert_eq!(sent_len(&h), before);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.change_directory(p, b"missing"),
        Err(source(SourceError::Remote(-2)))
    );
    assert_eq!(
        f.change_directory(p, b"file"),
        Err(source(SourceError::Remote(-20)))
    );
    assert_eq!(f.records[0].cwd, cwd);
    let fd = f.open_read(p, b"file", false).unwrap();
    f.close(p, fd).unwrap();
    f.settled(p).unwrap();
    assert_eq!(f.disconnect(), Ok([0; 2]));
}

#[test]
fn stale_and_foreign_process_keys_cannot_change_any_cwd() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.settled(child).unwrap();
    let replacement = f.inherited_child(p, identity(2, 2), 9).unwrap();
    let cwd = f.records[0].cwd;
    let before = sent_len(&h);
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
        assert_eq!(f.change_directory(stale, b"/"), Err(ProcessError::Stale));
        assert_eq!(f.change_directory(stale, b"dir"), Err(ProcessError::Stale));
    }
    assert_eq!(f.records[0].cwd, cwd);
    assert_eq!(f.records[1].cwd, cwd);
    assert_eq!(sent_len(&h), before);
    let f = h.fds.as_mut().unwrap();
    f.settled(replacement).unwrap();
    f.settled(p).unwrap();
    assert_eq!(close_tokens(&h), vec![2]);
}

#[test]
fn directory_slots_and_full_fd_preflight_do_not_expand_resource_limits() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let cwd = f.records[0].cwd;
    for _ in 0..13 {
        f.open_read(p, b"file", false).unwrap();
    }
    let before = sent_len(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.change_directory(p, b"dir/dir"),
        Err(source(SourceError::Full))
    );
    assert_eq!(
        f.open_read(p, b"file", false),
        Err(ProcessError::Files(Failure::Full))
    );
    assert_eq!(f.records[0].cwd, cwd);
    assert_eq!(sent_len(&h), before);
    let f = h.fds.as_mut().unwrap();
    // One free source slot is sufficient for a single-component replacement.
    f.change_directory(p, b"dir").unwrap();
    assert_ne!(f.records[0].cwd, cwd);
    f.settled(p).unwrap();
    assert_eq!(f.disconnect(), Ok([0; 2]));
}

#[test]
fn failed_old_directory_close_retires_without_publishing_prepared_replacement() {
    let mut h = Harness::new(Fault::Close, [-7, -9]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let cwd = f.records[0].cwd;
    assert_eq!(
        f.change_directory(p, b"dir"),
        Err(source(SourceError::Transport(-32)))
    );
    assert_eq!(f.records[0].cwd, cwd);
    assert_eq!(f.cleanup(), Some([-7, -9]));
    let before = sent_len(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.change_directory(p, b"/"),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(f.settled(p), Err(ProcessError::Files(Failure::Retired)));
    assert!(f.records[0].process.is_some());
    assert_eq!(sent_len(&h), before);
    assert_eq!(close_tokens(&h), vec![2]);
}

#[test]
fn failed_final_directory_release_preserves_occupancy_and_generation_history() {
    let mut h = Harness::new(Fault::Close, [-7, -9]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    f.settled(p).unwrap();
    assert_eq!(f.settled(child), Err(source(SourceError::Transport(-32))));
    assert_eq!(f.records[1].process, Some(child));
    assert_eq!(f.records[1].last_generation, 1);
    assert!(f.records[1].cwd.is_some());
    assert_eq!(f.cleanup(), Some([-7, -9]));
    assert_eq!(close_tokens(&h), vec![2]);
}

#[test]
fn refused_unknown_and_unwound_copy_preserve_directory_ownership_obligations() {
    for mode in 0..3 {
        let mut h = Harness::new(Fault::None, [0; 2]);
        let f = h.fds.as_mut().unwrap();
        let p = shell(f);
        f.change_directory(p, b"dir").unwrap();
        let cwd = f.records[0].cwd;
        if mode == 2 {
            let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                let _ = f.copy_inherit_serialized_v1::<i32>(p, identity(2, 1), 9, || {
                    panic!("unknown copy")
                });
            }));
            assert!(result.is_err());
        } else {
            let result = f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || {
                if mode == 0 {
                    CopyAttempt::Refused(-11)
                } else {
                    CopyAttempt::Unknown(-5)
                }
            });
            assert!(result.is_err());
        }
        assert_eq!(f.records[0].cwd, cwd);
        assert!(f.records[1].cwd.is_none());
        assert!(f.records[1].process.is_none());
        if mode == 0 {
            assert_eq!(f.cleanup(), None);
            f.settled(p).unwrap();
            assert_eq!(f.disconnect(), Ok([0; 2]));
        } else {
            assert_eq!(f.cleanup(), Some([0; 2]));
            assert_eq!(
                f.change_directory(p, b"/"),
                Err(ProcessError::Files(Failure::Retired))
            );
        }
    }
}

#[test]
fn serialized_copy_preserves_cwd_and_settlement_closes_inherited_handle_once() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let cwd = f.records[0].cwd;
    let child = f
        .copy_inherit_serialized_v1(p, identity(2, 1), 9, || CopyAttempt::<i32>::Copied {
            identity: identity(2, 1),
            parent_pid: 9,
        })
        .unwrap();
    assert_eq!(f.records[1].cwd, cwd);
    f.settled(p).unwrap();
    let fd = f.open_read(child, b"file", false).unwrap();
    f.close(child, fd).unwrap();
    f.settled(child).unwrap();
    assert!(f.records.iter().all(|record| record.cwd.is_none()));
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(close_tokens(&h), vec![3, 2]);
}

#[test]
fn uncertain_directory_lookup_retires_every_view_without_changing_retained_labels() {
    let mut h = Harness::new(Fault::LookupBelowRoot, [-7, -9]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    let cwd = f.records[0].cwd;
    assert_eq!(
        f.change_directory(child, b"dir"),
        Err(source(SourceError::Transport(-32)))
    );
    assert_eq!(f.records[0].cwd, cwd);
    assert_eq!(f.records[1].cwd, cwd);
    assert_eq!(f.records[1].process, Some(child));
    assert_eq!(f.cleanup(), Some([-7, -9]));
    let before = sent_len(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.change_directory(p, b"/"),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(
        f.open_read(child, b"file", false),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(sent_len(&h), before);
    assert_eq!(close_tokens(&h), Vec::<u64>::new());
}

#[test]
fn four_retained_directories_compete_with_files_for_existing_sixteen_bindings() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    f.change_directory(p, b"dir").unwrap();
    let mut children = Vec::new();
    for slot in 2..=4 {
        let child = f.inherited_child(p, identity(slot, 1), 9).unwrap();
        f.change_directory(child, b"dir").unwrap();
        children.push(child);
    }
    let mut files = Vec::new();
    for _ in 0..11 {
        files.push(f.open_read(p, b"file", false).unwrap());
    }
    let before = sent_len(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.open_read(p, b"file", false),
        Err(source(SourceError::Full))
    );
    assert_eq!(
        f.change_directory(p, b"dir"),
        Err(source(SourceError::Full))
    );
    assert_eq!(f.cleanup(), None);
    assert_eq!(sent_len(&h), before);
    let f = h.fds.as_mut().unwrap();
    f.close(p, files.pop().unwrap()).unwrap();
    files.push(f.open_read(p, b"file", false).unwrap());
    for file in files {
        f.close(p, file).unwrap();
    }
    for child in children {
        f.settled(child).unwrap();
    }
    f.settled(p).unwrap();
    assert!(f.records.iter().all(|record| record.cwd.is_none()));
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(close_tokens(&h).len(), 16);
}
