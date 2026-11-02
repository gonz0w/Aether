// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! One owner-local terminal policy core. Caller context must be authenticated
//! outside this module; these values create no native authority or POSIX FDs.

const ALIASES: usize = 4;
const TRANSFER: usize = 16;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Caller {
    pub identity: u64,
    pub generation: u64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Rights(u8);
impl Rights {
    pub const READ: Self = Self(1);
    pub const WRITE: Self = Self(2);
    pub const MODE: Self = Self(4);
    pub const fn union(self, other: Self) -> Self {
        Self(self.0 | other.0)
    }
    fn contains(self, required: Self) -> bool {
        self.0 & required.0 == required.0
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Role {
    Stdin,
    Stdout,
    Stderr,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Reference {
    terminal: u64,
    caller: Caller,
    slot: usize,
    serial: u64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Bindings {
    pub stdin: Reference,
    pub stdout: Reference,
    pub stderr: Reference,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Invalid,
    Denied,
    Stale,
    Exhausted,
    Unsupported,
    WouldBlock,
    Interrupted,
    HungUp,
    Backend(i32),
    UnknownCompletion,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Mode {
    pub canonical: bool,
    pub echo: bool,
    pub signals: bool,
    pub icrnl: bool,
    pub igncr: bool,
    pub inlcr: bool,
    pub opost: bool,
    pub vmin: u8,
    pub vtime: u8,
}
impl Mode {
    pub const IMMEDIATE: Self = Self {
        canonical: false,
        echo: false,
        signals: false,
        icrnl: false,
        igncr: false,
        inlcr: false,
        opost: false,
        vmin: 1,
        vtime: 0,
    };
    fn supported(self) -> bool {
        !self.canonical
            && !self.echo
            && !self.signals
            && !self.igncr
            && !self.inlcr
            && !self.opost
            && self.vmin == 1
            && self.vtime == 0
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ApplyWhen {
    Now,
    Drain,
    Flush,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ModeRequest {
    pub mode: Mode,
    pub action: ApplyWhen,
}
#[derive(Debug, PartialEq, Eq)]
pub struct Snapshot {
    terminal: u64,
    caller: Caller,
    saved: Mode,
    expected_revision: u64,
    active: bool,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stop {
    Complete,
    WouldBlock,
    Interrupted,
    End,
    /// Known zero-effect negative errno. Positive count plus Error is malformed.
    Error(i32),
    Unknown,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Completion {
    pub count: usize,
    pub stop: Stop,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ReadOutcome {
    Bytes(usize),
    EmptyRequest,
    Eof,
}
#[derive(Clone, Copy, Debug)]
struct Alias {
    serial: u64,
    rights: Rights,
    role: Role,
}
impl Alias {
    const EMPTY: Self = Self {
        serial: 0,
        rights: Rights(0),
        role: Role::Stdin,
    };
}
#[derive(Debug)]
pub struct Terminal {
    identity: u64,
    caller: Caller,
    aliases: [Alias; ALIASES],
    next_serial: u64,
    mode: Mode,
    revision: u64,
    disconnected: bool,
    input_ended: bool,
    failed: bool,
}
impl Terminal {
    /// Owner-only local admission. A numeric identity is not authentication.
    pub fn admit(
        identity: u64,
        caller: Caller,
        rights: [Rights; 3],
        mode: Mode,
    ) -> Result<(Self, Bindings), Error> {
        if identity == 0
            || caller.identity == 0
            || caller.generation == 0
            || rights.iter().any(|right| right.0 == 0)
        {
            return Err(Error::Invalid);
        }
        if !mode.supported() {
            return Err(Error::Unsupported);
        }
        let mut terminal = Self {
            identity,
            caller,
            aliases: [Alias::EMPTY; ALIASES],
            next_serial: 4,
            mode,
            revision: 1,
            disconnected: false,
            input_ended: false,
            failed: false,
        };
        for (slot, role) in [Role::Stdin, Role::Stdout, Role::Stderr]
            .into_iter()
            .enumerate()
        {
            terminal.aliases[slot] = Alias {
                serial: slot as u64 + 1,
                rights: rights[slot],
                role,
            };
        }
        let bindings = Bindings {
            stdin: terminal.reference(0),
            stdout: terminal.reference(1),
            stderr: terminal.reference(2),
        };
        Ok((terminal, bindings))
    }
    fn reference(&self, slot: usize) -> Reference {
        Reference {
            terminal: self.identity,
            caller: self.caller,
            slot,
            serial: self.aliases[slot].serial,
        }
    }
    fn validate(
        &self,
        caller: Caller,
        reference: &Reference,
        required: Rights,
    ) -> Result<Alias, Error> {
        if caller.identity != self.caller.identity {
            return Err(Error::Denied);
        }
        if caller.generation != self.caller.generation
            || reference.caller.generation != self.caller.generation
        {
            return Err(Error::Stale);
        }
        if reference.terminal != self.identity || reference.caller.identity != self.caller.identity
        {
            return Err(Error::Denied);
        }
        let alias = self.aliases.get(reference.slot).ok_or(Error::Stale)?;
        if alias.serial == 0 || alias.serial != reference.serial {
            return Err(Error::Stale);
        }
        if !alias.rights.contains(required) {
            return Err(Error::Denied);
        }
        Ok(*alias)
    }
    pub fn classify(&self, caller: Caller, reference: &Reference) -> Result<Role, Error> {
        Ok(self.validate(caller, reference, Rights(0))?.role)
    }
    /// Read-only validation of an existing reference's admitted data access.
    /// This checks caller/lifetime exactly like classify and grants nothing.
    pub fn access(&self, caller: Caller, reference: &Reference) -> Result<Rights, Error> {
        Ok(self.validate(caller, reference, Rights(0))?.rights)
    }
    pub fn duplicate(&mut self, caller: Caller, reference: &Reference) -> Result<Reference, Error> {
        let alias = self.validate(caller, reference, Rights(0))?;
        let slot = self
            .aliases
            .iter()
            .position(|alias| alias.serial == 0)
            .ok_or(Error::Exhausted)?;
        let next = self.next_serial.checked_add(1).ok_or(Error::Exhausted)?;
        self.aliases[slot] = Alias {
            serial: self.next_serial,
            ..alias
        };
        self.next_serial = next;
        Ok(self.reference(slot))
    }
    pub fn close(&mut self, caller: Caller, reference: Reference) -> Result<usize, Error> {
        self.validate(caller, &reference, Rights(0))?;
        self.aliases[reference.slot] = Alias::EMPTY;
        Ok(self
            .aliases
            .iter()
            .filter(|alias| alias.serial != 0)
            .count())
    }
    /// Unknown effects cannot be retried. Only owner replacement clears failure.
    fn poison(&mut self) -> Error {
        self.failed = true;
        Error::UnknownCompletion
    }
    fn completion(&mut self, completion: Completion, offered: usize) -> Result<usize, Error> {
        if completion.count > offered
            || matches!(completion.stop, Stop::Unknown)
            || matches!(completion.stop, Stop::Error(code) if !(-4095..=-1).contains(&code) || completion.count != 0)
        {
            return Err(self.poison());
        }
        if completion.stop == Stop::End {
            self.disconnected = true;
        }
        if completion.count > 0 {
            return Ok(completion.count);
        }
        match completion.stop {
            Stop::Complete | Stop::WouldBlock => Err(Error::WouldBlock),
            Stop::Interrupted => Err(Error::Interrupted),
            Stop::End => Ok(0),
            Stop::Error(code) => Err(Error::Backend(code)),
            Stop::Unknown => unreachable!(),
        }
    }
    pub fn read(
        &mut self,
        caller: Caller,
        reference: &Reference,
        output: &mut [u8],
        transport: impl FnOnce(&mut [u8]) -> Completion,
    ) -> Result<ReadOutcome, Error> {
        self.validate(caller, reference, Rights::READ)?;
        if self.failed {
            return Err(Error::UnknownCompletion);
        }
        if output.is_empty() {
            return Ok(ReadOutcome::EmptyRequest);
        }
        if self.input_ended {
            return Ok(ReadOutcome::Eof);
        }
        let offered = output.len().min(TRANSFER);
        let mut scratch = [0; TRANSFER];
        let completed = transport(&mut scratch[..offered]);
        let count = match self.completion(completed, offered) {
            Err(Error::WouldBlock) if self.disconnected => {
                self.input_ended = true;
                return Ok(ReadOutcome::Eof);
            }
            outcome => outcome?,
        };
        if completed.stop == Stop::End {
            self.input_ended = true;
        }
        for (target, value) in output[..count].iter_mut().zip(&scratch[..count]) {
            *target = if self.mode.icrnl && *value == b'\r' {
                b'\n'
            } else {
                *value
            };
        }
        Ok(if count == 0 {
            ReadOutcome::Eof
        } else {
            ReadOutcome::Bytes(count)
        })
    }
    pub fn write(
        &mut self,
        caller: Caller,
        reference: &Reference,
        input: &[u8],
        transport: impl FnOnce(Role, &[u8]) -> Completion,
    ) -> Result<usize, Error> {
        let alias = self.validate(caller, reference, Rights::WRITE)?;
        if self.failed {
            return Err(Error::UnknownCompletion);
        }
        if input.is_empty() {
            return Ok(0);
        }
        if self.disconnected {
            return Err(Error::HungUp);
        }
        let offered = input.len().min(TRANSFER);
        let completed = transport(alias.role, &input[..offered]);
        let count = self.completion(completed, offered)?;
        if count == 0 {
            Err(Error::HungUp)
        } else {
            Ok(count)
        }
    }
    /// Public control query: lifetime/MODE plus known healthy client state.
    pub fn mode_state(&self, caller: Caller, reference: &Reference) -> Result<(Mode, u64), Error> {
        self.validate(caller, reference, Rights::MODE)?;
        if self.failed {
            return Err(Error::UnknownCompletion);
        }
        if self.disconnected {
            return Err(Error::HungUp);
        }
        Ok((self.mode, self.revision))
    }
    pub fn snapshot(&self, caller: Caller, reference: &Reference) -> Result<Snapshot, Error> {
        self.mode_state(caller, reference)?;
        Ok(Snapshot {
            terminal: self.identity,
            caller,
            saved: self.mode,
            expected_revision: self.revision,
            active: true,
        })
    }
    fn check_snapshot(&self, snapshot: &Snapshot) -> Result<(), Error> {
        if !snapshot.active
            || snapshot.terminal != self.identity
            || snapshot.caller != self.caller
            || snapshot.expected_revision != self.revision
        {
            return Err(Error::Stale);
        }
        Ok(())
    }
    pub fn apply_now(
        &mut self,
        caller: Caller,
        reference: &Reference,
        snapshot: &mut Snapshot,
        request: ModeRequest,
    ) -> Result<u64, Error> {
        self.mode_state(caller, reference)?;
        self.check_snapshot(snapshot)?;
        if request.action != ApplyWhen::Now || !request.mode.supported() {
            return Err(Error::Unsupported);
        }
        let revision = self.revision.checked_add(1).ok_or(Error::Exhausted)?;
        self.mode = request.mode;
        self.revision = revision;
        snapshot.expected_revision = revision;
        Ok(revision)
    }
    pub fn restore(
        &mut self,
        caller: Caller,
        reference: &Reference,
        snapshot: &mut Snapshot,
    ) -> Result<u64, Error> {
        self.validate(caller, reference, Rights::MODE)?;
        self.check_snapshot(snapshot)?;
        let revision = self.revision.checked_add(1).ok_or(Error::Exhausted)?;
        self.mode = snapshot.saved;
        self.revision = revision;
        snapshot.active = false;
        Ok(revision)
    }
    /// Trusted owner event, not close of an application alias.
    pub fn disconnect(&mut self) {
        self.disconnected = true;
    }
    /// Trusted owner admission/recovery; never callable through terminal rights.
    pub fn replace(
        &mut self,
        caller: Caller,
        rights: [Rights; 3],
        mode: Mode,
    ) -> Result<Bindings, Error> {
        if caller.generation <= self.caller.generation {
            return Err(Error::Stale);
        }
        let (replacement, bindings) = Self::admit(self.identity, caller, rights, mode)?;
        *self = replacement;
        Ok(bindings)
    }
}

#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "tty-tests.rs"]
mod tests;
