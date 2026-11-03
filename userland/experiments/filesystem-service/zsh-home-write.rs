// SPDX-License-Identifier: BSD-2-Clause
//! One fixed held-home write. The Owner authenticates exec/READY before admission.
use super::*;
use filesystem_client::{MutationOutcome, MutationProgress};
pub const ENTRY: &[u8] = b"/home/probe";
pub const BYTES: &[u8; 16] = b"AETHER-ZSH-HOME\n";

pub(super) struct HomeWrite {
    pub(super) binding: Binding,
    pub(super) sequence: u64,
    pub(super) close_sequence: u64,
    status: i64,
    count: u64,
    pub(super) receipt: [u64; 8],
    fd: i32,
    pub(super) phase: u8,
    pub(super) poisoned: bool,
}
impl HomeWrite {
    pub(super) const fn new() -> Self {
        Self {
            binding: Binding {
                slot: 0,
                epoch: 0,
                handle: 0,
                generation: 0,
            },
            sequence: 0,
            close_sequence: 0,
            status: 0,
            count: 0,
            receipt: [0; 8],
            fd: -1,
            phase: 0,
            poisoned: false,
        }
    }
}
const _: () = assert!(core::mem::size_of::<HomeWrite>() <= 128);
impl<T: Channel> Files<T> {
    /// Sole trusted Owner call AFTER matched C003 publication and native READY.
    pub fn admit_home_write(&mut self, binding: Binding) -> Result<(), Error> {
        if self.child != Some(binding)
            || self.home_write.binding != binding
            || binding.slot != 2
            || !self.live(binding)
            || self.home_write.phase != 0
            || self.home_write.poisoned
        {
            return Err(Error::Protocol);
        }
        self.home_write.binding = binding;
        self.home_write.phase = 1;
        Ok(())
    }
    /// Retained through known child settlement and healthy namespace disconnect.
    /// No teardown, unknown delivery or reconstructed object grants completion.
    pub fn home_write_complete(&self) -> bool {
        self.home_write.phase == 5
            && !self.home_write.poisoned
            && self.home_write.status == 0
            && self.home_write.count == 16
            && self.home_write.receipt[0] == 14
            && self.home_write.receipt[1] == 0
            && self.home_write.receipt[2] != 0
            && self.home_write.receipt[3] == 16
            && (!self.retired || self.cleanup() == Some([0; 2]))
    }
    fn home_actor(&self, binding: Binding) -> bool {
        !self.home_write.poisoned
            && self.child == Some(binding)
            && self.home_write.binding == binding
            && self.live(binding)
    }
    pub(super) fn is_home_file(&self, view: usize, fd: i32) -> bool {
        view == 1 && self.home_write.phase >= 2 && fd == self.home_write.fd
    }
    pub(super) fn open_home_write(
        &mut self,
        view: usize,
        name: &[u8],
        cloexec: bool,
    ) -> descriptions::Result<i32, Error> {
        if view != 1 || !self.home_actor(self.home_write.binding) || self.home_write.phase != 1 {
            return Err(Failure::BadFd);
        }
        if name != ENTRY {
            return Err(Failure::Source(Error::Remote(-2)));
        }
        let fd = self.descriptions.open_read_using(view, cloexec, |source| {
            let home = source.client.home()?;
            let entry = source.client.lookup(home, b"probe", 4)?;
            if entry.kind != Kind::File || entry.size != 0 {
                source.client.close(entry.handle)?;
                return Err(Error::Invalid);
            }
            Ok(entry.handle)
        })?;
        self.home_write.fd = fd;
        self.home_write.phase = 2;
        Ok(fd)
    }
    pub(super) fn prepare_home_write<'a>(
        &'a mut self,
        binding: Binding,
        raw: &[u8; FRAME],
        workspace: &'a mut [u8; PAYLOAD],
    ) -> Result<Reply<'a, T>, Error> {
        let view = self.view(binding).ok_or(Error::Protocol)?;
        let fd = word(raw, 4) as i32;
        let requested = word(raw, 5) as usize;
        let mut receipt = [0u64; 8];
        let mut status = -9i64;
        let mut count = 0u64;
        receipt[6] = 1; // Known local BadFd; no mutation was sent.
        let allowed =
            self.home_actor(binding) && self.home_write.phase == 2 && fd == self.home_write.fd;
        if allowed {
            status = -22;
            receipt[6] = 3; // Invalid fixed workload; still no source effect.
            if requested == BYTES.len() && workspace[..requested] == BYTES[..] {
                let (_, descriptor) = self
                    .descriptions
                    .binding_in(view, fd)
                    .map_err(|_| Error::Protocol)?;
                let index = descriptor.description as usize;
                let file = self.descriptions.descriptions[index].ok_or(Error::Protocol)?;
                if file.offset != 0 {
                    return Err(Error::Protocol);
                }
                match self
                    .descriptions
                    .source
                    .client
                    .write(file.handle, file.offset, BYTES)
                {
                    Ok(done) => {
                        status = 0;
                        count = done.bytes as u64;
                        receipt = [14, file.offset, done.txg, count, 0, 0, 0, 0];
                        self.descriptions.descriptions[index] = Some(descriptions::Description {
                            offset: file.offset + count,
                            ..file
                        });
                        self.home_write.phase = 3;
                    }
                    Err(failure) => {
                        self.mutation_failure = Some(failure);
                        let (kind, value, error) = match failure.error {
                            Error::Invalid => (7, 0, -22),
                            Error::Closed => (8, 0, -5),
                            Error::Full => (9, 0, -28),
                            Error::Protocol => (10, 0, -5),
                            Error::Transport(v) => (11, v, -5),
                            Error::Remote(v) => (12, v, v),
                        };
                        status = error;
                        let (tag, txg, staged) = match failure.outcome {
                            MutationOutcome::NotSent => (0, 0, 0),
                            MutationOutcome::Unknown => (5, 0, 0),
                            MutationOutcome::Reported(progress) => match progress {
                                MutationProgress::Unassigned => (1, 0, 0),
                                MutationProgress::Committed { txg, bytes_staged } => {
                                    (2, txg, bytes_staged as u64)
                                }
                                MutationProgress::Completed { txg, bytes_staged } => {
                                    (3, txg, bytes_staged as u64)
                                }
                                MutationProgress::Unknown => (4, 0, 0),
                            },
                        };
                        let cleanup = failure.cleanup.unwrap_or([0; 2]);
                        receipt = [
                            tag | 8 | if failure.cleanup.is_some() { 16 } else { 0 },
                            file.offset,
                            txg,
                            staged,
                            cleanup[0] as u64,
                            cleanup[1] as u64,
                            kind,
                            value as u64,
                        ];
                        self.home_write.poisoned = true;
                        if failure.cleanup.is_some() {
                            self.descriptions.retire();
                            self.retired = true;
                        }
                    }
                }
                // Retain the correlated completed/failed effect before transport delivery.
                self.home_write.sequence = word(raw, 3);
                self.home_write.status = status;
                self.home_write.count = count;
                self.home_write.receipt = receipt;
            }
        }
        workspace.fill(0);
        for (index, value) in receipt.into_iter().enumerate() {
            put((&mut workspace[..FRAME]).try_into().unwrap(), index, value);
        }
        let mut header = [0; FRAME];
        header[..8].copy_from_slice(MAGIC);
        put(&mut header, 1, status as u64);
        put(&mut header, 2, binding.generation);
        put(&mut header, 3, word(raw, 3));
        put(&mut header, 4, count);
        put(&mut header, 5, FRAME as u64);
        if view == 1 {
            self.child_pending = true;
        } else {
            self.pending = true;
        }
        Ok(Reply {
            view,
            files: self,
            workspace,
            header,
            body: FRAME,
            delivered: false,
        })
    }
}
