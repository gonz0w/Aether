// SPDX-License-Identifier: BSD-2-Clause
//! Host actual-service effects and owned observations, not native delivery proof.
use super::*;
use fd_dispatch::{Error as PeerError, Exchange, Peer};
use filesystem_client::MutationOutcome;
use filesystem_fd_protocol::FileWriteResult;
use filesystem_remote_descriptors::{HomeAccess, NativeIdentity, Process, ProcessFiles};

#[derive(Default)]
struct PeerSeen {
    receives: usize,
    sends: usize,
    output: Vec<u8>,
    closes: usize,
}
struct App {
    input: VecDeque<Result<Message, i64>>,
    seen: Arc<Mutex<PeerSeen>>,
    limit: usize,
    fail_after: Option<usize>,
}
impl Channel for App {
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        self.seen.lock().unwrap().receives += 1;
        *frame = self.input.pop_front().unwrap_or(Err(-777))?;
        Ok(())
    }
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        let mut s = self.seen.lock().unwrap();
        s.sends += 1;
        let count = self.limit.saturating_sub(s.output.len()).min(64);
        s.output.extend_from_slice(&frame[..count]);
        if count < 64 || self.fail_after == Some(s.output.len()) {
            Err(i64::MIN)
        } else {
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        [-7, -8]
    }
}
fn request(op: u64, seq: u64, args: [u64; 4]) -> Message {
    let mut h = [0; 64];
    h[..8].copy_from_slice(fd_dispatch::MAGIC);
    for (i, v) in [op, 31, seq, args[0], args[1], args[2], args[3]]
        .into_iter()
        .enumerate()
    {
        put(&mut h, i + 1, v);
    }
    h
}
fn app(input: Vec<Result<Message, i64>>, limit: usize) -> (App, Arc<Mutex<PeerSeen>>) {
    let seen = Arc::new(Mutex::new(PeerSeen::default()));
    (
        App {
            input: input.into(),
            seen: seen.clone(),
            limit,
            fail_after: None,
        },
        seen,
    )
}
fn admitted<T: Channel>(f: &mut ProcessFiles<T>, access: HomeAccess) -> (Process, i32) {
    let p = f
        .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
        .unwrap();
    let fd = f.open_home_file(p, b"data", access, false).unwrap();
    (p, fd)
}
fn body() -> Message {
    let mut b = [0; 64];
    b[..4].copy_from_slice(b"home");
    b
}
fn check_context(e: &Exchange, p: Process, fd: i32, count: usize) {
    let o = e.observation.expect("PEER_WRITE_CAPTURE");
    assert_eq!(o.process, p, "PEER_WRITE_CONTEXT");
    assert_eq!(
        (
            o.receipt.generation,
            o.receipt.sequence,
            o.receipt.fd,
            o.receipt.requested
        ),
        (31, 1, fd, count),
        "PEER_WRITE_CONTEXT"
    );
}
#[test]
fn success_copy_survives_delivery_peer_drop_and_real_readback() {
    let (io, j, state, _, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (p, fd) = admitted(&mut f, HomeAccess::ReadWrite);
    let (channel, seen) = app(
        vec![Ok(request(11, 1, [fd as u64, 4, 0, 0])), Ok(body())],
        usize::MAX,
    );
    let mut peer = Peer::bind(channel, p, 31).unwrap();
    let mut w = [0; 4096];
    let e = peer.serve_one_observed(&mut f, &mut w);
    check_context(&e, p, fd, 4);
    assert_eq!(e.delivery, Ok(()));
    assert_eq!(e.cleanup, None);
    assert!(w.iter().all(|b| *b == 0));
    assert!(
        matches!(e.observation.unwrap().receipt.result,FileWriteResult::Completed{offset:0,completion} if completion.txg==1 && completion.bytes==4)
    );
    f.seek(p, fd, filesystem_remote_descriptors::Seek::Set(0))
        .unwrap();
    assert_eq!(f.read(p, fd, 4, &mut w), Ok(4));
    assert_eq!(&w[..4], b"home");
    drop(peer);
    assert_eq!(seen.lock().unwrap().closes, 1);
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    assert_eq!(j.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 1);
    check_context(&e, p, fd, 4);
}
#[test]
fn every_reply_byte_loss_and_complete_physical_error_keep_one_effect() {
    let cases = (0..128)
        .map(|n| (n, None))
        .chain([(usize::MAX, Some(64)), (usize::MAX, Some(128))]);
    for (limit, fail_after) in cases {
        let (io, j, state, _, _) = start();
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let (p, fd) = admitted(&mut f, HomeAccess::ReadWrite);
        let (mut channel, seen) = app(vec![Ok(body())], limit);
        channel.fail_after = fail_after;
        let mut peer = Peer::bind(channel, p, 31).unwrap();
        let mut w = [0; 4096];
        let e = peer.serve_received_observed(&mut f, &request(11, 1, [fd as u64, 4, 0, 0]), &mut w);
        check_context(&e, p, fd, 4);
        assert_eq!(
            e.delivery,
            Err(PeerError::Transport(i64::MIN)),
            "PEER_DELIVERY_IDENTITY"
        );
        assert_eq!(e.cleanup, Some([-7, -8]), "PEER_SEPARATE_CLOSES");
        assert!(w.iter().all(|b| *b == 0));
        assert!(
            matches!(e.observation.unwrap().receipt.result,FileWriteResult::Completed{offset:0,completion} if completion.bytes==4),
            "PEER_WRITE_CAPTURE"
        );
        assert!(f.cleanup().is_some(), "PEER_SOURCE_RETIRE");
        let calls = {
            let s = seen.lock().unwrap();
            (s.receives, s.sends)
        };
        let again = peer.serve_one_observed(&mut f, &mut w);
        assert_eq!(again.delivery, Err(PeerError::Closed));
        assert!(again.observation.is_none());
        assert_eq!(again.cleanup, Some([-7, -8]));
        {
            let s = seen.lock().unwrap();
            assert_eq!((s.receives, s.sends), calls, "PEER_NO_REPLAY");
        }
        drop(peer);
        assert_eq!(seen.lock().unwrap().closes, 1);
        assert_eq!(
            seen.lock().unwrap().output.len(),
            fail_after.unwrap_or(limit)
        );
        drop(f);
        assert_eq!(j.join().unwrap().stop, Stop::Receive(-32));
        assert_eq!(state.lock().unwrap().writes, 1, "PEER_NO_REPLAY");
        assert_eq!(state.lock().unwrap().data, *b"home", "PEER_WRITE_EFFECT");
        check_context(&e, p, fd, 4);
    }
}
#[test]
fn terminal_source_progress_delivers_then_closes_peer_without_erasing_receipt() {
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
            bytes_staged: 4,
            state: 1,
        }),
        Some(p::Completion {
            error: 5,
            txg: 17,
            bytes_staged: 4,
            state: 2,
        }),
    ] {
        let (io, j, state, _, _) = start();
        state.lock().unwrap().failure = failure;
        state.lock().unwrap().lost = failure.is_none();
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let (p, fd) = admitted(&mut f, HomeAccess::ReadWrite);
        let (channel, seen) = app(vec![Ok(body())], usize::MAX);
        let mut peer = Peer::bind(channel, p, 31).unwrap();
        let mut w = [0; 4096];
        let e = peer.serve_received_observed(&mut f, &request(11, 1, [fd as u64, 4, 0, 0]), &mut w);
        let o = e.observation.expect("PEER_TERMINAL_RECEIPT");
        check_context(&e, p, fd, 4);
        assert_eq!(e.delivery, Ok(()));
        let closes = seen.lock().unwrap().closes;
        assert_eq!(closes, 1, "PEER_TERMINAL_CLOSE");
        assert_eq!(e.cleanup, Some([-7, -8]), "PEER_SEPARATE_CLOSES");
        let FileWriteResult::Failed(error) = o.receipt.result else {
            panic!("PEER_TERMINAL_RECEIPT")
        };
        let progress = match failure {
            None => filesystem_client::MutationProgress::Unknown,
            Some(p::Completion { state: 0, .. }) => filesystem_client::MutationProgress::Unassigned,
            Some(p::Completion {
                state: 1,
                txg,
                bytes_staged,
                ..
            }) => filesystem_client::MutationProgress::Committed {
                txg,
                bytes_staged: bytes_staged as usize,
            },
            Some(p::Completion {
                txg, bytes_staged, ..
            }) => filesystem_client::MutationProgress::Completed {
                txg,
                bytes_staged: bytes_staged as usize,
            },
        };
        let code = failure.map_or(5, |c| c.error);
        assert_eq!(
            error,
            filesystem_remote_descriptors::ProcessWriteFailure {
                error: filesystem_remote_descriptors::ProcessError::Files(
                    filesystem_remote_descriptors::Failure::Source(
                        filesystem_client::Error::Remote(-(code as i64))
                    )
                ),
                outcome: MutationOutcome::Reported(progress),
                cleanup: Some([0, 0]),
                offset: Some(0),
            },
            "PEER_TERMINAL_RECEIPT"
        );
        assert!(w.iter().all(|b| *b == 0));
        drop(peer);
        drop(f);
        assert_eq!(j.join().unwrap().stop, Stop::Retired);
        assert_eq!(state.lock().unwrap().writes, 1);
        assert_eq!(o.receipt.generation, 31);
    }
}
#[test]
fn local_not_sent_and_ordinary_reply_keep_connection() {
    let (io, j, state, _, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (p, fd) = admitted(&mut f, HomeAccess::ReadOnly);
    let (channel, seen) = app(
        vec![Ok(body()), Ok(request(2, 2, [fd as u64, 4, 0, 0]))],
        usize::MAX,
    );
    let mut peer = Peer::bind(channel, p, 31).unwrap();
    let mut w = [0; 4096];
    let e = peer.serve_received_observed(&mut f, &request(11, 1, [fd as u64, 4, 0, 0]), &mut w);
    check_context(&e, p, fd, 4);
    assert_eq!(e.delivery, Ok(()));
    assert_eq!(e.cleanup, None);
    assert!(
        matches!(e.observation.unwrap().receipt.result,FileWriteResult::Failed(error) if error.outcome==MutationOutcome::NotSent && error.cleanup.is_none())
    );
    let ordinary = peer.serve_one_observed(&mut f, &mut w);
    assert!(ordinary.observation.is_none());
    assert_eq!(ordinary.delivery, Ok(()));
    assert_eq!(ordinary.cleanup, None);
    assert_eq!(state.lock().unwrap().writes, 0);
    drop(peer);
    assert_eq!(seen.lock().unwrap().closes, 1);
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    j.join().unwrap();
}
#[test]
fn inbound_loss_or_malformed_request_has_no_mutation_observation() {
    for mode in 0..4 {
        let (io, j, state, _, _) = start();
        let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
        let (p, fd) = admitted(&mut f, HomeAccess::ReadWrite);
        let mut h = request(11, 1, [fd as u64, 4, 0, 0]);
        let mut b = body();
        if mode == 1 {
            put(&mut h, 2, 30);
        }
        if mode == 2 {
            b[4] = 1;
        }
        let input = if mode == 0 { Err(i64::MIN) } else { Ok(b) };
        let (channel, seen) = app(vec![input], usize::MAX);
        let mut peer = Peer::bind(channel, p, 31).unwrap();
        let mut w = [0; 4096];
        let e = if mode == 3 {
            peer.serve_one_observed(&mut f, &mut w)
        } else {
            peer.serve_received_observed(&mut f, &h, &mut w)
        };
        assert!(e.observation.is_none(), "PEER_PREFLIGHT_OBSERVATION");
        assert!(e.delivery.is_err());
        assert_eq!(e.cleanup, Some([-7, -8]));
        assert!(f.cleanup().is_some(), "PEER_PREFLIGHT_RETIRE");
        assert!(w.iter().all(|b| *b == 0));
        drop(peer);
        assert_eq!(seen.lock().unwrap().closes, 1);
        drop(f);
        j.join().unwrap();
        assert_eq!(state.lock().unwrap().writes, 0, "PEER_PREFLIGHT_EFFECT");
    }
}
#[test]
fn current_child_binding_and_valid_rebind_keep_copied_context() {
    let (io, j, state, _, _) = start();
    let mut f = ProcessFiles::connect_home(io, 91).ok().unwrap();
    let (parent, fd) = admitted(&mut f, HomeAccess::ReadWrite);
    let child = f
        .inherited_child(
            parent,
            NativeIdentity::admitted(2, 1, 0xb0000103).unwrap(),
            9,
        )
        .unwrap();
    let (channel, _) = app(vec![Ok(body()), Ok(body())], usize::MAX);
    let mut peer = Peer::bind(channel, child, 31).unwrap();
    let mut w = [0; 4096];
    let first = peer.serve_received_observed(&mut f, &request(11, 1, [fd as u64, 4, 0, 0]), &mut w);
    check_context(&first, child, fd, 4);
    assert_ne!(child, parent);
    f.commit_exec_close(child).unwrap();
    peer.rebind_after_exec(child, 32).unwrap();
    f.seek(child, fd, filesystem_remote_descriptors::Seek::Set(0))
        .unwrap();
    let mut h = request(11, 1, [fd as u64, 4, 0, 0]);
    put(&mut h, 2, 32);
    let next = peer.serve_received_observed(&mut f, &h, &mut w);
    assert_eq!(next.delivery, Ok(()));
    assert_eq!(next.observation.unwrap().process, child);
    assert_eq!(next.observation.unwrap().receipt.generation, 32);
    drop(peer);
    f.settled(child).unwrap();
    f.settled(parent).unwrap();
    f.disconnect().unwrap();
    j.join().unwrap();
    assert_eq!(state.lock().unwrap().writes, 2);
    check_context(&first, child, fd, 4);
}
