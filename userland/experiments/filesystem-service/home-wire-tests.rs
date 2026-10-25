// SPDX-License-Identifier: BSD-2-Clause
//! Actual two-grant service/client over synthetic storage; no native IPC claim.
use filesystem_client::{Client, Error};
use filesystem_policy as p;
use filesystem_service::{message, put, word, Channel, Message, Report, Stop};
use std::{
    collections::VecDeque,
    sync::{mpsc, Arc, Mutex},
    thread,
    time::Duration,
};

#[derive(Default)]
struct State {
    lookups: usize,
    writes: usize,
    mutations: usize,
    drops: usize,
    created: bool,
    renamed: bool,
    made_directory: bool,
    failure: Option<p::Completion>,
    lost: bool,
    data: [u8; 4],
}
type Shared = Arc<Mutex<State>>;
struct Storage(Shared);
struct Clock;
fn node(id: u64) -> p::Node {
    p::Node::new(
        id,
        id + 10,
        if id == 4 || id == 5 { 4 } else { 2 },
        if id == 4 || id == 5 {
            p::Kind::File
        } else {
            p::Kind::Directory
        },
    )
}
impl Drop for Storage {
    fn drop(&mut self) {
        self.0.lock().unwrap().drops += 1;
    }
}
impl p::Backend for Storage {
    fn root(&mut self) -> Result<p::Node, p::Error> {
        Ok(node(1))
    }
    fn directory(&mut self, n: p::Node) -> Result<p::Node, p::Error> {
        Ok(n)
    }
    fn lookup(&mut self, at: p::Node, name: &[u8]) -> Result<p::Node, p::Error> {
        let mut s = self.0.lock().unwrap();
        s.lookups += 1;
        match (at.identity().0, name) {
            (1, b"home") => Ok(node(2)),
            (1, b"system") => Ok(node(5)),
            (2, b"nested") => Ok(node(3)),
            (2 | 3, b"data") => Ok(node(4)),
            (2, b"created") if s.created => Ok(node(4)),
            (2, b"renamed") if s.renamed => Ok(node(4)),
            (2, b"dir") if s.made_directory => Ok(node(3)),
            _ => Err(p::Error::Backend(2)),
        }
    }
    fn read(&mut self, n: p::Node, offset: u64, out: &mut [u8]) -> Result<usize, p::Error> {
        let s = self.0.lock().unwrap();
        let data = if n.identity().0 == 5 {
            *b"sys!"
        } else {
            s.data
        };
        let start = (offset as usize).min(4);
        let count = out.len().min(4 - start);
        out[..count].copy_from_slice(&data[start..start + count]);
        Ok(count)
    }
    fn write(
        &mut self,
        n: p::Node,
        offset: u64,
        data: &[u8],
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        assert_eq!(n.identity().0, 4, "SYSTEM_WRITE");
        let mut s = self.0.lock().unwrap();
        s.writes += 1;
        if s.lost {
            return Err(p::Lost);
        }
        if let Some(failure) = s.failure {
            return Ok(failure);
        }
        let start = offset as usize;
        s.data[start..start + data.len()].copy_from_slice(data);
        Ok(p::Completion {
            error: 0,
            txg: 1,
            bytes_staged: data.len() as u64,
            state: 2,
        })
    }
    fn mutate(
        &mut self,
        n: p::Node,
        op: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        assert_eq!(n.identity().0, 2, "SYSTEM_MUTATION");
        let mut s = self.0.lock().unwrap();
        s.mutations += 1;
        if s.lost {
            return Err(p::Lost);
        }
        if let Some(failure) = s.failure {
            return Ok(failure);
        }
        match op {
            p::Namespace::Create {
                name: b"created", ..
            } => s.created = true,
            p::Namespace::Rename {
                from: b"created",
                to: b"renamed",
                ..
            } => {
                s.created = false;
                s.renamed = true;
            }
            p::Namespace::Remove {
                name: b"renamed", ..
            } => s.renamed = false,
            p::Namespace::MakeDirectory { name: b"dir", .. } => s.made_directory = true,
            p::Namespace::RemoveDirectory { name: b"dir", .. } => s.made_directory = false,
            _ => panic!("unexpected fixture namespace operation"),
        }
        Ok(p::Completion {
            error: 0,
            txg: 2,
            bytes_staged: 0,
            state: 2,
        })
    }
    fn directory_context(
        &mut self,
        root: p::Node,
        at: p::Node,
        out: &mut [u8; 256],
    ) -> Result<(p::Node, usize), p::Error> {
        assert_eq!(root.identity().0, 1);
        let (parent, path) = match at.identity().0 {
            1 => (1, b"/\0".as_slice()),
            2 => (1, b"/home\0".as_slice()),
            3 => (2, b"/home/nested\0".as_slice()),
            _ => return Err(p::Error::NotDirectory),
        };
        out[..path.len()].copy_from_slice(path);
        Ok((node(parent), path.len()))
    }
}
impl p::Clock for Clock {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        Ok(p::Utc {
            seconds: 1,
            nanoseconds: 0,
        })
    }
}
fn owner(s: Shared) -> (p::Owner<Storage, Clock>, p::Attachment, p::Entry) {
    let mut o = p::Owner::new(Storage(s), Clock, 91)
        .unwrap()
        .with_namespace_identity(p::Identity::new(1, 1).unwrap());
    let a = o.attach(7, p::Rights::ALL).unwrap();
    let h = o
        .lookup(7, a.session, a.root.handle, b"home", p::Rights::ALL)
        .unwrap();
    (o, a, h)
}
#[derive(Default)]
struct Seen {
    sent: Vec<Message>,
    closes: usize,
    receives: usize,
}
type Observed = Arc<Mutex<Seen>>;
struct Pipe {
    tx: Option<mpsc::Sender<Message>>,
    rx: mpsc::Receiver<Message>,
    seen: Observed,
}
impl Channel for Pipe {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        *out = self
            .rx
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        Ok(())
    }
    fn send(&mut self, f: &Message) -> Result<(), i64> {
        self.seen.lock().unwrap().sent.push(*f);
        self.tx.as_ref().unwrap().send(*f).map_err(|_| -32)
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        self.tx.take();
        [0; 2]
    }
}
fn pair() -> (Pipe, Pipe, Observed, Observed) {
    let (a, b) = mpsc::channel();
    let (c, d) = mpsc::channel();
    let x = Observed::default();
    let y = Observed::default();
    (
        Pipe {
            tx: Some(a),
            rx: d,
            seen: x.clone(),
        },
        Pipe {
            tx: Some(c),
            rx: b,
            seen: y.clone(),
        },
        x,
        y,
    )
}
fn start() -> (Pipe, thread::JoinHandle<Report>, Shared, Observed, Observed) {
    let (c, s, cs, ss) = pair();
    let state = Shared::default();
    let shared = state.clone();
    let join = thread::spawn(move || {
        let (o, a, h) = owner(shared);
        filesystem_service::run_home(o, s, 7, a.session, h.handle, 8, 91)
    });
    (c, join, state, cs, ss)
}
fn greeting(token: u64) -> Message {
    let mut f = message(91, 0);
    put(&mut f, 3, token);
    put(&mut f, 4, 1);
    put(&mut f, 5, 2);
    f
}
struct Script {
    input: VecDeque<Result<Message, i64>>,
    seen: Observed,
    fail: Option<usize>,
}
impl Channel for Script {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        self.seen.lock().unwrap().receives += 1;
        *out = self.input.pop_front().unwrap_or(Err(-32))?;
        Ok(())
    }
    fn send(&mut self, f: &Message) -> Result<(), i64> {
        let mut s = self.seen.lock().unwrap();
        s.sent.push(*f);
        if self.fail == Some(s.sent.len()) {
            Err(-32)
        } else {
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        [-9, -5]
    }
}
fn script(frames: Vec<Result<Message, i64>>) -> (Script, Observed) {
    let seen = Observed::default();
    (
        Script {
            input: frames.into(),
            seen: seen.clone(),
            fail: None,
        },
        seen,
    )
}
#[test]
fn actual_client_reads_both_grants_and_keeps_parents_read_only() {
    let (io, j, state, cs, ss) = start();
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let root = c.root().unwrap();
    let home = c.home().unwrap();
    assert_ne!(root, home);
    let mut path = [0; 256];
    assert_eq!(c.directory_path(home, &mut path), Ok(6));
    assert_eq!(&path[..6], b"/home\0");
    let parent = c.parent_directory(home).unwrap();
    assert_eq!(parent.handle, root);
    assert!(
        matches!(c.resolve_directory_from(home, b".").unwrap(), filesystem_client::ResolvedDirectory::Borrowed(entry) if entry.handle == home)
    );
    assert!(
        matches!(c.resolve_directory_from(home, b"..").unwrap(), filesystem_client::ResolvedDirectory::Borrowed(entry) if entry.handle == root)
    );
    let nested = c.lookup(home, b"nested", 15).unwrap();
    let physical_home = c.parent_directory(nested.handle).unwrap();
    assert_ne!(physical_home.handle, home);
    let before_alias = cs.lock().unwrap().sent.len();
    assert_eq!(
        c.lookup(physical_home.handle, b"data", 6),
        Err(Error::Invalid)
    );
    assert_eq!(cs.lock().unwrap().sent.len(), before_alias);
    c.close(physical_home.handle).unwrap();
    c.close(nested.handle).unwrap();
    let before = cs.lock().unwrap().sent.len();
    assert_eq!(c.lookup(root, b"home", 15), Err(Error::Invalid));
    assert_eq!(c.lookup(parent.handle, b"home", 15), Err(Error::Invalid));
    assert_eq!(c.close(root), Err(Error::Invalid));
    assert_eq!(c.close(home), Err(Error::Invalid));
    assert_eq!(cs.lock().unwrap().sent.len(), before);
    let f = c.lookup(home, b"data", 6).unwrap();
    let mut out = [0; 4096];
    assert_eq!(c.read(f.handle, 0, 4, &mut out), Ok(4));
    c.close(f.handle).unwrap();
    let f = c.lookup(root, b"system", 2).unwrap();
    assert_eq!(c.read(f.handle, 0, 4, &mut out), Ok(4));
    assert_eq!(&out[..4], b"sys!");
    c.close(f.handle).unwrap();
    assert_eq!(c.disconnect(), Ok([0, 0]));
    drop(c);
    let r = j.join().unwrap();
    assert_eq!(r.stop, Stop::Disconnected);
    assert!(r.ready);
    assert_eq!(cs.lock().unwrap().closes, 1);
    assert_eq!(ss.lock().unwrap().closes, 1);
    assert_eq!(state.lock().unwrap().drops, 1);
    let frames = &ss.lock().unwrap().sent;
    assert_eq!(frames[0], greeting(1));
    assert_eq!(frames[1], greeting(2));
    assert_eq!(word(&frames[4], 3), 1);
}
#[test]
fn malformed_or_lost_either_greeting_never_publishes_or_sends() {
    for position in 0..2 {
        for field in [0, 1, 2, 3, 4, 6, 7] {
            let mut frames = vec![Ok(greeting(1)), Ok(greeting(2))];
            let mut f = frames[position].unwrap();
            if field == 0 {
                f[0] ^= 1
            } else {
                put(
                    &mut f,
                    field,
                    if field == 1 {
                        (-13i64) as u64
                    } else if field == 4 {
                        2
                    } else {
                        999
                    },
                )
            }
            frames[position] = Ok(f);
            let (io, seen) = script(frames);
            assert!(
                Client::connect_home(io, 91).is_err(),
                "HOME_GREETING_VALIDATION"
            );
            let s = seen.lock().unwrap();
            assert_eq!(s.closes, 1);
            assert!(s.sent.is_empty());
        }
        let mut frames = vec![Ok(greeting(1)), Ok(greeting(2))];
        frames[position] = Err(-32);
        let (io, seen) = script(frames);
        assert!(Client::connect_home(io, 91).is_err());
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn old_connect_and_zero_epoch_refuse_without_receiving() {
    for epoch in [0, 91] {
        let (io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2))]);
        assert!(Client::connect(io, epoch, 3).is_err());
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
    let (io, seen) = script(vec![]);
    assert!(Client::connect_home(io, 0).is_err());
    assert_eq!(seen.lock().unwrap().closes, 1);
}
#[test]
fn each_service_greeting_loss_stops_before_ready_or_dispatch() {
    for failure in [1, 2] {
        let state = Shared::default();
        let (o, a, h) = owner(state.clone());
        let (mut io, seen) = script(vec![]);
        io.fail = Some(failure);
        let r = filesystem_service::run_home(o, io, 7, a.session, h.handle, 8, 91);
        assert_eq!(r.stop, Stop::ReplyLost(-32));
        assert!(!r.ready, "HOME_READY_AFTER_BOTH");
        assert_eq!(r.requests, 0);
        assert_eq!(seen.lock().unwrap().sent.len(), failure);
        assert_eq!(seen.lock().unwrap().closes, 1);
        assert_eq!(r.cleanup, [-9, -5]);
        assert_eq!(state.lock().unwrap().drops, 1);
    }
}
#[test]
fn failed_source_provisioning_has_no_greeting() {
    for zero_epoch in [false, true] {
        let state = Shared::default();
        let (o, a, h) = owner(state.clone());
        let (io, seen) = script(vec![]);
        let r = filesystem_service::run_home(
            o,
            io,
            if zero_epoch { 7 } else { 9 },
            a.session,
            h.handle,
            8,
            if zero_epoch { 0 } else { 91 },
        );
        assert!(matches!(r.stop, Stop::Provision(_)));
        assert!(!r.ready);
        assert_eq!(r.requests, 0);
        assert!(seen.lock().unwrap().sent.is_empty());
        assert_eq!(state.lock().unwrap().drops, 1);
    }
}
fn exchange(io: &mut Pipe, f: Message) -> Message {
    io.send(&f).unwrap();
    let mut out = [0; 64];
    io.receive(&mut out).unwrap();
    out
}
fn named(io: &mut Pipe, op: u64, parent: u64, rights: u64, name: &[u8]) -> Message {
    let mut f = message(91, op);
    put(&mut f, 3, parent);
    put(&mut f, 4, rights);
    put(&mut f, 5, name.len() as u64);
    io.send(&f).unwrap();
    let mut body = [0; 64];
    body[..name.len()].copy_from_slice(name);
    exchange(io, body)
}
fn raw_start() -> (Pipe, thread::JoinHandle<Report>, Shared) {
    let (mut io, j, s, _, _) = start();
    let mut f = [0; 64];
    io.receive(&mut f).unwrap();
    assert_eq!(f, greeting(1));
    io.receive(&mut f).unwrap();
    assert_eq!(f, greeting(2));
    (io, j, s)
}
#[test]
fn raw_home_mutations_work_but_system_and_read_aliases_are_denied() {
    let (mut io, j, s) = raw_start();
    assert_eq!(word(&named(&mut io, 7, 1, 0, b"created"), 1) as i64, -13);
    assert_eq!(word(&named(&mut io, 1, 1, 15, b"home"), 1) as i64, -13);
    assert_eq!(
        word(&named(&mut io, 7, 2, 0, b"created"), 1),
        0,
        "HOME_MUTATION_ACK"
    );
    let f = named(&mut io, 1, 2, 6, b"created");
    assert_eq!(word(&f, 3), 3, "HOME_TOKEN_AFTER_TWO");
    let mut write = message(91, 5);
    put(&mut write, 3, 3);
    put(&mut write, 5, 4);
    io.send(&write).unwrap();
    let mut bytes = [0; 64];
    bytes[..4].copy_from_slice(b"home");
    assert_eq!(word(&exchange(&mut io, bytes), 1), 0);
    let alias = named(&mut io, 1, 1, 3, b"home");
    assert_eq!(word(&alias, 3), 4);
    assert_eq!(word(&named(&mut io, 7, 4, 0, b"created"), 1) as i64, -13);
    let mut disconnect = message(91, 4);
    put(&mut disconnect, 3, 0);
    exchange(&mut io, disconnect);
    io.close();
    let r = j.join().unwrap();
    assert_eq!(r.stop, Stop::Disconnected);
    let s = s.lock().unwrap();
    assert_eq!((s.writes, s.mutations, s.drops), (1, 1, 1));
}
#[test]
fn malformed_body_and_reply_loss_retire_without_replay() {
    let (mut io, j, s) = raw_start();
    let mut f = message(91, 7);
    put(&mut f, 3, 2);
    put(&mut f, 5, 7);
    io.send(&f).unwrap();
    let mut body = [0; 64];
    body[..7].copy_from_slice(b"created");
    body[63] = 1;
    io.send(&body).unwrap();
    io.close();
    assert_eq!(j.join().unwrap().stop, Stop::Receive(-22));
    assert_eq!(s.lock().unwrap().mutations, 0);
    let (io, seen) = script(vec![Ok(greeting(1)), Ok(greeting(2)), Err(-32)]);
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let home = c.home().unwrap();
    assert!(c.stat(home).is_err());
    let count = seen.lock().unwrap().sent.len();
    assert_eq!(c.home(), Err(Error::Closed));
    assert!(c.stat(home).is_err());
    drop(c);
    assert_eq!(seen.lock().unwrap().sent.len(), count);
    assert_eq!(seen.lock().unwrap().closes, 1);
}
#[test]
fn retained_source_slots_bound_owner_capacity_and_failed_lookup_keeps_next_token() {
    let (io, j, _, _, _) = start();
    let mut c = Client::connect_home(io, 91).ok().unwrap();
    let home = c.home().unwrap();
    let mut handles = vec![];
    for _ in 0..12 {
        handles.push(c.lookup(home, b"data", 2).unwrap().handle);
    }
    assert_eq!(c.lookup(home, b"data", 2), Err(Error::Remote(-28)));
    c.close(handles.pop().unwrap()).unwrap();
    let f = c.lookup(home, b"data", 2).unwrap();
    c.close(f.handle).unwrap();
    for h in handles {
        c.close(h).unwrap();
    }
    c.disconnect().unwrap();
    assert_eq!(j.join().unwrap().stop, Stop::Disconnected);
}

#[cfg(fs_client_mutations)]
#[path = "mutation-client-tests.rs"]
mod mutations;

#[cfg(fs_process_writes)]
#[path = "process-write-tests.rs"]
mod process_writes;

#[cfg(fs_file_write_wire)]
#[path = "file-write-tests.rs"]
mod file_writes;

#[cfg(fs_home_in_place)]
#[path = "home-in-place-tests.rs"]
mod home_in_place;
