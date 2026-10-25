// SPDX-License-Identifier: BSD-2-Clause
//! Single-owner AENIN001 adapter. No service policy or elapsed-time conversion.
use core::arch::asm;

#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Worker(u64);
impl Worker {
    // Comparison only: an expected number never constructs an owned handle.
    pub(super) fn matches_target(self, expected: u64) -> bool { self.0 == expected }
}
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Reader(u64);
#[derive(Clone, Copy)]
pub struct Writer(u64);
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct InterruptTick(u64);
impl InterruptTick {
    pub fn after(self, ticks: u64) -> Result<Self, Error> {
        self.0.checked_add(ticks).map(Self).ok_or(Error { operation: 0x25000, errno: 75 })
    }
}
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Error { pub operation: u64, pub errno: u64 }
pub type Result<T, E = Error> = core::result::Result<T, E>;
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum WaitState { Pending, Changed, Timeout, Cancelled, Reclaimed }
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Completion { pub state: WaitState, pub revision: u64, pub tick: InterruptTick }
pub struct WorkerStatus { pub result: u64, pub kind: u64, pub historical_ready: bool }
pub struct Observation { pub revision: u64, pub terminal: u64, pub historical_ready: bool }
#[derive(Clone, Copy)]
pub struct Wait { token: u64, target: Worker }
pub enum Read { Pending, Eof, Byte(u8) }

fn trap(op: u64, h: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64, u64) {
    let result: i64; let extra: u64; let detail: u64;
    unsafe { asm!("int 0x81", inlateout("rax") op => result, in("rdi") h, in("rsi") a,
        inlateout("rdx") b => extra, in("r10") c, inlateout("r8") d => detail,
        in("r9") 0u64, lateout("rcx") _, options(nostack)); }
    (result, extra, detail)
}
fn call(op: u64, h: u64) -> (i64, u64, u64) { trap(op, h, 0, 0, 0, 0) }
fn decoded(op: u64, value: i64) -> Result<u64> {
    if value < 0 { Err(Error { operation: op, errno: value.unsigned_abs() }) } else { Ok(value as u64) }
}
fn guard(ok: bool, operation: u64, errno: u64) -> Result<()> {
    if ok { Ok(()) } else { Err(Error { operation, errno }) }
}
fn completion(op: u64, raw: (i64, u64, u64)) -> Result<Completion> {
    let state = match decoded(op, raw.0)? {
        0 => WaitState::Pending, 1 => WaitState::Changed, 2 => WaitState::Timeout,
        3 => WaitState::Cancelled, 4 => WaitState::Reclaimed,
        _ => return Err(Error { operation: op, errno: 71 }),
    };
    Ok(Completion { state, revision: raw.1, tick: InterruptTick(raw.2) })
}
pub fn finish(code: u64) -> ! { call(0x20006, code); loop { core::hint::spin_loop(); } }
pub fn yield_now() { call(0x1fffe, 0); }
pub fn exit_owner() -> ! { call(0x1003c, 0); finish(829) }
pub fn fault_owner() -> ! { unsafe { asm!("ud2", options(noreturn)); } }

// One supervisor owns every handle minted through this adapter. The kernel
// enforces per-handle authority and stale rejection; counts track outstanding
// ownership, not a second authority registry. Failed operations retain counts.
// No Drop cleanup: explicit, observed cleanup is required before completion.
pub struct Adapter {
    workers: u8, endpoints: u8,
    wait: u64, wait_target: u64, issued: u8,
}
impl Adapter {
    pub fn new(abi: u64, factory: u64, image: u64, other: u64, channels: u64, observer: u64) -> Result<Self> {
        guard((abi, factory, image, other, channels, observer) ==
              (if cfg!(init_composed) { 16 } else if cfg!(init_large) { 15 } else { 6 }, 0xa001, 0xc001, 0xc002, 0xd001, 0xe001), 0, 22)?;
        Ok(Self { workers: 0, endpoints: 0, wait: 0, wait_target: 0, issued: 0 })
    }
    pub fn clock(&self) -> Result<InterruptTick> { decoded(0x25000, call(0x25000, 0xe001).0).map(InterruptTick) }
    pub fn channel(&mut self) -> Result<(Reader, Writer)> {
        let raw = call(0x24000, 0xd001); let reader = decoded(0x24000, raw.0)?;
        self.endpoints += 2;
        Ok((Reader(reader), Writer(raw.1)))
    }
    pub fn launch(&mut self, slot: usize, writer: Writer, mode: &[u8]) -> Result<Worker> {
        guard(slot < 2 && mode.len() < 32, 0x23001, 22)?;
        #[repr(C)]
        struct Startup { argc: u64, envc: u64, text: [[u8; 32]; 8] }
        let mut record = Startup { argc: 2, envc: 0, text: [[0; 32]; 8] };
        record.text[0][0] = b's'; record.text[1][..mode.len()].copy_from_slice(mode);
        let worker = decoded(0x23001, trap(0x23001, 0xa001, 0xc001, slot as u64,
            &record as *const Startup as u64, writer.0).0)?;
        self.workers += 1; self.endpoints -= 1;
        Ok(Worker(worker))
    }
    pub(super) fn raw_worker_status(&self, worker: Worker) -> super::sample_receipts::Raw {
        let (rax, rdx, r8) = call(0x20001, worker.0);
        super::sample_receipts::Raw { rax, rdx, r8 }
    }
    pub(super) fn raw_observe(&self, worker: Worker) -> super::sample_receipts::Raw {
        let (rax, rdx, r8) = trap(0x25001, 0xe001, worker.0, 0, 0, 0);
        super::sample_receipts::Raw { rax, rdx, r8 }
    }
    pub fn worker_status(&self, worker: Worker) -> Result<WorkerStatus> {
        let raw = call(0x20001, worker.0);
        let result = decoded(0x20001, raw.0)?;
        guard(raw.1 <= 1, 0x20001, 71)?;
        Ok(WorkerStatus { result, kind: raw.2, historical_ready: raw.1 == 1 })
    }
    pub fn observe(&self, worker: Worker) -> Result<Observation> {
        let raw = trap(0x25001, 0xe001, worker.0, 0, 0, 0);
        let revision = decoded(0x25001, raw.0)?;
        guard(raw.2 <= 1, 0x25001, 71)?;
        Ok(Observation { revision, terminal: raw.1, historical_ready: raw.2 == 1 })
    }
    pub fn register(&mut self, worker: Worker, revision: u64, deadline: InterruptTick) -> Result<Wait> {
        guard(self.wait == 0, 0x25002, 16)?;
        guard(self.issued < 64, 0x25002, 28)?;
        let token = decoded(0x25002, trap(0x25002, 0xe001, worker.0, revision, deadline.0, 0).0)?;
        self.wait = token; self.wait_target = worker.0; self.issued += 1;
        Ok(Wait { token, target: worker })
    }
    fn owns_wait(&self, wait: Wait, op: u64) -> Result<()> {
        guard(self.wait != 0 && self.wait == wait.token && self.wait_target == wait.target.0, op, 9)
    }
    pub fn status(&self, wait: Wait) -> Result<Completion> {
        completion(0x25003, trap(0x25003, 0xe001, wait.token, 0, 0, 0))
    }
    pub fn cancel(&self, wait: Wait) -> Result<Completion> {
        completion(0x25004, trap(0x25004, 0xe001, wait.token, 0, 0, 0))
    }
    pub fn release(&mut self, wait: Wait) -> Result<()> {
        self.owns_wait(wait, 0x25005)?;
        decoded(0x25005, trap(0x25005, 0xe001, wait.token, 0, 0, 0).0)?;
        self.wait = 0; self.wait_target = 0; Ok(())
    }
    pub fn read(&self, reader: Reader) -> Result<Read> {
        let mut byte = 0u8;
        let raw = trap(0x24001, reader.0, &mut byte as *mut u8 as u64, 1, 0, 0).0;
        match raw { -11 => Ok(Read::Pending), 0 => Ok(Read::Eof), 1 => Ok(Read::Byte(byte)),
            _ => { decoded(0x24001, raw)?; Err(Error { operation: 0x24001, errno: 71 }) } }
    }
    pub fn close(&mut self, reader: Reader) -> Result<()> {
        decoded(0x24003, call(0x24003, reader.0).0)?; self.endpoints -= 1; Ok(())
    }
    pub fn close_writer(&mut self, writer: Writer) -> Result<()> {
        decoded(0x24003, call(0x24003, writer.0).0)?; self.endpoints -= 1; Ok(())
    }
    pub fn stop(&self, worker: Worker) -> Result<()> {
        decoded(0x20007, call(0x20007, worker.0).0)?; Ok(())
    }
    pub fn reclaim(&mut self, worker: Worker) -> Result<()> {
        guard(self.observe(worker)?.terminal != 0, 0x20002, 16)?;
        decoded(0x20002, call(0x20002, worker.0).0)?; self.workers -= 1; Ok(())
    }
    pub fn clean(&self) -> bool {
        if cfg!(bad_clean) { return true; }
        self.workers == 0 && self.endpoints == 0 && self.wait == 0
    }
}

// Fixture-only denial probes deliberately bypass the local ledger to retain
// kernel enforcement witnesses. They are not general adapter operations.
pub mod probes {
    use super::*;
    pub fn exhausted(worker: Worker, deadline: InterruptTick) -> bool {
        trap(0x25002, 0xe001, worker.0, 2, deadline.0, 0).0 == -28
    }
    pub fn rejected_launch(writer: Writer) -> bool {
        trap(0x23001, 0, 0xc001, 0, 0, writer.0).0 == -13
    }
    pub fn first_generation(worker: Worker) -> bool { worker.0 == 0xb0000101 }
    pub fn foreign_clock() -> bool { call(0x25000, 0).0 == -13 }
    pub fn transferred(writer: Writer) -> bool { call(0x24003, writer.0).0 == -13 }
    pub fn released(wait: Wait) -> bool { trap(0x25003, 0xe001, wait.token, 0, 0, 0).0 == -9 }
    pub fn reclaimed(worker: Worker) -> bool { call(0x20001, worker.0).0 == -9 }
    pub fn closed(reader: Reader) -> bool {
        let mut byte = 0u8;
        trap(0x24001, reader.0, &mut byte as *mut u8 as u64, 1, 0, 0).0 == -13
    }
    pub fn busy(worker: Worker, revision: u64, deadline: InterruptTick) -> bool {
        trap(0x25002, 0xe001, worker.0, revision, deadline.0, 0).0 == -16
    }
}

// Preserve complete operation returns for the issued-effect driver. The ledger
// follows successful kernel operations; policy interpretation stays with the caller.
impl Adapter {
    pub(super) fn close_return(&mut self, reader: Reader) -> super::sample_receipts::Raw {
        let (rax, rdx, r8) = call(0x24003, reader.0);
        if rax == 0 { self.endpoints -= 1; }
        super::sample_receipts::Raw { rax, rdx, r8 }
    }
    pub(super) fn reclaim_return(&mut self, worker: Worker) -> super::sample_receipts::Raw {
        let (rax, rdx, r8) = call(0x20002, worker.0);
        if rax == 0 { self.workers -= 1; }
        super::sample_receipts::Raw { rax, rdx, r8 }
    }
}
