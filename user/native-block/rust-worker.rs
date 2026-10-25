// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#[path = "../storage/block.rs"]
mod block;
use block::{Block, Cause, Error};
use core::arch::asm;
unsafe extern "C" {
    fn block_tls_witness() -> u32;
}
fn control(op: u64) -> i64 {
    let result;
    // No pointer inputs; native interrupt context preserves other registers.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") 0u64,
             in("rsi") 0u64, inlateout("rdx") 0u64 => _, in("r10") 0u64,
             lateout("rcx") _, lateout("r8") _, lateout("r9") _);
    }
    result
}
fn invalid(r: Result<(), Error>) -> bool {
    r == Err(Error {
        cause: Cause::InvalidRequest,
        completed: 0,
    })
}
#[unsafe(no_mangle)]
pub extern "C" fn main() -> i32 {
    // The linked C witness takes no pointers, cannot unwind and reads this TLS.
    if unsafe { block_tls_witness() } != 17 {
        return 70;
    }
    if control(0x20005) != 2 {
        return if matches!(Block::open(0xf101), Err(Cause::Native(-13))) {
            0
        } else {
            71
        };
    }
    let mut device = None;
    for _ in 0..1000000 {
        match Block::open(0xf101) {
            Ok(b) => {
                device = Some(b);
                break;
            }
            Err(Cause::Native(-13)) => {
                control(0x1fffe);
            }
            _ => return 72,
        }
    }
    let Some(mut disk) = device else {
        return 72;
    };
    let rights = if cfg!(block_readonly) { 1 } else { 7 };
    if disk.size_bytes() != 8388608 || disk.rights() != rights {
        return 72;
    }
    if !matches!(Block::open(0xf100), Err(Cause::Native(-13))) {
        return 74;
    }
    let mut bytes = [0x5au8; 1024];
    if !invalid(disk.read(1, &mut bytes))
        || !invalid(disk.read(u64::MAX, &mut bytes))
        || !invalid(disk.read(0, &mut bytes[..511]))
        || !invalid(disk.read(0, &mut []))
        || !invalid(disk.read(disk.size_bytes() - 512, &mut bytes))
        || bytes != [0x5a; 1024]
    {
        return 75;
    }
    let mut oversized = [0x5au8; 8192];
    if !invalid(disk.read(0, &mut oversized)) || oversized != [0x5a; 8192] {
        return 76;
    }
    if disk.read(0, &mut oversized[..4096]).is_err() || oversized[512..4096] != [0xa5; 3584] {
        return 85;
    }
    // A two-sector read must retain byte order and preserve the untouched canary sector.
    if disk.read(0, &mut bytes).is_err() || bytes[512..] != [0xa5; 512] {
        return 77;
    }
    for (j, sector) in [0u64, 777, 16383].iter().enumerate() {
        if disk.read(sector * 512, &mut bytes[..512]).is_err() {
            return 77;
        }
        let base = if cfg!(block_verify) { 91 } else { 3 };
        for (i, b) in bytes[..512].iter().enumerate() {
            if *b != (i * 17 + base + j) as u8 {
                return 73;
            }
        }
        if cfg!(block_readonly) {
            if disk.write(sector * 512, &bytes[..512])
                != Err(Error {
                    cause: Cause::Native(-13),
                    completed: 0,
                })
            {
                return 78;
            }
        } else {
            if !invalid(disk.write(disk.size_bytes() - 512, &bytes)) {
                return 79;
            }
            if !cfg!(block_verify) {
                for (i, b) in bytes[..512].iter_mut().enumerate() {
                    *b = (i * 17 + 91 + j) as u8;
                }
                let length = if j == 0 { 1024 } else { 512 };
                if disk.write(sector * 512, &bytes[..length]).is_err() {
                    return 80;
                }
            }
        }
    }
    let flushed = disk.flush();
    if cfg!(block_readonly) {
        if flushed
            != Err(Error {
                cause: Cause::Native(-13),
                completed: 0,
            })
        {
            return 81;
        }
    } else if flushed.is_err() {
        return 82;
    }
    if cfg!(block_fault) {
        // Deliberate target fault; grant is still open when the task dies.
        unsafe {
            asm!("ud2", options(noreturn));
        }
    }
    let Ok(mut cached) = Block::open(0xf101) else {
        return 84;
    };
    if disk.close().is_err() || !matches!(Block::open(0xf101), Err(Cause::Native(-9))) {
        return 83;
    }
    if cached.read(0, &mut bytes[..512])
        != Err(Error {
            cause: Cause::Native(-9),
            completed: 0,
        })
    {
        return 84;
    }
    0
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    // Fail the target explicitly instead of relying on a timeout.
    unsafe {
        asm!("ud2", options(noreturn));
    }
}
