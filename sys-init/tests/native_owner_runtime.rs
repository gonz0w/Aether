// SPDX-License-Identifier: BSD-2-Clause
use af07_transport::{Endpoints, Kernel};
use core::mem::MaybeUninit;
use filesystem_service::{channel::Framed, message, put};
use owner_control::{Control, Status};
use owner_runtime::{Error, Runtime, provision};
use std::{cell::RefCell, rc::Rc};

#[derive(Default)]
struct Seen {
    events: Vec<(u64, u64)>,
    channels: u64,
    incoming: Vec<u8>,
    at: usize,
    startup: Vec<u8>,
    requests: Vec<u8>,
    reaped: Vec<u64>,
    engine_state: Status,
    eof: i64,
    epipe: i64,
    bad_launch: bool,
    bad_close: bool,
    ready_seen: bool,
}
#[derive(Clone)]
struct Mock(Rc<RefCell<Seen>>);
impl Kernel for Mock {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        assert!(!bytes.is_empty() && bytes.len() <= 16);
        let mut s = self.0.borrow_mut();
        s.events
            .push((if writing { 0x24002 } else { 0x24001 }, endpoint));
        if writing {
            if endpoint == 101 {
                if s.at == 128 {
                    return s.epipe;
                }
                s.requests.extend_from_slice(bytes);
            } else {
                assert_eq!(endpoint, 11);
                s.startup.extend_from_slice(bytes);
            }
            return bytes.len() as i64;
        }
        assert_eq!(endpoint, 100);
        if s.at == s.incoming.len() {
            return s.eof;
        }
        let n = bytes.len().min(s.incoming.len() - s.at);
        bytes[..n].copy_from_slice(&s.incoming[s.at..s.at + n]);
        s.at += n;
        n as i64
    }
    fn wait(&mut self, _: u64) -> i64 {
        panic!("immediate fixture must not wait on a channel")
    }
    fn close(&mut self, endpoint: u64) -> i64 {
        let mut s = self.0.borrow_mut();
        s.events.push((0x24003, endpoint));
        if s.bad_close && endpoint == 12 { -9 } else { 0 }
    }
}
impl Control for Mock {
    fn exec(&mut self, _: u64, _: u64, _: &[u8; 272]) -> i64 {
        panic!("no exec in immediate fixture")
    }
    fn receipt(&mut self, _: u64) -> Status {
        panic!("no receipt in immediate fixture")
    }
    fn publish(&mut self, _: u64, _: u64) -> i64 {
        panic!("no publish in immediate fixture")
    }
    fn ctl(&mut self, op: u64, handle: u64, argument: u64) -> Status {
        let mut s = self.0.borrow_mut();
        s.events.push((op, handle));
        assert_eq!(argument, 0);
        match op {
            0x24000 => {
                s.channels += 1;
                let n = 8 + 2 * s.channels;
                (n as i64, n + 1, 0)
            }
            0x20001 if s.reaped.contains(&handle) => (-9, 0, 0),
            0x20001 if handle == 0xb0000101 => {
                if s.at == 128 {
                    (1, 1, 1)
                } else {
                    s.engine_state
                }
            }
            0x20001 if handle == 0xb0000102 => {
                if !s.ready_seen && s.startup.len() == 304 {
                    s.ready_seen = true;
                    (0, 1, 0)
                } else {
                    (1, 0, 1)
                }
            }
            0x20002 => {
                s.reaped.push(handle);
                (0, 0, 0)
            }
            0x2a000 => (0, 77, 0),
            0x1fffe | 0x26002 | 0x2a002 => (0, 0, 0),
            _ => panic!("unexpected native operation {op:x}"),
        }
    }
    fn engine(&mut self, reader: u64, writer: u64) -> i64 {
        assert_eq!((reader, writer), (10, 13));
        self.0.borrow_mut().events.push((0x20008, reader));
        0xb0000101
    }
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64 {
        assert_eq!((engine, *region), (0xb0000101, [8, 2097152, 7]));
        self.0.borrow_mut().events.push((0x27005, engine));
        0
    }
    fn launch(&mut self, args: &[u8; 272], reader: u64, writer: u64) -> i64 {
        assert_eq!((reader, writer), (10, 13));
        assert_eq!(args[0], 1);
        assert_eq!(&args[16..18], b"sh");
        let mut s = self.0.borrow_mut();
        s.events.push((0x23002, reader));
        if s.bad_launch { -13 } else { 0xb0000102 }
    }
    fn copy(&mut self, _: u64, _: u32, _: u64, _: u64, _: u64) -> i64 {
        panic!("no copy in immediate-exit fixture")
    }
    fn serial(&mut self, _: bool, _: &mut [u8]) -> i64 {
        panic!("no serial request in immediate-exit fixture")
    }
}
fn setup() -> Mock {
    let mut greeting = message(77, 0);
    put(&mut greeting, 3, 1);
    put(&mut greeting, 4, 1);
    let mut incoming = greeting.to_vec();
    incoming.extend_from_slice(&message(77, 0));
    Mock(Rc::new(RefCell::new(Seen {
        incoming,
        engine_state: (0, 1, 0),
        eof: 0,
        epipe: -32,
        ..Seen::default()
    })))
}

#[test]
fn concrete_owner_orders_startup_settlement_export_proof_and_native_reclaim() {
    for failure in 0..5 {
        let kernel = setup();
        {
            let mut s = kernel.0.borrow_mut();
            match failure {
                1 => s.eof = -11,
                2 => s.epipe = 0,
                3 => {
                    s.incoming[88] = 1;
                }
                4 => s.bad_close = true,
                _ => {}
            }
        }
        let mut slot = MaybeUninit::uninit();
        let channel = Framed(Endpoints::new(kernel.clone(), 100, 101).ok().unwrap());
        let owner =
            Runtime::connect_in_place(&mut slot, kernel.clone(), 0xb0000101, channel, 77, 10000)
                .ok()
                .unwrap();
        let mut workspace = [0; 4096];
        let result = owner.run(&mut workspace);
        let events = kernel.0.borrow().events.clone();
        if failure == 0 {
            assert_eq!(result, Err(Error::ReturnedHalt));
            let s = kernel.0.borrow();
            assert_eq!(s.startup.len(), 304);
            assert_eq!(&s.startup[..8], fd_startup::MAGIC);
            assert_eq!(s.requests.len(), 64);
            assert_eq!(u64::from_le_bytes(s.requests[8..16].try_into().unwrap()), 4);
            assert_eq!(s.reaped, [0xb0000102, 0xb0000101]);
            assert_eq!(
                &events[events.len() - 2..],
                &[(0x26002, 0xf001), (0x2a002, 0xf002)]
            );
        } else {
            assert!(result.is_err());
            assert!(!events.iter().any(|(op, _)| *op == 0x2a002));
            assert!(!kernel.0.borrow().reaped.contains(&0xb0000101));
        }
        assert_eq!(owner.run(&mut workspace), Err(Error::Protocol));
        assert_eq!(kernel.0.borrow().events, events); // no retry or second launch
        assert!(workspace.iter().all(|b| *b == 0));
        let before_drop = kernel.0.borrow().events.clone();
        // SAFETY: successful final-slot initialization, no outstanding owner borrow.
        unsafe { slot.assume_init_drop() };
        assert_eq!(kernel.0.borrow().events, before_drop);
        let position = |event| events.iter().position(|e| *e == event).unwrap();
        assert!(position((0x24003, 12)) < position((0x24003, 11)));
        if failure != 4 {
            assert!(position((0x20002, 0xb0000102)) < position((0x24003, 100)));
            assert!(position((0x24003, 100)) < position((0x24003, 101)));
        }
    }
}

#[test]
fn provisioning_observes_actual_ready_and_exhausts_one_shared_budget() {
    for state in [(0, 1, 0), (0, 0, 0), (1, 1, 1), (0, 2, 0), (-9, 0, 0)] {
        let mut kernel = setup();
        kernel.0.borrow_mut().engine_state = state;
        let mut remaining = 3;
        let result = provision(&mut kernel, &mut remaining);
        if state == (0, 1, 0) {
            assert_eq!(result, Ok((0xb0000101, [10, 11, 12, 13])));
            assert_eq!(remaining, 2);
        } else {
            assert!(result.is_err());
            if state == (0, 0, 0) {
                assert_eq!(result, Err(Error::Native(-110)));
                assert_eq!(remaining, 0);
            }
        }
        let s = kernel.0.borrow();
        assert_eq!(
            &s.events[..4],
            &[
                (0x24000, 0xd002),
                (0x24000, 0xd002),
                (0x20008, 10),
                (0x27005, 0xb0000101)
            ]
        );
        assert!(
            !s.events
                .iter()
                .any(|(op, _)| matches!(op, 0x24003 | 0x20002 | 0x23002))
        );
    }
}

#[test]
fn failed_initial_launch_is_not_replayed_or_reported_reclaimed() {
    let kernel = setup();
    kernel.0.borrow_mut().bad_launch = true;
    let mut slot = MaybeUninit::uninit();
    let channel = Framed(Endpoints::new(kernel.clone(), 100, 101).ok().unwrap());
    let owner = Runtime::connect_in_place(&mut slot, kernel.clone(), 0xb0000101, channel, 77, 1000)
        .ok()
        .unwrap();
    assert_eq!(owner.run(&mut [0; 4096]), Err(Error::Native(-13)));
    let events = kernel.0.borrow().events.clone();
    assert_eq!(owner.run(&mut [0; 4096]), Err(Error::Protocol));
    assert_eq!(events, kernel.0.borrow().events);
    assert!(kernel.0.borrow().reaped.is_empty());
    // SAFETY: successful initialization, owner borrow ends, sole drop.
    unsafe { slot.assume_init_drop() };
}
