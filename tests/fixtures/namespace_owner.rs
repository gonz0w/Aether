// SPDX-License-Identifier: BSD-2-Clause
//! Actual owner semantics over a failure-injectable provider, not ZPL or IPC proof.
use super::*;
use std::{cell::RefCell, rc::Rc, vec::Vec};

const PEER: u64 = 71;
const OTHER: u64 = 72;
const SIZE: u64 = 9001;

#[derive(Default)]
struct State {
    calls: Vec<&'static str>,
    drops: usize,
    root_error: bool,
    bad_root: bool,
    lookup_error: bool,
    bad_lookup: bool,
    read_mode: u8,
}
struct Provider(Rc<RefCell<State>>);

impl Drop for Provider {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}

fn data(offset: u64) -> u8 {
    (offset.wrapping_mul(37).wrapping_add(19) % 251) as u8
}

impl Backend for Provider {
    fn root(&mut self) -> Result<Node, Error> {
        let mut state = self.0.borrow_mut();
        state.calls.push("root");
        if state.root_error {
            return Err(Error::Backend(5));
        }
        Ok(Node::new(
            if state.bad_root { 0 } else { 34 },
            45,
            1,
            Kind::Directory,
        ))
    }

    fn lookup(&mut self, directory: Node, name: &[u8]) -> Result<Node, Error> {
        let mut state = self.0.borrow_mut();
        state.calls.push("lookup");
        assert!(directory.identity() == (34, 45) || directory.identity() == (35, 46));
        if state.lookup_error {
            return Err(Error::Backend(5));
        }
        if state.bad_lookup {
            return Ok(Node::new(2, 0, SIZE, Kind::File));
        }
        match name {
            b"file" => Ok(Node::new(2, 47, SIZE, Kind::File)),
            b"dir" => Ok(Node::new(35, 46, 1, Kind::Directory)),
            _ => Err(Error::Backend(2)),
        }
    }

    fn read(&mut self, file: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error> {
        let mut state = self.0.borrow_mut();
        state.calls.push("read");
        assert_eq!(file.identity(), (2, 47));
        let count = SIZE.saturating_sub(offset).min(buffer.len() as u64) as usize;
        // Deliberately dirty the tail as well. The owner must publish only the
        // confirmed count, and clear all partial bytes on provider failure.
        buffer.fill(0xa5);
        for (index, byte) in buffer[..count].iter_mut().enumerate() {
            *byte = data(offset + index as u64);
        }
        match state.read_mode {
            0 => Ok(count),
            1 => Err(Error::Backend(5)),
            2 => Ok(count + 1),
            3 => Ok(count.saturating_sub(1)),
            _ => Err(Error::Backend(116)),
        }
    }
}

fn make(epoch: u64) -> (Owner<Provider>, Rc<RefCell<State>>) {
    let state = Rc::new(RefCell::new(State::default()));
    (Owner::new(Provider(state.clone()), epoch).unwrap(), state)
}

fn file(owner: &mut Owner<Provider>, attachment: Attachment, rights: Rights) -> Entry {
    owner
        .lookup(
            PEER,
            attachment.session,
            attachment.root.handle,
            b"file",
            rights,
        )
        .unwrap()
}

fn denied_read(
    owner: &mut Owner<Provider>,
    peer: u64,
    session: Session,
    handle: Handle,
    expected: Error,
) {
    let mut reply = [0xa5; MAX_READ];
    assert_eq!(
        owner.read(peer, session, handle, 0, 16, &mut reply),
        Err(expected),
        "AUTHORITY denial"
    );
    assert_eq!(reply, [0; MAX_READ], "FAILED_REPLY must clear all bytes");
}

#[test]
fn whole_file_relative_lookup_and_exact_eof_tail() {
    let (mut owner, state) = make(11);
    let attachment = owner.attach(PEER, Rights::ALL).unwrap();
    let directory = owner
        .lookup(
            PEER,
            attachment.session,
            attachment.root.handle,
            b"dir",
            Rights::ALL,
        )
        .unwrap();
    let file = owner
        .lookup(
            PEER,
            attachment.session,
            directory.handle,
            b"file",
            Rights::READ,
        )
        .unwrap();
    assert_eq!((file.kind, file.size), (Kind::File, SIZE));
    let mut offset = 0;
    let mut reply = [0xa5; MAX_READ];
    while offset < SIZE {
        let count = owner
            .read(
                PEER,
                attachment.session,
                file.handle,
                offset,
                MAX_READ,
                &mut reply,
            )
            .unwrap();
        assert_eq!(count as u64, (SIZE - offset).min(MAX_READ as u64));
        for (index, byte) in reply[..count].iter().enumerate() {
            assert_eq!(*byte, data(offset + index as u64));
        }
        assert!(
            reply[count..].iter().all(|b| *b == 0),
            "SUCCESS_TAIL must be zero"
        );
        offset += count as u64;
    }
    for (offset, length) in [(SIZE, 4096), (SIZE + 900, 17), (u64::MAX, 0), (0, 0)] {
        reply.fill(0xa5);
        assert_eq!(
            owner.read(
                PEER,
                attachment.session,
                file.handle,
                offset,
                length,
                &mut reply
            ),
            Ok(0)
        );
        assert_eq!(reply, [0; MAX_READ]);
    }
    assert_eq!(state.borrow().drops, 0);
    owner.shutdown();
    assert_eq!(
        state.borrow().drops,
        1,
        "BACKEND_LIFETIME shutdown closes once"
    );
    assert!(owner.handles.iter().all(Option::is_none));
    assert!(owner.connections.iter().all(Option::is_none));
    owner.shutdown();
    drop(owner);
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn peer_session_and_service_epoch_never_alias() {
    let (mut owner, state) = make(21);
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    let b = owner.attach(OTHER, Rights::ALL).unwrap();
    let c = owner.attach(PEER, Rights::ALL).unwrap();
    let f = file(&mut owner, a, Rights::READ);
    let before = state.borrow().calls.len();
    denied_read(&mut owner, OTHER, a.session, f.handle, Error::Denied);
    denied_read(&mut owner, OTHER, b.session, f.handle, Error::Denied);
    denied_read(&mut owner, PEER, c.session, f.handle, Error::Denied);
    assert_eq!(owner.close(OTHER, a.session, f.handle), Err(Error::Denied));
    assert_eq!(owner.disconnect(OTHER, a.session), Err(Error::Denied));
    assert_eq!(
        owner.lookup(OTHER, a.session, a.root.handle, b"file", Rights::READ),
        Err(Error::Denied)
    );
    let (mut replacement, _) = make(22);
    let fresh = replacement.attach(PEER, Rights::ALL).unwrap();
    assert_eq!(
        replacement.lookup(PEER, a.session, fresh.root.handle, b"file", Rights::READ),
        Err(Error::Stale)
    );
    denied_read(
        &mut replacement,
        PEER,
        fresh.session,
        f.handle,
        Error::Stale,
    );
    assert_eq!(
        state.borrow().calls.len(),
        before,
        "AUTHORITY denial before backend"
    );
    let mut reply = [0; MAX_READ];
    assert_eq!(
        owner.read(PEER, a.session, f.handle, 0, 1, &mut reply),
        Ok(1)
    );
}

#[test]
fn rights_are_attenuated_and_types_checked_before_provider() {
    let (mut owner, state) = make(31);
    let a = owner.attach(PEER, Rights::LOOKUP).unwrap();
    let before = state.borrow().calls.len();
    assert_eq!(
        owner.lookup(PEER, a.session, a.root.handle, b"file", Rights::READ),
        Err(Error::Denied),
        "RIGHTS_CEILING"
    );
    let f = file(&mut owner, a, Rights::LOOKUP);
    let after_lookup = state.borrow().calls.len();
    denied_read(&mut owner, PEER, a.session, f.handle, Error::Denied);
    assert_eq!(
        owner.lookup(PEER, a.session, f.handle, b"file", Rights::LOOKUP),
        Err(Error::NotDirectory)
    );
    assert_eq!(state.borrow().calls.len(), after_lookup);
    let b = owner.attach(OTHER, Rights::READ).unwrap();
    assert_eq!(
        owner.lookup(OTHER, b.session, b.root.handle, b"file", Rights::READ),
        Err(Error::Denied)
    );
    denied_read(
        &mut owner,
        OTHER,
        b.session,
        b.root.handle,
        Error::IsDirectory,
    );
    assert_eq!(after_lookup, before + 1);
    for bits in 0..=255 {
        assert_eq!(Rights::new(bits).is_ok(), (1..=3).contains(&bits));
    }
}

#[test]
fn invalid_names_lengths_offsets_and_partial_backend_errors() {
    let (mut owner, state) = make(41);
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    let before = state.borrow().calls.len();
    for name in [
        b"".as_slice(),
        b".",
        b"..",
        b"a/b",
        b"/",
        b"a\0b",
        &[b'x'; 256],
    ] {
        assert_eq!(
            owner.lookup(PEER, a.session, a.root.handle, name, Rights::READ),
            Err(Error::Invalid)
        );
    }
    assert_eq!(
        state.borrow().calls.len(),
        before,
        "NAME_BOUNDARY before backend"
    );
    // The 255-byte edge is admitted to the backend (which reports missing).
    assert_eq!(
        owner.lookup(PEER, a.session, a.root.handle, &[b'x'; 255], Rights::READ),
        Err(Error::Backend(2))
    );
    let f = file(&mut owner, a, Rights::READ);
    let before = state.borrow().calls.len();
    let mut reply = [0xa5; MAX_READ];
    for (offset, length) in [(0, MAX_READ + 1), (u64::MAX, 1), (u64::MAX - 2, 3)] {
        reply.fill(0xa5);
        assert_eq!(
            owner.read(PEER, a.session, f.handle, offset, length, &mut reply),
            Err(Error::Invalid)
        );
        assert_eq!(reply, [0; MAX_READ]);
    }
    assert_eq!(state.borrow().calls.len(), before);
    for (mode, error) in [
        (1, Error::Backend(5)),
        (2, Error::InvalidCompletion),
        (3, Error::InvalidCompletion),
        (4, Error::Backend(116)),
    ] {
        state.borrow_mut().read_mode = mode;
        reply.fill(0xa5);
        assert_eq!(
            owner.read(PEER, a.session, f.handle, 0, 32, &mut reply),
            Err(error),
            "READ_COMPLETION"
        );
        assert_eq!(reply, [0; MAX_READ], "FAILED_REPLY must clear partial data");
    }
}

#[test]
fn close_disconnect_and_repeated_slot_reuse_preserve_other_sessions() {
    let (mut owner, state) = make(51);
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    let b = owner.attach(OTHER, Rights::ALL).unwrap();
    let mut retired = Vec::new();
    let mut reply = [0; MAX_READ];
    for _ in 0..64 {
        let f = file(&mut owner, a, Rights::READ);
        for handle in &retired {
            denied_read(&mut owner, PEER, a.session, *handle, Error::Stale);
        }
        owner.close(PEER, a.session, f.handle).unwrap();
        assert_eq!(
            owner.close(PEER, a.session, f.handle),
            Err(Error::Stale),
            "CLOSE_REUSE"
        );
        retired.push(f.handle);
        assert_eq!(
            state.borrow().drops,
            0,
            "BACKEND_LIFETIME close is not teardown"
        );
    }
    let f = file(&mut owner, a, Rights::READ);
    owner.disconnect(PEER, a.session).unwrap();
    let again = owner.attach(PEER, Rights::ALL).unwrap();
    assert_ne!(a.session, again.session);
    denied_read(&mut owner, PEER, a.session, f.handle, Error::Stale);
    denied_read(&mut owner, PEER, again.session, f.handle, Error::Stale);
    assert_eq!(
        owner
            .lookup(OTHER, b.session, b.root.handle, b"file", Rights::READ)
            .unwrap()
            .size,
        SIZE
    );
    let f = file(&mut owner, again, Rights::READ);
    assert_eq!(
        owner.read(PEER, again.session, f.handle, 1, 1, &mut reply),
        Ok(1)
    );
    owner.shutdown();
    denied_read(&mut owner, PEER, again.session, f.handle, Error::Closed);
    assert_eq!(owner.attach(PEER, Rights::ALL), Err(Error::Closed));
    assert_eq!(
        owner.close(PEER, again.session, f.handle),
        Err(Error::Closed)
    );
    assert_eq!(owner.disconnect(OTHER, b.session), Err(Error::Closed));
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn bounded_tables_deny_without_backend_effects_and_recover_closed_slots() {
    let (mut owner, state) = make(61);
    let mut attachments = Vec::new();
    for _ in 0..MAX_CONNECTIONS {
        attachments.push(owner.attach(PEER, Rights::ALL).unwrap());
    }
    assert_eq!(owner.attach(PEER, Rights::ALL), Err(Error::Full));
    owner
        .disconnect(PEER, attachments.pop().unwrap().session)
        .unwrap();
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    let mut files = Vec::new();
    for _ in MAX_CONNECTIONS..MAX_HANDLES {
        files.push(file(&mut owner, a, Rights::READ));
    }
    let before = state.borrow().calls.len();
    let serial = owner.next_serial;
    assert_eq!(
        owner.lookup(PEER, a.session, a.root.handle, b"file", Rights::READ),
        Err(Error::Full)
    );
    assert_eq!(
        state.borrow().calls.len(),
        before,
        "CAPACITY before backend"
    );
    assert_eq!(owner.next_serial, serial);
    owner
        .close(PEER, a.session, files.pop().unwrap().handle)
        .unwrap();
    file(&mut owner, a, Rights::READ);
    owner.disconnect(PEER, a.session).unwrap();
    owner.attach(OTHER, Rights::ALL).unwrap();
}

#[test]
fn serial_exhaustion_is_atomic_and_never_wraps() {
    let (mut owner, state) = make(71);
    owner.next_serial = u64::MAX;
    assert_eq!(owner.attach(PEER, Rights::ALL), Err(Error::Full));
    assert!(owner.connections.iter().all(Option::is_none));
    assert!(owner.handles.iter().all(Option::is_none));
    assert_eq!(owner.next_serial, u64::MAX);
    owner.next_serial = u64::MAX - 1;
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    assert_eq!(a.root.handle.serial, u64::MAX);
    assert_eq!(owner.next_serial, 0, "SERIAL_EXHAUSTION must never wrap");
    let before = state.borrow().calls.len();
    assert_eq!(
        owner.lookup(PEER, a.session, a.root.handle, b"file", Rights::READ),
        Err(Error::Full)
    );
    assert_eq!(state.borrow().calls.len(), before);
    owner.close(PEER, a.session, a.root.handle).unwrap();
    owner.disconnect(PEER, a.session).unwrap();
    assert_eq!(owner.attach(PEER, Rights::ALL), Err(Error::Full));
    let (mut owner, _) = make(72);
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    owner.next_serial = u64::MAX;
    let f = file(&mut owner, a, Rights::READ);
    assert_eq!(f.handle.serial, u64::MAX);
    assert_eq!(owner.next_serial, 0);
}

#[test]
fn provider_admission_failure_and_drop_own_one_cleanup() {
    for mode in 0..4 {
        let state = Rc::new(RefCell::new(State::default()));
        state.borrow_mut().root_error = mode == 1;
        state.borrow_mut().bad_root = mode == 2;
        let epoch = if mode == 3 { 0 } else { 81 };
        let owner = Owner::new(Provider(state.clone()), epoch);
        if mode != 0 {
            assert!(owner.is_err());
        }
        drop(owner);
        assert_eq!(
            state.borrow().drops,
            1,
            "BACKEND_LIFETIME construction/drop closes once"
        );
    }
    let (mut owner, state) = make(82);
    assert_eq!(owner.attach(0, Rights::ALL), Err(Error::Invalid));
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    for bad in [false, true] {
        state.borrow_mut().lookup_error = !bad;
        state.borrow_mut().bad_lookup = bad;
        let serial = owner.next_serial;
        for _ in 0..32 {
            assert!(
                owner
                    .lookup(PEER, a.session, a.root.handle, b"file", Rights::READ)
                    .is_err(),
                "FAILED_LOOKUP no invalid metadata publication"
            );
        }
        assert_eq!(owner.next_serial, serial);
        assert_eq!(
            owner.handles.iter().filter(|h| h.is_some()).count(),
            1,
            "FAILED_LOOKUP no published slot"
        );
    }
    state.borrow_mut().bad_lookup = false;
    file(&mut owner, a, Rights::READ);
}

#[test]
fn same_peer_old_session_reuse_does_not_authorize_fresh_root() {
    let (mut owner, state) = make(91);
    let mut old = Vec::new();
    for _ in 0..64 {
        let a = owner.attach(PEER, Rights::ALL).unwrap();
        for previous in &old {
            assert_eq!(
                owner.lookup(PEER, *previous, a.root.handle, b"file", Rights::READ),
                Err(Error::Stale)
            );
        }
        owner.disconnect(PEER, a.session).unwrap();
        old.push(a.session);
    }
    assert_eq!(state.borrow().calls, ["root"]);
}

#[test]
fn full_handle_table_attach_and_forged_tokens_have_no_effect() {
    let (mut owner, state) = make(101);
    let a = owner.attach(PEER, Rights::ALL).unwrap();
    let f = file(&mut owner, a, Rights::READ);
    let before = state.borrow().calls.len();
    for session in [
        Session {
            epoch: 0,
            serial: a.session.serial,
        },
        Session {
            epoch: 101,
            serial: 0,
        },
        Session {
            epoch: 101,
            serial: u64::MAX,
        },
    ] {
        denied_read(&mut owner, PEER, session, f.handle, Error::Stale);
    }
    for handle in [
        Handle {
            epoch: 0,
            serial: f.handle.serial,
        },
        Handle {
            epoch: 101,
            serial: 0,
        },
        Handle {
            epoch: 101,
            serial: 34,
        },
        Handle {
            epoch: 101,
            serial: u64::MAX,
        },
    ] {
        denied_read(&mut owner, PEER, a.session, handle, Error::Stale);
    }
    assert_eq!(state.borrow().calls.len(), before);
    for _ in 2..MAX_HANDLES {
        file(&mut owner, a, Rights::READ);
    }
    let serial = owner.next_serial;
    assert_eq!(owner.attach(OTHER, Rights::ALL), Err(Error::Full));
    assert_eq!(owner.connections.iter().filter(|c| c.is_some()).count(), 1);
    assert_eq!(owner.next_serial, serial);
}
