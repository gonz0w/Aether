// SPDX-License-Identifier: BSD-2-Clause
//! Scripted native facts; these host checks do not prove kernel authority.
use super::*;
use core::mem::MaybeUninit;
use filesystem_remote_descriptors::HomeAccess;
use filesystem_service::{Message, message, put as fs_put, word as fs_word};
use std::{cell::RefCell, rc::Rc, vec, vec::Vec};

#[derive(Default)]
struct Seen {
    source: Vec<u8>,
    source_at: usize,
    source_sent: Vec<u8>,
    app: Vec<u8>,
    app_at: usize,
    app_sent: Vec<u8>,
    fail_read: Option<usize>,
    fail_send: Option<usize>,
    closes: Vec<u64>,
    controls: usize,
    tick: u64,
    transfer_ticks: u64,
    source_blocked: usize,
    event_sequence: u64,
    observation_error: i64,
    wake_status: i64,
    wake_ticks: u64,
    parks: Vec<(u64, u64)>,
    engine_complete: bool,
    expire_after_engine_proof: bool,
    drain: bool,
    drain_fault: u8,
    stopped: bool,
    reaped: Vec<u64>,
    operations: Vec<(u64, u64)>,
}
#[derive(Clone)]
struct Mock(Rc<RefCell<Seen>>);
impl af07_transport::Kernel for Mock {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        let mut s = self.0.borrow_mut();
        if s.drain && (endpoint == 100 || endpoint == 101) {
            s.tick += s.transfer_ticks;
            if s.source_blocked > 0 {
                s.source_blocked -= 1;
                s.event_sequence += 1;
                return -11;
            }
        }
        if writing {
            if endpoint == 101 {
                if s.engine_complete && s.source_at == s.source.len() {
                    return -32;
                }
                s.source_sent.extend_from_slice(bytes);
                return bytes.len() as i64;
            }
            if endpoint != 103 {
                return -9;
            }
            let count = s.fail_send.map_or(bytes.len(), |n| {
                n.saturating_sub(s.app_sent.len()).min(bytes.len())
            });
            s.app_sent.extend_from_slice(&bytes[..count]);
            if count < bytes.len() {
                -91
            } else {
                count as i64
            }
        } else if endpoint == 100 {
            let n = bytes.len().min(s.source.len().saturating_sub(s.source_at));
            if n == 0 {
                return if s.engine_complete { 0 } else { -32 };
            }
            let at = s.source_at;
            bytes[..n].copy_from_slice(&s.source[at..at + n]);
            s.source_at += n;
            n as i64
        } else if endpoint == 102 {
            if s.fail_read.is_some_and(|n| s.app_at >= n) {
                return -91;
            }
            let n = bytes.len().min(s.app.len().saturating_sub(s.app_at));
            if n == 0 {
                return -32;
            }
            let at = s.app_at;
            bytes[..n].copy_from_slice(&s.app[at..at + n]);
            s.app_at += n;
            n as i64
        } else {
            -9
        }
    }
    fn wait(&mut self, _: u64) -> i64 {
        -91
    }
    fn close(&mut self, endpoint: u64) -> i64 {
        self.0.borrow_mut().closes.push(endpoint);
        if self.0.borrow().drain {
            return if self.0.borrow().drain_fault == 4 && endpoint == 102 {
                -91
            } else {
                0
            };
        }
        match endpoint {
            100 => -7,
            101 => -8,
            102 => -9,
            103 => -10,
            _ => -22,
        }
    }
}
impl Control for Mock {
    fn park_events(&mut self, sequence: u64, deadline: Option<Deadline>) -> owner_control::Status {
        if !self.0.borrow().drain {
            return self.ctl(0x2a001, 0xe002, sequence);
        }
        let mut s = self.0.borrow_mut();
        s.parks.push((sequence, deadline.map_or(0, Deadline::get)));
        s.tick += s.wake_ticks;
        let status = if s.drain_fault == 1 {
            -110
        } else {
            s.wake_status
        };
        if status == 0 {
            (0, s.event_sequence, s.tick)
        } else {
            (status, u64::MAX, u64::MAX)
        }
    }
    fn ctl(&mut self, op: u64, handle: u64, _: u64) -> owner_control::Status {
        let mut s = self.0.borrow_mut();
        s.controls += 1;
        if s.drain {
            s.operations.push((op, handle));
            return match op {
                0x2a000 => {
                    if s.observation_error == 0 {
                        (0, s.event_sequence, s.tick)
                    } else {
                        (s.observation_error, u64::MAX, u64::MAX)
                    }
                }
                0x2a001 => (-110, 0, 0),
                0x20001 if s.reaped.contains(&handle) => {
                    if handle == 99 && s.expire_after_engine_proof {
                        s.tick = 500;
                    }
                    (-9, 0, 0)
                }
                0x20001 if handle == 99 && s.engine_complete => (1, 0, 1),
                0x20001 if handle == 0xb0000102 => (1, 0, 1),
                0x20001 if s.stopped && s.drain_fault != 1 => {
                    if s.drain_fault == 2 {
                        (144, 0, 9)
                    } else {
                        (144, 0, 3)
                    }
                }
                0x20001 => (0, 0, 0),
                0x20007 => {
                    s.stopped = true;
                    (0, 0, 0)
                }
                0x20002 if s.drain_fault == 3 => (-91, 0, 0),
                0x20002 => {
                    s.reaped.push(handle);
                    (0, 0, 0)
                }
                _ => (-95, 0, 0),
            };
        }
        if op == 0x20001 {
            (0, 0, 0)
        } else {
            (-95, 0, 0)
        }
    }
    fn engine(&mut self, _: u64, _: u64) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
    fn delegate(&mut self, _: u64, _: &[u64; 3]) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
    fn launch(&mut self, _: &[u8; 272], _: u64, _: u64) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
    fn copy(&mut self, _: u64, _: u32, _: u64, _: u64, _: u64) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
    fn serial(&mut self, _: bool, _: &mut [u8]) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
    fn exec(&mut self, _: u64, _: u64, _: &[u8; 272]) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
    fn receipt(&mut self, _: u64) -> owner_control::Status {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        (-95, 0, 0)
    }
    fn publish(&mut self, _: u64, _: u64) -> i64 {
        assert!(!self.0.borrow().drain, "DRAIN_NO_NATIVE_EFFECT");
        -95
    }
}
fn greet(token: u64) -> Message {
    let mut f = message(77, 0);
    fs_put(&mut f, 3, token);
    fs_put(&mut f, 4, 1);
    f
}
fn kernel(frames: Vec<Message>) -> Mock {
    Mock(Rc::new(RefCell::new(Seen {
        source: frames.concat(),
        ..Seen::default()
    })))
}
fn source(k: &Mock) -> Channel<Mock> {
    Framed(Endpoints::new(k.clone(), 100, 101).ok().unwrap())
}
#[repr(C)]
struct Guard {
    before: u64,
    slot: MaybeUninit<Runtime<Mock>>,
    after: u64,
}
fn poisoned() -> Guard {
    let mut g = Guard {
        before: 17,
        slot: MaybeUninit::uninit(),
        after: 31,
    };
    // SAFETY: exactly the exclusive uninitialized slot, with canaries outside it.
    unsafe {
        core::ptr::write_bytes(
            g.slot.as_mut_ptr().cast::<u8>(),
            0xa5,
            core::mem::size_of::<Runtime<Mock>>(),
        )
    };
    g
}
#[test]
fn final_slot_home_constructor_initializes_every_record_and_outcome() {
    let k = kernel(vec![greet(1), greet(2)]);
    let mut g = poisoned();
    let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
        .expect("OWNER_HOME_INIT");
    assert_eq!(k.0.borrow().source_at, 128, "OWNER_TWO_GRANTS");
    assert_eq!(r.gate.phase(), fork_gate::Phase::Idle);
    assert!(!r.started);
    assert!(r.last_file().is_none(), "OWNER_INITIAL_OUTCOME");
    assert_eq!(r.source_cleanup(), None, "OWNER_SOURCE_CLEANUP");
    for n in 0..4 {
        assert!(r.peers[n].is_none());
        assert!(r.records[n].identity.is_none());
        assert_eq!(r.records[n].epoch, 0);
    }
    assert_eq!((r.engine, r.remaining), (99, 5000));
    assert_eq!((g.before, g.after), (17, 31));
    // SAFETY: success initialized every field; no returned borrow is used again.
    unsafe { g.slot.assume_init_drop() };
    assert_eq!(k.0.borrow().closes, [100, 101]);
}
#[test]
fn both_greeting_failures_and_invalid_inputs_keep_exact_close_results() {
    for stage in 0..2 {
        for change in 0..8 {
            let mut frames = vec![greet(1), greet(2)];
            let mut expected = FsError::Protocol;
            match change {
                0 => frames[stage][0] ^= 1,
                1 => fs_put(&mut frames[stage], 2, 78),
                2 => fs_put(&mut frames[stage], 3, 99),
                3 => fs_put(&mut frames[stage], 4, 2),
                4 => fs_put(&mut frames[stage], 6, 1),
                5 => fs_put(&mut frames[stage], 7, 1),
                6 => {
                    frames[stage] = message(77, (-13i64) as u64);
                    expected = FsError::Remote(-13);
                }
                _ => {
                    frames.truncate(stage);
                    expected = FsError::Transport(-32);
                }
            }
            let k = kernel(frames);
            let mut g = poisoned();
            let e =
                Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
                    .err()
                    .expect("OWNER_HOME_REJECT");
            assert_eq!(e.error, expected, "OWNER_HOME_FAILURE");
            assert_eq!(e.cleanup, [-7, -8], "OWNER_HOME_CLOSES");
            assert_eq!(k.0.borrow().closes, [100, 101]);
            assert_eq!(Rc::strong_count(&k.0), 1, "OWNER_HOME_FAILURE_DROP");
            assert_eq!((g.before, g.after), (17, 31));
        }
    }
    for (engine, epoch, budget) in [(99, 0, 5000), (99, 77, 0), (99, 77, 1000001), (0, 77, 5000)] {
        let k = kernel(vec![greet(1), greet(2)]);
        let mut g = poisoned();
        let e = Runtime::connect_home_in_place(
            &mut g.slot,
            k.clone(),
            engine,
            source(&k),
            epoch,
            budget,
        )
        .err()
        .unwrap();
        assert_eq!(e.error, FsError::Invalid);
        assert_eq!(e.cleanup, [-7, -8]);
        assert_eq!(k.0.borrow().source_at, 0, "OWNER_INIT_PREFLIGHT");
        assert_eq!(k.0.borrow().closes, [100, 101]);
    }
}
fn packets(status: i64) -> Vec<Message> {
    let mut lookup = message(77, 0);
    fs_put(&mut lookup, 3, 3);
    fs_put(&mut lookup, 4, 2);
    fs_put(&mut lookup, 5, 4);
    let mut done = message(77, status as u64);
    fs_put(&mut done, 4, if status == 0 { 1 } else { 0 });
    fs_put(&mut done, 5, 4);
    fs_put(&mut done, 6, if status == 0 { 2 } else { 1 });
    vec![greet(1), greet(2), lookup, done]
}
fn header() -> Message {
    let mut f = [0; 64];
    f[..8].copy_from_slice(fd_dispatch::MAGIC);
    for (i, v) in [11, 31, 1, 0, 4, 0, 0].into_iter().enumerate() {
        fs_put(&mut f, i + 1, v);
    }
    f
}
fn data() -> Message {
    let mut f = [0; 64];
    f[..4].copy_from_slice(b"home");
    f
}
fn prepare(r: &mut Runtime<Mock>, k: &Mock, access: HomeAccess) -> Process {
    prepare_at(r, k, access, 0, false)
}
fn prepare_at(
    r: &mut Runtime<Mock>,
    k: &Mock,
    access: HomeAccess,
    index: usize,
    rebind: bool,
) -> Process {
    let parent = Identity::admitted(1, 1, 0xb0000102).unwrap();
    let id = Identity::admitted((index + 1) as u32, 1, 0xb0000102 + index as u64).unwrap();
    let p = r
        .gate
        .admit(|f, _| {
            let p = f.admitted_shell(native(parent).unwrap(), 7).unwrap();
            assert_eq!(
                f.open_home_file(p, b"data", access, false),
                Ok(0),
                "OWNER_HOME_RIGHTS"
            );
            if index == 0 {
                p
            } else {
                f.inherited_child(p, native(id).unwrap(), parent.pid)
                    .unwrap()
            }
        })
        .unwrap();
    r.records[index] = Instance {
        identity: Some(id),
        epoch: 1,
        generation: 31,
        writer: 103,
        ..Instance::empty()
    };
    r.peers[index] = Some(
        Peer::bind(
            Framed(Endpoints::new(k.clone(), 102, 103).ok().unwrap()),
            p,
            31,
        )
        .unwrap(),
    );
    let mut request = header();
    if rebind {
        r.peers[index]
            .as_mut()
            .unwrap()
            .rebind_after_exec(p, 32)
            .unwrap();
        r.records[index].generation = 32;
        fs_put(&mut request, 2, 32);
    }
    k.0.borrow_mut().app = [request, data()].concat();
    p
}
#[test]
fn runtime_keeps_whole_file_event_before_error_and_never_overwrites_on_second_run() {
    for (status, limit, index, rebind) in [
        (0, None, 0, false),
        (0, Some(0), 0, false),
        (0, Some(64), 1, true),
        (-5, None, 1, true),
    ] {
        let k = kernel(packets(status));
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        let p = prepare_at(r, &k, HomeAccess::ReadWrite, index, rebind);
        k.0.borrow_mut().fail_send = limit;
        // Host fixture represents the admitted parent inside the once-only run.
        r.started = true;
        let mut w = [0xa5; 4096];
        let result = r.poll(index, &mut w);
        let event = r.last_file().expect("OWNER_FILE_RETENTION");
        assert_eq!(
            (event.index, event.identity, event.generation),
            (
                index,
                Identity::admitted((index + 1) as u32, 1, 0xb0000102 + index as u64).unwrap(),
                if rebind { 32 } else { 31 }
            ),
            "OWNER_NATIVE_CONTEXT"
        );
        let observation = event
            .event
            .exchange
            .observation
            .expect("OWNER_FILE_RETENTION");
        assert_eq!(observation.process, p);
        let expected_result = if status == 0 {
            filesystem_fd_protocol::FileWriteResult::Completed {
                offset: 0,
                completion: filesystem_client::MutationCompletion { txg: 1, bytes: 4 },
            }
        } else {
            filesystem_fd_protocol::FileWriteResult::Failed(
                filesystem_remote_descriptors::ProcessWriteFailure {
                    error: filesystem_remote_descriptors::ProcessError::Files(
                        filesystem_remote_descriptors::Failure::Source(FsError::Remote(-5)),
                    ),
                    outcome: filesystem_client::MutationOutcome::Reported(
                        filesystem_client::MutationProgress::Committed {
                            txg: 0,
                            bytes_staged: 4,
                        },
                    ),
                    cleanup: Some([-7, -8]),
                    offset: Some(0),
                },
            )
        };
        assert_eq!(
            observation.receipt,
            filesystem_fd_protocol::FileWriteReceipt {
                generation: if rebind { 32 } else { 31 },
                sequence: 1,
                fd: 0,
                requested: 4,
                result: expected_result
            },
            "OWNER_EXACT_RECEIPT"
        );
        if status == 0 && limit.is_none() {
            assert_eq!(result, Ok(true));
            assert_eq!(event.event.admission, Ok(()));
            assert_eq!(event.event.exchange.delivery, Ok(()));
        } else {
            assert!(result.is_err(), "OWNER_FILE_FAILSTOP");
            assert_eq!(
                event.event.admission,
                Err(if limit.is_some() {
                    fork_gate::GateError::Capture(-91)
                } else {
                    fork_gate::GateError::Closed
                }),
                "OWNER_FILE_ADMISSION"
            );
            assert_eq!(
                event.event.exchange.cleanup,
                Some([-9, -10]),
                "OWNER_FILE_CLOSES"
            );
            assert_eq!(r.gate.phase(), fork_gate::Phase::Retired);
        }
        if limit.is_some() {
            assert!(
                matches!(
                    event.event.exchange.delivery,
                    Err(fd_dispatch::Error::Transport(-91))
                ),
                "OWNER_FILE_DELIVERY"
            );
        }
        if status < 0 {
            assert!(
                matches!(observation.receipt.result,filesystem_fd_protocol::FileWriteResult::Failed(e) if matches!(e.outcome,filesystem_client::MutationOutcome::Reported(filesystem_client::MutationProgress::Committed{txg:0,bytes_staged:4}))),
                "OWNER_FILE_PROGRESS"
            );
        }
        assert_eq!(
            r.source_cleanup(),
            if status == 0 && limit.is_none() {
                None
            } else {
                Some([-7, -8])
            },
            "OWNER_SOURCE_CLEANUP"
        );
        let snapshot = std::format!("{:?}", r.last_file());
        let calls = k.0.borrow().controls;
        assert_eq!(r.run(&mut w), Err(Error::Protocol), "OWNER_ONCE_ONLY");
        assert_eq!(
            std::format!("{:?}", r.last_file()),
            snapshot,
            "OWNER_NO_OVERWRITE"
        );
        assert_eq!(k.0.borrow().controls, calls);
        assert!(w.iter().all(|b| *b == 0));
        // SAFETY: successful final-slot construction; all borrows ended.
        unsafe { g.slot.assume_init_drop() };
        assert_eq!((g.before, g.after), (17, 31));
    }
}
#[test]
fn typed_local_not_sent_keeps_owner_live_and_every_header_tail_loss_has_no_event() {
    let k = kernel(packets(0));
    let mut g = poisoned();
    let r =
        Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000).unwrap();
    prepare(r, &k, HomeAccess::ReadOnly);
    let mut w = [0; 4096];
    assert_eq!(r.poll(0, &mut w), Ok(true));
    let e = r.last_file().unwrap();
    assert_eq!(e.event.admission, Ok(()));
    assert!(
        matches!(e.event.exchange.observation.unwrap().receipt.result,filesystem_fd_protocol::FileWriteResult::Failed(e) if e.outcome==filesystem_client::MutationOutcome::NotSent)
    );
    assert_eq!(r.gate.phase(), fork_gate::Phase::Idle);
    // SAFETY: successful initialization; no returned references remain in use.
    unsafe { g.slot.assume_init_drop() };
    for at in [16, 32, 48] {
        let k = kernel(packets(0));
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        prepare(r, &k, HomeAccess::ReadWrite);
        k.0.borrow_mut().fail_read = Some(at);
        let mut w = [0xa5; 4096];
        assert!(r.poll(0, &mut w).is_err());
        assert!(r.last_file().is_none(), "OWNER_HEADER_BOUNDARY");
        assert_eq!(r.source_cleanup(), Some([-7, -8]), "OWNER_SOURCE_CLEANUP");
        assert_eq!(r.gate.phase(), fork_gate::Phase::Retired);
        assert_eq!(r.peers[0].as_ref().unwrap().cleanup(), Some([-9, -10]));
        assert!(w.iter().all(|b| *b == 0));
        let count =
            k.0.borrow()
                .source_sent
                .as_chunks::<64>()
                .0
                .iter()
                .filter(|f| f[..8] == filesystem_service::MAGIC[..] && fs_word(f, 1) == 11)
                .count();
        assert_eq!(count, 0, "OWNER_HEADER_NO_WRITE");
        // SAFETY: initialized slot despite the normal-return I/O failure.
        unsafe { g.slot.assume_init_drop() };
    }
}

#[test]
fn independent_admission_and_delivery_errors_are_retained_before_return() {
    // Synthetic independent statuses exercise the consumer contract directly;
    // they are not claimed as outcomes naturally emitted by the actual router.
    for failed_admission in [false, true] {
        let k = kernel(vec![greet(1), greet(2)]);
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        let id = Identity::admitted(2, 1, 0xb0000103).unwrap();
        let event = owner_dispatch::FileEvent {
            admission: if failed_admission {
                Err(fork_gate::GateError::Capture(-91))
            } else {
                Ok(())
            },
            exchange: fd_dispatch::Exchange {
                observation: None,
                delivery: if failed_admission {
                    Ok(())
                } else {
                    Err(fd_dispatch::Error::Transport(-92))
                },
                cleanup: Some([-9, -10]),
            },
        };
        assert_eq!(
            r.file_event(1, id, 32, event),
            Err(if failed_admission {
                Error::Gate
            } else {
                Error::Source
            }),
            "OWNER_INDEPENDENT_STATUS"
        );
        let retained = r.last_file().expect("OWNER_INDEPENDENT_RETAIN");
        assert_eq!(
            (retained.index, retained.identity, retained.generation),
            (1, id, 32)
        );
        assert_eq!(retained.event.exchange.cleanup, Some([-9, -10]));
        // SAFETY: successful final-slot construction, no remaining borrow.
        unsafe { g.slot.assume_init_drop() };
    }
}

// Use the production post-launch loop with actual FILE, child and stream ledgers.
// Only native facts are scripted; no alternate drain state is modeled here.
fn drain_fixture(r: &mut Runtime<Mock>, k: &Mock) -> Child {
    let process = prepare_at(r, k, HomeAccess::ReadWrite, 1, false);
    let parent = Identity::admitted(1, 1, 0xb0000102).unwrap();
    let id = r.records[1].id().unwrap();
    let parent_process = r
        .gate
        .admit(|files, _| files.current(native(parent).unwrap()).unwrap())
        .unwrap();
    assert_ne!(parent_process, process);
    r.records[0] = Instance {
        identity: Some(parent),
        generation: 30,
        writer: 105,
        ..Instance::empty()
    };
    r.peers[0] = Some(
        Peer::bind(
            Framed(Endpoints::new(k.clone(), 104, 105).ok().unwrap()),
            parent_process,
            30,
        )
        .unwrap(),
    );
    let child = child(id).unwrap();
    r.children.admit(child).unwrap();
    r.gate.admit(|_, streams| {
        let mut create = [0; 32];
        put(&mut create, 0, 82); put(&mut create, 4, 0x76050001); put(&mut create, 8, 1);
        assert!(matches!(streams.request(Caller::Parent, &create, |_, _| panic!("no console I/O")), Outcome::Reply(raw) if word(&raw,0)==0));
        let mut plan = Plan { identity: parent, shell: 1, parent: 7, generation: 30, bindings: [Binding::default();16], sources:[Source::default();7], history:[1,0] };
        for i in 0..5 {
            plan.bindings[i] = Binding { kind: if i<3 {1} else {2}, selector:i as u8, cloexec:0 };
            plan.sources[i] = Source { reference: if i<3 {0x7a000001 | (i as u32)<<16} else {0x79000100 | (i as u32-2)}, selector:i as u32, rights:if i==0 || i==3 {1} else {2}, bound:16 };
        }
        streams.stage_child(id.pid, &plan).unwrap();
        fork_gate::ForkStreams::child_ready(streams, id.pid).unwrap();
    }).unwrap();
    // Last shared FILE alias closes only after both native instances settle.
    // The preceding lookup consumed frame 3; settlement has no mutation reply.
    k.0.borrow_mut().source.truncate(192);
    k.0.borrow_mut().source.extend_from_slice(&message(77, 0));
    k.0.borrow_mut().drain = true;
    child
}
fn no_export(k: &Mock) {
    let s = k.0.borrow();
    assert!(
        s.source_sent
            .as_chunks::<64>()
            .0
            .iter()
            .all(|f| fs_word(f, 1) != 11 && fs_word(f, 1) != 4),
        "DRAIN_NO_PROVIDER_OR_EXPORT"
    );
    assert!(
        !s.operations
            .iter()
            .any(|(op, h)| *op == 0x24000 || *op == 0x2a002 || (*op == 0x20002 && *h == 99)),
        "DRAIN_NO_ALLOC_ENGINE_RECLAIM_HALT"
    );
}
#[test]
fn parent_terminal_cuts_off_queued_child_file_exec_fork_and_stream() {
    for request in 0..4 {
        let k = kernel(packets(0));
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        drain_fixture(r, &k);
        // These are unread queued bytes, not an already-consumed partial exchange.
        let bytes = match request {
            0 => [header(), data()].concat(),
            1 | 2 => {
                let plan = Plan {
                    identity: r.records[1].id().unwrap(),
                    shell: 1,
                    parent: 9,
                    generation: 31,
                    bindings: [Binding::default(); 16],
                    sources: [Source::default(); 7],
                    history: [0; 2],
                };
                let mut raw = [0; 304];
                fd_startup::encode(&plan, &mut raw).unwrap();
                raw[..8].copy_from_slice(if request == 1 {
                    exec_frames::MAGIC
                } else {
                    fork_frames::MAGIC
                });
                raw[8..12].copy_from_slice(&1u32.to_le_bytes());
                raw[12..16]
                    .copy_from_slice(&(if request == 1 { 608u32 } else { 304u32 }).to_le_bytes());
                raw[296..304].copy_from_slice(&1u64.to_le_bytes());
                if request == 1 {
                    let mut bytes = raw.to_vec();
                    bytes.resize(608, 0);
                    bytes[304..308].copy_from_slice(b"/bin");
                    bytes[336..344].copy_from_slice(&1u64.to_le_bytes());
                    bytes[352..354].copy_from_slice(b"sh");
                    bytes
                } else {
                    raw.to_vec()
                }
            }
            _ => {
                let mut f = [0; 32];
                put(&mut f, 0, 2);
                put(&mut f, 4, 0x79000102);
                put(&mut f, 8, 4);
                put(&mut f, 12, 1);
                f[16] = b'x';
                f.to_vec()
            }
        };
        k.0.borrow_mut().app = bytes;
        let result = r.run_session(&mut [0; 4096]).map(|_| ());
        assert_eq!(k.0.borrow().app_at, 0, "DRAIN_NO_CHILD_BYTES");
        assert_eq!(result, Ok(()), "DRAIN_CUTPOINT");
        assert!(k.0.borrow().app_sent.is_empty(), "DRAIN_NO_REPLY");
        assert!(r.last_file().is_none(), "DRAIN_NO_FILE_EVENT");
        no_export(&k);
        assert_eq!(k.0.borrow().reaped, [0xb0000103, 0xb0000102]);
        assert!(r.records.iter().all(|v| v.identity.is_none()));
        assert_eq!(r.gate.phase(), fork_gate::Phase::Idle);
        // SAFETY: successful final-slot initialization; all borrows have ended.
        unsafe { g.slot.assume_init_drop() };
    }
}
#[test]
fn pending_no_effect_read_and_reserved_wait_settle_then_retire_pipe() {
    for reserved in [false, true] {
        let k = kernel(packets(0));
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        let id = drain_fixture(r, &k);
        let mut read = [0; 32];
        put(&mut read, 0, 1);
        put(&mut read, 4, 0x79000101);
        put(&mut read, 8, 3);
        put(&mut read, 12, 1);
        k.0.borrow_mut().app = read.to_vec();
        assert_eq!(r.poll(1, &mut [0; 4096]), Ok(false));
        assert_eq!(r.records[1].pending, Some(read), "DRAIN_PENDING_NO_EFFECT");
        assert!(k.0.borrow().app_sent.is_empty());
        if reserved {
            // Actual terminal observation precedes reservation. The parent then
            // dies before its reserved wait receipt can be delivered.
            k.0.borrow_mut().stopped = true;
            assert_eq!(r.terminal(1), Ok(true));
            assert!(
                matches!(r.children.wait(-1,false),Ok(Wait::Ready {identity,..}) if identity==id)
            );
        }
        assert_eq!(
            r.run_session(&mut [0; 4096]).map(|_| ()),
            Ok(()),
            "DRAIN_SETTLEMENT"
        );
        assert_eq!(k.0.borrow().app_at, 32, "DRAIN_NO_PENDING_REPLAY");
        assert!(k.0.borrow().app_sent.is_empty(), "DRAIN_UNDELIVERABLE_WAIT");
        assert_eq!(r.children.wait(-1, false), Ok(Wait::NoChild));
        assert!(r.records.iter().all(|v| v.pending.is_none()));
        assert!(
            !r.gate
                .admit(|_, s| s.pipe_mut(0).unwrap().retire_if_idle([false; 4]))
                .unwrap(),
            "DRAIN_FINAL_PIPE_RETIRE"
        );
        no_export(&k);
        // SAFETY: successful final-slot initialization; all borrows have ended.
        unsafe { g.slot.assume_init_drop() };
    }
}
#[test]
fn failed_settlement_preserves_identity_pending_and_prevents_export() {
    for fault in 1..=4 {
        let k = kernel(packets(0));
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        drain_fixture(r, &k);
        r.records[1].pending = Some([0; 32]);
        k.0.borrow_mut().drain_fault = fault;
        assert!(
            r.run_session(&mut [0; 4096]).is_err(),
            "DRAIN_FAILURE_NOT_CLEAN"
        );
        assert!(
            r.records[0].identity.is_some() && r.records[1].identity.is_some(),
            "DRAIN_RETAIN_OBLIGATIONS"
        );
        if fault <= 2 {
            assert!(r.records[1].terminal.is_none());
            assert!(
                r.records[1].pending.is_some(),
                "DRAIN_STOP_ACK_NOT_TERMINAL"
            );
            assert!(
                !r.gate
                    .admit(|_, s| s.pipe_mut(0).unwrap().retire_if_idle([false; 4]))
                    .unwrap(),
                "DRAIN_HOLDERS_RETAINED"
            );
        }
        no_export(&k);
        assert!(k.0.borrow().reaped.is_empty());
        // SAFETY: successful initialization; failure preserves owned obligations.
        unsafe { g.slot.assume_init_drop() };
    }
}

#[test]
fn partial_exchange_and_unknown_mutation_cannot_become_clean_drain() {
    for partial in [false, true] {
        let mut frames = packets(0);
        if !partial {
            frames.truncate(3);
        }
        let k = kernel(frames);
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        drain_fixture(r, &k);
        if partial {
            k.0.borrow_mut().fail_read = Some(16);
        } else {
            k.0.borrow_mut().source.truncate(192);
        }
        assert!(
            r.poll(1, &mut [0; 4096]).is_err(),
            "DRAIN_PREEXISTING_FAILURE"
        );
        if partial {
            assert!(r.last_file().is_none());
        } else {
            let receipt = r
                .last_file()
                .unwrap()
                .event
                .exchange
                .observation
                .unwrap()
                .receipt;
            assert!(
                matches!(receipt.result,filesystem_fd_protocol::FileWriteResult::Failed(f) if f.outcome==filesystem_client::MutationOutcome::Unknown),
                "DRAIN_UNKNOWN_RETAINED"
            );
        }
        assert_eq!(r.gate.phase(), fork_gate::Phase::Retired);
        let retained = std::format!("{:?}", r.last_file());
        assert!(
            r.run_session(&mut [0; 4096]).is_err(),
            "DRAIN_RETIRED_NOT_GRACEFUL"
        );
        assert_eq!(std::format!("{:?}", r.last_file()), retained);
        assert!(r.records[0].identity.is_some() && r.records[1].identity.is_some());
        let s = k.0.borrow();
        assert!(s.reaped.is_empty());
        assert!(!s.operations.iter().any(|(op, _)| *op == 0x2a002));
        drop(s);
        // SAFETY: initialized slot; failure does not discharge native obligations.
        unsafe { g.slot.assume_init_drop() };
    }
}

#[test]
fn continuous_source_progress_cannot_outlive_fixed_drain_deadline() {
    let k = kernel(packets(0));
    let mut g = poisoned();
    let r =
        Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000).unwrap();
    drain_fixture(r, &k);
    k.0.borrow_mut().transfer_ticks = 150;
    assert!(
        r.run_session(&mut [0; 4096]).is_err(),
        "DRAIN_PROGRESS_DEADLINE"
    );
    assert_eq!(k.0.borrow().source_at, 192, "DRAIN_SOURCE_EXPIRED_IO");
    assert!(
        r.records[0].identity.is_some(),
        "DRAIN_EXPIRED_VIEW_RETAINED"
    );
    assert_eq!(r.engine, 99);
    assert!(
        !k.0.borrow()
            .operations
            .iter()
            .any(|(op, h)| *op == 0x2a002 || (*op == 0x20002 && *h == 99))
    );
    // SAFETY: initialized slot; expiry does not discharge remaining obligations.
    unsafe { g.slot.assume_init_drop() };
}

#[test]
fn source_wait_keeps_pretransfer_sequence_and_one_deadline_across_events() {
    let k = kernel(packets(0));
    let mut g = poisoned();
    let r =
        Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000).unwrap();
    drain_fixture(r, &k);
    k.0.borrow_mut().source_blocked = 2;
    k.0.borrow_mut().wake_ticks = 50;
    let d = r.run_session(&mut [0; 4096]).expect("DRAIN_EVENT_RACE");
    assert_eq!(d.get(), 500);
    assert_eq!(
        k.0.borrow().parks,
        [(0, 500), (1, 500)],
        "DRAIN_PRETRANSFER_SEQUENCE"
    );
    assert_eq!(k.0.borrow().source_at, 256);
    assert!(r.records.iter().all(|record| record.identity.is_none()));
    // SAFETY: initialized slot and no remaining loan.
    unsafe { g.slot.assume_init_drop() };
}
#[test]
fn repeated_wakes_cannot_renew_source_deadline_or_clear_failed_view() {
    let k = kernel(packets(0));
    let mut g = poisoned();
    let r =
        Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000).unwrap();
    drain_fixture(r, &k);
    k.0.borrow_mut().source_blocked = 3;
    k.0.borrow_mut().wake_ticks = 200;
    assert!(
        r.run_session(&mut [0; 4096]).is_err(),
        "DRAIN_FIXED_DEADLINE"
    );
    assert_eq!(
        k.0.borrow().parks,
        [(0, 500), (1, 500), (2, 500)],
        "DRAIN_NO_RENEWAL"
    );
    assert!(r.records[0].identity.is_some());
    assert_eq!(r.source_cleanup(), Some([0, 0]));
    assert_eq!(
        k.0.borrow()
            .closes
            .iter()
            .filter(|&&v| v == 100 || v == 101)
            .count(),
        2,
        "DRAIN_EXPIRED_CLOSES"
    );
    // SAFETY: initialized slot; unresolved FILE view remains a failed obligation.
    unsafe { g.slot.assume_init_drop() };
}
#[test]
fn source_adapter_rejects_error_aux_timeout_cancel_and_positive_observation() {
    for error in [-13, -110, -125, 1] {
        let k = kernel(vec![]);
        k.0.borrow_mut().drain = true;
        k.0.borrow_mut().observation_error = error;
        let mut io = DrainIo {
            endpoints: Endpoints::new(k.clone(), 100, 101).ok().unwrap(),
            observer: k.clone(),
            deadline: Some(Deadline::after(0, 500).unwrap()),
            sequence: 7,
        };
        assert_eq!(
            io.transfer(true, &mut [0; 16]),
            if error < 0 { error } else { -5 },
            "DRAIN_OBSERVATION_ERROR"
        );
        assert!(k.0.borrow().source_sent.is_empty());
        assert_eq!(io.close(), [0, 0]);
    }
    for status in [-110, -125] {
        let k = kernel(vec![]);
        k.0.borrow_mut().drain = true;
        k.0.borrow_mut().wake_status = status;
        let mut io = DrainIo {
            endpoints: Endpoints::new(k.clone(), 100, 101).ok().unwrap(),
            observer: k.clone(),
            deadline: Some(Deadline::after(0, 500).unwrap()),
            sequence: 7,
        };
        assert_eq!(io.wait(false), status, "DRAIN_WAKE_ERROR_AUX");
        assert_eq!(k.0.borrow().parks, [(7, 500)]);
        assert_eq!(io.close(), [0, 0]);
    }
}
#[test]
fn source_configuration_is_once_and_retired_callbacks_never_run() {
    let k = kernel(vec![greet(1), greet(2)]);
    let mut g = poisoned();
    let r =
        Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000).unwrap();
    k.0.borrow_mut().drain = true;
    assert_eq!(r.begin_drain().unwrap().get(), 500);
    assert_eq!(r.begin_drain(), Err(Error::Source), "DRAIN_NO_REARM");
    let mut called = false;
    r.gate
        .admit(|files, _| {
            files.abort();
            assert!(
                files
                    .configure_channel(|_| {
                        called = true;
                        Ok(())
                    })
                    .is_err()
            );
        })
        .unwrap();
    assert!(!called, "DRAIN_RETIRED_CONFIG");
    assert_eq!(r.gate.phase(), fork_gate::Phase::Retired);
    // SAFETY: successful construction; retirement closed both source endpoints.
    unsafe { g.slot.assume_init_drop() };
    let k = kernel(vec![greet(1), greet(2)]);
    let mut client = filesystem_client::Client::connect_home(source(&k), 77).unwrap();
    client.abort();
    assert_eq!(
        client.configure_channel(|_| {
            called = true;
            Ok(())
        }),
        Err(FsError::Closed)
    );
    assert!(!called, "DRAIN_CLOSED_CLIENT_CONFIG");
}
#[test]
fn child_stop_timeout_and_work_exhaustion_keep_pending_and_holders() {
    for exhausted in [false, true] {
        let k = kernel(packets(0));
        let mut g = poisoned();
        let r = Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000)
            .unwrap();
        drain_fixture(r, &k);
        r.records[1].pending = Some([0; 32]);
        k.0.borrow_mut().drain_fault = 1;
        if exhausted {
            r.remaining = 2;
        }
        assert_eq!(
            r.run_session(&mut [0; 4096]),
            Err(Error::Native(-110)),
            "DRAIN_STOP_OR_WORK_EXHAUSTION"
        );
        assert!(r.records[1].pending.is_some() && r.records[1].terminal.is_none());
        assert!(k.0.borrow().reaped.is_empty());
        if !exhausted {
            assert_eq!(k.0.borrow().parks, [(0, 500)]);
        }
        // SAFETY: initialized slot; no terminal proof or native reclaim is inferred.
        unsafe { g.slot.assume_init_drop() };
    }
}

#[test]
fn expiry_after_engine_stale_proof_keeps_known_settlement_without_halt() {
    let k = kernel(vec![greet(1), greet(2), message(77, 0)]);
    let mut g = poisoned();
    let r =
        Runtime::connect_home_in_place(&mut g.slot, k.clone(), 99, source(&k), 77, 5000).unwrap();
    {
        let mut s = k.0.borrow_mut();
        s.drain = true;
        s.engine_complete = true;
        s.expire_after_engine_proof = true;
    }
    let d = r.begin_drain().unwrap();
    assert_eq!(
        r.shutdown(d),
        Err(Error::Native(-110)),
        "DRAIN_POST_PROOF_EXPIRY"
    );
    assert_eq!(r.engine, 0, "DRAIN_KNOWN_ENGINE_SETTLED");
    assert_eq!(k.0.borrow().reaped, [99]);
    assert_eq!(r.source_cleanup(), Some([0, 0]));
    assert!(
        !k.0.borrow()
            .operations
            .iter()
            .any(|(op, _)| *op == 0x2a002 || *op == 0x26002)
    );
    // SAFETY: initialized slot; engine proof retained despite failed overall drain.
    unsafe { g.slot.assume_init_drop() };
}
