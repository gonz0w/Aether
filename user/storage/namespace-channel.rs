// SPDX-License-Identifier: BSD-2-Clause
//! Private synchronous channel adapter. The local kernel authenticates each
//! invocation against the active domain's endpoint binding, including workers.
use core::arch::asm;

/// # Safety
/// Any pointer argument must denote initialized, correctly sized storage, with
/// exclusive access for writes, for the entire synchronous kernel operation.
#[inline(never)]
pub unsafe fn trap(op: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64) {
    let result: i64;
    let secondary: u64;
    // SAFETY: int81 is the selected native profile's synchronous syscall entry.
    // All caller-saved result registers are declared; memory is not marked
    // nomem. For pointer operations the caller owns live initialized storage
    // for the complete call. Kernel validates direction, bounds and mappings,
    // copies at most16 bytes and retains no pointer after completion.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") a,
             in("rsi") b, inlateout("rdx") c => secondary,
             inlateout("r10") d => _, inlateout("r8") 0u64 => _,
             inlateout("r9") 0u64 => _, lateout("rcx") _, lateout("r11") _);
    }
    (result, secondary)
}

/// Complete one fixed frame. Partial EOF/failure is never a request. The caller
/// discards its buffer and revokes its connection on error. No dynamic storage,
/// cross-request partial state or kernel wait registration is retained.
pub fn frame(endpoint: u64, bytes: &mut [u8; 64], writing: bool) -> Result<(), i64> {
    let mut offset = 0;
    for _ in 0..100_000 {
        let chunk = (64 - offset).min(16);
        // SAFETY: exclusive live initialized frame slice covers this chunk.
        let (count, _) = unsafe {
            trap(
                if writing { 0x24002 } else { 0x24001 },
                endpoint,
                bytes[offset..].as_mut_ptr() as u64,
                chunk as u64,
                0,
            )
        };
        if count == -11 {
            // SAFETY: yield has no pointer arguments or retained storage.
            unsafe { trap(0x1fffe, 0, 0, 0, 0) };
        } else if count <= 0 || count as usize > chunk {
            bytes.fill(0);
            return Err(if count < 0 { count } else { -5 });
        } else {
            offset += count as usize;
            if offset == bytes.len() {
                return Ok(());
            }
        }
    }
    bytes.fill(0);
    Err(-110)
}
