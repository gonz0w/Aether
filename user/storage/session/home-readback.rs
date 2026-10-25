// SPDX-License-Identifier: BSD-2-Clause
//! AF09 independent late digest reader; derived from the unchanged readback.rs.
//! Gen1 validates32 eight-byte digest rows after engine shutdown. Gen2/3 retain
//! denied B/N/R resource rows and the original three-generation reclaim seam.
//! The host compares all32 opaque digest bytes across fresh pristine/recovery
//! SPAs; this controller certifies neither content semantics nor peak resources.
#![cfg_attr(not(test), no_std)]
#![cfg_attr(not(test), no_main)]
#[cfg(not(test))]
use core::arch::asm;
/// Validate the exact owned output copy without issuing native calls.
fn valid_rows(generation: u64, bytes: &[u8]) -> bool {
    if generation == 1 {
        return bytes.len() == 256
            && bytes
                .as_chunks::<8>()
                .0
                .iter()
                .all(|row| row[1..].iter().all(|byte| *byte == 0));
    }
    if !(2..=3).contains(&generation) || bytes.len() != 24 {
        return false;
    }
    bytes
        .as_chunks::<8>()
        .0
        .iter()
        .zip(b"BNR")
        .all(|(row, tag)| {
            let admissions = u16::from_le_bytes([row[2], row[3]]);
            let free = u16::from_le_bytes([row[4], row[5]]);
            let total = u16::from_le_bytes([row[6], row[7]]);
            row[0] == *tag
                && total == 8192
                && free <= total
                && row[1] <= 82
                && (1..=512).contains(&admissions)
        })
}

#[cfg(not(test))]
fn call(op: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64) {
    let status: i64;
    let kind: u64;
    // SAFETY: scalar owner-local operations or a synchronous exclusive region
    // record borrow. Kernel validates the complete record and retains no pointer.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => status, inlateout("rdi") a => _,
            inlateout("rsi") b => _, inlateout("rdx") c => _, inlateout("r10") d => _,
            inlateout("r8") 0u64 => kind, inlateout("r9") 0u64 => _,
            lateout("rcx") _, lateout("r11") _);
    }
    (status, kind)
}
#[cfg(not(test))]
fn end(code: u64) -> ! {
    call(0x20006, code, 0, 0, 0);
    loop {
        core::hint::spin_loop();
    }
}
#[cfg(not(test))]
fn check(ok: bool) {
    if !ok {
        end(401);
    }
}
#[cfg(not(test))]
fn byte(owner: u64, offset: usize) -> u8 {
    let value = call(0x20003, owner, offset as u64, 0, 0).0;
    check((0..=255).contains(&value));
    value as u8
}
#[cfg(not(test))]
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, block: u64) -> ! {
    check((abi, factory, block) == (14, 0xa001, 0xf101));
    check(call(0x20000, factory, 1, 0, 0).0 == -12);
    let mut stale = 0;
    let mut remaining = 1_000_000;
    for generation in 1..=3 {
        let handle = call(0x20000, factory, 0, 0, 0).0;
        check(handle > 0 && handle != stale);
        let owner = handle as u64;
        if stale != 0 {
            check(call(0x20001, stale as u64, 0, 0, 0).0 == -9);
            check(call(0x20002, stale as u64, 0, 0, 0).0 == -9);
        } else {
            let region = [8u64, 2097152, 1]; // READ only; no write/flush authority.
            check(call(0x27005, block, owner, region.as_ptr() as u64, 24).0 == 0);
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
        let length = if generation == 1 { 256 } else { 24 };
        let mut rows = core::mem::MaybeUninit::<[u8; 256]>::uninit();
        let bytes = rows.as_mut_ptr().cast::<u8>();
        for offset in 0..length {
            // SAFETY: offset is within the exclusive256-byte stack allocation.
            // Every byte in the selected prefix is initialized exactly once;
            // no pointer crosses the native syscall boundary or escapes.
            unsafe {
                bytes.add(offset).write(byte(owner, offset));
            }
        }
        // SAFETY: the preceding loop initialized all length bytes. Borrow only
        // that prefix, never the uninitialized remainder of a denied row set.
        let initialized = unsafe { core::slice::from_raw_parts(bytes, length) };
        check(valid_rows(generation, initialized));
        // EAGAIN proves the exact256/24-byte output extent; no partial digest,
        // hidden healthy phase row or surplus observation may be accepted.
        check(call(0x20003, owner, length as u64, 0, 0).0 == -11);
        check(call(0x20002, owner, 0, 0, 0).0 == 0);
        check(call(0x20001, owner, 0, 0, 0).0 == -9);
        stale = handle;
    }
    end(100)
}
#[cfg(not(test))]
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(403)
}

#[cfg(test)]
mod tests {
    use super::valid_rows;
    fn guards() -> [u8; 24] {
        let mut rows = [0; 24];
        for (row, tag) in rows.as_chunks_mut::<8>().0.iter_mut().zip(b"BNR") {
            row[0] = *tag;
            row[2] = 1;
            row[5] = 32;
            row[7] = 32;
        }
        rows
    }
    #[test]
    fn entire_opaque_digest_including_zero_and_ff() {
        let mut rows = [0; 256];
        for (index, row) in rows.as_chunks_mut::<8>().0.iter_mut().enumerate() {
            row[0] = (index * 17) as u8;
        }
        assert!(valid_rows(1, &rows));
        for index in 0..32 {
            let mut changed = rows;
            changed[index * 8] ^= 255;
            assert!(valid_rows(1, &changed));
        }
    }
    #[test]
    fn every_padding_byte_must_be_zero() {
        for offset in 0..256 {
            if offset % 8 == 0 {
                continue;
            }
            let mut rows = [0; 256];
            rows[offset] = 1;
            assert!(!valid_rows(1, &rows));
        }
    }
    #[test]
    fn exact_primary_extent_and_legacy_denial() {
        for length in 0..256 {
            assert!(!valid_rows(1, &[0; 256][..length]));
        }
        assert!(!valid_rows(1, &[0; 257]));
        assert!(!valid_rows(1, b"BIUVWLP????????OAMZDJFR"));
    }
    #[test]
    fn exact_denied_tags_and_generations() {
        for generation in [2, 3] {
            assert!(valid_rows(generation, &guards()));
        }
        for generation in [0, 4, u64::MAX] {
            assert!(!valid_rows(generation, &guards()));
        }
        for length in 0..24 {
            assert!(!valid_rows(2, &guards()[..length]));
        }
        assert!(!valid_rows(2, &[0; 25]));
        for index in [0, 8, 16] {
            let mut rows = guards();
            rows[index] ^= 1;
            assert!(!valid_rows(2, &rows));
        }
    }
    #[test]
    fn denied_resources_are_checked_at_every_stage() {
        for start in [0, 8, 16] {
            for (offset, value) in [(1, 83), (2, 0), (3, 3), (5, 33), (7, 31)] {
                let mut rows = guards();
                rows[start + offset] = value;
                assert!(!valid_rows(2, &rows));
            }
        }
    }
}
