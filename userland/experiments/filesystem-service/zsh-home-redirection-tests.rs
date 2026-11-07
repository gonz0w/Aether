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
