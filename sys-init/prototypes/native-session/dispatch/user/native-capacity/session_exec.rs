// SPDX-License-Identifier: BSD-2-Clause
//! Inert validation for the session's bounded exec vector. The authenticated
//! dispatcher owns image authority, freeze tokens and descriptor commit.
pub const RECORD_BYTES: usize = 272;
pub const HELPER: u32 = 0xc002;

fn word(frame: &[u8; 32], offset: usize) -> u32 {
    u32::from_le_bytes(frame[offset..offset + 4].try_into().unwrap())
}

pub fn header(frame: &[u8; 32]) -> Result<(), i32> {
    if word(frame, 0) != 84 || word(frame, 8) != RECORD_BYTES as u32 || frame[12..] != [0; 20] {
        return Err(-22);
    }
    if word(frame, 4) != HELPER {
        return Err(-13);
    }
    Ok(())
}

fn string(record: &[u8; RECORD_BYTES], slot: usize) -> Result<&[u8], i32> {
    let bytes = &record[16 + slot * 32..16 + (slot + 1) * 32];
    let length = bytes.iter().position(|&b| b == 0).ok_or(-22)?;
    if bytes[length..].iter().any(|&b| b != 0) {
        return Err(-22);
    }
    Ok(&bytes[..length])
}

/// Preserve the exact record for native admission; no replacement values are
/// synthesized. Success says nothing about descriptor or image authority.
fn vector(record: &[u8; RECORD_BYTES]) -> Result<(), i32> {
    let argc = u64::from_le_bytes(record[..8].try_into().unwrap());
    let envc = u64::from_le_bytes(record[8..16].try_into().unwrap());
    if !(1..=4).contains(&argc) || envc > 4 {
        return Err(-22);
    }
    for slot in 0..8 {
        let bytes = string(record, slot)?;
        let used = if slot < 4 {
            (slot as u64) < argc
        } else {
            (slot as u64 - 4) < envc
        };
        if !used && !bytes.is_empty() {
            return Err(-22);
        }
        if slot >= 4 && used {
            let split = bytes.iter().position(|&b| b == b'=').ok_or(-22)?;
            if split == 0 {
                return Err(-22);
            }
            let key = &bytes[..split];
            for previous in 4..slot {
                let earlier = string(record, previous)?;
                let end = earlier.iter().position(|&b| b == b'=').ok_or(-22)?;
                if key == &earlier[..end] {
                    return Err(-22);
                }
            }
        }
    }
    Ok(())
}

pub fn arguments(record: &[u8; RECORD_BYTES]) -> Result<(), i32> {
    vector(record)?;
    if string(record, 0)? != b"/inputs/helper" {
        return Err(-13);
    }
    Ok(())
}

/// Private owner namespace for opcode85. A path is independent of argv[0];
/// no caller-provided image identifier is accepted. Validation is inert.
/// These two entries are owned by the fixture, not a mounted filesystem.
pub fn lookup(frame: &[u8; 32], path: &[u8; 32], record: &[u8; RECORD_BYTES]) -> Result<u32, i32> {
    if word(frame, 0) != 85
        || word(frame, 4) != 32
        || word(frame, 8) != RECORD_BYTES as u32
        || frame[12..] != [0; 20]
    {
        return Err(-22);
    }
    let end = path.iter().position(|&b| b == 0).ok_or(-22)?;
    if end == 0 || path[end..].iter().any(|&b| b != 0) {
        return Err(-22);
    }
    vector(record)?;
    match &path[..end] {
        b"/inputs/helper" => Ok(HELPER),
        b"/inputs/not-executable" => Err(-13),
        _ => Err(-2),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn record() -> [u8; RECORD_BYTES] {
        let mut record = [0; RECORD_BYTES];
        record[..8].copy_from_slice(&4u64.to_le_bytes());
        record[8..16].copy_from_slice(&4u64.to_le_bytes());
        for (slot, bytes) in [
            b"/inputs/helper".as_slice(),
            b"argv",
            b"a b",
            b"*",
            b"PWD=/work",
            b"WITNESS=value",
            b"LC_ALL=C",
            b"PATH=/nonexistent",
        ]
        .iter()
        .enumerate()
        {
            record[16 + slot * 32..][..bytes.len()].copy_from_slice(bytes);
        }
        record
    }
    fn frame() -> [u8; 32] {
        let mut frame = [0; 32];
        frame[..4].copy_from_slice(&84u32.to_le_bytes());
        frame[4..8].copy_from_slice(&HELPER.to_le_bytes());
        frame[8..12].copy_from_slice(&(RECORD_BYTES as u32).to_le_bytes());
        frame
    }
    #[test]
    fn lookup_uses_owner_namespace_not_argv_or_supplied_image() {
        let mut f = frame();
        f[..4].copy_from_slice(&85u32.to_le_bytes());
        f[4..8].copy_from_slice(&32u32.to_le_bytes());
        let mut value = record();
        value[16..48].fill(0);
        value[16..21].copy_from_slice(b"alias");
        for (name, expected) in [
            (b"/inputs/helper".as_slice(), Ok(HELPER)),
            (b"/inputs/not-executable", Err(-13)),
            (b"/inputs/missing", Err(-2)),
            (b"/inputs/../helper", Err(-2)),
        ] {
            let mut path = [0; 32];
            path[..name.len()].copy_from_slice(name);
            let before = (f, path, value);
            assert_eq!(lookup(&f, &path, &value), expected);
            assert_eq!((f, path, value), before);
        }
        let mut path = [0; 32];
        path[..14].copy_from_slice(b"/inputs/helper");
        for offset in [0, 4, 8, 12, 16, 20, 24, 28, 31] {
            let mut bad = f;
            bad[offset] ^= 1;
            assert_eq!(lookup(&bad, &path, &value), Err(-22));
        }
        for bad in [[0; 32], [b'x'; 32]] {
            assert_eq!(lookup(&f, &bad, &value), Err(-22));
        }
        path[31] = 1;
        assert_eq!(lookup(&f, &path, &value), Err(-22));
        path[31] = 0;
        value[0] = 0;
        assert_eq!(lookup(&f, &path, &value), Err(-22));
        // Legacy opcode and arguments retain their own contract.
        assert_eq!(lookup(&frame(), &path, &record()), Err(-22));
        assert_eq!(header(&f), Err(-22));
    }
    #[test]
    fn actual_values_are_preserved_including_wrong_witness() {
        let mut value = record();
        arguments(&value).unwrap();
        value[16 + 5 * 32 + 8..][..5].copy_from_slice(b"wrong");
        let before = value;
        arguments(&value).unwrap();
        assert_eq!(value, before);
        assert_eq!(string(&value, 5), Ok(b"WITNESS=wrong".as_slice()));
        // The unchanged helper, not this parser, decides whether argv succeeds.
        value[16 + 32] = b'X';
        arguments(&value).unwrap();
    }
    #[test]
    fn header_rejects_old_frames_and_ungranted_image() {
        header(&frame()).unwrap();
        for offset in [0, 8, 12, 16, 20, 24, 28, 31] {
            let mut bad = frame();
            bad[offset] ^= 1;
            assert_eq!(header(&bad), Err(-22));
        }
        let mut denied = frame();
        denied[4..8].copy_from_slice(&0xc003u32.to_le_bytes());
        assert_eq!(header(&denied), Err(-13));
    }
    #[test]
    fn malformed_counts_strings_unused_slots_and_keys_reject() {
        for (offset, count) in [(0, 0), (0, 5), (8, 5), (0, u64::MAX), (8, u64::MAX)] {
            let mut bad = record();
            bad[offset..offset + 8].copy_from_slice(&count.to_le_bytes());
            assert_eq!(arguments(&bad), Err(-22));
        }
        for slot in 0..8 {
            let mut bad = record();
            bad[16 + slot * 32..16 + (slot + 1) * 32].fill(b'x');
            assert_eq!(arguments(&bad), Err(-22));
            let mut bad = record();
            bad[16 + slot * 32 + 31] = b'x';
            assert_eq!(arguments(&bad), Err(-22));
        }
        for offset in [0, 8] {
            let mut bad = record();
            bad[offset..offset + 8].copy_from_slice(&1u64.to_le_bytes());
            assert_eq!(arguments(&bad), Err(-22));
        }
        for value in [b"WITNESS=duplicate".as_slice(), b"=empty", b"missing"] {
            let mut bad = record();
            bad[16 + 7 * 32..].fill(0);
            bad[16 + 7 * 32..][..value.len()].copy_from_slice(value);
            assert_eq!(arguments(&bad), Err(-22));
        }
        let mut denied = record();
        denied[16] = b'!';
        assert_eq!(arguments(&denied), Err(-13));
    }
}
