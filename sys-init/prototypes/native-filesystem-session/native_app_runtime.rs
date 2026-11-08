// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! One ordinary app; the selected Zsh variant privately retains filesystem custody.
use abi29_dispatch_core::startup::Identity;
use af07_transport::Endpoints;
use core::mem::ManuallyDrop;
#[cfg(native_zsh_filesystem)]
use core::mem::MaybeUninit;
#[cfg(native_zsh_filesystem)]
#[path = "zsh_namespace.rs"]
mod zsh_namespace;
#[cfg(native_zsh_filesystem)]
use zsh_namespace::Namespace;
#[cfg(native_zsh_filesystem)]
const TERMINFO: &[u8] = include_bytes!(env!("AETHER_ZSH_TERMINFO"));
#[cfg(native_zsh_file_exec)]
const FILE_EXEC_ELF: &[u8] = include_bytes!(env!("AETHER_ZSH_FILE_EXEC_ELF"));
#[cfg(native_zsh_file_exec)]
const _: () = assert!(!FILE_EXEC_ELF.is_empty() && FILE_EXEC_ELF.len() <= 4096);
#[cfg(all(
    native_zsh_filesystem,
    not(all(
        native_tty_mode_probe,
        native_tty_signal_probe,
        native_tty_canonical_probe
    ))
))]
compile_error!("Zsh filesystem requires matched canonical MODE and SIGINT");
use fd_startup::{Binding, Plan, Source};
use filesystem_service::channel::Io;
use fork_streams::{Caller, Outcome, SessionPipe, State};
pub use owner_control::AppControl;
use owner_control::{Control, Deadline, Observation, Status};
#[path = "stream_transport.rs"]
mod stream_transport;
#[cfg(native_tty_mode_probe)]
#[path = "tty_mode.rs"]
pub mod tty_mode;

pub const ATTEMPTS: u32 = 1_000_000;
pub const RESERVED: u32 = 12;
pub const WRITER_DEADLINE_TICK: u64 = 6_000;
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
use serial_tty::{
    Bindings, Completion, Error as TtyError, Mode, ReadOutcome, Rights, Stop, Terminal,
};

#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
const DESCRIPTORS: usize = 3;
#[cfg(not(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
)))]
const DESCRIPTORS: usize = 2;
pub const TEMPLATE: &[u8] = b"/home/t.XXXXXX";
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct End {
    pub cap: u64,
    pub owned: bool,
    pub attempted: bool,
    pub status: i64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Snapshot {
    pub ends: [End; 8],
    pub engine: u64,
    pub app: u64,
    pub left: u32,
    pub reserved: u32,
    pub failure: i64,
    pub request_bytes: usize,
    pub reply_bytes: usize,
    pub terminal_attempted: bool,
    pub cleanup_started: bool,
    pub cleanup_attempted: [[bool; 4]; 2],
    pub cleanup: [[Status; 4]; 2],
    pub console_status: i64,
    pub observed_terminal: [Option<Status>; 2],
    pub sequence: u64,
    #[cfg(native_zsh_filesystem)]
    pub filesystem_requests: u32,
    #[cfg(native_tty_mode_probe)]
    pub mode_cleanup: Option<i64>,
    #[cfg(native_tty_mode_probe)]
    pub mode_state: Option<(bool, u64)>,
}
struct Bound {
    left: u32,
    reserved: u32,
    deadline: Deadline,
    sequence: u64,
    last_tick: u64,
    failed: i64,
}
impl Bound {
    fn spend(&mut self) -> Result<(), i64> {
        if self.failed != 0 {
            return Err(self.failed);
        }
        if self.left == 0 {
            self.failed = -110;
            return Err(-110);
        }
        self.left -= 1;
        Ok(())
    }
    fn check(&mut self, kernel: &mut impl Control) -> Result<(), i64> {
        self.spend()?;
        let raw = kernel.observe_events();
        let result = (|| {
            let observation = Observation::checked(raw)?;
            if observation.tick < self.last_tick {
                return Err(-5);
            }
            self.last_tick = observation.tick;
            self.sequence = self.deadline.check(raw)?;
            Ok(())
        })();
        if let Err(error) = result {
            self.failed = error;
        }
        result
    }
    fn before(&mut self, kernel: &mut impl Control) -> Result<(), i64> {
        self.check(kernel)?;
        self.spend()
    }
    #[cfg(native_zsh_operator)]
    fn wake(&mut self, raw: Status, sequence: u64) -> Result<(), i64> {
        let observed = Observation::checked(raw)?;
        if observed.tick < self.last_tick
            || observed.sequence < self.sequence
            || observed.sequence < sequence
        {
            return Err(-5);
        }
        self.sequence = self.deadline.check(raw)?;
        self.last_tick = observed.tick;
        Ok(())
    }
    fn reserve(&mut self) -> Result<(), i64> {
        if self.reserved == 0 {
            self.failed = -5;
            return Err(-5);
        }
        self.reserved -= 1;
        Ok(())
    }
}
#[cfg(native_zsh_process)]
// This shared closed codec also provides opposite-direction encoders for tests.
#[allow(dead_code)]
#[path = "zsh_process_frames.rs"]
mod zsh_process_frames;
#[cfg(native_zsh_process)]
use abi29_dispatch_core::children::{Children, Identity as ChildIdentity, ReadLease, Wait};
#[cfg(native_zsh_process)]
use fd_startup::ForkStreams;
#[cfg(all(native_zsh_process, not(native_zsh_filesystem)))]
compile_error!("Zsh process controller requires retained filesystem custody");
#[cfg(all(native_zsh_home_write, not(native_zsh_process)))]
compile_error!("Zsh home write requires the matched process controller");
#[cfg(all(native_zsh_file_exec, not(native_zsh_process)))]
compile_error!("Zsh file exec requires the matched process controller");
#[cfg(all(native_zsh_file_exec, native_zsh_home_write))]
compile_error!("Zsh file exec and home write are separate closed profiles");
#[cfg(all(
    native_zsh_cold_reopen,
    not(all(native_zsh_file_exec, native_zsh_process, native_zsh_filesystem))
))]
compile_error!("cold reopen requires the complete selected filesystem file-exec profile");
#[cfg(all(
    native_zsh_idle_exit,
    not(any(native_zsh_cold_reopen, native_zsh_home_redirection))
))]
compile_error!("idle exit requires the selected cold reopen profile");
#[cfg(all(native_zsh_login_startup, not(native_zsh_home_redirection)))]
compile_error!("login startup requires its complete home redirection profile");
#[cfg(all(native_zsh_repeat_exec, not(native_zsh_home_cwd_exec)))]
compile_error!("repeat exec requires the complete cold home CWD exec profile");
#[cfg(all(native_zsh_home_cwd_exec, not(native_zsh_home_cwd)))]
compile_error!("home CWD exec requires the complete cold home CWD profile");
#[cfg(all(native_zsh_operator, not(native_zsh_idle_exit)))]
compile_error!("operator session requires the selected idle exit profile");

#[cfg(native_zsh_process)]
struct ZshProcess<K: AppControl> {
    binding: Option<filesystem_readonly::Binding>,
    endpoints: Option<ManuallyDrop<Endpoints<K>>>,
    ends: [End; 4],
    children: Children,
    lease: ReadLease,
    request: [u8; 32],
    at: usize,
    parent_at: usize,
    fork_sequence: u64,
    sequence: u64,
    epoch: u8,
    prepaid: u8,
    fork_ready: bool,
    committed: bool,
    exec_ready: bool,
    wait_status: Option<i32>,
    terminal: Option<i32>,
    reclaimed: bool,
    cleanup_attempted: u8,
    cleanup_last: Status,
}
#[cfg(native_zsh_process)]
impl<K: AppControl> ZshProcess<K> {
    fn new() -> Self {
        Self {
            binding: None,
            endpoints: None,
            ends: [End::default(); 4],
            children: Children::new(),
            lease: ReadLease::Parent,
            request: [0; 32],
            at: 0,
            parent_at: 0,
            fork_sequence: 0,
            sequence: 0,
            epoch: 0,
            prepaid: 0,
            fork_ready: false,
            committed: false,
            exec_ready: false,
            wait_status: None,
            terminal: None,
            reclaimed: false,
            cleanup_attempted: 0,
            cleanup_last: (-5, 0, 0),
        }
    }
    #[cfg(all(native_zsh_idle_exit, any(not(native_zsh_repeat_exec), test)))]
    fn pristine(&self) -> bool {
        self.epoch == 0
            && self.fork_sequence == 0
            && self.sequence == 0
            && self.children == Children::new()
            && self.binding.is_none()
            && self.endpoints.is_none()
            && self.ends == [End::default(); 4]
            && self.lease == ReadLease::Parent
            && self.at == 0
            && self.parent_at == 0
            && self.prepaid == 0
            && !self.fork_ready
            && !self.committed
            && !self.exec_ready
            && self.wait_status.is_none()
            && self.terminal.is_none()
            && !self.reclaimed
            && self.cleanup_attempted == 0
            && self.cleanup_last == (-5, 0, 0)
    }
    #[cfg(native_zsh_repeat_exec)]
    fn repeat_ready(&self) -> bool {
        self.epoch == 1
            && self.committed
            && self.exec_ready
            && self.terminal == Some(5888)
            && self.wait_status == Some(5888)
            && self.reclaimed
            && self.lease == ReadLease::Parent
            && self.binding.is_none()
            && self.endpoints.is_none()
            && self
                .ends
                .iter()
                .all(|end| !end.owned || (end.attempted && end.status == 0))
    }
    fn identity(&self) -> Result<Identity, i64> {
        let binding = self.binding.ok_or(-9)?;
        Identity::admitted(2, u32::from(binding.epoch), binding.handle).map_err(i64::from)
    }
    fn child(&self) -> Result<ChildIdentity, i64> {
        let id = self.identity()?;
        ChildIdentity::admitted(2, id.epoch, id.handle).map_err(i64::from)
    }
    fn caller(&self) -> Result<Caller, i64> {
        Ok(Caller::Child(self.identity()?.epoch))
    }
}

pub struct Runtime<K: AppControl> {
    kernel: K,
    bound: Bound,
    ends: [End; 8],
    engine: u64,
    app: u64,
    identity: Option<Identity>,
    streams: State,
    // Explicit ledger owns physical close attempts. Suppress Endpoints' fallback
    // Drop so a recorded negative close can never be retried on function return.
    endpoints: Option<ManuallyDrop<Endpoints<K>>>,
    #[cfg(native_zsh_filesystem)]
    files: MaybeUninit<filesystem_readonly::Files<Namespace<K>>>,
    #[cfg(native_zsh_filesystem)]
    files_live: bool,
    #[cfg(native_zsh_filesystem)]
    file_binding: Option<filesystem_readonly::Binding>,
    #[cfg(native_zsh_filesystem)]
    file_header: [u8; 64],
    #[cfg(native_zsh_filesystem)]
    filesystem_requests: u32,
    #[cfg(native_zsh_filesystem)]
    namespace_prepaid: [u64; 2],
    request: [u8; 32],
    reply: [u8; 32],
    request_at: usize,
    reply_at: usize,
    closed: [bool; DESCRIPTORS],
    #[cfg(any(
        native_tty_byte_probe,
        native_tty_descriptor_probe,
        any(native_tty_duplex_probe, native_tty_mode_probe)
    ))]
    tty: Option<(Terminal, Bindings, serial_tty::Caller)>,
    #[cfg(native_tty_mode_probe)]
    mode: Option<tty_mode::State>,
    console_attempted: bool,
    terminal_attempted: bool,
    started: bool,
    cleanup_started: bool,
    cleanup_attempted: [[bool; 4]; 2],
    cleanup: [[Status; 4]; 2],
    console_status: i64,
    observed_terminal: [Option<Status>; 2],
    #[cfg(native_zsh_process)]
    process: ZshProcess<K>,
}
impl<K: AppControl> Runtime<K> {
    pub fn new(kernel: K) -> Result<Self, i64> {
        let streams = State::new(
            [
                if cfg!(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                )) {
                    Some(console(0))
                } else {
                    None
                },
                Some(console(1)),
                Some(console(2)),
            ],
            [SessionPipe::new(), SessionPipe::new()],
        )
        .map_err(i64::from)?;
        Ok(Self {
            kernel,
            bound: Bound {
                left: ATTEMPTS - RESERVED,
                reserved: RESERVED,
                deadline: Deadline::after(0, WRITER_DEADLINE_TICK)?,
                sequence: 0,
                last_tick: 0,
                failed: 0,
            },
            ends: [End::default(); 8],
            engine: 0,
            app: 0,
            identity: None,
            streams,
            endpoints: None,
            #[cfg(native_zsh_filesystem)]
            files: MaybeUninit::uninit(),
            #[cfg(native_zsh_filesystem)]
            files_live: false,
            #[cfg(native_zsh_filesystem)]
            file_binding: None,
            #[cfg(native_zsh_filesystem)]
            file_header: [0; 64],
            #[cfg(native_zsh_filesystem)]
            filesystem_requests: 0,
            #[cfg(native_zsh_filesystem)]
            namespace_prepaid: [0; 2],
            request: [0; 32],
            reply: [0; 32],
            request_at: 0,
            reply_at: 0,
            closed: [false; DESCRIPTORS],
            #[cfg(any(
                native_tty_byte_probe,
                native_tty_descriptor_probe,
                any(native_tty_duplex_probe, native_tty_mode_probe)
            ))]
            tty: None,
            #[cfg(native_tty_mode_probe)]
            mode: None,
            console_attempted: false,
            terminal_attempted: false,
            started: false,
            cleanup_started: false,
            cleanup_attempted: [[false; 4]; 2],
            cleanup: [[(-5, 0, 0); 4]; 2],
            console_status: -5,
            observed_terminal: [None; 2],
            #[cfg(native_zsh_process)]
            process: ZshProcess::new(),
        })
    }
    /// Selected Owner construction in its final mapped slot. Initialization
    /// scratch returns before dispatch; no whole Runtime value is copied through
    /// the entry frame. Existing by-value constructors/profiles stay unchanged.
    #[cfg(native_zsh_filesystem)]
    #[inline(never)]
    pub fn initialize_in_place(slot: &mut MaybeUninit<Self>, kernel: K) -> Result<&mut Self, i64> {
        let streams = State::new(
            [Some(console(0)), Some(console(1)), Some(console(2))],
            [SessionPipe::new(), SessionPipe::new()],
        )
        .map_err(i64::from)?;
        let deadline = Deadline::after(0, WRITER_DEADLINE_TICK)?;
        let pointer = slot.as_mut_ptr();
        // SAFETY: slot is unique aligned uninitialized storage. Only raw field
        // projections are formed; every field is initialized before publication.
        // State/deadline validation precedes writes and no later step can fail.
        // Kernel moves last, so no owning field is abandoned by a returned error.
        // files intentionally remains MaybeUninit until Client admission; no
        // padding or uninitialized Files bytes are read or copied as Runtime.
        unsafe {
            core::ptr::addr_of_mut!((*pointer).bound).write(Bound {
                left: ATTEMPTS - RESERVED,
                reserved: RESERVED,
                deadline,
                sequence: 0,
                last_tick: 0,
                failed: 0,
            });
            core::ptr::addr_of_mut!((*pointer).ends).write([End::default(); 8]);
            core::ptr::addr_of_mut!((*pointer).engine).write(0);
            core::ptr::addr_of_mut!((*pointer).app).write(0);
            core::ptr::addr_of_mut!((*pointer).identity).write(None);
            core::ptr::addr_of_mut!((*pointer).streams).write(streams);
            core::ptr::addr_of_mut!((*pointer).endpoints).write(None);
            core::ptr::addr_of_mut!((*pointer).files).write(MaybeUninit::uninit());
            core::ptr::addr_of_mut!((*pointer).files_live).write(false);
            core::ptr::addr_of_mut!((*pointer).file_binding).write(None);
            core::ptr::addr_of_mut!((*pointer).file_header).write([0; 64]);
            core::ptr::addr_of_mut!((*pointer).filesystem_requests).write(0);
            core::ptr::addr_of_mut!((*pointer).namespace_prepaid).write([0; 2]);
            core::ptr::addr_of_mut!((*pointer).request).write([0; 32]);
            core::ptr::addr_of_mut!((*pointer).reply).write([0; 32]);
            core::ptr::addr_of_mut!((*pointer).request_at).write(0);
            core::ptr::addr_of_mut!((*pointer).reply_at).write(0);
            core::ptr::addr_of_mut!((*pointer).closed).write([false; DESCRIPTORS]);
            core::ptr::addr_of_mut!((*pointer).tty).write(None);
            core::ptr::addr_of_mut!((*pointer).mode).write(None);
            core::ptr::addr_of_mut!((*pointer).console_attempted).write(false);
            core::ptr::addr_of_mut!((*pointer).terminal_attempted).write(false);
            core::ptr::addr_of_mut!((*pointer).started).write(false);
            core::ptr::addr_of_mut!((*pointer).cleanup_started).write(false);
            core::ptr::addr_of_mut!((*pointer).cleanup_attempted).write([[false; 4]; 2]);
            core::ptr::addr_of_mut!((*pointer).cleanup).write([[(-5, 0, 0); 4]; 2]);
            core::ptr::addr_of_mut!((*pointer).console_status).write(-5);
            core::ptr::addr_of_mut!((*pointer).observed_terminal).write([None; 2]);
            #[cfg(native_zsh_process)]
            core::ptr::addr_of_mut!((*pointer).process).write(ZshProcess::new());
            core::ptr::addr_of_mut!((*pointer).kernel).write(kernel);
            Ok(slot.assume_init_mut())
        }
    }
    pub fn snapshot(&self) -> Snapshot {
        Snapshot {
            ends: self.ends,
            engine: self.engine,
            app: self.app,
            left: self.bound.left,
            reserved: self.bound.reserved,
            failure: self.bound.failed,
            request_bytes: self.request_at,
            reply_bytes: self.reply_at,
            terminal_attempted: self.terminal_attempted,
            cleanup_started: self.cleanup_started,
            cleanup_attempted: self.cleanup_attempted,
            cleanup: self.cleanup,
            console_status: self.console_status,
            observed_terminal: self.observed_terminal,
            sequence: self.bound.sequence,
            #[cfg(native_zsh_filesystem)]
            filesystem_requests: self.filesystem_requests,
            #[cfg(native_tty_mode_probe)]
            mode_cleanup: self.mode.as_ref().and_then(tty_mode::State::cleanup_result),
            #[cfg(native_tty_mode_probe)]
            mode_state: self
                .tty
                .as_ref()
                .and_then(|(t, b, c)| t.mode_state(*c, &b.stdin).ok().map(|(m, r)| (m.icrnl, r))),
        }
    }
    fn ctl(&mut self, op: u64, cap: u64, argument: u64) -> Result<Status, i64> {
        self.bound.before(&mut self.kernel)?;
        Ok(self.kernel.ctl(op, cap, argument))
    }
    fn yield_now(&mut self) -> Result<(), i64> {
        zero(self.ctl(0x1fffe, 0, 0)?.0)
    }
    fn acquire(&mut self, cap: u64) -> Result<(), i64> {
        if cap == 0 || self.ends.iter().any(|end| end.cap == cap) {
            return Err(-5);
        }
        let end = self.ends.iter_mut().find(|end| end.cap == 0).ok_or(-28)?;
        *end = End {
            cap,
            owned: true,
            attempted: false,
            status: -5,
        };
        Ok(())
    }
    fn transferred(&mut self, cap: u64) -> Result<(), i64> {
        let end = self
            .ends
            .iter_mut()
            .find(|end| end.cap == cap && end.owned)
            .ok_or(-5)?;
        end.owned = false;
        Ok(())
    }
    fn pair(&mut self, factory: u64) -> Result<[u64; 4], i64> {
        let first = self.ctl(0x24000, factory, 0)?;
        if first.0 <= 0 {
            return Err(if first.0 < 0 { first.0 } else { -5 });
        }
        self.acquire(first.0 as u64)?;
        self.acquire(first.1)?;
        // Never discard first-pair obligations if this second acquisition fails.
        let second = self.ctl(0x24000, factory, 0)?;
        if second.0 <= 0 {
            return Err(if second.0 < 0 { second.0 } else { -5 });
        }
        self.acquire(second.0 as u64)?;
        self.acquire(second.1)?;
        let caps = [first.0 as u64, first.1, second.0 as u64, second.1];
        let service = factory == 0xd002;
        for (index, cap) in caps.iter().enumerate() {
            let object = (cap >> 16) & 255;
            let generation = (cap >> 8) & 255;
            if cap >> 24 != 0xd1
                || cap & 255 != (index % 2 + 1) as u64
                || generation == 0
                || generation > if service { 3 } else { 15 }
                || if service {
                    !(10..12).contains(&object)
                } else {
                    object >= 10
                }
            {
                return Err(-5);
            }
        }
        Ok(caps)
    }
    /// Snapshot320 bytes/real returned Identity; no namespace read is reachable.
    pub fn provision(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        if self.started {
            return Err(-16);
        }
        self.started = true;
        self.bound.check(&mut self.kernel)?;
        let service = self.pair(0xd002)?;
        self.bound.before(&mut self.kernel)?;
        let engine = self.kernel.engine(service[0], service[3]);
        if engine <= 0 {
            return Err(if engine < 0 { engine } else { -5 });
        }
        self.engine = engine as u64;
        self.transferred(service[0])?;
        self.transferred(service[3])?;
        if self.engine != 0xb0000101 {
            return Err(-5);
        }
        self.bound.before(&mut self.kernel)?;
        zero(self.kernel.delegate(self.engine, &[8, 2097152, 7]))?;
        loop {
            let state = self.ctl(0x20001, self.engine, 0)?;
            if state.0 != 0 || state.1 > 1 || state.2 != 0 {
                return Err(-5);
            }
            if state.1 == 1 {
                break;
            }
            self.yield_now()?;
        }
        let process = self.pair(0xd001)?;
        let record: &mut [u8; 320] = (&mut workspace[..320]).try_into().unwrap();
        encode_launch(record, self.engine, service[2], service[1])?;
        #[cfg(native_zsh_filesystem)]
        {
            // Prepay exactly two retained namespace closes from the ordinary
            // allowance before app admission. No reserve increase or refund.
            self.bound.spend()?;
            self.bound.spend()?;
            self.namespace_prepaid = [service[2], service[1]];
        }
        self.bound.before(&mut self.kernel)?;
        let app = self.kernel.launch_app(record, process[2], process[1]);
        record.fill(0);
        if app <= 0 {
            return Err(if app < 0 { app } else { -5 });
        }
        self.app = app as u64;
        #[cfg(not(native_zsh_filesystem))]
        for cap in [service[2], service[1], process[2], process[1]] {
            self.transferred(cap)?;
        }
        #[cfg(native_zsh_filesystem)]
        for cap in [process[2], process[1]] {
            self.transferred(cap)?;
        }
        self.identity = Some(Identity::admitted(1, 1, self.app).map_err(i64::from)?);
        #[cfg(any(
            native_tty_byte_probe,
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        ))]
        {
            let identity = self.identity.ok_or(-9)?;
            let caller = serial_tty::Caller {
                identity: identity.handle,
                generation: u64::from(identity.epoch),
            };
            let (terminal, bindings) = Terminal::admit(
                identity.handle,
                caller,
                [
                    if cfg!(native_tty_mode_probe) {
                        Rights::READ.union(Rights::MODE)
                    } else {
                        Rights::READ
                    },
                    Rights::WRITE,
                    Rights::WRITE,
                ],
                Mode::IMMEDIATE,
            )
            .map_err(tty_errno)?;
            #[cfg(native_tty_mode_probe)]
            let (terminal, bindings) = {
                let mut terminal = terminal;
                self.mode = Some(tty_mode::State::admit(&mut terminal, &bindings, caller)?);
                (terminal, bindings)
            };
            self.tty = Some((terminal, bindings, caller));
        }
        self.endpoints = Some(ManuallyDrop::new(
            Endpoints::new(self.kernel.clone(), process[0], process[3]).map_err(|_| -5)?,
        ));
        #[cfg(native_zsh_filesystem)]
        {
            let identity = self.identity.ok_or(-9)?;
            let binding = filesystem_readonly::Binding {
                slot: identity.slot as u8,
                epoch: identity.epoch as u8,
                handle: identity.handle,
                generation: process[0],
            };
            let mut namespace = Namespace::new(self.kernel.clone(), service[2], service[1]);
            // SAFETY: these disjoint Runtime fields stay exclusively borrowed
            // through construction. No Self reference/move/reentry is possible;
            // failed construction drops/closes while the loans remain live.
            unsafe {
                namespace.arm(
                    &mut self.bound,
                    &mut self.ends,
                    &mut self.filesystem_requests,
                    &mut self.namespace_prepaid,
                )
            }
            .map_err(fs_errno)?;
            let connected = filesystem_readonly::Files::connect_in_place(
                &mut self.files,
                namespace,
                service[0],
                binding,
            );
            match connected {
                Ok(files) => {
                    files
                        .configure(|io| {
                            io.disarm();
                            Ok(())
                        })
                        .map_err(fs_errno)?;
                    self.files_live = true;
                    self.file_binding = Some(binding);
                }
                Err(error) => return Err(fs_errno(error.error)),
            }
            #[cfg(not(native_zsh_cold_reopen))]
            self.with_files(|files| files.provision(TERMINFO, workspace))?;
            #[cfg(native_zsh_cold_reopen)]
            self.with_files(|files| files.reopen(TERMINFO, workspace))?;
            #[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
            self.with_files(|files| files.provision_file_exec(FILE_EXEC_ELF))?;
            #[cfg(native_zsh_cold_reopen)]
            self.with_files(|files| files.reopen_file_exec(FILE_EXEC_ELF, workspace))?;
            #[cfg(native_zsh_home_redirection_reader)]
            self.with_files(|files| files.reopen_note(workspace))?;
        }
        let mut bindings = [Binding::default(); 16];
        bindings[1] = Binding {
            kind: 1,
            selector: 1,
            cloexec: 0,
        };
        bindings[2] = Binding {
            kind: 1,
            selector: 2,
            cloexec: 0,
        };
        #[cfg(any(
            native_tty_byte_probe,
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        ))]
        {
            bindings[0] = Binding {
                kind: 1,
                selector: 0,
                cloexec: 0,
            };
        }
        #[cfg(any(
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        ))]
        {
            let (terminal, references, caller) = self.tty.as_ref().ok_or(-9)?;
            for (selector, reference, role) in [
                (0, &references.stdin, serial_tty::Role::Stdin),
                (1, &references.stdout, serial_tty::Role::Stdout),
                (2, &references.stderr, serial_tty::Role::Stderr),
            ] {
                if terminal.classify(*caller, reference).map_err(tty_errno)? != role {
                    return Err(-9);
                }
                bindings[selector].kind = 4;
            }
        }
        let mut sources = [Source::default(); 7];
        #[cfg(any(
            native_tty_byte_probe,
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        ))]
        {
            sources[0] = console(0);
        }
        sources[1] = console(1);
        sources[2] = console(2);
        #[cfg(any(native_tty_duplex_probe, native_tty_mode_probe))]
        {
            let (terminal, references, caller) = self.tty.as_ref().ok_or(-9)?;
            validate_terminal_sources(
                terminal,
                references,
                *caller,
                &sources[..3].try_into().unwrap(),
            )?;
        }
        let plan = Plan {
            identity: self.identity.unwrap(),
            shell: 1,
            parent: 7,
            generation: process[0],
            bindings,
            sources,
            history: [0; 2],
        };
        let startup: &mut [u8; fd_startup::BYTES] =
            (&mut workspace[..fd_startup::BYTES]).try_into().unwrap();
        fd_startup::encode(&plan, startup).map_err(i64::from)?;
        let mut progress = 0;
        let result = stream_transport::transfer(
            &mut OwnerSteps {
                kernel: &mut self.kernel,
                bound: &mut self.bound,
                endpoints: self.endpoints.as_mut().ok_or(-9)?,
                progress: &mut progress,
            },
            startup,
            true,
        );
        startup.fill(0);
        result
    }
    #[cfg(not(native_zsh_process))]
    fn request(
        &mut self,
        #[allow(unused_variables)] workspace: &mut [u8; 4096],
    ) -> Result<bool, i64> {
        self.request.fill(0);
        self.request_at = 0;
        self.reply_at = 0;
        // A real EOF before the header, after successful descriptor closes,
        // ends the process stream. A yield result is never interpreted as EOF.
        loop {
            self.bound.before(&mut self.kernel)?;
            let count = self
                .endpoints
                .as_mut()
                .ok_or(-9)?
                .transfer(false, &mut self.request[..16]);
            if count == -11 {
                self.yield_now()?;
                continue;
            }
            if count == 0 {
                return if self.closed == [true; DESCRIPTORS] {
                    Ok(false)
                } else {
                    Err(-5)
                };
            }
            if !(0..=16).contains(&count) {
                return Err(if count < 0 { count } else { -5 });
            }
            self.request_at = count as usize;
            break;
        }
        let header_remaining = 16 - self.request_at;
        if header_remaining != 0 {
            let start = self.request_at;
            stream_transport::transfer(
                &mut OwnerSteps {
                    kernel: &mut self.kernel,
                    bound: &mut self.bound,
                    endpoints: self.endpoints.as_mut().ok_or(-9)?,
                    progress: &mut self.request_at,
                },
                &mut self.request[start..16],
                false,
            )?;
        }
        #[cfg(native_zsh_filesystem)]
        if self.request[..8] == filesystem_readonly::MAGIC[..] {
            self.file_header.fill(0);
            self.file_header[..16].copy_from_slice(&self.request[..16]);
            stream_transport::transfer(
                &mut OwnerSteps {
                    kernel: &mut self.kernel,
                    bound: &mut self.bound,
                    endpoints: self.endpoints.as_mut().ok_or(-9)?,
                    progress: &mut self.request_at,
                },
                &mut self.file_header[16..],
                false,
            )?;
            self.file_request(workspace)?;
            return Ok(true);
        }
        let control = cfg!(native_tty_mode_probe)
            && (matches!(u32_at(&self.request, 0), 0x10..=0x1f)
                || u32_at(&self.request, 4) == 0x7d000001);
        if !output_header(&self.request) && !control {
            return Err(-22);
        }
        stream_transport::transfer(
            &mut OwnerSteps {
                kernel: &mut self.kernel,
                bound: &mut self.bound,
                endpoints: self.endpoints.as_mut().ok_or(-9)?,
                progress: &mut self.request_at,
            },
            &mut self.request[16..],
            false,
        )?;
        #[cfg(native_tty_mode_probe)]
        if control {
            self.reply = self.mode_request()?;
        }
        if !control {
            #[cfg(native_tty_canonical_probe)]
            if u32_at(&self.request, 0) == 3 {
                self.flush_terminal_output()?;
            }
            #[cfg(native_tty_signal_probe)]
            let eligible = {
                if u32_at(&self.request, 0) == 1 {
                    if self.request[16] > 1 || self.request[17..] != [0; 15] {
                        return Err(-22);
                    }
                    self.request[16] != 0
                } else {
                    false
                }
            };
            #[cfg(native_tty_signal_probe)]
            let mut frame = self.request;
            #[cfg(native_tty_signal_probe)]
            if u32_at(&frame, 0) == 1 {
                frame[16] = 0;
            }
            #[cfg(not(native_tty_signal_probe))]
            let frame = self.request;
            loop {
                let kernel = &mut self.kernel;
                let bound = &mut self.bound;
                #[cfg(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                ))]
                let (terminal, bindings, caller) = self.tty.as_mut().ok_or(-9)?;
                #[cfg(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                ))]
                let reference = match u32_at(&self.request, 8) {
                    0 => bindings.stdin,
                    1 => bindings.stdout,
                    _ => bindings.stderr,
                };
                #[cfg(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                ))]
                let mut unknown = false;
                let reply = self
                    .streams
                    .request(Caller::Parent, &frame, |writing, bytes| {
                        if let Err(error) = bound.before(kernel) {
                            return error;
                        }
                        #[cfg(not(any(
                            native_tty_byte_probe,
                            native_tty_descriptor_probe,
                            any(native_tty_duplex_probe, native_tty_mode_probe)
                        )))]
                        {
                            kernel.serial(writing, bytes)
                        }
                        #[cfg(any(
                            native_tty_byte_probe,
                            native_tty_descriptor_probe,
                            any(native_tty_duplex_probe, native_tty_mode_probe)
                        ))]
                        {
                            let result = if writing {
                                terminal.write(*caller, &reference, bytes, |role, input| {
                                    #[cfg(not(native_tty_canonical_probe))]
                                    debug_assert_eq!(
                                        role,
                                        if u32_at(&self.request, 8) == 1 {
                                            serial_tty::Role::Stdout
                                        } else {
                                            serial_tty::Role::Stderr
                                        }
                                    );
                                    #[cfg(native_tty_canonical_probe)]
                                    {
                                        let _ = role;
                                        if bound.before(kernel).is_err() {
                                            return Completion {
                                                count: 0,
                                                stop: Stop::Unknown,
                                            };
                                        }
                                    }
                                    let mut scratch = [0; 16];
                                    scratch[..input.len()].copy_from_slice(input);
                                    completion(
                                        kernel.serial(true, &mut scratch[..input.len()]),
                                        input.len(),
                                    )
                                })
                            } else {
                                #[cfg(native_tty_signal_probe)]
                                let result = terminal.read_signalled(
                                    *caller,
                                    &reference,
                                    bytes,
                                    eligible,
                                    &mut SignalBackend {
                                        kernel,
                                        bound,
                                        target: self.app,
                                        #[cfg(native_zsh_operator)]
                                        rx_empty: &mut false,
                                    },
                                );
                                #[cfg(not(native_tty_signal_probe))]
                                let result = terminal.read(*caller, &reference, bytes, |output| {
                                    completion(kernel.serial(false, output), output.len())
                                });
                                result.map(|outcome| match outcome {
                                    ReadOutcome::Bytes(n) => n,
                                    ReadOutcome::EmptyRequest | ReadOutcome::Eof => 0,
                                })
                            };
                            match result {
                                Ok(count) => count as i64,
                                Err(TtyError::UnknownCompletion) => {
                                    unknown = true;
                                    -5
                                }
                                Err(error) => tty_errno(error),
                            }
                        }
                    });
                #[cfg(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                ))]
                if unknown {
                    return Err(-5);
                }
                #[cfg(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                ))]
                if u32_at(&self.request, 0) == 3
                    && matches!(&reply, Outcome::Reply(raw) if u32_at(raw, 0) == 0)
                {
                    terminal.close(*caller, reference).map_err(tty_errno)?;
                }
                match reply {
                    Outcome::Pending => self.yield_now()?,
                    Outcome::Reply(reply) => {
                        self.reply = reply;
                        break;
                    }
                }
            }
        }
        stream_transport::transfer(
            &mut OwnerSteps {
                kernel: &mut self.kernel,
                bound: &mut self.bound,
                endpoints: self.endpoints.as_mut().ok_or(-9)?,
                progress: &mut self.reply_at,
            },
            &mut self.reply,
            true,
        )?;
        if u32_at(&self.request, 0) == 3 && u32_at(&self.reply, 0) == 0 {
            self.closed[u32_at(&self.request, 8) as usize
                - usize::from(!cfg!(any(
                    native_tty_byte_probe,
                    native_tty_descriptor_probe,
                    any(native_tty_duplex_probe, native_tty_mode_probe)
                )))] = true;
        }
        Ok(true)
    }
    #[cfg(native_tty_canonical_probe)]
    fn flush_terminal_output(&mut self) -> Result<(), i64> {
        loop {
            if !self.tty.as_ref().ok_or(-9)?.0.output_pending() {
                return Ok(());
            }
            self.mode_peer_live()?;
            let (terminal, _, caller) = self.tty.as_mut().ok_or(-9)?;
            let kernel = &mut self.kernel;
            let bound = &mut self.bound;
            let result = terminal.flush_output(*caller, |_role, bytes| {
                if bound.before(kernel).is_err() {
                    return Completion {
                        count: 0,
                        stop: Stop::Unknown,
                    };
                }
                let mut scratch = [0; 3];
                scratch[..bytes.len()].copy_from_slice(bytes);
                completion(
                    kernel.serial(true, &mut scratch[..bytes.len()]),
                    bytes.len(),
                )
            });
            match result {
                Ok(()) => return Ok(()),
                Err(TtyError::WouldBlock) => self.yield_now()?,
                Err(e) => return Err(tty_errno(e)),
            }
        }
    }
    #[cfg(native_tty_mode_probe)]
    fn drain(&mut self) -> Result<(), i64> {
        #[cfg(native_tty_canonical_probe)]
        self.flush_terminal_output()?;
        loop {
            self.mode_peer_live()?;
            self.bound.before(&mut self.kernel)?;
            match self.kernel.transmitter_empty() {
                0 => return Ok(()),
                -11 => {}
                e => return Err(e),
            }
            // Observe, recheck, then timed park. No later request can pass this
            // fixed request while it owns the synchronous owner loop.
            self.bound.check(&mut self.kernel)?;
            self.bound.spend()?;
            match self.kernel.transmitter_empty() {
                0 => return Ok(()),
                -11 => {}
                e => return Err(e),
            }
            let wake = self
                .bound
                .last_tick
                .saturating_add(1)
                .min(self.bound.deadline.get());
            let deadline = Deadline::after(wake - 1, 1)?;
            self.bound.spend()?;
            let status = self.kernel.park_events(self.bound.sequence, Some(deadline));
            match status.0 {
                0 => {
                    self.bound.deadline.check(status)?;
                }
                -110 => {} // Timed sample; rescan from a fresh observation.
                error => return Err(error),
            }
        }
    }
    #[cfg(native_tty_mode_probe)]
    fn mode_peer_live(&mut self) -> Result<(), i64> {
        let state = self.ctl(0x20001, self.app, 0)?;
        if state.0 == 0 { Ok(()) } else { Err(-125) }
    }
    #[cfg(native_tty_mode_probe)]
    fn mode_request(&mut self) -> Result<[u8; 32], i64> {
        let op = u32_at(&self.request, 0);
        let prepared = {
            let (terminal, refs, caller) = self.tty.as_ref().ok_or(-9)?;
            self.mode
                .as_ref()
                .ok_or(-9)?
                .prepare(terminal, refs, *caller, &self.request)
        };
        let request = match prepared {
            Ok(request) => request,
            Err(e) => return Ok(tty_mode::error(op, e)),
        };
        #[cfg(native_tty_signal_probe)]
        if request.enabling_signals() {
            self.bound.before(&mut self.kernel)?;
            match self.kernel.terminal_sigint(self.app, false) {
                0 | 1 => {}
                e if e < 0 => return Ok(tty_mode::error(op, e)),
                _ => return Err(-5),
            }
        }
        if request.drain()
            && let Err(e) = self.drain()
        {
            if matches!(e, -110 | -125) || self.bound.failed != 0 {
                return Err(e);
            }
            return Ok(tty_mode::error(op, e));
        }
        self.mode_peer_live()?;
        self.bound.check(&mut self.kernel)?;
        #[cfg(native_tty_signal_probe)]
        if request.enabling_signals() {
            self.bound.spend()?;
            match self.kernel.terminal_sigint(self.app, false) {
                0 | 1 => {}
                e if e < 0 => return Ok(tty_mode::error(op, e)),
                _ => return Err(-5),
            }
            // The kernel preflight is an observation, never a deadline lease.
            self.bound.check(&mut self.kernel)?;
        }
        let (terminal, refs, caller) = self.tty.as_mut().ok_or(-9)?;
        Ok(
            match self
                .mode
                .as_mut()
                .ok_or(-9)?
                .commit(terminal, refs, *caller, request)
            {
                Ok(reply) => reply,
                Err(error) => tty_mode::error(op, error),
            },
        )
    }
    #[cfg(native_tty_mode_probe)]
    fn cleanup_mode(&mut self) -> Result<(), i64> {
        if let (Some(mode), Some((terminal, _, caller))) = (self.mode.as_mut(), self.tty.as_mut()) {
            mode.cleanup(terminal, *caller, true)?;
        }
        Ok(())
    }
    #[cfg(native_zsh_filesystem)]
    fn with_files<R>(
        &mut self,
        call: impl FnOnce(
            &mut filesystem_readonly::Files<Namespace<K>>,
        ) -> Result<R, filesystem_readonly::Error>,
    ) -> Result<R, i64> {
        if !self.files_live {
            return Err(-9);
        }
        // SAFETY: files_live is set only after successful in-place construction;
        // the field has not moved or been dropped. Other field loans are disjoint.
        let files = unsafe { self.files.assume_init_mut() };
        files
            .configure(|io| {
                // SAFETY: sole synchronous callback, exclusive disjoint field loans;
                // all result paths below disarm, and fatal close disarms itself.
                unsafe {
                    io.arm(
                        &mut self.bound,
                        &mut self.ends,
                        &mut self.filesystem_requests,
                        &mut self.namespace_prepaid,
                    )
                }
            })
            .map_err(fs_errno)?;
        let result = call(files);
        if files.cleanup().is_none() {
            files
                .configure(|io| {
                    io.disarm();
                    Ok(())
                })
                .map_err(fs_errno)?;
        }
        result.map_err(fs_errno)
    }
    #[cfg(native_zsh_filesystem)]
    fn file_request(
        &mut self,
        workspace: &mut [u8; 4096],
        #[cfg(native_zsh_process)] child: bool,
    ) -> Result<(), i64> {
        #[cfg(native_zsh_process)]
        let binding = if child {
            self.process.binding
        } else {
            self.file_binding
        }
        .ok_or(-9)?;
        #[cfg(not(native_zsh_process))]
        let binding = self.file_binding.ok_or(-9)?;
        #[cfg(native_zsh_process)]
        let identity = if child {
            Some(self.process.identity()?)
        } else {
            self.identity
        };
        #[cfg(not(native_zsh_process))]
        let identity = self.identity;
        if identity.map(|id| (id.slot as u8, id.epoch as u8, id.handle))
            != Some((binding.slot, binding.epoch, binding.handle))
        {
            return Err(-9);
        }
        #[cfg(native_zsh_process)]
        self.zsh_live(child)?;
        #[cfg(not(native_zsh_process))]
        self.mode_peer_live()?;
        let header = self.file_header;
        let length = self.with_files(|files| files.body_length(binding, &header))?;
        workspace.fill(0);
        #[cfg(native_zsh_process)]
        let endpoints = if child {
            self.process.endpoints.as_mut()
        } else {
            self.endpoints.as_mut()
        }
        .ok_or(-9)?;
        #[cfg(not(native_zsh_process))]
        let endpoints = self.endpoints.as_mut().ok_or(-9)?;
        stream_transport::transfer(
            &mut OwnerSteps {
                kernel: &mut self.kernel,
                bound: &mut self.bound,
                endpoints,
                progress: &mut self.request_at,
            },
            &mut workspace[..length],
            false,
        )?;
        // Authenticate the exact admitted generation again after body assembly.
        #[cfg(native_zsh_process)]
        self.zsh_live(child)?;
        #[cfg(not(native_zsh_process))]
        self.mode_peer_live()?;
        let files = unsafe { self.files.assume_init_mut() };
        files
            .configure(|io| {
                // SAFETY: same nonmoving disjoint synchronous loans as with_files.
                unsafe {
                    io.arm(
                        &mut self.bound,
                        &mut self.ends,
                        &mut self.filesystem_requests,
                        &mut self.namespace_prepaid,
                    )
                }
            })
            .map_err(fs_errno)?;
        let result = (|| {
            let mut reply = files
                .prepare(binding, &header, length, workspace)
                .map_err(fs_errno)?;
            let mut bytes = *reply.header();
            #[cfg(any(native_zsh_home_write, native_zsh_home_redirection))]
            let source_closed = reply.source_closed();
            #[cfg(not(any(native_zsh_home_write, native_zsh_home_redirection)))]
            let source_closed = false;
            // End the namespace loan before process I/O reborrows Bound. A lost
            // reply rearms only the close journal before Reply's abort/drop.
            if !source_closed {
                reply
                    .configure(|io| {
                        io.disarm();
                        Ok(())
                    })
                    .map_err(fs_errno)?;
            }
            #[cfg(native_zsh_process)]
            let endpoint = if child {
                self.process.endpoints.as_mut()
            } else {
                self.endpoints.as_mut()
            };
            #[cfg(not(native_zsh_process))]
            let endpoint = self.endpoints.as_mut();
            let delivery = if let Some(endpoints) = endpoint {
                let mut steps = OwnerSteps {
                    kernel: &mut self.kernel,
                    bound: &mut self.bound,
                    endpoints,
                    progress: &mut self.reply_at,
                };
                stream_transport::transfer(&mut steps, &mut bytes, true)
                    .and_then(|()| stream_transport::transfer(&mut steps, reply.body_mut(), true))
            } else {
                Err(-9)
            };
            if !source_closed {
                reply
                    .configure(|io| {
                        // SAFETY: process Steps loan ended above; these four disjoint
                        // fields are exclusively reloaned through settlement/drop.
                        unsafe {
                            io.arm(
                                &mut self.bound,
                                &mut self.ends,
                                &mut self.filesystem_requests,
                                &mut self.namespace_prepaid,
                            )
                        }
                    })
                    .map_err(fs_errno)?;
            }
            delivery?;
            reply.delivered();
            // Namespace::close already recorded physical closes and disarmed
            // all loans. A retained typed failure may be delivered once, but
            // a closed source cannot resume service or become write success.
            if source_closed { Err(-5) } else { Ok(()) }
        })();
        if files.cleanup().is_none() {
            files
                .configure(|io| {
                    io.disarm();
                    Ok(())
                })
                .map_err(fs_errno)?;
        }
        result
    }
    #[cfg(native_zsh_process)]
    fn zsh_expected(&self, child: bool) -> Result<zsh_process_frames::Expected, i64> {
        Ok(zsh_process_frames::Expected {
            identity: if child {
                self.process.identity()?
            } else {
                self.identity.ok_or(-9)?
            },
            parent: if child {
                self.identity.ok_or(-9)?.pid
            } else {
                7
            },
            generation: if child {
                self.process.binding.ok_or(-9)?.generation
            } else {
                self.file_binding.ok_or(-9)?.generation
            },
        })
    }
    #[cfg(native_zsh_process)]
    #[inline(never)]
    fn zsh_io(&mut self, child: bool, bytes: &mut [u8], writing: bool) -> Result<(), i64> {
        let endpoints = if child {
            self.process.endpoints.as_mut()
        } else {
            self.endpoints.as_mut()
        }
        .ok_or(-9)?;
        let mut progress = 0;
        stream_transport::transfer(
            &mut OwnerSteps {
                kernel: &mut self.kernel,
                bound: &mut self.bound,
                endpoints,
                progress: &mut progress,
            },
            bytes,
            writing,
        )
    }
    #[cfg(native_zsh_process)]
    fn zsh_live(&mut self, child: bool) -> Result<(), i64> {
        self.mode_peer_live()?;
        if child {
            let state = self.ctl(0x20001, self.process.identity()?.handle, 0)?;
            if state.0 != 0 {
                return Err(if state.0 < 0 { state.0 } else { -5 });
            }
        }
        Ok(())
    }
    // Child cleanup calls are prepaid from the SAME ordinary allowance before
    // channel/copy effects. No reserve, deadline or new child budget is created.
    #[cfg(native_zsh_process)]
    fn zsh_leaf(&mut self, op: u64, argument: u64) -> Result<Status, i64> {
        self.bound.check(&mut self.kernel)?;
        self.zsh_leaf_reserved(op, argument)
    }
    #[cfg(native_zsh_process)]
    fn zsh_leaf_reserved(&mut self, op: u64, argument: u64) -> Result<Status, i64> {
        if self.process.prepaid == 0 {
            return Err(-5);
        }
        self.process.prepaid -= 1;
        Ok(self
            .kernel
            .ctl(op, self.process.identity()?.handle, argument))
    }
    #[cfg(native_zsh_process)]
    fn zsh_close_child(&mut self) -> Result<(), i64> {
        let mut error = 0;
        for index in 0..4 {
            let end = self.process.ends[index];
            if !end.owned || end.attempted {
                continue;
            }
            if self.process.prepaid == 0 {
                return Err(-5);
            }
            self.process.prepaid -= 1;
            self.process.ends[index].attempted = true;
            self.process.ends[index].status = self.kernel.close(end.cap);
            if self.process.ends[index].status != 0 {
                error = self.process.ends[index].status;
            }
        }
        zero(error)
    }
    #[cfg(native_zsh_process)]
    fn zsh_pair(&mut self) -> Result<[u64; 4], i64> {
        if self.process.ends.iter().any(|e| e.owned && !e.attempted) {
            return Err(-16);
        }
        for _ in 0..6 {
            self.bound.spend()?;
        }
        self.process.prepaid = 6;
        self.process.ends = [End::default(); 4];
        for pair in 0..2 {
            let value = self.ctl(0x24000, 0xd001, 0)?;
            if value.0 <= 0 {
                return Err(if value.0 < 0 { value.0 } else { -5 });
            }
            for (side, cap) in [value.0 as u64, value.1].into_iter().enumerate() {
                self.process.ends[pair * 2 + side] = End {
                    cap,
                    owned: true,
                    ..End::default()
                };
                if cap >> 24 != 0xd1
                    || cap & 255 != side as u64 + 1
                    || ((cap >> 8) & 255) == 0
                    || ((cap >> 8) & 255) > 15
                    || ((cap >> 16) & 255) >= 10
                {
                    return Err(-5);
                }
            }
        }
        let caps = self.process.ends.map(|e| e.cap);
        for i in 0..4 {
            if caps[..i].contains(&caps[i]) {
                return Err(-5);
            }
        }
        Ok(caps)
    }
    #[cfg(native_zsh_process)]
    fn zsh_frozen(&mut self, handle: u64) -> Result<u64, i64> {
        loop {
            let state = self.ctl(0x23004, handle, 0)?;
            if state.0 > 0 {
                return Ok(state.0 as u64);
            }
            if state.0 < 0 {
                return Err(state.0);
            }
            self.yield_now()?;
        }
    }
    #[cfg(native_zsh_process)]
    fn zsh_validate_files(&mut self, child: bool, raw: &[u8; 336]) -> Result<(), i64> {
        let binding = if child {
            self.process.binding
        } else {
            self.file_binding
        }
        .ok_or(-9)?;
        let actual = self.with_files(|files| files.file_view(binding))?;
        let (mut present, mut cloexec) = (0u16, 0u16);
        for binding in raw[112..176].chunks_exact(4) {
            if binding[0] == 3 {
                present |= 1 << binding[1];
                if binding[2] != 0 {
                    cloexec |= 1 << binding[1];
                }
            }
        }
        if actual != (present, cloexec) {
            return Err(-9);
        }
        Ok(())
    }
    #[cfg(native_zsh_process)]
    #[inline(never)]
    fn zsh_fork(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        if cfg!(all(native_zsh_home_cwd, not(native_zsh_home_cwd_exec))) {
            return Err(-95);
        }
        let expected = self.zsh_expected(false)?;
        let (snapshot, sequence) =
            zsh_process_frames::fork_request(&workspace[..368], expected).map_err(i64::from)?;
        if sequence != self.process.fork_sequence.checked_add(1).ok_or(-28)?
            || self.process.binding.is_some()
            || self.process.lease != ReadLease::Parent
        {
            return Err(-16);
        }
        #[cfg(native_zsh_repeat_exec)]
        if self.process.epoch > 1
            || (self.process.epoch == 1
                && (!self.process.repeat_ready()
                    || !self.with_files(|files| {
                        Ok(files.file_exec_consumed() && !files.file_exec_repeated())
                    })?))
        {
            return Err(-16);
        }
        #[cfg(all(native_zsh_home_redirection, not(native_zsh_home_cwd_exec)))]
        if self.with_files(|files| Ok(files.note_io_active()))? {
            return Err(-16);
        }
        #[cfg(native_zsh_home_cwd_exec)]
        if !self.with_files(|files| Ok(files.note_fork_ready()))? {
            return Err(-16);
        }
        let plan = zsh_stream_plan(snapshot.raw(), expected)?;
        self.streams
            .validate_context(Caller::Parent, &plan)
            .map_err(i64::from)?;
        self.zsh_validate_files(false, snapshot.raw())?;
        let freeze = self.zsh_frozen(expected.identity.handle)?;
        let epoch = self
            .process
            .epoch
            .checked_add(1)
            .filter(|v| *v <= 15)
            .ok_or(-28)?;
        let id = Identity::admitted(2, u32::from(epoch), 0xb0000000 | u64::from(epoch) << 8 | 3)
            .map_err(i64::from)?;
        let caps = self.zsh_pair()?;
        self.streams.stage_child(id.pid, &plan).map_err(i64::from)?;
        self.process.fork_sequence = sequence;
        self.process.sequence = sequence;
        self.process.binding = Some(filesystem_readonly::Binding {
            slot: 2,
            epoch,
            handle: id.handle,
            generation: caps[0],
        });
        self.process.fork_ready = false;
        self.process.committed = false;
        self.process.exec_ready = false;
        self.process.terminal = None;
        self.process.wait_status = None;
        self.process.reclaimed = false;
        self.process.cleanup_attempted = 0;
        self.process.cleanup_last = (-5, 0, 0);
        // On unknown copy, these two ends may already belong to child2. They
        // must never be closed as Owner-held capabilities after that ambiguity.
        self.process.ends[2].owned = false;
        self.process.ends[1].owned = false;
        self.bound.before(&mut self.kernel)?;
        let copied = self
            .kernel
            .copy(expected.identity.handle, 2, freeze, caps[2], caps[1]);
        if copied != id.handle as i64 {
            if !(-4095..=-1).contains(&copied) {
                return Err(-5);
            }
            self.process.ends[2].owned = true;
            self.process.ends[1].owned = true;
            self.process.binding = None;
            self.streams.cancel_stage(id.pid).map_err(i64::from)?;
            self.zsh_close_child()?;
            self.process.prepaid = 0;
            zero(self.ctl(0x23005, expected.identity.handle, freeze)?.0)?;
            let mut reply =
                zsh_process_frames::receipt(b"AEZFR001", sequence, copied).map_err(i64::from)?;
            self.zsh_io(false, &mut reply, true)?;
            workspace.fill(0);
            return Ok(());
        }
        self.process.epoch = epoch;
        self.process
            .children
            .admit(self.process.child()?)
            .map_err(i64::from)?;
        let binding = self.process.binding.ok_or(-9)?;
        let parent = self.file_binding.ok_or(-9)?;
        self.with_files(|files| files.inherit_child(parent, binding))?;
        self.process.endpoints = Some(ManuallyDrop::new(
            Endpoints::new(self.kernel.clone(), caps[0], caps[3]).map_err(|_| -5)?,
        ));
        self.process
            .lease
            .give_child(self.process.child()?, false)
            .map_err(i64::from)?;
        // Publish the complete checked raw snapshot, including duplex byte3.
        let out: &mut [u8; 336] = (&mut workspace[32..368]).try_into().unwrap();
        zsh_rebind_snapshot(out, id, expected.identity.pid, binding.generation)?;
        self.zsh_io(true, out, true)?;
        workspace.fill(0);
        Ok(())
    }
    #[cfg(native_zsh_process)]
    fn zsh_child_ready(&mut self, frame: &[u8; 32]) -> Result<(), i64> {
        let id = self.process.identity()?;
        if self.process.fork_ready || self.process.committed {
            return Err(-9);
        }
        let pid = zsh_process_frames::decode_receipt(frame, b"AEZFC001", self.process.sequence)
            .map_err(i64::from)?;
        if pid != i64::from(id.pid) {
            return Err(-9);
        }
        self.streams.child_ready(id.pid).map_err(i64::from)?;
        self.process.fork_ready = true;
        let mut reply = zsh_process_frames::receipt(b"AEZFR001", self.process.sequence, pid)
            .map_err(i64::from)?;
        self.zsh_io(false, &mut reply, true)
    }
    #[cfg(native_zsh_process)]
    #[inline(never)]
    fn zsh_exec(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        let expected = self.zsh_expected(true)?;
        // The file read clears the whole workspace. Keep the complete exec
        // request, snapshot and arguments in one disjoint owned stack value.
        #[cfg(native_zsh_file_exec)]
        let saved: [u8; 672] = workspace[..672].try_into().unwrap();
        #[cfg(native_zsh_file_exec)]
        let request = &saved;
        #[cfg(not(native_zsh_file_exec))]
        let request: &[u8; 672] = (&workspace[..672]).try_into().unwrap();
        let (snapshot, sequence) =
            zsh_process_frames::exec_request(request, expected).map_err(i64::from)?;
        if !self.process.fork_ready
            || self.process.terminal.is_some()
            || sequence != self.process.sequence.checked_add(1).ok_or(-28)?
        {
            return Err(-9);
        }
        let mut plan = zsh_stream_plan(snapshot.raw(), expected)?;
        self.streams
            .validate_context(self.process.caller()?, &plan)
            .map_err(i64::from)?;
        self.zsh_validate_files(true, snapshot.raw())?;
        let path = &request[368..400];
        #[cfg(native_zsh_file_exec)]
        let rejection = if !path.starts_with(b"/home/probe\0")
            || !zsh_helper_arguments((&request[400..672]).try_into().unwrap())
        {
            -13
        } else {
            0
        };
        #[cfg(not(native_zsh_file_exec))]
        let rejection = if path.starts_with(b"/inputs/missing\0") {
            -2
        } else if path.starts_with(b"/inputs/denied\0") {
            -13
        } else if !path.starts_with(b"/inputs/helper\0") {
            -13
        } else if !zsh_helper_arguments((&request[400..672]).try_into().unwrap()) {
            -13
        } else {
            0
        };
        let freeze = self.zsh_frozen(expected.identity.handle)?;
        self.process.sequence = sequence;
        self.bound.before(&mut self.kernel)?;
        let before = self.kernel.receipt(expected.identity.handle);
        if before.0 < 0 || before.2 != 0 {
            return Err(-5);
        }
        let arguments: &[u8; 272] = (&request[400..672]).try_into().unwrap();
        self.bound.before(&mut self.kernel)?;
        let committed = if rejection != 0 {
            rejection
        } else {
            #[cfg(native_zsh_file_exec)]
            {
                let binding = self.process.binding.ok_or(-9)?;
                #[cfg(native_zsh_repeat_exec)]
                if binding.epoch == 2 {
                    self.with_files(|files| {
                        files.revalidate_file_exec(binding, FILE_EXEC_ELF, workspace)
                    })?;
                }
                let size = self.with_files(|files| files.acquire_file_exec(binding, workspace))?;
                self.bound.before(&mut self.kernel)?;
                self.kernel.exec_file(
                    expected.identity.handle,
                    freeze,
                    arguments,
                    &workspace[..size],
                )
            }
            #[cfg(not(native_zsh_file_exec))]
            self.kernel
                .exec(expected.identity.handle, freeze, arguments)
        };
        #[cfg(native_zsh_file_exec)]
        workspace[..672].copy_from_slice(&saved);
        if committed != 0 {
            if !(-4095..=-1).contains(&committed) {
                return Err(-5);
            }
            self.bound.before(&mut self.kernel)?;
            if self.kernel.receipt(expected.identity.handle) != before {
                return Err(-5);
            }
            zero(self.ctl(0x23005, expected.identity.handle, freeze)?.0)?;
            let mut reply =
                zsh_process_frames::receipt(b"AEZER001", sequence, committed).map_err(i64::from)?;
            self.zsh_io(true, &mut reply, true)?;
            workspace.fill(0);
            return Ok(());
        }
        self.bound.before(&mut self.kernel)?;
        if self.kernel.receipt(expected.identity.handle)
            != (
                freeze as i64,
                if cfg!(native_zsh_file_exec) {
                    0xc004
                } else {
                    0xc003
                },
                1,
            )
        {
            return Err(-5);
        }
        self.streams
            .commit_exec(self.process.caller()?, &mut plan)
            .map_err(i64::from)?;
        let old = self.process.binding.ok_or(-9)?;
        let generation = old
            .generation
            .checked_add(1)
            .filter(|v| *v != u64::MAX)
            .ok_or(-28)?;
        let binding = self.with_files(|files| files.exec_child(old, generation))?;
        self.process.binding = Some(binding);
        let raw: &mut [u8; 336] = (&mut workspace[32..368]).try_into().unwrap();
        zsh_exec_snapshot(raw)?;
        zsh_rebind_snapshot(raw, expected.identity, expected.parent, generation)?;
        // Publish cannot be inferred from a returning exec or a fake READY.
        self.bound.before(&mut self.kernel)?;
        zero(self.kernel.publish(expected.identity.handle, freeze))?;
        self.process.committed = true;
        self.process.exec_ready = false;
        self.zsh_io(true, raw, true)?;
        workspace.fill(0);
        Ok(())
    }
    #[cfg(native_zsh_process)]
    fn zsh_terminal(&mut self) -> Result<(), i64> {
        if self.process.binding.is_none() || self.process.terminal.is_some() {
            return Ok(());
        }
        let state = self.ctl(0x20001, self.process.identity()?.handle, 0)?;
        if state.0 < 0 {
            return Err(state.0);
        }
        if self.process.committed && state.1 == 1 {
            #[cfg(native_zsh_home_write)]
            if !self.process.exec_ready && state.0 == 0 {
                // Matched C003 receipt and publication preceded this actual
                // live native READY; labels alone never arm FILE mutation.
                let binding = self.process.binding.ok_or(-9)?;
                self.with_files(|files| files.admit_home_write(binding))?;
            }
            self.process.exec_ready = true;
        }
        if state.0 == 0 {
            return Ok(());
        }
        if !self.process.fork_ready || state.2 != 1 || !(1..=256).contains(&state.0) {
            return Err(-5);
        }
        let status = ((state.0 - 1) as i32) << 8;
        self.process
            .children
            .terminal(self.process.child()?, status)
            .map_err(i64::from)?;
        self.streams
            .confirmed_terminal(self.process.caller()?)
            .map_err(i64::from)?;
        self.process.terminal = Some(status);
        self.process.at = 0;
        Ok(())
    }
    #[cfg(native_zsh_process)]
    fn zsh_collect(&mut self, identity: ChildIdentity, status: i32) -> Result<(), i64> {
        self.process
            .children
            .delivered(identity)
            .map_err(i64::from)?;
        self.process.wait_status = Some(status);
        let binding = self.process.binding.ok_or(-9)?;
        self.with_files(|files| files.settle_child(binding))?;
        self.zsh_close_child()?;
        zero(self.zsh_leaf(0x20002, 0)?.0)?;
        if self.zsh_leaf(0x20001, 0)?.0 != -9 {
            return Err(-5);
        }
        self.process
            .children
            .reclaimed(identity)
            .map_err(i64::from)?;
        self.process
            .lease
            .restore_parent(identity, &self.process.children)
            .map_err(i64::from)?;
        self.process.binding = None;
        self.process.endpoints = None;
        self.process.prepaid = 0;
        self.process.reclaimed = true;
        self.process.at = 0;
        Ok(())
    }
    #[cfg(native_zsh_process)]
    fn zsh_stream(&mut self, child: bool, frame: &[u8; 32]) -> Result<bool, i64> {
        let op = u32_at(frame, 0);
        let selector = u32_at(frame, 8) as usize;
        #[cfg(native_zsh_operator)]
        let idle_sequence = if !child
            && op == 1
            && selector == 0
            && self.process.parent_at == 32
            && self.process.at == 0
            && self.process.binding.is_none()
            && self.process.lease == ReadLease::Parent
        {
            // Preserve this observation across all final rescan calls. A newer
            // Bound check must not absorb an event before park registration.
            self.bound.check(&mut self.kernel)?;
            let sequence = self.bound.sequence;
            self.operator_peers_live()?;
            Some(sequence)
        } else {
            None
        };
        if op == 68 {
            if child || frame[12..] != [0; 20] {
                return Err(-22);
            }
            let wait = self
                .process
                .children
                .wait_flags(u32_at(frame, 4) as i32, u32_at(frame, 8))
                .map_err(i64::from)?;
            let (mut reply, collected) = match wait {
                Wait::Pending => return Ok(false),
                Wait::NoChange => ([0; 32], None),
                Wait::NoChild => {
                    let mut r = [0; 32];
                    r[..4].copy_from_slice(&(-10i32).to_le_bytes());
                    (r, None)
                }
                Wait::Ready { identity, status } => {
                    let mut r = [0; 32];
                    r[..4].copy_from_slice(&identity.pid.to_le_bytes());
                    r[4..8].copy_from_slice(&status.to_le_bytes());
                    (r, Some((identity, status)))
                }
            };
            self.zsh_io(false, &mut reply, true)?;
            if let Some((identity, status)) = collected {
                self.zsh_collect(identity, status)?;
            }
            return Ok(true);
        }
        if cfg!(native_tty_mode_probe)
            && (matches!(op, 0x10..=0x1f) || u32_at(frame, 4) == 0x7d000001)
        {
            let mut reply = if child {
                let mut r = [0; 32];
                r[..4].copy_from_slice(&(-95i32).to_le_bytes());
                r
            } else {
                self.mode_request()?
            };
            self.zsh_io(child, &mut reply, true)?;
            return Ok(true);
        }
        if op == 1 && selector < 3 {
            if child {
                let (terminal, refs, caller) = self.tty.as_ref().ok_or(-9)?;
                let mode = terminal
                    .mode_state(*caller, &refs.stdin)
                    .map_err(tty_errno)?
                    .0;
                if let Err(error) = self.process.lease.child_read(
                    self.process.child()?,
                    mode.canonical,
                    mode.signals,
                ) {
                    let mut reply = [0; 32];
                    reply[..4].copy_from_slice(&error.to_le_bytes());
                    self.zsh_io(true, &mut reply, true)?;
                    return Ok(true);
                }
            } else if self.process.lease != ReadLease::Parent {
                return Ok(false);
            }
        }
        if op == 3 && selector < 3 {
            self.flush_terminal_output()?;
        }
        let who = if child {
            self.process.caller()?
        } else {
            Caller::Parent
        };
        let kernel = &mut self.kernel;
        let bound = &mut self.bound;
        let (terminal, refs, caller) = self.tty.as_mut().ok_or(-9)?;
        let reference = match selector {
            0 => refs.stdin,
            1 => refs.stdout,
            _ => refs.stderr,
        };
        let mut unknown = false;
        #[cfg(native_zsh_operator)]
        let mut rx_empty = false;
        let mut plain = *frame;
        let eligible = if op == 1 {
            if frame[16] > 1 || frame[17..] != [0; 15] {
                return Err(-22);
            }
            plain[16] = 0;
            frame[16] != 0
        } else {
            false
        };
        let outcome = self.streams.request(who, &plain, |writing, bytes| {
            if let Err(e) = bound.before(kernel) {
                return e;
            }
            let result = if writing {
                terminal.write(*caller, &reference, bytes, |_, input| {
                    let mut scratch = [0; 16];
                    scratch[..input.len()].copy_from_slice(input);
                    completion(
                        kernel.serial(true, &mut scratch[..input.len()]),
                        input.len(),
                    )
                })
            } else {
                terminal
                    .read_signalled(
                        *caller,
                        &reference,
                        bytes,
                        eligible,
                        &mut SignalBackend {
                            kernel,
                            bound,
                            target: self.app,
                            #[cfg(native_zsh_operator)]
                            rx_empty: &mut rx_empty,
                        },
                    )
                    .map(|n| match n {
                        ReadOutcome::Bytes(n) => n,
                        ReadOutcome::EmptyRequest | ReadOutcome::Eof => 0,
                    })
            };
            match result {
                Ok(n) => n as i64,
                Err(TtyError::UnknownCompletion) => {
                    unknown = true;
                    -5
                }
                Err(e) => tty_errno(e),
            }
        });
        if unknown {
            return Err(-5);
        }
        match outcome {
            Outcome::Pending => {
                #[cfg(native_zsh_operator)]
                if rx_empty && !self.tty.as_ref().ok_or(-9)?.0.output_pending() {
                    if let Some(sequence) = idle_sequence {
                        self.operator_peers_live()?;
                        self.bound.before(&mut self.kernel)?;
                        // A synchronous pending request permits no next frame.
                        // EOF or unexpected bytes cannot be hidden by caching it.
                        let mut byte = [0];
                        if self
                            .endpoints
                            .as_mut()
                            .ok_or(-9)?
                            .transfer(false, &mut byte)
                            != -11
                        {
                            return Err(-5);
                        }
                        self.bound.before(&mut self.kernel)?;
                        let wake = self.kernel.park_events(sequence, Some(self.bound.deadline));
                        self.bound.wake(wake, sequence)?;
                        self.operator_peers_live()?;
                    }
                }
                Ok(false)
            }
            Outcome::Reply(mut reply) => {
                self.zsh_io(child, &mut reply, true)?;
                if !child && op == 3 && selector < 3 && u32_at(&reply, 0) == 0 {
                    self.closed[selector] = true;
                }
                Ok(true)
            }
        }
    }
    #[cfg(native_zsh_process)]
    fn zsh_poll(&mut self, child: bool, workspace: &mut [u8; 4096]) -> Result<Option<bool>, i64> {
        if child && (self.process.binding.is_none() || self.process.terminal.is_some()) {
            return Ok(None);
        }
        let mut at = if child {
            self.process.at
        } else {
            self.process.parent_at
        };
        if at < 16 {
            self.bound.before(&mut self.kernel)?;
            let endpoints = if child {
                self.process.endpoints.as_mut()
            } else {
                self.endpoints.as_mut()
            }
            .ok_or(-9)?;
            let frame = if child {
                &mut self.process.request
            } else {
                &mut self.request
            };
            let count = endpoints.transfer(false, &mut frame[at..16]);
            if count == -11 {
                return Ok(None);
            }
            if count == 0 {
                if !child
                    && at == 0
                    && self.closed == [true; DESCRIPTORS]
                    && self.process.binding.is_none()
                {
                    return Ok(Some(false));
                }
                return Err(-5);
            }
            if count < 0 || count as usize > 16 - at {
                return Err(if count < 0 { count } else { -5 });
            }
            at += count as usize;
            if child {
                self.process.at = at;
            } else {
                self.process.parent_at = at;
            }
            if at < 16 {
                return Ok(Some(true));
            }
        }
        if at == 16 {
            let frame = if child {
                self.process.request
            } else {
                self.request
            };
            let large = if &frame[..8] == b"AEZFK001" {
                if child {
                    return Err(-13);
                }
                368
            } else if &frame[..8] == b"AEZEX001" {
                if !child {
                    return Err(-13);
                }
                672
            } else {
                0
            };
            if large != 0 {
                workspace.fill(0);
                workspace[..16].copy_from_slice(&frame[..16]);
                self.zsh_io(child, &mut workspace[16..large], false)?;
                let result = if child {
                    self.zsh_exec(workspace)
                } else {
                    self.zsh_fork(workspace)
                };
                if child {
                    self.process.at = 0;
                } else {
                    self.process.parent_at = 0;
                }
                return result.map(|()| Some(true));
            }
            if frame[..8] == filesystem_readonly::MAGIC[..] {
                self.file_header.fill(0);
                self.file_header[..16].copy_from_slice(&frame[..16]);
                let mut tail = [0; 48];
                self.zsh_io(child, &mut tail, false)?;
                self.file_header[16..].copy_from_slice(&tail);
                self.file_request(workspace, child)?;
                if child {
                    self.process.at = 0;
                } else {
                    self.process.parent_at = 0;
                }
                return Ok(Some(true));
            }
            // A wrong size prefix cannot be a recoverable32-byte request.
            // Reject it before reading any guessed tail or resynchronizing.
            if !zsh_small_header(&frame, child) {
                return Err(-22);
            }
            let mut tail = [0; 16];
            self.zsh_io(child, &mut tail, false)?;
            if child {
                self.process.request[16..].copy_from_slice(&tail);
                self.process.at = 32;
            } else {
                self.request[16..].copy_from_slice(&tail);
                self.process.parent_at = 32;
            }
        }
        let frame = if child {
            self.process.request
        } else {
            self.request
        };
        if &frame[..8] == b"AEZFC001" {
            if !child {
                return Err(-13);
            }
            self.zsh_child_ready(&frame)?;
            self.process.at = 0;
            return Ok(Some(true));
        }
        if self.zsh_stream(child, &frame)? {
            if child {
                self.process.at = 0;
            } else {
                self.process.parent_at = 0;
            }
            return Ok(Some(true));
        }
        Ok(None)
    }
    #[cfg(native_zsh_process)]
    fn request(&mut self, workspace: &mut [u8; 4096]) -> Result<bool, i64> {
        loop {
            self.zsh_terminal()?;
            if let Some(result) = self.zsh_poll(false, workspace)? {
                return Ok(result);
            }
            if let Some(result) = self.zsh_poll(true, workspace)? {
                return Ok(result);
            }
            self.streams.retire_idle([
                self.process.parent_at == 32,
                self.process.at == 32,
                false,
                false,
            ]);
            self.yield_now()?;
        }
    }

    #[cfg(native_zsh_operator)]
    fn operator_peers_live(&mut self) -> Result<(), i64> {
        let parent = self.ctl(0x20001, self.app, 0)?;
        let engine = self.ctl(0x20001, self.engine, 0)?;
        if parent.0 != 0 || parent.1 > 1 || parent.2 != 0 || engine != (0, 1, 0) {
            return Err(-5);
        }
        Ok(())
    }
    #[cfg(native_zsh_operator)]
    fn operator_dispatch(&mut self) -> Result<(), i64> {
        self.bound.check(&mut self.kernel)?;
        if self.bound.deadline.get() != WRITER_DEADLINE_TICK {
            return Err(-5);
        }
        self.bound.deadline = Deadline::after(0, 24_000)?;
        Ok(())
    }
    #[cfg(native_zsh_operator)]
    fn operator_teardown(&mut self) -> Result<(), i64> {
        self.bound.check(&mut self.kernel)?;
        if self.bound.deadline.get() != 24_000 {
            return Err(-5);
        }
        let end = self
            .bound
            .last_tick
            .checked_add(6_000)
            .ok_or(-22)?
            .min(30_000);
        self.bound.deadline = Deadline::after(0, end)?;
        Ok(())
    }

    fn terminal_zero(&mut self, handle: u64) -> Result<(), i64> {
        loop {
            let state = self.ctl(0x20001, handle, 0)?;
            if state.0 < 0 {
                return Err(state.0);
            }
            if state.0 > 0 {
                self.observed_terminal[usize::from(handle == self.engine)] = Some(state);
                // Kernel RAX is retained status+1; RDX is readiness, R8 kind.
                return if state.0 == 1 && state.2 == 1 {
                    Ok(())
                } else {
                    Err(-5)
                };
            }
            self.yield_now()?;
        }
    }
    fn reclaim(&mut self, handle: u64) -> Result<(), i64> {
        zero(self.ctl(0x20002, handle, 0)?.0)?;
        if self.ctl(0x20001, handle, 0)?.0 == -9 {
            Ok(())
        } else {
            Err(-5)
        }
    }
    pub fn run(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        let result = self.run_inner(workspace);
        #[cfg(native_zsh_process)]
        if result.is_err() {
            self.process.lease.contain();
        }
        if let Err(error) = result
            && self.bound.failed == 0
        {
            self.bound.failed = error;
        }
        result
    }
    fn run_inner(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        self.provision(workspace)?;
        #[cfg(native_zsh_operator)]
        self.operator_dispatch()?;
        while self.request(workspace)? {}
        self.terminal_zero(self.app)?;
        #[cfg(native_zsh_operator)]
        self.operator_teardown()?;
        #[cfg(native_zsh_process)]
        {
            if self.process.binding.is_some() || self.process.lease != ReadLease::Parent {
                return Err(-5);
            }
            self.flush_terminal_output()?;
            let (terminal, refs, caller) = self.tty.as_mut().ok_or(-9)?;
            for reference in [refs.stdin, refs.stdout, refs.stderr] {
                terminal.close(*caller, reference).map_err(tty_errno)?;
            }
        }
        #[cfg(native_tty_mode_probe)]
        self.cleanup_mode()?;
        #[cfg(native_zsh_filesystem)]
        {
            let engine = self.engine;
            self.with_files(|files| {
                files
                    .disconnect_checked(|io| io.verify_disconnect(engine))
                    .map(|_| ())
            })?;
        }
        self.close_owned()?;
        self.reclaim(self.app)?;
        self.app = 0;
        // App success/EOF is deliberately independent of engine export/terminal.
        self.terminal_zero(self.engine)?;
        self.reclaim(self.engine)?;
        self.engine = 0;
        self.bound.check(&mut self.kernel)?;
        #[cfg(native_zsh_filesystem)]
        self.write_native_oracle(workspace)?;
        self.close_console()?;
        self.bound.reserve()?;
        self.terminal_attempted = true;
        let _ = self.kernel.ctl(0x2a002, 0xf002, 0);
        Err(-5) // A returning successful halt is a defect, never another attempt.
    }
    /// Selected diagnostic, only after checked healthy teardown.
    /// This reports the actual shared request ledger and cached private MODE
    /// cleanup result. It grants no authority and is not the final halt witness.
    #[cfg(native_zsh_filesystem)]
    #[inline(never)]
    fn write_native_oracle(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        if !(14..=96).contains(&self.filesystem_requests)
            || self.app != 0
            || self.engine != 0
            || !self.files_live
            || self.cleanup_started
            || self.console_attempted
            || self.terminal_attempted
            || self.bound.failed != 0
            || self.namespace_prepaid != [0; 2]
            || self.mode.as_ref().and_then(tty_mode::State::cleanup_result) != Some(0)
            || self
                .observed_terminal
                .iter()
                .any(|state| !matches!(state, Some((1, _, 1))))
            || self
                .ends
                .iter()
                .any(|end| end.owned && (!end.attempted || end.status != 0))
        {
            return Err(-5);
        }
        // SAFETY: files_live is set only after successful final-slot Client
        // construction. Healthy disconnect consumed both close obligations.
        let files = unsafe { self.files.assume_init_ref() };
        if files.cleanup() != Some([0; 2]) {
            return Err(-5);
        }
        #[cfg(native_zsh_home_redirection)]
        if !files.note_complete() {
            return Err(-5);
        }
        #[cfg(all(native_zsh_idle_exit, not(native_zsh_repeat_exec)))]
        let no_child = self.process.pristine() && files.file_exec_unused_closed();
        #[cfg(any(
            native_zsh_repeat_exec,
            all(native_zsh_process, not(native_zsh_idle_exit))
        ))]
        let no_child = false;
        #[cfg(native_zsh_process)]
        {
            let status = if cfg!(native_zsh_file_exec) {
                5888
            } else if cfg!(native_zsh_home_write) {
                0
            } else {
                1792
            };
            if !no_child
                && (self.process.wait_status != Some(status)
                    || self.process.terminal != Some(status)
                    || !self.process.committed
                    || !self.process.exec_ready
                    || !self.process.reclaimed
                    || self.process.lease != ReadLease::Parent
                    || self.process.binding.is_some()
                    || self
                        .process
                        .ends
                        .iter()
                        .any(|end| end.owned && (!end.attempted || end.status != 0)))
            {
                return Err(-5);
            }
        }
        #[cfg(all(native_zsh_idle_exit, not(native_zsh_repeat_exec)))]
        if !no_child && self.process.epoch != 1 {
            return Err(-5);
        }
        #[cfg(native_zsh_repeat_exec)]
        if self.process.epoch != 2 || !files.file_exec_repeated() {
            return Err(-5);
        }
        #[cfg(native_zsh_home_write)]
        if !files.home_write_complete() {
            return Err(-5);
        }
        #[cfg(native_zsh_home_write)]
        const ROW: &[u8] = b"\nAETHER ZSH OWNER v=3 requests=00 child_status=0 exec_ready=1 child_reclaimed=1 parent_lease=1 write_bytes=16 write_closed=1 mode_cleanup=0\n";
        #[cfg(native_zsh_file_exec)]
        let file_exec_size = if no_child {
            0
        } else {
            files.file_exec_size().ok_or(-5)?
        };
        #[cfg(native_zsh_file_exec)]
        const ROW: &[u8] = b"\nAETHER ZSH OWNER v=4 requests=00 child_status=5888 exec_ready=1 child_reclaimed=1 parent_lease=1 file_exec_bytes=0000 file_exec_closed=1 image_receipt=49156 mode_cleanup=0\n";
        #[cfg(all(
            native_zsh_process,
            not(any(native_zsh_home_write, native_zsh_file_exec))
        ))]
        const ROW: &[u8] = b"\nAETHER ZSH OWNER v=2 requests=00 child_status=1792 exec_ready=1 child_reclaimed=1 parent_lease=1 mode_cleanup=0\n";
        #[cfg(not(native_zsh_process))]
        const ROW: &[u8; 49] = b"\nAETHER ZSH OWNER v=1 requests=00 mode_cleanup=0\n";
        #[cfg(native_zsh_idle_exit)]
        let row = if no_child {
            b"\nAETHER ZSH OWNER v=5 requests=00 child=none helper_unused_closed=1 mode_cleanup=0\n"
        } else {
            ROW
        };
        #[cfg(not(native_zsh_idle_exit))]
        let row = ROW;
        workspace[..row.len()].copy_from_slice(row);
        workspace[31] = b'0' + (self.filesystem_requests / 10) as u8;
        workspace[32] = b'0' + (self.filesystem_requests % 10) as u8;
        #[cfg(native_zsh_file_exec)]
        if !no_child {
            const AT: usize = b"\nAETHER ZSH OWNER v=4 requests=00 child_status=5888 exec_ready=1 child_reclaimed=1 parent_lease=1 file_exec_bytes=".len();
            for (index, divisor) in [1000, 100, 10, 1].into_iter().enumerate() {
                workspace[AT + index] = b'0' + ((file_exec_size / divisor) % 10) as u8;
            }
        }
        let result = (|| {
            let mut offset = 0;
            while offset < row.len() {
                let length = (row.len() - offset).min(16);
                self.bound.before(&mut self.kernel)?;
                let count = self
                    .kernel
                    .serial(true, &mut workspace[offset..offset + length]);
                if count == -11 {
                    self.yield_now()?;
                } else if count <= 0 || count as u64 > length as u64 {
                    return Err(if count < 0 { count } else { -5 });
                } else {
                    offset += count as usize;
                }
            }
            Ok(())
        })();
        workspace[..row.len()].fill(0);
        result
    }
    fn close_owned(&mut self) -> Result<(), i64> {
        let mut failure = 0;
        for index in 0..self.ends.len() {
            let end = self.ends[index];
            if !end.owned {
                continue;
            }
            if !end.attempted {
                #[cfg(native_zsh_filesystem)]
                if let Some(credit) = self
                    .namespace_prepaid
                    .iter_mut()
                    .find(|cap| **cap == end.cap)
                {
                    *credit = 0;
                } else {
                    self.bound.reserve()?;
                }
                #[cfg(not(native_zsh_filesystem))]
                self.bound.reserve()?;
                self.ends[index].attempted = true;
                self.ends[index].status = self.kernel.close(end.cap);
            }
            if self.ends[index].status != 0 {
                failure = self.ends[index].status;
            }
        }
        zero(failure)
    }
    fn close_console(&mut self) -> Result<(), i64> {
        if self.console_attempted {
            return Err(-9);
        }
        self.bound.reserve()?;
        self.console_attempted = true;
        self.console_status = self.kernel.ctl(0x26002, 0xf001, 0).0;
        zero(self.console_status)
    }
    /// One-shot containment uses only reserved leaf calls. Unknown terminal read
    /// forbids reclaim. No polling, new logical I/O, grace, or successful halt.
    pub fn contain(&mut self) -> Result<(), i64> {
        if self.terminal_attempted || self.cleanup_started {
            return Err(-5);
        }
        self.cleanup_started = true;
        #[cfg(native_zsh_process)]
        {
            self.process.lease.contain();
            let _ = self.zsh_close_child();
            if self.process.binding.is_some() {
                if let Ok(status) = self.zsh_leaf_reserved(0x20007, 0) {
                    self.process.cleanup_attempted |= 1;
                    self.process.cleanup_last = status;
                }
                if let Ok(status) = self.zsh_leaf_reserved(0x20001, 0) {
                    self.process.cleanup_attempted |= 2;
                    self.process.cleanup_last = status;
                    if status.0 > 0 && matches!(status.2, 1..=4) {
                        if let Ok(status) = self.zsh_leaf_reserved(0x20002, 0) {
                            self.process.cleanup_attempted |= 4;
                            self.process.cleanup_last = status;
                            if status.0 == 0 {
                                if let Ok(status) = self.zsh_leaf_reserved(0x20001, 0) {
                                    self.process.cleanup_attempted |= 8;
                                    self.process.cleanup_last = status;
                                }
                            }
                        }
                    }
                }
            }
        }
        #[cfg(native_zsh_filesystem)]
        if self.files_live {
            let _ = self.with_files(|files| {
                files.abort();
                Ok(())
            });
        }
        let _ = self.close_owned();
        for (index, handle) in [self.app, self.engine].into_iter().enumerate() {
            if handle == 0 {
                continue;
            }
            self.bound.reserve()?;
            self.cleanup_attempted[index][0] = true;
            self.cleanup[index][0] = self.kernel.ctl(0x20007, handle, 0);
            self.bound.reserve()?;
            self.cleanup_attempted[index][1] = true;
            let state = self.kernel.ctl(0x20001, handle, 0);
            self.cleanup[index][1] = state;
            if state.0 > 0 && matches!(state.2, 1..=4) {
                #[cfg(native_tty_mode_probe)]
                if index == 0 {
                    let _ = self.cleanup_mode();
                }
                self.bound.reserve()?;
                self.cleanup_attempted[index][2] = true;
                let reclaimed = self.kernel.ctl(0x20002, handle, 0);
                self.cleanup[index][2] = reclaimed;
                if reclaimed.0 == 0 {
                    self.bound.reserve()?;
                    self.cleanup_attempted[index][3] = true;
                    self.cleanup[index][3] = self.kernel.ctl(0x20001, handle, 0);
                }
            }
        }
        let _ = self.close_console();
        self.bound.reserve()?;
        self.terminal_attempted = true;
        let _ = self.kernel.ctl(0x100e7, 125, 0);
        Err(-5)
    }
}
#[cfg(native_zsh_process)]
fn zsh_stream_plan(raw: &[u8; 336], expected: zsh_process_frames::Expected) -> Result<Plan, i64> {
    zsh_process_frames::snapshot(raw, expected).map_err(i64::from)?;
    let mut plan = Plan {
        identity: expected.identity,
        shell: if expected.identity.slot == 1 {
            expected.identity.epoch
        } else {
            (expected.parent - 2) / 7
        },
        parent: expected.parent,
        generation: expected.generation,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [0; 2],
    };
    let mut held = [false; 7];
    let mut kept = [false; 7];
    for b in raw[112..176].chunks_exact(4) {
        let mut mark = |selector: usize| {
            held[selector] = true;
            kept[selector] |= b[2] == 0;
        };
        match b[0] {
            2 | 4 => mark(b[1] as usize),
            5 => {
                mark(0);
                mark(1);
            }
            0 | 3 => (),
            _ => return Err(-22),
        }
    }
    // This is a stream-holder/CLOEXEC projection, never a serialized FD map.
    // The complete raw map, including every duplex byte3, stays in workspace.
    for i in 0..7 {
        if held[i] {
            plan.bindings[i] = Binding {
                kind: if i < 3 { 1 } else { 2 },
                selector: i as u8,
                cloexec: u8::from(!kept[i]),
            };
            let at = 176 + i * 16;
            plan.sources[i] = Source {
                reference: u32::from_le_bytes(raw[at..at + 4].try_into().unwrap()),
                selector: u32::from_le_bytes(raw[at + 4..at + 8].try_into().unwrap()),
                rights: u32::from_le_bytes(raw[at + 8..at + 12].try_into().unwrap()),
                bound: 16,
            };
        }
    }
    plan.history = [
        u32::from_le_bytes(raw[288..292].try_into().unwrap()),
        u32::from_le_bytes(raw[292..296].try_into().unwrap()),
    ];
    Ok(plan)
}
#[cfg(native_zsh_process)]
fn zsh_rebind_snapshot(
    raw: &mut [u8; 336],
    id: Identity,
    parent: u32,
    generation: u64,
) -> Result<(), i64> {
    let shell = if id.slot == 1 {
        id.epoch
    } else {
        parent.checked_sub(2).ok_or(-9)? / 7
    };
    let greeting = abi29_dispatch_core::startup::greeting(id, shell, parent).map_err(i64::from)?;
    raw[16..48].copy_from_slice(&greeting);
    raw[56..64].copy_from_slice(&generation.to_le_bytes());
    raw[296..304].fill(0);
    zsh_process_frames::snapshot(
        raw,
        zsh_process_frames::Expected {
            identity: id,
            parent,
            generation,
        },
    )
    .map_err(i64::from)?;
    Ok(())
}
#[cfg(native_zsh_process)]
fn zsh_exec_snapshot(raw: &mut [u8; 336]) -> Result<(), i64> {
    for binding in raw[112..176].chunks_exact_mut(4) {
        if binding[2] != 0 {
            binding.fill(0);
        }
    }
    let mut held = [false; 7];
    for binding in raw[112..176].chunks_exact(4) {
        match binding[0] {
            2 | 4 => held[binding[1] as usize] = true,
            5 => {
                held[0] = true;
                held[1] = true;
            }
            0 | 3 => (),
            _ => return Err(-22),
        }
    }
    for (i, used) in held.into_iter().enumerate() {
        if !used {
            raw[176 + i * 16..192 + i * 16].fill(0);
        }
    }
    Ok(())
}

struct OwnerSteps<'a, K: AppControl> {
    kernel: &'a mut K,
    bound: &'a mut Bound,
    endpoints: &'a mut Endpoints<K>,
    progress: &'a mut usize,
}
impl<K: AppControl> stream_transport::Steps for OwnerSteps<'_, K> {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        if let Err(error) = self.bound.before(self.kernel) {
            return error;
        }
        let count = self.endpoints.transfer(writing, bytes);
        if count > 0 && count as u64 <= bytes.len() as u64 {
            *self.progress += count as usize;
        }
        count
    }
    fn wait(&mut self, _: bool) -> i64 {
        if let Err(error) = self.bound.before(self.kernel) {
            return error;
        }
        self.kernel.ctl(0x1fffe, 0, 0).0
    }
}
#[cfg(any(native_tty_duplex_probe, native_tty_mode_probe))]
pub fn validate_terminal_sources(
    terminal: &Terminal,
    references: &Bindings,
    caller: serial_tty::Caller,
    sources: &[Source; 3],
) -> Result<(), i64> {
    for (i, reference, role, rights) in [
        (
            0,
            &references.stdin,
            serial_tty::Role::Stdin,
            if cfg!(native_tty_mode_probe) {
                Rights::READ.union(Rights::MODE)
            } else {
                Rights::READ
            },
        ),
        (
            1,
            &references.stdout,
            serial_tty::Role::Stdout,
            Rights::WRITE,
        ),
        (
            2,
            &references.stderr,
            serial_tty::Role::Stderr,
            Rights::WRITE,
        ),
    ] {
        if sources[i] != console(i as u32)
            || terminal.classify(caller, reference).map_err(tty_errno)? != role
            || terminal.access(caller, reference).map_err(tty_errno)? != rights
        {
            return Err(-13);
        }
    }
    Ok(())
}
fn console(selector: u32) -> Source {
    Source {
        reference: 0x7a000001 | selector << 16,
        selector,
        rights: if cfg!(any(
            native_tty_byte_probe,
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        )) && selector == 0
        {
            1
        } else {
            2
        },
        bound: 16,
    }
}
fn zero(value: i64) -> Result<(), i64> {
    if value == 0 {
        Ok(())
    } else {
        Err(if value < 0 { value } else { -5 })
    }
}
fn u32_at(frame: &[u8; 32], at: usize) -> u32 {
    u32::from_le_bytes(frame[at..at + 4].try_into().unwrap())
}
#[cfg(native_tty_signal_probe)]
struct SignalBackend<'a, K> {
    kernel: &'a mut K,
    bound: &'a mut Bound,
    target: u64,
    #[cfg(native_zsh_operator)]
    rx_empty: &'a mut bool,
}
#[cfg(native_tty_signal_probe)]
impl<K: AppControl> serial_tty::SignalInput for SignalBackend<'_, K> {
    fn read(&mut self, output: &mut [u8]) -> serial_tty::Completion {
        if self.bound.before(self.kernel).is_err() {
            return serial_tty::Completion {
                count: 0,
                stop: serial_tty::Stop::Unknown,
            };
        }
        let raw = self.kernel.serial(false, output);
        #[cfg(native_zsh_operator)]
        {
            *self.rx_empty = raw == -11;
        }
        completion(raw, output.len())
    }
    #[cfg(native_tty_canonical_probe)]
    fn write(&mut self, _role: serial_tty::Role, input: &[u8]) -> Completion {
        if self.bound.before(self.kernel).is_err() {
            return Completion {
                count: 0,
                stop: Stop::Unknown,
            };
        }
        let mut scratch = [0; 3];
        scratch[..input.len()].copy_from_slice(input);
        completion(
            self.kernel.serial(true, &mut scratch[..input.len()]),
            input.len(),
        )
    }
    fn post_sigint(&mut self) -> Result<u8, TtyError> {
        self.bound
            .before(self.kernel)
            .map_err(|_| TtyError::UnknownCompletion)?;
        match self.kernel.terminal_sigint(self.target, true) {
            result @ 0..=2 => Ok(result as u8),
            _ => Err(TtyError::UnknownCompletion),
        }
    }
}
// Closed selected workload policy, after the wire codec checked canonical slots.
#[cfg(all(
    native_zsh_process,
    not(any(native_zsh_home_write, native_zsh_file_exec))
))]
fn zsh_helper_arguments(raw: &[u8; 272]) -> bool {
    u64::from_le_bytes(raw[..8].try_into().unwrap()) == 2
        && raw[8..16] == [0; 8]
        && raw[16..30] == *b"/inputs/helper"
        && raw[30..48] == [0; 18]
        && raw[48..54] == *b"status"
        && raw[54..] == [0; 218]
}
#[cfg(native_zsh_file_exec)]
fn zsh_helper_arguments(raw: &[u8; 272]) -> bool {
    u64::from_le_bytes(raw[..8].try_into().unwrap()) == 1
        && raw[8..16] == [0; 8]
        && raw[16..27] == *b"/home/probe"
        && raw[27..] == [0; 245]
}
#[cfg(native_zsh_home_write)]
fn zsh_helper_arguments(raw: &[u8; 272]) -> bool {
    u64::from_le_bytes(raw[..8].try_into().unwrap()) == 2
        && raw[8..16] == [0; 8]
        && raw[16..30] == *b"/inputs/helper"
        && raw[30..48] == [0; 18]
        && raw[48..58] == *b"home-write"
        && raw[58..] == [0; 214]
}
#[cfg(native_zsh_process)]
fn zsh_small_header(raw: &[u8; 32], child: bool) -> bool {
    if &raw[..8] == b"AEZFC001" {
        return child;
    }
    let op = u32_at(raw, 0);
    let reference = u32_at(raw, 4);
    let selector = u32_at(raw, 8);
    let count = u32_at(raw, 12);
    match op {
        1..=3 => {
            let tagged = if selector < 3 {
                reference == console(selector).reference
            } else if selector < 7 {
                let generation = (reference >> 8) & 255;
                (1..=9).contains(&generation)
                    && reference
                        == 0x79000000
                            | ((selector - 3) / 2) << 16
                            | generation << 8
                            | ((selector - 3) % 2 + 1)
            } else {
                false
            };
            tagged && count <= 16 && (op != 3 || count == 0)
        }
        82 => !child && reference == 0x76050001 && selector == 1 && count == 0,
        68 => {
            !child
                && (reference == u32::MAX
                    || (10..=108).contains(&reference) && (reference - 10) % 7 == 0)
                && selector & !11 == 0
                && count == 0
        }
        0x10..=0x12 => reference == tty_mode::CONTROL && count == 0,
        _ => false,
    }
}
#[cfg(not(native_zsh_process))]
fn output_header(frame: &[u8; 32]) -> bool {
    (matches!(u32_at(frame, 0), 2 | 3)
        || cfg!(any(
            native_tty_byte_probe,
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        )) && u32_at(frame, 0) == 1)
        && (u32::from(!cfg!(any(
            native_tty_byte_probe,
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        )))..=2)
            .contains(&u32_at(frame, 8))
        && u32_at(frame, 4) == console(u32_at(frame, 8)).reference
        && u32_at(frame, 12) <= 16
        && (u32_at(frame, 0) != 3 || u32_at(frame, 12) == 0)
}
pub fn encode_launch(
    out: &mut [u8; 320],
    engine: u64,
    reader: u64,
    writer: u64,
) -> Result<(), i64> {
    if engine == 0 || reader == 0 || writer == 0 || reader == writer {
        return Err(-22);
    }
    out.fill(0);
    out[..8].copy_from_slice(if cfg!(native_zsh_filesystem) {
        b"AENAP002"
    } else {
        b"AENAP001"
    });
    out[8..16].copy_from_slice(&320u64.to_le_bytes());
    out[16..24].copy_from_slice(
        &(if cfg!(native_zsh_filesystem) {
            4u64
        } else {
            3u64
        })
        .to_le_bytes(),
    );
    out[24..32].copy_from_slice(
        &(if cfg!(native_zsh_filesystem) {
            4u64
        } else {
            1u64
        })
        .to_le_bytes(),
    );
    #[cfg(not(native_zsh_filesystem))]
    for (slot, text) in [
        (0, b"mktemp".as_slice()),
        (1, b"-d".as_slice()),
        (2, TEMPLATE),
        (4, b"LC_ALL=C".as_slice()),
    ] {
        out[32 + slot * 32..][..text.len()].copy_from_slice(text);
    }
    #[cfg(native_zsh_filesystem)]
    for (slot, text) in [
        b"zsh".as_slice(),
        if cfg!(native_zsh_login_startup) {
            b"-d"
        } else {
            b"-f"
        },
        if cfg!(native_zsh_login_startup) {
            b"-il".as_slice()
        } else {
            b"-i".as_slice()
        },
        b"+m",
        b"TERM=vt100",
        b"LC_ALL=C",
        if cfg!(native_zsh_login_startup) {
            b"HOME=/home".as_slice()
        } else {
            b"HOME=/".as_slice()
        },
        b"PWD=/",
    ]
    .iter()
    .enumerate()
    {
        out[32 + slot * 32..][..text.len()].copy_from_slice(text);
    }
    out[288..296].copy_from_slice(&engine.to_le_bytes());
    out[296..304].copy_from_slice(&reader.to_le_bytes());
    out[304..312].copy_from_slice(&writer.to_le_bytes());
    Ok(())
}

// The native console returns a count, including one for a NUL byte. Only -11
// means live-empty; an out-of-range count/errno has unknown effects.
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
fn completion(raw: i64, offered: usize) -> Completion {
    if raw >= 0 && raw as u64 <= offered as u64 {
        Completion {
            count: raw as usize,
            stop: Stop::Complete,
        }
    } else {
        Completion {
            count: 0,
            stop: match raw {
                -11 => Stop::WouldBlock,
                -4 => Stop::Interrupted,
                -4095..=-1 => Stop::Error(raw as i32),
                _ => Stop::Unknown,
            },
        }
    }
}
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
fn tty_errno(error: TtyError) -> i64 {
    match error {
        TtyError::WouldBlock => -11,
        TtyError::Interrupted => -4,
        TtyError::Denied => -13,
        TtyError::Stale => -9,
        TtyError::HungUp => -32,
        TtyError::Backend(value) => i64::from(value),
        _ => -5,
    }
}

#[cfg(native_zsh_filesystem)]
fn fs_errno(error: filesystem_readonly::Error) -> i64 {
    match error {
        filesystem_readonly::Error::Remote(code) | filesystem_readonly::Error::Transport(code) => {
            code
        }
        filesystem_readonly::Error::Invalid => -22,
        filesystem_readonly::Error::Full => -28,
        _ => -5,
    }
}

#[cfg(all(test, native_zsh_filesystem))]
extern crate std;
#[cfg(all(test, native_zsh_filesystem, not(native_zsh_process)))]
#[path = "zsh_owner_tests.rs"]
mod zsh_owner_tests;

#[cfg(all(test, native_zsh_process))]
#[path = "zsh_process_runtime_tests.rs"]
mod zsh_process_runtime_tests;
