// SPDX-License-Identifier: BSD-2-Clause
use super::*;
fn exec_request(source: Connection, path: &[u8], mask: &mut [u8; 32]) -> Args {
    let name = receive(source);
    let mut expected = [0; 32];
    expected[..path.len()].copy_from_slice(path);
    check(name == expected, 2111);
    let mut raw = [0; 272];
    // The wire record exceeds the channel's 256-byte request limit.
    for chunk in raw.chunks_mut(256) {
        check(
            transfer_bounded(source.reader, chunk, false, 100000) == 1,
            2112,
        );
    }
    if cfg!(exec_mask) {
        *mask = receive(source);
        let value = u64::from_le_bytes(mask[8..16].try_into().unwrap());
        check(
            &mask[..8] == b"AEEMSK01"
                && mask[16..] == [0; 16]
                && value & ((1 << 8) | (1 << 18)) == 0,
            2114,
        );
    }
    decode_args(&raw)
}
fn decode_args(raw: &[u8]) -> Args {
    let mut a = args(b"");
    a.argc = u64::from_le_bytes(raw[..8].try_into().unwrap());
    a.envc = u64::from_le_bytes(raw[8..16].try_into().unwrap());
    for (slot, bytes) in a.strings.iter_mut().zip(raw[16..].chunks_exact(32)) {
        slot.copy_from_slice(bytes);
    }
    a
}
fn parked(h: u64, sequence: i64) {
    for _ in 0..10000 {
        let value = ctl(0x23004, h).0;
        if value == sequence {
            return;
        }
        check(value == 0, 2040);
        ctl(0x1fffe, 0);
    }
    end(2040)
}
// Timeout is not stop. Observe every terminal before discarding queued bytes.
fn contain(source: Connection, service: Connection, peer: Connection) {
    for (index, connection) in [source, service, peer].iter().enumerate() {
        if !(cfg!(exec_close_skip_stop) && index == 0) {
            check(ctl(0x20007, connection.child).0 == 0, 2051);
        }
        let state = ctl(0x20001, connection.child);
        check(state.0 == 144 && state.2 == 3, 2051);
    }
    for connection in [source, service, peer] {
        dispose(connection);
    }
}
fn rejected_bootstrap(
    source: Connection,
    service: Connection,
    peer: Connection,
    writer_closed: bool,
    status: u32,
) {
    check(bounded_record(source, false) == Err(0), 2070);
    check(terminal(source.child) == (status, 1), 2071);
    for (index, connection) in [service, peer].iter().enumerate() {
        if !(cfg!(exec_reject_skip_stop) && index == 0) {
            check(ctl(0x20007, connection.child).0 == 0, 2072);
        }
        let state = ctl(0x20001, connection.child);
        check(state.0 == 144 && state.2 == 3, 2072);
    }
    if writer_closed {
        check(
            ctl(0x24003, source.reader).0 == 0 && ctl(0x20002, source.child).0 == 0,
            2073,
        );
    } else {
        dispose(source);
    }
    dispose(service);
    dispose(peer);
}
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    for generation in 1u32..=2 {
        let source = launch(factory, first, 0);
        let service = launch(factory, second, 1);
        let peer = launch(factory, if cfg!(exec_shared) { third } else { second }, 2);
        let mut holders = [[true; 3]; 2];
        let mut closes = 0;
        let hello = receive(service);
        let handles = [get(&hello, 4), get(&hello, 8), get(&hello, 12)];
        check(
            get(&hello, 0) == 0 && hello[16..] == [0; 16] && handles == [0xf101, 0xf201, 0xf202],
            2040,
        );
        let mut boot = [0u8; 128];
        boot[..8].copy_from_slice(b"AECAT001");
        boot[8..12].copy_from_slice(&3u32.to_le_bytes());
        boot[12..16].copy_from_slice(&generation.to_le_bytes());
        for j in 0..3 {
            for (k, v) in [
                j as u32 + 1,
                0x76000000 + ((j as u32) << 16) + generation,
                j as u32,
                if j == 0 { 1 } else { 2 },
                if j == 2 { 256 } else { 32 },
            ]
            .iter()
            .enumerate()
            {
                let at = 32 + j * 32 + k * 4;
                boot[at..at + 4].copy_from_slice(&v.to_le_bytes());
            }
        }
        if cfg!(exec_shared) {
            send(peer, &mut boot);
        }
        send(source, &mut boot);
        let mut pos = 0;
        read(source, 0, generation, service, handles[0], &mut pos, b'a');
        let mut mask = [0; 32];
        let mut a = if cfg!(exec_public) {
            exec_request(source, b"/denied", &mut mask)
        } else {
            args(b"exec-stream")
        };
        let mut table = [0; 64];
        table[..32].copy_from_slice(&receive(source));
        table[32..].copy_from_slice(&receive(source));
        let mut expected = [0; 64];
        expected[..12].copy_from_slice(&[0, 0, 1, 0, 1, 1, 1, 0, 2, 0, 1, 0]);
        expected[40..44].copy_from_slice(&[0, 1, 1, 0]);
        check(table == expected, 2040);
        parked(source.child, 1);
        let mut plan = crate::exec_fds::prepare(&table, &[2, 1, 1]).unwrap_or_else(|_| end(2040));
        let ptr = &a as *const Args as u64;
        check(
            call(0x23007, factory, source.child, 0xffff, 1, ptr, 0).0 == -13,
            2040,
        );
        check(call(0x23005, source.child, 1, 0, 0, 0, 0).0 == 0, 2040);
        if cfg!(exec_public) {
            let mut reply = [0; 32];
            put(&mut reply, 0, (-13i32) as u32);
            send(source, &mut reply);
        }
        read(source, 0, generation, service, handles[0], &mut pos, b'b');
        if cfg!(exec_public) {
            let before = mask;
            a = exec_request(source, b"/next", &mut mask);
            check(mask == before, 2114);
            let mut again = [0; 64];
            again[..32].copy_from_slice(&receive(source));
            again[32..].copy_from_slice(&receive(source));
            check(again == table, 2113);
        }
        let ptr = &a as *const Args as u64;
        parked(source.child, 2);
        check(
            call(0x23007, factory, source.child, third, 2, ptr, 0).0 == 0,
            2040,
        );
        check(
            call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 1),
            2040,
        );
        check(plan.release == [false, true, false], 2040);
        if cfg!(exec_close_incomplete) {
            let mut close = [0; 32];
            put(&mut close, 0, 3);
            put(&mut close, 4, handles[1]);
            send(service, &mut close);
            let observed = bounded_record(service, cfg!(exec_close_pad));
            check(
                observed == Err(if cfg!(exec_close_partial) { 17 } else { 0 }),
                2050,
            );
            check(
                call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 1)
                    && ctl(0x23004, source.child).0 == 2,
                2050,
            );
            contain(source, service, peer);
            continue;
        }
        for j in 0..3 {
            if plan.release[j] {
                holders[0][j] = false;
                if !cfg!(exec_shared) || !holders[1][j] || cfg!(exec_shared_early_close) {
                    check(backend(service, 3, handles[j], 0) == [0; 32], 2040);
                    closes += 1;
                }
            }
        }
        if cfg!(exec_peer_first) {
            let mut barrier = [0; 32];
            put(&mut barrier, 0, 91);
            send(peer, &mut barrier);
            if cfg!(exec_peer_incomplete) {
                check(
                    holders == [[true, false, true], [true; 3]] && closes == 0,
                    2100,
                );
                if cfg!(exec_peer_fault) {
                    check(terminal(peer.child) == (134, 2), 2100);
                    check(bounded_record(peer, false) == Err(0), 2100);
                } else {
                    request(peer, 1, generation, 3, 0);
                    send(peer, &mut [0; 32]);
                    request(peer, 1, generation, 3, 1);
                }
                let mut close = [0; 32];
                put(&mut close, 0, 3);
                put(&mut close, 4, handles[1]);
                send(service, &mut close);
                check(
                    bounded_record(service, cfg!(exec_peer_pad))
                        == Err(if cfg!(exec_peer_partial) { 17 } else { 0 }),
                    2100,
                );
                check(
                    call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 1)
                        && ctl(0x23004, source.child).0 == 2,
                    2100,
                );
                if !cfg!(exec_peer_fault) {
                    check(ctl(0x20001, peer.child).0 == 0, 2100);
                }
                for (index, connection) in [source, service, peer].iter().enumerate() {
                    if index == 2 && cfg!(exec_peer_fault) {
                        check(terminal(peer.child) == (134, 2), 2101);
                    } else {
                        if !(index == 1 && cfg!(exec_peer_skip_stop)) {
                            check(ctl(0x20007, connection.child).0 == 0, 2101);
                        }
                        let state = ctl(0x20001, connection.child);
                        check(state.0 == 144 && state.2 == 3, 2101);
                    }
                }
                for connection in [source, service, peer] {
                    dispose(connection);
                }
                continue;
            }
            if cfg!(exec_peer_fault) {
                check(terminal(peer.child) == (134, 2), 2090);
                check(bounded_record(peer, false) == Err(0), 2090);
                if !cfg!(exec_peer_leak) {
                    for j in 0..3 {
                        check(holders[1][j], 2090);
                        holders[1][j] = false;
                        if !holders[0][j] || cfg!(exec_peer_close_live) {
                            check(backend(service, 3, handles[j], 0) == [0; 32], 2090);
                            closes += 1;
                        }
                    }
                }
            } else {
                release(
                    peer,
                    1,
                    generation,
                    service,
                    &handles,
                    &mut holders,
                    &mut closes,
                );
                check(terminal(peer.child) == (64, 1), 2090);
            }
            check(
                call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 1)
                    && ctl(0x23004, source.child).0 == 2,
                2090,
            );
        }
        if cfg!(exec_keep_fds) {
            plan.table = table;
        }
        check(
            call(0x23009, factory, source.child, 2, 0, 0, 0).0 == 0,
            2040,
        );
        if cfg!(exec_reject) {
            if cfg!(exec_reject_table) {
                send(source, &mut boot);
                if cfg!(exec_reject_malformed) {
                    plan.table[3] = 1;
                    send(source, &mut plan.table);
                } else if cfg!(exec_reject_partial) {
                    send(source, &mut plan.table[..16]);
                }
            } else if cfg!(exec_reject_malformed) {
                boot[0] = b'X';
                send(source, &mut boot[..32]);
            } else if cfg!(exec_reject_partial) {
                send(source, &mut boot[..16]);
            }
            let writer_closed = !cfg!(exec_reject_malformed);
            if writer_closed {
                check(ctl(0x24003, source.writer).0 == 0, 2073);
            }
            check(
                call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 0),
                2071,
            );
            rejected_bootstrap(
                source,
                service,
                peer,
                writer_closed,
                if cfg!(exec_reject_table) && cfg!(exec_reject_malformed) {
                    216
                } else {
                    215
                },
            );
            continue;
        }
        if cfg!(exec_boot_incomplete) {
            if cfg!(exec_boot_table) {
                send(source, &mut boot);
                if cfg!(exec_boot_partial) {
                    send(source, &mut plan.table[..16]);
                }
            } else if cfg!(exec_boot_partial) {
                send(source, &mut boot[..16]);
            }
            check(bounded_record(source, false) == Err(0), 2060);
            check(
                ctl(0x20001, source.child).0 == 0
                    && call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 0),
                2060,
            );
            contain(source, service, peer);
            continue;
        }
        send(source, &mut boot);
        send(source, &mut plan.table);
        if cfg!(exec_mask) {
            send(source, &mut mask);
        }
        if cfg!(exec_keep_fds) {
            check(terminal(source.child) != (216, 1), 2040);
            end(2041);
        }
        if cfg!(exec_reset_offset) {
            pos = 0;
        }
        read(source, 0, generation, service, handles[0], &mut pos, b'c');
        for j in [0, 2] {
            request(source, 0, generation, 3, j);
            holders[0][j] = false;
            if !cfg!(exec_shared) || !holders[1][j] {
                check(backend(service, 3, handles[j], 0) == [0; 32], 2040);
                closes += 1;
            }
            send(source, &mut [0; 32]);
        }
        check(terminal(source.child) == (62, 1), 2040);
        if cfg!(exec_peer_first) {
            check(pos == 3 && holders == [[false; 3]; 2] && closes == 3, 2091);
            dispose(peer);
            dispose(source);
            finish_backend(service);
            continue;
        }
        if cfg!(exec_shared) {
            read(peer, 1, generation, service, handles[0], &mut pos, b'd');
            request(peer, 1, generation, 2, 1);
            let mut write = [0; 32];
            put(&mut write, 0, 4);
            put(&mut write, 4, handles[1]);
            put(&mut write, 12, 1);
            write[16] = b'z';
            send(service, &mut write);
            let mut written = [0; 32];
            put(&mut written, 0, 1);
            check(receive(service) == written, 2080);
            let mut echoed = written;
            echoed[16] = b'z';
            check(backend(service, 2, handles[1], 0) == echoed, 2080);
            send(peer, &mut written);
            release(
                peer,
                1,
                generation,
                service,
                &handles,
                &mut holders,
                &mut closes,
            );
            check(
                terminal(peer.child) == (63, 1)
                    && pos == 4
                    && holders == [[false; 3]; 2]
                    && closes == 3,
                2081,
            );
            dispose(source);
            dispose(peer);
            finish_backend(service);
            continue;
        }
        dispose(source);
        finish_backend(service);
        let hello = receive(peer);
        check(hello[0..4] == [0; 4] && hello[16..] == [0; 16], 2040);
        for j in 0..3 {
            check(backend(peer, 3, get(&hello, 4 + j * 4), 0) == [0; 32], 2040);
        }
        finish_backend(peer);
    }
    end(100)
}

// The copied child's connection remains authoritative across replacement.
#[cfg(all(fork_exec, not(shell_files)))]
pub fn replace_fork(
    factory: u64,
    image: u64,
    child: Connection,
    boot: &mut [u8; 128],
    holders: &mut [[bool; 3]; 2],
) {
    let mut mask = [0; 32];
    let args = exec_request(child, b"/next", &mut mask);
    let mut table = [0; 64];
    table[..32].copy_from_slice(&receive(child));
    table[32..].copy_from_slice(&receive(child));
    publish_fork(factory, image, child, boot, holders, args, mask, table);
}
#[cfg(fork_dispatch)]
pub fn replace_record(
    factory: u64,
    image: u64,
    child: Connection,
    boot: &mut [u8; 128],
    holders: &mut [[bool; 3]; 2],
    record: &[u8; 400],
    #[cfg(shell_files)] files: &crate::scratch_owner::Owner,
    #[cfg(shell_files)] file_reference: u32,
) {
    let mut mask = [0; 32];
    mask.copy_from_slice(&record[304..336]);
    let value = u64::from_le_bytes(mask[8..16].try_into().unwrap());
    check(
        &mask[..8] == b"AEEMSK01" && mask[16..] == [0; 16] && value & ((1 << 8) | (1 << 18)) == 0,
        2133,
    );
    let mut table = [0; 64];
    table.copy_from_slice(&record[336..]);
    let mut arguments = decode_args(&record[32..304]);
    if cfg!(shell_argv_arg) {
        arguments.strings[2][0] = b'x';
    }
    if cfg!(shell_argv_env) {
        for entry in &mut arguments.strings[4..] {
            if entry[..8] == *b"WITNESS=" {
                entry[8] = b'x';
            }
        }
    }
    publish_fork(
        factory,
        image,
        child,
        boot,
        holders,
        arguments,
        mask,
        table,
        #[cfg(shell_files)]
        files,
        #[cfg(shell_files)]
        file_reference,
    );
}
#[cfg(shell_null)]
pub fn deny_null(factory: u64, child: Connection, record: &[u8; 400]) {
    let arguments = decode_args(&record[32..304]);
    let mut expected = [0; 64];
    expected[..12].copy_from_slice(&[3, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0]);
    expected[40..44].copy_from_slice(&[0, 1, 1, 0]);
    check(record[336..] == expected, 2320);
    let mut mask = [0; 32];
    mask[..8].copy_from_slice(b"AEEMSK01");
    check(record[304..336] == mask, 2320);
    parked(child.child, 1);
    let before = call(0x23008, factory, child.child, 0, 0, 0, 0);
    check(before == (0, 0, 0), 2320);
    check(
        call(
            0x23007,
            factory,
            child.child,
            0xffff,
            1,
            &arguments as *const Args as u64,
            0,
        )
        .0 == -13,
        2320,
    );
    check(
        call(0x23008, factory, child.child, 0, 0, 0, 0) == before,
        2320,
    );
    check(ctl(0x23004, child.child).0 == 1, 2320);
    check(call(0x23005, child.child, 1, 0, 0, 0, 0).0 == 0, 2320);
    let mut response = [0; 32];
    put(&mut response, 0, (-13i32) as u32);
    send(child, &mut response);
}

#[cfg(fork_exec)]
fn publish_fork(
    factory: u64,
    image: u64,
    child: Connection,
    boot: &mut [u8; 128],
    holders: &mut [[bool; 3]; 2],
    args: Args,
    mut mask: [u8; 32],
    table: [u8; 64],
    #[cfg(shell_files)] files: &crate::scratch_owner::Owner,
    #[cfg(shell_files)] file_reference: u32,
) {
    let mut expected = [0; 64];
    expected[..12].copy_from_slice(&[0, 0, 1, 0, 1, 1, 1, 0, 2, 0, 1, 0]);
    if cfg!(shell_dash) {
        expected[5] = 0;
    }
    expected[40..44].copy_from_slice(&[0, 1, 1, 0]);
    if cfg!(shell_null) {
        expected[0] = 3;
    }
    #[cfg(all(shell_files, not(shell_files_redirect)))]
    expected[36..40].copy_from_slice(&[3, 0, 1, 0]);
    #[cfg(shell_files_redirect)]
    {
        expected[0] = 3;
        expected[44..48].copy_from_slice(&[0, 1, 1, 0]);
    }
    check(table == expected && holders == &[[true; 3]; 2], 2120);
    #[cfg(shell_files)]
    let mut descriptions = files
        .describe_files(1, &[1, 0])
        .unwrap_or_else(|_| end(2506));
    #[cfg(shell_files)]
    check(
        get(&descriptions, 0) == file_reference
            && get(&descriptions, 4) == if cfg!(shell_files_redirect) { 1 } else { 14 },
        2506,
    );
    #[cfg(shell_files)]
    let plan =
        crate::exec_fds::prepare_files(&table, &[2, 1, 1, 1, 0]).unwrap_or_else(|_| end(2120));
    #[cfg(shell_null)]
    let plan = crate::exec_fds::prepare_null(&table, &[1, 1, 1, 1]).unwrap_or_else(|_| end(2120));
    #[cfg(not(any(shell_null, shell_files)))]
    let plan = crate::exec_fds::prepare(&table, &[2, 1, 1]).unwrap_or_else(|_| end(2120));
    let sequence = if cfg!(shell_null) { 2 } else { 1 };
    parked(child.child, sequence as i64);
    check(
        call(
            0x23007,
            factory,
            child.child,
            image,
            sequence,
            &args as *const Args as u64,
            0,
        )
        .0 == 0,
        2120,
    );
    check(
        call(0x23008, factory, child.child, 0, 0, 0, 0) == (sequence as i64, image, 1),
        2120,
    );
    #[cfg(shell_null)]
    {
        check(
            plan.release == [true, false, false, false] && holders[0][0],
            2120,
        );
        holders[1][0] = false;
    }
    #[cfg(not(any(shell_null, shell_files)))]
    check(
        plan.release == [false, !cfg!(shell_dash), false] && holders[0][1],
        2120,
    );
    #[cfg(all(shell_files, not(shell_files_redirect)))]
    check(
        plan.release == [false; 5] && plan.users == [1, 1, 1, 1, 0],
        2506,
    );
    #[cfg(shell_files_redirect)]
    {
        check(
            plan.release == [true, false, false, false, false]
                && plan.users == [0, 1, 1, 1, 0]
                && holders[0][0],
            2506,
        );
        if !cfg!(files_redirect_keep_stdin) {
            holders[1][0] = false;
        }
    }
    // Dropping the extra stdin alias leaves its description held by stdio.
    if !cfg!(shell_dash) {
        holders[1][1] = false;
    }
    check(
        call(0x23009, factory, child.child, sequence, 0, 0, 0).0 == 0,
        2120,
    );
    send(child, boot);
    let mut survivors = if cfg!(fork_exec_keep) {
        table
    } else {
        plan.table
    };
    send(child, &mut survivors);
    send(child, &mut mask);
    #[cfg(shell_files)]
    {
        scratch_bootstrap(child, files, 1);
        if cfg!(shell_files_drop_description) {
            descriptions[..16].fill(0);
        }
        send(child, &mut descriptions);
    }
}
