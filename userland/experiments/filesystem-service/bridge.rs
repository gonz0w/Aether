// SPDX-License-Identifier: BSD-2-Clause
//! Private synchronous original-engine bridge. No RPC or SPA creation API.
#![no_std]
#[cfg(fs_mixed)]
#[path = "mixed-bridge.rs"]
mod mixed_bridge;
#[cfg(fs_namespace)]
#[path = "namespace-bridge.rs"]
mod namespace_bridge;

use core::{
    ffi::{c_char, c_void, CStr},
    marker::PhantomData,
    ptr::NonNull,
};
pub use filesystem_policy as policy;
use policy::{Backend, Clock, Completion, Error, Kind, Lost, Node, Utc, MAX_READ};

#[repr(C)]
#[derive(Default)]
struct RawNode {
    object: u64,
    generation: u64,
    size: u64,
    mode: u64,
}
#[repr(C)]
#[derive(Default)]
struct RawWrite {
    txg: u64,
    bytes_staged: u64,
    state: u64,
}
#[repr(C)]
#[derive(Default)]
struct Timespec {
    seconds: i64,
    nanoseconds: i64,
}

const _: () = {
    assert!(core::mem::size_of::<RawNode>() == 32);
    assert!(core::mem::align_of::<RawNode>() == 8);
    assert!(core::mem::offset_of!(RawNode, mode) == 24);
    assert!(core::mem::size_of::<RawWrite>() == 24);
    assert!(core::mem::align_of::<RawWrite>() == 8);
    assert!(core::mem::offset_of!(RawWrite, bytes_staged) == 8);
    assert!(core::mem::offset_of!(RawWrite, state) == 16);
    assert!(core::mem::size_of::<Timespec>() == 16);
    assert!(core::mem::align_of::<Timespec>() == 8);
};

unsafe extern "C" {
    fn aether_zpl_open_write(
        spa: *mut c_void,
        dataset: *const c_char,
        out: *mut *mut c_void,
    ) -> i32;
    fn aether_zpl_close(owned: *mut *mut c_void);
    fn aether_zpl_root(view: *mut c_void, out: *mut RawNode) -> i32;
    fn aether_zpl_lookup(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        name: *const u8,
        length: usize,
        out: *mut RawNode,
    ) -> i32;
    fn aether_zpl_read(
        view: *mut c_void,
        object: u64,
        generation: u64,
        offset: u64,
        buffer: *mut u8,
        length: usize,
        count: *mut usize,
    ) -> i32;
    fn aether_zpl_write(
        view: *mut c_void,
        object: u64,
        generation: u64,
        offset: u64,
        buffer: *const u8,
        length: usize,
        seconds: u64,
        nanoseconds: u64,
        out: *mut RawWrite,
    ) -> i32;
    fn aether_utc_read(out: *mut Timespec) -> i32;
    #[cfg(all(fs_lifetimes, not(fs_bulk)))]
    fn aether_pool_service16_retire(error: i32, target: u64, staged: u64, state: u64) -> i32;
}

fn status(code: i32) -> Result<(), Error> {
    match code {
        0 => Ok(()),
        1.. => Err(Error::Backend(code)),
        _ => Err(Error::InvalidCompletion),
    }
}

fn node(raw: RawNode) -> Result<Node, Error> {
    let kind = match raw.mode & 0o170000 {
        0o040000 => Kind::Directory,
        0o100000 => Kind::File,
        _ => return Err(Error::InvalidMetadata),
    };
    if raw.object == 0 || raw.generation == 0 {
        return Err(Error::InvalidMetadata);
    }
    Ok(Node::new(raw.object, raw.generation, raw.size, kind))
}

/// Uniquely borrowed engine owner state, not a client-selected capability.
/// NonNull and the exclusive lifetime prevent auto-Send/Sync and duplication.
pub struct Spa<'spa> {
    pointer: NonNull<c_void>,
    _borrow: PhantomData<&'spa mut c_void>,
}

impl<'spa> Spa<'spa> {
    /// # Safety
    /// The pointer is a live exclusively borrowed writable SPA for all of 'spa.
    /// Its original accounting callback is registered before import; the linked
    /// functions implement the pinned ABI, including valid owned nonnull context
    /// outputs and consuming close. Exclude external mutation, import/export,
    /// property changes and teardown until every derived context has been closed.
    /// Creating a second overlapping Spa token or choosing an untrusted pointer
    /// violates this contract. This function neither initializes nor grants a SPA.
    pub unsafe fn from_raw(pointer: NonNull<c_void>) -> Self {
        Self {
            pointer,
            _borrow: PhantomData,
        }
    }

    /// Dataset is trusted owner configuration, not a deserialized client path.
    /// Only one context can borrow this token at a time, including on errors.
    pub fn open<'context>(
        &'context mut self,
        dataset: &'context CStr,
    ) -> Result<Zpl<'context>, Error> {
        let mut raw = core::ptr::null_mut();
        // SAFETY: constructor guarantees live exclusive SPA; CStr is terminated,
        // output is initialized and separate; neither input borrow may escape C.
        let code =
            unsafe { aether_zpl_open_write(self.pointer.as_ptr(), dataset.as_ptr(), &mut raw) };
        let owned = NonNull::new(raw).map(|pointer| Zpl {
            pointer,
            _spa: PhantomData,
            #[cfg(all(fs_namespace, not(fs_mixed)))]
            namespace_used: false,
            #[cfg(fs_lifetimes)]
            spa: self.pointer,
            #[cfg(fs_lifetimes)]
            dataset,
            #[cfg(fs_lifetimes)]
            consumed: false,
            #[cfg(fs_lifetimes)]
            writes: 0,
        });
        status(code)?; // Drops any valid owned output even on provider error.
        owned.ok_or(Error::InvalidCompletion)
    }
}

pub struct Zpl<'context> {
    #[cfg(all(fs_namespace, not(fs_mixed)))]
    namespace_used: bool,
    pointer: NonNull<c_void>,
    _spa: PhantomData<&'context mut c_void>,
    #[cfg(fs_lifetimes)]
    spa: NonNull<c_void>,
    #[cfg(fs_lifetimes)]
    dataset: &'context CStr,
    #[cfg(fs_lifetimes)]
    consumed: bool,
    #[cfg(fs_lifetimes)]
    writes: policy::MutationCount,
}

impl Drop for Zpl<'_> {
    fn drop(&mut self) {
        #[cfg(fs_lifetimes)]
        if self.consumed {
            return;
        }
        let mut raw = self.pointer.as_ptr();
        // SAFETY: unique context, no call in flight, SPA token remains borrowed.
        // The pinned close consumes/nulls the context before returning.
        unsafe { aether_zpl_close(&mut raw) };
        // Deliberate fail-stop on ABI violation; native builds use panic=abort.
        assert!(raw.is_null(), "ZPL close did not consume context");
    }
}

#[cfg(fs_mixed)]
impl policy::CreatingBackend for Zpl<'_> {
    fn create_identity(
        &mut self,
        parent: Node,
        creation: policy::Creation<'_>,
        identity: policy::Identity,
        utc: Utc,
    ) -> Result<policy::CreatedMutation, Lost> {
        self.create_with_identity(parent, creation, identity, utc)
    }
}

impl Backend for Zpl<'_> {
    #[cfg(fs_directory_contexts)]
    fn directory_context(
        &mut self,
        root: Node,
        directory: Node,
        out: &mut [u8; 256],
    ) -> Result<(Node, usize), Error> {
        self.read_directory_context(root, directory, out)
    }

    #[cfg(fs_metadata)]
    fn metadata(&mut self, node: Node) -> Result<policy::Metadata, Error> {
        if self.consumed {
            return Err(Error::Closed);
        }
        let (object, generation) = node.identity();
        // SAFETY: this exclusive live context retains its SPA borrow; policy
        // supplies an authorized retained identity. No operation/property change,
        // export or teardown overlaps this synchronous borrowed getter. The
        // separate metadata crate uses the pinned initialized136-byte C ABI.
        unsafe { filesystem_metadata::read(self.pointer, object, generation) }.map_err(|error| {
            match error {
                filesystem_metadata::Error::Backend(code) => Error::Backend(code),
                filesystem_metadata::Error::InvalidCompletion => Error::InvalidCompletion,
                _ => Error::InvalidMetadata,
            }
        })
    }
    #[cfg(fs_directories)]
    fn directory(&mut self, directory: Node) -> Result<Node, Error> {
        self.refresh_directory(directory)
    }
    #[cfg(fs_namespace)]
    fn mutate(
        &mut self,
        directory: Node,
        operation: policy::Namespace<'_>,
        utc: Utc,
    ) -> Result<Completion, Lost> {
        self.namespace_mutation(directory, operation, utc)
    }

    fn root(&mut self) -> Result<Node, Error> {
        #[cfg(fs_lifetimes)]
        if self.consumed {
            return Err(Error::Closed);
        }
        let mut raw = RawNode::default();
        // SAFETY: sole live context and separate initialized writable output.
        status(unsafe { aether_zpl_root(self.pointer.as_ptr(), &mut raw) })?;
        node(raw)
    }

    fn lookup(&mut self, directory: Node, name: &[u8]) -> Result<Node, Error> {
        #[cfg(fs_lifetimes)]
        if self.consumed {
            return Err(Error::Closed);
        }
        if name.is_empty()
            || name.len() > 255
            || name == b"."
            || name == b".."
            || name.contains(&0)
            || name.contains(&b'/')
        {
            return Err(Error::Invalid);
        }
        let (object, generation) = directory.identity();
        let mut raw = RawNode::default();
        // SAFETY: live unique context; exact initialized slice and nonaliasing
        // output stay alive throughout the synchronous call. No pointer retained.
        status(unsafe {
            aether_zpl_lookup(
                self.pointer.as_ptr(),
                object,
                generation,
                name.as_ptr(),
                name.len(),
                &mut raw,
            )
        })?;
        node(raw)
    }

    fn read(&mut self, file: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error> {
        buffer.fill(0);
        #[cfg(fs_lifetimes)]
        if self.consumed {
            return Err(Error::Closed);
        }
        if buffer.len() > MAX_READ || offset.checked_add(buffer.len() as u64).is_none() {
            return Err(Error::Invalid);
        }
        let (object, generation) = file.identity();
        let mut count = 0;
        // SAFETY: borrowed context, initialized writable exact slice and separate
        // count; no overlap/retention; mutable borrow prevents concurrent calls.
        let code = unsafe {
            aether_zpl_read(
                self.pointer.as_ptr(),
                object,
                generation,
                offset,
                buffer.as_mut_ptr(),
                buffer.len(),
                &mut count,
            )
        };
        if let Err(error) = status(code) {
            buffer.fill(0);
            return Err(error);
        }
        if count > buffer.len() {
            buffer.fill(0);
            return Err(Error::InvalidCompletion);
        }
        buffer[count..].fill(0);
        Ok(count)
    }

    fn write(
        &mut self,
        file: Node,
        offset: u64,
        bytes: &[u8],
        utc: Utc,
    ) -> Result<Completion, Lost> {
        if bytes.len() > MAX_READ
            || offset > i64::MAX as u64
            || bytes.len() as u64 > i64::MAX as u64 - offset
            || utc.seconds > i64::MAX as u64
            || utc.nanoseconds >= 1_000_000_000
        {
            return Ok(Completion {
                error: 22,
                txg: 0,
                bytes_staged: 0,
                state: 0,
            });
        }
        #[cfg(fs_lifetimes)]
        {
            if self.consumed
                || self.writes == policy::MUTATION_LIMIT
                || (if cfg!(fs_bulk) {
                    bytes.is_empty()
                } else {
                    bytes.len() != 16
                })
            {
                return Ok(Completion {
                    error: 28,
                    txg: 0,
                    bytes_staged: 0,
                    state: 0,
                });
            }
            self.writes += 1;
        }
        #[cfg(all(fs_namespace, not(fs_mixed)))]
        if core::mem::replace(&mut self.namespace_used, true) {
            return Ok(Completion {
                error: 28,
                txg: 0,
                bytes_staged: 0,
                state: 0,
            });
        }
        let (object, generation) = file.identity();
        let mut raw = RawWrite::default();
        // SAFETY: live sole context; exact initialized readable bytes and distinct
        // initialized output stay valid through C. UTC is owner policy, not a
        // request field. C cannot retain a pointer or unwind into Rust.
        let error = unsafe {
            aether_zpl_write(
                self.pointer.as_ptr(),
                object,
                generation,
                offset,
                bytes.as_ptr(),
                bytes.len(),
                utc.seconds,
                utc.nanoseconds,
                &mut raw,
            )
        };
        #[cfg(all(fs_lifetimes, not(fs_mixed)))]
        let error = if error == 0 && raw.txg != 0 && raw.state == 2 && raw.bytes_staged == 16 {
            self.finish_synced16(file, offset, bytes, &raw)
        } else {
            error
        };
        #[cfg(fs_mixed)]
        let error = if error == 0
            && raw.txg != 0
            && raw.state == 2
            && raw.bytes_staged
                == if cfg!(fs_bulk) {
                    bytes.len() as u64
                } else {
                    16
                } {
            self.finish_mixed(&raw, Some((file, offset, bytes)))
        } else {
            error
        };
        Ok(Completion {
            error,
            txg: raw.txg,
            bytes_staged: raw.bytes_staged,
            state: raw.state,
        })
    }
}

#[cfg(all(fs_lifetimes, not(fs_mixed)))]
impl Zpl<'_> {
    // Return an overall post-write error with the original SYNCED progress intact.
    // Every failure leaves the consumed flag permanent; Owner retires all aliases.
    fn finish_synced16(&mut self, file: Node, offset: u64, bytes: &[u8], raw: &RawWrite) -> i32 {
        let mut check = [0u8; 16];
        let verified = matches!(self.read(file, offset, &mut check), Ok(16)) && check == bytes;
        let mut owned = self.pointer.as_ptr();
        self.consumed = true;
        // SAFETY: sole live context, no read/write borrow remains. SPA and dataset
        // remain exclusively retained. Original close must consume and null it.
        unsafe { aether_zpl_close(&mut owned) };
        assert!(owned.is_null(), "ZPL close did not consume context");
        if !verified {
            return 5;
        }
        // SAFETY: exact original successful outcome, consumed context and no call
        // in flight. The selected trusted producer excludes observer borrows and
        // preserves all permanent errors/epochs/device identity; no pointer RPC.
        let retired =
            unsafe { aether_pool_service16_retire(0, raw.txg, raw.bytes_staged, raw.state) };
        if retired != 0 {
            return if retired > 0 { retired } else { 5 };
        }
        let mut next = core::ptr::null_mut();
        // SAFETY: same retained live SPA and immutable NUL dataset, initialized
        // separate output. Reopen only after successful consuming retirement.
        let reopened =
            unsafe { aether_zpl_open_write(self.spa.as_ptr(), self.dataset.as_ptr(), &mut next) };
        if reopened != 0 || next.is_null() {
            if !next.is_null() {
                // SAFETY: consume the sole valid owned error output once.
                unsafe { aether_zpl_close(&mut next) };
                assert!(next.is_null(), "ZPL error close did not consume context");
            }
            return if reopened > 0 { reopened } else { 5 };
        }
        self.pointer = NonNull::new(next).unwrap();
        self.consumed = false;
        0
    }
}

/// Reads an already-established shared runtime UTC anchor, without reset or
/// close authority. Service bootstrap owns policy selection and anchor lifetime.
pub struct RuntimeUtc;
impl Clock for RuntimeUtc {
    fn utc(&mut self) -> Result<Utc, Error> {
        let mut raw = Timespec::default();
        // SAFETY: linked pinned reader accepts this separate initialized output,
        // retains no pointer and explicitly fails if its anchor is unavailable.
        let code = unsafe { aether_utc_read(&mut raw) };
        if code != 0 || raw.seconds < 0 || !(0..1_000_000_000).contains(&raw.nanoseconds) {
            return Err(Error::Clock);
        }
        Ok(Utc {
            seconds: raw.seconds as u64,
            nanoseconds: raw.nanoseconds as u64,
        })
    }
}

#[cfg(test)]
extern crate std;
#[cfg(all(test, not(fs_runtime)))]
#[path = "bridge-tests.rs"]
mod tests;

#[cfg(all(test, fs_runtime))]
#[path = "runtime-bridge-tests.rs"]
mod tests;

#[cfg(fs_directories)]
#[path = "directory-bridge.rs"]
mod directories;

#[cfg(fs_directory_contexts)]
#[path = "directory-context-bridge.rs"]
mod directory_context;
