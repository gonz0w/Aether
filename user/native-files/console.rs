// SPDX-License-Identifier: BSD-2-Clause
// Private serial backend: the supervisor channel owns three logical streams.
use super::*;
fn uart(op: u64, bytes: &mut [u8]) -> i64 {
    let result: i64;
    // The borrowed stack span remains live for this synchronous trap; no pointer
    // is retained. The kernel validates the grant, span and bounded byte count.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") op => result,
            in("rdi") 0xf001u64, in("rsi") bytes.as_mut_ptr(),
            inlateout("rdx") bytes.len() as u64 => _, in("r10") 0u64,
            lateout("rcx") _, lateout("r8") _, options(nostack));
    }
    result
}
fn generation() -> i64 {
    let result: i64;
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") 0x20005u64 => result,
            in("rdi") 0u64, in("rsi") 0u64, inlateout("rdx") 0u64 => _,
            in("r10") 0u64, lateout("rcx") _, lateout("r8") _, options(nostack));
    }
    result
}
pub fn run() -> i32 {
    if generation() == 2 {
        return if uart(0x26000, &mut [0; 1]) == -13 {
            0
        } else {
            125
        };
    }
    let mut granted = false;
    for _ in 0..100000 {
        let result = uart(0x26001, &mut []);
        if result == 0 {
            granted = true;
            break;
        }
        if result != -13 {
            return 125;
        }
        unsafe { bridge_yield() };
    }
    if !granted {
        return 125;
    }
    let handles = [0xf101, 0xf201, 0xf202];
    let mut hello = [0; 32];
    for j in 0..3 {
        put(&mut hello, 4 + j * 4, handles[j]);
    }
    if !send(&hello) {
        return 120;
    }
    let mut live = [true; 3];
    let mut positions = [0u32; 3];
    let mut sessions = 1;
    loop {
        let mut req = [0; 32];
        match receive(&mut req) {
            0 => {
                return if live == [false; 3] && sessions == if cfg!(shell_repeat) { 1 } else { 2 } {
                    0
                } else {
                    123
                };
            }
            1 => (),
            _ => return 121,
        }
        if !cfg!(shell_repeat) && req == [0; 32] && live == [false; 3] && sessions == 1 {
            live = [true; 3];
            positions = [0; 3];
            sessions += 1;
            if !send(&hello) {
                return 122;
            }
            continue;
        }
        let mut response = [0; 32];
        let mut result = -9;
        if let Some(j) = (0..3).find(|j| live[*j] && get(&req, 4) == handles[*j]) {
            let op = get(&req, 0);
            let offset = get(&req, 8);
            let n = get(&req, 12) as usize;
            result = -22;
            if op == 3 && offset == 0 && n == 0 && req[16..] == [0; 16] {
                live[j] = false;
                result = 0;
            } else if n <= 16
                && offset == positions[j]
                && ((op == 2 && j == 0 && req[16..] == [0; 16])
                    || (op == 4 && j != 0 && req[16 + n..].iter().all(|b| *b == 0)))
            {
                let mut bytes = [0; 16];
                if op == 4 {
                    bytes[..n].copy_from_slice(&req[16..16 + n]);
                }
                result = uart(if op == 2 { 0x26000 } else { 0x26001 }, &mut bytes[..n]) as i32;
                if cfg!(console_eof) && result == -11 && op == 2 {
                    result = 0;
                }
                if result > n as i32 || result < -4095 {
                    return 126;
                }
                if result >= 0 {
                    positions[j] += result as u32;
                    if op == 2 {
                        response[16..16 + result as usize]
                            .copy_from_slice(&bytes[..result as usize]);
                    }
                }
            }
        }
        put(&mut response, 0, result as u32);
        if !send(&response) {
            return 122;
        }
    }
}
