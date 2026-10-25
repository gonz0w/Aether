// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_policy::{Completion, Lost, Node, Utc};
use std::{cell::RefCell, collections::VecDeque, rc::Rc, vec, vec::Vec};

#[derive(Default)]
struct State {
    bytes: Vec<u8>,
    writes: usize,
    lookups: usize,
    reads: usize,
    drops: usize,
    sent: Vec<Message>,
    closes: usize,
    failure: Option<Result<Completion, Lost>>,
}
struct Provider(Rc<RefCell<State>>);
impl Drop for Provider {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
impl Backend for Provider {
    fn root(&mut self) -> Result<Node, Error> {
        Ok(Node::new(34, 45, 0, Kind::Directory))
    }
    fn lookup(&mut self, _: Node, name: &[u8]) -> Result<Node, Error> {
        let mut s = self.0.borrow_mut();
        s.lookups += 1;
        if name != b"file" {
            return Err(Error::Backend(2));
        }
        Ok(Node::new(2, 47, s.bytes.len() as u64, Kind::File))
    }
    fn read(&mut self, _: Node, offset: u64, bytes: &mut [u8]) -> Result<usize, Error> {
        let mut s = self.0.borrow_mut();
        s.reads += 1;
        let start = offset.min(s.bytes.len() as u64) as usize;
        let count = bytes.len().min(s.bytes.len() - start);
        bytes[..count].copy_from_slice(&s.bytes[start..start + count]);
        Ok(count)
    }
    fn write(&mut self, _: Node, offset: u64, bytes: &[u8], _: Utc) -> Result<Completion, Lost> {
        let mut s = self.0.borrow_mut();
        s.writes += 1;
        if let Some(failure) = s.failure {
            return failure;
        }
        let end = offset as usize + bytes.len();
        if s.bytes.len() < end {
            s.bytes.resize(end, 0);
        }
        s.bytes[offset as usize..end].copy_from_slice(bytes);
        Ok(Completion {
            error: 0,
            txg: 788,
            bytes_staged: bytes.len() as u64,
            state: 2,
        })
    }
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> Result<Utc, Error> {
        Ok(Utc {
            seconds: 1791290040,
            nanoseconds: 0,
        })
    }
}
struct Transport {
    state: Rc<RefCell<State>>,
    incoming: VecDeque<Message>,
    fail_send: usize,
    cleanup: [i64; 2],
}
impl Channel for Transport {
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        match self.incoming.pop_front() {
            Some(value) => {
                *frame = value;
                Ok(())
            }
            None => Err(-32),
        }
    }
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        let mut s = self.state.borrow_mut();
        s.sent.push(*frame);
        if s.sent.len() == self.fail_send {
            Err(-32)
        } else {
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        let mut s = self.state.borrow_mut();
        assert_eq!(s.drops, 1);
        s.closes += 1;
        self.cleanup
    }
}
fn setup(
    frames: Vec<Message>,
    fail_send: usize,
) -> (Owner<Provider, Time>, Transport, Rc<RefCell<State>>) {
    let state = Rc::new(RefCell::new(State {
        bytes: b"abcd".to_vec(),
        ..State::default()
    }));
    (
        Owner::new(Provider(state.clone()), Time, 71).unwrap(),
        Transport {
            state: state.clone(),
            incoming: frames.into(),
            fail_send,
            cleanup: [0, 0],
        },
        state,
    )
}
fn request(op: u64, token: u64, arg: u64, count: u64, bytes: &[u8]) -> Message {
    let mut m = message(71, op);
    put(&mut m, 3, token);
    put(&mut m, 4, arg);
    put(&mut m, 5, count);
    m[48..48 + bytes.len()].copy_from_slice(bytes);
    m
}
fn lookup(rights: u64) -> Message {
    request(1, 1, rights, 4, b"file")
}
fn disconnect() -> Message {
    message(71, 4)
}
fn status(m: &Message) -> i64 {
    word(m, 1) as i64
}

#[test]
fn ready_write_alias_eof_and_shutdown() {
    let frames = vec![
        lookup(7),
        lookup(2),
        request(5, 2, 4, 2, b"EF"),
        request(2, 3, 0, 16, b""),
        request(6, 3, 0, 0, b""),
        request(2, 3, 6, 16, b""),
        request(5, 2, 0, 1, b"X"),
        disconnect(),
    ];
    let (o, t, s) = setup(frames, 0);
    let r = run(o, t, 71, Rights::ALL, 71);
    assert_eq!(r.stop, Stop::Disconnected);
    assert!(r.ready);
    assert_eq!(r.requests, 8);
    assert_eq!(r.cleanup, [0, 0]);
    let s = s.borrow();
    assert_eq!(s.writes, 1);
    assert_eq!(s.drops, 1);
    assert_eq!(s.closes, 1);
    let mut greeting = message(71, 0);
    put(&mut greeting, 3, 1);
    put(&mut greeting, 4, 1);
    assert_eq!(s.sent[0], greeting);
    assert_eq!(word(&s.sent[3], 4), 788);
    assert_eq!(word(&s.sent[3], 6), 2);
    assert_eq!(&s.sent[4][48..54], b"abcdEF");
    assert!(s.sent[4][54..].iter().all(|b| *b == 0));
    assert_eq!(word(&s.sent[5], 5), 6);
    assert!(s.sent[6][24..].iter().all(|b| *b == 0));
    assert_eq!(status(&s.sent[7]), -28);
}

#[test]
fn authority_version_stale_and_reserved_fields_have_no_effect() {
    let mut wrong_version = lookup(7);
    wrong_version[0] ^= 1;
    let mut stale = lookup(7);
    put(&mut stale, 2, 70);
    let mut padding = lookup(7);
    padding[63] = 1;
    let frames = vec![
        wrong_version,
        stale,
        padding,
        lookup(8),
        lookup(7),
        request(5, 999, 0, 1, b"X"),
        request(5, 1, 0, 1, b"X"),
        disconnect(),
    ];
    let (o, t, s) = setup(frames, 0);
    let r = run(o, t, 71, Rights::new(3).unwrap(), 71);
    assert_eq!(r.stop, Stop::Disconnected);
    let s = s.borrow();
    assert_eq!(s.lookups, 0);
    assert_eq!(s.writes, 0);
    let codes: Vec<_> = s.sent[1..8].iter().map(status).collect();
    assert_eq!(codes, [-22, -9, -22, -22, -13, -9, -13]);
    for reply in &s.sent[1..8] {
        assert!(reply[24..].iter().all(|b| *b == 0));
    }
}

#[test]
fn closed_token_never_reused_and_lookup_attenuates() {
    let frames = vec![
        lookup(2),
        request(3, 2, 0, 0, b""),
        lookup(4),
        request(2, 2, 0, 1, b""),
        request(2, 3, 0, 1, b""),
        disconnect(),
    ];
    let (o, t, s) = setup(frames, 0);
    assert_eq!(run(o, t, 71, Rights::ALL, 71).stop, Stop::Disconnected);
    let s = s.borrow();
    assert_eq!(word(&s.sent[3], 3), 3);
    assert_eq!(status(&s.sent[4]), -9);
    assert_eq!(status(&s.sent[5]), -13);
    assert_eq!(s.reads, 0);
}

#[test]
fn lost_replies_consume_context_and_never_receive_replay() {
    for fail_send in 1..=4 {
        let (o, t, s) = setup(
            vec![lookup(7), request(5, 2, 0, 2, b"EF"), disconnect()],
            fail_send,
        );
        let r = run(o, t, 71, Rights::ALL, 71);
        assert_eq!(r.stop, Stop::ReplyLost(-32));
        assert_eq!(r.requests, fail_send - 1);
        assert_eq!(r.ready, fail_send != 1);
        let s = s.borrow();
        assert_eq!(s.drops, 1);
        assert_eq!(s.closes, 1);
        assert_eq!(s.writes, usize::from(fail_send >= 3));
        if fail_send >= 3 {
            assert_eq!(r.last_write.unwrap().txg, 788);
        }
    }
}

#[test]
fn unassigned_error_consumes_write_budget_but_preserves_reads() {
    let (o, t, s) = setup(
        vec![
            lookup(7),
            request(5, 2, 0, 2, b"EF"),
            request(5, 2, 0, 2, b"EF"),
            request(2, 2, 0, 16, b""),
            disconnect(),
        ],
        0,
    );
    s.borrow_mut().failure = Some(Ok(Completion {
        error: 28,
        txg: 0,
        bytes_staged: 0,
        state: 0,
    }));
    let r = run(o, t, 71, Rights::ALL, 71);
    assert_eq!(r.stop, Stop::Disconnected);
    assert_eq!(r.last_write, None);
    let s = s.borrow();
    assert_eq!(s.writes, 1);
    assert_eq!(status(&s.sent[2]), -28);
    assert_eq!(status(&s.sent[3]), -28);
    assert_eq!(&s.sent[4][48..52], b"abcd");
}

#[test]
fn unknown_committed_malformed_results_stop_without_next_request() {
    let values = [
        Err(Lost),
        Ok(Completion {
            error: 5,
            txg: 788,
            bytes_staged: 0,
            state: 1,
        }),
        Ok(Completion {
            error: 0,
            txg: 0,
            bytes_staged: 2,
            state: 2,
        }),
    ];
    for value in values {
        let (o, t, s) = setup(vec![lookup(7), request(5, 2, 0, 2, b"EF"), disconnect()], 0);
        s.borrow_mut().failure = Some(value);
        let r = run(o, t, 71, Rights::ALL, 71);
        assert_eq!(r.stop, Stop::Retired);
        assert_eq!(r.requests, 2);
        assert_eq!(s.borrow().writes, 1);
        assert_eq!(s.borrow().drops, 1);
        assert!(matches!(r.last_write.unwrap().state, 1 | 3));
    }
}

#[test]
fn receive_failure_budget_and_close_failures_stay_distinct() {
    let (o, mut t, s) = setup(vec![], 0);
    t.cleanup = [-5, -13];
    let r = run(o, t, 71, Rights::ALL, 71);
    assert_eq!(r.stop, Stop::Receive(-32));
    assert_eq!(r.cleanup, [-5, -13]);
    assert_eq!(s.borrow().drops, 1);
    let (o, t, s) = setup(vec![request(99, 1, 0, 0, b""); REQUESTS + 1], 0);
    let r = run(o, t, 71, Rights::ALL, 71);
    assert_eq!(r.stop, Stop::Limit);
    assert_eq!(r.requests, REQUESTS);
    assert_eq!(s.borrow().sent.len(), REQUESTS + 1);
}

#[test]
fn bad_provision_never_publishes_ready() {
    for (peer, epoch) in [(0, 71), (71, 0)] {
        let (o, t, s) = setup(vec![disconnect()], 0);
        let r = run(o, t, peer, Rights::ALL, epoch);
        assert_eq!(r.stop, Stop::Provision(Error::Invalid));
        assert!(!r.ready);
        assert!(s.borrow().sent.is_empty());
        assert_eq!(s.borrow().drops, 1);
    }
}

struct Raw {
    data: VecDeque<u8>,
    output: Vec<u8>,
    chunk: usize,
    stop: usize,
    calls: usize,
    would_block: usize,
    yields: usize,
    oversized: bool,
}
impl channel::Io for Raw {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        self.calls += 1;
        if self.would_block > 0 {
            self.would_block -= 1;
            return -11;
        }
        if self.oversized {
            return 17;
        }
        if self.stop == 0 {
            return 0;
        }
        let n = bytes.len().min(self.chunk).min(self.stop);
        self.stop -= n;
        if writing {
            self.output.extend_from_slice(&bytes[..n]);
        } else {
            for b in &mut bytes[..n] {
                *b = self.data.pop_front().unwrap();
            }
        }
        n as i64
    }
    fn yield_now(&mut self) {
        self.yields += 1;
    }
    fn close(&mut self) -> [i64; 2] {
        [0, 0]
    }
}
fn raw(chunk: usize, stop: usize) -> channel::Framed<Raw> {
    channel::Framed(Raw {
        data: (0..64).collect(),
        output: vec![],
        chunk,
        stop,
        calls: 0,
        would_block: 0,
        yields: 0,
        oversized: false,
    })
}

#[test]
fn all_short_transfer_sizes_assemble_exactly_and_send_does_not_mutate() {
    for chunk in 1..=16 {
        let mut io = raw(chunk, 128);
        io.0.would_block = 3;
        let mut bytes = [0xa5; FRAME];
        io.receive(&mut bytes).unwrap();
        let expected: Message = core::array::from_fn(|i| i as u8);
        assert_eq!(bytes, expected);
        io.send(&bytes).unwrap();
        assert_eq!(io.0.output, expected);
        assert_eq!(bytes, expected);
        assert_eq!(io.0.yields, 3);
    }
}

#[test]
fn every_partial_eof_discards_input_and_output_never_replays() {
    for stop in 0..FRAME {
        let mut io = raw(7, stop);
        let mut bytes = [0xa5; FRAME];
        assert_eq!(io.receive(&mut bytes), Err(-5));
        assert_eq!(bytes, [0; FRAME]);
        let mut io = raw(7, stop);
        let bytes = [0xa5; FRAME];
        assert_eq!(io.send(&bytes), Err(-5));
        assert_eq!(io.0.output, vec![0xa5; stop]);
        assert_eq!(bytes, [0xa5; FRAME]);
    }
}

#[test]
fn stalled_and_impossible_counts_fail_boundedly() {
    let mut io = raw(16, 64);
    io.0.would_block = channel::POLLS;
    let mut bytes = [0xa5; FRAME];
    assert_eq!(io.receive(&mut bytes), Err(-110));
    assert_eq!(bytes, [0; FRAME]);
    assert_eq!(io.0.calls, channel::POLLS);
    let mut io = raw(16, 64);
    io.0.oversized = true;
    assert_eq!(io.receive(&mut bytes), Err(-5));
    assert_eq!(bytes, [0; FRAME]);
}
