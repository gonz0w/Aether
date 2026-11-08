// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Closed readonly real-terminfo view. Names and equality keys confer no authority.
use core::mem::MaybeUninit;
#[cfg(not(native_zsh_cold_reopen))]
use filesystem_client::NamespaceMutation;
use filesystem_client::{Client, Handle, Kind};
pub use filesystem_client::{ConnectFailure, Error};
use filesystem_service::Channel;
// Shared table also contains exec/disconnect constructors unused by this closed view.
#[allow(dead_code)]
#[path = "file-descriptions.rs"]
mod descriptions;
pub use descriptions::{Failure, Seek};
const _: () = assert!(!cfg!(fs_file16) && !cfg!(fs_replace) && !cfg!(fs_process_views));
const _: () = assert!(matches!(filesystem_service::MAGIC, b"AFSRPC09"));
#[cfg(all(native_zsh_home_write, not(native_zsh_process)))]
compile_error!("home write requires the selected Zsh process view");
#[cfg(native_zsh_home_write)]
#[path = "zsh-home-write.rs"]
mod home_write;
#[cfg(all(native_zsh_file_exec, not(native_zsh_process)))]
compile_error!("file exec requires the selected Zsh process view");
#[cfg(all(native_zsh_file_exec, native_zsh_home_write))]
compile_error!("file exec and home write are separate closed profiles");
#[cfg(native_zsh_file_exec)]
#[path = "zsh-file-exec.rs"]
mod file_exec;
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
#[cfg(all(
    native_zsh_home_redirection,
    not(all(
        native_zsh_filesystem,
        native_zsh_process,
        native_zsh_file_exec,
        native_zsh_idle_exit,
        native_zsh_operator
    ))
))]
compile_error!("home redirection requires its complete closed operator profile");
#[cfg(all(native_zsh_home_redirection, native_zsh_home_write))]
compile_error!("home redirection and old home write are separate profiles");
#[cfg(all(
    native_zsh_home_redirection_reader,
    not(all(native_zsh_home_redirection, native_zsh_cold_reopen))
))]
compile_error!("home reader requires redirection and cold reopen");
#[cfg(all(
    native_zsh_home_redirection,
    native_zsh_cold_reopen,
    not(native_zsh_home_redirection_reader)
))]
compile_error!("cold home redirection requires the reader profile");
#[cfg(all(native_zsh_login_startup, not(native_zsh_home_redirection)))]
compile_error!("login startup requires its complete home redirection profile");
#[cfg(all(
    native_zsh_home_cwd,
    not(all(native_zsh_login_startup, native_zsh_home_redirection_reader))
))]
compile_error!("home CWD requires the complete cold login reader profile");
#[cfg(all(native_zsh_operator_login, not(native_zsh_repeat_exec)))]
compile_error!("operator login requires the complete repeat-exec profile");
#[cfg(native_zsh_operator_login)]
#[path = "zsh-operator-login.rs"]
mod operator_login;
#[cfg(all(native_zsh_repeat_exec, not(native_zsh_home_cwd_exec)))]
compile_error!("repeat exec requires the complete cold home CWD exec profile");
#[cfg(all(native_zsh_home_cwd_exec, not(native_zsh_home_cwd)))]
compile_error!("home CWD exec requires the complete cold home CWD profile");
#[cfg(native_zsh_home_redirection)]
#[path = "zsh-home-redirection.rs"]
mod home_redirection;
pub const MAGIC: &[u8; 8] = if cfg!(native_zsh_home_cwd) {
    b"AEFP0007"
} else if cfg!(native_zsh_home_redirection) {
    b"AEFP0006"
} else if cfg!(native_zsh_home_write) {
    b"AEFP0005"
} else {
    b"AEFP0004"
};
pub const DIRECTORY: &[u8] = b"/home/.terminfo";
pub const ENTRY: &[u8] = b"/home/.terminfo/v/vt100";
const ALIAS: &[u8] = b"/home/.terminfo/./v/vt100";
pub const FRAME: usize = 64;
pub const PAYLOAD: usize = 4096;
const VIEWS: usize = if cfg!(native_zsh_process) { 2 } else { 1 };
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Binding {
    pub slot: u8,
    pub epoch: u8,
    pub handle: u64,
    pub generation: u64,
}
impl Binding {
    fn valid(self) -> bool {
        (self.slot == 1 || (cfg!(native_zsh_process) && self.slot == 2))
            && (1..=15).contains(&self.epoch)
            && self.handle == 0xb0000000 | u64::from(self.epoch) << 8 | u64::from(self.slot + 1)
            && self.generation != 0
    }
}
struct Remote<T: Channel> {
    client: Client<T>,
    held: Option<Handle>,
}
impl<T: Channel> descriptions::Store for Remote<T> {
    type Handle = Handle;
    type Error = Error;
    type Cleanup = [i64; 2];
    fn open_read(&mut self, name: &[u8]) -> Result<Handle, Error> {
        if name != ENTRY && name != ALIAS {
            return Err(Error::Remote(-2));
        }
        self.client.open_root_path(ENTRY).map(|entry| entry.handle)
    }
    fn read(
        &mut self,
        handle: Handle,
        offset: u64,
        length: usize,
        out: &mut [u8; PAYLOAD],
    ) -> Result<usize, Error> {
        self.client.read(handle, offset, length, out)
    }
    fn size(&mut self, handle: Handle) -> Result<u64, Error> {
        self.client.stat(handle).map(|entry| entry.size)
    }
    fn close(&mut self, handle: Handle) -> Result<(), Error> {
        self.client.close(handle)
    }
    fn failure_is_fatal(&self, _: Error) -> bool {
        self.client.cleanup().is_some()
    }
    fn retire(&mut self) {
        self.client.abort();
    }
    fn disconnect(&mut self) -> Result<[i64; 2], Error> {
        self.client.disconnect()
    }
}
/// One native-admitted app and one namespace epoch, with the existing sole alias ledger.
/// Runtime must authenticate the actual endpoint before passing its binding here.
#[must_use]
pub struct Files<T: Channel> {
    descriptions: descriptions::Descriptions<Remote<T>, VIEWS>,
    binding: Binding,
    #[cfg(native_zsh_process)]
    child: Option<Binding>,
    #[cfg(native_zsh_process)]
    child_next: u64,
    #[cfg(native_zsh_process)]
    child_pending: bool,
    #[cfg(native_zsh_process)]
    child_epoch: u8,
    #[cfg(native_zsh_home_redirection)]
    note: home_redirection::Note,
    namespace_epoch: u64,
    next: u64,
    pending: bool,
    retired: bool,
    mutation_failure: Option<filesystem_client::MutationFailure>,
    #[cfg(native_zsh_home_write)]
    home_write: home_write::HomeWrite,
    #[cfg(native_zsh_file_exec)]
    file_exec: file_exec::FileExec,
}
impl<T: Channel> Files<T> {
    /// Initialize the Client in final storage; failure consumes both close obligations.
    /// No Files reference is published before both greetings have validated.
    pub fn connect_in_place(
        slot: &mut MaybeUninit<Self>,
        channel: T,
        epoch: u64,
        binding: Binding,
    ) -> Result<&mut Self, ConnectFailure> {
        let pointer = slot.as_mut_ptr();
        if !binding.valid() || binding.slot != 1 || epoch == 0 {
            let mut channel = channel;
            return Err(ConnectFailure {
                error: Error::Invalid,
                cleanup: channel.close(),
            });
        }
        // SAFETY: exclusive MaybeUninit storage, raw disjoint projections only;
        // all non-Client fields are initialized before any Self reference exists.
        let client_slot = unsafe {
            core::ptr::addr_of_mut!((*pointer).binding).write(binding);
            #[cfg(native_zsh_process)]
            {
                core::ptr::addr_of_mut!((*pointer).child).write(None);
                core::ptr::addr_of_mut!((*pointer).child_next).write(0);
                core::ptr::addr_of_mut!((*pointer).child_pending).write(false);
                core::ptr::addr_of_mut!((*pointer).child_epoch).write(0);
            }
            #[cfg(native_zsh_home_redirection)]
            core::ptr::addr_of_mut!((*pointer).note).write(home_redirection::Note::new());
            core::ptr::addr_of_mut!((*pointer).namespace_epoch).write(epoch);
            core::ptr::addr_of_mut!((*pointer).next).write(1);
            core::ptr::addr_of_mut!((*pointer).pending).write(false);
            core::ptr::addr_of_mut!((*pointer).retired).write(false);
            core::ptr::addr_of_mut!((*pointer).mutation_failure).write(None);
            #[cfg(native_zsh_home_write)]
            core::ptr::addr_of_mut!((*pointer).home_write).write(home_write::HomeWrite::new());
            #[cfg(native_zsh_file_exec)]
            core::ptr::addr_of_mut!((*pointer).file_exec).write(file_exec::FileExec::new());
            let desc = &mut *core::ptr::addr_of_mut!((*pointer).descriptions)
                .cast::<MaybeUninit<descriptions::Descriptions<Remote<T>, VIEWS>>>();
            let source = descriptions::Descriptions::prepare_in_place(desc).as_mut_ptr();
            core::ptr::addr_of_mut!((*source).held).write(None);
            &mut *core::ptr::addr_of_mut!((*source).client).cast::<MaybeUninit<Client<T>>>()
        };
        Client::connect_home_in_place(client_slot, channel, epoch)?;
        // SAFETY: every field, including the sole Client, is now valid.
        Ok(unsafe { slot.assume_init_mut() })
    }
    /// Scoped transport configuration only; never reconnects or changes admission.
    pub fn configure(
        &mut self,
        configure: impl FnOnce(&mut T) -> Result<(), Error>,
    ) -> Result<(), Error> {
        self.descriptions.source.client.configure_channel(configure)
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.descriptions.source.client.cleanup()
    }
    pub fn abort(&mut self) -> [i64; 2] {
        #[cfg(native_zsh_home_cwd)]
        {
            // An unconfirmed state-changing reply cannot reuse a past read's
            // completion, even when namespace close itself is known clean.
            self.note.phase = 1;
        }
        #[cfg(native_zsh_file_exec)]
        self.file_exec.poison();
        #[cfg(native_zsh_home_write)]
        {
            self.home_write.poisoned = true;
        }
        self.retired = true;
        self.pending = false;
        #[cfg(native_zsh_process)]
        {
            self.child_pending = false;
        }
        self.descriptions.retire();
        self.cleanup().unwrap_or([-5; 2])
    }
    pub fn mutation_failure(&self) -> Option<filesystem_client::MutationFailure> {
        self.mutation_failure
    }
    /// Fixed pre-startup materialization: 12 real requests, four mutations.
    /// Keep .terminfo's actual reference until healthy teardown.
    #[cfg(not(native_zsh_cold_reopen))]
    pub fn provision(&mut self, asset: &[u8], workspace: &mut [u8; PAYLOAD]) -> Result<(), Error> {
        if self.retired
            || self.pending
            || self.descriptions.source.held.is_some()
            || asset.is_empty()
            || asset.len() > PAYLOAD
        {
            return Err(Error::Invalid);
        }
        let mut mutation_failure = None;
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let home = client.home()?;
            client
                .namespace(home, NamespaceMutation::MakeDirectory(b".terminfo"))
                .map_err(|e| {
                    mutation_failure = Some(e);
                    e.error
                })?;
            let directory = client.lookup(home, b".terminfo", 15)?;
            if directory.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            self.descriptions.source.held = Some(directory.handle);
            client
                .namespace(directory.handle, NamespaceMutation::MakeDirectory(b"v"))
                .map_err(|e| {
                    mutation_failure = Some(e);
                    e.error
                })?;
            let v = client.lookup(directory.handle, b"v", 15)?;
            if v.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            client
                .namespace(v.handle, NamespaceMutation::Create(b"vt100"))
                .map_err(|e| {
                    mutation_failure = Some(e);
                    e.error
                })?;
            let file = client.lookup(v.handle, b"vt100", 6)?;
            if file.kind != Kind::File {
                return Err(Error::Protocol);
            }
            client.write(file.handle, 0, asset).map_err(|e| {
                mutation_failure = Some(e);
                e.error
            })?;
            let stat = client.stat(file.handle)?;
            if stat.kind != Kind::File || stat.size != asset.len() as u64 {
                return Err(Error::Protocol);
            }
            if client.read(file.handle, 0, asset.len(), workspace)? != asset.len()
                || workspace[..asset.len()] != *asset
            {
                return Err(Error::Protocol);
            }
            if client.read(file.handle, asset.len() as u64, 1, workspace)? != 0 {
                return Err(Error::Protocol);
            }
            client.close(file.handle)?;
            client.close(v.handle)?;
            Ok(())
        })();
        self.mutation_failure = mutation_failure;
        workspace.fill(0);
        if result.is_err() {
            self.abort();
        }
        result
    }
    /// Trusted cold startup only: reopen the existing retained directory view.
    /// Every acquisition stays in the sole Client ledger; failed validation or
    /// close retires that channel and never repairs or replays a mutation.
    #[cfg(native_zsh_cold_reopen)]
    pub fn reopen(&mut self, asset: &[u8], workspace: &mut [u8; PAYLOAD]) -> Result<(), Error> {
        if self.retired
            || self.pending
            || self.descriptions.source.held.is_some()
            || asset.is_empty()
            || asset.len() > PAYLOAD
        {
            return Err(Error::Invalid);
        }
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let home = client.home()?;
            let directory = client.lookup(home, b".terminfo", 3)?;
            if directory.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            self.descriptions.source.held = Some(directory.handle);
            let v = client.lookup(directory.handle, b"v", 3)?;
            if v.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            let file = client.lookup(v.handle, b"vt100", 2)?;
            if file.kind != Kind::File || file.size != asset.len() as u64 {
                return Err(Error::Protocol);
            }
            if client.read(file.handle, asset.len() as u64, 1, workspace)? != 0
                || client.read(file.handle, 0, asset.len(), workspace)? != asset.len()
                || workspace[..asset.len()] != *asset
            {
                return Err(Error::Protocol);
            }
            let stat = client.stat(file.handle)?;
            if stat.kind != Kind::File || stat.size != asset.len() as u64 {
                return Err(Error::Protocol);
            }
            client.close(file.handle)?;
            client.close(v.handle)?;
            Ok(())
        })();
        workspace.fill(0);
        if result.is_err() {
            self.abort();
        }
        result
    }
    fn view(&self, binding: Binding) -> Option<usize> {
        if self.binding == binding {
            return Some(0);
        }
        #[cfg(native_zsh_process)]
        if self.child == Some(binding) {
            return Some(1);
        }
        None
    }
    fn sequence(&self, view: usize) -> u64 {
        #[cfg(native_zsh_process)]
        if view == 1 {
            return self.child_next;
        }
        let _ = view;
        self.next
    }
    fn pending_in(&self, view: usize) -> bool {
        #[cfg(native_zsh_process)]
        if view == 1 {
            return self.child_pending;
        }
        let _ = view;
        self.pending
    }
    fn live(&self, binding: Binding) -> bool {
        !self.retired
            && self
                .view(binding)
                .is_some_and(|view| !self.pending_in(view))
            && self.cleanup().is_none()
            && self.descriptions.source.held.is_some()
    }
    /// Owner-authenticated snapshot check; no namespace operation or new handle.
    #[cfg(native_zsh_process)]
    pub fn file_view(&self, binding: Binding) -> Result<(u16, u16), Error> {
        if !self.live(binding) {
            return Err(Error::Protocol);
        }
        self.descriptions
            .file_view_in(self.view(binding).unwrap())
            .map_err(|_| Error::Protocol)
    }
    /// Only after exact native copy admission. Parent remains frozen/awaiting
    /// its correlated reply; real descriptions/positions, not handles, are shared.
    #[cfg(native_zsh_process)]
    pub fn inherit_child(&mut self, parent: Binding, child: Binding) -> Result<(), Error> {
        if !self.live(parent)
            || parent != self.binding
            || self.child.is_some()
            || !child.valid()
            || child.slot != 2
            || child.epoch != self.child_epoch + 1
            || child.generation == parent.generation
        {
            return Err(Error::Protocol);
        }
        #[cfg(all(native_zsh_home_redirection, not(native_zsh_home_cwd_exec)))]
        if cfg!(native_zsh_home_cwd) || self.note_io_active() {
            return Err(Error::Invalid);
        }
        #[cfg(native_zsh_home_cwd_exec)]
        if !self.note_fork_ready() {
            return Err(Error::Invalid);
        }
        self.descriptions
            .inherit_view(0, 1)
            .map_err(|_| Error::Protocol)?;
        #[cfg(native_zsh_home_cwd_exec)]
        {
            // Native copy is known admitted; only the exact published binding
            // below authenticates this snapshot. Parent selectors remain local.
            self.note.child_cwd_home = self.note.cwd_home;
        }
        self.child = Some(child);
        self.child_epoch = child.epoch;
        self.child_next = 1;
        self.child_pending = false;
        Ok(())
    }
    /// Native selected-image receipt must already prove commit. Refusals never call this.
    #[cfg(native_zsh_process)]
    pub fn exec_child(&mut self, child: Binding, generation: u64) -> Result<Binding, Error> {
        if self.child != Some(child)
            || !self.live(child)
            || child.generation.checked_add(1) != Some(generation)
            || generation == u64::MAX
        {
            return Err(Error::Protocol);
        }
        #[cfg(native_zsh_home_write)]
        if self.home_write.phase != 0 || self.home_write.poisoned {
            return Err(Error::Protocol);
        }
        self.descriptions
            .commit_exec_close_in(1)
            .map_err(|_| Error::Closed)?;
        let next = Binding {
            generation,
            ..child
        };
        self.child = Some(next);
        self.child_next = 1;
        #[cfg(native_zsh_home_write)]
        {
            self.home_write.binding = next;
        }
        Ok(next)
    }
    /// Caller proved native terminal and known wait delivery before settlement.
    #[cfg(native_zsh_process)]
    pub fn settle_child(&mut self, child: Binding) -> Result<(), Error> {
        if self.child != Some(child) || !self.live(child) {
            return Err(Error::Protocol);
        }
        self.descriptions
            .settle_view(1)
            .map_err(|_| Error::Closed)?;
        self.child = None;
        self.child_next = 0;
        #[cfg(native_zsh_home_cwd_exec)]
        {
            self.note.child_cwd_home = false;
        }
        Ok(())
    }
    /// Validate complete fixed header before body assembly or source effects.
    pub fn body_length(&mut self, binding: Binding, raw: &[u8; FRAME]) -> Result<usize, Error> {
        let a = word(raw, 4);
        let b = word(raw, 5);
        let c = word(raw, 6);
        let d = word(raw, 7);
        let valid = self.live(binding)
            && raw[..8] == MAGIC[..]
            && word(raw, 2) == binding.generation
            && word(raw, 3) == self.sequence(self.view(binding).unwrap())
            && self.sequence(self.view(binding).unwrap()) != u64::MAX
            && match word(raw, 1) {
                1 => a <= 1 && (1..=255).contains(&b) && c == 0 && d == 0,
                2 => fd(a) && b <= PAYLOAD as u64 && c == 0 && d == 0,
                3 => fd(a) && c <= 2 && d == 0,
                4 => fd(a) && b < 16 && c <= 1 && d == 0,
                5 => fd(a) && b == 0 && c == 0 && d == 0,
                6 => fd(a) && b <= 1 && c == 0 && d == 0,
                8 => matches!(a, 0 | 4) && (1..=255).contains(&b) && c == 0 && d == 0,
                9 => a == 0 && b == 0 && c == 0 && d == 0,
                10 => a == 0 && (1..=255).contains(&b) && c == 0 && d == 0,
                #[cfg(native_zsh_home_cwd)]
                13 => a == 0 && matches!(b, 1 | 5) && c == 0 && d == 0,
                #[cfg(native_zsh_home_redirection)]
                11 => fd(a) && (1..=16).contains(&b) && c == 0 && d == 0,
                #[cfg(native_zsh_home_redirection)]
                12 => a <= 1 && b == home_redirection::ENTRY.len() as u64 && c == 0o600 && d == 0,
                #[cfg(native_zsh_home_write)]
                11 => fd(a) && (1..=PAYLOAD as u64).contains(&b) && c == 0 && d == 0,
                #[cfg(native_zsh_home_write)]
                12 => a <= 1 && (1..=255).contains(&b) && c == 0 && d == 0,
                _ => false,
            };
        if !valid {
            self.abort();
            return Err(Error::Protocol);
        }
        Ok(
            if matches!(word(raw, 1), 1 | 8 | 10)
                || (cfg!(native_zsh_home_cwd) && word(raw, 1) == 13)
                || ((cfg!(native_zsh_home_write) || cfg!(native_zsh_home_redirection))
                    && matches!(word(raw, 1), 11 | 12))
            {
                (b as usize).div_ceil(FRAME) * FRAME
            } else {
                0
            },
        )
    }
    /// Own the effect until the complete reply/header/body has been delivered.
    #[cfg(any(not(native_zsh_operator_login), test))]
    pub fn prepare<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        received: usize,
        workspace: &'a mut [u8; PAYLOAD],
    ) -> Result<Reply<'a, T>, Error> {
        self.prepare_inner(binding, raw, received, workspace, u32::MAX)
    }
    #[cfg(native_zsh_operator_login)]
    pub fn prepare_bounded<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        received: usize,
        workspace: &'a mut [u8; PAYLOAD],
        remaining: u32,
    ) -> Result<Reply<'a, T>, Error> {
        self.prepare_inner(binding, raw, received, workspace, remaining)
    }
    fn prepare_inner<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        received: usize,
        workspace: &'a mut [u8; PAYLOAD],
        _remaining: u32,
    ) -> Result<Reply<'a, T>, Error> {
        let needed = self.body_length(binding, raw)?;
        let b = word(raw, 5) as usize;
        if received != needed || (needed != 0 && workspace[b..needed].iter().any(|v| *v != 0)) {
            workspace.fill(0);
            self.abort();
            return Err(Error::Protocol);
        }
        let view = self.view(binding).ok_or(Error::Protocol)?;
        #[cfg(native_zsh_home_write)]
        if word(raw, 1) == 11 {
            return self.prepare_home_write(binding, raw, workspace);
        }
        #[cfg(native_zsh_home_redirection)]
        if matches!(word(raw, 1), 11 | 12) {
            return self.prepare_note(binding, raw, workspace);
        }
        #[cfg(native_zsh_operator_login)]
        let denied = self.operation_budget(view, raw, workspace) > _remaining;
        #[cfg(not(native_zsh_operator_login))]
        let denied = false;
        let (result, body) = if denied {
            (Err(Failure::Source(Error::Remote(-28))), 0)
        } else {
            self.execute(view, raw, workspace)
        };
        if self.cleanup().is_some() {
            workspace.fill(0);
            self.abort();
            return Err(Error::Closed);
        }
        let mut reply = [0; FRAME];
        reply[..8].copy_from_slice(MAGIC);
        put(&mut reply, 2, binding.generation);
        put(&mut reply, 3, self.sequence(view));
        let body = match result {
            Ok(value) => {
                put(&mut reply, 4, value);
                put(&mut reply, 5, body as u64);
                body
            }
            Err(error) => {
                workspace.fill(0);
                put(&mut reply, 1, errno(error) as u64);
                0
            }
        };
        #[cfg(native_zsh_process)]
        if view == 1 {
            self.child_pending = true;
        } else {
            self.pending = true;
        }
        #[cfg(not(native_zsh_process))]
        {
            self.pending = true;
        }
        Ok(Reply {
            #[cfg(native_zsh_process)]
            view,
            files: self,
            workspace,
            header: reply,
            body,
            delivered: false,
        })
    }
    fn execute(
        &mut self,
        view: usize,
        raw: &[u8; FRAME],
        workspace: &mut [u8; PAYLOAD],
    ) -> (Result<u64, Failure<Error>>, usize) {
        let a = word(raw, 4);
        let b = word(raw, 5);
        let c = word(raw, 6);
        let mut body = 0;
        let result = match word(raw, 1) {
            #[cfg(native_zsh_home_write)]
            12 => {
                let result = self.open_home_write(view, &workspace[..b as usize], a != 0);
                workspace.fill(0);
                result.map(|fd| fd as u64)
            }
            #[cfg(native_zsh_home_cwd)]
            1 if workspace[..b as usize] == *b".zprofile" => {
                let value = if view == 0 && self.note.cwd_home {
                    self.open_note_read(view, a != 0).map(|fd| fd as u64)
                } else {
                    Err(Failure::Source(Error::Remote(-13)))
                };
                workspace.fill(0);
                value
            }
            #[cfg(native_zsh_home_redirection)]
            1 if workspace[..b as usize] == *home_redirection::ENTRY => {
                let value = self.open_note_read(view, a != 0).map(|fd| fd as u64);
                workspace.fill(0);
                value
            }
            1 => {
                #[cfg(native_zsh_home_cwd)]
                if workspace[0] != b'/' {
                    workspace.fill(0);
                    return (Err(Failure::Source(Error::Remote(-13))), 0);
                }
                let value = self
                    .descriptions
                    .open_read_in(view, &workspace[..b as usize], a != 0)
                    .map(|fd| fd as u64);
                workspace.fill(0);
                value
            }
            2 => {
                #[cfg(native_zsh_home_redirection)]
                if self.note_write_fd(view, a as i32) {
                    workspace.fill(0);
                    return (Err(Failure::BadFd), 0);
                }
                #[cfg(native_zsh_home_write)]
                if self.is_home_file(view, a as i32) {
                    workspace.fill(0);
                    return (Err(Failure::BadFd), 0);
                }
                #[cfg(native_zsh_home_redirection)]
                let before = self.note_position(view, a as i32);
                #[cfg(native_zsh_operator_login)]
                if b == 0 {
                    workspace.fill(0);
                    return (self.descriptions.position_in(view, a as i32).map(|_| 0), 0);
                }
                let result = self
                    .descriptions
                    .read_in(view, a as i32, b as usize, workspace);
                #[cfg(native_zsh_operator_login)]
                if before.is_some() && result.is_err() {
                    // An attempted source failure cannot leave a supposedly
                    // funded immutable-profile completion available for retry.
                    self.abort();
                }
                #[cfg(native_zsh_home_redirection)]
                if let Ok(count) = result {
                    self.note_read(view, a as i32, before, count, workspace);
                }
                result
            }
            .map(|count| {
                body = count;
                count as u64
            }),
            8 => {
                let source = &mut self.descriptions.source;
                let result = descriptions::Store::open_read(source, &workspace[..b as usize])
                    .and_then(|handle| source.client.close(handle));
                workspace.fill(0);
                result.map(|()| 0).map_err(Failure::Source)
            }
            #[cfg(native_zsh_home_cwd)]
            13 => self
                .change_home_cwd(view, b as usize, workspace)
                .map(|()| 0),
            #[cfg(native_zsh_home_cwd)]
            9 => {
                let home = self.note.cwd_home;
                #[cfg(native_zsh_home_cwd_exec)]
                let home = if view == 1 {
                    self.note.child_cwd_home
                } else {
                    home
                };
                self.observe_home_cwd(view, home, workspace).map(|length| {
                    body = length;
                    0
                })
            }
            #[cfg(not(native_zsh_home_cwd))]
            9 => {
                workspace.fill(0);
                self.descriptions
                    .source
                    .client
                    .root()
                    .map(|_| {
                        workspace[..2].copy_from_slice(b"/\0");
                        body = 2;
                        0
                    })
                    .map_err(Failure::Source)
            }
            10 => {
                let allowed = workspace[..b as usize] == *DIRECTORY;
                workspace.fill(0);
                if !allowed {
                    Err(Failure::Source(Error::Remote(-2)))
                } else {
                    let source = &mut self.descriptions.source;
                    source
                        .held
                        .ok_or(Failure::Retired)
                        .and_then(|handle| source.client.stat(handle).map_err(Failure::Source))
                        .and_then(|entry| {
                            if entry.kind != Kind::Directory {
                                return Err(Failure::InvalidCompletion);
                            }
                            workspace[..8].copy_from_slice(&2u64.to_le_bytes());
                            workspace[8..16].copy_from_slice(&entry.size.to_le_bytes());
                            workspace[16..24].copy_from_slice(&1u64.to_le_bytes());
                            workspace[24..32].copy_from_slice(&self.namespace_epoch.to_le_bytes());
                            body = 32;
                            Ok(0)
                        })
                }
            }
            opcode => {
                workspace.fill(0);
                #[cfg(native_zsh_home_write)]
                if self.is_home_file(view, a as i32) && opcode != 5 {
                    return (Err(Failure::Invalid), 0);
                }
                #[cfg(native_zsh_home_redirection)]
                if opcode == 3 && self.note_write_fd(view, a as i32) {
                    return (Err(Failure::Invalid), 0);
                }
                match opcode {
                    3 => self.descriptions.seek_in(
                        view,
                        a as i32,
                        match c {
                            0 => Seek::Set(b as i64),
                            1 => Seek::Current(b as i64),
                            _ => Seek::End(b as i64),
                        },
                    ),
                    4 => self
                        .descriptions
                        .duplicate_in(view, a as i32, b as i32, c != 0)
                        .map(|fd| fd as u64),
                    5 => {
                        #[cfg(native_zsh_home_write)]
                        let closing_home = self.is_home_file(view, a as i32);
                        #[cfg(native_zsh_home_redirection)]
                        let note_position = self.note_position(view, a as i32);
                        let result = self.descriptions.close_in(view, a as i32).map(|()| 0);
                        #[cfg(native_zsh_home_redirection)]
                        self.note_closed(note_position, result.is_ok());
                        #[cfg(native_zsh_home_write)]
                        if closing_home {
                            self.home_write.close_sequence = word(raw, 3);
                            if result.is_ok() && self.home_write.phase == 3 {
                                self.home_write.phase = 4;
                            } else {
                                self.home_write.poisoned = true;
                            }
                        }
                        result
                    }
                    6 => self
                        .descriptions
                        .set_close_on_exec_in(view, a as i32, b != 0)
                        .map(|()| 0),
                    _ => Err(Failure::Invalid),
                }
            }
        };
        (result, body)
    }
    /// Called only after app access is retired by its confirmed terminal state.
    pub fn disconnect_checked(
        &mut self,
        verify: impl FnOnce(&mut T) -> Result<(), Error>,
    ) -> Result<[i64; 2], Error> {
        #[cfg(native_zsh_process)]
        if self.child.is_some() || self.child_pending {
            return Err(Error::Closed);
        }
        if self.retired || self.pending || self.cleanup().is_some() {
            return Err(Error::Closed);
        }
        self.retired = true;
        for fd in 3..16 {
            if self.descriptions.position(fd).is_ok() {
                self.descriptions.close(fd).map_err(|_| Error::Closed)?;
            }
        }
        #[cfg(native_zsh_file_exec)]
        self.release_file_exec()?;
        let held = self.descriptions.source.held.take().ok_or(Error::Closed)?;
        self.descriptions.source.client.close(held)?;
        let result = self.descriptions.source.client.disconnect_checked(verify)?;
        if result != [0; 2] {
            return Err(Error::Closed);
        }
        Ok(result)
    }
}
pub struct Reply<'a, T: Channel> {
    #[cfg(native_zsh_process)]
    view: usize,
    files: &'a mut Files<T>,
    workspace: &'a mut [u8; PAYLOAD],
    header: [u8; FRAME],
    body: usize,
    delivered: bool,
}
impl<T: Channel> Reply<'_, T> {
    /// Trusted transport-only scope control; never changes Client authority.
    pub fn configure(
        &mut self,
        configure: impl FnOnce(&mut T) -> Result<(), Error>,
    ) -> Result<(), Error> {
        self.files.configure(configure)
    }
    /// Real namespace close receipt; process reply delivery may still finish once.
    #[cfg(any(native_zsh_home_write, native_zsh_home_redirection))]
    pub fn source_closed(&self) -> bool {
        self.files.cleanup().is_some()
    }
    pub fn header(&self) -> &[u8; FRAME] {
        &self.header
    }
    pub fn body_mut(&mut self) -> &mut [u8] {
        &mut self.workspace[..self.body.div_ceil(FRAME) * FRAME]
    }
    pub fn delivered(mut self) {
        #[cfg(native_zsh_home_redirection)]
        if self.view == 0 && self.files.note.phase == 8 {
            self.files.note.phase = 7;
        }
        #[cfg(native_zsh_home_write)]
        if self.view == 1
            && self.files.home_write.phase == 4
            && self.files.home_write.close_sequence == word(&self.header, 3)
        {
            self.files.home_write.phase = 5;
        }
        #[cfg(native_zsh_process)]
        if self.view == 1 {
            self.files.child_next += 1;
            self.files.child_pending = false;
        } else {
            self.files.next += 1;
            self.files.pending = false;
        }
        #[cfg(not(native_zsh_process))]
        {
            self.files.next += 1;
            self.files.pending = false;
        }
        self.workspace.fill(0);
        self.delivered = true;
    }
}
impl<T: Channel> Drop for Reply<'_, T> {
    fn drop(&mut self) {
        if !self.delivered {
            self.workspace.fill(0);
            self.files.abort();
        }
    }
}
fn fd(value: u64) -> bool {
    (3..16).contains(&value)
}
fn word(raw: &[u8; FRAME], index: usize) -> u64 {
    u64::from_le_bytes(raw[index * 8..index * 8 + 8].try_into().unwrap())
}
fn put(raw: &mut [u8; FRAME], index: usize, value: u64) {
    raw[index * 8..index * 8 + 8].copy_from_slice(&value.to_le_bytes());
}
fn errno(error: Failure<Error>) -> i64 {
    match error {
        Failure::BadFd => -9,
        Failure::Full => -24,
        Failure::Invalid => -22,
        Failure::Overflow => -75,
        Failure::Source(Error::Invalid) => -22,
        Failure::Source(Error::Full) => -28,
        Failure::Source(Error::Remote(code)) => code,
        _ => -5,
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "readonly-files-tests.rs"]
mod tests;
