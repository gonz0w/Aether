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
    fn reserve(&mut self) -> Result<(), i64> {
        if self.reserved == 0 {
            self.failed = -5;
            return Err(-5);
        }
        self.reserved -= 1;
        Ok(())
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
            self.with_files(|files| files.provision(TERMINFO, workspace))?;
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
    fn file_request(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        let binding = self.file_binding.ok_or(-9)?;
        if self
            .identity
            .map(|id| (id.slot as u8, id.epoch as u8, id.handle))
            != Some((binding.slot, binding.epoch, binding.handle))
        {
            return Err(-9);
        }
        self.mode_peer_live()?;
        let header = self.file_header;
        let length = self.with_files(|files| files.body_length(binding, &header))?;
        workspace.fill(0);
        stream_transport::transfer(
            &mut OwnerSteps {
                kernel: &mut self.kernel,
                bound: &mut self.bound,
                endpoints: self.endpoints.as_mut().ok_or(-9)?,
                progress: &mut self.request_at,
            },
            &mut workspace[..length],
            false,
        )?;
        // Authenticate the exact admitted generation again after body assembly.
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
            // End the namespace loan before process I/O reborrows Bound. A lost
            // reply rearms only the close journal before Reply's abort/drop.
            reply
                .configure(|io| {
                    io.disarm();
                    Ok(())
                })
                .map_err(fs_errno)?;
            let delivery = if let Some(endpoints) = self.endpoints.as_mut() {
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
            delivery?;
            reply.delivered();
            Ok(())
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
        if let Err(error) = result
            && self.bound.failed == 0
        {
            self.bound.failed = error;
        }
        result
    }
    fn run_inner(&mut self, workspace: &mut [u8; 4096]) -> Result<(), i64> {
        self.provision(workspace)?;
        while self.request(workspace)? {}
        self.terminal_zero(self.app)?;
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
        self.close_console()?;
        self.bound.reserve()?;
        self.terminal_attempted = true;
        let _ = self.kernel.ctl(0x2a002, 0xf002, 0);
        Err(-5) // A returning successful halt is a defect, never another attempt.
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
        completion(self.kernel.serial(false, output), output.len())
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
        b"-f",
        b"-i",
        b"+m",
        b"TERM=vt100",
        b"LC_ALL=C",
        b"HOME=/",
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
#[cfg(all(test, native_zsh_filesystem))]
#[path = "zsh_owner_tests.rs"]
mod zsh_owner_tests;
