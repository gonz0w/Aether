// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use std::{cell::RefCell, rc::Rc, vec, vec::Vec};

struct State {
    bytes: Vec<u8>,
    calls: [usize; 4],
    drops: usize,
    utc_calls: usize,
    utc: Result<Utc, Error>,
    completion: Result<Completion, Lost>,
    stale_lookup: bool,
    bad_read: bool,
}

struct Provider(Rc<RefCell<State>>);
impl Drop for Provider {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
impl Backend for Provider {
    fn root(&mut self) -> Result<Node, Error> {
        self.0.borrow_mut().calls[0] += 1;
        Ok(Node::new(34, 45, 0, Kind::Directory))
    }
    fn lookup(&mut self, _: Node, name: &[u8]) -> Result<Node, Error> {
        let mut state = self.0.borrow_mut();
        state.calls[1] += 1;
        match name {
            b"file" | b"alias" => Ok(Node::new(
                2,
                7,
                if state.stale_lookup {
                    4
                } else {
                    state.bytes.len() as u64
                },
                Kind::File,
            )),
            b"other" => Ok(Node::new(3, 7, 1, Kind::File)),
            _ => Err(Error::Backend(2)),
        }
    }
    fn read(&mut self, file: Node, offset: u64, out: &mut [u8]) -> Result<usize, Error> {
        let mut state = self.0.borrow_mut();
        state.calls[2] += 1;
        if state.bad_read {
            out.fill(0x55);
            return Ok(out.len() + 1);
        }
        let bytes = if file.object == 3 {
            b"z".as_slice()
        } else {
            &state.bytes
        };
        let start = (offset.min(bytes.len() as u64)) as usize;
        let length = out.len().min(bytes.len() - start);
        out[..length].copy_from_slice(&bytes[start..start + length]);
        Ok(length)
    }
    fn write(&mut self, _: Node, offset: u64, bytes: &[u8], utc: Utc) -> Result<Completion, Lost> {
        let mut state = self.0.borrow_mut();
        state.calls[3] += 1;
        assert_eq!(
            utc,
            Utc {
                seconds: 1_792_300_000,
                nanoseconds: 123
            }
        );
        let completion = state.completion;
        if completion.is_ok_and(|c| c.state != 0 && c.bytes_staged == bytes.len() as u64) {
            let start = offset as usize;
            let end = (start + bytes.len()).max(state.bytes.len());
            state.bytes.resize(end, 0);
            state.bytes[start..start + bytes.len()].copy_from_slice(bytes);
        }
        completion
    }
}
struct Time(Rc<RefCell<State>>);
impl Clock for Time {
    fn utc(&mut self) -> Result<Utc, Error> {
        let mut state = self.0.borrow_mut();
        state.utc_calls += 1;
        state.utc
    }
}
type Service = Owner<Provider, Time>;
fn setup() -> (Service, Rc<RefCell<State>>) {
    let state = Rc::new(RefCell::new(State {
        bytes: vec![b'a', b'b', b'c', b'd'],
        calls: [0; 4],
        drops: 0,
        utc_calls: 0,
        utc: Ok(Utc {
            seconds: 1_792_300_000,
            nanoseconds: 123,
        }),
        completion: Ok(Completion {
            error: 0,
            txg: 788,
            bytes_staged: 2,
            state: 2,
        }),
        stale_lookup: false,
        bad_read: false,
    }));
    (
        Owner::new(Provider(state.clone()), Time(state.clone()), 1).unwrap(),
        state,
    )
}
fn file(owner: &mut Service, peer: u64, attachment: Attachment, rights: Rights) -> Entry {
    owner
        .lookup(
            peer,
            attachment.session,
            attachment.root.handle,
            b"file",
            rights,
        )
        .unwrap()
}

#[test]
fn write_updates_every_alias_and_actual_read_eof() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let b = owner.attach(12, Rights::ALL).unwrap();
    let writer = file(&mut owner, 11, a, Rights::WRITE);
    let alias = file(&mut owner, 12, b, Rights::READ);
    let other = owner
        .lookup(12, b.session, b.root.handle, b"other", Rights::READ)
        .unwrap();
    assert_eq!(
        owner.write(11, a.session, writer.handle, 4, b"EF"),
        Ok(Written {
            bytes: 2,
            assigned_txg: Some(788)
        })
    );
    assert_eq!(owner.stat(12, b.session, alias.handle).unwrap().size, 6);
    assert_eq!(owner.stat(12, b.session, other.handle).unwrap().size, 1);
    let mut reply = [0xa5; MAX_READ];
    assert_eq!(
        owner.read(12, b.session, alias.handle, 0, 20, &mut reply),
        Ok(6)
    );
    assert_eq!(&reply[..6], b"abcdEF");
    assert!(reply[6..].iter().all(|b| *b == 0));
    assert_eq!(
        owner.read(12, b.session, alias.handle, 6, 20, &mut reply),
        Ok(0)
    );
    let fresh = file(&mut owner, 11, a, Rights::READ);
    assert_eq!(fresh.size, 6);
    assert_eq!(
        owner.write(11, a.session, writer.handle, 0, b"XX"),
        Err(Error::WriteLimit)
    );
    assert_eq!(state.borrow().calls[3], 1);
    drop(owner);
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn authority_denials_precede_time_and_backend() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let b = owner.attach(12, Rights::ALL).unwrap();
    let writer = file(&mut owner, 11, a, Rights::WRITE);
    let read = file(&mut owner, 11, a, Rights::READ);
    for (peer, session, handle, error) in [
        (12, a.session, writer.handle, Error::Denied),
        (12, b.session, writer.handle, Error::Denied),
        (11, a.session, read.handle, Error::Denied),
        (11, a.session, a.root.handle, Error::IsDirectory),
        (
            11,
            a.session,
            Handle {
                epoch: 2,
                serial: writer.handle.serial,
            },
            Error::Stale,
        ),
    ] {
        assert_eq!(owner.write(peer, session, handle, 0, b"XX"), Err(error));
    }
    let limited = owner.attach(13, Rights::LOOKUP).unwrap();
    assert_eq!(
        owner.lookup(
            13,
            limited.session,
            limited.root.handle,
            b"file",
            Rights::WRITE
        ),
        Err(Error::Denied)
    );
    assert_eq!(state.borrow().utc_calls, 0);
    assert_eq!(state.borrow().calls[3], 0);
}

#[test]
fn invalid_names_and_write_ranges_have_no_effect() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    for name in [b"".as_slice(), b".", b"..", b"a/b", b"a\0b", &[b'x'; 256]] {
        assert_eq!(
            owner.lookup(11, a.session, a.root.handle, name, Rights::READ),
            Err(Error::Invalid)
        );
    }
    let f = file(&mut owner, 11, a, Rights::WRITE);
    for (offset, bytes) in [
        (5, b"x".as_slice()),
        (u64::MAX, b"xx"),
        (0, &[1; MAX_READ + 1]),
    ] {
        assert_eq!(
            owner.write(11, a.session, f.handle, offset, bytes),
            Err(Error::Invalid)
        );
    }
    assert_eq!(
        owner.write(11, a.session, f.handle, 0, b""),
        Ok(Written {
            bytes: 0,
            assigned_txg: None
        })
    );
    assert_eq!(state.borrow().utc_calls, 0);
    assert_eq!(state.borrow().calls[3], 0);
}

#[test]
fn policy_clock_failure_and_invalid_time_do_not_consume_write() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let f = file(&mut owner, 11, a, Rights::WRITE);
    for utc in [
        Err(Error::Clock),
        Ok(Utc {
            seconds: u64::MAX,
            nanoseconds: 0,
        }),
        Ok(Utc {
            seconds: 1,
            nanoseconds: 1_000_000_000,
        }),
    ] {
        state.borrow_mut().utc = utc;
        assert_eq!(
            owner.write(11, a.session, f.handle, 0, b"XX"),
            Err(Error::Clock)
        );
    }
    assert_eq!(state.borrow().calls[3], 0);
    assert!(!owner.write_used);
}

#[test]
fn unassigned_error_keeps_reads_but_never_replays() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let f = file(&mut owner, 11, a, Rights::ALL);
    state.borrow_mut().completion = Ok(Completion {
        error: 28,
        txg: 0,
        bytes_staged: 0,
        state: 0,
    });
    assert_eq!(
        owner.write(11, a.session, f.handle, 0, b"XX"),
        Err(Error::Backend(28))
    );
    assert_eq!(owner.stat(11, a.session, f.handle).unwrap().size, 4);
    assert_eq!(state.borrow().drops, 0);
    let mut reply = [0; MAX_READ];
    assert_eq!(owner.read(11, a.session, f.handle, 0, 4, &mut reply), Ok(4));
    assert_eq!(&reply[..4], b"abcd");
    assert_eq!(
        owner.write(11, a.session, f.handle, 0, b"XX"),
        Err(Error::WriteLimit)
    );
}

#[test]
fn committed_errors_and_completion_loss_retire_all_aliases_once() {
    for completion in [
        Err(Lost),
        Ok(Completion {
            error: 5,
            txg: 788,
            bytes_staged: 2,
            state: 1,
        }),
        Ok(Completion {
            error: 5,
            txg: 788,
            bytes_staged: 0,
            state: 1,
        }),
    ] {
        let (mut owner, state) = setup();
        let a = owner.attach(11, Rights::ALL).unwrap();
        let b = owner.attach(12, Rights::ALL).unwrap();
        let f = file(&mut owner, 11, a, Rights::WRITE);
        let alias = file(&mut owner, 12, b, Rights::READ);
        state.borrow_mut().completion = completion;
        let expected = match completion {
            Err(Lost) => Error::Uncertain,
            Ok(c) => Error::WriteFailed(c),
        };
        assert_eq!(
            owner.write(11, a.session, f.handle, 0, b"XX"),
            Err(expected)
        );
        assert_eq!(
            owner.stat(12, b.session, alias.handle),
            Err(Error::Poisoned)
        );
        assert_eq!(owner.attach(13, Rights::ALL), Err(Error::Poisoned));
        assert_eq!(
            owner.write(11, a.session, f.handle, 0, b"XX"),
            Err(Error::Poisoned)
        );
        let mut reply = [0xa5; MAX_READ];
        assert_eq!(
            owner.read(12, b.session, alias.handle, 0, 2, &mut reply),
            Err(Error::Poisoned)
        );
        assert!(reply.iter().all(|b| *b == 0));
        owner.shutdown();
        drop(owner);
        assert_eq!((state.borrow().drops, state.borrow().calls[3]), (1, 1));
    }
}

#[test]
fn malformed_completion_matrix_is_not_publishable() {
    for completion in [
        Completion {
            error: 0,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        },
        Completion {
            error: -5,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        },
        Completion {
            error: 5,
            txg: 1,
            bytes_staged: 0,
            state: 0,
        },
        Completion {
            error: 5,
            txg: 0,
            bytes_staged: 2,
            state: 0,
        },
        Completion {
            error: 0,
            txg: 1,
            bytes_staged: 2,
            state: 1,
        },
        Completion {
            error: 5,
            txg: 0,
            bytes_staged: 2,
            state: 1,
        },
        Completion {
            error: 5,
            txg: 1,
            bytes_staged: 1,
            state: 1,
        },
        Completion {
            error: 0,
            txg: 0,
            bytes_staged: 2,
            state: 2,
        },
        Completion {
            error: 0,
            txg: 1,
            bytes_staged: 1,
            state: 2,
        },
        Completion {
            error: 5,
            txg: 1,
            bytes_staged: 2,
            state: 2,
        },
        Completion {
            error: 0,
            txg: 1,
            bytes_staged: 2,
            state: 3,
        },
    ] {
        let (mut owner, state) = setup();
        let a = owner.attach(11, Rights::ALL).unwrap();
        let f = file(&mut owner, 11, a, Rights::ALL);
        state.borrow_mut().completion = Ok(completion);
        assert_eq!(
            owner.write(11, a.session, f.handle, 0, b"XX"),
            Err(Error::InvalidCompletion)
        );
        assert_eq!(state.borrow().drops, 1);
        assert_eq!(owner.stat(11, a.session, f.handle), Err(Error::Poisoned));
    }
}

#[test]
fn stale_metadata_from_new_alias_retires_context() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let f = file(&mut owner, 11, a, Rights::WRITE);
    owner.write(11, a.session, f.handle, 4, b"EF").unwrap();
    state.borrow_mut().stale_lookup = true;
    assert_eq!(
        owner.lookup(11, a.session, a.root.handle, b"alias", Rights::READ),
        Err(Error::InvalidMetadata)
    );
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn handle_and_session_retirement_never_reuse_serials() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let old = file(&mut owner, 11, a, Rights::WRITE);
    owner.close(11, a.session, old.handle).unwrap();
    let fresh = file(&mut owner, 11, a, Rights::WRITE);
    assert_ne!(old.handle, fresh.handle);
    assert_eq!(
        owner.write(11, a.session, old.handle, 0, b"XX"),
        Err(Error::Stale)
    );
    owner.disconnect(11, a.session).unwrap();
    assert_eq!(
        owner.write(11, a.session, fresh.handle, 0, b"XX"),
        Err(Error::Stale)
    );
    owner.shutdown();
    assert_eq!(owner.attach(11, Rights::ALL), Err(Error::Closed));
    assert_eq!(state.borrow().calls[3], 0);
}

#[test]
fn bounded_tables_and_serial_overflow_deny_before_backend() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    for _ in 1..MAX_HANDLES {
        file(&mut owner, 11, a, Rights::READ);
    }
    let before = state.borrow().calls;
    assert_eq!(
        owner.lookup(11, a.session, a.root.handle, b"file", Rights::READ),
        Err(Error::Full)
    );
    assert_eq!(state.borrow().calls, before);
    let (mut owner, _) = setup();
    for peer in 1..=MAX_CONNECTIONS {
        owner.attach(peer as u64, Rights::ALL).unwrap();
    }
    assert_eq!(owner.attach(100, Rights::ALL), Err(Error::Full));
    let (mut owner, _) = setup();
    owner.next_serial = u64::MAX;
    assert_eq!(owner.attach(11, Rights::ALL), Err(Error::Full));
    assert_eq!(owner.next_serial, u64::MAX);
}

#[test]
fn read_failure_does_not_leak_provider_bytes() {
    let (mut owner, state) = setup();
    let a = owner.attach(11, Rights::ALL).unwrap();
    let f = file(&mut owner, 11, a, Rights::READ);
    state.borrow_mut().bad_read = true;
    let mut reply = [0xa5; MAX_READ];
    assert_eq!(
        owner.read(11, a.session, f.handle, 0, 4, &mut reply),
        Err(Error::InvalidCompletion)
    );
    assert!(reply.iter().all(|b| *b == 0));
}

#[test]
fn existing_file_overwrite_extension_and_maximum_payload() {
    for (offset, length) in [(1, 2), (2, 4), (0, MAX_READ)] {
        let (mut owner, state) = setup();
        let a = owner.attach(11, Rights::ALL).unwrap();
        let f = file(&mut owner, 11, a, Rights::ALL);
        let bytes = vec![b'X'; length];
        state.borrow_mut().completion.as_mut().unwrap().bytes_staged = length as u64;
        let mut expected = b"abcd".to_vec();
        expected.resize(4.max(offset + length), 0);
        expected[offset..offset + length].copy_from_slice(&bytes);
        assert_eq!(
            owner
                .write(11, a.session, f.handle, offset as u64, &bytes)
                .unwrap()
                .bytes,
            length
        );
        assert_eq!(
            owner.stat(11, a.session, f.handle).unwrap().size,
            expected.len() as u64
        );
        assert_eq!(state.borrow().bytes, expected);
    }
}

#[test]
fn signed_size_boundary_and_unknown_rights_reject_before_provider() {
    let (mut owner, state) = setup();
    for bits in [0, 8, 128, 255] {
        assert_eq!(Rights::new(bits), Err(Error::Invalid));
    }
    assert!(!Rights::new(3).unwrap().contains(Rights::WRITE));
    let a = owner.attach(11, Rights::ALL).unwrap();
    let f = file(&mut owner, 11, a, Rights::WRITE);
    // A trusted provider could report a very large file; avoid allocating it.
    for open in owner.handles.iter_mut().flatten() {
        if open.node.identity() == (2, 7) {
            open.node.size = i64::MAX as u64;
        }
    }
    assert_eq!(
        owner.write(11, a.session, f.handle, i64::MAX as u64, b"X"),
        Err(Error::Invalid)
    );
    assert_eq!(state.borrow().utc_calls, 0);
    assert_eq!(state.borrow().calls[3], 0);
}
