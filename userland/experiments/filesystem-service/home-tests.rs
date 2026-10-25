// SPDX-License-Identifier: BSD-2-Clause
//! Bounded trusted home delegation over the real owner ledger; no native claim.
use super::*;
use std::{cell::RefCell, rc::Rc, vec::Vec};

#[derive(Clone, Default, Debug, PartialEq, Eq)]
struct State {
    lookups: usize,
    writes: usize,
    mutations: usize,
    clocks: usize,
    drops: usize,
    lost: bool,
    created: bool,
    bytes: [u8; 16],
    length: usize,
}
type Shared = Rc<RefCell<State>>;
struct Graph(Shared);
struct Time(Shared);
type Service = Owner<Graph, Time>;

fn node(id: u64, state: &State) -> Node {
    Node::new(
        id,
        id + 10,
        match id {
            2 => 2 + u64::from(state.created),
            4 => state.length as u64,
            _ => 2,
        },
        if matches!(id, 4 | 5) {
            Kind::File
        } else {
            Kind::Directory
        },
    )
}
impl Drop for Graph {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
impl Backend for Graph {
    fn root(&mut self) -> Result<Node, Error> {
        Ok(node(1, &self.0.borrow()))
    }
    fn directory(&mut self, directory: Node) -> Result<Node, Error> {
        Ok(node(directory.object, &self.0.borrow()))
    }
    fn lookup(&mut self, directory: Node, name: &[u8]) -> Result<Node, Error> {
        let mut state = self.0.borrow_mut();
        state.lookups += 1;
        let id = match (directory.object, name) {
            (1, b"home") => 2,
            (1, b"root-alias") => 1,
            (1, b"system") => 5,
            (2, b"nested") => 3,
            (2 | 3, b"data") => 4,
            (2, b"created") if state.created => 4,
            _ => return Err(Error::Backend(2)),
        };
        Ok(node(id, &state))
    }
    fn read(&mut self, file: Node, offset: u64, out: &mut [u8]) -> Result<usize, Error> {
        assert_eq!(file.object, 4);
        let state = self.0.borrow();
        let start = (offset as usize).min(state.length);
        let count = out.len().min(state.length - start);
        out[..count].copy_from_slice(&state.bytes[start..start + count]);
        Ok(count)
    }
    fn write(&mut self, file: Node, offset: u64, bytes: &[u8], _: Utc) -> Result<Completion, Lost> {
        assert_eq!(file.object, 4, "SYSTEM_WRITE_REACHED_PROVIDER");
        let mut state = self.0.borrow_mut();
        state.writes += 1;
        if state.lost {
            return Err(Lost);
        }
        let start = offset as usize;
        let end = start + bytes.len();
        state.bytes[start..end].copy_from_slice(bytes);
        state.length = state.length.max(end);
        Ok(Completion {
            error: 0,
            txg: state.writes as u64,
            bytes_staged: bytes.len() as u64,
            state: 2,
        })
    }
    fn mutate(
        &mut self,
        directory: Node,
        operation: Namespace<'_>,
        _: Utc,
    ) -> Result<Completion, Lost> {
        assert_eq!(directory.object, 2, "SYSTEM_MUTATION_REACHED_PROVIDER");
        let Namespace::Create { name, uid, gid } = operation else {
            panic!("unexpected test mutation")
        };
        assert_eq!((name, uid, gid), (b"created".as_slice(), 1000, 1000));
        let mut state = self.0.borrow_mut();
        state.mutations += 1;
        state.created = true;
        Ok(Completion {
            error: 0,
            txg: state.mutations as u64,
            bytes_staged: 0,
            state: 2,
        })
    }
    fn directory_context(
        &mut self,
        root: Node,
        directory: Node,
        out: &mut [u8; 256],
    ) -> Result<(Node, usize), Error> {
        assert_eq!(root.identity(), (1, 11));
        let (parent, path) = match directory.object {
            1 => (1, b"/\0".as_slice()),
            2 => (1, b"/home\0".as_slice()),
            3 => (2, b"/home/nested\0".as_slice()),
            _ => return Err(Error::NotDirectory),
        };
        out[..path.len()].copy_from_slice(path);
        Ok((node(parent, &self.0.borrow()), path.len()))
    }
}
impl Clock for Time {
    fn utc(&mut self) -> Result<Utc, Error> {
        self.0.borrow_mut().clocks += 1;
        Ok(Utc {
            seconds: 1_792_800_000,
            nanoseconds: 7,
        })
    }
}
fn rights(bits: u8) -> Rights {
    Rights::new(bits).unwrap()
}
fn setup() -> (Service, Attachment, Entry, Shared) {
    let state = Rc::new(RefCell::new(State::default()));
    let mut owner = Owner::new(Graph(state.clone()), Time(state.clone()), 91)
        .unwrap()
        .with_namespace_identity(Identity::new(1000, 1000).unwrap());
    let source = owner.attach(7, Rights::ALL).unwrap();
    let home = owner
        .lookup(7, source.session, source.root.handle, b"home", Rights::ALL)
        .unwrap();
    (owner, source, home, state)
}
// Exact ledger snapshot makes partial publication and serial consumption visible.
fn ledger(owner: &Service) -> Vec<u64> {
    let mut values = std::vec![owner.next_serial];
    for connection in owner.connections {
        values.extend(connection.map_or([0; 2], |c| [c.serial, c.peer]));
    }
    for handle in owner.handles {
        values.extend(handle.map_or([0; 7], |h| {
            [
                h.serial,
                h.session,
                h.node.object,
                h.node.generation,
                h.node.size,
                h.node.kind as u64,
                u64::from(h.rights.0),
            ]
        }));
    }
    values
}

#[test]
fn provision_derives_exact_home_without_backend_work_or_metadata_authority() {
    let (mut owner, source, home, state) = setup();
    let before = state.borrow().clone();
    let next = owner.next_serial;
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    assert_eq!(*state.borrow(), before, "HOME_PROVISION_NO_PROVIDER");
    assert_eq!(owner.next_serial, next + 3);
    assert_ne!(target.session, source.session);
    assert_ne!(target.home.handle, home.handle);
    for (entry, identity, bits) in [(target.root, (1, 11), 3), (target.home, (2, 12), 15)] {
        let index = owner.open(8, target.session, entry.handle).unwrap();
        let opened = owner.handles[index].unwrap();
        assert_eq!(opened.node.identity(), identity, "HOME_EXACT_OBJECT");
        assert_eq!(opened.rights, rights(bits), "HOME_EXACT_RIGHTS");
        assert_eq!(
            owner.metadata(8, target.session, entry.handle),
            Err(Error::Denied),
            "HOME_NO_METADATA"
        );
    }
}

#[test]
fn home_create_write_and_read_work_while_system_and_read_aliases_are_denied() {
    let (mut owner, source, home, state) = setup();
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    owner
        .namespace(
            8,
            target.session,
            target.home.handle,
            Mutation::Create(b"created"),
        )
        .unwrap();
    let file = owner
        .lookup(8, target.session, target.home.handle, b"created", rights(6))
        .unwrap();
    owner
        .write(8, target.session, file.handle, 0, b"home")
        .unwrap();
    let mut out = [0; MAX_READ];
    assert_eq!(
        owner.read(8, target.session, file.handle, 0, 4, &mut out),
        Ok(4)
    );
    assert_eq!(&out[..4], b"home");
    let read_home = owner
        .lookup(8, target.session, target.root.handle, b"home", rights(3))
        .unwrap();
    assert_ne!(read_home.handle, target.home.handle);
    let read_file = owner
        .lookup(8, target.session, read_home.handle, b"data", Rights::READ)
        .unwrap();
    let system_file = owner
        .lookup(
            8,
            target.session,
            target.root.handle,
            b"system",
            Rights::READ,
        )
        .unwrap();
    let before = state.borrow().clone();
    for directory in [target.root.handle, read_home.handle] {
        assert_eq!(
            owner.namespace(8, target.session, directory, Mutation::Create(b"created")),
            Err(Error::Denied)
        );
        assert_eq!(
            owner.lookup(8, target.session, directory, b"home", rights(15)),
            Err(Error::Denied)
        );
    }
    for handle in [read_file.handle, system_file.handle] {
        assert_eq!(
            owner.write(8, target.session, handle, 0, b"bad"),
            Err(Error::Denied)
        );
    }
    assert_eq!(*state.borrow(), before, "HOME_DENIAL_NO_PROVIDER_EFFECT");
}

#[test]
fn parent_handles_remain_read_only_inside_and_outside_home() {
    let (mut owner, source, home, state) = setup();
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    let nested = owner
        .lookup(8, target.session, target.home.handle, b"nested", rights(15))
        .unwrap();
    let mut path = [0; 256];
    let parent = owner
        .parent_directory(8, target.session, nested.handle, &mut path)
        .unwrap();
    assert_ne!(parent.handle, target.home.handle);
    assert_eq!(&path[..13], b"/home/nested\0");
    let root = owner
        .parent_directory(8, target.session, target.home.handle, &mut path)
        .unwrap();
    assert_eq!(root.handle, target.root.handle);
    let before = state.borrow().clone();
    for directory in [parent.handle, root.handle] {
        assert_eq!(
            owner.namespace(8, target.session, directory, Mutation::Create(b"created")),
            Err(Error::Denied),
            "HOME_PARENT_READ_ONLY"
        );
    }
    assert_eq!(*state.borrow(), before);
}

#[test]
fn every_missing_source_right_rejects_without_publication() {
    for missing in [1, 2, 4, 8] {
        let (mut owner, source, _, state) = setup();
        let limited = owner
            .lookup(
                7,
                source.session,
                source.root.handle,
                b"home",
                rights(15 & !missing),
            )
            .unwrap();
        let before = ledger(&owner);
        let effects = state.borrow().clone();
        assert_eq!(
            owner.attach_home(7, source.session, limited.handle, 8),
            Err(Error::Denied),
            "HOME_SOURCE_RIGHT_REQUIRED"
        );
        assert_eq!(ledger(&owner), before);
        assert_eq!(*state.borrow(), effects);
    }
}

#[test]
fn root_identity_file_and_zero_recipient_reject_without_publication() {
    let (mut owner, source, home, state) = setup();
    let alias = owner
        .lookup(
            7,
            source.session,
            source.root.handle,
            b"root-alias",
            rights(15),
        )
        .unwrap();
    let file = owner
        .lookup(7, source.session, home.handle, b"data", rights(7))
        .unwrap();
    for (handle, peer, error) in [
        (source.root.handle, 8, Error::Denied),
        (alias.handle, 8, Error::Denied),
        (file.handle, 8, Error::NotDirectory),
        (home.handle, 0, Error::Invalid),
    ] {
        let before = ledger(&owner);
        let effects = state.borrow().clone();
        assert_eq!(
            owner.attach_home(7, source.session, handle, peer),
            Err(error)
        );
        assert_eq!(ledger(&owner), before);
        assert_eq!(*state.borrow(), effects);
    }
}

#[test]
fn wrong_peer_session_epoch_and_closed_sources_reject_atomically() {
    let (mut owner, source, home, _) = setup();
    let other = owner.attach(9, Rights::ALL).unwrap();
    for (peer, session, handle, error) in [
        (8, source.session, home.handle, Error::Denied),
        (9, other.session, home.handle, Error::Denied),
        (
            7,
            Session {
                epoch: 90,
                ..source.session
            },
            home.handle,
            Error::Stale,
        ),
        (
            7,
            Session {
                serial: 999,
                ..source.session
            },
            home.handle,
            Error::Stale,
        ),
        (
            7,
            source.session,
            Handle {
                epoch: 90,
                ..home.handle
            },
            Error::Stale,
        ),
        (
            7,
            source.session,
            Handle {
                serial: 999,
                ..home.handle
            },
            Error::Stale,
        ),
    ] {
        let before = ledger(&owner);
        assert_eq!(owner.attach_home(peer, session, handle, 10), Err(error));
        assert_eq!(ledger(&owner), before);
    }
    owner.close(7, source.session, home.handle).unwrap();
    let before = ledger(&owner);
    assert_eq!(
        owner.attach_home(7, source.session, home.handle, 10),
        Err(Error::Stale)
    );
    assert_eq!(ledger(&owner), before);
    owner.disconnect(7, source.session).unwrap();
    let before = ledger(&owner);
    assert_eq!(
        owner.attach_home(7, source.session, home.handle, 10),
        Err(Error::Stale)
    );
    assert_eq!(ledger(&owner), before);
}

#[test]
fn connection_exhaustion_never_publishes_handles_or_consumes_serials() {
    let (mut owner, source, home, _) = setup();
    for peer in 8..11 {
        owner.attach(peer, Rights::READ).unwrap();
    }
    let before = ledger(&owner);
    assert_eq!(
        owner.attach_home(7, source.session, home.handle, 11),
        Err(Error::Full)
    );
    assert_eq!(ledger(&owner), before, "HOME_FULL_CONNECTION_ATOMIC");
}

#[test]
fn fewer_than_two_handle_slots_never_partially_publish() {
    for free in [0, 1] {
        let (mut owner, source, home, _) = setup();
        while owner.handles.iter().filter(|h| h.is_none()).count() > free {
            owner
                .lookup(7, source.session, home.handle, b"data", Rights::READ)
                .unwrap();
        }
        let before = ledger(&owner);
        assert_eq!(
            owner.attach_home(7, source.session, home.handle, 8),
            Err(Error::Full)
        );
        assert_eq!(ledger(&owner), before, "HOME_TWO_SLOTS_ATOMIC");
    }
}

#[test]
fn three_serial_reservation_never_wraps_or_partially_publishes() {
    for serial in [0, u64::MAX - 1, u64::MAX] {
        let (mut owner, source, home, _) = setup();
        owner.next_serial = serial;
        let before = ledger(&owner);
        assert_eq!(
            owner.attach_home(7, source.session, home.handle, 8),
            Err(Error::Full)
        );
        assert_eq!(ledger(&owner), before, "HOME_THREE_SERIALS_ATOMIC");
    }
    let (mut owner, source, home, _) = setup();
    owner.next_serial = u64::MAX - 2;
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    assert_eq!(target.session.serial, u64::MAX - 2);
    assert_eq!(target.root.handle.serial, u64::MAX - 1);
    assert_eq!(target.home.handle.serial, u64::MAX);
    assert_eq!(owner.next_serial, 0);
    owner.disconnect(8, target.session).unwrap();
    let before = ledger(&owner);
    assert_eq!(
        owner.attach_home(7, source.session, home.handle, 8),
        Err(Error::Full)
    );
    assert_eq!(ledger(&owner), before);
}

#[test]
fn source_close_and_disconnect_do_not_revoke_the_recipient() {
    let (mut owner, source, home, _) = setup();
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    owner.close(7, source.session, home.handle).unwrap();
    owner.disconnect(7, source.session).unwrap();
    owner
        .namespace(
            8,
            target.session,
            target.home.handle,
            Mutation::Create(b"created"),
        )
        .unwrap();
    assert!(owner.stat(8, target.session, target.root.handle).is_ok());
    let onward = owner
        .attach_home(8, target.session, target.home.handle, 9)
        .unwrap();
    owner.disconnect(8, target.session).unwrap();
    assert!(owner.stat(9, onward.session, onward.home.handle).is_ok());
}

#[test]
fn recipient_disconnect_closes_both_handles_and_slot_reuse_stays_stale() {
    let (mut owner, source, home, _) = setup();
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    owner.disconnect(8, target.session).unwrap();
    assert!(owner
        .handles
        .iter()
        .flatten()
        .all(|h| h.session != target.session.serial));
    let replacement = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    assert_ne!(replacement.session, target.session);
    for handle in [target.root.handle, target.home.handle] {
        assert_eq!(owner.stat(8, target.session, handle), Err(Error::Stale));
        assert_eq!(
            owner.stat(8, replacement.session, handle),
            Err(Error::Stale)
        );
    }
    assert!(owner.stat(7, source.session, home.handle).is_ok());
}

#[test]
fn uncertain_write_retires_source_and_recipient_once_without_replay() {
    let (mut owner, source, home, state) = setup();
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    let file = owner
        .lookup(8, target.session, target.home.handle, b"data", rights(6))
        .unwrap();
    state.borrow_mut().lost = true;
    assert_eq!(
        owner.write(8, target.session, file.handle, 0, b"x"),
        Err(Error::Uncertain)
    );
    assert_eq!(
        owner.stat(7, source.session, home.handle),
        Err(Error::Poisoned)
    );
    assert_eq!(
        owner.stat(8, target.session, target.root.handle),
        Err(Error::Poisoned)
    );
    assert_eq!(
        owner.attach_home(7, source.session, home.handle, 9),
        Err(Error::Poisoned)
    );
    assert_eq!(
        owner.write(8, target.session, file.handle, 0, b"x"),
        Err(Error::Poisoned)
    );
    assert_eq!((state.borrow().writes, state.borrow().drops), (1, 1));
    owner.shutdown();
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn shutdown_closes_every_grant_and_backend_once() {
    let (mut owner, source, home, state) = setup();
    let target = owner
        .attach_home(7, source.session, home.handle, 8)
        .unwrap();
    owner.shutdown();
    assert_eq!(
        owner.stat(8, target.session, target.home.handle),
        Err(Error::Closed)
    );
    assert_eq!(
        owner.stat(8, target.session, target.root.handle),
        Err(Error::Closed)
    );
    assert_eq!(
        owner.attach_home(7, source.session, home.handle, 9),
        Err(Error::Closed)
    );
    assert_eq!(state.borrow().drops, 1);
    owner.shutdown();
    assert_eq!(state.borrow().drops, 1);
}
