// SPDX-License-Identifier: BSD-2-Clause
//! Small freestanding memcmp for the bounded ABI9 command image.
/// Compare unsigned bytes; only the sign of a nonzero result is specified.
///
/// # Safety
/// Both pointers must permit reads of `len` bytes for this call. The ranges may
/// overlap and need no alignment. With zero length neither pointer is accessed.
/// Callers must exclude concurrent mutation. This is not a constant-time compare.
#[cfg_attr(target_os = "none", unsafe(no_mangle))]
pub unsafe extern "C" fn memcmp(left: *const u8, right: *const u8, len: usize) -> i32 {
    for i in 0..len {
        // Volatile reads prevent this implementation becoming a recursive call
        // to the very compiler helper it supplies. No device-memory use is intended.
        let a = unsafe { left.add(i).read_volatile() };
        let b = unsafe { right.add(i).read_volatile() };
        if a != b { return i32::from(a) - i32::from(b); }
    }
    0
}
