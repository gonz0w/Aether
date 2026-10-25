// SPDX-License-Identifier: BSD-2-Clause
//! Current actual AF09 libraries over synthetic storage; no native drain claim.
#![forbid(unsafe_code)]
use filesystem_activation::run_home;
use filesystem_client::{Client, MutationOutcome, MutationProgress};
use filesystem_policy::{self as p, Backend, Clock, Owner, Rights};
use filesystem_service::{Channel, Message, Report, Stop};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::Duration;

#[derive(Clone, Copy, PartialEq, Eq)]
enum Fault {
    None,
    LostSecondWrite,
    CommittedSecondWrite,
    CompletedSecondWrite,
}
#[derive(Default)]
struct Seen {
    roots: usize,
    mutations: usize,
    writes: usize,
    drops: usize,
    published: usize,
    frames: usize,
    server_closes: usize,
    client_closes: usize,
    greetings: usize,
    home: bool,
    probe: bool,
    size: usize,
    data: [u8; 16],
}
type Shared = Arc<Mutex<Seen>>;
struct Storage(Shared, Fault);
struct Time;
fn node(id: u64, size: u64) -> p::Node {
    p::Node::new(
        id,
        id + 10,
        size,
        if id < 3 {
            p::Kind::Directory
        } else {
            p::Kind::File
        },
    )
}
fn done(txg: u64, bytes: u64) -> p::Completion {
    p::Completion {
        error: 0,
        txg,
        bytes_staged: bytes,
        state: 2,
    }
}
impl Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        Ok(p::Utc {
            seconds: 1,
            nanoseconds: 0,
        })
    }
}
impl Drop for Storage {
    fn drop(&mut self) {
        self.0.lock().unwrap().drops += 1;
    }
}
impl Backend for Storage {
    fn root(&mut self) -> Result<p::Node, p::Error> {
        self.0.lock().unwrap().roots += 1;
        Ok(node(1, 0))
    }
    fn directory(&mut self, n: p::Node) -> Result<p::Node, p::Error> {
        Ok(n)
    }
    fn lookup(&mut self, at: p::Node, name: &[u8]) -> Result<p::Node, p::Error> {
        let s = self.0.lock().unwrap();
        match (at.identity().0, name) {
            (1, b"home") if s.home => Ok(node(2, 0)),
            (2, b"probe") if s.probe => Ok(node(3, s.size as u64)),
            (1, b"system") => Ok(node(4, 4)),
            _ => Err(p::Error::Backend(2)),
        }
    }
    fn read(&mut self, n: p::Node, at: u64, out: &mut [u8]) -> Result<usize, p::Error> {
        let s = self.0.lock().unwrap();
        let content: &[u8] = if n.identity().0 == 4 {
            b"sys!"
        } else {
            &s.data[..s.size]
        };
        let start = (at as usize).min(content.len());
        let count = out.len().min(content.len() - start);
        out[..count].copy_from_slice(&content[start..start + count]);
        Ok(count)
    }
    fn mutate(
        &mut self,
        at: p::Node,
        op: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        let mut s = self.0.lock().unwrap();
        s.mutations += 1;
        match op {
            p::Namespace::MakeDirectory { name: b"home", .. }
                if at.identity().0 == 1 && !s.home =>
            {
                s.home = true
            }
            p::Namespace::Create { name: b"probe", .. } if at.identity().0 == 2 && !s.probe => {
                s.probe = true
            }
            _ => panic!("LIFETIME_BOOTSTRAP_ONLY"),
        }
        Ok(done(s.mutations as u64, 0))
    }
    fn write(
        &mut self,
        n: p::Node,
        at: u64,
        bytes: &[u8],
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        assert_eq!(n.identity().0, 3, "LIFETIME_ROOT_WRITE_NO_EFFECT");
        let mut s = self.0.lock().unwrap();
        s.writes += 1;
        if s.writes == 2 {
            if self.1 == Fault::LostSecondWrite {
                return Err(p::Lost);
            }
            if matches!(
                self.1,
                Fault::CommittedSecondWrite | Fault::CompletedSecondWrite
            ) {
                return Ok(p::Completion {
                    error: 5,
                    txg: 4,
                    bytes_staged: bytes.len() as u64,
                    state: if self.1 == Fault::CommittedSecondWrite {
                        1
                    } else {
                        2
                    },
                });
            }
        }
        let offset = at as usize;
        s.data[offset..offset + bytes.len()].copy_from_slice(bytes);
        s.size = s.size.max(offset + bytes.len());
        Ok(done((s.mutations + s.writes) as u64, bytes.len() as u64))
    }
}
fn bootstrap(shared: Shared, fault: Fault) -> (Owner<Storage, Time>, p::Attachment, p::Entry) {
    let mut owner = Owner::new(Storage(shared, fault), Time, 91)
        .unwrap()
        .with_namespace_identity(p::Identity::new(1000, 1000).unwrap());
    let source = owner.attach(7, Rights::new(15).unwrap()).unwrap();
    owner
        .namespace(
            7,
            source.session,
            source.root.handle,
            p::Mutation::MakeDirectory(b"home"),
        )
        .unwrap();
    let home = owner
        .lookup(
            7,
            source.session,
            source.root.handle,
            b"home",
            Rights::new(15).unwrap(),
        )
        .unwrap();
    owner
        .validate_home_source(7, source.session, home.handle)
        .unwrap();
    owner
        .namespace(
            7,
            source.session,
            home.handle,
            p::Mutation::Create(b"probe"),
        )
        .unwrap();
    assert_eq!(owner.mutation_attempts(), 2, "LIFETIME_BOOTSTRAP_COUNT");
    (owner, source, home)
}
struct Pipe {
    tx: Option<mpsc::SyncSender<Message>>,
    rx: mpsc::Receiver<Message>,
    seen: Shared,
    server: bool,
    idle: Option<mpsc::SyncSender<()>>,
    corrupt_home: bool,
}
impl Channel for Pipe {
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        let mut frame = *frame;
        if self.server {
            let mut s = self.seen.lock().unwrap();
            assert_eq!(s.published, 1, "LIFETIME_READY_BEFORE_GREETING");
            if s.greetings < 2 {
                s.greetings += 1;
                if self.corrupt_home && s.greetings == 2 {
                    filesystem_service::put(&mut frame, 3, 1);
                }
            }
        }
        self.tx.as_ref().ok_or(-9)?.send(frame).map_err(|_| -32)
    }
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        if self.server {
            let idle = self.seen.lock().unwrap().frames == 5;
            if idle {
                if let Some(signal) = self.idle.take() {
                    signal.send(()).map_err(|_| -32)?;
                }
            }
        }
        *out = self
            .rx
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        if self.server {
            self.seen.lock().unwrap().frames += 1;
        }
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.tx.take();
        let mut s = self.seen.lock().unwrap();
        if self.server {
            s.server_closes += 1;
        } else {
            s.client_closes += 1;
        }
        [0; 2]
    }
}
struct Harness {
    client: Client<Pipe>,
    join: thread::JoinHandle<Report>,
    seen: Shared,
    idle: mpsc::Receiver<()>,
}
fn start(fault: Fault, corrupt_home: bool) -> Result<Harness, filesystem_client::ConnectFailure> {
    let seen = Shared::default();
    let state = seen.clone();
    let (a, b) = mpsc::sync_channel(0);
    let (c, d) = mpsc::sync_channel(0);
    let (idle, waiting) = mpsc::sync_channel(1);
    let server = Pipe {
        tx: Some(c),
        rx: b,
        seen: seen.clone(),
        server: true,
        idle: Some(idle),
        corrupt_home,
    };
    let client = Pipe {
        tx: Some(a),
        rx: d,
        seen: seen.clone(),
        server: false,
        idle: None,
        corrupt_home: false,
    };
    let join = thread::spawn(move || {
        let (o, a, h) = bootstrap(state.clone(), fault);
        run_home(o, server, 7, a.session, h.handle, 8, 91, move || {
            state.lock().unwrap().published += 1;
            0
        })
    });
    match Client::connect_home(client, 91) {
        Ok(client) => Ok(Harness {
            client,
            join,
            seen,
            idle: waiting,
        }),
        Err(error) => {
            let report = join.join().unwrap();
            assert!(!matches!(report.stop, Stop::Disconnected));
            Err(error)
        }
    }
}
fn checked(
    h: &mut Harness,
    result: Result<(), filesystem_client::Error>,
) -> Result<[i64; 2], filesystem_client::Error> {
    let seen = h.seen.clone();
    h.client.disconnect_checked(|channel| {
        assert_eq!(
            seen.lock().unwrap().client_closes,
            0,
            "LIFETIME_VERIFY_BEFORE_CLOSE"
        );
        let mut frame = [0; 64];
        assert_eq!(
            channel.receive(&mut frame),
            Err(-32),
            "LIFETIME_HOST_SERVER_EOF"
        );
        assert_eq!(
            seen.lock().unwrap().drops,
            1,
            "LIFETIME_OWNER_DROP_BEFORE_VERIFIED_CLOSE"
        );
        result
    })
}
#[test]
fn one_owner_two_phases_idle_and_one_checked_disconnect() {
    assert_eq!((filesystem_service::REQUESTS, p::MUTATION_LIMIT), (96, 9));
    let mut h = start(Fault::None, false).unwrap();
    let home = h.client.home().unwrap();
    let file = h.client.lookup(home, b"probe", 6).unwrap();
    h.client.write(file.handle, 0, b"phase-one-state!").unwrap();
    let mut bytes = [0; 4096];
    assert_eq!(h.client.read(file.handle, 0, 16, &mut bytes), Ok(16));
    assert_eq!(&bytes[..16], b"phase-one-state!");
    h.idle
        .recv_timeout(Duration::from_secs(2))
        .expect("LIFETIME_CONTROLLED_NO_REQUEST_IDLE");
    {
        let s = h.seen.lock().unwrap();
        assert_eq!(
            (
                s.roots,
                s.mutations,
                s.writes,
                s.published,
                s.drops,
                s.frames
            ),
            (1, 2, 1, 1, 0, 5)
        );
        assert_eq!((s.server_closes, s.client_closes), (0, 0));
    }
    assert_eq!(h.client.home().unwrap(), home, "LIFETIME_SAME_GRANT");
    h.client.write(file.handle, 0, b"phase-two-state!").unwrap();
    assert_eq!(h.client.read(file.handle, 0, 16, &mut bytes), Ok(16));
    assert_eq!(&bytes[..16], b"phase-two-state!");
    h.client.close(file.handle).unwrap();
    assert_eq!(checked(&mut h, Ok(())), Ok([0; 2]));
    assert!(
        h.client.disconnect().is_err(),
        "LIFETIME_NO_SECOND_DISCONNECT"
    );
    let report = h.join.join().unwrap();
    assert_eq!(
        (report.requests, report.mutation_attempts),
        (7, 4),
        "LIFETIME_GLOBAL_COUNTS_INCLUDE_TEARDOWN"
    );
    assert_eq!(report.stop, Stop::Disconnected);
    assert!(report.ready);
    assert_eq!(report.cleanup, [0; 2]);
    let s = h.seen.lock().unwrap();
    assert_eq!(
        (
            s.roots,
            s.published,
            s.drops,
            s.server_closes,
            s.client_closes
        ),
        (1, 1, 1, 1, 1)
    );
}
#[test]
fn global_mutation_limit_includes_bootstrap_without_reset() {
    let shared = Shared::default();
    let (mut owner, source, home) = bootstrap(shared.clone(), Fault::None);
    let file = owner
        .lookup(
            7,
            source.session,
            home.handle,
            b"probe",
            Rights::new(6).unwrap(),
        )
        .unwrap();
    for _ in 0..7 {
        owner
            .write(7, source.session, file.handle, 0, b"phase-one-state!")
            .unwrap();
    }
    assert_eq!(owner.mutation_attempts(), 9);
    assert_eq!(
        owner.write(7, source.session, file.handle, 0, b"phase-two-state!"),
        Err(p::Error::WriteLimit)
    );
    assert_eq!(
        (shared.lock().unwrap().writes, owner.mutation_attempts()),
        (7, 9)
    );
}
#[test]
fn unknown_and_committed_second_phase_never_replay_or_disconnect_cleanly() {
    for fault in [
        Fault::LostSecondWrite,
        Fault::CommittedSecondWrite,
        Fault::CompletedSecondWrite,
    ] {
        let mut h = start(fault, false).unwrap();
        let file = h
            .client
            .lookup(h.client.home().unwrap(), b"probe", 6)
            .unwrap();
        h.client.write(file.handle, 0, b"phase-one-state!").unwrap();
        let failure = h
            .client
            .write(file.handle, 0, b"phase-two-state!")
            .unwrap_err();
        let expected = if fault == Fault::LostSecondWrite {
            MutationProgress::Unknown
        } else if fault == Fault::CommittedSecondWrite {
            MutationProgress::Committed {
                txg: 4,
                bytes_staged: 16,
            }
        } else {
            MutationProgress::Completed {
                txg: 4,
                bytes_staged: 16,
            }
        };
        assert_eq!(
            failure.outcome,
            MutationOutcome::Reported(expected),
            "LIFETIME_RETAIN_PROGRESS"
        );
        assert_eq!(
            h.client
                .write(file.handle, 0, b"phase-two-state!")
                .unwrap_err()
                .outcome,
            MutationOutcome::NotSent
        );
        assert!(h
            .client
            .disconnect_checked(|_| panic!("retired source must not verify clean"))
            .is_err());
        let report = h.join.join().unwrap();
        assert_eq!(report.stop, Stop::Retired);
        assert_eq!((report.requests, report.mutation_attempts), (3, 4));
        let s = h.seen.lock().unwrap();
        assert_eq!((s.writes, s.drops, s.client_closes), (2, 1, 1));
    }
}
#[test]
fn wrong_home_greeting_is_not_client_admission() {
    let error = start(Fault::None, true)
        .err()
        .expect("LIFETIME_TWO_GRANTS_REQUIRED");
    assert_eq!(error.error, filesystem_client::Error::Protocol);
    assert_eq!(error.cleanup, [0; 2]);
}
#[test]
fn root_write_denial_has_no_provider_effect() {
    let mut h = start(Fault::None, false).unwrap();
    let root = h.client.root().unwrap();
    assert!(h.client.lookup(root, b"system", 7).is_err());
    let system = h.client.lookup(root, b"system", 3).unwrap();
    assert_eq!(
        h.client
            .write(system.handle, 0, b"deny")
            .unwrap_err()
            .outcome,
        MutationOutcome::NotSent
    );
    assert_eq!(h.seen.lock().unwrap().writes, 0);
    h.client.close(system.handle).unwrap();
    assert_eq!(checked(&mut h, Ok(())), Ok([0; 2]));
    assert_eq!(h.join.join().unwrap().stop, Stop::Disconnected);
}
#[test]
fn verification_failure_is_not_a_clean_disconnect() {
    let mut h = start(Fault::None, false).unwrap();
    assert_eq!(
        checked(&mut h, Err(filesystem_client::Error::Transport(-5))),
        Err(filesystem_client::Error::Transport(-5))
    );
    assert_eq!(h.client.cleanup(), Some([0; 2]));
    assert!(h.client.disconnect().is_err());
    assert_eq!(h.join.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(h.seen.lock().unwrap().client_closes, 1);
}
#[test]
fn spending_all96_requests_leaves_no_clean_teardown_slot() {
    let mut h = start(Fault::None, false).unwrap();
    let home = h.client.home().unwrap();
    for _ in 0..96 {
        h.client.stat(home).unwrap();
    }
    assert!(h
        .client
        .disconnect_checked(|_| panic!("limit cannot prove export"))
        .is_err());
    let report = h.join.join().unwrap();
    assert_eq!((report.requests, report.mutation_attempts), (96, 2));
    assert_eq!(report.stop, Stop::Limit);
}
