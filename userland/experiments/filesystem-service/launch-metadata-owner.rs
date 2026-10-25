// SPDX-License-Identifier: BSD-2-Clause
//! Separate AF07 executable owner; initialization policy, not a new service protocol.
#![no_std]
use core::ffi::c_void;
const FINISHED: u64 = 8191;
const ENTERED: u64 = 32;
#[repr(C)]
#[derive(Default, PartialEq, Eq)]
pub struct ServiceResult {
    pub ready: u64,
    pub requests: u64,
    pub stop: u64,
    pub reader_close: i64,
    pub writer_close: i64,
    pub error: i64,
    pub txg: u64,
    pub bytes_staged: u64,
    pub state: u64,
}
#[repr(C)]
#[derive(Default)]
pub struct LaunchState {
    pub version: u64,
    pub bytes: u64,
    pub reader: u64,
    pub writer: u64,
    pub phases: u64,
    pub engine_error: i64,
    pub service: ServiceResult,
    pub startup_reader_close: i64,
    pub startup_writer_close: i64,
}
const _: () = assert!(core::mem::size_of::<LaunchState>() == 136);
const _: () = assert!(core::mem::offset_of!(LaunchState, service) == 48);
const _: () = assert!(core::mem::size_of::<ServiceResult>() == 72);
const _: () = assert!(core::mem::align_of::<LaunchState>() == 8);
const _: () = assert!(core::mem::offset_of!(LaunchState, engine_error) == 40);
const _: () = assert!(core::mem::offset_of!(LaunchState, startup_reader_close) == 120);
const _: () = assert!(core::mem::offset_of!(LaunchState, startup_writer_close) == 128);
#[cfg(not(test))]
extern "C" {
    fn getauxval(tag: usize) -> usize;
    fn aether_fs_engine_run(grant: u64, state: *mut LaunchState) -> i32;
    fn aether_fs_metadata_run(
        spa: *mut c_void,
        dataset: *const u8,
        length: usize,
        reader: u64,
        writer: u64,
        rights: u64,
        uid: u64,
        gid: u64,
        result: *mut ServiceResult,
    ) -> i32;
}
#[cfg(test)]
use tests::{aether_fs_engine_run, aether_fs_metadata_run, getauxval};

#[cfg(not(test))]
unsafe fn close(endpoint: u64) -> i64 {
    let status: i64;
    // SAFETY: existing scalar close, enforced for this holder; no pointer retained.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") 0x24003u64 => status,
            in("rdi") endpoint, inlateout("rsi") 0u64=>_, inlateout("rdx") 0u64=>_,
            inlateout("r10") 0u64=>_, inlateout("r8") 0u64=>_, inlateout("r9") 0u64=>_,
            lateout("rcx") _, lateout("r11") _);
    }
    status
}
#[cfg(test)]
use tests::close;
fn provisioned(reader: u64, writer: u64) -> bool {
    reader & 255 == 1
        && writer & 255 == 2
        && reader >> 16 != 0
        && writer >> 16 != 0
        && reader >> 16 != writer >> 16
        && reader <= i64::MAX as u64
        && writer <= i64::MAX as u64
}
fn close_startup(state: &mut LaunchState) {
    // A nonzero inherited token is attempted once; native holder checks remain
    // authoritative even for malformed bootstrap. Never close an alias twice.
    state.startup_reader_close = if state.reader == 0 {
        -9
    } else {
        // SAFETY: scalar inherited token, synchronous owner-bound close.
        unsafe { close(state.reader) }
    };
    state.startup_writer_close = if state.writer == 0 || state.writer == state.reader {
        -9
    } else {
        // SAFETY: separate inherited token; no service acquired it yet.
        unsafe { close(state.writer) }
    };
}
fn run(state: &mut LaunchState) -> i32 {
    if !provisioned(state.reader, state.writer) {
        close_startup(state);
        return 22;
    }
    // SAFETY: sole initialized aligned state; the engine retains no pointer on
    // return. Original SPA and executable remain resident throughout callbacks.
    let error = unsafe { aether_fs_engine_run(0xf101, state) };
    // Contradictory engine evidence cannot hand endpoint ownership back after a
    // service report. Fail below without a second close or inferred reclamation.
    let service_unobserved = state.service == ServiceResult::default();
    if state.phases & ENTERED == 0 && service_unobserved {
        close_startup(state);
    }
    if error != 0 {
        return if (1..=255).contains(&error) { error } else { 5 };
    }
    let service = &state.service;
    // A clean disconnect cannot erase uncertain/committed last-operation state.
    // Namespace success legitimately stages zero bytes; metadata/read-only
    // sessions legitimately have no transaction. Neither promises durability.
    let progress_valid = match service.state {
        0 => service.txg == 0 && service.bytes_staged == 0,
        2 => service.txg != 0 && service.bytes_staged <= 4096,
        _ => false,
    };
    if state.version != 1
        || state.bytes != 136
        || state.phases != FINISHED
        || state.engine_error != 0
        || service.ready != 1
        || service.requests == 0
        || service.stop != 0
        || service.error != 0
        || service.reader_close != 0
        || service.writer_close != 0
        || !progress_valid
    {
        return 5;
    }
    0
}
#[cfg_attr(not(test), export_name = "main")]
pub extern "C" fn filesystem_main() -> i32 {
    let mut state = LaunchState {
        version: 1,
        bytes: 136,
        // SAFETY: existing native ELF auxv holds the authenticated transferred
        // pair. Names/IDs/this format check never replace native holder checks.
        reader: unsafe { getauxval(0xa004) } as u64,
        writer: unsafe { getauxval(0xa005) } as u64,
        ..LaunchState::default()
    };
    run(&mut state)
}

/// # Safety
/// Engine supplies its exclusive, validated live writable SPA and the sole
/// initialized launch state. Both remain resident until this synchronous call
/// returns; there is no concurrent mutation, reentry or import/export. The
/// retained AF07 entry consumes its contexts and endpoints before returning.
#[no_mangle]
pub unsafe extern "C" fn aether_fs_launch_serve(spa: *mut c_void, state: *mut LaunchState) -> i32 {
    // SAFETY: trusted engine caller guarantees this exclusive process-local
    // borrow; null is rejected before any pointer dereference or service call.
    let Some(state) = (unsafe { state.as_mut() }) else {
        return 22;
    };
    if spa.is_null()
        || state.version != 1
        || state.bytes != 136
        || state.phases & ENTERED == 0
        || !provisioned(state.reader, state.writer)
    {
        return 22;
    }
    const DATASET: &[u8] = b"testpool_zstd/x86_64\0";
    // SAFETY: immutable NUL dataset, trusted labels/rights, separately aligned
    // writable result and exclusively live SPA satisfy the exact sealed entry.
    unsafe {
        aether_fs_metadata_run(
            spa,
            DATASET.as_ptr(),
            DATASET.len() - 1,
            state.reader,
            state.writer,
            31,
            1000,
            1000,
            &mut state.service,
        )
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "launch-metadata-owner-tests.rs"]
mod tests;
