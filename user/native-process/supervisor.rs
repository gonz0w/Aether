// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;
#[path = "../native-launch/namespace.rs"]
mod namespace;
#[repr(C)]
struct Args {
    argc: u64,
    envc: u64,
    strings: [[u8; 32]; 8],
}
fn args(name: &[u8]) -> Args {
    let mut a = Args {
        argc: 1,
        envc: 0,
        strings: [[0; 32]; 8],
    };
    a.strings[0][..name.len()].copy_from_slice(name);
    a
}
#[inline(never)]
fn call(op: u64, a: u64, b: u64, c: u64, d: u64, e: u64, f: u64) -> (i64, u64, u64) {
    let r: i64;
    let x: u64;
    let k: u64;
    unsafe {
        asm!("int 0x81",inlateout("rax")op=>r,in("rdi")a,in("rsi")b,inlateout("rdx")c=>x,in("r10")d,inlateout("r8")e=>k,in("r9")f,lateout("rcx")_,options(nostack));
    }
    (r, x, k)
}
fn ctl(op: u64, h: u64) -> (i64, u64, u64) {
    call(op, h, 0, 0, 0, 0, 0)
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
fn terminal(h: u64) -> (u32, u32) {
    for _ in 0..100000 {
        let s = ctl(0x20001, h);
        if s.0 > 0 {
            return ((s.0 - 1) as u32, s.2 as u32);
        }
        check(s.0 == 0, 911);
        ctl(0x1fffe, 0);
    }
    end(912)
}
fn transfer(cap: u64, b: &mut [u8; 32], write: bool) -> i32 {
    let mut n = 0;
    for _ in 0..100000 {
        let r = call(
            if write { 0x24002 } else { 0x24001 },
            cap,
            b[n..].as_mut_ptr() as u64,
            (32 - n) as u64,
            0,
            0,
            0,
        )
        .0;
        if r == -11 {
            ctl(0x1fffe, 0);
            continue;
        }
        if r == 0 && !write {
            return if n == 0 { 0 } else { -1 };
        }
        if r <= 0 || r as usize > 32 - n {
            return -1;
        }
        n += r as usize;
        if n == 32 {
            return 1;
        }
    }
    -1
}
fn get(b: &[u8; 32], i: usize) -> u32 {
    u32::from_le_bytes(b[i..i + 4].try_into().unwrap())
}
fn put(b: &mut [u8; 32], i: usize, v: u32) {
    b[i..i + 4].copy_from_slice(&v.to_le_bytes());
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    abi: u64,
    factory: u64,
    requester_image: u64,
    worker_image: u64,
    channels: u64,
    program_image: u64,
) -> ! {
    check(
        abi == if cfg!(program) {
            8
        } else if cfg!(coexist) {
            7
        } else {
            5
        } && factory == 0xa001
            && requester_image == 0xc001
            && worker_image == 0xc002
            && channels == 0xd001,
        900,
    );
    if cfg!(program) {
        check(program_image == 0xc003, 930);
    }
    let req = ctl(0x24000, channels);
    let rep = ctl(0x24000, channels);
    check(req.0 > 0 && rep.0 > 0, 901);
    let a = args(b"requester");
    let requester = call(
        0x23002,
        factory,
        requester_image,
        0,
        &a as *const Args as u64,
        rep.0 as u64,
        req.1,
    )
    .0 as u64;
    check(
        requester == 0xb0000101
            && ctl(0x24003, req.1).0 == -13
            && ctl(0x24003, rep.0 as u64).0 == -13,
        902,
    );
    let entries = [namespace::Entry {
        name: b"worker",
        executable: worker_image,
    }];
    let scope = namespace::Namespace { entries: &entries };
    let mut program_child = 0;
    let mut program_ticket = 0u32;
    let mut program_generation = 0u32;
    let mut backend_read = 0;
    let mut backend_write = 0;
    let mut child = 0;
    let mut ticket = 0u32;
    let mut generation = 0u32;
    let mut cached = (0, 0);
    let healthy;
    loop {
        let mut request = [0u8; 32];
        let received = transfer(req.0 as u64, &mut request, false);
        if received != 1 {
            healthy = received == 0;
            break;
        }
        let mut reply = [0u8; 32];
        let op = get(&request, 0);
        let mut payload = [0u8; 32];
        if cfg!(coexist) && op == 3 && transfer(req.0 as u64, &mut payload, false) != 1 {
            healthy = false;
            break;
        }
        let supplied = get(&request, 4);
        let inherit = get(&request, 8);
        let mut result = -22i64;
        if get(&request, 12) == 1 {
            if op == 1 && supplied == 0 {
                if inherit != 0 && !cfg!(allow_inherit) {
                    result = -95;
                } else if let Some(n) = request[16..].iter().position(|b| *b == 0) {
                    if request[16 + n..].iter().all(|b| *b == 0) {
                        let name = &request[16..16 + n];
                        let selected = if cfg!(wide_scope) && name == b"requester" {
                            Ok(requester_image)
                        } else {
                            scope.lookup(name)
                        };
                        match selected {
                            Err(e) => result = e,
                            Ok(exec) => {
                                if ticket != 0 {
                                    result = -16;
                                } else {
                                    let a = args(b"worker");
                                    let h = if cfg!(coexist) {
                                        let values = backend_launch(factory, exec, channels);
                                        backend_read = values.1;
                                        backend_write = values.2;
                                        values.0
                                    } else {
                                        call(
                                            0x23000,
                                            factory,
                                            exec,
                                            1,
                                            &a as *const Args as u64,
                                            0,
                                            0,
                                        )
                                        .0
                                    };
                                    result = if h < 0 { h } else { 0 };
                                    if h > 0 {
                                        child = h as u64;
                                        generation += 1;
                                        ticket = 0x51000000 | generation;
                                        put(&mut reply, 4, ticket);
                                        if cfg!(coexist) {
                                            let mut hello = [0u8; 32];
                                            check(
                                                transfer(backend_read, &mut hello, false) == 1
                                                    && get(&hello, 0) == 0,
                                                924,
                                            );
                                            put(&mut reply, 8, get(&hello, 4));
                                            put(&mut reply, 12, get(&hello, 8));
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            } else if op == 2 && inherit == 0 && request[16..].iter().all(|b| *b == 0) {
                if cfg!(program) && program_child != 0 {
                    result = -16;
                } else if ticket == 0 || supplied != ticket {
                    result = -10;
                } else {
                    if child != 0 {
                        if cfg!(coexist) {
                            check(ctl(0x24003, backend_write).0 == 0, 925);
                            backend_write = 0;
                        }
                        cached = terminal(child);
                        if cfg!(coexist) {
                            check(ctl(0x24003, backend_read).0 == 0, 926);
                            backend_read = 0;
                        }
                        check(ctl(0x20002, child).0 == 0, 910);
                        child = 0;
                    }
                    result = 0;
                    put(&mut reply, 4, ticket);
                    put(&mut reply, 8, cached.0);
                    put(&mut reply, 12, cached.1);
                    if !cfg!(repeat_collect) {
                        ticket = 0;
                    }
                }
            } else if cfg!(coexist)
                && op == 3
                && inherit == 0
                && request[16..].iter().all(|b| *b == 0)
            {
                if ticket == 0 || supplied != ticket || child == 0 {
                    result = -10;
                } else {
                    check(
                        transfer(backend_write, &mut payload, true) == 1
                            && transfer(backend_read, &mut payload, false) == 1,
                        927,
                    );
                    reply = payload;
                    result = get(&reply, 0) as i32 as i64;
                }
            } else if cfg!(program) && op == 4 && supplied == 0 {
                if inherit != 0 {
                    result = -95;
                } else if request[16..] != *b"program\0\0\0\0\0\0\0\0\0" {
                    result = -2;
                } else if program_child != 0 {
                    result = -16;
                } else if child == 0 {
                    result = -10;
                } else {
                    let a = args(b"program");
                    let h = call(
                        0x23000,
                        factory,
                        program_image,
                        2,
                        &a as *const Args as u64,
                        0,
                        0,
                    )
                    .0;
                    result = if h < 0 { h } else { 0 };
                    if h > 0 {
                        program_child = h as u64;
                        program_generation += 1;
                        program_ticket = 0x52000000 | program_generation;
                        program_ready(program_child);
                        put(&mut reply, 4, program_ticket);
                    }
                }
            } else if cfg!(program)
                && op == 5
                && inherit == 0
                && request[16..].iter().all(|b| *b == 0)
            {
                if program_child == 0 || supplied != program_ticket {
                    result = -10;
                } else {
                    check(
                        ctl(0x20001, program_child).0 == 0 && ctl(0x20003, program_child).0 == 80,
                        934,
                    );
                    if !cfg!(program_skip_stop) {
                        check(ctl(0x20007, program_child).0 == 0, 935);
                    }
                    let stopped = ctl(0x20001, program_child);
                    check(stopped.0 == 144 && stopped.2 == 3, 936);
                    check(
                        ctl(0x20002, program_child).0 == 0 && ctl(0x20001, program_child).0 == -9,
                        937,
                    );
                    result = 0;
                    put(&mut reply, 4, program_ticket);
                    put(&mut reply, 8, 143);
                    put(&mut reply, 12, 3);
                    program_child = 0;
                    program_ticket = 0;
                }
            } else if op != 1
                && op != 2
                && !(cfg!(coexist) && op == 3)
                && !(cfg!(program) && (op == 4 || op == 5))
            {
                result = -38;
            }
        }
        put(&mut reply, 0, result as i32 as u32);
        if transfer(rep.1, &mut reply, true) != 1 {
            healthy = false;
            break;
        }
    }
    if cfg!(program) && program_child != 0 {
        check(ctl(0x20007, program_child).0 == 0, 938);
        terminal(program_child);
        check(ctl(0x20002, program_child).0 == 0, 939);
    }
    // EOF/failed transport closes this connection's admission, then releases its inventory.
    if cfg!(coexist) {
        if backend_write != 0 {
            check(ctl(0x24003, backend_write).0 == 0, 928);
        }
        if backend_read != 0 {
            check(ctl(0x24003, backend_read).0 == 0, 929);
        }
    }
    if child != 0 {
        check(ctl(0x20007, child).0 == 0, 913);
        terminal(child);
        check(ctl(0x20002, child).0 == 0, 914);
    }
    check(
        ctl(0x24003, req.0 as u64).0 == 0 && ctl(0x24003, rep.1).0 == 0,
        915,
    );
    let outcome = terminal(requester);
    check(ctl(0x20002, requester).0 == 0, 916);
    check(
        healthy
            && outcome == (29, 1)
            && generation == 2
            && ticket == 0
            && (!cfg!(program) || (program_child == 0 && program_generation == 2)),
        903,
    );
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(999)
}

// Allocate only this backend's explicit pair and roll it back on failed admission.
#[allow(dead_code)]
fn backend_launch(factory: u64, exec: u64, channels: u64) -> (i64, u64, u64) {
    let a = ctl(0x24000, channels);
    if a.0 < 0 {
        return (a.0, 0, 0);
    }
    let b = ctl(0x24000, channels);
    if b.0 < 0 {
        ctl(0x24003, a.0 as u64);
        ctl(0x24003, a.1);
        return (b.0, 0, 0);
    }
    check(ctl(0x24000, channels).0 == -16, 920);
    let mut args = args(b"worker");
    args.argc = 5;
    check(
        call(
            0x23002,
            factory,
            exec,
            1,
            &args as *const Args as u64,
            a.0 as u64,
            b.1,
        )
        .0 == -22,
        921,
    );
    check(
        call(0x24001, a.0 as u64, 0, 0, 0, 0, 0).0 == 0 && call(0x24002, b.1, 0, 0, 0, 0, 0).0 == 0,
        922,
    );
    args.argc = 1;
    let h = call(
        0x23002,
        factory,
        exec,
        1,
        &args as *const Args as u64,
        a.0 as u64,
        b.1,
    )
    .0;
    if h < 0 {
        for cap in [a.0 as u64, a.1, b.0 as u64, b.1] {
            check(ctl(0x24003, cap).0 == 0, 923);
        }
        return (h, 0, 0);
    }
    check(
        ctl(0x24003, a.0 as u64).0 == -13 && ctl(0x24003, b.1).0 == -13,
        923,
    );
    (h, b.0 as u64, a.1)
}

#[allow(dead_code)]
fn program_ready(h: u64) {
    for _ in 0..100000 {
        let s = ctl(0x20001, h);
        check(s.0 == 0, 933);
        if s.1 == 1 {
            return;
        }
        ctl(0x1fffe, 0);
    }
    end(932)
}
