#![no_std]
#![no_main]

use core::arch::asm;

// Test program, not a service ABI. Each case runs in a fresh protection domain.
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    case: usize,
    grant: u64,
    stack: u64,
    old_stack: u64,
    fresh_stack: u64,
) -> ! {
    unsafe {
        if cfg!(bad_fixture) {
            exit(0);
        }
        match case {
            0 => asm!("mov rax, [rax]", in("rax") 0xffffffff80000000u64, options(nostack)),
            1 => asm!("mov byte ptr [rax], 0", in("rax") 0x400000usize, options(nostack)),
            2 => {
                // Valid RET instruction on writable memory must still fail NX.
                asm!("mov byte ptr [rax], 0xc3", "jmp rax", in("rax") 0x800000usize, options(noreturn));
            }
            3 => asm!("out dx, al", in("dx") 0x3f8u16, in("al") 0u8, options(nostack)),
            4 => asm!("mov rax, [rax]", in("rax") 0usize, options(nostack)),
            5 => {
                let bottom = 0x800000 as *mut u64;
                if bottom.read_volatile() != 0 {
                    exit(1);
                }
                bottom.write_volatile(21);
                exit(bottom.read_volatile() * 2);
            }
            6 | 7 | 12 | 13 => {
                if case >= 12 {
                    swarm(case, grant);
                }
                asm!(
                    "xor rax, rax",
                    "mov rbx, 257",
                    "mov rcx, 258",
                    "mov rdx, 259",
                    "mov rbp, 260",
                    "mov rsi, 261",
                    "mov r8, 264",
                    "mov r9, 265",
                    "mov r10, 272",
                    "mov r11, 273",
                    "mov r12, 4660",
                    "mov r13, 22136",
                    "mov r14, 276",
                    "mov r15, 277",
                    "mov qword ptr [0x800000], rdi",
                    "2:",
                    "cmp qword ptr [0x800000], rdi",
                    "jne 4f",
                    "cmp rbx, 257",
                    "jne 4f",
                    "cmp rcx, 258",
                    "jne 4f",
                    "cmp rdx, 259",
                    "jne 4f",
                    "cmp rbp, 260",
                    "jne 4f",
                    "cmp rsi, 261",
                    "jne 4f",
                    "cmp r8, 264",
                    "jne 4f",
                    "cmp r9, 265",
                    "jne 4f",
                    "cmp r10, 272",
                    "jne 4f",
                    "cmp r11, 273",
                    "jne 4f",
                    "cmp r12, 4660",
                    "jne 4f",
                    "cmp r13, 22136",
                    "jne 4f",
                    "cmp r14, 276",
                    "jne 4f",
                    "cmp r15, 277",
                    "jne 4f",
                    "inc rax",
                    "cmp rdi, 7",
                    "je 2b",
                    "cmp rdi, 12",
                    "je 2b",
                    "cmp rax, 20000000",
                    "jb 2b",
                    "xor rcx, rcx",
                    "cmp rdi, 13",
                    "jne 5f",
                    "mov rcx, 0x02000000",
                    "mov rcx, [rcx]", // Worker has no framebuffer grant or mapping.
                    "mov rcx, 0x01000000",
                    "mov rcx, [rcx]", // Must fault; kernel skips this three-byte probe.
                    "mov rcx, 0xfee00000", // AP worker must not read kernel APIC MMIO.
                    "5: mov rcx, [rcx]",
                    "4: ud2",
                    in("rdi") case,
                    options(noreturn)
                );
            }
            8 => sender(grant),
            9 => receiver(grant),
            11 => worker(grant, stack, old_stack),
            14 => publish(grant, stack, old_stack, fresh_stack),
            _ => exit(2),
        }
        // Reaching here means the expected hardware protection failed.
        exit(3);
    }
}

unsafe fn exit(status: u64) -> ! {
    unsafe {
        asm!("int 0x80", in("rax") status, options(noreturn));
    }
}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { exit(u64::MAX) }
}

// Transitional register-only endpoint ABI. No user pointers cross the boundary.
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
unsafe fn sender(root: u64) -> ! {
    unsafe {
        check(1, 0, 0, 1);
        check(2, root, 0, 2);
        check(3, root, 2, 2); // Cannot add receive rights.
        let child = check(3, root, 13, 0);
        let grandchild = check(3, child, 1, 0);
        check(5, child, 0, 6); // Descendants require explicit revoke.
        check(4, root, 0, 0);
        check(1, child, 0, 1);
        check(1, grandchild, 0, 1);
        let fresh = check(3, root, 1, 0);
        if fresh == child {
            finish(2);
        }
        check(5, fresh, 0, 0);
        check(1, fresh, 0, 1);
        for _ in 0..7 {
            check(3, root, 1, 0);
        }
        check(3, root, 1, 3);
        check(4, root, 0, 0);
        for value in 10..14 {
            check(1, root, value, 0);
        }
        check(1, root, 99, 4);
        finish(80);
    }
}
unsafe fn receiver(root: u64) -> ! {
    unsafe {
        check(1, root, 99, 2);
        for value in 10..14 {
            if check(2, root, 0, 0) != value + u64::from(cfg!(bad_ipc)) {
                finish(3);
            }
        }
        check(2, root, 0, 5);
        check(6, root, 0, 0);
        check(2, root, 0, 1);
        finish(90);
    }
}

unsafe fn worker(generation: u64, stack: u64, old_stack: u64) -> ! {
    unsafe {
        // Leave room for this function's own active stack frames at the top.
        for offset in 0..3840 {
            if ((stack + offset) as *const u8).read_volatile() != 0 {
                finish(6);
            }
        }
        for offset in 0..3840 {
            ((stack + offset) as *mut u8).write_volatile(generation as u8);
        }
        if generation == 9 {
            loop {
                check(20, 0, 0, 0);
            }
        }
        if old_stack != 0 {
            asm!("mov rax, [rax]", in("rax") old_stack, options(nostack));
            finish(7); // A stale mapping was accessible.
        }
        finish(110);
    }
}

// Retry only transient queue states. Local timer watchdogs bound stalled peers.
unsafe fn exchange(operation: u64, handle: u64, value: u64) -> u64 {
    unsafe {
        loop {
            let (status, result) = call(operation, handle, value);
            if status == 0 {
                return result;
            }
            if status != if operation == 1 { 4 } else { 5 } {
                finish(8);
            }
        }
    }
}
unsafe fn swarm(case: usize, request: u64) {
    unsafe {
        let reply = request | 1;
        let ready = request | 2;
        check(1, 0, 0, 1);
        check(1, request ^ (3u64 << 32), 0, 1); // Peer namespace confers no grant.
        check(1, request | 3, 0, 1);
        check(if case == 12 { 2 } else { 1 }, request, 0, 2);
        if case == 12 {
            if exchange(2, ready, 0) != 1 {
                finish(9);
            }
            for value in 0..4 {
                if exchange(2, reply, 0) != value {
                    finish(10);
                }
            }
            for value in 0..100 {
                exchange(1, request, value);
                if exchange(2, reply, 0) != value * 3 + 1 + u64::from(cfg!(bad_smp_ipc)) {
                    finish(11);
                }
            }
        } else {
            for value in 0..4 {
                check(1, reply, value, 0);
            }
            check(1, reply, 999, 4);
            check(1, ready, 1, 0);
            for value in 0..100 {
                if exchange(2, request, 0) != value {
                    finish(12);
                }
                exchange(1, reply, value * 3 + 1);
            }
        }
        check(0, 0, if case == 12 { 120 } else { 130 }, 0);
    }
}

unsafe fn publish(request: u64, first: u64, old_stack: u64, fresh_stack: u64) -> ! {
    unsafe {
        asm!("mov rax, [rax]", in("rax") 0x02000000u64, options(nostack));
        check(1, 0, 0, 1);
        check(1, 2u64 << 32, 0, 1); // Previous M3 namespace is not authority here.
        check(1, request, 0, 2);
        if old_stack != 0 {
            asm!("mov rax, [rax]", in("rax") old_stack, options(nostack));
        }
        if (fresh_stack as *const u64).read_volatile() != 0 {
            finish(15);
        }
        (fresh_stack as *mut u64).write_volatile(0xfeedface);
        check(50, (1u64 << 32) | 0x100, 0, 1);
        let generation = (first - 1) / 20 + 1;
        let mut sum = first * (first - 1) / 2;
        for sequence in first..first + 20 {
            sum += sequence;
            let tag = if cfg!(bad_stream_generation) && sequence == 21 {
                1
            } else {
                generation
            };
            let value = (tag << 56)
                | (sequence << 32)
                | (sum + u64::from(cfg!(bad_display_message) && sequence == 50));
            exchange(1, request | 1, value);
            if exchange(2, request, 0) != sequence {
                finish(13);
            }
        }
        if generation < 5 {
            let next = first + 20;
            exchange(
                1,
                request | 1,
                (generation << 56) | (next << 32) | (next * (next + 1) / 2),
            );
        }
        if generation % 2 == 0 {
            asm!("ud2", options(noreturn));
        }
        check(0, 0, 140, 0);
        loop {
            asm!("pause", options(nomem, nostack));
        }
    }
}
