// SPDX-License-Identifier: BSD-2-Clause
//! Fixed AF05 native witness. Components are digest-shaped, differing at byte63.
use super::*;
const FIRST: &[u8; 64] = b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
const SECOND: &[u8; 64] = b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b856";

/// Translate only the fixture's p/q labels, never an application pathname.
/// Each complete header and padded body uses the unchanged bounded transport.
pub(super) fn send(endpoint: u64, raw: &mut [u8; 64]) -> bool {
    let op = get(raw, 1);
    if !matches!(op, 1 | 7..=9) {
        return channel::frame(endpoint, raw, true).is_ok();
    }
    let tags = [raw[48], raw[49]];
    let total = if op == 8 { 2 } else { 1 };
    let lengths = tags.map(|tag| if tag == b'p' || tag == b'q' { 64 } else { 1 });
    put(
        raw,
        5,
        lengths[0] | if op == 8 { lengths[1] << 32 } else { 0 },
    );
    // Only the fixed p/q rename is needed here; do not emit padding between
    // arbitrary short components and misrepresent it as one joined body.
    if op == 8 && lengths != [64, 64] {
        return false;
    }
    raw[48..].fill(0);
    if channel::frame(endpoint, raw, true).is_err() {
        return false;
    }
    for tag in tags.into_iter().take(total) {
        let mut frame = [0; 64];
        match tag {
            b'p' => frame.copy_from_slice(FIRST),
            b'q' => frame.copy_from_slice(SECOND),
            _ => frame[0] = tag,
        }
        if channel::frame(endpoint, &mut frame, true).is_err() {
            return false;
        }
    }
    true
}
