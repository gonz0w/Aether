// SPDX-License-Identifier: BSD-2-Clause
//! Four-page mapping witness only; no sys-init policy or writable state.
static BYTES: [u8; 8192] = {
    let mut bytes = [0; 8192];
    let mut i = 0;
    while i < bytes.len() {
        bytes[i] = (i % 251) as u8;
        i += 1;
    }
    bytes
};
#[inline(never)]
pub fn verify() -> bool {
    let mut total = 0u64;
    for i in 0..BYTES.len() {
        // SAFETY: each address is within the live immutable static mapped RX by
        // this private profile; volatile retains the complete mapping witness.
        total += u64::from(unsafe { core::ptr::read_volatile(BYTES.as_ptr().add(i)) });
    }
    total == 1_016_720
}
