// SPDX-License-Identifier: BSD-2-Clause
//! Native engine entry for the bounded service; requires matched provisioning.
#![no_std]
#[cfg(not(test))]
use core::arch::asm;
use core::{ffi::c_void, ptr::NonNull};
use filesystem_bridge::{
    policy::{Error, Owner, Rights},
    RuntimeUtc, Spa,
};
use filesystem_service::{
    channel::{Framed, Io},
    Stop,
};

/// Selected private native channel trap, derived from pinned namespace-channel.
/// # Safety
/// Pointer arguments must name initialized, live, nonaliasing storage of the
/// exact requested extent through this synchronous call; kernel retains none.
unsafe fn trap(op: u64, a: u64, b: u64, c: u64) -> i64 {
    #[cfg(test)]
    // SAFETY: tests substitute a synchronous checked host transport; the same
    // caller-owned slice obligations apply, and no real native trap is executed.
    unsafe {
        tests::trap(op, a, b, c)
    }
    #[cfg(not(test))]
    {
        let result: i64;
        // SAFETY: selected x86-64 profile uses int81, validates holder/direction and
        // copies at most16 bytes. Registers and memory effects match pinned adapter.
        unsafe {
            asm!("int 0x81", inlateout("rax") op => result, in("rdi") a,
             in("rsi") b, inlateout("rdx") c => _,
             inlateout("r10") 0u64 => _, inlateout("r8") 0u64 => _,
             inlateout("r9") 0u64 => _, lateout("rcx") _, lateout("r11") _);
        }
        result
    }
}

struct Endpoints {
    reader: u64,
    writer: u64,
    closed: bool,
}
impl Io for Endpoints {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        // SAFETY: Framed supplies live initialized exclusive slices<=16 bytes.
        // Tokens are retained bootstrap bindings; the trap enforces holders.
        unsafe {
            trap(
                if writing { 0x24002 } else { 0x24001 },
                if writing { self.writer } else { self.reader },
                bytes.as_mut_ptr() as u64,
                bytes.len() as u64,
            )
        }
    }
    #[cfg(not(fs_wait))]
    fn yield_now(&mut self) {
        // SAFETY: scalar yield operation, no pointers or retained references.
        unsafe { trap(0x1fffe, 0, 0, 0) };
    }
    #[cfg(fs_wait)]
    fn wait(&mut self, writing: bool) -> i64 {
        // SAFETY: ABI26 scalar holder-scoped primary wait; no pointer survives
        // the completed transfer. Wake is only a hint, not transferred bytes.
        unsafe {
            trap(
                0x24004,
                if writing { self.writer } else { self.reader },
                0,
                0,
            )
        }
    }
    fn close(&mut self) -> [i64; 2] {
        if self.closed {
            return [-9, -9];
        }
        self.closed = true;
        // SAFETY: both scalar tokens owned by this instance, no pending I/O.
        unsafe {
            [
                trap(0x24003, self.reader, 0, 0),
                trap(0x24003, self.writer, 0, 0),
            ]
        }
    }
}
impl Drop for Endpoints {
    fn drop(&mut self) {
        if !self.closed {
            let _ = self.close();
        }
    }
}

#[repr(C)]
#[derive(Default)]
pub struct ServiceResult {
    pub ready: u64,
    pub requests: u64,
    /// 0 disconnect,1 receive,2 reply loss,3 budget,4 provision,5 retired.
    pub stop: u64,
    pub reader_close: i64,
    pub writer_close: i64,
    pub error: i64,
    pub txg: u64,
    pub bytes_staged: u64,
    pub state: u64,
}
const _: () = assert!(core::mem::size_of::<ServiceResult>() == 72);
const _: () = assert!(core::mem::align_of::<ServiceResult>() == 8);
const _: () = assert!(core::mem::offset_of!(ServiceResult, txg) == 48);

/// # Safety
/// Trusted importer only, NOT a client RPC. SPA satisfies Spa::from_raw's
/// exclusive live writable/accounted import contract; shared UTC is established.
/// One unused ordered transaction slot is reserved; this entry does not retire
/// observer history or authorize a replacement/replay after an unknown outcome.
/// dataset denotes1..255 initialized bytes with no NUL followed by one NUL and
/// remains immutable through return. out is separate aligned writable storage.
/// reader/writer are uniquely retained native request-reader/reply-writer tokens
/// with their counterpart holders provisioned to the sole authenticated client.
/// Their nonreused request token is this service generation. No concurrent/reentrant
/// calls, teardown or external mutation. Code and engine stay resident through
/// original ordered drain/export/kernel_fini. Caller retains full independent
/// data/hash/metadata/recovery and cleanup oracles; result is NOT durability.
#[cfg(not(fs_namespace))]
#[no_mangle]
pub unsafe extern "C" fn aether_fs_service_run(
    spa: *mut c_void,
    dataset: *const u8,
    length: usize,
    reader: u64,
    writer: u64,
    rights: u64,
    out: *mut ServiceResult,
) -> i32 {
    // SAFETY: this wrapper forwards the same documented trusted importer contract.
    unsafe { entry(spa, dataset, length, reader, writer, rights, out) }
}

/// Trusted namespace importer. In addition to the base entry's pointer/SPA,
/// endpoint and serialization obligations, uid/gid are immutable trusted labels
/// <=INT32_MAX, never client-selected authority. One namespace attempt, no reuse.
/// # Safety
/// All base importer obligations apply; original C context close consumes/nulls.
#[cfg(all(fs_namespace, not(fs_mixed)))]
#[no_mangle]
pub unsafe extern "C" fn aether_fs_namespace_run(
    spa: *mut c_void,
    dataset: *const u8,
    length: usize,
    reader: u64,
    writer: u64,
    rights: u64,
    uid: u64,
    gid: u64,
    out: *mut ServiceResult,
) -> i32 {
    // SAFETY: trusted caller retains the documented independent live inputs.
    unsafe { entry(spa, dataset, length, reader, writer, rights, uid, gid, out) }
}

/// Trusted namespace importer. In addition to the base entry's pointer/SPA,
/// endpoint and serialization obligations, uid/gid are immutable trusted labels
/// <=INT32_MAX, never client-selected authority. The selected finite/runtime lifetime applies; original contexts retire before reuse.
/// # Safety
/// All base importer obligations apply; original C context close consumes/nulls.
#[cfg(fs_mixed)]
#[cfg_attr(not(fs_wait), no_mangle)]
#[cfg_attr(all(fs_wait, not(fs_bulk)), export_name = "aether_fs_mixed_wait_run")]
#[cfg_attr(all(fs_bulk, not(fs_runtime)), export_name = "aether_fs_bulk_run")]
#[cfg_attr(
    all(fs_runtime, not(fs_activation)),
    export_name = "aether_fs_runtime_run"
)]
#[cfg_attr(
    all(fs_activation, not(fs_names)),
    export_name = "aether_fs_activation_run"
)]
#[cfg_attr(
    all(fs_names, not(fs_directories)),
    export_name = "aether_fs_names_run"
)]
#[cfg_attr(
    all(fs_directories, not(fs_metadata)),
    export_name = "aether_fs_directories_run"
)]
#[cfg_attr(fs_metadata, export_name = "aether_fs_metadata_run")]
pub unsafe extern "C" fn aether_fs_mixed_run(
    spa: *mut c_void,
    dataset: *const u8,
    length: usize,
    reader: u64,
    writer: u64,
    rights: u64,
    uid: u64,
    gid: u64,
    out: *mut ServiceResult,
) -> i32 {
    // SAFETY: trusted caller retains the documented independent live inputs.
    unsafe { entry(spa, dataset, length, reader, writer, rights, uid, gid, out) }
}

#[cfg_attr(
    fs_namespace,
    allow(
        clippy::too_many_arguments,
        reason = "Mirrors the nine-field private C namespace ABI."
    )
)]
unsafe fn entry(
    spa: *mut c_void,
    dataset: *const u8,
    length: usize,
    reader: u64,
    writer: u64,
    rights: u64,
    #[cfg(fs_namespace)] uid: u64,
    #[cfg(fs_namespace)] gid: u64,
    out: *mut ServiceResult,
) -> i32 {
    let Some(mut out) = NonNull::new(out) else {
        return 22;
    };
    // SAFETY: trusted caller provides exclusive valid separate result storage.
    unsafe {
        *out.as_mut() = ServiceResult::default();
        out.as_mut().stop = 4;
        out.as_mut().reader_close = -9;
        out.as_mut().writer_close = -9;
        out.as_mut().error = -22;
    }
    // Invalid scalar provisioning acquires no endpoint/context obligation.
    if reader & 0xff != 1
        || writer & 0xff != 2
        || reader >> 16 == 0
        || writer >> 16 == 0
        || reader >> 16 == writer >> 16
        || dataset.is_null()
        || length == 0
        || length > 255
        || spa.is_null()
    {
        return 22;
    }
    // SAFETY: caller guarantees length+1 live immutable bytes, bounded above.
    let bytes = unsafe { core::slice::from_raw_parts(dataset, length + 1) };
    let Ok(name) = core::ffi::CStr::from_bytes_with_nul(bytes) else {
        return 22;
    };
    let Ok(rights) = u8::try_from(rights)
        .map_err(|_| Error::Invalid)
        .and_then(Rights::new)
    else {
        return 22;
    };
    #[cfg(fs_namespace)]
    let Ok(identity) = filesystem_bridge::policy::Identity::new(uid, gid) else {
        return 22;
    };
    let mut endpoints = Endpoints {
        reader,
        writer,
        closed: false,
    };
    // SAFETY: nonnull checked, caller retains exclusive writable SPA obligations.
    let mut spa = unsafe { Spa::from_raw(NonNull::new(spa).unwrap()) };
    let setup = spa.open(name).and_then(|backend| {
        let owner = Owner::new(backend, RuntimeUtc, reader)?;
        #[cfg(fs_namespace)]
        let owner = owner.with_namespace_identity(identity);
        Ok(owner)
    });
    let report = match setup {
        Ok(owner) => run(owner, Framed(endpoints), reader, rights, reader),
        Err(error) => {
            let closes = endpoints.close();
            // SAFETY: same separate exclusively borrowed output remains valid.
            unsafe {
                out.as_mut().stop = 4;
                out.as_mut().reader_close = closes[0];
                out.as_mut().writer_close = closes[1];
                out.as_mut().error = match error {
                    Error::Backend(code) if code > 0 => -i64::from(code),
                    _ => -5,
                };
            }
            return match error {
                Error::Backend(code) if code > 0 => code,
                _ => 5,
            };
        }
    };
    let stop = match report.stop {
        Stop::Disconnected => 0,
        Stop::Receive(_) => 1,
        Stop::ReplyLost(_) => 2,
        Stop::Limit => 3,
        Stop::Provision(_) => 4,
        Stop::Retired => 5,
        #[cfg(fs_namespace)]
        Stop::NamespaceComplete => 6,
    };
    // SAFETY: sole output borrow, no references or pointers retained on return.
    unsafe {
        let output = out.as_mut();
        output.ready = u64::from(report.ready);
        output.requests = report.requests as u64;
        output.stop = stop;
        output.reader_close = report.cleanup[0];
        output.writer_close = report.cleanup[1];
        output.error = match report.stop {
            Stop::Receive(code) | Stop::ReplyLost(code) => code,
            Stop::Limit => -28,
            Stop::Provision(_) => -22,
            Stop::Retired => -5,
            #[cfg(fs_namespace)]
            Stop::NamespaceComplete => report
                .cleanup
                .iter()
                .copied()
                .find(|code| *code != 0)
                .unwrap_or(0),
            Stop::Disconnected => report
                .cleanup
                .iter()
                .copied()
                .find(|code| *code != 0)
                .unwrap_or(0),
        };
        if let Some(progress) = report.last_write {
            output.txg = progress.txg;
            output.bytes_staged = progress.bytes_staged;
            output.state = progress.state;
        }
    }
    if (stop == 0 || (cfg!(fs_namespace) && stop == 6)) && report.cleanup == [0, 0] {
        0
    } else {
        5
    }
}

#[cfg(test)]
extern crate std;
#[cfg(all(test, not(fs_lifetimes), not(fs_namespace)))]
#[path = "native-service-tests.rs"]
mod tests;
#[cfg(all(test, fs_lifetimes, not(fs_namespace)))]
#[path = "lifetime-service-tests.rs"]
mod tests;

#[cfg(all(test, fs_namespace, not(fs_mixed)))]
#[path = "namespace-service-tests.rs"]
mod tests;
#[cfg(all(test, fs_mixed, not(fs_bulk)))]
#[path = "mixed-service-tests.rs"]
mod tests;

#[cfg(all(test, fs_bulk, not(fs_runtime)))]
#[path = "bulk-service-tests.rs"]
mod tests;

#[cfg(all(test, fs_runtime, not(fs_directories)))]
#[path = "runtime-service-tests.rs"]
mod tests;

#[cfg(all(fs_activation, not(fs_runtime)))]
compile_error!("fs_activation requires the separate runtime lifetime selection");
#[cfg(not(fs_activation))]
use filesystem_service::run;

#[cfg(fs_activation)]
fn run<
    B: filesystem_bridge::policy::Backend,
    C: filesystem_bridge::policy::Clock,
    T: filesystem_service::Channel,
>(
    owner: Owner<B, C>,
    channel: T,
    peer: u64,
    rights: Rights,
    epoch: u64,
) -> filesystem_service::Report {
    filesystem_activation::run(owner, channel, peer, rights, epoch, || {
        // Read the shared userland UTC provider before declaring writable readiness.
        // Every later mutation still reads/checks UTC independently.
        use filesystem_bridge::policy::Clock;
        if RuntimeUtc.utc().is_err() {
            return -5;
        }
        // SAFETY: existing worker-local scalar ready operation; no pointers,
        // transferred grants or retained borrows. Failure remains a failure.
        unsafe { trap(0x20004, 0, 0, 0) }
    })
}

#[cfg(all(test, fs_directories))]
#[path = "directory-service-tests.rs"]
mod tests;
