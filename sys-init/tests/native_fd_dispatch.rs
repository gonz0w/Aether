// SPDX-License-Identifier: BSD-2-Clause
use fd_dispatch::{Error, Peer};
use filesystem_fd_protocol::Error as ProtocolError;
use filesystem_remote_descriptors::NativeIdentity;
use filesystem_service::{Message, put, word};
use fixture::{Fault, Harness};
use std::{cell::RefCell, collections::VecDeque, rc::Rc};

#[derive(Default)]
struct Seen {
    received: usize,
    sent: Vec<Message>,
    closed: usize,
}
struct App {
    input: VecDeque<Message>,
    seen: Rc<RefCell<Seen>>,
    receive_fail: usize,
    send_fail: usize,
}
impl App {
    fn new(input: Vec<Message>) -> Self {
        Self {
            input: input.into(),
            seen: Rc::default(),
            receive_fail: usize::MAX,
            send_fail: usize::MAX,
        }
    }
}
impl Channel for App {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        let mut s = self.seen.borrow_mut();
        s.received += 1;
        if s.received == self.receive_fail {
            return Err(-32);
        }
        *out = self.input.pop_front().ok_or(-32)?;
        Ok(())
    }
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        let mut s = self.seen.borrow_mut();
        s.sent.push(*frame);
        if s.sent.len() == self.send_fail {
            Err(-32)
        } else {
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.borrow_mut().closed += 1;
        [-9, -5]
    }
}
fn identity() -> NativeIdentity {
    NativeIdentity::admitted(1, 1, 0xb0000102).unwrap()
}
fn request(op: u64, seq: u64, a: u64, b: u64) -> Message {
    let mut r = [0; 64];
    r[..8].copy_from_slice(fd_dispatch::MAGIC);
    for (i, v) in [op, 77, seq, a, b, 0, 0].into_iter().enumerate() {
        put(&mut r, i + 1, v);
    }
    r
}
fn name() -> Message {
    let mut n = [0; 64];
    n[..4].copy_from_slice(b"file");
    n
}
fn bind(h: &mut Harness, app: App) -> Peer<App> {
    let key = h
        .fds
        .as_mut()
        .unwrap()
        .admitted_shell(identity(), 7)
        .unwrap();
    Peer::bind(app, key, 77).unwrap_or_else(|e| panic!("{e:?}"))
}
#[test]
fn complete_delivery_advances_once_and_semantic_error_continues() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let app = App::new(vec![
        request(1, 1, 0, 4),
        name(),
        request(
            2,
            2,
            filesystem_remote_descriptors::FIRST_FILE_FD as u64,
            4096,
        ),
        request(77, 3, 0, 0),
        request(2, 4, filesystem_remote_descriptors::FIRST_FILE_FD as u64, 1),
    ]);
    let seen = app.seen.clone();
    let mut peer = bind(&mut h, app);
    let mut w = [0xa5; 4096];
    peer.serve_one(h.fds.as_mut().unwrap(), &mut w).unwrap();
    assert_eq!(
        word(&seen.borrow().sent[0], 4),
        filesystem_remote_descriptors::FIRST_FILE_FD as u64
    );
    assert!(w.iter().all(|b| *b == 0));
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), None);
    peer.serve_one(h.fds.as_mut().unwrap(), &mut w).unwrap();
    assert_eq!(word(&seen.borrow().sent[1], 4), 6);
    assert_eq!(seen.borrow().sent.len(), 3);
    assert_eq!(&seen.borrow().sent[2][..6], b"abcdef");
    assert!(w.iter().all(|b| *b == 0));
    peer.serve_one(h.fds.as_mut().unwrap(), &mut w).unwrap();
    assert_eq!(word(&seen.borrow().sent[3], 1) as i64, -38);
    peer.serve_one(h.fds.as_mut().unwrap(), &mut w).unwrap();
    assert_eq!(word(&seen.borrow().sent[4], 3), 4);
    assert_eq!(word(&seen.borrow().sent[4], 4), 0);
    assert_eq!(peer.close(), [-9, -5]);
    drop(peer);
    assert_eq!(seen.borrow().closed, 1);
    assert_eq!(h.opcodes(), [1, 2, 2]);
}
#[test]
fn lost_header_or_body_reply_retires_without_replay_or_sequence_reuse() {
    for failed in 2..=3 {
        let mut h = Harness::new(Fault::None, [-5, -9]);
        let mut app = App::new(vec![
            request(1, 1, 0, 4),
            name(),
            request(
                2,
                2,
                filesystem_remote_descriptors::FIRST_FILE_FD as u64,
                4096,
            ),
            request(
                2,
                2,
                filesystem_remote_descriptors::FIRST_FILE_FD as u64,
                4096,
            ),
        ]);
        app.send_fail = failed;
        let seen = app.seen.clone();
        let mut peer = bind(&mut h, app);
        let mut w = [0xa5; 4096];
        peer.serve_one(h.fds.as_mut().unwrap(), &mut w).unwrap();
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut w),
            Err(Error::Transport(-32))
        );
        assert!(w.iter().all(|b| *b == 0));
        assert_eq!(peer.cleanup(), Some([-9, -5]));
        assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([-5, -9]));
        let count = seen.borrow().received;
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut w),
            Err(Error::Closed)
        );
        assert_eq!(seen.borrow().received, count);
        assert_eq!(h.storage.lock().unwrap().reads, 1);
        drop(peer);
        assert_eq!(seen.borrow().closed, 1);
    }
}
#[test]
fn partial_input_and_bad_padding_never_dispatch_lookup() {
    for failure in 1..=3 {
        let mut h = Harness::new(Fault::None, [0; 2]);
        let mut n = name();
        if failure == 3 {
            n[63] = 1;
        }
        let mut app = App::new(vec![request(1, 1, 0, 4), n]);
        if failure < 3 {
            app.receive_fail = failure;
        }
        let seen = app.seen.clone();
        let mut peer = bind(&mut h, app);
        let mut w = [0xa5; 4096];
        assert!(peer.serve_one(h.fds.as_mut().unwrap(), &mut w).is_err());
        assert!(w.iter().all(|b| *b == 0));
        assert_eq!(h.storage.lock().unwrap().lookups, 0);
        assert!(seen.borrow().sent.is_empty());
        assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([0; 2]));
        drop(peer);
        assert_eq!(seen.borrow().closed, 1);
    }
}
#[test]
fn stale_process_rejects_even_unknown_opcode_and_bad_bind_closes() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let key = h
        .fds
        .as_mut()
        .unwrap()
        .admitted_shell(identity(), 7)
        .unwrap();
    let app = App::new(vec![]);
    let seen = app.seen.clone();
    let bad = Peer::bind(app, key, 0);
    assert!(bad.is_err());
    assert_eq!(seen.borrow().closed, 1);
    let app = App::new(vec![request(77, 1, 0, 0)]);
    let seen = app.seen.clone();
    let mut peer = Peer::bind(app, key, 77).unwrap_or_else(|e| panic!("{e:?}"));
    h.fds.as_mut().unwrap().settled(key).unwrap();
    let mut w = [0xa5; 4096];
    assert_eq!(
        peer.serve_one(h.fds.as_mut().unwrap(), &mut w),
        Err(Error::Protocol(ProtocolError::Retired))
    );
    assert!(seen.borrow().sent.is_empty());
    assert!(w.iter().all(|b| *b == 0));
}

#[test]
fn backend_partial_body_bad_count_and_failed_close_retire_the_peer() {
    for fault in [Fault::ReadBody, Fault::Count, Fault::Close] {
        let mut h = Harness::new(fault, [0; 2]);
        let mut input = vec![request(1, 1, 0, 4), name()];
        input.push(if fault == Fault::Close {
            request(5, 2, filesystem_remote_descriptors::FIRST_FILE_FD as u64, 0)
        } else {
            request(2, 2, filesystem_remote_descriptors::FIRST_FILE_FD as u64, 6)
        });
        let app = App::new(input);
        let seen = app.seen.clone();
        let mut peer = bind(&mut h, app);
        let mut w = [0xa5; 4096];
        peer.serve_one(h.fds.as_mut().unwrap(), &mut w).unwrap();
        assert!(peer.serve_one(h.fds.as_mut().unwrap(), &mut w).is_err());
        assert!(w.iter().all(|b| *b == 0));
        assert_eq!(seen.borrow().sent.len(), 1);
        assert_eq!(h.local.lock().unwrap().closes, 1);
        drop(peer);
        assert_eq!(seen.borrow().closed, 1);
    }
}
