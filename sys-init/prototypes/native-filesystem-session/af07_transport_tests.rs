// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_client::{Client, Error};
use filesystem_service::{channel::Framed, message, put};
use std::{cell::RefCell, rc::Rc, vec::Vec};

#[derive(Default)]
struct Seen {
    reads: usize,
    writes: usize,
    waits: Vec<u64>,
    closed: Vec<u64>,
    output: Vec<u8>,
}
struct Mock {
    seen: Rc<RefCell<Seen>>,
    input: Vec<u8>,
    offset: usize,
    read_limit: usize,
    write_limit: usize,
    wait_result: i64,
    never_ready: bool,
    close_results: [i64; 2],
}
impl Mock {
    fn new() -> Self {
        let mut greeting = message(10, 0);
        put(&mut greeting, 3, 1);
        put(&mut greeting, 4, 1);
        Self {
            seen: Rc::default(),
            input: [greeting, message(10, 0)].concat(),
            offset: 0,
            read_limit: 128,
            write_limit: 64,
            wait_result: 0,
            never_ready: false,
            close_results: [0, 0],
        }
    }
}
impl Kernel for Mock {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        assert_eq!(endpoint, if writing { 11 } else { 20 });
        assert!(!bytes.is_empty() && bytes.len() <= 16);
        let mut seen = self.seen.borrow_mut();
        let calls = if writing {
            &mut seen.writes
        } else {
            &mut seen.reads
        };
        *calls += 1;
        if self.never_ready || *calls == 1 {
            return -11;
        }
        if writing {
            if seen.output.len() >= self.write_limit {
                return -32;
            }
            let count = bytes.len().min(7).min(self.write_limit - seen.output.len());
            seen.output.extend_from_slice(&bytes[..count]);
            count as i64
        } else {
            if self.offset >= self.read_limit {
                return -32;
            }
            let count = bytes.len().min(7).min(self.read_limit - self.offset);
            bytes[..count].copy_from_slice(&self.input[self.offset..self.offset + count]);
            self.offset += count;
            count as i64
        }
    }
    fn wait(&mut self, endpoint: u64) -> i64 {
        self.seen.borrow_mut().waits.push(endpoint);
        self.wait_result
    }
    fn close(&mut self, endpoint: u64) -> i64 {
        self.seen.borrow_mut().closed.push(endpoint);
        self.close_results[usize::from(endpoint == 11)]
    }
}
fn endpoints(mock: Mock) -> Endpoints<Mock> {
    Endpoints::new(mock, 20, 11).unwrap_or_else(|_| panic!("valid endpoints rejected"))
}

#[test]
fn actual_client_short_wait_and_acknowledged_disconnect() {
    let mock = Mock::new();
    let seen = mock.seen.clone();
    let mut client =
        Client::connect(Framed(endpoints(mock)), 10, 3).unwrap_or_else(|e| panic!("{e:?}"));
    assert!(client.root().is_ok());
    assert_eq!(client.disconnect(), Ok([0, 0]));
    assert_eq!(client.cleanup(), Some([0, 0]));
    assert_eq!(client.root(), Err(Error::Closed));
    drop(client);
    let seen = seen.borrow();
    assert_eq!(seen.waits, [20, 11]);
    assert_eq!(seen.closed, [20, 11]);
    let mut expected = message(10, 4);
    put(&mut expected, 3, 0);
    assert_eq!(seen.output, expected);
}

#[test]
fn every_partial_greeting_retires_once_with_both_close_results() {
    for prefix in 0..64 {
        let mut mock = Mock::new();
        mock.read_limit = prefix;
        mock.close_results = [-9, -5];
        let seen = mock.seen.clone();
        let failed = match Client::connect(Framed(endpoints(mock)), 10, 3) {
            Ok(_) => panic!("partial greeting admitted"),
            Err(failed) => failed,
        };
        assert_eq!(failed.error, Error::Transport(-32));
        assert_eq!(failed.cleanup, [-9, -5]);
        assert_eq!(seen.borrow().closed, [20, 11]);
        assert!(seen.borrow().output.is_empty());
    }
}

#[test]
fn every_partial_disconnect_and_malformed_reply_never_replay() {
    for prefix in 0..64 {
        let mut mock = Mock::new();
        mock.write_limit = prefix;
        let seen = mock.seen.clone();
        let mut client =
            Client::connect(Framed(endpoints(mock)), 10, 3).unwrap_or_else(|e| panic!("{e:?}"));
        assert_eq!(client.disconnect(), Err(Error::Transport(-32)));
        assert_eq!(client.cleanup(), Some([0, 0]));
        let calls = seen.borrow().writes;
        assert_eq!(client.disconnect(), Err(Error::Closed));
        drop(client);
        assert_eq!(seen.borrow().writes, calls);
        assert_eq!(seen.borrow().output.len(), prefix);
        assert_eq!(seen.borrow().closed, [20, 11]);
    }
    let mut mock = Mock::new();
    mock.input[64 + 16] ^= 1;
    let seen = mock.seen.clone();
    let mut client =
        Client::connect(Framed(endpoints(mock)), 10, 3).unwrap_or_else(|e| panic!("{e:?}"));
    assert_eq!(client.disconnect(), Err(Error::Protocol));
    assert_eq!(client.root(), Err(Error::Closed));
    drop(client);
    assert_eq!(seen.borrow().closed, [20, 11]);
    assert_eq!(seen.borrow().output.len(), 64);
}

#[test]
fn failed_wait_exhaustion_bad_rights_and_old_greeting_fail_closed() {
    for result in [-125, 1] {
        let mut mock = Mock::new();
        mock.wait_result = result;
        let seen = mock.seen.clone();
        let failed = match Client::connect(Framed(endpoints(mock)), 10, 3) {
            Ok(_) => panic!("failed wait admitted"),
            Err(e) => e,
        };
        assert_eq!(
            failed.error,
            Error::Transport(if result < 0 { result } else { -5 })
        );
        assert_eq!(seen.borrow().reads, 1);
        assert_eq!(seen.borrow().waits, [20]);
        assert_eq!(seen.borrow().closed, [20, 11]);
    }
    let mut mock = Mock::new();
    mock.never_ready = true;
    let seen = mock.seen.clone();
    let failed = match Client::connect(Framed(endpoints(mock)), 10, 3) {
        Ok(_) => panic!("exhaustion admitted"),
        Err(e) => e,
    };
    assert_eq!(failed.error, Error::Transport(-110));
    assert_eq!(seen.borrow().reads, 100_000);
    assert_eq!(seen.borrow().waits.len(), 100_000);
    assert_eq!(seen.borrow().closed, [20, 11]);
    for bad_rights in [0, 4] {
        let mock = Mock::new();
        let seen = mock.seen.clone();
        assert!(Client::connect(Framed(endpoints(mock)), 10, bad_rights).is_err());
        assert_eq!(seen.borrow().reads, 0);
        assert_eq!(seen.borrow().closed, [20, 11]);
    }
    let mut mock = Mock::new();
    mock.input[7] = b'6';
    let seen = mock.seen.clone();
    assert!(Client::connect(Framed(endpoints(mock)), 10, 3).is_err());
    assert_eq!(seen.borrow().closed, [20, 11]);
}

#[test]
fn failed_local_close_is_preserved_and_bare_drop_attempts_both_once() {
    let mut mock = Mock::new();
    mock.close_results = [-9, -5];
    let seen = mock.seen.clone();
    let mut client =
        Client::connect(Framed(endpoints(mock)), 10, 3).unwrap_or_else(|e| panic!("{e:?}"));
    assert_eq!(client.disconnect(), Ok([-9, -5])); // Ack alone is not local cleanup.
    assert_eq!(client.cleanup(), Some([-9, -5]));
    drop(client);
    assert_eq!(seen.borrow().closed, [20, 11]);
    let mock = Mock::new();
    let seen = mock.seen.clone();
    drop(endpoints(mock));
    assert_eq!(seen.borrow().closed, [20, 11]);
}

#[test]
fn shape_rejection_local_bounds_and_closed_io_have_no_effect() {
    for (reader, writer) in [(0, 11), (20, 0), (20, 20)] {
        let mock = Mock::new();
        let seen = mock.seen.clone();
        assert!(Endpoints::new(mock, reader, writer).is_err());
        assert!(seen.borrow().closed.is_empty());
    }
    let mock = Mock::new();
    let seen = mock.seen.clone();
    let mut ends = endpoints(mock);
    assert_eq!(ends.transfer(false, &mut []), -22);
    assert_eq!(ends.transfer(true, &mut [0; 17]), -22);
    assert_eq!(ends.close(), [0, 0]);
    assert_eq!(ends.close(), [0, 0]);
    assert_eq!(ends.cleanup(), Some([0, 0]));
    assert_eq!(ends.transfer(false, &mut [0]), -9);
    assert_eq!(ends.wait(true), -9);
    drop(ends);
    assert_eq!(seen.borrow().reads + seen.borrow().writes, 0);
    assert!(seen.borrow().waits.is_empty());
    assert_eq!(seen.borrow().closed, [20, 11]);
}
