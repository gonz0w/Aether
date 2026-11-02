// SPDX-License-Identifier: BSD-2-Clause
//! Closed 009 process snapshots. These inert bytes confer no native authority.
//! The caller supplies actual authenticated identity/channel observations.
use abi29_dispatch_core::startup::{Identity, greeting};

pub const STARTUP_BYTES: usize = 336;
pub const FORK_BYTES: usize = 368;
pub const EXEC_BYTES: usize = 672;

#[derive(Clone, Copy)]
pub struct Expected {
    pub identity: Identity,
    pub parent: u32,
    pub generation: u64,
}
#[derive(Clone, Copy)]
pub struct Snapshot<'a> {
    raw: &'a [u8; STARTUP_BYTES],
    expected: Expected,
}
impl Snapshot<'_> {
    pub fn raw(&self) -> &[u8; STARTUP_BYTES] {
        self.raw
    }
    pub fn identity(&self) -> Identity {
        self.expected.identity
    }
    pub fn generation(&self) -> u64 {
        self.expected.generation
    }
}
fn u32_at(raw: &[u8], at: usize) -> u32 {
    u32::from_le_bytes(raw[at..at + 4].try_into().unwrap())
}
fn u64_at(raw: &[u8], at: usize) -> u64 {
    u64::from_le_bytes(raw[at..at + 8].try_into().unwrap())
}
fn sequence_ok(sequence: u64) -> bool {
    sequence != 0 && sequence != u64::MAX
}

/// Validate every field before returning a borrowed view. No partial publication.
pub fn snapshot(raw: &[u8], expected: Expected) -> Result<Snapshot<'_>, i32> {
    let raw: &[u8; STARTUP_BYTES] = raw.try_into().map_err(|_| -22)?;
    let id = expected.identity;
    if !matches!(id.slot, 1 | 2) || expected.generation == 0 {
        return Err(-9);
    }
    let shell = if id.slot == 1 {
        id.epoch
    } else {
        expected.parent.checked_sub(2).ok_or(-9)? / 7
    };
    let identity = greeting(id, shell, expected.parent)?;
    if &raw[..8] != b"AEFDB009"
        || u32_at(raw, 8) != 1
        || u32_at(raw, 12) != 336
        || raw[16..48] != identity
        || &raw[48..56] != b"AEFDT009"
        || u64_at(raw, 56) != expected.generation
        || u64_at(raw, 64) != 16
        || raw[72..112].iter().any(|v| *v != 0)
        || u32_at(raw, 296) != if id.slot == 1 { 0x76050001 } else { 0 }
        || u32_at(raw, 300) != if id.slot == 1 { 0x7d000001 } else { 0 }
        || [304, 308, 312, 316]
            .iter()
            .any(|at| u32_at(raw, *at) != 1000)
        || u32_at(raw, 320) != 1
        || raw[324..336].iter().any(|v| *v != 0)
    {
        return Err(-22);
    }
    let mut used = [false; 7];
    let mut files = [false; 16];
    for b in raw[112..176].chunks_exact(4) {
        if b[2] > 1 {
            return Err(-22);
        }
        match b[0] {
            0 if b[1..] == [0; 3] => (),
            2 if (3..=6).contains(&b[1]) && b[3] == 0 => used[b[1] as usize] = true,
            3 if (3..=15).contains(&b[1]) && b[3] == 0 => {
                let slot = &mut files[b[1] as usize];
                if *slot {
                    return Err(-22);
                }
                *slot = true;
            }
            4 if b[1] <= 2 && b[3] == 0 => used[b[1] as usize] = true,
            5 if b[1] == 0 && (1..=16).contains(&b[3]) => {
                used[0] = true;
                used[1] = true;
            }
            _ => return Err(-22),
        }
    }
    let history = [u32_at(raw, 288), u32_at(raw, 292)];
    if history.iter().any(|v| *v > 9) {
        return Err(-22);
    }
    for (i, held) in used.iter().enumerate() {
        let at = 176 + i * 16;
        if !*held {
            if raw[at..at + 16].iter().any(|v| *v != 0) {
                return Err(-9);
            }
            continue;
        }
        let reference = if i < 3 {
            0x7a000001 | (i as u32) << 16
        } else {
            let generation = history[(i - 3) / 2];
            if generation == 0 {
                return Err(-9);
            }
            0x79000000 | (((i - 3) / 2) as u32) << 16 | generation << 8 | ((i - 3) % 2 + 1) as u32
        };
        if u32_at(raw, at) != reference
            || u32_at(raw, at + 4) != i as u32
            || u32_at(raw, at + 8) != if matches!(i, 0 | 3 | 5) { 1 } else { 2 }
            || u32_at(raw, at + 12) != 16
        {
            return Err(-9);
        }
    }
    Ok(Snapshot { raw, expected })
}
fn header(raw: &[u8], magic: &[u8; 8], length: usize) -> Result<u64, i32> {
    if raw.len() != length
        || &raw[..8] != magic
        || u32_at(raw, 8) != 1
        || u32_at(raw, 12) != length as u32
        || !sequence_ok(u64_at(raw, 16))
        || u64_at(raw, 24) != 0
    {
        return Err(-22);
    }
    Ok(u64_at(raw, 16))
}
fn prefix(raw: &mut [u8], magic: &[u8; 8], sequence: u64) {
    let length = raw.len() as u32;
    raw[..32].fill(0);
    raw[..8].copy_from_slice(magic);
    raw[8..12].copy_from_slice(&1u32.to_le_bytes());
    raw[12..16].copy_from_slice(&length.to_le_bytes());
    raw[16..24].copy_from_slice(&sequence.to_le_bytes());
}
pub fn fork_request(raw: &[u8], expected: Expected) -> Result<(Snapshot<'_>, u64), i32> {
    let sequence = header(raw, b"AEZFK001", FORK_BYTES)?;
    let view = snapshot(&raw[32..], expected)?;
    if view.identity().slot != 1 {
        return Err(-9);
    }
    Ok((view, sequence))
}
pub fn encode_fork(
    raw: &[u8; STARTUP_BYTES],
    expected: Expected,
    sequence: u64,
    out: &mut [u8; FORK_BYTES],
) -> Result<(), i32> {
    let view = snapshot(raw, expected)?;
    if view.identity().slot != 1 || !sequence_ok(sequence) {
        return Err(-22);
    }
    prefix(out, b"AEZFK001", sequence);
    out[32..].copy_from_slice(raw);
    Ok(())
}
pub fn child_match<'a>(
    request: &[u8],
    parent: Expected,
    startup: &'a [u8],
    child: Expected,
) -> Result<Snapshot<'a>, i32> {
    let (before, _) = fork_request(request, parent)?;
    let after = snapshot(startup, child)?;
    if after.identity().slot != 2
        || child.parent != before.identity().pid
        || after.generation() == before.generation()
        || before.raw[112..296] != after.raw[112..296]
        || before.raw[304..336] != after.raw[304..336]
    {
        return Err(-9);
    }
    Ok(after)
}
fn arguments(raw: &[u8; 272]) -> Result<(), i32> {
    let argc = u64_at(raw, 0);
    let envc = u64_at(raw, 8);
    if !(1..=4).contains(&argc) || envc > 4 {
        return Err(-22);
    }
    for i in 0..8 {
        let value = &raw[16 + i * 32..48 + i * 32];
        let active = i % 4 < if i < 4 { argc as usize } else { envc as usize };
        let end = if active {
            value.iter().position(|v| *v == 0).ok_or(-22)?
        } else {
            0
        };
        if value[end..].iter().any(|v| *v != 0) {
            return Err(-22);
        }
    }
    Ok(())
}
pub fn exec_request(raw: &[u8], expected: Expected) -> Result<(Snapshot<'_>, u64), i32> {
    let sequence = header(raw, b"AEZEX001", EXEC_BYTES)?;
    let view = snapshot(&raw[32..368], expected)?;
    if view.identity().slot != 2 {
        return Err(-9);
    }
    let path = &raw[368..400];
    let end = path.iter().position(|v| *v == 0).ok_or(-22)?;
    if end == 0 || path[end..].iter().any(|v| *v != 0) {
        return Err(-22);
    }
    arguments(raw[400..].try_into().unwrap())?;
    Ok((view, sequence))
}
pub fn encode_exec(
    raw: &[u8; STARTUP_BYTES],
    expected: Expected,
    sequence: u64,
    path: &[u8],
    args: &[u8; 272],
    out: &mut [u8; EXEC_BYTES],
) -> Result<(), i32> {
    let view = snapshot(raw, expected)?;
    arguments(args)?;
    if view.identity().slot != 2
        || !sequence_ok(sequence)
        || path.is_empty()
        || path.len() > 31
        || path.contains(&0)
    {
        return Err(-22);
    }
    prefix(out, b"AEZEX001", sequence);
    out[32..368].copy_from_slice(raw);
    out[368..400].fill(0);
    out[368..368 + path.len()].copy_from_slice(path);
    out[400..].copy_from_slice(args);
    Ok(())
}
fn child_pid(pid: i64) -> bool {
    (10..=108).contains(&pid) && (pid - 3) % 7 == 0
}
fn receipt_value(magic: &[u8; 8], result: i64) -> bool {
    match magic {
        b"AEZFR001" => child_pid(result) || (-4095..=-1).contains(&result),
        b"AEZFC001" => child_pid(result),
        b"AEZER001" => (-4095..=-1).contains(&result),
        _ => false,
    }
}
pub fn receipt(magic: &[u8; 8], sequence: u64, result: i64) -> Result<[u8; 32], i32> {
    if !sequence_ok(sequence) || !receipt_value(magic, result) {
        return Err(-22);
    }
    let mut out = [0; 32];
    out[..8].copy_from_slice(magic);
    out[8..16].copy_from_slice(&sequence.to_le_bytes());
    out[16..24].copy_from_slice(&result.to_le_bytes());
    Ok(out)
}
pub fn decode_receipt(raw: &[u8], magic: &[u8; 8], sequence: u64) -> Result<i64, i32> {
    if raw.len() != 32
        || !sequence_ok(sequence)
        || &raw[..8] != magic
        || u64_at(raw, 8) != sequence
        || u64_at(raw, 24) != 0
    {
        return Err(-22);
    }
    let result = i64::from_le_bytes(raw[16..24].try_into().unwrap());
    if !receipt_value(magic, result) {
        return Err(-22);
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn put(raw: &mut [u8], at: usize, value: u32) {
        raw[at..at + 4].copy_from_slice(&value.to_le_bytes());
    }
    fn fixture(child: bool) -> ([u8; 336], Expected) {
        let identity = Identity::admitted(
            if child { 2 } else { 1 },
            1,
            if child { 0xb0000103 } else { 0xb0000102 },
        )
        .unwrap();
        let expected = Expected {
            identity,
            parent: if child { 9 } else { 7 },
            generation: if child { 32 } else { 31 },
        };
        let mut raw = [0; 336];
        raw[..8].copy_from_slice(b"AEFDB009");
        put(&mut raw, 8, 1);
        put(&mut raw, 12, 336);
        raw[16..48].copy_from_slice(&greeting(identity, 1, expected.parent).unwrap());
        raw[48..56].copy_from_slice(b"AEFDT009");
        raw[56..64].copy_from_slice(&expected.generation.to_le_bytes());
        raw[64..72].copy_from_slice(&16u64.to_le_bytes());
        for i in 0..3 {
            raw[112 + i * 4] = 4;
            raw[113 + i * 4] = i as u8;
            put(&mut raw, 176 + i * 16, 0x7a000001 | (i as u32) << 16);
            put(&mut raw, 180 + i * 16, i as u32);
            put(&mut raw, 184 + i * 16, if i == 0 { 1 } else { 2 });
            put(&mut raw, 188 + i * 16, 16);
        }
        raw[124] = 2;
        raw[125] = 3;
        raw[128] = 2;
        raw[129] = 4;
        raw[132] = 3;
        raw[133] = 3;
        raw[152] = 5;
        raw[155] = 1;
        for i in 3..5 {
            put(&mut raw, 176 + i * 16, 0x79000100 | (i as u32 - 2));
            put(&mut raw, 180 + i * 16, i as u32);
            put(&mut raw, 184 + i * 16, if i == 3 { 1 } else { 2 });
            put(&mut raw, 188 + i * 16, 16);
        }
        put(&mut raw, 288, 1);
        put(&mut raw, 296, if child { 0 } else { 0x76050001 });
        put(&mut raw, 300, if child { 0 } else { 0x7d000001 });
        for at in [304, 308, 312, 316] {
            put(&mut raw, at, 1000);
        }
        put(&mut raw, 320, 1);
        (raw, expected)
    }
    #[test]
    fn selected_startup_producer_encodes_complete_role_metadata() {
        for child in [false, true] {
            let (_, expected) = fixture(child);
            let mut plan = fd_startup::Plan {
                identity: expected.identity,
                shell: 1,
                parent: expected.parent,
                generation: expected.generation,
                bindings: [fd_startup::Binding::default(); 16],
                sources: [fd_startup::Source::default(); 7],
                history: [0; 2],
            };
            for i in 0..3 {
                plan.bindings[i] = fd_startup::Binding {
                    kind: 4,
                    selector: i as u8,
                    cloexec: 0,
                };
                plan.sources[i] = fd_startup::Source {
                    reference: 0x7a000001 | (i as u32) << 16,
                    selector: i as u32,
                    rights: if i == 0 { 1 } else { 2 },
                    bound: 16,
                };
            }
            let mut out = [0; 336];
            fd_startup::encode(&plan, &mut out).unwrap();
            snapshot(&out, expected).unwrap();
            assert_eq!(u32_at(&out, 296), if child { 0 } else { 0x76050001 });
            assert_eq!(u32_at(&out, 300), if child { 0 } else { 0x7d000001 });
        }
    }
    #[test]
    fn whole_startup_roles_aliases_pipe_and_old_version_denials() {
        for child in [false, true] {
            let (raw, expected) = fixture(child);
            let checked = snapshot(&raw, expected).unwrap();
            assert_eq!(checked.raw(), &raw);
            for n in 0..336 {
                assert!(snapshot(&raw[..n], expected).is_err());
            }
            for at in [7, 55, 72, 115, 155, 176, 288, 296, 300, 304, 320, 324, 335] {
                let mut bad = raw;
                bad[at] ^= 0x80;
                assert!(snapshot(&bad, expected).is_err(), "byte{at}");
            }
        }
    }
    #[test]
    fn fork_full_snapshot_sequence_and_child_correspondence() {
        let (raw, parent) = fixture(false);
        let (child_raw, child) = fixture(true);
        let mut out = [0; 368];
        encode_fork(&raw, parent, 41, &mut out).unwrap();
        assert_eq!(&out[32..], &raw);
        assert_eq!(fork_request(&out, parent).unwrap().1, 41);
        child_match(&out, parent, &child_raw, child).unwrap();
        for n in 0..368 {
            assert!(fork_request(&out[..n], parent).is_err());
        }
        for seq in [0, u64::MAX] {
            let mut bad = out;
            bad[16..24].copy_from_slice(&seq.to_le_bytes());
            assert!(fork_request(&bad, parent).is_err());
        }
        let mut changed = child_raw;
        changed[154] = 1;
        assert!(child_match(&out, parent, &changed, child).is_err());
    }
    #[test]
    fn exec_full_snapshot_arguments_padding_roles_and_atomic_failure() {
        let (raw, child) = fixture(true);
        let (parent_raw, parent) = fixture(false);
        let mut args = [0; 272];
        args[..8].copy_from_slice(&2u64.to_le_bytes());
        args[16..30].copy_from_slice(b"/inputs/helper");
        args[48..54].copy_from_slice(b"status");
        let mut out = [0; 672];
        encode_exec(&raw, child, 42, b"/inputs/helper", &args, &mut out).unwrap();
        assert_eq!(&out[32..368], &raw);
        assert_eq!(&out[400..], &args);
        exec_request(&out, child).unwrap();
        for n in 0..672 {
            assert!(exec_request(&out[..n], child).is_err());
        }
        let mut bad = out;
        bad[671] = 1;
        assert!(exec_request(&bad, child).is_err());
        let saved = out;
        assert!(encode_exec(&parent_raw, parent, 42, b"/inputs/helper", &args, &mut out).is_err());
        assert_eq!(out, saved);
        let stale = Expected {
            generation: 33,
            ..child
        };
        assert!(exec_request(&out, stale).is_err());
    }
    #[test]
    fn typed_receipts_reject_wrong_role_sequence_version_and_padding() {
        for (magic, result) in [(b"AEZFR001", 10), (b"AEZFC001", 10), (b"AEZER001", -13)] {
            let raw = receipt(magic, 43, result).unwrap();
            assert_eq!(decode_receipt(&raw, magic, 43), Ok(result));
            assert!(decode_receipt(&raw, magic, 44).is_err());
            let mut bad = raw;
            bad[31] = 1;
            assert!(decode_receipt(&bad, magic, 43).is_err());
        }
        assert!(receipt(b"AEZER001", 43, 7).is_err());
        assert!(receipt(b"AEZFC001", 43, -13).is_err());
        assert!(receipt(b"AEZFR001", 43, 11).is_err());
    }
}
