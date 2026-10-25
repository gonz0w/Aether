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
}
#[derive(Clone)]
struct Mock(Rc<RefCell<Seen>>);
impl af07_transport::Kernel for Mock {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        let mut s = self.0.borrow_mut();
        if writing {
            if endpoint == 101 {
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
                return -32;
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
    fn ctl(&mut self, op: u64, _: u64, _: u64) -> owner_control::Status {
        self.0.borrow_mut().controls += 1;
        if op == 0x20001 {
            (0, 0, 0)
        } else {
            (-95, 0, 0)
        }
    }
    fn engine(&mut self, _: u64, _: u64) -> i64 {
        -95
    }
    fn delegate(&mut self, _: u64, _: &[u64; 3]) -> i64 {
        -95
    }
    fn launch(&mut self, _: &[u8; 272], _: u64, _: u64) -> i64 {
        -95
    }
    fn copy(&mut self, _: u64, _: u32, _: u64, _: u64, _: u64) -> i64 {
        -95
    }
    fn serial(&mut self, _: bool, _: &mut [u8]) -> i64 {
        -95
    }
    fn exec(&mut self, _: u64, _: u64, _: &[u8; 272]) -> i64 {
        -95
    }
    fn receipt(&mut self, _: u64) -> owner_control::Status {
        (-95, 0, 0)
    }
    fn publish(&mut self, _: u64, _: u64) -> i64 {
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
