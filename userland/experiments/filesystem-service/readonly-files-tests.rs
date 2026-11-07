// SPDX-License-Identifier: BSD-2-Clause
//! Actual AF09 Owner/service/Client over synthetic storage; native execution is separate.
use super::*;
use filesystem_policy as p;
use std::{
    sync::{Arc, Mutex, mpsc},
    thread,
    time::Duration,
    vec::Vec,
};
const DATA: &[u8] = b"actual terminfo bytes";
#[derive(Default)]
struct StorageState {
    made: [bool; 3],
    data: Vec<u8>,
    #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
    probe: Vec<u8>,
    #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
    probe_failure: u8,
    #[cfg(native_zsh_file_exec)]
    probe_read_failure: u8,
    #[cfg(native_zsh_cold_reopen)]
    data_read_failure: u8,
    #[cfg(native_zsh_cold_reopen)]
    wrong_kind: u64,
    #[cfg(native_zsh_home_redirection)]
    note: Vec<u8>,
    #[cfg(native_zsh_home_redirection)]
    note_exists: bool,
    #[cfg(native_zsh_home_redirection)]
    note_failure: u8,
    #[cfg(native_zsh_home_redirection)]
    note_lookup_failure: bool,
    mutations: usize,
    lookups: usize,
    reads: usize,
}
type Shared = Arc<Mutex<StorageState>>;
struct Storage(Shared);
fn node(id: u64, size: usize) -> p::Node {
    p::Node::new(
        id,
        1,
        size as u64,
        if id == 5
            || (cfg!(any(native_zsh_home_write, native_zsh_file_exec)) && id == 6)
            || (cfg!(native_zsh_home_redirection) && id == 7)
        {
            p::Kind::File
        } else {
            p::Kind::Directory
        },
    )
}
impl p::Backend for Storage {
    fn root(&mut self) -> Result<p::Node, p::Error> {
        Ok(node(1, 0))
    }
    fn directory(&mut self, n: p::Node) -> Result<p::Node, p::Error> {
        Ok(n)
    }
    fn lookup(&mut self, at: p::Node, name: &[u8]) -> Result<p::Node, p::Error> {
        let mut s = self.0.lock().unwrap();
        s.lookups += 1;
        let id = match (at.identity().0, name) {
            (1, b"home") => 2,
            (2, b".terminfo") if s.made[0] => 3,
            (3, b"v") if s.made[1] => 4,
            (4, b"vt100") if s.made[2] => 5,
            #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
            (2, b"probe") => 6,
            #[cfg(native_zsh_home_redirection)]
            (2, b"note") if s.note_exists => {
                if s.note_lookup_failure {
                    return Err(p::Error::Backend(5));
                }
                7
            }
            _ => return Err(p::Error::Backend(2)),
        };
        #[cfg(native_zsh_cold_reopen)]
        if s.wrong_kind == id {
            return Ok(p::Node::new(id, 1, 0, p::Kind::Directory));
        }
        #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
        if id == 6 {
            return Ok(node(id, s.probe.len()));
        }
        #[cfg(native_zsh_home_redirection)]
        if id == 7 {
            return Ok(node(id, s.note.len()));
        }
        Ok(node(id, if id == 5 { s.data.len() } else { 0 }))
    }
    fn read(&mut self, at: p::Node, offset: u64, out: &mut [u8]) -> Result<usize, p::Error> {
        let mut s = self.0.lock().unwrap();
        s.reads += 1;
        #[cfg(native_zsh_cold_reopen)]
        if at.identity().0 == 5 {
            match s.data_read_failure {
                1 if offset == 0 => return Ok(out.len().saturating_sub(1)),
                2 => return Err(p::Error::Backend(5)),
                3 if offset > 0 => {
                    out[0] = 1;
                    return Ok(1);
                }
                _ => (),
            }
        }
        #[cfg(native_zsh_file_exec)]
        if at.identity().0 == 6 {
            match s.probe_read_failure {
                1 if offset == 0 => return Ok(out.len().saturating_sub(1)),
                2 => return Err(p::Error::Backend(5)),
                3 if offset > 0 => {
                    out[0] = 1;
                    return Ok(1);
                }
                _ => (),
            }
        }
        #[cfg(not(any(native_zsh_home_write, native_zsh_file_exec)))]
        let _ = at;
        #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
        let data = if at.identity().0 == 6 {
            &s.probe
        } else {
            &s.data
        };
        #[cfg(not(any(native_zsh_home_write, native_zsh_file_exec)))]
        let data = &s.data;
        #[cfg(native_zsh_home_redirection)]
        let data = if at.identity().0 == 7 { &s.note } else { data };
        let start = (offset as usize).min(data.len());
        let count = out.len().min(data.len() - start);
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
        #[cfg(native_zsh_home_redirection)]
        if n.identity().0 == 7 {
            let mut s = self.0.lock().unwrap();
            s.mutations += 1;
            assert_eq!(offset, 0);
            s.note = data.to_vec();
            return match s.note_failure {
                4 => Err(p::Lost),
                5 => Ok(p::Completion {
                    error: 5,
                    txg: 99,
                    bytes_staged: data.len() as u64,
                    state: 1,
                }),
                _ => Ok(p::Completion {
                    error: 0,
                    txg: s.mutations as u64,
                    bytes_staged: data.len() as u64,
                    state: 2,
                }),
            };
        }
        #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
        if n.identity().0 == 6 {
            assert_eq!(offset, 0);
            let mut s = self.0.lock().unwrap();
            s.mutations += 1;
            s.probe = data.to_vec();
            return match s.probe_failure {
                1 => Err(p::Lost),
                2 => Ok(p::Completion {
                    error: 5,
                    txg: 99,
                    bytes_staged: data.len() as u64,
                    state: 1,
                }),
                _ => Ok(p::Completion {
                    error: 0,
                    txg: s.mutations as u64,
                    bytes_staged: data.len() as u64,
                    state: 2,
                }),
            };
        }
        assert_eq!((n.identity().0, offset), (5, 0));
        let mut s = self.0.lock().unwrap();
        s.mutations += 1;
        s.data = data.to_vec();
        Ok(p::Completion {
            error: 0,
            txg: s.mutations as u64,
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
        #[cfg(native_zsh_home_redirection)]
        if matches!(
            (n.identity().0, &op),
            (2, p::Namespace::Create { name: b"note", .. })
        ) {
            let mut s = self.0.lock().unwrap();
            s.mutations += 1;
            if s.note_exists || s.note_failure == 3 {
                return Ok(p::Completion {
                    error: 17,
                    txg: 0,
                    bytes_staged: 0,
                    state: 0,
                });
            }
            s.note_exists = true;
            return match s.note_failure {
                1 => Err(p::Lost),
                2 => Ok(p::Completion {
                    error: 5,
                    txg: 99,
                    bytes_staged: 0,
                    state: 1,
                }),
                _ => Ok(p::Completion {
                    error: 0,
                    txg: s.mutations as u64,
                    bytes_staged: 0,
                    state: 2,
                }),
            };
        }
        let index = match (n.identity().0, op) {
            (
                2,
                p::Namespace::MakeDirectory {
                    name: b".terminfo", ..
                },
            ) => 0,
            (3, p::Namespace::MakeDirectory { name: b"v", .. }) => 1,
            (4, p::Namespace::Create { name: b"vt100", .. }) => 2,
            _ => panic!("UNAUTHORIZED_MUTATION"),
        };
        let mut s = self.0.lock().unwrap();
        assert!(!s.made[index]);
        s.made[index] = true;
        s.mutations += 1;
        Ok(p::Completion {
            error: 0,
            txg: s.mutations as u64,
            bytes_staged: 0,
            state: 2,
        })
    }
}
struct Time;
impl p::Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        Ok(p::Utc {
            seconds: 1,
            nanoseconds: 0,
        })
    }
}
#[derive(Default)]
struct Seen {
    closes: usize,
    sent: Vec<[u8; 64]>,
    #[cfg(native_zsh_cold_reopen)]
    fail_close: usize,
    #[cfg(native_zsh_cold_reopen)]
    close_replies: usize,
    #[cfg(native_zsh_cold_reopen)]
    bad_stat: bool,
}
struct Pipe {
    tx: Option<mpsc::Sender<[u8; 64]>>,
    rx: mpsc::Receiver<[u8; 64]>,
    seen: Arc<Mutex<Seen>>,
}
impl Channel for Pipe {
    fn send(&mut self, f: &[u8; 64]) -> Result<(), i64> {
        self.seen.lock().unwrap().sent.push(*f);
        self.tx.as_ref().unwrap().send(*f).map_err(|_| -32)
    }
    fn receive(&mut self, f: &mut [u8; 64]) -> Result<(), i64> {
        *f = self
            .rx
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        #[cfg(native_zsh_cold_reopen)]
        {
            let mut seen = self.seen.lock().unwrap();
            if seen.bad_stat
                && seen
                    .sent
                    .last()
                    .is_some_and(|request| word(request, 1) == 6)
            {
                put(f, 5, word(f, 5) + 1);
            }
            if seen
                .sent
                .last()
                .is_some_and(|request| word(request, 1) == 3)
            {
                seen.close_replies += 1;
                if seen.fail_close == seen.close_replies {
                    put(f, 1, (-5i64) as u64);
                }
            }
        }
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        if self.tx.take().is_some() {
            self.seen.lock().unwrap().closes += 1;
        }
        [0; 2]
    }
}
fn binding() -> Binding {
    Binding {
        slot: 1,
        epoch: 1,
        handle: 0xb0000102,
        generation: 31,
    }
}
struct Harness {
    slot: MaybeUninit<Files<Pipe>>,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
    state: Shared,
    seen: Arc<Mutex<Seen>>,
}
impl Harness {
    fn new() -> Self {
        let mut h = Self::connected(cfg!(native_zsh_cold_reopen));
        #[cfg(not(native_zsh_cold_reopen))]
        h.files().provision(DATA, &mut [0; 4096]).unwrap();
        #[cfg(native_zsh_cold_reopen)]
        h.files().reopen(DATA, &mut [0; 4096]).unwrap();
        h
    }
    fn connected(prepared: bool) -> Self {
        let (a, b) = mpsc::channel();
        let (c, d) = mpsc::channel();
        let state = Shared::default();
        if prepared {
            let mut storage = state.lock().unwrap();
            storage.made = [true; 3];
            storage.data = DATA.to_vec();
        }
        let shared = state.clone();
        let seen = Arc::new(Mutex::new(Seen::default()));
        let worker = thread::spawn(move || {
            let mut owner = p::Owner::new(Storage(shared), Time, 91)
                .unwrap()
                .with_namespace_identity(p::Identity::new(1000, 1000).unwrap());
            let a = owner.attach(7, p::Rights::new(15).unwrap()).unwrap();
            let home = owner
                .lookup(
                    7,
                    a.session,
                    a.root.handle,
                    b"home",
                    p::Rights::new(15).unwrap(),
                )
                .unwrap();
            filesystem_service::run_home(
                owner,
                Pipe {
                    tx: Some(c),
                    rx: b,
                    seen: Arc::default(),
                },
                7,
                a.session,
                home.handle,
                8,
                91,
            )
        });
        let mut slot = MaybeUninit::uninit();
        Files::connect_in_place(
            &mut slot,
            Pipe {
                tx: Some(a),
                rx: d,
                seen: seen.clone(),
            },
            91,
            binding(),
        )
        .ok()
        .unwrap();
        Self {
            slot,
            worker: Some(worker),
            state,
            seen,
        }
    }
    fn files(&mut self) -> &mut Files<Pipe> {
        unsafe { self.slot.assume_init_mut() }
    }
    fn requests(&self) -> usize {
        let seen = self.seen.lock().unwrap();
        let mut frames = 0;
        let mut requests = 0;
        for f in &seen.sent {
            if frames != 0 {
                frames -= 1;
                continue;
            }
            requests += 1;
            let op = word(f, 1);
            let n = word(f, 5);
            let bytes = match op {
                1 | 5 => n,
                7..=11 => (n & 0xffffffff) + (n >> 32),
                _ => 0,
            };
            frames = (bytes as usize).div_ceil(64);
        }
        requests
    }
    fn rpc(&mut self, op: u64, args: [u64; 4], body: &[u8]) -> ([u8; 64], Vec<u8>) {
        let files = self.files();
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(MAGIC);
        put(&mut raw, 1, op);
        put(&mut raw, 2, 31);
        put(&mut raw, 3, files.next);
        for (i, a) in args.iter().enumerate() {
            put(&mut raw, i + 4, *a);
        }
        let mut workspace = [0; 4096];
        workspace[..body.len()].copy_from_slice(body);
        let length = files.body_length(binding(), &raw).unwrap();
        let mut reply = files
            .prepare(binding(), &raw, length, &mut workspace)
            .unwrap();
        let header = *reply.header();
        let body = reply.body_mut().to_vec();
        reply.delivered();
        (header, body)
    }
}
impl Drop for Harness {
    fn drop(&mut self) {
        self.files().abort();
        unsafe {
            self.slot.assume_init_drop();
        }
        if let Some(worker) = self.worker.take() {
            worker.join().unwrap();
        }
    }
}
#[test]
fn zsh_actual_service_provision_access_cwd_directory_and_cleanup() {
    let mut h = Harness::new();
    assert_eq!(h.requests(), 12);
    assert_eq!(h.state.lock().unwrap().mutations, 4);
    for mode in [0, 4] {
        let (r, b) = h.rpc(8, [mode, ENTRY.len() as u64, 0, 0], ENTRY);
        assert_eq!((word(&r, 1), word(&r, 4), word(&r, 5)), (0, 0, 0));
        assert!(b.is_empty());
    }
    let (r, b) = h.rpc(9, [0; 4], &[]);
    assert_eq!((word(&r, 1), word(&r, 4), word(&r, 5)), (0, 0, 2));
    assert_eq!(&b[..2], b"/\0");
    assert!(b[2..].iter().all(|v| *v == 0));
    let (mut key, mut epoch) = (0, 0);
    for _ in 0..2 {
        let (r, b) = h.rpc(10, [0, DIRECTORY.len() as u64, 0, 0], DIRECTORY);
        assert_eq!((word(&r, 1), word(&r, 4), word(&r, 5)), (0, 0, 32));
        assert_eq!(u64::from_le_bytes(b[..8].try_into().unwrap()), 2);
        let k = u64::from_le_bytes(b[16..24].try_into().unwrap());
        let e = u64::from_le_bytes(b[24..32].try_into().unwrap());
        assert!(k != 0 && e == 91);
        if key != 0 {
            assert_eq!((k, e), (key, epoch));
        }
        (key, epoch) = (k, e);
        assert!(b[32..].iter().all(|v| *v == 0));
    }
    h.files().disconnect_checked(|_| Ok(())).unwrap();
    assert_eq!(h.seen.lock().unwrap().closes, 1);
    let report = h.worker.take().unwrap().join().unwrap();
    assert_eq!(report.stop, filesystem_service::Stop::Disconnected);
    assert_eq!(report.requests, h.requests());
    assert!(report.requests <= 96);
}
#[test]
fn zsh_actual_independent_opens_dup_shared_offsets_eof_and_seek() {
    let mut h = Harness::new();
    let (a, _) = h.rpc(1, [0, ENTRY.len() as u64, 0, 0], ENTRY);
    let first = word(&a, 4);
    let (a, _) = h.rpc(1, [0, ALIAS.len() as u64, 0, 0], ALIAS);
    let independent = word(&a, 4);
    assert_ne!(first, independent);
    let (a, _) = h.rpc(4, [first, 3, 1, 0], &[]);
    let alias = word(&a, 4);
    for (fd, want) in [
        (first, &DATA[..3]),
        (alias, &DATA[3..6]),
        (independent, &DATA[..3]),
    ] {
        let (r, b) = h.rpc(2, [fd, 3, 0, 0], &[]);
        assert_eq!(word(&r, 5), 3);
        assert_eq!(&b[..3], want);
    }
    let (r, _) = h.rpc(3, [first, 0, 2, 0], &[]);
    assert_eq!(word(&r, 4), DATA.len() as u64);
    let (r, b) = h.rpc(2, [alias, 1, 0, 0], &[]);
    assert_eq!(word(&r, 5), 0);
    assert!(b.is_empty());
    for fd in [first, alias, independent] {
        let (r, _) = h.rpc(5, [fd, 0, 0, 0], &[]);
        assert_eq!(word(&r, 1), 0);
    }
    h.files().disconnect_checked(|_| Ok(())).unwrap();
    let report = h.worker.take().unwrap().join().unwrap();
    assert_eq!(report.stop, filesystem_service::Stop::Disconnected);
    assert_eq!(report.requests, h.requests());
}
#[test]
fn zsh_denied_names_do_not_traverse_and_valid_error_does_not_retire() {
    let mut h = Harness::new();
    for op in [1, 8, 10] {
        for name in [
            b"/".as_slice(),
            b"/home/.terminfo/../v/vt100",
            b"/home/.terminfo/x",
        ] {
            let before = h.requests();
            let (r, b) = h.rpc(op, [0, name.len() as u64, 0, 0], name);
            assert_eq!(word(&r, 1) as i64, -2);
            assert!(b.is_empty());
            assert_eq!(h.requests(), before);
            assert!(h.files().cleanup().is_none());
        }
    }
}
#[test]
fn zsh_malformed_unknown_stale_and_padding_retire_before_effects() {
    for defect in 0..9 {
        let mut h = Harness::new();
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(MAGIC);
        put(&mut raw, 1, 9);
        put(&mut raw, 2, 31);
        put(&mut raw, 3, 1);
        let mut b = binding();
        match defect {
            0 => raw[7] ^= 1,
            1 => put(&mut raw, 1, 7),
            2 => put(&mut raw, 1, 11),
            3 => put(&mut raw, 2, 32),
            4 => put(&mut raw, 3, 2),
            5 => put(&mut raw, 4, 1),
            6 => b.epoch = 2,
            7 => b.handle ^= 1,
            _ => {
                put(&mut raw, 1, 8);
                put(&mut raw, 4, 2);
                put(&mut raw, 5, ENTRY.len() as u64);
            }
        }
        let before = h.requests();
        assert!(h.files().body_length(b, &raw).is_err());
        assert_eq!(h.requests(), before);
        assert_eq!(h.seen.lock().unwrap().closes, 1);
    }
}
#[test]
fn zsh_partial_reply_retires_effect_without_replay() {
    let mut h = Harness::new();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    for (i, v) in [(1, 1), (2, 31), (3, 1), (4, 0), (5, ENTRY.len() as u64)] {
        put(&mut raw, i, v);
    }
    let mut w = [0; 4096];
    w[..ENTRY.len()].copy_from_slice(ENTRY);
    let needed = h.files().body_length(binding(), &raw).unwrap();
    let reply = h.files().prepare(binding(), &raw, needed, &mut w).unwrap();
    assert_eq!(word(reply.header(), 1), 0);
    drop(reply);
    let before = h.requests();
    assert!(h.files().body_length(binding(), &raw).is_err());
    assert_eq!(h.requests(), before);
    assert_eq!(h.seen.lock().unwrap().closes, 1);
}
#[test]
fn zsh_bad_body_padding_retires_before_lookup() {
    let mut h = Harness::new();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    for (i, v) in [(1, 1), (2, 31), (3, 1), (5, ENTRY.len() as u64)] {
        put(&mut raw, i, v);
    }
    let mut w = [1; 4096];
    w[..ENTRY.len()].copy_from_slice(ENTRY);
    let before = h.requests();
    assert!(h.files().prepare(binding(), &raw, 64, &mut w).is_err());
    assert_eq!(h.requests(), before);
}

#[cfg(native_zsh_process)]
#[test]
fn selected_child_binding_has_its_actual_native_and_session_identity() {
    let child = Binding {
        slot: 2,
        epoch: 1,
        handle: 0xb0000103,
        generation: 47,
    };
    assert!(child.valid(), "SELECTED_CHILD_BINDING");
    assert!(
        !Binding {
            handle: binding().handle,
            ..child
        }
        .valid()
    );
    assert!(
        !Binding {
            generation: 0,
            ..child
        }
        .valid()
    );
}

#[cfg(native_zsh_process)]
fn child_binding() -> Binding {
    Binding {
        slot: 2,
        epoch: 1,
        handle: 0xb0000103,
        generation: 47,
    }
}
#[cfg(native_zsh_process)]
fn rpc_as(h: &mut Harness, binding: Binding, op: u64, args: [u64; 4]) -> ([u8; 64], Vec<u8>) {
    let files = h.files();
    let view = files.view(binding).unwrap();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, op);
    put(&mut raw, 2, binding.generation);
    put(&mut raw, 3, files.sequence(view));
    for (i, value) in args.iter().enumerate() {
        put(&mut raw, 4 + i, *value);
    }
    let mut workspace = [0; 4096];
    let mut reply = files.prepare(binding, &raw, 0, &mut workspace).unwrap();
    let header = *reply.header();
    let body = reply.body_mut().to_vec();
    reply.delivered();
    (header, body)
}
#[cfg(native_zsh_process)]
#[test]
fn selected_two_views_share_real_offsets_closes_and_commit_only_cloexec() {
    let mut h = Harness::new();
    let (r, _) = h.rpc(1, [0, ENTRY.len() as u64, 0, 0], ENTRY);
    let first = word(&r, 4);
    let (r, _) = h.rpc(1, [1, ALIAS.len() as u64, 0, 0], ALIAS);
    let second = word(&r, 4);
    let before = h.requests();
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    assert_eq!(h.requests(), before);
    assert_eq!(
        h.files().file_view(child).unwrap(),
        ((1 << first) | (1 << second), 1 << second)
    );
    assert!(h.files().disconnect_checked(|_| Ok(())).is_err()); // A live child view cannot be silently dropped.
    let (_, body) = h.rpc(2, [first, 2, 0, 0], &[]);
    assert_eq!(&body[..2], &DATA[..2]);
    let (r, body) = rpc_as(&mut h, child, 2, [first, 2, 0, 0]);
    assert_eq!((word(&r, 2), word(&r, 3)), (47, 1));
    assert_eq!(&body[..2], &DATA[2..4]);
    let before = h.requests();
    h.rpc(5, [first, 0, 0, 0], &[]);
    assert_eq!(h.requests(), before);
    let (_, body) = rpc_as(&mut h, child, 2, [first, 2, 0, 0]);
    assert_eq!(&body[..2], &DATA[4..6]);
    // Merely validating a refused replacement leaves both CLOEXEC views intact.
    assert!(h.files().exec_child(child, 49).is_err());
    assert_eq!(h.files().file_view(child).unwrap().1, 1 << second);
    let next = h.files().exec_child(child, 48).unwrap();
    assert!(h.files().file_view(child).is_err());
    assert_eq!(h.files().file_view(next).unwrap(), (1 << first, 0));
    assert_eq!(
        h.files().file_view(binding()).unwrap(),
        (1 << second, 1 << second)
    );
    let (r, body) = rpc_as(&mut h, next, 2, [first, 2, 0, 0]);
    assert_eq!((word(&r, 2), word(&r, 3)), (48, 1));
    assert_eq!(&body[..2], &DATA[6..8]);
    h.files().settle_child(next).unwrap();
    assert!(h.files().file_view(next).is_err());
    h.rpc(5, [second, 0, 0, 0], &[]);
    h.files().disconnect_checked(|_| Ok(())).unwrap();
    let report = h.worker.take().unwrap().join().unwrap();
    assert_eq!(report.stop, filesystem_service::Stop::Disconnected);
    assert_eq!(report.requests, h.requests());
    assert!(report.requests <= 96);
}
#[cfg(native_zsh_process)]
#[test]
fn selected_stale_or_mixed_view_admission_has_no_parent_or_source_effect() {
    let mut h = Harness::new();
    let parent = binding();
    let child = child_binding();
    for wrong in [
        Binding { slot: 1, ..child },
        Binding {
            epoch: 2,
            handle: 0xb0000203,
            ..child
        },
        Binding {
            generation: parent.generation,
            ..child
        },
    ] {
        assert!(h.files().inherit_child(parent, wrong).is_err());
        assert_eq!(h.files().file_view(parent).unwrap(), (0, 0));
    }
    h.files().inherit_child(parent, child).unwrap();
    assert!(h.files().inherit_child(parent, child).is_err());
    assert!(
        h.files()
            .settle_child(Binding {
                generation: 48,
                ..child
            })
            .is_err()
    );
    h.files().settle_child(child).unwrap();
    assert!(h.files().inherit_child(parent, child).is_err());
    let next = Binding {
        epoch: 2,
        handle: 0xb0000203,
        generation: 49,
        ..child
    };
    h.files().inherit_child(parent, next).unwrap();
    h.files().settle_child(next).unwrap();
    assert_eq!(h.requests(), 12);
    h.files().disconnect_checked(|_| Ok(())).unwrap();
}
#[cfg(native_zsh_process)]
#[test]
fn selected_unknown_child_reply_retires_the_single_namespace_once() {
    let mut h = Harness::new();
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, 9);
    put(&mut raw, 2, child.generation);
    put(&mut raw, 3, 1);
    let mut workspace = [0; 4096];
    {
        let _unknown = h.files().prepare(child, &raw, 0, &mut workspace).unwrap();
    }
    assert_eq!(workspace, [0; 4096]);
    assert_eq!(h.files().cleanup(), Some([0; 2]));
    assert!(h.files().file_view(binding()).is_err());
    assert!(h.files().file_view(child).is_err());
    assert_eq!(h.files().abort(), [0; 2]);
    assert_eq!(h.seen.lock().unwrap().closes, 1);
}

#[cfg(native_zsh_home_write)]
fn home_rpc(
    h: &mut Harness,
    binding: Binding,
    op: u64,
    args: [u64; 4],
    body: &[u8],
    deliver: bool,
) -> ([u8; 64], Vec<u8>) {
    let files = h.files();
    let view = files.view(binding).unwrap();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, op);
    put(&mut raw, 2, binding.generation);
    put(&mut raw, 3, files.sequence(view));
    for (i, v) in args.into_iter().enumerate() {
        put(&mut raw, 4 + i, v);
    }
    let mut workspace = [0; 4096];
    workspace[..body.len()].copy_from_slice(body);
    let n = files.body_length(binding, &raw).unwrap();
    let mut reply = files.prepare(binding, &raw, n, &mut workspace).unwrap();
    let header = *reply.header();
    let body = reply.body_mut().to_vec();
    if deliver {
        reply.delivered();
    }
    (header, body)
}
#[cfg(native_zsh_home_write)]
fn admitted_home(h: &mut Harness) -> Binding {
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    assert!(h.files().admit_home_write(child).is_err()); // No native exec commit yet.
    let child = h.files().exec_child(child, child.generation + 1).unwrap();
    h.files().admit_home_write(child).unwrap();
    child
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_actual_completion_close_delivery_and_healthy_teardown() {
    let mut h = Harness::new();
    let child = admitted_home(&mut h);
    let (r, _) = home_rpc(&mut h, child, 12, [0, 11, 0, 0], b"/home/probe", true);
    assert_eq!(word(&r, 1), 0);
    let fd = word(&r, 4);
    let (r, body) = home_rpc(
        &mut h,
        child,
        11,
        [fd, 16, 0, 0],
        b"AETHER-ZSH-HOME\n",
        true,
    );
    assert_eq!((word(&r, 1), word(&r, 4), word(&r, 5)), (0, 16, 64));
    assert_eq!(
        (
            word(body[..64].try_into().unwrap(), 0),
            word(body[..64].try_into().unwrap(), 1)
        ),
        (14, 0)
    );
    assert!(!h.files().home_write_complete());
    assert_eq!(h.state.lock().unwrap().probe, b"AETHER-ZSH-HOME\n");
    assert_eq!(h.state.lock().unwrap().mutations, 5);
    let (r, _) = home_rpc(&mut h, child, 5, [fd, 0, 0, 0], &[], true);
    assert_eq!(word(&r, 1), 0);
    assert!(h.files().home_write_complete());
    h.files().settle_child(child).unwrap();
    assert!(h.files().home_write_complete());
    h.files().disconnect_checked(|_| Ok(())).unwrap();
    assert!(h.files().home_write_complete());
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_parent_preexec_stale_paths_and_modes_have_no_effect() {
    let mut h = Harness::new();
    let before = h.requests();
    assert!(h.files().admit_home_write(binding()).is_err());
    let (r, _) = home_rpc(&mut h, binding(), 12, [0, 11, 0, 0], b"/home/probe", true);
    assert_eq!(word(&r, 1) as i64, -9);
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    let (r, _) = home_rpc(&mut h, child, 12, [0, 11, 0, 0], b"/home/probe", true);
    assert_eq!(word(&r, 1) as i64, -9);
    assert!(h.files().admit_home_write(child).is_err());
    let next = h.files().exec_child(child, 48).unwrap();
    assert!(h.files().admit_home_write(child).is_err());
    h.files().admit_home_write(next).unwrap();
    let (r, _) = home_rpc(&mut h, next, 12, [0, ENTRY.len() as u64, 0, 0], ENTRY, true);
    assert_eq!(word(&r, 1) as i64, -2);
    assert_eq!(h.requests(), before);
    assert_eq!(h.state.lock().unwrap().mutations, 4);
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_only_fixed_bytes_and_descriptor_can_mutate_once() {
    let mut h = Harness::new();
    let child = admitted_home(&mut h);
    let (r, _) = home_rpc(&mut h, child, 12, [0, 11, 0, 0], b"/home/probe", true);
    let fd = word(&r, 4);
    let before = h.requests();
    let (r, _) = home_rpc(&mut h, child, 11, [fd, 15, 0, 0], b"AETHER-ZSH-HOME", true);
    assert_eq!(word(&r, 1) as i64, -22);
    let (r, _) = home_rpc(&mut h, child, 11, [fd, 16, 0, 0], b"AETHER-ZSH-HOME!", true);
    assert_eq!(word(&r, 1) as i64, -22);
    let (r, _) = home_rpc(
        &mut h,
        child,
        11,
        [fd + 1, 16, 0, 0],
        b"AETHER-ZSH-HOME\n",
        true,
    );
    assert_eq!(word(&r, 1) as i64, -9);
    let (r, _) = home_rpc(&mut h, child, 2, [fd, 16, 0, 0], &[], true);
    assert_eq!(word(&r, 1) as i64, -9);
    let (r, _) = home_rpc(&mut h, child, 4, [fd, 3, 0, 0], &[], true);
    assert_eq!(word(&r, 1) as i64, -22);
    assert_eq!(h.requests(), before);
    assert_eq!(h.state.lock().unwrap().mutations, 4);
    home_rpc(
        &mut h,
        child,
        11,
        [fd, 16, 0, 0],
        b"AETHER-ZSH-HOME\n",
        true,
    );
    let after = h.requests();
    let (r, _) = home_rpc(
        &mut h,
        child,
        11,
        [fd, 16, 0, 0],
        b"AETHER-ZSH-HOME\n",
        true,
    );
    assert_eq!(word(&r, 1) as i64, -9);
    assert_eq!(h.requests(), after);
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_reply_loss_preserves_effect_without_replay_or_completion() {
    let mut h = Harness::new();
    let child = admitted_home(&mut h);
    let (r, _) = home_rpc(&mut h, child, 12, [0, 11, 0, 0], b"/home/probe", true);
    let fd = word(&r, 4);
    let (r, _) = home_rpc(
        &mut h,
        child,
        11,
        [fd, 16, 0, 0],
        b"AETHER-ZSH-HOME\n",
        false,
    );
    assert_eq!(word(&r, 4), 16);
    assert!(!h.files().home_write_complete());
    assert_eq!(h.files().home_write.receipt[0], 14);
    assert_eq!(h.files().home_write.sequence, 2);
    assert_eq!(h.files().cleanup(), Some([0; 2]));
    assert_eq!(h.state.lock().unwrap().probe, b"AETHER-ZSH-HOME\n");
    assert_eq!(h.state.lock().unwrap().mutations, 5);
    assert_eq!(h.files().abort(), [0; 2]);
    assert_eq!(h.seen.lock().unwrap().closes, 1);
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_unknown_and_committed_failures_keep_typed_receipts_and_retire() {
    for failure in [1, 2] {
        let mut h = Harness::new();
        let child = admitted_home(&mut h);
        let (r, _) = home_rpc(&mut h, child, 12, [0, 11, 0, 0], b"/home/probe", true);
        let fd = word(&r, 4);
        h.state.lock().unwrap().probe_failure = failure;
        let (r, body) = home_rpc(
            &mut h,
            child,
            11,
            [fd, 16, 0, 0],
            b"AETHER-ZSH-HOME\n",
            true,
        );
        assert_eq!(word(&r, 1) as i64, -5);
        assert_eq!(word(&r, 4), 0);
        assert_eq!(word(&r, 5), 64);
        assert_eq!(
            word(body[..64].try_into().unwrap(), 0) & 7,
            if failure == 1 { 4 } else { 2 }
        );
        assert!(!h.files().home_write_complete());
        assert!(h.files().cleanup().is_some());
        assert!(h.files().mutation_failure().is_some());
    }
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_close_reply_loss_never_qualifies_cleanup() {
    let mut h = Harness::new();
    let child = admitted_home(&mut h);
    let (r, _) = home_rpc(&mut h, child, 12, [0, 11, 0, 0], b"/home/probe", true);
    let fd = word(&r, 4);
    home_rpc(
        &mut h,
        child,
        11,
        [fd, 16, 0, 0],
        b"AETHER-ZSH-HOME\n",
        true,
    );
    home_rpc(&mut h, child, 5, [fd, 0, 0, 0], &[], false);
    assert!(!h.files().home_write_complete());
    assert_eq!(h.files().home_write.phase, 4);
}
#[cfg(native_zsh_home_write)]
#[test]
fn home_write_second_exec_denies_before_generation_or_cloexec_effects() {
    let mut h = Harness::new();
    let child = admitted_home(&mut h);
    home_rpc(&mut h, child, 12, [1, 11, 0, 0], b"/home/probe", true);
    let before = h.files().file_view(child).unwrap();
    let requests = h.requests();
    assert!(h.files().exec_child(child, child.generation + 1).is_err());
    assert_eq!(
        h.files().file_view(child),
        Ok(before),
        "SECOND_EXEC_CHANGED_VIEW"
    );
    assert_eq!(h.requests(), requests, "SECOND_EXEC_CLOSED_FILE");
}

#[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
#[test]
fn file_exec_sealed_handle_delivers_exact_bytes_and_closes_once() {
    for size in [1, 4096] {
        let mut h = Harness::new();
        let image = std::vec![0xa5; size];
        h.files().provision_file_exec(&image).unwrap();
        let child = child_binding();
        h.files().inherit_child(binding(), child).unwrap();
        let before = h.requests();
        let mut work = [0x55; 4096];
        assert_eq!(
            h.files().acquire_file_exec(child, &mut work),
            Ok(size),
            "SEALED_FILE_EXEC_BYTES"
        );
        assert_eq!(&work[..size], &image);
        assert!(work[size..].iter().all(|byte| *byte == 0));
        assert_eq!(
            h.requests() - before,
            5,
            "EOF_FULL_STAT_CLOSE_EXACT_REQUESTS"
        );
        assert!(h.files().file_exec_consumed());
        let before = h.requests();
        assert_eq!(
            h.files().acquire_file_exec(child, &mut work),
            Err(Error::Invalid)
        );
        assert_eq!(h.files().provision_file_exec(&image), Err(Error::Invalid));
        assert_eq!(h.requests(), before, "NO_FILE_EXEC_REPLAY");
        assert_eq!(h.state.lock().unwrap().mutations, 5);
        h.files().settle_child(child).unwrap();
        h.files().disconnect_checked(|_| Ok(())).unwrap();
    }
}
#[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
#[test]
fn file_exec_rejects_unsealed_wrong_actor_and_bad_size_before_source_effect() {
    let mut h = Harness::new();
    let before = h.requests();
    assert_eq!(
        h.files().acquire_file_exec(binding(), &mut [0; 4096]),
        Err(Error::Invalid)
    );
    assert_eq!(h.files().provision_file_exec(&[]), Err(Error::Invalid));
    assert_eq!(
        h.files().provision_file_exec(&[0; 4097]),
        Err(Error::Invalid)
    );
    assert_eq!(h.requests(), before);
    h.files().provision_file_exec(b"actual held bytes").unwrap();
    let before = h.requests();
    let mut wrong = binding();
    wrong.generation += 1;
    assert_eq!(
        h.files().acquire_file_exec(wrong, &mut [0; 4096]),
        Err(Error::Invalid)
    );
    assert_eq!(h.requests(), before, "AUTHORITY_BEFORE_ACQUISITION");
    assert_eq!(h.state.lock().unwrap().mutations, 5);
}
#[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
#[test]
fn file_exec_seal_exposes_no_write_or_namespace_alias_to_parent() {
    for op in [7, 11, 12] {
        let mut h = Harness::new();
        h.files().provision_file_exec(b"sealed bytes").unwrap();
        let before = h.requests();
        let (header, _) = h.rpc(1, [0, 11, 0, 0], b"/home/probe");
        assert_ne!(word(&header, 1), 0, "NO_PROBE_FILE_PROXY");
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(MAGIC);
        put(&mut raw, 1, op);
        put(&mut raw, 2, 31);
        put(&mut raw, 3, 2);
        assert!(
            h.files().body_length(binding(), &raw).is_err(),
            "NO_MUTATION_ALIAS"
        );
        assert_eq!(h.requests(), before, "NO_UNTRUSTED_SOURCE_EFFECT");
        assert_eq!(h.state.lock().unwrap().probe, b"sealed bytes");
    }
}

#[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
#[test]
fn file_exec_short_bad_eof_and_source_failure_poison_without_replay() {
    for failure in [1, 2, 3] {
        let mut h = Harness::new();
        h.files().provision_file_exec(b"sealed source").unwrap();
        let child = child_binding();
        h.files().inherit_child(binding(), child).unwrap();
        h.state.lock().unwrap().probe_read_failure = failure;
        let mut workspace = [0xa5; 4096];
        assert!(
            h.files().acquire_file_exec(child, &mut workspace).is_err(),
            "EXACT_READ_EOF_BEFORE_EXEC"
        );
        assert_eq!(workspace, [0; 4096]);
        assert!(!h.files().file_exec_consumed());
        let requests = h.requests();
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        assert_eq!(
            h.files().acquire_file_exec(child, &mut workspace),
            Err(Error::Invalid)
        );
        assert_eq!(h.requests(), requests, "NO_FAILED_ACQUISITION_REPLAY");
    }
}
#[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
#[test]
fn file_exec_failed_provision_never_seals_or_replays_mutation() {
    for failure in [1, 2] {
        let mut h = Harness::new();
        h.state.lock().unwrap().probe_failure = failure;
        assert!(h.files().provision_file_exec(b"source").is_err());
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        assert!(!h.files().file_exec_consumed());
        let requests = h.requests();
        assert_eq!(
            h.files().provision_file_exec(b"source"),
            Err(Error::Invalid)
        );
        assert_eq!(h.requests(), requests);
        assert_eq!(h.state.lock().unwrap().mutations, 5, "NO_PROVISION_REPLAY");
    }
}

#[cfg(native_zsh_cold_reopen)]
#[test]
fn cold_reopen_existing_bytes_seals_current_object_without_mutation() {
    let mut h = Harness::new();
    let image = b"persisted complete helper";
    h.state.lock().unwrap().probe = image.to_vec();
    let mut work = [0xa5; 4096];
    h.files().reopen_file_exec(image, &mut work).unwrap();
    assert_eq!(work, [0; 4096]);
    assert_eq!(h.state.lock().unwrap().mutations, 0, "COLD_NO_MUTATION");
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    let requests = h.requests();
    let mut wrong = child;
    wrong.generation += 1;
    assert!(h.files().acquire_file_exec(wrong, &mut work).is_err());
    assert_eq!(h.requests(), requests, "COLD_ACTOR_BEFORE_ACQUIRE");
    assert_eq!(
        h.files().acquire_file_exec(child, &mut work),
        Ok(image.len())
    );
    assert_eq!(&work[..image.len()], image);
    assert!(h.files().file_exec_consumed());
    assert!(h.files().acquire_file_exec(child, &mut work).is_err());
    h.files().settle_child(child).unwrap();
    h.files().disconnect_checked(|_| Ok(())).unwrap();
    assert_eq!(h.state.lock().unwrap().mutations, 0);
}
#[cfg(native_zsh_cold_reopen)]
#[test]
fn cold_reopen_terminfo_rejects_missing_kind_size_bytes_and_read_failures() {
    for case in 0..8 {
        let mut h = Harness::connected(true);
        {
            let mut s = h.state.lock().unwrap();
            match case {
                0 => s.made[0] = false,
                1 => s.wrong_kind = 5,
                2 => {
                    s.data.pop();
                }
                3 => s.data[0] ^= 1,
                4 => s.data.push(0),
                _ => s.data_read_failure = case - 4,
            }
        }
        let mut work = [0xa5; 4096];
        assert!(
            h.files().reopen(DATA, &mut work).is_err(),
            "COLD_TERMINFO_REJECT_{case}"
        );
        assert_eq!(work, [0; 4096]);
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        let requests = h.requests();
        assert!(h.files().reopen(DATA, &mut work).is_err());
        assert_eq!(h.requests(), requests, "COLD_NO_REOPEN_REPLAY");
        assert_eq!(h.state.lock().unwrap().mutations, 0);
    }
}
#[cfg(native_zsh_cold_reopen)]
#[test]
fn cold_reopen_helper_rejects_wrong_bytes_kind_size_and_read_failures() {
    let expected = b"persisted helper";
    for case in 0..8 {
        let mut h = Harness::new();
        {
            let mut s = h.state.lock().unwrap();
            s.probe = expected.to_vec();
            match case {
                0 => s.probe.clear(),
                1 => s.wrong_kind = 6,
                2 => {
                    s.probe.pop();
                }
                3 => s.probe[0] ^= 1,
                4 => s.probe.push(0),
                _ => s.probe_read_failure = case - 4,
            }
        }
        let mut work = [0xa5; 4096];
        assert!(
            h.files().reopen_file_exec(expected, &mut work).is_err(),
            "COLD_EXEC_REJECT_{case}"
        );
        assert_eq!(work, [0; 4096]);
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        let requests = h.requests();
        assert!(h.files().reopen_file_exec(expected, &mut work).is_err());
        assert_eq!(h.requests(), requests);
        assert!(!h.files().file_exec_consumed());
        assert_eq!(h.state.lock().unwrap().mutations, 0);
    }
}
#[cfg(native_zsh_cold_reopen)]
#[test]
fn cold_reopen_checks_temporary_closes_and_contains_unknown_close() {
    for close in 1..=2 {
        let mut h = Harness::connected(true);
        h.seen.lock().unwrap().fail_close = close;
        assert!(h.files().reopen(DATA, &mut [0; 4096]).is_err());
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        assert_eq!(h.state.lock().unwrap().mutations, 0);
    }
}

#[cfg(native_zsh_cold_reopen)]
#[test]
fn cold_reopen_post_stat_and_retained_helper_close_are_required() {
    let image = b"actual persisted executable";
    let mut h = Harness::connected(true);
    h.seen.lock().unwrap().bad_stat = true;
    assert!(h.files().reopen(DATA, &mut [0; 4096]).is_err());
    assert_eq!(h.files().cleanup(), Some([0; 2]));
    let mut h = Harness::new();
    h.state.lock().unwrap().probe = image.to_vec();
    h.seen.lock().unwrap().bad_stat = true;
    assert!(h.files().reopen_file_exec(image, &mut [0; 4096]).is_err());
    assert_eq!(h.files().cleanup(), Some([0; 2]));
    let mut h = Harness::new();
    h.state.lock().unwrap().probe = image.to_vec();
    h.files().reopen_file_exec(image, &mut [0; 4096]).unwrap();
    {
        let mut seen = h.seen.lock().unwrap();
        seen.fail_close = seen.close_replies + 1;
    }
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    let mut work = [0xa5; 4096];
    assert!(
        h.files().acquire_file_exec(child, &mut work).is_err(),
        "COLD_CLOSE_BEFORE_EXEC"
    );
    assert_eq!(work, [0; 4096]);
    assert!(!h.files().file_exec_consumed());
    assert_eq!(h.files().cleanup(), Some([0; 2]));
    assert_eq!(h.state.lock().unwrap().mutations, 0);
}

#[cfg(all(native_zsh_idle_exit, native_zsh_cold_reopen))]
#[test]
fn unused_helper_close_requires_the_validated_held_reference_and_known_success() {
    let image = b"actual persisted executable";
    for failure in 0..3 {
        let mut h = Harness::new();
        assert!(!h.files().file_exec_unused_closed());
        if failure != 1 {
            h.state.lock().unwrap().probe = image.to_vec();
            h.files().reopen_file_exec(image, &mut [0; 4096]).unwrap();
            assert!(!h.files().file_exec_unused_closed());
        }
        if failure == 2 {
            let mut seen = h.seen.lock().unwrap();
            seen.fail_close = seen.close_replies + 1;
        }
        let result = h.files().disconnect_checked(|_| Ok(()));
        assert_eq!(h.files().file_exec_unused_closed(), failure == 0);
        assert!(!h.files().file_exec_consumed());
        if failure == 2 {
            assert!(result.is_err());
            let requests = h.requests();
            assert!(h.files().disconnect_checked(|_| Ok(())).is_err());
            assert_eq!(h.requests(), requests);
        } else {
            assert_eq!(result, Ok([0; 2]));
        }
        assert_eq!(h.state.lock().unwrap().mutations, 0);
    }
}

#[cfg(native_zsh_home_redirection)]
#[path = "zsh-home-redirection-tests.rs"]
mod home_redirection_tests;
