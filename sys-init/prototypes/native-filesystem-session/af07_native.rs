// SPDX-License-Identifier: BSD-2-Clause
//! ABI29 synchronous native channel operations; target witness still required.
use super::Kernel;
use core::arch::asm;
#[derive(Clone)]
pub struct Native;

fn call(op: u64, endpoint: u64, pointer: u64, count: u64) -> i64 {
    let status: i64;
    // SAFETY: scalar operations or an exclusive synchronous initialized slice;
    // no pointer retained. Fixed ABI29 registers/clobbers, no memory/flags claims.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => status, in("rdi") endpoint,
             in("rsi") pointer, inlateout("rdx") count => _, in("r10") 0u64,
             inlateout("r8") 0u64 => _, in("r9") 0u64,
             lateout("rcx") _, lateout("r11") _);
    }
    status
}
impl Native {
    /// Cancel this owned parked process's exact observed freeze token. The native
    /// supervisor receives0; the separate parent return becomes-11. Source/token
    /// labels confer no authority and all shape/state/grant checks stay in kernel.
    pub fn cancel_freeze(&mut self, source: u64, token: u64) -> i64 {
        call(0x23005, source, token, 0)
    }
}
impl Kernel for Native {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        call(
            if writing { 0x24002 } else { 0x24001 },
            endpoint,
            bytes.as_mut_ptr() as u64,
            bytes.len() as u64,
        )
    }
    fn wait(&mut self, endpoint: u64) -> i64 {
        call(0x24004, endpoint, 0, 0)
    }
    fn close(&mut self, endpoint: u64) -> i64 {
        call(0x24003, endpoint, 0, 0)
    }
}
