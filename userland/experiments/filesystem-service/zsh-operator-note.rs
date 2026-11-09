// SPDX-License-Identifier: BSD-2-Clause
//! One absolute scratch path in the parent view. Alias/offset custody stays in
//! the sole description table, independently of the immutable startup profile.
use super::*;
use filesystem_client::{MutationFailure, NamespaceMutation};

pub(super) const ENTRY: &[u8] = b"/home/note";
pub(super) const LIMIT: usize = 256;
const NAME: &[u8] = b"note";
const NONE: u8 = u8::MAX;
type Mutation = (
    descriptions::Result<u64, Error>,
    u64,
    Option<MutationFailure>,
);

pub(super) struct Scratch {
    description: u8,
    writable: bool,
    create_attempted: bool,
    write_attempted: bool,
}
impl Scratch {
    pub(super) const fn new() -> Self {
        Self {
            description: NONE,
            writable: false,
            create_attempted: false,
            write_attempted: false,
        }
    }
}

impl<T: Channel> Files<T> {
    pub fn scratch_active(&self) -> bool {
        self.scratch.description != NONE
    }

    pub(super) fn scratch_index(&self, view: usize, fd: i32) -> Option<usize> {
        let (_, descriptor) = self.descriptions.binding_in(view, fd).ok()?;
        (view == 0 && descriptor.description == self.scratch.description)
            .then_some(descriptor.description as usize)
    }

    pub(super) fn scratch_write_fd(&self, view: usize, fd: i32) -> bool {
        self.scratch.writable && self.scratch_index(view, fd).is_some()
    }

    pub(super) fn scratch_closed(&mut self, index: Option<usize>) {
        if index.is_some_and(|i| self.descriptions.descriptions[i].is_none()) {
            self.scratch.description = NONE;
            self.scratch.writable = false;
        }
    }

    pub(super) fn open_scratch_read(
        &mut self,
        view: usize,
        cloexec: bool,
    ) -> descriptions::Result<i32, Error> {
        if view != 0 {
            return Err(Failure::Source(Error::Remote(-13)));
        }
        if self.scratch_active() {
            return Err(Failure::Source(Error::Remote(-16)));
        }
        let fd = self.descriptions.open_read_using(view, cloexec, |source| {
            let client = &mut source.client;
            let entry = client.lookup(client.home()?, NAME, 2)?;
            if entry.kind != Kind::File || entry.size > LIMIT as u64 {
                client.close(entry.handle)?;
                return Err(Error::Invalid);
            }
            Ok(entry.handle)
        })?;
        self.scratch.description = self.descriptions.binding_in(view, fd)?.1.description;
        Ok(fd)
    }

    /// A successful acquisition needs a future source close; reserve it before
    /// lookup. CREATE has a separate existence lookup before any mutation.
    pub(super) fn scratch_create(&mut self, cloexec: bool, funded: bool) -> Mutation {
        let mut failure: Option<MutationFailure> = None;
        let mut txg = 0;
        let scratch = &mut self.scratch;
        let result = self.descriptions.open_read_using(0, cloexec, |source| {
            let client = &mut source.client;
            let home = client.home()?;
            client.preflight_lookup(home, NAME, 4)?;
            match client.lookup(home, NAME, 1) {
                Ok(entry) => {
                    client.close(entry.handle)?;
                    return Err(Error::Remote(-17));
                }
                Err(Error::Remote(-2)) => (),
                Err(error) => return Err(error),
            }
            if scratch.create_attempted || scratch.description != NONE {
                return Err(Error::Remote(-16));
            }
            if !funded {
                return Err(Error::Full);
            }
            scratch.create_attempted = true;
            let done = client
                .namespace(home, NamespaceMutation::Create(NAME))
                .map_err(|error| {
                    failure = Some(error);
                    error.error
                })?;
            txg = done.txg;
            let entry = client.lookup(home, NAME, 4)?;
            if entry.kind != Kind::File || entry.size != 0 {
                client.close(entry.handle)?;
                return Err(Error::Protocol);
            }
            Ok(entry.handle)
        });
        let result = match result {
            Ok(fd) => self.descriptions.binding_in(0, fd).map(|(_, binding)| {
                self.scratch.description = binding.description;
                self.scratch.writable = true;
                fd as u64
            }),
            Err(error) => Err(error),
        };
        (result, txg, failure)
    }

    pub(super) fn scratch_write(&mut self, fd: i32, data: &[u8]) -> Mutation {
        let Some(index) = self.scratch_index(0, fd) else {
            return (Err(Failure::BadFd), 0, None);
        };
        if !self.scratch.writable || self.scratch.write_attempted {
            return (Err(Failure::BadFd), 0, None);
        }
        let Some(file) = self.descriptions.descriptions[index] else {
            return (Err(Failure::BadFd), 0, None);
        };
        if file.offset != 0 {
            return (Err(Failure::Invalid), 0, None);
        }
        self.scratch.write_attempted = true;
        match self.descriptions.source.client.write(file.handle, 0, data) {
            Ok(done) => {
                let count = done.bytes as u64;
                self.descriptions.descriptions[index] = Some(descriptions::Description {
                    offset: count,
                    ..file
                });
                (Ok(count), done.txg, None)
            }
            Err(error) => (Err(Failure::Source(error.error)), 0, Some(error)),
        }
    }
}
