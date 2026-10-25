// SPDX-License-Identifier: BSD-2-Clause
//! Actual retained directory selection; no synthetic getcwd or public wire.
#[cfg(not(fs_cwd_wire))]
use super::Failure;
use super::{Channel, Process, ProcessError, ProcessFiles, Result};
use filesystem_client::{Error, Handle};

impl<T: Channel> ProcessFiles<T> {
    pub(super) fn directory_error(&mut self, error: Error) -> ProcessError {
        ProcessError::Files(self.files.source_error(error))
    }

    pub(super) fn directory_for(&mut self, view: usize) -> Result<Handle> {
        if let Some(directory) = self.records[view].cwd {
            return Ok(directory);
        }
        self.files
            .source
            .client
            .root()
            .map_err(|error| self.directory_error(error))
    }

    // Caller already authenticated the record and holds exclusive admission.
    // An inherited directory is closed only after its final local reference.
    pub(super) fn release_directory(&mut self, view: usize) -> Result<()> {
        if let Some(directory) = self.records[view].cwd {
            let shared = self.records.iter().enumerate().any(|(other, record)| {
                other != view && record.process.is_some() && record.cwd == Some(directory)
            });
            if !shared {
                self.files
                    .source
                    .client
                    .close(directory)
                    .map_err(|error| self.directory_error(error))?;
            }
        }
        Ok(())
    }

    /// Trusted canonical-path candidate, not a complete POSIX chdir backend.
    /// A new owned directory is published only after old ownership is settled.
    #[cfg(not(fs_cwd_wire))]
    pub fn change_directory(&mut self, process: Process, path: &[u8]) -> Result<()> {
        let view = self.exact(process)?;
        if path.is_empty() || path.len() > 255 || path.contains(&0) {
            return Err(ProcessError::Files(Failure::Invalid));
        }
        if path == b"." {
            return Ok(());
        }
        let next = if path == b"/" {
            None
        } else {
            let directory = if path.starts_with(b"/") {
                self.files
                    .source
                    .client
                    .root()
                    .map_err(|error| self.directory_error(error))?
            } else {
                self.directory_for(view)?
            };
            let relative = path.strip_prefix(b"/").unwrap_or(path);
            let entry = self
                .files
                .source
                .client
                .open_directory_from(directory, relative)
                .map_err(|error| self.directory_error(error))?;
            Some(entry.handle)
        };
        self.release_directory(view)?;
        self.records[view].cwd = next;
        Ok(())
    }
}

#[cfg(fs_cwd_wire)]
impl<T: Channel> ProcessFiles<T> {
    pub fn change_directory(&mut self, process: Process, path: &[u8]) -> Result<()> {
        let view = self.exact(process)?;
        let base = self.directory_for(view)?;
        let result = self
            .files
            .source
            .client
            .resolve_directory_from(base, path)
            .map_err(|error| self.directory_error(error))?;
        let handle = result.entry().handle;
        let root = self
            .files
            .source
            .client
            .root()
            .map_err(|error| self.directory_error(error))?;
        let next = if handle == root { None } else { Some(handle) };
        if next == self.records[view].cwd {
            return Ok(());
        }
        self.release_directory(view)?;
        self.records[view].cwd = next;
        Ok(())
    }
    pub fn current_directory(&mut self, process: Process, out: &mut [u8; 256]) -> Result<usize> {
        out.fill(0);
        let view = self.exact(process)?;
        let directory = self.directory_for(view)?;
        self.files
            .source
            .client
            .directory_path(directory, out)
            .map_err(|error| self.directory_error(error))
    }
}
