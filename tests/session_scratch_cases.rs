// SPDX-License-Identifier: BSD-2-Clause
use crate::session_scratch::Scratch;
fn word(frame: &[u8; 32], at: usize) -> u32 {
    u32::from_le_bytes(frame[at..at + 4].try_into().unwrap())
}
fn put(frame: &mut [u8; 32], at: usize, value: u32) {
    frame[at..at + 4].copy_from_slice(&value.to_le_bytes());
}
fn open(scratch: &Scratch, mode: u32) -> [u8; 32] {
    let mut frame = [0; 32];
    put(&mut frame, 0, 86);
    put(&mut frame, 4, scratch.root());
    put(&mut frame, 12, mode);
    frame[16..29].copy_from_slice(b"/scratch/data");
    frame
}
#[test]
fn description_exhaustion_cannot_truncate_live_data() {
    let mut scratch = Scratch::new(1);
    for peer in [0, 1] {
        assert_eq!(word(&scratch.request(peer, &open(&scratch, 1)), 0), 0);
    }
    let before = scratch.clone();
    assert_eq!(
        word(&scratch.request(2, &open(&scratch, 14)), 0) as i32,
        -23
    );
    assert_eq!(scratch, before);
}
#[test]
fn full_file_write_fails_without_changing_offset_or_bytes() {
    let mut scratch = Scratch::new(1);
    let grant = scratch.request(0, &open(&scratch, 14));
    let mut frame = [0; 32];
    put(&mut frame, 0, 2);
    put(&mut frame, 4, word(&grant, 4));
    put(&mut frame, 8, word(&grant, 8));
    put(&mut frame, 12, 16);
    frame[16..].fill(b'x');
    for _ in 0..2 {
        assert_eq!(word(&scratch.request(0, &frame), 0), 16);
    }
    let before = scratch.clone();
    assert_eq!(word(&scratch.request(0, &frame), 0) as i32, -28);
    assert_eq!(scratch, before);
}
#[test]
fn rejected_inheritance_and_commit_leave_other_holders_untouched() {
    let mut scratch = Scratch::new(1);
    scratch.request(0, &open(&scratch, 14));
    let before = scratch.clone();
    let mut users = [0; 9];
    users[7] = 1;
    assert!(scratch.inherit(0, 4, &users).is_err());
    assert!(scratch.inherit(1, 2, &users).is_err());
    assert!(scratch.inherit(0, 2, &[0; 9]).is_err());
    let mut forged = users;
    forged[8] = 1;
    assert!(scratch.commit(0, &users, &forged).is_err());
    assert_eq!(scratch, before);
}
