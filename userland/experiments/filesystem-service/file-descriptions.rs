// SPDX-License-Identifier: BSD-2-Clause
//! Shared bounded file-description state; Store owns its actual source context.
pub const MAX_READ: usize = 4096;
pub trait Store {
    type Handle: Copy;
    type Error: Copy;
    type Cleanup;
    fn open_read(&mut self, name: &[u8]) -> core::result::Result<Self::Handle, Self::Error>;
    fn read(
        &mut self,
        handle: Self::Handle,
        offset: u64,
        length: usize,
        out: &mut [u8; MAX_READ],
    ) -> core::result::Result<usize, Self::Error>;
    fn size(&mut self, handle: Self::Handle) -> core::result::Result<u64, Self::Error>;
    fn close(&mut self, handle: Self::Handle) -> core::result::Result<(), Self::Error>;
    fn failure_is_fatal(&self, error: Self::Error) -> bool;
    fn retire(&mut self);
    fn disconnect(&mut self) -> core::result::Result<Self::Cleanup, Self::Error>;
}

/// Selected alias geometry; descriptions and source handles do not grow.
pub const FIRST_FILE_FD: i32 = if cfg!(fs_file16) { 0 } else { 3 };
pub const MAX_FDS: i32 = 16;
const SLOTS: usize = (MAX_FDS - FIRST_FILE_FD) as usize;
const DESCRIPTIONS: usize = 13;
const _: () = assert!(SLOTS <= u8::MAX as usize);

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Failure<E> {
    BadFd,
    Full,
    Invalid,
    Overflow,
    Retired,
    Source(E),
    InvalidCompletion,
}
pub type Result<T, E> = core::result::Result<T, Failure<E>>;

#[derive(Clone, Copy)]
pub(crate) struct Descriptor {
    pub(crate) description: u8,
    close_on_exec: bool,
}
#[derive(Clone, Copy)]
pub(crate) struct Description<H> {
    pub(crate) handle: H,
    pub(crate) offset: u64,
}

pub enum Seek {
    Set(i64),
    Current(i64),
    End(i64),
}

/// Shared serialized state. The concrete Store owns authority and cleanup.
#[must_use]
pub struct Descriptions<S: Store, const VIEWS: usize = 1> {
    pub(crate) source: S,
    descriptors: [[Option<Descriptor>; SLOTS]; VIEWS],
    pub(crate) descriptions: [Option<Description<S::Handle>>; DESCRIPTIONS],
    retired: bool,
}
impl<S: Store, const VIEWS: usize> Descriptions<S, VIEWS> {
    pub(crate) fn from_source(source: S) -> Self {
        Self {
            source,
            descriptors: [[None; SLOTS]; VIEWS],
            descriptions: [None; DESCRIPTIONS],
            retired: false,
        }
    }

    /// Initialize all non-owning fields, returning only the uninitialized source
    /// slot. Caller must initialize that source before publishing any Self.
    #[cfg(fs_in_place)]
    pub(crate) fn prepare_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
    ) -> &mut core::mem::MaybeUninit<S> {
        let pointer = slot.as_mut_ptr();
        // SAFETY: unique aligned parent storage; elementwise writes stay within
        // the two arrays. No Self/source reference or padding read is formed.
        // MaybeUninit<S> has S's layout and permits an uninitialized field borrow.
        unsafe {
            for index in 0..VIEWS * SLOTS {
                core::ptr::addr_of_mut!((*pointer).descriptors)
                    .cast::<Option<Descriptor>>()
                    .add(index)
                    .write(None);
            }
            for index in 0..DESCRIPTIONS {
                core::ptr::addr_of_mut!((*pointer).descriptions)
                    .cast::<Option<Description<S::Handle>>>()
                    .add(index)
                    .write(None);
            }
            core::ptr::addr_of_mut!((*pointer).retired).write(false);
            &mut *core::ptr::addr_of_mut!((*pointer).source).cast::<core::mem::MaybeUninit<S>>()
        }
    }

    pub(crate) fn active(&self) -> Result<(), S::Error> {
        if self.retired {
            Err(Failure::Retired)
        } else {
            Ok(())
        }
    }

    pub(crate) fn binding_in(&self, view: usize, fd: i32) -> Result<(usize, Descriptor), S::Error> {
        self.view(view)?;
        if !(FIRST_FILE_FD..MAX_FDS).contains(&fd) {
            return Err(Failure::BadFd);
        }
        let index = (fd - FIRST_FILE_FD) as usize;
        Ok((index, self.descriptors[view][index].ok_or(Failure::BadFd)?))
    }

    #[cfg(fs_process_views)]
    /// Exact remote FD presence/flags, computed from the sole authoritative view.
    pub(crate) fn file_view_in(&self, view: usize) -> Result<(u16, u16), S::Error> {
        self.view(view)?;
        let mut present = 0u16;
        let mut cloexec = 0u16;
        for (index, binding) in self.descriptors[view].iter().enumerate() {
            if let Some(binding) = binding {
                let bit = 1u16 << (index + FIRST_FILE_FD as usize);
                present |= bit;
                if binding.close_on_exec {
                    cloexec |= bit;
                }
            }
        }
        Ok((present, cloexec))
    }

    pub(crate) fn retire(&mut self) {
        self.retired = true;
        self.descriptors.fill([None; SLOTS]);
        self.descriptions.fill(None);
        self.source.retire();
    }

    pub(crate) fn source_error(&mut self, error: S::Error) -> Failure<S::Error> {
        if self.source.failure_is_fatal(error) {
            self.retire();
        }
        Failure::Source(error)
    }

    pub(crate) fn open_read_in(
        &mut self,
        view: usize,
        name: &[u8],
        close_on_exec: bool,
    ) -> Result<i32, S::Error> {
        self.open_read_using(view, close_on_exec, |source| source.open_read(name))
    }

    // Keep admission/capacity/publication identical for root and retained-CWD
    // consumers. The source callback is called once, only after local preflight.
    pub(crate) fn open_read_using(
        &mut self,
        view: usize,
        close_on_exec: bool,
        open: impl FnOnce(&mut S) -> core::result::Result<S::Handle, S::Error>,
    ) -> Result<i32, S::Error> {
        self.view(view)?;
        let fd = self.descriptors[view]
            .iter()
            .position(Option::is_none)
            .ok_or(Failure::Full)?;
        let description = self
            .descriptions
            .iter()
            .position(Option::is_none)
            .ok_or(Failure::Full)?;
        let handle = open(&mut self.source).map_err(|error| self.source_error(error))?;
        self.descriptions[description] = Some(Description { handle, offset: 0 });
        self.descriptors[view][fd] = Some(Descriptor {
            description: description as u8,
            close_on_exec,
        });
        Ok(fd as i32 + FIRST_FILE_FD)
    }

    pub(crate) fn duplicate_in(
        &mut self,
        view: usize,
        fd: i32,
        minimum: i32,
        close_on_exec: bool,
    ) -> Result<i32, S::Error> {
        let (_, binding) = self.binding_in(view, fd)?;
        if !(0..MAX_FDS).contains(&minimum) {
            return Err(Failure::Invalid);
        }
        let first = (minimum.max(FIRST_FILE_FD) - FIRST_FILE_FD) as usize;
        let target = (first..SLOTS)
            .find(|&i| self.descriptors[view][i].is_none())
            .ok_or(Failure::Full)?;
        self.descriptors[view][target] = Some(Descriptor {
            close_on_exec,
            ..binding
        });
        Ok(target as i32 + FIRST_FILE_FD)
    }

    /// Exact-target aliasing; failed last-handle close retires every view.
    #[cfg(fs_replace)]
    pub(crate) fn replace_in(&mut self, view: usize, from: i32, to: i32) -> Result<i32, S::Error> {
        let (source, binding) = self.binding_in(view, from)?;
        if !(FIRST_FILE_FD..MAX_FDS).contains(&to) {
            return Err(Failure::BadFd);
        }
        let target = (to - FIRST_FILE_FD) as usize;
        let previous = self.descriptors[view][target];
        for entry in [Some(binding), previous].into_iter().flatten() {
            if self
                .descriptions
                .get(entry.description as usize)
                .and_then(|v| *v)
                .is_none()
            {
                self.retire();
                return Err(Failure::InvalidCompletion);
            }
        }
        if source == target {
            return Ok(to);
        }
        self.descriptors[view][target] = Some(Descriptor {
            close_on_exec: false,
            ..binding
        });
        if let Some(previous) = previous {
            if !self
                .descriptors
                .iter()
                .flatten()
                .flatten()
                .any(|other| other.description == previous.description)
            {
                // Both descriptions were checked before changing the sole view;
                // exclusive borrowing prevents another mutation before take.
                let file = self.descriptions[previous.description as usize]
                    .take()
                    .unwrap();
                if let Err(error) = self.source.close(file.handle) {
                    self.retire();
                    return Err(Failure::Source(error));
                }
            }
        }
        Ok(to)
    }

    pub(crate) fn position_in(&self, view: usize, fd: i32) -> Result<u64, S::Error> {
        let (_, binding) = self.binding_in(view, fd)?;
        Ok(self.descriptions[binding.description as usize]
            .ok_or(Failure::BadFd)?
            .offset)
    }

    pub(crate) fn read_in(
        &mut self,
        view: usize,
        fd: i32,
        length: usize,
        reply: &mut [u8; MAX_READ],
    ) -> Result<usize, S::Error> {
        reply.fill(0);
        let (_, binding) = self.binding_in(view, fd)?;
        let file = self.descriptions[binding.description as usize].ok_or(Failure::BadFd)?;
        if length > MAX_READ {
            return Err(Failure::Invalid);
        }
        // This experimental subset rejects a requested range outside off_t
        // before provider effects, even if a near-limit read might meet EOF.
        if file
            .offset
            .checked_add(length as u64)
            .is_none_or(|end| end > i64::MAX as u64)
        {
            return Err(Failure::Overflow);
        }
        let result = self.source.read(file.handle, file.offset, length, reply);
        let count = match result {
            Ok(count) if count <= length => count,
            Ok(_) => {
                reply.fill(0);
                self.retire();
                return Err(Failure::InvalidCompletion);
            }
            Err(error) => {
                reply.fill(0);
                return Err(self.source_error(error));
            }
        };
        reply[count..].fill(0);
        self.descriptions[binding.description as usize] = Some(Description {
            offset: file.offset + count as u64,
            ..file
        });
        Ok(count)
    }

    pub(crate) fn seek_in(&mut self, view: usize, fd: i32, seek: Seek) -> Result<u64, S::Error> {
        let (_, binding) = self.binding_in(view, fd)?;
        let mut file = self.descriptions[binding.description as usize].ok_or(Failure::BadFd)?;
        let (base, delta) = match seek {
            Seek::Set(value) => (0, value),
            Seek::Current(value) => (file.offset, value),
            Seek::End(value) => {
                let size = self
                    .source
                    .size(file.handle)
                    .map_err(|error| self.source_error(error))?;
                (size, value)
            }
        };
        let offset = base.checked_add_signed(delta).ok_or(if delta < 0 {
            Failure::Invalid
        } else {
            Failure::Overflow
        })?;
        if offset > i64::MAX as u64 {
            return Err(Failure::Overflow);
        }
        file.offset = offset;
        self.descriptions[binding.description as usize] = Some(file);
        Ok(offset)
    }

    pub(crate) fn close_in(&mut self, view: usize, fd: i32) -> Result<(), S::Error> {
        let (index, binding) = self.binding_in(view, fd)?;
        self.descriptors[view][index] = None;
        if self
            .descriptors
            .iter()
            .flatten()
            .flatten()
            .any(|other| other.description == binding.description)
        {
            return Ok(());
        }
        let file = self.descriptions[binding.description as usize]
            .take()
            .ok_or(Failure::BadFd)?;
        if let Err(error) = self.source.close(file.handle) {
            self.retire();
            return Err(Failure::Source(error));
        }
        Ok(())
    }

    pub(crate) fn set_close_on_exec_in(
        &mut self,
        view: usize,
        fd: i32,
        value: bool,
    ) -> Result<(), S::Error> {
        let (index, mut binding) = self.binding_in(view, fd)?;
        binding.close_on_exec = value;
        self.descriptors[view][index] = Some(binding);
        Ok(())
    }

    /// Destructive local commit only AFTER confirmed native image admission.
    /// Do not call during failed preparation or unknown exec; the dispatcher
    /// must stage/settle native outcomes separately. No loader implemented here.
    pub(crate) fn commit_exec_close_in(&mut self, view: usize) -> Result<(), S::Error> {
        self.view(view)?;
        for index in 0..SLOTS {
            if self.descriptors[view][index].is_some_and(|fd| fd.close_on_exec) {
                self.close_in(view, index as i32 + FIRST_FILE_FD)?;
            }
        }
        Ok(())
    }

    fn view(&self, view: usize) -> Result<(), S::Error> {
        self.active()?;
        if view >= VIEWS {
            return Err(Failure::Invalid);
        }
        Ok(())
    }
    #[cfg(fs_process_views)]
    pub(crate) fn inherit_view(&mut self, parent: usize, child: usize) -> Result<(), S::Error> {
        self.view(parent)?;
        self.view(child)?;
        if parent == child || self.descriptors[child].iter().any(Option::is_some) {
            return Err(Failure::Invalid);
        }
        self.descriptors[child] = self.descriptors[parent];
        Ok(())
    }
    #[cfg(fs_process_views)]
    pub(crate) fn settle_view(&mut self, view: usize) -> Result<(), S::Error> {
        self.view(view)?;
        for index in 0..SLOTS {
            if self.descriptors[view][index].is_some() {
                self.close_in(view, index as i32 + FIRST_FILE_FD)?;
            }
        }
        Ok(())
    }
    pub fn open_read(&mut self, name: &[u8], cloexec: bool) -> Result<i32, S::Error> {
        self.open_read_in(0, name, cloexec)
    }
    #[cfg(fs_replace)]
    pub fn replace(&mut self, from: i32, to: i32) -> Result<i32, S::Error> {
        self.replace_in(0, from, to)
    }

    pub fn duplicate(&mut self, fd: i32, minimum: i32, cloexec: bool) -> Result<i32, S::Error> {
        self.duplicate_in(0, fd, minimum, cloexec)
    }
    pub fn position(&self, fd: i32) -> Result<u64, S::Error> {
        self.position_in(0, fd)
    }
    pub fn read(
        &mut self,
        fd: i32,
        length: usize,
        out: &mut [u8; MAX_READ],
    ) -> Result<usize, S::Error> {
        self.read_in(0, fd, length, out)
    }
    pub fn seek(&mut self, fd: i32, seek: Seek) -> Result<u64, S::Error> {
        self.seek_in(0, fd, seek)
    }
    pub fn close(&mut self, fd: i32) -> Result<(), S::Error> {
        self.close_in(0, fd)
    }
    pub fn set_close_on_exec(&mut self, fd: i32, value: bool) -> Result<(), S::Error> {
        self.set_close_on_exec_in(0, fd, value)
    }
    pub fn commit_exec_close(&mut self) -> Result<(), S::Error> {
        self.commit_exec_close_in(0)
    }

    pub(crate) fn disconnect_source(&mut self) -> Result<S::Cleanup, S::Error> {
        self.disconnect_with(|source| source.disconnect())
    }
    pub(crate) fn disconnect_with(
        &mut self,
        disconnect: impl FnOnce(&mut S) -> core::result::Result<S::Cleanup, S::Error>,
    ) -> Result<S::Cleanup, S::Error> {
        self.active()?;
        self.descriptors.fill([None; SLOTS]);
        self.descriptions.fill(None);
        let result = disconnect(&mut self.source);
        self.retired = true;
        result.map_err(|error| self.source_error(error))
    }
    /// Consuming source-specific disconnect; not native export/reclaim evidence.
    pub fn disconnect(mut self) -> Result<S::Cleanup, S::Error> {
        self.disconnect_source()
    }
}
