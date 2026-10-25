// SPDX-License-Identifier: BSD-2-Clause
//! Trusted broker process views, not a native admission/authentication mechanism.
use super::{descriptions, Channel, Failure, Remote, Seek, MAX_READ};
#[path = "vendor/abi29-startup.rs"]
mod startup;
pub use startup::Identity as NativeIdentity;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Process {
    service_epoch: u64,
    identity: NativeIdentity,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ProcessError {
    Identity(i32),
    Stale,
    Busy,
    Generation,
    Files(Failure),
}
/// Trusted native-copy observation. Labels never authorize native operations.
#[derive(Debug, PartialEq, Eq)]
pub enum CopyAttempt<E> {
    Copied {
        identity: NativeIdentity,
        parent_pid: u32,
    },
    /// Confirmed no child, with native reservations/parent thaw caller-owned.
    Refused(E),
    /// Neither retry nor rollback is justified by this observation.
    Unknown(E),
}
#[derive(Debug, PartialEq, Eq)]
pub enum CopyInheritanceError<E> {
    BeforeCopy(ProcessError),
    Refused(E),
    Unknown(E),
    /// A native child exists but was not bound. Caller retains settlement duty.
    Unbound {
        identity: NativeIdentity,
        parent_pid: u32,
        error: ProcessError,
    },
}
type Result<T> = core::result::Result<T, ProcessError>;
#[derive(Clone, Copy)]
struct Record {
    process: Option<Process>,
    last_generation: u32,
    #[cfg(fs_cwd)]
    cwd: Option<filesystem_client::Handle>,
}

/// One bounded broker, four views and thirteen shared descriptions.
/// The dispatcher MUST authenticate channels/native observations externally.
/// Keys/identity labels are selectors within that trusted binding, never grants.
pub struct ProcessFiles<T: Channel> {
    files: descriptions::Descriptions<Remote<T>, 4>,
    epoch: u64,
    records: [Record; 4],
}
// Keep admission closed if the native outcome is unknown, including unwind.
// No native termination, thaw, holder rollback or reclaim is implied by abort.
struct CopyGuard<'a, T: Channel> {
    files: &'a mut ProcessFiles<T>,
    complete: bool,
}
impl<T: Channel> Drop for CopyGuard<'_, T> {
    fn drop(&mut self) {
        if !self.complete {
            self.files.abort();
        }
    }
}
impl<T: Channel> ProcessFiles<T> {
    pub fn connect(
        channel: T,
        epoch: u64,
    ) -> core::result::Result<Self, filesystem_client::ConnectFailure> {
        Ok(Self {
            files: descriptions::Descriptions::connect(channel, epoch)?,
            epoch,
            records: [Record {
                process: None,
                last_generation: 0,
                #[cfg(fs_cwd)]
                cwd: None,
            }; 4],
        })
    }
    /// See FS-BROKER-INIT: only success initializes slot; no second greeting.
    #[cfg(fs_in_place)]
    pub fn connect_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
    ) -> core::result::Result<&mut Self, filesystem_client::ConnectFailure> {
        let files = Self::prepare_in_place(slot, epoch);
        descriptions::Descriptions::connect_in_place(files, channel, epoch)?;
        // SAFETY: the sole owning field is valid after nested success; all other
        // fields are initialized above. No aliases to fields escape initialization.
        Ok(unsafe { slot.assume_init_mut() })
    }
    #[cfg(fs_in_place)]
    fn prepare_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        epoch: u64,
    ) -> &mut core::mem::MaybeUninit<descriptions::Descriptions<Remote<T>, 4>> {
        let pointer = slot.as_mut_ptr();
        // SAFETY: exclusive aligned storage; only non-owning valid values are
        // written before the fallible nested constructor. No Self reference or
        // assumption that zero represents an Option is used.
        unsafe {
            core::ptr::addr_of_mut!((*pointer).epoch).write(epoch);
            for index in 0..4 {
                core::ptr::addr_of_mut!((*pointer).records)
                    .cast::<Record>()
                    .add(index)
                    .write(Record {
                        process: None,
                        last_generation: 0,
                        #[cfg(fs_cwd)]
                        cwd: None,
                    });
            }
            &mut *core::ptr::addr_of_mut!((*pointer).files)
                .cast::<core::mem::MaybeUninit<descriptions::Descriptions<Remote<T>, 4>>>()
        }
    }
    fn active(&self) -> Result<()> {
        self.files.active().map_err(ProcessError::Files)
    }
    fn exact(&self, process: Process) -> Result<usize> {
        self.active()?;
        let slot = process.identity.slot;
        if !(1..=4).contains(&slot) || self.records[slot as usize - 1].process != Some(process) {
            return Err(ProcessError::Stale);
        }
        Ok(slot as usize - 1)
    }
    /// Check a trusted opaque key without selecting an FD or source operation.
    pub fn validate_binding(&self, process: Process) -> Result<()> {
        self.exact(process).map(|_| ())
    }
    /// Version 1 read-only authoritative FILE metadata: (presence, cloexec).
    /// Bit n denotes remote FD n; the default profile admits3–15, fs_file16
    /// admits0–15. Cloexec is a subset of presence. No source/native callbacks or mutation.
    /// The owner must compare BOTH complete masks against the claimed remote
    /// FILE map while holding exclusive admission through copy/publication.
    /// These inert labels do not authenticate a request or validate streams,
    /// source history, native grants or freshness after subsequent mutation.
    pub fn file_view_v1(&self, process: Process) -> Result<(u16, u16)> {
        let view = self.exact(process)?;
        self.files.file_view_in(view).map_err(ProcessError::Files)
    }
    /// For an authenticated currently admitted endpoint observation only.
    /// Does not authenticate a caller-supplied identity request.
    pub fn current(&self, observed: NativeIdentity) -> Result<Process> {
        let process = Process {
            service_epoch: self.epoch,
            identity: observed,
        };
        self.exact(process)?;
        Ok(process)
    }
    /// AFTER real shell admission and exact native parent observation. No fields
    /// are rewritten to repair mismatches. New shell needs all old views settled.
    pub fn admitted_shell(
        &mut self,
        identity: NativeIdentity,
        observed_parent: u32,
    ) -> Result<Process> {
        self.active()?;
        if identity.slot != 1 {
            return Err(ProcessError::Stale);
        }
        startup::greeting(identity, identity.epoch, observed_parent)
            .map_err(ProcessError::Identity)?;
        if self.records.iter().any(|r| r.process.is_some()) {
            return Err(ProcessError::Busy);
        }
        if identity.epoch != self.records[0].last_generation + 1 {
            return Err(ProcessError::Generation);
        }
        let process = Process {
            service_epoch: self.epoch,
            identity,
        };
        self.records[0] = Record {
            process: Some(process),
            last_generation: identity.epoch,
            #[cfg(fs_cwd)]
            cwd: None,
        };
        Ok(process)
    }
    /// AFTER confirmed native copy/admission. Caller freezes parent between
    /// native copy and this local binding copy, and owns failed native cleanup.
    /// No native admission, endpoint transfer or extra AF07 lookup is performed.
    pub fn inherited_child(
        &mut self,
        parent: Process,
        child: NativeIdentity,
        observed_parent: u32,
    ) -> Result<Process> {
        self.inherit_local(parent, child, observed_parent)
    }

    /// Version 1 alternative to the frozen-parent API. One exclusive borrow
    /// spans preflight, the synchronous native-copy callback and local clone.
    /// Safe callbacks cannot reenter any view in this ledger. The dispatcher
    /// must also exclude external file/stream admissions, validate the tagged
    /// snapshot while parked, authenticate actual copy observations, and own
    /// bounded waits, native cleanup and child readiness. No wire is selected.
    /// Do not hold a second service view or mutate the source out of band.
    /// Refused means confirmed no child; unknown/unbound/unwind retire local
    /// admission, preserve process occupancy and never claim native settlement.
    pub fn copy_inherit_serialized_v1<E>(
        &mut self,
        parent: Process,
        target: NativeIdentity,
        observed_parent: u32,
        copy: impl FnOnce() -> CopyAttempt<E>,
    ) -> core::result::Result<Process, CopyInheritanceError<E>> {
        self.child_view(parent, target, observed_parent)
            .map_err(CopyInheritanceError::BeforeCopy)?;
        let mut guard = CopyGuard {
            files: self,
            complete: false,
        };
        match copy() {
            CopyAttempt::Refused(error) => {
                guard.complete = true;
                Err(CopyInheritanceError::Refused(error))
            }
            CopyAttempt::Unknown(error) => Err(CopyInheritanceError::Unknown(error)),
            CopyAttempt::Copied {
                identity,
                parent_pid,
            } => {
                let result = if identity != target || parent_pid != observed_parent {
                    Err(ProcessError::Stale)
                } else {
                    guard.files.inherit_local(parent, identity, parent_pid)
                };
                match result {
                    Ok(process) => {
                        guard.complete = true;
                        Ok(process)
                    }
                    Err(error) => Err(CopyInheritanceError::Unbound {
                        identity,
                        parent_pid,
                        error,
                    }),
                }
            }
        }
    }

    fn child_view(
        &self,
        parent: Process,
        child: NativeIdentity,
        observed_parent: u32,
    ) -> Result<usize> {
        let parent_view = self.exact(parent)?;
        if parent_view != 0 || !(2..=4).contains(&child.slot) {
            return Err(ProcessError::Stale);
        }
        startup::greeting(child, parent.identity.epoch, observed_parent)
            .map_err(ProcessError::Identity)?;
        if observed_parent != parent.identity.pid {
            return Err(ProcessError::Stale);
        }
        let view = child.slot as usize - 1;
        if self.records[view].process.is_some() {
            return Err(ProcessError::Busy);
        }
        if child.epoch != self.records[view].last_generation + 1 {
            return Err(ProcessError::Generation);
        }
        Ok(view)
    }

    // Called only under the old native-freeze contract or the exclusive v1
    // callback sequence. Both use the same validation and binding algorithm.
    fn inherit_local(
        &mut self,
        parent: Process,
        child: NativeIdentity,
        observed_parent: u32,
    ) -> Result<Process> {
        let view = self.child_view(parent, child, observed_parent)?;
        self.files
            .inherit_view(0, view)
            .map_err(ProcessError::Files)?;
        let process = Process {
            service_epoch: self.epoch,
            identity: child,
        };
        self.records[view] = Record {
            process: Some(process),
            last_generation: child.epoch,
            #[cfg(fs_cwd)]
            cwd: self.records[0].cwd,
        };
        Ok(process)
    }
    pub fn open_read(&mut self, process: Process, name: &[u8], cloexec: bool) -> Result<i32> {
        let view = self.exact(process)?;
        #[cfg(fs_cwd)]
        {
            let directory = self.directory_for(view)?;
            self.files
                .open_read_using(view, cloexec, |source| {
                    #[cfg(fs_cwd_wire)]
                    let result = source.client.resolve_file_from(directory, name);
                    #[cfg(not(fs_cwd_wire))]
                    let result = {
                        if name.starts_with(b"/") {
                            source.client.open_root_path(name)
                        } else {
                            source.client.open_file_from(directory, name)
                        }
                    };
                    result.map(|entry| entry.handle)
                })
                .map_err(ProcessError::Files)
        }
        #[cfg(not(fs_cwd))]
        self.files
            .open_read_in(view, name, cloexec)
            .map_err(ProcessError::Files)
    }
    pub fn duplicate(
        &mut self,
        process: Process,
        fd: i32,
        minimum: i32,
        cloexec: bool,
    ) -> Result<i32> {
        let view = self.exact(process)?;
        self.files
            .duplicate_in(view, fd, minimum, cloexec)
            .map_err(ProcessError::Files)
    }
    #[cfg(fs_replace)]
    pub fn replace(&mut self, process: Process, from: i32, to: i32) -> Result<i32> {
        let view = self.exact(process)?;
        self.files
            .replace_in(view, from, to)
            .map_err(ProcessError::Files)
    }
    pub fn position(&self, process: Process, fd: i32) -> Result<u64> {
        let view = self.exact(process)?;
        self.files
            .position_in(view, fd)
            .map_err(ProcessError::Files)
    }
    pub fn read(
        &mut self,
        process: Process,
        fd: i32,
        length: usize,
        out: &mut [u8; MAX_READ],
    ) -> Result<usize> {
        out.fill(0);
        let view = self.exact(process)?;
        self.files
            .read_in(view, fd, length, out)
            .map_err(ProcessError::Files)
    }
    pub fn seek(&mut self, process: Process, fd: i32, seek: Seek) -> Result<u64> {
        let view = self.exact(process)?;
        self.files
            .seek_in(view, fd, seek)
            .map_err(ProcessError::Files)
    }
    pub fn close(&mut self, process: Process, fd: i32) -> Result<()> {
        let view = self.exact(process)?;
        self.files.close_in(view, fd).map_err(ProcessError::Files)
    }
    pub fn set_close_on_exec(&mut self, process: Process, fd: i32, value: bool) -> Result<()> {
        let view = self.exact(process)?;
        self.files
            .set_close_on_exec_in(view, fd, value)
            .map_err(ProcessError::Files)
    }
    /// Destructive local commit only after actual image admission is confirmed.
    /// A failed/unknown exec MUST NOT call this. No exec implementation here.
    pub fn commit_exec_close(&mut self, process: Process) -> Result<()> {
        let view = self.exact(process)?;
        self.files
            .commit_exec_close_in(view)
            .map_err(ProcessError::Files)
    }
    /// Only AFTER the exact instance/endpoints have actually settled. Removes
    /// this view's aliases, not native process/memory/channel objects. Failed
    /// closes preserve ledger occupancy and retire the entire shared source.
    pub fn settled(&mut self, process: Process) -> Result<()> {
        let view = self.exact(process)?;
        self.files.settle_view(view).map_err(ProcessError::Files)?;
        #[cfg(fs_cwd)]
        {
            self.release_directory(view)?;
            self.records[view].cwd = None;
        }
        self.records[view].process = None;
        Ok(())
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.files.cleanup()
    }
    /// Unknown native/I/O outcome closes admission, never claims settlement.
    pub fn abort(&mut self) {
        self.files.retire();
    }
    /// Wire disconnect is allowed only after every process view is settled.
    /// Exact native engine/channel verification after acknowledgment, before
    /// endpoint closure. All process views must already be actually settled.
    pub fn disconnect_checked(
        &mut self,
        verify: impl FnOnce(&mut T) -> core::result::Result<(), filesystem_client::Error>,
    ) -> Result<[i64; 2]> {
        self.active()?;
        if self.records.iter().any(|r| r.process.is_some()) {
            return Err(ProcessError::Busy);
        }
        self.files
            .disconnect_checked(verify)
            .map_err(ProcessError::Files)
    }
    pub fn disconnect(&mut self) -> Result<[i64; 2]> {
        self.active()?;
        if self.records.iter().any(|r| r.process.is_some()) {
            return Err(ProcessError::Busy);
        }
        self.files.disconnect_source().map_err(ProcessError::Files)
    }
}
#[cfg(test)]
#[cfg_attr(not(fs_file16), path = "process-descriptor-tests.rs")]
#[cfg_attr(fs_file16, path = "file16-tests.rs")]
mod tests;

#[cfg(all(test, fs_in_place))]
#[path = "broker-init-tests.rs"]
mod init_tests;

#[cfg(fs_cwd)]
#[path = "process-cwd.rs"]
mod cwd;

#[cfg(fs_process_writes)]
#[path = "process-writes.rs"]
mod writes;
#[cfg(fs_process_writes)]
pub use writes::{HomeAccess, ProcessWriteFailure};
