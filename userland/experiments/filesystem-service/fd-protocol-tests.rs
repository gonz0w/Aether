// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_remote_descriptors::NativeIdentity;
const FIRST: u64 = filesystem_remote_descriptors::FIRST_FILE_FD as u64;
#[path = "fd-wire-fixture.rs"]
mod fixture;
use fixture::{Fault, Harness};
fn identity(slot: u32, epoch: u32) -> NativeIdentity {
    NativeIdentity::admitted(
        slot,
        epoch,
        0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
    )
    .unwrap()
}
fn binding(h: &mut Harness) -> Connection {
    let p = h
        .fds
        .as_mut()
        .unwrap()
        .admitted_shell(identity(1, 1), 7)
        .unwrap();
    Connection::bind(p, 77).unwrap()
}
fn request(op: u64, seq: u64, args: [u64; 4]) -> Message {
    let mut f = [0; FRAME];
    f[..8].copy_from_slice(MAGIC);
    put(&mut f, 1, op);
    put(&mut f, 2, 77);
    put(&mut f, 3, seq);
    for (i, v) in args.into_iter().enumerate() {
        put(&mut f, 4 + i, v);
    }
    f
}
fn open(h: &mut Harness, c: &mut Connection, w: &mut [u8; MAX_READ]) {
    w.fill(0);
    w[..4].copy_from_slice(b"file");
    let r = c
        .prepare(h.fds.as_mut().unwrap(), &request(1, 1, [0, 4, 0, 0]), 64, w)
        .ok()
        .unwrap();
    assert_eq!(word(r.header(), 4), FIRST);
    r.delivered();
}
#[test]
fn actual_c_requests_and_actual_rust_replies_interoperate() {
    let input = std::fs::read(std::env::var("AEFD_C_REQUESTS").unwrap()).unwrap();
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let mut w = [0; MAX_READ];
    let mut offset = 0;
    let mut out = std::vec::Vec::new();
    let mut count = 0;
    while offset < input.len() {
        let frame = &input[offset..offset + FRAME];
        offset += FRAME;
        let needed = c.input_length(h.fds.as_mut().unwrap(), frame).unwrap();
        w.fill(0);
        w[..needed].copy_from_slice(&input[offset..offset + needed]);
        offset += needed;
        let reply = c
            .prepare(h.fds.as_mut().unwrap(), frame, needed, &mut w)
            .ok()
            .unwrap();
        out.extend_from_slice(reply.header());
        out.extend_from_slice(reply.body());
        reply.delivered();
        count += 1;
    }
    assert_eq!(count, if cfg!(fs_dup2_wire) { 12 } else { 10 });
    let count = if cfg!(fs_path_wire) { 2 } else { 1 };
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 3).count(), count);
    assert_eq!(h.opcodes().iter().filter(|&&op| op == 1).count(), count);
    std::fs::write(std::env::var("AEFD_RUST_REPLIES").unwrap(), out).unwrap();
    let storage = h.storage.clone();
    drop(h);
    assert_eq!(storage.lock().unwrap().drops, 1);
}
#[test]
fn malformed_header_lengths_reserved_fields_epoch_and_sequence_have_no_source_effects() {
    for mode in 0..73 {
        let mut h = Harness::new(Fault::None, [0; 2]);
        let mut c = binding(&mut h);
        let mut raw = request(5, 1, [FIRST, 0, 0, 0]).to_vec();
        match mode {
            0..=63 => raw.truncate(mode),
            64 => raw.push(0),
            65 => raw[0] ^= 1,
            66 => raw[16] ^= 1,
            67 => raw[24] ^= 1,
            68 => raw[40] = 1,
            69 => raw[48] = 1,
            70 => raw[56] = 1,
            71 => put(raw.as_mut_slice().try_into().unwrap(), 4, 16),
            _ => put(raw.as_mut_slice().try_into().unwrap(), 4, u64::MAX),
        }
        let mut w = [0x77; MAX_READ];
        assert!(c.prepare(h.fds.as_mut().unwrap(), &raw, 0, &mut w).is_err());
        assert_eq!(w, [0; MAX_READ]);
        assert!(h.opcodes().is_empty());
        assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([0; 2]));
    }
}
#[test]
fn every_incomplete_name_body_and_nonzero_padding_reject_before_lookup() {
    for prefix in 0..=256 {
        let mut h = Harness::new(Fault::None, [0; 2]);
        let mut c = binding(&mut h);
        let mut w = [0; MAX_READ];
        w[..255].fill(b'x');
        if prefix == 256 {
            w[255] = 1;
        }
        assert_eq!(
            c.input_length(h.fds.as_mut().unwrap(), &request(1, 1, [0, 255, 0, 0])),
            Ok(256)
        );
        assert!(c
            .prepare(
                h.fds.as_mut().unwrap(),
                &request(1, 1, [0, 255, 0, 0]),
                prefix,
                &mut w
            )
            .is_err());
        assert_eq!(w, [0; MAX_READ]);
        assert!(h.opcodes().is_empty());
    }
}
#[test]
fn canonical_semantic_errors_continue_with_zero_results_and_output() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let mut w = [0x77; MAX_READ];
    for (seq, op, args, body, expected) in [
        (1, 2, [FIRST, 1, 0, 0], b"".as_slice(), -9),
        (2, 99, [0; 4], b"", -38),
        (
            3,
            1,
            [0, 1, 0, 0],
            b"/",
            if cfg!(fs_path_wire) { -21 } else { -22 },
        ),
        (4, 1, [0, 7, 0, 0], b"missing", -2),
    ] {
        w.fill(0);
        w[..body.len()].copy_from_slice(body);
        let r = c
            .prepare(
                h.fds.as_mut().unwrap(),
                &request(op, seq, args),
                if body.is_empty() { 0 } else { 64 },
                &mut w,
            )
            .ok()
            .unwrap();
        assert_eq!(word(r.header(), 1) as i64, expected);
        assert_eq!(word(r.header(), 4), 0);
        assert!(r.body().is_empty());
        r.delivered();
        assert_eq!(w, [0; MAX_READ]);
    }
    w[..4].copy_from_slice(b"file");
    let r = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(1, 5, [1, 4, 0, 0]),
            64,
            &mut w,
        )
        .ok()
        .unwrap();
    assert_eq!(word(r.header(), 4), FIRST);
    r.delivered();
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), None);
}
#[test]
fn dropping_any_pending_response_retires_without_request_or_reply_replay() {
    for mode in 0..3 {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let mut c = binding(&mut h);
        let mut w = [0; MAX_READ];
        if mode == 0 {
            w[..4].copy_from_slice(b"file");
            let r = c
                .prepare(
                    h.fds.as_mut().unwrap(),
                    &request(1, 1, [0, 4, 0, 0]),
                    64,
                    &mut w,
                )
                .ok()
                .unwrap();
            drop(r);
        } else {
            open(&mut h, &mut c, &mut w);
            let r = c
                .prepare(
                    h.fds.as_mut().unwrap(),
                    &request(2, 2, [if mode == 1 { FIRST } else { FIRST + 1 }, 2, 0, 0]),
                    0,
                    &mut w,
                )
                .ok()
                .unwrap();
            if mode == 1 {
                assert_eq!(&r.body()[..2], b"ab");
            }
            drop(r);
        }
        assert_eq!(w, [0; MAX_READ]);
        assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([-9, -5]));
        assert_eq!(
            c.input_length(h.fds.as_mut().unwrap(), &request(5, 2, [FIRST, 0, 0, 0])),
            Err(Error::Retired)
        );
        assert_eq!(h.local.lock().unwrap().closes, 1);
        assert!(!h.opcodes().contains(&4));
    }
}
#[test]
fn confirmed_delivery_advances_sequence_but_stale_sequence_and_wrap_reject() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let mut w = [0; MAX_READ];
    open(&mut h, &mut c, &mut w);
    assert_eq!(
        c.input_length(h.fds.as_mut().unwrap(), &request(5, 1, [FIRST, 0, 0, 0])),
        Err(Error::Protocol)
    );
    assert_eq!(h.opcodes(), [1]);
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    c.next = u64::MAX - 1;
    let r = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(99, u64::MAX - 1, [0; 4]),
            0,
            &mut w,
        )
        .ok()
        .unwrap();
    r.delivered();
    assert_eq!(c.next, u64::MAX);
    assert_eq!(
        c.input_length(h.fds.as_mut().unwrap(), &request(99, u64::MAX, [0; 4])),
        Err(Error::Protocol)
    );
    assert!(h.opcodes().is_empty());
}
#[test]
fn stale_bound_process_and_backend_loss_never_publish_usable_reply() {
    for (stale, unsupported) in [(false, false), (true, false), (true, true)] {
        let mut h = Harness::new(if stale { Fault::None } else { Fault::ReadBody }, [-9, -5]);
        let mut c = binding(&mut h);
        let mut w = [0; MAX_READ];
        open(&mut h, &mut c, &mut w);
        if stale {
            let f = h.fds.as_mut().unwrap();
            let p = f.current(identity(1, 1)).unwrap();
            let child = f.inherited_child(p, identity(2, 1), 9).unwrap();
            c = Connection::bind(child, 77).unwrap();
            f.settled(child).unwrap();
            f.inherited_child(p, identity(2, 2), 9).unwrap();
        }
        let frame = request(
            if unsupported { 99 } else { 2 },
            if stale { 1 } else { 2 },
            if unsupported {
                [0; 4]
            } else {
                [FIRST, 2, 0, 0]
            },
        );
        assert!(c
            .prepare(h.fds.as_mut().unwrap(), &frame, 0, &mut w)
            .is_err());
        assert_eq!(w, [0; MAX_READ]);
        assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([-9, -5]));
    }
}

#[test]
fn forgotten_reply_remains_pending_and_cannot_replay_effects() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let mut workspace = [0; MAX_READ];
    open(&mut h, &mut c, &mut workspace);
    let pending = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(2, 2, [FIRST, 2, 0, 0]),
            0,
            &mut workspace,
        )
        .ok()
        .unwrap();
    assert_eq!(&pending.body()[..2], b"ab");
    std::mem::forget(pending);
    assert!(c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(2, 2, [FIRST, 2, 0, 0]),
            0,
            &mut workspace
        )
        .is_err());
    assert_eq!(workspace, [0; MAX_READ]);
    assert_eq!(h.opcodes(), [1, 2]);
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([0; 2]));
}

#[test]
fn full_4096_body_and_multiframe_eof_keep_exact_counts_and_zero_padding() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    h.storage.lock().unwrap().size = 5003;
    let mut c = binding(&mut h);
    let mut workspace = [0; MAX_READ];
    open(&mut h, &mut c, &mut workspace);
    for (sequence, offset, count, padded) in [(2, 0, 4096, 4096), (3, 4096, 907, 960)] {
        let reply = c
            .prepare(
                h.fds.as_mut().unwrap(),
                &request(2, sequence, [FIRST, 4096, 0, 0]),
                0,
                &mut workspace,
            )
            .ok()
            .unwrap();
        assert_eq!(word(reply.header(), 4), count as u64);
        assert_eq!(word(reply.header(), 5), count as u64);
        assert_eq!(reply.body().len(), padded);
        for (index, &byte) in reply.body()[..count].iter().enumerate() {
            assert_eq!(byte, b'a'.wrapping_add((offset + index) as u8));
        }
        assert!(reply.body()[count..].iter().all(|&byte| byte == 0));
        reply.delivered();
        assert_eq!(workspace, [0; MAX_READ]);
    }
}

#[test]
fn opposite_wire_version_retires_before_any_source_effect() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let mut raw = request(1, 1, [0, 9, 0, 0]);
    let other = if cfg!(fs_dup2_wire) {
        b"AEFP0001"
    } else if cfg!(fs_path_wire) {
        b"AEFD0001"
    } else {
        b"AEFP0001"
    };
    raw[..8].copy_from_slice(other);
    let mut w = [0; MAX_READ];
    w[..9].copy_from_slice(b"/dir/file");
    assert_eq!(
        c.prepare(h.fds.as_mut().unwrap(), &raw, 64, &mut w).err(),
        Some(Error::Protocol)
    );
    assert_eq!(w, [0; MAX_READ]);
    assert!(h.opcodes().is_empty());
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([0; 2]));
}

#[cfg(fs_path_wire)]
#[test]
fn canonical_paths_inherit_descriptions_and_known_failures_preserve_the_root() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let mut c = binding(&mut h);
    let mut w = [0; MAX_READ];
    let mut sequence = 1;
    for (path, expected) in [
        (b"/dir/missing".as_slice(), -2),
        (b"/dir/../file", -22),
        (b"/dir//file", -22),
        (b"/dir/", -22),
        (b"/file/next", -20),
        (b"/dir", -21),
    ] {
        w.fill(0);
        w[..path.len()].copy_from_slice(path);
        let r = c
            .prepare(
                h.fds.as_mut().unwrap(),
                &request(1, sequence, [0, path.len() as u64, 0, 0]),
                64,
                &mut w,
            )
            .ok()
            .unwrap();
        assert_eq!(word(r.header(), 1) as i64, expected);
        assert_eq!(word(r.header(), 4), 0);
        r.delivered();
        assert_eq!(w, [0; MAX_READ]);
        sequence += 1;
    }
    w[..9].copy_from_slice(b"/dir/file");
    let r = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(1, sequence, [0, 9, 0, 0]),
            64,
            &mut w,
        )
        .ok()
        .unwrap();
    assert_eq!(word(r.header(), 4), FIRST);
    r.delivered();
    let parent = h.fds.as_mut().unwrap().current(identity(1, 1)).unwrap();
    let child = h
        .fds
        .as_mut()
        .unwrap()
        .inherited_child(parent, identity(2, 1), 9)
        .unwrap();
    let mut child = Connection::bind(child, 78).unwrap();
    let mut raw = request(2, 1, [FIRST, 2, 0, 0]);
    put(&mut raw, 2, 78);
    let r = child
        .prepare(h.fds.as_mut().unwrap(), &raw, 0, &mut w)
        .ok()
        .unwrap();
    assert_eq!(&r.body()[..2], b"ab");
    r.delivered();
    let r = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(2, sequence + 1, [FIRST, 2, 0, 0]),
            0,
            &mut w,
        )
        .ok()
        .unwrap();
    assert_eq!(&r.body()[..2], b"cd");
    r.delivered();
    let r = c
        .prepare(
            h.fds.as_mut().unwrap(),
            &request(5, sequence + 2, [FIRST, 0, 0, 0]),
            0,
            &mut w,
        )
        .ok()
        .unwrap();
    r.delivered();
    let mut raw = request(5, 2, [FIRST, 0, 0, 0]);
    put(&mut raw, 2, 78);
    let r = child
        .prepare(h.fds.as_mut().unwrap(), &raw, 0, &mut w)
        .ok()
        .unwrap();
    r.delivered();
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), None);
    let closes = h.opcodes().iter().filter(|&&op| op == 3).count();
    assert_eq!(closes, 5);
}

#[cfg(fs_dup2_wire)]
#[path = "fd-dup2-wire-tests.rs"]
mod dup2_tests;
