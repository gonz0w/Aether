// SPDX-License-Identifier: BSD-2-Clause
#[path = "../../user/storage/namespace.rs"]
mod owner;
use owner::wire::{Binding, Message, put, word};
use owner::{Backend, Error, Kind, Node, Owner};
use std::{cell::Cell, rc::Rc};

struct Provider(Rc<Cell<usize>>, bool);
impl Backend for Provider {
    fn root(&mut self) -> Result<Node, Error> {
        Ok(Node::new(900, 700, 0, Kind::Directory))
    }
    fn lookup(&mut self, _: Node, name: &[u8]) -> Result<Node, Error> {
        self.0.set(self.0.get() + 1);
        if name == b"file" {
            Ok(Node::new(901, 701, 5, Kind::File))
        } else {
            Err(Error::Backend(2))
        }
    }
    fn read(&mut self, _: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error> {
        self.0.set(self.0.get() + 1);
        buffer.fill(0xa5);
        if self.1 {
            return Err(Error::Backend(5));
        }
        let source = b"hello";
        let count = source
            .len()
            .saturating_sub(offset as usize)
            .min(buffer.len());
        if count != 0 {
            buffer[..count].copy_from_slice(&source[offset as usize..offset as usize + count]);
        }
        Ok(count)
    }
}

fn message(op: u64, entry: &Message, a: u64, b: u64) -> Message {
    let mut raw = [0; 64];
    for (index, value) in [op, word(entry, 1), word(entry, 2), a, b]
        .into_iter()
        .enumerate()
    {
        put(&mut raw, index, value);
    }
    raw
}
fn lookup(root: &Message, rights: u64) -> Message {
    let mut raw = message(1, root, rights, 4);
    raw[40..44].copy_from_slice(b"file");
    raw
}
fn denied(reply: Message, code: i64) {
    assert_eq!(word(&reply, 0) as i64, code, "WIRE_AUTHORITY");
    assert!(reply[8..].iter().all(|b| *b == 0), "WIRE_FAILED_REPLY");
}

#[test]
fn connection_is_selected_by_binding_not_wire_tokens() {
    let calls = Rc::new(Cell::new(0));
    let mut owner = Owner::new(Provider(calls.clone(), false), 0xd1000101).unwrap();
    let mut a = Binding::new(&mut owner, 0xd1000101).unwrap();
    let mut b = Binding::new(&mut owner, 0xd1020101).unwrap();
    let root = a.greeting();
    assert_eq!(word(&root, 1), 0xd1000101);
    assert_eq!(word(&root, 3), 1);
    assert_ne!(word(&root, 2), 900); // Raw backend object is never published.
    let file = a.request(&mut owner, &lookup(&root, 2));
    assert_eq!(word(&file, 3), 2);
    denied(b.request(&mut owner, &message(2, &file, 0, 5)), -13);
    assert_eq!(calls.get(), 1, "WIRE_AUTHORITY");
    let reply = a.request(&mut owner, &message(2, &file, 0, 24));
    assert_eq!(word(&reply, 4), 5);
    assert_eq!(&reply[40..45], b"hello");
    assert!(reply[45..].iter().all(|b| *b == 0));
    denied(a.request(&mut owner, &message(2, &root, 0, 1)), -21);
    let restricted = a.request(&mut owner, &lookup(&root, 1));
    denied(a.request(&mut owner, &message(2, &restricted, 0, 1)), -13);
}

#[test]
fn canonical_rejection_precedes_provider_and_never_echoes_request() {
    let calls = Rc::new(Cell::new(0));
    let mut owner = Owner::new(Provider(calls.clone(), false), 11).unwrap();
    let mut binding = Binding::new(&mut owner, 71).unwrap();
    let root = binding.greeting();
    for index in 44..64 {
        let mut raw = lookup(&root, 2);
        raw[index] = 0xa5;
        denied(binding.request(&mut owner, &raw), -22);
    }
    for op in [0, 5, 0xffff, u64::MAX] {
        denied(binding.request(&mut owner, &message(op, &root, 0, 0)), -22);
    }
    for count in [0, 25, u64::MAX] {
        let raw = message(1, &root, 2, count);
        denied(binding.request(&mut owner, &raw), -22);
    }
    let mut forged = root;
    put(&mut forged, 1, 900);
    put(&mut forged, 2, 700);
    denied(binding.request(&mut owner, &lookup(&forged, 2)), -9);
    assert_eq!(calls.get(), 0, "WIRE_CANONICAL");
}

#[test]
fn close_disconnect_and_provider_epoch_reject_replays() {
    let calls = Rc::new(Cell::new(0));
    let mut owner = Owner::new(Provider(calls.clone(), false), 11).unwrap();
    let mut binding = Binding::new(&mut owner, 71).unwrap();
    let root = binding.greeting();
    let file = binding.request(&mut owner, &lookup(&root, 2));
    assert_eq!(
        binding.request(&mut owner, &message(3, &file, 0, 0)),
        [0; 64]
    );
    denied(binding.request(&mut owner, &message(2, &file, 0, 1)), -9);
    let fresh = binding.request(&mut owner, &lookup(&root, 2));
    assert_ne!(word(&file, 2), word(&fresh, 2));
    let mut disconnect = [0; 64];
    put(&mut disconnect, 0, 4);
    assert_eq!(binding.request(&mut owner, &disconnect), [0; 64]);
    assert!(binding.closed(), "WIRE_DISCONNECT");
    denied(binding.request(&mut owner, &message(2, &fresh, 0, 1)), -9);
    owner.shutdown();
    let mut replacement = Owner::new(Provider(calls, false), 12).unwrap();
    let mut connection = Binding::new(&mut replacement, 71).unwrap();
    denied(
        connection.request(&mut replacement, &message(2, &fresh, 0, 1)),
        -9,
    );
}

#[test]
fn failed_partial_provider_output_is_canonical_and_overlength_never_calls_it() {
    let calls = Rc::new(Cell::new(0));
    let mut owner = Owner::new(Provider(calls.clone(), true), 11).unwrap();
    let mut binding = Binding::new(&mut owner, 71).unwrap();
    let root = binding.greeting();
    let file = binding.request(&mut owner, &lookup(&root, 2));
    denied(binding.request(&mut owner, &message(2, &file, 0, 25)), -22);
    assert_eq!(calls.get(), 1);
    denied(binding.request(&mut owner, &message(2, &file, 0, 5)), -5);
    assert_eq!(calls.get(), 2);
}
