// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! AEEXEC01 is a captured context plus path/argv, never executable authority.
use abi29_dispatch_core::startup::Identity;
use fd_startup::Plan;
pub const BYTES: usize = 608;
pub const MAGIC: &[u8; 8] = if fd_startup::FILE_SLOTS_16 {
    b"AEEXEC02"
} else {
    b"AEEXEC01"
};
pub fn header(raw: &[u8]) -> bool {
    raw.len() == 16
        && &raw[..8] == MAGIC
        && u32::from_le_bytes(raw[8..12].try_into().unwrap()) == 1
        && u32::from_le_bytes(raw[12..16].try_into().unwrap()) == BYTES as u32
}
pub fn request(
    raw: &[u8; BYTES],
    expected: (Identity, u32, u64),
    scratch: &mut [u8; 304],
) -> Result<(Plan, u64), i32> {
    if !header(&raw[..16]) {
        return Err(-22);
    }
    // Reuse exact canonical body validation without rewriting or relaxing bytes.
    let plan = fork_frames::context(&raw[..304], expected.0, expected.1, expected.2, scratch)?;
    let sequence = u64::from_le_bytes(raw[296..304].try_into().unwrap());
    if sequence == 0 {
        return Err(-22);
    }
    let path = &raw[304..336];
    let end = path.iter().position(|b| *b == 0).ok_or(-22)?;
    if end == 0 || path[end..].iter().any(|b| *b != 0) {
        return Err(-22);
    }
    arguments(raw[336..].try_into().unwrap())?;
    Ok((plan, sequence))
}
pub fn arguments(raw: &[u8; 272]) -> Result<(), i32> {
    let argc = u64::from_le_bytes(raw[..8].try_into().unwrap());
    let envc = u64::from_le_bytes(raw[8..16].try_into().unwrap());
    if !(1..=4).contains(&argc) || envc > 4 {
        return Err(-22);
    }
    for i in 0..8 {
        let s = &raw[16 + i * 32..48 + i * 32];
        let active = if i < 4 {
            i < (argc as usize)
        } else {
            i - 4 < (envc as usize)
        };
        if active {
            let end = s.iter().position(|b| *b == 0).ok_or(-22)?;
            if s[end..].iter().any(|b| *b != 0) {
                return Err(-22);
            }
        } else if s.iter().any(|b| *b != 0) {
            return Err(-22);
        }
    }
    Ok(())
}
pub fn refusal(sequence: u64, error: i64) -> Result<[u8; 32], i32> {
    if sequence == 0 || !(-4095..=-1).contains(&error) {
        return Err(-22);
    }
    let mut out = [0; 32];
    out[..8].copy_from_slice(b"AEEXR001");
    out[8..16].copy_from_slice(&sequence.to_le_bytes());
    out[16..24].copy_from_slice(&error.to_le_bytes());
    Ok(out)
}
