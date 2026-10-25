// SPDX-License-Identifier: BSD-2-Clause
// Native two-process pipe probe; the exec dispatcher remains unchanged.
use super::*;
#[path = "pipe.rs"]
mod pipe;
use pipe::{Caller, Outcome, Pipe};
#[cfg(pipe_dash)]
#[path = "pipe-dash.rs"]
mod dash;

fn simple(c: Connection, value: i32) {
    let mut response = [0; 32];
    put(&mut response, 0, value as u32);
    send(c, &mut response);
}

#[cfg(pipe_signal)]
fn signal_probe(mut pipe: Pipe, source: Connection, service: Connection, handles: [u32; 3]) {
    let mut frame = [0; 32];
    let mut used = 0;
    let mut reader_closed = false;
    let mut empty_writes = 0;
    let mut broken_writes = 0;
    for _ in 0..100000 {
        let state = ctl(0x20001, source.child);
        if state.0 != 0 {
            check(
                state.0 == 14
                    && state.2 == 4
                    && used == 0
                    && reader_closed
                    && empty_writes == 1
                    && broken_writes == 6,
                2172,
            );
            let mut extra = [0; 1];
            check(
                call(
                    0x24001,
                    source.reader,
                    extra.as_mut_ptr() as u64,
                    1,
                    0,
                    0,
                    0,
                )
                .0 == 0
                    && pipe.confirmed_terminal(Caller::Parent).is_ok()
                    && pipe.retire_if_idle([false; 2]),
                2172,
            );
            for handle in handles {
                check(backend(service, 3, handle, 0) == [0; 32], 2172);
            }
            finish_backend(service);
            dispose(source);
            return;
        }
        let n = call(
            0x24001,
            source.reader,
            frame[used..].as_mut_ptr() as u64,
            (32 - used) as u64,
            0,
            0,
            0,
        )
        .0;
        if n == -11 || n == 0 {
            ctl(0x1fffe, 0);
            continue;
        }
        check(n > 0 && n as usize <= 32 - used, 2172);
        used += n as usize;
        if used != 32 {
            continue;
        }
        let Outcome::Reply(mut reply) = pipe.request(Caller::Parent, &frame) else {
            end(2172)
        };
        if get(&frame, 0) == 3 {
            check(
                !reader_closed && get(&frame, 8) == 3 && reply == [0; 32],
                2172,
            );
            reader_closed = true;
        } else {
            check(
                reader_closed && get(&frame, 0) == 2 && get(&frame, 8) == 4,
                2172,
            );
            if get(&frame, 12) == 0 {
                check(reply == [0; 32] && empty_writes == 0, 2172);
                empty_writes += 1;
            } else {
                check(
                    get(&frame, 12) == 1
                        && frame[16] == 0x5a
                        && get(&reply, 0) as i32 == -32
                        && reply[4..] == [0; 28],
                    2172,
                );
                broken_writes += 1;
                check(broken_writes <= 6, 2172);
            }
        }
        send(source, &mut reply);
        used = 0;
        frame = [0; 32];
    }
    end(2172)
}

pub fn run(
    source: Connection,
    service: Connection,
    factory: u64,
    generation: u32,
    handles: [u32; 3],
) {
    let mut pipe = Pipe::new();
    let mut grant = [0; 32];
    grant[..8].copy_from_slice(b"AEPIPE01");
    for (index, value) in [1, pipe::FACTORY, 256, 16, 1, 0].iter().enumerate() {
        put(&mut grant, 8 + index * 4, *value);
    }
    send(source, &mut grant);
    #[cfg(pipe_dash)]
    {
        dash::run(pipe, source, service, factory, generation, handles);
        return;
    }
    let request = receive(source);
    check(get(&request, 0) == 82, 2160);
    let Outcome::Reply(created) = pipe.request(Caller::Parent, &request) else {
        end(2160)
    };
    check(get(&created, 0) == 0 && get(&created, 4) == 1, 2160);
    let mut response = created;
    if cfg!(pipe_bad_reply) {
        response = [0; 32];
        put(&mut response, 0, 0x80000000);
    }
    let interrupted = cfg!(pipe_reply_lost) || cfg!(pipe_reply_one) || cfg!(pipe_reply_short);
    if interrupted {
        let length = if cfg!(pipe_reply_one) {
            1
        } else if cfg!(pipe_reply_short) {
            31
        } else {
            0
        };
        if length != 0 {
            send(source, &mut response[..length]);
        }
        check(ctl(0x24003, source.writer).0 == 0, 2168);
        // Transport closure alone does not release endpoint ownership.
        check(!pipe.retire_if_idle([false; 2]), 2168);
    } else {
        send(source, &mut response);
    }
    if cfg!(pipe_bad_reply) || interrupted {
        check(terminal(source.child) == (92, 1), 2168);
        // No retry or fork publication may be queued after the unknown reply.
        let mut extra = [0; 32];
        check(
            call(
                0x24001,
                source.reader,
                extra.as_mut_ptr() as u64,
                32,
                0,
                0,
                0,
            )
            .0 == 0,
            2168,
        );
        if !cfg!(pipe_reply_retain) {
            check(pipe.confirmed_terminal(Caller::Parent).is_ok(), 2168);
        }
        check(pipe.retire_if_idle([false; 2]), 2168);
        if cfg!(pipe_bad_reply) {
            end(2167); // Intentional malformed-reply fixture abort, not recovery.
        }
        for handle in handles {
            check(backend(service, 3, handle, 0) == [0; 32], 2168);
        }
        finish_backend(service);
        // Reply writer is already closed; never close that capability twice.
        check(
            ctl(0x24003, source.reader).0 == 0 && ctl(0x20002, source.child).0 == 0,
            2168,
        );
        return;
    }
    #[cfg(pipe_signal)]
    {
        signal_probe(pipe, source, service, handles);
        return;
    }
    let header = receive(source);
    check(
        get(&header, 0) == 64
            && get(&header, 4) == 2
            && get(&header, 8) == generation
            && get(&header, 12) == 16
            && header[16..] == [0; 16],
        2160,
    );
    let mut table = [0; 64];
    table[..32].copy_from_slice(&receive(source));
    table[32..].copy_from_slice(&receive(source));
    let mut expected = [0; 64];
    for (fd, binding, flags) in [
        (0, 0, 0),
        (1, 1, 0),
        (2, 2, 0),
        (4, 4, 0),
        (10, 0, 1),
        (11, 3, 0),
    ] {
        expected[fd * 4] = binding;
        expected[fd * 4 + 1] = flags;
        expected[fd * 4 + 2] = 1;
    }
    check(table == expected, 2160);
    let mut frozen = false;
    for _ in 0..10000 {
        let state = ctl(0x23004, source.child).0;
        if state == 1 {
            frozen = true;
            break;
        }
        check(state == 0, 2160);
        ctl(0x1fffe, 0);
    }
    check(frozen, 2160);
    check(pipe.stage_child(generation, [true; 2]).is_ok(), 2160);
    let req = ctl(0x24000, 0xd001);
    let rep = ctl(0x24000, 0xd001);
    check(req.0 > 0 && rep.0 > 0, 2160);
    let handle = call(0x23006, factory, source.child, 2, 1, req.0 as u64, rep.1).0;
    check(
        handle == (0xb0000000 | ((generation as u64) << 8) | 3) as i64,
        2160,
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
    send(child, &mut receipt);
    let ready = receive(child);
    check(get(&ready, 0) == 66 && ready[4..] == [0; 28], 2161);
    check(pipe.finish_child_copy(generation, true).is_ok(), 2161);
    let mut complete = [0; 32];
    put(&mut complete, 0, 67);
    send(source, &mut complete);
    send(child, &mut complete);

    let clients = [source, child];
    let callers = [Caller::Parent, Caller::Child(generation)];
    let mut frames = [[0; 32]; 2];
    let mut used = [0usize; 2];
    let mut dead = [false; 2];
    let mut holders = [[true; 3]; 2];
    let mut closes = 0;
    let mut written = 0;
    let mut read = 0;
    let mut blocked_write = false;
    let mut gate = false;
    let mut issued = false;
    let mut collected = false;
    let expected_bytes = if cfg!(pipe_fault) || cfg!(pipe_stop) {
        256
    } else {
        320
    };
    let mut stopped_pending = false;
    let mut child_status: u32 = 0;
    for _ in 0..100000 {
        for who in 0..2 {
            if dead[who] {
                continue;
            }
            let state = ctl(0x20001, clients[who].child);
            if state.0 != 0 {
                if who == 1 && cfg!(pipe_stop) {
                    check(stopped_pending && state.0 == 144 && state.2 == 3, 2171);
                    let mut expected = [0; 32];
                    put(&mut expected, 0, 2);
                    put(&mut expected, 4, get(&created, 12));
                    put(&mut expected, 8, 4);
                    put(&mut expected, 12, 16);
                    for i in 0..16 {
                        expected[16 + i] = i as u8;
                    }
                    let mut extra = [0; 1];
                    check(
                        used[who] == 32
                            && frames[who] == expected
                            && written == 256
                            && read == 0
                            && call(
                                0x24001,
                                clients[who].reader,
                                extra.as_mut_ptr() as u64,
                                1,
                                0,
                                0,
                                0,
                            )
                            .0 == 0,
                        2171,
                    );
                    if !cfg!(pipe_stop_keep_frame) {
                        frames[who] = [0; 32];
                        used[who] = 0;
                    }
                    // Private wait policy for this exact supervisor stop; this
                    // does not claim that a native SIGTERM was delivered.
                    child_status = 15;
                } else if who == 1 && cfg!(pipe_fault) {
                    check(state.0 == 135 && state.2 == 2, 2163);
                    // The terminal client cannot append; account for every queued
                    // byte before discarding its incomplete, unapplied request.
                    check(used[who] <= 17, 2170);
                    loop {
                        let n = call(
                            0x24001,
                            clients[who].reader,
                            frames[who][used[who]..].as_mut_ptr() as u64,
                            (32 - used[who]) as u64,
                            0,
                            0,
                            0,
                        )
                        .0;
                        if n == 0 {
                            break;
                        }
                        check(n > 0 && n as usize <= 17 - used[who], 2170);
                        used[who] += n as usize;
                    }
                    let mut expected = [0; 32];
                    put(&mut expected, 0, 2);
                    put(&mut expected, 4, get(&created, 12));
                    put(&mut expected, 8, 4);
                    put(&mut expected, 12, 16);
                    check(
                        used[who] == 17
                            && frames[who][..17] == expected[..17]
                            && written == 256
                            && read == 0,
                        2170,
                    );
                    if !cfg!(pipe_fault_keep_frame) {
                        frames[who] = [0; 32];
                        used[who] = 0;
                    }
                    child_status = if cfg!(pipe_fault_as_exit) {
                        134 << 8
                    } else {
                        wait_status(((state.0 - 1) as u32, state.2 as u32))
                    };
                } else {
                    check(state.0 == 1 && state.2 == 1 && used[who] == 0, 2163);
                }
                dead[who] = true;
                if !(who == 1 && cfg!(pipe_keep_writer)) {
                    check(pipe.confirmed_terminal(callers[who]).is_ok(), 2163);
                }
                for j in 0..3 {
                    if holders[who][j] {
                        holders[who][j] = false;
                        if !holders[1 - who][j] {
                            check(backend(service, 3, handles[j], 0) == [0; 32], 2163);
                            closes += 1;
                        }
                    }
                }
            }
        }
        if dead == [true; 2] {
            check(
                collected
                    && !issued
                    && written == expected_bytes
                    && read == expected_bytes
                    && gate
                    && (blocked_write || cfg!(pipe_fault))
                    && closes == 3
                    && holders == [[false; 3]; 2]
                    && pipe.retire_if_idle([used[0] != 0, used[1] != 0]),
                2166,
            );
            finish_backend(service);
            dispose(source);
            dispose(child);
            return;
        }
        for who in 0..2 {
            if dead[who] {
                continue;
            }
            if used[who] < 32 {
                let n = call(
                    0x24001,
                    clients[who].reader,
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
                check(n > 0 && n as usize <= 32 - used[who], 2162);
                used[who] += n as usize;
                if used[who] != 32 {
                    continue;
                }
            }
            let frame = &frames[who];
            let op = get(frame, 0);
            let binding = get(frame, 8) as usize;
            if op == 83 {
                check(who == 0 && !gate && frame[4..] == [0; 28], 2162);
                if if cfg!(pipe_fault) || cfg!(pipe_stop) {
                    !dead[1]
                } else {
                    !blocked_write
                } {
                    continue;
                }
                gate = true;
                simple(clients[who], 0);
            } else if op == 80 || op == 81 {
                check(
                    who == 0 && get(frame, 4) == generation * 4 + 3 && frame[8..] == [0; 24],
                    2162,
                );
                if op == 80 {
                    check(!collected && read == expected_bytes, 2162);
                    if !dead[1] {
                        continue;
                    }
                    let mut response = [0; 32];
                    put(&mut response, 0, generation * 4 + 3);
                    put(&mut response, 4, generation * 4 + 3);
                    send(source, &mut response);
                    send(source, &mut child_status.to_le_bytes());
                    issued = true;
                } else {
                    check(issued && dead[1] && !collected, 2162);
                    issued = false;
                    collected = true;
                    simple(source, 0);
                }
            } else if op == 3 && binding < 3 {
                let expected_ref = (if who == 0 { 0x76000000 } else { 0x77000000 })
                    + ((binding as u32) << 16)
                    + generation;
                check(
                    get(frame, 4) == expected_ref
                        && frame[12..] == [0; 20]
                        && holders[who][binding],
                    2162,
                );
                holders[who][binding] = false;
                if !holders[1 - who][binding] {
                    check(backend(service, 3, handles[binding], 0) == [0; 32], 2162);
                    closes += 1;
                }
                simple(clients[who], 0);
            } else {
                let outcome = if cfg!(pipe_early_eof) && who == 0 && op == 1 {
                    Outcome::Reply([0; 32])
                } else {
                    pipe.request(callers[who], frame)
                };
                match outcome {
                    Outcome::Pending => {
                        if who == 1 && op == 2 {
                            if !blocked_write {
                                check(written == 256 && read == 0, 2164);
                                blocked_write = true;
                                if cfg!(pipe_stop) {
                                    if !cfg!(pipe_stop_skip) {
                                        check(ctl(0x20007, child.child).0 == 0, 2171);
                                    }
                                    let terminal = ctl(0x20001, child.child);
                                    check(terminal.0 == 144 && terminal.2 == 3, 2171);
                                    stopped_pending = true;
                                }
                            }
                        }
                        // The probe's parent has closed its writer before any read.
                        // An empty read cannot remain pending after child terminal.
                        check(
                            !(who == 0 && op == 1 && dead[1] && read == expected_bytes),
                            2164,
                        );
                        continue;
                    }
                    Outcome::Reply(mut response) => {
                        let count = get(&response, 0) as i32;
                        if count > 0 && op == 2 {
                            written += count as usize;
                        }
                        if count > 0 && op == 1 {
                            read += count as usize;
                        }
                        check(written <= 320 && read <= written, 2164);
                        send(clients[who], &mut response);
                    }
                }
            }
            // Reply has completed. No retry of an applied read/write on failure.
            used[who] = 0;
            frames[who] = [0; 32];
        }
        ctl(0x1fffe, 0);
    }
    end(2169)
}
