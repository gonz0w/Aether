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
    #[cfg(native_tty_canonical_probe)]
    pub const CANONICAL: Self = Self {
        canonical: true,
        echo: true,
        signals: true,
        icrnl: true,
        opost: true,
        ..Self::IMMEDIATE
    };
    #[cfg(native_tty_canonical_probe)]
    pub const ZLE: Self = Self {
        signals: true,
        icrnl: true,
        inlcr: true,
        opost: true,
        ..Self::IMMEDIATE
    };
    fn supported(self) -> bool {
        #[cfg(native_tty_canonical_probe)]
        if self == Self::CANONICAL || self == Self::ZLE {
            return true;
        }
        !self.canonical
            && !self.echo
            && (!self.signals || cfg!(native_tty_signal_probe))
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
/// Selected owner input; target authority is checked outside this policy core.
#[cfg(native_tty_signal_probe)]
pub trait SignalInput {
    fn read(&mut self, output: &mut [u8]) -> Completion;
    fn post_sigint(&mut self) -> Result<u8, Error>;
    #[cfg(native_tty_canonical_probe)]
    fn write(&mut self, _role: Role, _input: &[u8]) -> Completion {
        Completion {
            count: 0,
            stop: Stop::Unknown,
        }
    }
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
#[cfg(native_tty_canonical_probe)]
#[derive(Debug)]
struct Buffered {
    record: [u8; 64],
    len: usize,
    at: usize,
    ready: bool,
    empty_eof: bool,
    interrupt: bool,
    tx: [u8; 3],
    tx_len: usize,
    tx_at: usize,
    tx_role: Role,
}
#[cfg(native_tty_canonical_probe)]
impl Buffered {
    const EMPTY: Self = Self {
        record: [0; 64],
        len: 0,
        at: 0,
        ready: false,
        empty_eof: false,
        interrupt: false,
        tx: [0; 3],
        tx_len: 0,
        tx_at: 0,
        tx_role: Role::Stdout,
    };
    fn clear_record(&mut self) {
        self.record.fill(0);
        self.len = 0;
        self.at = 0;
        self.ready = false;
        self.empty_eof = false;
    }
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
    #[cfg(native_tty_canonical_probe)]
    buffered: Buffered,
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
            #[cfg(native_tty_canonical_probe)]
            buffered: Buffered::EMPTY,
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
    /// One physical byte at a time: VINTR never owns a suffix. Positive data
    /// progress wins over interruption; unknown post effects are never replayed.
    #[cfg(all(native_tty_signal_probe, not(native_tty_canonical_probe)))]
    pub fn read_signalled(
        &mut self,
        caller: Caller,
        reference: &Reference,
        output: &mut [u8],
        eligible: bool,
        input: &mut impl SignalInput,
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
        let mut scratch = [0; TRANSFER];
        let mut count = 0;
        for _ in 0..TRANSFER {
            let mut byte = [0];
            let done = input.read(&mut byte);
            if done.stop == Stop::Interrupted {
                self.failed = true;
                return Err(Error::UnknownCompletion);
            }
            let n = match self.completion(done, 1) {
                Ok(n) => n,
                Err(Error::WouldBlock | Error::Backend(_)) if count != 0 => break,
                Err(Error::WouldBlock) if self.disconnected => {
                    self.input_ended = true;
                    break;
                }
                Err(e) => return Err(e),
            };
            if done.stop == Stop::End {
                self.input_ended = true;
            }
            if n == 0 {
                break;
            }
            if self.mode.signals && byte[0] == 3 {
                let outcome = match input.post_sigint() {
                    Ok(outcome @ 0..=2) => outcome,
                    _ => {
                        self.failed = true;
                        return Err(Error::UnknownCompletion);
                    }
                };
                if outcome != 0 && eligible {
                    if count == 0 {
                        return Err(Error::Interrupted);
                    }
                    break;
                }
                if self.input_ended {
                    break;
                }
                continue;
            }
            scratch[count] = if self.mode.icrnl && byte[0] == b'\r' {
                b'\n'
            } else {
                byte[0]
            };
            count += 1;
            if self.input_ended || count == output.len().min(TRANSFER) {
                break;
            }
        }
        if count == 0 && !self.input_ended {
            return Err(Error::WouldBlock);
        }
        output[..count].copy_from_slice(&scratch[..count]);
        Ok(if count == 0 {
            ReadOutcome::Eof
        } else {
            ReadOutcome::Bytes(count)
        })
    }
    #[cfg(native_tty_canonical_probe)]
    fn output_live(&self, role: Role) -> bool {
        self.aliases
            .iter()
            .any(|a| a.serial != 0 && a.role == role && a.rights.contains(Rights::WRITE))
    }
    #[cfg(native_tty_canonical_probe)]
    pub fn output_pending(&self) -> bool {
        self.buffered.tx_at < self.buffered.tx_len
    }
    /// Trusted owner drains only a previously accepted sequence through its
    /// still-held WRITE role; this creates no source or application authority.
    #[cfg(native_tty_canonical_probe)]
    pub fn flush_output(
        &mut self,
        caller: Caller,
        mut transport: impl FnMut(Role, &[u8]) -> Completion,
    ) -> Result<(), Error> {
        if caller != self.caller {
            return Err(Error::Denied);
        }
        if self.failed {
            return Err(Error::UnknownCompletion);
        }
        while self.buffered.tx_at < self.buffered.tx_len {
            let role = self.buffered.tx_role;
            if !self.output_live(role) {
                return Err(Error::Denied);
            }
            let at = self.buffered.tx_at;
            let len = self.buffered.tx_len;
            let done = transport(role, &self.buffered.tx[at..len]);
            let count = self.completion(done, len - at)?;
            if count == 0 {
                return Err(Error::WouldBlock);
            }
            self.buffered.tx_at += count;
        }
        self.buffered.tx.fill(0);
        self.buffered.tx_at = 0;
        self.buffered.tx_len = 0;
        Ok(())
    }
    #[cfg(native_tty_canonical_probe)]
    fn stage_output(&mut self, role: Role, bytes: &[u8]) -> Result<(), Error> {
        if !self.output_live(role) {
            return Err(Error::Denied);
        }
        if self.buffered.tx_at != self.buffered.tx_len || bytes.len() > 3 {
            return Err(self.poison());
        }
        self.buffered.tx[..bytes.len()].copy_from_slice(bytes);
        self.buffered.tx_at = 0;
        self.buffered.tx_len = bytes.len();
        self.buffered.tx_role = role;
        Ok(())
    }
    #[cfg(native_tty_canonical_probe)]
    fn stage_byte(&mut self, role: Role, byte: u8) -> Result<(), Error> {
        if self.mode.opost && byte == b'\n' {
            self.stage_output(role, b"\r\n")
        } else {
            self.stage_output(role, &[byte])
        }
    }
    #[cfg(native_tty_canonical_probe)]
    fn write_processed(
        &mut self,
        role: Role,
        input: &[u8],
        mut transport: impl FnMut(Role, &[u8]) -> Completion,
    ) -> Result<usize, Error> {
        self.flush_output(self.caller, &mut transport)?;
        let mut accepted = 0;
        for byte in &input[..input.len().min(TRANSFER)] {
            self.stage_byte(role, *byte)?;
            accepted += 1;
            match self.flush_output(self.caller, &mut transport) {
                Ok(()) => {}
                Err(Error::WouldBlock | Error::Backend(_)) => return Ok(accepted),
                Err(e) => return Err(e),
            }
        }
        Ok(accepted)
    }
    #[cfg(native_tty_canonical_probe)]
    fn publish_record(&mut self, output: &mut [u8]) -> ReadOutcome {
        let n = (self.buffered.len - self.buffered.at)
            .min(output.len())
            .min(TRANSFER);
        output[..n].copy_from_slice(&self.buffered.record[self.buffered.at..self.buffered.at + n]);
        self.buffered.at += n;
        if self.buffered.at == self.buffered.len {
            self.buffered.clear_record();
        }
        ReadOutcome::Bytes(n)
    }
    /// Local retirement follows confirmed application stop, never a client mode
    /// restore. Snapshots save attributes, not input or output history.
    #[cfg(native_tty_canonical_probe)]
    pub fn retire_buffered_io(&mut self) {
        self.buffered = Buffered::EMPTY;
    }
    #[cfg(native_tty_canonical_probe)]
    pub fn read_signalled(
        &mut self,
        caller: Caller,
        reference: &Reference,
        output: &mut [u8],
        eligible: bool,
        input: &mut impl SignalInput,
    ) -> Result<ReadOutcome, Error> {
        self.validate(caller, reference, Rights::READ)?;
        if self.failed {
            return Err(Error::UnknownCompletion);
        }
        if output.is_empty() {
            return Ok(ReadOutcome::EmptyRequest);
        }
        if self.mode.echo && !self.output_live(Role::Stdout) {
            return Err(Error::Denied);
        }
        self.flush_output(caller, |role, bytes| input.write(role, bytes))?;
        if self.buffered.interrupt {
            self.buffered.interrupt = false;
            return Err(Error::Interrupted);
        }
        if self.buffered.len > self.buffered.at
            && (self.buffered.ready || !self.mode.canonical || self.input_ended)
        {
            return Ok(self.publish_record(output));
        }
        if self.buffered.empty_eof {
            self.buffered.empty_eof = false;
            return Ok(ReadOutcome::Eof);
        }
        if self.input_ended {
            return Ok(ReadOutcome::Eof);
        }
        for _ in 0..TRANSFER {
            self.flush_output(caller, |role, bytes| input.write(role, bytes))?;
            let mut byte = [0];
            let done = input.read(&mut byte);
            if done.stop == Stop::Interrupted {
                return Err(self.poison());
            }
            let n = match self.completion(done, 1) {
                Ok(n) => n,
                Err(Error::WouldBlock) if self.buffered.len > 0 && !self.mode.canonical => break,
                Err(Error::Backend(_)) if self.buffered.len > 0 => {
                    self.buffered.ready = true;
                    break;
                }
                Err(Error::WouldBlock) if self.disconnected => {
                    self.input_ended = true;
                    self.buffered.ready = true;
                    break;
                }
                Err(e) => return Err(e),
            };
            if done.stop == Stop::End {
                self.input_ended = true;
            }
            if n == 0 {
                self.buffered.ready = true;
                break;
            }
            let raw = byte[0];
            if self.mode.signals && raw == 3 {
                let outcome = match input.post_sigint() {
                    Ok(v @ 0..=2) => v,
                    _ => return Err(self.poison()),
                };
                if self.mode.canonical {
                    self.buffered.clear_record();
                }
                if self.mode.echo {
                    self.stage_byte(Role::Stdout, raw)?;
                }
                if outcome != 0 && eligible {
                    if self.buffered.len == 0 {
                        self.buffered.interrupt = true;
                    } else {
                        self.buffered.ready = true;
                    }
                    break;
                }
                if self.input_ended {
                    break;
                }
                continue;
            }
            let value = if raw == b'\r' && self.mode.icrnl {
                b'\n'
            } else if raw == b'\n' && self.mode.inlcr {
                b'\r'
            } else {
                raw
            };
            if self.mode.canonical {
                match raw {
                    127 => {
                        if self.buffered.len > 0 {
                            self.buffered.len -= 1;
                            self.buffered.record[self.buffered.len] = 0;
                            if self.mode.echo {
                                self.stage_output(Role::Stdout, b"\x08 \x08")?;
                            }
                        }
                    }
                    21 => {
                        self.buffered.clear_record();
                        if self.mode.echo {
                            self.stage_byte(Role::Stdout, b'\n')?;
                        }
                    }
                    4 => {
                        if self.buffered.len == 0 {
                            self.buffered.empty_eof = true;
                        } else {
                            self.buffered.ready = true;
                        }
                    }
                    _ => {
                        if self.buffered.len == 63 && value != b'\n' {
                            self.failed = true;
                            return Err(Error::Backend(-75));
                        }
                        self.buffered.record[self.buffered.len] = value;
                        self.buffered.len += 1;
                        if self.mode.echo {
                            self.stage_byte(Role::Stdout, value)?;
                        }
                        if value == b'\n' {
                            self.buffered.ready = true;
                        }
                    }
                }
            } else {
                self.buffered.record[self.buffered.len] = value;
                self.buffered.len += 1;
                if self.buffered.len == output.len().min(TRANSFER) {
                    self.buffered.ready = true;
                }
            }
            if self.buffered.ready || self.buffered.empty_eof || self.input_ended {
                break;
            }
        }
        self.flush_output(caller, |role, bytes| input.write(role, bytes))?;
        if self.buffered.interrupt {
            self.buffered.interrupt = false;
            return Err(Error::Interrupted);
        }
        if self.buffered.len > 0
            && (self.buffered.ready || !self.mode.canonical || self.input_ended)
        {
            return Ok(self.publish_record(output));
        }
        if self.buffered.empty_eof {
            self.buffered.empty_eof = false;
            return Ok(ReadOutcome::Eof);
        }
        if self.input_ended {
            return Ok(ReadOutcome::Eof);
        }
        Err(Error::WouldBlock)
    }
    pub fn write(
        &mut self,
        caller: Caller,
        reference: &Reference,
        input: &[u8],
        mut transport: impl FnMut(Role, &[u8]) -> Completion,
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
        #[cfg(native_tty_canonical_probe)]
        if self.mode.opost || self.buffered.tx_at < self.buffered.tx_len {
            return self.write_processed(alias.role, input, transport);
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
