// SPDX-License-Identifier: BSD-2-Clause
//! Actual selected Files/service/Client note authority and progress controls.
use super::*;
const NOTE: &[u8] = if cfg!(native_zsh_login_startup) {
    b"/home/.zprofile"
} else {
    b"/home/note"
};
const BYTES: &[u8] = if cfg!(native_zsh_login_startup) {
    b"setopt no_beep;\n"
} else {
    b"AETHER-HOME-158\n"
};
fn create(h: &mut Harness) -> ([u8; 64], Vec<u8>) {
    h.rpc(12, [0, NOTE.len() as u64, 0o600, 0], NOTE)
}
fn prepared() -> Harness {
    #[allow(unused_mut)]
    let mut h = Harness::new();
    #[cfg(native_zsh_home_redirection_reader)]
    {
        let mut s = h.state.lock().unwrap();
        s.note_exists = true;
        s.note = BYTES.to_vec();
    }
    #[cfg(native_zsh_home_redirection_reader)]
    h.files().reopen_note(&mut [0; 4096]).unwrap();
    h
}
#[cfg(not(native_zsh_home_redirection_reader))]
#[test]
fn note_actual_create_write_alias_offset_and_last_close() {
    let mut h = prepared();
    let prior = h.state.lock().unwrap().mutations;
    let (r, b) = create(&mut h);
    let fd = word(&r, 4);
    assert_eq!(word(&r, 1), 0);
    assert_eq!(b.len(), 64);
    assert_eq!(word(b[..64].try_into().unwrap(), 0), 6);
    assert!(h.files().note_io_active());
    assert!(h.files().inherit_child(binding(), child_binding()).is_err());
    let (alias, _) = h.rpc(4, [fd, 10, 0, 0], &[]);
    let alias = word(&alias, 4);
    assert_eq!(word(&h.rpc(2, [alias, 1, 0, 0], &[]).0, 1) as i64, -9);
    assert_eq!(word(&h.rpc(3, [alias, 0, 0, 0], &[]).0, 1) as i64, -22);
    let (w, wb) = h.rpc(11, [alias, 16, 0, 0], BYTES);
    assert_eq!((word(&w, 1), word(&w, 4)), (0, 16));
    assert_eq!(word(wb[..64].try_into().unwrap(), 0), 14);
    assert_eq!(h.files().descriptions.position(fd as i32), Ok(16));
    h.rpc(5, [fd, 0, 0, 0], &[]);
    assert!(h.files().note_io_active());
    h.rpc(5, [alias, 0, 0, 0], &[]);
    assert!(!h.files().note_io_active());
    let (read, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    let read = word(&read, 4);
    let (bytes, body) = h.rpc(2, [read, 16, 0, 0], &[]);
    assert_eq!(word(&bytes, 4), 16);
    assert_eq!(&body[..16], BYTES);
    h.rpc(5, [read, 0, 0, 0], &[]);
    assert!(h.files().note_complete());
    assert_eq!(h.state.lock().unwrap().mutations, prior + 2);
}
#[cfg(not(native_zsh_home_redirection_reader))]
#[test]
fn note_cannot_write_twice_seek_or_mutate_another_description() {
    let mut h = prepared();
    let (r, _) = create(&mut h);
    let fd = word(&r, 4);
    let (other, _) = h.rpc(1, [0, ENTRY.len() as u64, 0, 0], ENTRY);
    let other = word(&other, 4);
    let before = h.state.lock().unwrap().mutations;
    assert_ne!(word(&h.rpc(11, [other, 16, 0, 0], BYTES).0, 1), 0);
    assert_eq!(h.state.lock().unwrap().mutations, before);
    assert_eq!(word(&h.rpc(11, [fd, 16, 0, 0], BYTES).0, 1), 0);
    let after = h.state.lock().unwrap().mutations;
    assert_ne!(word(&h.rpc(11, [fd, 16, 0, 0], BYTES).0, 1), 0);
    assert_eq!(h.state.lock().unwrap().mutations, after);
}
#[cfg(not(native_zsh_home_redirection_reader))]
#[test]
fn note_create_retains_reported_and_unknown_progress_once() {
    for failure in 1..=3 {
        let mut h = prepared();
        h.state.lock().unwrap().note_failure = failure;
        let (r, b) = create(&mut h);
        assert_ne!(word(&r, 1), 0);
        let receipt: &[u8; 64] = b[..64].try_into().unwrap();
        assert_eq!(
            word(receipt, 0),
            match failure {
                1 => 20,
                2 => 18,
                _ => 17,
            }
        );
        assert_eq!(word(receipt, 1), if failure == 2 { 99 } else { 0 });
        assert!(h.files().cleanup().is_some());
        let before = h.requests();
        assert!(h.files().note_io_active());
        assert!(!h.files().note_complete());
        assert_eq!(h.requests(), before);
    }
}
#[cfg(not(native_zsh_home_redirection_reader))]
#[test]
fn note_completed_create_survives_later_lookup_failure() {
    let mut h = prepared();
    h.state.lock().unwrap().note_lookup_failure = true;
    let (r, b) = create(&mut h);
    let receipt: &[u8; 64] = b[..64].try_into().unwrap();
    assert_ne!(word(&r, 1), 0);
    assert_eq!(word(receipt, 0), 22);
    assert!(word(receipt, 1) > 0);
    assert_eq!(word(receipt, 2), 0);
    assert_eq!((word(receipt, 6), word(receipt, 7) as i64), (12, -5));
    assert!(h.state.lock().unwrap().note_exists);
    assert_eq!(h.files().cleanup(), Some([0; 2]));
}
#[test]
fn note_child_cannot_create_open_or_write_parent_note() {
    let mut h = prepared();
    let child = child_binding();
    if cfg!(native_zsh_home_cwd) {
        let before = h.requests();
        assert!(h.files().inherit_child(binding(), child).is_err());
        assert_eq!(h.requests(), before);
        return;
    }
    h.files().inherit_child(binding(), child).unwrap();
    let before = h.requests();
    let files = h.files();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, 12);
    put(&mut raw, 2, child.generation);
    put(&mut raw, 3, 1);
    put(&mut raw, 5, NOTE.len() as u64);
    put(&mut raw, 6, 0o600);
    let mut workspace = [0; 4096];
    workspace[..NOTE.len()].copy_from_slice(NOTE);
    let reply = files.prepare(child, &raw, 64, &mut workspace).unwrap();
    let r = *reply.header();
    reply.delivered();
    assert_ne!(word(&r, 1), 0);
    assert_eq!(h.requests(), before);
}
#[cfg(native_zsh_home_redirection_reader)]
#[test]
fn note_reader_reopens_exact_bytes_without_mutation_and_refuses_create() {
    let mut h = prepared();
    let before = h.state.lock().unwrap().mutations;
    assert_ne!(word(&create(&mut h).0, 1), 0);
    let (r, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    let fd = word(&r, 4);
    let (r, b) = h.rpc(2, [fd, 16, 0, 0], &[]);
    assert_eq!(word(&r, 4), 16);
    assert_eq!(&b[..16], BYTES);
    h.rpc(5, [fd, 0, 0, 0], &[]);
    assert!(h.files().note_complete());
    assert_eq!(h.state.lock().unwrap().mutations, before);
}

#[cfg(not(native_zsh_home_redirection_reader))]
#[test]
fn note_alias_capacity_is_checked_before_create() {
    let mut h = prepared();
    let (r, _) = h.rpc(1, [0, ENTRY.len() as u64, 0, 0], ENTRY);
    let fd = word(&r, 4);
    for minimum in 4..16 {
        assert_eq!(word(&h.rpc(4, [fd, minimum, 0, 0], &[]).0, 1), 0);
    }
    let before = h.state.lock().unwrap().mutations;
    let (r, b) = create(&mut h);
    let receipt: &[u8; 64] = b[..64].try_into().unwrap();
    assert_eq!(word(&r, 1) as i64, -24);
    assert_eq!(word(receipt, 0), 0);
    assert_eq!(word(receipt, 2), 2);
    assert_eq!(h.state.lock().unwrap().mutations, before);
    assert!(!h.state.lock().unwrap().note_exists);
    assert!(h.files().cleanup().is_none());
}
#[cfg(not(native_zsh_home_redirection_reader))]
#[test]
fn note_write_failure_retains_progress_without_advancing_or_replaying() {
    for failure in [4, 5] {
        let mut h = prepared();
        let (r, _) = create(&mut h);
        let fd = word(&r, 4);
        h.state.lock().unwrap().note_failure = failure;
        let (r, b) = h.rpc(11, [fd, 16, 0, 0], BYTES);
        let receipt: &[u8; 64] = b[..64].try_into().unwrap();
        assert_eq!(word(&r, 1) as i64, -5);
        assert_eq!(word(receipt, 0), if failure == 4 { 28 } else { 26 });
        assert_eq!(word(receipt, 2), if failure == 5 { 99 } else { 0 });
        assert!(!h.files().note_complete());
        assert!(h.files().cleanup().is_some());
        assert_eq!(h.seen.lock().unwrap().closes, 1);
    }
}

#[test]
fn note_seek_without_read_never_establishes_completion() {
    let mut h = prepared();
    #[cfg(not(native_zsh_home_redirection_reader))]
    {
        let (r, _) = create(&mut h);
        let fd = word(&r, 4);
        h.rpc(11, [fd, 16, 0, 0], BYTES);
        h.rpc(5, [fd, 0, 0, 0], &[]);
    }
    let (r, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    let fd = word(&r, 4);
    assert_eq!(word(&h.rpc(3, [fd, 16, 0, 0], &[]).0, 1), 0);
    h.rpc(5, [fd, 0, 0, 0], &[]);
    assert!(!h.files().note_complete());
}

#[test]
fn note_dropped_final_close_reply_never_qualifies_completion() {
    let mut h = prepared();
    #[cfg(not(native_zsh_home_redirection_reader))]
    {
        let (r, _) = create(&mut h);
        let fd = word(&r, 4);
        h.rpc(11, [fd, 16, 0, 0], BYTES);
        h.rpc(5, [fd, 0, 0, 0], &[]);
    }
    let (r, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    let fd = word(&r, 4);
    h.rpc(2, [fd, 16, 0, 0], &[]);
    let files = h.files();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, 5);
    put(&mut raw, 2, binding().generation);
    put(&mut raw, 3, files.next);
    put(&mut raw, 4, fd);
    let mut workspace = [0; 4096];
    let reply = files.prepare(binding(), &raw, 0, &mut workspace).unwrap();
    assert!(
        !reply.files.note_complete(),
        "FINAL_CLOSE_REPLY_NOT_DELIVERED"
    );
    drop(reply);
    assert!(!h.files().note_complete());
    assert_eq!(h.files().cleanup(), Some([0; 2]));
}

#[cfg(all(native_zsh_login_startup, not(native_zsh_home_redirection_reader)))]
#[test]
fn login_missing_profile_is_real_lookup_and_keeps_create_live() {
    let mut h = prepared();
    let before = h.state.lock().unwrap().lookups;
    let (r, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    assert_eq!(word(&r, 1) as i64, -2);
    assert_eq!(h.state.lock().unwrap().lookups, before + 1);
    assert!(h.files().cleanup().is_none());
    assert_eq!(h.files().note.phase, 0);
    assert_eq!(word(&create(&mut h).0, 1), 0);
}
#[cfg(all(native_zsh_login_startup, not(native_zsh_home_redirection_reader)))]
#[test]
fn login_unexpected_existing_profile_is_contained_before_parser_or_create() {
    let mut h = prepared();
    {
        let mut s = h.state.lock().unwrap();
        s.note_exists = true;
        s.note = BYTES.to_vec();
    }
    let before = h.state.lock().unwrap().mutations;
    let files = h.files();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, 1);
    put(&mut raw, 2, 31);
    put(&mut raw, 3, files.next);
    put(&mut raw, 5, NOTE.len() as u64);
    let mut workspace = [0; 4096];
    workspace[..NOTE.len()].copy_from_slice(NOTE);
    assert!(matches!(
        files.prepare(binding(), &raw, 64, &mut workspace),
        Err(Error::Closed)
    ));
    assert_eq!(h.files().note.phase, 1);
    assert!(h.files().cleanup().is_some());
    assert!(!h.files().live(binding()));
    assert_eq!(h.state.lock().unwrap().mutations, before);
    assert!(!h.files().note_complete());
}
#[cfg(native_zsh_login_startup)]
#[test]
fn login_scalar_source_reads_alias_shared_offset_eof_and_final_close() {
    let mut h = prepared();
    #[cfg(not(native_zsh_home_redirection_reader))]
    {
        let (r, _) = create(&mut h);
        let fd = word(&r, 4);
        h.rpc(11, [fd, 16, 0, 0], BYTES);
        h.rpc(5, [fd, 0, 0, 0], &[]);
    }
    let (r, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    assert_eq!(word(&r, 1), 0);
    let fd = word(&r, 4);
    let (r, _) = h.rpc(4, [fd, 10, 0, 0], &[]);
    let alias = word(&r, 4);
    h.rpc(5, [fd, 0, 0, 0], &[]);
    for byte in BYTES {
        let (r, b) = h.rpc(2, [alias, 1, 0, 0], &[]);
        assert_eq!(word(&r, 4), 1);
        assert_eq!(b[0], *byte);
    }
    assert_eq!(word(&h.rpc(2, [alias, 1, 0, 0], &[]).0, 4), 0);
    assert!(!h.files().note_complete());
    h.rpc(5, [alias, 0, 0, 0], &[]);
    assert!(h.files().note_complete());
}

#[cfg(all(native_zsh_login_startup, native_zsh_home_redirection_reader))]
#[test]
fn login_cold_invalid_profile_or_unknown_close_never_enables_startup_read() {
    for variant in 0..4 {
        let mut h = Harness::new();
        {
            let mut s = h.state.lock().unwrap();
            s.note_exists = true;
            s.note = BYTES.to_vec();
            match variant {
                0 => {
                    s.note.pop();
                }
                1 => {
                    s.note[0] ^= 1;
                }
                2 => {
                    s.wrong_kind = 7;
                }
                _ => {}
            }
        }
        let before = h.state.lock().unwrap().mutations;
        if variant == 3 {
            let mut seen = h.seen.lock().unwrap();
            seen.fail_close = seen.close_replies + 1;
        }
        assert!(h.files().reopen_note(&mut [0; 4096]).is_err());
        assert!(h.files().cleanup().is_some());
        assert!(!h.files().note_complete());
        assert!(!h.files().live(binding()));
        assert_eq!(h.state.lock().unwrap().mutations, before);
    }
}

#[cfg(native_zsh_home_cwd)]
fn sourced() -> Harness {
    let mut h = prepared();
    let (r, _) = h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE);
    let fd = word(&r, 4);
    assert_eq!(word(&h.rpc(2, [fd, 16, 0, 0], &[]).0, 4), 16);
    h.rpc(5, [fd, 0, 0, 0], &[]);
    assert!(h.files().note_complete());
    h
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn cwd_root_home_relative_reread_uses_actual_directory_and_preserves_denial() {
    let mut h = sourced();
    assert_eq!(MAGIC, b"AEFP0007");
    let (r, body) = h.rpc(9, [0; 4], &[]);
    assert_eq!((word(&r, 1), word(&r, 5)), (0, 2));
    assert_eq!(&body[..2], b"/\0");
    let prior = h.requests();
    let (r, _) = h.rpc(1, [0, 9, 0, 0], b".zprofile");
    assert_eq!(word(&r, 1) as i64, -13);
    assert_eq!(h.requests(), prior);
    assert!(h.files().note_complete());
    assert_eq!(word(&h.rpc(13, [0, 5, 0, 0], b"/home").0, 1), 0);
    let (r, body) = h.rpc(9, [0; 4], &[]);
    assert_eq!((word(&r, 1), word(&r, 5)), (0, 6));
    assert_eq!(&body[..6], b"/home\0");
    let (r, _) = h.rpc(1, [0, 9, 0, 0], b".zprofile");
    assert_eq!(word(&r, 1), 0);
    let fd = word(&r, 4);
    assert!(!h.files().note_complete());
    assert_eq!(word(&h.rpc(13, [0, 1, 0, 0], b"/").0, 1) as i64, -16);
    h.rpc(2, [fd, 16, 0, 0], &[]);
    h.rpc(5, [fd, 0, 0, 0], &[]);
    assert!(h.files().note_complete());
    assert_eq!(word(&h.rpc(13, [0, 1, 0, 0], b"/").0, 1), 0);
    let (r, body) = h.rpc(9, [0; 4], &[]);
    assert_eq!((word(&r, 1), word(&r, 5)), (0, 2));
    assert_eq!(&body[..2], b"/\0");
    #[cfg(not(native_zsh_home_cwd_exec))]
    assert!(h.files().inherit_child(binding(), child_binding()).is_err());
    assert_eq!(h.state.lock().unwrap().cwd_observations, [1, 2, 2, 1, 1]);
}

#[cfg(native_zsh_home_cwd)]
fn cwd_frame(h: &mut Harness, op: u64, args: [u64; 4]) -> [u8; 64] {
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, op);
    put(&mut raw, 2, binding().generation);
    put(&mut raw, 3, h.files().next);
    for (i, value) in args.into_iter().enumerate() {
        put(&mut raw, i + 4, value);
    }
    raw
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn cwd_unknown_change_reply_never_reuses_historical_completion() {
    let mut h = sourced();
    let raw = cwd_frame(&mut h, 13, [0, 5, 0, 0]);
    let mut work = [0; 4096];
    work[..5].copy_from_slice(b"/home");
    let reply = h.files().prepare(binding(), &raw, 64, &mut work).unwrap();
    assert_eq!(word(reply.header(), 1), 0);
    drop(reply);
    assert!(h.files().cleanup().is_some());
    assert!(!h.files().live(binding()));
    assert!(!h.files().note_complete());
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn cwd_known_observation_failure_preserves_root_and_publishes_no_path() {
    let mut h = sourced();
    h.state.lock().unwrap().cwd_failure = 1;
    let (r, body) = h.rpc(13, [0, 5, 0, 0], b"/home");
    assert_eq!(word(&r, 1) as i64, -13);
    assert!(body.is_empty());
    assert!(!h.files().note.cwd_home);
    let (r, body) = h.rpc(9, [0; 4], &[]);
    assert_eq!(word(&r, 1) as i64, -13);
    assert!(body.is_empty());
    assert!(!h.files().note.cwd_home);
    assert!(h.files().note_complete());
    assert!(h.files().cleanup().is_none());
    h.state.lock().unwrap().cwd_failure = 0;
    let (r, body) = h.rpc(9, [0; 4], &[]);
    assert_eq!(word(&r, 1), 0);
    assert_eq!(&body[..2], b"/\0");
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn cwd_busy_path_child_and_header_denials_precede_source_effects() {
    let mut h = prepared();
    let prior = h.requests();
    assert_eq!(word(&h.rpc(13, [0, 5, 0, 0], b"/home").0, 1) as i64, -16);
    assert_eq!(h.requests(), prior);
    let mut h = sourced();
    let prior = h.requests();
    assert_eq!(word(&h.rpc(13, [0, 5, 0, 0], b"/root").0, 1) as i64, -13);
    assert_eq!(word(&h.rpc(1, [0, 3, 0, 0], b"foo").0, 1) as i64, -13);
    let mut work = [0; 4096];
    work[..5].copy_from_slice(b"/home");
    assert!(matches!(
        h.files().change_home_cwd(1, 5, &mut work),
        Err(Failure::Source(Error::Remote(-13)))
    ));
    assert_eq!(h.requests(), prior);
    assert!(h.files().note_complete());
    for variant in 0..4 {
        let mut h = sourced();
        let prior = h.requests();
        let mut raw = cwd_frame(&mut h, 13, [0, 5, 0, 0]);
        match variant {
            0 => raw[..8].copy_from_slice(b"AEFP0006"),
            1 => put(&mut raw, 1, 7),
            2 => put(&mut raw, 2, 999),
            _ => put(&mut raw, 6, 1),
        }
        assert_eq!(h.files().body_length(binding(), &raw), Err(Error::Protocol));
        assert_eq!(h.requests(), prior);
        assert!(!h.files().live(binding()));
    }
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn cwd_admitted_failed_reread_and_partial_read_cannot_reuse_completion() {
    let mut h = sourced();
    h.rpc(13, [0, 5, 0, 0], b"/home");
    h.state.lock().unwrap().note_lookup_denied = true;
    let (r, _) = h.rpc(1, [0, 9, 0, 0], b".zprofile");
    assert_eq!(word(&r, 1) as i64, -13);
    assert_eq!(h.files().note.phase, 5);
    assert!(!h.files().note_complete());
    assert!(h.files().note.cwd_home);
    let mut h = sourced();
    h.rpc(13, [0, 5, 0, 0], b"/home");
    let (r, _) = h.rpc(1, [0, 9, 0, 0], b".zprofile");
    let fd = word(&r, 4);
    h.rpc(2, [fd, 1, 0, 0], &[]);
    h.rpc(5, [fd, 0, 0, 0], &[]);
    assert!(!h.files().note_complete());
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn cwd_unexpected_physical_directory_and_padding_are_contained() {
    for variant in 0..2 {
        let mut h = sourced();
        let raw = cwd_frame(&mut h, 13, [0, 5, 0, 0]);
        let mut work = [0; 4096];
        work[..5].copy_from_slice(b"/home");
        if variant == 0 {
            h.state.lock().unwrap().cwd_failure = 2;
        } else {
            work[5] = 1;
        }
        assert!(h.files().prepare(binding(), &raw, 64, &mut work).is_err());
        assert!(!h.files().live(binding()));
        assert!(!h.files().note.cwd_home);
        assert!(!h.files().note_complete());
    }
}

#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn cwd_exec_child_observes_snapshot_independent_of_parent_and_exec() {
    for home in [false, true] {
        let mut h = sourced();
        if home {
            assert_eq!(word(&h.rpc(13, [0, 5, 0, 0], b"/home").0, 1), 0);
        }
        let child = child_binding();
        h.files().inherit_child(binding(), child).unwrap();
        let (_, path) = rpc_as(&mut h, child, 9, [0; 4]);
        assert_eq!(
            &path[..if home { 6 } else { 2 }],
            if home { &b"/home\0"[..] } else { &b"/\0"[..] }
        );
        let target: &[u8] = if home { b"/" } else { b"/home" };
        assert_eq!(
            word(&h.rpc(13, [0, target.len() as u64, 0, 0], target).0, 1),
            0
        );
        let next = h.files().exec_child(child, child.generation + 1).unwrap();
        let (_, path) = rpc_as(&mut h, next, 9, [0; 4]);
        assert_eq!(
            &path[..if home { 6 } else { 2 }],
            if home { &b"/home\0"[..] } else { &b"/\0"[..] }
        );
        h.files().settle_child(next).unwrap();
        assert!(h.files().child.is_none());
        assert!(!h.files().live(next));
    }
}

#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn cwd_exec_unsettled_profile_never_admits_child() {
    for phase in [0, 1, 5, 6, 8] {
        let mut h = sourced();
        h.files().note.phase = phase;
        let prior = h.requests();
        assert!(h.files().inherit_child(binding(), child_binding()).is_err());
        assert!(h.files().child.is_none());
        assert_eq!(h.requests(), prior);
    }
    let mut h = sourced();
    let raw = cwd_frame(&mut h, 9, [0; 4]);
    let mut work = [0; 4096];
    let reply = h.files().prepare(binding(), &raw, 0, &mut work).unwrap();
    assert!(!reply.files.note_fork_ready());
    reply.delivered();
    assert!(h.files().note_fork_ready());
    h.files().inherit_child(binding(), child_binding()).unwrap();
}

#[cfg(native_zsh_home_cwd_exec)]
fn cwd_exec_child_rpc(
    h: &mut Harness,
    child: Binding,
    op: u64,
    body: &[u8],
) -> ([u8; 64], Vec<u8>) {
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    put(&mut raw, 1, op);
    put(&mut raw, 2, child.generation);
    put(&mut raw, 3, h.files().child_next);
    put(&mut raw, 5, body.len() as u64);
    let mut work = [0; 4096];
    work[..body.len()].copy_from_slice(body);
    let mut reply = h
        .files()
        .prepare(child, &raw, if body.is_empty() { 0 } else { 64 }, &mut work)
        .unwrap();
    let header = *reply.header();
    let payload = reply.body_mut().to_vec();
    reply.delivered();
    (header, payload)
}
#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn cwd_exec_child_denials_and_observation_errors_preserve_actual_state() {
    let mut h = sourced();
    h.rpc(13, [0, 5, 0, 0], b"/home");
    let child = child_binding();
    h.files().inherit_child(binding(), child).unwrap();
    let before = h.requests();
    for (op, path) in [(13, &b"/"[..]), (1, &b".zprofile"[..]), (1, NOTE)] {
        let (r, body) = cwd_exec_child_rpc(&mut h, child, op, path);
        assert!(word(&r, 1) != 0);
        assert!(body.is_empty());
    }
    assert_eq!(h.requests(), before);
    assert!(h.files().note.child_cwd_home);
    assert!(h.files().inherit_child(child, child).is_err());
    h.state.lock().unwrap().cwd_failure = 1;
    let (r, body) = rpc_as(&mut h, child, 9, [0; 4]);
    assert_eq!(word(&r, 1) as i64, -13);
    assert!(body.is_empty());
    assert!(h.files().live(child));
    h.state.lock().unwrap().cwd_failure = 0;
    let (_, body) = rpc_as(&mut h, child, 9, [0; 4]);
    assert_eq!(&body[..6], b"/home\0");
    h.files().settle_child(child).unwrap();
    assert!(!h.files().note.child_cwd_home);
}
#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn cwd_exec_stale_generation_unknown_reply_and_moved_object_retire() {
    for variant in 0..3 {
        let mut h = sourced();
        h.rpc(13, [0, 5, 0, 0], b"/home");
        let child = child_binding();
        h.files().inherit_child(binding(), child).unwrap();
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(MAGIC);
        put(&mut raw, 1, 9);
        put(&mut raw, 2, child.generation);
        put(&mut raw, 3, 1);
        let mut work = [0; 4096];
        match variant {
            0 => {
                h.files().exec_child(child, child.generation + 1).unwrap();
                let before = h.requests();
                assert_eq!(h.files().body_length(child, &raw), Err(Error::Protocol));
                assert_eq!(h.requests(), before);
            }
            1 => {
                let reply = h.files().prepare(child, &raw, 0, &mut work).unwrap();
                assert_eq!(word(reply.header(), 1), 0);
                drop(reply);
            }
            _ => {
                h.state.lock().unwrap().cwd_failure = 2;
                assert!(h.files().prepare(child, &raw, 0, &mut work).is_err());
            }
        }
        assert!(h.files().retired);
        assert!(!h.files().note_complete());
        assert!(!h.files().live(child));
    }
}

#[cfg(native_zsh_repeat_exec)]
fn repeat_second_files() -> (Harness, Binding) {
    let mut h = sourced();
    let image = b"same persisted sealed helper";
    h.state.lock().unwrap().probe = image.to_vec();
    h.files().reopen_file_exec(image, &mut [0; 4096]).unwrap();
    let first = child_binding();
    h.files().inherit_child(binding(), first).unwrap();
    h.files().acquire_file_exec(first, &mut [0; 4096]).unwrap();
    let executed = h.files().exec_child(first, first.generation + 1).unwrap();
    h.files().settle_child(executed).unwrap();
    let second = Binding {
        epoch: 2,
        handle: 0xb0000203,
        generation: 61,
        ..first
    };
    h.files().inherit_child(binding(), second).unwrap();
    (h, second)
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_exact_second_revalidation_is_fresh_closed_and_one_use() {
    let (mut h, child) = repeat_second_files();
    let image = b"same persisted sealed helper";
    let before = h.requests();
    let mut work = [0xa5; 4096];
    h.files()
        .revalidate_file_exec(child, image, &mut work)
        .unwrap();
    assert_eq!(work, [0; 4096]);
    assert!(h.requests() > before);
    assert!(!h.files().file_exec_consumed());
    assert_eq!(
        h.files().acquire_file_exec(child, &mut work),
        Ok(image.len())
    );
    assert_eq!(&work[..image.len()], image);
    assert!(h.files().file_exec_repeated());
    let after = h.requests();
    assert_eq!(
        h.files().revalidate_file_exec(child, image, &mut work),
        Err(Error::Invalid)
    );
    assert_eq!(h.requests(), after, "NO_SECOND_REVALIDATION_REARM");
    assert_eq!(h.state.lock().unwrap().mutations, 0);
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_stale_parent_pending_and_wrong_epoch_deny_before_lookup() {
    for case in 0..5 {
        let (mut h, child) = repeat_second_files();
        let mut caller = child;
        match case {
            0 => caller = binding(),
            1 => caller = child_binding(),
            2 => caller.generation += 1,
            3 => h.files().pending = true,
            _ => h.files().child_pending = true,
        }
        let before = h.requests();
        assert!(
            h.files()
                .revalidate_file_exec(caller, b"same persisted sealed helper", &mut [0; 4096])
                .is_err()
        );
        assert_eq!(h.requests(), before);
        h.files().pending = false;
        h.files().child_pending = false;
        h.files()
            .revalidate_file_exec(child, b"same persisted sealed helper", &mut [0; 4096])
            .unwrap();
    }
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_failed_validation_never_inherits_first_consumed_success_or_rearms() {
    let expected = b"same persisted sealed helper";
    for case in 0..8 {
        let (mut h, child) = repeat_second_files();
        {
            let mut s = h.state.lock().unwrap();
            match case {
                0 => s.probe[0] ^= 1,
                1 => {
                    s.probe.pop();
                }
                2 => s.probe.push(0),
                3 => s.wrong_kind = 6,
                4..=6 => s.probe_read_failure = case - 3,
                _ => (),
            }
        }
        if case == 7 {
            h.seen.lock().unwrap().bad_stat = true;
        }
        let mut work = [0xa5; 4096];
        assert!(
            h.files()
                .revalidate_file_exec(child, expected, &mut work)
                .is_err()
        );
        assert_eq!(work, [0; 4096]);
        assert!(!h.files().file_exec_consumed());
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        let requests = h.requests();
        assert!(
            h.files()
                .revalidate_file_exec(child, expected, &mut work)
                .is_err()
        );
        assert_eq!(h.requests(), requests);
        assert_eq!(h.state.lock().unwrap().mutations, 0);
    }
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_unknown_second_acquire_close_contains_and_never_rearms() {
    let (mut h, child) = repeat_second_files();
    let image = b"same persisted sealed helper";
    h.files()
        .revalidate_file_exec(child, image, &mut [0; 4096])
        .unwrap();
    {
        let mut seen = h.seen.lock().unwrap();
        seen.fail_close = seen.close_replies + 1;
    }
    let mut work = [0xa5; 4096];
    assert!(h.files().acquire_file_exec(child, &mut work).is_err());
    assert_eq!(work, [0; 4096]);
    assert!(!h.files().file_exec_repeated());
    let requests = h.requests();
    assert!(
        h.files()
            .revalidate_file_exec(child, image, &mut work)
            .is_err()
    );
    assert_eq!(h.requests(), requests);
}

#[cfg(native_zsh_operator_login)]
fn operator_login_rpc(
    h: &mut Harness,
    op: u64,
    args: [u64; 4],
    body: &[u8],
    remaining: u32,
) -> ([u8; 64], Vec<u8>) {
    let raw = cwd_frame(h, op, args);
    let mut work = [0; 4096];
    work[..body.len()].copy_from_slice(body);
    let needed = h.files().body_length(binding(), &raw).unwrap();
    let mut reply = h
        .files()
        .prepare_bounded(binding(), &raw, needed, &mut work, remaining)
        .unwrap();
    let head = *reply.header();
    let bytes = reply.body_mut().to_vec();
    reply.delivered();
    (head, bytes)
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_initial_home_is_observed_once_and_failures_cannot_publish() {
    let mut h = prepared();
    let before = h.requests();
    h.files().initialize_home_cwd(&mut [0; 4096]).unwrap();
    assert_eq!(h.requests(), before + 1);
    assert!(h.files().note.cwd_home);
    assert_eq!(
        h.files().initialize_home_cwd(&mut [0; 4096]),
        Err(Error::Invalid)
    );
    for mode in [1, 2] {
        let mut h = prepared();
        h.state.lock().unwrap().cwd_failure = mode;
        assert!(h.files().initialize_home_cwd(&mut [0; 4096]).is_err());
        assert!(!h.files().note.cwd_home);
        assert!(!h.files().note_complete());
    }
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_denied_profile_open_preserves_completion_and_namespace() {
    let mut h = sourced();
    let before = h.requests();
    let phase = h.files().note.phase;
    let need = h.files().shutdown_budget() + 19;
    let (r, _) = operator_login_rpc(&mut h, 1, [0, NOTE.len() as u64, 0, 0], NOTE, need - 1);
    assert_eq!(word(&r, 1) as i64, -28);
    assert_eq!(h.requests(), before);
    assert_eq!(h.files().note.phase, phase);
    assert!(h.files().note_complete());
    let (r, _) = operator_login_rpc(&mut h, 1, [0, NOTE.len() as u64, 0, 0], NOTE, need);
    assert_eq!(word(&r, 1), 0);
    assert_eq!(h.requests(), before + 1);
    assert!(!h.files().note_complete());
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_short_reads_and_eof_keep_actual_last_close_credit() {
    let mut h = sourced();
    let mut remaining = h.files().shutdown_budget() + 19;
    let (r, _) = operator_login_rpc(&mut h, 1, [0, NOTE.len() as u64, 0, 0], NOTE, remaining);
    let fd = word(&r, 4);
    assert_eq!(word(&r, 1), 0);
    remaining -= 1;
    for expected in BYTES {
        let before = h.requests();
        // A competing CWD call cannot steal completion/EOF/close credit.
        let (denied, _) = operator_login_rpc(&mut h, 9, [0; 4], &[], remaining);
        assert_eq!(word(&denied, 1) as i64, -28);
        assert_eq!(h.requests(), before);
        let (r, b) = operator_login_rpc(&mut h, 2, [fd, 1, 0, 0], &[], remaining);
        assert_eq!((word(&r, 1), word(&r, 4)), (0, 1));
        assert_eq!(b[0], *expected);
        remaining -= 1;
    }
    let (r, _) = operator_login_rpc(&mut h, 2, [fd, 1, 0, 0], &[], remaining);
    assert_eq!((word(&r, 1), word(&r, 4)), (0, 0));
    remaining -= 1;
    assert_eq!(remaining, h.files().shutdown_budget());
    let before = h.requests();
    let (r, _) = operator_login_rpc(&mut h, 2, [fd, 1, 0, 0], &[], remaining);
    assert_eq!(word(&r, 1) as i64, -28);
    assert_eq!(h.requests(), before);
    let (r, _) = operator_login_rpc(&mut h, 5, [fd, 0, 0, 0], &[], remaining);
    assert_eq!(word(&r, 1), 0);
    assert!(h.files().note_complete());
    assert_eq!(h.requests(), before + 1);
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_zero_length_reads_and_aliases_do_not_spend_namespace_or_close_credit() {
    let mut h = sourced();
    let need = h.files().shutdown_budget() + 19;
    let (r, _) = operator_login_rpc(&mut h, 1, [0, NOTE.len() as u64, 0, 0], NOTE, need);
    let fd = word(&r, 4);
    let before = h.requests();
    let reserve = h.files().shutdown_budget() + h.files().note_completion_credit();
    let (r, _) = operator_login_rpc(&mut h, 2, [fd, 0, 0, 0], &[], reserve);
    assert_eq!((word(&r, 1), word(&r, 4)), (0, 0));
    assert_eq!(h.requests(), before);
    let (r, _) = operator_login_rpc(&mut h, 4, [fd, 10, 0, 0], &[], reserve);
    assert_eq!(word(&r, 1), 0);
    assert_eq!(
        h.files().shutdown_budget() + h.files().note_completion_credit(),
        reserve
    );
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_each_epoch_revalidates_once_and_keeps_full_current_bytes() {
    let (mut h, second) = repeat_second_files();
    let image = b"same persisted sealed helper";
    for epoch in 2..=4 {
        let child = if epoch == 2 {
            second
        } else {
            let previous = h.files().child.unwrap();
            h.files().settle_child(previous).unwrap();
            let next = Binding {
                epoch,
                handle: 0xb0000003 | u64::from(epoch) << 8,
                generation: 61 + u64::from(epoch),
                ..second
            };
            h.files().inherit_child(binding(), next).unwrap();
            next
        };
        let before = h.requests();
        h.files()
            .revalidate_file_exec(child, image, &mut [0; 4096])
            .unwrap();
        assert_eq!(h.requests(), before + 4);
        h.files().acquire_file_exec(child, &mut [0; 4096]).unwrap();
        assert_eq!(h.requests(), before + 9);
        assert!(h.files().file_exec_epoch_complete(epoch));
        let after = h.requests();
        assert!(
            h.files()
                .revalidate_file_exec(child, image, &mut [0; 4096])
                .is_err()
        );
        assert_eq!(h.requests(), after);
    }
}

#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_live_child_credit_cannot_be_spent_by_cwd_or_file_calls() {
    let (mut h, child) = repeat_second_files();
    assert_eq!(h.files().file_exec_credit(), 9);
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(MAGIC);
    for (i, v) in [9, child.generation, 1, 0, 0, 0, 0].into_iter().enumerate() {
        put(&mut raw, i + 1, v);
    }
    let reserve = h.files().shutdown_budget() + 9;
    let before = h.requests();
    let mut work = [0; 4096];
    let reply = h
        .files()
        .prepare_bounded(child, &raw, 0, &mut work, reserve)
        .unwrap();
    assert_eq!(word(reply.header(), 1) as i64, -28);
    reply.delivered();
    assert_eq!(h.requests(), before);
    assert_eq!(h.files().file_exec_credit(), 9);
    h.files()
        .revalidate_file_exec(child, b"same persisted sealed helper", &mut [0; 4096])
        .unwrap();
    assert_eq!(h.files().file_exec_credit(), 5);
    h.files().acquire_file_exec(child, &mut [0; 4096]).unwrap();
    assert_eq!(h.files().file_exec_credit(), 0);
}

#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_changed_profile_bytes_or_early_eof_contain_without_credit_replay() {
    for bad_eof in [false, true] {
        let mut h = sourced();
        let need = h.files().shutdown_budget() + 19;
        let (r, _) = operator_login_rpc(&mut h, 1, [0, NOTE.len() as u64, 0, 0], NOTE, need);
        let fd = word(&r, 4);
        if bad_eof {
            h.state.lock().unwrap().note.clear();
        } else {
            h.state.lock().unwrap().note[0] ^= 1;
        }
        let raw = cwd_frame(&mut h, 2, [fd, 1, 0, 0]);
        let mut work = [0; 4096];
        assert!(
            h.files()
                .prepare_bounded(binding(), &raw, 0, &mut work, need - 1)
                .is_err()
        );
        assert_eq!(work, [0; 4096]);
        assert_eq!(h.files().cleanup(), Some([0; 2]));
        assert!(!h.files().note_complete());
    }
}

#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_write_denial_keeps_source_and_read_only_states_unchanged() {
    for state in 0..5 {
        let mut h = match state {
            0 => Harness::new(),
            3 => sourced(),
            _ => prepared(),
        };
        let fd = if state == 2 {
            word(&h.rpc(1, [0, NOTE.len() as u64, 0, 0], NOTE).0, 4)
        } else {
            3
        };
        if state == 4 {
            h.files().abort();
        }
        let before = h.requests();
        let phase = h.files().note.phase;
        let completed = h.files().note_complete();
        let mutations = h.state.lock().unwrap().mutations;
        let raw = cwd_frame(&mut h, 11, [fd, 16, 0, 0]);
        let mut work = [0; 4096];
        work[..16].copy_from_slice(BYTES);
        let result = h
            .files()
            .prepare_bounded(binding(), &raw, 64, &mut work, 96);
        if state == 4 {
            assert!(result.is_err());
            drop(result);
        } else {
            let mut reply = result.unwrap();
            assert_eq!(word(reply.header(), 1) as i64, -9);
            assert_eq!(word(reply.header(), 5), 64);
            let receipt: &[u8; 64] = reply.body_mut()[..64].try_into().unwrap();
            assert_eq!(word(receipt, 0), 0);
            assert_eq!(word(receipt, 6), 1);
            reply.delivered();
        }
        assert_eq!(h.requests(), before);
        assert_eq!(h.state.lock().unwrap().mutations, mutations);
        assert_eq!(h.files().note.phase, phase);
        assert_eq!(h.files().note_complete(), completed);
    }
}
