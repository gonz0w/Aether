// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;
#[repr(C)]
struct Args {
    argc: u64,
    envc: u64,
    strings: [[u8; 32]; 8],
}
fn args(mode: &[u8]) -> Args {
    let mut a = Args {
        argc: 2,
        envc: 0,
        strings: [[0; 32]; 8],
    };
    a.strings[0][0] = b'h';
    for (i, b) in mode.iter().enumerate() {
        a.strings[1][i] = *b;
    }
    a
}
fn call(op: u64, a: u64, b: u64, c: u64, d: u64, e: u64) -> (i64, u64, u64) {
    let r: i64;
    let extra: u64;
    let kind: u64;
    unsafe {
        asm!("int 0x81",inlateout("rax")op=>r,in("rdi")a,in("rsi")b,inlateout("rdx")c=>extra,
        in("r10")d,inlateout("r8")e=>kind,in("r9")0u64,lateout("rcx")_,options(nostack));
    }
    (r, extra, kind)
}
fn ctl(op: u64, h: u64) -> (i64, u64, u64) {
    call(op, h, 0, 0, 0, 0)
}
fn end(n: u64) -> ! {
    ctl(0x20006, n);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool, n: u64) {
    if !ok {
        end(n);
    }
}

fn terminal(h: u64) {
    for _ in 0..1000000 {
        let state = ctl(0x20001, h);
        if state.0 != 0 {
            check(state.0 == 1 && state.2 == 1, 941);
            return;
        }
        ctl(0x1fffe, 0);
    }
    end(952)
}
fn launch(image: u64, slot: u64, mode: &[u8], reader: u64, writer: u64) -> u64 {
    let a = args(mode);
    let result: i64;
    // Synchronous native launch copies the complete stack-owned argument record;
    // endpoint ownership moves only after kernel validation succeeds.
    unsafe {
        asm!("int 0x81", inlateout("rax") (if reader == 0 {0x23000u64} else {0x23002u64}) => result,
             in("rdi") 0xa001u64, in("rsi") image, inlateout("rdx") slot => _,
             in("r10") &a, inlateout("r8") reader => _, inlateout("r9") writer => _, lateout("rcx") _);
    }
    check(result > 0, 953);
    result as u64
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    abi: u64,
    factory: u64,
    a: u64,
    b: u64,
    channels: u64,
    last_grant: u64,
) -> ! {
    check(
        abi == if cfg!(connections_console) { 18 } else { 12 }
            && factory == 0xa001
            && a == 0xc001
            && b == 0xc002
            && channels == 0xd001
            && last_grant
                == if cfg!(connections_console) {
                    0xc003
                } else {
                    0xe001
                },
        950,
    );
    if !cfg!(connections_console) {
        check(ctl(0x25000, last_grant).0 >= 0, 951);
    }
    let first = ctl(0x24000, channels);
    let second = ctl(0x24000, channels);
    check(first.0 > 0 && second.0 > 0, 954);
    let console = launch(a, 0, b"c", second.0 as u64, first.1);
    let peer = launch(b, 1, b"p", first.0 as u64, second.1);
    for endpoint in [first.0 as u64, first.1, second.0 as u64, second.1] {
        check(ctl(0x24003, endpoint).0 == -13, 955);
    }
    check(call(0x26003, 0xf001, console, 0, 0, 0).0 == 0, 956);
    check(ctl(0x26000, 0xf001).0 == -13, 957);
    terminal(peer);
    terminal(console);
    check(
        ctl(0x20002, peer).0 == 0 && ctl(0x20002, console).0 == 0,
        958,
    );
    for &slot in if cfg!(connections_console) {
        &[0, 1, 2, 0][..]
    } else {
        &[0][..]
    } {
        let fresh = launch(
            if cfg!(connections_console) {
                last_grant
            } else {
                a
            },
            slot,
            b"n",
            0,
            0,
        );
        terminal(fresh);
        check(ctl(0x20002, fresh).0 == 0, 959);
    }
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(960)
}
