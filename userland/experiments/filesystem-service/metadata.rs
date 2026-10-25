// SPDX-License-Identifier: BSD-2-Clause
//! Private borrowed engine metadata. Values are observations, never authority.
use core::{ffi::c_void, ptr::NonNull};

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Node {
    pub object: u64,
    pub generation: u64,
    pub size: u64,
    pub mode: u64,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Time {
    pub seconds: i64,
    pub nanoseconds: u64,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Metadata {
    pub node: Node,
    pub parent: u64,
    pub links: u64,
    pub uid: u64,
    pub gid: u64,
    pub flags: u64,
    pub atime: Time,
    pub mtime: Time,
    pub ctime: Time,
    pub birthtime: Time,
}

const _: () = {
    assert!(core::mem::size_of::<Node>() == 32);
    assert!(core::mem::size_of::<Time>() == 16);
    assert!(core::mem::offset_of!(Time, nanoseconds) == 8);
    assert!(core::mem::size_of::<Metadata>() == 136);
    assert!(core::mem::align_of::<Metadata>() == 8);
    assert!(core::mem::offset_of!(Metadata, parent) == 32);
    assert!(core::mem::offset_of!(Metadata, links) == 40);
    assert!(core::mem::offset_of!(Metadata, uid) == 48);
    assert!(core::mem::offset_of!(Metadata, gid) == 56);
    assert!(core::mem::offset_of!(Metadata, flags) == 64);
    assert!(core::mem::offset_of!(Metadata, atime) == 72);
    assert!(core::mem::offset_of!(Metadata, mtime) == 88);
    assert!(core::mem::offset_of!(Metadata, ctime) == 104);
    assert!(core::mem::offset_of!(Metadata, birthtime) == 120);
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    InvalidInput,
    Backend(i32),
    InvalidCompletion,
    InvalidMetadata,
}

unsafe extern "C" {
    fn aether_zpl_getattr(
        view: *mut c_void,
        object: u64,
        generation: u64,
        out: *mut Metadata,
    ) -> i32;
}

/// Read an already authorized retained identity. No ownership is transferred.
///
/// # Safety
/// `view` must be a live exclusively borrowed original ZPL view with its SPA
/// borrow retained until return. The caller excludes reentry, all concurrent
/// view/dataset mutation, property changes, export and teardown. The linked C
/// function must implement the pinned136-byte ABI, write only the initialized
/// disjoint output and retain no pointer. Object/generation come from trusted
/// service-handle resolution, never raw client fields. This function neither
/// grants access nor translates FUIDs, credentials, ACLs or POSIX permission.
pub unsafe fn read(view: NonNull<c_void>, object: u64, generation: u64) -> Result<Metadata, Error> {
    if object == 0 || generation == 0 {
        return Err(Error::InvalidInput);
    }
    let mut value = Metadata::default();
    // SAFETY: caller retains the exclusive live view/SPA; this initialized local
    // output is disjoint, synchronous and never exposed on any failed result.
    let code = unsafe { aether_zpl_getattr(view.as_ptr(), object, generation, &mut value) };
    if code != 0 {
        return Err(if code > 0 {
            Error::Backend(code)
        } else {
            Error::InvalidCompletion
        });
    }
    if value.node.object != object
        || value.node.generation != generation
        || !matches!(value.node.mode & 0o170000, 0o040000 | 0o100000)
        || value.parent == 0
        || value.links == 0
        || value.flags & 1 != 0
        || [value.atime, value.mtime, value.ctime, value.birthtime]
            .iter()
            .any(|time| time.nanoseconds >= 1_000_000_000)
    {
        return Err(Error::InvalidMetadata);
    }
    Ok(value)
}
