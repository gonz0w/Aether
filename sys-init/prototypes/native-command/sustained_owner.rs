// SPDX-License-Identifier: BSD-2-Clause
// ABI22 fixture wait/input operations, adapted from the sealed SI-07 producer.
// Sys-init owns admission and paired-owner cleanup; this is not an operator UI.
use super::*;
fn op(number: u64, cap: u64, a: u64, b: u64) -> (i64, u64, u64) {
    call(number, cap, a, b, 0, 0, 0)
}
pub fn write(bytes: &[u8]) {
    for byte in bytes {
        loop {
            let result = op(0x26001, 0xf001, byte as *const u8 as u64, 1).0;
            if result == 1 {
                break;
            }
            check(result == -11, 2805);
            ctl(0x1fffe, 0);
        }
    }
}
#[cfg(not(init_service_table))]
pub fn begin() {
    check(op(0x2a000, 0xe001, 0, 0).0 == -13, 2805);
    check(op(0x2a002, 0xe002, 0, 0).0 == -13, 2805);
    check(op(0x2a002, 0xf002, 1, 0).0 == -38, 2805);
    check(op(0x2a002, 0xf002, 0, 0).0 == -16, 2805);
    let before = op(0x2a000, 0xe002, 0, 0);
    write(b"SI07 idle-ready\n");
    let done = op(0x2a001, 0xe002, before.1, 3005);
    check(done.0 == -110 && done.2 >= 3005, 2805);
}
pub fn input(prompt: &[u8]) -> u8 {
    write(prompt);
    loop {
        let before = op(0x2a000, 0xe002, 0, 0);
        check(before.0 == 0, 2805);
        let mut byte = 0u8;
        let result = op(0x26000, 0xf001, &mut byte as *mut u8 as u64, 1).0;
        if result == 1 {
            check(byte == b'r' || byte == b'h', 2805);
            return byte;
        }
        check(result == -11, 2805);
        check(op(0x2a001, 0xe002, before.1, 0).0 == 0, 2805);
    }
}
pub fn halt() -> ! {
    check(op(0x26002, 0xf001, 0, 0).0 == 0, 2805);
    op(0x2a002, 0xf002, 0, 0);
    end(2805)
}

// Validate full-width native identity before any private protocol publication.
// A mismatch retires only actually owned peers, clients before their provider.
pub fn cohort<'a>(backend: &mut Owned<'a, Native>, clients: &mut [Owned<'a, Native>; 2], native: &mut Native, epoch: u32) {
    #[cfg(init_sustained_bad_cohort)]
    let epoch = epoch + 65536;
    #[cfg(init_sustained_bad_cohort_late)]
    let epoch = if clients[1].resources().2 { epoch + 65536 } else { epoch };
    let mut valid = (1..=65535).contains(&epoch);
    for (owner, slot) in [(&*backend, 1), (&clients[0], 0), (&clients[1], 2)] {
        if owner.resources().2 {
            let c = lifecycle::borrowed(owner);
            valid &= c.child == ((0x31u64 << 56) | (slot << 32) | epoch as u64);
        }
    }
    if valid { return; }
    let (runner, command) = clients.split_at_mut(1);
    for owner in [&mut command[0], &mut runner[0], backend] {
        if !owner.resources().2 { continue; }
        let key = owner.key();
        owner.request_stop(native, &key).unwrap_or_else(|_| end(2806));
        let mut stopped = false;
        for _ in 0..100000 {
            match owner.observe(native, &key) {
                Ok(Some(t)) => { check(t.detail == 143 && t.kind == 3, 2806); stopped = true; break; }
                Ok(None) => { ctl(0x1fffe, 0); }
                Err(_) => end(2806),
            }
        }
        check(stopped, 2806);
        owner.cleanup(native, &key).unwrap_or_else(|_| end(2806));
        check(owner.resources() == ([false; 2], [false; 2], false), 2806);
    }
    write(b"SI07 cohort rejected after reclaim\n");
    end(2806)
}

// Known cleanup permits halt, but a failed request cannot admit more workers.
#[cfg(init_supervised)]
pub fn failed(message: &[u8]) -> ! {
    write(message);
    loop {
        if input(b"SI07 failed-ready\n") == b'h' { halt(); }
        write(b"SYSINIT-RETRY-BLOCKED admission remains closed\n");
    }
}
