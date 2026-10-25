#![no_std]
#![no_main]
use core::arch::asm;
unsafe fn call(op: u64, cap: u64) -> (u64, u64) {
    let status: u64;
    let value: u64;
    unsafe {
        asm!("int 0x80", inlateout("rax") op => status, in("rdi") cap, in("rsi") 0u64, lateout("rdx") value);
    }
    (status, value)
}
fn fail() -> ! {
    unsafe {
        asm!("ud2", options(noreturn));
    }
}
fn check(op: u64, cap: u64, expected: u64) -> u64 {
    let result = unsafe { call(op, cap) };
    if result.0 != expected {
        fail();
    }
    result.1
}
fn yield_cpu() {
    if unsafe { (0x800000 as *const u64).read_volatile() } != 0x51a7 {
        fail();
    }
    check(20, 0, 0);
}
fn command(op: u64, cap: u64) -> u64 {
    loop {
        let result = unsafe { call(op, cap) };
        if result.0 == 0 {
            return result.1;
        }
        if result.0 != 6 {
            fail();
        }
        yield_cpu();
    }
}
fn wait(cap: u64, wanted: u64) {
    loop {
        let result = unsafe { call(51, cap) };
        if result.0 == 0 && result.1 == wanted {
            return;
        }
        if result.0 != 0 && result.0 != 6 {
            fail();
        }
        yield_cpu();
    }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    fail()
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(mut control: u64) -> ! {
    if cfg!(fail_supervisor) {
        fail();
    }
    unsafe {
        (0x800000 as *mut u64).write_volatile(0x51a7);
        asm!("mov rax, [rax]", in("rax") 0x02000000u64, options(nostack));
    }
    check(40, 3u64 << 32, 1);
    check(1, 4u64 << 32, 1);
    check(51, 0, 1);
    check(50, control | 1, 2);
    check(52, control, 6);
    check(53, control, 6);
    for generation in 1u64..=5 {
        let terminal = if generation % 2 == 0 {
            (2u64 << 32) | 6
        } else {
            3u64 << 32
        };
        if generation % 2 != 0 {
            wait(control, (generation << 32) | 2);
            command(50, control);
        }
        wait(control, (generation << 32) | 3);
        if check(57, control | 1, 0) != terminal {
            fail();
        }
        check(53, control, 6);
        check(52, control, 6); // Memory reuse cannot outrun transport disposal.
        check(56, control | 1, 2);
        if command(56, control) != if generation < 5 { 1 } else { 0 } {
            fail();
        }
        yield_cpu();
        if check(57, control | 1, 0) != terminal {
            fail();
        }
        command(52, control);
        wait(control, (generation << 32) | 4);
        yield_cpu();
        if check(57, control | 1, 0) != terminal {
            fail();
        }
        if generation < 5 {
            command(53, control);
            wait(control, ((generation + 1) << 32) | 1);
            check(51, control, 1);
            control = ((generation + 1) << 32) | 0x100;
        } else {
            check(53, control, 3);
        }
    }
    yield_cpu();
    check(0, 0, 0);
    fail()
}
