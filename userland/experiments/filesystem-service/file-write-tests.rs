// SPDX-License-Identifier: BSD-2-Clause
//! Real FILE/process/AF09 service mutations and retained delivery observations.
use super::*;
use filesystem_fd_protocol::{Connection, Error as WireError, FileWriteResult};
use filesystem_remote_descriptors::{NativeIdentity, Process, ProcessFiles, Seek};
use std::vec::Vec;

fn word(raw: &[u8], lane: usize) -> u64 {
    u64::from_le_bytes(raw[lane * 8..lane * 8 + 8].try_into().unwrap())
}
fn identity() -> NativeIdentity {
    NativeIdentity::admitted(1, 1, 0xb0000102).unwrap()
}
fn bind<T: Channel>(files: &mut ProcessFiles<T>) -> (Process, Connection) {
    let p = files.admitted_shell(identity(), 7).unwrap();
    (p, Connection::bind(p, 31).unwrap())
}
fn request(op: u64, seq: u64, args: [u64; 4]) -> Message {
    let mut f = [0; 64];
    f[..8].copy_from_slice(filesystem_fd_protocol::MAGIC);
    put(&mut f, 1, op);
    put(&mut f, 2, 31);
    put(&mut f, 3, seq);
    for (i, v) in args.into_iter().enumerate() {
        put(&mut f, i + 4, v);
    }
    f
}
fn open<T: Channel>(files: &mut ProcessFiles<T>, c: &mut Connection, mode: u64) -> i32 {
    let mut w = [0; 4096];
    w[..4].copy_from_slice(b"data");
    let r = c
        .prepare(files, &request(10, 1, [0, 4, mode, 0]), 64, &mut w)
        .expect("FILE_HOME_OPEN");
    assert_eq!(word(r.header(), 1), 0, "FILE_HOME_OPEN");
    let fd = word(r.header(), 4) as i32;
    assert!(r.write_receipt().is_none());
    r.delivered();
    fd
}

#[test]
fn actual_write_reply_readback_and_owner_success_receipt() {
    let (io, j, state, _, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (p, mut c) = bind(&mut f);
    let fd = open(&mut f, &mut c, 2);
    let mut w = [0; 4096];
    w[..4].copy_from_slice(b"home");
    assert_eq!(
        c.input_length(&mut f, &request(11, 2, [fd as u64, 4, 0, 0])),
        Ok(64)
    );
    let r = c
        .prepare(&mut f, &request(11, 2, [fd as u64, 4, 0, 0]), 64, &mut w)
        .unwrap();
    let observed = r.write_receipt().expect("FILE_OWNER_RECEIPT");
    assert_eq!(
        (
            observed.generation,
            observed.sequence,
            observed.fd,
            observed.requested
        ),
        (31, 2, fd, 4)
    );
    assert!(
        matches!(observed.result, FileWriteResult::Completed { offset: 0, completion } if completion.txg == 1 && completion.bytes == 4),
        "FILE_OWNER_RECEIPT"
    );
    assert_eq!(word(r.header(), 4), 4);
    assert_eq!(word(r.header(), 5), 64);
    assert_eq!(word(r.body(), 0), 14);
    assert_eq!(word(r.body(), 2), 1);
    assert_eq!(word(r.body(), 3), 4);
    assert_eq!(r.body().len(), 64);
    r.delivered();
    assert!(w.iter().all(|b| *b == 0));
    assert_eq!(f.position(p, fd), Ok(4));
    let r = c
        .prepare(&mut f, &request(3, 3, [fd as u64, 0, 0, 0]), 0, &mut w)
        .unwrap();
    r.delivered();
    let r = c
        .prepare(&mut f, &request(2, 4, [fd as u64, 4, 0, 0]), 0, &mut w)
        .unwrap();
    assert_eq!(&r.body()[..4], b"home");
    r.delivered();
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    assert_eq!(j.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 1);
    assert!(matches!(
        observed.result,
        FileWriteResult::Completed { offset: 0, .. }
    ));
}

#[test]
fn terminal_error_receipts_are_delivered_after_source_retirement() {
    let mut actual_replies = Vec::new();
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
            bytes_staged: 1,
            state: 1,
        }),
        Some(p::Completion {
            error: 5,
            txg: 17,
            bytes_staged: 1,
            state: 2,
        }),
    ] {
        let (io, j, state, seen, _) = start();
        state.lock().unwrap().failure = failure;
        state.lock().unwrap().lost = failure.is_none();
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let (p, mut c) = bind(&mut f);
        let fd = open(&mut f, &mut c, 2);
        f.seek(p, fd, Seek::Set(2)).unwrap();
        let mut w = [0; 4096];
        w[0] = b'x';
        let r = c
            .prepare(&mut f, &request(11, 2, [fd as u64, 1, 0, 0]), 64, &mut w)
            .expect("FILE_TERMINAL_RECEIPT");
        actual_replies.extend_from_slice(r.header());
        actual_replies.extend_from_slice(r.body());
        let copy = r.write_receipt().expect("FILE_OWNER_RECEIPT");
        let expected_tag = match failure {
            None => 4,
            Some(p::Completion { state: 0, .. }) => 1,
            Some(p::Completion { state: 1, .. }) => 2,
            _ => 3,
        };
        assert_eq!(
            word(r.body(), 0),
            expected_tag | 24,
            "FILE_TERMINAL_RECEIPT"
        );
        assert_eq!(word(r.body(), 1), 2);
        assert_eq!(word(r.body(), 6), 12);
        assert!(
            matches!(copy.result, FileWriteResult::Failed(e) if e.offset == Some(2) && e.cleanup == Some([0, 0]))
        );
        r.delivered();
        assert_eq!(
            c.prepare(&mut f, &request(11, 3, [fd as u64, 1, 0, 0]), 64, &mut w)
                .err(),
            Some(WireError::Retired),
            "FILE_TERMINAL_STAYS_RETIRED"
        );
        assert!(w.iter().all(|b| *b == 0));
        assert_eq!(state.lock().unwrap().writes, 1);
        drop(f);
        assert_eq!(j.join().unwrap().stop, Stop::Retired);
        assert_eq!(seen.lock().unwrap().closes, 1);
        assert!(matches!(copy.result, FileWriteResult::Failed(e) if e.offset == Some(2)));
    }
    std::fs::write(std::env::var("AEFW_ERRORS").unwrap(), actual_replies).unwrap();
}

#[test]
fn copied_success_and_error_survive_dropped_guard_without_replay() {
    for failing in [false, true] {
        let (io, j, state, seen, _) = start();
        if failing {
            state.lock().unwrap().failure = Some(p::Completion {
                error: 5,
                txg: 0,
                bytes_staged: 1,
                state: 1,
            });
        }
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let (_, mut c) = bind(&mut f);
        let fd = open(&mut f, &mut c, 2);
        let mut w = [0; 4096];
        w[0] = b'x';
        let r = c
            .prepare(&mut f, &request(11, 2, [fd as u64, 1, 0, 0]), 64, &mut w)
            .expect("FILE_TERMINAL_RECEIPT");
        let copy = r.write_receipt().expect("FILE_OWNER_RECEIPT");
        drop(r);
        assert!(f.cleanup().is_some(), "FILE_WRITE_DROP_RETIRE");
        assert!(w.iter().all(|b| *b == 0), "FILE_WRITE_GUARD_CLEAR");
        let before = seen.lock().unwrap().sent.len();
        assert_eq!(
            c.prepare(&mut f, &request(11, 2, [fd as u64, 1, 0, 0]), 64, &mut w)
                .err(),
            Some(WireError::Retired)
        );
        assert_eq!(
            seen.lock().unwrap().sent.len(),
            before,
            "FILE_WRITE_NO_REPLAY"
        );
        drop(f);
        j.join().unwrap();
        if failing {
            assert!(
                matches!(copy.result, FileWriteResult::Failed(e) if matches!(e.outcome, filesystem_client::MutationOutcome::Reported(filesystem_client::MutationProgress::Committed { txg: 0, .. }))),
                "FILE_OWNER_RECEIPT"
            );
        } else {
            assert!(
                matches!(copy.result, FileWriteResult::Completed { offset: 0, completion } if completion.bytes == 1),
                "FILE_OWNER_RECEIPT"
            );
        }
        assert_eq!(state.lock().unwrap().writes, 1);
    }
}

#[test]
fn local_denials_keep_connection_and_receipt_without_progress() {
    let (io, j, _, seen, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (p, mut c) = bind(&mut f);
    let fd = open(&mut f, &mut c, 0);
    let before = seen.lock().unwrap().sent.len();
    let mut w = [0; 4096];
    w[0] = 1;
    let r = c
        .prepare(&mut f, &request(11, 2, [fd as u64, 1, 0, 0]), 64, &mut w)
        .unwrap();
    assert_eq!(word(r.body(), 0), 8); // NotSent, attempted offset, no cleanup
    assert_eq!(word(r.body(), 6), 7); // original SourceInvalid
    assert_eq!(word(r.header(), 1) as i64, -22);
    r.delivered();
    assert_eq!(seen.lock().unwrap().sent.len(), before);
    w[0] = 1;
    let r = c
        .prepare(&mut f, &request(11, 3, [15, 1, 0, 0]), 64, &mut w)
        .unwrap();
    assert_eq!(word(r.body(), 0), 0);
    assert_eq!(word(r.body(), 6), 1);
    r.delivered();
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    assert_eq!(j.join().unwrap().stop, Stop::Disconnected);
}

#[test]
fn malformed_request_or_padding_and_old_versions_precede_effects() {
    for change in 0..13 {
        let (io, j, state, _, _) = start();
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let (_, mut c) = bind(&mut f);
        let fd = open(&mut f, &mut c, 2);
        let mut raw = request(11, 2, [fd as u64, 1, 0, 0]);
        let mut w = [0; 4096];
        w[0] = b'x';
        let mut received = 64;
        match change {
            0 => raw[..8].copy_from_slice(b"AEFP0003"),
            1 => put(&mut raw, 2, 0),
            2 => put(&mut raw, 3, 1),
            3 => put(&mut raw, 4, 16),
            4 => put(&mut raw, 5, 0),
            5 => put(&mut raw, 5, 4097),
            6 => put(&mut raw, 6, 1),
            7 => put(&mut raw, 7, 1),
            8 => received = 0,
            9 => received = 128,
            10 => w[1] = 9,
            11 => raw[..8].copy_from_slice(b"AEFP0002"),
            _ => raw[..8].copy_from_slice(b"AEFD0001"),
        }
        assert_eq!(
            c.prepare(&mut f, &raw, received, &mut w).err(),
            Some(WireError::Protocol),
            "FILE_WRITE_PREFLIGHT"
        );
        assert!(w.iter().all(|b| *b == 0));
        drop(f);
        j.join().unwrap();
        assert_eq!(state.lock().unwrap().writes, 0, "FILE_WRITE_PREFLIGHT");
    }
}

#[test]
fn forgotten_pending_reply_cannot_redispatch() {
    let (io, j, state, _, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (_, mut c) = bind(&mut f);
    let fd = open(&mut f, &mut c, 2);
    let mut w = [0; 4096];
    w[0] = b'x';
    let r = c
        .prepare(&mut f, &request(11, 2, [fd as u64, 1, 0, 0]), 64, &mut w)
        .unwrap();
    let copied = r.write_receipt().unwrap();
    core::mem::forget(r);
    assert_eq!(
        c.prepare(&mut f, &request(11, 2, [fd as u64, 1, 0, 0]), 64, &mut w)
            .err(),
        Some(WireError::Retired)
    );
    drop(f);
    j.join().unwrap();
    assert_eq!(state.lock().unwrap().writes, 1);
    assert!(matches!(copied.result, FileWriteResult::Completed { .. }));
}

#[test]
fn actual_c_requests_and_rust_replies() {
    let requests = std::fs::read(std::env::var("AEFW_REQUESTS").unwrap()).unwrap();
    let (io, j, state, _, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (p, mut c) = bind(&mut f);
    let mut cursor = 0;
    let mut output = Vec::new();
    let mut w = [0; 4096];
    while cursor < requests.len() {
        let header: Message = requests[cursor..cursor + 64].try_into().unwrap();
        cursor += 64;
        let needed = c.input_length(&mut f, &header).unwrap();
        w[..needed].copy_from_slice(&requests[cursor..cursor + needed]);
        cursor += needed;
        let r = c.prepare(&mut f, &header, needed, &mut w).unwrap();
        output.extend_from_slice(r.header());
        output.extend_from_slice(r.body());
        r.delivered();
    }
    std::fs::write(std::env::var("AEFW_REPLIES").unwrap(), output).unwrap();
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    assert_eq!(j.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 1);
}

#[test]
fn actual_c_client_facade_over_live_pipes() {
    use std::io::{Read, Write};
    use std::process::{Command, Stdio};
    let executable = std::env::var("AEFW_C_FIXTURE").unwrap();
    let mut child = Command::new(executable)
        .arg("live")
        .env_remove("DYLD_LIBRARY_PATH")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let mut input = child.stdout.take().unwrap();
    let mut output = child.stdin.take().unwrap();
    let (io, j, state, _, _) = start();
    let mut files = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (p, mut c) = bind(&mut files);
    let mut workspace = [0; 4096];
    for _ in 0..5 {
        let mut header = [0; 64];
        input.read_exact(&mut header).unwrap();
        let needed = c.input_length(&mut files, &header).unwrap();
        input.read_exact(&mut workspace[..needed]).unwrap();
        let reply = c
            .prepare(&mut files, &header, needed, &mut workspace)
            .unwrap();
        let retained = reply.write_receipt();
        output.write_all(reply.header()).unwrap();
        output.write_all(reply.body()).unwrap();
        output.flush().unwrap();
        reply.delivered();
        if let Some(retained) = retained {
            assert!(matches!(retained.result, FileWriteResult::Completed { .. }));
        }
    }
    drop(output);
    drop(input);
    assert!(child.wait().unwrap().success());
    files.settled(p).unwrap();
    files.disconnect().unwrap();
    assert_eq!(j.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 1);
}

#[test]
fn actual_c_terminal_receipt_after_real_source_retirement() {
    use std::io::{Read, Write};
    use std::process::{Command, Stdio};
    let mut child = Command::new(std::env::var("AEFW_C_FIXTURE").unwrap())
        .arg("live-error")
        .env_remove("DYLD_LIBRARY_PATH")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let mut input = child.stdout.take().unwrap();
    let mut output = child.stdin.take().unwrap();
    let (io, j, state, _, _) = start();
    state.lock().unwrap().failure = Some(p::Completion {
        error: 5,
        txg: 0,
        bytes_staged: 4,
        state: 1,
    });
    let mut files = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (_, mut c) = bind(&mut files);
    let mut workspace = [0; 4096];
    let mut retained = None;
    for _ in 0..2 {
        let mut header = [0; 64];
        input.read_exact(&mut header).unwrap();
        let needed = c.input_length(&mut files, &header).unwrap();
        input.read_exact(&mut workspace[..needed]).unwrap();
        let r = c
            .prepare(&mut files, &header, needed, &mut workspace)
            .expect("FILE_TERMINAL_RECEIPT");
        if r.write_receipt().is_some() {
            retained = r.write_receipt();
        }
        output.write_all(r.header()).unwrap();
        output.write_all(r.body()).unwrap();
        output.flush().unwrap();
        r.delivered();
    }
    drop(output);
    drop(input);
    assert!(child.wait().unwrap().success(), "FILE_C_LIVE_TERMINAL");
    assert!(
        matches!(retained.unwrap().result, FileWriteResult::Failed(e) if matches!(e.outcome, filesystem_client::MutationOutcome::Reported(filesystem_client::MutationProgress::Committed { txg: 0, bytes_staged: 4 })))
    );
    drop(files);
    assert_eq!(j.join().unwrap().stop, Stop::Retired);
    assert_eq!(state.lock().unwrap().writes, 1);
}
