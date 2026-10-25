// SPDX-License-Identifier: BSD-2-Clause
//! Versioned FILE RPC over an authenticated process binding.
#![no_std]
use filesystem_client::Error as SourceError;
use filesystem_remote_descriptors::{Failure, Process, ProcessError, ProcessFiles, Seek, MAX_READ};
use filesystem_service::Channel;

#[cfg(not(fs_file_write_wire))]
const _: () = assert!(
    !matches!(filesystem_service::MAGIC, b"AFSRPC09"),
    "FILE writes require a separately integrated contract"
);

#[cfg(all(
    fs_file_write_wire,
    not(all(fs_process_writes, fs_path_wire, fs_dup2_wire))
))]
compile_error!("FILE write wire requires matched process writes, path and dup2 wire");
#[cfg(all(
    fs_file_write_wire,
    any(fs_cwd_wire, all(fs_in_place, not(fs_home_in_place)))
))]
compile_error!("FILE write wire excludes CWD or unselected home in-place");
#[cfg(all(
    fs_home_in_place,
    not(all(fs_in_place, fs_home_wire, fs_file_write_wire))
))]
compile_error!("home in-place FILE requires matched in-place home write wire");
#[cfg(fs_file_write_wire)]
const _: () = assert!(
    matches!(filesystem_service::MAGIC, b"AFSRPC09"),
    "FILE write wire requires AF09"
);

// Reject a mismatched dependency selection before a component wire can acquire
// path semantics (or a path wire can accidentally use a component-only broker).
const _: () = assert!(cfg!(fs_path_wire) == filesystem_remote_descriptors::ROOT_PATHS);
// Current root/component wires cannot silently acquire process-relative paths.
const _: () = assert!(
    cfg!(fs_cwd_wire) == filesystem_remote_descriptors::CURRENT_DIRECTORIES
        && cfg!(fs_cwd_wire) == filesystem_remote_descriptors::PUBLIC_DIRECTORIES,
    "CWD requires a separate public FILE contract"
);
// Selector geometry must match the explicit new wire, never peer negotiation.
const _: () = assert!(cfg!(fs_dup2_wire) == filesystem_remote_descriptors::FILE_SLOTS_16);
pub const PUBLIC_DIRECTORIES: bool = cfg!(fs_cwd_wire);
#[cfg(all(fs_cwd_wire, not(fs_dup2_wire)))]
compile_error!("fs_cwd_wire requires the matched dup2 wire");
pub const FILE_SLOTS_16: bool = cfg!(fs_dup2_wire);
#[cfg(all(fs_dup2_wire, not(all(fs_path_wire, fs_replace, fs_process_views))))]
compile_error!("fs_dup2_wire requires path wire, replacement and process views");
pub const FRAME: usize = 64;
#[cfg(all(fs_path_wire, not(all(fs_paths, fs_process_views))))]
compile_error!("fs_path_wire requires fs_paths and fs_process_views");
#[cfg(not(fs_path_wire))]
pub const MAGIC: &[u8; 8] = b"AEFD0001";
#[cfg(all(fs_path_wire, not(fs_dup2_wire)))]
pub const MAGIC: &[u8; 8] = b"AEFP0001";
#[cfg(all(fs_dup2_wire, not(any(fs_cwd_wire, fs_file_write_wire))))]
pub const MAGIC: &[u8; 8] = b"AEFP0002";
#[cfg(fs_cwd_wire)]
pub const MAGIC: &[u8; 8] = b"AEFP0003";
#[cfg(fs_file_write_wire)]
pub const MAGIC: &[u8; 8] = b"AEFW0001";
pub type Message = [u8; FRAME];
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    InvalidBinding,
    Protocol,
    Retired,
}

fn word(raw: &[u8], index: usize) -> u64 {
    // Called only after exact64-byte validation, with constant indices0..7.
    u64::from_le_bytes(raw[index * 8..index * 8 + 8].try_into().unwrap())
}
fn put(raw: &mut Message, index: usize, value: u64) {
    raw[index * 8..index * 8 + 8].copy_from_slice(&value.to_le_bytes());
}
fn fd(value: u64) -> bool {
    (filesystem_remote_descriptors::FIRST_FILE_FD as u64..16).contains(&value)
}
fn errno(error: ProcessError) -> i64 {
    match error {
        ProcessError::Identity(_) | ProcessError::Stale => -9,
        ProcessError::Busy => -16,
        ProcessError::Generation => -9,
        ProcessError::Files(value) => match value {
            Failure::BadFd => -9,
            Failure::Full => -24,
            Failure::Invalid => -22,
            Failure::Overflow => -75,
            Failure::Retired | Failure::InvalidCompletion => -5,
            Failure::Source(source) => match source {
                SourceError::Invalid => -22,
                SourceError::Full => -28,
                SourceError::Remote(code) => code,
                _ => -5,
            },
        },
    }
}

/// One authenticated application endpoint generation. Request labels cannot bind
/// or admit processes. The trusted dispatcher supplies the current opaque key.
pub struct Connection {
    process: Process,
    generation: u64,
    next: u64,
    retired: bool,
    pending: bool,
}
impl Connection {
    /// Opaque broker key for this binding, including retained error context.
    /// The caller still authenticates the actual endpoint/native observation;
    /// this copied selector grants no authority or proof of live admission.
    #[cfg(fs_file_write_wire)]
    pub fn bound_process(&self) -> Process {
        self.process
    }
    /// Trusted owner only, after actual native image commit and CLOEXEC effects.
    /// Same process/source view; a strictly fresh context generation resets FILE
    /// sequencing. This supplies no native authority or image-commit proof.
    pub fn rebind_after_exec(&mut self, process: Process, generation: u64) -> Result<(), Error> {
        if self.retired || self.pending || process != self.process || generation <= self.generation
        {
            return Err(Error::InvalidBinding);
        }
        *self = Self::bind(process, generation)?;
        Ok(())
    }
    pub fn bind(process: Process, generation: u64) -> core::result::Result<Self, Error> {
        if generation == 0 {
            return Err(Error::InvalidBinding);
        }
        Ok(Self {
            process,
            generation,
            next: 1,
            retired: false,
            pending: false,
        })
    }
    fn validate(&self, raw: &[u8]) -> core::result::Result<usize, Error> {
        if self.retired || self.pending {
            return Err(Error::Retired);
        }
        if raw.len() != FRAME
            || raw[..8] != MAGIC[..]
            || word(raw, 2) != self.generation
            || word(raw, 3) != self.next
            || self.next == u64::MAX
        {
            return Err(Error::Protocol);
        }
        let a = word(raw, 4);
        let b = word(raw, 5);
        let c = word(raw, 6);
        let d = word(raw, 7);
        let valid = match word(raw, 1) {
            1 => a <= 1 && (1..=255).contains(&b) && c == 0 && d == 0,
            #[cfg(fs_file_write_wire)]
            10 => a <= 1 && (1..=255).contains(&b) && c <= 2 && d == 0,
            #[cfg(fs_file_write_wire)]
            11 => fd(a) && (1..=MAX_READ as u64).contains(&b) && c == 0 && d == 0,
            2 => fd(a) && b <= MAX_READ as u64 && c == 0 && d == 0,
            3 => fd(a) && c <= 2 && d == 0,
            4 => fd(a) && b < 16 && c <= 1 && d == 0,
            5 => fd(a) && b == 0 && c == 0 && d == 0,
            6 => fd(a) && b <= 1 && c == 0 && d == 0,
            #[cfg(fs_dup2_wire)]
            7 => fd(a) && fd(b) && c == 0 && d == 0,
            #[cfg(fs_cwd_wire)]
            8 => a == 0 && (1..=255).contains(&b) && c == 0 && d == 0,
            _ => a == 0 && b == 0 && c == 0 && d == 0,
        };
        if !valid {
            return Err(Error::Protocol);
        }
        Ok(
            if word(raw, 1) == 1
                || (cfg!(fs_cwd_wire) && word(raw, 1) == 8)
                || (cfg!(fs_file_write_wire) && matches!(word(raw, 1), 10 | 11))
            {
                (b as usize).div_ceil(FRAME) * FRAME
            } else {
                0
            },
        )
    }
    fn validate_bound<T: Channel>(
        &self,
        files: &ProcessFiles<T>,
        raw: &[u8],
    ) -> core::result::Result<usize, Error> {
        let needed = self.validate(raw)?;
        files
            .validate_binding(self.process)
            .map_err(|_| Error::Retired)?;
        Ok(needed)
    }
    /// Complete padded inbound body bytes required after a validated header.
    /// Caller must assemble all frames boundedly before prepare; this has no effects.
    pub fn input_length<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        raw: &[u8],
    ) -> core::result::Result<usize, Error> {
        let result = self.validate_bound(files, raw);
        if result.is_err() {
            self.abort(files);
        }
        result
    }
    pub fn abort<T: Channel>(&mut self, files: &mut ProcessFiles<T>) {
        self.retired = true;
        self.pending = false;
        files.abort();
    }
    /// Workspace initially contains exactly `received` inbound body bytes, if
    /// any. Safe borrows prevent reuse of pool/connection/output until settled.
    pub fn prepare<'a, T: Channel>(
        &'a mut self,
        files: &'a mut ProcessFiles<T>,
        raw: &[u8],
        received: usize,
        workspace: &'a mut [u8; MAX_READ],
    ) -> core::result::Result<PreparedReply<'a, T>, Error> {
        let needed = match self.validate_bound(files, raw) {
            Ok(value) => value,
            Err(error) => {
                workspace.fill(0);
                self.abort(files);
                return Err(error);
            }
        };
        if received != needed
            || (needed != 0
                && workspace[word(raw, 5) as usize..needed]
                    .iter()
                    .any(|&b| b != 0))
        {
            workspace.fill(0);
            self.abort(files);
            return Err(Error::Protocol);
        }
        self.pending = true;
        #[cfg(fs_file_write_wire)]
        if word(raw, 1) == 11 {
            return self.prepare_write(files, raw, workspace);
        }
        let (result, mut body) = execute(files, self.process, raw, workspace);
        // A retired source cannot produce an apparently usable error reply.
        if files.cleanup().is_some()
            || matches!(
                result,
                Err(ProcessError::Stale | ProcessError::Identity(_) | ProcessError::Generation)
            )
        {
            workspace.fill(0);
            self.abort(files);
            return Err(Error::Retired);
        }
        let (status, value) = match result {
            Ok(value) => (0, value),
            Err(error) => {
                workspace.fill(0);
                body = 0;
                (errno(error), 0)
            }
        };
        let mut reply = [0; FRAME];
        reply[..8].copy_from_slice(MAGIC);
        put(&mut reply, 1, status as u64);
        put(&mut reply, 2, self.generation);
        put(&mut reply, 3, self.next);
        put(&mut reply, 4, value);
        put(&mut reply, 5, body as u64);
        Ok(PreparedReply {
            connection: self,
            files,
            workspace,
            reply,
            body,
            delivered: false,
            #[cfg(fs_file_write_wire)]
            write: None,
        })
    }
}
// Keep source operations shared rather than inlining them into frame/lifetime
// orchestration. The caller already validated the complete bound request.
#[inline(never)]
fn execute<T: Channel>(
    files: &mut ProcessFiles<T>,
    process: Process,
    raw: &[u8],
    workspace: &mut [u8; MAX_READ],
) -> (core::result::Result<u64, ProcessError>, usize) {
    let opcode = word(raw, 1);
    let a = word(raw, 4);
    let b = word(raw, 5);
    let c = word(raw, 6);
    let mut body = 0usize;
    let result = match opcode {
        #[cfg(fs_file_write_wire)]
        10 => {
            let access = match c {
                0 => filesystem_remote_descriptors::HomeAccess::ReadOnly,
                1 => filesystem_remote_descriptors::HomeAccess::WriteOnly,
                _ => filesystem_remote_descriptors::HomeAccess::ReadWrite,
            };
            let result = files
                .open_home_file(process, &workspace[..b as usize], access, a != 0)
                .map(|fd| fd as u64);
            workspace.fill(0);
            result
        }
        1 => {
            let value = files
                .open_read(process, &workspace[..b as usize], a != 0)
                .map(|fd| fd as u64);
            workspace.fill(0);
            value
        }
        #[cfg(fs_cwd_wire)]
        8 => {
            let result = files
                .change_directory(process, &workspace[..b as usize])
                .map(|()| 0);
            workspace.fill(0);
            result
        }
        #[cfg(fs_cwd_wire)]
        9 => {
            workspace.fill(0);
            files
                .current_directory(process, (&mut workspace[..256]).try_into().unwrap())
                .map(|length| {
                    body = length;
                    length as u64
                })
        }
        2 => files
            .read(process, a as i32, b as usize, workspace)
            .map(|count| {
                body = count;
                count as u64
            }),
        _ => {
            workspace.fill(0);
            match opcode {
                3 => files.seek(
                    process,
                    a as i32,
                    match c {
                        0 => Seek::Set(b as i64),
                        1 => Seek::Current(b as i64),
                        _ => Seek::End(b as i64),
                    },
                ),
                4 => files
                    .duplicate(process, a as i32, b as i32, c != 0)
                    .map(|fd| fd as u64),
                5 => files.close(process, a as i32).map(|()| 0),
                6 => files
                    .set_close_on_exec(process, a as i32, b != 0)
                    .map(|()| 0),
                #[cfg(fs_dup2_wire)]
                7 => files
                    .replace(process, a as i32, b as i32)
                    .map(|fd| fd as u64),
                _ => Err(ProcessError::Files(Failure::Source(SourceError::Remote(
                    -38,
                )))),
            }
        }
    };
    (result, body)
}
/// Owns the pending outcome until its entire header AND padded body are sent.
/// Drop/unknown/partial delivery retires the shared source with no replay.
#[must_use]
pub struct PreparedReply<'a, T: Channel> {
    connection: &'a mut Connection,
    files: &'a mut ProcessFiles<T>,
    workspace: &'a mut [u8; MAX_READ],
    reply: Message,
    body: usize,
    delivered: bool,
    #[cfg(fs_file_write_wire)]
    write: Option<FileWriteReceipt>,
}
impl<T: Channel> PreparedReply<'_, T> {
    pub fn header(&self) -> &Message {
        &self.reply
    }
    pub fn body(&self) -> &[u8] {
        &self.workspace[..self.body.div_ceil(FRAME) * FRAME]
    }
    /// Trusted transport callback only after complete confirmed delivery.
    pub fn delivered(mut self) {
        self.connection.next += 1;
        self.connection.pending = false;
        self.delivered = true;
        self.workspace.fill(0);
    }
}
impl<T: Channel> Drop for PreparedReply<'_, T> {
    fn drop(&mut self) {
        if !self.delivered {
            self.workspace.fill(0);
            self.connection.abort(self.files);
        }
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "fd-protocol-tests.rs"]
mod tests;

#[cfg(fs_file_write_wire)]
#[path = "file-write-wire.rs"]
mod writes;
#[cfg(fs_file_write_wire)]
pub use writes::{FileWriteReceipt, FileWriteResult};
