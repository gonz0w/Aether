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
            2 => {
                if cfg!(native_tty_signal_probe) {
                    invalid.mode.canonical = true;
                } else {
                    invalid.mode.signals = true;
                }
            }
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

#[test]
fn readonly_access_validates_rights_caller_and_retired_reference() {
    let (mut terminal, refs) = admitted();
    assert_eq!(terminal.access(CALLER, &refs.stdin), Ok(GRANTS[0]));
    assert_eq!(terminal.access(CALLER, &refs.stdout), Ok(Rights::WRITE));
    assert!(
        terminal
            .access(
                Caller {
                    generation: 2,
                    ..CALLER
                },
                &refs.stdin
            )
            .is_err()
    );
    terminal.close(CALLER, refs.stdin).unwrap();
    assert!(terminal.access(CALLER, &refs.stdin).is_err());
}

#[test]
fn failed_client_mode_change_rejects_without_mutation() {
    let (mut terminal, refs) = admitted();
    let mut saved = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    assert_eq!(
        terminal.write(CALLER, &refs.stdout, b"x", |_, _| Completion {
            count: 0,
            stop: Stop::Unknown
        }),
        Err(Error::UnknownCompletion)
    );
    assert_eq!(
        terminal.apply_now(CALLER, &refs.stdin, &mut saved, request(true)),
        Err(Error::UnknownCompletion),
        "FAILED_CLIENT_MODE_GUARD"
    );
    assert_eq!(terminal.mode, Mode::IMMEDIATE);
}

#[test]
fn trusted_private_restore_survives_unknown_io_and_all_public_closes() {
    let (mut terminal, refs) = admitted();
    let private = terminal.duplicate(CALLER, &refs.stdin).unwrap();
    let mut baseline = terminal.snapshot(CALLER, &refs.stdin).unwrap();
    terminal
        .apply_now(CALLER, &refs.stdin, &mut baseline, request(true))
        .unwrap();
    terminal
        .write(CALLER, &refs.stdout, b"x", |_, _| Completion {
            count: 0,
            stop: Stop::Unknown,
        })
        .unwrap_err();
    for reference in [refs.stdin, refs.stdout, refs.stderr] {
        terminal.close(CALLER, reference).unwrap();
    }
    assert!(
        terminal
            .restore(CALLER, &refs.stdin, &mut baseline)
            .is_err()
    );
    terminal.restore(CALLER, &private, &mut baseline).unwrap();
    assert_eq!(
        terminal.mode,
        Mode::IMMEDIATE,
        "PRIVATE_LOCAL_BASELINE_RESET"
    );
    assert_eq!(terminal.close(CALLER, private), Ok(0));
}

#[test]
fn mode_revision_exhaustion_has_no_mutation() {
    let (mut t, b) = admitted();
    let mut snapshot = t.snapshot(CALLER, &b.stdin).unwrap();
    t.revision = u64::MAX;
    snapshot.expected_revision = u64::MAX;
    assert_eq!(
        t.apply_now(CALLER, &b.stdin, &mut snapshot, request(true)),
        Err(Error::Exhausted)
    );
    assert_eq!(t.mode, Mode::IMMEDIATE);
    assert_eq!(t.revision, u64::MAX);
}

#[test]
fn data_reference_cannot_query_or_snapshot_mode() {
    let (t, b) = Terminal::admit(
        41,
        CALLER,
        [Rights::READ, Rights::WRITE, Rights::WRITE],
        Mode::IMMEDIATE,
    )
    .unwrap();
    assert_eq!(
        t.mode_state(CALLER, &b.stdin),
        Err(Error::Denied),
        "EXPLICIT_CORE_MODE_GRANT"
    );
    assert!(matches!(t.snapshot(CALLER, &b.stdin), Err(Error::Denied)));
}

#[cfg(native_tty_signal_probe)]
#[test]
fn selected_signal_mode_admits_only_the_limited_profile() {
    let caller = Caller {
        identity: 7,
        generation: 1,
    };
    let mode = Mode {
        signals: true,
        icrnl: true,
        ..Mode::IMMEDIATE
    };
    assert!(
        Terminal::admit(
            41,
            caller,
            [
                Rights::READ.union(Rights::MODE),
                Rights::WRITE,
                Rights::WRITE
            ],
            mode
        )
        .is_ok(),
        "SELECTED_LIMITED_ISIG_PROFILE"
    );
}

#[cfg(native_tty_signal_probe)]
mod signal_cases {
    use super::*;
    use std::{collections::VecDeque, vec};
    struct Input {
        bytes: VecDeque<u8>,
        posts: VecDeque<Result<u8, Error>>,
        count: usize,
    }
    impl SignalInput for Input {
        fn read(&mut self, out: &mut [u8]) -> Completion {
            assert_eq!(out.len(), 1, "ONE_BYTE_NO_SUFFIX");
            match self.bytes.pop_front() {
                Some(b) => {
                    out[0] = b;
                    Completion {
                        count: 1,
                        stop: Stop::Complete,
                    }
                }
                None => Completion {
                    count: 0,
                    stop: Stop::WouldBlock,
                },
            }
        }
        fn post_sigint(&mut self) -> Result<u8, Error> {
            self.count += 1;
            self.posts.pop_front().unwrap()
        }
    }
    #[test]
    fn handled_ignored_masked_positive_and_unknown_outcomes() {
        for (eligible, post, data, expected, remaining) in [
            (true, 1, vec![3, b'X'], Err(Error::Interrupted), vec![b'X']),
            (true, 2, vec![3, b'X'], Err(Error::Interrupted), vec![b'X']),
            (true, 0, vec![3, b'X'], Ok(ReadOutcome::Bytes(1)), vec![]),
            (false, 1, vec![3, b'X'], Ok(ReadOutcome::Bytes(1)), vec![]),
            (
                true,
                1,
                vec![b'P', 3, b'X'],
                Ok(ReadOutcome::Bytes(1)),
                vec![b'X'],
            ),
        ] {
            let (mut t, refs) = admitted();
            let mut saved = t.snapshot(CALLER, &refs.stdin).unwrap();
            let mut mode = request(true);
            mode.mode.signals = true;
            t.apply_now(CALLER, &refs.stdin, &mut saved, mode).unwrap();
            let mut input = Input {
                bytes: data.into(),
                posts: vec![Ok(post)].into(),
                count: 0,
            };
            let mut out = [0xa5; 4];
            assert_eq!(
                t.read_signalled(CALLER, &refs.stdin, &mut out, eligible, &mut input),
                expected,
                "SIGNAL_ELIGIBILITY_AND_PROGRESS"
            );
            assert_eq!(input.count, 1);
            assert_eq!(input.bytes, remaining);
            if expected == Err(Error::Interrupted) {
                assert_eq!(out, [0xa5; 4], "INTERRUPTED_SENTINEL_UNTOUCHED");
            } else {
                assert_eq!(out[0], if post == 0 || !eligible { b'X' } else { b'P' });
            }
        }
        for result in [
            Ok(3),
            Err(Error::Backend(-95)),
            Err(Error::UnknownCompletion),
        ] {
            let (mut t, refs) = admitted();
            let mut saved = t.snapshot(CALLER, &refs.stdin).unwrap();
            let mut mode = request(false);
            mode.mode.signals = true;
            t.apply_now(CALLER, &refs.stdin, &mut saved, mode).unwrap();
            let mut input = Input {
                bytes: vec![3, b'X'].into(),
                posts: vec![result].into(),
                count: 0,
            };
            let mut out = [0xa5; 2];
            assert_eq!(
                t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
                Err(Error::UnknownCompletion),
                "UNKNOWN_POST_CONTAINS"
            );
            assert_eq!(
                t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
                Err(Error::UnknownCompletion)
            );
            assert_eq!(input.count, 1, "NO_POST_REPLAY");
            assert_eq!(out, [0xa5; 2]);
            assert_eq!(input.bytes, vec![b'X']);
        }
    }
}

#[cfg(native_tty_signal_probe)]
mod signal_review_cases {
    use super::*;
    use std::collections::VecDeque;
    struct Input {
        results: VecDeque<Completion>,
        calls: usize,
    }
    impl SignalInput for Input {
        fn read(&mut self, out: &mut [u8]) -> Completion {
            self.calls += 1;
            let result = self
                .results
                .pop_front()
                .expect("NO_SECOND_BACKEND_AFTER_FINAL_PREFIX");
            if result.count == 1 {
                out[0] = b'P';
            }
            result
        }
        fn post_sigint(&mut self) -> Result<u8, Error> {
            panic!("NO_SIGNAL_BYTE")
        }
    }
    #[test]
    fn known_backend_error_preserves_confirmed_prefix_unknown_stays_closed() {
        for stop in [Stop::Error(-5), Stop::Unknown] {
            let (mut t, refs) = admitted();
            let mut out = [0xa5; 3];
            let mut input = Input {
                results: [
                    Completion {
                        count: 1,
                        stop: Stop::Complete,
                    },
                    Completion { count: 0, stop },
                ]
                .into(),
                calls: 0,
            };
            assert_eq!(
                t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
                if stop == Stop::Unknown {
                    Err(Error::UnknownCompletion)
                } else {
                    Ok(ReadOutcome::Bytes(1))
                },
                "CONFIRMED_PREFIX_BEFORE_KNOWN_ERROR"
            );
            assert_eq!(
                out,
                if stop == Stop::Unknown {
                    [0xa5; 3]
                } else {
                    [b'P', 0xa5, 0xa5]
                }
            );
            assert_eq!(input.calls, 2);
            if stop == Stop::Unknown {
                assert_eq!(
                    t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
                    Err(Error::UnknownCompletion)
                );
                assert_eq!(input.calls, 2, "UNKNOWN_NO_REPLAY");
            }
        }
        let (mut t, refs) = admitted();
        let mut out = [0xa5; 3];
        let mut input = Input {
            results: [Completion {
                count: 0,
                stop: Stop::Error(-5),
            }]
            .into(),
            calls: 0,
        };
        assert_eq!(
            t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
            Err(Error::Backend(-5))
        );
        assert_eq!(out, [0xa5; 3]);
        assert_eq!(input.calls, 1);
    }
    #[test]
    fn final_prefix_stops_backend_and_next_read_is_eof() {
        let (mut t, refs) = admitted();
        let mut out = [0xa5; 3];
        let mut input = Input {
            results: [Completion {
                count: 1,
                stop: Stop::End,
            }]
            .into(),
            calls: 0,
        };
        assert_eq!(
            t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
            Ok(ReadOutcome::Bytes(1)),
            "CERTIFIED_FINAL_PREFIX"
        );
        assert_eq!(out, [b'P', 0xa5, 0xa5]);
        assert_eq!(input.calls, 1);
        assert_eq!(
            t.read_signalled(CALLER, &refs.stdin, &mut out, true, &mut input),
            Ok(ReadOutcome::Eof)
        );
        assert_eq!(input.calls, 1, "EOF_NO_BACKEND_REENTRY");
    }
}

#[cfg(native_tty_canonical_probe)]
#[test]
fn canonical_selected_fixed_saved_tuple_is_supported() {
    let mode = Mode {
        canonical: true,
        echo: true,
        signals: true,
        icrnl: true,
        opost: true,
        ..Mode::IMMEDIATE
    };
    assert!(
        Terminal::admit(
            41,
            CALLER,
            [
                Rights::READ.union(Rights::MODE),
                Rights::WRITE,
                Rights::WRITE
            ],
            mode
        )
        .is_ok(),
        "FIXED_CANONICAL_S_IS_REAL"
    );
}

#[cfg(native_tty_canonical_probe)]
mod canonical_cases {
    use super::*;
    use std::{collections::VecDeque, vec, vec::Vec};
    struct Input {
        bytes: VecDeque<u8>,
        tx: VecDeque<i64>,
        physical: Vec<u8>,
        reads: usize,
        writes: usize,
        posts: usize,
        post: u8,
        end: bool,
    }
    impl Input {
        fn new(bytes: &[u8]) -> Self {
            Self {
                bytes: bytes.to_vec().into(),
                tx: VecDeque::new(),
                physical: vec![],
                reads: 0,
                writes: 0,
                posts: 0,
                post: 1,
                end: false,
            }
        }
    }
    impl SignalInput for Input {
        fn read(&mut self, out: &mut [u8]) -> Completion {
            assert_eq!(out.len(), 1);
            self.reads += 1;
            if let Some(b) = self.bytes.pop_front() {
                out[0] = b;
                Completion {
                    count: 1,
                    stop: Stop::Complete,
                }
            } else {
                Completion {
                    count: 0,
                    stop: if self.end {
                        Stop::End
                    } else {
                        Stop::WouldBlock
                    },
                }
            }
        }
        fn post_sigint(&mut self) -> Result<u8, Error> {
            self.posts += 1;
            Ok(self.post)
        }
        fn write(&mut self, role: Role, bytes: &[u8]) -> Completion {
            assert!(matches!(role, Role::Stdout | Role::Stderr));
            self.writes += 1;
            let count = self.tx.pop_front().unwrap_or(bytes.len() as i64);
            if count > 0 && count as usize <= bytes.len() {
                self.physical.extend(&bytes[..count as usize]);
            }
            Completion {
                count: if count > 0 { count as usize } else { 0 },
                stop: if count == -5000 {
                    Stop::Unknown
                } else if count == -11 {
                    Stop::WouldBlock
                } else if count < 0 {
                    Stop::Error(count as i32)
                } else if count == 0 {
                    Stop::End
                } else {
                    Stop::Complete
                },
            }
        }
    }
    fn canonical() -> (Terminal, Bindings) {
        Terminal::admit(
            41,
            CALLER,
            [
                Rights::READ.union(Rights::MODE),
                Rights::WRITE,
                Rights::WRITE,
            ],
            Mode::CANONICAL,
        )
        .unwrap()
    }
    #[test]
    fn records_editing_short_suffix_and_live_eof() {
        let (mut t, b) = canonical();
        let mut io = Input::new(b"abX\x7fc\rqr\x15d\ref\x04\x04g\r");
        let mut out = [0xa5; 16];
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out[..2], true, &mut io),
            Ok(ReadOutcome::Bytes(2))
        );
        assert_eq!(&out[..2], b"ab");
        let before = (io.reads, io.writes);
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Ok(ReadOutcome::Bytes(2))
        );
        assert_eq!(&out[..2], b"c\n");
        assert_eq!(
            (io.reads, io.writes),
            before,
            "SUFFIX_NO_RETRANSLATE_OR_REECHO"
        );
        for expected in [b"d\n".as_slice(), b"ef", b"", b"g\n"] {
            let result = t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io);
            assert_eq!(
                result,
                Ok(if expected.is_empty() {
                    ReadOutcome::Eof
                } else {
                    ReadOutcome::Bytes(expected.len())
                }),
                "CANONICAL_RECORD_BOUNDARY_AND_EOF"
            );
            assert_eq!(&out[..expected.len()], expected);
        }
        assert_eq!(
            io.physical, b"abX\x08 \x08c\r\nqr\r\nd\r\nefg\r\n",
            "EXACT_BYTE_ECHO"
        );
        assert!(io.bytes.is_empty());
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::WouldBlock),
            "EMPTY_EOF_DOES_NOT_HANG_UP"
        );
    }
    #[test]
    fn zero_read_empty_eof_hangup_and_capacity_are_distinct() {
        let (mut t, b) = canonical();
        let mut io = Input::new(&[4]);
        let mut out = [0xa5; 16];
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut [], true, &mut io),
            Ok(ReadOutcome::EmptyRequest)
        );
        assert_eq!(io.reads, 0);
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Ok(ReadOutcome::Eof)
        );
        assert_eq!(io.reads, 1);
        io.bytes.extend(b"xy");
        io.end = true;
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Ok(ReadOutcome::Bytes(2))
        );
        assert_eq!(&out[..2], b"xy");
        let reads = io.reads;
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Ok(ReadOutcome::Eof)
        );
        assert_eq!(io.reads, reads, "PERSISTENT_HANGUP_NO_BACKEND");
        let (mut t, b) = canonical();
        let mut io = Input::new(&[b'a'; 63]);
        io.bytes.extend(b"\x7fb\r");
        for _ in 0..4 {
            assert_eq!(
                t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
                Err(Error::WouldBlock)
            );
        }
        let mut record = vec![];
        for _ in 0..4 {
            assert_eq!(
                t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
                Ok(ReadOutcome::Bytes(16))
            );
            record.extend(out);
        }
        assert_eq!(record.len(), 64);
        assert_eq!(&record[..62], &[b'a'; 62]);
        assert_eq!(&record[62..], b"b\n");
    }
    #[test]
    fn overflow_consumes_once_without_truncated_success() {
        let (mut t, b) = canonical();
        let mut io = Input::new(&[b'x'; 64]);
        let mut out = [0xa5; 16];
        for _ in 0..3 {
            assert_eq!(
                t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
                Err(Error::WouldBlock)
            );
        }
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::Backend(-75)),
            "EXPLICIT_RECORD_OVERFLOW"
        );
        assert_eq!(out, [0xa5; 16]);
        assert_eq!(io.reads, 64);
        assert_eq!(io.physical.len(), 63);
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::UnknownCompletion)
        );
        assert_eq!(io.reads, 64, "OVERFLOW_NO_REPLAY");
    }
    #[test]
    fn partial_echo_and_source_count_preserve_interpreted_suffix() {
        let (mut t, b) = canonical();
        let mut io = Input::new(b"a\r");
        io.tx.extend([-11, 1, 1, -11]);
        let mut out = [0xa5; 4];
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::WouldBlock)
        );
        assert_eq!(io.reads, 1);
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::WouldBlock)
        );
        assert_eq!(io.reads, 2);
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Ok(ReadOutcome::Bytes(2))
        );
        assert_eq!(&out[..2], b"a\n");
        assert_eq!(io.physical, b"a\r\n", "NO_PARTIAL_ECHO_REPLAY");
        io.physical.clear();
        io.tx.extend([1, -11]);
        assert_eq!(
            t.write(CALLER, &b.stdout, b"\nB", |r, p| io.write(r, p)),
            Ok(1),
            "SOURCE_BYTES_NOT_UART_BYTES"
        );
        assert_eq!(io.physical, b"\r");
        let mut snapshot = t.snapshot(CALLER, &b.stdin).unwrap();
        t.apply_now(
            CALLER,
            &b.stdin,
            &mut snapshot,
            ModeRequest {
                mode: Mode::IMMEDIATE,
                action: ApplyWhen::Now,
            },
        )
        .unwrap();
        assert_eq!(
            t.write(CALLER, &b.stdout, b"B", |r, p| io.write(r, p)),
            Ok(1)
        );
        assert_eq!(io.physical, b"\r\nB", "NOW_RETAINS_PREINTERPRETED_SUFFIX");
        let (mut t, b) = canonical();
        let mut io = Input::new(b"");
        io.tx.extend([1, -5000]);
        assert_eq!(
            t.write(CALLER, &b.stdout, b"\n", |r, p| io.write(r, p)),
            Err(Error::UnknownCompletion)
        );
        let writes = io.writes;
        assert_eq!(
            t.write(CALLER, &b.stdout, b"\n", |r, p| io.write(r, p)),
            Err(Error::UnknownCompletion)
        );
        assert_eq!(io.writes, writes, "UNKNOWN_TX_NO_REPLAY");
        assert_eq!(io.physical, b"\r");
    }
    #[test]
    fn zle_swap_retained_prefix_and_snapshot_never_replay_history() {
        let (mut t, b) = canonical();
        let mut snapshot = t.snapshot(CALLER, &b.stdin).unwrap();
        let mut io = Input::new(b"a\r");
        let mut out = [0; 16];
        // An incomplete translated prefix survives the attribute change.
        io.bytes = vec![b'a'].into();
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::WouldBlock)
        );
        let reads = io.reads;
        t.apply_now(
            CALLER,
            &b.stdin,
            &mut snapshot,
            ModeRequest {
                mode: Mode::ZLE,
                action: ApplyWhen::Now,
            },
        )
        .unwrap();
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Ok(ReadOutcome::Bytes(1))
        );
        assert_eq!(out[0], b'a');
        assert_eq!(io.reads, reads);
        io.bytes.extend(b"\0A\r\n\x7f\x04");
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out[..6], true, &mut io),
            Ok(ReadOutcome::Bytes(6))
        );
        assert_eq!(
            &out[..6],
            b"\0A\n\r\x7f\x04",
            "SWAP_ORIGINAL_BYTE_NO_CASCADE"
        );
        assert_eq!(io.physical, b"a", "ZLE_ECHO_OFF");
        t.restore(CALLER, &b.stdin, &mut snapshot).unwrap();
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::WouldBlock),
            "SNAPSHOT_HAS_NO_INPUT_HISTORY"
        );
    }
    #[test]
    fn canonical_signal_flushes_unfinished_record_and_requires_live_echo_output() {
        for (eligible, outcome) in [(true, 0), (false, 1), (true, 1)] {
            let (mut t, b) = canonical();
            let mut io = Input::new(b"ab\x03c\r");
            io.post = outcome;
            let mut out = [0xa5; 8];
            let result = t.read_signalled(CALLER, &b.stdin, &mut out, eligible, &mut io);
            if eligible && outcome == 1 {
                assert_eq!(result, Err(Error::Interrupted));
                assert_eq!(out, [0xa5; 8]);
                assert_eq!(io.bytes, b"c\r".to_vec());
            } else {
                assert_eq!(result, Ok(ReadOutcome::Bytes(2)));
                assert_eq!(&out[..2], b"c\n");
            }
            assert_eq!(io.posts, 1);
            assert!(io.physical.starts_with(b"ab\x03"), "NO_ECHOCTL_CARET");
        }
        let (mut t, b) = canonical();
        t.close(CALLER, b.stdout).unwrap();
        let mut io = Input::new(b"a\r");
        let mut out = [0; 4];
        assert_eq!(
            t.read_signalled(CALLER, &b.stdin, &mut out, true, &mut io),
            Err(Error::Denied)
        );
        assert_eq!((io.reads, io.writes), (0, 0), "NO_ECHO_FROM_RETIRED_OUTPUT");
    }
}
