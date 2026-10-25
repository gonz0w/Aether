// SPDX-License-Identifier: BSD-2-Clause
use super::{Control, Status};
use af07_transport::native::Native;
use core::arch::asm;
#[inline(never)]
fn call(op: u64, args: [u64; 6]) -> Status {
    let status: i64;
    let second: u64;
    let third: u64;
    // SAFETY: fixed ABI30 scalar arguments or synchronous borrows supplied only
    // by the typed methods below. No buffer survives return; all three outputs
    // and volatile rcx/r11 clobbers are explicit. No nomem/preserves_flags claim.
    unsafe {
        asm!("int 0x81",inlateout("rax")op=>status,in("rdi")args[0],in("rsi")args[1],
            inlateout("rdx")args[2]=>second,in("r10")args[3],inlateout("r8")args[4]=>third,
            in("r9")args[5],lateout("rcx")_,lateout("r11")_);
    }
    (status, second, third)
}
impl Control for Native {
    fn exec(&mut self, process: u64, token: u64, arguments: &[u8; 272]) -> i64 {
        call(
            0x23007,
            [0xa001, process, 0xc003, token, arguments.as_ptr() as u64, 0],
        )
        .0
    }
    fn receipt(&mut self, process: u64) -> Status {
        call(0x23008, [0xa001, process, 0, 0, 0, 0])
    }
    fn publish(&mut self, process: u64, token: u64) -> i64 {
        call(0x23009, [0xa001, process, token, 0, 0, 0]).0
    }
    fn ctl(&mut self, op: u64, handle: u64, argument: u64) -> Status {
        call(op, [handle, argument, 0, 0, 0, 0])
    }
    fn engine(&mut self, reader: u64, writer: u64) -> i64 {
        call(0x20008, [0xa001, 0, reader, writer, 0, 0]).0
    }
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64 {
        call(0x27005, [0xf101, engine, region.as_ptr() as u64, 24, 0, 0]).0
    }
    fn launch(&mut self, args: &[u8; 272], reader: u64, writer: u64) -> i64 {
        call(
            0x23002,
            [0xa001, 0xc002, 1, args.as_ptr() as u64, reader, writer],
        )
        .0
    }
    fn copy(&mut self, parent: u64, slot: u32, token: u64, reader: u64, writer: u64) -> i64 {
        call(
            0x23006,
            [0xa001, parent, slot as u64, token, reader, writer],
        )
        .0
    }
    fn serial(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        if bytes.len() > 16 {
            return -22;
        }
        call(
            if writing { 0x26001 } else { 0x26000 },
            [
                0xf001,
                bytes.as_mut_ptr() as u64,
                bytes.len() as u64,
                0,
                0,
                0,
            ],
        )
        .0
    }
}
