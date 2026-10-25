// SPDX-License-Identifier: BSD-2-Clause
//! One fixed receipt survives source retirement; delivery is a separate result.
use super::*;
use filesystem_client::{MutationCompletion, MutationOutcome, MutationProgress};
use filesystem_remote_descriptors::ProcessWriteFailure;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FileWriteResult {
    Completed {
        offset: u64,
        completion: MutationCompletion,
    },
    Failed(ProcessWriteFailure),
}
/// Caller must also retain its authenticated Process/endpoint association.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct FileWriteReceipt {
    pub generation: u64,
    pub sequence: u64,
    pub fd: i32,
    pub requested: usize,
    pub result: FileWriteResult,
}
fn cause(error: ProcessError) -> (u64, i64) {
    match error {
        ProcessError::Identity(value) => (13, i64::from(value)),
        ProcessError::Stale => (14, 0),
        ProcessError::Busy => (15, 0),
        ProcessError::Generation => (16, 0),
        ProcessError::Files(error) => match error {
            Failure::BadFd => (1, 0),
            Failure::Full => (2, 0),
            Failure::Invalid => (3, 0),
            Failure::Overflow => (4, 0),
            Failure::Retired => (5, 0),
            Failure::InvalidCompletion => (6, 0),
            Failure::Source(error) => match error {
                SourceError::Invalid => (7, 0),
                SourceError::Closed => (8, 0),
                SourceError::Full => (9, 0),
                SourceError::Protocol => (10, 0),
                SourceError::Transport(value) => (11, value),
                SourceError::Remote(value) => (12, value),
            },
        },
    }
}
impl Connection {
    pub(super) fn prepare_write<'a, T: Channel>(
        &'a mut self,
        files: &'a mut ProcessFiles<T>,
        raw: &[u8],
        workspace: &'a mut [u8; MAX_READ],
    ) -> core::result::Result<PreparedReply<'a, T>, Error> {
        let fd = word(raw, 4) as i32;
        let requested = word(raw, 5) as usize;
        let offset = files.position(self.process, fd).ok();
        let outcome = files.write(self.process, fd, &workspace[..requested]);
        let mut flags;
        let (status, count, offset, txg, staged, cleanup, kind, value, result) = match outcome {
            Ok(completion) => {
                flags = 6;
                let offset = offset.expect("validated write retained its selected description");
                (
                    0,
                    completion.bytes as u64,
                    Some(offset),
                    completion.txg,
                    completion.bytes as u64,
                    None,
                    0,
                    0,
                    FileWriteResult::Completed { offset, completion },
                )
            }
            Err(failure) => {
                let (tag, txg, staged) = match failure.outcome {
                    MutationOutcome::NotSent => (0, 0, 0),
                    MutationOutcome::Unknown => (5, 0, 0),
                    MutationOutcome::Reported(progress) => match progress {
                        MutationProgress::Unassigned => (1, 0, 0),
                        MutationProgress::Committed { txg, bytes_staged } => {
                            (2, txg, bytes_staged as u64)
                        }
                        MutationProgress::Completed { txg, bytes_staged } => {
                            (3, txg, bytes_staged as u64)
                        }
                        MutationProgress::Unknown => (4, 0, 0),
                    },
                };
                flags = tag;
                let (kind, value) = cause(failure.error);
                (
                    errno(failure.error),
                    0,
                    failure.offset,
                    txg,
                    staged,
                    failure.cleanup,
                    kind,
                    value,
                    FileWriteResult::Failed(failure),
                )
            }
        };
        workspace.fill(0);
        if offset.is_some() {
            flags |= 8;
        }
        if cleanup.is_some() {
            flags |= 16;
        }
        for (i, value) in [
            flags,
            offset.unwrap_or(0),
            txg,
            staged,
            cleanup.map_or(0, |c| c[0] as u64),
            cleanup.map_or(0, |c| c[1] as u64),
            kind,
            value as u64,
        ]
        .into_iter()
        .enumerate()
        {
            workspace[i * 8..i * 8 + 8].copy_from_slice(&value.to_le_bytes());
        }
        // Exactly this already-retained write reply may outlive a retired source.
        // Confirmed delivery must not reopen either admission boundary.
        if files.cleanup().is_some() {
            self.retired = true;
        }
        let mut reply = [0; FRAME];
        reply[..8].copy_from_slice(MAGIC);
        for (i, value) in [status as u64, self.generation, self.next, count, 64, 0, 0]
            .into_iter()
            .enumerate()
        {
            put(&mut reply, i + 1, value);
        }
        let receipt = FileWriteReceipt {
            generation: self.generation,
            sequence: self.next,
            fd,
            requested,
            result,
        };
        Ok(PreparedReply {
            connection: self,
            files,
            workspace,
            reply,
            body: 64,
            delivered: false,
            write: Some(receipt),
        })
    }
}
impl<T: Channel> PreparedReply<'_, T> {
    /// Copy before any transport attempt. The dispatcher owns retention through
    /// unknown delivery and keeps authenticated Process/endpoint correlation.
    pub fn write_receipt(&self) -> Option<FileWriteReceipt> {
        self.write
    }
}
