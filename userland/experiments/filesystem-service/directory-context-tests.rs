// SPDX-License-Identifier: BSD-2-Clause
//! Host AF08 policy/service/client qualification; no native disk claim.
use filesystem_client::{Client, Error, Kind, ResolvedDirectory};
use filesystem_policy as p;
use filesystem_service::{message, put, word, Channel, Message};
use std::{
    collections::VecDeque,
    sync::{mpsc, Arc, Mutex},
    thread,
    time::Duration,
};

#[derive(Default)]
struct State {
    renamed: bool,
    removed: bool,
    mode: u8,
    gets: usize,
    drops: usize,
}
type Shared = Arc<Mutex<State>>;
struct Graph(Shared);
fn node(id: u64) -> p::Node {
    p::Node::new(
        id,
        id + 10,
        if id == 2 { 6 } else { 2 },
        if id == 2 {
            p::Kind::File
        } else {
            p::Kind::Directory
        },
    )
}
impl Drop for Graph {
    fn drop(&mut self) {
        self.0.lock().unwrap().drops += 1;
    }
}
impl p::Backend for Graph {
    fn root(&mut self) -> Result<p::Node, p::Error> {
        Ok(node(1))
    }
    fn directory(&mut self, n: p::Node) -> Result<p::Node, p::Error> {
        Ok(n)
    }
    fn lookup(&mut self, at: p::Node, name: &[u8]) -> Result<p::Node, p::Error> {
        let s = self.0.lock().unwrap();
        let name3 = if s.renamed {
            b"renamed".as_slice()
        } else {
            b"work"
        };
        match (at.identity().0, name) {
            (1, n) if n == name3 && !s.removed => Ok(node(3)),
            (3, b"nested") if !s.removed => Ok(node(4)),
            (1 | 3 | 4, b"file") => Ok(node(2)),
            _ => Err(p::Error::Backend(2)),
        }
    }
    fn read(&mut self, _: p::Node, offset: u64, out: &mut [u8]) -> Result<usize, p::Error> {
        let n = 6u64.saturating_sub(offset).min(out.len() as u64) as usize;
        out[..n].copy_from_slice(&b"abcdef"[offset.min(6) as usize..offset.min(6) as usize + n]);
        Ok(n)
    }
    fn write(&mut self, _: p::Node, _: u64, _: &[u8], _: p::Utc) -> Result<p::Completion, p::Lost> {
        panic!("read-only test")
    }
    fn mutate(
        &mut self,
        _: p::Node,
        _: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        panic!("read-only test")
    }
    fn directory_context(
        &mut self,
        root: p::Node,
        at: p::Node,
        out: &mut [u8; 256],
    ) -> Result<(p::Node, usize), p::Error> {
        assert_eq!(root.identity(), (1, 11));
        let mut s = self.0.lock().unwrap();
        s.gets += 1;
        if s.removed && at.identity().0 != 1 {
            return Err(p::Error::Backend(2));
        }
        let path = match at.identity().0 {
            1 => b"/\0".as_slice(),
            3 if s.renamed => b"/renamed\0",
            3 => b"/work\0",
            4 if s.renamed => b"/renamed/nested\0",
            4 => b"/work/nested\0",
            _ => return Err(p::Error::NotDirectory),
        };
        out[..path.len()].copy_from_slice(path);
        let parent = node(if at.identity().0 == 4 { 3 } else { 1 });
        match s.mode {
            1 => {
                out[0] = b'x';
                Err(p::Error::Backend(5))
            }
            2 => Ok((parent, 257)),
            3 => Ok((p::Node::new(0, 1, 0, p::Kind::Directory), path.len())),
            4 => {
                out[0] = b'x';
                Ok((parent, path.len()))
            }
            5 => {
                out[255] = 1;
                Ok((parent, path.len()))
            }
            6 => Ok((node(2), path.len())),
            7 => {
                out.fill(0);
                out[..2].copy_from_slice(b"/\0");
                Ok((parent, 2))
            }
            8 => Ok((node(3), path.len())),
            _ => Ok((parent, path.len())),
        }
    }
}
struct Time;
impl p::Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        panic!("no mutation")
    }
}
struct Pipe {
    tx: Option<mpsc::SyncSender<Message>>,
    rx: Option<mpsc::Receiver<Message>>,
}
impl Channel for Pipe {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        *out = self
            .rx
            .as_ref()
            .unwrap()
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        Ok(())
    }
    fn send(&mut self, out: &Message) -> Result<(), i64> {
        self.tx.as_ref().unwrap().send(*out).map_err(|_| -32)
    }
    fn close(&mut self) -> [i64; 2] {
        self.tx.take();
        self.rx.take();
        [0; 2]
    }
}
fn transport(state: Shared) -> (Pipe, thread::JoinHandle<filesystem_service::Report>) {
    let (ct, sr) = mpsc::sync_channel(128);
    let (st, cr) = mpsc::sync_channel(128);
    let observed = state.clone();
    let worker = thread::spawn(move || {
        filesystem_service::run(
            p::Owner::new(Graph(observed), Time, 72).unwrap(),
            Pipe {
                tx: Some(st),
                rx: Some(sr),
            },
            17,
            p::Rights::new(3).unwrap(),
            91,
        )
    });
    (
        Pipe {
            tx: Some(ct),
            rx: Some(cr),
        },
        worker,
    )
}
struct Harness {
    client: Option<Client<Pipe>>,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
    state: Shared,
}
impl Harness {
    fn new() -> Self {
        let state = Shared::default();
        let (pipe, worker) = transport(state.clone());
        let client = Client::connect(pipe, 91, 3).ok().unwrap();
        Self {
            client: Some(client),
            worker: Some(worker),
            state,
        }
    }
    fn finish(&mut self) {
        assert_eq!(self.client.as_mut().unwrap().disconnect(), Ok([0; 2]));
        assert_eq!(
            self.worker.take().unwrap().join().unwrap().stop,
            filesystem_service::Stop::Disconnected
        );
        assert_eq!(self.state.lock().unwrap().drops, 1);
    }
}
impl Drop for Harness {
    fn drop(&mut self) {
        self.client.take();
        if let Some(w) = self.worker.take() {
            w.join().unwrap();
        }
    }
}
#[test]
fn actual_service_physical_path_tracks_rename_and_unlink_without_cache() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let dir = c
        .resolve_directory_from(root, b"/work/nested")
        .unwrap()
        .entry();
    let mut out = [0xa5; 256];
    assert_eq!(c.directory_path(dir.handle, &mut out), Ok(13));
    assert_eq!(&out[..13], b"/work/nested\0");
    h.state.lock().unwrap().renamed = true;
    assert_eq!(c.directory_path(dir.handle, &mut out), Ok(16));
    assert_eq!(&out[..16], b"/renamed/nested\0");
    let parent = c.parent_directory(dir.handle).unwrap();
    assert_ne!(parent.handle, root);
    assert_eq!(c.parent_directory(parent.handle).unwrap().handle, root);
    h.state.lock().unwrap().removed = true;
    assert_eq!(
        c.directory_path(dir.handle, &mut out),
        Err(Error::Remote(-2))
    );
    assert_eq!(out, [0; 256]);
    c.close(parent.handle).unwrap();
    c.close(dir.handle).unwrap();
    h.finish();
}
#[test]
fn component_walk_obeys_dot_dotdot_root_confinement_and_directory_types() {
    for path in [
        b"/work//nested/.././file".as_slice(),
        b"../../work/file",
        b"/../../work/../file",
    ] {
        let mut h = Harness::new();
        let c = h.client.as_mut().unwrap();
        let root = c.root().unwrap();
        let file = c.resolve_file_from(root, path).unwrap();
        let mut out = [0; 4096];
        assert_eq!(c.read(file.handle, 0, 6, &mut out), Ok(6));
        assert_eq!(&out[..6], b"abcdef");
        c.close(file.handle).unwrap();
        h.finish();
    }
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    for path in [b"file/..".as_slice(), b"file/.", b"file/", b"file//nested"] {
        assert_eq!(
            c.resolve_directory_from(root, path),
            Err(Error::Remote(-20))
        );
    }
    assert_eq!(c.resolve_file_from(root, b"work/"), Err(Error::Remote(-21)));
    for path in [b"/".as_slice(), b"/./../..//", b"."] {
        assert_eq!(
            c.resolve_directory_from(root, path),
            Ok(ResolvedDirectory::Borrowed(filesystem_client::Entry {
                handle: root,
                kind: Kind::Directory,
                size: 2
            }))
        );
    }
    for path in [b"".as_slice(), b"a\0b", &[b'x'; 256]] {
        assert_eq!(c.resolve_directory_from(root, path), Err(Error::Invalid));
    }
    // All temporary opens, including known failing walks, have been released.
    let mut handles = Vec::new();
    for _ in 0..15 {
        handles.push(c.lookup(root, b"file", 2).unwrap().handle);
    }
    assert_eq!(
        c.resolve_directory_from(root, b"work/nested"),
        Err(Error::Full)
    );
    for f in handles {
        c.close(f).unwrap();
    }
    h.finish();
}
#[test]
fn retained_base_is_borrowed_and_absolute_paths_start_at_root() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let base = c.resolve_directory_from(root, b"work").unwrap().entry();
    assert_eq!(
        c.resolve_directory_from(base.handle, b"."),
        Ok(ResolvedDirectory::Borrowed(base))
    );
    let nested = c
        .resolve_directory_from(base.handle, b"nested")
        .unwrap()
        .entry();
    let up = c
        .resolve_directory_from(nested.handle, b"..")
        .unwrap()
        .entry();
    let mut path = [0; 256];
    assert_eq!(c.directory_path(up.handle, &mut path), Ok(6));
    assert_eq!(&path[..6], b"/work\0");
    c.close(up.handle).unwrap();
    let file = c.resolve_file_from(nested.handle, b"../../file").unwrap();
    c.close(file.handle).unwrap();
    let file = c.resolve_file_from(nested.handle, b"/file").unwrap();
    c.close(file.handle).unwrap();
    c.close(nested.handle).unwrap();
    c.close(base.handle).unwrap();
    h.finish();
}
#[test]
fn policy_rejects_foreign_handles_missing_rights_and_files_before_provider() {
    let s = Shared::default();
    let mut o = p::Owner::new(Graph(s.clone()), Time, 72).unwrap();
    let a = o.attach(17, p::Rights::new(3).unwrap()).unwrap();
    let b = o.attach(18, p::Rights::new(3).unwrap()).unwrap();
    let mut out = [0xa5; 256];
    assert!(matches!(
        o.directory_context(18, b.session, a.root.handle, &mut out),
        Err(p::Error::Denied)
    ));
    let f = o
        .lookup(17, a.session, a.root.handle, b"file", p::Rights::READ)
        .unwrap();
    assert!(matches!(
        o.directory_context(17, a.session, f.handle, &mut out),
        Err(p::Error::Denied)
    ));
    let f = o
        .lookup(
            17,
            a.session,
            a.root.handle,
            b"file",
            p::Rights::new(3).unwrap(),
        )
        .unwrap();
    assert!(matches!(
        o.directory_context(17, a.session, f.handle, &mut out),
        Err(p::Error::NotDirectory)
    ));
    let limited = o.attach(19, p::Rights::LOOKUP).unwrap();
    assert!(matches!(
        o.directory_context(19, limited.session, limited.root.handle, &mut out),
        Err(p::Error::Denied)
    ));
    assert_eq!(s.lock().unwrap().gets, 0);
    assert_eq!(out, [0; 256]);
    o.shutdown();
}
#[test]
fn malformed_provider_context_is_zeroed_and_retires_owner() {
    for mode in 2..=8 {
        let s = Shared::default();
        let mut o = p::Owner::new(Graph(s.clone()), Time, 72).unwrap();
        let a = o.attach(17, p::Rights::new(3).unwrap()).unwrap();
        let dir = if mode == 8 {
            a.root
        } else {
            o.lookup(
                17,
                a.session,
                a.root.handle,
                b"work",
                p::Rights::new(3).unwrap(),
            )
            .unwrap()
        };
        s.lock().unwrap().mode = mode;
        let mut out = [0xa5; 256];
        assert!(
            matches!(
                o.directory_context(17, a.session, dir.handle, &mut out),
                Err(p::Error::InvalidMetadata)
            ),
            "mode{mode}"
        );
        assert_eq!(out, [0; 256]);
        let drops = s.lock().unwrap().drops;
        assert_eq!(drops, 1);
        assert!(o
            .directory_context(17, a.session, dir.handle, &mut out)
            .is_err());
        assert_eq!(s.lock().unwrap().gets, 1);
    }
}
fn reply(token: u64, kind: u64, size: u64) -> Message {
    let mut r = message(91, 0);
    put(&mut r, 3, token);
    put(&mut r, 4, kind);
    put(&mut r, 5, size);
    r
}
#[derive(Default)]
struct Seen {
    sent: Vec<Message>,
    closes: usize,
}
struct Script {
    input: VecDeque<Result<Message, i64>>,
    seen: Arc<Mutex<Seen>>,
}
impl Channel for Script {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        *out = self.input.pop_front().unwrap_or(Err(-32))?;
        Ok(())
    }
    fn send(&mut self, out: &Message) -> Result<(), i64> {
        self.seen.lock().unwrap().sent.push(*out);
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        [0; 2]
    }
}
fn scripted(input: Vec<Result<Message, i64>>) -> (Client<Script>, Arc<Mutex<Seen>>) {
    let seen = Arc::new(Mutex::new(Seen::default()));
    let c = Client::connect(
        Script {
            input: input.into(),
            seen: seen.clone(),
        },
        91,
        3,
    )
    .ok()
    .unwrap();
    (c, seen)
}
#[test]
fn every_path_frame_loss_padding_and_malformed_path_retires_without_partial_output() {
    for mode in 0..8 {
        let mut header = reply(0, 0, 7);
        let mut body = [0; 64];
        body[..7].copy_from_slice(b"/workx\0");
        match mode {
            0 => put(&mut header, 5, 257),
            1 => put(&mut header, 3, 1),
            2 => header[48] = 1,
            3 => body[8] = 1,
            4 => body[0] = b'x',
            5 => body[6] = b'x',
            6 => body[2] = 0,
            _ => (),
        };
        let last = if mode == 7 { Err(-32) } else { Ok(body) };
        let (mut c, seen) = scripted(vec![
            Ok(reply(1, 1, 2)),
            Ok(reply(2, 1, 2)),
            Ok(header),
            last,
        ]);
        let dir = c.lookup(c.root().unwrap(), b"work", 3).unwrap();
        let mut out = [0xa5; 256];
        assert!(c.directory_path(dir.handle, &mut out).is_err());
        assert_eq!(out, [0; 256]);
        assert_eq!(c.root(), Err(Error::Closed));
        assert_eq!(seen.lock().unwrap().closes, 1);
        let before = seen.lock().unwrap().sent.len();
        assert!(c.directory_path(dir.handle, &mut out).is_err());
        assert_eq!(seen.lock().unwrap().sent.len(), before);
    }
}
#[test]
fn parent_reply_root_is_borrowed_but_arbitrary_token_or_file_retires() {
    for invalid in [reply(99, 1, 2), reply(2, 2, 2), reply(1, 2, 2)] {
        let (mut c, seen) = scripted(vec![Ok(reply(1, 1, 2)), Ok(invalid)]);
        assert!(c.parent_directory(c.root().unwrap()).is_err());
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
    let (mut c, seen) = scripted(vec![
        Ok(reply(1, 1, 2)),
        Ok(reply(2, 1, 2)),
        Ok(reply(1, 1, 2)),
    ]);
    let root = c.root().unwrap();
    let dir = c.lookup(root, b"work", 3).unwrap();
    assert_eq!(c.parent_directory(dir.handle).unwrap().handle, root);
    assert_eq!(word(&seen.lock().unwrap().sent[2], 1), 13);
}
#[test]
fn failed_temporary_close_overrides_known_error_and_does_not_replay() {
    let mut denied = message(91, (-13i64) as u64);
    put(&mut denied, 3, 0);
    let missing = message(91, (-2i64) as u64);
    let (mut c, seen) = scripted(vec![
        Ok(reply(1, 1, 2)),
        Ok(reply(2, 1, 2)),
        Ok(missing),
        Ok(denied),
    ]);
    let root = c.root().unwrap();
    assert_eq!(
        c.resolve_file_from(root, b"work/missing"),
        Err(Error::Remote(-13))
    );
    assert_eq!(c.root(), Err(Error::Closed));
    assert_eq!(seen.lock().unwrap().closes, 1);
    assert_eq!(
        seen.lock()
            .unwrap()
            .sent
            .iter()
            .filter(|r| word(r, 1) == 3)
            .count(),
        1
    );
}

use filesystem_fd_protocol::Connection;
use filesystem_remote_descriptors::{NativeIdentity, ProcessFiles};
fn identity(slot: u32) -> NativeIdentity {
    NativeIdentity::admitted(slot, 1, 0xb0000100 | (u64::from(slot) + 1)).unwrap()
}
fn pool() -> (
    ProcessFiles<Pipe>,
    thread::JoinHandle<filesystem_service::Report>,
    Shared,
) {
    let state = Shared::default();
    let (io, w) = transport(state.clone());
    (ProcessFiles::connect(io, 91).ok().unwrap(), w, state)
}
#[test]
fn public_cwd_is_inherited_fork_local_preserved_exec_and_released_at_settlement() {
    let (mut f, w, s) = pool();
    let parent = f.admitted_shell(identity(1), 7).unwrap();
    f.change_directory(parent, b"work/nested").unwrap();
    let child = f.inherited_child(parent, identity(2), 9).unwrap();
    let mut out = [0; 256];
    assert_eq!(f.current_directory(child, &mut out), Ok(13));
    f.change_directory(parent, b"../..").unwrap();
    assert_eq!(f.current_directory(parent, &mut out), Ok(2));
    f.commit_exec_close(child).unwrap();
    assert_eq!(f.current_directory(child, &mut out), Ok(13));
    s.lock().unwrap().renamed = true;
    assert_eq!(f.current_directory(child, &mut out), Ok(16));
    let fd = f.open_read(child, b"../../file", true).unwrap();
    let mut bytes = [0; 4096];
    assert_eq!(f.read(child, fd, 6, &mut bytes), Ok(6));
    assert_eq!(&bytes[..6], b"abcdef");
    f.close(child, fd).unwrap();
    f.settled(parent).unwrap();
    assert_eq!(f.current_directory(child, &mut out), Ok(16));
    f.settled(child).unwrap();
    assert!(f.current_directory(child, &mut out).is_err());
    assert_eq!(out, [0; 256]);
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(w.join().unwrap().cleanup, [0; 2]);
}
fn file_request(op: u64, seq: u64, args: [u64; 4]) -> Message {
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(filesystem_fd_protocol::MAGIC);
    put(&mut raw, 1, op);
    put(&mut raw, 2, 31);
    put(&mut raw, 3, seq);
    for (i, a) in args.iter().enumerate() {
        put(&mut raw, i + 4, *a);
    }
    raw
}
#[test]
fn public_wire_chdir_getcwd_error_and_exec_generation_match() {
    let (mut f, w, _) = pool();
    let p = f.admitted_shell(identity(1), 7).unwrap();
    let mut conn = Connection::bind(p, 31).unwrap();
    let mut space = [0; 4096];
    let raw = file_request(8, 1, [0, 13, 0, 0]);
    space[..13].copy_from_slice(b"/work//nested");
    assert_eq!(conn.input_length(&mut f, &raw), Ok(64));
    let reply = conn.prepare(&mut f, &raw, 64, &mut space).ok().unwrap();
    assert_eq!(word(reply.header(), 1), 0);
    assert!(reply.body().is_empty());
    reply.delivered();
    let reply = conn
        .prepare(&mut f, &file_request(9, 2, [0; 4]), 0, &mut space)
        .ok()
        .unwrap();
    assert_eq!(word(reply.header(), 4), 13);
    assert_eq!(word(reply.header(), 5), 13);
    assert_eq!(&reply.body()[..13], b"/work/nested\0");
    assert!(reply.body()[13..].iter().all(|b| *b == 0));
    reply.delivered();
    let raw = file_request(8, 3, [0, 7, 0, 0]);
    space[..7].copy_from_slice(b"missing");
    let reply = conn.prepare(&mut f, &raw, 64, &mut space).ok().unwrap();
    assert_eq!(word(reply.header(), 1) as i64, -2);
    assert!(reply.body().is_empty());
    reply.delivered();
    f.commit_exec_close(p).unwrap();
    conn.rebind_after_exec(p, 32).unwrap();
    assert_eq!(
        f.current_directory(p, (&mut space[..256]).try_into().unwrap()),
        Ok(13)
    );
    f.settled(p).unwrap();
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(w.join().unwrap().cleanup, [0; 2]);
}
#[test]
fn bad_file_version_reserved_bytes_body_padding_and_lost_reply_retire() {
    for mode in 0..6 {
        let (mut f, w, _) = pool();
        let p = f.admitted_shell(identity(1), 7).unwrap();
        let mut conn = Connection::bind(p, 31).unwrap();
        let mut space = [0; 4096];
        let mut raw = file_request(8, 1, [0, 4, 0, 0]);
        space[..4].copy_from_slice(b"work");
        match mode {
            0 => raw[..8].copy_from_slice(b"AEFP0002"),
            1 => put(&mut raw, 4, 1),
            2 => put(&mut raw, 6, 1),
            3 => space[4] = 1,
            4 => put(&mut raw, 5, 256),
            _ => (),
        }
        let result = conn.prepare(&mut f, &raw, 64, &mut space);
        if mode == 5 {
            drop(result.ok().unwrap());
        } else {
            assert!(result.is_err());
            drop(result);
        }
        assert!(f.cleanup().is_some());
        assert_eq!(space, [0; 4096]);
        drop(f);
        w.join().unwrap();
    }
}
#[test]
fn c_requests_execute_through_actual_service_and_file_owner() {
    let (mut f, w, _) = pool();
    let p = f.admitted_shell(identity(1), 7).unwrap();
    let mut conn = Connection::bind(p, 31).unwrap();
    let mut space = [0; 4096];
    let bytes = std::fs::read(std::env::var("AEFD_C_REQUESTS").unwrap()).unwrap();
    let mut offset = 0;
    let mut out = Vec::new();
    while offset < bytes.len() {
        let raw = &bytes[offset..offset + 64];
        offset += 64;
        let needed = conn.input_length(&mut f, raw).unwrap();
        space.fill(0);
        space[..needed].copy_from_slice(&bytes[offset..offset + needed]);
        offset += needed;
        let reply = conn.prepare(&mut f, raw, needed, &mut space).ok().unwrap();
        out.extend_from_slice(reply.header());
        out.extend_from_slice(reply.body());
        reply.delivered();
    }
    std::fs::write(std::env::var("AEFD_RUST_REPLIES").unwrap(), out).unwrap();
    f.settled(p).unwrap();
    assert_eq!(f.disconnect(), Ok([0; 2]));
    assert_eq!(w.join().unwrap().cleanup, [0; 2]);
}
#[test]
fn service_rejects_old_version_reserved_tokens_and_rights_before_getter() {
    for opcode in [13, 14] {
        for mode in 0..9 {
            let state = Shared::default();
            let seen = Arc::new(Mutex::new(Seen::default()));
            let mut raw = message(91, opcode);
            put(&mut raw, 3, 1);
            match mode {
                0 => raw[7] = b'7',
                1 => put(&mut raw, 2, 90),
                2 => put(&mut raw, 3, 999),
                3..=6 => put(&mut raw, mode + 1, 1),
                _ => (),
            }
            let rights = if mode == 7 {
                1
            } else if mode == 8 {
                2
            } else {
                3
            };
            let owner = p::Owner::new(Graph(state.clone()), Time, 72).unwrap();
            let result = filesystem_service::run(
                owner,
                Script {
                    input: vec![Ok(raw)].into(),
                    seen: seen.clone(),
                },
                17,
                p::Rights::new(rights).unwrap(),
                91,
            );
            assert_eq!(result.requests, 1);
            assert_eq!(state.lock().unwrap().gets, 0);
            let sent = seen.lock().unwrap().sent.clone();
            assert_eq!(sent.len(), 2);
            assert_ne!(word(&sent[1], 1), 0);
            assert!(sent[1][24..].iter().all(|b| *b == 0));
            assert_eq!(seen.lock().unwrap().closes, 1);
        }
    }
}
