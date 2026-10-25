// SPDX-License-Identifier: BSD-2-Clause
//! Shared descriptions over one authenticated client; AF09 requires process writes.
#![no_std]
#[cfg(not(fs_paths))]
use filesystem_client::Kind;
use filesystem_client::{Client, Error, Handle};
use filesystem_service::Channel;
const _: () = assert!(
    !matches!(filesystem_service::MAGIC, b"AFSRPC09") || cfg!(fs_process_writes),
    "home service requires a separately integrated consumer"
);

#[path = "file-descriptions.rs"]
mod descriptions;
use descriptions::Store;
pub use descriptions::{Seek, FIRST_FILE_FD, MAX_FDS, MAX_READ};
/// Compile-time protocol compatibility; never a grant or peer negotiation.
pub const ROOT_PATHS: bool = cfg!(fs_paths);
/// Separate process-directory selection; current public FILE wires must reject it.
pub const CURRENT_DIRECTORIES: bool = cfg!(fs_cwd);
pub const PUBLIC_DIRECTORIES: bool = cfg!(fs_cwd_wire);
#[cfg(all(
    fs_cwd_wire,
    not(all(fs_cwd, fs_directory_contexts, fs_paths, fs_file16, fs_replace))
))]
compile_error!("fs_cwd_wire requires cwd, directory contexts, paths, file16 and replacement");
#[cfg(all(fs_cwd, not(fs_paths)))]
compile_error!("fs_cwd requires fs_paths");
/// Must be matched by the FILE/startup consumer; no runtime negotiation.
pub const FILE_SLOTS_16: bool = cfg!(fs_file16);
#[cfg(all(fs_file16, not(fs_replace)))]
compile_error!("fs_file16 requires fs_replace");
pub type Failure = descriptions::Failure<Error>;
pub type Result<T> = descriptions::Result<T, Error>;
pub type Descriptors<T> = descriptions::Descriptions<Remote<T>>;
#[cfg(all(
    fs_process_writes,
    any(
        not(all(fs_home_wire, fs_process_views, fs_paths, fs_file16, fs_replace)),
        fs_cwd,
        all(fs_in_place, not(fs_home_in_place))
    )
))]
compile_error!(
    "process writes require matched AF09 process/path/file16/replacement without CWD or unselected home in-place"
);
#[cfg(all(
    fs_home_in_place,
    not(all(fs_in_place, fs_process_writes, fs_home_wire))
))]
compile_error!("home in-place broker requires matched in-place AF09 process writes");
#[cfg(fs_process_writes)]
const _: () = assert!(
    matches!(filesystem_service::MAGIC, b"AFSRPC09"),
    "process writes require matched AF09 service"
);
pub struct Remote<T: Channel> {
    client: Client<T>,
}
impl<T: Channel, const VIEWS: usize> descriptions::Descriptions<Remote<T>, VIEWS> {
    /// Trusted caller supplies dedicated authenticated endpoints and a nonreused
    /// epoch matching a service delegated LOOKUP|READ. No preexisting handles.
    pub fn connect(
        channel: T,
        epoch: u64,
    ) -> core::result::Result<Self, filesystem_client::ConnectFailure> {
        let client = Client::connect(channel, epoch, 3)?;
        Ok(Self::from_source(Remote { client }))
    }
    #[cfg(fs_in_place)]
    pub fn connect_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
    ) -> core::result::Result<&mut Self, filesystem_client::ConnectFailure> {
        let client = Self::client_slot(slot);
        Client::connect_in_place(client, channel, epoch, 3)?;
        // SAFETY: prepare initialized every other field; Client success initialized
        // Remote's sole field. Failure returns before this reference is formed.
        Ok(unsafe { slot.assume_init_mut() })
    }
    #[cfg(fs_in_place)]
    fn client_slot(
        slot: &mut core::mem::MaybeUninit<Self>,
    ) -> &mut core::mem::MaybeUninit<Client<T>> {
        let source = Self::prepare_in_place(slot);
        // SAFETY: source is unique uninitialized Remote storage. Its sole field
        // is Client, with identical field alignment; no Remote reference exists.
        unsafe {
            &mut *core::ptr::addr_of_mut!((*source.as_mut_ptr()).client)
                .cast::<core::mem::MaybeUninit<Client<T>>>()
        }
    }
    #[cfg(fs_home_in_place)]
    pub fn connect_home_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
    ) -> core::result::Result<&mut Self, filesystem_client::ConnectFailure> {
        let client = Self::client_slot(slot);
        Client::connect_home_in_place(client, channel, epoch)?;
        // SAFETY: prepare initialized all non-owning fields; the only owning
        // Client field is initialized after both greetings. No borrow escaped.
        Ok(unsafe { slot.assume_init_mut() })
    }
    #[cfg(fs_process_views)]
    pub(crate) fn disconnect_checked(
        &mut self,
        verify: impl FnOnce(&mut T) -> core::result::Result<(), Error>,
    ) -> Result<[i64; 2]> {
        self.disconnect_with(|source| source.client.disconnect_checked(verify))
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.source.client.cleanup()
    }
}
impl<T: Channel> Store for Remote<T> {
    type Handle = Handle;
    type Error = Error;
    type Cleanup = [i64; 2];
    fn open_read(&mut self, name: &[u8]) -> core::result::Result<Handle, Error> {
        #[cfg(fs_paths)]
        {
            self.client.open_root_path(name).map(|entry| entry.handle)
        }
        #[cfg(not(fs_paths))]
        {
            let root = self.client.root()?;
            let entry = self.client.lookup(root, name, 2)?;
            if entry.kind != Kind::File {
                self.client.close(entry.handle)?;
                return Err(Error::Remote(-21));
            }
            Ok(entry.handle)
        }
    }
    fn read(
        &mut self,
        handle: Handle,
        offset: u64,
        length: usize,
        out: &mut [u8; MAX_READ],
    ) -> core::result::Result<usize, Error> {
        self.client.read(handle, offset, length, out)
    }
    fn size(&mut self, handle: Handle) -> core::result::Result<u64, Error> {
        self.client.stat(handle).map(|entry| entry.size)
    }
    fn close(&mut self, handle: Handle) -> core::result::Result<(), Error> {
        self.client.close(handle)
    }
    fn failure_is_fatal(&self, _: Error) -> bool {
        self.client.cleanup().is_some()
    }
    fn retire(&mut self) {
        self.client.abort();
    }
    fn disconnect(&mut self) -> core::result::Result<[i64; 2], Error> {
        self.client.disconnect()
    }
}
#[cfg(test)]
extern crate std;
#[cfg(all(test, not(fs_file16)))]
#[path = "remote-descriptor-tests.rs"]
mod tests;

#[cfg(fs_process_views)]
#[path = "process-descriptors.rs"]
mod processes;
#[cfg(fs_process_views)]
pub use processes::{
    CopyAttempt, CopyInheritanceError, NativeIdentity, Process, ProcessError, ProcessFiles,
};

#[cfg(fs_process_writes)]
pub use processes::{HomeAccess, ProcessWriteFailure};
