// SPDX-License-Identifier: BSD-2-Clause
// Actual dash command substitution over the bounded stream and pipe owners.
use super::*;
fn admit(
    pipe: &mut Pipe,
    source: Connection,
    factory: u64,
    generation: u32,
    created: &[u8; 32],
) -> Connection {
    let mut table = [0; 64];
    table[..32].copy_from_slice(&receive(source));
    table[32..].copy_from_slice(&receive(source));
    let mut expected = [0; 64];
    for (fd, binding, flags) in [
        (0, 0, 0),
        (1, 1, 0),
        (2, 2, 0),
        (3, 3, 0),
        (4, 4, 0),
        (10, 0, 1),
    ] {
        expected[fd * 4] = binding;
        expected[fd * 4 + 1] = flags;
        expected[fd * 4 + 2] = 1;
    }
    check(table == expected, 2174);
    let token = if cfg!(pipe_dash_repeat) {
        generation as u64
    } else {
        1
    };
    let mut frozen = false;
    for _ in 0..10000 {
        let state = ctl(0x23004, source.child).0;
        if state == token as i64 {
            frozen = true;
            break;
        }
        check(state == 0, 2174);
        ctl(0x1fffe, 0);
    }
    check(frozen, 2174);
    check(pipe.stage_child(generation, [true; 2]).is_ok(), 2174);
    let req = ctl(0x24000, 0xd001);
    let rep = ctl(0x24000, 0xd001);
    check(req.0 > 0 && rep.0 > 0, 2174);
    let copy_token = if cfg!(pipe_repeat_token) { 1 } else { token };
    let handle = call(
        0x23006,
        factory,
        source.child,
        2,
        copy_token,
        req.0 as u64,
        rep.1,
    )
    .0;
    check(
        handle == (0xb0000000 | ((generation as u64) << 8) | 3) as i64,
        if cfg!(pipe_dash_repeat) { 2179 } else { 2174 },
    );
    let child = Connection {
        reader: rep.0 as u64,
        writer: req.1,
        child: handle as u64,
    };
    let mut receipt = [0; 32];
    put(&mut receipt, 0, 65);
    put(&mut receipt, 4, generation);
    put(&mut receipt, 8, 2);
    for j in 0..3 {
        put(
            &mut receipt,
            12 + j * 4,
            0x77000000 + ((j as u32) << 16) + generation,
        );
    }
    put(&mut receipt, 24, get(&created, 8));
    put(&mut receipt, 28, get(&created, 12));
    if cfg!(pipe_repeat_receipt) && generation == 2 {
        put(&mut receipt, 24, 0x78000101);
    }
    send(child, &mut receipt);
    let ready = if cfg!(pipe_dash_repeat) {
        readiness(child).unwrap_or_else(|_| end(2180))
    } else {
        receive(child)
    };
    check(get(&ready, 0) == 66 && ready[4..] == [0; 28], 2174);
    check(pipe.finish_child_copy(generation, true).is_ok(), 2174);
    let mut complete = [0; 32];
    put(&mut complete, 0, 67);
    send(source, &mut complete);
    send(child, &mut complete);

    child
}

#[cfg(pipe_exec)]
fn replace(
    pipe: &mut Pipe,
    child: Connection,
    factory: u64,
    generation: u32,
    denied: bool,
    created: &[u8; 32],
    holders: &[[bool; 3]; 2],
) {
    let token = if denied { 1 } else { 2 };
    let mut arguments = [0; 272];
    // The staged argv/env record exceeds the existing 256-byte channel limit.
    for chunk in arguments.chunks_mut(256) {
        check(
            transfer_bounded(child.reader, chunk, false, 100000) == 1,
            2301,
        );
    }
    let mut mask = receive(child);
    let mut table = [0; 64];
    table[..32].copy_from_slice(&receive(child));
    table[32..].copy_from_slice(&receive(child));
    let mut expected = [0; 64];
    for (fd, binding, flags) in [(0, 0, 0), (1, 4, 0), (2, 2, 0), (10, 0, 1), (11, 4, 1)] {
        expected[fd * 4..fd * 4 + 4].copy_from_slice(&[binding, flags, 1, 0]);
    }
    check(table == expected, 2185);
    check(holders[1] == [true, false, true], 2188);
    let mut expected_mask = [0; 32];
    expected_mask[..8].copy_from_slice(b"AEEMSK01");
    check(mask == expected_mask, 2186);
    let plan =
        crate::exec_fds::prepare_pipe(&table, &[2, 0, 1, 0, 2]).unwrap_or_else(|_| end(2302));
    let mut frozen = false;
    for _ in 0..10000 {
        let state = ctl(0x23004, child.child).0;
        if state == token {
            frozen = true;
            break;
        }
        check(state == 0, 2187);
        ctl(0x1fffe, 0);
    }
    check(frozen, 2187);
    let mut args = Args {
        argc: u64::from_le_bytes(arguments[..8].try_into().unwrap()),
        envc: u64::from_le_bytes(arguments[8..16].try_into().unwrap()),
        strings: [[0; 32]; 8],
    };
    for i in 0..8 {
        args.strings[i].copy_from_slice(&arguments[16 + i * 32..48 + i * 32]);
    }
    if cfg!(pipe_consumer) {
        check(args.argc == 4 && args.envc == 4, 2189);
        for (index, value) in [b"/inputs/helper".as_slice(), b"argv", b"a b", b"*"]
            .iter()
            .enumerate()
        {
            let mut expected = [0; 32];
            expected[..value.len()].copy_from_slice(value);
            check(args.strings[index] == expected, 2189);
        }
        if cfg!(pipe_consumer_args) && !denied {
            args.strings[2][0] = b'x';
        }
    } else {
        check(
            args.argc == 1
                && args.strings[0][..6] == *b"/next\0"
                && args.strings[0][6..] == [0; 26],
            2189,
        );
    }
    let image = if denied { 0xc004 } else { 0xc003 };
    let result = call(
        0x23007,
        factory,
        child.child,
        image,
        token as u64,
        &args as *const Args as u64,
        0,
    )
    .0;
    if denied {
        check(
            result == -13 && call(0x23008, factory, child.child, 0, 0, 0, 0) == (0, 0, 0),
            2190,
        );
        check(
            call(0x23005, child.child, token as u64, 0, 0, 0, 0).0 == 0,
            2303,
        );
        simple(child, -13);
        return;
    }
    check(
        result == 0 && call(0x23008, factory, child.child, 0, 0, 0, 0) == (2, image, 1),
        2191,
    );
    check(
        plan.users == [1, 0, 1, 0, 1] && plan.release == [false; 5],
        2184,
    );
    check(
        pipe.commit_exec(
            Caller::Child(generation),
            if cfg!(pipe_exec_stale) {
                2
            } else if cfg!(pipe_exec_serial_stale) && generation == 2 {
                1
            } else {
                get(created, 4)
            },
            [false, true],
            [false, true],
        )
        .is_ok(),
        2184,
    );
    check(
        call(0x23009, factory, child.child, token as u64, 0, 0, 0).0 == 0,
        2304,
    );
    let mut boot = [0; 128];
    boot[..8].copy_from_slice(b"AECAT001");
    boot[8..12].copy_from_slice(&3u32.to_le_bytes());
    boot[12..16].copy_from_slice(&generation.to_le_bytes());
    for j in 0..3 {
        for (k, value) in [
            j as u32 + 1,
            0x76000000 + ((j as u32) << 16) + generation,
            j as u32,
            if j == 0 { 1 } else { 2 },
            if j == 2 { 256 } else { 32 },
        ]
        .iter()
        .enumerate()
        {
            boot[32 + j * 32 + k * 4..36 + j * 32 + k * 4].copy_from_slice(&value.to_le_bytes());
        }
    }
    let mut survivors = plan.table;
    if cfg!(pipe_exec_drop) {
        survivors[4..8].fill(0);
    }
    let mut grant = [0; 32];
    grant[..8].copy_from_slice(b"AEPEX001");
    for (i, v) in [
        generation,
        get(created, 4),
        get(created, 8),
        get(created, 12),
    ]
    .iter()
    .enumerate()
    {
        put(&mut grant, 8 + i * 4, *v);
    }
    if cfg!(pipe_exec_serial_grant) && generation == 2 {
        put(&mut grant, 12, 1);
        put(&mut grant, 16, 0x78000101);
        put(&mut grant, 20, 0x78000102);
    }
    send(child, &mut boot);
    send(child, &mut survivors);
    send(child, &mut grant);
    send(child, &mut mask);
}

fn serial_bytes(generation: u32, binding: usize) -> &'static [u8] {
    match (generation, binding) {
        (1, 0) if cfg!(pipe_exec_serial) => {
            b"a=$(/next); echo \"$a\"\nb=$(/next); echo \"$b\"\nexit 0\n"
        }
        (1, 0) => b"a=$(echo pipe); echo \"$a\"\nb=$(echo pipe); echo \"$b\"\nexit 0\n",
        (1, 1) => b"SHELL READY\npipe\npipe\n",
        (1, 2) => b"$ $ $ ",
        (2, 0) => b"echo clean; exit 0\n",
        (2, 1) => b"SHELL READY\nclean\n",
        (2, 2) => b"$ ",
        _ => b"",
    }
}
fn pipe_bytes() -> &'static [u8] {
    if cfg!(pipe_consumer) {
        b"argv ok\n"
    } else if cfg!(dash_signal) {
        b"USR1\n"
    } else {
        b"pipe\n"
    }
}
fn output(generation: u32) -> &'static [u8] {
    if cfg!(pipe_consumer) {
        b"substitution ok\n"
    } else if cfg!(dash_signal) {
        b"signal ok\n"
    } else if cfg!(pipe_dash_repeat) {
        if generation == 1 {
            b"pipe\npipe\n"
        } else {
            b"clean\n"
        }
    } else {
        b"pipe\n"
    }
}
fn close_backend(
    service: Connection,
    handle: u32,
    binding: usize,
    positions: &[u32; 3],
    generation: u32,
) {
    if binding == 1 && !cfg!(shell_console) {
        check(*positions == [0, output(generation).len() as u32, 0], 2175);
        let mut request = [0; 32];
        put(&mut request, 0, 2);
        put(&mut request, 4, handle);
        put(&mut request, 12, 16);
        send(service, &mut request);
        let response = receive(service);
        let mut expected = [0; 32];
        put(&mut expected, 0, output(generation).len() as u32);
        expected[16..16 + output(generation).len()].copy_from_slice(output(generation));
        check(response == expected, 2175);
    }
    check(backend(service, 3, handle, 0) == [0; 32], 2175);
}

pub fn run(
    mut pipe: Pipe,
    source: Connection,
    service: Connection,
    factory: u64,
    generation: u32,
    handles: [u32; 3],
) {
    let mut child = None;
    let mut exec_denied = false;
    let mut exec_done = false;
    let mut created = [0; 32];
    let mut frames = [[0; 32]; 2];
    let mut used = [0usize; 2];
    let mut dead = [false; 2];
    let mut holders = [[true; 3], [false; 3]];
    let mut positions = [0u32; 3];
    let mut closes = 0;
    let mut input_pending = false;
    let mut written = 0usize;
    let mut read = 0usize;
    let mut eof = false;
    let mut issued = false;
    let mut collected = false;
    let mut completed = 0;
    let cycles = if cfg!(pipe_dash_repeat) {
        if generation == 1 { 2 } else { 0 }
    } else {
        1
    };
    let mut child_generation = generation;
    let mut pid = generation * 4 + 3;
    for _ in 0..100000 {
        let clients = [Some(source), child];
        for who in 0..2 {
            let Some(client) = clients[who] else { continue };
            if dead[who] || (who == 1 && child.is_none()) {
                continue;
            }
            let state = ctl(0x20001, client.child);
            if state.0 != 0 {
                check(state.0 == 1 && state.2 == 1 && used[who] == 0, 2176);
                let mut extra = [0; 1];
                check(
                    call(
                        0x24001,
                        client.reader,
                        extra.as_mut_ptr() as u64,
                        1,
                        0,
                        0,
                        0,
                    )
                    .0 == 0,
                    2176,
                );
                check(
                    pipe.confirmed_terminal(if who == 0 {
                        Caller::Parent
                    } else {
                        Caller::Child(child_generation)
                    })
                    .is_ok(),
                    2176,
                );
                dead[who] = true;
                for j in 0..3 {
                    if holders[who][j] {
                        holders[who][j] = false;
                        if !holders[1 - who][j] {
                            close_backend(service, handles[j], j, &positions, generation);
                            closes += 1;
                        }
                    }
                }
            }
        }
        if dead[0]
            && (if cfg!(pipe_dash_repeat) {
                child.is_none()
            } else {
                dead[1]
            })
        {
            check(
                (if cfg!(pipe_dash_repeat) {
                    completed == cycles
                } else {
                    child.is_some()
                        && collected
                        && eof
                        && written == pipe_bytes().len()
                        && read == pipe_bytes().len()
                        && pipe.retire_if_idle([used[0] != 0, used[1] != 0])
                }) && (!cfg!(pipe_exec) || cycles == 0 || (exec_denied && exec_done))
                    && !issued
                    && (if cfg!(shell_console) {
                        input_pending
                            && positions
                                == [
                                    serial_bytes(generation, 0).len() as u32,
                                    serial_bytes(generation, 1).len() as u32,
                                    serial_bytes(generation, 2).len() as u32,
                                ]
                    } else {
                        positions == [0, output(generation).len() as u32, 0]
                    })
                    && closes == 3
                    && holders == [[false; 3]; 2],
                2177,
            );
            if !cfg!(shell_console) {
                finish_backend(service);
            }
            dispose(source);
            if let Some(c) = child {
                dispose(c);
            }
            return;
        }
        for who in 0..2 {
            let Some(client) = clients[who] else { continue };
            if dead[who] || (who == 1 && child.is_none()) {
                continue;
            }
            if used[who] < 32 {
                let n = call(
                    0x24001,
                    client.reader,
                    frames[who][used[who]..].as_mut_ptr() as u64,
                    (32 - used[who]) as u64,
                    0,
                    0,
                    0,
                )
                .0;
                if n == -11 || n == 0 {
                    continue;
                }
                check(n > 0 && n as usize <= 32 - used[who], 2175);
                used[who] += n as usize;
                if used[who] != 32 {
                    continue;
                }
            }
            let frame = &frames[who];
            let op = get(frame, 0);
            let binding = get(frame, 8) as usize;
            match op {
                #[cfg(pipe_exec)]
                0x6e65642f | 0x78656e2f | 0x706e692f => {
                    let denied = op == 0x6e65642f;
                    let mut name = [0; 32];
                    let path: &[u8] = if denied {
                        b"/denied"
                    } else if cfg!(pipe_consumer) {
                        b"/inputs/helper"
                    } else {
                        b"/next"
                    };
                    name[..path.len()].copy_from_slice(path);
                    check(
                        who == 1 && *frame == name && !exec_done && denied != exec_denied,
                        2305,
                    );
                    replace(
                        &mut pipe,
                        client,
                        factory,
                        child_generation,
                        denied,
                        &created,
                        &holders,
                    );
                    if denied {
                        exec_denied = true;
                    } else {
                        exec_done = true;
                    }
                }

                4 | 5 => shell::directory_reply(client, frame, generation),
                82 => {
                    check(
                        who == 0 && child.is_none() && created == [0; 32] && completed < cycles,
                        2174,
                    );
                    let Outcome::Reply(mut response) = pipe.request(Caller::Parent, frame) else {
                        end(2174)
                    };
                    check(
                        get(&response, 0) == 0 && get(&response, 4) == completed + 1,
                        2174,
                    );
                    created = response;
                    written = 0;
                    read = 0;
                    eof = false;
                    send(client, &mut response);
                }
                64 => {
                    check(
                        who == 0
                            && child.is_none()
                            && get(&created, 4) == completed + 1
                            && get(frame, 4) == 2
                            && get(frame, 8) == generation
                            && get(frame, 12) == 16
                            && frame[16..] == [0; 16]
                            && holders == [[true; 3], [false; 3]],
                        2174,
                    );
                    child_generation = if cfg!(pipe_dash_repeat) {
                        completed + 1
                    } else {
                        generation
                    };
                    pid = child_generation * 4 + 3;
                    child = Some(admit(
                        &mut pipe,
                        source,
                        factory,
                        child_generation,
                        &created,
                    ));
                    collected = false;
                    exec_denied = false;
                    exec_done = false;
                    holders[1] = [true; 3];
                }
                80 => {
                    let selector = get(frame, 4) as i32;
                    let options = get(frame, 8);
                    check(
                        who == 0
                            && !issued
                            && (selector == -1 || selector == pid as i32)
                            && options <= 1
                            && frame[12..] == [0; 20],
                        2175,
                    );
                    if child.is_none() || collected {
                        simple(client, -10);
                    } else if !dead[1] {
                        if options == 0 {
                            continue;
                        }
                        simple(client, 0);
                    } else {
                        check(
                            eof && read == pipe_bytes().len() && written == pipe_bytes().len(),
                            2175,
                        );
                        let mut response = [0; 32];
                        put(&mut response, 0, pid);
                        put(&mut response, 4, pid);
                        send(client, &mut response);
                        let status: u32 = if cfg!(pipe_dash_status) { 256 } else { 0 };
                        send(client, &mut status.to_le_bytes());
                        issued = true;
                    }
                }
                81 => {
                    check(
                        who == 0
                            && issued
                            && dead[1]
                            && !collected
                            && get(frame, 4) == pid
                            && frame[8..] == [0; 24],
                        2175,
                    );
                    check(!cfg!(pipe_exec) || (exec_denied && exec_done), 2305);
                    issued = false;
                    collected = true;
                    simple(client, 0);
                    if cfg!(pipe_dash_repeat) {
                        check(
                            eof && read == pipe_bytes().len()
                                && written == pipe_bytes().len()
                                && used[1] == 0
                                && holders[1] == [false; 3]
                                && pipe.retire_if_idle([false; 2]),
                            2181,
                        );
                        dispose(child.unwrap());
                        child = None;
                        dead[1] = false;
                        created = [0; 32];
                        completed += 1;
                    }
                }
                1..=3 if binding < 3 => {
                    let n = get(frame, 12) as usize;
                    let reference = (if who == 0 { 0x76000000 } else { 0x77000000 })
                        + ((binding as u32) << 16)
                        + if who == 0 {
                            generation
                        } else {
                            child_generation
                        };
                    check(
                        holders[who][binding]
                            && get(frame, 4) == reference
                            && n <= 16
                            && (op != 3 || n == 0)
                            && (op != 1 || binding == 0)
                            && (op != 2 || binding != 0)
                            && frame[16 + if op == 2 { n } else { 0 }..]
                                .iter()
                                .all(|v| *v == 0),
                        2175,
                    );
                    if op == 3 {
                        holders[who][binding] = false;
                        if !holders[1 - who][binding] {
                            close_backend(
                                service,
                                handles[binding],
                                binding,
                                &positions,
                                generation,
                            );
                            closes += 1;
                        }
                        simple(client, 0);
                    } else {
                        let mut request = *frame;
                        put(&mut request, 0, if op == 1 { 2 } else { 4 });
                        put(&mut request, 4, handles[binding]);
                        put(&mut request, 8, positions[binding]);
                        send(service, &mut request);
                        let mut response = receive(service);
                        let count = get(&response, 0) as i32;
                        if cfg!(shell_console) && op == 1 && n > 0 && count == -11 {
                            check(response[4..] == [0; 28], 2182);
                            input_pending = true;
                            continue;
                        }
                        check(
                            count >= 0
                                && count <= n as i32
                                && response[4..16] == [0; 12]
                                && response[16 + if op == 1 { count as usize } else { 0 }..]
                                    .iter()
                                    .all(|v| *v == 0),
                            2175,
                        );
                        if cfg!(shell_console) {
                            let expected = serial_bytes(generation, binding);
                            let start = positions[binding] as usize;
                            let end = start + count as usize;
                            let bytes = if op == 1 { &response } else { frame };
                            check(
                                end <= expected.len()
                                    && bytes[16..16 + count as usize] == expected[start..end],
                                2182,
                            );
                            positions[binding] = end as u32;
                        } else {
                            positions[binding] += count as u32;
                            check(
                                positions[0] == 0
                                    && positions[1] <= output(generation).len() as u32
                                    && positions[2] == 0,
                                2175,
                            );
                        }
                        send(client, &mut response);
                    }
                }
                1..=3 => {
                    check(child.is_some(), 2175);
                    let caller = if who == 0 {
                        Caller::Parent
                    } else {
                        Caller::Child(child_generation)
                    };
                    let Outcome::Reply(mut response) = pipe.request(caller, frame) else {
                        continue;
                    };
                    let count = get(&response, 0) as i32;
                    check(count >= 0, 2175);
                    if op == 2 {
                        check(
                            who == 1 && written + count as usize <= pipe_bytes().len(),
                            2175,
                        );
                        check(
                            frame[16..16 + count as usize]
                                == pipe_bytes()[written..written + count as usize],
                            2175,
                        );
                        written += count as usize;
                    } else if op == 1 {
                        check(who == 0 && !eof && read + count as usize <= written, 2175);
                        check(
                            response[16..16 + count as usize]
                                == pipe_bytes()[read..read + count as usize],
                            2175,
                        );
                        read += count as usize;
                        if count == 0 {
                            check(read == pipe_bytes().len(), 2175);
                            eof = true;
                        }
                    }
                    send(client, &mut response);
                }
                _ => end(2175),
            }
            used[who] = 0;
            frames[who] = [0; 32];
        }
        ctl(0x1fffe, 0);
    }
    end(2178)
}
