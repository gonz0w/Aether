// SPDX-License-Identifier: BSD-2-Clause
//! Fixed filesystem-exec witness; no libc, FILE request or ambient namespace.
#![cfg_attr(not(test), no_std)]
#![cfg_attr(not(test), no_main)]
#[cfg(not(test))]
extern crate self as abi29_dispatch_core;
#[cfg(test)]
use file_exec_frames as frames;
#[cfg(test)]
pub use file_exec_frames::startup;
#[cfg(not(test))]
#[path = "../../../sys-init/prototypes/native-filesystem-session/startup.rs"]
pub mod startup;
// Reuse the actual selected 336-byte validator; other process-frame operations
// are deliberately unused by this one consumer and are removed by the linker.
#[cfg(not(test))]
#[allow(dead_code)]
#[path = "../../../sys-init/prototypes/native-filesystem-session/zsh_process_frames.rs"]
mod frames;

fn grants(words: &[u64; 68]) -> Option<[u64; 3]> {
    if words[..4] != [1, 0x0800e100, 0, 0] {
        return None;
    }
    let mut found = [0; 3];
    for pair in words[4..].chunks_exact(2) {
        if pair[0] == 0 {
            return (pair[1] == 0 && found.iter().all(|v| *v != 0) && found[1] != found[2])
                .then_some(found);
        }
        if (0xa000..=0xa002).contains(&pair[0]) {
            let i = (pair[0] - 0xa000) as usize;
            if found[i] != 0 || pair[1] == 0 {
                return None;
            }
            found[i] = pair[1];
        }
    }
    None
}
fn validate(raw: &[u8; 336], memory: u64, pid: i64, parent: i64, epoch: i64) -> bool {
    if !(1..=15).contains(&epoch) || parent <= 0 || parent > u32::MAX as i64 {
        return false;
    }
    let Ok(id) = startup::Identity::admitted(2, epoch as u32, 0xb0000000 | (epoch as u64) << 8 | 3)
    else {
        return false;
    };
    let generation = u64::from_le_bytes(raw[56..64].try_into().unwrap());
    id.memory == memory
        && id.pid as i64 == pid
        && frames::snapshot(
            raw,
            frames::Expected {
                identity: id,
                parent: parent as u32,
                generation,
            },
        )
        .is_ok()
}

#[cfg(not(test))]
#[inline(always)]
fn trap(op: u64, a: u64, b: u64, c: u64) -> i64 {
    let result: i64;
    // SAFETY: fixed int81 ABI. Buffer arguments are synchronous stack borrows;
    // all scalar outputs/clobbers are declared. No pointer survives the trap.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") op => result,
            in("rdi") a, in("rsi") b, inlateout("rdx") c => _,
            in("r10") 0u64, inlateout("r8") 0u64 => _, in("r9") 0u64,
            lateout("rcx") _, lateout("r11") _);
    }
    result
}
#[cfg(not(test))]
fn exit(status: u64) -> ! {
    let _ = trap(0x100e7, status, 0, 0);
    // SAFETY: native exit is nonreturning; an unexpected return must fault.
    unsafe {
        core::arch::asm!("ud2", options(noreturn));
    }
}
#[cfg(not(test))]
#[unsafe(naked)]
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub unsafe extern "C" fn _start() -> ! {
    // SAFETY: launchStack supplies aligned RSP=0x0800c000 with the checked
    // fixed argv/auxv record above it. A call supplies the SysV return slot.
    core::arch::naked_asm!("mov rdi, rsp", "call {run}", "ud2", run = sym run);
}
#[cfg(not(test))]
extern "C" fn run(sp: u64) -> ! {
    if sp != 0x0800c000 {
        exit(143);
    }
    // SAFETY: the admitted eager loader maps/zeros all 16 stack pages. This
    // fixed window and argv slot lie above the fresh runtime stack and are only
    // read here. The child image cannot obtain a namespace reference from them.
    let words = unsafe { &*(sp as *const [u64; 68]) };
    let Some([memory, input, _output]) = grants(words) else {
        exit(143);
    };
    let argv = unsafe { &*(0x0800e100usize as *const [u8; 12]) };
    if argv != b"/home/probe\0" {
        exit(143);
    }
    let pid = trap(0x10027, 0, 0, 0);
    let parent = trap(0x1006e, 0, 0, 0);
    let epoch = trap(0x20005, 0, 0, 0);
    let mut raw = [0u8; 336];
    let mut offset = 0;
    for _ in 0..16384 {
        let count = (336 - offset).min(16);
        let result = trap(
            0x24001,
            input,
            raw[offset..].as_mut_ptr() as u64,
            count as u64,
        );
        if result > 0 && result <= count as i64 {
            offset += result as usize;
            if offset == 16 && (raw[..8] != *b"AEFDB009" || raw[8..16] != [1, 0, 0, 0, 80, 1, 0, 0])
            {
                exit(143);
            }
            if offset == 336 {
                if !validate(&raw, memory, pid, parent, epoch) {
                    exit(143);
                }
                if trap(0x20004, 0, 0, 0) != 0 {
                    exit(143);
                }
                // Owner terminal reconciliation owns proxy/endpoint cleanup.
                // No FD operation or request is issued after READY.
                exit(23);
            }
        } else if result != -11 || trap(0x24004, input, 0, 0) != 0 {
            exit(143);
        }
    }
    exit(143)
}
#[cfg(not(test))]
#[panic_handler]
fn panic(_: &core::panic::PanicInfo<'_>) -> ! {
    exit(143)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn frame() -> [u8; 336] {
        let mut raw = [0; 336];
        raw[..8].copy_from_slice(b"AEFDB009");
        raw[8..16].copy_from_slice(&[1, 0, 0, 0, 80, 1, 0, 0]);
        let id = startup::Identity::admitted(2, 1, 0xb0000103).unwrap();
        raw[16..48].copy_from_slice(&startup::greeting(id, 1, 9).unwrap());
        raw[48..56].copy_from_slice(b"AEFDT009");
        raw[56..64].copy_from_slice(&32u64.to_le_bytes());
        raw[64] = 16;
        for byte in raw[304..320].chunks_exact_mut(4) {
            byte.copy_from_slice(&1000u32.to_le_bytes());
        }
        raw[320] = 1;
        raw
    }
    #[test]
    fn complete_startup_and_native_identity_required() {
        let valid = frame();
        assert!(validate(&valid, 0x40000103, 10, 9, 1));
        for at in [
            0, 8, 12, 16, 24, 28, 32, 36, 40, 44, 48, 56, 64, 72, 112, 176, 288, 296, 300, 304,
            308, 312, 316, 320, 324, 328, 335,
        ] {
            let mut bad = valid;
            bad[at] ^= 0x80;
            if at == 56 {
                bad[56..64].fill(0);
            }
            assert!(!validate(&bad, 0x40000103, 10, 9, 1), "offset {at}");
        }
        for observed in [
            (0, 10, 9, 1),
            (0x40000103, 9, 9, 1),
            (0x40000103, 10, 7, 1),
            (0x40000103, 10, 9, 2),
        ] {
            assert!(!validate(
                &valid, observed.0, observed.1, observed.2, observed.3
            ));
        }
    }
    #[test]
    fn checked_auxv_requires_all_distinct_grants_and_terminator() {
        let mut words = [0; 68];
        words[..10].copy_from_slice(&[
            1, 0x0800e100, 0, 0, 0xa000, 0x40000103, 0xa001, 81, 0xa002, 82,
        ]);
        assert_eq!(grants(&words), Some([0x40000103, 81, 82]));
        for at in [0, 1, 2, 3, 4, 6, 8, 11] {
            let mut bad = words;
            bad[at] ^= 1;
            assert_eq!(grants(&bad), None, "word {at}");
        }
        for at in [5, 7, 9] {
            let mut bad = words;
            bad[at] = 0;
            assert_eq!(grants(&bad), None);
        }
        words[9] = 81;
        assert_eq!(grants(&words), None);
    }
}
