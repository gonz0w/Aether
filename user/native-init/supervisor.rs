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
fn clock() -> u64 {
    let n = ctl(0x25000, 0xe001).0;
    check(n >= 0, 700);
    n as u64
}
fn wait(op: u64, h: u64) -> (i64, u64, u64) {
    call(op, 0xe001, h, 0, 0, 0)
}
fn register(h: u64, revision: u64, deadline: u64) -> i64 {
    call(0x25002, 0xe001, h, revision, deadline, 0).0
}
fn terminal(h: u64, detail: i64) {
    for _ in 0..100000 {
        let s = ctl(0x20001, h);
        if s.0 != 0 {
            check(s.0 == detail + 1, 711);
            return;
        }
        ctl(0x1fffe, 0);
    }
    end(712)
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    abi: u64,
    factory: u64,
    first: u64,
    _second: u64,
    streams: u64,
    observation: u64,
) -> ! {
    check(
        abi == if cfg!(init_composed) {
            16
        } else if cfg!(init_large) {
            15
        } else {
            6
        } && factory == 0xa001
            && first == 0xc001
            && (!cfg!(init_large) || _second == 0xc002)
            && streams == 0xd001
            && observation == 0xe001,
        710,
    );
    if cfg!(sequential) || cfg!(sequential_reverse) {
        // SI-04: loading another slot must not restore a retired image's
        // read-only backing aliases before that slot is reused.
        let order = if cfg!(sequential_reverse) {
            [1, 0, 1]
        } else {
            [0, 1, 0]
        };
        for slot in order {
            let channel = ctl(0x24000, streams);
            check(channel.0 > 0, 740);
            let a = args(b"exit");
            let child = call(
                0x23001,
                factory,
                first,
                slot,
                &a as *const Args as u64,
                channel.1,
            )
            .0;
            check(child > 0, 741);
            terminal(child as u64, 17);
            check(ctl(0x24003, channel.0 as u64).0 == 0, 742);
            check(ctl(0x20002, child as u64).0 == 0, 743);
            check(ctl(0x20001, child as u64).0 == -9, 744);
        }
        end(100);
    }
    check(
        ctl(0x25000, 0).0 == -13 && wait(0x25001, 0xb0000101).0 == -9,
        713,
    );
    let channel = ctl(0x24000, streams);
    let read = channel.0 as u64;
    let write = channel.1;
    check(channel.0 > 0, 714);
    let mut a = args(b"exit");
    a.argc = 5;
    check(
        call(0x23001, factory, first, 0, &a as *const Args as u64, write).0 == -22,
        715,
    );
    check(call(0x24002, write, 0, 0, 0, 0).0 == 0, 716);
    a.argc = 2;
    let child = call(0x23001, factory, first, 0, &a as *const Args as u64, write).0 as u64;
    check(child == 0xb0000101 && ctl(0x24003, write).0 == -13, 717);
    let t = register(child, 0, clock() + 100) as u64;
    for _ in 0..100000 {
        if wait(0x25003, t).0 != 0 {
            break;
        }
        ctl(0x1fffe, 0);
    }
    check(
        wait(0x25003, t).0 == 1 && wait(0x25005, t).0 == 0 && wait(0x25003, t).0 == -9,
        718,
    );
    terminal(child, 17);
    let before = register(child, 0, clock() + 100) as u64;
    check(
        wait(0x25003, before).0 == 1 && wait(0x25005, before).0 == 0,
        719,
    );
    let obs = wait(0x25001, child);
    check(obs.0 == 2 && obs.1 == 18 && obs.2 == 1, 720);
    let boundary = register(child, 2, clock()) as u64;
    check(
        wait(0x25003, boundary).0 == if cfg!(bad_deadline) { 1 } else { 2 },
        701,
    );
    check(wait(0x25005, boundary).0 == 0, 721);
    let cancel = register(child, 2, clock() + 100) as u64;
    check(register(child, 2, clock() + 100) == -16, 722);
    check(
        wait(0x25004, cancel).0 == 3
            && wait(0x25003, cancel).0 == 3
            && wait(0x25005, cancel).0 == 0,
        723,
    );
    // Delayed timer completion with no lifecycle event, not a fixture iteration timeout.
    let deadline = clock() + 2;
    let timed = register(child, 2, deadline) as u64;
    loop {
        let s = wait(0x25003, timed);
        if s.0 != 0 {
            check(s.0 == 2 && s.2 >= deadline, 724);
            break;
        }
        ctl(0x1fffe, 0);
    }
    check(wait(0x25005, timed).0 == 0, 725);
    let second_channel = ctl(0x24000, streams);
    check(second_channel.0 > 0, 726);
    let b = args(b"live");
    let helper = call(
        0x23001,
        factory,
        first,
        1,
        &b as *const Args as u64,
        second_channel.1,
    )
    .0 as u64;
    check(helper == 0xb0000102, 727);
    loop {
        if ctl(0x20001, helper).1 == 1 {
            break;
        }
        ctl(0x1fffe, 0);
    }
    let retained = register(child, 2, clock() + 100) as u64;
    if cfg!(owner_exit) {
        ctl(0x1003c, 0);
        end(728);
    }
    if cfg!(owner_fault) {
        unsafe {
            asm!("ud2", options(noreturn));
        }
    }
    // Buffered late readiness is transport data; terminal owner cannot be admitted.
    let mut data = [0u8; 16];
    check(
        call(0x24001, read, data.as_mut_ptr() as u64, 16, 0, 0).0 == 1 && data[0] == 42,
        729,
    );
    let admissible = ctl(0x20001, child).0 == 0;
    check(admissible == cfg!(bad_late), 702);
    check(
        call(0x24001, read, data.as_mut_ptr() as u64, 16, 0, 0).0 == 0 && ctl(0x24003, read).0 == 0,
        730,
    );
    check(
        ctl(0x20002, child).0 == 0
            && wait(0x25003, retained).0 == 4
            && wait(0x25005, retained).0 == 0,
        731,
    );
    check(wait(0x25001, child).0 == -9, 732);
    // Main termination does not kill its independently launched helper; explicit stop does.
    check(
        ctl(0x20001, helper).0 == 0 && ctl(0x20007, helper).0 == 0,
        733,
    );
    terminal(helper, 143);
    check(
        ctl(0x20002, helper).0 == 0 && ctl(0x24003, second_channel.0 as u64).0 == 0,
        734,
    );
    let fresh = ctl(0x24000, streams);
    check(fresh.0 > 0 && fresh.0 as u64 != read, 735);
    check(
        call(0x24001, read, data.as_mut_ptr() as u64, 1, 0, 0).0 == -13,
        736,
    );
    check(
        call(0x24001, fresh.0 as u64, data.as_mut_ptr() as u64, 1, 0, 0).0 == -11,
        737,
    );
    let c = args(b"stale");
    let replacement = call(
        0x23001,
        factory,
        first,
        0,
        &c as *const Args as u64,
        fresh.1,
    )
    .0 as u64;
    check(replacement == 0xb0000201, 738);
    terminal(replacement, 33);
    let revision = wait(0x25001, replacement).0 as u64;
    let mut exhausted = false;
    let mut available = 0;
    for _ in 0..65 {
        let token = register(replacement, revision, clock() + 100);
        if token == -28 {
            exhausted = true;
            break;
        }
        available += 1;
        check(token > 0 && wait(0x25005, token as u64).0 == 0, 739);
    }
    check(
        exhausted
            && available == 58
            && ctl(0x20002, replacement).0 == 0
            && ctl(0x24003, fresh.0 as u64).0 == 0,
        740,
    );
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(799)
}
