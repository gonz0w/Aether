// SPDX-License-Identifier: BSD-2-Clause
//! One parent-owned note, bound to its actual sole-table description and aliases.
use super::*;
use filesystem_client::{MutationFailure, MutationOutcome, MutationProgress};
pub const ENTRY: &[u8] = b"/home/note";
const BYTES: &[u8; 16] = b"AETHER-HOME-158\n";
pub(super) struct Note {
    create_txg: u64,
    write_txg: u64,
    pub(super) phase: u8,
    description: u8,
    count: u8,
}
impl Note {
    pub(super) const fn new() -> Self {
        Self {
            create_txg: 0,
            write_txg: 0,
            phase: 0,
            description: 255,
            count: 0,
        }
    }
}
const _: () = assert!(core::mem::size_of::<Note>() <= 24);
fn cause(error: Failure<Error>) -> (u64, i64) {
    match error {
        Failure::BadFd => (1, 0),
        Failure::Full => (2, 0),
        Failure::Invalid => (3, 0),
        Failure::Overflow => (4, 0),
        Failure::Retired => (5, 0),
        Failure::InvalidCompletion => (6, 0),
        Failure::Source(e) => match e {
            Error::Invalid => (7, 0),
            Error::Closed => (8, 0),
            Error::Full => (9, 0),
            Error::Protocol => (10, 0),
            Error::Transport(v) => (11, v),
            Error::Remote(v) => (12, v),
        },
    }
}
fn progress(failure: MutationFailure) -> (u64, u64, u64) {
    let (tag, txg, staged) = match failure.outcome {
        MutationOutcome::NotSent => (0, 0, 0),
        MutationOutcome::Unknown => (5, 0, 0),
        MutationOutcome::Reported(p) => match p {
            MutationProgress::Unassigned => (1, 0, 0),
            MutationProgress::Committed { txg, bytes_staged } => (2, txg, bytes_staged as u64),
            MutationProgress::Completed { txg, bytes_staged } => (3, txg, bytes_staged as u64),
            MutationProgress::Unknown => (4, 0, 0),
        },
    };
    (
        tag | if failure.cleanup.is_some() { 16 } else { 0 },
        txg,
        staged,
    )
}
impl<T: Channel> Files<T> {
    /// No fork snapshot may copy note descriptions, attempted effects, or live aliases.
    pub fn note_io_active(&self) -> bool {
        matches!(self.note.phase, 1..=4 | 6)
    }
    /// Actual explicit read/last-close completion; teardown never invents it.
    pub fn note_complete(&self) -> bool {
        self.note.phase == 7
            && self.note.count == 16
            && (cfg!(native_zsh_home_redirection_reader)
                || (self.note.create_txg != 0 && self.note.write_txg != 0))
            && (!self.retired || self.cleanup() == Some([0; 2]))
    }
    fn note_index(&self, view: usize, fd: i32) -> Option<usize> {
        let (_, binding) = self.descriptions.binding_in(view, fd).ok()?;
        (binding.description == self.note.description).then_some(binding.description as usize)
    }
    pub(super) fn note_write_fd(&self, view: usize, fd: i32) -> bool {
        matches!(self.note.phase, 2..=4) && self.note_index(view, fd).is_some()
    }
    pub(super) fn note_position(&self, view: usize, fd: i32) -> Option<u64> {
        let index = self.note_index(view, fd)?;
        Some(self.descriptions.descriptions[index]?.offset)
    }
    pub(super) fn note_closed(&mut self, position: Option<u64>, ok: bool) {
        if let Some(position) = position {
            if !ok {
                self.note.phase = 1;
            } else if self.descriptions.descriptions[self.note.description as usize].is_none() {
                self.note.phase = match (self.note.phase, position) {
                    (4, 16) => 5,
                    (6, 16) => 8,
                    _ => 1,
                };
                self.note.description = 255;
            }
        }
    }
    pub(super) fn open_note_read(
        &mut self,
        view: usize,
        cloexec: bool,
    ) -> descriptions::Result<i32, Error> {
        if view != 0 || self.note.phase != 5 {
            return Err(Failure::BadFd);
        }
        let fd = self.descriptions.open_read_using(view, cloexec, |source| {
            let home = source.client.home()?;
            let entry = source.client.lookup(home, b"note", 2)?;
            if entry.kind != Kind::File || entry.size != 16 {
                return Err(Error::Protocol);
            }
            Ok(entry.handle)
        })?;
        self.note.description = self.descriptions.binding_in(view, fd)?.1.description;
        self.note.phase = 6;
        self.note.count = 0;
        Ok(fd)
    }
    pub(super) fn note_read(
        &mut self,
        view: usize,
        fd: i32,
        before: Option<u64>,
        count: usize,
        workspace: &[u8; PAYLOAD],
    ) {
        if self.note.phase == 6 && self.note_index(view, fd).is_some() {
            let offset = usize::from(self.note.count);
            if before == Some(offset as u64)
                && count <= 16 - offset
                && workspace[..count] == BYTES[offset..offset + count]
            {
                self.note.count += count as u8;
            }
        }
    }
    #[cfg(native_zsh_home_redirection_reader)]
    pub fn reopen_note(&mut self, workspace: &mut [u8; PAYLOAD]) -> Result<(), Error> {
        if self.note.phase != 0 || !self.live(self.binding) {
            return Err(Error::Invalid);
        }
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let home = client.home()?;
            let file = client.lookup(home, b"note", 2)?;
            if file.kind != Kind::File
                || file.size != 16
                || client.read(file.handle, 0, 16, workspace)? != 16
                || workspace[..16] != BYTES[..]
                || client.read(file.handle, 16, 1, workspace)? != 0
            {
                return Err(Error::Protocol);
            }
            let stat = client.stat(file.handle)?;
            if stat.kind != Kind::File || stat.size != 16 {
                return Err(Error::Protocol);
            }
            client.close(file.handle)
        })();
        workspace.fill(0);
        if result.is_err() {
            self.abort();
        } else {
            self.note.phase = 5;
            self.note.count = 16;
        }
        result
    }
    #[inline(never)]
    pub(super) fn prepare_note<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        workspace: &'a mut [u8; PAYLOAD],
    ) -> Result<Reply<'a, T>, Error> {
        let view = self.view(binding).ok_or(Error::Protocol)?;
        let create = word(raw, 1) == 12;
        let mut receipt = [0u64; 8];
        let mut value = 0;
        let mut failure = Some(Failure::BadFd);
        if create {
            #[cfg(not(native_zsh_home_redirection_reader))]
            if view == 0 && self.note.phase == 0 && workspace[..10] == *ENTRY {
                let mut mutation = None;
                let mut completed = 0;
                let phase = &mut self.note.phase;
                let result = self
                    .descriptions
                    .open_read_using(0, word(raw, 4) != 0, |source| {
                        let home = source.client.home()?;
                        source.client.preflight_lookup(home, b"note", 4)?;
                        *phase = 1; // mark the only create attempt before its effect
                        let done = source
                            .client
                            .namespace(home, NamespaceMutation::Create(b"note"))
                            .map_err(|e| {
                                mutation = Some(e);
                                e.error
                            })?;
                        completed = done.txg;
                        let entry = source.client.lookup(home, b"note", 4)?;
                        if entry.kind != Kind::File || entry.size != 0 {
                            return Err(Error::Protocol);
                        }
                        Ok(entry.handle)
                    });
                match result {
                    Ok(fd) => {
                        self.note.create_txg = completed;
                        self.note.phase = 2;
                        self.note.description = self
                            .descriptions
                            .binding_in(0, fd)
                            .map_err(|_| Error::Protocol)?
                            .1
                            .description;
                        receipt = [6, completed, 0, 0, 0, 0, 0, 0];
                        value = fd as u64;
                        failure = None;
                    }
                    Err(error) => {
                        failure = Some(error);
                        if let Some(m) = mutation {
                            self.mutation_failure = Some(m);
                            let (flags, txg, _) = progress(m);
                            let (kind, val) = cause(Failure::Source(m.error));
                            let close = m.cleanup.unwrap_or([0; 2]);
                            receipt = [
                                flags,
                                txg,
                                kind,
                                val as u64,
                                close[0] as u64,
                                close[1] as u64,
                                0,
                                0,
                            ];
                            if !matches!(m.outcome, MutationOutcome::NotSent) {
                                self.note.phase = 1;
                                self.abort();
                            }
                        } else if completed != 0 {
                            self.note.create_txg = completed;
                            self.note.phase = 1;
                            let close = self.abort();
                            let (kind, val) = cause(error);
                            receipt = [
                                22,
                                completed,
                                0,
                                0,
                                close[0] as u64,
                                close[1] as u64,
                                kind,
                                val as u64,
                            ];
                        }
                    }
                }
            }
        } else {
            let fd = word(raw, 4) as i32;
            if view == 0 && self.note.phase == 2 && self.note_write_fd(view, fd) {
                let index = self.note_index(view, fd).ok_or(Error::Protocol)?;
                let file = self.descriptions.descriptions[index].ok_or(Error::Protocol)?;
                failure = Some(Failure::Invalid);
                if file.offset == 0 {
                    self.note.phase = 3; // one attempt, before the source effect
                    match self.descriptions.source.client.write(
                        file.handle,
                        0,
                        &workspace[..word(raw, 5) as usize],
                    ) {
                        Ok(done) => {
                            self.note.write_txg = done.txg;
                            self.note.count = done.bytes as u8;
                            self.note.phase = 4;
                            self.descriptions.descriptions[index] =
                                Some(descriptions::Description {
                                    offset: done.bytes as u64,
                                    ..file
                                });
                            value = done.bytes as u64;
                            receipt = [14, 0, done.txg, value, 0, 0, 0, 0];
                            failure = None;
                        }
                        Err(m) => {
                            self.mutation_failure = Some(m);
                            failure = Some(Failure::Source(m.error));
                            let (flags, txg, staged) = progress(m);
                            let (kind, val) = cause(Failure::Source(m.error));
                            let close = m.cleanup.unwrap_or([0; 2]);
                            receipt = [
                                flags | 8,
                                0,
                                txg,
                                staged,
                                close[0] as u64,
                                close[1] as u64,
                                kind,
                                val as u64,
                            ];
                            if m.cleanup.is_some() {
                                self.abort();
                            }
                        }
                    }
                }
            }
        }
        if receipt[0] == 0 {
            let (kind, val) = cause(failure.unwrap_or(Failure::Invalid));
            if create {
                receipt[2] = kind;
                receipt[3] = val as u64;
            } else {
                receipt[6] = kind;
                receipt[7] = val as u64;
            }
        }
        workspace.fill(0);
        for (index, val) in receipt.into_iter().enumerate() {
            put((&mut workspace[..FRAME]).try_into().unwrap(), index, val);
        }
        let mut header = [0; FRAME];
        header[..8].copy_from_slice(MAGIC);
        put(&mut header, 1, failure.map(errno).unwrap_or(0) as u64);
        put(&mut header, 2, binding.generation);
        put(&mut header, 3, word(raw, 3));
        put(&mut header, 4, value);
        put(&mut header, 5, 64);
        if view == 1 {
            self.child_pending = true;
        } else {
            self.pending = true;
        }
        Ok(Reply {
            view,
            files: self,
            workspace,
            header,
            body: FRAME,
            delivered: false,
        })
    }
}
