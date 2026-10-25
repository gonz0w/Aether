// SPDX-License-Identifier: BSD-2-Clause
//! Separate AF09 executable owner; initialization policy, not a new service protocol.
#![no_std]
use core::ffi::c_void;
const FINISHED: u64 = 8191;
const ENTERED: u64 = 32;
#[path = "home-native-result.rs"]
pub mod result;
pub use result::*;
#[cfg(not(fs_home_native))]
compile_error!("home executable owner requires fs_home_native");
#[cfg(not(test))]
extern "C" {
    fn getauxval(tag: usize) -> usize;
    fn aether_fs_home_engine_run(grant: u64, state: *mut HomeLaunchState) -> i32;
    fn aether_fs_home_run(
        spa: *mut c_void,
        dataset: *const u8,
        length: usize,
        reader: u64,
        writer: u64,
        uid: u64,
        gid: u64,
        result: *mut HomeResult,
        out_bytes: usize,
    ) -> i32;
}
#[cfg(test)]
use tests::{aether_fs_home_engine_run, aether_fs_home_run, getauxval};

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
fn close_startup(state: &mut HomeLaunchState) {
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
fn run(state: &mut HomeLaunchState) -> i32 {
    if !provisioned(state.reader, state.writer) {
        close_startup(state);
        return 22;
    }
    let endpoints = (state.reader, state.writer);
    // SAFETY: sole initialized aligned state; the engine retains no pointer on
    // return. Original SPA and executable remain resident throughout callbacks.
    let error = unsafe { aether_fs_home_engine_run(0xf101, state) };
    // Only a canonical unaccepted outcome proves handback after callback entry.
    // Contradictory or absent evidence never causes a speculative second close.
    if state.version == 1
        && state.bytes == 384
        && (state.reader, state.writer) == endpoints
        && state.phases & !FINISHED == 0
        && ((state.phases & ENTERED == 0 && state.home.canonical_initial(false))
            || (state.phases & ENTERED != 0
                && state.home.flags == CALLBACK | ENTRY
                && state.home.canonical_unaccepted()))
    {
        close_startup(state);
    }
    if error != 0 {
        return if (1..=255).contains(&error) { error } else { 5 };
    }
    let home = &state.home;
    let service = &home.service;
    let progress_valid = match service.state {
        0 => service.txg == 0 && service.bytes_staged == 0,
        2 => service.txg != 0 && service.bytes_staged <= 4096,
        _ => false,
    };
    if state.version != 1
        || state.bytes != 384
        || state.phases != FINISHED
        || state.engine_error != 0
        || !home.valid()
        || home.phase != 0
        || home.flags != CALLBACK | ENTRY | ACCEPTED | CLOSE_ATTEMPTED | ORDERED | ACTIVATION
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
    let mut state = HomeLaunchState {
        version: 1,
        bytes: 384,
        // SAFETY: existing native ELF auxv holds the authenticated transferred
        // pair. Names/IDs/this format check never replace native holder checks.
        reader: unsafe { getauxval(0xa004) } as u64,
        writer: unsafe { getauxval(0xa005) } as u64,
        home: HomeResult::initial(),
        ..HomeLaunchState::default()
    };
    run(&mut state)
}

/// # Safety
/// Engine supplies its exclusive, validated live writable SPA and the sole
/// initialized launch state. Both remain resident until this synchronous call
/// returns; there is no concurrent mutation, reentry or import/export. The
/// selected AF09 entry consumes its contexts and endpoints before returning.
#[no_mangle]
pub unsafe extern "C" fn aether_fs_home_launch_serve(
    spa: *mut c_void,
    state: *mut HomeLaunchState,
) -> i32 {
    // SAFETY: trusted engine caller guarantees this exclusive process-local
    // borrow; null is rejected before any pointer dereference or service call.
    let Some(state) = (unsafe { state.as_mut() }) else {
        return 22;
    };
    if spa.is_null()
        || state.version != 1
        || state.bytes != 384
        || state.phases & ENTERED == 0
        || state.phases & !FINISHED != 0
        || state.engine_error != 0
        || state.startup_reader_close != 0
        || state.startup_writer_close != 0
        || !provisioned(state.reader, state.writer)
        || !state.home.canonical_initial(false)
    {
        return 22;
    }
    state.home.flags |= CALLBACK;
    const DATASET: &[u8] = b"testpool_zstd/x86_64\0";
    // SAFETY: immutable NUL dataset, trusted labels/rights, separately aligned
    // writable result and exclusively live SPA satisfy the exact sealed entry.
    unsafe {
        aether_fs_home_run(
            spa,
            DATASET.as_ptr(),
            DATASET.len() - 1,
            state.reader,
            state.writer,
            1000,
            1000,
            &mut state.home,
            320,
        )
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "launch-home-owner-tests.rs"]
mod tests;
