// SPDX-License-Identifier: BSD-2-Clause
//! Native engine entry for the bounded service; requires matched provisioning.
#![no_std]
#[cfg(not(test))]
use core::arch::asm;
use core::{ffi::c_void, ptr::NonNull};
use filesystem_bridge::{
    policy::{
        Completion, Error, Handle, Identity, Kind, Mutation, NamespaceObservation, Owner, Rights,
        Session,
    },
    Spa,
};
use filesystem_service::{
    channel::{Framed, Io},
    Stop,
};

#[cfg(not(fs_home_probe_three))]
use filesystem_bridge::RuntimeUtc as EntryUtc;
/// The fixed preparation profile accepts only observations in its recorded
/// half-open UTC window. This delegates to the real shared provider and keeps
/// no state, adjustment, reset authority or independent mutation ledger.
#[cfg(fs_home_probe_three)]
struct EntryUtc;
#[cfg(fs_home_probe_three)]
impl filesystem_bridge::policy::Clock for EntryUtc {
    fn utc(&mut self) -> Result<filesystem_bridge::policy::Utc, Error> {
        let value = filesystem_bridge::policy::Clock::utc(&mut filesystem_bridge::RuntimeUtc)?;
        if !(1791290040..1791290100).contains(&value.seconds) || value.nanoseconds >= 1_000_000_000
        {
            return Err(Error::Clock);
        }
        Ok(value)
    }
}
const _: () = assert!(core::mem::size_of::<EntryUtc>() == 0);

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

struct Endpoints<'a> {
    reader: u64,
    writer: u64,
    closed: bool,
    flags: Option<&'a mut u64>,
}
impl Io for Endpoints<'_> {
    #[cfg(fs_af09_drain)]
    fn af09_counts(&mut self, mutations: u64, requests: u64) -> Result<(), i64> {
        let mutations = u16::try_from(mutations).map_err(|_| -75)?;
        let requests = u16::try_from(requests).map_err(|_| -75)?;
        let [m0, m1] = mutations.to_le_bytes();
        let [r0, r1] = requests.to_le_bytes();
        let record = [1u8, 1, m0, m1, r0, r1, 0, 0];
        // SAFETY: the existing checked output ABI synchronously copies this
        // initialized read-only record8; no pointer survives the call. Stream1
        // and all remaining zero scalars preserve ordinary output authority.
        match unsafe { trap(0x10001, 1, record.as_ptr() as u64, 8) } {
            8 => Ok(()),
            error if error < 0 => Err(error),
            _ => Err(-5),
        }
    }

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
        if let Some(flags) = self.flags.as_mut() {
            **flags |= CLOSE_ATTEMPTED;
        }
        // SAFETY: both scalar tokens owned by this instance, no pending I/O.
        unsafe {
            [
                trap(0x24003, self.reader, 0, 0),
                trap(0x24003, self.writer, 0, 0),
            ]
        }
    }
}
impl Drop for Endpoints<'_> {
    fn drop(&mut self) {
        if !self.closed {
            let _ = self.close();
        }
    }
}

#[path = "home-native-result.rs"]
pub mod result;
pub use result::*;
#[cfg(not(all(
    fs_home_native,
    fs_home_activation,
    fs_home_wire,
    fs_home,
    fs_runtime,
    fs_mixed,
    fs_directories,
    fs_directory_contexts,
    fs_metadata
)))]
compile_error!("home native entry requires the complete explicit AF09 selection");
const _: () = assert!(
    matches!(filesystem_service::MAGIC, b"AFSRPC09"),
    "home native requires matching AF09 service"
);

fn error_fields(error: Error) -> (u64, i64) {
    (
        match error {
            Error::Invalid => 1,
            Error::Denied => 2,
            Error::Stale => 3,
            Error::Full => 4,
            Error::Closed => 5,
            Error::NotDirectory => 6,
            Error::IsDirectory => 7,
            Error::InvalidMetadata => 8,
            Error::InvalidCompletion => 9,
            Error::Backend(_) => 10,
            Error::Clock => 11,
            Error::WriteLimit => 12,
            Error::Poisoned => 13,
            Error::Uncertain => 14,
            Error::WriteFailed(_) => 15,
            Error::Unsupported => 16,
        },
        if let Error::Backend(code) = error {
            i64::from(code)
        } else {
            0
        },
    )
}
fn fail(out: &mut HomeResult, phase: u64, error: Error) {
    out.phase = phase;
    (out.error_kind, out.error_value) = error_fields(error);
}
fn retain(
    receipt: &mut BootstrapReceipt,
    observation: NamespaceObservation,
) -> Result<Completion, Error> {
    if let Some(provider) = observation.provider {
        match provider {
            Ok(value) => {
                receipt.provider = 1;
                receipt.provider_error = i64::from(value.error);
                receipt.provider_txg = value.txg;
                receipt.provider_staged = value.bytes_staged;
                receipt.provider_state = value.state;
            }
            Err(_) => receipt.provider = 2,
        }
    }
    let completion = match observation.result {
        Ok(value) => {
            receipt.returned = 1;
            Some(value)
        }
        Err(error) => {
            receipt.returned = 2;
            (receipt.error_kind, receipt.error_value) = error_fields(error);
            if let Error::WriteFailed(value) = error {
                Some(value)
            } else {
                None
            }
        }
    };
    if let Some(value) = completion {
        receipt.returned_error = i64::from(value.error);
        receipt.returned_txg = value.txg;
        receipt.returned_staged = value.bytes_staged;
        receipt.returned_state = value.state;
    }
    observation.result
}
fn bootstrap<B: filesystem_bridge::policy::Backend, C: filesystem_bridge::policy::Clock>(
    owner: &mut Owner<B, C>,
    peer: u64,
    out: &mut HomeResult,
) -> Result<(Session, Handle), (u64, Error)> {
    let rights = Rights::new(15).map_err(|e| (3, e))?;
    let admin = owner.attach(peer, rights).map_err(|e| (3, e))?;
    let observed = owner.namespace_observed(
        peer,
        admin.session,
        admin.root.handle,
        Mutation::MakeDirectory(b"home"),
    );
    let outcome = retain(&mut out.mkdir, observed);
    if out.mkdir.requires_ordering() {
        out.flags |= ORDERED;
    }
    outcome.map_err(|e| (4, e))?;
    let home = owner
        .lookup(peer, admin.session, admin.root.handle, b"home", rights)
        .map_err(|e| (5, e))?;
    owner
        .validate_home_source(peer, admin.session, home.handle)
        .map_err(|e| (5, e))?;
    let observed =
        owner.namespace_observed(peer, admin.session, home.handle, Mutation::Create(b"probe"));
    let outcome = retain(&mut out.create, observed);
    if out.create.requires_ordering() {
        out.flags |= ORDERED;
    }
    outcome.map_err(|e| (6, e))?;
    let probe = owner
        .lookup(
            peer,
            admin.session,
            home.handle,
            b"probe",
            Rights::new(3).map_err(|e| (7, e))?,
        )
        .map_err(|e| (7, e))?;
    if probe.kind != Kind::File || probe.size != 0 {
        return Err((7, Error::InvalidMetadata));
    }
    owner
        .close(peer, admin.session, probe.handle)
        .map_err(|e| (8, e))?;
    Ok((admin.session, home.handle))
}
/// Trusted synchronous importer only; this is never a client RPC.
/// # Safety
/// SPA is an exclusive live writable/accounted import satisfying Spa::from_raw;
/// dataset is1..255 immutable non-NUL bytes plus NUL. Output is320 live aligned,
/// initialized integer-carrier bytes, exclusive and disjoint from SPA/dataset.
/// Endpoints are unique authenticated request-reader/reply-writer tokens with
/// live counterpart holders. No concurrent mutation, reentry, teardown or pointer
/// retention; engine/code/SPA remain resident through original ordered export.
#[allow(
    clippy::too_many_arguments,
    reason = "Exact nine-argument private C ABI."
)]
#[no_mangle]
pub unsafe extern "C" fn aether_fs_home_run(
    spa: *mut c_void,
    dataset: *const u8,
    length: usize,
    reader: u64,
    writer: u64,
    uid: u64,
    gid: u64,
    out: *mut HomeResult,
    out_bytes: usize,
) -> i32 {
    if out.is_null()
        || out_bytes != 320
        || !(out as usize).is_multiple_of(core::mem::align_of::<HomeResult>())
    {
        return 22;
    }
    // SAFETY: caller supplies initialized exclusive aligned storage of exact extent.
    let output = unsafe { &mut *out };
    if !output.canonical_initial(true) {
        return 22;
    }
    output.flags |= ENTRY;
    if reader & 255 != 1
        || writer & 255 != 2
        || reader >> 16 == 0
        || writer >> 16 == 0
        || reader >> 16 == writer >> 16
        || reader > i64::MAX as u64
        || writer > i64::MAX as u64
        || spa.is_null()
        || dataset.is_null()
        || length == 0
        || length > 255
        || uid != 1000
        || gid != 1000
    {
        fail(output, 1, Error::Invalid);
        return 22;
    }
    // SAFETY: documented live immutable dataset extent is bounded above.
    let bytes = unsafe { core::slice::from_raw_parts(dataset, length + 1) };
    let Ok(name) = core::ffi::CStr::from_bytes_with_nul(bytes) else {
        fail(output, 1, Error::Invalid);
        return 22;
    };
    output.flags |= ACCEPTED;
    let mut endpoints = Endpoints {
        reader,
        writer,
        closed: false,
        flags: None,
    };
    // SAFETY: checked nonnull; trusted caller guarantees exclusive live SPA contract.
    let mut spa = unsafe { Spa::from_raw(NonNull::new(spa).unwrap()) };
    let setup = spa
        .open(name)
        .and_then(|backend| Owner::new(backend, EntryUtc, reader));
    let mut owner = match setup {
        Ok(owner) => owner.with_namespace_identity(Identity::new(uid, gid).unwrap()),
        Err(error) => {
            fail(output, 2, error);
            output.flags |= CLOSE_ATTEMPTED;
            let closes = endpoints.close();
            output.service.reader_close = closes[0];
            output.service.writer_close = closes[1];
            return 5;
        }
    };
    let (session, home) = match bootstrap(&mut owner, reader, output) {
        Ok(value) => value,
        Err((phase, error)) => {
            fail(output, phase, error);
            output.mutation_attempts = owner.mutation_attempts() as u64;
            owner.shutdown();
            output.flags |= CLOSE_ATTEMPTED;
            let closes = endpoints.close();
            output.service.reader_close = closes[0];
            output.service.writer_close = closes[1];
            return 5;
        }
    };
    output.flags |= ACTIVATION | ORDERED;
    endpoints.flags = Some(&mut output.flags);
    let report = filesystem_activation::run_home(
        owner,
        Framed(endpoints),
        reader,
        session,
        home,
        reader,
        reader,
        || {
            use filesystem_bridge::policy::Clock;
            if EntryUtc.utc().is_err() {
                return -5;
            }
            // SAFETY: scalar worker-local ready operation, no retained pointers.
            unsafe { trap(0x20004, 0, 0, 0) }
        },
    );
    output.mutation_attempts = report.mutation_attempts as u64;
    let service = &mut output.service;
    service.ready = u64::from(report.ready);
    service.requests = report.requests as u64;
    service.stop = match report.stop {
        Stop::Disconnected => 0,
        Stop::Receive(_) => 1,
        Stop::ReplyLost(_) => 2,
        Stop::Limit => 3,
        Stop::Provision(_) => 4,
        Stop::Retired => 5,
        Stop::NamespaceComplete => 6,
    };
    service.reader_close = report.cleanup[0];
    service.writer_close = report.cleanup[1];
    service.error = match report.stop {
        Stop::Receive(code) | Stop::ReplyLost(code) => code,
        Stop::Limit => -28,
        Stop::Provision(_) => -22,
        Stop::Retired => -5,
        Stop::Disconnected | Stop::NamespaceComplete => report
            .cleanup
            .iter()
            .copied()
            .find(|c| *c != 0)
            .unwrap_or(0),
    };
    if let Some(value) = report.last_write {
        service.txg = value.txg;
        service.bytes_staged = value.bytes_staged;
        service.state = value.state;
    }
    let clean = matches!(report.stop, Stop::Disconnected | Stop::NamespaceComplete)
        && report.cleanup == [0, 0];
    if let Stop::Provision(error) = report.stop {
        fail(output, 9, error);
    }
    if clean {
        0
    } else {
        5
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "native-home-tests.rs"]
mod tests;
