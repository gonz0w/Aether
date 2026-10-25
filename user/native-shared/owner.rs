// SPDX-License-Identifier: BSD-2-Clause
// Fixed bootstrap delegation oracle; user-space state, no new kernel ABI.
use super::*;
fn backend_op(
    c: Connection,
    op: u32,
    handle: u32,
    offset: u32,
    length: u32,
    data: &[u8],
) -> [u8; 32] {
    let mut m = [0; 32];
    put(&mut m, 0, op);
    put(&mut m, 4, handle);
    put(&mut m, 8, offset);
    put(&mut m, 12, length);
    m[16..16 + data.len()].copy_from_slice(data);
    rpc(c, &mut m);
    m
}
fn release(backend: Connection, handle: u32, live: &mut [bool; 2], i: usize) {
    live[i] = false;
    if (!live[0] && !live[1]) || cfg!(early_close) {
        if cfg!(file_io) {
            for offset in (0..64).step_by(16) {
                let data = backend_op(backend, 2, handle, offset, 16, &[]);
                check(get(&data, 0) == 16, 985);
                for j in 0..16 {
                    let n = offset as usize + j;
                    check(data[16 + j] == if n < 6 { b"abcdef"[n] } else { b'X' }, 985);
                }
            }
        }
        if !cfg!(leak_close) {
            check(get(&backend_op(backend, 3, handle, 0, 0, &[]), 0) == 0, 973);
        }
    }
}
fn admit(factory: u64, image: u64, reject: bool) -> Result<Connection, i32> {
    let req = ctl(0x24000, 0xd001);
    if req.0 < 0 {
        return Err(req.0 as i32);
    }
    let rep = ctl(0x24000, 0xd001);
    if rep.0 < 0 {
        if !cfg!(leak_reservation) {
            check(
                ctl(0x24003, req.0 as u64).0 == 0 && ctl(0x24003, req.1).0 == 0,
                980,
            );
        }
        return Err(rep.0 as i32);
    }
    let mut startup = args(b"client");
    if reject {
        startup.argc = 5;
    }
    let h = call(
        0x23002,
        factory,
        image,
        2,
        &startup as *const Args as u64,
        req.0 as u64,
        rep.1,
    )
    .0;
    if h < 0 {
        // Failed native admission retains both endpoints, no alias was published.
        for cap in [req.0 as u64, req.1, rep.0 as u64, rep.1] {
            if !cfg!(leak_admission) {
                check(ctl(0x24003, cap).0 == 0, 980);
            }
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
fn bootstrap(c: Connection, reference: u32, index: usize) {
    let mut boot = [0; 32];
    put(&mut boot, 4, reference);
    put(&mut boot, 8, if index == 0 { 3 } else { 10 });
    put(&mut boot, 12, if index == 0 { 3 } else { 1 });
    check(transfer(c.writer, &mut boot, true) == 1, 971);
}
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    for generation in 1..=2 {
        let backend = launch(factory, second, 1);
        let mut hello = [0; 32];
        check(
            transfer(backend.reader, &mut hello, false) == 1 && get(&hello, 8) == 0xf002,
            971,
        );
        let created = backend_op(backend, 5, 0xf002, 0, 3, b"scratch");
        check(get(&created, 0) == 0, 971);
        let handle = get(&created, 4);
        check(
            get(&backend_op(backend, 4, handle, 0, 6, b"abcdef"), 0) == 6,
            971,
        );
        let parent = launch(factory, first, 0);
        let mut clients = [parent, parent];
        let refs = [0x61000000 | generation, 0x62000000 | generation];
        bootstrap(parent, refs[0], 0);
        let mut admitted = !cfg!(requested);
        if admitted {
            clients[1] = launch(factory, third, 2);
            bootstrap(clients[1], refs[1], 1);
        }
        let mut attempts = 0;
        let mut collected = false;
        let mut child_terminal = (0u32, 0u32);
        let mut live = [true, admitted];
        let mut exited = [false; 2];
        let mut position = 0u32;
        let mut frames = [[0u8; 32]; 2];
        let mut used = [0usize; 2];
        for _ in 0..100000 {
            for i in 0..2 {
                if exited[i] || (i == 1 && !admitted) {
                    continue;
                }
                let status = ctl(0x20001, clients[i].child);
                if status.0 != 0 {
                    check(status.0 == 30 && status.2 == 1, 970);
                    if live[i] {
                        release(backend, handle, &mut live, i);
                    }
                    if i == 1 {
                        child_terminal = ((status.0 - 1) as u32, status.2 as u32);
                    }
                    exited[i] = true;
                    continue;
                }
                let n = call(
                    0x24001,
                    clients[i].reader,
                    frames[i][used[i]..].as_mut_ptr() as u64,
                    (32 - used[i]) as u64,
                    0,
                    0,
                    0,
                )
                .0;
                if n == -11 || n == 0 {
                    continue;
                }
                check(n > 0 && n as usize <= 32 - used[i], 972);
                used[i] += n as usize;
                if used[i] != 32 {
                    continue;
                }
                let request = frames[i];
                used[i] = 0;
                frames[i] = [0; 32];
                let op = get(&request, 0);
                let mut reply = [0; 32];
                let result: i32;
                if cfg!(requested) && op == 5 {
                    if i != 0 {
                        result = -13;
                    } else if get(&request, 4) != refs[0] || get(&request, 8) != 3 {
                        result = -9;
                    } else if get(&request, 12) != (0x53000000 | generation)
                        || !admitted
                        || collected
                    {
                        result = -10;
                    } else if request[16..].iter().any(|b| *b != 0) {
                        result = -22;
                    } else if !exited[1] {
                        result = -11;
                    } else {
                        put(&mut reply, 4, 0x53000000 | generation);
                        put(
                            &mut reply,
                            8,
                            if cfg!(wrong_status) {
                                child_terminal.0 ^ 1
                            } else {
                                child_terminal.0
                            },
                        );
                        put(&mut reply, 12, child_terminal.1);
                        if !cfg!(repeat_status) {
                            collected = true;
                        }
                        result = 0;
                    }
                } else if !live[i]
                    || get(&request, 4) != refs[i]
                    || get(&request, 8) != if i == 0 { 3 } else { 10 }
                {
                    result = -9;
                } else if cfg!(requested) && op == 4 {
                    if i != 0 {
                        result = -13;
                    } else if get(&request, 12) != 1
                        || get(&request, 16) != 10
                        || get(&request, 24) != 1
                        || get(&request, 28) != 0
                    {
                        result = -22;
                    } else if get(&request, 20) != 1 && !cfg!(allow_widen) {
                        result = -13;
                    } else if admitted {
                        result = -16;
                    } else {
                        attempts += 1;
                        let held = if (cfg!(partial_reservation) || cfg!(leak_reservation))
                            && generation == 1
                            && attempts == 1
                        {
                            let h = ctl(0x24000, 0xd001);
                            check(h.0 > 0, 980);
                            Some(h)
                        } else {
                            None
                        };
                        let outcome = admit(
                            factory,
                            third,
                            (cfg!(reject_launch) || cfg!(leak_admission))
                                && generation == 1
                                && attempts == 1,
                        );
                        if let Some(h) = held {
                            check(
                                ctl(0x24003, h.0 as u64).0 == 0 && ctl(0x24003, h.1).0 == 0,
                                980,
                            );
                        }
                        match outcome {
                            Err(e) => {
                                check(!live[1] && position == 2, 980);
                                result = e;
                            }
                            Ok(c) => {
                                // Commit the route and alias before servicing any child request.
                                clients[1] = c;
                                live[1] = true;
                                admitted = true;
                                bootstrap(c, refs[1], 1);
                                put(&mut reply, 4, 0x53000000 | generation);
                                result = 0;
                            }
                        }
                    }
                } else if cfg!(file_io) && op == 2 {
                    let count = get(&request, 12);
                    if i == 1 && !cfg!(wide_rights) {
                        result = -13;
                    } else if count > 16
                        || request[16 + count.min(16) as usize..]
                            .iter()
                            .any(|b| *b != 0)
                    {
                        result = -22;
                    } else {
                        if cfg!(skip_write) {
                            result = if position <= 64 && count <= 64 - position {
                                count as i32
                            } else {
                                -28
                            };
                        } else {
                            reply = backend_op(
                                backend,
                                4,
                                handle,
                                position,
                                count,
                                &request[16..16 + count as usize],
                            );
                            result = get(&reply, 0) as i32;
                        }
                        check(result <= count as i32, 984);
                        if result > 0 {
                            position += result as u32;
                        }
                    }
                } else if op == 2 {
                    result = if i == 1 && !cfg!(wide_rights) {
                        -13
                    } else {
                        -95
                    };
                } else if cfg!(file_io) && op == 1 {
                    let count = get(&request, 12);
                    if count > 16 || request[16..].iter().any(|b| *b != 0) {
                        result = -22;
                    } else {
                        reply = backend_op(backend, 2, handle, position, count, &[]);
                        result = get(&reply, 0) as i32;
                        check(result <= count as i32, 984);
                        if result > 0 && !cfg!(frozen_offset) {
                            position += result as u32;
                        }
                        if count == 0 && cfg!(zero_consumes) {
                            position += 1;
                        }
                    }
                } else if op == 1 && get(&request, 12) == 2 && request[16..].iter().all(|b| *b == 0)
                {
                    if (i == 1 && (position == 0 || (cfg!(parent_first) && !exited[0])))
                        || (i == 0 && position >= 2 && !exited[1])
                    {
                        result = -11;
                    } else {
                        reply = backend_op(backend, 2, handle, position, 2, &[]);
                        result = get(&reply, 0) as i32;
                        if result > 0 && !cfg!(frozen_offset) {
                            position += result as u32;
                        }
                    }
                } else if op == 3 && get(&request, 12) == 0 && request[16..].iter().all(|b| *b == 0)
                {
                    release(backend, handle, &mut live, i);
                    result = 0;
                } else {
                    result = -22;
                }
                put(&mut reply, 0, result as u32);
                check(transfer(clients[i].writer, &mut reply, true) == 1, 972);
            }
            if exited == [true, true] {
                break;
            }
            ctl(0x1fffe, 0);
        }
        check(
            admitted
                && exited == [true, true]
                && live == [false, false]
                && position == if cfg!(file_io) { 64 } else { 6 },
            974,
        );
        // Confirm that the last reference consumed the real backend handle.
        check(
            get(&backend_op(backend, 2, handle, 0, 1, &[]), 0) as i32 == -9,
            975,
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
            ctl(0x24003, backend.writer).0 == 0
                && terminal(backend.child) == (17, 1)
                && ctl(0x24003, backend.reader).0 == 0
                && ctl(0x20002, backend.child).0 == 0,
            976,
        );
    }
    end(100)
}
