// SPDX-License-Identifier: BSD-2-Clause
//! Private userland filesystem policy, derived from the pinned readonly owner.
//! No native bridge or client wire is selected by this module.
#![no_std]
#[cfg(all(fs_namespace, fs_lifetimes, not(fs_mixed)))]
compile_error!("namespace and lifetime profiles are exclusive");
#[cfg(all(fs_mixed, not(all(fs_namespace, fs_lifetimes))))]
compile_error!("mixed requires namespace and lifetime profiles");
#[cfg(fs_namespace)]
#[path = "namespace-policy.rs"]
mod namespace_policy;
#[cfg(fs_home_native)]
pub use namespace_policy::NamespaceObservation;
#[cfg(fs_mixed)]
pub use namespace_policy::{CreatedAcquisition, CreatedMutation, CreatingBackend, Creation};
#[cfg(fs_namespace)]
pub use namespace_policy::{Identity, Mutation, Namespace};
#[cfg(all(
    fs_home_native,
    not(all(fs_home, fs_runtime, fs_mixed, fs_namespace, fs_directories))
))]
compile_error!("fs_home_native requires matched home runtime namespace policy");
#[cfg(fs_metadata)]
#[path = "metadata-policy.rs"]
mod metadata_policy;
#[cfg(fs_metadata)]
pub use filesystem_metadata::Metadata;
#[cfg(all(fs_metadata, not(fs_directories)))]
compile_error!("fs_metadata requires the separate directory service selection");

pub const MAX_CONNECTIONS: usize = 4;
pub const MAX_HANDLES: usize = 16;
// Representation exhaustion is permanent; only the separate runtime selection
// replaces the experimental cumulative eight-call allowance.
#[cfg(fs_runtime)]
pub type MutationCount = usize;
#[cfg(not(fs_runtime))]
pub type MutationCount = u8;
pub const MUTATION_LIMIT: MutationCount = if cfg!(fs_home_native) {
    9
} else if cfg!(fs_runtime) {
    MutationCount::MAX
} else {
    8
};
pub const MAX_READ: usize = 4096;

/// Trusted policy input, never accepted as client write fields.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Utc {
    pub seconds: u64,
    pub nanoseconds: u64,
}

pub trait Clock {
    fn utc(&mut self) -> Result<Utc, Error>;
}

/// Private engine progress; neither staged bytes nor state2 promise durability.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Completion {
    pub error: i32,
    pub txg: u64,
    pub bytes_staged: u64,
    pub state: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Lost;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Written {
    pub bytes: usize,
    pub assigned_txg: Option<u64>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    #[cfg(fs_metadata)]
    Unsupported,
    Invalid,
    Denied,
    Stale,
    Full,
    Closed,
    NotDirectory,
    IsDirectory,
    InvalidMetadata,
    InvalidCompletion,
    Backend(i32),
    Clock,
    WriteLimit,
    Poisoned,
    Uncertain,
    WriteFailed(Completion),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Directory,
    File,
}

/// Trusted backend identity, never included in client replies or accepted as authority.
#[derive(Clone, Copy)]
pub struct Node {
    object: u64,
    generation: u64,
    size: u64,
    kind: Kind,
}

impl Node {
    pub fn new(object: u64, generation: u64, size: u64, kind: Kind) -> Self {
        Self {
            object,
            generation,
            size,
            kind,
        }
    }

    pub fn identity(self) -> (u64, u64) {
        (self.object, self.generation)
    }

    #[cfg(fs_directories)]
    pub fn kind(self) -> Kind {
        self.kind
    }

    fn valid(self) -> bool {
        self.object != 0 && self.generation != 0
    }
}

/// Trusted synchronous provider; borrows may not escape a call. Its Drop owns
/// context cleanup. A future C bridge must preserve the SPA borrow through Drop.
pub trait Backend {
    #[cfg(fs_directory_contexts)]
    fn directory_context(
        &mut self,
        _root: Node,
        _directory: Node,
        _out: &mut [u8; 256],
    ) -> Result<(Node, usize), Error> {
        Err(Error::Unsupported)
    }
    /// Only a retained policy-authorized identity may enter this adapter.
    #[cfg(fs_metadata)]
    fn metadata(&mut self, _node: Node) -> Result<Metadata, Error> {
        Err(Error::Unsupported)
    }
    #[cfg(fs_namespace)]
    fn mutate(
        &mut self,
        directory: Node,
        operation: Namespace<'_>,
        utc: Utc,
    ) -> Result<Completion, Lost>;
    #[cfg(fs_directories)]
    fn directory(&mut self, _directory: Node) -> Result<Node, Error> {
        Err(Error::InvalidMetadata)
    }
    fn root(&mut self) -> Result<Node, Error>;
    fn lookup(&mut self, directory: Node, name: &[u8]) -> Result<Node, Error>;
    fn read(&mut self, file: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error>;
    /// Serialized synchronous provider. Input/context borrows cannot escape.
    /// Completion loss is uncertain even if the provider cannot report progress.
    /// Drop consumes the sole context before its SPA borrow can end.
    fn write(
        &mut self,
        file: Node,
        offset: u64,
        bytes: &[u8],
        utc: Utc,
    ) -> Result<Completion, Lost>;
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Rights(u8);

impl Rights {
    pub const LOOKUP: Self = Self(1);
    pub const READ: Self = Self(2);
    pub const WRITE: Self = Self(4);
    #[cfg(fs_namespace)]
    pub const MUTATE_DIR: Self = Self(8);
    #[cfg(fs_metadata)]
    pub const METADATA: Self = Self(16);
    #[cfg(fs_metadata)]
    pub const ALL: Self = Self(31);
    #[cfg(all(fs_namespace, not(fs_metadata)))]
    pub const ALL: Self = Self(15);
    #[cfg(not(fs_namespace))]
    pub const ALL: Self = Self(7);

    pub fn new(bits: u8) -> Result<Self, Error> {
        if bits == 0 || bits & !Self::ALL.0 != 0 {
            return Err(Error::Invalid);
        }
        Ok(Self(bits))
    }

    pub fn contains(self, required: Self) -> bool {
        self.0 & required.0 == required.0
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Session {
    epoch: u64,
    serial: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Handle {
    epoch: u64,
    serial: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Entry {
    pub handle: Handle,
    pub kind: Kind,
    pub size: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Attachment {
    pub session: Session,
    pub root: Entry,
}

#[derive(Clone, Copy)]
struct Connection {
    serial: u64,
    peer: u64,
}

#[derive(Clone, Copy)]
struct Open {
    serial: u64,
    session: u64,
    node: Node,
    rights: Rights,
}

pub struct Owner<B: Backend, C: Clock> {
    clock: C,
    poisoned: bool,
    write_used: bool,
    #[cfg(fs_lifetimes)]
    writes: MutationCount,
    #[cfg(fs_namespace)]
    identity: Option<Identity>,
    backend: Option<B>,
    root: Node,
    epoch: u64,
    // Zero means permanently exhausted, never a wrapping/reusable serial.
    next_serial: u64,
    connections: [Option<Connection>; MAX_CONNECTIONS],
    handles: [Option<Open>; MAX_HANDLES],
}

impl<B: Backend, C: Clock> Drop for Owner<B, C> {
    fn drop(&mut self) {
        self.shutdown();
    }
}

impl<B: Backend, C: Clock> Owner<B, C> {
    /// Trusted provisioning only: epoch is nonzero and never reused at this
    /// enforcing endpoint. The caller retains endpoint/generation provenance.
    pub fn new(mut backend: B, clock: C, epoch: u64) -> Result<Self, Error> {
        if epoch == 0 {
            return Err(Error::Invalid);
        }
        let root = backend.root()?;
        if !root.valid() || root.kind != Kind::Directory {
            return Err(Error::InvalidMetadata);
        }
        Ok(Self {
            clock,
            poisoned: false,
            write_used: false,
            #[cfg(fs_lifetimes)]
            writes: 0,
            #[cfg(fs_namespace)]
            identity: None,
            backend: Some(backend),
            root,
            epoch,
            next_serial: 1,
            connections: [None; MAX_CONNECTIONS],
            handles: [None; MAX_HANDLES],
        })
    }

    fn active(&self) -> Result<(), Error> {
        if self.poisoned {
            Err(Error::Poisoned)
        } else if self.backend.is_none() {
            Err(Error::Closed)
        } else {
            Ok(())
        }
    }

    // Reserve the complete request before publication; no serial is consumed on
    // exhaustion. Closing handles does not recover serial space.
    fn issue(&mut self, count: u64) -> Result<u64, Error> {
        if self.next_serial == 0 {
            return Err(Error::Full);
        }
        let last = self.next_serial.checked_add(count - 1).ok_or(Error::Full)?;
        let first = self.next_serial;
        self.next_serial = last.checked_add(1).unwrap_or(0);
        Ok(first)
    }

    fn entry(&self, serial: u64, node: Node) -> Entry {
        Entry {
            handle: Handle {
                epoch: self.epoch,
                serial,
            },
            kind: node.kind,
            size: node.size,
        }
    }

    /// Owner administration, never a client opcode. `peer` is the authenticated
    /// transport binding, not a deserialized request field, UID or PID.
    pub fn attach(&mut self, peer: u64, rights: Rights) -> Result<Attachment, Error> {
        self.active()?;
        if peer == 0 {
            return Err(Error::Invalid);
        }
        let connection = self
            .connections
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Full)?;
        let handle = self
            .handles
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Full)?;
        let serial = self.issue(2)?;
        self.connections[connection] = Some(Connection { serial, peer });
        self.handles[handle] = Some(Open {
            serial: serial + 1,
            session: serial,
            node: self.root,
            rights,
        });
        Ok(Attachment {
            session: Session {
                epoch: self.epoch,
                serial,
            },
            root: self.entry(serial + 1, self.root),
        })
    }

    fn connection(&self, peer: u64, session: Session) -> Result<usize, Error> {
        self.active()?;
        if session.epoch != self.epoch {
            return Err(Error::Stale);
        }
        let index = self
            .connections
            .iter()
            .position(|c| c.is_some_and(|c| c.serial == session.serial))
            .ok_or(Error::Stale)?;
        if self.connections[index].is_none_or(|c| c.peer != peer) {
            return Err(Error::Denied);
        }
        Ok(index)
    }

    fn open(&self, peer: u64, session: Session, handle: Handle) -> Result<usize, Error> {
        self.connection(peer, session)?;
        if handle.epoch != self.epoch {
            return Err(Error::Stale);
        }
        let index = self
            .handles
            .iter()
            .position(|h| h.is_some_and(|h| h.serial == handle.serial))
            .ok_or(Error::Stale)?;
        if self.handles[index].is_none_or(|h| h.session != session.serial) {
            return Err(Error::Denied);
        }
        Ok(index)
    }

    pub fn lookup(
        &mut self,
        peer: u64,
        session: Session,
        directory: Handle,
        name: &[u8],
        rights: Rights,
    ) -> Result<Entry, Error> {
        let index = self.open(peer, session, directory)?;
        let parent = self.handles[index].ok_or(Error::Stale)?;
        if !parent.rights.contains(Rights::LOOKUP) || !parent.rights.contains(rights) {
            return Err(Error::Denied);
        }
        if parent.node.kind != Kind::Directory {
            return Err(Error::NotDirectory);
        }
        if name.is_empty()
            || name.len() > 255
            || name == b"."
            || name == b".."
            || name.contains(&0)
            || name.contains(&b'/')
        {
            return Err(Error::Invalid);
        }
        let free = self
            .handles
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Full)?;
        if self.next_serial == 0 {
            return Err(Error::Full);
        }
        let node = self
            .backend
            .as_mut()
            .ok_or(Error::Closed)?
            .lookup(parent.node, name)?;
        if !node.valid() {
            return Err(Error::InvalidMetadata);
        }
        if self.handles.iter().flatten().any(|open| {
            open.node.identity() == node.identity()
                && (open.node.size != node.size || open.node.kind != node.kind)
        }) {
            self.retire();
            return Err(Error::InvalidMetadata);
        }
        #[cfg(fs_namespace)]
        if node.kind == Kind::File && rights.contains(Rights::MUTATE_DIR) {
            return Err(Error::Denied);
        }
        let serial = self.issue(1)?;
        self.handles[free] = Some(Open {
            serial,
            session: session.serial,
            node,
            rights,
        });
        Ok(self.entry(serial, node))
    }

    pub fn read(
        &mut self,
        peer: u64,
        session: Session,
        handle: Handle,
        offset: u64,
        length: usize,
        reply: &mut [u8; MAX_READ],
    ) -> Result<usize, Error> {
        reply.fill(0);
        let index = self.open(peer, session, handle)?;
        let file = self.handles[index].ok_or(Error::Stale)?;
        if !file.rights.contains(Rights::READ) {
            return Err(Error::Denied);
        }
        if file.node.kind != Kind::File {
            return Err(Error::IsDirectory);
        }
        if length > MAX_READ || offset.checked_add(length as u64).is_none() {
            return Err(Error::Invalid);
        }
        let expected = file.node.size.saturating_sub(offset).min(length as u64) as usize;
        let result = self.backend.as_mut().ok_or(Error::Closed)?.read(
            file.node,
            offset,
            &mut reply[..length],
        );
        match result {
            Ok(count) if count == expected => {
                reply[count..].fill(0);
                Ok(count)
            }
            other => {
                reply.fill(0);
                Err(match other {
                    Err(error) => error,
                    Ok(_) => Error::InvalidCompletion,
                })
            }
        }
    }

    pub fn close(&mut self, peer: u64, session: Session, handle: Handle) -> Result<(), Error> {
        let index = self.open(peer, session, handle)?;
        self.handles[index] = None;
        Ok(())
    }

    /// Current coherent size, rather than the caller's prior Entry snapshot.
    pub fn stat(&self, peer: u64, session: Session, handle: Handle) -> Result<Entry, Error> {
        let index = self.open(peer, session, handle)?;
        let file = self.handles[index].ok_or(Error::Stale)?;
        Ok(self.entry(file.serial, file.node))
    }

    fn retire(&mut self) {
        self.poisoned = true;
        self.shutdown();
    }

    /// Existing regular files only, no holes. One nonempty provider call per
    /// context mirrors current producer qualification; this is not sustained IO.
    /// Explicit offset avoids inventing shared POSIX file-description semantics.
    pub fn write(
        &mut self,
        peer: u64,
        session: Session,
        handle: Handle,
        offset: u64,
        bytes: &[u8],
    ) -> Result<Written, Error> {
        let index = self.open(peer, session, handle)?;
        let file = self.handles[index].ok_or(Error::Stale)?;
        if !file.rights.contains(Rights::WRITE) {
            return Err(Error::Denied);
        }
        if file.node.kind != Kind::File {
            return Err(Error::IsDirectory);
        }
        let end = offset
            .checked_add(bytes.len() as u64)
            .ok_or(Error::Invalid)?;
        if bytes.len() > MAX_READ || offset > file.node.size || end > i64::MAX as u64 {
            return Err(Error::Invalid);
        }
        if bytes.is_empty() {
            return Ok(Written {
                bytes: 0,
                assigned_txg: None,
            });
        }
        #[cfg(all(fs_lifetimes, not(fs_bulk)))]
        if bytes.len() != 16 {
            return Err(Error::Invalid);
        }
        #[cfg(fs_lifetimes)]
        if self.writes == MUTATION_LIMIT {
            return Err(Error::WriteLimit);
        }
        if self.write_used {
            return Err(Error::WriteLimit);
        }
        let utc = self.clock.utc()?;
        if utc.seconds > i64::MAX as u64 || utc.nanoseconds >= 1_000_000_000 {
            return Err(Error::Clock);
        }
        self.write_used = true;
        #[cfg(fs_lifetimes)]
        {
            self.writes += 1;
        }
        let completion = match self
            .backend
            .as_mut()
            .ok_or(Error::Closed)?
            .write(file.node, offset, bytes, utc)
        {
            Ok(value) => value,
            Err(Lost) => {
                self.retire();
                return Err(Error::Uncertain);
            }
        };
        let staged = completion.bytes_staged;
        if completion.error > 0 && completion.state == 0 && completion.txg == 0 && staged == 0 {
            // Known unassigned. The mixed profile still permanently retires its owner.
            #[cfg(fs_mixed)]
            self.retire();
            return Err(Error::Backend(completion.error));
        }
        if completion.error > 0
            && (completion.state == 1 || (cfg!(fs_lifetimes) && completion.state == 2))
            && (completion.txg > 0 || (cfg!(fs_mixed) && completion.state == 1))
            && (staged == 0 || staged == bytes.len() as u64)
        {
            self.retire();
            return Err(Error::WriteFailed(completion));
        }
        if completion.error != 0
            || completion.state != 2
            || completion.txg == 0
            || staged != bytes.len() as u64
        {
            self.retire();
            return Err(Error::InvalidCompletion);
        }
        // All sessions/rights aliases share a backend identity, not a handle's
        // private stale EOF. New opens still obtain current metadata from C.
        for open in self.handles.iter_mut().flatten() {
            if open.node.identity() == file.node.identity() {
                open.node.size = file.node.size.max(end);
            }
        }
        // The separately compiled lifetime bridge has consumed/retired its old
        // context and opened a fresh one before reporting success. The aggregate
        // eight-call counter never resets; errors never reach this publication.
        #[cfg(fs_lifetimes)]
        {
            self.write_used = false;
        }
        Ok(Written {
            bytes: bytes.len(),
            assigned_txg: Some(completion.txg),
        })
    }

    pub fn disconnect(&mut self, peer: u64, session: Session) -> Result<(), Error> {
        let index = self.connection(peer, session)?;
        for handle in &mut self.handles {
            if handle.is_some_and(|h| h.session == session.serial) {
                *handle = None;
            }
        }
        self.connections[index] = None;
        Ok(())
    }

    /// Exclusive borrow means no backend operation remains in flight. Revoke
    /// references before consuming the sole backend cleanup obligation.
    pub fn shutdown(&mut self) {
        self.handles.fill(None);
        self.connections.fill(None);
        drop(self.backend.take());
    }
}

#[cfg(test)]
extern crate std;
#[cfg(all(test, not(fs_runtime)))]
#[path = "tests.rs"]
mod tests;

#[cfg(all(test, fs_runtime))]
#[path = "runtime-counter-tests.rs"]
mod tests;

#[cfg(all(
    fs_directories,
    not(all(fs_names, fs_activation, fs_runtime, fs_bulk, fs_wait, fs_mixed))
))]
compile_error!("fs_directories requires names, activation and checked mixed lifetime");

#[cfg(fs_directory_contexts)]
#[path = "directory-context-policy.rs"]
mod directory_context;

#[cfg(all(fs_directory_contexts, not(fs_metadata)))]
compile_error!("fs_directory_contexts requires fs_metadata");

#[cfg(all(fs_home, not(fs_directory_contexts)))]
compile_error!("fs_home requires fs_directory_contexts");

#[cfg(fs_home)]
#[path = "home-policy.rs"]
mod home_policy;
#[cfg(fs_home)]
pub use home_policy::HomeAttachment;

#[cfg(all(test, fs_home))]
#[path = "home-tests.rs"]
mod home_tests;

#[cfg(all(test, fs_mixed, fs_runtime))]
mod created_admission_tests {
    use super::*;
    use std::{cell::Cell, rc::Rc};
    struct Provider(Rc<Cell<usize>>);
    impl Backend for Provider {
        fn root(&mut self) -> Result<Node, Error> {
            Ok(Node::new(34, 45, 2, Kind::Directory))
        }
        #[cfg(fs_directories)]
        fn directory(&mut self, node: Node) -> Result<Node, Error> {
            Ok(node)
        }
        fn lookup(&mut self, _: Node, _: &[u8]) -> Result<Node, Error> {
            Err(Error::Invalid)
        }
        fn read(&mut self, _: Node, _: u64, _: &mut [u8]) -> Result<usize, Error> {
            Err(Error::Invalid)
        }
        fn write(&mut self, _: Node, _: u64, _: &[u8], _: Utc) -> Result<Completion, Lost> {
            panic!("unexpected write")
        }
        fn mutate(&mut self, _: Node, _: Namespace<'_>, _: Utc) -> Result<Completion, Lost> {
            panic!("unexpected legacy mutation")
        }
    }
    impl CreatingBackend for Provider {
        fn create_identity(
            &mut self,
            _: Node,
            _: Creation<'_>,
            _: Identity,
            _: Utc,
        ) -> Result<CreatedMutation, Lost> {
            self.0.set(self.0.get() + 1);
            Err(Lost)
        }
    }
    struct Time;
    impl Clock for Time {
        fn utc(&mut self) -> Result<Utc, Error> {
            Ok(Utc {
                seconds: 1,
                nanoseconds: 0,
            })
        }
    }
    #[test]
    fn created_serial_and_mutation_exhaustion_precede_provider_effect() {
        for serial_exhausted in [true, false] {
            let calls = Rc::new(Cell::new(0));
            let mut owner = Owner::new(Provider(calls.clone()), Time, 7)
                .unwrap()
                .with_namespace_identity(Identity::new(1000, 1000).unwrap());
            let a = owner.attach(20, Rights::ALL).unwrap();
            if serial_exhausted {
                owner.next_serial = 0;
            } else {
                owner.writes = MUTATION_LIMIT;
            }
            assert_eq!(
                owner.create(
                    20,
                    a.session,
                    a.root.handle,
                    Creation::File(b"p"),
                    Rights::READ
                ),
                Err(if serial_exhausted {
                    Error::Full
                } else {
                    Error::WriteLimit
                })
            );
            assert_eq!(calls.get(), 0);
        }
    }
}
