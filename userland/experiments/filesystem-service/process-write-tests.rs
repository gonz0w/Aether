// SPDX-License-Identifier: BSD-2-Clause
//! AF09 broker mutations over the actual service and hostile client transport.
use super::*;
use filesystem_client::{MutationOutcome as Outcome, MutationProgress as Progress};
use filesystem_remote_descriptors::{
    Failure, HomeAccess, NativeIdentity, Process, ProcessError, ProcessFiles, ProcessWriteFailure,
    Seek,
};

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
fn response(code: i64, txg: u64, bytes: u64, state: u64) -> Message {
    let mut f = message(91, code as u64);
    put(&mut f, 4, txg);
    put(&mut f, 5, bytes);
    put(&mut f, 6, state);
    f
}
fn scripted(reply: Result<Message, i64>) -> (ProcessFiles<Script>, Process, i32, Observed) {
    let mut entry = greeting(3);
    put(&mut entry, 4, 2);
    put(&mut entry, 5, 4);
    let (io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2)), Ok(entry), reply]);
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let p = shell(&mut f);
    let fd = f
        .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
        .unwrap();
    seen.lock().unwrap().sent.clear();
    (f, p, fd, seen)
}
fn check_retired(
    mut f: ProcessFiles<Script>,
    p: Process,
    fd: i32,
    seen: Observed,
    receipt: ProcessWriteFailure,
) {
    assert_eq!(receipt.cleanup, Some([-9, -5]), "PROCESS_WRITE_RETIRE");
    let sends = seen.lock().unwrap().sent.len();
    let later = f.write(p, fd, b"x").unwrap_err();
    assert_eq!(
        later.error,
        ProcessError::Files(Failure::Retired),
        "PROCESS_WRITE_RETIRE"
    );
    assert_eq!(later.outcome, Outcome::NotSent);
    assert_eq!(later.offset, None);
    assert_eq!(later.cleanup, receipt.cleanup);
    assert_eq!(f.settled(p), Err(ProcessError::Files(Failure::Retired)));
    assert_eq!(
        f.admitted_shell(identity(1, 2), 7),
        Err(ProcessError::Files(Failure::Retired))
    );
    f.abort();
    drop(f);
    assert_eq!(
        seen.lock().unwrap().sent.len(),
        sends,
        "PROCESS_WRITE_NO_REPLAY"
    );
    assert_eq!(seen.lock().unwrap().closes, 1);
}

#[test]
fn actual_shared_alias_inheritance_and_independent_positions() {
    let (io, join, state, seen, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let p = shell(&mut f);
    let fd = f
        .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
        .expect("PROCESS_HOME_BINDING");
    let alias = f.duplicate(p, fd, 0, true).unwrap();
    let separate = f
        .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
        .unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    assert_eq!(f.write(p, alias, b"ho").unwrap().bytes, 2);
    assert_eq!(f.position(child, fd), Ok(2), "PROCESS_WRITE_OFFSET");
    assert_eq!(f.position(p, separate), Ok(0));
    assert_eq!(f.write(child, fd, b"me").unwrap().bytes, 2);
    assert_eq!(f.position(p, alias), Ok(4), "PROCESS_WRITE_OFFSET");
    f.seek(p, separate, Seek::Set(0)).unwrap();
    let mut out = [0; 4096];
    assert_eq!(f.read(p, separate, 4, &mut out), Ok(4));
    assert_eq!(&out[..4], b"home", "PROCESS_HOME_BINDING");
    f.replace(p, alias, separate).unwrap();
    assert_eq!(f.position(p, separate), Ok(4));
    f.commit_exec_close(p).unwrap();
    assert_eq!(
        f.position(p, alias),
        Err(ProcessError::Files(Failure::BadFd))
    );
    assert_eq!(f.position(child, alias), Ok(4));
    f.settled(p).unwrap();
    assert_eq!(f.position(child, fd), Ok(4));
    f.settled(child).unwrap();
    assert_eq!(f.disconnect(), Ok([0, 0]));
    drop(f);
    assert_eq!(join.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 2);
    assert_eq!(state.lock().unwrap().drops, 1);
    let closes = seen
        .lock()
        .unwrap()
        .sent
        .iter()
        .filter(|r| &r[..8] == filesystem_service::MAGIC && word(r, 1) == 3)
        .count();
    assert_eq!(closes, 2, "PROCESS_LAST_CLOSE");
}

#[test]
fn actual_modes_root_and_directory_rejection_preserve_authority() {
    let (io, join, state, seen, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let p = shell(&mut f);
    let root = f.open_read(p, b"system", false).unwrap();
    let read = f
        .open_home_file(p, b"data", HomeAccess::ReadOnly, false)
        .unwrap();
    for fd in [root, read] {
        let before = seen.lock().unwrap().sent.len();
        let e = f.write(p, fd, b"x").expect_err("PROCESS_WRITE_RIGHTS");
        assert_eq!(e.outcome, Outcome::NotSent);
        assert_eq!(e.offset, Some(0));
        assert_eq!(e.cleanup, None);
        assert_eq!(
            seen.lock().unwrap().sent.len(),
            before,
            "PROCESS_WRITE_RIGHTS"
        );
        assert_eq!(f.position(p, fd), Ok(0));
    }
    let write = f
        .open_home_file(p, b"data", HomeAccess::WriteOnly, false)
        .unwrap();
    let before = seen.lock().unwrap().sent.len();
    let mut out = [0xa5; 4096];
    assert_eq!(
        f.read(p, write, 1, &mut out),
        Err(ProcessError::Files(Failure::Source(Error::Invalid)))
    );
    assert!(out.iter().all(|b| *b == 0));
    assert_eq!(seen.lock().unwrap().sent.len(), before);
    assert_eq!(f.write(p, write, b"x").unwrap().bytes, 1);
    assert_eq!(
        f.open_home_file(p, b"nested", HomeAccess::ReadOnly, false),
        Err(ProcessError::Files(Failure::Source(Error::Remote(-21))))
    );
    assert_eq!(f.file_view_v1(p), Ok((7, 0)));
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    assert_eq!(join.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 1);
}

#[test]
fn actual_remote_capacity_and_full_alias_preflight_have_no_leaks() {
    let (io, join, state, seen, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let p = shell(&mut f);
    for fd in 0..12 {
        assert_eq!(
            f.open_home_file(p, b"data", HomeAccess::ReadWrite, false),
            Ok(fd)
        );
    }
    assert_eq!(
        f.open_home_file(p, b"data", HomeAccess::ReadWrite, false),
        Err(ProcessError::Files(Failure::Source(Error::Remote(-28))))
    );
    for fd in 12..16 {
        assert_eq!(f.duplicate(p, 0, 0, false), Ok(fd));
    }
    let before = seen.lock().unwrap().sent.len();
    assert_eq!(
        f.open_home_file(p, b"data", HomeAccess::ReadWrite, false),
        Err(ProcessError::Files(Failure::Full))
    );
    assert_eq!(
        seen.lock().unwrap().sent.len(),
        before,
        "PROCESS_WRITE_CAPACITY"
    );
    assert_eq!(f.file_view_v1(p), Ok((0xffff, 0)));
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    assert_eq!(join.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().lookups, 13); // source home + twelve admitted lookups
    assert_eq!(state.lock().unwrap().drops, 1);
}

#[test]
fn local_bounds_names_and_stale_process_never_send() {
    let (mut f, p, fd, seen) = scripted(Err(-32));
    for (offset, bytes) in [(0, &b""[..]), (0, &[0; 4097][..]), (i64::MAX, &b"x"[..])] {
        f.seek(p, fd, Seek::Set(offset)).unwrap();
        let error = f.write(p, fd, bytes).unwrap_err();
        assert_eq!(error.outcome, Outcome::NotSent);
        assert_eq!(error.offset, Some(offset as u64));
        assert_eq!(error.cleanup, None);
        assert_eq!(f.position(p, fd), Ok(offset as u64));
    }
    assert_eq!(f.write(p, 16, b"x").unwrap_err().offset, None);
    for name in [
        &b""[..],
        b".",
        b"..",
        b"/data",
        b"a/b",
        b"a\0",
        &[b'a'; 256],
    ] {
        assert_eq!(
            f.open_home_file(p, name, HomeAccess::ReadWrite, false),
            Err(ProcessError::Files(Failure::Source(Error::Invalid)))
        );
    }
    let (io, _) = script(vec![Ok(greeting(1)), Ok(greeting(2))]);
    let mut other = ProcessFiles::connect_home(io, 92).err(); // wrong epoch cannot publish
    assert!(other.take().is_some());
    let (io, _) = script(vec![Ok(greeting(1)), Ok(greeting(2))]);
    let mut other = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let mut foreign_id = identity(1, 1);
    // A distinct current key uses its actual process generation, never a user FD.
    let foreign = other.admitted_shell(foreign_id, 7).unwrap();
    other.settled(foreign).unwrap();
    foreign_id = identity(1, 2);
    let foreign = other.admitted_shell(foreign_id, 7).unwrap();
    let receipt = f.write(foreign, fd, b"x").unwrap_err();
    assert_eq!(
        receipt.error,
        ProcessError::Stale,
        "PROCESS_WRITE_EXACT_KEY"
    );
    assert_eq!(receipt.outcome, Outcome::NotSent);
    assert_eq!(receipt.offset, None);
    assert!(
        seen.lock().unwrap().sent.is_empty(),
        "PROCESS_WRITE_PREFLIGHT"
    );
    f.abort();
}

#[test]
fn all_remote_progress_and_attempted_offsets_survive_retirement_and_drop() {
    for (code, txg, bytes, state, expected) in [
        (-28, 0, 0, 0, Progress::Unassigned),
        (
            -5,
            0,
            1,
            1,
            Progress::Committed {
                txg: 0,
                bytes_staged: 1,
            },
        ),
        (
            -5,
            17,
            1,
            2,
            Progress::Completed {
                txg: 17,
                bytes_staged: 1,
            },
        ),
        (-5, 0, 0, 3, Progress::Unknown),
    ] {
        let (mut f, p, fd, seen) = scripted(Ok(response(code, txg, bytes, state)));
        f.seek(p, fd, Seek::Set(3)).unwrap();
        let e = f.write(p, fd, b"x").expect_err("PROCESS_WRITE_PROGRESS");
        assert_eq!(
            e.error,
            ProcessError::Files(Failure::Source(Error::Remote(code)))
        );
        assert_eq!(
            e.outcome,
            Outcome::Reported(expected),
            "PROCESS_WRITE_PROGRESS"
        );
        assert_eq!(e.offset, Some(3), "PROCESS_WRITE_ATTEMPT");
        check_retired(f, p, fd, seen, e);
        assert_eq!(e.outcome, Outcome::Reported(expected));
        assert_eq!(e.offset, Some(3));
    }
}

#[test]
fn malformed_and_receive_loss_retain_unknown_attempt_once() {
    for reply in [Err(-32), Ok(response(0, 0, 1, 2)), Ok(response(0, 4, 2, 2))] {
        let (mut f, p, fd, seen) = scripted(reply);
        let e = f.write(p, fd, b"x").expect_err("PROCESS_WRITE_UNKNOWN");
        assert_eq!(e.outcome, Outcome::Unknown);
        assert_eq!(e.offset, Some(0));
        check_retired(f, p, fd, seen, e);
    }
}

#[test]
fn constructor_validates_both_greetings_and_old_entry_refuses_before_input() {
    let (io, seen) = script(vec![Ok(greeting(1)), Err(-32)]);
    let failure = ProcessFiles::connect_home(io, 91).err().unwrap();
    assert_eq!(failure.cleanup, [-9, -5]);
    assert_eq!(seen.lock().unwrap().closes, 1);
    let (io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2))]);
    assert_eq!(
        ProcessFiles::connect(io, 91).err().unwrap().error,
        Error::Invalid
    );
    assert_eq!(seen.lock().unwrap().closes, 1);
    assert_eq!(seen.lock().unwrap().receives, 0);
}

#[test]
fn every_send_prefix_failure_preserves_shared_attempt_without_replay() {
    for failure in 1..=65 {
        let mut entry = greeting(3);
        put(&mut entry, 4, 2);
        put(&mut entry, 5, 4);
        let (mut io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2)), Ok(entry)]);
        io.fail = Some(failure + 2); // lookup header/body precede this write
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let p = shell(&mut f);
        let fd = f
            .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
            .unwrap();
        let alias = f.duplicate(p, fd, 0, false).unwrap();
        f.seek(p, alias, Seek::Set(7)).unwrap();
        let e = f.write(p, fd, &[0x5a; 4096]).unwrap_err();
        assert_eq!(e.outcome, Outcome::Unknown);
        assert_eq!(e.offset, Some(7));
        assert_eq!(seen.lock().unwrap().sent.len(), failure + 2);
        check_retired(f, p, fd, seen, e);
    }
}

#[test]
fn actual_reported_errors_retire_all_views_with_progress() {
    for completion in [
        p::Completion {
            error: 28,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        },
        p::Completion {
            error: 5,
            txg: 0,
            bytes_staged: 1,
            state: 1,
        },
        p::Completion {
            error: 5,
            txg: 42,
            bytes_staged: 1,
            state: 2,
        },
    ] {
        let (io, join, state, seen, _) = start();
        state.lock().unwrap().failure = Some(completion);
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let p = shell(&mut f);
        let fd = f
            .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
            .unwrap();
        let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
        f.seek(child, fd, Seek::Set(2)).unwrap();
        let e = f.write(p, fd, b"x").unwrap_err();
        let progress = match completion.state {
            0 => Progress::Unassigned,
            1 => Progress::Committed {
                txg: completion.txg,
                bytes_staged: 1,
            },
            _ => Progress::Completed {
                txg: completion.txg,
                bytes_staged: 1,
            },
        };
        assert_eq!(e.outcome, Outcome::Reported(progress));
        assert_eq!(e.offset, Some(2));
        assert_eq!(e.cleanup, Some([0, 0]));
        let before = seen.lock().unwrap().sent.len();
        assert_eq!(
            f.write(child, fd, b"x").unwrap_err().outcome,
            Outcome::NotSent
        );
        assert_eq!(seen.lock().unwrap().sent.len(), before);
        drop(f);
        assert_eq!(join.join().unwrap().stop, Stop::Retired);
        assert_eq!(state.lock().unwrap().writes, 1);
    }
}

struct LostWriteReply {
    io: Pipe,
    writing: bool,
}
impl Channel for LostWriteReply {
    fn send(&mut self, f: &Message) -> Result<(), i64> {
        if &f[..8] == filesystem_service::MAGIC && word(f, 1) == 5 {
            self.writing = true;
        }
        self.io.send(f)
    }
    fn receive(&mut self, f: &mut Message) -> Result<(), i64> {
        self.io.receive(f)?;
        if self.writing {
            self.writing = false;
            return Err(-32);
        }
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.io.close()
    }
}
#[test]
fn actual_write_effect_with_lost_reply_is_one_unknown_effect() {
    let (io, join, state, seen, _) = start();
    let mut f = ProcessFiles::connect_home(LostWriteReply { io, writing: false }, 91)
        .ok()
        .unwrap();
    let p = shell(&mut f);
    let fd = f
        .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
        .unwrap();
    f.seek(p, fd, Seek::Set(1)).unwrap();
    let e = f.write(p, fd, b"yes").unwrap_err();
    assert_eq!(e.outcome, Outcome::Unknown);
    assert_eq!(e.offset, Some(1));
    assert_eq!(e.cleanup, Some([0, 0]));
    let before = seen.lock().unwrap().sent.len();
    assert_eq!(
        f.write(p, fd, b"yes").unwrap_err().outcome,
        Outcome::NotSent
    );
    drop(f);
    assert_eq!(seen.lock().unwrap().sent.len(), before);
    assert_eq!(join.join().unwrap().stop, Stop::Receive(-32));
    assert_eq!(state.lock().unwrap().writes, 1);
    assert_eq!(&state.lock().unwrap().data[1..], b"yes");
    assert_eq!(e.offset, Some(1));
}

#[test]
fn directory_temporary_close_failure_retires_without_publication() {
    let (io, seen) = script(vec![
        Ok(greeting(1)),
        Ok(greeting(2)),
        Ok(greeting(3)),
        Err(-32),
    ]);
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let p = shell(&mut f);
    assert_eq!(
        f.open_home_file(p, b"nested", HomeAccess::ReadOnly, false),
        Err(ProcessError::Files(Failure::Source(Error::Transport(-32))))
    );
    assert_eq!(
        f.file_view_v1(p),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(f.cleanup(), Some([-9, -5]));
    drop(f);
    assert_eq!(seen.lock().unwrap().closes, 1);
}

#[test]
fn full_bounded_success_advances_to_signed_limit_only_once() {
    let (mut f, p, fd, seen) = scripted(Ok(response(0, 19, 4096, 2)));
    f.seek(p, fd, Seek::Set(i64::MAX - 4096)).unwrap();
    assert_eq!(f.write(p, fd, &[0x5a; 4096]).unwrap().bytes, 4096);
    assert_eq!(
        f.position(p, fd),
        Ok(i64::MAX as u64),
        "PROCESS_WRITE_OFFSET"
    );
    let count = seen.lock().unwrap().sent.len();
    let error = f.write(p, fd, b"x").unwrap_err();
    assert_eq!(error.error, ProcessError::Files(Failure::Overflow));
    assert_eq!(error.offset, Some(i64::MAX as u64));
    assert_eq!(error.outcome, Outcome::NotSent);
    assert_eq!(error.cleanup, None);
    assert_eq!(seen.lock().unwrap().sent.len(), count);
    assert_eq!(count, 65);
    f.abort();
}
