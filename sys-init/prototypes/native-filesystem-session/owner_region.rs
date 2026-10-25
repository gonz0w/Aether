// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! A single boot-owned object/workspace partition, not an allocator or authority.
use core::mem::{MaybeUninit, align_of, size_of};
pub const BASE: usize = 0x900000;
pub const BYTES: usize = 8192;
pub const WORKSPACE: usize = 4096;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Binding,
    Bytes,
    Alignment,
    Dirty,
    Layout,
}
/// Inert validated entry metadata, not proof that a region is mapped or owned.
pub struct Binding {
    _private: (),
}
pub fn validate(entry: [u64; 8]) -> Result<Binding, Error> {
    validate_abi(entry, 30)
}
/// Explicit ABI31 stack profile only. Old ABI30 consumers remain exact.
pub fn validate_stack(entry: [u64; 8]) -> Result<Binding, Error> {
    validate_abi(entry, 31)
}
fn validate_abi(entry: [u64; 8], abi: u64) -> Result<Binding, Error> {
    if entry
        != [
            abi,
            0xa001,
            0xf101,
            0xc002,
            0xd001,
            0xc003,
            BASE as u64,
            BYTES as u64,
        ]
    {
        return Err(Error::Binding);
    }
    Ok(Binding { _private: () })
}
pub struct Region<'a> {
    bytes: &'a mut [MaybeUninit<u8>],
}
pub struct Slots<'a, T> {
    owner: &'a mut MaybeUninit<T>,
    workspace: &'a mut [u8; WORKSPACE],
    spare: &'a mut [u8],
}
pub struct Placed<'a, T> {
    pub owner: &'a mut T,
    pub workspace: &'a mut [u8; WORKSPACE],
    pub spare: &'a mut [u8],
}
impl<'a> Region<'a> {
    /// The exclusive storage borrow supplies local authority. Initialize bytes
    /// explicitly; retain MaybeUninit backing because T writes may uninitialize
    /// padding. This does not check a native producer's zeroing guarantee.
    pub fn from_storage(bytes: &'a mut [MaybeUninit<u8>]) -> Result<Self, Error> {
        check_layout(bytes.as_ptr() as usize, bytes.len())?;
        for byte in bytes.iter_mut() {
            byte.write(0);
        }
        Ok(Self { bytes })
    }
    /// Validate before obtaining a typed slot or constructing any owner value.
    pub fn partition<T: 'a>(self) -> Result<Slots<'a, T>, Error> {
        let size = size_of::<T>();
        if size == 0 || size > BYTES - WORKSPACE || align_of::<T>() > 4096 {
            return Err(Error::Layout);
        }
        let (head, rest) = self.bytes.split_at_mut(size);
        let (workspace, spare) = rest.split_at_mut(WORKSPACE);
        // SAFETY: page-aligned exclusive head covers exactly size_of<T> bytes;
        // alignment was checked above. MaybeUninit<T> accepts arbitrary bytes.
        // Head is never used again; split_at_mut makes other regions disjoint.
        let owner = unsafe { &mut *head.as_mut_ptr().cast::<MaybeUninit<T>>() };
        // SAFETY: from_storage initialized all these bytes to zero; neither
        // disjoint tail has been exposed as T or had padding invalidated.
        let workspace = unsafe { &mut *workspace.as_mut_ptr().cast::<[u8; WORKSPACE]>() };
        // SAFETY: same initialized disjoint tail, preserving its exact length.
        let spare = unsafe {
            core::slice::from_raw_parts_mut(spare.as_mut_ptr().cast::<u8>(), spare.len())
        };
        Ok(Slots {
            owner,
            workspace,
            spare,
        })
    }
}
impl<'a, T> Slots<'a, T> {
    /// Consume the partition for field-wise construction in its original slot.
    /// MaybeUninit exposes no T reference before the owner initializer writes it.
    pub fn into_parts(
        self,
    ) -> (
        &'a mut MaybeUninit<T>,
        &'a mut [u8; WORKSPACE],
        &'a mut [u8],
    ) {
        (self.owner, self.workspace, self.spare)
    }
    /// Consumes the only slot. A valid T is written before its reference exists.
    /// No automatic T/resource destruction is implied on owner/VM termination.
    pub fn initialize(self, value: T) -> Placed<'a, T> {
        Placed {
            owner: self.owner.write(value),
            workspace: self.workspace,
            spare: self.spare,
        }
    }
}
fn check_layout(address: usize, length: usize) -> Result<(), Error> {
    if length != BYTES {
        return Err(Error::Bytes);
    }
    if !address.is_multiple_of(4096) {
        return Err(Error::Alignment);
    }
    Ok(())
}
/// Check initialized bytes before granting any typed view. This is an observation,
/// not memory authority, and must precede any writes that can invalidate padding.
pub fn check_zeroed(bytes: &[u8]) -> Result<(), Error> {
    check_layout(bytes.as_ptr() as usize, bytes.len())?;
    if bytes.iter().any(|byte| *byte != 0) {
        return Err(Error::Dirty);
    }
    Ok(())
}
/// # Safety
/// Only the actual selected ABI30/31 boot owner may call, once, after capturing initial entry
/// scalars. The kernel must have supplied the unique mapped zeroed RW/NX region
/// under the pinned contract, alive until VM termination. No alias, second call,
/// unmap/restart or unrelated process is permitted. Binding alone is not authority.
pub unsafe fn claim(_: Binding) -> Result<Region<'static>, Error> {
    // SAFETY: exactly the caller's boot provenance/lifetime/exclusivity obligation.
    let bytes = unsafe { core::slice::from_raw_parts_mut(BASE as *mut u8, BYTES) };
    check_zeroed(bytes)?;
    // SAFETY: same exclusive mapped region after the initialized byte check.
    // Retain backing as MaybeUninit so typed owner padding is never read as u8.
    let storage = unsafe { core::slice::from_raw_parts_mut(BASE as *mut MaybeUninit<u8>, BYTES) };
    Region::from_storage(storage)
}
