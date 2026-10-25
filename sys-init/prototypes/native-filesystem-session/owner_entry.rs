// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! ABI30/31 entry register bridge only. The linked owner_main supplies actual policy.
use core::arch::naked_asm;
unsafe extern "C" {
    fn owner_main(
        abi: u64,
        factory: u64,
        block: u64,
        image: u64,
        channels: u64,
        cleanup: u64,
        data_base: u64,
        data_bytes: u64,
    ) -> !;
}
/// # Safety
/// Kernel-only boot entry under the selected ABI30/31 mapping/startup contract.
/// Initial RSP is0x801000-8 (ABI30), or0x802000-8 (ABI31). Capture all eight
/// scalars before any ordinary call; the consumer validates the exact selection.
#[unsafe(naked)]
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub unsafe extern "C" fn _start() -> ! {
    // Entry RSP%16=8. Reserve16 bytes for args7/8 plus8 for call alignment.
    // Only RSP changes before the volatile r10/r11 values are saved. The six
    // ordinary argument registers remain untouched. Callee entry is aligned8.
    naked_asm!("sub rsp,24", "mov [rsp],r10", "mov [rsp+8],r11", "call {main}",
        "ud2", main=sym owner_main);
}
