// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Concrete owner composition. Offline construction is not native acceptance.
use abi29_dispatch_core::{
    children::{Children, Identity as Child, Wait},
    startup::Identity,
};
use af07_transport::Endpoints;
use core::mem::MaybeUninit;
use fd_dispatch::Peer;
use fd_startup::{Binding, Plan, Source};
use filesystem_client::Error as FsError;
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity, Process};
use filesystem_service::channel::{Framed, Io};
use fork_gate::Owner;
use fork_streams::{Caller, Outcome, SessionPipe, State};
use owner_control::Control;
use owner_dispatch::{Completion, Event};
pub type Channel<K> = Framed<Endpoints<K>>;
type Gate<K> = Owner<Channel<K>, State>;
#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    Native(i64),
    Protocol,
    Source,
    Gate,
    ReturnedHalt,
}
type Result<T> = core::result::Result<T, Error>;
fn require(ok: bool) -> Result<()> {
    if ok { Ok(()) } else { Err(Error::Protocol) }
}
fn zero(raw: i64) -> Result<()> {
    if raw == 0 {
        Ok(())
    } else {
        Err(Error::Native(raw))
    }
}
fn native(id: Identity) -> Result<NativeIdentity> {
    NativeIdentity::admitted(id.slot, id.epoch, id.handle).map_err(|_| Error::Protocol)
}
fn child(id: Identity) -> Result<Child> {
    Child::admitted(id.slot as usize, id.epoch, id.handle).map_err(|_| Error::Protocol)
}
fn caller(id: Identity) -> Caller {
    if id.slot == 1 {
        Caller::Parent
    } else {
        Caller::Participant {
            slot: (id.slot - 1) as usize,
            generation: id.epoch,
        }
    }
}
fn word(frame: &[u8; 32], at: usize) -> u32 {
    u32::from_le_bytes(frame[at..at + 4].try_into().unwrap())
}
fn put(frame: &mut [u8; 32], at: usize, value: u32) {
    frame[at..at + 4].copy_from_slice(&value.to_le_bytes())
}
#[derive(Clone, Copy)]
struct Instance {
    identity: Option<Identity>,
    epoch: u32,
    generation: u64,
    // Labels only: the Peer owns both local endpoint-close obligations.
    writer: u64,
    terminal: Option<i32>,
    collected: bool,
    pending: Option<[u8; 32]>,
    exec_sequence: u64,
}
impl Instance {
    const fn empty() -> Self {
        Self {
            identity: None,
            epoch: 0,
            generation: 0,
            writer: 0,
            terminal: None,
            collected: false,
            pending: None,
            exec_sequence: 0,
        }
    }
    fn id(&self) -> Result<Identity> {
        self.identity.ok_or(Error::Protocol)
    }
}
/// Immutable outcome selectors; these labels grant no native authority.
#[cfg(fs_file_write_wire)]
#[derive(Debug, PartialEq, Eq)]
pub struct FileObservation {
    pub index: usize,
    pub identity: Identity,
    pub generation: u64,
    pub event: owner_dispatch::FileEvent,
}
pub struct Runtime<K: Control> {
    gate: Gate<K>,
    peers: [Option<Peer<Channel<K>>>; 4],
    records: [Instance; 4],
    children: Children,
    kernel: K,
    engine: u64,
    remaining: u32,
    started: bool,
    #[cfg(fs_file_write_wire)]
    last_file: Option<FileObservation>,
}
impl<K: Control> Runtime<K> {
    /// Single final-slot initialization. The caller retains native obligations
    /// on every failure; no rollback or clean engine export is inferred.
    #[cfg(not(fs_home_owner))]
    pub fn connect_in_place(
        slot: &mut MaybeUninit<Self>,
        kernel: K,
        engine: u64,
        channel: Channel<K>,
        epoch: u64,
        remaining: u32,
    ) -> Result<&mut Self> {
        require(remaining > 0 && remaining <= 1_000_000)?;
        Self::connect_selected(slot, kernel, engine, channel, epoch, remaining)
            .map_err(|_| Error::Source)
    }
    /// Both delegated grants must validate before a Runtime reference exists.
    #[cfg(fs_home_owner)]
    pub fn connect_home_in_place(
        slot: &mut MaybeUninit<Self>,
        kernel: K,
        engine: u64,
        channel: Channel<K>,
        epoch: u64,
        remaining: u32,
    ) -> core::result::Result<&mut Self, filesystem_client::ConnectFailure> {
        Self::connect_selected(slot, kernel, engine, channel, epoch, remaining)
    }
    #[inline(never)]
    fn connect_selected(
        slot: &mut MaybeUninit<Self>,
        kernel: K,
        engine: u64,
        mut channel: Channel<K>,
        epoch: u64,
        remaining: u32,
    ) -> core::result::Result<&mut Self, filesystem_client::ConnectFailure> {
        use filesystem_service::Channel as _;
        if remaining == 0 || remaining > 1_000_000 || (cfg!(fs_home_owner) && engine == 0) {
            return Err(filesystem_client::ConnectFailure {
                error: FsError::Invalid,
                cleanup: channel.close(),
            });
        }
        let console = core::array::from_fn(|i| {
            Some(Source {
                reference: 0x7a000001 | (i as u32) << 16,
                selector: i as u32,
                rights: if i == 0 { 1 } else { 2 },
                bound: 16,
            })
        });
        let streams =
            State::new(console, [SessionPipe::new(), SessionPipe::new()]).map_err(|_| {
                filesystem_client::ConnectFailure {
                    error: FsError::Invalid,
                    cleanup: channel.close(),
                }
            })?;
        let pointer = slot.as_mut_ptr();
        // SAFETY: exclusive aligned MaybeUninit storage. Only the uninitialized
        // gate field is borrowed. No enclosing Runtime reference exists yet.
        let gate = unsafe {
            &mut *core::ptr::addr_of_mut!((*pointer).gate).cast::<MaybeUninit<Gate<K>>>()
        };
        #[cfg(not(fs_home_owner))]
        Owner::connect_in_place(gate, channel, epoch, streams)?;
        #[cfg(fs_home_owner)]
        Owner::connect_home_in_place(gate, channel, epoch, streams)?;
        // SAFETY: gate is fully initialized; all remaining valid fields are moved
        // exactly once without fallible work or callbacks before publication.
        Ok(unsafe {
            for i in 0..4 {
                core::ptr::addr_of_mut!((*pointer).peers)
                    .cast::<Option<Peer<Channel<K>>>>()
                    .add(i)
                    .write(None);
                core::ptr::addr_of_mut!((*pointer).records)
                    .cast::<Instance>()
                    .add(i)
                    .write(Instance::empty());
            }
            core::ptr::addr_of_mut!((*pointer).children).write(Children::new());
            core::ptr::addr_of_mut!((*pointer).kernel).write(kernel);
            core::ptr::addr_of_mut!((*pointer).engine).write(engine);
            core::ptr::addr_of_mut!((*pointer).remaining).write(remaining);
            core::ptr::addr_of_mut!((*pointer).started).write(false);
            #[cfg(fs_file_write_wire)]
            core::ptr::addr_of_mut!((*pointer).last_file).write(None);
            slot.assume_init_mut()
        })
    }
    #[cfg(fs_file_write_wire)]
    pub fn last_file(&self) -> Option<&FileObservation> {
        self.last_file.as_ref()
    }
    /// Current sole-source closes, including retirement after the original
    /// receipt was copied. This neither changes that receipt nor settles natives.
    #[cfg(fs_file_write_wire)]
    pub fn source_cleanup(&self) -> Option<[i64; 2]> {
        self.gate.cleanup()
    }
    fn step(&mut self) -> Result<()> {
        if self.remaining == 0 {
            return Err(Error::Native(-110));
        }
        self.remaining -= 1;
        Ok(())
    }
    fn observe(&mut self) -> Result<u64> {
        self.step()?;
        let r = self.kernel.ctl(0x2a000, 0xe002, 0);
        zero(r.0)?;
        Ok(r.1)
    }
    fn park(&mut self, sequence: u64) -> Result<()> {
        self.step()?;
        zero(self.kernel.ctl(0x2a001, 0xe002, sequence).0)
    }
    fn allocate_pair(&mut self) -> Result<[u64; 4]> {
        pairs(&mut self.kernel, 0xd001)
    }
    #[inline(never)]
    fn launch_parent(&mut self, workspace: &mut [u8; 4096]) -> Result<()> {
        let pair = self.allocate_pair()?;
        let mut args = [0; 272];
        args[0] = 1;
        args[16..18].copy_from_slice(b"sh");
        let raw = self.kernel.launch(&args, pair[0], pair[3]);
        let id = Identity::admitted(1, 1, raw as u64).map_err(|_| Error::Native(raw))?;
        let process = self
            .gate
            .admit(|files, _| {
                files
                    .admitted_shell(native(id)?, 7)
                    .map_err(|_| Error::Source)
            })
            .map_err(|_| Error::Gate)??;
        self.install(0, id, process, pair)?;
        let mut plan = Plan {
            identity: id,
            shell: 1,
            parent: 7,
            generation: pair[0],
            bindings: [Binding::default(); 16],
            sources: [Source::default(); 7],
            history: [0; 2],
        };
        for i in 0..3 {
            plan.bindings[i] = Binding {
                kind: 1,
                selector: i as u8,
                cloexec: 0,
            };
            plan.sources[i] = Source {
                reference: 0x7a000001 | (i as u32) << 16,
                selector: i as u32,
                rights: if i == 0 { 1 } else { 2 },
                bound: 16,
            };
        }
        let scratch: &mut [u8; 304] = (&mut workspace[..304]).try_into().unwrap();
        fd_startup::encode(&plan, scratch).map_err(|_| Error::Protocol)?;
        fork_transport::transfer(
            &mut self.kernel,
            self.records[0].writer,
            scratch,
            &mut self.remaining,
            true,
        )
        .map_err(Error::Native)?;
        workspace.fill(0);
        ready(&mut self.kernel, id.handle, &mut self.remaining).map_err(Error::Native)?;
        Ok(())
    }
    fn install(
        &mut self,
        index: usize,
        id: Identity,
        process: Process,
        pair: [u64; 4],
    ) -> Result<()> {
        require(self.peers[index].is_none() && self.records[index].identity.is_none())?;
        self.records[index] = Instance {
            identity: Some(id),
            epoch: id.epoch,
            generation: pair[0],
            writer: pair[1],
            ..Instance::empty()
        };
        let io =
            Endpoints::new(self.kernel.clone(), pair[2], pair[1]).map_err(|_| Error::Protocol)?;
        self.peers[index] =
            Some(Peer::bind(Framed(io), process, pair[0]).map_err(|_| Error::Protocol)?);
        Ok(())
    }
    #[inline(never)]
    fn terminal(&mut self, index: usize) -> Result<bool> {
        if self.records[index].identity.is_none() {
            return Ok(false);
        }
        if self.records[index].terminal.is_some() {
            return Ok(true);
        }
        let id = self.records[index].id()?;
        let status = self.kernel.ctl(0x20001, id.handle, 0);
        if status.0 < 0 {
            return Err(Error::Native(status.0));
        }
        if status.0 == 0 {
            return Ok(false);
        }
        let value = if status.2 == 1 && (1..=256).contains(&status.0) {
            ((status.0 - 1) as i32) << 8
        } else if status.2 == 3 && status.0 == 144 {
            15
        } else {
            return Err(Error::Protocol);
        };
        self.gate
            .admit(|_, streams| streams.confirmed_terminal(caller(id)))
            .map_err(|_| Error::Gate)?
            .map_err(|_| Error::Protocol)?;
        if index != 0 {
            self.children
                .terminal(child(id)?, value)
                .map_err(|_| Error::Protocol)?;
        }
        self.records[index].terminal = Some(value);
        self.records[index].pending = None;
        Ok(true)
    }
    #[inline(never)]
    fn reclaim(&mut self, index: usize) -> Result<()> {
        let record = self.records[index];
        let id = record.id()?;
        require(record.terminal.is_some() && (index == 0 || record.collected))?;
        let peer = self.peers[index].as_mut().ok_or(Error::Protocol)?;
        require(peer.close() == [0; 2])?;
        zero(self.kernel.ctl(0x20002, id.handle, 0).0)?;
        require(self.kernel.ctl(0x20001, id.handle, 0).0 == -9)?;
        self.gate
            .admit(|files, _| {
                let process = files.current(native(id)?).map_err(|_| Error::Source)?;
                files.settled(process).map_err(|_| Error::Source)
            })
            .map_err(|_| Error::Gate)??;
        if index != 0 {
            self.children
                .reclaimed(child(id)?)
                .map_err(|_| Error::Protocol)?;
        }
        self.peers[index] = None;
        self.records[index] = Instance {
            epoch: record.epoch,
            ..Instance::empty()
        };
        Ok(())
    }
    fn stopped(&mut self, index: usize) -> Result<()> {
        if self.records[index].identity.is_none() || self.terminal(index)? {
            return Ok(());
        }
        zero(
            self.kernel
                .ctl(0x20007, self.records[index].id()?.handle, 0)
                .0,
        )?;
        loop {
            let sequence = self.observe()?;
            if self.terminal(index)? {
                return Ok(());
            }
            self.park(sequence)?;
        }
    }
    #[inline(never)]
    fn copy(&mut self, mut plan: Plan, workspace: &mut [u8; 4096]) -> Result<()> {
        let sequence = self.gate.sequence();
        let parent = self.records[0].id()?;
        let freeze = loop {
            let observed = self.observe()?;
            let raw = self.kernel.ctl(0x23004, parent.handle, 0).0;
            if raw < 0 {
                return Err(Error::Native(raw));
            }
            if raw > 0 {
                break raw as u64;
            }
            self.park(observed)?;
        };
        let index = (1..4)
            .find(|&i| self.records[i].identity.is_none() && self.records[i].epoch < 15)
            .ok_or(Error::Native(-28))?;
        let epoch = self.records[index].epoch + 1;
        let slot = index as u32 + 1;
        let target = NativeIdentity::admitted(
            slot,
            epoch,
            0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
        )
        .map_err(|_| Error::Protocol)?;
        let pair = self.allocate_pair()?;
        // Source key is obtained without reopening admission while Capturing.
        let parent_key = self
            .gate
            .captured_process(native(parent)?)
            .map_err(|_| Error::Gate)?;
        let mut staged = false;
        let copied = self
            .gate
            .copy(sequence, parent_key, target, parent.pid, &plan, |streams| {
                if let Err(error) = streams.stage_child(target.pid, &plan) {
                    return CopyAttempt::Refused(i64::from(error));
                }
                staged = true;
                let raw = self
                    .kernel
                    .copy(parent.handle, slot, freeze, pair[0], pair[3]);
                if raw == target.handle as i64 {
                    CopyAttempt::Copied {
                        identity: target,
                        parent_pid: parent.pid,
                    }
                } else if (-4095..=-1).contains(&raw) {
                    CopyAttempt::Refused(raw)
                } else {
                    CopyAttempt::Unknown(raw)
                }
            })
            .map_err(|_| Error::Gate)?;
        match copied {
            Ok(process) => {
                let id =
                    Identity::admitted(slot, epoch, target.handle).map_err(|_| Error::Protocol)?;
                self.children
                    .admit(child(id)?)
                    .map_err(|_| Error::Protocol)?;
                self.install(index, id, process, pair)?;
                plan.identity = id;
                plan.parent = parent.pid;
                plan.generation = pair[0];
                fork_transport::publish(
                    &mut self.gate,
                    &mut self.kernel,
                    fork_transport::Publication {
                        sequence,
                        startup: &plan,
                        child_writer: pair[1],
                        child_reader: pair[2],
                        parent_writer: self.records[0].writer,
                    },
                    &mut self.remaining,
                    (&mut workspace[..304]).try_into().unwrap(),
                )
                .map_err(|_| Error::Gate)?;
            }
            Err(filesystem_remote_descriptors::CopyInheritanceError::Refused(error)) => {
                let outcome = self
                    .gate
                    .resolve_native_refusal(sequence, error, |streams| {
                        if staged {
                            streams.cancel_stage(target.pid).map_err(i64::from)?;
                        }
                        let closed = pair.map(|endpoint| self.kernel.close(endpoint));
                        if closed != [0; 4] {
                            return Err(-5);
                        }
                        Ok(self.kernel.ctl(0x23005, parent.handle, freeze).0)
                    })
                    .map_err(|_| Error::Gate)?;
                require(outcome == Ok(0))?;
                fork_transport::refuse(
                    &mut self.gate,
                    &mut self.kernel,
                    sequence,
                    error,
                    self.records[0].writer,
                    &mut self.remaining,
                    (&mut workspace[..304]).try_into().unwrap(),
                )
                .map_err(|_| Error::Gate)?;
            }
            Err(_) => return Err(Error::Gate),
        }
        workspace.fill(0);
        Ok(())
    }
    #[inline(never)]
    fn stream(
        kernel: &mut K,
        children: &mut Children,
        records: &mut [Instance; 4],
        request: (usize, &[u8; 32]),
        streams: &mut State,
        peer: &mut Peer<Channel<K>>,
        remaining: &mut u32,
    ) -> core::result::Result<Completion, i64> {
        let (index, frame) = request;
        let id = records[index].identity.ok_or(-9)?;
        let mut reserved = None;
        let outcome = if word(frame, 0) == 68 {
            if index != 0 || frame[12..].iter().any(|b| *b != 0) || word(frame, 8) > 1 {
                return Err(-22);
            }
            match children
                .wait(word(frame, 4) as i32, word(frame, 8) == 1)
                .map_err(i64::from)?
            {
                Wait::Pending => Outcome::Pending,
                Wait::NoChange => Outcome::Reply([0; 32]),
                Wait::NoChild => {
                    let mut raw = [0; 32];
                    put(&mut raw, 0, (-10i32) as u32);
                    Outcome::Reply(raw)
                }
                Wait::Ready { identity, status } => {
                    let mut raw = [0; 32];
                    put(&mut raw, 0, identity.pid as u32);
                    put(&mut raw, 4, status as u32);
                    reserved = Some(identity);
                    Outcome::Reply(raw)
                }
            }
        } else {
            streams.request(caller(id), frame, |writing, bytes| {
                kernel.serial(writing, bytes)
            })
        };
        match outcome {
            Outcome::Pending => Ok(Completion::Pending),
            Outcome::Reply(mut raw) => {
                owner_dispatch::reply(peer, &mut raw, remaining)?;
                if let Some(id) = reserved {
                    children.delivered(id).map_err(i64::from)?;
                    records[id.slot - 1].collected = true;
                }
                Ok(Completion::Replied)
            }
        }
    }
    #[inline(never)]
    fn poll(&mut self, index: usize, workspace: &mut [u8; 4096]) -> Result<bool> {
        if self.records[index].identity.is_none() {
            return Ok(false);
        }
        let was_terminal = self.records[index].terminal.is_some();
        if self.terminal(index)? {
            if index != 0 && self.records[index].collected {
                self.reclaim(index)?;
                return Ok(true);
            }
            return Ok(!was_terminal);
        }
        let id = self.records[index].id()?;
        let generation = self.records[index].generation;
        let peer = self.peers[index].as_mut().ok_or(Error::Protocol)?;
        let outcome = if let Some(frame) = self.records[index].pending {
            let result = self
                .gate
                .admit(|_, streams| {
                    Self::stream(
                        &mut self.kernel,
                        &mut self.children,
                        &mut self.records,
                        (index, &frame),
                        streams,
                        peer,
                        &mut self.remaining,
                    )
                })
                .map_err(|_| Error::Gate)?
                .map_err(Error::Native)?;
            if result == Completion::Pending {
                Event::Pending(frame)
            } else {
                Event::Complete
            }
        } else {
            owner_dispatch::poll_exec(
                &mut self.gate,
                peer,
                (id, if index == 0 { 7 } else { 9 }, generation),
                &mut self.remaining,
                workspace,
                |files, streams, peer, request, budget| match request {
                    owner_dispatch::Request::Stream(frame) => Self::stream(
                        &mut self.kernel,
                        &mut self.children,
                        &mut self.records,
                        (index, frame),
                        streams,
                        peer,
                        budget,
                    ),
                    owner_dispatch::Request::Exec(plan, sequence, extra) => {
                        execute(
                            &mut self.kernel,
                            files,
                            streams,
                            peer,
                            &mut self.records[index],
                            (plan, sequence, extra),
                            budget,
                        )?;
                        Ok(Completion::Replied)
                    }
                },
            )
            .map_err(|_| Error::Gate)?
        };
        match outcome {
            #[cfg(fs_file_write_wire)]
            Event::File(event) => self.file_event(index, id, generation, event),
            Event::Idle => Ok(false),
            Event::Eof => {
                require(self.terminal(index)?)?;
                Ok(true)
            }
            Event::Pending(frame) => {
                self.records[index].pending = Some(frame);
                Ok(false)
            }
            Event::Complete => {
                self.records[index].pending = None;
                Ok(true)
            }
            Event::Fork(plan) => {
                require(index == 0)?;
                self.copy(plan, workspace)?;
                Ok(true)
            }
        }
    }
    #[cfg(fs_file_write_wire)]
    #[inline(always)]
    fn file_event(
        &mut self,
        index: usize,
        identity: Identity,
        generation: u64,
        event: owner_dispatch::FileEvent,
    ) -> Result<bool> {
        self.last_file = Some(FileObservation {
            index,
            identity,
            generation,
            event,
        });
        let retained = self.last_file.as_ref().unwrap();
        retained.event.admission.as_ref().map_err(|_| Error::Gate)?;
        retained
            .event
            .exchange
            .delivery
            .as_ref()
            .map_err(|_| Error::Source)?;
        Ok(true)
    }
    #[inline(never)]
    pub fn run(&mut self, workspace: &mut [u8; 4096]) -> Result<()> {
        require(!self.started)?;
        self.started = true;
        let result = self.run_inner(workspace);
        if result.is_err() {
            // A partial reply or unknown copy cannot be retried through run().
            // Native obligations remain retained; no terminal/reclaim is inferred.
            self.gate.retire();
        }
        result
    }
    #[inline(never)]
    fn run_inner(&mut self, workspace: &mut [u8; 4096]) -> Result<()> {
        self.launch_parent(workspace)?;
        loop {
            let observed = self.observe()?;
            let mut progress = false;
            for index in 0..4 {
                progress |= self.poll(index, workspace)?;
            }
            let pending = core::array::from_fn(|i| self.records[i].pending.is_some());
            self.gate
                .admit(|_, streams| streams.retire_idle(pending))
                .map_err(|_| Error::Gate)?;
            if self.records[0].terminal.is_some() {
                for index in 1..4 {
                    if self.records[index].identity.is_some() {
                        self.stopped(index)?;
                        if !self.records[index].collected {
                            self.children
                                .abandon_after_parent_terminal(child(self.records[index].id()?)?)
                                .map_err(|_| Error::Protocol)?;
                            self.records[index].collected = true;
                        }
                        self.reclaim(index)?;
                    }
                }
                self.reclaim(0)?;
                break;
            }
            if !progress {
                self.park(observed)?;
            }
        }
        self.shutdown()
    }
    // Keep terminal source-close scratch off the live polling call chain.
    #[inline(never)]
    fn shutdown(&mut self) -> Result<()> {
        let engine = self.engine;
        let outcome = self
            .gate
            .admit(|files, _| {
                files.disconnect_checked(|channel| {
                    loop {
                        if self.remaining == 0 {
                            return Err(FsError::Transport(-110));
                        }
                        self.remaining -= 1;
                        let sequence = self.kernel.ctl(0x2a000, 0xe002, 0);
                        if sequence.0 != 0 {
                            return Err(FsError::Transport(sequence.0));
                        }
                        let state = self.kernel.ctl(0x20001, engine, 0);
                        if state.0 > 0 {
                            if state.0 != 1 || state.2 != 1 {
                                return Err(FsError::Protocol);
                            }
                            break;
                        }
                        if state.0 < 0 {
                            return Err(FsError::Transport(state.0));
                        }
                        let raw = self.kernel.ctl(0x2a001, 0xe002, sequence.1).0;
                        if raw != 0 {
                            return Err(FsError::Transport(raw));
                        }
                    }
                    let mut byte = [0];
                    if channel.0.transfer(false, &mut byte) != 0
                        || channel.0.transfer(true, &mut byte) != -32
                    {
                        return Err(FsError::Protocol);
                    }
                    Ok(())
                })
            })
            .map_err(|_| Error::Gate)?
            .map_err(|_| Error::Source)?;
        require(outcome == [0; 2])?;
        zero(self.kernel.ctl(0x20002, engine, 0).0)?;
        require(self.kernel.ctl(0x20001, engine, 0).0 == -9)?;
        self.engine = 0;
        zero(self.kernel.ctl(0x26002, 0xf001, 0).0)?;
        self.kernel.ctl(0x2a002, 0xf002, 0);
        Err(Error::ReturnedHalt)
    }
}
fn pairs(kernel: &mut impl Control, factory: u64) -> Result<[u64; 4]> {
    let req = kernel.ctl(0x24000, factory, 0);
    if req.0 <= 0 {
        return Err(Error::Native(req.0));
    }
    let rep = kernel.ctl(0x24000, factory, 0);
    if rep.0 <= 0 {
        return Err(Error::Native(rep.0));
    }
    let endpoints = [req.0 as u64, req.1, rep.0 as u64, rep.1];
    for i in 0..4 {
        require(endpoints[i] != 0 && !endpoints[..i].contains(&endpoints[i]))?;
    }
    Ok(endpoints)
}
/// Provision only the engine/service connection. No greeting is consumed here.
pub fn provision(kernel: &mut impl Control, remaining: &mut u32) -> Result<(u64, [u64; 4])> {
    let endpoints = pairs(kernel, 0xd002)?;
    let engine = kernel.engine(endpoints[0], endpoints[3]);
    require(engine == 0xb0000101)?;
    zero(kernel.delegate(engine as u64, &[8, 2097152, 7]))?;
    while *remaining > 0 {
        *remaining -= 1;
        let state = kernel.ctl(0x20001, engine as u64, 0);
        require(state.0 == 0 && state.1 <= 1)?;
        if state.1 == 1 {
            return Ok((engine as u64, endpoints));
        }
        zero(kernel.ctl(0x1fffe, 0, 0).0)?;
    }
    Err(Error::Native(-110))
}

fn ready(
    kernel: &mut impl Control,
    process: u64,
    remaining: &mut u32,
) -> core::result::Result<(), i64> {
    loop {
        let sequence = observe(kernel, remaining)?;
        let state = kernel.ctl(0x20001, process, 0);
        if state.0 != 0 || state.1 > 1 {
            return Err(-5);
        }
        if state.1 == 1 {
            return Ok(());
        }
        pause(kernel, sequence, remaining)?;
    }
}
fn observe(kernel: &mut impl Control, remaining: &mut u32) -> core::result::Result<u64, i64> {
    spend(remaining)?;
    let raw = kernel.ctl(0x2a000, 0xe002, 0);
    if raw.0 != 0 {
        return Err(raw.0);
    }
    Ok(raw.1)
}
fn spend(remaining: &mut u32) -> core::result::Result<(), i64> {
    if *remaining == 0 {
        return Err(-110);
    }
    *remaining -= 1;
    Ok(())
}
fn pause(
    kernel: &mut impl Control,
    sequence: u64,
    remaining: &mut u32,
) -> core::result::Result<(), i64> {
    spend(remaining)?;
    let raw = kernel.ctl(0x2a001, 0xe002, sequence).0;
    if raw == 0 { Ok(()) } else { Err(raw) }
}
/// One complete immutable-helper exec under the already closed route gate.
/// Actual source/frame/native observations remain distinct; no retry on error.
#[inline(never)]
fn execute<K: Control>(
    kernel: &mut K,
    files: &mut filesystem_remote_descriptors::ProcessFiles<Channel<K>>,
    streams: &mut State,
    peer: &mut Peer<Channel<K>>,
    record: &mut Instance,
    request: (&mut Plan, u64, &[u8; 304]),
    remaining: &mut u32,
) -> core::result::Result<(), i64> {
    let (plan, sequence, extra) = request;
    let id = record.identity.ok_or(-9)?;
    if plan.identity != id || plan.generation != record.generation {
        return Err(-9);
    }
    if sequence <= record.exec_sequence || sequence == u64::MAX {
        return Err(-22);
    }
    let process = files.current(native(id).map_err(|_| -9)?).map_err(|_| -9)?;
    let mut view = (0u16, 0u16);
    for binding in &plan.bindings {
        if binding.kind == 3 {
            view.0 |= 1u16 << binding.selector;
            if binding.cloexec == 1 {
                view.1 |= 1u16 << binding.selector;
            }
        }
    }
    if files.file_view_v1(process).map_err(|_| -9)? != view {
        return Err(-13);
    }
    streams
        .validate_context(caller(id), plan)
        .map_err(i64::from)?;
    record.exec_sequence = sequence;
    let freeze = loop {
        let observed = observe(kernel, remaining)?;
        let raw = kernel.ctl(0x23004, id.handle, 0).0;
        if raw < 0 {
            return Err(raw);
        }
        if raw > 0 {
            break raw as u64;
        }
        pause(kernel, observed, remaining)?;
    };
    let before = kernel.receipt(id.handle);
    if before.0 < 0 || before.2 != 0 {
        return Err(-5);
    }
    let next = record.generation.checked_add(1);
    let denied = if id.slot == 1 {
        -13
    } else if &extra[..14] != b"/inputs/helper" || extra[14..32].iter().any(|b| *b != 0) {
        if extra.starts_with(b"/inputs/missing\0") {
            -2
        } else {
            -13
        }
    } else if next.is_none() {
        -75
    } else {
        0
    };
    let raw = if denied != 0 {
        denied
    } else {
        kernel.exec(id.handle, freeze, extra[32..].try_into().unwrap())
    };
    if (-4095..=-1).contains(&raw) {
        if kernel.receipt(id.handle) != before {
            return Err(-5);
        }
        if kernel.ctl(0x23005, id.handle, freeze).0 != 0 {
            return Err(-5);
        }
        let mut refusal = exec_frames::refusal(sequence, raw).map_err(i64::from)?;
        owner_dispatch::reply(peer, &mut refusal, remaining)?;
        return Ok(());
    }
    if raw != 0 || kernel.receipt(id.handle) != (freeze as i64, 0xc003, 1) {
        return Err(-5);
    }
    // Only confirmed image commit permits destructive FILE/stream changes.
    files.commit_exec_close(process).map_err(|_| -5)?;
    streams.commit_exec(caller(id), plan).map_err(i64::from)?;
    plan.generation = next.ok_or(-75)?;
    peer.rebind_after_exec(process, plan.generation)
        .map_err(|_| -5)?;
    record.generation = plan.generation;
    record.exec_sequence = 0;
    let mut startup = [0; 304];
    fd_startup::encode(plan, &mut startup).map_err(i64::from)?;
    if kernel.publish(id.handle, freeze) != 0 {
        return Err(-5);
    }
    // The committed image may run only its validated startup reader until ready.
    fork_transport::transfer(kernel, record.writer, &mut startup, remaining, true)?;
    startup.fill(0);
    ready(kernel, id.handle, remaining)?;
    plan.sources.fill(Source::default());
    Ok(())
}

#[cfg(test)]
extern crate std;
#[cfg(all(test, not(fs_home_owner)))]
#[path = "owner_exec_tests.rs"]
mod exec_tests;

#[cfg(all(test, fs_home_owner))]
#[path = "home_owner_tests.rs"]
mod home_tests;
