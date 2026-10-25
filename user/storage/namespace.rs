// SPDX-License-Identifier: BSD-2-Clause
//! Private serialized namespace owner. This is not an IPC or public SDK API.

#[path = "namespace-wire.rs"]
pub mod wire;

pub const MAX_CONNECTIONS: usize = 4;
pub const MAX_HANDLES: usize = 16;
pub const MAX_READ: usize = 4096;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
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

    fn valid(self) -> bool {
        self.object != 0 && self.generation != 0
    }
}

/// Trusted synchronous provider; borrows may not escape a call. Its Drop owns
/// context cleanup. A future C bridge must preserve the SPA borrow through Drop.
pub trait Backend {
    fn root(&mut self) -> Result<Node, Error>;
    fn lookup(&mut self, directory: Node, name: &[u8]) -> Result<Node, Error>;
    fn read(&mut self, file: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error>;
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Rights(u8);

impl Rights {
    pub const LOOKUP: Self = Self(1);
    pub const READ: Self = Self(2);
    pub const ALL: Self = Self(3);

    pub fn new(bits: u8) -> Result<Self, Error> {
        if bits == 0 || bits & !Self::ALL.0 != 0 {
            return Err(Error::Invalid);
        }
        Ok(Self(bits))
    }

    fn contains(self, required: Self) -> bool {
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

pub struct Owner<B: Backend> {
    backend: Option<B>,
    root: Node,
    epoch: u64,
    // Zero means permanently exhausted, never a wrapping/reusable serial.
    next_serial: u64,
    connections: [Option<Connection>; MAX_CONNECTIONS],
    handles: [Option<Open>; MAX_HANDLES],
}

impl<B: Backend> Drop for Owner<B> {
    fn drop(&mut self) {
        self.shutdown();
    }
}

impl<B: Backend> Owner<B> {
    /// Trusted provisioning only: epoch is nonzero and never reused at this
    /// enforcing endpoint. The caller retains endpoint/generation provenance.
    pub fn new(mut backend: B, epoch: u64) -> Result<Self, Error> {
        if epoch == 0 {
            return Err(Error::Invalid);
        }
        let root = backend.root()?;
        if !root.valid() || root.kind != Kind::Directory {
            return Err(Error::InvalidMetadata);
        }
        Ok(Self {
            backend: Some(backend),
            root,
            epoch,
            next_serial: 1,
            connections: [None; MAX_CONNECTIONS],
            handles: [None; MAX_HANDLES],
        })
    }

    fn active(&self) -> Result<(), Error> {
        if self.backend.is_none() {
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
#[cfg(test)]
#[path = "../../tests/fixtures/namespace_owner.rs"]
mod tests;
