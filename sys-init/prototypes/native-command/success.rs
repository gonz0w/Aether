// SPDX-License-Identifier: BSD-2-Clause
// Bounded AERIO001/opt-in AERIO002 witness; policy stays in this owner.
use super::*;
#[path = "lifecycle.rs"]
mod lifecycle;
#[cfg(init_service_table)]
#[path = "service_table.rs"]
mod service_table;
use lifecycle::{connection_owner::Connection as Owned, connection_owner::Role, service_owner::Identity, service_owner::Error, Native};
fn carrier(parent: Connection, generation: u32) {
    let mut b = [0; 32];
    b[..8].copy_from_slice(if cfg!(init_sustained_v2) { b"AERIO002" } else { b"AERIO001" });
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
fn parent_ref(j: usize, generation: u32) -> u32 {
    if j < 2 {
        0x75000000 + ((j as u32 + 1) << 16) + generation
    } else {
        reference(0, j - 2, generation)
    }
}
fn receipt(generation: u32) -> u32 {
    (if cfg!(init_sustained_v2) { 0x7b000000 } else { 0x73000000 }) | generation
}
#[cfg(init_sustained)]
#[path = "sustained_owner.rs"]
mod sustained;
#[cfg(ownership_probe)]
#[path = "ownership_probe.rs"]
mod ownership_probe;
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    #[cfg(ownership_probe)]
    ownership_probe::run(factory, first, second, third);
    #[cfg(all(init_sustained, not(init_service_table)))]
    sustained::begin();
    let attempts = if cfg!(init_sustained) { 65535 } else { 2 };
    let mut backend_id = Identity::new();
    let mut runner_id = Identity::new();
    let mut command_id = Identity::new();
    #[cfg(init_service_table)]
    let roles = service_table::SERVICES.map(|service| service.role);
    #[cfg(not(init_service_table))]
    let roles = [Role::Backend, Role::Runner, Role::Command];
    let mut backend_owner = Owned::new(&mut backend_id, roles[0], attempts);
    let mut owners = [Owned::new(&mut runner_id, roles[1], attempts), Owned::new(&mut command_id, roles[2], attempts)];
    let mut native = Native { factory, images: [first, second, third], startup: args(b"worker") };
    #[cfg(init_supervised)]
    let mut retrying = false;
    #[cfg(init_supervised)]
    let mut remaining = service_table::SERVICES[2].retries;
    for generation in 1..=(attempts as u32 + if cfg!(init_sustained) { 1 } else { 0 }) {
        #[cfg(init_sustained)]
        {
            #[cfg(init_supervised)]
            let requested = !retrying;
            #[cfg(not(init_supervised))]
            let requested = true;
            if requested {
                if sustained::input(b"SI07 request-ready\n") == b'h' { sustained::halt(); }
                #[cfg(init_supervised)]
                { remaining = service_table::SERVICES[2].retries; }
            }
        }
        #[cfg(init_sustained_exhausted)]
        let generation = 65536;
        #[cfg(init_sustained_v2)]
        if !(1..=65535).contains(&generation) {
            sustained::write(b"SI07 epoch exhausted before admission\n");
            end(2806)
        }
        native.startup = args(b"worker");
        backend_owner.start(&mut native).unwrap_or_else(|_| end(1400));
        #[cfg(init_sustained_v2)]
        sustained::cohort(&mut backend_owner, &mut owners, &mut native, generation);
        let service = lifecycle::borrowed(&backend_owner);
        let mut hello = [0; 32];
        check(transfer(service.reader, &mut hello, false) == 1, 1400);
        let handles = [0xf201, 0xf202, 0xf101, 0xf203];
        check(
            (0..4).all(|j| get(&hello, 4 + j * 4) == [0xf101, 0xf201, 0xf202, 0xf203][j]),
            1400,
        );
        native.startup = args(b"client");
        owners[0].start(&mut native).unwrap_or_else(|_| end(1400));
        #[cfg(init_sustained_v2)]
        sustained::cohort(&mut backend_owner, &mut owners, &mut native, generation);
        let parent = lifecycle::borrowed(&owners[0]);
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
        #[cfg(init_supervised)]
        let mut command_dispatched = false;
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
                if let Some(terminal) = owners[i].observe(&mut native, &owners[i].key())
                    .unwrap_or_else(|_| end(1401)) {
                    let actual = (terminal.detail as u32, terminal.kind as u32);
                    if i == 0 {
                        let mapped = if terminal_result.1 == 1 && terminal_result.0 <= 255 {
                            terminal_result.0
                        } else {
                            1
                        };
                        check(actual == (mapped, 1), 1401);
                    } else {
                        #[cfg(not(init_supervised))]
                        let expected = if cfg!(success_stop) {
                            (143, 3)
                        } else if cfg!(success_fault) {
                            (134, 2)
                        } else if cfg!(success_nonzero) {
                            (134, 1)
                        } else if cfg!(success_wide) {
                            (64, 1)
                        } else {
                            (0, 1)
                        };
                        #[cfg(not(init_supervised))]
                        check(actual == expected, 1407);
                        #[cfg(init_supervised)]
                        check((actual.1 == 1 && actual.0 <= 255)
                            || actual == (134, 2) || actual == (143, 3), 1407);
                        #[cfg(supervised_stop_after_read)]
                        {
                            check(actual == (143, 3), 1407);
                            sustained::write(b"SI07 stopped command terminal143 verified\n");
                        }
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
                        && (cfg!(success_stop) || cfg!(success_fault) || cfg!(success_nonzero) || cfg!(success_wide)
                            || (cfg!(init_supervised) && terminal_result != (0, 1)))
                    {
                        #[cfg(not(init_supervised))]
                        check(live[i] == [false, false, true, true], 1403);
                        #[cfg(init_supervised)]
                        check(!live[i][0] && !live[i][1], 1403);
                        if cfg!(success_stop) && cfg!(success_skip_retire) {
                            live[i] = core::hint::black_box(live[i]);
                        } else if !cfg!(success_skip_retire) {
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
                // Dispatch only complete frames; the next frame overwrites its
                // entire 32/384-byte extent before inspection or dispatch.
                let request = &frames[i];
                used[i] = 0;
                let op = word(request, 0);
                // Stop only after consuming a complete first command read, before
                // dispatching any backend effect or sending a reply. The command
                // cannot issue another request while this reply is outstanding.
                #[cfg(success_stop)]
                if i == 1 {
                    let mut expected = [0; 32];
                    put(&mut expected, 0, 1);
                    put(&mut expected, 4, reference(1, 0, generation));
                    put(&mut expected, 12, 16);
                    check(request[..32] == expected && positions == [0; 4], 1408);
                    owners[1].request_stop(&mut native, &owners[1].key())
                        .unwrap_or_else(|_| end(1408));
                    continue;
                }
                // Private native control: stop after a completed read, before write.
                #[cfg(supervised_stop_after_read)]
                if i == 1 && op == 2 {
                    check(command_dispatched && positions[2] == 6 && positions[3] == 0, 1408);
                    owners[1].request_stop(&mut native, &owners[1].key())
                        .unwrap_or_else(|_| end(1408));
                    continue;
                }
                let mut reply = [0; 32];
                let result: i32;
                if op == 4 {
                    check(i == 0 && !admitted && live[0] == [true; 4], 1404);
                    let args = validate(request, generation, [live[0][2], live[0][3]])
                        .unwrap_or_else(|_| end(1404));
                    #[cfg(any(supervised_bad_once, supervised_bad_always))]
                    let args = {
                        let mut bad = args;
                        if cfg!(supervised_bad_always) || generation == 1 {
                            bad.strings[1] = [0; 32];
                            bad.strings[1][..6].copy_from_slice(b"--fail");
                        }
                        bad
                    };
                    native.startup = args;
                    owners[1].start(&mut native).unwrap_or_else(|_| end(1404));
                    #[cfg(init_sustained_v2)]
                    sustained::cohort(&mut backend_owner, &mut owners, &mut native, generation);
                    clients[1] = lifecycle::borrowed(&owners[1]);
                    live[1] = [false, false, true, true];
                    admitted = true;
                    result = 0;
                    put(&mut reply, 4, receipt(generation));
                } else if op == 5 {
                    check(
                        i == 0
                            && admitted
                            && word(request, 4) == receipt(generation)
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
                            && word(request, 4)
                                == if i == 0 {
                                    parent_ref(*j, generation)
                                } else {
                                    reference(1, *j - 2, generation)
                                }
                            && word(request, 8)
                                == if i == 0 { *j as u32 + 1 } else { *j as u32 - 2 }
                    });
                    if let Some(j) = j {
                        let count = word(request, 12);
                        if op == 3 && count == 0 && request[16..32].iter().all(|v| *v == 0) {
                            live[i][j] = false;
                            result = 0;
                            if i == 0 && j == 2 {
                                check(admitted && !started && live[1][2], 1404);
                                #[cfg(init_supervised)]
                                let live_command = owners[1].observe(&mut native, &owners[1].key())
                                    .unwrap_or_else(|_| end(1404)).is_none();
                                #[cfg(not(init_supervised))]
                                let live_command = true;
                                // A known early terminal receives no bootstrap publication.
                                if live_command { bootstrap(clients[1], 1, generation); }
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
                                #[cfg(init_supervised)]
                                if i == 1 { command_dispatched = true; }
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
        #[cfg(init_supervised)]
        let command_failed = terminal_result != (0, 1);
        #[cfg(init_supervised)]
        check(exited == [true; 2] && positions[0..2] == [0; 2]
            && positions[2] <= 6 && positions[3] <= 2
            && (command_failed || positions[2..4] == [6, 2]), 1405);
        #[cfg(not(init_supervised))]
        check(
            exited == [true; 2]
                && positions
                    == [
                        0,
                        0,
                        if cfg!(success_stop) || cfg!(init_command_empty) || cfg!(init_command_fault) {
                            0
                        } else {
                            6
                        },
                        if cfg!(success_stop) || cfg!(init_command_fault) { 0 } else { 2 },
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
                    #[cfg(init_supervised)]
                    if command_failed { &b"6\n"[..positions[3] as usize] }
                    else { b"6\n" }
                    #[cfg(not(init_supervised))]
                    if cfg!(success_stop) || cfg!(init_command_fault) {
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
        #[cfg(supervised_unknown_cleanup)]
        {
            check(ctl(0x24003, clients[1].reader).0 == 0, 1406);
            let key = owners[1].key();
            let error = owners[1].cleanup(&mut native, &key).unwrap_err();
            check(matches!(error, Error::Backend(lifecycle::service_owner::Fault::Unknown(e))
                if e.operation == 0x24003 && e.value == -13), 1406);
            check(owners[1].resources().2 && owners[1].resources().0.iter().any(|v| *v), 1406);
            check(matches!(owners[1].cleanup(&mut native, &key), Err(Error::Closed)), 1406);
            sustained::write(b"SYSINIT-CLEANUP-UNKNOWN retained ownership; replay denied\n");
            end(1406)
        }
        for owner in &mut owners {
            owner.cleanup(&mut native, &owner.key()).unwrap_or_else(|_| end(1406));
        }
        backend_owner.backend_eof(&mut native, &backend_owner.key()).unwrap_or_else(|_| end(1406));
        let mut complete = false;
        for _ in 0..100000 {
            match backend_owner.cleanup(&mut native, &backend_owner.key()) {
                Ok(()) => { complete = true; break; }
                Err(Error::Busy) => { ctl(0x1fffe, 0); }
                _ => end(1406),
            }
        }
        check(complete, 1406);
        let terminal = backend_owner.observe(&mut native, &backend_owner.key()).unwrap_or_else(|_| end(1406)).unwrap_or_else(|| end(1406));
        check(terminal.detail == 17 && terminal.kind == 1, 1406);
        #[cfg(init_sustained)]
        {
            for c in clients { check(ctl(0x20001, c.child).0 == -9 && ctl(0x24003, c.reader).0 == -13, 2805); }
            #[cfg(init_supervised)]
            {
                for owner in [&backend_owner, &owners[0], &owners[1]] {
                    check(owner.resources() == ([false; 2], [false; 2], false), 1406);
                }
                check(ctl(0x20001, service.child).0 == -9, 1406);
                if command_failed {
                    if command_dispatched {
                        sustained::failed(b"SYSINIT-RETRY-BLOCKED command failed after I/O\n");
                    }
                    if remaining == 0 {
                        sustained::failed(b"SYSINIT-RETRY-EXHAUSTED command attempts exhausted\n");
                    }
                    remaining -= 1;
                    retrying = true;
                    sustained::write(b"SYSINIT-RETRY command failed before I/O; cleanup complete\n");
                    continue;
                }
                retrying = false;
            }
            sustained::write(b"SI07 command-complete\n");
        }
    }
    #[cfg(init_sustained)]
    end(2806);
    #[cfg(not(init_sustained))]
    end(100)
}
