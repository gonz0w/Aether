#![no_std]
#![no_main]
use core::arch::asm;
// Aether conformance client; replaceable by a separately authored fixture client.
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, quota: u64, page_size: u64) -> ! {
    if cfg!(fail_supervisor) {
        unsafe {
            asm!("ud2", options(noreturn));
        }
    }
    if abi != 1 || quota != 1 || page_size != 4096 {
        unsafe {
            finish(19);
        }
    }
    unsafe { supervisor(factory) }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { finish(18) }
}
unsafe fn call(operation: u64, handle: u64, value: u64) -> (u64, u64) {
    let status: u64;
    let result: u64;
    unsafe {
        asm!("int 0x80", inlateout("rax") operation => status,
        in("rdi") handle, in("rsi") value, lateout("rdx") result);
    }
    (status, result)
}
unsafe fn check(operation: u64, handle: u64, value: u64, expected: u64) -> u64 {
    let (status, result) = unsafe { call(operation, handle, value) };
    if status != expected {
        unsafe { finish(1) }
    }
    result
}
unsafe fn finish(value: u64) -> ! {
    unsafe {
        asm!("int 0x80", in("rax") 0u64, in("rsi") value, options(noreturn));
    }
}
unsafe fn supervisor(factory: u64) -> ! {
    unsafe {
        if check(30, factory, 0, 0) != 1 {
            finish(20);
        }
        check(34, 0, 0, 1);
        let observe = check(3, factory, 16, 0);
        check(37, observe, 1, 2);
        check(5, observe, 0, 0);
        let restricted_factory = check(3, factory, 1, 0);
        check(34, restricted_factory, 0, 2);
        check(5, restricted_factory, 0, 0);
        if check(34, factory, 0, 0) != 0 {
            finish(21);
        }
        let mut old_memory = 0;
        let mut old_task = 0;
        for generation in 1..=9 {
            let memory = check(10, factory, 0, 0);
            check(10, factory, 0, 3);
            check(12, memory, 0, 1); // Wrong object type, despite matching right bit.
            if generation > 1 {
                check(15, old_memory, 0, 1);
                check(12, old_task, 0, 1);
                if old_memory == memory {
                    finish(4);
                }
            }
            let restricted = check(3, memory, 1, 0);
            check(15, restricted, 0, 2);
            check(5, restricted, 0, 0);
            // Fill the remaining six holder slots; task creation must be atomic.
            for _ in 0..6 {
                check(3, memory, 1, 0);
            }
            check(11, factory, memory, 3);
            check(4, memory, 0, 0);
            let task = check(11, factory, memory, 0);
            check(11, factory, memory, 3);
            if check(31, task, 0, 0) != generation {
                finish(22);
            }
            check(31, memory, 0, 1);
            check(15, memory, 0, 6);
            let start_only = check(3, task, 1, 0);
            check(14, start_only, 0, 2);
            check(4, task, 0, 0);
            check(12, start_only, 0, 1);
            check(12, task, 0, 0);
            if generation < 9 {
                loop {
                    let result = check(13, task, 0, 0);
                    if result != 0 {
                        if result != if generation == 1 { 1 } else { 2 } {
                            finish(5);
                        }
                        break;
                    }
                    check(20, 0, 0, 0);
                }
                check(12, task, 0, 6);
            } else {
                // The last worker explicitly yields after dirtying its stack,
                // then remains runnable. Stop authority must handle this state.
                for _ in 0..4 {
                    check(20, 0, 0, 0);
                }
            }
            if generation < 9 {
                if check(34, factory, 0, 0) != generation {
                    finish(23);
                }
                check(37, factory, generation, 6);
            }
            check(14, task, 0, 0);
            check(31, task, 0, 1);
            let reason = if generation == 1 {
                1
            } else if generation == 9 {
                3
            } else {
                2
            };
            let detail = if generation == 1 {
                110
            } else if generation == 9 {
                0
            } else {
                14
            };
            if check(34, factory, 0, 0) != generation
                || check(35, factory, 0, 0) != reason
                || check(36, factory, 0, 0) != detail
            {
                finish(24);
            }
            check(37, factory, generation, 6);
            check(13, task, 0, 1);
            check(11, factory, memory, 6); // Dirty detached backing cannot be reattached.
            check(15, memory, 0, 0);
            check(15, memory, 0, 1);
            if check(34, factory, 0, 0) != generation
                || check(35, factory, 0, 0) != reason
                || check(36, factory, 0, 0) != detail
            {
                finish(25);
            }
            check(10, factory, 0, 6);
            check(37, factory, generation + 1, 1);
            check(37, factory, generation, 0);
            check(37, factory, generation, 1);
            if check(34, factory, 0, 0) != 0 {
                finish(26);
            }
            old_memory = memory;
            old_task = task;
        }
        finish(100);
    }
}
