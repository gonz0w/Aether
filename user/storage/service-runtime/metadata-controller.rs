// SPDX-License-Identifier: BSD-2-Clause
//! Separate fixed AF07/ABI26 conformance owner, not sys-init policy.
#![no_std]
#![no_main]
use core::arch::asm;
// Build selection inserts absolute, immutable-at-run module paths here.
fn call(op: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64) {
    let status: i64;
    let kind: u64;
    // SAFETY: owner-local scalar operations or one synchronous, disjoint region
    // record borrow; the kernel validates the record and retains no pointer.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => status, inlateout("rdi") a => _,
            inlateout("rsi") b => _, inlateout("rdx") c => _, inlateout("r10") d => _,
            inlateout("r8") 0u64 => kind, inlateout("r9") 0u64 => _,
            lateout("rcx") _, lateout("r11") _);
    }
    (status, kind)
}
fn end(code: u64) -> ! {
    call(0x20006, code, 0, 0, 0);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool) {
    if !ok {
        end(401);
    }
}
fn byte(owner: u64, offset: usize) -> u8 {
    let value = call(0x20003, owner, offset as u64, 0, 0).0;
    check((0..=255).contains(&value));
    value as u8
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, block: u64) -> ! {
    check((abi, factory, block) == (26, 0xa001, 0xf101));
    check(call(0x20000, factory, 1, 0, 0).0 == -38);
    let (mut stale, mut endpoint) = (0u64, 0);
    let mut remaining = 1_000_000;
    for generation in 1..=3 {
        let connection = namespace_client::Connection::new();
        if endpoint != 0 {
            namespace_client::stale(endpoint);
        }
        let owner = connection.admit(factory);
        check(owner > 0);
        let owner = owner as u64;
        check(owner != stale);
        if stale != 0 {
            check(call(0x20001, stale, 0, 0, 0).0 == -9);
            check(call(0x20002, stale, 0, 0, 0).0 == -9);
        } else {
            let region = [8u64, 2097152, 7];
            check(call(0x27005, block, owner, region.as_ptr() as u64, 24).0 == 0);
            check(activation::ready(owner, &mut remaining));
            connection.exercise();
        }
        loop {
            check(remaining != 0);
            remaining -= 1;
            let state = call(0x20001, owner, 0, 0, 0);
            if state.0 != 0 {
                check(state == (1, 1));
                break;
            }
            call(0x1fffe, 0, 0, 0, 0);
        }
        endpoint = connection.finish(generation == 1);
        let tags: &[u8] = if generation == 1 {
            b"BIUVWLP????????OAMT????????SDJFR"
        } else {
            b"BNR"
        };
        for (stage, tag) in tags.iter().enumerate() {
            let offset = stage * 8;
            check(
                (generation == 1 && ((7..15).contains(&stage) || (19..27).contains(&stage)))
                    || byte(owner, offset) == *tag,
            );
            let live = byte(owner, offset + 1);
            let admissions = u16::from_le_bytes([byte(owner, offset + 2), byte(owner, offset + 3)]);
            let free = u16::from_le_bytes([byte(owner, offset + 4), byte(owner, offset + 5)]);
            let total = u16::from_le_bytes([byte(owner, offset + 6), byte(owner, offset + 7)]);
            check(total == 8192 && free <= total && live <= 82 && (1..=512).contains(&admissions));
        }
        check(call(0x20003, owner, (tags.len() * 8) as u64, 0, 0).0 == -11);
        if generation == 1 {
            let mut target = [0; 8];
            for (i, value) in target.iter_mut().enumerate() {
                *value = byte(owner, (19 + i) * 8);
            }
            check(u64::from_le_bytes(target) > 790);
        }
        check(call(0x20002, owner, 0, 0, 0).0 == 0);
        check(call(0x20001, owner, 0, 0, 0).0 == -9);
        stale = owner;
    }
    namespace_client::exhausted();
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(403)
}
