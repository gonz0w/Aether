// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;
#[cfg(pipeline_copy)]
mod copies;
#[cfg(pipeline_exec_request)]
mod exec_request;
mod output;
#[cfg(pipeline_dispatch)]
#[path = "../native-connections/pipe.rs"]
mod pipe;
#[cfg(pipeline_dispatch)]
#[path = "../native-connections/pipeline.rs"]
mod pipeline;
#[cfg(pipeline_dispatch)]
mod pipes;
#[cfg(pipeline_copy)]
mod session_children;
#[cfg(pipeline_dash_main)]
mod startup;
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
#[cfg_attr(
    any(fork_dispatch, command_runner, pipeline_exec_request),
    inline(never)
)]
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
                if cfg!(session_lifetime) && !cfg!(session_legacy) {
                    21
                } else if cfg!(pipeline_serial) {
                    20
                } else {
                    19
                },
                0xa001,
                0xc001,
                0xc002,
                0xd001,
                0xc003,
            ),
        2600,
    );
    let mut old = [0; 5];
    #[cfg(pipeline_dispatch)]
    let mut objects = [pipe::PipelinePipe::new(), pipe::PipelinePipe::new()];
    #[cfg(session_lifetime)]
    check(
        ctl(0x2000a, 0xa001).0 == if cfg!(session_legacy) { -38 } else { -22 },
        2608,
    );
    let slots = if cfg!(session_lifetime) { 2 } else { 5 };
    let generations = if cfg!(session_lifetime) { 15 } else { 3 };
    #[cfg(session_lifetime)]
    check(call(0x26000, 0xf001, 0, 0, 0, 0, 0).0 == -38, 2810);
    for generation in 1..=generations {
        let mut stdout = output::Output::new(generation as u32);
        let mut handles = [0; 5];
        let mut readers = [0; 5];
        let mut writers = [0; 5];
        #[cfg(pipeline_copy)]
        if !cfg!(pipeline_factory) {
            pipes::create(&mut objects, generation as u32);
        }
        for slot in 0..slots {
            let req = ctl(0x24000, channels);
            let rep = ctl(0x24000, channels);
            check(req.0 > 0 && rep.0 > 0, 2601);
            #[cfg(all(session_lifetime, not(session_legacy)))]
            {
                let identity = 0xd1000000 | ((slot as u64 * 2) << 16) | (generation << 8);
                check(
                    (req.0 as u64, req.1, rep.0 as u64, rep.1)
                        == (
                            identity | 1,
                            identity | 2,
                            (identity + 0x10000) | 1,
                            (identity + 0x10000) | 2,
                        ),
                    2810,
                );
            }
            readers[slot] = rep.0 as u64;
            writers[slot] = req.1;
            let mut arguments = args(b"capacity");
            arguments.argc = 3;
            arguments.strings[1][0] = b'0' + slot as u8;
            arguments.strings[2][0] = b'0' + generation as u8;
            check(
                call(
                    0x23002,
                    factory,
                    first,
                    5,
                    &arguments as *const Args as u64,
                    req.0 as u64,
                    rep.1,
                )
                .0 == -22,
                2602,
            );
            #[cfg(pipeline_copy)]
            let sequence = if slot >= 2 && !(cfg!(pipeline_shell_early) && slot == 4) {
                copies::stage(
                    &mut objects,
                    &mut stdout,
                    generation as u32,
                    slot,
                    handles[0],
                    readers[0],
                    writers[0],
                )
            } else {
                0
            };
            #[cfg(not(pipeline_copy))]
            let sequence = 0;
            let launched = if sequence != 0 {
                check(
                    call(
                        0x23006,
                        factory,
                        handles[0],
                        slot as u64,
                        sequence - 1,
                        req.0 as u64,
                        rep.1,
                    )
                    .0 == -9,
                    2732,
                );
                call(
                    0x23006,
                    factory,
                    handles[0],
                    slot as u64,
                    sequence,
                    req.0 as u64,
                    rep.1,
                )
                .0
            } else {
                call(
                    0x23002,
                    factory,
                    first,
                    slot as u64,
                    &arguments as *const Args as u64,
                    req.0 as u64,
                    rep.1,
                )
                .0
            };
            handles[slot] = 0xb0000000 | (generation << 8) | (slot as u64 + 1);
            check(launched == handles[slot] as i64, 2603);
            check(
                ctl(0x24003, req.0 as u64).0 == -13 && ctl(0x24003, rep.1).0 == -13,
                2604,
            );
            if generation > 1 {
                check(ctl(0x20001, old[slot]).0 == -9, 2605);
            }
        }
        #[cfg(not(session_lifetime))]
        check(ctl(0x24000, channels).0 == -16, 2606);
        // Every slot must report while all five are still admitted and waiting.
        for slot in 0..slots {
            if cfg!(pipeline_copy) && slot == 0 {
                continue;
            }
            let mut words = [0u64; 2];
            let mut received = false;
            for _ in 0..100000 {
                let n = call(
                    0x24001,
                    readers[slot],
                    words.as_mut_ptr() as u64,
                    16,
                    0,
                    0,
                    0,
                )
                .0;
                if n == 16 {
                    received = true;
                    break;
                }
                check(n == -11, 2607);
                check(ctl(0x20001, handles[slot]).0 == 0, 2607);
                ctl(0x1fffe, 0);
            }
            check(
                received && words == [generation * 6 + slot as u64 + 1, slot as u64 + 1],
                2608,
            );
        }
        #[cfg(pipeline_dispatch)]
        pipes::prepare(&mut objects, generation as u32, &handles);
        #[cfg(all(pipeline_exec, not(pipeline_exec_overlap)))]
        let cancelled = copies::replace(
            &mut objects,
            &mut stdout,
            generation as u32,
            &handles,
            &readers,
            &writers,
        );
        #[cfg(any(not(pipeline_exec), pipeline_exec_overlap))]
        let cancelled = false;
        #[cfg(all(pipeline_wait_any, not(pipeline_wait_io)))]
        copies::wait_any(generation as u32, &handles, readers[0], writers[0], true);
        for slot in 0..slots {
            if cfg!(pipeline_dash_parent) && slot == 0 {
                continue;
            }
            if cancelled && slot >= 2 {
                continue;
            }
            if cfg!(pipeline_autonomous)
                && slot >= 2
                && !(cfg!(pipeline_shell_early) && slot == 4)
                && !(cfg!(pipeline_obsolete_release) && slot == 2)
            {
                continue;
            }
            if !cfg!(pipeline_dispatch) && generation == 2 && slot == 4 {
                check(ctl(0x20007, handles[slot]).0 == 0, 2609);
            } else {
                #[cfg(pipeline_wait_any)]
                copies::release(writers[slot]);
                #[cfg(not(pipeline_wait_any))]
                {
                    let token = [1u8];
                    check(
                        call(0x24002, writers[slot], token.as_ptr() as u64, 1, 0, 0, 0).0 == 1,
                        2610,
                    );
                }
            }
        }
        #[cfg(all(pipeline_factory, not(pipeline_dash_parent)))]
        copies::close_parent(&mut objects, &mut stdout, readers[0], writers[0]);
        #[cfg(all(pipeline_dash_main, not(pipeline_dash_parent)))]
        copies::shell_startup(generation as u32, writers[2]);
        #[cfg(pipeline_dispatch)]
        if !cancelled {
            pipes::dispatch(
                &mut objects,
                &mut stdout,
                generation as u32,
                &handles,
                &readers,
                &writers,
            );
        }
        #[cfg(all(pipeline_wait_any, not(pipeline_wait_io)))]
        copies::wait_any(generation as u32, &handles, readers[0], writers[0], false);
        #[cfg(all(pipeline_factory, not(pipeline_wait_any)))]
        copies::collect(generation as u32, &handles, readers[0], writers[0]);
        for slot in 0..slots {
            let expected = if cfg!(pipeline_shell_early) && slot == 2 {
                (43, 1)
            } else if (cfg!(pipeline_wait_stop) && slot == 0)
                || (cfg!(pipeline_exec_overlap_stop) && slot == 4)
                || (cancelled && slot >= 2)
                || (!cfg!(pipeline_dispatch) && generation == 2 && slot == 4)
                || ((cfg!(pipeline_stop_request) || cfg!(pipeline_stop_reply)) && slot == 2)
            {
                (144, 3)
            } else {
                (1, 1)
            };
            let mut terminal = false;
            for _ in 0..100000 {
                let state = ctl(0x20001, handles[slot]);
                if state.0 != 0 {
                    check((state.0, state.2) == expected, 2611);
                    terminal = true;
                    break;
                }
                ctl(0x1fffe, 0);
            }
            check(terminal, 2612);
            check(
                ctl(0x24003, readers[slot]).0 == 0 && ctl(0x24003, writers[slot]).0 == 0,
                2613,
            );
            check(
                ctl(0x20002, handles[slot]).0 == 0 && ctl(0x20001, handles[slot]).0 == -9,
                2614,
            );
            old[slot] = handles[slot];
        }
    }
    #[cfg(not(session_lifetime))]
    check(ctl(0x24000, channels).0 == -28, 2615);
    #[cfg(session_lifetime)]
    {
        let spare = ctl(0x24000, channels);
        check((spare.0, spare.1) == (0xd1040101, 0xd1040102), 2810);
        check(
            ctl(0x24003, spare.0 as u64).0 == 0 && ctl(0x24003, spare.1).0 == 0,
            2810,
        );
    }
    let arguments = args(b"capacity");
    for slot in 0..slots {
        check(
            call(
                0x23000,
                factory,
                first,
                slot as u64,
                &arguments as *const Args as u64,
                0,
                0,
            )
            .0 == -28,
            2616,
        );
    }
    #[cfg(pipeline_serial)]
    {
        check(ctl(0x26002, 0xf001).0 == 0, 2795);
        check(call(0x26000, 0xf001, 0, 0, 0, 0, 0).0 == -9, 2795);
    }
    end(100)
}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(2699)
}
