// SPDX-License-Identifier: BSD-2-Clause
//! Explicit home access and serialized shared-position writes; no FILE wire.
use super::*;
use filesystem_client::{Error, Kind, MutationCompletion, MutationOutcome};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HomeAccess {
    ReadOnly,
    WriteOnly,
    ReadWrite,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ProcessWriteFailure {
    pub error: ProcessError,
    pub outcome: MutationOutcome,
    pub cleanup: Option<[i64; 2]>,
    /// Selected shared position, retained even when retirement erases the view.
    pub offset: Option<u64>,
}
impl<T: Channel> ProcessFiles<T> {
    /// Trusted authenticated AF09 endpoints and nonreused epoch. Both greetings
    /// validate before publication; actual native admission stays caller-owned.
    pub fn connect_home(
        channel: T,
        epoch: u64,
    ) -> core::result::Result<Self, filesystem_client::ConnectFailure> {
        let client = filesystem_client::Client::connect_home(channel, epoch)?;
        Ok(Self {
            files: descriptions::Descriptions::from_source(Remote { client }),
            epoch,
            records: [Record {
                process: None,
                last_generation: 0,
                #[cfg(fs_cwd)]
                cwd: None,
            }; 4],
        })
    }

    /// Final caller storage; both AF09 greetings validate before publication.
    /// Failure drops the channel once and leaves no initialized caller value.
    #[cfg(fs_home_in_place)]
    pub fn connect_home_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
    ) -> core::result::Result<&mut Self, filesystem_client::ConnectFailure> {
        let files = Self::prepare_in_place(slot, epoch);
        descriptions::Descriptions::connect_home_in_place(files, channel, epoch)?;
        // SAFETY: the nested constructor initialized the sole owning field;
        // all process records and epoch were initialized before entering it.
        Ok(unsafe { slot.assume_init_mut() })
    }

    /// One existing component under the retained home; no creation or path policy.
    pub fn open_home_file(
        &mut self,
        process: Process,
        name: &[u8],
        access: HomeAccess,
        cloexec: bool,
    ) -> Result<i32> {
        let view = self.exact(process)?;
        let rights = match access {
            HomeAccess::ReadOnly => 2,
            HomeAccess::WriteOnly => 4,
            HomeAccess::ReadWrite => 6,
        };
        self.files
            .open_read_using(view, cloexec, |source| {
                let home = source.client.home()?;
                let entry = source.client.lookup(home, name, rights)?;
                if entry.kind != Kind::File {
                    source.client.close(entry.handle)?;
                    return Err(Error::Remote(-21));
                }
                Ok(entry.handle)
            })
            .map_err(ProcessError::Files)
    }

    fn write_failure(&self, error: ProcessError, offset: Option<u64>) -> ProcessWriteFailure {
        ProcessWriteFailure {
            error,
            outcome: MutationOutcome::NotSent,
            cleanup: self.cleanup(),
            offset,
        }
    }

    /// One explicit client transfer and success-only cursor update under the same
    /// exclusive broker borrow. Failures retain the attempted cursor, never replay.
    pub fn write(
        &mut self,
        process: Process,
        fd: i32,
        bytes: &[u8],
    ) -> core::result::Result<MutationCompletion, ProcessWriteFailure> {
        let view = match self.exact(process) {
            Ok(view) => view,
            Err(error) => return Err(self.write_failure(error, None)),
        };
        let (_, binding) = self
            .files
            .binding_in(view, fd)
            .map_err(|error| self.write_failure(ProcessError::Files(error), None))?;
        let index = binding.description as usize;
        let file = self.files.descriptions[index]
            .ok_or_else(|| self.write_failure(ProcessError::Files(Failure::BadFd), None))?;
        if bytes.is_empty() || bytes.len() > MAX_READ {
            return Err(
                self.write_failure(ProcessError::Files(Failure::Invalid), Some(file.offset))
            );
        }
        if file
            .offset
            .checked_add(bytes.len() as u64)
            .is_none_or(|end| end > i64::MAX as u64)
        {
            return Err(
                self.write_failure(ProcessError::Files(Failure::Overflow), Some(file.offset))
            );
        }
        match self
            .files
            .source
            .client
            .write(file.handle, file.offset, bytes)
        {
            Ok(completion) => {
                self.files.descriptions[index] = Some(descriptions::Description {
                    offset: file.offset + completion.bytes as u64,
                    ..file
                });
                Ok(completion)
            }
            Err(failure) => {
                if failure.cleanup.is_some() {
                    self.files.retire();
                }
                Err(ProcessWriteFailure {
                    error: ProcessError::Files(Failure::Source(failure.error)),
                    outcome: failure.outcome,
                    cleanup: failure.cleanup,
                    offset: Some(file.offset),
                })
            }
        }
    }
}
