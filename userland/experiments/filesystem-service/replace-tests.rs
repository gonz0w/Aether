// SPDX-License-Identifier: BSD-2-Clause
use super::fixture::{Fault, Harness};
use super::*;

fn identity(slot: u32, generation: u32) -> NativeIdentity {
    NativeIdentity::admitted(
        slot,
        generation,
        0xb0000000 | (generation as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
fn parent(h: &mut Harness) -> Process {
    h.fds
        .as_mut()
        .unwrap()
        .admitted_shell(identity(1, 1), 7)
        .unwrap()
}
fn sent(h: &Harness) -> usize {
    h.local.lock().unwrap().sent.len()
}
fn closes(h: &Harness) -> usize {
    h.opcodes().iter().filter(|&&op| op == 3).count()
}

#[test]
fn full_table_replaces_exact_target_shares_offsets_and_clears_only_target_flag() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let p = parent(&mut h);
    let f = h.fds.as_mut().unwrap();
    for fd in 3..16 {
        assert_eq!(f.open_read(p, b"file", true), Ok(fd));
    }
    let before = closes(&h);
    assert_eq!(h.fds.as_mut().unwrap().replace(p, 15, 3), Ok(3));
    assert_eq!(closes(&h), before + 1);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.file_view_v1(p), Ok((0xfff8, 0xfff0)));
    assert_eq!(
        f.open_read(p, b"file", false),
        Err(ProcessError::Files(Failure::Full))
    );
    let mut out = [0; MAX_READ];
    assert_eq!(f.read(p, 15, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert_eq!(f.read(p, 3, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
    assert_eq!(f.read(p, 14, 1, &mut out), Ok(1));
    assert_eq!(out[0], b'a');
    assert_eq!(f.replace(p, 15, 15), Ok(15));
    assert_eq!(f.file_view_v1(p), Ok((0xfff8, 0xfff0)));
    let reads = h.storage.lock().unwrap().reads;
    assert_eq!(reads, 3);
}

#[test]
fn empty_and_same_description_targets_need_no_spare_or_source_close() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let p = parent(&mut h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.open_read(p, b"file", true), Ok(3));
    assert_eq!(f.replace(p, 3, 10), Ok(10));
    assert_eq!(f.file_view_v1(p), Ok((0x408, 8)));
    f.set_close_on_exec(p, 10, true).unwrap();
    assert_eq!(f.replace(p, 3, 10), Ok(10));
    assert_eq!(f.file_view_v1(p), Ok((0x408, 8)));
    assert_eq!(f.replace(p, 3, 3), Ok(3));
    assert_eq!(f.file_view_v1(p), Ok((0x408, 8)));
    assert_eq!(closes(&h), 0);
    let f = h.fds.as_mut().unwrap();
    f.close(p, 3).unwrap();
    assert_eq!(f.position(p, 10), Ok(0));
    f.close(p, 10).unwrap();
    assert_eq!(closes(&h), 1);
}

#[test]
fn inherited_victim_lives_until_last_view_close_and_stale_inputs_have_no_effects() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let p = parent(&mut h);
    let f = h.fds.as_mut().unwrap();
    f.open_read(p, b"file", false).unwrap();
    f.open_read(p, b"file", true).unwrap();
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    assert_eq!(f.replace(p, 3, 4), Ok(4));
    assert_eq!(closes(&h), 0);
    let f = h.fds.as_mut().unwrap();
    let mut out = [0; MAX_READ];
    assert_eq!(f.read(p, 4, 2, &mut out), Ok(2));
    assert_eq!(f.position(child, 3), Ok(2));
    assert_eq!(f.position(child, 4), Ok(0));
    assert_eq!(f.file_view_v1(child), Ok((24, 16)));
    f.close(child, 4).unwrap();
    assert_eq!(closes(&h), 1);
    h.fds.as_mut().unwrap().settled(child).unwrap();
    let before = sent(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.replace(child, 3, 4), Err(ProcessError::Stale));
    let child2 = f.inherited_child(p, identity(2, 2), 9).unwrap();
    assert_eq!(f.replace(child, 3, 4), Err(ProcessError::Stale));
    for (from, to) in [(2, 3), (15, 3), (3, -1), (3, 0), (3, 2), (3, 16)] {
        assert_eq!(
            f.replace(p, from, to),
            Err(ProcessError::Files(Failure::BadFd))
        );
    }
    assert_eq!(f.file_view_v1(p), Ok((24, 0)));
    assert_eq!(f.position(p, 3), Ok(2));
    assert_eq!(f.position(child2, 3), Ok(2));
    assert_eq!(sent(&h), before);
}

#[test]
fn failed_victim_close_retires_all_views_once_without_publishing_or_replay() {
    let mut h = Harness::new(Fault::Close, [-9, -5]);
    let p = parent(&mut h);
    let f = h.fds.as_mut().unwrap();
    f.open_read(p, b"file", false).unwrap();
    f.open_read(p, b"file", false).unwrap();
    assert!(matches!(
        f.replace(p, 3, 4),
        Err(ProcessError::Files(Failure::Source(_)))
    ));
    assert_eq!(f.cleanup(), Some([-9, -5]));
    assert_eq!(
        f.file_view_v1(p),
        Err(ProcessError::Files(Failure::Retired))
    );
    let before = sent(&h);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(
        f.replace(p, 3, 4),
        Err(ProcessError::Files(Failure::Retired))
    );
    assert_eq!(sent(&h), before);
    assert_eq!(closes(&h), 1);
    let endpoint_closes = h.local.lock().unwrap().closes;
    assert_eq!(endpoint_closes, 1);
}
