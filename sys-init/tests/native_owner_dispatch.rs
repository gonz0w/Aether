// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use fd_dispatch::Peer;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity, Process, ProcessFiles};
use filesystem_service::{
    channel::{Framed, Io},
    put,
};
use fixture::{Fault, Harness, Pipe};
use fork_gate::{GateError, Owner, Phase};
use fork_streams::{Caller, Outcome, SessionPipe, State};
use std::{
    cell::RefCell,
    panic::{AssertUnwindSafe, catch_unwind},
    rc::Rc,
};
#[derive(Default)]
struct Seen {
    at: usize,
    sent: Vec<u8>,
    calls: usize,
    waits: usize,
    closed: usize,
}
struct Wire {
    bytes: Vec<u8>,
    seen: Rc<RefCell<Seen>>,
    limit: usize,
    eagain: bool,
    wait_error: i64,
    overcount: bool,
    fail_send: Option<usize>,
    panic_at: Option<usize>,
    idle: bool,
    eof: bool,
}
impl Io for Wire {
    fn transfer(&mut self, writing: bool, out: &mut [u8]) -> i64 {
        assert!(!out.is_empty() && out.len() <= 16);
        let mut seen = self.seen.borrow_mut();
        seen.calls += 1;
        if self.eagain && seen.calls % 2 == 1 {
            return -11;
        }
        if self.overcount {
            return 17;
        }
        if writing {
            let mut n = out.len().min(7);
            if let Some(limit) = self.fail_send {
                if seen.sent.len() == limit {
                    return -32;
                }
                n = n.min(limit - seen.sent.len());
            }
            seen.sent.extend_from_slice(&out[..n]);
            return n as i64;
        }
        assert_ne!(self.panic_at, Some(seen.at), "receive unwind");
        if seen.at == self.limit {
            return if self.eof {
                0
            } else if self.idle {
                -11
            } else {
                -32
            };
        }
        let n = out.len().min(7).min(self.limit - seen.at);
        out[..n].copy_from_slice(&self.bytes[seen.at..seen.at + n]);
        seen.at += n;
        n as i64
    }
    fn wait(&mut self, _: bool) -> i64 {
        self.seen.borrow_mut().waits += 1;
        self.wait_error
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.borrow_mut().closed += 1;
        [-7, -8]
    }
}
fn identity() -> Identity {
    Identity::admitted(1, 1, 0xb0000102).unwrap()
}
fn native(slot: u32) -> NativeIdentity {
    NativeIdentity::admitted(slot, 1, 0xb0000100 | (slot as u64 + 1)).unwrap()
}
fn plan(file: bool) -> Plan {
    let mut p = Plan {
        identity: identity(),
        shell: 1,
        parent: 7,
        generation: 77,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [0; 2],
    };
    if file {
        p.bindings[15] = Binding {
            kind: 3,
            selector: filesystem_remote_descriptors::FIRST_FILE_FD as u8,
            cloexec: 1,
        };
    }
    p
}
fn fork(file: bool, sequence: u64) -> Vec<u8> {
    let mut raw = [0; 304];
    fd_startup::encode(&plan(file), &mut raw).unwrap();
    raw[..8].copy_from_slice(fork_frames::MAGIC);
    raw[296..].copy_from_slice(&sequence.to_le_bytes());
    raw.to_vec()
}
fn file(op: u64, sequence: u64, a: u64, b: u64) -> Vec<u8> {
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(fd_dispatch::MAGIC);
    for (index, word) in [op, 77, sequence, a, b, 0, 0].into_iter().enumerate() {
        put(&mut raw, index + 1, word);
    }
    raw.to_vec()
}
fn pipe() -> Vec<u8> {
    let mut raw = vec![0; 32];
    raw[0] = 82;
    raw[4..8].copy_from_slice(&0x76050001u32.to_le_bytes());
    raw[8] = 1;
    raw
}
type Gate = Owner<Pipe, State>;
type App = Peer<Framed<Wire>>;
fn setup(bytes: Vec<u8>) -> (Harness, Gate, App, Process, Rc<RefCell<Seen>>) {
    setup_fault(bytes, Fault::None)
}
fn setup_fault(bytes: Vec<u8>, fault: Fault) -> (Harness, Gate, App, Process, Rc<RefCell<Seen>>) {
    let mut h = Harness::new(fault, [-9, -5]);
    let mut files = h.fds.take().unwrap();
    let parent = files.admitted_shell(native(1), 7).unwrap();
    let (peer, seen) = application(bytes, parent, 77);
    let state = State::new([None; 3], [SessionPipe::new(), SessionPipe::new()]).unwrap();
    (h, Owner::new(files, state), peer, parent, seen)
}
fn application(bytes: Vec<u8>, process: Process, generation: u64) -> (App, Rc<RefCell<Seen>>) {
    let seen = Rc::new(RefCell::new(Seen::default()));
    let limit = bytes.len();
    let app = Wire {
        bytes,
        seen: seen.clone(),
        limit,
        eagain: false,
        wait_error: 0,
        overcount: false,
        fail_send: None,
        panic_at: None,
        idle: false,
        eof: false,
    };
    (Peer::bind(Framed(app), process, generation).unwrap(), seen)
}
fn no_stream(
    _: &mut ProcessFiles<Pipe>,
    _: &mut State,
    _: &mut App,
    _: &[u8; 32],
    _: &mut u32,
) -> Result<(), i64> {
    panic!("unexpected stream callback")
}
fn pipe_stream(
    _: &mut ProcessFiles<Pipe>,
    state: &mut State,
    peer: &mut App,
    frame: &[u8; 32],
    budget: &mut u32,
) -> Result<(), i64> {
    let Outcome::Reply(mut response) = state.pipe_mut(0).unwrap().request(Caller::Parent, frame)
    else {
        panic!("factory cannot pend")
    };
    owner_dispatch::reply(peer, &mut response, budget)
}
fn cleanup(h: Harness, mut g: Gate, mut p: App) {
    g.retire();
    assert_eq!(g.cleanup(), Some([-9, -5]));
    p.close();
    drop(p);
    drop(g);
    assert_eq!(h.local.lock().unwrap().closes, 1);
    drop(h);
}

#[test]
fn same_channel_file_offset_then_fork_retains_exact_closed_capture() {
    let mut input = file(1, 1, 1, 4);
    let mut name = vec![0; 64];
    name[..4].copy_from_slice(b"file");
    input.extend(name);
    input.extend(file(
        2,
        2,
        filesystem_remote_descriptors::FIRST_FILE_FD as u64,
        2,
    ));
    input.extend(fork(true, 7));
    let (h, mut g, mut p, parent, seen) = setup(input);
    p.with_channel(|c| c.0.eagain = true).unwrap();
    let mut workspace = [0xa5; 4096];
    let mut budget = 1000;
    for target in [64, 192] {
        for _ in 0..3 {
            if seen.borrow().sent.len() >= target {
                break;
            }
            assert!(
                owner_dispatch::dispatch(
                    &mut g,
                    &mut p,
                    (identity(), 7, 77),
                    &mut budget,
                    &mut workspace,
                    no_stream
                )
                .unwrap()
                .is_none()
            );
        }
        assert_eq!(seen.borrow().sent.len(), target);
        assert_eq!(g.phase(), Phase::Idle);
        assert_eq!(workspace, [0; 4096]);
    }
    let mut snapshot = None;
    for _ in 0..3 {
        snapshot = owner_dispatch::dispatch(
            &mut g,
            &mut p,
            (identity(), 7, 77),
            &mut budget,
            &mut workspace,
            no_stream,
        )
        .unwrap();
        if snapshot.is_some() {
            break;
        }
    }
    assert!(
        snapshot.is_some(),
        "fork must retain captured owner admission"
    );
    let snapshot = snapshot.unwrap();
    assert_eq!(g.sequence(), 7);
    assert_eq!(g.phase(), Phase::Capturing);
    assert_eq!(
        g.admit(|files, _| files.close(parent, filesystem_remote_descriptors::FIRST_FILE_FD)),
        Err(GateError::Closed)
    );
    assert_eq!(
        snapshot.bindings[15],
        Binding {
            kind: 3,
            selector: filesystem_remote_descriptors::FIRST_FILE_FD as u8,
            cloexec: 1
        }
    );
    assert_eq!(workspace, [0; 4096]);
    assert_eq!(seen.borrow().at, 496);
    assert!(seen.borrow().waits > 0);
    assert_eq!(h.opcodes(), [1, 2]);
    assert_eq!(&seen.borrow().sent[128..130], b"ab");
    let child = g
        .copy(7, parent, native(2), 9, &snapshot, |streams| {
            for i in 0..2 {
                streams
                    .pipe_mut(i)
                    .unwrap()
                    .stage_participant(1, 1, [false; 2])
                    .unwrap();
            }
            CopyAttempt::Copied {
                identity: native(2),
                parent_pid: 9,
            }
        })
        .unwrap()
        .unwrap();
    g.context_ready(7, 10).unwrap();
    g.parent_delivered(7, 10).unwrap();
    g.admit(|files, _| {
        assert_eq!(
            files.file_view_v1(child),
            Ok((
                1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
            ))
        );
        let mut data = [0; 4096];
        assert_eq!(
            files.read(
                child,
                filesystem_remote_descriptors::FIRST_FILE_FD,
                2,
                &mut data
            ),
            Ok(2)
        );
        assert_eq!(&data[..2], b"cd");
    })
    .unwrap();
    cleanup(h, g, p);
    assert_eq!(seen.borrow().closed, 1);
}

#[test]
fn every_short_file_fork_stream_prefix_retires_once_and_clears_workspace() {
    let mut open = file(1, 1, 0, 4);
    let mut name = vec![0; 64];
    name[..4].copy_from_slice(b"file");
    open.extend(name);
    for input in [open, fork(false, 1), pipe()] {
        for limit in 0..input.len() {
            let (h, mut g, mut p, _, seen) = setup(input.clone());
            p.with_channel(|c| c.0.limit = limit).unwrap();
            let mut workspace = [0xa5; 4096];
            assert!(
                owner_dispatch::dispatch(
                    &mut g,
                    &mut p,
                    (identity(), 7, 77),
                    &mut 1000,
                    &mut workspace,
                    pipe_stream
                )
                .is_err()
            );
            assert_eq!(g.phase(), Phase::Retired);
            assert_eq!(workspace, [0; 4096]);
            assert_eq!(seen.borrow().at, limit);
            assert_eq!(p.cleanup(), Some([-7, -8]));
            cleanup(h, g, p);
            assert_eq!(seen.borrow().closed, 1);
        }
    }
}

#[test]
fn stream_handler_uses_same_channel_and_actual_pipe_then_rejects_stale_history() {
    let mut input = pipe();
    input.extend(fork(false, 1));
    let (h, mut g, mut p, parent, seen) = setup(input);
    let mut workspace = [0xa5; 4096];
    assert!(
        owner_dispatch::dispatch(
            &mut g,
            &mut p,
            (identity(), 7, 77),
            &mut 1000,
            &mut workspace,
            pipe_stream
        )
        .unwrap()
        .is_none()
    );
    assert_eq!(g.phase(), Phase::Idle);
    assert_eq!(seen.borrow().sent.len(), 32);
    assert_eq!(seen.borrow().sent[4], 1);
    assert_eq!(workspace, [0; 4096]);
    let snapshot = owner_dispatch::dispatch(
        &mut g,
        &mut p,
        (identity(), 7, 77),
        &mut 1000,
        &mut workspace,
        no_stream,
    )
    .unwrap()
    .unwrap();
    // Decoder accepts labels, but actual holder/history preflight must reject
    // the old no-pipe snapshot before a native copy callback can be invoked.
    assert_eq!(g.retired_streams(|_| ()).err(), Some(GateError::Closed));
    assert_eq!(snapshot.history, [0; 2]);
    assert!(matches!(
        g.copy(1, parent, native(2), 9, &snapshot, |_| panic!(
            "invalid actual streams copied"
        )),
        Err(GateError::Streams(-9))
    ));
    cleanup(h, g, p);
}

#[test]
fn unknown_headers_wrong_identity_generation_and_bad_source_never_reach_handlers() {
    for (case, at) in [
        (0, 0),
        (1, 8),
        (2, 12),
        (3, 16),
        (4, 56),
        (5, 112),
        (6, 296),
        (7, 0),
    ] {
        let mut input = fork(false, 7);
        input[at] ^= 1;
        if case == 6 {
            input[296..].fill(0);
        }
        if case == 7 {
            input = file(1, 1, 0, 4);
            let other = if fd_dispatch::MAGIC == b"AEFD0001" {
                b"AEFP0001"
            } else {
                b"AEFD0001"
            };
            input[..8].copy_from_slice(other);
        }
        let (h, mut g, mut p, _, seen) = setup(input);
        let mut workspace = [0xa5; 4096];
        assert!(
            owner_dispatch::dispatch(
                &mut g,
                &mut p,
                (identity(), 7, 77),
                &mut 1000,
                &mut workspace,
                no_stream
            )
            .is_err(),
            "case {case}"
        );
        if case < 3 || case == 7 {
            assert_eq!(seen.borrow().at, 16);
        }
        assert_eq!(g.phase(), Phase::Retired);
        assert_eq!(workspace, [0; 4096]);
        assert!(h.opcodes().is_empty());
        cleanup(h, g, p);
    }
}

#[test]
fn closed_admission_and_unwind_cannot_consume_or_reopen() {
    for at in [0, 16, 23] {
        let (h, mut g, mut p, _, seen) = setup(fork(false, 7));
        p.with_channel(|c| c.0.panic_at = Some(at)).unwrap();
        let mut workspace = [0xa5; 4096];
        assert!(
            catch_unwind(AssertUnwindSafe(|| owner_dispatch::dispatch(
                &mut g,
                &mut p,
                (identity(), 7, 77),
                &mut 1000,
                &mut workspace,
                no_stream
            )))
            .is_err()
        );
        assert_eq!(g.phase(), Phase::Receiving);
        assert_eq!(workspace, [0; 4096]);
        let before = seen.borrow().calls;
        assert!(matches!(
            owner_dispatch::dispatch(
                &mut g,
                &mut p,
                (identity(), 7, 77),
                &mut 1000,
                &mut workspace,
                no_stream
            ),
            Err(GateError::Closed)
        ));
        assert_eq!(seen.borrow().calls, before);
        cleanup(h, g, p);
    }
}

#[test]
fn lost_file_reply_and_raw_budget_count_wait_errors_do_not_replay() {
    for case in 0..5 {
        let mut input = file(1, 1, 0, 4);
        let mut name = vec![0; 64];
        name[..4].copy_from_slice(b"file");
        input.extend(name);
        let (h, mut g, mut p, _, seen) = setup(input);
        p.with_channel(|c| match case {
            0 => c.0.fail_send = Some(7),
            1 => c.0.overcount = true,
            2 => {
                c.0.eagain = true;
                c.0.wait_error = -7;
            }
            3 => {
                c.0.eagain = true;
                c.0.wait_error = 1;
            }
            _ => (),
        })
        .unwrap();
        let mut budget = if case == 4 { 0 } else { 1000 };
        let mut workspace = [0xa5; 4096];
        let mut result = Ok(None);
        for _ in 0..2 {
            result = owner_dispatch::dispatch(
                &mut g,
                &mut p,
                (identity(), 7, 77),
                &mut budget,
                &mut workspace,
                no_stream,
            );
            if result.is_err() {
                break;
            }
        }
        assert!(result.is_err());
        assert_eq!(g.phase(), Phase::Retired);
        assert_eq!(workspace, [0; 4096]);
        assert_eq!(h.opcodes(), if case == 0 { vec![1] } else { vec![] });
        let before = seen.borrow().calls;
        assert!(
            owner_dispatch::dispatch(
                &mut g,
                &mut p,
                (identity(), 7, 77),
                &mut 1000,
                &mut workspace,
                no_stream
            )
            .is_err()
        );
        assert_eq!(seen.borrow().calls, before);
        cleanup(h, g, p);
        assert_eq!(seen.borrow().closed, 1);
    }
}

#[test]
fn idle_parent_does_not_park_owner_or_starve_an_active_copied_child() {
    let (h, mut g, mut parent_peer, parent, parent_seen) = setup(Vec::new());
    parent_peer.with_channel(|c| c.0.idle = true).unwrap();
    g.begin(1, |_, _| ()).unwrap();
    let child = g
        .copy(1, parent, native(2), 9, &plan(false), |streams| {
            for object in 0..2 {
                streams
                    .pipe_mut(object)
                    .unwrap()
                    .stage_participant(1, 1, [false; 2])
                    .unwrap();
            }
            CopyAttempt::Copied {
                identity: native(2),
                parent_pid: 9,
            }
        })
        .unwrap()
        .unwrap();
    g.context_ready(1, 10).unwrap();
    g.parent_delivered(1, 10).unwrap();
    let mut input = file(1, 1, 0, 4);
    input[16..24].copy_from_slice(&78u64.to_le_bytes());
    let mut name = vec![0; 64];
    name[..4].copy_from_slice(b"file");
    input.extend(name);
    let (mut child_peer, child_seen) = application(input, child, 78);
    let mut workspace = [0xa5; 4096];
    assert!(
        owner_dispatch::dispatch(
            &mut g,
            &mut parent_peer,
            (identity(), 7, 77),
            &mut 1000,
            &mut workspace,
            no_stream
        )
        .unwrap()
        .is_none()
    );
    assert_eq!(g.phase(), Phase::Idle);
    assert_eq!(parent_seen.borrow().at, 0);
    assert_eq!(parent_seen.borrow().waits, 0);
    assert!(h.opcodes().is_empty());
    assert_eq!(workspace, [0; 4096]);
    let id = Identity::admitted(2, 1, 0xb0000103).unwrap();
    assert!(
        owner_dispatch::dispatch(
            &mut g,
            &mut child_peer,
            (id, 9, 78),
            &mut 1000,
            &mut workspace,
            no_stream
        )
        .unwrap()
        .is_none()
    );
    assert_eq!(child_seen.borrow().sent.len(), 64);
    assert_eq!(h.opcodes(), [1]);
    assert_eq!(workspace, [0; 4096]);
    child_peer.close();
    drop(child_peer);
    cleanup(h, g, parent_peer);
    assert_eq!(child_seen.borrow().closed, 1);
    assert_eq!(parent_seen.borrow().closed, 1);
}

#[test]
fn consumed_fork_sequence_cannot_be_replayed_after_settled_refusal() {
    for sequence in [7, u64::MAX] {
        let (h, mut g, mut p, parent, seen) = setup(fork(false, sequence));
        g.begin(sequence, |_, _| ()).unwrap();
        g.copy(sequence, parent, native(2), 9, &plan(false), |_| {
            CopyAttempt::Refused(-12)
        })
        .unwrap()
        .unwrap_err();
        g.resolve_refusal(sequence, -12, |_| Ok(-11))
            .unwrap()
            .unwrap();
        g.refusal_delivered(sequence, -12).unwrap();
        let mut workspace = [0xa5; 4096];
        assert!(matches!(
            owner_dispatch::dispatch(
                &mut g,
                &mut p,
                (identity(), 7, 77),
                &mut 1000,
                &mut workspace,
                no_stream
            ),
            Err(GateError::Sequence)
        ));
        assert_eq!(g.sequence(), sequence);
        assert_eq!(g.phase(), Phase::Retired);
        assert_eq!(seen.borrow().at, 304);
        assert!(h.opcodes().is_empty());
        assert_eq!(workspace, [0; 4096]);
        cleanup(h, g, p);
    }
}

#[test]
fn source_loss_during_file_read_closes_without_an_error_reply() {
    let mut input = file(1, 1, 0, 4);
    let mut name = vec![0; 64];
    name[..4].copy_from_slice(b"file");
    input.extend(name);
    input.extend(file(
        2,
        2,
        filesystem_remote_descriptors::FIRST_FILE_FD as u64,
        2,
    ));
    let (h, mut g, mut p, _, seen) = setup_fault(input, Fault::ReadBody);
    let mut workspace = [0xa5; 4096];
    assert!(
        owner_dispatch::dispatch(
            &mut g,
            &mut p,
            (identity(), 7, 77),
            &mut 1000,
            &mut workspace,
            no_stream
        )
        .unwrap()
        .is_none()
    );
    assert!(
        owner_dispatch::dispatch(
            &mut g,
            &mut p,
            (identity(), 7, 77),
            &mut 1000,
            &mut workspace,
            no_stream
        )
        .is_err()
    );
    assert_eq!(g.phase(), Phase::Retired);
    assert_eq!(g.cleanup(), Some([-9, -5]));
    assert_eq!(p.cleanup(), Some([-7, -8]));
    assert_eq!(h.opcodes(), [1, 2]);
    assert_eq!(workspace, [0; 4096]);
    assert_eq!(seen.borrow().sent.len(), 64);
    cleanup(h, g, p);
    assert_eq!(seen.borrow().closed, 1);
}

#[test]
fn polling_defers_an_effect_free_pipe_read_and_retains_exact_request() {
    let mut core = SessionPipe::new();
    let mut factory = [0; 32];
    factory[0] = 82;
    factory[4..8].copy_from_slice(&0x76050001u32.to_le_bytes());
    factory[8] = 1;
    assert!(matches!(
        core.request(Caller::Parent, &factory),
        Outcome::Reply(_)
    ));
    let mut read = [0; 32];
    read[0] = 1;
    read[4..8].copy_from_slice(&0x78000101u32.to_le_bytes());
    read[8] = 3;
    read[12] = 2;
    let (h, mut g, mut p, _, seen) = setup(read.to_vec());
    let mut workspace = [0xa5; 4096];
    let event = owner_dispatch::poll(
        &mut g,
        &mut p,
        (identity(), 7, 77),
        &mut 1000,
        &mut workspace,
        |_, _, _, frame, _| {
            assert!(matches!(
                core.request(Caller::Parent, frame),
                Outcome::Pending
            ));
            Ok(owner_dispatch::Completion::Pending)
        },
    )
    .unwrap();
    let owner_dispatch::Event::Pending(retained) = event else {
        panic!("blocked read needs retained request")
    };
    assert_eq!(retained, read);
    assert_eq!(g.phase(), Phase::Idle);
    assert!(seen.borrow().sent.is_empty());
    assert_eq!(workspace, [0; 4096]);
    let mut write = read;
    write[0] = 2;
    write[4] = 2;
    write[8] = 4;
    write[16..18].copy_from_slice(b"ab");
    assert!(matches!(
        core.request(Caller::Parent, &write),
        Outcome::Reply(_)
    ));
    g.admit(|_, _| {
        let Outcome::Reply(mut response) = core.request(Caller::Parent, &retained) else {
            panic!("data must complete retained read")
        };
        assert_eq!(&response[16..18], b"ab");
        owner_dispatch::reply(&mut p, &mut response, &mut 1000).unwrap();
    })
    .unwrap();
    assert_eq!(seen.borrow().sent.len(), 32);
    assert!(matches!(
        core.request(Caller::Parent, &retained),
        Outcome::Pending
    ));
    cleanup(h, g, p);
}
#[test]
fn polling_initial_eof_is_not_terminal_or_cleanup_and_legacy_stays_fail_closed() {
    let (h, mut g, mut p, _, seen) = setup(vec![]);
    p.with_channel(|c| c.0.eof = true).unwrap();
    let mut workspace = [0xa5; 4096];
    assert!(matches!(
        owner_dispatch::poll(
            &mut g,
            &mut p,
            (identity(), 7, 77),
            &mut 1000,
            &mut workspace,
            |_, _, _, _, _| panic!("EOF cannot invoke a handler")
        )
        .unwrap(),
        owner_dispatch::Event::Eof
    ));
    assert_eq!(g.phase(), Phase::Idle);
    assert_eq!(g.cleanup(), None);
    assert_eq!(p.cleanup(), None);
    assert_eq!(seen.borrow().closed, 0);
    assert_eq!(workspace, [0; 4096]);
    assert!(
        owner_dispatch::dispatch(
            &mut g,
            &mut p,
            (identity(), 7, 77),
            &mut 1000,
            &mut workspace,
            no_stream
        )
        .is_err()
    );
    assert_eq!(g.phase(), Phase::Retired);
    cleanup(h, g, p);
}
