// SPDX-License-Identifier: BSD-2-Clause
// Direct role/copy prerequisite: one conformance client and one backend.
use super::*;
fn reference(j: usize, generation: u32) -> u32 {
    0x76000000 + ((j as u32) << 16) + generation
}
fn peer_record() {
    if cfg!(cat_action_peer) {
        let mut observed = [0u64; 4];
        check(
            call(0x29001, 10, 0, observed.as_mut_ptr() as u64, 8, 0, 0).0 == 0
                && observed == [1, 0x04000000, 29, 16],
            1591,
        );
    }
}
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    if cfg!(cat_parent_identity) {
        check(call(0x10027, 0, 0, 0, 0, 0, 0).0 == 4, 1592);
        check(call(0x1006e, 1, 2, 3, 4, 5, 6).0 == 0, 1592);
    }
    let invalid = cfg!(cat_files_bad)
        || cfg!(cat_cwd_bad)
        || cfg!(cat_identity_bad)
        || cfg!(cat_bad_rights)
        || cfg!(cat_bad_fd)
        || cfg!(cat_stale)
        || cfg!(cat_missing);
    let input: &[u8] = if cfg!(cat_empty) {
        b""
    } else {
        include_bytes!("cat-input.bin")
    };
    let copy_chunk = if cfg!(toybox_applet) { 16 } else { 11 };
    let fault = cfg!(cat_fault_before) || cfg!(cat_fault_copy) || cfg!(cat_fault_diag);
    let abnormal = fault || cfg!(cat_force_stop);
    let unknown = cfg!(cat_unknown_read)
        || cfg!(cat_unknown_write)
        || cfg!(cat_unknown_diag)
        || cfg!(cat_unknown_close)
        || cfg!(toybox_close_diag_unknown);
    let io_error = cfg!(cat_read_error) || cfg!(cat_write_error) || cfg!(cat_diag_error);
    let close_error = cfg!(cat_close_input) || cfg!(cat_close_output) || cfg!(cat_close_diag);
    if cfg!(cat_action_peer) {
        let requested = [1u64, 0x04000000, 29, 16];
        let mut old = [u64::MAX; 4];
        check(
            call(
                0x29001,
                10,
                requested.as_ptr() as u64,
                old.as_mut_ptr() as u64,
                8,
                0,
                0,
            )
            .0 == 0
                && old == [0; 4],
            1590,
        );
    }
    for generation in 1..=2 {
        let files = if cfg!(cat_file_service) {
            let connection = launch(factory, third, 2);
            let mut hello = [0; 32];
            let mut expected = [0; 32];
            put(&mut expected, 4, 0xf001);
            check(
                transfer(connection.reader, &mut hello, false) == 1 && hello == expected,
                1596,
            );
            if !cfg!(cat_files) {
                file_service_probe(connection, 1);
            }
            Some(connection)
        } else {
            None
        };
        let service = launch(factory, second, if cfg!(cat_parent_swap) { 0 } else { 1 });
        let mut hello = [0; 32];
        check(transfer(service.reader, &mut hello, false) == 1, 1500);
        let handles = [0xf101, 0xf201, 0xf202];
        check(
            (0..3).all(|j| get(&hello, 4 + j * 4) == handles[j]) && get(&hello, 16) == 0,
            1500,
        );
        let client = if cfg!(cat_admission) {
            cat_admission::launch_cat(factory, first)
        } else {
            launch(factory, first, if cfg!(cat_parent_swap) { 1 } else { 0 })
        };
        let mut bootstrap_remaining = if cfg!(cat_cwd_cut_empty) || cfg!(cat_identity_cut_empty) {
            0
        } else if cfg!(cat_cwd_cut_header) || cfg!(cat_identity_cut_header) {
            16
        } else if cfg!(cat_cwd_cut_role) || cfg!(cat_identity_cut_role) {
            48
        } else if cfg!(cat_cwd_cut_metadata) || cfg!(cat_identity_cut_metadata) {
            144
        } else if cfg!(cat_identity_cut_tail) {
            159
        } else if cfg!(cat_cwd_cut_tail) {
            191
        } else if cfg!(cat_files_cut_start) {
            192
        } else if cfg!(cat_files_cut_middle) {
            208
        } else if cfg!(cat_files_cut_tail) {
            223
        } else {
            if cfg!(cat_files) { 224 } else { 192 }
        };
        let mut b = [0; 32];
        b[..8].copy_from_slice(if cfg!(cat_files_version) {
            b"AECAT003"
        } else if cfg!(cat_files) {
            b"AECAT004"
        } else if cfg!(cat_cwd) && !cfg!(cat_cwd_version) {
            b"AECAT003"
        } else if cfg!(cat_identity) && !cfg!(cat_identity_version) {
            b"AECAT002"
        } else {
            b"AECAT001"
        });
        put(&mut b, 8, if cfg!(cat_missing) { 2 } else { 3 });
        put(
            &mut b,
            12,
            if cfg!(cat_identity_stale) {
                generation - 1
            } else {
                generation
            },
        );
        send_bootstrap(client.writer, &mut b, &mut bootstrap_remaining);
        if cfg!(cat_queued_body) {
            let mut acknowledgment = [0; 32];
            let mut expected = [0; 32];
            expected[..8].copy_from_slice(b"AEQUEUE1");
            put(&mut expected, 8, generation);
            check(
                transfer(client.reader, &mut acknowledgment, false) == 1
                    && acknowledgment == expected,
                1595,
            );
            let body = [if cfg!(cat_queued_wrong_marker) {
                0
            } else {
                0xa0 + generation as u8
            }; 16];
            // Header acknowledgment proves an empty queue. This synchronous trap
            // copies the whole live array before the client can consume its marker.
            check(
                call(0x24002, client.writer, body.as_ptr() as u64, 16, 0, 0, 0).0 == 16,
                1595,
            );
        }
        if !cfg!(cat_identity_version)
            && !cfg!(cat_identity_legacy)
            && !cfg!(cat_cwd_version)
            && !cfg!(cat_cwd_legacy)
        {
            for j in 0..3 {
                b = [0; 32];
                for (k, v) in [
                    j as u32 + 1,
                    reference(j, generation),
                    j as u32,
                    if j == 0 { 1 } else { 2 },
                    if j == 2 { 256 } else { 32 },
                ]
                .iter()
                .enumerate()
                {
                    put(&mut b, k * 4, *v);
                }
                if j == 2 {
                    if cfg!(cat_bad_rights) {
                        put(&mut b, 12, 3);
                    }
                    if cfg!(cat_bad_fd) {
                        put(&mut b, 8, 1);
                    }
                    if cfg!(cat_stale) {
                        put(&mut b, 4, reference(j, generation - 1));
                    }
                }
                send_bootstrap(client.writer, &mut b, &mut bootstrap_remaining);
            }
            if cfg!(cat_identity) {
                b = [0; 32];
                let base = 1000 + generation;
                for (j, value) in [
                    base,
                    if cfg!(cat_identity_zero) {
                        0
                    } else {
                        base + 10
                    },
                    base + 20,
                    base + 30,
                    1,
                ]
                .iter()
                .enumerate()
                {
                    put(&mut b, j * 4, *value);
                }
                if cfg!(cat_env) {
                    put(&mut b, 4, base + if cfg!(cat_env_uid) { 1 } else { 0 });
                    put(
                        &mut b,
                        12,
                        base + 20 + if cfg!(cat_env_gid) { 1 } else { 0 },
                    );
                }
                if cfg!(cat_identity_source) {
                    put(&mut b, 16, 2);
                }
                if cfg!(cat_identity_flags) {
                    put(&mut b, 20, 1);
                }
                if cfg!(cat_identity_reserved) {
                    b[31] = 1;
                }
                for (j, bad) in [
                    cfg!(cat_identity_uid),
                    cfg!(cat_identity_euid),
                    cfg!(cat_identity_gid),
                    cfg!(cat_identity_egid),
                ]
                .iter()
                .enumerate()
                {
                    if *bad {
                        put(&mut b, j * 4, u32::MAX);
                    }
                }
                if cfg!(cat_identity_short) {
                    send_half(client.writer, &b);
                } else {
                    send_bootstrap(client.writer, &mut b, &mut bootstrap_remaining);
                }
            }
        }
        if cfg!(cat_cwd) && !cfg!(cat_cwd_version) && !cfg!(cat_cwd_legacy) {
            b = [0; 32];
            put(
                &mut b,
                0,
                if cfg!(cat_cwd_missing) {
                    0
                } else if cfg!(cat_cwd_alias) {
                    reference(0, generation)
                } else if cfg!(cat_cwd_alias_output) {
                    reference(1, generation)
                } else if cfg!(cat_cwd_alias_diagnostic) {
                    reference(2, generation)
                } else {
                    reference(3, generation)
                },
            );
            put(&mut b, 4, if cfg!(cat_cwd_rights) { 3 } else { 1 });
            put(&mut b, 8, if cfg!(cat_cwd_kind) { 2 } else { 1 });
            put(
                &mut b,
                12,
                if cfg!(cat_cwd_stale) {
                    generation - 1
                } else {
                    generation
                },
            );
            if cfg!(cat_cwd_reserved) {
                b[31] = 1;
            }
            if cfg!(cat_cwd_short) {
                send_half(client.writer, &b);
            } else {
                send_bootstrap(client.writer, &mut b, &mut bootstrap_remaining);
            }
        }
        if cfg!(cat_files) && !cfg!(cat_cwd_version) && !cfg!(cat_cwd_legacy) {
            let mut root = [0; 32];
            put(&mut root, 0, reference(4, generation));
            put(&mut root, 4, 1);
            put(&mut root, 8, 1);
            put(&mut root, 12, generation);
            if cfg!(cat_files_missing) {
                put(&mut root, 0, 0);
            }
            for (selected, role) in [
                (cfg!(cat_files_alias_input), 0),
                (cfg!(cat_files_alias_output), 1),
                (cfg!(cat_files_alias_diagnostic), 2),
                (cfg!(cat_files_alias_cwd), 3),
            ] {
                if selected {
                    put(&mut root, 0, reference(role, generation));
                }
            }
            if cfg!(cat_files_rights) {
                put(&mut root, 4, 3);
            }
            if cfg!(cat_files_kind) {
                put(&mut root, 8, 2);
            }
            if cfg!(cat_files_stale) {
                put(&mut root, 12, generation - 1);
            }
            if cfg!(cat_files_reserved) {
                root[31] = 1;
            }
            send_bootstrap(client.writer, &mut root, &mut bootstrap_remaining);
        }
        let mut file_records = [FileRecord::EMPTY; 2];
        let mut file_sequence = 0;
        let mut file_reads = 0;
        if cfg!(cat_cwd_cut)
            || cfg!(cat_identity_cut)
            || cfg!(cat_identity_short)
            || cfg!(cat_identity_version)
            || cfg!(cat_identity_legacy)
            || cfg!(cat_cwd_short)
            || cfg!(cat_cwd_version)
            || cfg!(cat_cwd_legacy)
        {
            check(ctl(0x24003, client.writer).0 == 0, 1500);
        }
        let mut live = [true; 3];
        let mut positions = [0u32; 3];
        let mut request = [0; 32];
        let mut used = 0usize;
        let mut exited = false;
        let mut injected = false;
        let mut uncertain = false;
        let mut stopped = false;
        let mut directory_poisoned = false;
        let mut file_poisoned = false;
        let mut file_uncertain = false;
        let mut pwd_queries = 0usize;
        for _ in 0..200000 {
            let state = ctl(0x20001, client.child);
            check(state.0 >= 0, 1501);
            if state.0 > 0 {
                peer_record();
                check(
                    state.0
                        == if cfg!(cat_signal) {
                            if cfg!(cat_signal_int) { 3 } else { 16 }
                        } else if fault {
                            135
                        } else if cfg!(cat_force_stop) {
                            144
                        } else if cfg!(cat_files_bad) {
                            111
                        } else if cfg!(cat_files_poison) {
                            2
                        } else if cfg!(cat_privileged) || cfg!(cat_syntax) {
                            3
                        } else if cfg!(cat_env) {
                            8
                        } else if cfg!(cat_files) {
                            1
                        } else if cfg!(cat_dash_main) {
                            8
                        } else if invalid {
                            111
                        } else if cfg!(cat_usage) || cfg!(toybox_final_status) {
                            65
                        } else if io_error
                            || close_error
                            || unknown
                            || cfg!(toybox_close_reentry)
                            || cfg!(cat_cwd_poison)
                        {
                            2
                        } else {
                            1
                        }
                        && state.2
                            == if cfg!(cat_signal) {
                                4
                            } else if fault {
                                2
                            } else if cfg!(cat_force_stop) && !cfg!(cat_stop_wrong_kind) {
                                3
                            } else {
                                1
                            },
                    1501,
                );
                if cfg!(cat_signal) {
                    check(
                        ctl(0x20001, client.child) == state
                            && ctl(0x20007, client.child).0 == 0
                            && ctl(0x20001, client.child) == state,
                        1592,
                    );
                }
                let mut pending = [0u8; 1];
                check(
                    used == 0
                        && call(
                            0x24001,
                            client.reader,
                            pending.as_mut_ptr() as u64,
                            1,
                            0,
                            0,
                            0,
                        )
                        .0 == 0,
                    1502,
                );
                check(
                    invalid
                        || live
                            == if abnormal || cfg!(cat_cwd_poison) || cfg!(cat_files_poison) {
                                [true; 3]
                            } else if unknown {
                                if cfg!(toybox_close_policy) {
                                    [
                                        false,
                                        !cfg!(toybox_unknown_output)
                                            && !cfg!(toybox_unknown_diag_close)
                                            && !cfg!(toybox_close_diag_unknown),
                                        !cfg!(toybox_unknown_diag_close),
                                    ]
                                } else {
                                    [!cfg!(cat_unknown_close), true, true]
                                }
                            } else {
                                [false; 3]
                            },
                    1503,
                );
                exited = true;
                break;
            }
            let n = call(
                0x24001,
                client.reader,
                request[used..].as_mut_ptr() as u64,
                (32 - used).min(16) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 || n == 0 {
                ctl(0x1fffe, 0);
                continue;
            }
            check(n > 0 && n as usize <= 32 - used, 1502);
            used += n as usize;
            if used < 32 {
                continue;
            }
            peer_record();
            check(!invalid, 1502);
            check(!uncertain, 1532);
            check(!directory_poisoned, 1593);
            check(!file_poisoned, 1600);
            if cfg!(cat_files) && matches!(get(&request, 0), 6..=8) {
                let mut reply = [0; 32];
                let completed = file_reply(
                    files.unwrap(),
                    &request,
                    generation,
                    &mut file_records,
                    &mut file_sequence,
                    &mut file_reads,
                    &mut reply,
                );
                if !completed {
                    file_uncertain = true;
                    file_poisoned = true;
                    if cfg!(cat_files_backend_late) {
                        late_reply_witness(files.unwrap());
                    }
                    check(ctl(0x24003, client.writer).0 == 0, 1601);
                    request = [0; 32];
                    used = 0;
                    continue;
                }
                let poison_op = if cfg!(cat_files_poison_read) {
                    7
                } else if cfg!(cat_files_poison_close) {
                    8
                } else {
                    6
                };
                if cfg!(cat_files_poison)
                    && !cfg!(cat_files_backend)
                    && get(&request, 0) == poison_op
                {
                    check(get(&reply, 0) == if poison_op == 7 { 4 } else { 0 }, 1600);
                    file_poisoned = true;
                    if cfg!(cat_files_poison_cut) {
                        send_half(client.writer, &reply);
                        check(ctl(0x24003, client.writer).0 == 0, 1600);
                    } else {
                        reply[if poison_op == 6 { 31 } else { 4 }] = 1;
                        check(transfer(client.writer, &mut reply, true) == 1, 1600);
                    }
                } else {
                    check(transfer(client.writer, &mut reply, true) == 1, 1598);
                }
                request = [0; 32];
                used = 0;
                continue;
            }
            if cfg!(cat_cwd) && (get(&request, 8) >= 3 || matches!(get(&request, 0), 4 | 5)) {
                if cfg!(cat_cwd_pwd) {
                    let expected_path: &[u8] = if pwd_queries == 0 { b"/work" } else { b"." };
                    check(
                        get(&request, 4) == reference(3, generation) && get(&request, 8) == 3,
                        1594,
                    );
                    if pwd_queries < 2 {
                        check(
                            get(&request, 0) == 5
                                && get(&request, 12) as usize == expected_path.len()
                                && &request[16..16 + expected_path.len()] == expected_path
                                && request[16 + expected_path.len()..].iter().all(|b| *b == 0),
                            1594,
                        );
                    } else {
                        check(
                            pwd_queries == 2
                                && (cfg!(cat_cwd_pwd_dev) || cfg!(cat_cwd_pwd_ino))
                                && get(&request, 0) == 4
                                && request[12..].iter().all(|b| *b == 0),
                            1594,
                        );
                    }
                    pwd_queries += 1;
                }
                let mut reply = directory_reply(&request, generation);
                if cfg!(cat_cwd_poison) {
                    check(
                        get(&request, 4) == reference(3, generation)
                            && get(&request, 0) == if cfg!(cat_cwd_reply_mode) { 5 } else { 4 },
                        1593,
                    );
                    directory_poisoned = true;
                    if cfg!(cat_cwd_reply_cut) {
                        send_half(client.writer, &reply);
                        check(ctl(0x24003, client.writer).0 == 0, 1593);
                    } else {
                        if cfg!(cat_cwd_reply_length) {
                            put(&mut reply, 0, 0);
                        } else if cfg!(cat_cwd_reply_mode) {
                            put(&mut reply, 24, 0);
                        } else {
                            reply[4] = 1;
                        }
                        check(transfer(client.writer, &mut reply, true) == 1, 1502);
                    }
                } else {
                    check(transfer(client.writer, &mut reply, true) == 1, 1502);
                }
                request = [0; 32];
                used = 0;
                continue;
            }
            let j = get(&request, 8) as usize;
            check(
                j < 3 && live[j] && get(&request, 4) == reference(j, generation),
                1504,
            );
            let (op, count) = (get(&request, 0), get(&request, 12));
            let mut reply = [0; 32];
            if op == 3 {
                check(count == 0 && request[16..].iter().all(|v| *v == 0), 1504);
                live[j] = false;
                if (cfg!(cat_close_input) && j == 0)
                    || (cfg!(cat_close_output) && j == 1)
                    || ((cfg!(cat_close_diag) || cfg!(toybox_close_diag_close)) && j == 2)
                {
                    check(!injected || (cfg!(toybox_close_diag_close) && j == 2), 1530);
                    injected = true;
                    put(&mut reply, 0, (-5i32) as u32);
                }
            } else {
                check(
                    !injected || (cfg!(toybox_applet) && !uncertain && op == 2 && j == 2),
                    1530,
                );
                check(!cfg!(cat_usage) || (op == 2 && j == 2), 1520);
                check(
                    count <= 16
                        && ((op == 1 && j == 0) || (op == 2 && j > 0))
                        && request[16 + if op == 2 { count as usize } else { 0 }..]
                            .iter()
                            .all(|v| *v == 0),
                    1504,
                );
                let count = if cfg!(cat_short) {
                    count.min(if op == 1 { 7 } else { 3 })
                } else {
                    count
                };
                if cfg!(toybox_close_policy) && op == 2 && j == 2 {
                    check(!live[0] && !live[1], 1550);
                }
                let reject = (cfg!(cat_read_error) && j == 0 && positions[0] == copy_chunk)
                    || (cfg!(cat_write_error) && j == 1 && positions[1] == copy_chunk)
                    || ((cfg!(cat_diag_error) || cfg!(toybox_close_diag_error))
                        && j == 2
                        && positions[2] == 16);
                if reject {
                    injected = true;
                    put(
                        &mut reply,
                        0,
                        (if cfg!(cat_eintr) { -4i32 } else { -5i32 }) as u32,
                    );
                } else {
                    reply = backend(
                        service,
                        if op == 1 { 2 } else { 4 },
                        handles[j],
                        positions[j],
                        count,
                        if op == 2 {
                            &request[16..16 + count as usize]
                        } else {
                            &[]
                        },
                    );
                    let done = get(&reply, 0) as i32;
                    check(done >= 0 && done <= count as i32, 1504);
                    positions[j] += done as u32;
                }
            }
            if cfg!(cat_force_stop) && op == 2 && j == 1 {
                check(!stopped && positions == [11, 11, 0], 1540);
                check(ctl(0x20002, client.child).0 == -16, 1540);
                check(ctl(0x20007, client.child).0 == 0, 1540);
                let terminal = ctl(0x20001, client.child);
                check(terminal.0 == 144 && terminal.2 == 3, 1540);
                check(
                    ctl(0x20007, client.child).0 == 0 && ctl(0x20001, client.child) == terminal,
                    1540,
                );
                stopped = true;
                request = [0; 32];
                used = 0;
                continue;
            }
            let distort = unknown
                && ((cfg!(cat_unknown_read) && op == 1)
                    || (cfg!(cat_unknown_write) && op == 2 && j == 1)
                    || (cfg!(cat_unknown_diag) && op == 2 && j == 2)
                    || (cfg!(cat_unknown_close)
                        && op == 3
                        && j == if cfg!(toybox_unknown_output) {
                            1
                        } else if cfg!(toybox_unknown_diag_close) {
                            2
                        } else {
                            0
                        })
                    || (cfg!(toybox_close_diag_unknown) && op == 2 && j == 2));
            if distort {
                injected = true;
                uncertain = true;
                if cfg!(cat_reply_cut) {
                    // Empty response channel; borrowed stack bytes are copied by the trap.
                    check(
                        call(0x24002, client.writer, reply.as_ptr() as u64, 16, 0, 0, 0).0 == 16,
                        1502,
                    );
                    check(ctl(0x24003, client.writer).0 == 0, 1502);
                } else {
                    reply[4] = 1;
                    check(transfer(client.writer, &mut reply, true) == 1, 1502);
                }
            } else {
                check(transfer(client.writer, &mut reply, true) == 1, 1502);
            }
            request = [0; 32];
            used = 0;
        }
        check(exited, 1501);
        if cfg!(cat_cwd_pwd) {
            check(
                pwd_queries
                    == if cfg!(cat_cwd_pwd_dev) || cfg!(cat_cwd_pwd_ino) {
                        3
                    } else {
                        2
                    },
                1594,
            );
        }
        check(file_poisoned == cfg!(cat_files_poison), 1600);
        check(file_uncertain == cfg!(cat_files_backend), 1601);
        if file_uncertain {
            let connection = files.unwrap();
            if !cfg!(cat_files_backend_skip_stop) {
                check(ctl(0x20007, connection.child).0 == 0, 1601);
            }
            let state = ctl(0x20001, connection.child);
            check(state.0 == 144 && state.2 == 3, 1601);
            file_records.fill(FileRecord::EMPTY);
        } else if cfg!(cat_files_poison) {
            check(
                file_records.iter().filter(|r| r.reference != 0).count()
                    == if cfg!(cat_files_poison_close) { 0 } else { 1 },
                1600,
            );
            if !cfg!(cat_files_poison_skip_cleanup) {
                for record in &mut file_records {
                    if record.reference != 0 {
                        let connection = files.unwrap();
                        check(
                            backend(connection, 3, record.backend, 0, 0, b"") == [0; 32],
                            1599,
                        );
                        let stale = backend(connection, 2, record.backend, 0, 1, b"");
                        check(
                            get(&stale, 0) as i32 == -9 && stale[4..].iter().all(|b| *b == 0),
                            1599,
                        );
                        *record = FileRecord::EMPTY;
                    }
                }
            }
        }
        if cfg!(cat_files) {
            check(
                if invalid {
                    file_sequence == 0 && file_reads == 0
                } else if cfg!(cat_files_backend) {
                    file_sequence
                        == if cfg!(cat_files_poison_read) || cfg!(cat_files_poison_close) {
                            1
                        } else {
                            0
                        }
                        && file_reads == 0
                } else if cfg!(cat_files_poison) {
                    file_sequence == 1
                        && file_reads == if cfg!(cat_files_poison_read) { 1 } else { 0 }
                } else if cfg!(cat_env) && !cfg!(cat_env_load) {
                    file_sequence == 0 && file_reads == 0
                } else if cfg!(cat_files_boundaries) {
                    file_sequence == 6 && file_reads == 9
                } else {
                    file_sequence == 1 && file_reads > 0
                },
                1598,
            );
            check(file_records.iter().all(|r| r.reference == 0), 1599);
        }
        check(directory_poisoned == cfg!(cat_cwd_poison), 1593);
        check(stopped == cfg!(cat_force_stop), 1540);
        check(injected == (io_error || close_error || unknown), 1531);
        let diagnostic: &[u8] =
            if cfg!(toybox_close_policy) && (cfg!(cat_close_input) || cfg!(cat_close_output)) {
                if cfg!(toybox_close_diag_error) || cfg!(toybox_close_diag_unknown) {
                    &b"cat: close failed\n"[..16]
                } else {
                    b"cat: close failed\n"
                }
            } else if cfg!(toybox_applet) && io_error && !unknown {
                if cfg!(toybox_wrong_diagnostic) {
                    b"wrong\n"
                } else if cfg!(toybox_final_status) {
                    b""
                } else if cfg!(toybox_finalizer) {
                    if cfg!(cat_eintr) {
                        b"cat: write: Interrupted system call\n"
                    } else {
                        b"cat: write: I/O error\n"
                    }
                } else if cfg!(cat_read_error) {
                    if cfg!(cat_eintr) {
                        b"cat: -: Interrupted system call\n"
                    } else {
                        b"cat: -: I/O error\n"
                    }
                } else if cfg!(cat_eintr) {
                    b"cat: xwrite: Interrupted system call\n"
                } else {
                    b"cat: xwrite: I/O error\n"
                }
            } else if cfg!(cat_usage) && !invalid {
                let text = include_bytes!("cat-usage.txt");
                if cfg!(cat_diag_error) || cfg!(cat_unknown_diag) || cfg!(cat_fault_diag) {
                    &text[..16]
                } else {
                    text
                }
            } else if cfg!(cat_dash_init) && !cfg!(cat_cwd) && !invalid {
                b"sh: 0: getcwd() failed: Function not implemented\n"
            } else if cfg!(cat_syntax) {
                b"sh: 1: Syntax error: \"then\" unexpected\n"
            } else if cfg!(cat_privileged) {
                b"sh: 0: Illegal option -p\n"
            } else if cfg!(cat_diagnostic) && !invalid {
                b"D\n"
            } else {
                b""
            };
        let copied = if cfg!(cat_privileged) || cfg!(cat_syntax) {
            &b""[..]
        } else if cfg!(cat_env) {
            if cfg!(cat_env_load) {
                &b"hello\ndash-main\n"[..]
            } else {
                &b"dash-main\n"[..]
            }
        } else if cfg!(cat_files_boundaries) || cfg!(cat_files_poison) {
            &b""[..]
        } else if cfg!(cat_files) {
            &b"hello\n"[..]
        } else if cfg!(cat_dash_main) {
            &b"dash-main\n"[..]
        } else if cfg!(cat_cwd_poison)
            || cfg!(cat_guard_close)
            || cfg!(cat_unknown_read)
            || cfg!(cat_fault_before)
        {
            &input[..0]
        } else if cfg!(cat_read_error)
            || cfg!(cat_write_error)
            || cfg!(cat_unknown_write)
            || cfg!(cat_fault_copy)
            || cfg!(cat_force_stop)
        {
            &input[..copy_chunk as usize]
        } else {
            input
        };
        let read_len = if cfg!(cat_cwd_poison) || cfg!(cat_guard_close) {
            0
        } else if cfg!(toybox_finalizer) {
            input.len()
        } else if cfg!(cat_fault_before) {
            0
        } else if cfg!(cat_fault_copy) || cfg!(cat_force_stop) {
            copy_chunk as usize
        } else if cfg!(cat_read_error) || cfg!(cat_unknown_read) || cfg!(cat_unknown_write) {
            copy_chunk as usize
        } else if cfg!(cat_write_error) {
            (copy_chunk * 2) as usize
        } else {
            input.len()
        };
        check(
            positions
                == if invalid {
                    [0; 3]
                } else {
                    [
                        if cfg!(cat_usage) { 0 } else { read_len as u32 },
                        if cfg!(cat_usage) {
                            0
                        } else {
                            copied.len() as u32
                        },
                        diagnostic.len() as u32,
                    ]
                },
            1505,
        );
        for j in 0..3 {
            let expected: &[u8] = if j == 0 {
                input
            } else if j == 1 && !invalid && !cfg!(cat_usage) {
                copied
            } else if j == 2 {
                diagnostic
            } else {
                b""
            };
            let mut at = 0;
            while at < expected.len() {
                let b = backend(service, 2, handles[j], at as u32, 16, &[]);
                let n = (expected.len() - at).min(16);
                check(
                    get(&b, 0) as usize == n && &b[16..16 + n] == &expected[at..at + n],
                    1505,
                );
                at += n;
            }
            check(
                get(&backend(service, 2, handles[j], at as u32, 1, &[]), 0) == 0,
                1505,
            );
            if !cfg!(cat_skip_backend_close) || j != 2 {
                check(
                    get(&backend(service, 3, handles[j], 0, 0, &[]), 0) == 0,
                    1506,
                );
            }
            check(
                get(&backend(service, 2, handles[j], 0, 1, &[]), 0) as i32 == -9,
                1506,
            );
        }
        check(
            ctl(0x24003, client.reader).0 == 0
                && ctl(0x24003, client.writer).0
                    == if file_uncertain
                        || cfg!(cat_files_poison_cut)
                        || cfg!(cat_reply_cut)
                        || cfg!(cat_cwd_reply_cut)
                        || cfg!(cat_cwd_cut)
                        || cfg!(cat_identity_cut)
                        || cfg!(cat_identity_short)
                        || cfg!(cat_identity_version)
                        || cfg!(cat_identity_legacy)
                        || cfg!(cat_cwd_short)
                        || cfg!(cat_cwd_version)
                        || cfg!(cat_cwd_legacy)
                    {
                        -13
                    } else {
                        0
                    }
                && ctl(0x20002, client.child).0 == 0,
            1506,
        );
        if let Some(files) = files {
            if !cfg!(cat_files) {
                file_service_probe(files, 2);
            }
        }
        peer_record();
        if abnormal || cfg!(cat_signal) {
            check(
                ctl(0x20001, client.child).0 == -9
                    && ctl(0x20007, client.child).0 == -9
                    && ctl(0x20002, client.child).0 == -9,
                1541,
            );
        }
        check(
            ctl(0x24003, service.writer).0 == 0
                && terminal(service.child) == (17, 1)
                && ctl(0x24003, service.reader).0 == 0
                && ctl(0x20002, service.child).0 == 0,
            1506,
        );
        if let Some(files) = files {
            check(
                ctl(0x24003, files.writer).0 == if cfg!(cat_files_backend_late) { -13 } else { 0 }
                    && terminal(files.child) == if file_uncertain { (143, 3) } else { (17, 1) }
                    && ctl(0x24003, files.reader).0 == 0
                    && ctl(0x20002, files.child).0 == 0,
                1597,
            );
        }
    }
    end(100)
}

// The caller receives only from the current client's delegated endpoint. This
// immutable fixture namespace is local to that connection, not a global path map.
fn directory_reply(request: &[u8; 32], generation: u32) -> [u8; 32] {
    let mut reply = [0; 32];
    let reference_value = get(request, 4);
    let op = get(request, 0);
    let length = get(request, 12) as usize;
    let error = if get(request, 8) != 3 {
        22
    } else if reference_value == reference(3, generation - 1) {
        9
    } else if reference_value != reference(3, generation) {
        13
    } else if op == 4 {
        if length != 0 || request[16..].iter().any(|b| *b != 0) {
            22
        } else {
            put(&mut reply, 0, 6);
            reply[16..22].copy_from_slice(b"/work\0");
            0
        }
    } else if op == 5 {
        if length > 15 {
            36
        } else if length == 0 {
            2
        } else if request[16..16 + length].contains(&0)
            || request[16 + length..].iter().any(|b| *b != 0)
        {
            22
        } else {
            let path = &request[16..16 + length];
            if path == b"." || path == b"/work" {
                put(&mut reply, 16, 100 + generation);
                put(&mut reply, 20, 1);
                if path == b"/work" {
                    if cfg!(cat_cwd_pwd_dev) {
                        put(&mut reply, 16, 200 + generation);
                    }
                    if cfg!(cat_cwd_pwd_ino) {
                        put(&mut reply, 20, 2);
                    }
                }
                put(&mut reply, 24, 0o40500);
                0
            } else if path == b".." || path.starts_with(b"../") || path.starts_with(b"/") {
                13
            } else if path.contains(&b'/') {
                22
            } else {
                2
            }
        }
    } else {
        38
    };
    if error != 0 {
        put(&mut reply, 0, (-error as i32) as u32);
    }
    reply
}

// A post-timeout fixture witness only: leave the reply body unread and poisoned.
#[inline(never)]
fn late_reply_witness(connection: Connection) {
    check(ctl(0x24003, connection.writer).0 == 0, 1602);
    let mut byte = [0xffu8; 1];
    check(
        transfer_bounded(connection.reader, &mut byte, false, 4096) == 1 && byte[0] == 0,
        1602,
    );
}

// Deliberate truncated fixture frame; the syscall copies these borrowed bytes.
fn send_half(writer: u64, b: &[u8; 32]) {
    send_prefix(writer, b, 16);
}
fn send_bootstrap(writer: u64, b: &mut [u8; 32], remaining: &mut usize) {
    let count = (*remaining).min(32);
    if count == 32 {
        check(transfer(writer, b, true) == 1, 1500);
    } else if count > 0 {
        send_prefix(writer, b, count);
    }
    *remaining -= count;
}
fn send_prefix(writer: u64, b: &[u8; 32], count: usize) {
    check(count > 0 && count <= b.len(), 1500);
    let mut sent = 0usize;
    for _ in 0..100000 {
        let r = call(
            0x24002,
            writer,
            b[sent..].as_ptr() as u64,
            (count - sent) as u64,
            0,
            0,
            0,
        )
        .0;
        if r == -11 {
            ctl(0x1fffe, 0);
            continue;
        }
        check(r > 0 && r as usize <= count - sent, 1500);
        sent += r as usize;
        if sent == count {
            break;
        }
    }
    check(sent == count, 1500);
}

// Existing file-service connection only: a stream handle is not a file root.
fn file_service_probe(files: Connection, generation: u32) {
    for (root, rights, name, error) in [
        (0xf101, 1, &b"hello.sh"[..], -13i32),
        (0xf001, 3, &b"hello.sh"[..], -13),
        (0xf001, 1, &b"missing"[..], -2),
    ] {
        let reply = backend(files, 1, root, 0, rights, name);
        check(
            get(&reply, 0) as i32 == error && reply[4..].iter().all(|b| *b == 0),
            1596,
        );
    }
    let content = b"printf 'hello\\n'\n";
    let handle = 0xf1000001 | (generation << 8);
    if generation > 1 {
        check(
            get(&backend(files, 2, handle - 256, 0, 1, &[]), 0) as i32 == -9,
            1597,
        );
    }
    let opened = backend(files, 1, 0xf001, 0, 1, b"hello.sh");
    check(
        get(&opened, 0) == 0
            && get(&opened, 4) == handle
            && get(&opened, 8) as usize == content.len()
            && opened[12..].iter().all(|b| *b == 0),
        1596,
    );
    let mut offset = 0;
    while offset < content.len() {
        let reply = backend(files, 2, handle, offset as u32, 16, &[]);
        let count = (content.len() - offset).min(16);
        check(
            get(&reply, 0) as usize == count
                && reply[4..16].iter().all(|b| *b == 0)
                && reply[16..16 + count] == content[offset..offset + count]
                && reply[16 + count..].iter().all(|b| *b == 0),
            1596,
        );
        offset += count;
    }
    check(
        backend(files, 2, handle, offset as u32, 1, &[]) == [0; 32],
        1596,
    );
    check(
        get(&backend(files, 4, handle, 0, 0, &[]), 0) as i32 == -13,
        1596,
    );
    if !cfg!(cat_file_skip_close) {
        check(backend(files, 3, handle, 0, 0, &[]) == [0; 32], 1597);
    }
    check(
        get(&backend(files, 2, handle, 0, 1, &[]), 0) as i32 == -9,
        1597,
    );
}

// Connection-local file descriptions. References never escape to another client.
#[derive(Clone, Copy)]
struct FileRecord {
    reference: u32,
    backend: u32,
    offset: u32,
    size: u32,
}
impl FileRecord {
    const EMPTY: Self = Self {
        reference: 0,
        backend: 0,
        offset: 0,
        size: 0,
    };
}
fn file_reply(
    files: Connection,
    request: &[u8; 32],
    generation: u32,
    records: &mut [FileRecord; 2],
    sequence: &mut u32,
    reads: &mut u32,
    reply: &mut [u8; 32],
) -> bool {
    let op = get(request, 0);
    let token = get(request, 4);
    let selector = get(request, 8);
    let count = get(request, 12);
    let mut error = -22i32;
    if op == 6 {
        if token != reference(4, generation) || count != 1 {
            error = -13;
        } else if selector == 4 {
            if let Some(end) = request[16..].iter().position(|b| *b == 0) {
                let name = &request[16..16 + end];
                if !name.is_empty()
                    && name != b"."
                    && name != b".."
                    && !name.contains(&b'/')
                    && request[16 + end..].iter().all(|b| *b == 0)
                {
                    error = -24;
                    if *sequence < 6 {
                        if let Some(slot) = records.iter().position(|r| r.reference == 0) {
                            if !backend_exchange(files, 1, 0xf001, 0, 1, name, reply) {
                                return false;
                            }
                            let result = get(reply, 0) as i32;
                            if result < 0 {
                                if !(matches!(result, -2 | -24)
                                    && reply[4..].iter().all(|b| *b == 0))
                                {
                                    return false;
                                }
                                error = result;
                            } else {
                                let handle = get(reply, 4);
                                if !(result == 0
                                    && (handle & !0x303) == 0xf1000000
                                    && (1..=2).contains(&(handle & 3))
                                    && (1..=3).contains(&((handle >> 8) & 3))
                                    && reply[12..].iter().all(|b| *b == 0)
                                    && records
                                        .iter()
                                        .all(|r| r.reference == 0 || r.backend != handle)
                                    && (1..=255).contains(&generation))
                                {
                                    return false;
                                }
                                *sequence += 1;
                                let issued = 0x77000000
                                    | (generation << 16)
                                    | (*sequence << 8)
                                    | (slot as u32 + 1);
                                records[slot] = FileRecord {
                                    reference: issued,
                                    backend: handle,
                                    offset: 0,
                                    size: get(reply, 8),
                                };
                                put(reply, 4, issued);
                                put(reply, 8, slot as u32 + 3);
                                return true;
                            }
                        }
                    }
                }
            }
        }
    } else {
        error = -9;
        if let Some(slot) = (0..2).find(|s| {
            selector == *s as u32 + 3
                && records[*s].reference != 0
                && (records[*s].reference == token || cfg!(cat_files_ignore_reference))
        }) {
            error = -22;
            if request[16..].iter().all(|b| *b == 0)
                && ((op == 7 && count <= 16) || (op == 8 && count == 0))
            {
                let record = records[slot];
                if op == 7 {
                    if !backend_exchange(files, 2, record.backend, record.offset, count, b"", reply)
                    {
                        return false;
                    }
                    let n = get(reply, 0);
                    if !(n <= count
                        && n <= record.size.saturating_sub(record.offset)
                        && reply[4..16].iter().all(|b| *b == 0)
                        && reply[16 + n as usize..].iter().all(|b| *b == 0))
                    {
                        return false;
                    }
                    if !cfg!(cat_files_skip_offset) {
                        records[slot].offset += n;
                    }
                    *reads += 1;
                    return true;
                }
                if !cfg!(cat_files_skip_close) {
                    if !backend_exchange(files, 3, record.backend, 0, 0, b"", reply)
                        || *reply != [0; 32]
                    {
                        return false;
                    }
                    records[slot] = FileRecord::EMPTY;
                }
                return true;
            }
        }
    }
    put(reply, 0, error as u32);
    true
}
