// SPDX-License-Identifier: BSD-2-Clause
//! Private created-identity source-path tests; host fixtures are not native ZFS.
use filesystem_bridge::{RuntimeUtc, Spa, Zpl};
use filesystem_policy::{
    Attachment, Backend, Clock, Completion, CreatedMutation, CreatingBackend, Creation, Error,
    Handle, Identity, Kind, Lost, Node, Owner, Rights, Utc, MAX_HANDLES, MAX_READ,
};
use std::{cell::RefCell, ptr::NonNull, rc::Rc};

fn completed() -> Completion {
    Completion {
        error: 0,
        state: 2,
        txg: 788,
        bytes_staged: 0,
    }
}
fn actual(mode: u32, check: impl FnOnce(&mut Owner<Zpl<'_>, RuntimeUtc>, Attachment)) {
    super::reset(mode, &[]);
    let mut marker = 0u64;
    // SAFETY: serial typed host fixture, one exclusive SPA/context, immutable
    // dataset, and consuming Owner teardown before this backing expires.
    let mut spa = unsafe { Spa::from_raw(NonNull::from(&mut marker).cast()) };
    let mut owner = Owner::new(spa.open(c"testpool_zstd/x86_64").unwrap(), RuntimeUtc, 7)
        .unwrap()
        .with_namespace_identity(Identity::new(1000, 1000).unwrap());
    let attached = owner.attach(20, Rights::ALL).unwrap();
    check(&mut owner, attached);
    owner.shutdown();
    owner.shutdown();
    assert_eq!(super::count(0), super::count(1));
    assert_eq!(super::count(5), 0);
}

#[test]
fn created_real_file_and_retained_alias_lifetime() {
    actual(100, |owner, a| {
        let other = owner.attach(21, Rights::ALL).unwrap();
        let result = owner
            .create(
                20,
                a.session,
                a.root.handle,
                Creation::File(b"p"),
                Rights::READ,
            )
            .unwrap();
        assert_eq!(result.progress, Ok(completed()));
        let child = result.entry.unwrap();
        assert_eq!((child.kind, child.size), (Kind::File, 0));
        assert_eq!(
            owner.stat(20, a.session, a.root.handle).unwrap().size,
            if cfg!(fs_directories) { 3 } else { 2 }
        );
        assert_eq!(
            owner
                .stat(21, other.session, other.root.handle)
                .unwrap()
                .size,
            if cfg!(fs_directories) { 3 } else { 2 }
        );
        let late = owner.attach(22, Rights::ALL).unwrap();
        assert_eq!(
            owner.stat(22, late.session, late.root.handle).unwrap().size,
            if cfg!(fs_directories) { 3 } else { 2 }
        );
        assert_eq!(
            owner.write(20, a.session, child.handle, 0, &[1; 16]),
            Err(Error::Denied)
        );
        owner
            .namespace(
                20,
                a.session,
                a.root.handle,
                filesystem_policy::Mutation::Rename(b"p", b"q"),
            )
            .unwrap();
        let alias = owner
            .lookup(20, a.session, a.root.handle, b"q", Rights::READ)
            .unwrap();
        let mut out = [0; MAX_READ];
        assert_eq!(
            owner.read(20, a.session, child.handle, 0, 0, &mut out),
            Ok(0)
        );
        owner.close(20, a.session, child.handle).unwrap();
        assert_eq!(
            owner.read(20, a.session, alias.handle, 0, 0, &mut out),
            Ok(0)
        );
        owner.close(20, a.session, alias.handle).unwrap();
        assert_eq!(super::count(9), 1);
        assert_eq!(super::count(3), 2);
        owner.disconnect(20, a.session).unwrap();
        assert_eq!(owner.disconnect(20, a.session), Err(Error::Stale));
    });
}

#[test]
fn created_real_collision_never_replaces_or_retries() {
    actual(100, |owner, a| {
        owner
            .create(
                20,
                a.session,
                a.root.handle,
                Creation::File(b"p"),
                Rights::READ,
            )
            .unwrap()
            .entry
            .unwrap();
        let result = owner
            .create(
                20,
                a.session,
                a.root.handle,
                Creation::File(b"p"),
                Rights::READ,
            )
            .unwrap();
        assert_eq!(
            result.progress,
            Ok(Completion {
                error: 17,
                txg: 0,
                bytes_staged: 0,
                state: 0
            })
        );
        assert_eq!(result.entry, Err(Error::Backend(17)));
        assert_eq!(super::count(9), 2);
        assert_eq!(super::count(2), 1);
        assert_eq!(super::count(3), 1);
        assert!(owner.namespace_finished());
    });
}

fn acquisition_failure(mode: u32) -> Error {
    match mode {
        104 => Error::Backend(2),
        106 => Error::Backend(5),
        107 | 7 | 13 => Error::Closed,
        _ => Error::InvalidMetadata,
    }
}
#[test]
fn created_real_reopen_substitution_and_malformed_nodes_never_publish() {
    for mode in [
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        if cfg!(fs_directories) { 7 } else { 13 },
    ] {
        actual(mode, |owner, a| {
            let result = owner
                .create(
                    20,
                    a.session,
                    a.root.handle,
                    Creation::File(b"p"),
                    Rights::READ,
                )
                .unwrap();
            assert_eq!(
                result.progress,
                Ok(completed()),
                "mode {mode} must retain original completed progress"
            );
            assert_eq!(
                result.entry,
                Err(acquisition_failure(mode)),
                "mode {mode} must not publish a replacement or malformed node"
            );
            assert!(owner.namespace_finished());
            assert_eq!(super::count(9), 1);
        });
    }
}

#[cfg(fs_directories)]
#[test]
fn created_real_directory_retains_kind_and_authority() {
    actual(100, |owner, a| {
        let result = owner
            .create(
                20,
                a.session,
                a.root.handle,
                Creation::Directory(b"p"),
                Rights::ALL,
            )
            .unwrap();
        assert_eq!(result.progress, Ok(completed()));
        let child = result.entry.unwrap();
        assert_eq!((child.kind, child.size), (Kind::Directory, 2));
        assert_eq!(
            owner.read(20, a.session, child.handle, 0, 0, &mut [0; MAX_READ]),
            Err(Error::IsDirectory)
        );
        let nested = owner
            .create(
                20,
                a.session,
                child.handle,
                Creation::File(b"f"),
                Rights::READ,
            )
            .unwrap();
        assert!(nested.progress.is_ok());
        let nested = nested.entry.unwrap();
        assert_eq!(owner.stat(20, a.session, child.handle).unwrap().size, 3);
        owner.close(20, a.session, nested.handle).unwrap();
        owner.close(20, a.session, child.handle).unwrap();
        assert_eq!(super::count(9), 2);
    });
    for mode in [101, 102, 103, 104, 105, 106, 107, 108, 109, 7] {
        actual(mode, |owner, a| {
            let result = owner
                .create(
                    20,
                    a.session,
                    a.root.handle,
                    Creation::Directory(b"p"),
                    Rights::ALL,
                )
                .unwrap();
            assert_eq!(result.progress, Ok(completed()));
            assert_eq!(
                result.entry,
                Err(acquisition_failure(mode)),
                "directory mode {mode}"
            );
            assert_eq!(super::count(9), 1);
        });
    }
}

struct Control {
    progress: Result<Completion, Lost>,
    created: Option<Node>,
    candidate: Result<Node, Error>,
    parent: Node,
    calls: usize,
    drops: usize,
    closes: usize,
    bad_clock: bool,
}
impl Control {
    fn new() -> Self {
        let node = Node::new(90, 801, 0, Kind::File);
        Self {
            progress: Ok(completed()),
            created: Some(node),
            candidate: Ok(node),
            parent: Node::new(34, 45, 2, Kind::Directory),
            calls: 0,
            drops: 0,
            closes: 0,
            bad_clock: false,
        }
    }
}
struct Fake(Rc<RefCell<Control>>);
impl Drop for Fake {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
impl Backend for Fake {
    fn root(&mut self) -> Result<Node, Error> {
        Ok(self.0.borrow().parent)
    }
    #[cfg(fs_directories)]
    fn directory(&mut self, _: Node) -> Result<Node, Error> {
        self.root()
    }
    fn lookup(&mut self, _: Node, _: &[u8]) -> Result<Node, Error> {
        self.0.borrow().candidate
    }
    fn read(&mut self, _: Node, _: u64, _: &mut [u8]) -> Result<usize, Error> {
        Ok(0)
    }
    fn write(&mut self, _: Node, _: u64, _: &[u8], _: Utc) -> Result<Completion, Lost> {
        Err(Lost)
    }
    fn mutate(
        &mut self,
        _: Node,
        _: filesystem_policy::Namespace<'_>,
        _: Utc,
    ) -> Result<Completion, Lost> {
        panic!("new path must not call legacy mutate")
    }
}
impl CreatingBackend for Fake {
    fn create_identity(
        &mut self,
        _: Node,
        _: Creation<'_>,
        _: Identity,
        _: Utc,
    ) -> Result<CreatedMutation, Lost> {
        let mut c = self.0.borrow_mut();
        c.calls += 1;
        c.progress.map(|completion| CreatedMutation {
            completion,
            created: c.created,
        })
    }
}
struct Time(Rc<RefCell<Control>>);
impl Clock for Time {
    fn utc(&mut self) -> Result<Utc, Error> {
        Ok(Utc {
            seconds: 1791290040,
            nanoseconds: if self.0.borrow().bad_clock {
                1_000_000_000
            } else {
                123
            },
        })
    }
}
fn fake() -> (Owner<Fake, Time>, Attachment, Rc<RefCell<Control>>) {
    let c = Rc::new(RefCell::new(Control::new()));
    let mut owner = Owner::new(Fake(c.clone()), Time(c.clone()), 7)
        .unwrap()
        .with_namespace_identity(Identity::new(1000, 1000).unwrap());
    let a = owner.attach(20, Rights::ALL).unwrap();
    (owner, a, c)
}

#[test]
fn created_original_progress_is_independent_of_acquisition() {
    for progress in [
        Err(Lost),
        Ok(Completion {
            error: 17,
            state: 0,
            txg: 0,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 13,
            state: 0,
            txg: 0,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 13,
            state: 0,
            txg: 789,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 0,
            state: 1,
            txg: 789,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 5,
            state: 1,
            txg: 0,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 5,
            state: 1,
            txg: 789,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 5,
            state: 2,
            txg: 789,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 0,
            state: 2,
            txg: 0,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 0,
            state: 3,
            txg: 789,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: 0,
            state: 2,
            txg: 789,
            bytes_staged: 1,
        }),
        Ok(Completion {
            error: 5000,
            state: 0,
            txg: 0,
            bytes_staged: 0,
        }),
        Ok(Completion {
            error: -1,
            state: 0,
            txg: 0,
            bytes_staged: 0,
        }),
        Ok(completed()),
    ] {
        let (mut owner, a, c) = fake();
        c.borrow_mut().progress = progress;
        c.borrow_mut().created = None;
        let result = owner
            .create(
                20,
                a.session,
                a.root.handle,
                Creation::File(b"p"),
                Rights::READ,
            )
            .unwrap();
        assert_eq!(result.progress, progress);
        let expected = match progress {
            Err(Lost) => Error::Uncertain,
            Ok(value)
                if value.error > 0 && value.error <= 4095 && value.state == 0 && value.txg == 0 =>
            {
                Error::Backend(value.error)
            }
            Ok(value) if value.error == 5 => Error::WriteFailed(value),
            Ok(value) if value == completed() => Error::InvalidMetadata,
            _ => Error::InvalidCompletion,
        };
        assert_eq!(result.entry, Err(expected));
        owner.shutdown();
        owner.shutdown();
        assert_eq!((c.borrow().calls, c.borrow().drops), (1, 1));
    }
}

#[test]
fn created_exact_expected_identity_and_alias_metadata_are_enforced() {
    for candidate in [
        Ok(Node::new(91, 801, 0, Kind::File)),
        Ok(Node::new(90, 802, 0, Kind::File)),
        Ok(Node::new(90, 801, 0, Kind::Directory)),
        Ok(Node::new(0, 801, 0, Kind::File)),
        Ok(Node::new(90, 801, 9, Kind::File)),
        Err(Error::Backend(2)),
    ] {
        let (mut owner, a, c) = fake();
        c.borrow_mut().candidate = candidate;
        let result = owner
            .create(
                20,
                a.session,
                a.root.handle,
                Creation::File(b"p"),
                Rights::READ,
            )
            .unwrap();
        assert_eq!(result.progress, Ok(completed()));
        assert!(result.entry.is_err());
        assert!(owner.namespace_finished());
        assert_eq!(c.borrow().calls, 1);
    }
    let (mut owner, a, c) = fake();
    c.borrow_mut().candidate = Ok(Node::new(90, 801, 1, Kind::File));
    owner
        .lookup(20, a.session, a.root.handle, b"alias", Rights::READ)
        .unwrap();
    c.borrow_mut().candidate = Ok(Node::new(90, 801, 0, Kind::File));
    let result = owner
        .create(
            20,
            a.session,
            a.root.handle,
            Creation::File(b"p"),
            Rights::READ,
        )
        .unwrap();
    assert_eq!(result.progress, Ok(completed()));
    assert_eq!(result.entry, Err(Error::InvalidMetadata));
}

#[test]
fn created_preflight_denies_without_provider_dispatch() {
    for condition in 0..7 {
        let (mut owner, a, c) = fake();
        let mut parent = a.root.handle;
        let name = if condition == 0 {
            b"../p".as_slice()
        } else {
            b"p".as_slice()
        };
        if condition == 1 {
            c.borrow_mut().bad_clock = true;
        }
        if condition == 2 {
            c.borrow_mut().parent = Node::new(34, 46, 2, Kind::Directory);
        }
        if condition == 3 {
            owner.close(20, a.session, parent).unwrap();
        }
        if condition == 4 {
            parent = owner
                .lookup(20, a.session, parent, b"x", Rights::READ)
                .unwrap()
                .handle;
        }
        let rights = if condition == 5 {
            Rights::ALL
        } else {
            Rights::READ
        };
        let peer = if condition == 6 { 21 } else { 20 };
        assert!(owner
            .create(peer, a.session, parent, Creation::File(name), rights)
            .is_err());
        assert_eq!(c.borrow().calls, 0, "condition {condition}");
    }
    let (mut owner, a, c) = fake();
    let mut other = Owner::new(Fake(c.clone()), Time(c.clone()), 8).unwrap();
    let foreign = other.attach(20, Rights::ALL).unwrap();
    assert!(matches!(
        owner.create(
            20,
            foreign.session,
            a.root.handle,
            Creation::File(b"p"),
            Rights::READ
        ),
        Err(Error::Stale)
    ));
    assert_eq!(c.borrow().calls, 0);
    let absent = Rc::new(RefCell::new(Control::new()));
    let mut no_identity = Owner::new(Fake(absent.clone()), Time(absent.clone()), 7).unwrap();
    let root = no_identity.attach(20, Rights::ALL).unwrap();
    assert!(matches!(
        no_identity.create(
            20,
            root.session,
            root.root.handle,
            Creation::File(b"p"),
            Rights::READ
        ),
        Err(Error::Denied)
    ));
    assert_eq!(absent.borrow().calls, 0);
    let (mut owner, a, c) = fake();
    for _ in 1..MAX_HANDLES {
        owner
            .lookup(20, a.session, a.root.handle, b"x", Rights::READ)
            .unwrap();
    }
    assert!(matches!(
        owner.create(
            20,
            a.session,
            a.root.handle,
            Creation::File(b"p"),
            Rights::READ
        ),
        Err(Error::Full)
    ));
    assert_eq!(c.borrow().calls, 0);
}

// This host-only composition intentionally imports the complete maintained
// ledger; APIs outside this callback/alias test remain independently qualified.
#[allow(
    dead_code,
    reason = "Host-only inclusion of the complete existing descriptor ledger."
)]
#[path = "file-descriptions.rs"]
mod descriptions;
struct Store {
    owner: Owner<Fake, Time>,
    attached: Attachment,
    control: Rc<RefCell<Control>>,
}
impl descriptions::Store for Store {
    type Handle = Handle;
    type Error = Error;
    type Cleanup = ();
    fn open_read(&mut self, name: &[u8]) -> Result<Handle, Error> {
        self.owner
            .lookup(
                20,
                self.attached.session,
                self.attached.root.handle,
                name,
                Rights::READ,
            )
            .map(|v| v.handle)
    }
    fn read(
        &mut self,
        h: Handle,
        off: u64,
        len: usize,
        out: &mut [u8; MAX_READ],
    ) -> Result<usize, Error> {
        self.owner.read(20, self.attached.session, h, off, len, out)
    }
    fn size(&mut self, _: Handle) -> Result<u64, Error> {
        Ok(0)
    }
    fn close(&mut self, h: Handle) -> Result<(), Error> {
        self.control.borrow_mut().closes += 1;
        self.owner.close(20, self.attached.session, h)
    }
    fn failure_is_fatal(&self, _: Error) -> bool {
        false
    }
    fn retire(&mut self) {
        self.owner.shutdown();
    }
    fn disconnect(&mut self) -> Result<(), Error> {
        self.owner.disconnect(20, self.attached.session)
    }
}
#[test]
fn created_actual_descriptor_admission_suppresses_full_tables_and_closes_once() {
    for descriptions_full in [false, true] {
        let (owner, attached, control) = fake();
        let source = Store {
            owner,
            attached,
            control: control.clone(),
        };
        let mut files = descriptions::Descriptions::<_, 2>::from_source(source);
        let first = files.open_read_in(0, b"x", false).unwrap();
        for _ in 1..13 {
            if descriptions_full {
                files.open_read_in(0, b"x", false).unwrap();
            } else {
                files.duplicate_in(0, first, 3, false).unwrap();
            }
        }
        let view = usize::from(descriptions_full);
        let result = files.open_read_using(view, false, |store| {
            store
                .owner
                .create(
                    20,
                    store.attached.session,
                    store.attached.root.handle,
                    Creation::File(b"p"),
                    Rights::READ,
                )?
                .entry
                .map(|v| v.handle)
        });
        assert!(matches!(result, Err(descriptions::Failure::Full)));
        assert_eq!(control.borrow().calls, 0);
        if !descriptions_full {
            for fd in 3..15 {
                files.close_in(0, fd).unwrap();
            }
            assert_eq!(control.borrow().closes, 0);
            files.close_in(0, 15).unwrap();
            assert_eq!(control.borrow().closes, 1);
            let created = files
                .open_read_using(0, false, |store| {
                    store
                        .owner
                        .create(
                            20,
                            store.attached.session,
                            store.attached.root.handle,
                            Creation::File(b"p"),
                            Rights::READ,
                        )?
                        .entry
                        .map(|v| v.handle)
                })
                .unwrap();
            assert_eq!(control.borrow().calls, 1);
            files.close_in(0, created).unwrap();
        }
        files.disconnect().unwrap();
        assert_eq!(control.borrow().drops, 1);
    }
    let (owner, attached, control) = fake();
    control.borrow_mut().created = None;
    let mut files = descriptions::Descriptions::<_, 2>::from_source(Store {
        owner,
        attached,
        control: control.clone(),
    });
    let mut progress = None;
    let result = files.open_read_using(0, false, |store| {
        let result = store.owner.create(
            20,
            store.attached.session,
            store.attached.root.handle,
            Creation::File(b"p"),
            Rights::READ,
        )?;
        progress = Some(result.progress);
        result.entry.map(|value| value.handle)
    });
    assert_eq!(progress, Some(Ok(completed())));
    assert!(matches!(
        result,
        Err(descriptions::Failure::Source(Error::InvalidMetadata))
    ));
    assert!(files.descriptions.iter().all(Option::is_none));
    assert!(matches!(
        files.close_in(0, 3),
        Err(descriptions::Failure::BadFd)
    ));
    assert_eq!((control.borrow().calls, control.borrow().drops), (1, 1));
    drop(files);
    assert_eq!(control.borrow().drops, 1);
}
