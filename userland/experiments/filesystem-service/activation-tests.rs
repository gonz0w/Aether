// SPDX-License-Identifier: BSD-2-Clause
//! Execute the actual wrapper without native authority or guest timing claims.
extern crate std;
use super::*;
use filesystem_service::{message, put};
use std::{cell::Cell, vec::Vec};

struct Queue<'a> {
    published: &'a Cell<usize>,
    sends: &'a Cell<usize>,
    fail: bool,
}
impl Channel for Queue<'_> {
    fn receive(&mut self, _: &mut Message) -> Result<(), i64> {
        Err(-32)
    }
    fn send(&mut self, _: &Message) -> Result<(), i64> {
        assert_eq!(self.published.get(), 1, "ACTIVATION_BEFORE_QUEUE");
        self.sends.set(self.sends.get() + 1);
        if self.fail {
            Err(-32)
        } else {
            Ok(())
        }
    }
    fn close(&mut self) -> [i64; 2] {
        [-13, -32]
    }
}
fn greeting() -> Message {
    let mut frame = message(17, 0);
    put(&mut frame, 3, 1);
    put(&mut frame, 4, 1);
    put(&mut frame, 5, 8192);
    frame
}
fn exercise(
    frame: Message,
    epoch: u64,
    status: i64,
    fail: bool,
) -> (Result<(), i64>, usize, usize) {
    let published = Cell::new(0);
    let sends = Cell::new(0);
    let mut channel = Activated {
        inner: Queue {
            published: &published,
            sends: &sends,
            fail,
        },
        publish: || {
            published.set(published.get() + 1);
            status
        },
        epoch,
        first: true,
        failed: false,
    };
    let result = channel.send(&frame);
    if result.is_err() {
        assert!(channel.send(&greeting()).is_err(), "ACTIVATION_NO_RETRY");
    } else {
        channel.send(&greeting()).unwrap();
    }
    assert_eq!(channel.close(), [-13, -32]);
    (result, published.get(), sends.get())
}
#[test]
fn validates_every_greeting_field_before_publication_or_output() {
    let mut cases: Vec<Message> = Vec::new();
    for (index, value) in [
        (1, 1),
        (2, 0),
        (2, 18),
        (3, 0),
        (3, 2),
        (4, 2),
        (6, 1),
        (7, 1),
    ] {
        let mut frame = greeting();
        put(&mut frame, index, value);
        cases.push(frame);
    }
    let mut magic = greeting();
    magic[0] ^= 1;
    cases.push(magic);
    for frame in cases {
        assert_eq!(
            exercise(frame, 17, 0, false),
            (Err(-22), 0, 0),
            "ACTIVATION_GREETING"
        );
    }
    assert_eq!(exercise(greeting(), 0, 0, false), (Err(-22), 0, 0));
}
#[test]
fn publication_precedes_queue_and_occurs_once_across_replies() {
    assert_eq!(exercise(greeting(), 17, 0, false), (Ok(()), 1, 2));
}
#[test]
fn publication_and_output_errors_latch_without_retry() {
    for (status, expected) in [(-13, -13), (-9, -9), (1, -5)] {
        assert_eq!(
            exercise(greeting(), 17, status, false),
            (Err(expected), 1, 0),
            "ACTIVATION_PUBLISH_FAILURE"
        );
    }
    assert_eq!(exercise(greeting(), 17, 0, true), (Err(-32), 1, 1));
}
