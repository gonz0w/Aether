// SPDX-License-Identifier: BSD-2-Clause
// Bounded AERIO001 admission witness; policy remains in this user-space owner.
use super::*;
fn carrier(parent: Connection, generation: u32) {
    let mut b = [0; 32];
    b[..8].copy_from_slice(if cfg!(init_sustained_v2) {
        b"AERIO002"
    } else {
        b"AERIO001"
    });
    put(&mut b, 8, 4);
    put(&mut b, 12, generation);
    check(transfer(parent.writer, &mut b, true) == 1, 1400);
    for j in 0..4 {
        b = [0; 32];
        for (k, v) in [
            j as u32 + 1,
            parent_ref(j, generation),
            j as u32 + 1,
            [2, 2, 1, 3][j],
            [512, 256, 6, 64][j],
        ]
        .iter()
        .enumerate()
        {
            put(&mut b, k * 4, *v);
        }
        check(transfer(parent.writer, &mut b, true) == 1, 1400);
    }
}
fn receipt(generation: u32) -> u32 {
    (if cfg!(init_sustained_v2) {
        0x7b000000
    } else {
        0x73000000
    }) | generation
}
fn parent_ref(j: usize, generation: u32) -> u32 {
    if j < 2 {
        0x75000000 + ((j as u32 + 1) << 16) + generation
    } else {
        reference(0, j - 2, generation)
    }
}
#[cfg(init_sustained)]
#[path = "sustained.rs"]
mod sustained;
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    #[cfg(init_sustained)]
    sustained::begin();
    for generation in 1..=if cfg!(init_sustained) { 5 } else { 2 } {
        #[cfg(all(init_sustained_v2, init_sustained_exhausted))]
        let generation = 65536;
        #[cfg(init_sustained_v2)]
        if !(1..=65535).contains(&generation) {
            sustained::write(b"SI07 epoch exhausted before admission\n");
            end(2806);
        }
        let service = launch(factory, second, 1);
        #[cfg(init_sustained_v2)]
        sustained::cohort(
            &[(service, 1)],
            if cfg!(init_sustained_bad_cohort) {
                generation + 65536
            } else {
                generation
            },
        );
        let mut hello = [0; 32];
        check(transfer(service.reader, &mut hello, false) == 1, 1400);
        let handles = [0xf201, 0xf202, 0xf101, 0xf203];
        check(
            (0..4).all(|j| get(&hello, 4 + j * 4) == [0xf101, 0xf201, 0xf202, 0xf203][j]),
            1400,
        );
        #[cfg(init_sustained)]
        sustained::input(b"SI07 command-ready\n", b'r');
        let parent = launch(factory, first, 0);
        #[cfg(init_sustained_v2)]
        sustained::cohort(&[(service, 1), (parent, 0)], generation);
        #[cfg(runner_startup)]
        for chunk in startup_record().chunks_exact(32) {
            let mut bytes: [u8; 32] = chunk.try_into().unwrap();
            check(transfer(parent.writer, &mut bytes, true) == 1, 1400);
        }
        carrier(parent, generation);
        let mut clients = [parent, parent];
        let mut admitted = false;
        let mut started = false;
        let mut terminal_result = (0u32, 0u32);
        let mut collected = false;
        let mut recollected = false;
        let mut parent_eof = false;
        let mut exited = [false; 2];
        let mut live = [[true; 4], [false; 4]];
        let mut positions = [0u32; 4];
        let mut frames = [[0u8; 384]; 2];
        let mut used = [0usize; 2];
        for _ in 0..200000 {
            for i in 0..2 {
                if exited[i] || (i == 1 && !started) {
                    continue;
                }
                let state = ctl(0x20001, clients[i].child);
                check(state.0 >= 0, 1401);
                if state.0 > 0 {
                    let actual = ((state.0 - 1) as u32, state.2 as u32);
                    if i == 0 {
                        let mapped = if terminal_result.1 == 1 && terminal_result.0 <= 255 {
                            terminal_result.0
                        } else {
                            1
                        };
                        check(actual == (mapped, 1), 1401);
                    } else {
                        let expected = if cfg!(success_fault) {
                            (134, 2)
                        } else if cfg!(success_nonzero) {
                            (134, 1)
                        } else if cfg!(success_wide) {
                            (64, 1)
                        } else {
                            (0, 1)
                        };
                        check(actual == expected, 1407);
                        terminal_result = actual;
                    }
                    if i == 0 {
                        check(
                            admitted && collected && recollected && parent_eof && exited[1],
                            1401,
                        );
                    }
                    let mut pending = [0u8; 1];
                    check(
                        used[i] == 0
                            && call(
                                0x24001,
                                clients[i].reader,
                                pending.as_mut_ptr() as u64,
                                1,
                                0,
                                0,
                                0,
                            )
                            .0 == 0,
                        1402,
                    );
                    if i == 1
                        && (cfg!(success_fault) || cfg!(success_nonzero) || cfg!(success_wide))
                    {
                        check(live[i] == [false, false, true, true], 1403);
                        if !cfg!(success_skip_retire) {
                            live[i] = [false; 4];
                        }
                    }
                    check(live[i] == [false; 4], 1403);
                    exited[i] = true;
                    continue;
                }
                let need = if used[i] >= 4 && word(&frames[i], 0) == 4 {
                    384
                } else {
                    32
                };
                let n = call(
                    0x24001,
                    clients[i].reader,
                    frames[i][used[i]..].as_mut_ptr() as u64,
                    (need - used[i]).min(16) as u64,
                    0,
                    0,
                    0,
                )
                .0;
                if n == -11 {
                    continue;
                }
                check(n > 0 && n as usize <= need - used[i], 1402);
                used[i] += n as usize;
                if used[i] < if word(&frames[i], 0) == 4 { 384 } else { 32 } {
                    continue;
                }
                let request = frames[i];
                frames[i] = [0; 384];
                used[i] = 0;
                let op = word(&request, 0);
                let mut reply = [0; 32];
                let result: i32;
                if op == 4 {
                    check(i == 0 && !admitted && live[0] == [true; 4], 1404);
                    let mut args = validate(&request, generation, [live[0][2], live[0][3]])
                        .unwrap_or_else(|_| end(1404));
                    if cfg!(success_helper_bad_arg) {
                        args.strings[2][0] = b'X';
                    }
                    if cfg!(success_helper_bad_env) {
                        args.strings[5][8] = b'X';
                    }
                    clients[1] = admit(factory, third, &args, false).unwrap_or_else(|_| end(1404));
                    #[cfg(init_sustained_v2)]
                    sustained::cohort(&[(service, 1), (parent, 0), (clients[1], 2)], generation);
                    live[1] = [false, false, true, true];
                    admitted = true;
                    result = 0;
                    put(&mut reply, 4, receipt(generation));
                } else if op == 5 {
                    check(
                        i == 0
                            && admitted
                            && word(&request, 4) == receipt(generation)
                            && request[8..32].iter().all(|v| *v == 0),
                        1404,
                    );
                    if collected {
                        recollected = true;
                        result = -10;
                    } else if !exited[1] {
                        result = -11;
                    } else {
                        collected = true;
                        result = 0;
                        put(&mut reply, 4, receipt(generation));
                        put(&mut reply, 8, terminal_result.0);
                        put(&mut reply, 12, terminal_result.1);
                    }
                } else {
                    let j = (0..4).find(|j| {
                        live[i][*j]
                            && word(&request, 4)
                                == if i == 0 {
                                    parent_ref(*j, generation)
                                } else {
                                    reference(1, *j - 2, generation)
                                }
                            && word(&request, 8)
                                == if i == 0 { *j as u32 + 1 } else { *j as u32 - 2 }
                    });
                    if let Some(j) = j {
                        let count = word(&request, 12);
                        if op == 3 && count == 0 && request[16..32].iter().all(|v| *v == 0) {
                            live[i][j] = false;
                            result = 0;
                            if i == 0 && j == 2 {
                                check(admitted && !started && live[1][2], 1404);
                                bootstrap(clients[1], 1, generation);
                                started = true;
                            }
                        } else if count <= 16
                            && request[16 + if op == 2 { count as usize } else { 0 }..32]
                                .iter()
                                .all(|v| *v == 0)
                            && ((op == 1 && (j == 2 || (j == 3 && i == 0 && collected)))
                                || (op == 2 && j == 3 && i == 1))
                        {
                            let count = if cfg!(success_short) && op == 2 {
                                count.min(1)
                            } else {
                                count
                            };
                            if cfg!(success_skip_write) && op == 2 {
                                result = count as i32;
                            } else {
                                let handle = if cfg!(success_wrong_sink) && op == 2 {
                                    handles[0]
                                } else {
                                    handles[j]
                                };
                                reply = backend(
                                    service,
                                    if op == 1 { 2 } else { 4 },
                                    handle,
                                    positions[j],
                                    count,
                                    if op == 2 {
                                        &request[16..16 + count as usize]
                                    } else {
                                        &[]
                                    },
                                );
                                result = get(&reply, 0) as i32;
                            }
                            check(result >= 0 && result <= count as i32, 1405);
                            positions[j] += result as u32;
                            if i == 0 && j == 3 {
                                check(result == 0, 1405);
                                parent_eof = true;
                            }
                        } else {
                            result = -13;
                        }
                    } else {
                        result = -9;
                    }
                }
                put(&mut reply, 0, result as u32);
                check(transfer(clients[i].writer, &mut reply, true) == 1, 1402);
            }
            if exited == [true; 2] {
                break;
            }
            ctl(0x1fffe, 0);
        }
        check(
            exited == [true; 2]
                && positions
                    == [
                        0,
                        0,
                        if cfg!(success_helper_argv)
                            || cfg!(init_command_empty)
                            || cfg!(init_command_fault)
                        {
                            0
                        } else {
                            6
                        },
                        if cfg!(success_helper_argv) {
                            8
                        } else if cfg!(init_command_fault) {
                            0
                        } else {
                            2
                        },
                    ],
            1405,
        );
        for j in 0..4 {
            let expected: &[u8] = match j {
                2 => {
                    if cfg!(init_command_empty) {
                        b""
                    } else {
                        b"abcdef"
                    }
                }
                3 => {
                    if cfg!(success_helper_argv) {
                        b"argv ok\n"
                    } else if cfg!(init_command_fault) {
                        b""
                    } else if cfg!(init_command_empty) {
                        b"0\n"
                    } else {
                        b"6\n"
                    }
                }
                _ => b"",
            };
            let b = backend(service, 2, handles[j], 0, 16, &[]);
            check(
                get(&b, 0) as usize == expected.len() && &b[16..16 + expected.len()] == expected,
                1405,
            );
            check(
                get(
                    &backend(service, 2, handles[j], expected.len() as u32, 1, &[]),
                    0,
                ) == 0,
                1405,
            );
            check(
                get(&backend(service, 3, handles[j], 0, 0, &[]), 0) == 0,
                1406,
            );
            check(
                get(&backend(service, 2, handles[j], 0, 1, &[]), 0) as i32 == -9,
                1406,
            );
        }
        for c in clients {
            check(
                ctl(0x24003, c.reader).0 == 0
                    && ctl(0x24003, c.writer).0 == 0
                    && ctl(0x20002, c.child).0 == 0,
                1406,
            );
        }
        check(
            ctl(0x24003, service.writer).0 == 0
                && terminal(service.child) == (17, 1)
                && ctl(0x24003, service.reader).0 == 0
                && ctl(0x20002, service.child).0 == 0,
            1406,
        );
        #[cfg(init_sustained)]
        {
            for c in clients {
                check(
                    ctl(0x20001, c.child).0 == -9 && ctl(0x24003, c.reader).0 == -13,
                    2805,
                );
            }
            sustained::write(b"SI07 command-complete\n");
        }
    }
    #[cfg(init_sustained)]
    sustained::halt();
    #[cfg(not(init_sustained))]
    end(100)
}
