// SPDX-License-Identifier: BSD-2-Clause
//! One sealed held-object snapshot; namespace labels never grant native execute.
use super::*;

pub(super) struct FileExec {
    held: Option<Handle>,
    size: usize,
    phase: u8,
    #[cfg(native_zsh_repeat_exec)]
    repeated: bool,
}
impl FileExec {
    pub(super) const fn new() -> Self {
        Self {
            held: None,
            size: 0,
            phase: 0,
            #[cfg(native_zsh_repeat_exec)]
            repeated: false,
        }
    }
    pub(super) fn poison(&mut self) {
        self.held = None;
        self.phase = 3;
    }
}
const _: () = assert!(core::mem::size_of::<FileExec>() <= 48);
impl<T: Channel> Files<T> {
    /// Sole trusted bootstrap call, before any child exists. Keep a READ2 label
    /// for this actual object while retiring the sole temporary WRITE4 label.
    /// No untrusted FILE or namespace operation can create a mutation alias.
    #[cfg(not(native_zsh_cold_reopen))]
    pub fn provision_file_exec(&mut self, image: &[u8]) -> Result<(), Error> {
        if self.retired
            || self.pending
            || self.child.is_some()
            || self.descriptions.source.held.is_none()
            || self.file_exec.phase != 0
            || image.is_empty()
            || image.len() > PAYLOAD
        {
            return Err(Error::Invalid);
        }
        self.file_exec.phase = 3; // No replay even after a known partial failure.
        let mut mutation_failure = None;
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let home = client.home()?;
            let writable = client.lookup(home, b"probe", 4)?;
            if writable.kind != Kind::File || writable.size != 0 {
                return Err(Error::Protocol);
            }
            let done = client.write(writable.handle, 0, image).map_err(|failure| {
                mutation_failure = Some(failure);
                failure.error
            })?;
            if done.bytes != image.len() {
                return Err(Error::Protocol);
            }
            let sealed = client.lookup(home, b"probe", 2)?;
            if sealed.kind != Kind::File || sealed.size != image.len() as u64 {
                return Err(Error::Protocol);
            }
            client.close(writable.handle)?;
            self.file_exec.held = Some(sealed.handle);
            self.file_exec.size = image.len();
            self.file_exec.phase = 1;
            Ok(())
        })();
        self.mutation_failure = mutation_failure;
        if result.is_err() {
            self.abort();
        }
        result
    }
    /// The already-authorized trusted Owner selects this actual current-epoch
    /// object only after complete byte equality constrains its closed policy.
    /// Retain this same READ handle; acquire_file_exec closes it before native
    /// execution. No path, hash, READ label or previous-boot handle grants exec.
    #[cfg(native_zsh_cold_reopen)]
    pub fn reopen_file_exec(
        &mut self,
        image: &[u8],
        workspace: &mut [u8; PAYLOAD],
    ) -> Result<(), Error> {
        if self.retired
            || self.pending
            || self.child.is_some()
            || self.descriptions.source.held.is_none()
            || self.file_exec.phase != 0
            || image.is_empty()
            || image.len() > PAYLOAD
        {
            return Err(Error::Invalid);
        }
        self.validate_file_exec(image, workspace)
    }
    /// Trusted second exec only: this is not a child FILE rearm operation.
    /// The exact admitted epoch2 and one-use marker survive native refusal.
    #[cfg(native_zsh_repeat_exec)]
    pub fn revalidate_file_exec(
        &mut self,
        child: Binding,
        image: &[u8],
        workspace: &mut [u8; PAYLOAD],
    ) -> Result<(), Error> {
        if self.retired
            || self.pending
            || self.child_pending
            || !self.live(child)
            || self.child != Some(child)
            || child.slot != 2
            || child.epoch != 2
            || self.file_exec.phase != 2
            || self.file_exec.held.is_some()
            || self.file_exec.repeated
            || self.descriptions.source.held.is_none()
            || image.is_empty()
            || image.len() > PAYLOAD
        {
            return Err(Error::Invalid);
        }
        // Mark before lookup/read/close, and never undo it after any result.
        self.file_exec.repeated = true;
        self.validate_file_exec(image, workspace)
    }
    #[cfg(native_zsh_cold_reopen)]
    fn validate_file_exec(
        &mut self,
        image: &[u8],
        workspace: &mut [u8; PAYLOAD],
    ) -> Result<(), Error> {
        self.file_exec.phase = 3;
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let home = client.home()?;
            let sealed = client.lookup(home, b"probe", 2)?;
            if sealed.kind != Kind::File || sealed.size != image.len() as u64 {
                return Err(Error::Protocol);
            }
            if client.read(sealed.handle, image.len() as u64, 1, workspace)? != 0
                || client.read(sealed.handle, 0, image.len(), workspace)? != image.len()
                || workspace[..image.len()] != *image
            {
                return Err(Error::Protocol);
            }
            let stat = client.stat(sealed.handle)?;
            if stat.kind != Kind::File || stat.size != image.len() as u64 {
                return Err(Error::Protocol);
            }
            self.file_exec.held = Some(sealed.handle);
            self.file_exec.size = image.len();
            self.file_exec.phase = 1;
            Ok(())
        })();
        workspace.fill(0);
        if result.is_err() {
            self.abort();
        }
        result
    }
    /// Runtime authenticates the actual frozen child's endpoint before this call.
    /// The retained READ2 label binds the sealed object and Client epoch; names
    /// are not resolved again. EOF is checked first because read clears out.
    pub fn acquire_file_exec(
        &mut self,
        child: Binding,
        out: &mut [u8; PAYLOAD],
    ) -> Result<usize, Error> {
        if self.file_exec.phase != 1
            || self.pending
            || self.child_pending
            || !self.live(child)
            || self.child != Some(child)
            || child.slot != 2
        {
            return Err(Error::Invalid);
        }
        let held = self.file_exec.held.take().ok_or(Error::Invalid)?;
        let size = self.file_exec.size;
        self.file_exec.phase = 3;
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let stat = client.stat(held)?;
            if stat.kind != Kind::File || stat.size != size as u64 || !(1..=PAYLOAD).contains(&size)
            {
                return Err(Error::Protocol);
            }
            if client.read(held, size as u64, 1, out)? != 0 {
                return Err(Error::Protocol);
            }
            if client.read(held, 0, size, out)? != size {
                return Err(Error::Protocol);
            }
            let stat = client.stat(held)?;
            if stat.kind != Kind::File || stat.size != size as u64 {
                return Err(Error::Protocol);
            }
            // stat and close own small frames; neither overwrites the snapshot.
            client.close(held)?;
            Ok(size)
        })();
        if result.is_ok() {
            self.file_exec.phase = 2;
        } else {
            out.fill(0);
            self.abort();
        }
        result
    }
    pub fn file_exec_size(&self) -> Option<usize> {
        (self.file_exec.phase == 2
            && self.file_exec.held.is_none()
            && (!self.retired || self.cleanup() == Some([0; 2])))
        .then_some(self.file_exec.size)
    }
    pub fn file_exec_consumed(&self) -> bool {
        self.file_exec_size().is_some()
    }
    #[cfg(native_zsh_repeat_exec)]
    pub fn file_exec_repeated(&self) -> bool {
        self.file_exec.repeated && self.file_exec_consumed()
    }
    #[cfg(native_zsh_idle_exit)]
    pub fn file_exec_unused_closed(&self) -> bool {
        self.file_exec.phase == 4 && self.file_exec.held.is_none()
    }
    pub(super) fn release_file_exec(&mut self) -> Result<(), Error> {
        if let Some(held) = self.file_exec.held.take() {
            #[cfg(native_zsh_idle_exit)]
            let validated = self.file_exec.phase == 1;
            self.file_exec.phase = 3; // An unknown or failed close is never replayed.
            self.descriptions.source.client.close(held)?;
            #[cfg(native_zsh_idle_exit)]
            if validated {
                self.file_exec.phase = 4;
            }
        }
        Ok(())
    }
}
