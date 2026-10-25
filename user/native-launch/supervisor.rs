// SPDX-License-Identifier: BSD-2-Clause
// Kernel conformance only; no production process or supervision policy.
#![no_std]
#![no_main]
use core::arch::asm;
#[cfg(lookup)]
mod namespace;
#[repr(C)]
struct Args {
    argc: u64,
    envc: u64,
    strings: [[u8; 32]; 8],
}
fn args(second: bool, fault: bool) -> Args {
    let mut a = Args {
        argc: 2,
        envc: 1,
        strings: [[0; 32]; 8],
    };
    for (i, s) in [
        (
            0,
            if second {
                b"helper-b" as &[u8]
            } else {
                b"helper-a"
            },
        ),
        (1, if fault { b"fault" as &[u8] } else { b"exit" }),
        (
            4,
            if second {
                b"AETHER_LAUNCH=two" as &[u8]
            } else {
                b"AETHER_LAUNCH=one"
            },
        ),
    ] {
        for (j, b) in s.iter().enumerate() {
            a.strings[i][j] = *b;
        }
    }
    a
}
fn call(op: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64) {
    let r: i64;
    let kind: u64;
    unsafe {
        asm!("int 0x81",inlateout("rax") op=>r,in("rdi") a,in("rsi") b,
        inlateout("rdx") c=>_,in("r10") d,inlateout("r8") 0u64=>kind,
        in("r9") 0u64,lateout("rcx") _,options(nostack));
    }
    (r, kind)
}
fn end(n: u64) -> ! {
    call(0x20006, n, 0, 0, 0);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool, n: u64) {
    if !ok {
        end(n);
    }
}
fn ctl(op: u64, h: u64) -> (i64, u64) {
    call(op, h, 0, 0, 0)
}
fn terminal(h: u64, detail: i64, kind: u64) {
    for _ in 0..100000 {
        let s = ctl(0x20001, h);
        if s.0 != 0 {
            check(s == (detail + 1, kind), 411);
            check(ctl(0x20001, h) == s, 412);
            return;
        }
        ctl(0x1fffe, 0);
    }
    end(413)
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, first: u64, second: u64) -> ! {
    check(
        abi == 3 && factory == 0xa001 && first == 0xc001 && second == 0xc002,
        401,
    );
    #[cfg(lookup)]
    {
        use namespace::{Entry, Namespace};
        let entries = [
            Entry {
                name: b"helper-a",
                executable: first,
            },
            Entry {
                name: b"helper-b",
                executable: second,
            },
        ];
        let all = Namespace { entries: &entries };
        let restricted = Namespace {
            entries: &entries[..1],
        };
        check(restricted.lookup(b"helper-a") == Ok(first), 430);
        let denied = if cfg!(wide_namespace) {
            all.lookup(b"helper-b")
        } else {
            restricted.lookup(b"helper-b")
        };
        check(denied == Err(-2), 431);
        check(
            Namespace { entries: &[] }.lookup(b"helper-a") == Err(-2),
            432,
        );
        for name in [
            b"" as &[u8],
            b".",
            b"..",
            b"../helper-a",
            b"/helper-a",
            b"a/helper-a",
            b"helper-a/",
            b"helper-a\0",
            b"helper a",
        ] {
            check(all.lookup(name) == Err(-22), 433);
        }
        check(
            all.lookup(&[b'a'; 32]) == Err(-36) && all.lookup(b"missing") == Err(-2),
            434,
        );
        let unavailable = [Entry {
            name: b"helper-a",
            executable: 0,
        }];
        check(
            Namespace {
                entries: &unavailable,
            }
            .lookup(b"helper-a")
                == Err(-13),
            435,
        );
    }
    let mut a = args(false, false);
    let ptr = &a as *const Args as u64;
    check(call(0x23000, 0, first, 0, ptr).0 == -13, 402);
    check(call(0x23000, factory, 0, 0, ptr).0 == -13, 403);
    check(call(0x23000, factory, first, 2, ptr).0 == -22, 404);
    check(call(0x23000, factory, first, 0, u64::MAX).0 == -14, 405);
    check(call(0x23000, factory, first, 0, 0x800ff0).0 == -14, 406);
    a.argc = 5;
    check(
        call(0x23000, factory, first, 0, &a as *const Args as u64).0 == -22,
        407,
    );
    a.argc = 2;
    a.strings[0] = [b'x'; 32];
    check(
        call(0x23000, factory, first, 0, &a as *const Args as u64).0 == -22,
        408,
    );
    a = args(false, false);
    #[cfg(lookup)]
    {
        check(
            selected_launch(factory, first, second, b"missing", 0, &a) == -2,
            436,
        );
        check(
            selected_launch(factory, first, second, b"../helper-a", 0, &a) == -22,
            437,
        );
    }
    let h = selected_launch(factory, first, second, b"helper-a", 0, &a) as u64;
    check(h == 0xb0000101, 409);
    // Child startup bytes must survive parent-side input changes.
    unsafe {
        core::ptr::write_volatile(&mut a.strings[0][0], b'X');
    }
    check(call(0x23000, factory, second, 0, ptr).0 == -16, 410);
    check(ctl(0x20002, h).0 == -16, 414);
    check(call(0x20000, factory, 1, 0, 0).0 == -38, 415);
    let b = args(true, false);
    let peer = selected_launch(factory, first, second, b"helper-b", 1, &b) as u64;
    check(peer == 0xb0000102, 416);
    terminal(h, 17, 1);
    terminal(peer, 29, 1);
    check(
        call(0x20003, h, 0, 0, 0).0 == 65 && call(0x20003, peer, 0, 0, 0).0 == 66,
        417,
    );
    check(
        ctl(0x20002, h).0 == 0 && ctl(0x20001, h).0 == -9 && ctl(0x20002, h).0 == -9,
        418,
    );
    let replacement = args(true, true);
    let fresh = selected_launch(factory, first, second, b"helper-b", 0, &replacement) as u64;
    check(fresh == 0xb0000201 && ctl(0x20007, h).0 == -9, 419);
    terminal(fresh, 134, 2);
    check(ctl(0x20002, fresh).0 == 0 && ctl(0x20002, peer).0 == 0, 420);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(499)
}

fn selected_launch(
    factory: u64,
    first: u64,
    second: u64,
    name: &[u8],
    slot: u64,
    args: &Args,
) -> i64 {
    #[cfg(lookup)]
    let executable = {
        use namespace::{Entry, Namespace};
        let entries = [
            Entry {
                name: b"helper-a",
                executable: if cfg!(wrong_binding) { second } else { first },
            },
            Entry {
                name: b"helper-b",
                executable: second,
            },
        ];
        match (Namespace { entries: &entries }).lookup(name) {
            Ok(grant) => grant,
            Err(error) => return error,
        }
    };
    #[cfg(not(lookup))]
    let executable = if name == b"helper-a" { first } else { second };
    call(
        0x23000,
        factory,
        executable,
        slot,
        args as *const Args as u64,
    )
    .0
}
