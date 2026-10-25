// SPDX-License-Identifier: BSD-2-Clause
// Independent output and lifetime oracle; no command-line parsing policy.
use super::*;
fn expected() -> (&'static [u8], usize, u32) {
    if cfg!(runner_denial) {
        (
            if cfg!(denial_busy) || cfg!(denial_leak) {
                include_bytes!("text/capacity.txt") as &[u8]
            } else if cfg!(denial_rights) {
                include_bytes!("text/denied.txt")
            } else {
                include_bytes!("text/unavailable.txt")
            },
            1,
            2,
        )
    } else if cfg!(stream_exhaust) {
        (&[b'X'; 528], 0, 0)
    } else if cfg!(stream_usage) || cfg!(stream_usage_zero) || cfg!(stream_usage_cut) {
        (include_bytes!("text/usage.txt"), 1, 64)
    } else if cfg!(stream_version) {
        (include_bytes!("text/version.txt"), 0, 0)
    } else {
        (include_bytes!("text/help.txt"), 0, 0)
    }
}
fn reference(j: usize, generation: u32) -> u32 {
    if j < 2 {
        0x75000000 + (((j + 1) as u32) << 16) + generation
    } else {
        super::reference(0, j - 2, generation)
    }
}
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    const COUNT: usize = if cfg!(runner_denial) { 4 } else { 2 };
    let denial_error = if cfg!(denial_busy) || cfg!(denial_leak) {
        -16
    } else if cfg!(denial_rights) {
        -13
    } else {
        -2
    };
    let invalid = cfg!(stream_bad_rights)
        || cfg!(stream_bad_role)
        || cfg!(stream_bad_generation)
        || cfg!(stream_bad_magic)
        || cfg!(stream_missing_role)
        || cfg!(stream_excess_role)
        || cfg!(stream_bad_header_generation)
        || cfg!(stream_bad_header_padding)
        || cfg!(stream_bad_fd)
        || cfg!(stream_bad_capacity)
        || cfg!(stream_bad_record_padding)
        || cfg!(denial_bad_child);
    let (text, sink, status) = expected();
    let zero = cfg!(stream_zero) || cfg!(stream_usage_zero);
    let delivery_failure = zero || cfg!(stream_fatal) || cfg!(stream_exhaust);
    let close_failure = cfg!(stream_close_error);
    let cut_close = cfg!(stream_cut_close) || cfg!(stream_cut_close_partial);
    let cut_write = cfg!(stream_cut_write)
        || cfg!(stream_cut_partial)
        || cfg!(stream_usage_cut)
        || cfg!(stream_cut_skip_retire);
    let cut = cut_write || cut_close;
    let operational = delivery_failure || close_failure || cut;
    let expected_length = if cfg!(stream_exhaust) {
        512
    } else if delivery_failure || cut_write {
        16
    } else {
        text.len()
    };
    for generation in 1..=2 {
        let service = launch(factory, second, 1);
        let mut hello = [0; 32];
        check(transfer(service.reader, &mut hello, false) == 1, 1300);
        let handles = [
            get(&hello, 4),
            get(&hello, 8),
            get(&hello, 12),
            get(&hello, 16),
        ];
        check(
            handles
                == [
                    0xf101,
                    0xf201,
                    0xf202,
                    if cfg!(runner_denial) { 0xf203 } else { 0 },
                ],
            1300,
        );
        let parent = launch(factory, first, 0);
        let mut header = [0; 32];
        header[..8].copy_from_slice(if cfg!(runner_denial) {
            b"AERIO001"
        } else {
            b"AEOUT001"
        });
        put(&mut header, 8, COUNT as u32);
        put(&mut header, 12, generation);
        if cfg!(stream_bad_magic) {
            header[7] = b'2';
        }
        if cfg!(stream_missing_role) {
            put(&mut header, 8, 1);
        }
        if cfg!(stream_excess_role) {
            put(&mut header, 8, 3);
        }
        if cfg!(stream_bad_header_generation) {
            put(&mut header, 12, generation - 1);
        }
        if cfg!(stream_bad_header_padding) {
            header[31] = 1;
        }
        check(transfer(parent.writer, &mut header, true) == 1, 990);
        for j in 0..COUNT {
            let mut b = [0; 32];
            for (i, value) in [
                j as u32 + 1,
                reference(j, generation),
                j as u32 + 1,
                [2, 2, 1, 3][j],
                [512, 256, 6, 64][j],
            ]
            .iter()
            .enumerate()
            {
                put(&mut b, i * 4, *value);
            }
            if j == 3 && cfg!(denial_bad_child) {
                put(&mut b, 12, 2);
            }
            if j == 1 {
                if cfg!(stream_bad_fd) {
                    put(&mut b, 8, 1);
                }
                if cfg!(stream_bad_capacity) {
                    put(&mut b, 16, 512);
                }
                if cfg!(stream_bad_record_padding) {
                    b[31] = 1;
                }
                if cfg!(stream_bad_rights) {
                    put(&mut b, 12, 3);
                }
                if cfg!(stream_bad_role) {
                    put(&mut b, 0, 1);
                }
                if cfg!(stream_bad_generation) {
                    put(&mut b, 4, reference(j, generation - 1));
                }
            }
            check(transfer(parent.writer, &mut b, true) == 1, 990);
        }
        let mut live = [true; COUNT];
        let mut positions = [0u32; COUNT];
        let mut frame = [0u8; 384];
        let mut denied = false;
        let mut used = 0;
        let mut exited = false;
        let mut failure_seen = false;
        let mut reply_closed = false;
        for _ in 0..200000 {
            let state = ctl(0x20001, parent.child);
            check(state.0 >= 0, 1301);
            if state.0 > 0 {
                check(
                    state.0
                        == (if invalid {
                            110
                        } else if operational {
                            1
                        } else {
                            status
                        }) as i64
                            + 1
                        && state.2 == 1,
                    1301,
                );
                let mut pending = [0u8; 1];
                check(
                    used == 0
                        && call(
                            0x24001,
                            parent.reader,
                            pending.as_mut_ptr() as u64,
                            1,
                            0,
                            0,
                            0,
                        )
                        .0 == 0,
                    if cut { 1320 } else { 1302 },
                );
                if cut {
                    check(
                        reply_closed
                            && live
                                == if cut_close {
                                    core::array::from_fn(|j| j != 0)
                                } else {
                                    [true; COUNT]
                                },
                        1321,
                    );
                    // Terminal and channel EOF above establish the client is quiescent.
                    // Retire owner aliases; this is not a client close acknowledgment.
                    if !cfg!(stream_cut_skip_retire) {
                        live = [false; COUNT];
                    }
                    check(live == [false; COUNT], 1321);
                }
                check(invalid || live == [false; COUNT], 1303);
                check(failure_seen == operational, 1311);
                check(!cfg!(runner_denial) || invalid || denied, 1340);
                exited = true;
                break;
            }
            // Synchronous bounded trap; no pointer or alias escapes this call.
            let need = if cfg!(runner_denial) && used >= 4 && word(&frame, 0) == 4 {
                384
            } else {
                32
            };
            let n = call(
                0x24001,
                parent.reader,
                frame[used..].as_mut_ptr() as u64,
                (need - used).min(16) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == 0 || n == -11 {
                ctl(0x1fffe, 0);
                continue;
            }
            check(!reply_closed, 1320);
            check(
                !invalid && n > 0 && n as usize <= (need - used).min(16),
                1302,
            );
            used += n as usize;
            let complete = if cfg!(runner_denial) && word(&frame, 0) == 4 {
                384
            } else {
                32
            };
            if used != complete {
                continue;
            }
            if cfg!(runner_denial) && word(&frame, 0) == 4 {
                check(
                    !denied && live == [true; COUNT] && positions == [0; COUNT],
                    1340,
                );
                let result = match super::validate(
                    &frame,
                    generation,
                    [
                        live.get(2).copied().unwrap_or(false),
                        live.get(3).copied().unwrap_or(false),
                    ],
                ) {
                    Err(error) => error,
                    Ok(args) => {
                        check(denial_error == -16, 1341);
                        let held = ctl(0x24000, 0xd001);
                        check(held.0 > 0, 1342);
                        let error = match admit(factory, third, &args, false) {
                            Err(error) => error,
                            Ok(_) => {
                                end(1341);
                            }
                        };
                        if !cfg!(denial_leak) {
                            check(
                                ctl(0x24003, held.0 as u64).0 == 0 && ctl(0x24003, held.1).0 == 0,
                                1342,
                            );
                        }
                        // Slots allow only three generations: two failed reservations
                        // then one availability probe. The leak control probes early.
                        if generation == 2 || cfg!(denial_leak) {
                            let a = ctl(0x24000, 0xd001);
                            let b = ctl(0x24000, 0xd001);
                            check(a.0 > 0 && b.0 > 0 && ctl(0x24000, 0xd001).0 == -16, 1342);
                            for cap in [a.0 as u64, a.1, b.0 as u64, b.1] {
                                check(ctl(0x24003, cap).0 == 0, 1342);
                            }
                        }
                        error
                    }
                };
                check(result == denial_error, 1341);
                denied = true;
                let mut reply = [0; 32];
                put(
                    &mut reply,
                    0,
                    (if cfg!(denial_wrong_error) {
                        -13
                    } else {
                        result
                    }) as u32,
                );
                check(transfer(parent.writer, &mut reply, true) == 1, 990);
                used = 0;
                frame = [0; 384];
                continue;
            }
            check(!cfg!(runner_denial) || denied, 1340);
            let (op, fd, count) = (word(&frame, 0), word(&frame, 8), word(&frame, 12));
            check(
                (op == 2 || op == 3) && (fd >= 1 && fd <= COUNT as u32),
                1302,
            );
            let j = (fd - 1) as usize;
            check(live[j] && word(&frame, 4) == reference(j, generation), 1302);
            check(
                count <= 16 && frame[16 + count as usize..].iter().all(|b| *b == 0),
                1302,
            );
            let mut reply = [0; 32];
            if op == 3 {
                check(count == 0, 1302);
                live[j] = false;
                if close_failure && j == 0 {
                    check(!failure_seen, 1311);
                    failure_seen = true;
                    put(&mut reply, 0, (-5i32) as u32);
                }
            } else {
                check(j < 2, 1340);
                check(!failure_seen, 1310);
                let n = if cfg!(stream_short) {
                    count.min(1)
                } else {
                    count
                };
                if delivery_failure && !cfg!(stream_exhaust) && positions[j] == 16 {
                    check(j == sink && count > 0, 1311);
                    failure_seen = true;
                    put(&mut reply, 0, if zero { 0 } else { (-5i32) as u32 });
                } else {
                    let b = backend(
                        service,
                        4,
                        handles[j + 1],
                        positions[j],
                        n,
                        &frame[16..16 + n as usize],
                    );
                    let result = get(&b, 0) as i32;
                    if cfg!(stream_exhaust) && positions[j] == 512 {
                        check(j == sink && result == -28 && count > 0, 1311);
                        failure_seen = true;
                    } else {
                        check(result == n as i32, 1304);
                        positions[j] += n;
                    }
                    put(&mut reply, 0, result as u32);
                }
            }
            if (cut_write && op == 2) || (cut_close && op == 3 && j == 0) {
                check(!failure_seen, 1322);
                failure_seen = true;
                if cfg!(stream_cut_partial) || cfg!(stream_cut_close_partial) {
                    // The complete effect is retained, but only eight reply bytes
                    // enter the channel. This stack pointer cannot escape the trap.
                    check(
                        call(0x24002, parent.writer, reply.as_ptr() as u64, 8, 0, 0, 0).0 == 8,
                        1322,
                    );
                }
                check(ctl(0x24003, parent.writer).0 == 0, 1322);
                reply_closed = true;
            } else {
                check(transfer(parent.writer, &mut reply, true) == 1, 990);
            }
            used = 0;
            frame = [0; 384];
        }
        check(exited, 1306);
        for j in 0..if cfg!(runner_denial) { 4 } else { 3 } {
            let expected = if j == 0 {
                &b"abcdef"[..]
            } else if !invalid && j == sink + 1 {
                &text[..expected_length]
            } else {
                &[]
            };
            if j > 0 && j < 3 {
                check(positions[j - 1] as usize == expected.len(), 1305);
            }
            for offset in (0..expected.len()).step_by(16) {
                let count = (expected.len() - offset).min(16);
                let b = backend(service, 2, handles[j], offset as u32, 16, &[]);
                check(
                    get(&b, 0) as usize == count
                        && b[16..16 + count] == expected[offset..offset + count],
                    1305,
                );
            }
            check(
                get(
                    &backend(service, 2, handles[j], expected.len() as u32, 16, &[]),
                    0,
                ) == 0,
                1305,
            );
            check(
                get(&backend(service, 3, handles[j], 0, 0, &[]), 0) == 0,
                1307,
            );
            check(
                get(&backend(service, 2, handles[j], 0, 1, &[]), 0) as i32 == -9,
                1307,
            );
        }
        check(
            ctl(0x24003, parent.reader).0 == 0
                && (reply_closed || ctl(0x24003, parent.writer).0 == 0)
                && ctl(0x20002, parent.child).0 == 0,
            976,
        );
        check(
            ctl(0x24003, service.writer).0 == 0
                && terminal(service.child) == (17, 1)
                && ctl(0x24003, service.reader).0 == 0
                && ctl(0x20002, service.child).0 == 0,
            976,
        );
    }
    end(100)
}
