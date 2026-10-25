// SPDX-License-Identifier: BSD-2-Clause
use super::*;

#[test]
fn full_table_exact_replace_shares_offset_and_preserves_inherited_victim() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let f = h.fds.as_mut().unwrap();
    let p = f.current(identity(1, 1)).unwrap();
    for fd in 0..13 {
        assert_eq!(f.open_read(p, b"file", true), Ok(fd));
    }
    for fd in 13..16 {
        assert_eq!(f.duplicate(p, 12, 0, true), Ok(fd));
    }
    let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
    let mut w = [0xa5; MAX_READ];
    let reply = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(7, 1, [15, 0, 0, 0]),
            0,
            &mut w,
        )
        .ok()
        .unwrap();
    assert_eq!(word(reply.header(), 1), 0);
    assert_eq!(word(reply.header(), 4), 0);
    assert!(reply.body().is_empty());
    reply.delivered();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 0);
    let f = h.fds.as_mut().unwrap();
    assert_eq!(f.file_view_v1(p), Ok((0xffff, 0xfffe)));
    f.seek(p, 15, Seek::Set(2)).unwrap();
    assert_eq!(f.position(p, 0), Ok(2));
    assert_eq!(f.position(child, 0), Ok(0));
    assert_eq!(f.position(child, 15), Ok(2));
    f.close(child, 0).unwrap();
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), 1);
}

#[test]
fn malformed_replacement_or_foreign_version_never_changes_source() {
    for (lane, value) in [
        (4, 16),
        (4, u64::MAX),
        (5, 16),
        (5, u64::MAX),
        (6, 1),
        (7, 1),
        (0, 0),
    ] {
        let mut h = Harness::new(Fault::None, [0; 2]);
        let mut c = binding(&mut h);
        let mut raw = request(7, 1, [0, 15, 0, 0]);
        if lane == 0 {
            raw[..8].copy_from_slice(b"AEFP0001");
        } else {
            put(&mut raw, lane, value);
        }
        let mut w = [0xa5; MAX_READ];
        assert_eq!(
            c.prepare(h.fds.as_mut().unwrap(), &raw, 0, &mut w).err(),
            Some(Error::Protocol)
        );
        assert_eq!(w, [0; MAX_READ]);
        assert!(h.opcodes().is_empty());
    }
}

#[test]
fn absent_source_continues_but_failed_victim_close_never_publishes_reply() {
    for fail in [false, true] {
        let mut h = Harness::new(if fail { Fault::Close } else { Fault::None }, [-9, -5]);
        let mut c = binding(&mut h);
        let f = h.fds.as_mut().unwrap();
        let p = f.current(identity(1, 1)).unwrap();
        f.open_read(p, b"file", true).unwrap();
        f.open_read(p, b"file", true).unwrap();
        let mut w = [0xa5; MAX_READ];
        let reply = c.prepare(
            h.fds.as_mut().unwrap(),
            &request(7, 1, [if fail { 0 } else { 15 }, 1, 0, 0]),
            0,
            &mut w,
        );
        if fail {
            assert_eq!(reply.err(), Some(Error::Retired));
        } else {
            let r = reply.ok().unwrap();
            assert_eq!(word(r.header(), 1) as i64, -9);
            r.delivered();
            assert_eq!(h.fds.as_ref().unwrap().file_view_v1(p), Ok((3, 3)));
        }
        assert_eq!(w, [0; MAX_READ]);
        assert_eq!(
            h.fds.as_ref().unwrap().cleanup(),
            if fail { Some([-9, -5]) } else { None }
        );
    }
}

#[test]
fn lost_replacement_response_retires_without_replay() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let mut c = binding(&mut h);
    let f = h.fds.as_mut().unwrap();
    let p = f.current(identity(1, 1)).unwrap();
    f.open_read(p, b"file", true).unwrap();
    let mut w = [0; MAX_READ];
    let r = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(7, 1, [0, 15, 0, 0]),
            0,
            &mut w,
        )
        .ok()
        .unwrap();
    assert_eq!(word(r.header(), 4), 15);
    drop(r);
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([-9, -5]));
    assert_eq!(
        c.prepare(
            h.fds.as_mut().unwrap(),
            &request(7, 1, [0, 15, 0, 0]),
            0,
            &mut w
        )
        .err(),
        Some(Error::Retired)
    );
    assert_eq!(h.opcodes(), [1]);
    assert_eq!(h.local.lock().unwrap().closes, 1);
}
