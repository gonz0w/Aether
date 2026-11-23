// SPDX-License-Identifier: BSD-2-Clause
//! One sealed held-object snapshot; namespace labels never grant native execute.
use super::*;

pub(super) struct FileExec {
    held: Option<Handle>,
    size: usize,
    phase: u8,
    #[cfg(native_package_bytecount)]
    output_attempted: bool,
    #[cfg(all(native_zsh_repeat_exec, not(native_zsh_operator_login)))]
    repeated: bool,
    #[cfg(native_zsh_operator_login)]
    attempted_epoch: u8,
}
impl FileExec {
    pub(super) const fn new() -> Self {
        Self {
            held: None,
            size: 0,
            phase: 0,
            #[cfg(native_package_bytecount)]
            output_attempted: false,
            #[cfg(all(native_zsh_repeat_exec, not(native_zsh_operator_login)))]
            repeated: false,
            #[cfg(native_zsh_operator_login)]
            attempted_epoch: 0,
        }
    }
    pub(super) fn poison(&mut self) {
        self.held = None;
        self.phase = 3;
    }
}
const _: () = assert!(core::mem::size_of::<FileExec>() <= 48);
#[cfg(native_package_bytecount)]
#[inline(never)]
fn package_bytes_equal(actual: &[u8], expected: &[u8]) -> bool {
    actual == expected
}
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
    /// Trusted revalidation only, never a child FILE rearm operation. The old
    /// profile permits epoch2 once; operator login permits each exact next epoch
    /// once. Attempt markers survive native refusal and never move backwards.
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
            || if cfg!(native_zsh_operator_login) {
                !(2..=15).contains(&child.epoch)
            } else {
                child.epoch != 2
            }
            || self.file_exec.phase != 2
            || self.file_exec.held.is_some()
            || self.file_exec_revalidation_used(child.epoch)
            || self.descriptions.source.held.is_none()
            || image.is_empty()
            || image.len() > PAYLOAD
        {
            return Err(Error::Invalid);
        }
        // Mark before lookup/read/close, and never undo it after any result.
        #[cfg(not(native_zsh_operator_login))]
        {
            self.file_exec.repeated = true;
        }
        #[cfg(native_zsh_operator_login)]
        {
            self.file_exec.attempted_epoch = child.epoch;
        }
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
        #[cfg(native_zsh_operator_login)]
        if self.file_exec.attempted_epoch > child.epoch {
            return Err(Error::Invalid);
        }
        #[cfg(native_zsh_operator_login)]
        {
            self.file_exec.attempted_epoch = child.epoch;
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
    #[cfg(native_package_bytecount)]
    #[inline(never)]
    pub fn stage_package_bytecount(
        &mut self,
        expected: &[u8],
        block: &mut [u8; PAYLOAD],
        seed: bool,
    ) -> Result<(), Error> {
        use filesystem_client::NamespaceMutation;
        if self.retired
            || self.pending
            || self.child.is_some()
            || self.file_exec.phase != 0
            || self.descriptions.source.held.is_some()
            || expected.len() <= 10 * PAYLOAD
            || expected.len() > 11 * PAYLOAD
        {
            return Err(Error::Invalid);
        }
        self.file_exec.phase = 3;
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let pkg = client.home()?;
            if seed {
                for name in [b"bytecount".as_slice(), b"input", b"output"] {
                    client
                        .namespace(pkg, NamespaceMutation::Create(name))
                        .map_err(|e| e.error)?;
                }
                for (name, bytes) in [(b"bytecount".as_slice(), expected), (b"input", b"abcdef")] {
                    let file = client.lookup(pkg, name, 4)?;
                    if file.kind != Kind::File || file.size != 0 {
                        return Err(Error::Protocol);
                    }
                    for (index, bytes) in bytes.chunks(PAYLOAD).enumerate() {
                        let completion = client
                            .write(file.handle, (index * PAYLOAD) as u64, bytes)
                            .map_err(|e| e.error)?;
                        if completion.bytes != bytes.len() {
                            return Err(Error::Protocol);
                        }
                    }
                    client.close(file.handle)?;
                }
            }
            for (name, bytes) in [
                (b"input".as_slice(), b"abcdef".as_slice()),
                (b"output", if seed { b"".as_slice() } else { b"6\n" }),
            ] {
                let file = client.lookup(pkg, name, 2)?;
                if file.kind != Kind::File
                    || file.size != bytes.len() as u64
                    || client.read(file.handle, bytes.len() as u64, 1, block)? != 0
                    || client.read(file.handle, 0, bytes.len(), block)? != bytes.len()
                    || !package_bytes_equal(&block[..bytes.len()], bytes)
                {
                    return Err(Error::Protocol);
                }
                client.close(file.handle)?;
            }
            let image = client.lookup(pkg, b"bytecount", 2)?;
            if image.kind != Kind::File || image.size != expected.len() as u64 {
                return Err(Error::Protocol);
            }
            let root = client.root()?;
            let retained = client.lookup(root, b"pkg", 3)?;
            if retained.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            self.descriptions.source.held = Some(retained.handle);
            self.file_exec.held = Some(image.handle);
            self.file_exec.size = expected.len();
            self.file_exec.phase = 1;
            Ok(())
        })();
        block.fill(0);
        if result.is_err() {
            self.abort();
        }
        result
    }

    #[cfg(native_package_bytecount)]
    #[inline(never)]
    pub fn acquire_package_bytecount(
        &mut self,
        child: Binding,
        expected: &[u8],
        snapshot: &mut [u8; 48 * 1024],
        block: &mut [u8; PAYLOAD],
    ) -> Result<usize, Error> {
        snapshot.fill(0);
        if self.file_exec.phase != 1
            || self.pending
            || self.child_pending
            || !self.live(child)
            || self.child != Some(child)
            || child.slot != 2
            || self.file_exec.size != expected.len()
            || expected.len() > snapshot.len()
        {
            return Err(Error::Invalid);
        }
        let held = self.file_exec.held.take().ok_or(Error::Invalid)?;
        self.file_exec.phase = 3;
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let length = expected.len() as u64;
            let stat = client.stat(held)?;
            if stat.kind != Kind::File
                || stat.size != length
                || client.read(held, length, 1, block)? != 0
            {
                return Err(Error::Protocol);
            }
            for (index, want) in expected.chunks(PAYLOAD).enumerate() {
                let offset = index * PAYLOAD;
                if client.read(held, offset as u64, want.len(), block)? != want.len()
                    || !package_bytes_equal(&block[..want.len()], want)
                {
                    return Err(Error::Protocol);
                }
                snapshot[offset..offset + want.len()].copy_from_slice(&block[..want.len()]);
            }
            let stat = client.stat(held)?;
            if stat.kind != Kind::File || stat.size != length {
                return Err(Error::Protocol);
            }
            client.close(held)?;
            Ok(expected.len())
        })();
        block.fill(0);
        if result.is_ok() {
            self.file_exec.phase = 2;
        } else {
            snapshot.fill(0);
            self.abort();
        }
        result
    }

    #[cfg(native_package_bytecount)]
    pub fn bind_package_stdio(&mut self, child: Binding) -> Result<(), Error> {
        if !self.live(child)
            || self.child != Some(child)
            || child.slot != 2
            || self.file_exec.phase != 2
            || self.file_view(child)? != (0, 0)
        {
            return Err(Error::Invalid);
        }
        let result = (|| {
            for (selector, name, rights, minimum, maximum) in [
                (3, b"input".as_slice(), 2, 6, 6),
                (4, b"output".as_slice(), 4, 0, 2),
            ] {
                let fd = self
                    .descriptions
                    .open_read_using(1, false, |source| {
                        let pkg = source.client.home()?;
                        let entry = source.client.lookup(pkg, name, rights)?;
                        if entry.kind != Kind::File || !(minimum..=maximum).contains(&entry.size) {
                            return Err(Error::Protocol);
                        }
                        Ok(entry.handle)
                    })
                    .map_err(|_| Error::Protocol)?;
                if fd != selector {
                    return Err(Error::Protocol);
                }
            }
            Ok(())
        })();
        if result.is_err() {
            self.abort();
        }
        result
    }

    #[cfg(native_package_bytecount)]
    pub(super) fn package_operation_funded(&self, raw: &[u8; FRAME], remaining: u32) -> bool {
        match word(raw, 1) {
            // Retain credit for output, both FILE closes and complete verification.
            2 => !self.file_exec.output_attempted && remaining >= 14,
            5 => remaining >= 11,
            _ => true,
        }
    }

    #[cfg(native_package_bytecount)]
    pub(super) fn prepare_package_write<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        workspace: &'a mut [u8; PAYLOAD],
        remaining: u32,
    ) -> Result<Reply<'a, T>, Error> {
        let count = word(raw, 5) as usize;
        let fd = word(raw, 4) as i32;
        let mut receipt = [0u64; 8];
        let mut done = 0;
        let mut status = -9i64;
        let valid = self.live(binding)
            && self.child == Some(binding)
            && binding.slot == 2
            && self.file_exec.phase == 2
            && fd == 4
            && !self.file_exec.output_attempted
            && count == 2
            && &workspace[..2] == b"6\n";
        if valid && remaining >= 13 {
            let (_, descriptor) = self
                .descriptions
                .binding_in(1, fd)
                .map_err(|_| Error::Protocol)?;
            let index = descriptor.description as usize;
            let file = self.descriptions.descriptions[index].ok_or(Error::Protocol)?;
            if file.offset != 0 {
                return Err(Error::Protocol);
            }
            self.file_exec.output_attempted = true;
            match self
                .descriptions
                .source
                .client
                .write(file.handle, 0, &workspace[..2])
            {
                Ok(completion) if completion.bytes == 2 => {
                    done = 2;
                    status = 0;
                    receipt = [14, 0, completion.txg, 2, 0, 0, 0, 0];
                    self.descriptions.descriptions[index] =
                        Some(descriptions::Description { offset: 2, ..file });
                }
                Ok(_) => {
                    self.abort();
                    return Err(Error::Protocol);
                }
                Err(failure) => {
                    self.mutation_failure = Some(failure);
                    self.abort();
                    return Err(failure.error);
                }
            }
        } else {
            if valid {
                status = -28;
            }
            receipt[6] = 1;
        }
        workspace.fill(0);
        for (i, value) in receipt.into_iter().enumerate() {
            put((&mut workspace[..FRAME]).try_into().unwrap(), i, value);
        }
        let mut header = [0; FRAME];
        header[..8].copy_from_slice(MAGIC);
        put(&mut header, 1, status as u64);
        put(&mut header, 2, binding.generation);
        put(&mut header, 3, word(raw, 3));
        put(&mut header, 4, done);
        put(&mut header, 5, 64);
        self.child_pending = true;
        Ok(Reply {
            view: 1,
            files: self,
            workspace,
            header,
            body: FRAME,
            delivered: false,
        })
    }

    #[cfg(native_package_bytecount)]
    pub fn verify_package_output(&mut self, block: &mut [u8; PAYLOAD]) -> Result<(), Error> {
        if self.child.is_some() || !self.file_exec.output_attempted {
            return Err(Error::Invalid);
        }
        let result = (|| {
            let client = &mut self.descriptions.source.client;
            let pkg = client.home()?;
            for (name, expected) in [
                (b"input".as_slice(), b"abcdef".as_slice()),
                (b"output", b"6\n"),
            ] {
                let file = client.lookup(pkg, name, 2)?;
                if file.kind != Kind::File
                    || file.size != expected.len() as u64
                    || client.read(file.handle, expected.len() as u64, 1, block)? != 0
                    || client.read(file.handle, 0, expected.len(), block)? != expected.len()
                    || !package_bytes_equal(&block[..expected.len()], expected)
                {
                    return Err(Error::Protocol);
                }
                client.close(file.handle)?;
            }
            Ok(())
        })();
        block.fill(0);
        if result.is_err() {
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
        #[cfg(not(native_zsh_operator_login))]
        let repeated = self.file_exec.repeated;
        #[cfg(native_zsh_operator_login)]
        let repeated = self.file_exec.attempted_epoch >= 2;
        repeated && self.file_exec_consumed()
    }
    #[cfg(native_zsh_repeat_exec)]
    fn file_exec_revalidation_used(&self, epoch: u8) -> bool {
        #[cfg(not(native_zsh_operator_login))]
        {
            let _ = epoch;
            self.file_exec.repeated
        }
        #[cfg(native_zsh_operator_login)]
        {
            self.file_exec.attempted_epoch.checked_add(1) != Some(epoch)
        }
    }
    #[cfg(native_zsh_operator_login)]
    pub fn file_exec_epoch_complete(&self, epoch: u8) -> bool {
        self.file_exec_consumed() && self.file_exec.attempted_epoch == epoch
    }
    #[cfg(native_zsh_operator_login)]
    pub(super) fn file_exec_held(&self) -> bool {
        self.file_exec.held.is_some()
    }
    #[cfg(native_zsh_operator_login)]
    pub(super) fn file_exec_credit(&self) -> u32 {
        match self.child {
            Some(_) if self.file_exec.held.is_some() => 5,
            Some(child) if self.file_exec.attempted_epoch < child.epoch => 9,
            _ => 0,
        }
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
