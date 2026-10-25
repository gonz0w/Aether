// SPDX-License-Identifier: BSD-2-Clause
// Transport conformance only; terminal and supervision policy belong to consumers.
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, grant: u64, buffer: u64, count: u64) -> i64 {
    let result;
    // Native interrupt ABI preserves other registers except these documented outputs.
    // Buffer lifetime spans the synchronous call; the kernel validates mappings.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") grant,
             in("rsi") buffer, inlateout("rdx") count => _, lateout("rcx") _,
             lateout("r8") _, lateout("r9") _);
    }
    result
}
fn end(code: u64) -> ! {
    call(0x20006, code, 0, 0);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool, code: u64) {
    if !ok {
        end(code);
    }
}
fn write(grant: u64, bytes: &[u8]) {
    let mut offset = 0;
    for _ in 0..100000 {
        if offset == bytes.len() {
            return;
        }
        let n = call(
            0x26001,
            grant,
            bytes[offset..].as_ptr() as u64,
            (bytes.len() - offset) as u64,
        );
        check(
            n == -11 || (n > 0 && n <= 16 && n as usize <= bytes.len() - offset),
            902,
        );
        if n > 0 {
            offset += n as usize;
        } else {
            call(0x1fffe, 0, 0, 0);
        }
    }
    end(903)
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, grant: u64) -> ! {
    check(abi == 10 && factory == 0xa001 && grant != 0, 900);
    let mut data = [0u8; 32];
    let ptr = data.as_mut_ptr() as u64;
    check(call(0x26000, grant, ptr, 1) == -11, 904);
    for op in [0x26000, 0x26001] {
        check(call(op, grant ^ 1, ptr, 1) == -13, 905);
        check(call(op, grant, 0, 0) == 0, 906);
        check(call(op, grant, ptr, 257) == -14, 907);
        check(call(op, grant, u64::MAX, 2) == -14, 908);
        check(call(op, grant, 0x800fff, 2) == -14, 909);
    }
    check(call(0x26000, grant, 0x400000, 1) == -14, 910);
    for _ in 0..3 {
        let h = call(0x20000, factory, 0, 0);
        check(h > 0, 911);
        let mut terminal = false;
        for _ in 0..100000 {
            let status = call(0x20001, h as u64, 0, 0);
            if status != 0 {
                check(status == 1, 912);
                terminal = true;
                break;
            }
            call(0x1fffe, 0, 0, 0);
        }
        check(terminal && call(0x20002, h as u64, 0, 0) == 0, 913);
    }
    write(grant, b"CONSOLE READY\n");
    let expected = b"a\0\x1b\rZ9\n!";
    let mut used = 0;
    for _ in 0..1000000 {
        // Invalid calls must not consume queued UART bytes.
        check(call(0x26000, grant, 0x800fff, 2) == -14, 914);
        let n = call(
            0x26000,
            grant,
            ptr + used as u64,
            (expected.len() - used) as u64,
        );
        check(
            n == -11 || (n > 0 && n as usize <= expected.len() - used),
            915,
        );
        if n > 0 {
            used += n as usize;
        }
        if used == expected.len() {
            break;
        }
        call(0x1fffe, 0, 0, 0);
    }
    check(used == expected.len() && &data[..used] == expected, 901);
    write(grant, b"CONSOLE ECHO:");
    write(grant, &data[..used]);
    write(grant, b"\n0123456789abcdefghijklmnopqrstuv\n");
    check(call(0x26002, grant, 0, 0) == 0, 916);
    for op in 0x26000..=0x26002 {
        check(call(op, grant, ptr, 1) == -9, 917);
    }
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(918)
}
