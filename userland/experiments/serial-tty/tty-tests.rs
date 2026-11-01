// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use std::{format, vec::Vec};

const CALLER: Caller = Caller {
    identity: 7,
    generation: 1,
};
const GRANTS: [Rights; 3] = [
    Rights::READ.union(Rights::MODE),
    Rights::WRITE,
    Rights::WRITE,
];
fn admitted() -> (Terminal, Bindings) {
    Terminal::admit(41, CALLER, GRANTS, Mode::IMMEDIATE).unwrap()
}
fn request(icrnl: bool) -> ModeRequest {
    ModeRequest {
        mode: Mode {
            icrnl,
            ..Mode::IMMEDIATE
        },
        action: ApplyWhen::Now,
    }
}
fn completed(count: usize) -> Completion {
    Completion {
        count,
        stop: Stop::Complete,
    }
}

#[test]
fn admission_alias_read_mode_restore_close_and_successor() {
    let (mut terminal, refs) = admitted();
    let alias = terminal.duplicate(CALLER, &refs.stdin).unwrap();
    assert_eq!(terminal.classify(CALLER, &alias), Ok(Role::Stdin));
    let mut bytes = [165; 8];
    assert_eq!(
        terminal.read(CALLER, &alias, &mut bytes, |out| {
            out[..3].copy_from_slice(b"a\rb");
            completed(3)
        }),
        Ok(ReadOutcome::Bytes(3))
    );
    assert_eq!(&bytes[..4], b"a\rb\xa5");
    let mut saved = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    terminal
        .apply_now(CALLER, &refs.stdin, &mut saved, request(true))
        .unwrap();
    assert_eq!(
        terminal.read(CALLER, &alias, &mut bytes, |out| {
            out[..3].copy_from_slice(b"\r\n\x03");
            completed(3)
        }),
        Ok(ReadOutcome::Bytes(3))
    );
    assert_eq!(&bytes[..3], b"\n\n\x03");
    terminal.restore(CALLER, &refs.stdin, &mut saved).unwrap();
    assert_eq!(terminal.mode, Mode::IMMEDIATE);
    assert_eq!(terminal.close(CALLER, alias), Ok(3), "ALIAS_ISOLATION");
    assert_eq!(
        terminal.classify(CALLER, &refs.stdin),
        Ok(Role::Stdin),
        "ALIAS_ISOLATION"
    );
    terminal.disconnect();
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut bytes, |_| completed(0)),
        Ok(ReadOutcome::Eof)
    );
    let next = Caller {
        identity: 8,
        generation: 2,
    };
    let fresh = terminal.replace(next, GRANTS, Mode::IMMEDIATE).unwrap();
    assert_eq!(terminal.classify(next, &refs.stdin), Err(Error::Stale));
    assert_eq!(terminal.classify(next, &fresh.stdin), Ok(Role::Stdin));
    assert!(!terminal.disconnected && !terminal.failed);
}

#[test]
fn rights_foreign_identity_and_stale_alias_never_call_transport() {
    let (mut terminal, refs) = admitted();
    let before = format!("{terminal:?}");
    let mut calls = 0;
    assert_eq!(
        terminal.write(CALLER, &refs.stdin, b"bad", |_, _| {
            calls += 1;
            completed(3)
        }),
        Err(Error::Denied),
        "CAPABILITY_WRITE"
    );
    assert_eq!(calls, 0);
    let foreign = Caller {
        identity: 99,
        generation: 1,
    };
    assert_eq!(
        terminal.read(foreign, &refs.stdin, &mut [0; 1], |_| {
            calls += 1;
            completed(1)
        }),
        Err(Error::Denied),
        "FOREIGN_SAME_GENERATION"
    );
    assert_eq!(calls, 0);
    assert_eq!(
        terminal.read(CALLER, &refs.stdout, &mut [], |_| panic!("ZERO_AUTH")),
        Err(Error::Denied)
    );
    let (_, foreign_refs) = Terminal::admit(42, CALLER, GRANTS, Mode::IMMEDIATE).unwrap();
    assert_eq!(
        terminal.classify(CALLER, &foreign_refs.stdin),
        Err(Error::Denied)
    );
    let later = Caller {
        generation: 2,
        ..CALLER
    };
    assert_eq!(terminal.classify(later, &refs.stdin), Err(Error::Stale));
    assert_eq!(format!("{terminal:?}"), before, "DENIED_STATE_UNCHANGED");
    let alias = terminal.duplicate(CALLER, &refs.stdin).unwrap();
    terminal.close(CALLER, alias).unwrap();
    let replacement = terminal.duplicate(CALLER, &refs.stdin).unwrap();
    assert_eq!(terminal.classify(CALLER, &alias), Err(Error::Stale));
    assert_eq!(terminal.classify(CALLER, &replacement), Ok(Role::Stdin));
    assert_eq!(terminal.close(CALLER, alias), Err(Error::Stale));
    assert_eq!(
        terminal.duplicate(CALLER, &refs.stdin),
        Err(Error::Exhausted)
    );
}

#[test]
fn zero_length_live_empty_eof_and_interruption_remain_distinct() {
    let (mut terminal, refs) = admitted();
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut [], |_| panic!("ZERO_READ")),
        Ok(ReadOutcome::EmptyRequest)
    );
    assert_eq!(
        terminal.write(CALLER, &refs.stdout, b"", |_, _| panic!("ZERO_WRITE")),
        Ok(0)
    );
    let mut byte = [165];
    for (stop, wanted) in [
        (Stop::Complete, Error::WouldBlock),
        (Stop::WouldBlock, Error::WouldBlock),
        (Stop::Interrupted, Error::Interrupted),
        (Stop::Error(-5), Error::Backend(-5)),
    ] {
        assert_eq!(
            terminal.read(CALLER, &refs.stdin, &mut byte, |out| {
                out[0] = 9;
                Completion { count: 0, stop }
            }),
            Err(wanted)
        );
        assert_eq!(byte, [165], "NO_UNCONFIRMED_INPUT");
    }
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut byte, |_| Completion {
            count: 0,
            stop: Stop::End
        }),
        Ok(ReadOutcome::Eof)
    );
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut [], |_| panic!("EOF_ZERO")),
        Ok(ReadOutcome::EmptyRequest)
    );
    assert_eq!(
        terminal.write(CALLER, &refs.stdout, b"x", |_, _| panic!("HANGUP_WRITE")),
        Err(Error::HungUp)
    );
}

#[test]
fn confirmed_progress_precedes_would_block_and_interruption_without_retry() {
    for stop in [Stop::WouldBlock, Stop::Interrupted, Stop::Complete] {
        let (mut terminal, refs) = admitted();
        let mut out = [165; 32];
        let mut calls = 0;
        assert_eq!(
            terminal.read(CALLER, &refs.stdin, &mut out, |bytes| {
                calls += 1;
                assert_eq!(bytes.len(), 16);
                bytes[..2].copy_from_slice(b"ab");
                Completion { count: 2, stop }
            }),
            Ok(ReadOutcome::Bytes(2)),
            "PROGRESS_BEFORE_ERROR"
        );
        assert_eq!(calls, 1);
        assert_eq!(&out[..3], b"ab\xa5");
        let input = b"0123456789abcdefghijklmnop";
        let mut accepted = Vec::new();
        assert_eq!(
            terminal.write(CALLER, &refs.stderr, input, |role, bytes| {
                calls += 1;
                assert_eq!(role, Role::Stderr);
                assert_eq!(bytes, &input[..16]);
                accepted.extend_from_slice(&bytes[..3]);
                Completion { count: 3, stop }
            }),
            Ok(3),
            "WRITE_PROGRESS_BEFORE_ERROR"
        );
        assert_eq!(calls, 2);
        assert_eq!(accepted, b"012");
        assert_eq!(&input[3..], b"3456789abcdefghijklmnop");
    }
    let (mut terminal, refs) = admitted();
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut [0; 2], |out| {
            out[0] = 3;
            Completion {
                count: 1,
                stop: Stop::End,
            }
        }),
        Ok(ReadOutcome::Bytes(1))
    );
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut [0; 2], |_| panic!(
            "EOF_AFTER_PROGRESS"
        )),
        Ok(ReadOutcome::Eof)
    );
}

#[test]
fn unknown_or_malformed_completion_blocks_further_data_until_replacement() {
    for completion in [
        Completion {
            count: 1,
            stop: Stop::Unknown,
        },
        completed(17),
        Completion {
            count: 0,
            stop: Stop::Error(0),
        },
        Completion {
            count: 1,
            stop: Stop::Error(-5),
        },
    ] {
        let (mut terminal, refs) = admitted();
        let mut out = [165; 16];
        assert_eq!(
            terminal.read(CALLER, &refs.stdin, &mut out, |bytes| {
                bytes[0] = 7;
                completion
            }),
            Err(Error::UnknownCompletion)
        );
        assert_eq!(out, [165; 16]);
        assert_eq!(
            terminal.read(CALLER, &refs.stdin, &mut out, |_| panic!("UNKNOWN_REPLAY")),
            Err(Error::UnknownCompletion),
            "UNKNOWN_BLOCKS_DATA"
        );
        assert_eq!(
            terminal.write(CALLER, &refs.stdout, b"x", |_, _| panic!("UNKNOWN_WRITE")),
            Err(Error::UnknownCompletion)
        );
        assert_eq!(
            terminal.write(CALLER, &refs.stdout, b"", |_, _| panic!("UNKNOWN_ZERO")),
            Err(Error::UnknownCompletion)
        );
        let caller = Caller {
            generation: 2,
            ..CALLER
        };
        let fresh = terminal.replace(caller, GRANTS, Mode::IMMEDIATE).unwrap();
        assert_eq!(
            terminal.write(caller, &fresh.stdout, b"x", |_, _| completed(1)),
            Ok(1)
        );
    }
    let (mut terminal, refs) = admitted();
    assert_eq!(
        terminal.write(CALLER, &refs.stdout, b"x", |_, _| Completion {
            count: 0,
            stop: Stop::Unknown
        }),
        Err(Error::UnknownCompletion)
    );
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut [], |_| panic!(
            "UNKNOWN_READ_ZERO"
        )),
        Err(Error::UnknownCompletion)
    );
}

#[test]
fn unsupported_modes_and_actions_preserve_state_and_snapshot() {
    let (mut terminal, refs) = admitted();
    let mut saved = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    let before = format!("{terminal:?}{saved:?}");
    for index in 0..9 {
        let mut invalid = request(false);
        match index {
            0 => invalid.mode.canonical = true,
            1 => invalid.mode.echo = true,
            2 => invalid.mode.signals = true,
            3 => invalid.mode.igncr = true,
            4 => invalid.mode.inlcr = true,
            5 => invalid.mode.opost = true,
            6 => invalid.mode.vmin = 0,
            7 => invalid.mode.vtime = 1,
            _ => invalid.action = ApplyWhen::Drain,
        }
        assert_eq!(
            terminal.apply_now(CALLER, &refs.stdin, &mut saved, invalid),
            Err(Error::Unsupported)
        );
        assert_eq!(format!("{terminal:?}{saved:?}"), before);
    }
    let mut flush = request(false);
    flush.action = ApplyWhen::Flush;
    assert_eq!(
        terminal.apply_now(CALLER, &refs.stdin, &mut saved, flush),
        Err(Error::Unsupported)
    );
    assert_eq!(terminal.snapshot(CALLER, &refs.stdout), Err(Error::Denied));
}

#[test]
fn snapshots_are_revision_bound_idempotent_and_single_use() {
    let (mut terminal, refs) = admitted();
    let mut first = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    let mut competing = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    terminal
        .apply_now(CALLER, &refs.stdin, &mut first, request(false))
        .unwrap();
    assert_eq!(terminal.revision, 2, "VALID_IDEMPOTENCE");
    let before = format!("{terminal:?}{competing:?}");
    assert_eq!(
        terminal.restore(CALLER, &refs.stdin, &mut competing),
        Err(Error::Stale),
        "STALE_SNAPSHOT"
    );
    assert_eq!(format!("{terminal:?}{competing:?}"), before);
    terminal
        .apply_now(CALLER, &refs.stdin, &mut first, request(true))
        .unwrap();
    terminal.restore(CALLER, &refs.stdin, &mut first).unwrap();
    assert_eq!(terminal.mode, Mode::IMMEDIATE);
    assert_eq!(
        terminal.restore(CALLER, &refs.stdin, &mut first),
        Err(Error::Stale)
    );
    let mut stale = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    let caller = Caller {
        identity: 9,
        generation: 2,
    };
    let fresh = terminal.replace(caller, GRANTS, Mode::IMMEDIATE).unwrap();
    assert_eq!(
        terminal.restore(caller, &fresh.stdin, &mut stale),
        Err(Error::Stale)
    );
}

#[test]
fn admission_replacement_and_counter_exhaustion_have_no_partial_effects() {
    assert!(matches!(
        Terminal::admit(0, CALLER, GRANTS, Mode::IMMEDIATE),
        Err(Error::Invalid)
    ));
    let (mut terminal, refs) = admitted();
    let before = format!("{terminal:?}");
    assert_eq!(
        terminal.replace(CALLER, GRANTS, Mode::IMMEDIATE),
        Err(Error::Stale)
    );
    assert_eq!(format!("{terminal:?}"), before);
    terminal.next_serial = u64::MAX;
    let before = format!("{terminal:?}");
    assert_eq!(
        terminal.duplicate(CALLER, &refs.stdin),
        Err(Error::Exhausted)
    );
    assert_eq!(format!("{terminal:?}"), before);
    let mut saved = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    terminal.revision = u64::MAX;
    saved.expected_revision = u64::MAX;
    let before = format!("{terminal:?}{saved:?}");
    assert_eq!(
        terminal.apply_now(CALLER, &refs.stdin, &mut saved, request(true)),
        Err(Error::Exhausted)
    );
    assert_eq!(format!("{terminal:?}{saved:?}"), before);
}

#[test]
fn owner_hangup_drains_backend_prefix_and_remainder_before_eof() {
    let (mut terminal, refs) = admitted();
    let input = b"abcdefghijklmnopqrst";
    let mut offset = 0;
    let mut calls = 0;
    let mut output = [165; 32];
    terminal.disconnect();
    assert_eq!(
        terminal.write(CALLER, &refs.stdout, b"x", |_, _| panic!("HANGUP_WRITE")),
        Err(Error::HungUp)
    );
    for expected in [16, 4, 0] {
        let result = terminal.read(CALLER, &refs.stdin, &mut output, |bytes| {
            calls += 1;
            let count = bytes.len().min(input.len() - offset);
            bytes[..count].copy_from_slice(&input[offset..offset + count]);
            offset += count;
            completed(count)
        });
        assert_eq!(
            result,
            Ok(if expected == 0 {
                ReadOutcome::Eof
            } else {
                ReadOutcome::Bytes(expected)
            }),
            "HANGUP_DRAINS_INPUT"
        );
        if expected == 16 {
            assert_eq!(&output[..16], &input[..16]);
        }
        if expected == 4 {
            assert_eq!(&output[..4], &input[16..]);
        }
    }
    assert_eq!((offset, calls), (20, 3));
    assert_eq!(
        terminal.read(CALLER, &refs.stdin, &mut output, |_| panic!(
            "DRAINED_CALLBACK"
        )),
        Ok(ReadOutcome::Eof)
    );
    let (mut live, refs) = admitted();
    assert_eq!(
        live.read(CALLER, &refs.stdin, &mut output, |_| completed(0)),
        Err(Error::WouldBlock)
    );
}
