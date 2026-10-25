// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
#[cfg(all(init_sustained_v2, not(init_sustained)))]
compile_error!("v2 command wire requires the selected sustained owner profile");
use core::arch::asm;
#[cfg(command_runner)]
#[path = "../native-command/owner.rs"]
mod command;
#[cfg(process_copy)]
mod copy;
#[cfg(process_exec)]
mod exec;
#[cfg(any(exec_streams, fork_exec, pipe_exec, scratch_exec))]
mod exec_fds;
#[cfg(process_freeze)]
mod freeze;
#[cfg(any(process_inherit, exec_streams))]
mod inherit;
#[cfg(shell_null)]
mod null;
#[cfg(any(scratch_owner_probe, scratch_client, shell_files))]
mod scratch_owner;
#[cfg(shared_files)]
#[path = "../native-shared/owner.rs"]
mod shared;
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
#[cfg_attr(any(fork_dispatch, command_runner), inline(never))]
fn ctl(op: u64, h: u64) -> (i64, u64, u64) {
    call(op, h, 0, 0, 0, 0, 0)
}
fn end(n: u64) -> ! {
    #[cfg(init_sustained)]
    {
        // Test failures must stay observable when fixture finish is unsupported.
        for byte in b"SI07 fixture failure\n" {
            let _ = call(0x26001, 0xf001, byte as *const u8 as u64, 1, 0, 0, 0);
        }
        unsafe { asm!("ud2", options(noreturn)) }
    }
    #[cfg(not(init_sustained))]
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
#[inline(never)]
fn transfer(cap: u64, b: &mut [u8; 32], write: bool) -> i32 {
    transfer_bounded(cap, b, write, 100000)
}
fn transfer_bounded(cap: u64, b: &mut [u8], write: bool, attempts: usize) -> i32 {
    let original = b.len();
    let mut remaining = b;
    for _ in 0..attempts {
        let r = call(
            if write { 0x24002 } else { 0x24001 },
            cap,
            remaining.as_mut_ptr() as u64,
            remaining.len() as u64,
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
            return if remaining.len() == original { 0 } else { -1 };
        }
        if r <= 0 || r as usize > remaining.len() {
            return -1;
        }
        remaining = &mut remaining[r as usize..];
        if remaining.is_empty() {
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
#[derive(Clone, Copy)]
struct Connection {
    reader: u64,
    writer: u64,
    child: u64,
}
fn launch(factory: u64, image: u64, slot: u64) -> Connection {
    let req = ctl(0x24000, 0xd001);
    let rep = ctl(0x24000, 0xd001);
    check(req.0 > 0 && rep.0 > 0, 950);
    let a = args(
        if slot == (if cfg!(cat_parent_swap) { 0 } else { 1 })
            || (cfg!(cat_file_service) && slot == 2)
            || ((cfg!(inherit_rollback) || cfg!(exec_streams)) && slot == 2)
        {
            b"worker"
        } else {
            b"client"
        },
    );
    // Invalid startup leaves both transfer endpoints with the caller.
    let mut invalid = args(b"client");
    invalid.argc = 5;
    check(
        call(
            0x23002,
            factory,
            image,
            slot,
            &invalid as *const Args as u64,
            req.0 as u64,
            rep.1,
        )
        .0 == -22,
        951,
    );
    check(
        call(0x24001, req.0 as u64, 0, 0, 0, 0, 0).0 == 0
            && call(0x24002, rep.1, 0, 0, 0, 0, 0).0 == 0,
        951,
    );
    let child = call(
        0x23002,
        factory,
        image,
        slot,
        &a as *const Args as u64,
        req.0 as u64,
        rep.1,
    )
    .0;
    check(
        child > 0 && ctl(0x24003, req.0 as u64).0 == -13 && ctl(0x24003, rep.1).0 == -13,
        951,
    );
    Connection {
        reader: rep.0 as u64,
        writer: req.1,
        child: child as u64,
    }
}
fn rpc(c: Connection, message: &mut [u8; 32]) {
    check(
        transfer(c.writer, message, true) == 1 && transfer(c.reader, message, false) == 1,
        952,
    );
}
fn seed(c: Connection) -> [u8; 32] {
    let mut m = [0u8; 32];
    put(&mut m, 0, 1);
    put(&mut m, 4, 0xf001);
    put(&mut m, 12, 1);
    m[16..24].copy_from_slice(b"hello.sh");
    rpc(c, &mut m);
    check(get(&m, 0) == 0, 953);
    let handle = get(&m, 4);
    m = [0; 32];
    put(&mut m, 0, 2);
    put(&mut m, 4, handle);
    put(&mut m, 12, 16);
    rpc(c, &mut m);
    check(get(&m, 0) == 16, 953);
    let data = m;
    m = [0; 32];
    put(&mut m, 0, 3);
    put(&mut m, 4, handle);
    rpc(c, &mut m);
    check(get(&m, 0) == 0, 953);
    data
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    abi: u64,
    factory: u64,
    first: u64,
    second: u64,
    channels: u64,
    third: u64,
) -> ! {
    check(
        (abi, factory, first, second, channels, third)
            == (
                if cfg!(init_sustained) {
                    22
                } else if cfg!(shell_console) {
                    18
                } else if cfg!(shell_prelude)
                    || cfg!(pipe_probe)
                    || cfg!(scratch_owner_probe)
                    || cfg!(scratch_client)
                {
                    17
                } else {
                    9
                },
                0xa001,
                0xc001,
                0xc002,
                0xd001,
                0xc003,
            ),
        949,
    );
    #[cfg(exec_streams)]
    inherit::exec_streams::run(factory, first, second, third);
    #[cfg(process_exec)]
    exec::run(factory, first, second, third);
    #[cfg(process_inherit)]
    inherit::run(factory, first, second, third);
    #[cfg(process_copy)]
    copy::run(factory, first, second);
    #[cfg(process_freeze)]
    freeze::run(factory, first, second);
    #[cfg(command_runner)]
    command::run(factory, first, second, third);
    #[cfg(shared_files)]
    shared::run(factory, first, second, third);
    for _ in 0..2 {
        let backend = launch(factory, second, 1);
        let mut hello = [0; 32];
        check(
            transfer(backend.reader, &mut hello, false) == 1 && get(&hello, 4) == 0xf001,
            952,
        );
        let clients = [launch(factory, first, 0), launch(factory, third, 2)];
        check(ctl(0x24000, channels).0 == -16, 950);
        let mut frames = [[0u8; 32]; 2];
        let mut used = [0usize; 2];
        let mut done = [false; 2];
        let mut released = false;
        for _ in 0..100000 {
            for i in 0..2 {
                if done[i] {
                    continue;
                }
                let n = call(
                    0x24001,
                    clients[i].reader,
                    frames[i][used[i]..].as_mut_ptr() as u64,
                    (32 - used[i]) as u64,
                    0,
                    0,
                    0,
                )
                .0;
                if n == -11 {
                    continue;
                }
                check(n > 0 && n as usize <= 32 - used[i], 954);
                used[i] += n as usize;
                if cfg!(reject_partial) && used[i] < 32 {
                    end(959);
                }
                if used[i] == 32 {
                    check(
                        get(&frames[i], 0) == 1 && frames[i][4..].iter().all(|b| *b == 0),
                        954,
                    );
                    let mut reply = seed(backend);
                    if cfg!(wrong_data) {
                        reply[16] ^= 1;
                    }
                    check(transfer(clients[i].writer, &mut reply, true) == 1, 954);
                    done[i] = true;
                }
            }
            // The first client deliberately withholds its final 24 bytes until
            // the other client has received and validated its real file data.
            if done[1] {
                let peer = ctl(0x20001, clients[1].child);
                check(peer.0 == 0 || peer.0 == 30, 960);
            }
            if !released && done[1] && ctl(0x20001, clients[1].child).1 == 1 {
                check(used[0] == 8 && !done[0], 955);
                let mut go = [0u8; 32];
                put(&mut go, 0, 777);
                check(transfer(clients[0].writer, &mut go, true) == 1, 955);
                released = true;
            }
            if done[0] && done[1] {
                break;
            }
            ctl(0x1fffe, 0);
        }
        check(done == [true, true] && released, 956);
        for c in clients {
            check(terminal(c.child) == (29, 1), 957);
            check(
                ctl(0x24003, c.writer).0 == 0
                    && ctl(0x24003, c.reader).0 == 0
                    && ctl(0x20002, c.child).0 == 0,
                958,
            );
            check(
                ctl(0x20001, c.child).0 == -9 && ctl(0x24003, c.writer).0 == -13,
                958,
            );
        }
        check(
            ctl(0x24003, backend.writer).0 == 0 && terminal(backend.child) == (17, 1),
            958,
        );
        check(
            ctl(0x24003, backend.reader).0 == 0 && ctl(0x20002, backend.child).0 == 0,
            958,
        );
    }
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(999)
}
