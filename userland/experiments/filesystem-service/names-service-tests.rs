// SPDX-License-Identifier: BSD-2-Clause
//! Selected AF05 actual native-entry tests, host engine/transport substitutes.
use super::*;

fn component(length: usize, last: u8) -> Vec<u8> {
    let mut name = vec![b'a'; length];
    if let Some(byte) = name.last_mut() {
        *byte = last;
    }
    name
}
#[test]
fn component_boundaries_and_last_bytes_survive_create_lookup_write_and_remove() {
    for length in [1, 16, 17, 63, 64, 65, 254, 255] {
        let first = component(length, b'b');
        let second = component(length, b'c');
        let wrong = component(length, b'd');
        let commands = vec![
            named(7, &first, &[]),
            named(1, &first, &[]),
            data(5, 2, 0, 4096, 71),
            named(8, &first, &second),
            named(1, &wrong, &[]).denied(-2),
            named(1, &second, &[]),
            request(3, 2),
            request(3, 3),
            named(9, &second, &[]),
            request(4, 0),
        ];
        reset(0, &commands);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (code, out.stop, out.requests, count(2)),
            (0, 0, 10, 4),
            "NAMES_FULL_BYTES"
        );
        decoded(&commands);
        clean();
    }
}
#[test]
fn rename510_is_complete_but511_and_oversized_components_are_rejected() {
    let name = component(255, b'b');
    let to = component(255, b'c');
    let commands = vec![
        named(7, &name, &[]),
        named(8, &name, &to),
        named(9, &to, &[]),
        request(4, 0),
    ];
    reset(0, &commands);
    assert_eq!(invoke(15, 1000, 1000).0, 0);
    decoded(&commands);
    clean();
    for (first, second) in [(256, 0), (255, 256), (256, 255), (0, 255)] {
        let command = named(
            if second == 0 { 7 } else { 8 },
            &component(first, b'b'),
            &component(second, b'c'),
        );
        reset(0, &[command, request(4, 0)]);
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.error, out.requests, count(2)),
            (1, -22, 0, 0),
            "NAMES_BOUNDS"
        );
        clean();
    }
}
#[test]
fn malformed_name_headers_and_all_old_versions_close_before_any_effect() {
    for variant in 0..12 {
        let mut bad = named(7, &component(64, b'b'), &[]);
        match variant {
            0 => put(&mut bad.header, 5, 0),
            1 => put(&mut bad.header, 5, 256),
            2 => put(&mut bad.header, 5, 64 | (1 << 32)),
            3 => put(&mut bad.header, 5, u64::MAX),
            4 => put(&mut bad.header, 4, 1),
            5 => bad.header[48] = 1,
            6 => put(&mut bad.header, 2, READER + 1),
            7..=10 => bad.header[7] = b'1' + (variant - 7) as u8,
            _ => {
                put(&mut bad.header, 1, 8);
                put(&mut bad.header, 5, 64);
            }
        }
        reset(0, &[bad, named(7, b"p", &[])]);
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.error, out.requests, count(2)),
            (1, if variant == 6 { -9 } else { -22 }, 0, 0),
            "NAMES_HEADER_NO_EFFECT"
        );
        clean();
    }
}
#[test]
fn partial_long_name_and_rename_frames_never_reach_provider_or_replay() {
    let first = component(255, b'b');
    let second = component(255, b'c');
    for renaming in [false, true] {
        let bad = if renaming {
            named(8, &first, &second)
        } else {
            named(7, &first, &[])
        };
        let mut prefixes: Vec<_> = (0..bad.data.len()).step_by(64).collect();
        prefixes.extend([1, 15, 16, 63, bad.data.len() - 1]);
        for prefix in prefixes {
            reset(
                0,
                &if renaming {
                    vec![named(7, &first, &[])]
                } else {
                    vec![]
                },
            );
            STATE.with(|s| {
                let mut s = s.borrow_mut();
                s.input.extend(bad.header);
                s.input.extend(&bad.data[..prefix]);
            });
            let (_, out) = invoke(15, 1000, 1000);
            assert_eq!(
                (out.stop, out.requests, count(2)),
                (1, u64::from(renaming), u32::from(renaming)),
                "NAMES_PARTIAL_NO_EFFECT"
            );
            clean();
        }
    }
}
#[test]
fn nonzero_name_padding_is_not_a_second_request() {
    for length in [1, 17, 63, 65, 255] {
        let commands = [named(7, &component(length, b'b'), &[]), named(7, b"p", &[])];
        reset(0, &commands);
        STATE.with(|s| s.borrow_mut().input[64 + length] = 0xa5);
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.error, out.requests, count(2)),
            (1, -22, 0, 0),
            "NAMES_PADDING"
        );
        clean();
    }
}
#[test]
fn lexical_names_and_both_rename_components_reject_without_effects() {
    for name in [
        b".".to_vec(),
        b"..".to_vec(),
        b"a/b".to_vec(),
        b"a\0b".to_vec(),
    ] {
        let commands = [named(7, &name, &[]).denied(-22), request(4, 0)];
        reset(0, &commands);
        assert_eq!(invoke(15, 1000, 1000).0, 0);
        assert_eq!(count(2), 0);
        decoded(&commands);
        clean();
        let commands = [
            named(7, b"p", &[]),
            named(8, b"p", &name).denied(-22),
            request(4, 0),
        ];
        reset(0, &commands);
        assert_eq!(invoke(15, 1000, 1000).0, 0);
        assert_eq!(count(2), 1);
        decoded(&commands);
        clean();
    }
}
#[test]
fn complete_long_names_do_not_authorize_stale_tokens_or_escalate_rights() {
    for variant in 0..3 {
        let mut bad = named(if variant == 2 { 1 } else { 7 }, &component(64, b'b'), &[])
            .denied(if variant == 0 { -9 } else { -13 });
        if variant == 0 {
            put(&mut bad.header, 3, 99);
        }
        if variant == 2 {
            put(&mut bad.header, 4, 15);
        }
        reset(0, &[bad.clone(), request(4, 0)]);
        assert_eq!(invoke(if variant == 0 { 15 } else { 1 }, 1000, 1000).0, 0);
        assert_eq!(count(2), 0);
        decoded(&[bad, request(4, 0)]);
        clean();
    }
}
#[test]
fn lost_long_name_reply_preserves_commit_and_never_renames() {
    for prefix in 0..64 {
        let first = component(255, b'b');
        let second = component(255, b'c');
        reset(0, &[named(7, &first, &[]), named(8, &first, &second)]);
        STATE.with(|s| s.borrow_mut().fail_after = Some(64 + prefix));
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.requests, out.txg, out.state, count(2)),
            (2, 1, 788, 2, 1),
            "NAMES_REPLY_NO_REPLAY"
        );
        clean();
    }
}
