// SPDX-License-Identifier: BSD-2-Clause
// Bounded post-fork request owner. Initial admission remains in inherit.rs.
use super::*;
#[cfg(shell_null)]
fn null_bootstrap(child: Connection, object: &crate::null::Null, active: bool) {
    let mut b = [0; 32];
    b[..8].copy_from_slice(b"AENUL001");
    put(&mut b, 8, object.factory());
    put(&mut b, 12, if active { object.reference() } else { 0 });
    put(&mut b, 16, ((child.child >> 8) & 255) as u32);
    put(&mut b, 20, 1);
    put(&mut b, 24, 3);
    send(child, &mut b);
}
#[inline(never)]
fn reply(c: Connection, value: i32) {
    let mut b = [0; 32];
    put(&mut b, 0, value as u32);
    send(c, &mut b);
}
#[inline(never)]
fn status_reply(c: Connection, pid: u32, status: u32) {
    let mut b = [0; 32];
    put(&mut b, 0, pid);
    put(&mut b, 4, pid);
    send(c, &mut b);
    send(
        c,
        &mut (status + if cfg!(shell_wait_status) { 256 } else { 0 }).to_le_bytes(),
    );
}
#[inline(never)]
fn file_request(
    c: Connection,
    who: usize,
    generation: u32,
    b: &mut [u8; 32],
    service: Connection,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
    positions: &mut [u32; 3],
    closes: &mut u32,
) -> bool {
    let op = get(b, 0);
    let j = get(b, 8) as usize;
    let n = get(b, 12) as usize;
    if j >= 3
        || !holders[who][j]
        || (!cfg!(dispatch_foreign)
            && !(cfg!(prefork_foreign) && !holders[1][0])
            && get(b, 4)
                != (if (cfg!(shell_failed_exec) || cfg!(shell_files_denied)) && who == 1 {
                    0x77000000
                } else {
                    0x76000000
                }) + ((j as u32) << 16)
                    + generation)
    {
        reply(c, -13);
        return true;
    }
    if !(1..=3).contains(&op)
        || n > 16
        || (op == 3 && n != 0)
        || b[16 + if op == 2 { n } else { 0 }..]
            .iter()
            .any(|v| *v != 0)
    {
        reply(c, -22);
        return true;
    }
    if (op == 1 && j != 0) || (op == 2 && j == 0) {
        reply(c, -13);
        return true;
    }
    if (cfg!(failed_drop_output) || cfg!(files_denied_drop_output)) && op == 2 && who == 0 && j == 1
    {
        reply(c, n as i32);
        return true;
    }
    if op == 3 && holders[1 - who][j] {
        holders[who][j] = false;
        reply(c, 0);
        return true;
    }
    #[cfg(shell_null)]
    if op == 3 && j == 0 {
        let mut request = [0; 32];
        put(&mut request, 0, 2);
        put(&mut request, 4, handles[0]);
        put(&mut request, 12, 1);
        send(service, &mut request);
        let mut expected = [0; 32];
        put(&mut expected, 0, 1);
        expected[16] = b'a';
        check(receive(service) == expected && positions[0] == 0, 2311);
    }
    if cfg!(shell_argv) && op == 3 && j == 1 {
        let mut request = [0; 32];
        put(&mut request, 0, 2);
        put(&mut request, 4, handles[j]);
        put(&mut request, 12, 16);
        send(service, &mut request);
        let actual = receive(service);
        let mut expected = [0; 32];
        let output: &[u8] = if cfg!(shell_files_denied) {
            b"denied ok\n"
        } else if cfg!(shell_files_redirect) {
            b"AB"
        } else if cfg!(shell_files) {
            b""
        } else if cfg!(shell_failed_exec) {
            b"exec errors ok\n"
        } else if cfg!(shell_wait) {
            b"wait ok\n"
        } else if cfg!(shell_null) {
            b"null ok\n"
        } else if cfg!(shell_closed) {
            b"closed ok\n"
        } else {
            b"argv ok\n"
        };
        put(&mut expected, 0, output.len() as u32);
        expected[16..16 + output.len()].copy_from_slice(output);
        check(
            actual == expected
                && positions
                    == &[
                        0,
                        output.len() as u32,
                        if cfg!(shell_failed_exec) || cfg!(shell_files_denied) {
                            positions[2]
                        } else if cfg!(null_fault) {
                            20
                        } else {
                            0
                        },
                    ],
            2310,
        );
    }
    #[cfg(null_fault)]
    if op == 3 && j == 2 {
        let diagnostic = b"Illegal instruction\n";
        check(positions[2] == diagnostic.len() as u32, 2325);
        for offset in [0, 16] {
            let count = (diagnostic.len() - offset).min(16);
            let mut request = [0; 32];
            put(&mut request, 0, 2);
            put(&mut request, 4, handles[2]);
            put(&mut request, 8, offset as u32);
            put(&mut request, 12, count as u32);
            send(service, &mut request);
            let mut expected = [0; 32];
            put(&mut expected, 0, count as u32);
            expected[16..16 + count].copy_from_slice(&diagnostic[offset..offset + count]);
            check(receive(service) == expected, 2325);
        }
    }
    put(
        b,
        0,
        if op == 1 {
            2
        } else if op == 2 {
            4
        } else {
            3
        },
    );
    put(b, 4, handles[j]);
    put(b, 8, if op == 3 { 0 } else { positions[j] });
    send(service, b);
    let mut response = receive(service);
    let count = get(&response, 0) as i32;
    check(
        count >= -4095
            && count <= n as i32
            && response[4..16] == [0; 12]
            && response[16
                + if op == 1 && count > 0 {
                    count as usize
                } else {
                    0
                }..]
                .iter()
                .all(|v| *v == 0),
        2134,
    );
    if (cfg!(stream_pending) || cfg!(shell_console)) && op == 1 && n != 0 && count == -11 {
        if cfg!(pending_position) {
            positions[j] += 1;
        }
        if !cfg!(pending_reply) {
            return false;
        }
    }
    if count >= 0 {
        if op == 3 {
            holders[who][j] = false;
            *closes += 1;
        } else {
            positions[j] += count as u32;
        }
    }
    send(c, &mut response);
    true
}
// Only the parent exists here; bounded whole-frame receives cannot starve a child.
#[cfg(shell_prelude)]
pub fn before_fork(
    source: Connection,
    service: Connection,
    handles: &[u32; 3],
    generation: u32,
    positions: &mut [u32; 3],
    #[cfg(shell_files)] files: &mut crate::scratch_owner::Owner,
    #[cfg(shell_files)] references: &mut [u32; 2],
) -> [u8; 32] {
    let mut holders = [[true; 3], [false; 3]];
    let mut closes = 0;
    for _ in 0..if cfg!(shell_console) { 64 } else { 16 } {
        let mut b = receive(source);
        #[cfg(shell_files)]
        if get(&b, 0) == 6
            || (cfg!(shell_files_redirect) && (1..=3).contains(&get(&b, 0)) && get(&b, 8) >= 3)
        {
            #[cfg(shell_files_redirect)]
            {
                let op = get(&b, 0);
                if op == 6 {
                    check(b[16..] == *b"/scratch/data\0\0\0", 2553);
                    check(references[0] == 0, 2552);
                    check(matches!(get(&b, 12), 1 | 14), 2550);
                }
                let mut response = if cfg!(files_redirect_drop_write)
                    && op == 2
                    && get(&b, 12) == 1
                    && b[16] == b'B'
                {
                    let mut reply = [0; 32];
                    put(&mut reply, 0, 1);
                    reply
                } else {
                    scratch_gateway(service, files, 0, &b)
                };
                check((get(&response, 0) as i32) >= 0, 2551);
                if op == 6 {
                    references[0] = get(&response, 4);
                }
                if op == 3 {
                    references[0] = 0;
                }
                send(source, &mut response);
                continue;
            }
            // This selection witnesses one writer, later duplicated to FD9.
            check(
                references[0] == 0 && get(&b, 12) == 14 && b[16..] == *b"/scratch/leak\0\0\0",
                2506,
            );
            let mut response = scratch_gateway(service, files, 0, &b);
            check(get(&response, 0) == 0 && get(&response, 8) == 3, 2506);
            references[0] = get(&response, 4);
            send(source, &mut response);
            continue;
        }
        match get(&b, 0) {
            64 => return b,
            #[cfg(shell_dash)]
            4 | 5 => shell::directory_reply(source, &b, generation),
            80 => {
                if get(&b, 4) == u32::MAX && get(&b, 8) == 1 && b[12..] == [0; 20] {
                    reply(source, if cfg!(prefork_wait) { 0 } else { -10 });
                } else {
                    reply(source, -22);
                }
            }
            1 | 2 => {
                let mut done = false;
                for _ in 0..100000 {
                    let mut request = b;
                    if file_request(
                        source,
                        0,
                        generation,
                        &mut request,
                        service,
                        handles,
                        &mut holders,
                        positions,
                        &mut closes,
                    ) {
                        done = true;
                        break;
                    }
                    check(cfg!(shell_console), 2141);
                    ctl(0x1fffe, 0);
                }
                check(done, 2141);
            }
            _ => reply(source, -95),
        }
    }
    end(2140)
}
#[inline(never)]
pub fn run(
    factory: u64,
    image: u64,
    mut clients: [Connection; 2],
    service: Connection,
    handles: [u32; 3],
    mut boot: [u8; 128],
    mut holders: [[bool; 3]; 2],
    generation: u32,
    mut positions: [u32; 3],
    #[cfg(shell_files)] files: &mut crate::scratch_owner::Owner,
    #[cfg(shell_files)] file_references: [u32; 2],
) {
    #[cfg(shell_null)]
    let mut null = crate::null::Null::new(((clients[1].child >> 8) & 255) as u32);
    #[cfg(shell_null)]
    null_bootstrap(clients[1], &null, false);
    let mut buffers = [[0u8; 400]; 2];
    let mut used = [0usize; 2];
    let mut needed = [32usize; 2];
    let mut dead = [false; 2];
    let mut child_status = 0;
    let mut closes = 0;
    let mut executed = false;
    let mut denied_exec = false;
    #[cfg(shell_files_denied)]
    let mut denied_write = false;
    #[cfg(shell_null)]
    let mut denied = false;
    #[cfg(shell_null)]
    let mut denied_record = [0; 368];
    let mut waiting = false;
    let mut issued = false;
    let mut collected = false;
    let mut deferred = 0;
    // The existing frame remains owned by this caller until its reply is sent.
    let mut pending = [false; 2];
    let mut peer_progress = false;
    let mut pid = generation * 4 + 3;
    let mut admissions = 1u32;
    let mut reaped = false;
    for _ in 0..100000 {
        for who in 0..2 {
            if dead[who] {
                continue;
            }
            let state = ctl(0x20001, clients[who].child);
            if state.0 > 0 {
                #[cfg(null_fault)]
                if who == 1 {
                    check(
                        state.0 == 135
                            && state.2 == 2
                            && used[1] == 0
                            && !pending[1]
                            && denied
                            && !executed
                            && null.active()
                            && holders == [[true; 3]; 2],
                        2324,
                    );
                    let mut trailing = [0; 32];
                    check(
                        call(
                            0x24001,
                            clients[1].reader,
                            trailing.as_mut_ptr() as u64,
                            32,
                            0,
                            0,
                            0,
                        )
                        .0 == 0,
                        2324,
                    );
                    // Terminal observation precedes release; dead prevents further
                    // requests from this connection, including factory opens.
                    dead[1] = true;
                    let reference = null.reference();
                    if !cfg!(null_stop_keep) {
                        null.release_stopped();
                    }
                    check(!null.active(), 2322);
                    for op in 1..=3 {
                        let mut stale = [0; 32];
                        put(&mut stale, 0, op);
                        put(&mut stale, 4, reference);
                        put(&mut stale, 8, 3);
                        check(get(&null.request(true, &stale), 0) as i32 == -9, 2322);
                    }
                    // Parent still holds every backend object; no final close
                    // may be forwarded while retiring only the child's aliases.
                    if !cfg!(null_stop_holders) {
                        holders[1] = [false; 3];
                    }
                    check(holders == [[true; 3], [false; 3]] && closes == 0, 2323);
                    child_status = wait_status(((state.0 - 1) as u32, state.2 as u32));
                    continue;
                }
                check(
                    state.0
                        == if cfg!(shell_files_denied) {
                            if who == 1 { 3 } else { 1 }
                        } else if cfg!(shell_files_redirect) {
                            1
                        } else if cfg!(shell_files) {
                            if who == 1 { 96 } else { 23 }
                        } else if (cfg!(shell_failed_exec) || cfg!(shell_files_denied)) && who == 1
                        {
                            if admissions == 1 { 128 } else { 127 }
                        } else if cfg!(shell_null) && who == 1 {
                            8
                        } else if cfg!(shell_argv) {
                            1
                        } else if who == 0 && cfg!(shell_repeat) {
                            1
                        } else if who == 0 && cfg!(shell_resume) {
                            if generation == 1 { 1 } else { 8 }
                        } else if who == 0 && !cfg!(shell_dash) {
                            72
                        } else {
                            73
                        }
                        && state.2 == 1
                        && used[who] == 0
                        && !pending[who],
                    2130,
                );
                dead[who] = true;
                if who == 1 {
                    child_status = ((state.0 - 1) as u32) << 8;
                }
            } else {
                check(state.0 == 0, 2130);
            }
        }
        if waiting && dead[1] {
            status_reply(clients[0], pid, child_status);
            waiting = false;
            issued = true;
        }
        if dead == [true; 2] {
            #[cfg(shell_files_denied)]
            check(
                denied_write && !executed && positions[2] > 0 && positions[2] <= 256,
                2555,
            );
            #[cfg(shell_files)]
            check(files.closed() && !files.poisoned(), 2506);
            #[cfg(shell_null)]
            check(!null.active(), 2312);
            check(
                (executed
                    || cfg!(shell_files_denied)
                    || cfg!(null_fault)
                    || (cfg!(shell_failed_exec) && denied_exec))
                    && collected
                    && !waiting
                    && !issued
                    && (cfg!(shell_dash) || deferred > 0)
                    && positions
                        == if cfg!(shell_argv) {
                            [
                                0,
                                if cfg!(shell_files_denied) {
                                    10
                                } else if cfg!(shell_files_redirect) {
                                    2
                                } else if cfg!(shell_files) {
                                    0
                                } else if cfg!(shell_failed_exec) {
                                    15
                                } else if cfg!(shell_closed) {
                                    10
                                } else {
                                    8
                                },
                                if cfg!(shell_failed_exec) || cfg!(shell_files_denied) {
                                    positions[2]
                                } else if cfg!(null_fault) {
                                    20
                                } else {
                                    0
                                },
                            ]
                        } else if cfg!(shell_redirect) {
                            [72, 60, 19]
                        } else if cfg!(shell_repeat) {
                            [36, 51, 8]
                        } else if cfg!(shell_resume) {
                            [22, 27, 4]
                        } else if cfg!(shell_console) {
                            [16, 24, 2]
                        } else {
                            [
                                if cfg!(shell_dash) { 1 } else { 3 },
                                0,
                                if cfg!(stream_pending) { 1 } else { 0 },
                            ]
                        }
                    && (!cfg!(stream_pending) || peer_progress)
                    && closes == 3
                    && holders == [[false; 3]; 2],
                2131,
            );
            if cfg!(shell_failed_exec) {
                check(
                    admissions == 2 && reaped && positions[2] > 0 && positions[2] <= 256,
                    2341,
                );
                finish_backend(service);
                dispose(clients[0]);
            } else if cfg!(shell_repeat) {
                check(admissions == 3 && reaped, 2153);
                dispose(clients[0]);
            } else {
                finish(service, clients[0], clients[1]);
            }
            return;
        }
        for who in 0..2 {
            if dead[who] || (who == 0 && waiting) {
                continue;
            }
            if pending[who] {
                let mut request = [0; 32];
                request.copy_from_slice(&buffers[who][..32]);
                if file_request(
                    clients[who],
                    who,
                    if who == 1 {
                        ((clients[1].child >> 8) & 255) as u32
                    } else {
                        generation
                    },
                    &mut request,
                    service,
                    &handles,
                    &mut holders,
                    &mut positions,
                    &mut closes,
                ) {
                    pending[who] = false;
                    used[who] = 0;
                    needed[who] = 32;
                    buffers[who].fill(0);
                }
                continue;
            }
            let n = call(
                0x24001,
                clients[who].reader,
                buffers[who][used[who]..].as_mut_ptr() as u64,
                (needed[who] - used[who]).min(256) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 || n == 0 {
                continue;
            }
            check(n > 0 && n as usize <= needed[who] - used[who], 2132);
            used[who] += n as usize;
            if used[who] != needed[who] {
                continue;
            }
            if needed[who] == 400 {
                #[cfg(shell_failed_exec)]
                {
                    check(
                        who == 1 && !denied_exec && !executed && holders == [[true; 3]; 2],
                        2340,
                    );
                    failed_exec(clients[1], &buffers[who], admissions);
                    denied_exec = true;
                    used[who] = 0;
                    needed[who] = 32;
                    buffers[who].fill(0);
                    continue;
                }
                #[cfg(shell_null)]
                {
                    let mut denied_name = [0; 32];
                    denied_name[..7].copy_from_slice(b"/denied");
                    if buffers[who][..32] == denied_name {
                        check(
                            who == 1
                                && !denied
                                && !executed
                                && null.active()
                                && holders == [[true; 3]; 2],
                            2320,
                        );
                        let reference = null.reference();
                        exec_streams::deny_null(factory, clients[1], &buffers[who]);
                        check(
                            null.active()
                                && null.reference() == reference
                                && holders == [[true; 3]; 2],
                            2320,
                        );
                        if cfg!(null_bad_rollback) {
                            let mut close = [0; 32];
                            put(&mut close, 0, 3);
                            put(&mut close, 4, reference);
                            put(&mut close, 8, 3);
                            check(null.request(true, &close) == [0; 32], 2320);
                        }
                        denied_record.copy_from_slice(&buffers[who][32..]);
                        denied = true;
                        used[who] = 0;
                        needed[who] = 32;
                        buffers[who].fill(0);
                        continue;
                    }
                    check(denied && buffers[who][32..] == denied_record, 2321);
                }
                if cfg!(shell_repeat) && !cfg!(repeat_boot) {
                    let child_generation = ((clients[1].child >> 8) & 255) as u32;
                    boot[12..16].copy_from_slice(&child_generation.to_le_bytes());
                    for j in 0..3 {
                        boot[36 + j * 32..40 + j * 32].copy_from_slice(
                            &(0x76000000 + ((j as u32) << 16) + child_generation).to_le_bytes(),
                        );
                    }
                }
                exec_streams::replace_record(
                    factory,
                    image,
                    clients[1],
                    &mut boot,
                    &mut holders,
                    &buffers[who],
                    #[cfg(shell_files)]
                    files,
                    #[cfg(shell_files)]
                    file_references[1],
                );
                #[cfg(shell_null)]
                {
                    check(null.active(), 2312);
                    null_bootstrap(clients[1], &null, true);
                }
                executed = true;
            } else {
                let mut b = [0; 32];
                b.copy_from_slice(&buffers[who][..32]);
                let mut name = [0; 32];
                if cfg!(shell_argv) {
                    name[..14].copy_from_slice(b"/inputs/helper");
                } else {
                    name[..5].copy_from_slice(b"/next");
                }
                let mut denied_name = [0; 32];
                denied_name[..7].copy_from_slice(b"/denied");
                #[cfg(shell_failed_exec)]
                if who == 1 && !denied_exec {
                    let path: &[u8] = if admissions == 1 {
                        b"/inputs/missing"
                    } else {
                        b"/inputs/not-executable"
                    };
                    let mut expected = [0; 32];
                    expected[..path.len()].copy_from_slice(path);
                    if b == expected {
                        needed[who] = 400;
                        continue;
                    }
                }
                if who == 1 && !executed && (b == name || (cfg!(shell_null) && b == denied_name)) {
                    needed[who] = 400;
                    continue;
                }
                let op = get(&b, 0);
                #[cfg(shell_files)]
                if op == 6 || ((1..=3).contains(&op) && get(&b, 8) >= 3) {
                    check(who == 0 || executed || cfg!(shell_files_denied), 2506);
                    #[cfg(shell_files_denied)]
                    check(
                        who == 1
                            && !denied_write
                            && !executed
                            && op == 6
                            && get(&b, 12) == 14
                            && b[16..] == *b"/inputs/denied\0\0",
                        2554,
                    );
                    let mut response = scratch_gateway(service, files, who, &b);
                    #[cfg(shell_files_denied)]
                    {
                        if cfg!(files_denied_errno) {
                            put(&mut response, 0, (-2i32) as u32);
                        }
                        check(
                            get(&response, 0) as i32 == -13
                                && response[4..] == [0; 28]
                                && files.closed()
                                && !files.poisoned(),
                            2554,
                        );
                        denied_write = true;
                    }
                    send(clients[who], &mut response);
                    used[who] = 0;
                    needed[who] = 32;
                    buffers[who].fill(0);
                    continue;
                }
                #[cfg(shell_null)]
                if op == 6 || ((1..=3).contains(&op) && get(&b, 8) == 3) {
                    let mut request = b;
                    if cfg!(null_bad_handle) && op == 6 {
                        put(&mut request, 4, null.factory());
                    }
                    let mut response = null.request(who == 1, &request);
                    if cfg!(null_bad_eof) && executed && op == 1 && response == [0; 32] {
                        put(&mut response, 0, 1);
                        response[16] = b'a';
                    }
                    if cfg!(null_bad_stale) && op == 1 && get(&response, 0) as i32 == -9 {
                        response.fill(0);
                    }
                    if cfg!(null_bad_limit)
                        && op == 6
                        && !null.active()
                        && get(&response, 0) as i32 == -23
                    {
                        response.fill(0);
                        put(&mut response, 4, null.reference());
                        put(&mut response, 8, 3);
                    }
                    send(clients[who], &mut response);
                    used[who] = 0;
                    needed[who] = 32;
                    buffers[who].fill(0);
                    continue;
                }
                #[cfg(shell_dash)]
                if op == 4 || op == 5 {
                    shell::directory_reply(clients[who], &b, generation);
                    used[who] = 0;
                    needed[who] = 32;
                    buffers[who].fill(0);
                    continue;
                }
                #[cfg(any(shell_repeat, shell_failed_exec))]
                if op == 64 && who == 0 {
                    check(
                        reaped
                            && collected
                            && dead[1]
                            && !issued
                            && !waiting
                            && !pending[1]
                            && used[1] == 0
                            && holders == [[true; 3], [false; 3]]
                            && admissions < if cfg!(shell_failed_exec) { 2 } else { 3 }
                            && closes == 0,
                        2153,
                    );
                    admissions += 1;
                    clients[1] = admit(clients[0], factory, b, admissions);
                    holders[1] = [true; 3];
                    dead[1] = false;
                    reaped = false;
                    collected = false;
                    executed = false;
                    denied_exec = false;
                    child_status = 0;
                    pid = admissions * 4 + 3;
                    used[who] = 0;
                    needed[who] = 32;
                    buffers[who].fill(0);
                    continue;
                }
                if op == 80 || op == 81 {
                    let selector = get(&b, 4) as i32;
                    let options = get(&b, 8);
                    if who != 0 || (selector != pid as i32 && !(op == 80 && selector == -1)) {
                        reply(clients[who], -10);
                    } else if options > 1 || (op == 81 && options != 0) || b[12..] != [0; 20] {
                        reply(clients[who], -22);
                    } else if op == 81 {
                        if issued && !collected {
                            if cfg!(shell_repeat) || cfg!(shell_failed_exec) {
                                check(
                                    dead[1]
                                        && (executed || (cfg!(shell_failed_exec) && denied_exec))
                                        && !pending[1]
                                        && used[1] == 0
                                        && holders[1] == [false; 3]
                                        && !reaped,
                                    2153,
                                );
                                if !cfg!(failed_keep_child) {
                                    dispose(clients[1]);
                                }
                                check(ctl(0x20001, clients[1].child).0 == -9, 2153);
                                reaped = true;
                            }
                            collected = true;
                            issued = false;
                            reply(clients[who], 0);
                        } else {
                            reply(clients[who], -22);
                        }
                    } else if collected {
                        reply(clients[who], -10);
                    } else if dead[1] || cfg!(dispatch_early) {
                        status_reply(
                            clients[who],
                            pid,
                            if cfg!(dispatch_early) {
                                72 << 8
                            } else {
                                child_status
                            },
                        );
                        issued = true;
                    } else if options == 1 {
                        reply(clients[who], 0);
                    } else {
                        waiting = true;
                        deferred += 1;
                    }
                } else if who == 1
                    && !executed
                    && !(cfg!(shell_failed_exec) && denied_exec)
                    && !cfg!(shell_files_denied)
                {
                    reply(clients[who], -13);
                } else {
                    #[cfg(shell_files_denied)]
                    check(who == 0 || denied_write, 2555);
                    let completed = file_request(
                        clients[who],
                        who,
                        if who == 1 {
                            ((clients[1].child >> 8) & 255) as u32
                        } else {
                            generation
                        },
                        &mut b,
                        service,
                        &handles,
                        &mut holders,
                        &mut positions,
                        &mut closes,
                    );
                    if !completed {
                        pending[who] = true;
                        continue;
                    }
                    if who == 1 && pending[0] && op == 2 {
                        peer_progress = true;
                    }
                }
            }
            used[who] = 0;
            needed[who] = 32;
            buffers[who].fill(0);
        }
        ctl(0x1fffe, 0);
    }
    end(2132)
}

// A private immutable namespace object, intentionally carrying no image grant.
// Presence is owned here; a path string never grants execution authority.
#[cfg(shell_failed_exec)]
const NON_EXECUTABLE: (&[u8], Option<u64>) = (b"Aether non-executable fixture\n", None);
#[cfg(shell_failed_exec)]
fn failed_exec(child: Connection, record: &[u8; 400], admission: u32) {
    let path: &[u8] = if admission == 1 {
        b"/inputs/missing"
    } else {
        b"/inputs/not-executable"
    };
    let mut name = [0; 32];
    name[..path.len()].copy_from_slice(path);
    check(record[..32] == name, 2340);
    // Environment order is not part of the consumer contract; exact entries are.
    let mut expected = [0; 144];
    expected[..8].copy_from_slice(&1u64.to_le_bytes());
    expected[8..16].copy_from_slice(&4u64.to_le_bytes());
    expected[16..16 + path.len()].copy_from_slice(path);
    check(record[32..176] == expected, 2342);
    let mut seen = [false; 4];
    for entry in record[176..304].chunks_exact(32) {
        let values: [&[u8]; 4] = [
            b"PWD=/work",
            b"WITNESS=value",
            b"LC_ALL=C",
            b"PATH=/nonexistent",
        ];
        let index = values
            .iter()
            .position(|value| {
                entry[..value.len()] == **value
                    && entry[value.len()..].iter().all(|byte| *byte == 0)
            })
            .unwrap_or_else(|| end(2342));
        check(!seen[index], 2342);
        seen[index] = true;
    }
    check(seen == [true; 4], 2342);
    let mut mask = [0; 32];
    mask[..8].copy_from_slice(b"AEEMSK01");
    check(record[304..336] == mask, 2343);
    let mut table = [0; 64];
    table[..12].copy_from_slice(&[0, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0]);
    table[40..44].copy_from_slice(&[0, 1, 1, 0]);
    check(record[336..] == table, 2344);
    for _ in 0..10000 {
        if ctl(0x23004, child.child).0 == 1 {
            break;
        }
        ctl(0x1fffe, 0);
    }
    check(ctl(0x23004, child.child).0 == 1, 2340);
    let before = call(0x23008, 0xa001, child.child, 0, 0, 0, 0);
    check(before == (0, 0, 0), 2340);
    let object = if admission == 1 {
        None
    } else {
        Some(NON_EXECUTABLE)
    };
    let error = match object {
        None => -2,
        Some((bytes, image)) => {
            check(!bytes.is_empty() && image.is_none(), 2340);
            -13
        }
    };
    check(
        call(0x23008, 0xa001, child.child, 0, 0, 0, 0) == before,
        2340,
    );
    check(call(0x23005, child.child, 1, 0, 0, 0, 0).0 == 0, 2340);
    let error = if cfg!(failed_missing_denied) && admission == 1 {
        -13
    } else if cfg!(failed_denied_missing) && admission == 2 {
        -2
    } else {
        error
    };
    reply(child, error);
}
