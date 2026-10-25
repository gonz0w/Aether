// SPDX-License-Identifier: BSD-2-Clause
//! AF09 mutation replies retain irreversible progress without retry or replay.
use super::*;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct MutationCompletion {
    pub txg: u64,
    pub bytes: usize,
}

/// Provider observations, not device durability or permission to retry.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MutationProgress {
    Unassigned,
    /// Irreversible producer state1; txg0 remains a meaningful anomaly.
    Committed {
        txg: u64,
        bytes_staged: usize,
    },
    Completed {
        txg: u64,
        bytes_staged: usize,
    },
    Unknown,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MutationOutcome {
    NotSent,
    Reported(MutationProgress),
    /// No validated progress is available after loss or malformed input.
    Unknown,
}

/// Caller-owned observations remain valid after the client is retired/dropped.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct MutationFailure {
    pub error: Error,
    pub outcome: MutationOutcome,
    pub cleanup: Option<[i64; 2]>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NamespaceMutation<'a> {
    Create(&'a [u8]),
    MakeDirectory(&'a [u8]),
    Rename(&'a [u8], &'a [u8]),
    Remove(&'a [u8]),
    RemoveDirectory(&'a [u8]),
}

fn valid_name(name: &[u8]) -> bool {
    !name.is_empty()
        && name.len() <= 255
        && name != b"."
        && name != b".."
        && !name.iter().any(|byte| *byte == 0 || *byte == b'/')
}

impl<T: Channel> Client<T> {
    fn mutation_failure(&mut self, error: Error, outcome: MutationOutcome) -> MutationFailure {
        if !matches!(outcome, MutationOutcome::NotSent) {
            self.shutdown();
        }
        MutationFailure {
            error,
            outcome,
            cleanup: self.cleanup,
        }
    }

    fn mutation_reply(
        &mut self,
        reply: &Message,
        expected: usize,
        namespace: bool,
    ) -> core::result::Result<MutationCompletion, MutationFailure> {
        let invalid =
            |client: &mut Self| client.mutation_failure(Error::Protocol, MutationOutcome::Unknown);
        if reply[..8] != MAGIC[..]
            || word(reply, 2) != self.epoch
            || word(reply, 3) != 0
            || word(reply, 7) != 0
        {
            return Err(invalid(self));
        }
        let code = word(reply, 1) as i64;
        let txg = word(reply, 4);
        let staged = word(reply, 5);
        let state = word(reply, 6);
        if code == 0 {
            if txg == 0 || staged != expected as u64 || state != 2 {
                return Err(invalid(self));
            }
            return Ok(MutationCompletion {
                txg,
                bytes: expected,
            });
        }
        if !(-i64::from(i32::MAX)..0).contains(&code) {
            return Err(invalid(self));
        }
        let progress = match state {
            0 if txg == 0 && staged == 0 => MutationProgress::Unassigned,
            1 | 2
                if (staged == 0 || staged == expected as u64)
                    && (!namespace || code >= -4095)
                    && (state == 1 || txg != 0) =>
            {
                if state == 1 {
                    MutationProgress::Committed {
                        txg,
                        bytes_staged: staged as usize,
                    }
                } else {
                    MutationProgress::Completed {
                        txg,
                        bytes_staged: staged as usize,
                    }
                }
            }
            3 if code == -5 && txg == 0 && staged == 0 => MutationProgress::Unknown,
            _ => return Err(invalid(self)),
        };
        // Even an Unassigned report can precede server retirement. Never infer
        // continued admission or replay safety from its empty progress payload.
        Err(self.mutation_failure(Error::Remote(code), MutationOutcome::Reported(progress)))
    }

    fn mutation_exchange(
        &mut self,
        header: &Message,
        first: &[u8],
        second: &[u8],
        expected: usize,
        namespace: bool,
    ) -> core::result::Result<MutationCompletion, MutationFailure> {
        self.send(header)
            .map_err(|error| self.mutation_failure(error, MutationOutcome::Unknown))?;
        let mut frame = [0; FRAME];
        let mut filled = 0;
        // Rename names are one body: padding between names would change meaning.
        for byte in first.iter().chain(second) {
            frame[filled] = *byte;
            filled += 1;
            if filled == FRAME {
                self.send(&frame)
                    .map_err(|error| self.mutation_failure(error, MutationOutcome::Unknown))?;
                frame.fill(0);
                filled = 0;
            }
        }
        if filled != 0 {
            self.send(&frame)
                .map_err(|error| self.mutation_failure(error, MutationOutcome::Unknown))?;
        }
        let reply = self
            .receive()
            .map_err(|error| self.mutation_failure(error, MutationOutcome::Unknown))?;
        self.mutation_reply(&reply, expected, namespace)
    }

    /// Existing files, explicit offset, nonempty bounded data. Server owns EOF/
    /// no-hole enforcement. Completed provider work does not promise durability.
    pub fn write(
        &mut self,
        handle: Handle,
        offset: u64,
        bytes: &[u8],
    ) -> core::result::Result<MutationCompletion, MutationFailure> {
        let (_, binding) = self
            .binding(handle)
            .map_err(|error| self.mutation_failure(error, MutationOutcome::NotSent))?;
        if binding.entry.kind != Kind::File
            || binding.rights & 4 == 0
            || bytes.is_empty()
            || bytes.len() > MAX_READ
            || offset
                .checked_add(bytes.len() as u64)
                .is_none_or(|end| end > i64::MAX as u64)
        {
            return Err(self.mutation_failure(Error::Invalid, MutationOutcome::NotSent));
        }
        let mut header = self.request(5, handle.token);
        put(&mut header, 4, offset);
        put(&mut header, 5, bytes.len() as u64);
        self.mutation_exchange(&header, bytes, &[], bytes.len(), false)
    }

    pub fn namespace(
        &mut self,
        directory: Handle,
        operation: NamespaceMutation<'_>,
    ) -> core::result::Result<MutationCompletion, MutationFailure> {
        let (_, binding) = self
            .binding(directory)
            .map_err(|error| self.mutation_failure(error, MutationOutcome::NotSent))?;
        let (opcode, first, second) = match operation {
            NamespaceMutation::Create(name) => (7, name, &[][..]),
            NamespaceMutation::MakeDirectory(name) => (10, name, &[][..]),
            NamespaceMutation::Rename(from, to) => (8, from, to),
            NamespaceMutation::Remove(name) => (9, name, &[][..]),
            NamespaceMutation::RemoveDirectory(name) => (11, name, &[][..]),
        };
        if binding.entry.kind != Kind::Directory
            || binding.rights & 9 != 9
            || !valid_name(first)
            || (opcode == 8 && (!valid_name(second) || first == second))
        {
            return Err(self.mutation_failure(Error::Invalid, MutationOutcome::NotSent));
        }
        let mut header = self.request(opcode, directory.token);
        put(
            &mut header,
            5,
            first.len() as u64 | ((second.len() as u64) << 32),
        );
        self.mutation_exchange(&header, first, second, 0, true)
    }
}
