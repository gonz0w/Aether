// SPDX-License-Identifier: BSD-2-Clause
//! ABI26 primary-context transport; preserves the sealed polling adapter.
#[path = "namespace-channel.rs"]
#[expect(
    dead_code,
    reason = "Reuse only the sealed syscall; its polling frame remains unchanged and unused."
)]
mod primitive;
pub use primitive::trap;

/// Complete one initialized frame with holder-scoped level readiness hints.
/// The synchronous transfer retains no pointer when it returns EAGAIN. Only
/// the endpoint is parked; the exclusive frame borrow stays in this context.
/// Any failure clears the whole frame. No request or mutation is replayed.
pub fn frame(endpoint: u64, bytes: &mut [u8; 64], writing: bool) -> Result<(), i64> {
    let mut offset = 0;
    for _ in 0..100_000 {
        let chunk = (bytes.len() - offset).min(16);
        // SAFETY: exact live initialized exclusive chunk; no kernel retention.
        let count = unsafe {
            trap(
                if writing { 0x24002 } else { 0x24001 },
                endpoint,
                bytes[offset..].as_mut_ptr() as u64,
                chunk as u64,
                0,
            )
        }
        .0;
        if count == -11 {
            // SAFETY: scalar owned endpoint, no user pointer survives transfer.
            // Wake is only a hint; recheck the same remaining byte range.
            let status = unsafe { trap(0x24004, endpoint, 0, 0, 0) }.0;
            if status != 0 {
                bytes.fill(0);
                return Err(if status < 0 { status } else { -5 });
            }
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
