// SPDX-License-Identifier: BSD-2-Clause
//! Actual grant/service/client logic over synthetic storage and host channels.
use super::*;
use filesystem_client::{Client, MutationOutcome};
use filesystem_policy::{self as p, Rights};
use filesystem_service::{message, put, Stop};
use std::{
    collections::VecDeque,
    sync::{mpsc, Arc, Mutex},
    thread,
    time::Duration,
    vec,
    vec::Vec,
};

#[derive(Default)]
struct Seen {
    #[cfg(fs_af09_drain)]
    counts: Vec<(u64, u64)>,
    #[cfg(fs_af09_drain)]
    count_error: Option<i64>,
    published: usize,
    sent: Vec<Message>,
    completed: usize,
    receives: usize,
    closes: usize,
    client_closes: usize,
    drops: usize,
    writes: usize,
    clocks: usize,
    data: [u8; 4],
}
type Shared = Arc<Mutex<Seen>>;
struct Storage(Shared);
struct Time(Shared);
fn node(id: u64) -> p::Node {
    p::Node::new(
        id,
        id + 10,
        if id >= 3 { 4 } else { 0 },
        if id >= 3 {
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
        match (at.identity().0, name) {
            (1, b"home") => Ok(node(2)),
            (2, b"data") => Ok(node(3)),
            (1, b"system") => Ok(node(4)),
            _ => Err(p::Error::Backend(2)),
        }
    }
    fn read(&mut self, n: p::Node, at: u64, out: &mut [u8]) -> Result<usize, p::Error> {
        let data = if n.identity().0 == 4 {
            *b"sys!"
        } else {
            self.0.lock().unwrap().data
        };
        let start = (at as usize).min(4);
        let count = out.len().min(4 - start);
        out[..count].copy_from_slice(&data[start..start + count]);
        Ok(count)
    }
    fn write(
        &mut self,
        n: p::Node,
        at: u64,
        bytes: &[u8],
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        assert_eq!(n.identity().0, 3, "HOME_ACTIVATION_SYSTEM_WRITE");
        let mut s = self.0.lock().unwrap();
        s.writes += 1;
        s.data[at as usize..at as usize + bytes.len()].copy_from_slice(bytes);
        Ok(p::Completion {
            error: 0,
            txg: 1,
            bytes_staged: bytes.len() as u64,
            state: 2,
        })
    }
    fn mutate(
        &mut self,
        _: p::Node,
        _: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        Ok(p::Completion {
            error: 13,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        })
    }
}
impl p::Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        self.0.lock().unwrap().clocks += 1;
        Ok(p::Utc {
            seconds: 1,
            nanoseconds: 0,
        })
    }
}
fn owner(s: Shared) -> (Owner<Storage, Time>, p::Attachment, p::Entry) {
    let mut o = Owner::new(Storage(s.clone()), Time(s), 91)
        .unwrap()
        .with_namespace_identity(p::Identity::new(1000, 1000).unwrap());
    let a = o.attach(7, Rights::ALL).unwrap();
    let h = o
        .lookup(
            7,
            a.session,
            a.root.handle,
            b"home",
            Rights::new(15).unwrap(),
        )
        .unwrap();
    (o, a, h)
}
fn greeting(token: u64) -> Message {
    let mut f = message(91, 0);
    put(&mut f, 3, token);
    put(&mut f, 4, 1);
    f
}
struct Script {
    seen: Shared,
    input: VecDeque<Message>,
    fail: Option<usize>,
    error: i64,
}
impl Script {
    fn new(seen: Shared) -> Self {
        Self {
            seen,
            input: vec![message(91, 0)].into(),
            fail: None,
            error: -91,
        }
    }
}
impl Channel for Script {
    #[cfg(fs_af09_drain)]
    fn af09_counts(&mut self, mutations: u64, requests: u64) -> Result<(), i64> {
        let mut seen = self.seen.lock().unwrap();
        seen.counts.push((mutations, requests));
        seen.count_error.map_or(Ok(()), Err)
    }

    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        let (published, completed) = {
            let s = self.seen.lock().unwrap();
            (s.published, s.completed)
        };
        assert_eq!(
            (published, completed),
            (1, 2),
            "HOME_ACTIVATION_REQUEST_ORDER"
        );
        self.seen.lock().unwrap().receives += 1;
        *out = self.input.pop_front().ok_or(-32)?;
        Ok(())
    }
    fn send(&mut self, f: &Message) -> Result<(), i64> {
        let published = self.seen.lock().unwrap().published;
        assert_eq!(published, 1, "HOME_ACTIVATION_BEFORE_SEND");
        let mut s = self.seen.lock().unwrap();
        let index = s.sent.len();
        s.sent.push(*f);
        if self.fail == Some(index) {
            Err(self.error)
        } else {
            s.completed += 1;
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        [-7, -8]
    }
}
struct Pipe {
    tx: Option<mpsc::SyncSender<Message>>,
    rx: mpsc::Receiver<Message>,
    seen: Shared,
    server: bool,
}
impl Channel for Pipe {
    #[cfg(fs_af09_drain)]
    fn af09_counts(&mut self, mutations: u64, requests: u64) -> Result<(), i64> {
        if !self.server {
            return Err(-38);
        }
        let mut seen = self.seen.lock().unwrap();
        seen.counts.push((mutations, requests));
        seen.count_error.map_or(Ok(()), Err)
    }

    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        if self.server {
            let (p, n) = {
                let s = self.seen.lock().unwrap();
                (s.published, s.completed)
            };
            assert!(p == 1 && n >= 2, "HOME_ACTIVATION_REQUEST_ORDER");
            self.seen.lock().unwrap().receives += 1;
        }
        *out = self
            .rx
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        Ok(())
    }
    fn send(&mut self, f: &Message) -> Result<(), i64> {
        if self.server {
            let p = self.seen.lock().unwrap().published;
            assert_eq!(p, 1, "HOME_ACTIVATION_BEFORE_SEND");
            self.seen.lock().unwrap().sent.push(*f);
        }
        self.tx.as_ref().ok_or(-9)?.send(*f).map_err(|_| -32)?;
        if self.server {
            self.seen.lock().unwrap().completed += 1;
        }
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.tx.take();
        let mut s = self.seen.lock().unwrap();
        if self.server {
            s.closes += 1;
            [-7, -8]
        } else {
            s.client_closes += 1;
            [0, 0]
        }
    }
}
#[test]
fn actual_two_grants_activate_once_and_home_write_readback() {
    let seen = Shared::default();
    let state = seen.clone();
    let (a, b) = mpsc::sync_channel(0);
    let (c, d) = mpsc::sync_channel(0);
    let (ready, wait) = mpsc::sync_channel(1);
    let client = Pipe {
        tx: Some(a),
        rx: d,
        seen: seen.clone(),
        server: false,
    };
    let server = Pipe {
        tx: Some(c),
        rx: b,
        seen: seen.clone(),
        server: true,
    };
    let join = thread::spawn(move || {
        let (o, a, h) = owner(state.clone());
        run_home(o, server, 7, a.session, h.handle, 8, 91, move || {
            state.lock().unwrap().published += 1;
            ready.send(()).unwrap();
            0
        })
    });
    wait.recv_timeout(Duration::from_secs(2))
        .expect("HOME_ACTIVATION_PUBLISH");
    let mut f = Client::connect_home(client, 91).expect("HOME_ACTIVATION_TWO_GRANTS");
    let home = f.home().unwrap();
    let root = f.root().unwrap();
    assert!(
        f.lookup(root, b"system", 7).is_err(),
        "HOME_ACTIVATION_ROOT_RIGHTS"
    );
    let system = f.lookup(root, b"system", 3).unwrap();
    assert_eq!(
        f.write(system.handle, 0, b"nope").unwrap_err().outcome,
        MutationOutcome::NotSent
    );
    let file = f.lookup(home, b"data", 6).unwrap();
    let done = f.write(file.handle, 0, b"home").unwrap();
    assert_eq!((done.txg, done.bytes), (1, 4));
    let mut bytes = [0; 4096];
    assert_eq!(f.read(file.handle, 0, 4, &mut bytes), Ok(4));
    assert_eq!(&bytes[..4], b"home");
    f.close(file.handle).unwrap();
    f.close(system.handle).unwrap();
    assert_eq!(f.disconnect(), Ok([0, 0]));
    let report = join.join().unwrap();
    assert!(report.ready);
    assert_eq!(report.stop, Stop::Disconnected);
    assert_eq!(report.cleanup, [-7, -8]);
    let s = seen.lock().unwrap();
    assert_eq!(
        (
            s.published,
            s.writes,
            s.clocks,
            s.drops,
            s.closes,
            s.client_closes
        ),
        (1, 1, 1, 1, 1, 1)
    );
}
#[test]
fn invalid_sources_and_epoch_never_publish_or_send() {
    for lane in 0..8 {
        let seen = Shared::default();
        let (mut o, a, mut h) = owner(seen.clone());
        let mut source = 7;
        let mut peer = 8;
        let mut epoch = 91;
        let expected = match lane {
            0 => {
                epoch = 0;
                p::Error::Invalid
            }
            1 => {
                h = a.root;
                p::Error::Denied
            }
            2 => {
                h = o
                    .lookup(
                        7,
                        a.session,
                        a.root.handle,
                        b"home",
                        Rights::new(3).unwrap(),
                    )
                    .unwrap();
                p::Error::Denied
            }
            3 => {
                h = o
                    .lookup(
                        7,
                        a.session,
                        a.root.handle,
                        b"system",
                        Rights::new(7).unwrap(),
                    )
                    .unwrap();
                p::Error::NotDirectory
            }
            4 => {
                o.disconnect(7, a.session).unwrap();
                p::Error::Stale
            }
            5 => {
                source = 9;
                p::Error::Denied
            }
            6 => {
                peer = 0;
                p::Error::Invalid
            }
            _ => {
                o.close(7, a.session, h.handle).unwrap();
                p::Error::Stale
            }
        };
        let state = seen.clone();
        let report = run_home(
            o,
            Script::new(seen.clone()),
            source,
            a.session,
            h.handle,
            peer,
            epoch,
            move || {
                state.lock().unwrap().published += 1;
                0
            },
        );
        assert_eq!(report.stop, Stop::Provision(expected));
        assert!(!report.ready);
        assert_eq!(report.cleanup, [-7, -8]);
        let s = seen.lock().unwrap();
        let actual = (s.published, s.sent.len(), s.receives, s.drops, s.closes);
        drop(s);
        assert_eq!(
            actual,
            (0, 0, 0, 1, 1),
            "HOME_ACTIVATION_ATTACH_BEFORE_PUBLISH"
        );
    }
}
#[test]
fn both_greeting_losses_preserve_error_and_incomplete_ready() {
    for at in [0, 1] {
        let seen = Shared::default();
        let (o, a, h) = owner(seen.clone());
        let mut io = Script::new(seen.clone());
        io.fail = Some(at);
        io.error = i64::MIN;
        let state = seen.clone();
        let report = run_home(o, io, 7, a.session, h.handle, 8, 91, move || {
            state.lock().unwrap().published += 1;
            0
        });
        assert_eq!(report.stop, Stop::ReplyLost(i64::MIN));
        assert!(!report.ready, "HOME_ACTIVATION_TWO_SENDS");
        assert_eq!(report.cleanup, [-7, -8]);
        let s = seen.lock().unwrap();
        assert_eq!(
            (
                s.published,
                s.sent.len(),
                s.completed,
                s.receives,
                s.drops,
                s.closes
            ),
            (1, at + 1, at, 0, 1, 1)
        );
    }
}
#[test]
fn malformed_greeting_fields_at_both_stages_latch() {
    for stage in [0, 1] {
        for change in 0..10 {
            let seen = Shared::default();
            let state = seen.clone();
            let mut channel = HomeActivated {
                inner: Script::new(seen.clone()),
                publish: move || {
                    state.lock().unwrap().published += 1;
                    0
                },
                epoch: 91,
                stage: Stage::Root,
            };
            if stage == 1 {
                channel.send(&greeting(1)).unwrap();
            }
            let mut bad = greeting(if stage == 0 { 1 } else { 2 });
            match change {
                0 => bad[0] ^= 1,
                1 => put(&mut bad, 1, (-13i64) as u64),
                2 => put(&mut bad, 2, 0),
                3 => put(&mut bad, 2, 92),
                4 => put(&mut bad, 3, 0),
                5 => put(&mut bad, 3, if stage == 0 { 2 } else { 1 }),
                6 => put(&mut bad, 3, 3),
                7 => put(&mut bad, 4, 2),
                8 => put(&mut bad, 6, 1),
                _ => put(&mut bad, 7, 1),
            };
            assert_eq!(
                channel.send(&bad),
                Err(-22),
                "HOME_ACTIVATION_GREETING_VALIDATION"
            );
            assert_eq!(
                channel.send(&greeting(if stage == 0 { 1 } else { 2 })),
                Err(-5),
                "HOME_ACTIVATION_LATCH"
            );
            assert_eq!(channel.close(), [-7, -8]);
            let s = seen.lock().unwrap();
            assert_eq!((s.published, s.sent.len(), s.closes), (stage, stage, 1));
        }
    }
}
#[test]
fn publication_errors_preserve_raw_and_never_send() {
    for raw in [-91, i64::MIN, 1, i64::MAX] {
        let seen = Shared::default();
        let (o, a, h) = owner(seen.clone());
        let state = seen.clone();
        let report = run_home(
            o,
            Script::new(seen.clone()),
            7,
            a.session,
            h.handle,
            8,
            91,
            move || {
                state.lock().unwrap().published += 1;
                raw
            },
        );
        assert_eq!(
            report.stop,
            Stop::ReplyLost(if raw < 0 { raw } else { -5 }),
            "HOME_ACTIVATION_PUBLICATION_STATUS"
        );
        assert!(!report.ready);
        assert_eq!(report.cleanup, [-7, -8]);
        let s = seen.lock().unwrap();
        assert_eq!(
            (s.published, s.sent.len(), s.receives, s.drops, s.closes),
            (1, 0, 0, 1, 1)
        );
    }
}
#[test]
fn post_greeting_reply_error_latches_without_second_publication() {
    let seen = Shared::default();
    let state = seen.clone();
    let mut io = Script::new(seen.clone());
    io.fail = Some(2);
    io.error = i64::MIN;
    let mut channel = HomeActivated {
        inner: io,
        publish: move || {
            state.lock().unwrap().published += 1;
            0
        },
        epoch: 91,
        stage: Stage::Root,
    };
    channel.send(&greeting(1)).unwrap();
    channel.send(&greeting(2)).unwrap();
    let bytes = [0xa5; 64];
    assert_eq!(channel.send(&bytes), Err(i64::MIN));
    assert_eq!(channel.send(&bytes), Err(-5), "HOME_ACTIVATION_LATCH");
    assert_eq!(channel.close(), [-7, -8]);
    let s = seen.lock().unwrap();
    assert_eq!(
        (s.published, s.sent.len(), s.completed, s.closes),
        (1, 3, 2, 1)
    );
    assert_eq!(s.sent[2], bytes);
}

#[cfg(fs_af09_drain)]
#[test]
fn counter_forward_requires_ready_and_latches_failure_without_retry() {
    for stage in [Stage::Root, Stage::Home, Stage::Failed] {
        let seen = Arc::new(Mutex::new(Seen::default()));
        let mut channel = HomeActivated {
            inner: Script::new(seen.clone()),
            publish: || 0,
            epoch: 91,
            stage,
        };
        assert_eq!(channel.af09_counts(2, 3), Err(-5));
        assert_eq!(channel.af09_counts(2, 3), Err(-5));
        assert!(seen.lock().unwrap().counts.is_empty());
    }
    let seen = Arc::new(Mutex::new(Seen::default()));
    let mut channel = HomeActivated {
        inner: Script::new(seen.clone()),
        publish: || 0,
        epoch: 91,
        stage: Stage::Ready,
    };
    assert_eq!(channel.af09_counts(2, 3), Ok(()));
    seen.lock().unwrap().count_error = Some(-28);
    assert_eq!(channel.af09_counts(9, 4), Err(-28));
    assert_eq!(channel.af09_counts(2, 3), Err(-5));
    assert_eq!(channel.send(&[0; 64]), Err(-5));
    assert_eq!(channel.close(), [-7, -8]);
    let s = seen.lock().unwrap();
    assert_eq!(s.counts, [(2, 3), (9, 4)], "AF09_DRAIN_ACTIVATION_LATCH");
    assert!(s.sent.is_empty());
    assert_eq!(s.closes, 1);
}
