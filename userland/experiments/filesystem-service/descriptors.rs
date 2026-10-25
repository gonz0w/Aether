// SPDX-License-Identifier: BSD-2-Clause
//! Owner-local adapter for the shared read-only description state.
#![no_std]
use filesystem_policy::{Attachment, Backend, Clock, Error, Handle, Kind, Owner, Rights, MAX_READ};
#[path = "file-descriptions.rs"]
mod descriptions;
use descriptions::Store;
pub use descriptions::{Seek, FIRST_FILE_FD, MAX_FDS};
pub type Failure = descriptions::Failure<Error>;
pub type Result<T> = descriptions::Result<T, Error>;
pub type Descriptors<B, C> = descriptions::Descriptions<Local<B, C>>;
const _: () = assert!((MAX_FDS - FIRST_FILE_FD) < filesystem_policy::MAX_HANDLES as i32);

/// Dedicated test/local context only; never take over a running server's Owner.
pub struct Local<B: Backend, C: Clock> {
    owner: Owner<B, C>,
    peer: u64,
    attachment: Attachment,
    retired: bool,
}
impl<B: Backend, C: Clock> Descriptors<B, C> {
    pub fn new(mut owner: Owner<B, C>, peer: u64) -> Result<Self> {
        let attachment = owner
            .attach(peer, Rights::new(3).map_err(Failure::Source)?)
            .map_err(Failure::Source)?;
        Ok(Self::from_source(Local {
            owner,
            peer,
            attachment,
            retired: false,
        }))
    }
}
impl<B: Backend, C: Clock> Store for Local<B, C> {
    type Handle = Handle;
    type Error = Error;
    type Cleanup = ();
    fn open_read(&mut self, name: &[u8]) -> core::result::Result<Handle, Error> {
        let entry = self.owner.lookup(
            self.peer,
            self.attachment.session,
            self.attachment.root.handle,
            name,
            Rights::READ,
        )?;
        if entry.kind != Kind::File {
            if let Err(error) = self
                .owner
                .close(self.peer, self.attachment.session, entry.handle)
            {
                self.retire();
                return Err(error);
            }
            return Err(Error::IsDirectory);
        }
        Ok(entry.handle)
    }
    fn read(
        &mut self,
        handle: Handle,
        offset: u64,
        length: usize,
        out: &mut [u8; MAX_READ],
    ) -> core::result::Result<usize, Error> {
        self.owner.read(
            self.peer,
            self.attachment.session,
            handle,
            offset,
            length,
            out,
        )
    }
    fn size(&mut self, handle: Handle) -> core::result::Result<u64, Error> {
        self.owner
            .stat(self.peer, self.attachment.session, handle)
            .map(|entry| entry.size)
    }
    fn close(&mut self, handle: Handle) -> core::result::Result<(), Error> {
        self.owner.close(self.peer, self.attachment.session, handle)
    }
    fn failure_is_fatal(&self, error: Error) -> bool {
        self.retired
            || matches!(
                error,
                Error::InvalidCompletion
                    | Error::InvalidMetadata
                    | Error::Poisoned
                    | Error::Closed
                    | Error::Stale
                    | Error::Uncertain
                    | Error::WriteFailed(_)
            )
            || matches!(error, Error::Backend(code) if code <= 0)
    }
    fn retire(&mut self) {
        self.retired = true;
        self.owner.shutdown();
    }
    fn disconnect(&mut self) -> core::result::Result<(), Error> {
        self.owner.disconnect(self.peer, self.attachment.session)
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "descriptor-tests.rs"]
mod tests;
