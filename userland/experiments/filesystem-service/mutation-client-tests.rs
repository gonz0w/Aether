// SPDX-License-Identifier: BSD-2-Clause
//! Mutation receipts survive client retirement; actual service plus hostile wire.
use super::*;
use filesystem_client::{
    MutationCompletion, MutationFailure, MutationOutcome as Outcome, MutationProgress as Progress,
    NamespaceMutation as Namespace,
};

fn completion(code: i64, txg: u64, bytes: u64, state: u64) -> Message {
    let mut frame = message(91, code as u64);
    put(&mut frame, 4, txg);
    put(&mut frame, 5, bytes);
    put(&mut frame, 6, state);
    frame
}
fn prepared(
    reply: Result<Message, i64>,
    file: bool,
) -> (Client<Script>, filesystem_client::Handle, Observed) {
    let mut frames = vec![Ok(greeting(1)), Ok(greeting(2))];
    if file {
        let mut entry = greeting(3);
        put(&mut entry, 4, 2);
        put(&mut entry, 5, 4);
        frames.push(Ok(entry));
    }
    frames.push(reply);
    let (io, seen) = script(frames);
    let mut client = Client::connect_home(io, 91).ok().unwrap();
    let home = client.home().unwrap();
    let handle = if file {
        client.lookup(home, b"data", 6).unwrap().handle
    } else {
        home
    };
    seen.lock().unwrap().sent.clear();
    (client, handle, seen)
}
fn assert_retired(
    mut client: Client<Script>,
    handle: filesystem_client::Handle,
    seen: Observed,
    receipt: MutationFailure,
    expected: Outcome,
) {
    assert_eq!(receipt.outcome, expected, "MUTATION_EXACT_OUTCOME");
    assert_eq!(receipt.cleanup, Some([-9, -5]), "MUTATION_CLOSE_RECEIPT");
    let sends = seen.lock().unwrap().sent.len();
    let later = client.write(handle, 0, b"x").unwrap_err();
    assert_eq!(later.error, Error::Closed);
    assert_eq!(later.outcome, Outcome::NotSent);
    assert_eq!(later.cleanup, receipt.cleanup);
    assert_eq!(client.abort(), [-9, -5]);
    drop(client);
    assert_eq!(seen.lock().unwrap().sent.len(), sends, "MUTATION_NO_REPLAY");
    assert_eq!(seen.lock().unwrap().closes, 1, "MUTATION_CLOSE_ONCE");
    assert_eq!(receipt.outcome, expected);
}

#[test]
fn actual_write_and_all_namespace_operations_complete_and_continue() {
    let (io, join, state, local, server) = start();
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let home = c.home().unwrap();
    let file = c.lookup(home, b"data", 6).unwrap();
    assert_eq!(
        c.write(file.handle, 0, b"home"),
        Ok(MutationCompletion { txg: 1, bytes: 4 })
    );
    let mut out = [0; 4096];
    assert_eq!(c.read(file.handle, 0, 4, &mut out), Ok(4));
    assert_eq!(&out[..4], b"home");
    c.close(file.handle).unwrap();
    for operation in [
        Namespace::Create(b"created"),
        Namespace::Rename(b"created", b"renamed"),
        Namespace::Remove(b"renamed"),
        Namespace::MakeDirectory(b"dir"),
        Namespace::RemoveDirectory(b"dir"),
    ] {
        assert_eq!(
            c.namespace(home, operation),
            Ok(MutationCompletion { txg: 2, bytes: 0 })
        );
    }
    assert!(c.stat(home).is_ok());
    c.disconnect().unwrap();
    drop(c);
    assert_eq!(join.join().unwrap().stop, Stop::Disconnected);
    let s = state.lock().unwrap();
    assert_eq!((s.writes, s.mutations, s.drops), (1, 5, 1));
    assert!(!s.created && !s.renamed && !s.made_directory);
    assert_eq!(local.lock().unwrap().closes, 1);
    assert_eq!(server.lock().unwrap().closes, 1);
}

#[test]
fn actual_namespace_error_progress_is_not_erased() {
    for failure in [
        None,
        Some(p::Completion {
            error: 28,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        }),
        Some(p::Completion {
            error: 5,
            txg: 0,
            bytes_staged: 0,
            state: 1,
        }),
        Some(p::Completion {
            error: 5,
            txg: 42,
            bytes_staged: 0,
            state: 2,
        }),
    ] {
        let (io, join, state, _, _) = start();
        {
            let mut s = state.lock().unwrap();
            s.failure = failure;
            s.lost = failure.is_none();
        }
        let mut c = Client::connect_home(io, 91).ok().unwrap();
        let home = c.home().unwrap();
        let receipt = c
            .namespace(home, Namespace::Create(b"created"))
            .unwrap_err();
        let progress = match failure {
            None => Progress::Unknown,
            Some(p::Completion { state: 0, .. }) => Progress::Unassigned,
            Some(p::Completion { state: 1, txg, .. }) => Progress::Committed {
                txg,
                bytes_staged: 0,
            },
            Some(p::Completion { txg, .. }) => Progress::Completed {
                txg,
                bytes_staged: 0,
            },
        };
        assert_eq!(receipt.outcome, Outcome::Reported(progress));
        assert_eq!(receipt.cleanup, Some([0, 0]));
        drop(c);
        assert_eq!(join.join().unwrap().stop, Stop::Retired);
        let s = state.lock().unwrap();
        assert_eq!((s.mutations, s.drops), (1, 1));
    }
}

#[test]
fn actual_server_denies_holes_without_effect_and_client_retires() {
    let (io, join, state, local, _) = start();
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let file = c.lookup(c.home().unwrap(), b"data", 6).unwrap();
    let receipt = c.write(file.handle, 5, b"x").unwrap_err();
    assert_eq!(receipt.error, Error::Remote(-22));
    assert_eq!(receipt.outcome, Outcome::Reported(Progress::Unassigned));
    assert_eq!(receipt.cleanup, Some([0, 0]));
    let sends = local.lock().unwrap().sent.len();
    assert_eq!(
        c.write(file.handle, 0, b"x").unwrap_err().outcome,
        Outcome::NotSent
    );
    drop(c);
    assert_eq!(local.lock().unwrap().sent.len(), sends);
    // The validation error itself left Owner active. Client closure then ends
    // the service; an empty progress tuple cannot promise that lifetime.
    assert_eq!(join.join().unwrap().stop, Stop::Receive(-32));
    let s = state.lock().unwrap();
    assert_eq!((s.writes, s.drops), (0, 1));
}

#[test]
fn actual_reported_progress_and_unknown_retire_with_exact_receipts() {
    for failure in [
        p::Completion {
            error: 28,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        },
        p::Completion {
            error: 5,
            txg: 0,
            bytes_staged: 4,
            state: 1,
        },
        p::Completion {
            error: 5,
            txg: 42,
            bytes_staged: 4,
            state: 2,
        },
    ] {
        let (io, join, state, _, _) = start();
        state.lock().unwrap().failure = Some(failure);
        let mut c = Client::connect_home(io, 91).ok().unwrap();
        let f = c.lookup(c.home().unwrap(), b"data", 6).unwrap();
        let error = c.write(f.handle, 0, b"home").unwrap_err();
        let progress = match failure.state {
            0 => Progress::Unassigned,
            1 => Progress::Committed {
                txg: failure.txg,
                bytes_staged: 4,
            },
            _ => Progress::Completed {
                txg: failure.txg,
                bytes_staged: 4,
            },
        };
        assert_eq!(error.error, Error::Remote(-i64::from(failure.error)));
        assert_eq!(
            error.outcome,
            Outcome::Reported(progress),
            "MUTATION_ACTUAL_PROGRESS"
        );
        assert_eq!(error.cleanup, Some([0, 0]));
        assert_eq!(
            c.write(f.handle, 0, b"x").unwrap_err().outcome,
            Outcome::NotSent
        );
        drop(c);
        assert_eq!(join.join().unwrap().stop, Stop::Retired);
        let s = state.lock().unwrap();
        assert_eq!((s.writes, s.drops), (1, 1));
    }
    let (io, join, state, _, _) = start();
    state.lock().unwrap().lost = true;
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let f = c.lookup(c.home().unwrap(), b"data", 6).unwrap();
    let receipt = c.write(f.handle, 0, b"home").unwrap_err();
    assert_eq!(receipt.outcome, Outcome::Reported(Progress::Unknown));
    drop(c);
    assert_eq!(join.join().unwrap().stop, Stop::Retired);
    assert_eq!(state.lock().unwrap().writes, 1);
}

#[test]
fn write_error_progress_matrix_is_preserved_after_drop() {
    for (code, txg, bytes, state, progress) in [
        (-28, 0, 0, 0, Progress::Unassigned),
        (
            -5,
            0,
            0,
            1,
            Progress::Committed {
                txg: 0,
                bytes_staged: 0,
            },
        ),
        (
            -5,
            99,
            4,
            1,
            Progress::Committed {
                txg: 99,
                bytes_staged: 4,
            },
        ),
        (
            -5,
            99,
            0,
            2,
            Progress::Completed {
                txg: 99,
                bytes_staged: 0,
            },
        ),
        (
            -5,
            99,
            4,
            2,
            Progress::Completed {
                txg: 99,
                bytes_staged: 4,
            },
        ),
        (-5, 0, 0, 3, Progress::Unknown),
        (
            -i64::from(i32::MAX),
            99,
            4,
            1,
            Progress::Committed {
                txg: 99,
                bytes_staged: 4,
            },
        ),
    ] {
        let (mut c, h, seen) = prepared(Ok(completion(code, txg, bytes, state)), true);
        let receipt = c.write(h, 0, b"data").expect_err("MUTATION_EXACT_OUTCOME");
        assert_eq!(
            receipt.error,
            Error::Remote(code),
            "MUTATION_REMOTE_PROGRESS"
        );
        assert_retired(c, h, seen, receipt, Outcome::Reported(progress));
    }
}

#[test]
fn namespace_error_progress_requires_exact_errno_and_zero_staged() {
    for (code, txg, state, progress) in [
        (-6000, 0, 0, Progress::Unassigned),
        (
            -4095,
            0,
            1,
            Progress::Committed {
                txg: 0,
                bytes_staged: 0,
            },
        ),
        (
            -5,
            20,
            2,
            Progress::Completed {
                txg: 20,
                bytes_staged: 0,
            },
        ),
        (-5, 0, 3, Progress::Unknown),
    ] {
        let (mut c, h, seen) = prepared(Ok(completion(code, txg, 0, state)), false);
        let receipt = c.namespace(h, Namespace::Create(b"created")).unwrap_err();
        assert_eq!(
            receipt.error,
            Error::Remote(code),
            "MUTATION_REMOTE_PROGRESS"
        );
        assert_retired(c, h, seen, receipt, Outcome::Reported(progress));
    }
    for frame in [
        completion(-4096, 1, 0, 1),
        completion(-5, 1, 1, 1),
        completion(-5, 1, 1, 2),
    ] {
        let (mut c, h, seen) = prepared(Ok(frame), false);
        let receipt = c.namespace(h, Namespace::Create(b"created")).unwrap_err();
        assert_eq!(receipt.error, Error::Protocol, "MUTATION_NAMESPACE_SHAPE");
        assert_retired(c, h, seen, receipt, Outcome::Unknown);
    }
}

#[test]
fn malformed_success_or_error_never_publishes_progress() {
    let mut bad = vec![
        completion(0, 0, 4, 2),
        completion(0, 1, 3, 2),
        completion(0, 1, 4, 1),
        completion(1, 1, 4, 2),
        completion(-2147483648, 0, 0, 0),
        completion(-5, 1, 0, 0),
        completion(-5, 0, 4, 0),
        completion(-5, 1, 2, 1),
        completion(-5, 0, 4, 2),
        completion(-5, 0, 0, 4),
        completion(-28, 0, 0, 3),
        completion(-5, 1, 0, 3),
        completion(-5, 0, 4, 3),
    ];
    for error in [false, true] {
        for field in [0, 2, 3, 7] {
            let mut f = completion(if error { -5 } else { 0 }, 1, 4, 2);
            if field == 0 {
                f[0] ^= 1;
            } else {
                put(&mut f, field, 999);
            }
            bad.push(f);
        }
    }
    for reply in bad {
        let (mut c, h, seen) = prepared(Ok(reply), true);
        let receipt = c
            .write(h, 0, b"data")
            .expect_err("MUTATION_REPLY_VALIDATION");
        assert_eq!(receipt.error, Error::Protocol, "MUTATION_REPLY_VALIDATION");
        assert_retired(c, h, seen, receipt, Outcome::Unknown);
    }
}

#[test]
fn exact_write_body_lengths_and_success_bounds() {
    for count in [1, 64, 65, 4096] {
        let bytes = vec![0x5a; count];
        let (mut c, h, seen) = prepared(Ok(completion(0, 13, count as u64, 2)), true);
        assert_eq!(
            c.write(h, 0, &bytes),
            Ok(MutationCompletion {
                txg: 13,
                bytes: count
            })
        );
        assert_eq!(c.cleanup(), None);
        let frames = &seen.lock().unwrap().sent;
        assert_eq!(word(&frames[0], 1), 5);
        assert_eq!(word(&frames[0], 5), count as u64);
        let body: Vec<u8> = frames[1..].iter().flat_map(|f| f.iter().copied()).collect();
        assert_eq!(&body[..count], &bytes);
        assert!(body[count..].iter().all(|b| *b == 0));
        assert_eq!(frames.len(), 1 + count.div_ceil(64));
    }
}

#[test]
fn rename_uses_contiguous_510_byte_body_without_internal_padding() {
    let from = [b'a'; 255];
    let to = [b'b'; 255];
    let (mut c, h, seen) = prepared(Ok(completion(0, 17, 0, 2)), false);
    assert_eq!(
        c.namespace(h, Namespace::Rename(&from, &to)),
        Ok(MutationCompletion { txg: 17, bytes: 0 })
    );
    let frames = seen.lock().unwrap().sent.clone();
    assert_eq!(word(&frames[0], 1), 8);
    assert_eq!(word(&frames[0], 5), 255 | (255 << 32));
    let body: Vec<u8> = frames[1..].iter().flat_map(|f| f.iter().copied()).collect();
    assert_eq!(&body[..255], &from, "MUTATION_RENAME_CONTIGUOUS");
    assert_eq!(&body[255..510], &to, "MUTATION_RENAME_CONTIGUOUS");
    assert_eq!(&body[510..], &[0, 0]);
}

#[test]
fn every_write_send_prefix_and_receive_loss_is_unknown_without_replay() {
    for failure in 1..=65 {
        let mut file = greeting(3);
        put(&mut file, 4, 2);
        put(&mut file, 5, 4);
        let (io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2)), Ok(file)]);
        let mut io = io;
        io.fail = Some(failure + 2);
        let mut c = Client::connect_home(io, 91).ok().unwrap();
        let handle = c.lookup(c.home().unwrap(), b"data", 6).unwrap().handle;
        let receipt = c.write(handle, 0, &[7; 4096]).unwrap_err();
        assert_eq!(receipt.error, Error::Transport(-32));
        assert_retired(c, handle, seen, receipt, Outcome::Unknown);
    }
    let (mut c, h, seen) = prepared(Err(-32), true);
    let receipt = c.write(h, 0, b"data").unwrap_err();
    assert_retired(c, h, seen, receipt, Outcome::Unknown);
}

#[test]
fn namespace_send_prefix_loss_is_unknown_without_replay() {
    for failure in 1..=9 {
        let (mut io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2))]);
        io.fail = Some(failure);
        let mut c = Client::connect_home(io, 91).ok().unwrap();
        let home = c.home().unwrap();
        let receipt = c
            .namespace(home, Namespace::Rename(&[b'a'; 255], &[b'b'; 255]))
            .unwrap_err();
        assert_eq!(receipt.error, Error::Transport(-32));
        assert_retired(c, home, seen, receipt, Outcome::Unknown);
    }
}

#[test]
fn local_input_and_rights_errors_are_not_sent_and_keep_client_live() {
    let (io, join, state, local, _) = start();
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let root = c.root().unwrap();
    let home = c.home().unwrap();
    let file = c.lookup(home, b"data", 6).unwrap().handle;
    let read = c.lookup(home, b"data", 2).unwrap().handle;
    let alias = c.lookup(root, b"home", 3).unwrap().handle;
    let before = local.lock().unwrap().sent.len();
    for (handle, offset, bytes) in [
        (file, 0, b"".as_slice()),
        (file, 0, &[0; 4097]),
        (file, i64::MAX as u64, b"x"),
        (file, u64::MAX, b"x"),
        (read, 0, b"x"),
        (home, 0, b"x"),
    ] {
        let error = c.write(handle, offset, bytes).unwrap_err();
        assert_eq!(error.outcome, Outcome::NotSent, "MUTATION_LOCAL_PREFLIGHT");
        assert_eq!(error.cleanup, None);
    }
    for (directory, op) in [
        (root, Namespace::Create(b"created")),
        (alias, Namespace::Create(b"created")),
        (home, Namespace::Create(b"")),
        (home, Namespace::Remove(b".")),
        (home, Namespace::RemoveDirectory(b"..")),
        (home, Namespace::MakeDirectory(b"a/b")),
        (home, Namespace::Create(b"a\0b")),
        (home, Namespace::Create(&[b'x'; 256])),
        (home, Namespace::Rename(b"same", b"same")),
        (home, Namespace::Rename(b"valid", b"bad/target")),
    ] {
        let error = c.namespace(directory, op).unwrap_err();
        assert_eq!(error.outcome, Outcome::NotSent, "MUTATION_LOCAL_PREFLIGHT");
    }
    assert_eq!(
        local.lock().unwrap().sent.len(),
        before,
        "MUTATION_LOCAL_PREFLIGHT"
    );
    {
        let s = state.lock().unwrap();
        assert_eq!((s.writes, s.mutations), (0, 0));
    }
    c.close(file).unwrap();
    let before = local.lock().unwrap().sent.len();
    assert_eq!(
        c.write(file, 0, b"x").unwrap_err().outcome,
        Outcome::NotSent
    );
    assert_eq!(local.lock().unwrap().sent.len(), before);
    c.close(read).unwrap();
    c.close(alias).unwrap();
    c.disconnect().unwrap();
    assert_eq!(join.join().unwrap().stop, Stop::Disconnected);
}

struct LostReply {
    inner: Pipe,
    sends: usize,
}
impl Channel for LostReply {
    fn receive(&mut self, f: &mut Message) -> Result<(), i64> {
        self.inner.receive(f)
    }
    fn send(&mut self, f: &Message) -> Result<(), i64> {
        self.sends += 1;
        if self.sends == 4 {
            Err(-32)
        } else {
            self.inner.send(f)
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.inner.close()
    }
}
#[test]
fn real_effect_with_lost_reply_stays_unknown_and_is_not_repeated() {
    let (io, server, local, remote) = pair();
    let state = Shared::default();
    let shared = state.clone();
    let join = thread::spawn(move || {
        let (o, a, h) = owner(shared);
        filesystem_service::run_home(
            o,
            LostReply {
                inner: server,
                sends: 0,
            },
            7,
            a.session,
            h.handle,
            8,
            91,
        )
    });
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let file = c.lookup(c.home().unwrap(), b"data", 6).unwrap();
    let receipt = c.write(file.handle, 0, b"home").unwrap_err();
    assert_eq!(receipt.outcome, Outcome::Unknown);
    let sends = local.lock().unwrap().sent.len();
    assert_eq!(
        c.write(file.handle, 0, b"home").unwrap_err().outcome,
        Outcome::NotSent
    );
    drop(c);
    assert_eq!(local.lock().unwrap().sent.len(), sends);
    assert_eq!(join.join().unwrap().stop, Stop::ReplyLost(-32));
    let s = state.lock().unwrap();
    assert_eq!((s.writes, s.drops, s.data), (1, 1, *b"home"));
    assert_eq!(local.lock().unwrap().closes, 1);
    assert_eq!(remote.lock().unwrap().closes, 1);
}
