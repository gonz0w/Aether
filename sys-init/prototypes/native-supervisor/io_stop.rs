// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;

fn call(op: u64, holder: u64, arg: u64) -> (i64, u64, u64) {
    let result: i64;
    let ready: u64;
    let kind: u64;
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") holder,
             in("rsi") arg, lateout("rdx") ready, lateout("rcx") _, lateout("r8") kind);
    }
    (result, ready, kind)
}
fn end(code: u64) -> ! {
    call(0x20006, code, 0);
    loop { core::hint::spin_loop(); }
}
fn check(ok: bool, code: u64) { if !ok { end(code); } }
fn yield_now() { call(0x1fffe, 0, 0); }
fn launch(factory: u64) -> u64 {
    let handle = call(0x20000, factory, 0).0;
    check(handle > 0, 240);
    handle as u64
}
fn ready(handle: u64) {
    for _ in 0..100000 {
        let status = call(0x20001, handle, 0);
        check(status.0 == 0 && status.2 == 0, 241);
        if status.1 == 1 { return; }
        yield_now();
    }
    end(242);
}
fn output(handle: u64, stream: u64, expected: &[u8]) {
    for (offset, byte) in expected.iter().enumerate() {
        check(call(0x20009, handle, (stream << 32) | offset as u64).0 == *byte as i64, 250);
    }
    check(call(0x20009, handle, (stream << 32) | expected.len() as u64).0 == 256, 251);
}
fn open_outputs(handle: u64) {
    for stream in 1..=2 { check(call(0x20009, handle, stream << 32).0 == -11, 252); }
}
fn reclaim(handle: u64) {
    check(call(0x20002, handle, 0).0 == 0, 253);
    for (op, arg) in [(0x20001, 0), (0x20007, 0), (0x20008, 65),
                       (0x20009, 1 << 32), (0x20009, 2 << 32), (0x20002, 0)] {
        check(call(op, handle, arg).0 == -9, 254);
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64) -> ! {
    check(abi == 2 && factory == 0xa001, 239);
    let first = launch(factory);
    ready(first);
    open_outputs(first);
    for _ in 0..2 {
        check(call(0x20007, first, 0).0 == 0, 243);
        let status = call(0x20001, first, 0);
        let expected = if cfg!(wrong_stop_detail) { 145 } else { 144 };
        check(status.0 == expected && status.1 == 1 && status.2 == 3, 244);
    }
    output(first, 1, b"");
    output(first, 2, b"");
    check(call(0x20008, first, 65).0 == -32, 245);
    check(call(0x20008, first, 256).0 == -32, 246);
    reclaim(first);

    let second = launch(factory);
    check(second != first, 247);
    ready(second);
    open_outputs(second);
    for byte in b"0123456789abcdefghijklmnopqrstuv" {
        check(call(0x20008, second, *byte as u64).0 == 0, 255);
    }
    check(call(0x20008, second, 99).0 == -11, 256);
    check(call(0x20008, second, 256).0 == 0, 257);
    check(call(0x20008, second, 99).0 == -32, 258);
    let mut done = false;
    for _ in 0..100000 {
        let status = call(0x20001, second, 0);
        if status.0 != 0 {
            check(status.0 == 1 && status.1 == 1 && status.2 == 1, 259);
            done = true;
            break;
        }
        yield_now();
    }
    check(done, 260);
    output(second, 1, b"native descriptors ok\n");
    output(second, 2, b"native error stream\n");
    reclaim(second);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { end(299) }
