// SPDX-License-Identifier: BSD-2-Clause
//! Sealed native runner probe. The Owner retains all file and namespace rights.
#![no_std]
#![no_main]

extern crate self as abi29_dispatch_core;
#[allow(dead_code)]
#[path = "../../../sys-init/prototypes/native-filesystem-session/zsh_process_frames.rs"]
mod frames;
#[path = "../../../sys-init/prototypes/native-filesystem-session/startup.rs"]
pub mod startup;

fn grants(words: &[u64; 68]) -> Option<[u64; 3]> {
    // The loader places argv and envp in separate four-string banks.
    if words[..5] != [1, 0x0800e100, 0, 0x0800e180, 0] {
        return None;
    }
    let mut found = [0; 3];
    for pair in words[5..].chunks_exact(2) {
        if pair[0] == 0 {
            return (pair[1] == 0 && found.iter().all(|value| *value != 0) && found[1] != found[2])
                .then_some(found);
        }
        if (0xa000..=0xa002).contains(&pair[0]) {
            let index = (pair[0] - 0xa000) as usize;
            if found[index] != 0 || pair[1] == 0 {
                return None;
            }
            found[index] = pair[1];
        }
    }
    None
}

fn validate(raw: &[u8; 336], memory: u64, pid: i64, parent: i64, epoch: i64) -> bool {
    if !(1..=15).contains(&epoch)
        || parent <= 0
        || parent > u32::MAX as i64
        || raw[112..120] != [4, 0, 0, 0, 4, 1, 0, 0]
        || raw[120..176].iter().any(|value| *value != 0)
    {
        return false;
    }
    let Ok(identity) =
        startup::Identity::admitted(2, epoch as u32, 0xb0000000 | (epoch as u64) << 8 | 3)
    else {
        return false;
    };
    let generation = u64::from_le_bytes(raw[56..64].try_into().unwrap());
    identity.memory == memory
        && identity.pid as i64 == pid
        && frames::snapshot(
            raw,
            frames::Expected {
                identity,
                parent: parent as u32,
                generation,
            },
        )
        .is_ok()
}

#[inline(always)]
fn trap(op: u64, a: u64, b: u64, c: u64) -> i64 {
    let result: i64;
    // SAFETY: fixed int81 ABI. Any buffer is borrowed only for the trap.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") op => result,
            in("rdi") a, in("rsi") b, inlateout("rdx") c => _,
            in("r10") 0u64, inlateout("r8") 0u64 => _, in("r9") 0u64,
            lateout("rcx") _, lateout("r11") _);
    }
    result
}

fn exit(status: u64) -> ! {
    let _ = trap(0x100e7, status, 0, 0);
    // SAFETY: native exit is nonreturning. Fault if it unexpectedly returns.
    unsafe { core::arch::asm!("ud2", options(noreturn)) }
}

#[unsafe(naked)]
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub unsafe extern "C" fn _start() -> ! {
    // SAFETY: the kernel supplies the aligned launch stack at 0x0800c000.
    core::arch::naked_asm!("mov rdi, rsp", "call {run}", "ud2", run = sym run);
}

extern "C" fn run(sp: u64) -> ! {
    if sp != 0x0800c000 {
        exit(143);
    }
    // SAFETY: launchStack initialized the fixed stack window. The pointer
    // checks in grants select fixed, mapped argument and environment slots.
    let words = unsafe { &*(sp as *const [u64; 68]) };
    let Some([memory, input, _output]) = grants(words) else {
        exit(143);
    };
    let argv = unsafe { &*(0x0800e100usize as *const [u8; 32]) };
    let env = unsafe { &*(0x0800e180usize as *const [u8; 32]) };
    if argv[..6] != *b"probe\0"
        || argv[6..].iter().any(|value| *value != 0)
        || env[..9] != *b"LC_ALL=C\0"
        || env[9..].iter().any(|value| *value != 0)
    {
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
            if offset == 336 {
                if !validate(&raw, memory, pid, parent, epoch) || trap(0x20004, 0, 0, 0) != 0 {
                    exit(143);
                }
                exit(23);
            }
        } else if result != -11 || trap(0x24004, input, 0, 0) != 0 {
            exit(143);
        }
    }
    exit(143)
}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo<'_>) -> ! {
    exit(143)
}
