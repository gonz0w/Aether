// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Selected opt-in owner frame helpers. Authentication/native effects external.
use abi29_dispatch_core::startup::{Identity, greeting};
use fd_startup::{BYTES, Binding, Plan, Source, encode};
/// Exact compatible16-byte header only; the owner handles incomplete input and
/// any already parked caller independently of this shape predicate.
pub const MAGIC: &[u8; 8] = if fd_startup::FILE_SLOTS_16 {
    b"AEFORK02"
} else {
    b"AEFORK01"
};
pub fn header(raw: &[u8]) -> bool {
    raw.len() == 16 && &raw[..8] == MAGIC && word32(raw, 8) == 1 && word32(raw, 12) == BYTES as u32
}
/// Compare to actual authenticated parent observation, not payload-selected IDs.
/// Scratch must not alias input. On failure there is no admitted owner plan.
pub fn request(
    raw: &[u8],
    parent: Identity,
    boot_parent: u32,
    generation: u64,
    scratch: &mut [u8; BYTES],
) -> Result<(Plan, u64), i32> {
    if raw.len() != BYTES || !header(&raw[..16]) {
        return Err(-22);
    }
    if parent.slot != 1 {
        return Err(-9);
    }
    let identity = greeting(parent, parent.epoch, boot_parent)?;
    if raw[16..48] != identity {
        return Err(-9);
    }
    if generation == 0 || word64(raw, 56) != generation {
        return Err(-9);
    }
    let sequence = word64(raw, 296);
    if sequence == 0 {
        return Err(-22);
    }
    let plan = context(raw, parent, boot_parent, generation, scratch)?;
    Ok((plan, sequence))
}
/// Canonical full snapshot body for authenticated owner operations. Header and
/// sequence belong to the selecting operation; no native effects or admission.
pub fn context(
    raw: &[u8],
    parent: Identity,
    boot_parent: u32,
    generation: u64,
    scratch: &mut [u8; BYTES],
) -> Result<Plan, i32> {
    if raw.len() != BYTES || generation == 0 || word64(raw, 56) != generation {
        return Err(-9);
    }
    let shell = if parent.slot == 1 {
        parent.epoch
    } else {
        boot_parent.checked_sub(2).ok_or(-9)? / 7
    };
    let identity = greeting(parent, shell, boot_parent)?;
    if raw[16..48] != identity {
        return Err(-9);
    }
    let mut plan = Plan {
        identity: parent,
        shell,
        parent: boot_parent,
        generation: word64(raw, 56),
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [word32(raw, 288), word32(raw, 292)],
    };
    for (i, b) in plan.bindings.iter_mut().enumerate() {
        let offset = 112 + i * 4;
        if raw[offset + 3] != 0 {
            return Err(-22);
        }
        *b = Binding {
            kind: raw[offset],
            selector: raw[offset + 1],
            cloexec: raw[offset + 2],
        };
    }
    for (i, s) in plan.sources.iter_mut().enumerate() {
        let offset = 176 + i * 16;
        *s = Source {
            reference: word32(raw, offset),
            selector: word32(raw, offset + 4),
            rights: word32(raw, offset + 8),
            bound: word32(raw, offset + 12),
        };
    }
    encode(&plan, scratch)?;
    // Regeneration validates all map reserved bytes and exact source encoding.
    if raw[16..296] != scratch[16..296] {
        return Err(-22);
    }
    Ok(plan)
}
/// Only after confirmed context-ready, or settled known no-child refusal. The
/// stage rejects negative disposition after a positive actual copy return.
pub fn disposition(sequence: u64, result: i64) -> Result<[u8; 32], i32> {
    if sequence == 0 || !(canonical_child(result) || (-4095..=-1).contains(&result)) {
        return Err(-22);
    }
    let mut out = [0; 32];
    out[..8].copy_from_slice(b"AEFKR001");
    out[8..16].copy_from_slice(&sequence.to_le_bytes());
    out[16..24].copy_from_slice(&result.to_le_bytes());
    Ok(out)
}
pub fn ready(raw: &[u8], sequence: u64, pid: u32) -> bool {
    sequence != 0
        && canonical_child(pid as i64)
        && raw.len() == 32
        && &raw[..8] == b"AEFKC001"
        && word64(raw, 8) == sequence
        && word64(raw, 16) == pid as u64
        && word64(raw, 24) == 0
}
fn canonical_child(pid: i64) -> bool {
    if pid <= 0 || pid > 110 {
        return false;
    }
    let n = pid - 1;
    (2..=4).contains(&(n % 7)) && (1..=15).contains(&(n / 7))
}
fn word32(raw: &[u8], at: usize) -> u32 {
    u32::from_le_bytes(raw[at..at + 4].try_into().unwrap())
}
fn word64(raw: &[u8], at: usize) -> u64 {
    u64::from_le_bytes(raw[at..at + 8].try_into().unwrap())
}
