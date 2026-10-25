#![no_std]
#![no_main]
use core::arch::asm;

// The v1 profile is deliberately single-holder, single-worker and finite.
const OK: u64 = 0;
const INVALID: u64 = 1;
const DENIED: u64 = 2;
const EXHAUSTED: u64 = 3;
const BUSY: u64 = 6;

fn invoke(op: u64, handle: u64, value: u64) -> (u64, u64) {
    let status;
    let result;
    unsafe {
        asm!("int 0x80", inlateout("rax") op => status,
             in("rdi") handle, in("rsi") value, lateout("rdx") result);
    }
    (status, result)
}
fn complete(code: u64) -> ! {
    unsafe { asm!("int 0x80", in("rax") 0u64, in("rsi") code, options(noreturn)); }
}
fn require(condition: bool, code: u64) {
    if !condition { complete(code); }
}
fn request(op: u64, handle: u64, value: u64, status: u64) -> u64 {
    let answer = invoke(op, handle, value);
    require(answer.0 == status, 200 + op);
    answer.1
}
#[derive(PartialEq)]
struct Terminal { instance: u64, reason: u64, detail: u64 }
fn observe(factory: u64) -> Terminal {
    Terminal {
        instance: request(34, factory, 0, OK),
        reason: request(35, factory, 0, OK),
        detail: request(36, factory, 0, OK),
    }
}
fn expected(instance: u64) -> Terminal {
    let (reason, detail) = match instance {
        1 => (1, if cfg!(wrong_detail) { 111 } else { 110 }),
        9 => (3, 0),
        _ => (2, 14),
    };
    Terminal { instance, reason, detail }
}
fn check_record(factory: u64, instance: u64) {
    let first = observe(factory);
    require(first == expected(instance), 310 + instance);
    require(observe(factory) == first, 330 + instance);
}

#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, quota: u64, page: u64) -> ! {
    if cfg!(fault_entry) {
        unsafe { asm!("ud2", options(noreturn)); }
    }
    require(abi == 1 && quota == 1 && page == 4096, 301);
    require(request(30, factory, 0, OK) == 1, 302);
    require(observe(factory) == Terminal { instance: 0, reason: 0, detail: 0 }, 303);
    request(34, 0, 0, INVALID);
    // Observe authority never permits acknowledgment.
    let reader = request(3, factory, 16, OK);
    request(37, reader, 1, DENIED);
    request(5, reader, 0, OK);
    let allocator = request(3, factory, 1, OK);
    request(34, allocator, 0, DENIED);
    request(5, allocator, 0, OK);

    let mut previous_task = 0;
    let mut previous_memory = 0;
    for instance in 1..=9 {
        let memory = request(10, factory, 0, OK);
        request(10, factory, 0, EXHAUSTED);
        request(12, memory, 0, INVALID);
        if instance > 1 {
            request(12, previous_task, 0, INVALID);
            request(15, previous_memory, 0, INVALID);
            require(memory != previous_memory, 304);
        }
        let attach_only = request(3, memory, 1, OK);
        request(15, attach_only, 0, DENIED);
        request(5, attach_only, 0, OK);
        // Exhaust holder slots: rejected creation must leave quota untouched.
        for _ in 0..6 { request(3, memory, 1, OK); }
        request(11, factory, memory, EXHAUSTED);
        request(4, memory, 0, OK);
        let task = request(11, factory, memory, OK);
        require(request(31, task, 0, OK) == instance, 305);
        request(31, memory, 0, INVALID);
        request(11, factory, memory, EXHAUSTED);
        request(15, memory, 0, BUSY);
        let start_only = request(3, task, 1, OK);
        request(14, start_only, 0, DENIED);
        request(4, task, 0, OK);
        request(12, start_only, 0, INVALID);
        request(12, task, 0, OK);
        if instance == 9 {
            // Fixture 9 must dirty backing before the explicit live stop.
            for _ in 0..4 { request(20, 0, 0, OK); }
        } else {
            loop {
                let state = request(13, task, 0, OK);
                if state != 0 {
                    require(state == if instance == 1 { 1 } else { 2 }, 306);
                    break;
                }
                request(20, 0, 0, OK);
            }
            check_record(factory, instance);
            request(37, factory, instance, BUSY);
            request(12, task, 0, BUSY);
        }
        request(14, task, 0, OK);
        request(13, task, 0, INVALID);
        check_record(factory, instance);
        request(37, factory, instance, BUSY);
        request(11, factory, memory, BUSY);
        request(15, memory, 0, OK);
        request(15, memory, 0, INVALID);
        check_record(factory, instance);
        // Observe -> destroy -> release -> acknowledge is the policy invariant.
        request(10, factory, 0, BUSY);
        request(37, factory, instance + 1, INVALID);
        check_record(factory, instance);
        request(37, factory, instance, OK);
        request(37, factory, instance, INVALID);
        require(observe(factory) == Terminal { instance: 0, reason: 0, detail: 0 }, 307);
        previous_task = task;
        previous_memory = memory;
    }
    complete(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { complete(399) }
