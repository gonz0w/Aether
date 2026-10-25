// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
#[cfg(not(pipeline_dash_parent))]
compile_error!("SESSION requires the parent-slot directory profile: --cfg pipeline_dash_parent");
#[cfg(all(session_lifecycle, not(session_serial)))]
compile_error!("SESSION lifecycle requires session_serial");
use core::arch::asm;
#[path = "session_children.rs"]
mod children;
#[path = "../native-connections/exec_fds.rs"]
mod descriptors;
#[path = "session_exec.rs"]
mod exec;
#[path = "../native-connections/pipe.rs"]
mod pipe;
#[path = "../native-connections/pipeline.rs"]
mod pipeline;
#[cfg(session_scratch)]
mod session_scratch;
#[path = "startup.rs"]
mod startup;
const BINDINGS: usize = if cfg!(session_scratch) { 9 } else { 7 };
// The full snapshot is validated before files are removed from the pipe view.
fn pipe_table(table: &[u8; 64]) -> [u8; 64] {
    let mut view = *table;
    for r in view.chunks_exact_mut(4) {
        if r[0] >= 7 {
            r.fill(0);
        }
    }
    view
}
use children::{Children, Identity, Wait};
use pipe::{Caller, Outcome, SessionPipe};

#[inline(never)]
fn call(op: u64, a: u64, b: u64, c: u64, d: u64, e: u64, f: u64) -> (i64, u64, u64) {
    let r: i64;
    let x: u64;
    let k: u64;
    // Registers contain scalars or synchronously borrowed, live buffers.
    unsafe {
        asm!("int 0x81",inlateout("rax")op=>r,in("rdi")a,in("rsi")b,inlateout("rdx")c=>x,in("r10")d,inlateout("r8")e=>k,in("r9")f,lateout("rcx")_,options(nostack));
    }
    (r, x, k)
}
fn ctl(op: u64, h: u64) -> (i64, u64, u64) {
    call(op, h, 0, 0, 0, 0, 0)
}
fn end(code: u64) -> ! {
    if cfg!(session_lifecycle) {
        // Keep unknown-effect resources owned on failure; do not pretend to halt.
        for byte in b"SESSION owner failed\n" {
            call(0x26001, 0xf001, byte as *const u8 as u64, 1, 0, 0, 0);
        }
        unsafe { asm!("ud2", options(noreturn)) }
    }
    ctl(0x20006, code);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool) {
    if !ok {
        end(2820);
    }
}
fn observe() -> u64 {
    if cfg!(session_lifecycle) {
        let snapshot = ctl(0x2a000, 0xe002);
        check(snapshot.0 == 0);
        snapshot.1
    } else {
        0
    }
}
fn pause(sequence: u64) {
    if cfg!(session_lifecycle) {
        check(call(0x2a001, 0xe002, sequence, 0, 0, 0, 0).0 == 0);
    } else {
        ctl(0x1fffe, 0);
    }
}
// Only legacy fixtures retain an iteration budget.009 waits for owned events.
fn attempt(attempts: &mut u32) {
    if !cfg!(session_lifecycle) {
        if *attempts == 100000 {
            end(2821);
        }
        *attempts += 1;
    }
}
fn word(f: &[u8], at: usize) -> u32 {
    u32::from_le_bytes(f[at..at + 4].try_into().unwrap())
}
fn put(f: &mut [u8], at: usize, value: u32) {
    f[at..at + 4].copy_from_slice(&value.to_le_bytes());
}
fn reply(code: i32) -> [u8; 32] {
    let mut f = [0; 32];
    put(&mut f, 0, code as u32);
    f
}
fn transfer(channel: u64, bytes: &mut [u8], write: bool) {
    let mut used = 0;
    let mut attempts = 0;
    loop {
        attempt(&mut attempts);
        let observed = observe();
        let n = call(
            if write { 0x24002 } else { 0x24001 },
            channel,
            bytes[used..].as_mut_ptr() as u64,
            (bytes.len() - used).min(16) as u64,
            0,
            0,
            0,
        )
        .0;
        if n == -11 {
            pause(observed);
            continue;
        }
        check(n > 0 && n as usize <= (bytes.len() - used).min(16));
        used += n as usize;
        if used == bytes.len() {
            return;
        }
    }
}
fn slot(peer: usize) -> usize {
    if peer == 0 { 0 } else { peer + 1 }
}
fn identity(peer: usize, p: &Peer) -> Identity {
    Identity::admitted(slot(peer), p.epoch, p.handle).unwrap_or_else(|_| end(2820))
}
fn caller(peer: usize, p: &Peer) -> Caller {
    if peer == 0 {
        Caller::Parent
    } else {
        Caller::Participant {
            slot: peer,
            generation: p.epoch,
        }
    }
}

#[derive(Clone, Copy)]
struct Peer {
    handle: u64,
    reader: u64,
    writer: u64,
    epoch: u32,
    frame: [u8; 32],
    used: usize,
    replying: bool,
    terminal: bool,
    denied: u8,
    collected: bool,
    standard: [bool; 3],
    wait: Option<Identity>,
}
impl Peer {
    const fn new() -> Self {
        Self {
            handle: 0,
            reader: 0,
            writer: 0,
            epoch: 0,
            frame: [0; 32],
            used: 0,
            replying: false,
            terminal: false,
            denied: 0,
            collected: false,
            standard: [false; 3],
            wait: None,
        }
    }
}
struct Session {
    #[cfg(session_scratch)]
    scratch: session_scratch::Scratch,
    peers: [Peer; 4],
    pipes: [SessionPipe; 2],
    epochs: [Option<u32>; 2],
    children: Children,
    shell: u32,
    record: [u8; 176],
    changed: bool,
    parent_status: i32,
    denials: u8,
    bad_denial: bool,
    #[cfg(session_serial)]
    serial_stop: bool,
}
impl Session {
    fn new() -> Self {
        Self {
            #[cfg(session_scratch)]
            scratch: session_scratch::Scratch::new(1),
            peers: [Peer::new(); 4],
            pipes: [SessionPipe::new(), SessionPipe::new()],
            epochs: [None; 2],
            children: Children::new(),
            shell: 0,
            record: [0; 176],
            changed: false,
            parent_status: 0,
            denials: 0,
            bad_denial: false,
            #[cfg(session_serial)]
            serial_stop: false,
        }
    }
    fn channels(&mut self, peer: usize) -> (u64, u64) {
        let req = ctl(0x24000, 0xd001);
        let rep = ctl(0x24000, 0xd001);
        check(req.0 > 0 && rep.0 > 0);
        let p = &mut self.peers[peer];
        p.reader = rep.0 as u64;
        p.writer = req.1;
        (req.0 as u64, rep.1)
    }
    #[inline(never)]
    fn description(&mut self, peer: usize, table: &mut [u8; 64]) {
        let p = self.peers[peer];
        let mut id = [0; 16];
        put(&mut id, 0, slot(peer) as u32);
        put(&mut id, 4, p.epoch);
        put(&mut id, 8, self.shell * 6 + 1);
        put(&mut id, 12, self.shell);
        transfer(p.writer, &mut id, true);
        transfer(p.writer, table, true);
        for binding in 0..BINDINGS {
            let held = table
                .chunks_exact(4)
                .any(|r| r[2] == 1 && r[0] as usize == binding);
            let mut f = [0; 16];
            if held {
                #[cfg(session_scratch)]
                if binding >= 7 {
                    let (reference, rights) = self
                        .scratch
                        .binding(peer, binding - 7)
                        .unwrap_or_else(|| end(2820));
                    put(&mut f, 0, reference);
                    put(&mut f, 4, binding as u32);
                    put(&mut f, 8, rights as u32);
                    put(&mut f, 12, 16);
                    transfer(p.writer, &mut f, true);
                    continue;
                }
                let reference = if binding < 3 {
                    0x7a000000 | ((binding as u32) << 16) | self.shell
                } else {
                    0x79000000
                        | (((binding - 3) / 2) as u32) << 16
                        | (self.epochs[(binding - 3) / 2].unwrap() << 8)
                        | (((binding - 3) % 2 + 1) as u32)
                };
                put(&mut f, 0, reference);
                put(&mut f, 4, binding as u32);
                put(
                    &mut f,
                    8,
                    if binding == 0 || binding == 3 || binding == 5 {
                        1
                    } else {
                        2
                    },
                );
                put(&mut f, 12, 16);
            }
            transfer(p.writer, &mut f, true);
        }
        #[cfg(session_scratch)]
        {
            let mut root = [0; 16];
            put(&mut root, 0, self.scratch.root());
            transfer(p.writer, &mut root, true);
        }
        self.ready(peer);
    }
    fn ready(&mut self, peer: usize) {
        let p = self.peers[peer];
        let mut data = [0; 16];
        transfer(p.reader, &mut data, false);
        check(
            u64::from_le_bytes(data[..8].try_into().unwrap())
                == (p.epoch * 6 + slot(peer) as u32 + 1) as u64,
        );
        check(u64::from_le_bytes(data[8..].try_into().unwrap()) == slot(peer) as u64 + 1);
        let mut attempts = 0;
        loop {
            attempt(&mut attempts);
            let observed = observe();
            let status = ctl(0x20001, p.handle);
            check(status.0 == 0);
            if status.1 == 1 {
                return;
            }
            pause(observed);
        }
    }
    fn frozen(&self, peer: usize) -> u64 {
        let mut attempts = 0;
        loop {
            attempt(&mut attempts);
            let observed = observe();
            let r = ctl(0x23004, self.peers[peer].handle).0;
            check(r >= 0);
            if r > 0 {
                return r as u64;
            }
            pause(observed);
        }
    }
    fn users(table: &[u8; 64]) -> [u8; BINDINGS] {
        let mut users = [0; BINDINGS];
        for r in table.chunks_exact(4) {
            if r[2] == 1 && (r[0] as usize) < BINDINGS {
                users[r[0] as usize] += 1;
            }
        }
        check(descriptors::prepare_bindings(table, &users).is_ok());
        users
    }
    #[inline(never)]
    fn fork(&mut self) {
        if cfg!(session_recovery) && [2, 3, 6].contains(&word(&self.record, 8)) {
            check(self.peers[1..].iter().all(|p| p.handle == 0));
            // The healthy pipeline creates its new pipes before its first fork.
            if word(&self.record, 8) != 3 {
                check(self.epochs == [None; 2]);
            }
        }
        if cfg!(session_failed_exec) && [1, 2, 3, 6].contains(&word(&self.record, 8)) {
            check(self.peers[1..].iter().all(|p| p.handle == 0));
            if word(&self.record, 8) != 3 {
                check(self.epochs == [None; 2]);
            }
            if word(&self.record, 8) <= 2 {
                check(self.denials as u32 == word(&self.record, 8));
            }
        }
        let mut table = [0; 64];
        transfer(self.peers[0].reader, &mut table, false);
        let sequence = self.frozen(0);
        let users = Self::users(&table);
        let peer = (1..4)
            .find(|&p| self.peers[p].handle == 0)
            .unwrap_or_else(|| end(2822));
        let epoch = self.peers[peer].epoch + 1;
        check((0..3).all(|b| (users[b] != 0) == self.peers[0].standard[b]));
        #[cfg(session_scratch)]
        check(self.scratch.check(0, &users).is_ok());
        check(
            pipeline::stage_fork(
                &mut self.pipes,
                peer,
                epoch,
                self.epochs,
                &pipe_table(&table),
                users[..7].try_into().unwrap(),
            )
            .is_ok(),
        );
        let (reader, writer) = self.channels(peer);
        let h = call(
            0x23006,
            0xa001,
            self.peers[0].handle,
            slot(peer) as u64,
            sequence,
            reader,
            writer,
        )
        .0;
        let id = Identity::admitted(slot(peer), epoch, h as u64).unwrap_or_else(|_| end(2822));
        self.children.admit(id).unwrap_or_else(|_| end(2822));
        #[cfg(session_scratch)]
        check(self.scratch.inherit(0, peer, &users).is_ok());
        self.peers[peer].handle = id.handle;
        self.peers[peer].epoch = epoch;
        self.peers[peer].standard = [users[0] != 0, users[1] != 0, users[2] != 0];
        let mut identity = [0; 16];
        put(&mut identity, 0, id.slot as u32);
        put(&mut identity, 4, epoch);
        put(&mut identity, 8, self.shell * 6 + 1);
        put(&mut identity, 12, self.shell);
        transfer(self.peers[peer].writer, &mut identity, true);
        self.ready(peer);
        check(pipeline::finish_copy(&mut self.pipes, peer, epoch, true).is_ok());
        let r = &mut self.record;
        let n = word(r, 8);
        put(r, 8, n + 1);
    }
    #[inline(never)]
    fn replace(&mut self, peer: usize, header: [u8; 32]) {
        check(peer != 0);
        let mut path = [0; 32];
        if cfg!(session_failed_exec) {
            transfer(self.peers[peer].reader, &mut path, false);
        }
        let mut vector = [0; 272];
        transfer(self.peers[peer].reader, &mut vector, false);
        let mut error = if cfg!(session_failed_exec) {
            exec::lookup(&header, &path, &vector).map(|image| check(image == exec::HELPER))
        } else {
            exec::header(&header).and_then(|_| exec::arguments(&vector))
        };
        if cfg!(session_failed_exec) && word(&self.record, 8) <= 2 {
            let count = word(&self.record, 8);
            check(peer == 1 && count == self.denials as u32 + 1);
            check(error == Err(if count == 1 { -2 } else { -13 }));
            check(call(0x23008, 0xa001, self.peers[peer].handle, 0, 0, 0, 0) == (0, 0, 0));
            self.peers[peer].denied = if count == 1 { 127 } else { 126 };
            self.denials += 1;
            if (cfg!(exec_wrong_missing) && count == 1) || (cfg!(exec_wrong_denied) && count == 2) {
                error = Err(if count == 1 { -13 } else { -2 });
                self.peers[peer].denied = if count == 1 { 126 } else { 127 };
                self.changed = true;
            }
        }
        if let Err(code) = error {
            self.peers[peer].frame = reply(code);
            self.peers[peer].replying = true;
            self.peers[peer].used = 0;
            return;
        }
        transfer(self.peers[peer].writer, &mut [0; 32], true);
        let mut table = [0; 64];
        transfer(self.peers[peer].reader, &mut table, false);
        let sequence = self.frozen(peer);
        let users = Self::users(&table);
        check((0..3).all(|b| (users[b] != 0) == self.peers[peer].standard[b]));
        let who = caller(peer, &self.peers[peer]);
        // Validate on a private copy before native image admission, then commit
        // the same immutable descriptor snapshot before publishing execution.
        let mut plan = descriptors::prepare_bindings(&table, &users).unwrap_or_else(|_| end(2823));
        for index in 0..2 {
            check(
                self.pipes[index]
                    .check_bindings(
                        who,
                        self.epochs[index],
                        [users[3 + 2 * index] != 0, users[4 + 2 * index] != 0],
                    )
                    .is_ok(),
            );
        }
        #[cfg(session_scratch)]
        check(self.scratch.check(peer, &users).is_ok());
        let h = self.peers[peer].handle;
        check(
            call(
                0x23007,
                0xa001,
                h,
                0xc002,
                sequence,
                vector.as_ptr() as u64,
                0,
            )
            .0 == 0,
        );
        check(call(0x23008, 0xa001, h, 0, 0, 0, 0) == (sequence as i64, 0xc002, 1));
        check(
            pipeline::commit_exec(
                &mut self.pipes,
                who,
                self.epochs,
                &pipe_table(&table),
                users[..7].try_into().unwrap(),
            )
            .is_ok(),
        );
        #[cfg(session_scratch)]
        check(self.scratch.commit(peer, &users, &plan.users).is_ok());
        self.peers[peer].standard = [plan.users[0] != 0, plan.users[1] != 0, plan.users[2] != 0];
        check(call(0x23009, 0xa001, h, sequence, 0, 0, 0).0 == 0);
        self.description(peer, &mut plan.table);
        let r = &mut self.record;
        let n = word(r, 12);
        put(r, 12, n + 1);
    }
    fn io(&mut self, peer: usize, frame: &[u8; 32]) -> Outcome {
        let binding = word(frame, 8) as usize;
        #[cfg(session_scratch)]
        if binding >= 7 {
            return Outcome::Reply(self.scratch.request(peer, frame));
        }
        if binding >= 3 {
            // Deliberate test-only mutations operate on real requests/holders.
            let mut outcome =
                pipeline::request(&mut self.pipes, caller(peer, &self.peers[peer]), frame);
            if cfg!(session_bad_substitution) && !self.changed && peer == 0 && word(frame, 0) == 1 {
                if let Outcome::Reply(r) = &mut outcome {
                    if word(r, 0) as i32 > 0 {
                        r[16] ^= 1;
                        self.changed = true;
                    }
                }
            }
            if cfg!(recovery_wrong_epipe) {
                if let Outcome::Reply(r) = &mut outcome {
                    if word(r, 0) as i32 == -32 {
                        put(r, 0, (-5i32) as u32);
                        self.changed = true;
                    }
                }
            }
            return outcome;
        }
        if cfg!(scratch_stderr_error) && peer == 0 && binding == 2 && word(frame, 0) == 2 {
            self.peers[peer].standard[2] = false;
            self.changed = true;
        }
        if cfg!(serial_stderr_error)
            && peer == 0
            && binding == 2
            && word(frame, 0) == 2
            && word(&self.record, 8) == 9
        {
            self.peers[peer].standard[2] = false;
            self.changed = true;
        }
        if cfg!(exec_stderr_error)
            && peer == 0
            && binding == 2
            && word(frame, 0) == 2
            && self.denials == 2
        {
            self.changed = true;
            // Retire the parent's actual owner-held stderr binding. The normal
            // authority check below then denies this write; no fabricated byte
            // count or dropped observation stands in for a closed stream.
            self.peers[peer].standard[2] = false;
        }
        let op = word(frame, 0);
        let n = word(frame, 12) as usize;
        if !self.peers[peer].standard[binding]
            || word(frame, 4) != 0x7a000000 | ((binding as u32) << 16) | self.shell
        {
            return Outcome::Reply(reply(-13));
        }
        if !(1..=3).contains(&op)
            || n > 16
            || (op == 3 && n != 0)
            || frame[16 + if op == 2 { n } else { 0 }..]
                .iter()
                .any(|&b| b != 0)
        {
            return Outcome::Reply(reply(-22));
        }
        if op == 3 {
            self.peers[peer].standard[binding] = false;
            return Outcome::Reply(reply(0));
        }
        if binding == 0 {
            #[cfg(session_serial)]
            if op == 1 {
                check(peer == 0);
                let mut r = [0; 32];
                let got = call(
                    0x26000,
                    0xf001,
                    r[16..].as_mut_ptr() as u64,
                    n.min(1) as u64,
                    0,
                    0,
                    0,
                )
                .0;
                if got == -11 {
                    if cfg!(serial_cancel)
                        && word(&self.record, 8) == 4
                        && word(&self.record, 12) == 3
                        && self.peers[1..].iter().all(|p| p.handle == 0)
                        && self.epochs == [None; 2]
                    {
                        self.serial_stop = true;
                    }
                    return Outcome::Pending;
                }
                check(got >= 0 && got as usize <= n.min(1) && (n == 0 || got > 0));
                put(&mut r, 0, got as u32);
                return Outcome::Reply(r);
            }
            return Outcome::Reply(reply(if op == 1 { 0 } else { -13 }));
        }
        if op != 2 {
            return Outcome::Reply(reply(-13));
        }
        #[cfg(session_serial)]
        if peer == 0 && binding == 2 && n == 2 && frame[16..18] == *b"$ " {
            // Interactive parsing may request more bytes while assembling a job.
            // A returned prompt, rather than every read, is the phase boundary.
            check(self.peers[1..].iter().all(|p| p.handle == 0) && self.epochs == [None; 2]);
        }
        let (offset, capacity, index) = if binding == 1 {
            (16, 128, 0)
        } else {
            (144, 32, 4)
        };
        let used = word(&self.record, index) as usize;
        // Reject before forwarding any byte when the observation cannot retain it.
        if !cfg!(session_lifecycle)
            && (if cfg!(session_serial) { n.min(1) } else { n }) > capacity - used
        {
            return Outcome::Reply(reply(-28));
        }
        #[cfg(session_serial)]
        let n = {
            let mut byte = frame[16];
            if cfg!(serial_bad_byte) && binding == 1 && byte == b'p' {
                byte = b'P';
            }
            let got = call(
                0x26001,
                if cfg!(serial_wrong_grant) {
                    0xf002
                } else {
                    0xf001
                },
                &byte as *const u8 as u64,
                n.min(1) as u64,
                0,
                0,
                0,
            )
            .0;
            if cfg!(serial_wrong_grant) {
                check(got == -13);
                self.serial_stop = true;
                return Outcome::Pending;
            }
            if got == -11 {
                return Outcome::Pending;
            }
            check(got >= 0 && got as usize <= n.min(1));
            got as usize
        };
        if !cfg!(session_lifecycle) {
            let r = &mut self.record;
            r[offset + used..offset + used + n].copy_from_slice(&frame[16..16 + n]);
            put(r, index, (used + n) as u32);
        }
        Outcome::Reply(reply(n as i32))
    }
    #[inline(never)]
    fn terminal(&mut self, peer: usize) -> bool {
        if self.peers[peer].terminal {
            return true;
        }
        let t = ctl(0x20001, self.peers[peer].handle);
        check(t.0 >= 0);
        if t.0 == 0 {
            return false;
        }
        let status = if t.2 == 1 && (1..=256).contains(&t.0) {
            ((t.0 - 1) as i32) << 8
        } else if t.2 == 3 && t.0 == 144 {
            15
        } else {
            end(2824)
        };
        if cfg!(session_failed_exec) && peer != 0 && word(&self.record, 8) <= 2 {
            if self.peers[peer].denied == 0 || status != (self.peers[peer].denied as i32) << 8 {
                self.bad_denial = true;
            }
            check(call(0x23008, 0xa001, self.peers[peer].handle, 0, 0, 0, 0) == (0, 0, 0));
        }
        #[cfg(session_scratch)]
        {
            if peer != 0 && word(&self.record, 8) == 1 {
                if self.peers[peer].denied != 2 || status != 2 << 8 {
                    self.bad_denial = true;
                }
                check(call(0x23008, 0xa001, self.peers[peer].handle, 0, 0, 0, 0) == (0, 0, 0));
            }
            check(self.scratch.terminal(peer).is_ok());
        }
        self.peers[peer].terminal = true;
        if peer != 0 {
            self.children
                .terminal(identity(peer, &self.peers[peer]), status)
                .unwrap_or_else(|_| end(2820));
            check(
                pipeline::confirmed_terminal(&mut self.pipes, caller(peer, &self.peers[peer]))
                    .is_ok(),
            );
        }
        if peer == 0 {
            self.parent_status = status;
            if status != 0 {
                check(pipeline::confirmed_terminal(&mut self.pipes, Caller::Parent).is_ok());
            }
        }
        self.peers[peer].standard = [false; 3];
        self.peers[peer].frame = [0; 32];
        self.peers[peer].used = 0;
        self.peers[peer].replying = false;
        true
    }
    fn reclaim(&mut self, peer: usize) {
        let p = self.peers[peer];
        check(p.terminal && (peer == 0 || p.collected));
        check(ctl(0x24003, p.reader).0 == 0 && ctl(0x24003, p.writer).0 == 0);
        check(ctl(0x20002, p.handle).0 == 0 && ctl(0x20001, p.handle).0 == -9);
        if peer != 0 {
            self.children
                .reclaimed(identity(peer, &p))
                .unwrap_or_else(|_| end(2820));
        }
        self.peers[peer] = Peer {
            epoch: p.epoch,
            ..Peer::new()
        };
    }
    fn poll(&mut self, peer: usize) -> bool {
        if self.peers[peer].handle == 0 {
            return false;
        }
        let was_terminal = self.peers[peer].terminal;
        if self.terminal(peer) {
            if peer != 0 && self.peers[peer].collected {
                self.reclaim(peer);
                return true;
            }
            return !was_terminal;
        }
        let mut progress = false;
        let p = &mut self.peers[peer];
        if p.replying {
            let n = call(
                0x24002,
                p.writer,
                p.frame[p.used..].as_ptr() as u64,
                (32 - p.used).min(16) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 {
                return false;
            }
            if n == -32 {
                // Exit may close the peer between observation and this trap.
                // EPIPE alone is not terminal evidence or permission to reclaim.
                check(self.terminal(peer));
                return true;
            }
            check(n > 0 && n as usize <= (32 - p.used).min(16));
            p.used += n as usize;
            if p.used == 32 {
                if let Some(id) = p.wait.take() {
                    self.children.delivered(id).unwrap_or_else(|_| end(2820));
                    self.peers[id.slot - 1].collected = true;
                }
                let p = &mut self.peers[peer];
                p.used = 0;
                p.replying = false;
                p.frame = [0; 32];
            }
            return true;
        }
        if p.used < 32 {
            let n = call(
                0x24001,
                p.reader,
                p.frame[p.used..].as_mut_ptr() as u64,
                (32 - p.used).min(16) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 {
                return false;
            }
            if n == 0 {
                // Revalidate the same held task after a racing writer close.
                // A live peer's EOF remains an owner invariant failure.
                check(self.terminal(peer));
                return true;
            }
            check(n > 0 && n as usize <= (32 - p.used).min(16));
            p.used += n as usize;
            progress = true;
            if p.used < 32 {
                return true;
            }
        }
        #[allow(unused_mut)]
        let mut frame = p.frame;
        // Deliberate native routing control: use the actual stdout binding.
        if cfg!(serial_stderr_route)
            && peer == 0
            && word(&self.record, 8) == 9
            && word(&frame, 0) == 2
            && word(&frame, 8) == 2
        {
            put(&mut frame, 4, 0x7a010000 | self.shell);
            put(&mut frame, 8, 1);
            self.changed = true;
        }
        let outcome = match word(&frame, 0) {
            83 if peer == 0 => {
                check(word(&frame, 4) == 64 && frame[8..] == [0; 24]);
                self.fork();
                self.peers[0].used = 0;
                self.peers[0].frame = [0; 32];
                return true;
            }
            op if peer != 0 && op == if cfg!(session_failed_exec) { 85 } else { 84 } => {
                self.peers[peer].used = 0;
                self.peers[peer].frame = [0; 32];
                self.replace(peer, frame);
                return true;
            }
            68 if peer == 0 => {
                check(frame[12..] == [0; 20] && word(&frame, 8) <= 1);
                match self
                    .children
                    .wait(word(&frame, 4) as i32, word(&frame, 8) == 1)
                    .unwrap_or_else(|_| end(2820))
                {
                    Wait::Pending => Outcome::Pending,
                    Wait::NoChange => Outcome::Reply(reply(0)),
                    Wait::NoChild => {
                        if cfg!(session_stale_accept)
                            && word(&self.record, 8) == 4
                            && word(&frame, 4) == 9
                            && self.peers[1..].iter().all(|p| p.handle != 0)
                        {
                            self.changed = true;
                            Outcome::Reply(reply(9))
                        } else {
                            Outcome::Reply(reply(-10))
                        }
                    }
                    Wait::Ready { identity, status } => {
                        let mut r = reply(identity.pid);
                        put(&mut r, 4, status as u32);
                        self.peers[0].wait = Some(identity);
                        Outcome::Reply(r)
                    }
                }
            }
            82 if peer == 0 => {
                let mut result = Outcome::Reply(reply(-23));
                for object in [pipeline::Object::First, pipeline::Object::Second] {
                    result = pipeline::create(&mut self.pipes, object, Caller::Parent, &frame);
                    if let Outcome::Reply(r) = &result {
                        if word(r, 0) == 0 {
                            self.epochs[object.index()] = Some(word(r, 4));
                            break;
                        }
                        if word(r, 0) as i32 != -23 {
                            break;
                        }
                    }
                }
                result
            }
            4 | 5 if peer == 0 => Outcome::Reply(startup::directory(0, self.shell, &frame)),
            #[cfg(session_scratch)]
            86 => {
                let before = self.scratch.denied;
                let mut result = self.scratch.request(peer, &frame);
                if self.scratch.denied != before {
                    check(peer == 1 && word(&self.record, 8) == 1 && before == 0);
                    check(word(&result, 0) as i32 == -13 && result[4..] == [0; 28]);
                    self.peers[peer].denied = 2;
                    if cfg!(scratch_wrong_denied) {
                        result = reply(-2);
                        self.changed = true;
                    }
                }
                Outcome::Reply(result)
            }
            1..=3 => self.io(peer, &frame),
            _ => Outcome::Reply(reply(-38)),
        };
        if let Outcome::Reply(frame) = outcome {
            let p = &mut self.peers[peer];
            p.frame = frame;
            p.used = 0;
            p.replying = true;
            progress = true;
        }
        progress
    }
    #[inline(never)]
    fn launch_parent(&mut self, generation: u32) {
        let (reader, writer) = self.channels(0);
        let mut args = [0; 272];
        args[0] = 1;
        args[16..18].copy_from_slice(b"sh");
        let h = call(
            0x23002,
            0xa001,
            0xc001,
            0,
            args.as_ptr() as u64,
            reader,
            writer,
        )
        .0;
        check(h == (0xb0000001 | (generation as u64) << 8) as i64);
        self.peers[0].handle = h as u64;
        self.peers[0].epoch = generation;
        self.peers[0].standard = [true; 3];
        let mut table = [0; 64];
        for binding in 0..3 {
            table[binding * 4] = binding as u8;
            table[binding * 4 + 2] = 1;
        }
        self.description(0, &mut table);
    }
    #[cfg(session_serial)]
    fn close_serial(&self) {
        check(ctl(0x26002, 0xf001).0 == 0);
        check(call(0x26000, 0xf001, 0, 0, 0, 0, 0).0 == -9);
        check(call(0x26001, 0xf001, 0, 0, 0, 0, 0).0 == -9);
    }
    // Cancellation never releases backing on stop acceptance alone.
    #[inline(never)]
    fn stop(&mut self, peer: usize) {
        if self.peers[peer].handle == 0 || self.terminal(peer) {
            return;
        }
        check(ctl(0x20007, self.peers[peer].handle).0 == 0);
        let mut attempts = 0;
        loop {
            attempt(&mut attempts);
            let observed = observe();
            if self.terminal(peer) {
                return;
            }
            pause(observed);
        }
    }
    #[inline(never)]
    fn orphan_cleanup(&mut self) {
        check(self.peers[0].terminal);
        self.peers[0].wait = None;
        for peer in 1..4 {
            if self.peers[peer].handle == 0 {
                continue;
            }
            self.stop(peer);
            if !self.peers[peer].collected {
                self.children
                    .abandon_after_parent_terminal(identity(peer, &self.peers[peer]))
                    .unwrap_or_else(|_| end(2820));
                self.peers[peer].collected = true;
            }
            self.reclaim(peer);
        }
    }
    fn retained_reader_blocked(&self) -> bool {
        word(&self.record, 8) == 2
            && word(&self.record, 12) == 2
            && self.peers[0].used == 32
            && !self.peers[0].replying
            && word(&self.peers[0].frame, 0) == 68
            && self.peers[1].used == 32
            && !self.peers[1].replying
            && word(&self.peers[1].frame, 0) == 2
            && (self.peers[2].terminal || self.peers[2].handle == 0)
            && self.pipes[0]
                .check_bindings(Caller::Parent, Some(1), [true, false])
                .is_ok()
    }
    fn retained_writer_blocked(&self) -> bool {
        word(&self.record, 8) == 4
            && word(&self.record, 12) == 3
            && self.peers[0].used == 32
            && !self.peers[0].replying
            && word(&self.peers[0].frame, 0) == 68
            && (self.peers[1].terminal || self.peers[1].handle == 0)
            && [2, 3].iter().all(|&p| {
                self.peers[p].used == 32
                    && !self.peers[p].replying
                    && word(&self.peers[p].frame, 0) == 1
            })
            && self.pipes[0]
                .check_bindings(Caller::Parent, Some(1), [false, true])
                .is_ok()
    }
    #[inline(never)]
    fn observation_probes(&self) {
        let pointer = self.record.as_ptr() as u64;
        check(call(0x2000a, 0xa002, pointer, 176, 1, 0, 0).0 == -13);
        check(call(0x2000a, 0xa001, pointer, 175, 1, 0, 0).0 == -22);
        check(call(0x2000a, 0xa001, pointer, 176, 1, 1, 0).0 == -22);
        check(call(0x2000a, 0xa001, pointer, 176, 0, 0, 0).0 == -9);
        check(call(0x2000a, 0xa001, 0, 176, 1, 0, 0).0 == -14);
        check(call(0x2000a, 0xa001, u64::MAX - 16, 176, 1, 0, 0).0 == -14);
        let mut invalid = [0u8; 176];
        invalid[175] = 1;
        check(call(0x2000a, 0xa001, invalid.as_ptr() as u64, 176, 1, 0, 0).0 == -22);
        // Well-formed but no reclaimed parent: must not publish an observation.
        check(call(0x2000a, 0xa001, pointer, 176, 1, 0, 0).0 == -22);
        if cfg!(session_serial) {
            let mut byte = 0u8;
            check(call(0x26000, 0xf002, &mut byte as *mut u8 as u64, 1, 0, 0, 0).0 == -13);
            check(call(0x26000, 0xf001, &mut byte as *mut u8 as u64, 1, 0, 0, 0).0 == -11);
        } else {
            check(call(0x26000, 0xf001, 0, 0, 0, 0, 0).0 == -38);
        }
    }
    fn pump(&mut self) -> (bool, bool) {
        let mut progress = false;
        // Children first: terminal observations can satisfy the parent's wait.
        for peer in [1, 2, 3, 0] {
            if peer == 0 && self.bad_denial && !self.peers[0].terminal {
                self.stop(0);
            }
            #[cfg(session_serial)]
            if peer == 0 && self.serial_stop && !self.peers[0].terminal {
                self.stop(0);
            }
            progress |= self.poll(peer);
        }
        if (cfg!(session_retained_writer) && self.retained_writer_blocked())
            || (cfg!(recovery_retained_reader) && self.retained_reader_blocked())
        {
            self.changed = true;
            self.stop(0);
        }
        if self.peers[0].terminal {
            self.orphan_cleanup();
        }
        for object in 0..2 {
            let pending = core::array::from_fn(|peer| {
                self.peers[peer].used != 0 || self.peers[peer].replying
            });
            if self.pipes[object].retire_if_idle(pending) {
                progress = true;
                self.epochs[object] = None;
            }
        }
        if self.peers[0].terminal && self.peers[1..].iter().all(|p| p.handle == 0) {
            self.reclaim(0);
            check(self.epochs == [None; 2]);
            return (true, true);
        }
        (false, progress)
    }
    #[cfg(session_lifecycle)]
    fn run_lifecycle(&mut self) {
        self.shell = 1;
        self.launch_parent(1);
        loop {
            // Observe before draining: publications during the scan cannot be lost.
            let observed = observe();
            let (done, progress) = self.pump();
            if done {
                return;
            }
            if !progress {
                pause(observed);
            }
        }
    }
    fn run(&mut self) {
        self.observation_probes();
        for generation in 1..=3 {
            #[cfg(session_scratch)]
            {
                check(self.scratch.idle());
                self.scratch = session_scratch::Scratch::new(generation as u8);
            }
            self.shell = generation;
            self.record = [0; 176];
            self.denials = 0;
            self.launch_parent(generation);
            check(
                call(
                    0x2000a,
                    0xa001,
                    self.record.as_ptr() as u64,
                    176,
                    generation as u64,
                    0,
                    0,
                )
                .0 == -16,
            );
            let mut done = false;
            for _ in 0..100000 {
                if self.pump().0 {
                    done = true;
                    break;
                }
                ctl(0x1fffe, 0);
            }
            check(done);
            let r = &self.record;
            let (copies, execs, status, result) = if cfg!(serial_cancel) {
                (4, 3, 15, 2890)
            } else if cfg!(serial_wrong_grant) {
                (0, 0, 15, 2891)
            } else if cfg!(serial_stderr_error) {
                check(self.changed);
                (9, 7, 141 << 8, 2892)
            } else if cfg!(session_scratch) {
                #[cfg(session_scratch)]
                check(self.scratch.idle());
                if self.bad_denial {
                    (1, 0, 15, 2884)
                } else if cfg!(scratch_early_close) {
                    (0, 0, 141 << 8, 2885)
                } else if cfg!(scratch_wrong_env) {
                    (3, 2, 66 << 8, 2886)
                } else if cfg!(scratch_fd_leak) {
                    (7, 5, 68 << 8, 2887)
                } else if cfg!(scratch_stderr_error) {
                    check(self.changed);
                    (7, 5, 141 << 8, 2888)
                } else {
                    #[cfg(session_scratch)]
                    if cfg!(scratch_lose_b) || cfg!(scratch_skip_read) {
                        check(!self.scratch.complete());
                    } else {
                        check(self.scratch.complete());
                    }
                    if cfg!(scratch_wrong_denied) {
                        check(self.changed);
                    }
                    (
                        7,
                        5,
                        0,
                        if cfg!(scratch_lose_b) {
                            2880
                        } else if cfg!(scratch_skip_read) {
                            2883
                        } else if cfg!(scratch_wrong_denied) {
                            2882
                        } else {
                            100
                        },
                    )
                }
            } else if cfg!(session_failed_exec) {
                if self.bad_denial {
                    check(self.denials == 0);
                    (1, 0, 15, 2864)
                } else if cfg!(exec_wrong_missing) {
                    check(self.changed && self.denials == 1);
                    (1, 0, 51 << 8, 2860)
                } else {
                    check(self.denials == 2);
                    if cfg!(exec_wrong_denied) {
                        check(self.changed);
                        (2, 0, 52 << 8, 2861)
                    } else if cfg!(exec_wrong_env) {
                        (3, 1, 53 << 8, 2862)
                    } else if cfg!(exec_fd_leak) {
                        (7, 4, 55 << 8, 2863)
                    } else if cfg!(exec_stderr_error) {
                        check(self.changed);
                        // The revoked binding also rejects exit-time close. The
                        // unchanged client fails closed with wrapper status141.
                        (7, 4, 141 << 8, 2865)
                    } else {
                        (7, 4, 0, 100)
                    }
                }
            } else if cfg!(recovery_wrong_env) {
                (3, 3, 43 << 8, 2840)
            } else if cfg!(recovery_fd_leak) {
                (7, 6, 45 << 8, 2841)
            } else if cfg!(recovery_wrong_epipe) {
                check(self.changed);
                (2, 2, 42 << 8, 2842)
            } else if cfg!(recovery_retained_reader) {
                check(self.changed);
                (2, 2, 15, 2844)
            } else if cfg!(session_recovery) {
                (7, 6, 0, 100)
            } else if cfg!(session_wrong_env) {
                (1, 1, 31 << 8, 2800)
            } else if cfg!(session_bad_substitution) {
                check(self.changed);
                (5, 4, 33 << 8, 2801)
            } else if cfg!(session_fd_leak) {
                (9, 7, 35 << 8, 2802)
            } else if cfg!(session_stale_accept) {
                check(self.changed);
                (4, 3, 144 << 8, 2803)
            } else if cfg!(session_retained_writer) {
                check(self.changed);
                (4, 3, 15, 2804)
            } else {
                (9, 7, 0, 100)
            };
            check(word(r, 8) == copies && word(r, 12) == execs && self.parent_status == status);
            check(
                call(
                    0x2000a,
                    0xa001,
                    self.record.as_ptr() as u64,
                    176,
                    generation as u64,
                    0,
                    0,
                )
                .0 == 0,
            );
            check(
                call(
                    0x2000a,
                    0xa001,
                    self.record.as_ptr() as u64,
                    176,
                    generation as u64,
                    0,
                    0,
                )
                .0 == if generation == 3 { -28 } else { -9 },
            );
            if result != 100 {
                #[cfg(session_serial)]
                self.close_serial();
                end(result);
            }
        }
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    abi: u64,
    factory: u64,
    first: u64,
    second: u64,
    channels: u64,
    third: u64,
) -> ! {
    check(
        (abi, factory, first, second, channels, third)
            == (
                if cfg!(session_lifecycle) {
                    if cfg!(session_wrong_lifecycle_abi) {
                        23
                    } else {
                        24
                    }
                } else if cfg!(session_serial) {
                    23
                } else {
                    21
                },
                0xa001,
                0xc001,
                0xc002,
                0xd001,
                0xc003,
            ),
    );
    let mut session = Session::new();
    #[cfg(session_lifecycle)]
    session.run_lifecycle();
    #[cfg(not(session_lifecycle))]
    session.run();
    #[cfg(session_serial)]
    session.close_serial();
    #[cfg(session_lifecycle)]
    {
        ctl(0x2a002, 0xf002);
        unsafe { asm!("ud2", options(noreturn)) }
    }
    #[cfg(not(session_lifecycle))]
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(2820)
}
