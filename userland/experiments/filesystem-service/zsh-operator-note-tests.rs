// SPDX-License-Identifier: BSD-2-Clause
//! Actual note RPCs through the Owner, shared table, AF09 Client and service.
use super::*;

const PATH: &[u8] = b"/home/note";

fn send(
    h: &mut Harness,
    actor: Binding,
    op: u64,
    args: [u64; 4],
    input: &[u8],
    remaining: u32,
) -> Result<([u8; FRAME], Vec<u8>), Error> {
    let files = h.files();
    let mut raw = [0; FRAME];
    raw[..8].copy_from_slice(MAGIC);
    for (i, n) in [
        op,
        actor.generation,
        files.sequence(usize::from(actor.slot - 1)),
    ]
    .into_iter()
    .chain(args)
    .enumerate()
    {
        put(&mut raw, i + 1, n);
    }
    let mut work = [0; PAYLOAD];
    work[..input.len()].copy_from_slice(input);
    let length = input.len().div_ceil(FRAME) * FRAME;
    let mut reply = files.prepare_bounded(actor, &raw, length, &mut work, remaining)?;
    let header = *reply.header();
    let body = reply.body_mut().to_vec();
    reply.delivered();
    Ok((header, body))
}

fn ready() -> Harness {
    let mut h = Harness::new();
    {
        let mut state = h.state.lock().unwrap();
        state.note_exists = true;
        state.note = b"setopt no_beep;\n".to_vec();
    }
    h.files().reopen_note(&mut [0; PAYLOAD]).unwrap();
    let path = b"/home/.zprofile";
    let fd = word(&h.rpc(1, [0, path.len() as u64, 0, 0], path).0, 4);
    assert_eq!(word(&h.rpc(2, [fd, 16, 0, 0], &[]).0, 4), 16);
    assert_eq!(word(&h.rpc(2, [fd, 1, 0, 0], &[]).0, 4), 0);
    assert_eq!(word(&h.rpc(5, [fd, 0, 0, 0], &[]).0, 1), 0);
    assert!(h.files().note_complete());
    h
}

fn open(h: &mut Harness) -> [u8; FRAME] {
    h.rpc(1, [0, PATH.len() as u64, 0, 0], PATH).0
}

fn create(h: &mut Harness) -> [u8; FRAME] {
    h.rpc(12, [0, PATH.len() as u64, 0o600, 0], PATH).0
}

fn close(h: &mut Harness, fd: u64) {
    assert_eq!(word(&h.rpc(5, [fd, 0, 0, 0], &[]).0, 1), 0);
}

#[test]
fn scratch_save_bounds_offsets_alias_lifetime_and_exact_request_cost() {
    for length in [1, 256] {
        let mut h = ready();
        let bytes = [b'Z'; 256];
        let before = h.requests();
        let created = create(&mut h);
        assert_eq!(word(&created, 1), 0);
        let fd = word(&created, 4);
        let alias = word(&h.rpc(4, [fd, 10, 0, 0], &[]).0, 4);
        assert!(h.files().inherit_child(binding(), child_binding()).is_err());
        assert_eq!(
            word(
                &h.rpc(11, [alias, length as u64, 0, 0], &bytes[..length]).0,
                4
            ),
            length as u64
        );
        assert_eq!(
            h.files().descriptions.position(fd as i32),
            Ok(length as u64)
        );
        assert_ne!(word(&h.rpc(11, [fd, 1, 0, 0], b"x").0, 1), 0);
        close(&mut h, fd);
        assert!(h.files().scratch_active());
        close(&mut h, alias);
        assert!(!h.files().scratch_active());
        assert_eq!(h.requests() - before, 5);

        let before = h.requests();
        let fd = word(&open(&mut h), 4);
        for expected in bytes[..length].chunks(64) {
            let (header, body) = h.rpc(2, [fd, 64, 0, 0], &[]);
            assert_eq!(word(&header, 4), expected.len() as u64);
            assert_eq!(&body[..expected.len()], expected);
        }
        let (eof, _) = h.rpc(2, [fd, 64, 0, 0], &[]);
        assert_eq!((word(&eof, 1), word(&eof, 4)), (0, 0));
        close(&mut h, fd);
        assert_eq!(h.requests() - before, length.div_ceil(64) + 3);
        h.files().inherit_child(binding(), child_binding()).unwrap();
        assert_eq!(h.state.lock().unwrap().mutations, 2);
    }
}

#[test]
fn scratch_existing_preflight_and_child_denials_do_not_mutate() {
    let mut h = ready();
    h.state.lock().unwrap().scratch = Some(b"preserved".to_vec());
    let before = h.requests();
    let reserve = h.files().shutdown_budget();
    let (result, _) = send(
        &mut h,
        binding(),
        12,
        [0, PATH.len() as u64, 0o600, 0],
        PATH,
        reserve + 2,
    )
    .unwrap();
    assert_eq!(word(&result, 1) as i64, -17);
    assert_eq!(h.requests() - before, 2);
    assert!(h.files().mutation_failure().is_none());
    assert!(h.files().cleanup().is_none());
    let readonly = word(&open(&mut h), 4);
    let before = h.requests();
    assert_eq!(word(&h.rpc(11, [readonly, 1, 0, 0], b"x").0, 1) as i64, -9);
    assert_eq!(h.requests(), before);
    close(&mut h, readonly);
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    let before = h.requests();
    for (op, args, input) in [
        (12, [0, PATH.len() as u64, 0o600, 0], PATH),
        (1, [0, PATH.len() as u64, 0, 0], PATH),
        (11, [3, 1, 0, 0], b"x"),
    ] {
        let (reply, _) = send(&mut h, child, op, args, input, u32::MAX).unwrap();
        assert_ne!(word(&reply, 1), 0);
    }
    let profile = b"/home/.zprofile";
    assert_ne!(
        word(
            &h.rpc(12, [0, profile.len() as u64, 0o600, 0], profile).0,
            1
        ),
        0
    );
    assert_eq!(h.requests(), before);
    let state = h.state.lock().unwrap();
    assert_eq!(state.mutations, 0);
    assert_eq!(state.scratch.as_deref(), Some(b"preserved".as_slice()));
}

#[test]
fn scratch_empty_close_read_error_and_partial_close_need_no_fake_eof() {
    for choice in 0..4 {
        let mut h = ready();
        if choice == 1 {
            let fd = word(&create(&mut h), 4);
            close(&mut h, fd);
            let fd = word(&open(&mut h), 4);
            let (r, _) = h.rpc(2, [fd, 1, 0, 0], &[]);
            assert_eq!((word(&r, 1), word(&r, 4)), (0, 0));
            close(&mut h, fd);
        } else if choice >= 2 {
            h.state.lock().unwrap().scratch = Some(b"12345".to_vec());
            let fd = word(&open(&mut h), 4);
            if choice == 3 {
                h.state.lock().unwrap().scratch_read_error = 13;
            }
            let (r, _) = h.rpc(2, [fd, 2, 0, 0], &[]);
            assert_eq!(word(&r, 1) as i64, if choice == 3 { -13 } else { 0 });
            assert_eq!(word(&r, 4), if choice == 3 { 0 } else { 2 });
            close(&mut h, fd);
        }
        assert_eq!(h.files().disconnect_checked(|_| Ok(())), Ok([0; 2]));
        assert!(h.files().note_complete());
        assert_eq!(h.state.lock().unwrap().mutations, usize::from(choice == 1));
    }
}

#[test]
fn scratch_resource_denial_preserves_write_attempt_and_close_credit() {
    let mut h = ready();
    let (before, reserve) = (h.requests(), h.files().shutdown_budget());
    let (reply, _) = send(
        &mut h,
        binding(),
        12,
        [0, PATH.len() as u64, 0o600, 0],
        PATH,
        reserve + 1,
    )
    .unwrap();
    assert_eq!(word(&reply, 1) as i64, -28);
    assert_eq!(h.requests(), before);
    let (reply, _) = send(
        &mut h,
        binding(),
        12,
        [0, PATH.len() as u64, 0o600, 0],
        PATH,
        reserve + 3,
    )
    .unwrap();
    assert_eq!(word(&reply, 1) as i64, -28);
    assert_eq!(h.requests(), before + 1);
    assert_eq!(h.state.lock().unwrap().mutations, 0);
    let fd = word(&create(&mut h), 4);
    let (before, reserve) = (h.requests(), h.files().shutdown_budget());
    let (reply, _) = send(&mut h, binding(), 11, [fd, 1, 0, 0], b"x", reserve).unwrap();
    assert_eq!(word(&reply, 1) as i64, -28);
    assert_eq!(h.requests(), before);
    assert_eq!(word(&h.rpc(11, [fd, 1, 0, 0], b"x").0, 1), 0);
    close(&mut h, fd);
    let fd = word(&open(&mut h), 4);
    let (before, reserve) = (h.requests(), h.files().shutdown_budget());
    let (reply, _) = send(&mut h, binding(), 2, [fd, 1, 0, 0], b"", reserve).unwrap();
    assert_eq!(word(&reply, 1) as i64, -28);
    assert_eq!(h.requests(), before);
    let (reply, _) = send(&mut h, binding(), 5, [fd, 0, 0, 0], b"", reserve).unwrap();
    assert_eq!(word(&reply, 1), 0);
    assert_eq!(h.files().disconnect_checked(|_| Ok(())), Ok([0; 2]));
}

#[test]
fn scratch_failed_lookup_and_close_do_not_become_absence_or_completion() {
    let mut h = ready();
    h.state.lock().unwrap().scratch_lookup_error = 13;
    assert_eq!(word(&create(&mut h), 1) as i64, -13);
    assert_eq!(h.state.lock().unwrap().mutations, 0);
    h.state.lock().unwrap().scratch_lookup_error = 0;
    let fd = word(&create(&mut h), 4);
    {
        let mut seen = h.seen.lock().unwrap();
        seen.fail_close = seen.close_replies + 1;
    }
    assert_eq!(
        send(&mut h, binding(), 5, [fd, 0, 0, 0], &[], u32::MAX),
        Err(Error::Closed)
    );
    assert!(!h.files().note_complete());
    assert!(h.files().disconnect_checked(|_| Ok(())).is_err());
}

#[test]
fn scratch_excessive_wire_write_and_provider_refusal_never_rearm() {
    let mut h = ready();
    let fd = word(&create(&mut h), 4);
    let before = h.requests();
    assert_eq!(
        send(&mut h, binding(), 11, [fd, 257, 0, 0], &[0; 257], u32::MAX),
        Err(Error::Protocol)
    );
    assert_eq!(h.requests(), before);
    assert_eq!(h.state.lock().unwrap().mutations, 1);

    let mut h = ready();
    h.state.lock().unwrap().note_failure = 3;
    assert_eq!(word(&create(&mut h), 1) as i64, -17);
    assert!(h.files().mutation_failure().is_some());
    assert!(h.files().cleanup().is_some());
    let before = h.requests();
    assert_eq!(
        send(
            &mut h,
            binding(),
            12,
            [0, PATH.len() as u64, 0o600, 0],
            PATH,
            u32::MAX
        ),
        Err(Error::Protocol)
    );
    assert_eq!(h.requests(), before);
    assert_eq!(h.state.lock().unwrap().mutations, 1);
}
