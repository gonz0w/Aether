// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
mod policy;
use core::arch::asm;
struct Native;

#[inline(never)]
fn call(op: u64, a: u64, b: u64, c: u64, d: u64, e: u64) -> policy::Status {
    let status: i64;
    let second: u64;
    let third: u64;
    // SAFETY: fixed scalar ABI or exclusive synchronous live buffer borrows;
    // no pointer retained. No nomem/preserves_flags claim; outputs match ABI29.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => status, in("rdi") a,
             in("rsi") b, inlateout("rdx") c => second, in("r10") d,
             inlateout("r8") e => third, in("r9") 0u64,
             lateout("rcx") _, lateout("r11") _);
    }
    (status, second, third)
}
impl policy::Kernel for Native {
    fn ctl(&mut self, op: u64, handle: u64) -> policy::Status {
        call(op, handle, 0, 0, 0, 0)
    }
    fn channel(&mut self) -> policy::Status {
        self.ctl(0x24000, 0xd002)
    }
    fn engine(&mut self, reader: u64, writer: u64) -> i64 {
        call(0x20008, 0xa001, 0, reader, writer, 0).0
    }
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64 {
        call(0x27005, 0xf101, engine, region.as_ptr() as u64, 24, 0).0
    }
    fn process(&mut self, arguments: &[u8; 272]) -> i64 {
        call(0x23000, 0xa001, 0xc002, 1, arguments.as_ptr() as u64, 0).0
    }
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], write: bool) -> i64 {
        call(
            if write { 0x24002 } else { 0x24001 },
            endpoint,
            bytes.as_mut_ptr() as u64,
            bytes.len() as u64,
            0,
            0,
        )
        .0
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    abi: u64,
    factory: u64,
    block: u64,
    program: u64,
    channels: u64,
    spare: u64,
) -> ! {
    let _ = policy::run(
        &mut Native,
        [abi, factory, block, program, channels, spare],
        1_000_000,
    );
    fail()
}
fn fail() -> ! {
    // Unknown resources remain retained. No false completion or replay.
    unsafe { asm!("ud2", options(noreturn)) }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    fail()
}
