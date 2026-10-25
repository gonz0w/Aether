// SPDX-License-Identifier: BSD-2-Clause
// Local command integration candidate. All file/process policy stays in user space.
use super::*;
// Callers supply zeroed storage; partial replies never count as completed exchanges.
#[inline(never)]
fn backend_exchange(
    c: Connection,
    op: u32,
    h: u32,
    pos: u32,
    n: u32,
    data: &[u8],
    b: &mut [u8; 32],
) -> bool {
    for (i, v) in [op, h, pos, n].iter().enumerate() {
        put(b, i * 4, *v);
    }
    b[16..16 + data.len()].copy_from_slice(data);
    // Command backends use a smaller real polling budget than generic transport.
    transfer_bounded(c.writer, b, true, 4096) == 1
        && transfer_bounded(c.reader, b, false, 4096) == 1
}
#[inline(never)]
fn backend(c: Connection, op: u32, h: u32, pos: u32, n: u32, data: &[u8]) -> [u8; 32] {
    let mut reply = [0; 32];
    check(backend_exchange(c, op, h, pos, n, data, &mut reply), 952);
    reply
}
fn reference(i: usize, j: usize, generation: u32) -> u32 {
    0x71000000 + ((i as u32) << 24) + ((j as u32) << 16) + generation
}
fn bootstrap(c: Connection, i: usize, generation: u32) {
    let mut b = [0; 32];
    for j in 0..2 {
        put(&mut b, 4 + j * 12, reference(i, j, generation));
        put(
            &mut b,
            8 + j * 12,
            if i == 0 { 3 + j as u32 } else { j as u32 },
        );
        put(
            &mut b,
            12 + j * 12,
            if j == 0 {
                1
            } else if i == 0 {
                3
            } else {
                2
            },
        );
    }
    #[cfg(init_sustained_v2)]
    put(&mut b, 28, 0x324f494e);
    check(transfer(c.writer, &mut b, true) == 1, 990);
}
fn admit(factory: u64, image: u64, a: &Args, reject: bool) -> Result<Connection, i32> {
    let req = ctl(0x24000, 0xd001);
    if req.0 < 0 {
        return Err(req.0 as i32);
    }
    let rep = ctl(0x24000, 0xd001);
    if rep.0 < 0 {
        check(
            ctl(0x24003, req.0 as u64).0 == 0 && ctl(0x24003, req.1).0 == 0,
            980,
        );
        return Err(rep.0 as i32);
    }
    let invalid = Args {
        argc: 5,
        envc: 0,
        strings: [[0; 32]; 8],
    };
    let h = call(
        0x23002,
        factory,
        image,
        2,
        if reject { &invalid } else { a } as *const Args as u64,
        req.0 as u64,
        rep.1,
    )
    .0;
    if h < 0 {
        for cap in [req.0 as u64, req.1, rep.0 as u64, rep.1] {
            check(ctl(0x24003, cap).0 == 0, 980);
        }
        return Err(h as i32);
    }
    check(
        ctl(0x24003, req.0 as u64).0 == -13 && ctl(0x24003, rep.1).0 == -13,
        980,
    );
    Ok(Connection {
        reader: rep.0 as u64,
        writer: req.1,
        child: h as u64,
    })
}
fn word(b: &[u8], o: usize) -> u32 {
    u32::from_le_bytes(b[o..o + 4].try_into().unwrap())
}
fn validate(b: &[u8; 384], generation: u32, live: [bool; 2]) -> Result<Args, i32> {
    if (word(b, 4) != 1 && !cfg!(allow_launch_version))
        || word(b, 16) != 2
        || b[20..32].iter().any(|v| *v != 0)
    {
        return Err(-22);
    }
    let name: &[u8] = if cfg!(success_helper_argv) {
        b"/inputs/helper"
    } else {
        b"bytecount"
    };
    if &b[32..32 + name.len()] != name || b[32 + name.len()..64].iter().any(|v| *v != 0) {
        return Err(-2);
    }
    for j in 0..2 {
        let o = 64 + j * 32;
        if !live[j] || word(b, o) != reference(0, j, generation) || word(b, o + 4) != 3 + j as u32 {
            return Err(-9);
        }
        if word(b, o + 8) != j as u32 || b[o + 16..o + 32].iter().any(|v| *v != 0) {
            return Err(-22);
        }
        if word(b, o + 12) != if j == 0 { 1 } else { 2 } {
            return Err(-13);
        }
    }
    let argc = word(b, 8);
    let envc = word(b, 12);
    if !(1..=4).contains(&argc)
        || envc > if cfg!(success_helper_argv) { 2 } else { 1 }
        || (cfg!(success_helper_argv) && (argc != 4 || envc != 2))
    {
        return Err(-22);
    }
    let mut a = Args {
        argc: argc as u64,
        envc: envc as u64,
        strings: [[0; 32]; 8],
    };
    for j in 0..8 {
        let bytes = &b[128 + j * 32..160 + j * 32];
        if j < (argc + envc) as usize {
            let end = bytes.iter().position(|v| *v == 0).ok_or(-22)?;
            if bytes[end..].iter().any(|v| *v != 0) {
                return Err(-22);
            }
            if j >= argc as usize
                && &bytes[..end]
                    != if cfg!(success_helper_argv) && j == argc as usize + 1 {
                        &b"WITNESS=value"[..]
                    } else {
                        &b"LC_ALL=C"[..]
                    }
            {
                return Err(-22);
            }
            a.strings[if j < argc as usize {
                j
            } else {
                4 + j - argc as usize
            }]
            .copy_from_slice(bytes);
        } else if bytes.iter().any(|v| *v != 0) {
            return Err(-22);
        }
    }
    Ok(a)
}
fn release(
    c: Connection,
    handles: [u32; 2],
    live: &mut [[bool; 2]; 2],
    i: usize,
    j: usize,
    input_len: u32,
) {
    live[i][j] = false;
    if !live[0][j] && !live[1][j] {
        let b = backend(c, 2, handles[j], 0, 16, &[]);
        if j == 0 {
            check(
                get(&b, 0) == input_len
                    && &b[16..16 + input_len as usize] == &b"abcdef"[..input_len as usize],
                985,
            );
        } else if cfg!(full_output) {
            for offset in (0..64).step_by(16) {
                let b = backend(c, 2, handles[j], offset, 16, &[]);
                check(get(&b, 0) == 16 && b[16..] == [b'!'; 16], 985);
            }
        } else {
            check(
                get(&b, 0) == 2
                    && b[16] == if input_len == 0 { b'0' } else { b'6' }
                    && b[17] == b'\n',
                985,
            );
        }
        check(get(&backend(c, 3, handles[j], 0, 0, &[]), 0) == 0, 973);
        check(
            get(&backend(c, 2, handles[j], 0, 1, &[]), 0) as i32 == -9,
            975,
        );
    }
}
#[cfg(runner_startup)]
fn startup_record() -> &'static [u8; 224] {
    let b: &[u8; 224] = include_bytes!(env!("AETHER_RUNNER_STARTUP"));
    let count = word(b, 8) as usize;
    check(&b[..8] == b"AERUN001" && (1..=6).contains(&count), 994);
    check(b[12..32].iter().all(|v| *v == 0), 994);
    for j in 0..6 {
        let slot = &b[32 + j * 32..64 + j * 32];
        if j < count {
            let end = slot.iter().position(|v| *v == 0);
            check(end.is_some(), 994);
            check(slot[end.unwrap()..].iter().all(|v| *v == 0), 994);
            if j == 0 {
                check(&slot[..end.unwrap()] == b"aether-run", 994);
            }
        } else {
            check(slot.iter().all(|v| *v == 0), 994);
        }
    }
    b
}
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    if cfg!(cat_roles) {
        cat_roles::run(factory, first, second, third);
    }
    if cfg!(runner_success) {
        success::run(factory, first, second, third);
    }
    if cfg!(runner_streams) {
        streams::run(factory, first, second, third);
    }
    if cfg!(runner_local_empty) {
        local_empty::run(factory, first, second);
    }
    #[cfg(runner_startup)]
    let startup = startup_record();
    for generation in 1..=2 {
        let service = launch(factory, second, 1);
        let mut hello = [0; 32];
        check(
            transfer(service.reader, &mut hello, false) == 1 && get(&hello, 8) == 0xf002,
            953,
        );
        let a = backend(service, 1, 0xf001, 0, 1, b"hello.sh");
        check(get(&a, 0) == 0, 953);
        let input = get(&a, 4);
        let input_len = get(&a, 8);
        check(input_len == 0 || input_len == 6, 953);
        let b = backend(service, 5, 0xf002, 0, 3, b"output");
        check(get(&b, 0) == 0, 953);
        let handles = [input, get(&b, 4)];
        let parent = launch(factory, first, 0);
        #[cfg(runner_startup)]
        for chunk in startup.chunks_exact(32) {
            let mut bytes: [u8; 32] = chunk.try_into().unwrap();
            check(transfer(parent.writer, &mut bytes, true) == 1, 990);
        }
        bootstrap(parent, 0, generation);
        let mut clients = [parent, parent];
        let mut admitted = false;
        let mut rejected = false;
        let mut live = [[true, true], [false, false]];
        let mut exited = [false, false];
        let mut positions = [0u32; 2];
        if cfg!(full_output) {
            for offset in (0..64).step_by(16) {
                check(
                    get(&backend(service, 4, handles[1], offset, 16, &[b'!'; 16]), 0) == 16,
                    953,
                );
            }
            positions[1] = 64;
        }
        let mut terminal_result = (0u32, 0u32);
        let mut collected = false;
        let mut exit_window_forced = false;
        let mut frames = [[0u8; 384]; 2];
        let mut used = [0usize; 2];
        for _ in 0..200000 {
            for i in 0..2 {
                if (i == 1 && !admitted) || exited[i] {
                    continue;
                }
                let state = ctl(0x20001, clients[i].child);
                check(state.0 >= 0, 970);
                let force_exit_window = cfg!(exit_poll_window) && i == 1 && !exit_window_forced;
                if state.0 > 0 && !force_exit_window {
                    let actual = ((state.0 - 1) as u32, state.2 as u32);
                    if i == 0 {
                        if cfg!(mapped_results) {
                            let mapped = if terminal_result.1 == 1 && terminal_result.0 <= 255 {
                                terminal_result.0
                            } else {
                                1
                            };
                            check(
                                admitted && collected && exited[1] && actual == (mapped, 1),
                                970,
                            );
                        } else {
                            check(actual == (29, 1), 970);
                        }
                    } else {
                        terminal_result = actual;
                    }
                    for j in 0..2 {
                        if live[i][j] {
                            release(service, handles, &mut live, i, j, input_len);
                        }
                    }
                    exited[i] = true;
                    continue;
                }
                if force_exit_window {
                    // Model one stale running poll even if exit won this schedule.
                    // The subsequent read must see EOF backed by a real terminal.
                    exit_window_forced = true;
                    let mut terminal = false;
                    for _ in 0..200000 {
                        let observed = ctl(0x20001, clients[i].child);
                        check(observed.0 >= 0, 970);
                        if observed.0 > 0 {
                            terminal = true;
                            break;
                        }
                        ctl(0x1fffe, 0);
                    }
                    check(terminal, 993);
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
                if n == 0 {
                    // The earlier running observation may precede peer exit.
                    // EOF alone is not terminal authority: recheck this handle.
                    if !cfg!(skip_exit_recheck) {
                        let observed = ctl(0x20001, clients[i].child);
                        check(observed.0 >= 0, 970);
                        if observed.0 > 0 {
                            continue;
                        }
                    }
                    if cfg!(pad_launch_eof) && i == 0 && admitted {
                        // This mutant has already admitted the padded request.
                        // EOF can precede its parent's terminal observation.
                        ctl(0x1fffe, 0);
                        continue;
                    }
                    if cfg!(pad_launch_eof) && used[i] == 383 {
                        // Deliberate negative control: invent the missing zero byte.
                        used[i] = 384;
                    } else if i == 0 && !admitted {
                        check(
                            live == [[true, true], [false, false]]
                                && positions == [0, if cfg!(full_output) { 64 } else { 0 }],
                            992,
                        );
                        end(1100 + used[i] as u64);
                    } else {
                        end(990);
                    }
                } else {
                    check(n > 0 && n as usize <= need - used[i], 990);
                    used[i] += n as usize;
                }
                let need = if word(&frames[i], 0) == 4 { 384 } else { 32 };
                if used[i] < need {
                    continue;
                }
                let request = frames[i];
                frames[i] = [0; 384];
                used[i] = 0;
                let op = word(&request, 0);
                let mut reply = [0; 32];
                let result: i32;
                if op == 4 {
                    if i != 0 {
                        result = -13;
                    } else if admitted {
                        result = -16;
                    } else {
                        match validate(&request, generation, live[0]) {
                            Err(error) => result = error,
                            Ok(mut startup) => {
                                if cfg!(wrong_startup) {
                                    startup.strings[1][0] = b'X';
                                }
                                let reject = cfg!(reject_launch) && generation == 1 && !rejected;
                                let reserve =
                                    cfg!(partial_reservation) && generation == 1 && !rejected;
                                rejected = true;
                                let held = if reserve {
                                    let h = ctl(0x24000, 0xd001);
                                    check(h.0 > 0, 980);
                                    Some(h)
                                } else {
                                    None
                                };
                                let admission = admit(factory, third, &startup, reject);
                                if let Some(h) = held {
                                    check(
                                        ctl(0x24003, h.0 as u64).0 == 0 && ctl(0x24003, h.1).0 == 0,
                                        980,
                                    );
                                }
                                match admission {
                                    Err(error) => {
                                        check(
                                            positions
                                                == [0, if cfg!(full_output) { 64 } else { 0 }]
                                                && live == [[true, true], [false, false]],
                                            980,
                                        );
                                        result = error;
                                    }
                                    Ok(child) => {
                                        clients[1] = child;
                                        live[1] = [true, true];
                                        admitted = true;
                                        bootstrap(child, 1, generation);
                                        result = 0;
                                        put(&mut reply, 4, 0x73000000 | generation);
                                    }
                                }
                            }
                        }
                    }
                } else if op == 5 {
                    if i != 0 {
                        result = -13;
                    } else if !admitted
                        || collected
                        || word(&request, 4) != (0x73000000 | generation)
                    {
                        result = -10;
                    } else if request[8..32].iter().any(|v| *v != 0) {
                        result = -22;
                    } else if !exited[1] {
                        result = -11;
                    } else {
                        collected = true;
                        result = 0;
                        put(&mut reply, 4, 0x73000000 | generation);
                        put(
                            &mut reply,
                            8,
                            terminal_result.0 ^ if cfg!(wrong_status) { 1 } else { 0 },
                        );
                        put(
                            &mut reply,
                            12,
                            if cfg!(fault_as_exit) {
                                1
                            } else {
                                terminal_result.1
                            },
                        );
                    }
                } else {
                    let found = (0..2).find(|j| {
                        live[i][*j]
                            && word(&request, 4) == reference(i, *j, generation)
                            && word(&request, 8) == if i == 0 { 3 + *j as u32 } else { *j as u32 }
                    });
                    if let Some(j) = found {
                        let count = word(&request, 12);
                        if (op == 1 && i == 1 && j == 1) || (op == 2 && j == 0) {
                            result = -13;
                        } else if (op == 1 || op == 2)
                            && count <= 16
                            && request[16 + if op == 2 { count as usize } else { 0 }..32]
                                .iter()
                                .all(|v| *v == 0)
                        {
                            let count = if cfg!(short_write) && op == 2 {
                                count.min(1)
                            } else {
                                count
                            };
                            if cfg!(skip_write) && op == 2 {
                                result = count as i32;
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
                                result = get(&reply, 0) as i32;
                            }
                            check(result <= count as i32, 984);
                            if result > 0 {
                                positions[j] += result as u32;
                            }
                        } else if op == 3 && count == 0 && request[16..32].iter().all(|v| *v == 0) {
                            release(service, handles, &mut live, i, j, input_len);
                            result = 0;
                        } else {
                            result = -22;
                        }
                    } else {
                        result = -9;
                    }
                }
                put(&mut reply, 0, result as u32);
                check(transfer(clients[i].writer, &mut reply, true) == 1, 990);
            }
            if exited == [true, true] {
                break;
            }
            ctl(0x1fffe, 0);
        }
        check(
            admitted
                && collected
                && exited == [true, true]
                && live == [[false, false], [false, false]]
                && positions == [input_len, if cfg!(full_output) { 64 } else { 2 }],
            974,
        );
        for c in clients {
            check(
                ctl(0x24003, c.reader).0 == 0
                    && ctl(0x24003, c.writer).0 == 0
                    && ctl(0x20002, c.child).0 == 0,
                976,
            );
        }
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

#[path = "local-empty.rs"]
mod local_empty;

#[path = "streams.rs"]
mod streams;

#[path = "success.rs"]
mod success;

#[path = "cat-roles.rs"]
mod cat_roles;

#[path = "cat-admission.rs"]
mod cat_admission;
