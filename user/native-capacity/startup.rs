// SPDX-License-Identifier: BSD-2-Clause
//! Immutable directory view delegated only to the copied shell's connection.
fn word(frame: &[u8; 32], at: usize) -> u32 {
    u32::from_le_bytes(frame[at..at + 4].try_into().unwrap())
}

pub(super) fn directory(slot: usize, generation: u32, request: &[u8; 32]) -> [u8; 32] {
    let mut reply = [0; 32];
    let reference = word(request, 4);
    let length = word(request, 12) as usize;
    let result: i32 =
        if slot != if cfg!(pipeline_dash_parent) { 0 } else { 2 } || word(request, 8) != 3 {
            -13
        } else if reference != 0x76030000 + generation {
            if generation > 0 && reference == 0x76030000 + generation - 1 {
                -9
            } else {
                -13
            }
        } else if word(request, 0) == 4 {
            if length != 0 || request[16..] != [0; 16] {
                -22
            } else {
                reply[16..22].copy_from_slice(b"/work\0");
                6
            }
        } else if word(request, 0) != 5 {
            -38
        } else if length > 15 {
            -36
        } else if length == 0
            || request[16..16 + length].contains(&0)
            || request[16 + length..].iter().any(|byte| *byte != 0)
        {
            -22
        } else {
            let path = &request[16..16 + length];
            if path == b"." || path == b"/work" {
                reply[16..20].copy_from_slice(&(100 + generation).to_le_bytes());
                reply[20..24].copy_from_slice(&1u32.to_le_bytes());
                reply[24..28].copy_from_slice(&0o40500u32.to_le_bytes());
                0
            } else if path.starts_with(b"/") || path == b".." || path.starts_with(b"../") {
                -13
            } else {
                -2
            }
        };
    reply[..4].copy_from_slice(&result.to_le_bytes());
    reply
}

#[cfg(test)]
mod tests {
    use super::*;
    const OWNER: usize = if cfg!(pipeline_dash_parent) { 0 } else { 2 };
    fn request(op: u32, path: &[u8]) -> [u8; 32] {
        let mut frame = [0; 32];
        for (chunk, value) in frame
            .chunks_exact_mut(4)
            .zip([op, 0x76030002, 3, path.len() as u32])
        {
            chunk.copy_from_slice(&value.to_le_bytes());
        }
        frame[16..16 + path.len()].copy_from_slice(path);
        frame
    }
    fn denied(slot: usize, frame: [u8; 32], error: i32) {
        let mut expected = [0; 32];
        expected[..4].copy_from_slice(&error.to_le_bytes());
        assert_eq!(directory(slot, 2, &frame), expected);
    }
    #[test]
    fn matching_directory_identity_and_cwd() {
        let cwd = directory(OWNER, 2, &request(4, b""));
        assert_eq!(word(&cwd, 0), 6);
        assert_eq!(&cwd[16..], b"/work\0\0\0\0\0\0\0\0\0\0\0");
        let stat = directory(OWNER, 2, &request(5, b"."));
        assert_eq!(stat, directory(OWNER, 2, &request(5, b"/work")));
        assert_eq!(
            (
                word(&stat, 0),
                word(&stat, 16),
                word(&stat, 20),
                word(&stat, 24)
            ),
            (0, 102, 1, 0o40500)
        );
    }
    #[test]
    fn caller_and_generation_bound_authority() {
        for slot in [0, 1, 2, 3, 4, usize::MAX]
            .into_iter()
            .filter(|slot| *slot != OWNER)
        {
            denied(slot, request(4, b""), -13);
        }
        let mut frame = request(4, b"");
        frame[4..8].copy_from_slice(&0x76030001u32.to_le_bytes());
        denied(OWNER, frame, -9);
        frame[4..8].copy_from_slice(&0x76030003u32.to_le_bytes());
        denied(OWNER, frame, -13);
        frame = request(4, b"");
        frame[8] = 1;
        denied(OWNER, frame, -13);
    }
    #[test]
    fn malformed_and_escape_requests_have_zero_tails() {
        denied(OWNER, request(99, b"."), -38);
        denied(OWNER, request(4, b"x"), -22);
        denied(OWNER, request(5, b""), -22);
        denied(OWNER, request(5, b"a\0b"), -22);
        denied(OWNER, request(5, b"../work"), -13);
        denied(OWNER, request(5, b"/else"), -13);
        denied(OWNER, request(5, b"missing"), -2);
        let mut frame = request(5, b".");
        frame[31] = 1;
        denied(OWNER, frame, -22);
        frame = request(5, b".");
        frame[12..16].copy_from_slice(&u32::MAX.to_le_bytes());
        denied(OWNER, frame, -36);
    }
}
