// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_policy::{Backend, Clock, Completion, Lost, Namespace, Node, Owner, Rights, Utc};
use std::{
    collections::VecDeque,
    sync::{mpsc, Arc, Mutex},
    thread,
    time::Duration,
    vec::Vec,
};

#[cfg(fs_paths)]
#[path = "path-tests.rs"]
mod paths;

fn frame(status: i64, token: u64, kind: u64, size: u64) -> Message {
    let mut result = filesystem_service::message(91, status as u64);
    put(&mut result, 3, token);
    put(&mut result, 4, kind);
    put(&mut result, 5, size);
    result
}
#[derive(Default)]
struct Seen {
    sent: Vec<Message>,
    closes: usize,
    waits: usize,
    lookups: usize,
    reads: usize,
    drops: usize,
}
type Shared = Arc<Mutex<Seen>>;
struct Script {
    input: VecDeque<core::result::Result<Message, i64>>,
    seen: Shared,
    fail: Option<usize>,
    cleanup: [i64; 2],
}
impl Channel for Script {
    fn receive(&mut self, out: &mut Message) -> core::result::Result<(), i64> {
        *out = self.input.pop_front().unwrap_or(Err(-32))?;
        Ok(())
    }
    fn send(&mut self, value: &Message) -> core::result::Result<(), i64> {
        let mut seen = self.seen.lock().unwrap();
        seen.sent.push(*value);
        if self.fail == Some(seen.sent.len()) {
            Err(-32)
        } else {
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        self.cleanup
    }
}
fn script(input: Vec<Message>) -> (Script, Shared) {
    let seen = Shared::default();
    (
        Script {
            input: input.into_iter().map(Ok).collect(),
            seen: seen.clone(),
            fail: None,
            cleanup: [0; 2],
        },
        seen,
    )
}
fn connect(io: Script) -> Client<Script> {
    Client::connect(io, 91, 3).ok().unwrap()
}

struct Pipe {
    tx: Option<mpsc::SyncSender<Message>>,
    rx: Option<mpsc::Receiver<Message>>,
    seen: Shared,
}
impl Channel for Pipe {
    fn receive(&mut self, out: &mut Message) -> core::result::Result<(), i64> {
        *out = self
            .rx
            .as_ref()
            .unwrap()
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        Ok(())
    }
    fn send(&mut self, frame: &Message) -> core::result::Result<(), i64> {
        self.seen.lock().unwrap().sent.push(*frame);
        self.tx.as_ref().unwrap().send(*frame).map_err(|_| -32)
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        self.tx.take();
        self.rx.take();
        [0; 2]
    }
}
struct Storage(Shared);
impl Drop for Storage {
    fn drop(&mut self) {
        self.0.lock().unwrap().drops += 1;
    }
}
impl Backend for Storage {
    fn root(&mut self) -> core::result::Result<Node, filesystem_policy::Error> {
        Ok(Node::new(1, 1, 1, filesystem_policy::Kind::Directory))
    }
    fn directory(&mut self, node: Node) -> core::result::Result<Node, filesystem_policy::Error> {
        Ok(node)
    }
    fn lookup(
        &mut self,
        _: Node,
        name: &[u8],
    ) -> core::result::Result<Node, filesystem_policy::Error> {
        self.0.lock().unwrap().lookups += 1;
        if name == b"missing" {
            return Err(filesystem_policy::Error::Backend(2));
        }
        if name == b"dir" {
            return Ok(Node::new(3, 1, 1, filesystem_policy::Kind::Directory));
        }
        Ok(Node::new(2, 1, 5003, filesystem_policy::Kind::File))
    }
    fn read(
        &mut self,
        _: Node,
        offset: u64,
        out: &mut [u8],
    ) -> core::result::Result<usize, filesystem_policy::Error> {
        self.0.lock().unwrap().reads += 1;
        let count = 5003u64.saturating_sub(offset).min(out.len() as u64) as usize;
        for (i, byte) in out[..count].iter_mut().enumerate() {
            *byte = (offset as usize + i) as u8;
        }
        Ok(count)
    }
    fn write(
        &mut self,
        _: Node,
        _: u64,
        _: &[u8],
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("write forbidden");
    }
    fn mutate(
        &mut self,
        _: Node,
        _: Namespace<'_>,
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("mutation forbidden");
    }
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> core::result::Result<Utc, filesystem_policy::Error> {
        panic!("clock forbidden");
    }
}
struct Harness {
    client: Option<Client<Pipe>>,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
    storage: Shared,
    local: Shared,
}
impl Harness {
    fn new() -> Self {
        let (to_server, server_rx) = mpsc::sync_channel(128);
        let (to_client, client_rx) = mpsc::sync_channel(128);
        let storage = Shared::default();
        let local = Shared::default();
        let observed = storage.clone();
        let worker = thread::spawn(move || {
            let owner = Owner::new(Storage(observed), Time, 72).unwrap();
            filesystem_service::run(
                owner,
                Pipe {
                    tx: Some(to_client),
                    rx: Some(server_rx),
                    seen: Shared::default(),
                },
                17,
                Rights::new(3).unwrap(),
                91,
            )
        });
        let client = Client::connect(
            Pipe {
                tx: Some(to_server),
                rx: Some(client_rx),
                seen: local.clone(),
            },
            91,
            3,
        )
        .ok()
        .unwrap();
        Self {
            client: Some(client),
            worker: Some(worker),
            storage,
            local,
        }
    }
}
impl Drop for Harness {
    fn drop(&mut self) {
        self.client.take();
        if let Some(worker) = self.worker.take() {
            worker.join().unwrap();
        }
    }
}

#[test]
fn actual_sealed_server_long_names_multiframe_eof_nested_lookup_and_disconnect() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    assert_eq!(c.lookup(root, b"missing", 2), Err(Error::Remote(-2)));
    let directory = c.lookup(root, b"dir", 3).unwrap();
    let file = c.lookup(directory.handle, &[b'x'; 255], 2).unwrap();
    assert_eq!(
        (file.kind, c.stat(file.handle).unwrap().size),
        (Kind::File, 5003)
    );
    let mut out = [0x77; MAX_READ];
    assert_eq!(c.read(file.handle, 3, MAX_READ, &mut out), Ok(MAX_READ));
    for (i, byte) in out.iter().enumerate() {
        assert_eq!(*byte, (i + 3) as u8);
    }
    assert_eq!(c.read(file.handle, 4999, 73, &mut out), Ok(4));
    assert_eq!(&out[..4], &[135, 136, 137, 138]);
    assert!(out[4..].iter().all(|&b| b == 0));
    assert_eq!(c.read(file.handle, 6000, 1, &mut out), Ok(0));
    assert_eq!(out, [0; MAX_READ]);
    c.close(file.handle).unwrap();
    c.close(directory.handle).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
    assert_eq!(c.root(), Err(Error::Closed));
    let report = h.worker.take().unwrap().join().unwrap();
    assert_eq!(report.stop, filesystem_service::Stop::Disconnected);
    assert_eq!(report.cleanup, [0; 2]);
    assert_eq!(h.storage.lock().unwrap().drops, 1);
    assert_eq!(h.local.lock().unwrap().closes, 1);
}
#[test]
fn actual_capacity_rights_names_and_stale_handles_have_no_wire_effects() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    for name in [b"".as_slice(), b".", b"..", b"a/b", b"a\0b", &[b'x'; 256]] {
        assert_eq!(c.lookup(root, name, 2), Err(Error::Invalid));
    }
    assert_eq!(c.lookup(root, b"file", 4), Err(Error::Invalid));
    assert!(h.local.lock().unwrap().sent.is_empty());
    let mut handles = Vec::new();
    for _ in 1..SLOTS {
        let entry = c.lookup(root, b"file", 2);
        assert_eq!(entry.as_ref().map(|_| ()), Ok(()));
        handles.push(entry.unwrap().handle);
    }
    let before = h.local.lock().unwrap().sent.len();
    assert_eq!(c.lookup(root, b"file", 2), Err(Error::Full));
    assert_eq!(h.local.lock().unwrap().sent.len(), before);
    let old = handles[0];
    c.close(old).unwrap();
    let new = c.lookup(root, b"file", 2).unwrap().handle;
    assert_ne!(new, old);
    let before = h.local.lock().unwrap().sent.len();
    let mut out = [0x77; MAX_READ];
    assert_eq!(c.read(old, 0, 1, &mut out), Err(Error::Invalid));
    assert_eq!(out, [0; MAX_READ]);
    assert_eq!(
        c.read(
            Handle {
                epoch: 90,
                token: new.token
            },
            0,
            1,
            &mut out
        ),
        Err(Error::Invalid)
    );
    assert_eq!(c.lookup(new, b"file", 2), Err(Error::Invalid));
    assert_eq!(c.close(root), Err(Error::Invalid));
    assert_eq!(h.local.lock().unwrap().sent.len(), before);
}
#[test]
fn zero_reads_and_range_denial_validate_before_transfer_and_clear_output() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let file = c.lookup(root, b"file", 2).unwrap().handle;
    let denied = c.lookup(root, b"file", 1).unwrap().handle;
    let before = h.local.lock().unwrap().sent.len();
    let mut out = [0x77; MAX_READ];
    assert_eq!(c.read(file, 0, 0, &mut out), Ok(0));
    assert_eq!(out, [0; MAX_READ]);
    assert_eq!(c.read(denied, 0, 0, &mut out), Err(Error::Invalid));
    assert_eq!(
        c.read(file, i64::MAX as u64, 1, &mut out),
        Err(Error::Invalid)
    );
    assert_eq!(c.read(file, 0, MAX_READ + 1, &mut out), Err(Error::Invalid));
    assert_eq!(h.local.lock().unwrap().sent.len(), before);
}
#[test]
fn greeting_sweep_wrong_magic_epoch_role_and_reserved_fields_close_once() {
    for index in [0, 8, 16, 24, 32, 48, 56, 63] {
        let mut greeting = frame(0, 1, 1, 0);
        greeting[index] ^= 0x40;
        let (io, seen) = script(std::vec![greeting]);
        assert!(Client::connect(io, 91, 3).is_err());
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
    for (epoch, rights) in [(0, 3), (91, 0), (91, 4)] {
        let (io, seen) = script(Vec::new());
        assert!(Client::connect(io, epoch, rights).is_err());
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn malformed_lookup_tokens_and_stat_identity_retire_without_more_sends() {
    for mut reply in [
        frame(0, 1, 2, 10),
        frame(0, 3, 2, 10),
        frame(0, 2, 3, 10),
        frame(0, 2, 2, 10),
    ] {
        if word(&reply, 3) == 2 && word(&reply, 4) == 2 {
            reply[63] = 1;
        }
        let (io, seen) = script(std::vec![frame(0, 1, 1, 0), reply]);
        let mut c = connect(io);
        let root = c.root().unwrap();
        assert_eq!(c.lookup(root, b"file", 2), Err(Error::Protocol));
        assert_eq!(c.lookup(root, b"file", 2), Err(Error::Closed));
        assert_eq!(seen.lock().unwrap().sent.len(), 2);
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
    let (io, seen) = script(std::vec![
        frame(0, 1, 1, 0),
        frame(0, 2, 2, 10),
        frame(0, 2, 1, 10)
    ]);
    let mut c = connect(io);
    let f = c.lookup(c.root().unwrap(), b"file", 2).unwrap();
    assert_eq!(c.stat(f.handle), Err(Error::Protocol));
    drop(c);
    assert_eq!(seen.lock().unwrap().closes, 1);
}
#[test]
fn every_lookup_send_prefix_failure_retires_without_retransmission() {
    for fail in 1..=5 {
        let (mut io, seen) = script(std::vec![frame(0, 1, 1, 0)]);
        io.fail = Some(fail);
        let mut c = connect(io);
        let root = c.root().unwrap();
        assert_eq!(c.lookup(root, &[b'x'; 255], 2), Err(Error::Transport(-32)));
        assert_eq!(c.lookup(root, b"file", 2), Err(Error::Closed));
        assert_eq!(seen.lock().unwrap().sent.len(), fail);
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn every_missing_read_body_prefix_clears_all_previously_received_bytes() {
    for prefix in 0..64 {
        let mut input = std::vec![
            frame(0, 1, 1, 0),
            frame(0, 2, 2, 4096),
            frame(0, 0, 0, 4096)
        ];
        input.extend(core::iter::repeat_n([0x55; FRAME], prefix));
        let (io, seen) = script(input);
        let mut c = connect(io);
        let f = c.lookup(c.root().unwrap(), b"file", 2).unwrap();
        let mut out = [0x77; MAX_READ];
        assert_eq!(
            c.read(f.handle, 0, MAX_READ, &mut out),
            Err(Error::Transport(-32))
        );
        assert_eq!(out, [0; MAX_READ]);
        assert_eq!(c.read(f.handle, 0, 1, &mut out), Err(Error::Closed));
        assert_eq!(seen.lock().unwrap().sent.len(), 3);
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn read_count_reserved_tail_and_padding_corruption_are_fatal() {
    for field in [3, 4, 5, 6, 7, 8] {
        let mut header = frame(0, 0, 0, 1);
        let mut body = [0; FRAME];
        body[0] = 0x55;
        if field == 8 {
            body[1] = 1;
        } else {
            put(&mut header, field, if field == 5 { 2 } else { 1 });
        }
        let (io, seen) = script(std::vec![
            frame(0, 1, 1, 0),
            frame(0, 2, 2, 10),
            header,
            body
        ]);
        let mut c = connect(io);
        let f = c.lookup(c.root().unwrap(), b"file", 2).unwrap();
        let mut out = [0x77; MAX_READ];
        assert_eq!(c.read(f.handle, 0, 1, &mut out), Err(Error::Protocol));
        assert_eq!(out, [0; MAX_READ]);
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn known_errno_continues_but_uncertain_bad_status_and_final_close_fail_stop() {
    let (io, seen) = script(std::vec![
        frame(0, 1, 1, 0),
        frame(-13, 0, 0, 0),
        frame(0, 2, 2, 10),
        frame(-28, 0, 0, 0)
    ]);
    let mut c = connect(io);
    let root = c.root().unwrap();
    assert_eq!(c.lookup(root, b"file", 2), Err(Error::Remote(-13)));
    let f = c.lookup(root, b"file", 2).unwrap();
    assert_eq!(c.close(f.handle), Err(Error::Remote(-28)));
    assert_eq!(c.root(), Err(Error::Closed));
    drop(c);
    assert_eq!(seen.lock().unwrap().closes, 1);
    let mut bad = frame(-13, 0, 0, 0);
    bad[63] = 1;
    let (io, seen) = script(std::vec![frame(0, 1, 1, 0), bad]);
    let mut c = connect(io);
    let root = c.root().unwrap();
    assert_eq!(c.lookup(root, b"file", 2), Err(Error::Protocol));
    drop(c);
    assert_eq!(seen.lock().unwrap().closes, 1);
    for status in [-5, -9, 1, i64::MIN] {
        let mut reply = frame(status, 0, 0, 0);
        if status == -5 {
            put(&mut reply, 6, 3);
        }
        let (io, seen) = script(std::vec![frame(0, 1, 1, 0), reply]);
        let mut c = connect(io);
        let root = c.root().unwrap();
        assert!(c.lookup(root, b"file", 2).is_err());
        assert_eq!(c.root(), Err(Error::Closed));
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn disconnect_close_outcomes_are_retained_drop_never_retries() {
    let (mut io, seen) = script(std::vec![frame(0, 1, 1, 0), frame(0, 0, 0, 0)]);
    io.cleanup = [-9, -5];
    let mut c = connect(io);
    assert_eq!(c.disconnect(), Ok([-9, -5]));
    assert_eq!(c.cleanup(), Some([-9, -5]));
    assert_eq!(c.disconnect(), Err(Error::Closed));
    drop(c);
    assert_eq!(seen.lock().unwrap().closes, 1);
    let (io, seen) = script(std::vec![frame(0, 1, 1, 0)]);
    let mut c = connect(io);
    assert_eq!(c.disconnect(), Err(Error::Transport(-32)));
    drop(c);
    assert_eq!(seen.lock().unwrap().closes, 1);
}
struct Short {
    input: VecDeque<u8>,
    seen: Shared,
    again: bool,
}
impl filesystem_service::channel::Io for Short {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        if self.again {
            self.again = false;
            return -11;
        }
        self.again = true;
        let count = bytes.len().min(7);
        if !writing {
            for byte in &mut bytes[..count] {
                let Some(value) = self.input.pop_front() else {
                    return 0;
                };
                *byte = value;
            }
        }
        count as i64
    }
    fn wait(&mut self, _: bool) -> i64 {
        self.seen.lock().unwrap().waits += 1;
        0
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        [0; 2]
    }
}
#[test]
fn pinned_short_transfer_adapter_handles_eagain_and_partial_greeting() {
    let seen = Shared::default();
    let input = frame(0, 1, 1, 0)
        .into_iter()
        .chain(frame(0, 0, 0, 0))
        .collect();
    let io = filesystem_service::channel::Framed(Short {
        input,
        seen: seen.clone(),
        again: true,
    });
    let mut c = Client::connect(io, 91, 3).ok().unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
    drop(c);
    assert_eq!(seen.lock().unwrap().closes, 1);
    assert!(seen.lock().unwrap().waits > 3);
    for length in 0..FRAME {
        let seen = Shared::default();
        let io = filesystem_service::channel::Framed(Short {
            input: frame(0, 1, 1, 0)[..length].iter().copied().collect(),
            seen: seen.clone(),
            again: false,
        });
        assert!(Client::connect(io, 91, 3).is_err());
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}

#[test]
fn explicit_abort_keeps_both_close_results_and_sends_nothing() {
    let (mut io, seen) = script(std::vec![frame(0, 1, 1, 0)]);
    io.cleanup = [-9, -5];
    let mut client = connect(io);
    assert_eq!(client.abort(), [-9, -5]);
    assert_eq!(client.abort(), [-9, -5]);
    assert_eq!(client.root(), Err(Error::Closed));
    assert_eq!(client.disconnect(), Err(Error::Closed));
    drop(client);
    assert!(seen.lock().unwrap().sent.is_empty());
    assert_eq!(seen.lock().unwrap().closes, 1);
}

#[test]
fn checked_disconnect_validates_ack_before_callback_and_closes_each_failure_once() {
    for corrupt in [false, true] {
        let mut ack = frame(0, 0, 0, 0);
        if corrupt {
            put(&mut ack, 3, 1);
        }
        let (mut io, seen) = script(std::vec![frame(0, 1, 1, 0), ack]);
        io.cleanup = [-9, -5];
        let mut c = connect(io);
        let mut calls = 0;
        let outcome = c.disconnect_checked(|_| {
            let prior = seen.lock().unwrap().closes;
            assert_eq!(prior, 0);
            calls += 1;
            Err(Error::Transport(-32))
        });
        assert_eq!(
            outcome,
            Err(if corrupt {
                Error::Protocol
            } else {
                Error::Transport(-32)
            })
        );
        assert_eq!(calls, usize::from(!corrupt));
        assert_eq!(c.cleanup(), Some([-9, -5]));
        assert_eq!(
            c.disconnect_checked(|_| panic!("closed verifier")),
            Err(Error::Closed)
        );
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
