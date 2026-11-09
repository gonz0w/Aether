// SPDX-License-Identifier: BSD-2-Clause
//! One parent-owned note, bound to its actual sole-table description and aliases.
use super::*;
#[cfg(any(not(native_zsh_operator_login), native_zsh_operator_note))]
use filesystem_client::{MutationFailure, MutationOutcome, MutationProgress};
pub const ENTRY: &[u8] = if cfg!(native_zsh_login_startup) {
    b"/home/.zprofile"
} else {
    b"/home/note"
};
const NAME: &[u8] = if cfg!(native_zsh_login_startup) {
    b".zprofile"
} else {
    b"note"
};
const BYTES: &[u8; 16] = if cfg!(native_zsh_login_startup) {
    b"setopt no_beep;\n"
} else {
    b"AETHER-HOME-158\n"
};
pub(super) struct Note {
    create_txg: u64,
    write_txg: u64,
    pub(super) phase: u8,
    description: u8,
    count: u8,
    #[cfg(native_zsh_operator_login)]
    eof_observed: bool,
    #[cfg(native_zsh_home_cwd)]
    pub(super) cwd_home: bool,
    #[cfg(native_zsh_home_cwd_exec)]
    pub(super) child_cwd_home: bool,
}
impl Note {
    pub(super) const fn new() -> Self {
        Self {
            create_txg: 0,
            write_txg: 0,
            phase: 0,
            description: 255,
            count: 0,
            #[cfg(native_zsh_operator_login)]
            eof_observed: false,
            #[cfg(native_zsh_home_cwd)]
            cwd_home: false,
            #[cfg(native_zsh_home_cwd_exec)]
            child_cwd_home: false,
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
#[cfg(any(not(native_zsh_operator_login), native_zsh_operator_note))]
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
    #[cfg(native_zsh_operator_login)]
    pub fn initialize_home_cwd(&mut self, workspace: &mut [u8; PAYLOAD]) -> Result<(), Error> {
        if !self.live(self.binding)
            || self.child.is_some()
            || self.note.phase != 5
            || self.note.count != 16
            || self.note.cwd_home
        {
            return Err(Error::Invalid);
        }
        self.observe_home_cwd(0, true, workspace)
            .map_err(|failure| match failure {
                Failure::Source(error) => error,
                _ => Error::Invalid,
            })?;
        self.note.cwd_home = true;
        workspace.fill(0);
        Ok(())
    }
    #[cfg(native_zsh_operator_login)]
    pub(super) fn note_completion_credit(&self) -> u32 {
        if self.note.phase == 6 {
            u32::from(16 - self.note.count) + u32::from(!self.note.eof_observed)
        } else {
            0
        }
    }
    #[cfg(native_zsh_operator_login)]
    pub(super) fn note_read_uses_credit(&self, view: usize, fd: i32) -> bool {
        self.note.phase == 6
            && (self.note.count < 16 || !self.note.eof_observed)
            && self.note_position(view, fd) == Some(u64::from(self.note.count))
    }
    #[cfg(native_zsh_home_cwd)]
    pub(super) fn observe_home_cwd(
        &mut self,
        view: usize,
        home: bool,
        workspace: &mut [u8; PAYLOAD],
    ) -> descriptions::Result<usize, Error> {
        workspace.fill(0);
        if view != 0
            && !(cfg!(native_zsh_home_cwd_exec)
                && view == 1
                && self.child.is_some()
                && !self.retired)
        {
            return Err(Failure::Source(Error::Remote(-13)));
        }
        let client = &mut self.descriptions.source.client;
        let directory =
            if home { client.home() } else { client.root() }.map_err(Failure::Source)?;
        let path = (&mut workspace[..256]).try_into().unwrap();
        let length = client
            .directory_path(directory, path)
            .map_err(Failure::Source)?;
        let expected: &[u8] = if home { b"/home\0" } else { b"/\0" };
        if &workspace[..length] != expected {
            workspace.fill(0);
            self.abort();
            return Err(Failure::Source(Error::Protocol));
        }
        Ok(length)
    }
    #[cfg(native_zsh_home_cwd)]
    pub(super) fn change_home_cwd(
        &mut self,
        view: usize,
        length: usize,
        workspace: &mut [u8; PAYLOAD],
    ) -> descriptions::Result<(), Error> {
        if view != 0 {
            workspace.fill(0);
            return Err(Failure::Source(Error::Remote(-13)));
        }
        let home = match &workspace[..length] {
            b"/" => false,
            b"/home" => true,
            _ => {
                workspace.fill(0);
                return Err(Failure::Source(Error::Remote(-13)));
            }
        };
        if self.note.phase != 7 || self.note.description != 255 {
            workspace.fill(0);
            return Err(Failure::Source(Error::Remote(-16)));
        }
        self.observe_home_cwd(view, home, workspace)?;
        // This selector is committed only after an actual held-object observation.
        // The enclosing Reply owns it until delivery, or aborts the whole view.
        self.note.cwd_home = home;
        workspace.fill(0);
        Ok(())
    }
    /// The new child may inherit only a fully delivered profile read and no
    /// description/reply obligation. Phase5 and undelivered close8 are not ready.
    #[cfg(native_zsh_home_cwd_exec)]
    pub fn note_fork_ready(&self) -> bool {
        self.live(self.binding)
            && self.child.is_none()
            && self.note_complete()
            && self.note.description == 255
    }
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
                    #[cfg(native_zsh_operator_note)]
                    (6, 16) if self.note.eof_observed => 8,
                    #[cfg(not(native_zsh_operator_note))]
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
        #[cfg(native_zsh_home_cwd)]
        {
            if view != 0 {
                return Err(Failure::Source(Error::Remote(-13)));
            }
            if self.note.phase == 7 {
                // A new admitted read cannot inherit the previous completion.
                self.note.phase = 5;
                self.note.count = 0;
                self.note.description = 255;
            }
        }
        #[cfg(all(native_zsh_login_startup, not(native_zsh_home_redirection_reader)))]
        if view == 0 && self.note.phase == 0 {
            // Only the canonical remote missing result leaves this startup probe
            // live. Existing input is never published to the parser or adopted.
            let source = &mut self.descriptions.source.client;
            let home = source.home().map_err(Failure::Source)?;
            return match source.lookup(home, NAME, 2) {
                Err(Error::Remote(-2)) => Err(Failure::Source(Error::Remote(-2))),
                Err(error) => {
                    self.note.phase = 1;
                    self.abort();
                    Err(Failure::Source(error))
                }
                Ok(entry) => {
                    self.note.phase = 1;
                    let closed = source.close(entry.handle);
                    // Contain unexpected input even if its individual close is
                    // known successful; the selected startup must fail closed.
                    self.abort();
                    Err(Failure::Source(closed.err().unwrap_or(Error::Invalid)))
                }
            };
        }
        if view != 0 || self.note.phase != 5 {
            return Err(Failure::BadFd);
        }
        let fd = self.descriptions.open_read_using(view, cloexec, |source| {
            let home = source.client.home()?;
            let entry = source.client.lookup(home, NAME, 2)?;
            if entry.kind != Kind::File || entry.size != 16 {
                return Err(Error::Protocol);
            }
            Ok(entry.handle)
        })?;
        self.note.description = self.descriptions.binding_in(view, fd)?.1.description;
        self.note.phase = 6;
        self.note.count = 0;
        #[cfg(native_zsh_operator_login)]
        {
            self.note.eof_observed = false;
        }
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
                #[cfg(native_zsh_operator_login)]
                if count == 0 && offset < 16 {
                    self.abort();
                    return;
                }
                #[cfg(native_zsh_operator_login)]
                if count == 0 {
                    self.note.eof_observed = true;
                }
                self.note.count += count as u8;
            } else {
                #[cfg(native_zsh_operator_login)]
                if before == Some(offset as u64) {
                    self.abort();
                }
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
            let file = client.lookup(home, NAME, 2)?;
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
    #[cfg(not(native_zsh_operator_note))]
    #[inline(never)]
    pub(super) fn prepare_note<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        workspace: &'a mut [u8; PAYLOAD],
    ) -> Result<Reply<'a, T>, Error> {
        #[cfg(not(native_zsh_operator_login))]
        let view = self.view(binding).ok_or(Error::Protocol)?;
        let create = word(raw, 1) == 12;
        #[cfg(not(native_zsh_operator_login))]
        let (mut value, mut failure, mut receipt) = (0, Some(Failure::BadFd), [0; 8]);
        #[cfg(native_zsh_operator_login)]
        let (value, failure, receipt) = (0, Some(Failure::BadFd), [0; 8]);
        if create {
            #[cfg(not(native_zsh_home_redirection_reader))]
            if view == 0 && self.note.phase == 0 && workspace[..ENTRY.len()] == *ENTRY {
                let mut mutation = None;
                let mut completed = 0;
                let phase = &mut self.note.phase;
                let result = self
                    .descriptions
                    .open_read_using(0, word(raw, 4) != 0, |source| {
                        let home = source.client.home()?;
                        source.client.preflight_lookup(home, NAME, 4)?;
                        *phase = 1; // mark the only create attempt before its effect
                        let done = source
                            .client
                            .namespace(home, NamespaceMutation::Create(NAME))
                            .map_err(|e| {
                                mutation = Some(e);
                                e.error
                            })?;
                        completed = done.txg;
                        let entry = source.client.lookup(home, NAME, 4)?;
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
            // This closed cold reader cannot CREATE the writable phase2.
            // Preserve the negative receipt below without retaining a mutation
            // implementation that no admitted operator state can reach.
            #[cfg(not(native_zsh_operator_login))]
            {
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
        }
        self.finish_note_reply(binding, raw, workspace, value, failure, receipt)
    }

    #[cfg(native_zsh_operator_note)]
    #[inline(never)]
    pub(super) fn prepare_scratch_mutation<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        workspace: &'a mut [u8; PAYLOAD],
        remaining: u32,
    ) -> Result<Reply<'a, T>, Error> {
        let create = word(raw, 1) == 12;
        let fd = word(raw, 4) as i32;
        let length = word(raw, 5) as usize;
        let mut receipt = [0; 8];
        let mut value = 0;
        let mut failure = Some(Failure::BadFd);
        let allowed = binding == self.binding
            && if create {
                workspace[..length] == *operator_note::ENTRY
            } else {
                self.scratch_write_fd(0, fd)
            };
        if allowed {
            // Fund existing-object lookup and close independently. Absence
            // also needs CREATE and open lookup before a later consuming close.
            let reserve =
                self.shutdown_budget() + self.note_completion_credit() + self.file_exec_credit();
            if remaining < reserve + if create { 2 } else { 1 } {
                failure = Some(Failure::Source(Error::Full));
            } else {
                let (result, txg, mutation) = if create {
                    self.scratch_create(word(raw, 4) != 0, remaining >= reserve + 4)
                } else {
                    self.scratch_write(fd, &workspace[..length])
                };
                failure = result.err();
                if mutation.is_some() {
                    self.mutation_failure = mutation;
                }
                match result {
                    Ok(done) => {
                        value = done;
                        receipt = if create {
                            [6, txg, 0, 0, 0, 0, 0, 0]
                        } else {
                            [14, 0, txg, done, 0, 0, 0, 0]
                        };
                    }
                    Err(error) if create && txg != 0 => {
                        let close = self.abort();
                        let (kind, val) = cause(error);
                        receipt = [
                            22,
                            txg,
                            0,
                            0,
                            close[0] as u64,
                            close[1] as u64,
                            kind,
                            val as u64,
                        ];
                    }
                    Err(Failure::Source(error)) => {
                        if let Some(mutation) = mutation {
                            let (flags, txg, staged) = progress(mutation);
                            let (kind, val) = cause(Failure::Source(error));
                            let close = mutation.cleanup.unwrap_or([0; 2]);
                            receipt = if create {
                                [
                                    flags,
                                    txg,
                                    kind,
                                    val as u64,
                                    close[0] as u64,
                                    close[1] as u64,
                                    0,
                                    0,
                                ]
                            } else {
                                [
                                    if flags == 0 { 0 } else { flags | 8 },
                                    0,
                                    txg,
                                    staged,
                                    close[0] as u64,
                                    close[1] as u64,
                                    kind,
                                    val as u64,
                                ]
                            };
                            if mutation.cleanup.is_some() {
                                self.abort();
                            }
                        } else if self.cleanup().is_some() {
                            // Lookup/close loss before CREATE conveys no
                            // mutation receipt, and cannot become EEXIST.
                            workspace.fill(0);
                            self.abort();
                            return Err(Error::Closed);
                        }
                    }
                    Err(_) => (),
                }
            }
        }
        self.finish_note_reply(binding, raw, workspace, value, failure, receipt)
    }

    fn finish_note_reply<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        workspace: &'a mut [u8; PAYLOAD],
        value: u64,
        failure: Option<Failure<Error>>,
        mut receipt: [u64; 8],
    ) -> Result<Reply<'a, T>, Error> {
        let view = self.view(binding).ok_or(Error::Protocol)?;
        let create = word(raw, 1) == 12;
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
