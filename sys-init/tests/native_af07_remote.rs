// SPDX-License-Identifier: BSD-2-Clause
//! Actual sealed remote-description library over sys-init's endpoint adapter.
use af07_transport::{Endpoints, Kernel};
use filesystem_client::Error;
use filesystem_remote_descriptors::{Descriptors, Failure};
use filesystem_service::{message, put, word};
use std::{cell::RefCell, rc::Rc};

#[derive(Default)]
struct Seen {
    sent: Vec<u8>,
    closed: Vec<u64>,
    calls: usize,
    waits: Vec<u64>,
}
struct Mock {
    seen: Rc<RefCell<Seen>>,
    input: Vec<u8>,
    offset: usize,
    limit: usize,
}
impl Mock {
    fn new() -> Self {
        let mut root = message(10, 0);
        put(&mut root, 3, 1);
        put(&mut root, 4, 1);
        let mut file = message(10, 0);
        put(&mut file, 3, 2);
        put(&mut file, 4, 2);
        put(&mut file, 5, 3);
        let mut two = message(10, 0);
        put(&mut two, 5, 2);
        let mut one = message(10, 0);
        put(&mut one, 5, 1);
        let mut ab = [0; 64];
        ab[..2].copy_from_slice(b"ab");
        let mut c = [0; 64];
        c[0] = b'c';
        Self {
            seen: Rc::default(),
            input: [root, file, two, ab, one, c, message(10, 0), message(10, 0)].concat(),
            offset: 0,
            limit: 512,
        }
    }
}
impl Kernel for Mock {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        assert_eq!(endpoint, if writing { 11 } else { 20 });
        assert!(!bytes.is_empty() && bytes.len() <= 16);
        let mut seen = self.seen.borrow_mut();
        seen.calls += 1;
        if seen.calls.is_multiple_of(3) {
            return -11;
        }
        let n = bytes.len().min(7);
        if writing {
            seen.sent.extend_from_slice(&bytes[..n]);
            n as i64
        } else {
            if self.offset >= self.limit {
                return -32;
            }
            let n = n.min(self.limit - self.offset);
            bytes[..n].copy_from_slice(&self.input[self.offset..self.offset + n]);
            self.offset += n;
            n as i64
        }
    }
    fn wait(&mut self, endpoint: u64) -> i64 {
        self.seen.borrow_mut().waits.push(endpoint);
        0
    }
    fn close(&mut self, endpoint: u64) -> i64 {
        self.seen.borrow_mut().closed.push(endpoint);
        if endpoint == 20 { -9 } else { -5 }
    }
}
fn connect(mock: Mock) -> Descriptors<filesystem_service::channel::Framed<Endpoints<Mock>>> {
    let endpoints = Endpoints::new(mock, 20, 11).unwrap_or_else(|_| panic!("endpoints"));
    Descriptors::connect(filesystem_service::channel::Framed(endpoints), 10)
        .unwrap_or_else(|e| panic!("{e:?}"))
}
#[test]
fn actual_remote_shared_offset_final_close_and_raw_disconnect_results() {
    let mock = Mock::new();
    let seen = mock.seen.clone();
    let mut fd = connect(mock);
    let first = fd.open_read(b"file", false).unwrap();
    let alias = fd.duplicate(first, 3, true).unwrap();
    assert_ne!(first, alias);
    let mut output = [9; 4096];
    assert_eq!(fd.read(first, 2, &mut output), Ok(2));
    assert_eq!(&output[..2], b"ab");
    assert!(output[2..].iter().all(|b| *b == 0));
    assert_eq!(fd.read(alias, 2, &mut output), Ok(1));
    assert_eq!(output[0], b'c');
    assert!(output[1..].iter().all(|b| *b == 0));
    let before = seen.borrow().sent.len();
    fd.close(first).unwrap();
    assert_eq!(seen.borrow().sent.len(), before);
    fd.close(alias).unwrap();
    assert_eq!(fd.disconnect(), Ok([-9, -5]));
    let seen = seen.borrow();
    assert_eq!(seen.closed, [20, 11]);
    assert!(seen.waits.contains(&20) && seen.waits.contains(&11));
    assert_eq!(seen.sent.len(), 6 * 64);
    for (frame, op) in [(0, 1), (2, 2), (3, 2), (4, 3), (5, 4)] {
        let f: &[u8; 64] = seen.sent[frame * 64..(frame + 1) * 64].try_into().unwrap();
        assert_eq!(word(f, 1), op);
        if op == 2 {
            assert_eq!(word(f, 3), 2);
            assert_eq!(word(f, 4), if frame == 2 { 0 } else { 2 });
        }
    }
}
#[test]
fn every_partial_remote_body_clears_dirty_output_and_never_replays() {
    for prefix in 0..64 {
        let mut mock = Mock::new();
        mock.limit = 192 + prefix;
        let seen = mock.seen.clone();
        let mut fd = connect(mock);
        let file = fd.open_read(b"file", false).unwrap();
        let mut output = [0xa5; 4096];
        assert_eq!(
            fd.read(file, 2, &mut output),
            Err(Failure::Source(Error::Transport(-32)))
        );
        assert!(output.iter().all(|b| *b == 0));
        assert_eq!(fd.cleanup(), Some([-9, -5]));
        let calls = seen.borrow().calls;
        output.fill(0xa5);
        assert_eq!(fd.read(file, 2, &mut output), Err(Failure::Retired));
        assert!(output.iter().all(|b| *b == 0));
        drop(fd);
        assert_eq!(seen.borrow().calls, calls);
        assert_eq!(seen.borrow().closed, [20, 11]);
        assert_eq!(seen.borrow().sent.len(), 3 * 64);
    }
}
