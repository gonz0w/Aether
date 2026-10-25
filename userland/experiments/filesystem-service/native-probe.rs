// SPDX-License-Identifier: BSD-2-Clause
//! Unselected private producer callback; never a client entry or full oracle.
#![no_std]
use core::{ffi::c_void, ptr::NonNull};
use filesystem_bridge::{
    policy::{Error, Owner, Rights, MAX_READ},
    RuntimeUtc, Spa,
};

/// Private callback progress:0 unassigned,1 committed,2 synced,3 uncertain.
/// No state is a public durability acknowledgment.
#[repr(C)]
#[derive(Default)]
pub struct ProbeResult {
    pub txg: u64,
    pub bytes_staged: u64,
    pub state: u64,
}
const _: () = assert!(core::mem::size_of::<ProbeResult>() == 24);

fn exercise(spa: &mut Spa<'_>, progress: &mut ProbeResult) -> Result<(), Error> {
    let name = c"testpool_zstd/x86_64";
    let mut owner = Owner::new(spa.open(name)?, RuntimeUtc, 1)?;
    // Fixed internal test principals, NOT native transport authentication.
    let a = owner.attach(71, Rights::ALL)?;
    let b = owner.attach(72, Rights::new(3)?)?;
    let writer = owner.lookup(71, a.session, a.root.handle, b"zstd", Rights::WRITE)?;
    let alias = owner.lookup(72, b.session, b.root.handle, b"zstd", Rights::READ)?;
    if writer.size != 780248 || alias.size != writer.size {
        return Err(Error::InvalidMetadata);
    }
    let bytes = core::array::from_fn::<_, 16, _>(|i| (i * 17 + 91) as u8);
    if owner.write(72, b.session, writer.handle, 37, &bytes) != Err(Error::Denied) {
        return Err(Error::InvalidCompletion);
    }
    let result = match owner.write(71, a.session, writer.handle, 37, &bytes) {
        Ok(value) => value,
        Err(Error::WriteFailed(completion)) => {
            *progress = ProbeResult {
                txg: completion.txg,
                bytes_staged: completion.bytes_staged,
                state: completion.state,
            };
            return Err(Error::WriteFailed(completion));
        }
        Err(error @ (Error::Uncertain | Error::InvalidCompletion)) => {
            progress.state = 3;
            return Err(error);
        }
        Err(error) => return Err(error),
    };
    *progress = ProbeResult {
        txg: result.assigned_txg.ok_or(Error::InvalidCompletion)?,
        bytes_staged: result.bytes as u64,
        state: 2,
    };
    if result.bytes != bytes.len() {
        return Err(Error::InvalidCompletion);
    }
    let mut out = [0; MAX_READ];
    if owner.read(72, b.session, alias.handle, 37, bytes.len(), &mut out)? != bytes.len()
        || out[..bytes.len()] != bytes
        || out[bytes.len()..].iter().any(|b| *b != 0)
        || owner.stat(72, b.session, alias.handle)?.size != 780248
    {
        return Err(Error::InvalidCompletion);
    }
    owner.shutdown();
    Ok(())
}

/// # Safety
/// Proposed private engine-owner callback only: exclusive writable live SPA,
/// accounting registered before import, shared UTC established and retained,
/// one unused ordered transaction slot, no external context/property/teardown
/// access. progress is separate writable initialized ProbeResult storage. Caller must
/// retain its full pre/post-file hash, ordered close/drain/export, media guards
/// and fresh-VM readback oracles. This callback itself is NOT those oracles.
#[no_mangle]
pub unsafe extern "C" fn aether_fs_policy_write_probe(
    spa: *mut c_void,
    progress: *mut ProbeResult,
) -> i32 {
    let Some(mut progress) = NonNull::new(progress) else {
        return 22;
    };
    // SAFETY: caller retains separate valid exclusive output through return.
    unsafe {
        *progress.as_mut() = ProbeResult::default();
    }
    let Some(pointer) = NonNull::new(spa) else {
        return 22;
    };
    // SAFETY: caller retains all engine obligations until consuming context close.
    let mut borrowed = unsafe { Spa::from_raw(pointer) };
    // SAFETY: the separate progress output remains uniquely writable throughout.
    match exercise(&mut borrowed, unsafe { progress.as_mut() }) {
        Ok(()) => 0,
        Err(Error::Backend(code)) => code,
        Err(Error::WriteFailed(completion)) => completion.error,
        Err(_) => 5,
    }
}
