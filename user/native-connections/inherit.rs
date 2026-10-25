#[cfg(pipe_probe)]
#[path = "pipe-native.rs"]
mod pipe_native;
#[cfg(any(shell_dash, pipe_probe))]
#[path = "shell.rs"]
mod shell;
// SPDX-License-Identifier: BSD-2-Clause
// Bounded two-client stream owner; not a production fork service.
use super::*;
#[cfg(fork_dispatch)]
#[path = "dispatch.rs"]
mod dispatch;
#[cfg(any(exec_streams, fork_exec))]
#[path = "exec_streams.rs"]
pub mod exec_streams;
fn receive(c: Connection) -> [u8; 32] {
    let mut b = [0; 32];
    let mut used = 0;
    for _ in 0..100000 {
        let n = call(
            0x24001,
            c.reader,
            b[used..].as_mut_ptr() as u64,
            (32 - used) as u64,
            0,
            0,
            0,
        )
        .0;
        if n == -11 {
            check(ctl(0x20001, c.child).0 == 0, 1950);
            ctl(0x1fffe, 0);
            continue;
        }
        check(n > 0 && n as usize <= 32 - used, 1950);
        used += n as usize;
        if used == 32 {
            return b;
        }
    }
    end(1950)
}
// Incomplete publication is not readiness, even when its missing tail is zero.
fn bounded_record(c: Connection, pad: bool) -> Result<[u8; 32], usize> {
    let mut b = [0; 32];
    let mut used = 0;
    for _ in 0..256 {
        let n = call(
            0x24001,
            c.reader,
            b[used..].as_mut_ptr() as u64,
            (32 - used) as u64,
            0,
            0,
            0,
        )
        .0;
        if n == -11 {
            if pad && used != 0 {
                return Ok(b); // Deliberate false readiness from zero-filled tail.
            }
            ctl(0x1fffe, 0);
            continue;
        }
        if n == 0 {
            return Err(used);
        }
        check(n > 0 && n as usize <= 32 - used, 1980);
        used += n as usize;
        if used == 32 {
            return Ok(b);
        }
    }
    Err(used)
}
fn readiness(c: Connection) -> Result<[u8; 32], usize> {
    bounded_record(c, cfg!(inherit_pad_ack))
}
#[cfg_attr(fork_dispatch, inline(never))]
fn send(c: Connection, b: &mut [u8]) {
    check(transfer_bounded(c.writer, b, true, 100000) == 1, 1950);
}
fn backend(c: Connection, op: u32, handle: u32, pos: u32) -> [u8; 32] {
    let mut b = [0; 32];
    put(&mut b, 0, op);
    put(&mut b, 4, handle);
    put(&mut b, 8, pos);
    put(&mut b, 12, if op == 2 { 1 } else { 0 });
    send(c, &mut b);
    receive(c)
}
fn request(c: Connection, who: usize, generation: u32, op: u32, binding: usize) {
    let b = receive(c);
    check(
        get(&b, 0) == op
            && get(&b, 4)
                == 0x76000000
                    + (if cfg!(exec_shared) { 0 } else { who as u32 }) * 0x1000000
                    + ((binding as u32) << 16)
                    + generation
            && get(&b, 8) == binding as u32
            && get(&b, 12) == if op == 1 || op == 2 { 1 } else { 0 }
            && if op == 2 {
                b[16] == b'z' && b[17..].iter().all(|v| *v == 0)
            } else {
                b[16..].iter().all(|v| *v == 0)
            },
        1901,
    );
}
fn read(
    c: Connection,
    who: usize,
    generation: u32,
    service: Connection,
    handle: u32,
    pos: &mut u32,
    expected: u8,
) {
    request(c, who, generation, 1, 0);
    let at = if cfg!(inherit_private_position) && who == 1 {
        0
    } else {
        *pos
    };
    let mut b = backend(service, 2, handle, at);
    check(get(&b, 0) == 1, 1952);
    check(
        b[16] == expected && b[4..16].iter().all(|v| *v == 0) && b[17..].iter().all(|v| *v == 0),
        1903,
    );
    *pos += 1;
    send(c, &mut b);
}
fn release(
    c: Connection,
    who: usize,
    generation: u32,
    service: Connection,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
    closes: &mut u32,
) {
    for j in 0..3 {
        request(c, who, generation, 3, j);
        check(holders[who][j], 1901);
        holders[who][j] = false;
        if !holders[1 - who][j] || cfg!(inherit_early_close) && who == 0 && j == 0 {
            let b = backend(service, 3, handles[j], 0);
            check(b == [0; 32], 1952);
            *closes += 1;
        }
        send(c, &mut [0; 32]);
    }
}
fn dispose(c: Connection) {
    check(
        ctl(0x24003, c.writer).0 == 0
            && ctl(0x24003, c.reader).0 == 0
            && ctl(0x20002, c.child).0 == 0,
        1953,
    );
}
// Drain no application bytes: any child traffic here violates failed publication.
fn rejected(c: Connection, failure: u64) {
    for _ in 0..100000 {
        let mut b = [0u8; 32];
        let n = call(0x24001, c.reader, b.as_mut_ptr() as u64, 32, 0, 0, 0).0;
        check(n == -11 || n == 0, failure);
        let state = ctl(0x20001, c.child);
        if state.0 != 0 {
            check(state.0 == 252 && state.2 == 1, 1960);
            // The producer may have queued bytes between our read and terminal
            // observation. Once terminated it cannot append; require actual EOF.
            check(
                call(0x24001, c.reader, b.as_mut_ptr() as u64, 32, 0, 0, 0).0 == 0,
                failure,
            );
            return;
        }
        ctl(0x1fffe, 0);
    }
    end(1960)
}
fn finish_backend(service: Connection) {
    check(
        ctl(0x24003, service.writer).0 == 0 && terminal(service.child) == (17, 1),
        1953,
    );
    check(
        ctl(0x24003, service.reader).0 == 0 && ctl(0x20002, service.child).0 == 0,
        1953,
    );
}
fn finish(service: Connection, source: Connection, child: Connection) {
    if !cfg!(shell_console) {
        finish_backend(service);
    }
    dispose(source);
    dispose(child);
}
fn recover(
    source: Connection,
    child: Connection,
    service: Connection,
    generation: u32,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
) {
    recover_parent(source, service, generation, handles, holders);
    finish(service, source, child);
}
fn recover_parent(
    source: Connection,
    service: Connection,
    generation: u32,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
) {
    // Caller confirmed terminal state or no child publication. Probe before cleanup so
    // a broken parent gate cannot be hidden by a successful backend exchange.
    let mut probe = [0; 32];
    put(&mut probe, 0, 69);
    send(source, &mut probe);
    let ack = receive(source);
    check(get(&ack, 0) == 70 && ack[4..].iter().all(|v| *v == 0), 1962);
    holders[1] = [false; 3];
    let mut failed = [0; 32];
    put(&mut failed, 0, 68);
    send(source, &mut failed);
    let mut pos = 0;
    let mut closes = 0;
    read(source, 0, generation, service, handles[0], &mut pos, b'a');
    read(source, 0, generation, service, handles[0], &mut pos, b'b');
    release(
        source,
        0,
        generation,
        service,
        handles,
        holders,
        &mut closes,
    );
    check(
        terminal(source.child) == (73, 1) && pos == 2 && closes == 3 && *holders == [[false; 3]; 2],
        1965,
    );
}
// Shared backend uncertainty blocks every alias, while complete EIO replies let
// each client consume its local descriptors without claiming backend closure.
fn uncertain_backend(
    source: Connection,
    child: Connection,
    service: Connection,
    generation: u32,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
) {
    let mut uncertain = false;
    let mut requests = 0;
    for (who, c) in [source, child].iter().copied().enumerate() {
        for _ in 0..2 {
            request(
                c,
                who,
                generation,
                if cfg!(inherit_write) { 2 } else { 1 },
                if cfg!(inherit_write) { 1 } else { 0 },
            );
            let mut reply = [0; 32];
            put(&mut reply, 0, (-5i32) as u32);
            if !uncertain
                || (cfg!(inherit_uncertain_alias) || cfg!(inherit_write_replay)) && who == 1
            {
                let mut req = [0; 32];
                put(&mut req, 0, if cfg!(inherit_write) { 4 } else { 2 });
                put(
                    &mut req,
                    4,
                    handles[if cfg!(inherit_write) { 1 } else { 0 }],
                );
                put(&mut req, 12, 1);
                if cfg!(inherit_write) {
                    req[16] = b'z';
                }
                send(service, &mut req);
                requests += 1;
                let response = bounded_record(service, cfg!(inherit_backend_pad));
                if let Err(count) = response {
                    check(
                        cfg!(inherit_backend_incomplete)
                            && count == if cfg!(inherit_backend_partial) { 17 } else { 0 },
                        1994,
                    );
                }
                if let Ok(b) = response
                    && get(&b, 0) == 1
                    && b[4..16].iter().all(|v| *v == 0)
                    && if cfg!(inherit_write) {
                        b[16..].iter().all(|v| *v == 0)
                    } else {
                        b[16] == b'a' && b[17..].iter().all(|v| *v == 0)
                    }
                {
                    reply = b;
                } else {
                    uncertain = true;
                }
            }
            send(c, &mut reply);
            let ack = readiness(c);
            check(
                matches!(ack, Ok(b) if get(&b, 0) == 70 && b[4..].iter().all(|v| *v == 0)),
                1992,
            );
        }
        for j in 0..3 {
            request(c, who, generation, 3, j);
            check(holders[who][j] && uncertain, 1990);
            holders[who][j] = false;
            let mut reply = [0; 32];
            put(&mut reply, 0, (-5i32) as u32);
            send(c, &mut reply);
        }
        check(
            terminal(c.child) == (if who == 0 { 74 } else { 75 }, 1),
            1992,
        );
    }
    check(
        uncertain && requests == 1 && *holders == [[false; 3]; 2],
        1990,
    );
    stop_uncertain(service, source, child);
}
fn stop_uncertain(service: Connection, source: Connection, child: Connection) {
    if !cfg!(inherit_uncertain_skip_stop) {
        check(ctl(0x20007, service.child).0 == 0, 1993);
    }
    let status = ctl(0x20001, service.child);
    check(status.0 == 144 && status.2 == 3, 1993);
    dispose(service);
    dispose(source);
    dispose(child);
}
fn uncertain_close(
    source: Connection,
    child: Connection,
    service: Connection,
    generation: u32,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
) {
    let mut uncertain = false;
    let mut requests = 0;
    for (who, c) in [source, child].iter().copied().enumerate() {
        for j in 0..3 {
            request(c, who, generation, 3, j);
            check(holders[who][j], 1995);
            holders[who][j] = false;
            if !holders[1 - who][j] && (!uncertain || cfg!(inherit_close_replay)) {
                let mut req = [0; 32];
                put(&mut req, 0, 3);
                put(&mut req, 4, handles[j]);
                send(service, &mut req);
                requests += 1;
                uncertain = match bounded_record(service, cfg!(inherit_backend_pad)) {
                    Ok(reply) => reply != [0; 32],
                    Err(count) => {
                        check(
                            cfg!(inherit_backend_incomplete)
                                && count == if cfg!(inherit_backend_partial) { 17 } else { 0 },
                            1995,
                        );
                        true
                    }
                };
            }
            let mut reply = [0; 32];
            if uncertain && !cfg!(inherit_close_success) {
                put(&mut reply, 0, (-5i32) as u32);
            }
            send(c, &mut reply);
            check(
                matches!(readiness(c), Ok(b) if get(&b, 0) == 70 && b[4..].iter().all(|v| *v == 0)),
                1996,
            );
        }
        check(
            terminal(c.child) == (if who == 0 { 76 } else { 77 }, 1),
            1996,
        );
    }
    check(
        uncertain && requests == 1 && *holders == [[false; 3]; 2],
        1995,
    );
    stop_uncertain(service, source, child);
}
fn incomplete_final(
    source: Connection,
    child: Connection,
    service: Connection,
    generation: u32,
    handles: &[u32; 3],
    holders: &mut [[bool; 3]; 2],
) {
    let (target, peer, who) = if cfg!(inherit_final_parent) {
        (source, child, 1)
    } else {
        (child, source, 0)
    };
    let mut done = [0; 32];
    put(&mut done, 0, 67);
    send(peer, &mut done);
    if cfg!(inherit_final_partial) {
        send(target, &mut done[..16]);
    }
    // Any target traffic means incomplete publication escaped into application I/O.
    check(matches!(bounded_record(target, false), Err(0)), 2001);
    if !cfg!(inherit_final_skip_parent) {
        check(ctl(0x20007, source.child).0 == 0, 2002);
    }
    let status = ctl(0x20001, source.child);
    check(status.0 == 144 && status.2 == 3, 2002);
    if !cfg!(inherit_final_skip_child) {
        check(ctl(0x20007, child.child).0 == 0, 2003);
    }
    let status = ctl(0x20001, child.child);
    check(status.0 == 144 && status.2 == 3, 2003);
    // Both producers are stopped: queued peer traffic can now be discarded.
    request(peer, who, generation, 1, 0);
    for c in [source, child] {
        let mut byte = [0u8; 1];
        check(
            call(0x24001, c.reader, byte.as_mut_ptr() as u64, 1, 0, 0, 0).0 == 0,
            2004,
        );
    }
    *holders = [[false; 3]; 2];
    for handle in handles {
        check(backend(service, 3, *handle, 0) == [0; 32], 2004);
    }
    finish(service, source, child);
}
fn rejected_prepare(source: Connection, service: Connection, handles: &[u32; 3]) {
    check(
        matches!(bounded_record(source, false), Err(0)) && terminal(source.child) == (78, 1),
        2010,
    );
    check(ctl(0x20001, 0xb0000103).0 == -9, 2011);
    if cfg!(inherit_prepare_reserve) {
        check(ctl(0x24000, 0xd001).0 > 0, 2011);
    }
    let mut spare = [(0u64, 0u64); 2];
    for ends in &mut spare {
        let c = ctl(0x24000, 0xd001);
        check(c.0 > 0, 2011);
        *ends = (c.0 as u64, c.1);
    }
    check(ctl(0x24000, 0xd001).0 == -16, 2011);
    for (reader, writer) in spare {
        check(
            ctl(0x24003, reader).0 == 0 && ctl(0x24003, writer).0 == 0,
            2011,
        );
    }
    for handle in handles {
        check(backend(service, 3, *handle, 0) == [0; 32], 2012);
    }
    finish_backend(service);
    dispose(source);
}
fn wait_status(terminal: (u32, u32)) -> u32 {
    if cfg!(inherit_wait_as_exit) {
        return terminal.0 << 8;
    }
    match terminal {
        (detail, 1) if detail <= 255 => detail << 8,
        (134, 2) => 4, // Actual #UD, mapped to SIGILL without a core-dump claim.
        (15, 4) => 15, // Actual native SIGTERM termination.
        _ => end(2022),
    }
}
// Private single-child wait protocol; result retention is independent of FDs.
#[cfg(suspend_order)]
fn parked(h: u64, expected: i64) -> bool {
    let result: i64;
    let observed: u64;
    unsafe {
        asm!("int 0x81", inlateout("rax") 0x20001u64 => result,
            in("rdi") h, in("rsi") 0u64, lateout("rdx") _,
            in("r10") 0u64, lateout("r8") _, lateout("r9") observed,
            lateout("rcx") _, options(nostack));
    }
    check(result == expected && observed <= 1, 2330);
    observed == 1
}
fn wait_step(source: Connection, pid: u32, ready: bool, status: u32, collected: &mut bool) -> bool {
    let request = receive(source);
    let op = get(&request, 0);
    let selector = get(&request, 4) as i32;
    let options = get(&request, 8);
    let mut reply = [0; 32];
    let result: i32;
    if request[12..].iter().any(|v| *v != 0)
        || (op != 80 && op != 81)
        || options > 1
        || (op == 81 && options != 0)
    {
        result = -22;
    } else if (selector != pid as i32 && !(op == 80 && selector == -1)) || (op == 80 && *collected)
    {
        result = -10;
    } else if op == 81 {
        if ready {
            *collected = true;
            result = 0;
        } else {
            result = -22;
        }
    } else if !ready {
        result = 0;
    } else {
        result = pid as i32;
        put(&mut reply, 4, pid);
    }
    put(&mut reply, 0, result as u32);
    if cfg!(inherit_wait_broken)
        && ((op == 80 && selector == -1 && !cfg!(inherit_wait_ack))
            || (op == 81 && cfg!(inherit_wait_ack)))
    {
        if cfg!(inherit_wait_partial) {
            send(source, &mut reply[..16]);
        } else if cfg!(inherit_wait_body) {
            send(source, &mut reply);
            send(source, &mut status.to_le_bytes()[..2]);
        } else if cfg!(inherit_wait_ack_bad) {
            reply[31] = 1;
            send(source, &mut reply);
        }
        check(ctl(0x24003, source.writer).0 == 0, 2023);
        return true;
    }
    send(source, &mut reply);
    if result > 0 {
        let encoded = if cfg!(inherit_wait_bad_status) {
            status ^ 256
        } else {
            status
        };
        send(source, &mut encoded.to_le_bytes());
        if cfg!(inherit_wait_consume) {
            *collected = true;
        }
    }
    false
}
// The shell lifetime outlives each collected child. Tokens belong to the parent;
// destination generations belong to slot2 and never grant authority by themselves.
#[cfg(any(shell_repeat, shell_failed_exec))]
pub fn admit(source: Connection, factory: u64, header: [u8; 32], generation: u32) -> Connection {
    check(
        (1..=3).contains(&generation)
            && get(&header, 0) == 64
            && get(&header, 4) == 1
            && get(&header, 8) == 1
            && get(&header, 12) == 16
            && header[16..] == [0; 16],
        2150,
    );
    let mut snapshot = [0; 64];
    snapshot[..32].copy_from_slice(&receive(source));
    snapshot[32..].copy_from_slice(&receive(source));
    let mut expected = [0; 64];
    for j in 0..3 {
        expected[j * 4] = j as u8;
        expected[j * 4 + 2] = 1;
    }
    expected[41] = 1;
    expected[42] = 1;
    check(snapshot == expected, 2150);
    let sequence = generation as i64; // Exactly one fork freeze per command.
    let mut frozen = false;
    for _ in 0..10000 {
        let n = ctl(0x23004, source.child).0;
        if n == sequence {
            frozen = true;
            break;
        }
        check(n == 0, 2150);
        ctl(0x1fffe, 0);
    }
    check(frozen, 2150);
    let req = ctl(0x24000, 0xd001);
    let rep = ctl(0x24000, 0xd001);
    check(req.0 > 0 && rep.0 > 0, 2150);
    let token = if cfg!(repeat_token) {
        1
    } else {
        sequence as u64
    };
    let h = call(
        0x23006,
        factory,
        source.child,
        2,
        token,
        req.0 as u64,
        rep.1,
    )
    .0;
    check(
        h == (0xb0000000u64 | ((generation as u64) << 8) | 3) as i64,
        2151,
    );
    let child = Connection {
        reader: rep.0 as u64,
        writer: req.1,
        child: h as u64,
    };
    let mut receipt = [0; 32];
    put(&mut receipt, 0, 65);
    put(&mut receipt, 4, generation);
    put(&mut receipt, 8, 1);
    for j in 0..3 {
        put(
            &mut receipt,
            12 + j * 4,
            0x77000000 + ((j as u32) << 16) + generation,
        );
    }
    send(child, &mut receipt);
    let ack = readiness(child).unwrap_or_else(|_| end(2152));
    check(get(&ack, 0) == 66 && ack[4..] == [0; 28], 2152);
    let mut done = [0; 32];
    put(&mut done, 0, 67);
    send(source, &mut done);
    send(child, &mut done);
    child
}
pub fn run(factory: u64, first: u64, second: u64, _third: u64) -> ! {
    let generations = if cfg!(shell_repeat) || cfg!(shell_failed_exec) {
        1u32
    } else if cfg!(inherit_prepare)
        || cfg!(pipe_reply_lost)
        || cfg!(pipe_reply_one)
        || cfg!(pipe_reply_short)
        || cfg!(pipe_signal)
    {
        3
    } else {
        2
    };
    #[cfg(shell_console)]
    let console = {
        let c = launch(factory, second, 1);
        check(call(0x26003, 0xf001, c.child, 0, 0, 0, 0).0 == 0, 2142);
        check(call(0x26000, 0xf001, 0, 0, 0, 0, 0).0 == -13, 2142);
        c
    };
    #[cfg(suspend_stale)]
    let mut next_source: Option<Connection> = None;
    for generation in 1..=generations {
        #[cfg(suspend_stale)]
        let source = next_source
            .take()
            .unwrap_or_else(|| launch(factory, first, 0));
        #[cfg(not(suspend_stale))]
        let source = launch(factory, first, 0);
        #[cfg(shell_console)]
        let service = console;
        #[cfg(not(shell_console))]
        let service = launch(factory, second, 1);
        #[cfg(shell_console)]
        if generation == 2 {
            send(service, &mut [0; 32]);
        }
        #[cfg(scratch_backend)]
        {
            let mut boot = [0; 32];
            boot[..8].copy_from_slice(b"AESCR001");
            put(&mut boot, 8, ((service.child >> 8) & 255) as u32);
            send(service, &mut boot);
        }
        let hello = receive(service);
        let handles = [get(&hello, 4), get(&hello, 8), get(&hello, 12)];
        check(
            hello[0..4] == [0; 4]
                && (cfg!(scratch_backend) || hello[16..].iter().all(|v| *v == 0))
                && handles == [0xf101, 0xf201, 0xf202],
            1901,
        );
        #[cfg(any(scratch_client, shell_files))]
        check(
            get(&hello, 16) == (0xfb000000 | generation)
                && get(&hello, 20) == generation
                && hello[24..] == *b"AESCR001",
            2501,
        );
        #[cfg(all(scratch_backend, not(any(scratch_client, shell_files))))]
        scratch_probe(service, generation, &hello);
        let mut boot = [0u8; 128];
        boot[..8].copy_from_slice(b"AECAT001");
        boot[8..12].copy_from_slice(&3u32.to_le_bytes());
        boot[12..16].copy_from_slice(&generation.to_le_bytes());
        for j in 0..3usize {
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
                boot[32 + j * 32 + k * 4..36 + j * 32 + k * 4].copy_from_slice(&v.to_le_bytes());
            }
        }
        #[cfg(any(shell_dash, pipe_probe))]
        shell::bootstrap(source, &mut boot, generation);
        #[cfg(not(any(shell_dash, pipe_probe)))]
        send(source, &mut boot);
        #[cfg(all(scratch_client, not(scratch_copy)))]
        scratch_client_run(source, service, generation);
        #[cfg(scratch_copy)]
        let (mut file_owner, file_reference) = scratch_copy_start(source, service, generation);
        #[cfg(shell_files)]
        let mut file_owner = crate::scratch_owner::Owner::new(generation);
        #[cfg(shell_files)]
        scratch_bootstrap(source, &file_owner, 0);
        #[cfg(shell_files)]
        let mut file_references = [0u32; 2];
        #[cfg(pipe_probe)]
        {
            pipe_native::run(source, service, factory, generation, handles);
            continue;
        }
        if cfg!(inherit_prepare) {
            rejected_prepare(source, service, &handles);
            continue;
        }
        #[cfg(fork_dispatch)]
        let mut positions = [0; 3];
        #[cfg(shell_prelude)]
        let header = dispatch::before_fork(
            source,
            service,
            &handles,
            generation,
            &mut positions,
            #[cfg(shell_files)]
            &mut file_owner,
            #[cfg(shell_files)]
            &mut file_references,
        );
        #[cfg(not(shell_prelude))]
        let header = receive(source);
        #[cfg(any(shell_repeat, shell_failed_exec))]
        {
            let child = admit(source, factory, header, 1);
            dispatch::run(
                factory,
                _third,
                [source, child],
                service,
                handles,
                boot,
                [[true; 3]; 2],
                generation,
                positions,
                #[cfg(shell_files)]
                &mut file_owner,
                #[cfg(shell_files)]
                file_references,
            );
            continue;
        }
        check(
            get(&header, 0) == 64
                && get(&header, 4) == 1
                && get(&header, 8) == generation
                && get(&header, 12) == 16
                && header[16..].iter().all(|v| *v == 0),
            1901,
        );
        let mut snapshot = [0u8; 64];
        snapshot[..32].copy_from_slice(&receive(source));
        snapshot[32..].copy_from_slice(&receive(source));
        let mut expected = [0u8; 64];
        for j in 0..3 {
            expected[j * 4] = j as u8;
            expected[j * 4 + 2] = 1;
        }
        expected[41] = 1;
        expected[42] = 1;
        #[cfg(scratch_copy)]
        {
            expected[12..20].copy_from_slice(&[3, 0, 1, 0, 3, 1, 1, 0]);
            if cfg!(scratch_copy_bad_snapshot) {
                snapshot[17] = 0;
            }
            check(snapshot == expected, 2506);
        }
        #[cfg(all(shell_files, not(any(shell_files_redirect, shell_files_denied))))]
        expected[36..40].copy_from_slice(&[3, 0, 1, 0]);
        #[cfg(shell_files_redirect)]
        {
            expected[0] = 3;
            expected[44..48].copy_from_slice(&[0, 1, 1, 0]);
        }
        check(snapshot == expected, 1901);
        let mut frozen = false;
        for _ in 0..10000 {
            let n = ctl(0x23004, source.child).0;
            if n == 1 {
                frozen = true;
                break;
            }
            check(n == 0, 1901);
            ctl(0x1fffe, 0);
        }
        check(frozen, 1901);
        let req = ctl(0x24000, 0xd001);
        let rep = ctl(0x24000, 0xd001);
        check(req.0 > 0 && rep.0 > 0, 1901);
        let mut holders = [[true; 3]; 2]; // Child holders staged; no route is serviced yet.
        let h = call(0x23006, factory, source.child, 2, 1, req.0 as u64, rep.1).0;
        if cfg!(inherit_rollback) {
            let vacant = 0xb0000000u64 | ((generation as u64) << 8) | 3;
            check(
                h == -12 && ctl(0x23004, source.child).0 == 1 && ctl(0x20001, vacant).0 == -9,
                1970,
            );
            let ends = [
                (req.0 as u64, 0x24001),
                (req.1, 0x24002),
                (rep.0 as u64, 0x24001),
                (rep.1, 0x24002),
            ];
            for (i, &(cap, op)) in ends.iter().enumerate() {
                check(call(op, cap, 0, 0, 0, 0, 0).0 == 0, 1972);
                if !(cfg!(inherit_rollback_leak) && i == 0) {
                    check(ctl(0x24003, cap).0 == 0, 1972);
                }
                check(call(op, cap, 0, 0, 0, 0, 0).0 == -13, 1972);
            }
            holders[1] = [false; 3];
            if cfg!(inherit_rollback_close) {
                check(backend(service, 3, handles[0], 0) == [0; 32], 1952);
            }
            check(
                call(0x23005, source.child, 0, 0, 0, 0, 0).0 == -9
                    && ctl(0x23004, source.child).0 == 1,
                1973,
            );
            if !cfg!(inherit_rollback_cancel) {
                check(call(0x23005, source.child, 1, 0, 0, 0, 0).0 == 0, 1973);
            }
            check(ctl(0x23004, source.child).0 == 0, 1973);
            recover_parent(source, service, generation, &handles, &mut holders);
            finish_backend(service);
            dispose(source);
            // Admit only after old channel cleanup: channel generations are bounded.
            let replacement = launch(factory, second, 2);
            check(replacement.child == vacant, 1974);
            check(receive(replacement) == hello, 1974);
            for handle in handles {
                check(backend(replacement, 3, handle, 0) == [0; 32], 1974);
            }
            finish_backend(replacement);
            continue;
        }
        check(
            h == (0xb0000000u64 | ((generation as u64) << 8) | 3) as i64,
            1902,
        );
        let child = Connection {
            reader: rep.0 as u64,
            writer: req.1,
            child: h as u64,
        };
        #[cfg(scratch_copy)]
        let file_child = file_owner
            .inherit(generation, [Some(file_reference), None])
            .unwrap_or_else(|_| end(2506))[0]
            .unwrap();
        #[cfg(shell_files)]
        let mut file_grant = file_owner
            .inherit_files(
                generation,
                &snapshot,
                &[2, 1, 1, if cfg!(shell_files_denied) { 0 } else { 1 }, 0],
                [
                    if cfg!(shell_files_denied) {
                        None
                    } else {
                        Some(file_references[0])
                    },
                    None,
                ],
            )
            .unwrap_or_else(|_| end(2506));
        #[cfg(shell_files)]
        {
            file_references[1] = get(&file_grant, 16);
        }
        if cfg!(inherit_stop) {
            if !cfg!(inherit_skip_stop) {
                check(ctl(0x20007, child.child).0 == 0, 1964);
            }
            let status = ctl(0x20001, child.child);
            check(status.0 == 144 && status.2 == 3, 1964);
            recover(source, child, service, generation, &handles, &mut holders);
            continue;
        }
        let mut receipt = [0; 32];
        put(&mut receipt, 0, 65);
        put(&mut receipt, 4, generation);
        put(&mut receipt, 8, 1);
        for j in 0..3 {
            put(
                &mut receipt,
                12 + j * 4,
                0x77000000 + ((j as u32) << 16) + generation,
            );
        }
        #[cfg(scratch_copy)]
        {
            put(&mut receipt, 24, file_child);
            put(&mut receipt, 28, file_owner.root(1).unwrap());
        }
        if cfg!(inherit_bad_receipt) {
            receipt[31] = 1;
        }
        if cfg!(inherit_receipt_partial) {
            send(child, &mut receipt[..16]);
        } else if !cfg!(inherit_receipt_missing) {
            send(child, &mut receipt);
        }
        #[cfg(shell_files)]
        {
            if cfg!(shell_files_bad_grant) {
                put(&mut file_grant, 16, file_references[0]);
            }
            send(child, &mut file_grant);
        }
        if cfg!(inherit_bad_receipt) {
            rejected(child, 1961);
            recover(source, child, service, generation, &handles, &mut holders);
            continue;
        }
        let ack = match readiness(child) {
            Ok(ack) => {
                check(!cfg!(inherit_incomplete), 1982);
                ack
            }
            Err(count) => {
                check(
                    cfg!(inherit_incomplete)
                        && count == if cfg!(inherit_ack_partial) { 16 } else { 0 },
                    1980,
                );
                if !cfg!(inherit_incomplete_skip_stop) {
                    check(ctl(0x20007, child.child).0 == 0, 1981);
                }
                let status = ctl(0x20001, child.child);
                check(status.0 == 144 && status.2 == 3, 1981);
                recover(source, child, service, generation, &handles, &mut holders);
                continue;
            }
        };
        check(get(&ack, 0) == 66 && ack[4..].iter().all(|v| *v == 0), 1902);
        if cfg!(inherit_final) {
            incomplete_final(source, child, service, generation, &handles, &mut holders);
            continue;
        }
        let mut done = [0; 32];
        put(&mut done, 0, 67);
        if cfg!(inherit_bad_completion) {
            put(&mut done, 0, 68);
            send(child, &mut done);
            rejected(child, 1963);
            recover(source, child, service, generation, &handles, &mut holders);
            continue;
        }
        send(source, &mut done);
        #[cfg(fork_dispatch)]
        {
            send(child, &mut done);
            dispatch::run(
                factory,
                _third,
                [source, child],
                service,
                handles,
                boot,
                holders,
                generation,
                positions,
                #[cfg(shell_files)]
                &mut file_owner,
                #[cfg(shell_files)]
                file_references,
            );
            continue;
        }
        if cfg!(inherit_uncertain) {
            send(child, &mut done);
            if cfg!(inherit_close) {
                uncertain_close(source, child, service, generation, &handles, &mut holders);
            } else {
                uncertain_backend(source, child, service, generation, &handles, &mut holders);
            }
            continue;
        }
        #[cfg(scratch_copy)]
        scratch_copy_finish(source, service, &mut file_owner, 0);
        let mut pos = 0;
        let mut closes = 0;
        read(source, 0, generation, service, handles[0], &mut pos, b'a');
        send(child, &mut done);
        #[cfg(scratch_copy)]
        {
            #[cfg(scratch_exec)]
            scratch_exec_replace(
                factory,
                _third,
                child,
                generation,
                &boot,
                &mut file_owner,
                file_child,
                service,
            );
            scratch_copy_finish(child, service, &mut file_owner, 1);
            let mut rpc = |frame: &[u8; 32]| {
                let mut frame = *frame;
                send(service, &mut frame);
                Some(receive(service))
            };
            check(file_owner.closed() && !file_owner.poisoned(), 2507);
            let h = file_owner
                .open(0, b"/scratch/data", 1, &mut rpc)
                .unwrap_or_else(|_| end(2507));
            let reply = file_owner
                .io(0, h, 2, 16, &[], &mut rpc)
                .unwrap_or_else(|_| end(2507));
            check(get(&reply, 0) == 3 && reply[16..19] == *b"ABC", 2507);
            check(
                file_owner.close(0, h, &mut rpc).is_ok() && file_owner.closed(),
                2507,
            );
        }
        #[cfg(all(fork_exec, not(shell_files)))]
        exec_streams::replace_fork(factory, _third, child, &mut boot, &mut holders);
        read(child, 1, generation, service, handles[0], &mut pos, b'b');
        read(source, 0, generation, service, handles[0], &mut pos, b'c');
        release(
            source,
            0,
            generation,
            service,
            &handles,
            &mut holders,
            &mut closes,
        );
        let mut wait_collected = false;
        let wait_pid = generation * 4 + 3;
        if cfg!(inherit_wait) {
            check(ctl(0x20001, child.child).0 == 0, 2020);
            if cfg!(suspend_before) {
                let request = receive(source);
                check(
                    get(&request, 0) == 80
                        && get(&request, 4) == wait_pid
                        && get(&request, 8) == 1
                        && request[12..].iter().all(|v| *v == 0),
                    2330,
                );
            } else {
                wait_step(source, wait_pid, false, 0, &mut wait_collected);
            }
            #[cfg(suspend_order)]
            if !cfg!(suspend_before) {
                let mut observed = false;
                for _ in 0..10000 {
                    if parked(source.child, 0) {
                        observed = true;
                        break;
                    }
                    ctl(0x1fffe, 0);
                }
                check(observed && ctl(0x20001, child.child).0 == 0, 2330);
            }
            check(!wait_collected, 2020);
        } else {
            check(terminal(source.child) == (71, 1), 1951);
        }
        #[cfg(any(suspend_stop, suspend_stale))]
        if !cfg!(suspend_late_stop) && (!cfg!(suspend_stale) || generation == 1) {
            if !cfg!(suspend_stop_skip) {
                check(ctl(0x20007, source.child).0 == 0, 2331);
            }
            check(
                ctl(0x20001, source.child).0 == 144 && ctl(0x20001, source.child).2 == 3,
                2331,
            );
            check(!parked(source.child, 144), 2331);
            check(
                ctl(0x20007, source.child).0 == 0 && !parked(source.child, 144),
                2331,
            );
        }
        #[cfg(suspend_stale)]
        if generation == 1 {
            let mut bytes = [0; 32];
            check(
                call(
                    0x24001,
                    source.reader,
                    bytes.as_mut_ptr() as u64,
                    32,
                    0,
                    0,
                    0,
                )
                .0 == 0,
                2334,
            );
            dispose(source);
            let replacement = launch(factory, first, 0);
            check(
                replacement.child != source.child
                    && ctl(0x20001, source.child).0 == -9
                    && ctl(0x20007, source.child).0 == -9,
                2334,
            );
            let ready = receive(replacement);
            check(
                get(&ready, 0) == 86
                    && get(&ready, 4) == 2
                    && ready[8..].iter().all(|v| *v == 0)
                    && !parked(replacement.child, 0)
                    && ctl(0x20001, child.child).0 == 0,
                2334,
            );
            next_source = Some(replacement);
        }
        if cfg!(fork_exec) {
            for j in [0usize, 2] {
                request(child, 1, generation, 3, j);
                check(holders[1][j] && !holders[0][j], 2121);
                check(backend(service, 3, handles[j], 0) == [0; 32], 2121);
                holders[1][j] = false;
                closes += 1;
                send(child, &mut [0; 32]);
            }
        } else {
            read(child, 1, generation, service, handles[0], &mut pos, b'd');
            read(child, 1, generation, service, handles[0], &mut pos, b'e');
            release(
                child,
                1,
                generation,
                service,
                &handles,
                &mut holders,
                &mut closes,
            );
        }
        let child_terminal = terminal(child.child);
        #[cfg(suspend_order)]
        if cfg!(suspend_before) {
            check(!parked(source.child, 0), 2330);
            send(source, &mut [0; 32]);
        }

        let expected_terminal = if cfg!(inherit_wait_fault) {
            (134, 2)
        } else if cfg!(inherit_wait_signal) {
            (15, 4)
        } else if cfg!(inherit_wait_high) {
            (134, 1)
        } else {
            (72, 1)
        };
        check(
            child_terminal == expected_terminal
                && pos == if cfg!(fork_exec) { 3 } else { 5 }
                && closes == 3
                && holders == [[false; 3]; 2],
            1951,
        );
        #[cfg(suspend_stale)]
        if generation == 1 {
            finish_backend(service);
            dispose(child);
            let replacement = next_source.unwrap();
            let mut reply = [0; 32];
            put(&mut reply, 0, 87);
            put(&mut reply, 4, 2);
            send(replacement, &mut reply);
            let ack = receive(replacement);
            check(
                get(&ack, 0) == 88 && get(&ack, 4) == 2 && ack[8..].iter().all(|v| *v == 0),
                2334,
            );
            continue;
        }
        #[cfg(suspend_stop)]
        {
            if cfg!(suspend_late_stop) {
                for _ in 0..16 {
                    ctl(0x1fffe, 0);
                    check(parked(source.child, 0), 2332);
                }
                check(ctl(0x20007, source.child).0 == 0, 2331);
            }
            check(
                terminal(source.child) == (143, 3) && !parked(source.child, 144),
                2331,
            );
            check(
                ctl(0x20007, source.child).0 == 0 && !parked(source.child, 144),
                2331,
            );
            let mut bytes = [0u8; 32];
            check(
                call(
                    0x24001,
                    source.reader,
                    bytes.as_mut_ptr() as u64,
                    32,
                    0,
                    0,
                    0,
                )
                .0 == 0,
                2331,
            );
            finish(service, source, child);
            check(
                ctl(0x20001, source.child).0 == -9 && ctl(0x20007, source.child).0 == -9,
                2331,
            );
            continue;
        }
        #[cfg(suspend_repeat)]
        {
            let request = receive(source);
            check(
                get(&request, 0) == 80
                    && get(&request, 4) == wait_pid + 1
                    && request[8..].iter().all(|v| *v == 0),
                2333,
            );
            for _ in 0..2 {
                check(
                    ctl(0x20007, child.child).0 == 0 && terminal(child.child) == (72, 1),
                    2333,
                );
            }
            let mut reply = [0; 32];
            put(&mut reply, 0, (-10i32) as u32);
            send(source, &mut reply);
        }
        if cfg!(inherit_wait) {
            // The repeat probe already serviced the first invalid-selector request.
            // Translate the observed cause without changing retained native evidence.
            for _ in 0..if cfg!(suspend_repeat) { 5 } else { 6 } {
                if wait_step(
                    source,
                    wait_pid,
                    true,
                    wait_status(child_terminal),
                    &mut wait_collected,
                ) {
                    break;
                }
            }
            if cfg!(inherit_wait_broken) {
                check(wait_collected == cfg!(inherit_wait_ack), 2023);
                check(terminal(source.child) == (71, 1), 2023);
                let mut extra = [0u8; 32];
                let n = call(
                    0x24001,
                    source.reader,
                    extra.as_mut_ptr() as u64,
                    32,
                    0,
                    0,
                    0,
                )
                .0;
                check(n == 0 || n == -11, 2024); // Poisoned calls must emit no request.
                finish_backend(service);
                check(
                    ctl(0x24003, source.reader).0 == 0 && ctl(0x20002, source.child).0 == 0,
                    1953,
                );
                dispose(child);
                continue;
            }
            check(wait_collected && terminal(source.child) == (71, 1), 2021);
        }
        finish(service, source, child);
    }
    #[cfg(shell_console)]
    {
        finish_backend(console);
        let probe = launch(factory, second, 1);
        check(terminal(probe.child) == (17, 1), 2143);
        dispose(probe);
    }
    end(100)
}

#[cfg(scratch_backend)]
fn scratch_probe(service: Connection, generation: u32, hello: &[u8; 32]) {
    let root = 0xfb000000 | generation;
    check(
        get(hello, 16) == root && get(hello, 20) == generation && hello[24..] == *b"AESCR001",
        2501,
    );
    #[cfg(scratch_owner_probe)]
    {
        scratch_owner_probe(service, generation);
        return;
    }
    #[cfg(not(scratch_owner_probe))]
    {
        let rpc = |op, handle, offset, count, data: &[u8], status: i32| {
            let mut b = [0; 32];
            for (i, value) in [op, handle, offset, count].iter().enumerate() {
                put(&mut b, i * 4, *value);
            }
            b[16..16 + data.len()].copy_from_slice(data);
            send(service, &mut b);
            let r = receive(service);
            check(get(&r, 0) as i32 == status, 2502);
            if status < 0 {
                check(r[4..] == [0; 28], 2502);
            }
            r
        };
        rpc(1, root ^ 1, 0, 14, b"/scratch/data", -13);
        rpc(1, root, 0, 1, b"/scratch/data", -2);
        let opened = rpc(1, root, 0, 14, b"/scratch/data", 0);
        let h = 0xfa000000 | (generation << 16) | 0x101;
        check(get(&opened, 4) == h && opened[8..] == [0; 24], 2502);
        rpc(2, h, 0, 1, b"", -13);
        rpc(4, h, 0, 2, b"AB", 2);
        rpc(3, h, 0, 0, b"", 0);
        rpc(4, h, 0, 1, b"X", -9);
        let opened = rpc(1, root, 0, 1, b"/scratch/data", 0);
        let read = 0xfa000000 | (generation << 16) | 0x201;
        check(
            get(&opened, 4) == read && get(&opened, 8) == 2 && opened[12..] == [0; 20],
            2502,
        );
        rpc(4, read, 0, 1, b"X", -13);
        let r = rpc(2, read, 0, 16, b"", 2);
        check(
            r[4..16] == [0; 12] && r[16..18] == *b"AB" && r[18..] == [0; 14],
            2502,
        );
        rpc(2, read, 2, 16, b"", 0);
        rpc(3, read, 0, 0, b"", 0);
    }
}

#[cfg(scratch_owner_probe)]
fn scratch_owner_probe(service: Connection, generation: u32) {
    let mut owner = crate::scratch_owner::Owner::new(generation);
    let mut rpc = |frame: &[u8; 32]| {
        let mut frame = *frame;
        send(service, &mut frame);
        Some(receive(service))
    };
    check(
        owner.open(0, b"/scratch/data", 1, &mut rpc) == Err(-2),
        2503,
    );
    let parent = owner
        .open(0, b"/scratch/data", 14, &mut rpc)
        .unwrap_or_else(|_| end(2503));
    let mut forbidden = |_: &[u8; 32]| -> Option<[u8; 32]> { end(2504) };
    check(
        owner.io(0, parent, 2, 1, &[], &mut forbidden) == Err(-13),
        2503,
    );
    check(
        owner
            .io(0, parent, 4, 1, b"A", &mut rpc)
            .map(|r| get(&r, 0))
            == Ok(1),
        2503,
    );
    let child = owner
        .inherit(1, [Some(parent), None])
        .unwrap_or_else(|_| end(2503))[0]
        .unwrap_or_else(|| end(2503));
    check(
        parent != child && owner.close(0, parent, &mut rpc).is_ok(),
        2503,
    );
    check(
        owner.io(0, parent, 4, 1, b"X", &mut forbidden) == Err(-9),
        2503,
    );
    check(
        owner.io(1, child, 4, 1, b"B", &mut rpc).map(|r| get(&r, 0)) == Ok(1),
        2503,
    );
    check(owner.close(1, child, &mut rpc).is_ok(), 2503);
    let first = owner
        .open(0, b"/scratch/data", 1, &mut rpc)
        .unwrap_or_else(|_| end(2503));
    let second = owner
        .open(0, b"/scratch/data", 1, &mut rpc)
        .unwrap_or_else(|_| end(2503));
    check(first != second, 2503);
    for (handle, count, bytes) in [
        (first, 1, b"A".as_slice()),
        (first, 1, b"B".as_slice()),
        (second, 16, b"AB".as_slice()),
        (second, 1, b"".as_slice()),
    ] {
        let r = owner
            .io(0, handle, 2, count, &[], &mut rpc)
            .unwrap_or_else(|_| end(2503));
        check(
            get(&r, 0) as usize == bytes.len() && r[16..16 + bytes.len()] == *bytes,
            2503,
        );
    }
    check(
        owner.close(0, first, &mut rpc).is_ok()
            && owner.close(0, second, &mut rpc).is_ok()
            && !owner.poisoned(),
        2503,
    );
}

#[cfg(all(scratch_client, not(scratch_copy)))]
fn scratch_client_run(source: Connection, service: Connection, generation: u32) {
    let mut owner = crate::scratch_owner::Owner::new(generation);
    let mut grant = [0; 32];
    grant[..8].copy_from_slice(b"AESFD001");
    put(&mut grant, 8, owner.root(0).unwrap());
    put(&mut grant, 12, generation);
    put(&mut grant, 16, 3);
    put(&mut grant, 20, 2);
    send(source, &mut grant);
    let mut rpc = |frame: &[u8; 32]| {
        let mut frame = *frame;
        send(service, &mut frame);
        Some(receive(service))
    };
    let mut complete = false;
    for _ in 0..32 {
        let request = receive(source);
        if get(&request, 0) == 96 {
            check(
                request[4..] == [0; 28] && owner.closed() && !owner.poisoned(),
                2505,
            );
            complete = true;
            break;
        }
        let mut reply = owner.gateway(0, &request, &mut rpc);
        send(source, &mut reply);
    }
    check(complete, 2505);
    let h = owner
        .open(0, b"/scratch/data", 1, &mut rpc)
        .unwrap_or_else(|_| end(2505));
    let r = owner
        .io(0, h, 2, 16, &[], &mut rpc)
        .unwrap_or_else(|_| end(2505));
    check(get(&r, 0) == 2 && r[16..18] == *b"AB", 2505);
    let r = owner
        .io(0, h, 2, 1, &[], &mut rpc)
        .unwrap_or_else(|_| end(2505));
    check(
        r == [0; 32] && owner.close(0, h, &mut rpc).is_ok() && owner.closed(),
        2505,
    );
    send(source, &mut [0; 32]);
}

#[cfg(scratch_copy)]
fn scratch_copy_start(
    source: Connection,
    service: Connection,
    generation: u32,
) -> (crate::scratch_owner::Owner, u32) {
    let mut owner = crate::scratch_owner::Owner::new(generation);
    let mut grant = [0; 32];
    grant[..8].copy_from_slice(b"AESFD001");
    put(&mut grant, 8, owner.root(0).unwrap());
    put(&mut grant, 12, generation);
    put(&mut grant, 16, 3);
    put(&mut grant, 20, 2);
    send(source, &mut grant);
    let mut reference = 0;
    for step in 0..3 {
        let request = receive(source);
        if step == 2 {
            check(
                get(&request, 0) == 96
                    && request[4..] == [0; 28]
                    && !owner.closed()
                    && !owner.poisoned(),
                2506,
            );
            send(source, &mut [0; 32]);
            return (owner, reference);
        }
        check(get(&request, 0) == if step == 0 { 6 } else { 2 }, 2506);
        let mut reply = scratch_gateway(service, &mut owner, 0, &request);
        check(get(&reply, 0) == if step == 0 { 0 } else { 1 }, 2506);
        if step == 0 {
            reference = get(&reply, 4);
        }
        send(source, &mut reply);
    }
    end(2506)
}
#[cfg(scratch_copy)]
fn scratch_copy_finish(
    client: Connection,
    service: Connection,
    owner: &mut crate::scratch_owner::Owner,
    peer: usize,
) {
    for _ in 0..5 {
        let request = receive(client);
        if get(&request, 0) == 96 {
            check(request[4..] == [0; 28] && !owner.poisoned(), 2507);
            send(client, &mut [0; 32]);
            return;
        }
        let mut reply = scratch_gateway(service, owner, peer, &request);
        send(client, &mut reply);
    }
    end(2507)
}

#[cfg(scratch_exec)]
fn scratch_exec_replace(
    factory: u64,
    image: u64,
    child: Connection,
    generation: u32,
    boot: &[u8; 128],
    owner: &mut crate::scratch_owner::Owner,
    reference: u32,
    _service: Connection,
) {
    #[cfg(scratch_exec_last)]
    let reader = {
        let mut reference = 0;
        for step in 0..2 {
            let request = receive(child);
            check(get(&request, 0) == if step == 0 { 6 } else { 1 }, 2509);
            let mut reply = scratch_gateway(_service, owner, 1, &request);
            check(get(&reply, 0) == if step == 0 { 0 } else { 1 }, 2509);
            if step == 0 {
                reference = get(&reply, 4);
                check(get(&reply, 8) == 4, 2509);
            } else {
                check(reply[16] == b'A', 2509);
            }
            send(child, &mut reply);
        }
        reference
    };
    let header = receive(child);
    check(get(&header, 0) == 97 && header[4..] == [0; 28], 2508);
    let mut table = [0; 64];
    table[..32].copy_from_slice(&receive(child));
    table[32..].copy_from_slice(&receive(child));
    let mut expected = [0; 64];
    expected[..20].copy_from_slice(&[0, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 3, 1, 1, 0]);
    expected[40..44].copy_from_slice(&[0, 1, 1, 0]);
    #[cfg(scratch_exec_last)]
    expected[20..24].copy_from_slice(&[4, 1, 1, 0]);
    check(
        table == expected && !owner.closed() && !owner.poisoned(),
        2508,
    );
    let plan =
        crate::exec_fds::prepare_files(&table, &[2, 1, 1, 2, u8::from(cfg!(scratch_exec_last))])
            .unwrap_or_else(|_| end(2508));
    check(
        plan.release == [false, false, false, false, cfg!(scratch_exec_last)]
            && plan.users == [1, 1, 1, 1, 0],
        2508,
    );
    let mut frozen = false;
    for _ in 0..10000 {
        let state = ctl(0x23004, child.child).0;
        if state == 1 {
            frozen = true;
            break;
        }
        check(state == 0, 2508);
        ctl(0x1fffe, 0);
    }
    check(frozen, 2508);
    let arguments = args(b"scratch-next");
    #[cfg(scratch_exec_deny)]
    {
        check(
            call(0x23008, factory, child.child, 0, 0, 0, 0) == (0, 0, 0),
            2510,
        );
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
            2510,
        );
        check(
            call(0x23008, factory, child.child, 0, 0, 0, 0) == (0, 0, 0)
                && ctl(0x23004, child.child).0 == 1,
            2510,
        );
        if cfg!(scratch_exec_deny_close) {
            check(
                owner
                    .close(1, reader, &mut |frame| {
                        let mut frame = *frame;
                        send(_service, &mut frame);
                        Some(receive(_service))
                    })
                    .is_ok(),
                2510,
            );
        }
        check(call(0x23005, child.child, 1, 0, 0, 0, 0).0 == 0, 2510);
        let mut reply = [0; 32];
        put(
            &mut reply,
            0,
            if cfg!(scratch_exec_deny_error) {
                -2i32
            } else {
                -13i32
            } as u32,
        );
        send(child, &mut reply);
        for op in [1, 2] {
            let request = receive(child);
            check(get(&request, 0) == op, 2510);
            let mut reply = scratch_gateway(_service, owner, 1, &request);
            check(reply == [0; 32], 2510);
            send(child, &mut reply);
        }
        let retry = receive(child);
        check(retry == header, 2510);
        let first = receive(child);
        let second = receive(child);
        check(first == table[..32] && second == table[32..], 2510);
        let mut parked = false;
        for _ in 0..10000 {
            let state = ctl(0x23004, child.child).0;
            if state == 2 {
                parked = true;
                break;
            }
            check(state == 0, 2510);
            ctl(0x1fffe, 0);
        }
        check(parked, 2510);
    }
    let sequence = if cfg!(scratch_exec_deny) { 2 } else { 1 };
    check(
        call(
            0x23007,
            factory,
            child.child,
            image,
            sequence,
            &arguments as *const Args as u64,
            0,
        )
        .0 == 0,
        2508,
    );
    check(
        call(0x23008, factory, child.child, 0, 0, 0, 0) == (sequence as i64, image, 1),
        2508,
    );
    #[cfg(scratch_exec_last)]
    if !cfg!(scratch_exec_last_skip) {
        let closing = if cfg!(scratch_exec_last_wrong) {
            reference
        } else {
            reader
        };
        check(
            owner
                .close(1, closing, &mut |frame| {
                    let mut frame = *frame;
                    send(_service, &mut frame);
                    Some(receive(_service))
                })
                .is_ok(),
            2509,
        );
    }
    check(
        call(0x23009, factory, child.child, sequence, 0, 0, 0).0 == 0,
        2508,
    );
    let mut boot = *boot;
    send(child, &mut boot);
    let mut grant = [0; 32];
    grant[..8].copy_from_slice(b"AESFD001");
    put(&mut grant, 8, owner.root(1).unwrap());
    put(&mut grant, 12, generation);
    put(&mut grant, 16, 3);
    put(&mut grant, 20, 2);
    send(child, &mut grant);
    let mut survivors = if cfg!(scratch_exec_keep) {
        table
    } else {
        plan.table
    };
    send(child, &mut survivors);
    let mut records = [0; 32];
    put(
        &mut records,
        0,
        if cfg!(scratch_exec_stale) {
            reference ^ 8
        } else {
            reference
        },
    );
    put(&mut records, 4, 14);
    put(&mut records, 8, 1);
    send(child, &mut records);
}

#[cfg(any(scratch_copy, shell_files))]
#[inline(never)]
fn scratch_gateway(
    service: Connection,
    owner: &mut crate::scratch_owner::Owner,
    peer: usize,
    request: &[u8; 32],
) -> [u8; 32] {
    owner.gateway(peer, request, &mut |frame| {
        let mut frame = *frame;
        send(service, &mut frame);
        Some(receive(service))
    })
}

#[cfg(shell_files)]
fn scratch_bootstrap(client: Connection, owner: &crate::scratch_owner::Owner, peer: usize) {
    let root = owner.root(peer).unwrap_or_else(|| end(2506));
    let mut grant = [0; 32];
    grant[..8].copy_from_slice(b"AESFD001");
    put(&mut grant, 8, root);
    put(&mut grant, 12, (root >> 8) & 255);
    put(&mut grant, 16, 3);
    put(&mut grant, 20, 2);
    send(client, &mut grant);
}
