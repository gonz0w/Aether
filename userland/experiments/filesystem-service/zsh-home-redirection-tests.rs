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
