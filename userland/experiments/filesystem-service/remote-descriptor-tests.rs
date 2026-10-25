// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_policy::{Backend, Clock, Completion, Lost, Namespace, Node, Owner, Rights, Utc};
use filesystem_service::{put, word, Message, MAGIC};
use std::{
    sync::{mpsc, Arc, Mutex},
    thread,
    time::Duration,
    vec::Vec,
};
#[derive(Default)]
struct Seen {
    sent: Vec<Message>,
    closes: usize,
    reads: usize,
    lookups: usize,
    drops: usize,
    deny_read: bool,
}
type Shared = Arc<Mutex<Seen>>;
#[derive(Clone, Copy, PartialEq)]
enum Fault {
    None,
    ReadBody,
    Count,
    Close,
}
struct Pipe {
    tx: Option<mpsc::SyncSender<Message>>,
    rx: Option<mpsc::Receiver<Message>>,
    seen: Shared,
    fault: Fault,
    last: u64,
    body: bool,
    cleanup: [i64; 2],
}
impl Channel for Pipe {
    fn send(&mut self, frame: &Message) -> core::result::Result<(), i64> {
        self.seen.lock().unwrap().sent.push(*frame);
        if frame[..8] == MAGIC[..] {
            self.last = word(frame, 1);
        }
        self.tx.as_ref().unwrap().send(*frame).map_err(|_| -32)
    }
    fn receive(&mut self, out: &mut Message) -> core::result::Result<(), i64> {
        if (self.fault == Fault::ReadBody && self.body)
            || (self.fault == Fault::Close && self.last == 3)
        {
            return Err(-32);
        }
        *out = self
            .rx
            .as_ref()
            .unwrap()
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        if self.last == 2 && out[..8] == MAGIC[..] && word(out, 1) == 0 {
            self.body = word(out, 5) > 0;
            if self.fault == Fault::Count {
                put(out, 5, 4097);
            }
        }
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        self.tx.take();
        self.rx.take();
        self.cleanup
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
        match name {
            b"file" | b"alias" => Ok(Node::new(2, 1, 6, filesystem_policy::Kind::File)),
            b"dir" => Ok(Node::new(3, 1, 0, filesystem_policy::Kind::Directory)),
            _ => Err(filesystem_policy::Error::Backend(2)),
        }
    }
    fn read(
        &mut self,
        _: Node,
        offset: u64,
        out: &mut [u8],
    ) -> core::result::Result<usize, filesystem_policy::Error> {
        let mut seen = self.0.lock().unwrap();
        seen.reads += 1;
        if seen.deny_read {
            out.fill(0x55);
            return Err(filesystem_policy::Error::Backend(13));
        }
        let count = 6u64.saturating_sub(offset).min(out.len() as u64) as usize;
        for (i, b) in out[..count].iter_mut().enumerate() {
            *b = b'a' + offset as u8 + i as u8;
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
        panic!("write forbidden")
    }
    fn mutate(
        &mut self,
        _: Node,
        _: Namespace<'_>,
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("mutate forbidden")
    }
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> core::result::Result<Utc, filesystem_policy::Error> {
        panic!("clock forbidden")
    }
}
struct Harness {
    fds: Option<Descriptors<Pipe>>,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
    storage: Shared,
    local: Shared,
}
impl Harness {
    fn new(fault: Fault, cleanup: [i64; 2]) -> Self {
        let (server_tx, server_rx) = mpsc::sync_channel(128);
        let (client_tx, client_rx) = mpsc::sync_channel(128);
        let storage = Shared::default();
        let observed = storage.clone();
        let local = Shared::default();
        let worker = thread::spawn(move || {
            let owner = Owner::new(Storage(observed), Time, 72).unwrap();
            filesystem_service::run(
                owner,
                Pipe {
                    tx: Some(client_tx),
                    rx: Some(server_rx),
                    seen: Shared::default(),
                    fault: Fault::None,
                    last: 0,
                    body: false,
                    cleanup: [0; 2],
                },
                17,
                Rights::new(3).unwrap(),
                91,
            )
        });
        let fds = Descriptors::connect(
            Pipe {
                tx: Some(server_tx),
                rx: Some(client_rx),
                seen: local.clone(),
                fault,
                last: 0,
                body: false,
                cleanup,
            },
            91,
        )
        .ok()
        .unwrap();
        Self {
            fds: Some(fds),
            worker: Some(worker),
            storage,
            local,
        }
    }
    fn opcodes(&self) -> Vec<u64> {
        self.local
            .lock()
            .unwrap()
            .sent
            .iter()
            .filter(|f| f[..8] == MAGIC[..])
            .map(|f| word(f, 1))
            .collect()
    }
}
impl Drop for Harness {
    fn drop(&mut self) {
        self.fds.take();
        if let Some(w) = self.worker.take() {
            w.join().unwrap();
        }
    }
}
#[test]
fn real_af07_shared_offsets_independent_opens_seek_and_final_close() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let a = f.open_read(b"file", false).unwrap();
    let dup = f.duplicate(a, 0, false).unwrap();
    let other = f.open_read(b"alias", false).unwrap();
    let mut out = [0x77; MAX_READ];
    assert_eq!(f.read(a, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(f.position(dup), Ok(2));
    assert_eq!(f.position(other), Ok(0));
    assert_eq!(f.seek(dup, Seek::End(-1)), Ok(5));
    assert_eq!(f.read(a, 8, &mut out), Ok(1));
    assert_eq!(out[0], b'f');
    assert!(out[1..].iter().all(|&b| b == 0));
    assert_eq!(f.read(dup, 1, &mut out), Ok(0));
    assert_eq!(out, [0; MAX_READ]);
    f.close(a).unwrap();
    assert_eq!(f.position(dup), Ok(6));
    f.close(dup).unwrap();
    f.close(other).unwrap();
    assert!(h
        .local
        .lock()
        .unwrap()
        .sent
        .iter()
        .filter(|f| f[..8] == MAGIC[..] && word(f, 1) == 1)
        .all(|f| word(f, 4) == 2));
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 2);
    assert_eq!(h.fds.take().unwrap().disconnect(), Ok([0; 2]));
    let report = h.worker.take().unwrap().join().unwrap();
    assert_eq!(report.stop, filesystem_service::Stop::Disconnected);
    assert_eq!(h.storage.lock().unwrap().drops, 1);
}
#[test]
#[cfg(not(fs_paths))]
fn full_fd_table_and_invalid_names_do_not_send_lookup() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    for _ in FIRST_FILE_FD..MAX_FDS {
        let result = h.fds.as_mut().unwrap().open_read(b"file", false);
        assert_eq!(result.as_ref().map(|_| ()), Ok(()));
    }
    let before = h.opcodes();
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.open_read(b"alias", false), Err(Failure::Full));
    assert_eq!(f.duplicate(3, 0, false), Err(Failure::Full));
    assert_eq!(h.opcodes(), before);
    h.fds.as_mut().unwrap().close(3).unwrap();
    let before = h.opcodes();
    let f = h.fds.as_mut().unwrap();
    for name in [b"".as_slice(), b".", b"..", b"a/b", b"a\0b", &[b'x'; 256]] {
        assert_eq!(
            f.open_read(name, false),
            Err(Failure::Source(Error::Invalid))
        );
    }
    assert_eq!(h.opcodes(), before);
}

#[test]
#[cfg(fs_paths)]
fn root_paths_share_descriptions_offsets_and_keep_namespace_handles_bounded() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let fd = f.open_read(b"/dir/dir/file", false).unwrap();
    let alias = f.duplicate(fd, 10, true).unwrap();
    let mut out = [0; MAX_READ];
    assert_eq!(f.read(fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(f.read(alias, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
    f.close(fd).unwrap();
    assert_eq!(f.read(alias, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ef");
    f.close(alias).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 3);
    assert_eq!(h.fds.take().unwrap().disconnect(), Ok([0; 2]));
}

#[test]
#[cfg(fs_paths)]
fn root_path_capacity_and_error_cleanup_preserve_existing_descriptions() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    for _ in FIRST_FILE_FD..MAX_FDS {
        assert!(h
            .fds
            .as_mut()
            .unwrap()
            .open_read(b"dir/file", false)
            .is_ok());
    }
    let before = h.opcodes();
    assert_eq!(
        h.fds.as_mut().unwrap().open_read(b"dir/file", false),
        Err(Failure::Full)
    );
    assert_eq!(h.opcodes(), before);
    h.fds.as_mut().unwrap().close(3).unwrap();
    let before = h.opcodes();
    for path in [
        b"".as_slice(),
        b"/../file",
        b"dir//file",
        b"dir/../file",
        b"dir/",
        b"dir/\0",
        &[b'x'; 256],
    ] {
        assert_eq!(
            h.fds.as_mut().unwrap().open_read(path, false),
            Err(Failure::Source(Error::Invalid))
        );
    }
    assert_eq!(h.opcodes(), before);
    for _ in 0..20 {
        assert_eq!(
            h.fds.as_mut().unwrap().open_read(b"dir/missing", false),
            Err(Failure::Source(Error::Remote(-2)))
        );
    }
    assert_eq!(
        h.fds.as_mut().unwrap().open_read(b"/dir/file", false),
        Ok(3)
    );
    let mut out = [0; MAX_READ];
    assert_eq!(h.fds.as_mut().unwrap().read(4, 6, &mut out), Ok(6));
    assert_eq!(&out[..6], b"abcdef");
    assert_eq!(h.fds.take().unwrap().disconnect(), Ok([0; 2]));
}
#[test]
fn rejected_directory_opens_release_every_remote_handle() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    for _ in 0..40 {
        assert_eq!(
            h.fds.as_mut().unwrap().open_read(b"dir", false),
            Err(Failure::Source(Error::Remote(-21)))
        );
    }
    assert_eq!(h.fds.as_mut().unwrap().open_read(b"file", false), Ok(3));
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 40);
}
#[test]
fn cloexec_is_per_fd_and_commits_only_flagged_final_aliases() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let a = f.open_read(b"file", true).unwrap();
    let b = f.duplicate(a, 0, false).unwrap();
    let other = f.open_read(b"alias", true).unwrap();
    f.commit_exec_close().unwrap();
    assert_eq!(f.position(a), Err(Failure::BadFd));
    assert_eq!(f.position(other), Err(Failure::BadFd));
    assert_eq!(f.position(b), Ok(0));
    f.set_close_on_exec(b, true).unwrap();
    f.commit_exec_close().unwrap();
    assert_eq!(f.position(b), Err(Failure::BadFd));
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 2);
}
#[test]
fn known_read_error_keeps_offset_and_allows_later_read() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    h.storage.lock().unwrap().deny_read = true;
    let f = h.fds.as_mut().unwrap();
    let fd = f.open_read(b"file", false).unwrap();
    let dup = f.duplicate(fd, 0, false).unwrap();
    let mut out = [0x77; MAX_READ];
    assert_eq!(
        f.read(fd, 2, &mut out),
        Err(Failure::Source(Error::Remote(-13)))
    );
    assert_eq!(out, [0; MAX_READ]);
    assert_eq!(f.position(dup), Ok(0));
    h.storage.lock().unwrap().deny_read = false;
    assert_eq!(f.read(dup, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(f.position(fd), Ok(2));
}
#[test]
fn lost_read_body_and_bad_count_retire_all_aliases_without_replay() {
    for fault in [Fault::ReadBody, Fault::Count] {
        let mut h = Harness::new(fault, [-9, -5]);
        let f = h.fds.as_mut().unwrap();
        let fd = f.open_read(b"file", false).unwrap();
        let dup = f.duplicate(fd, 0, false).unwrap();
        let mut out = [0x77; MAX_READ];
        assert_eq!(
            f.read(fd, 2, &mut out),
            Err(Failure::Source(if fault == Fault::ReadBody {
                Error::Transport(-32)
            } else {
                Error::Protocol
            }))
        );
        assert_eq!(out, [0; MAX_READ]);
        assert_eq!(f.position(dup), Err(Failure::Retired));
        assert_eq!(f.open_read(b"file", false), Err(Failure::Retired));
        assert_eq!(f.cleanup(), Some([-9, -5]));
        assert_eq!(h.opcodes(), [1, 2]);
        h.fds.take();
        assert_eq!(h.local.lock().unwrap().closes, 1);
    }
}
#[test]
fn unknown_final_close_retires_even_after_server_may_have_closed() {
    let mut h = Harness::new(Fault::Close, [-9, -5]);
    let f = h.fds.as_mut().unwrap();
    let fd = f.open_read(b"file", false).unwrap();
    assert_eq!(f.close(fd), Err(Failure::Source(Error::Transport(-32))));
    assert_eq!(f.position(fd), Err(Failure::Retired));
    assert_eq!(f.cleanup(), Some([-9, -5]));
    assert_eq!(h.opcodes(), [1, 3]);
    h.fds.take();
    assert_eq!(h.local.lock().unwrap().closes, 1);
}
#[test]
fn zero_read_bad_fds_and_overflow_clear_without_wire_effects() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let fd = f.open_read(b"file", false).unwrap();
    let before = h.local.lock().unwrap().sent.len();
    let mut out = [0x77; MAX_READ];
    assert_eq!(f.read(fd, 0, &mut out), Ok(0));
    assert_eq!(out, [0; MAX_READ]);
    out.fill(0x77);
    assert_eq!(f.read(0, 1, &mut out), Err(Failure::BadFd));
    assert_eq!(out, [0; MAX_READ]);
    out.fill(0x77);
    f.seek(fd, Seek::Set(i64::MAX)).unwrap();
    assert_eq!(f.read(fd, 1, &mut out), Err(Failure::Overflow));
    assert_eq!(out, [0; MAX_READ]);
    assert_eq!(f.seek(fd, Seek::Current(1)), Err(Failure::Overflow));
    assert_eq!(f.position(fd), Ok(i64::MAX as u64));
    assert_eq!(h.local.lock().unwrap().sent.len(), before);
}
