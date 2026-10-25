// SPDX-License-Identifier: BSD-2-Clause
//! Trusted two-entry synthetic issuance. No journal execution or retirement API.
use super::{accepted, reclaim, require, terminal};
use super::adapter::{Adapter, Error, Reader, Worker, Writer, finish};
use core::hint::black_box;
#[path = "pending_history.rs"]
mod pending_history;
use pending_history::{View, Replay, Held, Offer};
use super::terminal::Fact;
use super::sample_receipts::{Sample, State, Failure, Raw, Cause};

// Injective, immutable symbols for the ten-field event-effect-v1 token.
// 0 is invalid; no runtime string parsing or remapping is implemented here.
const SYMBOLS: [&str; 8] = ["", "event-effect-v1", "binding-owner-1", "binding-revision-1",
    "a", "b", "launch", "activation"];
#[derive(Clone, Copy, Eq)]
struct Token([u64; 10]);
impl PartialEq for Token {
    fn eq(&self, other: &Self) -> bool {
        // Compare every scalar; no hash, truncation or timing guarantee.
        self.0.iter().zip(other.0.iter()).fold(0, |difference, (a, b)| difference | (a ^ b)) == 0
    }
}
const ISSUED: [Token; 2] = [Token([1, 2, 3, 1, 0, 4, 1, 6, 7, 1]),
                             Token([1, 2, 3, 1, 1, 5, 1, 6, 7, 1])];
fn issued(index: usize) -> Token { *ISSUED.get(index).unwrap() }
struct Context { profile: &'static str, producer: &'static str }
fn context() -> Context {
    Context { profile: "aether-init-abi6",
        producer: "3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155" }
}
#[derive(Clone, Copy, PartialEq, Eq)]
enum ChannelPhase { Reserved, Started, Returned, Applied }
struct Binding {
    sample_started: bool,
    fact: Option<Fact>,
    channel: ChannelPhase,
    launch_phase: ChannelPhase,
    token: &'static Token,
    slot: usize,
    reserved: bool,
    expected: u64,
    reader: Option<Reader>,
    writer: Option<Writer>,
    worker: Option<Worker>,
    error: Option<Error>,
}
struct Driver<'a> {
    owner: &'a Context,
    records: [Option<Binding>; 2],
    used: [bool; 2],
    pending: Option<usize>,
    reads: u8,
    acquisitions: u8,
    launches: u8,
    closed: bool,
    binding_failed: Option<usize>,
    target_failed: Option<usize>,
    generations: [u8; 2],
}
impl<'a> Driver<'a> {
    fn new(owner: &'a Context) -> Self {
        Self { owner, records: [None, None], used: [false; 2], pending: None,
               reads: 0, acquisitions: 0, launches: 0, closed: false, binding_failed: None, target_failed: None, generations: [0; 2] }
    }
    #[inline(never)]
    fn reserve(&mut self, owner: &Context, token: &Token, slot: usize) -> bool {
        if self.closed || !core::ptr::eq(owner, self.owner) || slot >= 2 ||
            (!cfg!(binding_skip_pending) && self.pending.is_some()) { return false; }
        if !cfg!(generation_skip_guard) && *self.generations.get(slot).unwrap() >= 3 {
            if cfg!(generation_consume_denied) { self.used[0] = true; }
            return false;
        }
        let index = if token == &ISSUED[0] { 0 } else if token == &ISSUED[1] { 1 } else { return false; };
        if *self.used.get(index).unwrap() || self.records.iter().flatten().any(|r| r.reserved && r.slot == slot) {
            return false;
        }
        *self.records.get_mut(index).unwrap() = Some(Binding { sample_started: false, fact: None, channel: ChannelPhase::Reserved, launch_phase: ChannelPhase::Reserved, token: ISSUED.get(index).unwrap(), slot, reserved: true, expected: 0xb0000000 | ((*self.generations.get(slot).unwrap() as u64 + 1) << 8) | (slot as u64 + 1), reader: None, writer: None,
                                            worker: None, error: None });
        *self.used.get_mut(index).unwrap() = true;
        self.pending = Some(index);
        true
    }
    #[inline(never)]
    fn acquire(&mut self, a: &mut Adapter, index: usize) -> bool {
        self.acquire_checked(a, index, true)
    }
    #[inline(never)]
    fn acquire_checked(&mut self, a: &mut Adapter, index: usize, binding_ok: bool) -> bool {
        if !self.receive_channel(a, index) { return false; }
        self.apply_channel(index, binding_ok)
    }
    // This is the actual invocation guard, also used by the omission probe before
    // any second syscall. A phase transition never authorizes retry.
    #[inline]
    fn start_channel(&mut self, index: usize) -> bool {
        if self.closed || self.pending != Some(index) || index >= 2 { return false; }
        let record = self.records.get_mut(index).unwrap().as_mut().unwrap();
        if !cfg!(receipt_skip_phase) && record.channel != ChannelPhase::Reserved { return false; }
        record.channel = ChannelPhase::Started;
        self.acquisitions += 1; // Two consumed entries; no phase reset in normal code.
        true
    }
    #[inline]
    fn receive_channel(&mut self, a: &mut Adapter, index: usize) -> bool {
        if !self.start_channel(index) { return false; }
        let record = self.records.get_mut(index).unwrap().as_mut().unwrap();
        match a.channel() {
            Ok((reader, writer)) => {
                record.reader = Some(reader); record.writer = Some(writer); #[cfg(composed_forget_reader)] { record.reader = None; }
                if cfg!(receipt_forget_writer) { record.writer = None; }
            }
            Err(error) => { record.error = Some(error); }
        }
        record.channel = ChannelPhase::Returned;
        true
    }
    #[inline]
    fn apply_channel(&mut self, index: usize, binding_ok: bool) -> bool {
        if self.closed || self.pending != Some(index) || index >= 2 { return false; }
        let record = self.records.get_mut(index).unwrap().as_mut().unwrap();
        if record.channel != ChannelPhase::Returned { return false; }
        if let Some(error) = record.error {
            if error == (Error { operation: 0x24000, errno: 16 }) {
                record.reserved = false; self.pending = None;
                record.channel = ChannelPhase::Applied;
                if cfg!(binding_reopen_token) { *self.used.get_mut(index).unwrap() = false; }
            } else { self.closed = true; }
            return false;
        }
        if !binding_ok {
            self.binding_failed = Some(index); self.closed = true;
            if cfg!(binding_forget_writer) { record.writer = None; }
            return false;
        }
        record.channel = ChannelPhase::Applied;
        self.pending = None;
        true
    }
    #[inline(never)]
    fn deliver_channel(&mut self, owner: &Context, index: usize, token: &Token,
                       operation: u64, expected: u64) -> bool {
        if !core::ptr::eq(owner, self.owner) || index >= 2 { return false; }
        let Some(record) = self.records.get(index).unwrap().as_ref() else { return false; };
        if record.token != token || operation != 0x24000 || record.expected != expected { return false; }
        self.apply_channel(index, true)
    }
    #[inline]
    fn can_launch(&self, index: usize) -> bool {
        if self.closed || self.pending.is_some() || index >= 2 { return false; }
        let Some(record) = self.records.get(index).unwrap().as_ref() else { return false; };
        record.channel == ChannelPhase::Applied && record.launch_phase == ChannelPhase::Reserved && record.error.is_none() &&
            record.worker.is_none() && record.writer.is_some()
    }
    #[inline(never)]
    fn launch(&mut self, a: &mut Adapter, index: usize) -> bool {
        if !self.receive_launch(a, index) { return false; }
        self.apply_launch(index)
    }
    #[inline]
    fn start_launch(&mut self, index: usize) -> bool {
        if !self.can_launch(index) { return false; }
        self.pending = Some(index);
        self.records.get_mut(index).unwrap().as_mut().unwrap().launch_phase = ChannelPhase::Started;
        self.launches += 1; // Counts starts; synthetic schedules omit the native call.
        true
    }
    #[inline]
    fn receive_launch(&mut self, a: &mut Adapter, index: usize) -> bool {
        if !self.start_launch(index) { return false; }
        let record = self.records.get_mut(index).unwrap().as_mut().unwrap();
        let writer = record.writer.unwrap(); // In-flight: not available to another operation.
        match a.launch(record.slot, writer, b"exit") {
            Ok(worker) => {
                record.worker = Some(worker);
                if !cfg!(launch_keep_writer) { record.writer = None; } #[cfg(composed_keep_writer)] { record.writer = Some(writer); }
                if cfg!(launch_early_generation) { self.generations[record.slot] += 1; }
            }
            Err(error) => { record.error = Some(error); }
        }
        record.launch_phase = ChannelPhase::Returned;
        true
    }
    #[inline]
    fn apply_launch(&mut self, index: usize) -> bool {
        if self.closed || self.pending != Some(index) || index >= 2 { return false; }
        let record = self.records.get_mut(index).unwrap().as_mut().unwrap();
        if record.launch_phase != ChannelPhase::Returned { return false; }
        if let Some(error) = record.error {
            if error == (Error { operation: 0x23001, errno: 16 }) {
                record.reserved = false; self.pending = None;
                record.launch_phase = ChannelPhase::Applied;
                if cfg!(binding_busy_forget) { record.writer = None; }
            } else { self.closed = true; }
            return false;
        }
        let worker = record.worker.unwrap();
        if !cfg!(target_skip_match) && !worker.matches_target(record.expected) {
            self.closed = true; self.target_failed = Some(index);
            if cfg!(target_forget_worker) { record.worker = None; }
            return false;
        }
        *self.generations.get_mut(record.slot).unwrap() += 1;
        record.launch_phase = ChannelPhase::Applied;
        self.pending = None;
        true
    }
    // Local missing-return disposition only. A blocked synchronous syscall
    // cannot execute this method; the absence probes inject that schedule.
    #[inline]
    fn close_missing(&mut self, index: usize) -> bool {
        if self.closed || self.pending != Some(index) || index >= 2 { return false; }
        let record = self.records.get_mut(index).unwrap().as_mut().unwrap();
        if record.channel != ChannelPhase::Started && record.launch_phase != ChannelPhase::Started {
            return false;
        }
        if !cfg!(missing_skip_close) { self.closed = true; }
        if cfg!(missing_invent_error) { record.error = Some(Error { operation: 0x24000, errno: 16 }); }
        if cfg!(missing_forget_writer) { record.writer = None; }
        true
    }
    #[inline(never)]
    fn begin_sample(&mut self, owner: &Context, index: usize, token: &Token, worker: Worker) -> bool {
        if (!cfg!(sampling_skip_pending) && self.pending.is_some()) ||
            !self.launched(owner, index, token, worker) { return false; }
        if self.records.get(index).unwrap().as_ref().unwrap().sample_started { return false; }
        self.pending = Some(index);
        true
    }
    #[inline(never)]
    fn launched(&self, owner: &Context, index: usize, token: &Token, worker: Worker) -> bool {
        if self.closed || !core::ptr::eq(owner, self.owner) || index >= 2 { return false; }
        let Some(record) = self.records.get(index).unwrap() else { return false; };
        #[cfg(composed_skip_launch)] { return record.token == token && record.worker == Some(worker); } #[cfg(composed_skip_token)] { return record.launch_phase == ChannelPhase::Applied && record.worker == Some(worker); } record.launch_phase == ChannelPhase::Applied &&
            (cfg!(binding_skip_token) || cfg!(sampling_skip_token) || record.token == token) && record.worker == Some(worker)
    }
}

// One session exclusively borrows the driver and caller-owned fixed receipt storage.
// Keep the session/storage until a future named history consumer permits retirement.
struct Sampling<'a, 'b> { driver: &'a mut Driver<'b>, sample: &'a mut Sample, index: usize }
impl<'a, 'b> Sampling<'a, 'b> {
    #[inline(always)]
    fn terminal_view(&self) -> Option<View<'_, Context, Token, Worker>> {
        if self.driver.closed || self.driver.pending != Some(self.index) { return None; }
        let record = self.driver.records.get(self.index)?.as_ref()?;
        if record.launch_phase != ChannelPhase::Applied || !record.sample_started { return None; }
        let State::Terminal(fact) = self.sample.state() else { return None; };
        let retained = record.fact?;
        if retained.revision != fact.revision || retained.result != fact.result ||
            retained.kind != fact.kind || retained.historical_ready != fact.historical_ready { return None; }
        View::terminal(self.driver.owner, record.token, self.index, record.worker?, self.sample)
    }

    #[inline]
    fn begin(driver: &'a mut Driver<'b>, sample: &'a mut Sample, owner: &Context,
             index: usize, token: &Token, worker: Worker) -> Option<Self> {
        if sample.received() != 0 || sample.state() != State::Awaiting ||
            !driver.begin_sample(owner, index, token, worker) { return None; }
        Some(Self { driver, sample, index })
    }
    #[inline(never)]
    fn receive(&mut self, a: &Adapter) -> bool {
        let index = self.index;
        if self.driver.closed || self.driver.pending != Some(index) { return false; }
        let record = self.driver.records.get_mut(index).unwrap_or_else(|| finish(1042)).as_mut().unwrap_or_else(|| finish(1042));
        if record.launch_phase != ChannelPhase::Applied || self.sample.state() != State::Awaiting ||
            (record.sample_started && self.sample.received() == 0) { return false; }
        record.sample_started = true;
        // Test-only synthetic slot: omit its syscall; never discard an actual return.
        let count = self.sample.received();
        let raw = if malformed_status() && count == 1 {
            Raw { rax: if cfg!(sample_bad_live) { 0 } else if cfg!(sample_bad_result) { 19 } else { 18 },
                  rdx: if malformed_boolean() { 2 } else { 1 },
                  r8: if cfg!(sample_bad_kind) { 4 } else if cfg!(sample_bad_live) { 0 } else { 1 } }
        } else if (cfg!(sample_bad_revision) || cfg!(sample_bad_readiness)) && count == 2 {
            let first = self.sample.receipts()[0].unwrap_or_else(|| finish(1042));
            Raw { rax: first.rax + if cfg!(sample_bad_revision) { 1 } else { 0 },
                  rdx: first.rdx, r8: if cfg!(sample_bad_readiness) { 0 } else { first.r8 } }
        } else {
            self.driver.reads += 1;
            if count == 1 { a.raw_worker_status(record.worker.unwrap_or_else(|| finish(1042))) }
            else { a.raw_observe(record.worker.unwrap_or_else(|| finish(1042))) }
        };
        require(self.sample.push(raw), 1042);
        match self.sample.state() {
            State::Awaiting => true,
            State::Live => { self.driver.pending = None; true }
            State::Terminal(fact) => {
                record.fact = Some(Fact { revision: fact.revision, result: fact.result,
                    kind: fact.kind, historical_ready: fact.historical_ready }); true
            }
            State::Failed(failure) => {
                if let Failure::Native { operation, errno } = failure {
                    record.error = Some(Error { operation, errno });
                }
                if cfg!(sample_forget_reader) { record.reader = None; }
                if cfg!(sample_invent_errno) { record.error = Some(Error { operation: 0x20001, errno: 71 }); }
                if !cfg!(sample_skip_close) { self.driver.closed = true; }
                false
            }
        }
    }
    // Explicit synthetic disposition between received returns, never a syscall cancel.
    #[inline(always)]
    fn interrupt_synthetic(&mut self) -> bool {
        if self.driver.closed || self.driver.pending != Some(self.index) ||
            !self.sample.interrupt() { return false; }
        if !cfg!(interrupt_skip_close) { self.driver.closed = true; }
        if cfg!(interrupt_forget_prefix) { *self.sample = Sample::new(); }
        if cfg!(interrupt_invent_fact) {
            self.driver.records[self.index].as_mut().unwrap_or_else(|| finish(1042)).fact =
                Some(Fact { revision: 1, result: 18, kind: 1, historical_ready: true });
        }
        if cfg!(interrupt_forget_reader) {
            self.driver.records[self.index].as_mut().unwrap_or_else(|| finish(1042)).reader = None;
        }
        true
    }
    #[inline]
    fn read(&mut self, a: &Adapter) -> bool {
        if self.driver.records.get(self.index).unwrap_or_else(|| finish(1042)).as_ref().unwrap_or_else(|| finish(1042)).sample_started { return false; }
        for _ in 0..3 {
            if !self.receive(a) { return false; }
            if self.sample.state() != State::Awaiting { return true; }
        }
        false
    }
}

pub fn run_preflight(a: &mut Adapter) -> ! {
    let owner = context(); let foreign = context();
    require(owner.profile == "aether-init-abi6" && owner.producer.len() == 64 &&
            SYMBOLS[4] != SYMBOLS[5], 1016);
    let mut driver = Driver::new(&owner);
    let first = black_box(issued(0)); let second = black_box(issued(1));
    // Each token field participates; all denials precede any native acquisition.
    for field in 0..10 {
        let mut wrong = first; wrong.0[field] = black_box(wrong.0[field] + 10);
        require(!driver.reserve(&owner, &wrong, 0), 1016);
    }
    require(!driver.reserve(black_box(&foreign), &first, 0) &&
            !driver.reserve(&owner, &first, 2) && driver.acquisitions == 0 &&
            driver.records.iter().all(Option::is_none), 1016);
    require(driver.reserve(&owner, &first, 0), 1015);
    require(!driver.reserve(&owner, &second, 1), 1015);
    require(driver.pending == Some(0) && driver.acquisitions == 0 &&
            driver.records[1].is_none() && !driver.used[1] &&
            *driver.records[0].as_ref().unwrap().token == first, 1015);
    require(a.clean(), 1016);
    for slot in [0, 1, 0] {
        let (reader, writer) = accepted(a.channel(), 1016);
        let worker = accepted(a.launch(slot, writer, b"exit"), 1016);
        terminal(a, worker, 18); accepted(a.close(reader), 1016); reclaim(a, worker);
    }
    require(a.clean(), 1016); finish(100)
}

pub fn run(a: &mut Adapter) -> ! {
    let owner = context(); let foreign = context();
    let mut driver = Driver::new(&owner);
    let first = black_box(&ISSUED[0]); let second = black_box(&ISSUED[1]);
    require(driver.reserve(&owner, first, 0), 1015);
    require(driver.acquire(a, 0) && driver.launch(a, 0), 1016);
    require(!driver.acquire(a, 0) && !driver.launch(a, 0) &&
            !driver.reserve(&owner, first, 1) && !driver.reserve(&owner, second, 0) &&
            driver.acquisitions == 1, 1016);
    require(driver.reserve(&owner, second, 1) && driver.acquire(a, 1) &&
            driver.launch(a, 1) && driver.acquisitions == 2, 1016);
    let one = driver.records[0].as_ref().unwrap().worker.unwrap();
    let two = driver.records[1].as_ref().unwrap().worker.unwrap();
    require(one != two && driver.launched(&owner, 0, first, one) &&
            driver.launched(&owner, 1, second, two), 1014);
    // Correct worker with another service's equal-generation token must fail.
    require(!driver.launched(&owner, 0, black_box(second), one), 1014);
    require(!driver.launched(&owner, 0, first, two) &&
            !driver.launched(black_box(&foreign), 0, first, one), 1014);
    dispose_bound(a, &mut driver, 0); dispose_bound(a, &mut driver, 1);
    // Fixture teardown is not journal retirement; records and consumed tokens stay.
    require(a.clean() && !driver.reserve(&owner, first, 0) &&
            !driver.reserve(&owner, second, 1) && driver.acquisitions == 2 &&
            !driver.launched(&owner, 0, first, one), 1016);
    ordinary(a, 0);
    require(a.clean(), 1016); finish(100)
}


pub fn run_binding_failure(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(issued(0));
    require(driver.reserve(&owner, &token, 0), 1017);
    require(!driver.acquire_checked(a, 0, black_box(false)), 1017);
    let record = driver.records[0].as_ref().unwrap();
    require(driver.closed && driver.binding_failed == Some(0) && driver.pending == Some(0) &&
            driver.used == [true, false] && driver.acquisitions == 1 &&
            *record.token == token && record.slot == 0 && record.reader.is_some() &&
            record.writer.is_some() && record.worker.is_none() && record.error.is_none() &&
            driver.records[1].is_none() && !a.clean(), 1017);
    let reader = record.reader.unwrap();
    require(!driver.acquire(a, 0) && !driver.acquire_checked(a, 0, true) &&
            !driver.launch(a, 0) && !driver.reserve(&owner, &token, 0) &&
            !driver.reserve(&owner, &issued(1), 1), 1017);
    let record = driver.records[0].as_ref().unwrap();
    require(driver.acquisitions == 1 && driver.pending == Some(0) &&
            record.reader == Some(reader) && record.writer.is_some() &&
            record.worker.is_none() && record.error.is_none(), 1017);
    // Independent fixture accounting while the failed pair remains owned.
    // The closed driver is never resumed or used to admit these workers.
    for slot in [0, 1, 0] {
        let (reader, writer) = accepted(a.channel(), 1017);
        let worker = accepted(a.launch(slot, writer, b"exit"), 1017);
        terminal(a, worker, 18); accepted(a.close(reader), 1017); reclaim(a, worker);
    }
    let record = driver.records[0].as_mut().unwrap();
    accepted(a.close_writer(record.writer.unwrap()), 1017); record.writer = None;
    accepted(a.close(record.reader.unwrap()), 1017); record.reader = None;
    require(a.clean() && driver.closed && driver.binding_failed == Some(0) &&
            driver.pending == Some(0) && driver.acquisitions == 1 &&
            !driver.reserve(&owner, &token, 0) && !driver.reserve(&owner, &issued(1), 1), 1017);
    finish(100)
}


// Explicit fixture disposal; neither method retires a binding or consumes a journal event.
#[inline(never)]
fn dispose_pair(a: &mut Adapter, reader: Reader, writer: Writer) {
    accepted(a.close_writer(writer), 1020); accepted(a.close(reader), 1020);
}
#[inline(never)]
fn dispose_bound(a: &mut Adapter, driver: &mut Driver<'_>, index: usize) {
    let record = driver.records.get_mut(index).unwrap().as_mut().unwrap();
    fixture_finish(a, record.reader.unwrap(), record.worker.unwrap());
    record.reader = None; record.worker = None;
}
#[inline(never)]
fn fixture_worker(a: &mut Adapter, slot: usize) -> (Reader, Worker) {
    let (reader, writer) = accepted(a.channel(), 1020);
    let worker = accepted(a.launch(slot, writer, b"exit"), 1020);
    (reader, worker)
}
#[inline(never)]
fn ordinary(a: &mut Adapter, slot: usize) {
    let (reader, worker) = fixture_worker(a, slot);
    fixture_finish(a, reader, worker);
}

#[inline(never)]
fn fixture_finish(a: &mut Adapter, reader: Reader, worker: Worker) {
    terminal(a, worker, 18); accepted(a.close(reader), 1020); reclaim(a, worker);
}

#[inline(never)]
fn admit_second(a: &mut Adapter, driver: &mut Driver<'_>) -> bool {
    driver.reserve(driver.owner, &issued(1), 0) && driver.acquire(a, 1) && driver.launch(a, 1)
}

pub fn run_creation_busy(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    // Controlled interference after construction, wholly inventoried by this fixture.
    let pair = accepted(a.channel(), 1018); let other = accepted(a.channel(), 1018);
    let first = issued(0);
    require(driver.reserve(&owner, &first, 0) && !driver.acquire(a, 0), 1018);
    let record = driver.records[0].as_ref().unwrap();
    require(record.error == Some(Error { operation: 0x24000, errno: 16 }) &&
            record.reader.is_none() && record.writer.is_none() && record.worker.is_none() &&
            !record.reserved && *record.token == first && record.slot == 0 &&
            !driver.closed && driver.binding_failed.is_none() && driver.pending.is_none(), 1018);
    require(!driver.reserve(&owner, &first, 0) && !driver.acquire(a, 0) &&
            !driver.launch(a, 0) && driver.acquisitions == 1, 1018);
    dispose_pair(a, pair.0, pair.1); dispose_pair(a, other.0, other.1);
    require(admit_second(a, &mut driver) && driver.acquisitions == 2, 1018);
    dispose_bound(a, &mut driver, 1);
    ordinary(a, 1); ordinary(a, 0);
    require(a.clean() && driver.used == [true, true] &&
            !driver.reserve(&owner, &first, 0) &&
            driver.records[0].as_ref().unwrap().error == Some(Error { operation: 0x24000, errno: 16 }), 1018);
    finish(100)
}

pub fn run_launch_busy(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let (reader, occupant) = fixture_worker(a, 0);
    // Exact trusted fixture history, before any reservation; never unknown adoption.
    require(occupant.matches_target(0xb0000101), 1019);
    driver.generations[0] = 1;
    let first = issued(0);
    require(driver.reserve(&owner, &first, 0) && driver.acquire(a, 0) &&
            !driver.launch(a, 0), 1019);
    let record = driver.records[0].as_ref().unwrap();
    require(record.error == Some(Error { operation: 0x23001, errno: 16 }) &&
            record.reader.is_some() && record.writer.is_some() && record.worker.is_none() &&
            !record.reserved && *record.token == first && record.slot == 0 &&
            !driver.closed && driver.pending.is_none() && driver.binding_failed.is_none(), 1019);
    require(!driver.reserve(&owner, &first, 0) && !driver.acquire(a, 0) &&
            !driver.launch(a, 0) && driver.acquisitions == 1, 1019);
    fixture_finish(a, reader, occupant);
    let record = driver.records[0].as_mut().unwrap();
    dispose_pair(a, record.reader.unwrap(), record.writer.unwrap());
    record.reader = None; record.writer = None;
    require(admit_second(a, &mut driver), 1019);
    dispose_bound(a, &mut driver, 1); ordinary(a, 1);
    require(a.clean() && driver.acquisitions == 2 && driver.used == [true, true] &&
            !driver.reserve(&owner, &first, 0) &&
            driver.records[0].as_ref().unwrap().error == Some(Error { operation: 0x23001, errno: 16 }), 1019);
    finish(100)
}


pub fn run_expected_target(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let (reader, initial) = fixture_worker(a, 0);
    require(initial.matches_target(0xb0000101), 1021);
    driver.generations[0] = 1; fixture_finish(a, reader, initial);
    require(driver.reserve(&owner, &issued(0), 0) && driver.acquire(a, 0) && driver.launch(a, 0), 1021);
    require(driver.reserve(&owner, &issued(1), 1) && driver.acquire(a, 1) && driver.launch(a, 1), 1021);
    for (record, expected) in driver.records.iter().flatten().zip([0xb0000201, 0xb0000102]) {
        require(record.expected == expected && record.worker.unwrap().matches_target(expected) && record.token.0[6] == 1, 1021);
    }
    require(driver.generations == [2, 1] && !driver.launch(a, 0) && !driver.launch(a, 1) &&
            !driver.closed && driver.target_failed.is_none(), 1021);
    dispose_bound(a, &mut driver, 0); dispose_bound(a, &mut driver, 1);
    require(a.clean() && driver.generations == [2, 1], 1021); finish(100)
}

pub fn run_target_mismatch(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    require(driver.reserve(&owner, &issued(0), 0) && driver.acquire(a, 0), 1021);
    // Test-only corrupted expectation, never an owned/fabricated Worker.
    let wrong = black_box(if cfg!(target_wrong_generation) { 0xb0000201 } else { 0xb0000102 });
    driver.records[0].as_mut().unwrap().expected = wrong;
    require(!driver.launch(a, 0), 1021);
    let record = driver.records[0].as_ref().unwrap();
    require(record.worker.is_some(), 1022);
    let actual = record.worker.unwrap();
    require(actual.matches_target(0xb0000101) && record.expected == wrong &&
            record.reader.is_some() && record.writer.is_none() && record.error.is_none() &&
            record.reserved && *record.token == issued(0) && driver.used == [true, false] &&
            driver.closed && driver.target_failed == Some(0) && driver.binding_failed.is_none() &&
            driver.generations == [0, 0], 1022);
    require(!driver.launch(a, 0) && !driver.acquire(a, 0) &&
            !driver.reserve(&owner, &issued(1), 1) && !driver.launched(&owner, 0, &issued(0), actual), 1022);
    dispose_bound(a, &mut driver, 0); ordinary(a, 1); ordinary(a, 0);
    require(a.clean() && driver.closed && driver.target_failed == Some(0) &&
            driver.generations == [0, 0] && driver.acquisitions == 1, 1022);
    finish(100)
}


pub fn run_generation_exhaustion(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    // Actual, explicitly inventoried fixture history before any reservation.
    for generation in 1..=3 {
        let (reader, worker) = fixture_worker(a, 0);
        require(worker.matches_target(0xb0000001 | (generation << 8)), 1023);
        driver.generations[0] = generation as u8;
        fixture_finish(a, reader, worker);
    }
    let token = black_box(issued(0));
    require(a.clean() && !driver.reserve(&owner, &token, 0), 1023);
    require(!driver.reserve(&owner, &token, 0) && driver.generations == [3, 0] &&
            driver.used == [false, false] && driver.acquisitions == 0 &&
            driver.records.iter().all(Option::is_none) && driver.pending.is_none() &&
            !driver.closed && driver.binding_failed.is_none() && driver.target_failed.is_none(), 1024);
    // Denial did not consume the occurrence or block an unexhausted native slot.
    require(driver.reserve(&owner, &token, 1) && driver.acquire(a, 0), 1024);
    let record = driver.records[0].as_ref().unwrap();
    require(record.expected == 0xb0000102 && record.slot == 1 && record.reserved &&
            *record.token == token && record.worker.is_none() && record.error.is_none() &&
            record.reader.is_some() && record.writer.is_some() &&
            driver.generations == [3, 0] && driver.acquisitions == 1 && driver.used == [true, false], 1024);
    require(!driver.reserve(&owner, &issued(1), 0) && driver.used == [true, false], 1024);
    let record = driver.records[0].as_mut().unwrap();
    dispose_pair(a, record.reader.unwrap(), record.writer.unwrap());
    record.reader = None; record.writer = None;
    require(a.clean() && driver.generations == [3, 0] && driver.acquisitions == 1 &&
            !driver.reserve(&owner, &token, 1), 1024);
    finish(100)
}

// Actual synchronous return held locally; no kernel reply is dropped or delayed.
pub fn run_channel_receipt(a: &mut Adapter) -> ! {
    let owner = context(); let foreign = context();
    let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let other = black_box(&ISSUED[1]);
    require(driver.reserve(&owner, token, 0) && driver.receive_channel(a, 0), 1025);
    let reader = driver.records[0].as_ref().unwrap().reader;
    require(reader.is_some() && driver.records[0].as_ref().unwrap().writer.is_some(), 1026);
    // Separate identity probe keeps the fixed image bounded; other probes cover
    // the same guard used by receive_channel before any second effect.
    if !cfg!(receipt_identity) {
        require(!driver.start_channel(0), 1025);
        require(!driver.receive_channel(a, 0) && !driver.reserve(&owner, other, 1) &&
                !driver.can_launch(0), 1025);
    }
    if cfg!(receipt_identity) {
        require(!driver.deliver_channel(black_box(&foreign), 0, token, 0x24000, 0xb0000101) &&
                !driver.deliver_channel(&owner, 1, token, 0x24000, 0xb0000101) &&
                !driver.deliver_channel(&owner, 0, other, 0x24000, 0xb0000101) &&
                !driver.deliver_channel(&owner, 0, token, black_box(0x23001), 0xb0000101) &&
                !driver.deliver_channel(&owner, 0, token, 0x24000, black_box(0xb0000102)), 1027);
    }
    require(driver.pending == Some(0) && driver.acquisitions == 1 &&
            driver.used == [true, false] && driver.generations == [0, 0] &&
            driver.records[1].is_none(), 1025);
    let record = driver.records[0].as_ref().unwrap();
    require(record.channel == ChannelPhase::Returned && record.reader == reader &&
            record.writer.is_some() && record.worker.is_none() && record.error.is_none() &&
            record.reserved && record.token == token, 1026);
    if cfg!(receipt_close) {
        driver.closed = true; // Inject local cancellation while the real receipt is held.
        require(!driver.deliver_channel(&owner, 0, token, 0x24000, 0xb0000101) &&
                !driver.receive_channel(a, 0) && !driver.reserve(&owner, other, 1) &&
                !driver.can_launch(0), 1028);
        require(driver.pending == Some(0) && driver.acquisitions == 1 && driver.used == [true, false] &&
                driver.records[0].as_ref().unwrap().channel == ChannelPhase::Returned, 1028);
    } else {
        require(driver.deliver_channel(&owner, 0, token, 0x24000, 0xb0000101), 1027);
        if !cfg!(receipt_identity) {
            require(!driver.deliver_channel(&owner, 0, token, 0x24000, 0xb0000101) &&
                    !driver.receive_channel(a, 0), 1027);
        }
        require(driver.acquisitions == 1 && driver.pending.is_none() &&
                driver.records[0].as_ref().unwrap().channel == ChannelPhase::Applied, 1027);
    }
    let record = driver.records[0].as_mut().unwrap();
    require(record.reader == reader && record.writer.is_some() && record.worker.is_none() &&
            record.error.is_none() && record.reserved && record.token == token, 1026);
    dispose_pair(a, record.reader.unwrap(), record.writer.unwrap());
    record.reader = None; record.writer = None;
    require(!driver.reserve(&owner, token, 0) && driver.used == [true, false] &&
            driver.generations == [0, 0] && a.clean(), 1028);
    // Explicit fixture accounting only; no retirement or lifecycle event.
    for slot in [0, 1, 0] { ordinary(a, slot); }
    require(a.clean(), 1028); finish(100)
}

// Real launch return retained locally, before generation application or routing.
pub fn run_launch_receipt(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let other = black_box(&ISSUED[1]);
    require(driver.reserve(&owner, token, 0) && driver.acquire(a, 0), 1029);
    let reader = driver.records[0].as_ref().unwrap().reader;
    require(driver.receive_launch(a, 0), 1029);
    let worker = driver.records[0].as_ref().unwrap().worker.unwrap();
    require(driver.records[0].as_ref().unwrap().writer.is_none(), 1030);
    require(driver.generations == [0, 0], 1031);
    if cfg!(launch_early_generation) { finish(1032); } // Unexpected control survival.
    if !cfg!(launch_receipt_close) {
        require(!driver.receive_launch(a, 0) && !driver.can_launch(0) &&
                !driver.reserve(&owner, other, 1) && !driver.launched(&owner, 0, token, worker), 1029);
    }
    let record = driver.records[0].as_ref().unwrap();
    require(driver.launches == 1 && driver.acquisitions == 1 && driver.pending == Some(0) &&
            driver.used == [true, false] && driver.records[1].is_none() &&
            record.launch_phase == ChannelPhase::Returned && record.reader == reader &&
            reader.is_some() && worker.matches_target(0xb0000101) && record.error.is_none() &&
            record.token == token && record.reserved, 1029);
    if cfg!(launch_receipt_close) {
        driver.closed = true; // Trusted local closure, not transport/cancellation delivery.
        require(!driver.apply_launch(0) && !driver.receive_launch(a, 0) &&
                !driver.reserve(&owner, other, 1) && !driver.launched(&owner, 0, token, worker) &&
                driver.pending == Some(0) && driver.generations == [0, 0] &&
                driver.records[0].as_ref().unwrap().launch_phase == ChannelPhase::Returned, 1029);
    } else {
        require(driver.apply_launch(0) && driver.launched(&owner, 0, token, worker), 1029);
        require(!driver.apply_launch(0) && !driver.receive_launch(a, 0) &&
                driver.pending.is_none() && driver.generations == [1, 0] &&
                driver.records[0].as_ref().unwrap().launch_phase == ChannelPhase::Applied, 1029);
    }
    let record = driver.records[0].as_ref().unwrap();
    require(driver.launches == 1 && record.worker == Some(worker) && record.reader == reader &&
            record.writer.is_none() && record.error.is_none() && record.token == token &&
            driver.used == [true, false], 1029);
    dispose_bound(a, &mut driver, 0);
    require(!driver.reserve(&owner, token, 0) && driver.used == [true, false] && a.clean(), 1029);
    for slot in [1, 0] { ordinary(a, slot); }
    require(a.clean(), 1029); finish(100)
}

// Synthetic absence: the selected start transition has NO corresponding syscall.
pub fn run_missing_return(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let other = black_box(&ISSUED[1]);
    require(driver.reserve(&owner, token, 0) && !driver.close_missing(0) && !driver.closed, 1033);
    if cfg!(missing_launch) || cfg!(missing_forget_writer) {
        require(driver.acquire(a, 0) && driver.start_launch(0), 1033);
    } else {
        require(driver.start_channel(0) && a.clean(), 1033);
    }
    require(!driver.close_missing(1) && !driver.closed && driver.close_missing(0), 1033);
    require(driver.closed && driver.pending == Some(0), 1033);
    require(driver.records[0].as_ref().unwrap().error.is_none(), 1034);
    let record = driver.records[0].as_ref().unwrap();
    if cfg!(missing_launch) || cfg!(missing_forget_writer) {
        require(record.reader.is_some() && record.writer.is_some(), 1035);
        require(record.channel == ChannelPhase::Applied && record.launch_phase == ChannelPhase::Started &&
                driver.launches == 1 && !a.clean(), 1033);
    } else {
        require(record.channel == ChannelPhase::Started && record.launch_phase == ChannelPhase::Reserved &&
                record.reader.is_none() && record.writer.is_none() && driver.launches == 0, 1033);
    }
    require(record.worker.is_none() && record.reserved && record.token == token &&
            driver.acquisitions == 1 && driver.generations == [0, 0] && driver.used == [true, false] &&
            driver.records[1].is_none(), 1033);
    require(!driver.close_missing(0) && !driver.start_channel(0) && !driver.start_launch(0) &&
            !driver.apply_channel(0, true) && !driver.apply_launch(0) &&
            !driver.reserve(&owner, token, 0) && !driver.reserve(&owner, other, 1), 1033);
    let record = driver.records[0].as_mut().unwrap();
    require(record.error.is_none() && record.worker.is_none() && driver.pending == Some(0) &&
            driver.acquisitions == 1 && driver.generations == [0, 0] && driver.used == [true, false], 1034);
    if cfg!(missing_launch) || cfg!(missing_forget_writer) {
        require(record.launch_phase == ChannelPhase::Started && driver.launches == 1, 1033);
        // Teardown authority is fixture knowledge that start_launch never invoked
        // Adapter::launch here. This is forbidden for genuinely unknown transfer.
        dispose_pair(a, record.reader.unwrap(), record.writer.unwrap());
        record.reader = None; record.writer = None;
    } else { require(record.channel == ChannelPhase::Started && driver.launches == 0, 1033); }
    require(a.clean() && driver.closed && driver.pending == Some(0) && driver.used == [true, false], 1033);
    for slot in [0, 1, 0] { ordinary(a, slot); }
    require(a.clean(), 1033); finish(100)
}

#[inline]
fn sample_setup(a: &mut Adapter, driver: &mut Driver) -> Worker {
    // Fixture-only admitted-state seed from actual handles, not a production
    // adoption API. Driver launch composition retains its separate witnesses.
    let (reader, worker) = fixture_worker(a, 0);
    require(worker.matches_target(0xb0000101), 1041);
    driver.records[0] = Some(Binding { sample_started: false, fact: None,
        channel: ChannelPhase::Applied, launch_phase: ChannelPhase::Returned,
        token: &ISSUED[0], slot: 0, reserved: true, expected: 0xb0000101,
        reader: Some(reader), writer: None, worker: Some(worker), error: None });
    driver.used[0] = true; driver.pending = None;
    driver.records[0].as_mut().unwrap().launch_phase = ChannelPhase::Applied;
    driver.pending = None; driver.generations[0] = 1;
    driver.acquisitions = 1; driver.launches = 1;
    worker
}
pub fn run_sampling(a: &mut Adapter) -> ! {
    let owner = context(); let foreign = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let other = black_box(&ISSUED[1]);
    let worker = sample_setup(a, &mut driver);
    let mut storage = Sample::new();
    if cfg!(sampling_status_stale) || cfg!(sampling_observe_stale) {
        terminal(a, worker, 18);
        let mut session = Sampling::begin(&mut driver, &mut storage, &owner, 0, token, worker).unwrap_or_else(|| finish(1042));
        require(session.receive(a), 1042);
        if cfg!(sampling_observe_stale) { require(session.receive(a), 1042); }
        let prefix = *session.sample.receipts();
        dispose_bound(a, session.driver, 0);
        session.driver.records[0].as_mut().unwrap_or_else(|| finish(1042)).worker = Some(worker); // Diagnostic only.
        let (reader, replacement) = fixture_worker(a, 0);
        require(replacement.matches_target(0xb0000201) && !session.receive(a), 1042);
        let index = if cfg!(sampling_observe_stale) { 2 } else { 1 };
        let operation = if index == 2 { 0x25001 } else { 0x20001 };
        require(session.sample.received() == index + 1 && session.sample.receipts()[0] == prefix[0] &&
                (index == 1 || session.sample.receipts()[1] == prefix[1]) &&
                session.sample.receipts()[index].unwrap_or_else(|| finish(1042)).rax == -9 &&
                session.sample.state() == State::Failed(Failure::Native { operation, errno: 9 }), 1042);
        let record = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1042));
        require(session.driver.closed && session.driver.pending == Some(0) && record.worker == Some(worker) &&
                record.fact.is_none() && record.error == Some(Error { operation, errno: 9 }), 1042);
        fixture_finish(a, reader, replacement); ordinary(a, 1);
    } else if cfg!(sampling_stale) {
        dispose_bound(a, &mut driver, 0);
        driver.records[0].as_mut().unwrap_or_else(|| finish(1042)).worker = Some(worker); // Diagnostic stale target, not ownership.
        let (reader, replacement) = fixture_worker(a, 0);
        require(replacement.matches_target(0xb0000201), 1041);
        let mut session = Sampling::begin(&mut driver, &mut storage, &owner, 0, token, worker).unwrap_or_else(|| finish(1042));
        require(!session.read(a), 1041);
        let record = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1042));
        require(session.driver.closed && session.driver.reads == 1 && session.driver.pending == Some(0) &&
                record.sample_started && record.fact.is_none() && record.worker == Some(worker) &&
                record.error == Some(Error { operation: 0x25001, errno: 9 }), 1041);
        require(session.sample.received() == 1 && session.sample.receipts()[0].unwrap_or_else(|| finish(1042)).rax == -9 &&
                session.sample.state() == State::Failed(Failure::Native { operation: 0x25001, errno: 9 }), 1042);
        fixture_finish(a, reader, replacement); ordinary(a, 1);
    } else if cfg!(sampling_preflight) {
        require(!driver.begin_sample(&foreign, 0, token, worker) &&
                !driver.begin_sample(&owner, 2, token, worker), 1040);
        require(driver.reads == 0 && driver.pending.is_none() &&
                !driver.records[0].as_ref().unwrap_or_else(|| finish(1042)).sample_started, 1040);
        require(driver.begin_sample(&owner, 0, token, worker) && driver.reads == 0, 1039);
        dispose_bound(a, &mut driver, 0); ordinary(a, 1); ordinary(a, 0);
    } else if cfg!(sampling_target) || cfg!(sampling_skip_token) {
        let (reader, other_worker) = fixture_worker(a, 1);
        require(!driver.begin_sample(&owner, 0, token, other_worker), 1040);
        require(!driver.begin_sample(&owner, 0, other, worker), 1040);
        require(driver.reads == 0 && driver.pending.is_none() &&
                !driver.records[0].as_ref().unwrap_or_else(|| finish(1042)).sample_started, 1040);
        require(driver.begin_sample(&owner, 0, token, worker) && driver.reads == 0, 1039);
        dispose_bound(a, &mut driver, 0); fixture_finish(a, reader, other_worker); ordinary(a, 0);
    } else {
        if cfg!(sampling_held) {
            driver.records[0].as_mut().unwrap_or_else(|| finish(1042)).launch_phase = ChannelPhase::Returned;
            require(!driver.begin_sample(&owner, 0, token, worker) && driver.reads == 0, 1041);
            driver.records[0].as_mut().unwrap_or_else(|| finish(1042)).launch_phase = ChannelPhase::Applied;
        }
        terminal(a, worker, 18);
        let mut session = Sampling::begin(&mut driver, &mut storage, &owner, 0, token, worker).unwrap_or_else(|| finish(1042));
        require(!session.driver.begin_sample(&owner, 0, token, worker) && session.driver.reads == 0 &&
                session.driver.pending == Some(0), 1039);
        require(session.read(a), 1041);
        require(session.sample.received() == 3 && session.sample.receipts()[0] == session.sample.receipts()[2] &&
                session.sample.receipts()[1].unwrap_or_else(|| finish(1042)).rax == 18, 1042);
        let fact = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1042)).fact.unwrap_or_else(|| finish(1042));
        require(fact.kind == 1 && fact.result == 18 && fact.revision > 0 && fact.historical_ready &&
                session.driver.reads == 3 && session.driver.pending == Some(0) && !session.driver.closed, 1041);
        require(!session.read(a) && !session.driver.begin_sample(&owner, 0, token, worker) &&
                !session.driver.reserve(&owner, other, 1) && session.driver.reads == 3, 1041);
        dispose_bound(a, session.driver, 0); ordinary(a, 1); ordinary(a, 0);
    }
    require(a.clean() && driver.used == [true, false], 1041);
    finish(100)
}

// These selectors fold away in every ordinary native configuration.
#[inline(always)]
fn malformed_boolean() -> bool {
    cfg!(seal_failed) || cfg!(sample_bad_boolean) || cfg!(sample_skip_close) ||
    cfg!(sample_forget_reader) || cfg!(sample_invent_errno)
}
#[inline(always)]
fn malformed_status() -> bool {
    malformed_boolean() || cfg!(sample_bad_kind) || cfg!(sample_bad_result) || cfg!(sample_bad_live)
}
pub fn run_malformed_sampling(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]);
    let worker = sample_setup(a, &mut driver);
    let reader = driver.records[0].as_ref().unwrap_or_else(|| finish(1042)).reader;
    terminal(a, worker, 18);
    let mut storage = Sample::new();
    let mut session = Sampling::begin(&mut driver, &mut storage, &owner, 0, token, worker).unwrap_or_else(|| finish(1042));
    require(session.receive(a), 1042);
    let first = session.sample.receipts()[0].unwrap_or_else(|| finish(1042));
    require(first.rax > 0 && first.rdx == 18 && first.r8 == 1, 1042);
    if !malformed_boolean() { require(session.receive(a), 1042); }
    require(!session.receive(a), 1042);
    let cause = if malformed_boolean() { Cause::Boolean }
                else if cfg!(sample_bad_kind) { Cause::KindPair }
                else if cfg!(sample_bad_revision) { Cause::Revision }
                else if cfg!(sample_bad_readiness) { Cause::Readiness }
                else { Cause::Result };
    let status = Raw { rax: if cfg!(sample_bad_live) { 0 } else if cfg!(sample_bad_result) { 19 } else { 18 },
                       rdx: if malformed_boolean() { 2 } else { 1 },
                       r8: if cfg!(sample_bad_kind) { 4 } else if cfg!(sample_bad_live) { 0 } else { 1 } };
    let last = if malformed_boolean() { None }
               else { Some(Raw { rax: first.rax + if cfg!(sample_bad_revision) { 1 } else { 0 },
                                 rdx: 18, r8: if cfg!(sample_bad_readiness) { 0 } else { 1 } }) };
    let expected_reads = if malformed_boolean() { 1 } else { 2 };
    require(session.sample.received() == if malformed_boolean() { 2 } else { 3 } &&
            *session.sample.receipts() == [Some(first), Some(status), last] &&
            session.sample.state() == State::Failed(Failure::Local(cause)), 1042);
    require(session.driver.closed && session.driver.pending == Some(0), 1043);
    let record = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1042));
    require(record.worker == Some(worker) && reader.is_some() && record.reader == reader &&
            record.writer.is_none() && record.token == token && record.fact.is_none() &&
            record.launch_phase == ChannelPhase::Applied && record.sample_started, 1044);
    require(record.error.is_none(), 1045);
    require(!session.receive(a) && session.driver.reads == expected_reads &&
            session.driver.used == [true, false] && session.driver.generations == [1, 0] &&
            session.driver.acquisitions == 1 && session.driver.launches == 1, 1042);
    dispose_bound(a, session.driver, 0); ordinary(a, 1); ordinary(a, 0);
    require(a.clean(), 1042); finish(100)
}

// Reuse the same full retention check before and after denied follow-up calls.
#[inline(never)]
fn interrupted_prefix(sample: &Sample, prefix: &[Option<Raw>; 3], count: usize) -> bool {
    sample.received() == count && sample.receipts() == prefix &&
        sample.state() == State::Failed(Failure::Local(Cause::Interrupted))
}
pub fn run_interrupted_sampling(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]);
    let worker = sample_setup(a, &mut driver);
    let reader = driver.records[0].as_ref().unwrap_or_else(|| finish(1042)).reader;
    terminal(a, worker, 18);
    let mut storage = Sample::new();
    let mut session = Sampling::begin(&mut driver, &mut storage, &owner, 0, token, worker).unwrap_or_else(|| finish(1042));
    if cfg!(interrupt_empty) {
    require(!session.interrupt_synthetic() && session.driver.reads == 0 &&
            !session.driver.closed && session.driver.pending == Some(0) &&
            session.sample.received() == 0 && session.sample.state() == State::Awaiting, 1046);
        dispose_bound(a, session.driver, 0); ordinary(a, 1); ordinary(a, 0);
        require(a.clean(), 1049); finish(100)
    }
    require(session.receive(a), 1042);
    if cfg!(interrupt_after_status) { require(session.receive(a), 1042); }
    let prefix = *session.sample.receipts();
    let count = if cfg!(interrupt_after_status) { 2 } else { 1 };
    let first = prefix[0].unwrap_or_else(|| finish(1042));
    require(first.rax > 0 && first.rdx == 18 && first.r8 == 1 && prefix[2].is_none() &&
            prefix[1] == if cfg!(interrupt_after_status) { Some(Raw { rax: 18, rdx: 1, r8: 1 }) } else { None }, 1047);
    require(session.interrupt_synthetic() && session.driver.closed &&
            session.driver.pending == Some(0), 1046);
    require(interrupted_prefix(session.sample, &prefix, count), 1047);
    let record = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1042));
    require(record.fact.is_none() && record.error.is_none(), 1048);
    require(record.worker == Some(worker) && reader.is_some() && record.reader == reader &&
            record.writer.is_none() && record.token == token &&
            record.launch_phase == ChannelPhase::Applied && record.sample_started, 1049);
    require(!session.interrupt_synthetic() && !session.receive(a) && !session.read(a) &&
            session.driver.reads as usize == count && interrupted_prefix(session.sample, &prefix, count) &&
            session.driver.used == [true, false] && session.driver.generations == [1, 0] &&
            session.driver.acquisitions == 1 && session.driver.launches == 1, 1047);
    dispose_bound(a, session.driver, 0); ordinary(a, 1); ordinary(a, 0);
    require(a.clean(), 1049); finish(100)
}

// One independent full-state oracle before and after replay/denial.
#[inline(never)]
fn history_retained(session: &Sampling, token: &Token, worker: Worker) -> bool {
    let record = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1051));
    !session.driver.closed && session.driver.pending == Some(0) &&
        session.driver.reads == 3 && session.driver.used == [true, false] &&
        session.driver.generations == [1, 0] && session.driver.acquisitions == 1 &&
        session.driver.launches == 1 && record.worker == Some(worker) &&
        record.reader.is_some() && record.writer.is_none() && record.error.is_none() &&
        record.token == token && record.fact.is_some()
 && session.sample.received() == 3 &&
        session.sample.receipts()[0] == session.sample.receipts()[2] &&
        session.sample.receipts()[1] == Some(Raw { rax: 18, rdx: 1, r8: 1 })
}

// PH-01/02: real bound capture, read-only replay; fixture disposal is not retirement.
pub fn run_history(a: &mut Adapter) -> ! {
    let owner = context(); let foreign = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]);
    let worker = sample_setup(a, &mut driver);
    terminal(a, worker, 18);
    let mut storage = Sample::new();
    let mut session = Sampling::begin(&mut driver, &mut storage, &owner, 0, token, worker)
        .unwrap_or_else(|| finish(1051));
    if cfg!(history_unsealed) {
        require(session.terminal_view().is_none() && session.driver.reads == 0 &&
            !session.driver.closed && session.driver.pending == Some(0), 1051);
        dispose_bound(a, session.driver, 0); ordinary(a, 1); ordinary(a, 0);
        require(a.clean(), 1051); finish(100)
    }
    require(session.read(a), 1051);
    require(history_retained(&session, token, worker), 1051);
    let prefix = *session.sample.receipts();
    let view = session.terminal_view().unwrap_or_else(|| finish(1051));
    if cfg!(history_identity) || cfg!(history_skip_token) {
        for field in 0..10 {
            let mut wrong = *token; wrong.0[field] = black_box(wrong.0[field] + 10);
            require(view.replay(&owner, &wrong, 0, worker) == Replay::Denied, 1050);
        }
    }
    if cfg!(history_service) {
        require(view.replay(&owner, black_box(&ISSUED[1]), 0, worker) == Replay::Denied, 1050);
    }
    if cfg!(history_context) {
        require(view.replay(black_box(&foreign), token, 0, worker) == Replay::Denied, 1050);
    }
    if cfg!(history_index) {
        for index in black_box([1usize, 2]) {
            require(view.replay(&owner, token, index, worker) == Replay::Denied, 1050);
        }
    }
    if cfg!(history_target) {
        // A real equal-generation worker from the other slot, never a numeric cast.
        let (reader, other) = fixture_worker(a, 1);
        require(view.replay(&owner, token, 0, black_box(other)) == Replay::Denied, 1050);
        fixture_finish(a, reader, other);
    }
    require(view.replay(&owner, token, 0, worker) == Replay::Duplicate &&
        view.replay(&owner, token, 0, worker) == Replay::Duplicate &&
        history_prefix(view.sample(), &prefix), 1051);
    require(history_retained(&session, token, worker), 1051);
    dispose_bound(a, session.driver, 0);
    if !cfg!(history_target) { ordinary(a, 1); }
    ordinary(a, 0); require(a.clean(), 1051); finish(100)
}

#[inline(never)]
fn history_prefix(sample: &Sample, prefix: &[Option<Raw>; 3]) -> bool {
    for i in 0..3 {
        if sample.receipts()[i] != prefix[i] { return false; }
    }
    true
}


// Exclusive Driver ownership and both borrowed histories live together.
struct Pending<'a, 'b> {
    driver: &'a mut Driver<'b>,
    held: Held<'a, Context, Token, Worker>,
    spare: Option<&'a mut Sample>,
    produced: Option<&'a Sample>,
    index: usize,
}
impl<'a, 'b: 'a> Pending<'a, 'b> {
    // Failure returns the original session and reserved storage unchanged.
    #[inline(always)]
    fn begin(session: Sampling<'a, 'b>, spare: &'a mut Sample)
        -> Result<Self, (Sampling<'a, 'b>, &'a mut Sample)> {
        if session.terminal_view().is_none() || spare.received() != 0 || spare.state() != State::Awaiting {
            if cfg!(guard_denial_forget_reader) {
                session.driver.records[session.index].as_mut().unwrap_or_else(|| finish(1055)).reader = None;
            }
            if cfg!(guard_denial_clear_spare) { *spare = Sample::new(); }
            return Err((session, spare));
        }
        let Sampling { driver, sample, index } = session;
        let record = driver.records.get(index).and_then(Option::as_ref).unwrap_or_else(|| finish(1052));
        let view = View::terminal(driver.owner, record.token, index,
            record.worker.unwrap_or_else(|| finish(1052)), sample).unwrap_or_else(|| finish(1052));
        Ok(Self { driver, held: Held::new(view), spare: Some(spare), produced: None, index })
    }
    #[inline(always)]
    fn conflict_synthetic(&mut self) -> Offer {
        self.conflict_synthetic_counted(&mut 0)
    }
    #[inline(always)]
    fn conflict_synthetic_counted(&mut self, entered: &mut u8) -> Offer {
        if self.driver.closed && !cfg!(guard_reoffer_produce) { return Offer::Closed; }
        let record = self.driver.records.get(self.index).and_then(Option::as_ref).unwrap_or_else(|| finish(1052));
        let owner = self.driver.owner; let token = record.token;
        let worker = record.worker.unwrap_or_else(|| finish(1052)); let index = self.index;
        let first = self.held.primary().receipts()[0].unwrap_or_else(|| finish(1052));
        let outcome = self.held.offer_synthetic(owner, token, index, worker, || {
            // Bounded fixture witness: count entry even if storage is unavailable.
            *entered += 1;
            let sample = self.spare.take()?;
            // Exactly one labelled synthetic candidate, no Adapter or syscall.
            for raw in [Raw { rax: first.rax, rdx: 19, r8: first.r8 },
                        Raw { rax: 19, rdx: first.r8, r8: 1 },
                        Raw { rax: first.rax, rdx: 19, r8: first.r8 }] {
                require(sample.push(raw), 1052);
            }
            let sample: &'a Sample = sample;
            self.produced = Some(sample);
            View::terminal(owner, token, index, worker, sample)
        });
        if outcome == Offer::Conflict {
            if !cfg!(guard_skip_close) { self.driver.closed = true; }
            if cfg!(guard_forget_reader) { self.driver.records.get_mut(index).and_then(Option::as_mut).unwrap_or_else(|| finish(1052)).reader = None; }
        }
        outcome
    }
}

pub fn run_conflict_guard(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let worker = sample_setup(a, &mut driver);
    let reader = driver.records[0].as_ref().unwrap().reader;
    terminal(a, worker, 18);
    let mut primary = Sample::new(); let mut diagnostic = Sample::new();
    let mut session = Sampling::begin(&mut driver, &mut primary, &owner, 0, token, worker)
        .unwrap_or_else(|| finish(1052));
    require(session.read(a), 1052);
    let first = session.sample.receipts()[0].unwrap_or_else(|| finish(1052));
    require(first.rax > 0 && first.rdx == 18 && first.r8 == 1 &&
        guard_prefix(session.sample, first.rax, 18), 1052);
    let mut pending = Pending::begin(session, &mut diagnostic).unwrap_or_else(|_| finish(1052));
    require(pending.conflict_synthetic() == Offer::Conflict, 1052);
    require(guard_prefix(pending.held.primary(), first.rax, 18), 1052);
    if !cfg!(guard_resources) && !cfg!(guard_forget_reader) {
    let other = pending.held.diagnostic().unwrap_or_else(|| finish(1052));
    require(guard_prefix(other, first.rax, 19), 1052);
    }
    require(pending.driver.closed && pending.held.is_closed(), 1053);
    if cfg!(guard_resources) || cfg!(guard_forget_reader) {
    let record = pending.driver.records[0].as_ref().unwrap_or_else(|| finish(1054));
    require(reader.is_some() && record.reader == reader && record.worker == Some(worker) &&
        record.writer.is_none() && record.error.is_none() && record.token == token &&
        record.fact.unwrap_or_else(|| finish(1054)).result == 18 && pending.driver.reads == 3 &&
        pending.driver.pending == Some(0) && pending.driver.used == [true, false] &&
        pending.driver.generations == [1, 0] && pending.driver.acquisitions == 1 &&
        pending.driver.launches == 1, 1054);
    }
    require(pending.conflict_synthetic() == Offer::Closed && pending.spare.is_none() &&
        guard_prefix(pending.held.primary(), first.rax, 18), 1053);
    dispose_bound(a, pending.driver, 0); ordinary(a, 1); ordinary(a, 0);
    require(a.clean(), 1054); finish(100)
}

#[inline(never)]
fn guard_prefix(sample: &Sample, revision: i64, result: u64) -> bool {
    if sample.received() != 3 { return false; }
    for (index, raw) in sample.receipts().iter().enumerate() {
        let expected = if index == 1 { Raw { rax: result as i64, rdx: 1, r8: 1 } }
                       else { Raw { rax: revision, rdx: result, r8: 1 } };
        if *raw != Some(expected) { return false; }
    }
    true
}


pub fn run_guard_denial(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let worker = sample_setup(a, &mut driver);
    let reader = driver.records[0].as_ref().unwrap().reader;
    terminal(a, worker, 18);
    let mut primary = Sample::new(); let mut diagnostic = Sample::new();
    let mut session = Sampling::begin(&mut driver, &mut primary, &owner, 0, token, worker)
        .unwrap_or_else(|| finish(1055));
    let unsealed = cfg!(guard_denial_unsealed);
    if !unsealed {
        require(session.read(a), 1055);
        require(diagnostic.push(Raw { rax: 1, rdx: 18, r8: 1 }), 1056);
    }
    let driver_address = session.driver as *const Driver;
    let primary_address = session.sample as *const Sample;
    let spare_address = &diagnostic as *const Sample;
    let primary_before = session.sample.clone(); let spare_before = diagnostic.clone();
    let (mut session, spare) = match Pending::begin(session, &mut diagnostic) {
        Err(returned) => returned,
        Ok(_) => finish(1055),
    };
    require(core::ptr::eq(session.driver, driver_address) &&
        core::ptr::eq(session.sample, primary_address) && core::ptr::eq(spare, spare_address) &&
        *session.sample == primary_before, 1055);
    require(*spare == spare_before, 1056);
    let record = session.driver.records[0].as_ref().unwrap_or_else(|| finish(1055));
    require(reader.is_some() && record.reader == reader && record.worker == Some(worker) &&
        record.writer.is_none() && record.error.is_none() && record.token == token &&
        record.sample_started == !unsealed &&
        session.driver.reads == if unsealed { 0 } else { 3 } &&
        !session.driver.closed && session.driver.pending == Some(0) &&
        session.driver.used == [true, false] && session.driver.generations == [1, 0] &&
        session.driver.acquisitions == 1 && session.driver.launches == 1, 1055);
    if unsealed {
        require(session.read(a), 1055);
        let pending = Pending::begin(session, spare).unwrap_or_else(|_| finish(1055));
        dispose_bound(a, pending.driver, 0);
    } else {
        dispose_bound(a, session.driver, 0);
        require(*spare == spare_before, 1056);
    }
    ordinary(a, 1); ordinary(a, 0); require(a.clean(), 1055); finish(100)
}

pub fn run_guard_reoffer(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]); let worker = sample_setup(a, &mut driver);
    terminal(a, worker, 18);
    let mut primary = Sample::new(); let mut diagnostic = Sample::new();
    let mut session = Sampling::begin(&mut driver, &mut primary, &owner, 0, token, worker)
        .unwrap_or_else(|| finish(1057));
    require(session.read(a), 1057);
    let revision = session.sample.receipts()[0].unwrap_or_else(|| finish(1057)).rax;
    let mut pending = Pending::begin(session, &mut diagnostic).unwrap_or_else(|_| finish(1057));
    let mut entered = 0;
    require(pending.conflict_synthetic_counted(&mut entered) == Offer::Conflict && entered == 1, 1057);
    let outcome = pending.conflict_synthetic_counted(&mut entered);
    require(entered == 1, 1057);
    require(outcome == Offer::Closed && pending.driver.closed && pending.held.is_closed() &&
        pending.spare.is_none() && guard_prefix(pending.held.primary(), revision, 18) &&
        guard_prefix(pending.held.diagnostic().unwrap_or_else(|| finish(1057)), revision, 19), 1057);
    dispose_bound(a, pending.driver, 0); ordinary(a, 1); ordinary(a, 0);
    require(a.clean(), 1057); finish(100)
}

// One exclusive owner keeps all three stores alive across sampling handles.
struct History<'a> {
    driver: Driver<'a>,
    primary: [Sample; 2],
    diagnostic: Sample,
    diagnostic_for: Option<usize>,
}
impl<'a> History<'a> {
    fn new(driver: Driver<'a>) -> Self {
        Self { driver, primary: [Sample::new(), Sample::new()],
            diagnostic: Sample::new(), diagnostic_for: None }
    }
    #[inline(always)]
    fn replay(&mut self, index: usize) -> Replay {
        if index >= self.primary.len() { return Replay::Denied; }
        let session = Sampling { driver: &mut self.driver, sample: &mut self.primary[index], index };
        let Some(view) = session.terminal_view() else {
            if cfg!(seal_promote) { return Replay::Duplicate; }
            if cfg!(seal_forget_sample) { *session.sample = Sample::new(); }
            if cfg!(seal_forget_reader) {
                session.driver.records[index].as_mut().unwrap_or_else(|| finish(1063)).reader = None;
            }
            return Replay::Denied;
        };
        let record = session.driver.records[index].as_ref().unwrap_or_else(|| finish(1061));
        view.replay(session.driver.owner, record.token, index,
            record.worker.unwrap_or_else(|| finish(1061)))
    }
    #[inline(always)]
    fn capture(&mut self, a: &Adapter, index: usize, worker: Worker) -> bool {
        if index >= self.primary.len() { return false; }
        if cfg!(capacity_forget_live) && index == 1 { self.primary[0] = Sample::new(); }
        if cfg!(capacity_recycle_primary) && self.primary[index].received() != 0 {
            self.primary[index] = Sample::new();
            self.driver.records[index].as_mut().unwrap_or_else(|| finish(1059)).sample_started = false;
            self.driver.pending = None;
        }
        let owner = self.driver.owner;
        let token = &ISSUED[index];
        let Some(mut session) = Sampling::begin(&mut self.driver, &mut self.primary[index],
            owner, index, token, worker) else { return false; };
        session.read(a)
    }
    #[inline(always)]
    fn conflict(&mut self, index: usize, entered: &mut u8) -> Offer {
        if cfg!(capacity_recycle_diagnostic) && self.diagnostic_for.is_some() {
            self.diagnostic = Sample::new(); self.diagnostic_for = None;
            self.driver.closed = false;
        }
        if self.driver.closed { return Offer::Closed; }
        if index >= self.primary.len() || self.diagnostic_for.is_some() { return Offer::Denied; }
        // Reconstitute only the original retained association, never a fresh sample.
        let session = Sampling { driver: &mut self.driver, sample: &mut self.primary[index], index };
        let Ok(mut pending) = Pending::begin(session, &mut self.diagnostic) else { return Offer::Denied; };
        let result = pending.conflict_synthetic_counted(entered);
        if result == Offer::Conflict { self.diagnostic_for = Some(index); }
        result
    }
}

pub fn run_history_capacity(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    // Fixture-only admission using actual handles; full launch composition is separate.
    for index in 0..2 {
        let (reader, writer) = accepted(a.channel(), 1058);
        let mode: &[u8] = if index == 0 { b"silent" } else { b"terminal-exit17" };
        let worker = accepted(a.launch(index, writer, mode), 1058);
        let expected = 0xb0000101 + index as u64;
        require(worker.matches_target(expected), 1058);
        driver.records[index] = Some(Binding { sample_started: false, fact: None,
            channel: ChannelPhase::Applied, launch_phase: ChannelPhase::Applied,
            token: &ISSUED[index], slot: index, reserved: true, expected,
            reader: Some(reader), writer: None, worker: Some(worker), error: None });
        driver.used[index] = true; driver.generations[index] = 1;
    }
    driver.acquisitions = 2; driver.launches = 2;
    let first = driver.records[0].as_ref().unwrap().worker.unwrap();
    let second = driver.records[1].as_ref().unwrap().worker.unwrap();
    let readers = [driver.records[0].as_ref().unwrap().reader, driver.records[1].as_ref().unwrap().reader];
    let mut history = History::new(driver);
    require(history.primary.len() == 2 && history.primary[0].receipts().len() +
        history.primary[1].receipts().len() + history.diagnostic.receipts().len() == 9, 1058);
    require(history.capture(a, 0, first) && history.primary[0].state() == State::Live &&
        history.primary[0].received() == 1 && history.driver.pending.is_none() && history.driver.reads == 1, 1058);
    let live = history.primary[0].receipts()[0];
    terminal(a, second, 18);
    require(history.capture(a, 1, second), 1058);
    let revision = history.primary[1].receipts()[0].unwrap_or_else(|| finish(1058)).rax;
    require(history.primary[0].state() == State::Live && history.primary[0].received() == 1 &&
        history.primary[0].receipts()[0] == live && guard_prefix(&history.primary[1], revision, 18), 1058);
    let denied = history.capture(a, 0, first);
    require(!denied && history.driver.reads == 4 && history.primary[0].received() == 1 &&
        history.primary[0].receipts()[0] == live && history.driver.pending == Some(1), 1059);
    require(!history.capture(a, 2, second) && history.driver.reads == 4, 1059);
    let mut entered = 0;
    require(history.conflict(1, &mut entered) == Offer::Conflict && entered == 1, 1060);
    let repeated = history.conflict(1, &mut entered);
    require(entered == 1 && repeated == Offer::Closed, 1060);
    require(history.diagnostic_for == Some(1) && history.driver.closed &&
        history.driver.pending == Some(1) && history.driver.reads == 4 &&
        history.primary[0].received() == 1 && history.primary[0].receipts()[0] == live &&
        guard_prefix(&history.primary[1], revision, 18) && guard_prefix(&history.diagnostic, revision, 19), 1060);
    for (index, worker) in [first, second].iter().enumerate() {
        let record = history.driver.records[index].as_ref().unwrap_or_else(|| finish(1060));
        require(record.reader == readers[index] && readers[index].is_some() &&
            record.worker == Some(*worker) && record.writer.is_none() && record.error.is_none() &&
            record.token == &ISSUED[index] && record.sample_started, 1060);
    }
    require(history.driver.used == [true, true] && history.driver.generations == [1, 1] &&
        history.driver.acquisitions == 2 && history.driver.launches == 2, 1060);
    accepted(a.stop(first), 1060); terminal(a, first, 144);
    require(history.primary[0].state() == State::Live && history.primary[0].receipts()[0] == live, 1060);
    accepted(a.close(readers[0].unwrap()), 1060); reclaim(a, first);
    dispose_bound(a, &mut history.driver, 1);
    let (reader, writer) = accepted(a.channel(), 1060);
    let replacement = accepted(a.launch(1, writer, b"terminal-exit17"), 1060);
    fixture_finish(a, reader, replacement);
    require(a.clean(), 1060); finish(100)
}

// PH-06: source qualification and retained owner state across ineligible replay.
pub fn run_history_sealing(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let live = cfg!(seal_live);
    let second = cfg!(seal_partial_two) || cfg!(seal_interrupt_two) || cfg!(seal_failed);
    let interrupted = cfg!(seal_interrupt_one) || cfg!(seal_interrupt_two);
    let closed = interrupted || cfg!(seal_failed);
    let (reader, writer) = accepted(a.channel(), 1061);
    let worker = accepted(a.launch(0, writer, if live { b"silent" } else { b"terminal-exit17" }), 1061);
    require(worker.matches_target(0xb0000101), 1061);
    driver.records[0] = Some(Binding { sample_started: false, fact: None,
        channel: ChannelPhase::Applied, launch_phase: ChannelPhase::Applied,
        token: &ISSUED[0], slot: 0, reserved: true, expected: 0xb0000101,
        reader: Some(reader), writer: None, worker: Some(worker), error: None });
    driver.used[0] = true; driver.generations[0] = 1;
    driver.acquisitions = 1; driver.launches = 1;
    let mut history = History::new(driver);
    if !live { terminal(a, worker, 18); }
    {
        let mut session = Sampling::begin(&mut history.driver, &mut history.primary[0],
            &owner, 0, &ISSUED[0], worker).unwrap_or_else(|| finish(1061));
        require(session.receive(a), 1061);
        if second { require(session.receive(a) != cfg!(seal_failed), 1061); }
        if interrupted { require(session.interrupt_synthetic(), 1061); }
    }
    let first = history.primary[0].receipts()[0].unwrap_or_else(|| finish(1061));
    require(first.r8 == if live { 0 } else { 1 } &&
        first.rdx == if live { 0 } else { 18 } && (live || first.rax > 0), 1061);
    let state = if live { State::Live } else if interrupted {
        State::Failed(Failure::Local(Cause::Interrupted))
    } else if cfg!(seal_failed) { State::Failed(Failure::Local(Cause::Boolean)) }
    else { State::Awaiting };
    require(history.primary[0].state() == state &&
        history.primary[0].received() == if second { 2 } else { 1 } &&
        history.primary[0].receipts()[1] == if second {
            Some(Raw { rax: 18, rdx: if cfg!(seal_failed) { 2 } else { 1 }, r8: 1 })
        } else { None } && history.primary[0].receipts()[2].is_none(), 1061);
    // Oracle snapshot is fixture data, separate from the owner's fixed stores.
    let before = history.primary[0].clone();
    let reads = if second && !cfg!(seal_failed) { 2 } else { 1 };
    for turn in 0..3 {
        require(history.replay(0) == Replay::Denied, 1061);
        require(history.primary[0] == before && history.primary[1] == Sample::new() &&
            history.diagnostic == Sample::new() && history.diagnostic_for.is_none(), 1062);
        let record = history.driver.records[0].as_ref().unwrap_or_else(|| finish(1063));
        require(core::ptr::eq(history.driver.owner, &owner) && record.token == &ISSUED[0] &&
            record.reader == Some(reader) && record.worker == Some(worker) &&
            record.writer.is_none() && record.fact.is_none() && record.error.is_none() &&
            record.sample_started && record.channel == ChannelPhase::Applied &&
            record.launch_phase == ChannelPhase::Applied && record.reserved &&
            record.slot == 0 && record.expected == 0xb0000101 &&
            history.driver.records[1].is_none() && history.driver.used == [true, false] &&
            history.driver.generations == [1, 0] && history.driver.acquisitions == 1 &&
            history.driver.launches == 1 && history.driver.reads == reads &&
            history.driver.closed == closed && history.driver.pending == if live { None } else { Some(0) } &&
            history.driver.binding_failed.is_none() && history.driver.target_failed.is_none(), 1063);
        if turn == 2 { break; }
        let mut entered = 0;
        require(history.conflict(0, &mut entered) == if closed { Offer::Closed } else { Offer::Denied } &&
            entered == 0 && !history.capture(a, 0, worker), 1061);
    }
    // Check after the last conflict/capture denial, too.
    require(history.primary[0] == before && history.driver.reads == reads &&
        history.diagnostic == Sample::new() && history.diagnostic_for.is_none(), 1062);
    if live {
        accepted(a.stop(worker), 1063); terminal(a, worker, 144);
        accepted(a.close(reader), 1063); reclaim(a, worker);
    } else { dispose_bound(a, &mut history.driver, 0); }
    require(history.primary[0] == before && history.driver.used == [true, false] &&
        history.driver.generations == [1, 0], 1062);
    for slot in [1, 0] {
        let (reader, writer) = accepted(a.channel(), 1063);
        let replacement = accepted(a.launch(slot, writer, b"terminal-exit17"), 1063);
        fixture_finish(a, reader, replacement);
    }
    require(a.clean(), 1063); finish(100)
}

// PH-06: retain actual stale-handle errno at every sampling position.
pub fn run_history_errno(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let worker = sample_setup(a, &mut driver); terminal(a, worker, 18);
    let mut history = History::new(driver);
    let prefix_count = if cfg!(history_errno_first) { 0 } else if cfg!(history_errno_last) { 2 } else { 1 };
    let operation = if prefix_count == 1 { 0x20001 } else { 0x25001 };
    let (reader, replacement);
    {
        let mut session = Sampling::begin(&mut history.driver, &mut history.primary[0],
            &owner, 0, &ISSUED[0], worker).unwrap_or_else(|| finish(1064));
        for _ in 0..prefix_count { require(session.receive(a), 1064); }
        let prefix = *session.sample.receipts();
        // Explicit fixture cleanup; the old target below is diagnostic, not live ownership.
        dispose_bound(a, session.driver, 0);
        session.driver.records[0].as_mut().unwrap_or_else(|| finish(1064)).worker = Some(worker);
        (reader, replacement) = fixture_worker(a, 0);
        require(replacement.matches_target(0xb0000201) && !session.receive(a), 1064);
        for index in 0..prefix_count { require(session.sample.receipts()[index] == prefix[index], 1065); }
        require(session.sample.received() == prefix_count + 1 &&
            session.sample.receipts()[prefix_count].unwrap_or_else(|| finish(1064)).rax == -9 &&
            session.sample.state() == State::Failed(Failure::Native { operation, errno: 9 }), 1064);
    }
    let before = history.primary[0].clone();
    for _ in 0..3 {
        let replay = history.replay(0);
        if cfg!(history_errno_forget) { history.primary[0] = Sample::new(); }
        if cfg!(history_errno_error) { history.driver.records[0].as_mut().unwrap().error = None; }
        require(replay == Replay::Denied, 1064);
        require(history.primary[0] == before && history.primary[1] == Sample::new() &&
            history.diagnostic == Sample::new() && history.diagnostic_for.is_none(), 1065);
        let record = history.driver.records[0].as_ref().unwrap_or_else(|| finish(1066));
        require(core::ptr::eq(history.driver.owner, &owner) && record.token == &ISSUED[0] &&
            record.worker == Some(worker) && record.reader.is_none() && record.writer.is_none() &&
            record.fact.is_none() && record.error == Some(Error { operation, errno: 9 }) &&
            record.sample_started && record.reserved && record.slot == 0 && record.expected == 0xb0000101 &&
            record.channel == ChannelPhase::Applied && record.launch_phase == ChannelPhase::Applied &&
            history.driver.closed && history.driver.pending == Some(0) &&
            history.driver.records[1].is_none() && history.driver.used == [true, false] &&
            history.driver.generations == [1, 0] && history.driver.reads == (prefix_count + 1) as u8 &&
            history.driver.acquisitions == 1 && history.driver.launches == 1 &&
            history.driver.binding_failed.is_none() && history.driver.target_failed.is_none(), 1066);
        let mut entered = 0;
        require(history.conflict(0, &mut entered) == Offer::Closed && entered == 0 &&
            !history.capture(a, 0, worker), 1064);
    }
    require(history.primary[0] == before && history.driver.reads == (prefix_count + 1) as u8, 1065);
    fixture_finish(a, reader, replacement); ordinary(a, 1);
    require(history.primary[0] == before && history.driver.closed &&
        history.driver.pending == Some(0) && history.driver.used == [true, false], 1066);
    require(a.clean(), 1066); finish(100)
}

// PH-06: closed inspection reads retained storage; it grants no replay authority.
pub fn run_history_closed(a: &mut Adapter) -> ! {
    let owner = context(); let mut driver = Driver::new(&owner);
    let worker = sample_setup(a, &mut driver); terminal(a, worker, 18);
    let reader = driver.records[0].as_ref().unwrap().reader;
    let mut history = History::new(driver);
    require(history.capture(a, 0, worker), 1067);
    let primary = history.primary[0].clone();
    let revision = primary.receipts()[0].unwrap_or_else(|| finish(1067)).rax;
    require(guard_prefix(&primary, revision, 18) && history.replay(0) == Replay::Duplicate, 1067);
    let mut entered = 0;
    require(history.conflict(0, &mut entered) == Offer::Conflict && entered == 1, 1068);
    let diagnostic = history.diagnostic.clone();
    require(guard_prefix(&diagnostic, revision, 19), 1068);
    for disposed in [false, true] {
        for _ in 0..3 {
            if cfg!(closed_reopen) { history.driver.closed = false; }
            require(history.replay(0) == Replay::Denied, 1069);
            if cfg!(closed_forget_primary) { history.primary[0] = Sample::new(); }
            if cfg!(closed_forget_diagnostic) { history.diagnostic = Sample::new(); }
            if cfg!(closed_clear_pending) { history.driver.pending = None; }
            require(history.primary[0] == primary && history.primary[1] == Sample::new(), 1067);
            require(history.diagnostic == diagnostic && history.diagnostic_for == Some(0), 1068);
            require(history.conflict(0, &mut entered) == Offer::Closed && entered == 1 &&
                !history.capture(a, 0, worker) && !history.capture(a, 1, worker), 1069);
            let record = history.driver.records[0].as_ref().unwrap_or_else(|| finish(1070));
            require(core::ptr::eq(history.driver.owner, &owner) && record.token == &ISSUED[0] &&
                record.reader == if disposed { None } else { reader } &&
                record.worker == if disposed { None } else { Some(worker) } &&
                record.writer.is_none() && record.error.is_none() && record.sample_started &&
                record.fact.is_some_and(|fact| fact.revision == revision as u64 &&
                    fact.result == 18 && fact.kind == 1 && fact.historical_ready) &&
                record.reserved && record.slot == 0 && record.expected == 0xb0000101 &&
                record.channel == ChannelPhase::Applied && record.launch_phase == ChannelPhase::Applied &&
                history.driver.closed && history.driver.pending == Some(0) &&
                history.driver.records[1].is_none() && history.driver.used == [true, false] &&
                history.driver.generations == [1, 0] && history.driver.reads == 3 &&
                history.driver.acquisitions == 1 && history.driver.launches == 1 &&
                history.driver.binding_failed.is_none() && history.driver.target_failed.is_none(), 1070);
        }
        if !disposed { dispose_bound(a, &mut history.driver, 0); }
    }
    ordinary(a, 0); ordinary(a, 1);
    require(history.primary[0] == primary && history.diagnostic == diagnostic &&
        history.driver.closed && history.driver.pending == Some(0) &&
        history.driver.used == [true, false] && history.driver.generations == [1, 0], 1070);
    require(a.clean(), 1070); finish(100)
}

// Actual acquisition/launch composition; issuance remains the fixed fixture token.
pub fn run_composed_history(a: &mut Adapter) -> ! {
    let owner = context(); let foreign = context(); let mut driver = Driver::new(&owner);
    let token = black_box(&ISSUED[0]);
    require(driver.reserve(&owner, token, 0) && driver.acquire(a, 0), 1073);
    require(driver.records[0].as_ref().unwrap().reader.is_some(), 1073);
    require(driver.receive_launch(a, 0), 1071);
    let worker = driver.records[0].as_ref().unwrap().worker.unwrap_or_else(|| finish(1071));
    require(!driver.launched(&owner, 0, token, worker) && driver.pending == Some(0), 1071);
    require(driver.apply_launch(0), 1071);
    let record = driver.records[0].as_ref().unwrap();
    require(record.channel == ChannelPhase::Applied && record.launch_phase == ChannelPhase::Applied &&
        record.writer.is_none() && record.reader.is_some() && record.error.is_none() &&
        record.worker == Some(worker) && record.expected == 0xb0000101 &&
        worker.matches_target(record.expected) && driver.generations == [1, 0] &&
        driver.used == [true, false] && driver.acquisitions == 1 && driver.launches == 1 &&
        driver.pending.is_none() && !driver.closed, 1072);
    require(driver.launched(&owner, 0, token, worker) &&
        !driver.launched(black_box(&foreign), 0, token, worker) &&
        !driver.launched(&owner, 0, black_box(&ISSUED[1]), worker), 1074);
    let reader = record.reader;
    terminal(a, worker, 18);
    let mut history = History::new(driver);
    require(history.capture(a, 0, worker), 1074);
    let primary = history.primary[0].clone();
    let revision = primary.receipts()[0].unwrap_or_else(|| finish(1074)).rax;
    require(guard_prefix(&primary, revision, 18), 1074);
    for _ in 0..3 { require(history.replay(0) == Replay::Duplicate, 1074); }
    let record = history.driver.records[0].as_ref().unwrap();
    require(core::ptr::eq(history.driver.owner, &owner) && record.token == token &&
        record.worker == Some(worker) && record.reader == reader && record.writer.is_none() &&
        record.fact.is_some_and(|fact| fact.revision == revision as u64 && fact.result == 18 &&
            fact.kind == 1 && fact.historical_ready) && record.sample_started &&
        history.driver.pending == Some(0) && history.driver.reads == 3 &&
        history.driver.acquisitions == 1 && history.driver.launches == 1 &&
        history.primary[0] == primary && history.primary[1] == Sample::new() &&
        history.diagnostic == Sample::new() && history.diagnostic_for.is_none(), 1074);
    dispose_bound(a, &mut history.driver, 0);
    require(history.replay(0) == Replay::Denied && history.primary[0] == primary &&
        history.driver.pending == Some(0) && history.driver.used == [true, false] &&
        history.driver.generations == [1, 0] && history.driver.reads == 3, 1074);
    ordinary(a, 0); ordinary(a, 1);
    require(a.clean(), 1074); finish(100)
}

#[path = "cut_reservation.rs"]
mod cut_reservation;
use cut_reservation::{Owner as CutOwner, Reservations, Key as CutKey, Member, Error as CutError};
#[derive(Clone, Copy)]
struct LaunchRequest { member: Member, token: Token, worker: Worker }
struct NativeReservations<'h, 'ctx, 'key> {
    history: &'h History<'ctx>,
    reservations: Reservations<'key>,
}
impl<'h, 'ctx, 'key> NativeReservations<'h, 'ctx, 'key> {
    fn new(history: &'h History<'ctx>, owner: &'key mut CutOwner) -> Self {
        Self { history, reservations: Reservations::new(owner) }
    }
    #[inline(never)]
    fn reserve(&mut self, owner: &Context, requests: &[LaunchRequest]) -> Result<CutKey<'key>, CutError> {
        let members = qualify_launch(self.history, owner, requests)?;
        self.reservations.reserve(members.get(..requests.len()).ok_or(CutError::Invalid)?)
    }
    fn cancel(&mut self, key: &CutKey<'_>) -> Result<(), CutError> { self.reservations.cancel(key) }
}

// Keep reservation storage out of the launch/capture stack frame.
#[inline(never)]
fn check_bound_reservation(history: &History<'_>, worker: Worker, applied: bool) {
    let owner = history.driver.owner;
    let request = LaunchRequest { member: Member { attempt: 0, phase: 1 }, token: ISSUED[0], worker };
    let mut anchor = CutOwner::new(); let mut bound = NativeReservations::new(history, &mut anchor);
    if !applied {
        require(matches!(bound.reserve(owner, &[request]), Err(CutError::Invalid)), 1076);
        return;
    }
    let foreign = context();
    require(matches!(bound.reserve(black_box(&foreign), &[request]), Err(CutError::Invalid)), 1075);
    let mut wrong = request; wrong.token.0[9] += 1;
    require(matches!(bound.reserve(owner, &[black_box(wrong)]), Err(CutError::Invalid)), 1077);
    wrong = request; wrong.member.attempt = 1;
    require(matches!(bound.reserve(owner, &[request, wrong]), Err(CutError::Invalid)), 1077);
    let key = bound.reserve(owner, &[request]).unwrap_or_else(|_| finish(1077));
    let first = bound.reservations.inspect(&key).unwrap_or_else(|_| finish(1077));
    require(first.serial == 1 && first.journal == 1 && first.count == 1 && !first.cancelled, 1077);
    let replay = bound.reserve(owner, &[request]).unwrap_or_else(|_| finish(1077));
    require(bound.reservations.inspect(&replay) == Ok(first), 1077);
    require(bound.cancel(&key).is_ok() && bound.reservations.inspect(&key).is_ok_and(|r| r.cancelled), 1077);
    let next = bound.reserve(owner, &[request]).unwrap_or_else(|_| finish(1077));
    require(bound.reservations.inspect(&next).is_ok_and(|r| r.serial == 2 && r.journal == 2), 1077);
    require(bound.cancel(&next).is_ok(), 1077);
}

pub fn run_bound_reservation(a: &mut Adapter) -> ! {
    let owner = context(); let mut history = History::new(Driver::new(&owner));
    require(history.driver.reserve(&owner, &ISSUED[0], 0) && history.driver.acquire(a, 0) &&
        history.driver.receive_launch(a, 0), 1076);
    let worker = history.driver.records[0].as_ref().unwrap().worker.unwrap_or_else(|| finish(1076));
    check_bound_reservation(&history, worker, false);
    require(history.driver.apply_launch(0), 1076); terminal(a, worker, 18);
    require(history.capture(a, 0, worker), 1076);
    let primary = history.primary[0].clone();
    check_bound_reservation(&history, worker, true);
    require(history.primary[0] == primary && history.driver.pending == Some(0) &&
        history.driver.reads == 3 && history.driver.acquisitions == 1 && history.driver.launches == 1 &&
        history.driver.used == [true, false] && history.driver.generations == [1, 0] &&
        history.replay(0) == Replay::Duplicate, 1077);
    dispose_bound(a, &mut history.driver, 0); ordinary(a, 0); ordinary(a, 1);
    require(history.primary[0] == primary && history.driver.pending == Some(0) && a.clean(), 1077);
    finish(100)
}


#[inline(never)]
fn qualify_launch(history: &History<'_>, owner: &Context, requests: &[LaunchRequest]) -> Result<[Member; 2], CutError> {
        let driver = &history.driver;
        if driver.closed { return Err(CutError::Closed); }
        if !cfg!(bound_skip_owner) && !core::ptr::eq(owner, driver.owner) { return Err(CutError::Invalid); }
        if requests.is_empty() || requests.len() > 2 { return Err(CutError::Invalid); }
        let mut members = [Member { attempt: 0, phase: 0 }; 2];
        for (position, request) in requests.iter().enumerate() {
            let index = request.member.attempt as usize;
            if index >= 2 || request.member.phase != 1 ||
                (position != 0 && requests[position - 1].member.attempt >= request.member.attempt) {
                return Err(CutError::Invalid);
            }
            let Some(record) = driver.records[index].as_ref() else { return Err(CutError::Invalid); };
            if record.slot >= 2 || !record.reserved || !driver.used[index] ||
                record.channel != ChannelPhase::Applied || record.error.is_some() ||
                record.reader.is_none() || record.writer.is_some() || record.worker != Some(request.worker) ||
                !request.worker.matches_target(record.expected) { return Err(CutError::Invalid); }
            if !cfg!(bound_skip_token) && (record.token != &request.token || record.token != &ISSUED[index]) {
                return Err(CutError::Invalid);
            }
            if !cfg!(bound_skip_qualification) && (record.launch_phase != ChannelPhase::Applied ||
                driver.generations[record.slot] == 0 || record.expected !=
                (0xb0000000 | ((driver.generations[record.slot] as u64) << 8) | (record.slot as u64 + 1))) {
                return Err(CutError::Invalid);
            }
            members[position] = request.member;
        }
        Ok(members)
}

use cut_reservation::{Application, Applied, ApplicationState, Profile};
struct NativeApplication<'h, 'ctx, 'key> {
    history: &'h mut History<'ctx>,
    application: &'h mut Application<'key>,
}
impl<'h, 'ctx, 'key> NativeApplication<'h, 'ctx, 'key> {
    fn new(history: &'h mut History<'ctx>, application: &'h mut Application<'key>) -> Self {
        Self { history, application }
    }
    fn qualify(&self, owner: &Context, request: LaunchRequest) -> Result<(), CutError> {
        if request.member.attempt != 0 { return Err(CutError::Invalid); }
        qualify_launch(self.history, owner, &[request]).map(|_| ())
    }
    fn reserve(&mut self, owner: &Context, request: LaunchRequest) -> Result<CutKey<'key>, CutError> {
        self.qualify(owner, request)?;
        self.application.reserve(&[request.member])
    }
    fn apply(&mut self, owner: &Context, request: LaunchRequest, key: &CutKey<'_>) -> Result<Applied<'key>, CutError> {
        self.qualify(owner, request)?;
        let result = self.application.apply(key);
        if matches!(result, Err(CutError::Closed)) { self.history.driver.closed = true; }
        result
    }
}
#[inline(never)]
fn check_native_application(history: &mut History<'_>, worker: Worker) {
    let owner = history.driver.owner; let foreign = context();
    let request = LaunchRequest { member: Member { attempt: 0, phase: 1 }, token: ISSUED[0], worker };
    let mut anchor = CutOwner::new();
    let mut application = Application::new(&mut anchor, Profile::StartedDependency);
    let mut bound = NativeApplication::new(history, &mut application);
    let mut wrong = request; wrong.member.attempt = 1;
    require(matches!(bound.reserve(owner, wrong), Err(CutError::Invalid)), 1078);
    require(matches!(bound.reserve(black_box(&foreign), request), Err(CutError::Invalid)), 1078);
    let key = bound.reserve(owner, request).unwrap_or_else(|_| finish(1078));
    wrong = request; wrong.token.0[9] += 1;
    require(matches!(bound.apply(owner, black_box(wrong), &key), Err(CutError::Invalid)), 1078);
    require(matches!(bound.apply(black_box(&foreign), request, &key), Err(CutError::Invalid)), 1078);
    let receipt = bound.apply(owner, request, &key).unwrap_or_else(|_| {
        require(bound.history.driver.closed && bound.application.state(&key) == Ok(ApplicationState::Unknown) &&
            matches!(bound.application.reserve(&[Member { attempt: 1, phase: 1 }]), Err(CutError::Closed)) &&
            matches!(bound.application.apply(&key), Err(CutError::Closed)) &&
            bound.application.cancel(&key) == Err(CutError::Closed), 1082);
        let captured = bound.application.effect(0);
        if cfg!(application_corrupt_capture) {
            require(effect_matches(&bound.application, [1, 2, 3, 1, 0, 5, 1, 6, 7, 2]), 1082); finish(1080)
        }
        require(captured.is_none(), 1082);
        if cfg!(application_drop_capture) { finish(1079) }
        finish(1078)
    });
    let inspected = bound.application.inspect(&receipt).unwrap_or_else(|_| finish(1078));
    require(inspected.serial == 1 && inspected.journal == 1 && inspected.before == [0, 0] &&
        inspected.after == [1, 0] && inspected.effects == 1 &&
        effect_matches(&bound.application, [1, 2, 3, 1, 0, 5, 1, 6, 7, 1]) &&
        bound.application.effect(1).is_none(), 1079);
    let replay = bound.apply(owner, request, &key).unwrap_or_else(|_| finish(1078));
    require(bound.application.inspect(&replay) == Ok(inspected) &&
        bound.application.cancel(&key) == Err(CutError::Invalid) &&
        matches!(bound.application.reserve(&[Member { attempt: 1, phase: 1 }]), Err(CutError::Full)), 1080);
}
pub fn run_native_application(a: &mut Adapter) -> ! {
    let owner = context(); let mut history = History::new(Driver::new(&owner));
    require(history.driver.reserve(&owner, &ISSUED[0], 0) && history.driver.acquire(a, 0) &&
        history.driver.receive_launch(a, 0) && history.driver.apply_launch(0), 1078);
    let worker = history.driver.records[0].as_ref().unwrap().worker.unwrap_or_else(|| finish(1078));
    check_native_application(&mut history, worker);
    require(history.driver.reads == 0 && history.driver.acquisitions == 1 && history.driver.launches == 1 &&
        history.driver.pending.is_none() && !history.driver.closed && history.driver.used == [true, false] &&
        history.driver.generations == [1, 0] && history.primary.iter().all(|sample|
            sample.received() == 0 && sample.state() == State::Awaiting &&
            sample.receipts().iter().all(Option::is_none)), 1080);
    dispose_bound(a, &mut history.driver, 0); ordinary(a, 0); ordinary(a, 1);
    require(a.clean() && history.driver.pending.is_none() && history.driver.reads == 0, 1080); finish(100)
}

fn effect_matches(application: &Application<'_>, expected: [u64; 10]) -> bool {
    application.effect(0).is_some_and(|(actual, disposition)| disposition == 1 &&
        actual.iter().zip(expected.iter()).fold(0, |difference, (a, b)| difference | (a ^ b)) == 0)
}

use cut_reservation::EffectKey;
struct GeneratedLaunch<'key> {
    key: EffectKey<'key>,
    channel: ChannelPhase,
    launch: ChannelPhase,
    reader: Option<Reader>, writer: Option<Writer>, worker: Option<Worker>, error: Option<Error>,
}
impl<'key> GeneratedLaunch<'key> {
    fn new(key: EffectKey<'key>) -> Self {
        Self { key, channel: ChannelPhase::Reserved, launch: ChannelPhase::Reserved,
            reader: None, writer: None, worker: None, error: None }
    }
    #[inline(never)]
    fn perform(&mut self, a: &mut Adapter, application: &mut Application<'_>) -> bool {
        if self.channel != ChannelPhase::Reserved || self.launch != ChannelPhase::Reserved ||
            !application.invocation_started(&self.key, &GENERATED_TOKEN) { return false; }
        self.channel = ChannelPhase::Started;
        match a.channel() {
            Ok((reader, writer)) => { self.reader = Some(reader); self.writer = Some(writer); }
            Err(error) => { self.error = Some(error); }
        }
        self.channel = ChannelPhase::Returned;
        if self.error.is_some() { let _ = application.effect_unknown(&self.key); return false; }
        self.channel = ChannelPhase::Applied;
        self.launch = ChannelPhase::Started;
        let Some(writer) = self.writer else { let _ = application.effect_unknown(&self.key); return false; };
        match a.launch(1, writer, b"exit") {
            Ok(worker) => {
                self.worker = Some(worker);
                if !cfg!(effect_keep_writer) { self.writer = None; }
            }
            Err(error) => { self.error = Some(error); }
        }
        self.launch = ChannelPhase::Returned;
        if application.effect_returned(&self.key).is_err() { return false; }
        if self.error.is_some() || self.writer.is_some() ||
            !self.worker.is_some_and(|worker| worker.matches_target(0xb0000102)) {
            let _ = application.effect_unknown(&self.key); return false;
        }
        self.launch = ChannelPhase::Applied;
        application.effect_applied(&self.key).is_ok()
    }
}
const GENERATED_TOKEN: [u64; 10] = [1, 2, 3, 1, 0, 5, 1, 6, 7, 1];
#[inline(never)]
fn prepare_generated(history: &mut History<'_>, application: &mut Application<'_>, worker: Worker) {
    let owner = history.driver.owner;
    let request = LaunchRequest { member: Member { attempt: 0, phase: 1 }, token: ISSUED[0], worker };
    let mut bound = NativeApplication::new(history, application);
    let key = bound.reserve(owner, request).unwrap_or_else(|_| finish(1083));
    let receipt = bound.apply(owner, request, &key).unwrap_or_else(|_| finish(1083));
    require(bound.application.inspect(&receipt).is_ok_and(|r| r.before == [0, 0] && r.after == [1, 0] &&
        r.effects == 1) && effect_matches(bound.application, GENERATED_TOKEN), 1083);
}
pub fn run_generated_launch(a: &mut Adapter) -> ! {
    let owner = context(); let mut history = History::new(Driver::new(&owner));
    require(history.driver.reserve(&owner, &ISSUED[0], 0) && history.driver.acquire(a, 0) &&
        history.driver.receive_launch(a, 0) && history.driver.apply_launch(0), 1083);
    let provider = history.driver.records[0].as_ref().unwrap().worker.unwrap_or_else(|| finish(1083));
    let mut anchor = CutOwner::new(); let mut application = Application::new(&mut anchor, Profile::StartedDependency);
    prepare_generated(&mut history, &mut application, provider);
    require(matches!(application.start_effect(0, &ISSUED[1].0), Err(CutError::Invalid)), 1083);
    let key = application.start_effect(0, &GENERATED_TOKEN).unwrap_or_else(|_| finish(1083));
    require(application.acknowledge_effect(&key) == Err(CutError::Invalid), 1084);
    if cfg!(effect_busy) {
        let (reader, occupant) = fixture_worker(a, 1);
        terminal(a, occupant, 18); // Its writer is gone; its unreclaimed worker slot stays occupied.
        require(a.close(reader).is_ok(), 1086); // Keep the occupied worker slot, free its channel.
    }
    let mut generated = GeneratedLaunch::new(key);
    if !generated.perform(a, &mut application) {
        history.driver.closed = true;
        require(application.effect(0).is_some_and(|(token, disposition)| token == GENERATED_TOKEN && disposition == 6) &&
            application.acknowledge_effect(&generated.key) == Err(CutError::Closed) &&
            matches!(application.start_effect(0, &GENERATED_TOKEN), Err(CutError::Closed)) &&
            !generated.perform(a, &mut application) && history.driver.closed, 1087);
        if cfg!(effect_busy) {
            require(generated.error == Some(Error { operation: 0x23001, errno: 16 }) &&
                generated.worker.is_none() && generated.writer.is_some() && generated.reader.is_some(), 1087);
            finish(1086)
        }
        require(generated.error.is_none() && generated.worker.is_some() &&
            generated.reader.is_some() && generated.writer.is_some(), 1087); finish(1085)
    }
    require(generated.channel == ChannelPhase::Applied && generated.launch == ChannelPhase::Applied &&
        generated.reader.is_some() && generated.writer.is_none() && generated.error.is_none() &&
        application.effect(0).is_some_and(|(_, disposition)| disposition == 4), 1084);
    require(application.acknowledge_effect(&generated.key).is_ok() &&
        application.acknowledge_effect(&generated.key) == Err(CutError::Invalid) &&
        !generated.perform(a, &mut application) &&
        matches!(application.start_effect(0, &GENERATED_TOKEN), Err(CutError::Invalid)), 1084);
    let worker = generated.worker.unwrap_or_else(|| finish(1085));
    fixture_finish(a, generated.reader.unwrap(), worker);
    generated.reader = None; generated.worker = None;
    dispose_bound(a, &mut history.driver, 0); ordinary(a, 0);
    require(application.effect(0).is_some_and(|(token, disposition)| token == GENERATED_TOKEN && disposition == 5) &&
        application.reserve(&[Member { attempt: 1, phase: 1 }]).is_err() &&
        generated.reader.is_none() && generated.worker.is_none() && generated.writer.is_none() &&
        history.driver.reads == 0 && history.driver.pending.is_none() && a.clean(), 1085);
    finish(100)
}
const _: () = assert!(core::mem::size_of::<GeneratedLaunch<'_>>() <= 192);


use cut_reservation::RetainedEffect;
#[inline(never)]
fn dependent_observation<'a>(history: &mut History<'_>, owner: &Context,
    generated: &GeneratedLaunch<'_>, retained: &RetainedEffect<'_>,
    application: &mut Application<'a>) -> Result<Applied<'a>, CutError> {
    if history.driver.closed || (!cfg!(dependent_skip_source) &&
        (!core::ptr::eq(owner, history.driver.owner) || generated.channel != ChannelPhase::Applied ||
         generated.launch != ChannelPhase::Applied || generated.reader.is_none() || generated.writer.is_some() ||
         generated.error.is_some() || !generated.worker.is_some_and(|w| w.matches_target(0xb0000102)))) ||
        !application.retained_by(retained, &generated.key) { return Err(CutError::Invalid); }
    let key = application.reserve(&[Member { attempt: 1, phase: 1 }])?;
    let result = application.apply(&key);
    if matches!(result, Err(CutError::Closed)) { history.driver.closed = true; }
    result
}
#[inline(never)]
fn prepare_retirement<'a>(history: &mut History<'_>, application: &mut Application<'a>, worker: Worker) -> Applied<'a> {
    let owner = history.driver.owner;
    let request = LaunchRequest { member: Member { attempt: 0, phase: 1 }, token: ISSUED[0], worker };
    let mut bound = NativeApplication::new(history, application);
    let key = bound.reserve(owner, request).unwrap_or_else(|_| finish(1088));
    bound.apply(owner, request, &key).unwrap_or_else(|_| finish(1088))
}
pub fn run_dependent_launch(a: &mut Adapter) -> ! {
    let owner = context(); let mut history = History::new(Driver::new(&owner));
    require(history.driver.reserve(&owner, &ISSUED[0], 0) && history.driver.acquire(a, 0) &&
        history.driver.receive_launch(a, 0) && history.driver.apply_launch(0), 1088);
    let provider = history.driver.records[0].as_ref().unwrap().worker.unwrap_or_else(|| finish(1088));
    let mut anchor = CutOwner::new(); let mut application = Application::new(&mut anchor, Profile::StartedDependency);
    let first = prepare_retirement(&mut history, &mut application, provider);
    let key = application.start_effect(0, &GENERATED_TOKEN).unwrap_or_else(|_| finish(1088));
    let mut generated = GeneratedLaunch::new(key);
    require(generated.perform(a, &mut application), 1088);
    let mut retained = None;
    require(application.retire_effect(&first, &generated.key, &mut retained) == Err(CutError::Invalid) && retained.is_none(), 1089);
    require(application.acknowledge_effect(&generated.key).is_ok(), 1088);
    if application.retire_effect(&first, &generated.key, &mut retained).is_err() {
        require(retained.is_none() && application.effect(0).is_some_and(|(_, disposition)| disposition == 5) &&
            matches!(application.reserve(&[Member { attempt: 1, phase: 1 }]), Err(CutError::Closed)), 1092);
        finish(1088)
    }
    let retained = retained.as_ref().unwrap_or_else(|| finish(1092));
    let foreign = context();
    require(matches!(dependent_observation(&mut history, black_box(&foreign), &generated, retained, &mut application),
        Err(CutError::Invalid)), 1091);
    let second = dependent_observation(&mut history, &owner, &generated, retained, &mut application)
        .unwrap_or_else(|_| finish(1091));
    require(application.inspect(&first).is_ok_and(|r| r.serial == 1 && r.journal == 1 &&
        r.before == [0, 0] && r.after == [1, 0] && r.effects == 1), 1090);
    require(application.inspect(&second).is_ok_and(|r| r.serial == 2 && r.journal == 2 &&
        r.before == [1, 0] && r.after == [1, 1] && r.effects == 0) && application.effect(0).is_none() &&
        application.retire_empty(&second).is_ok() && retained.matches(&generated.key), 1092);
    fixture_finish(a, generated.reader.unwrap(), generated.worker.unwrap());
    generated.reader = None; generated.worker = None;
    dispose_bound(a, &mut history.driver, 0); ordinary(a, 0);
    require(retained.matches(&generated.key) && history.driver.reads == 0 && history.driver.pending.is_none() && a.clean(), 1092);
    finish(100)
}


fn generated_source(history: &History<'_>, owner: &Context, generated: &GeneratedLaunch<'_>,
    retained: &RetainedEffect<'_>, application: &Application<'_>) -> bool {
    !history.driver.closed && history.driver.pending.is_none() &&
        (cfg!(terminal_skip_owner) || core::ptr::eq(owner, history.driver.owner)) &&
        generated.channel == ChannelPhase::Applied && generated.launch == ChannelPhase::Applied &&
        generated.reader.is_some() && generated.writer.is_none() && generated.error.is_none() &&
        generated.worker.is_some_and(|w| w.matches_target(0xb0000102)) &&
        application.retained_by(retained, &generated.key)
}
// This session fixes the source association before the first read. Its exclusive
// History borrow prevents replacing the primary sample while application is possible.
struct NativeTerminal<'h, 'ctx, 'key> {
    history: &'h mut History<'ctx>, generated: &'h GeneratedLaunch<'key>,
    retained: &'h RetainedEffect<'key>, application: &'h mut Application<'key>,
}
impl<'h, 'ctx, 'key> NativeTerminal<'h, 'ctx, 'key> {
    fn begin(history: &'h mut History<'ctx>, generated: &'h GeneratedLaunch<'key>,
        retained: &'h RetainedEffect<'key>, application: &'h mut Application<'key>) -> Result<Self, CutError> {
        if !generated_source(history, history.driver.owner, generated, retained, application) ||
            history.primary[1].received() != 0 || history.primary[1].state() != State::Awaiting {
            return Err(CutError::Invalid);
        }
        Ok(Self { history, generated, retained, application })
    }
    #[inline(never)]
    fn capture(&mut self, a: &Adapter) -> bool {
        if !generated_source(self.history, self.history.driver.owner, self.generated, self.retained, self.application) { return false; }
        let sample = &mut self.history.primary[1];
        if sample.received() != 0 || sample.state() != State::Awaiting { return false; }
        let Some(worker) = self.generated.worker else { return false; };
        for position in 0..3 {
            if cfg!(terminal_source_interrupt) && position == 2 { sample.interrupt(); return false; }
            self.history.driver.reads += 1;
            let raw = if position == 1 { a.raw_worker_status(worker) } else { a.raw_observe(worker) };
            if !sample.push(raw) { return false; }
            if !matches!(sample.state(), State::Awaiting | State::Terminal(_)) { return false; }
        }
        matches!(sample.state(), State::Terminal(_))
    }
    fn qualified(&self, owner: &Context) -> bool {
        generated_source(self.history, owner, self.generated, self.retained, self.application) &&
            (cfg!(terminal_skip_seal) || (self.history.primary[1].received() == 3 &&
                matches!(self.history.primary[1].state(), State::Terminal(_))))
    }
    #[inline(never)]
    fn apply(&mut self, owner: &Context) -> Result<Applied<'key>, CutError> {
        if !self.qualified(owner) { return Err(CutError::Invalid); }
        let key = self.application.reserve_terminal(&[Member { attempt: 1, phase: 2 }])?;
        if !self.qualified(owner) { return Err(CutError::Invalid); }
        let result = self.application.apply_terminal(&key);
        if matches!(result, Err(CutError::Closed)) { self.history.driver.closed = true; }
        result
    }
}
pub fn run_terminal_application(a: &mut Adapter) -> ! {
    let owner = context(); let mut history = History::new(Driver::new(&owner));
    require(history.driver.reserve(&owner, &ISSUED[0], 0) && history.driver.acquire(a, 0) &&
        history.driver.receive_launch(a, 0) && history.driver.apply_launch(0), 1093);
    let provider = history.driver.records[0].as_ref().unwrap().worker.unwrap_or_else(|| finish(1093));
    let mut anchor = CutOwner::new(); let mut application = Application::new(&mut anchor, Profile::StartedDependency);
    let first = prepare_retirement(&mut history, &mut application, provider);
    let key = application.start_effect(0, &GENERATED_TOKEN).unwrap_or_else(|_| finish(1093));
    let mut generated = GeneratedLaunch::new(key);
    require(generated.perform(a, &mut application) && application.acknowledge_effect(&generated.key).is_ok(), 1093);
    let mut retained = None;
    require(application.retire_effect(&first, &generated.key, &mut retained).is_ok(), 1093);
    let retained = retained.as_ref().unwrap_or_else(|| finish(1093));
    let second = dependent_observation(&mut history, &owner, &generated, retained, &mut application)
        .unwrap_or_else(|_| finish(1093));
    require(application.retire_empty(&second).is_ok(), 1093);
    let mut source = NativeTerminal::begin(&mut history, &generated, retained, &mut application).unwrap_or_else(|_| finish(1093));
    if !pair_workload() { require(matches!(source.apply(&owner),
        Err(CutError::Invalid)), 1095); }
    terminal(a, source.generated.worker.unwrap(), 18);
    if !source.capture(a) {
        source.history.driver.closed = true;
        require(source.history.primary[1].received() == 2 && source.history.driver.reads == 2 &&
            source.history.primary[1].state() == State::Failed(Failure::Local(Cause::Interrupted)) &&
            source.generated.reader.is_some() && source.generated.worker.is_some() && source.generated.writer.is_none() &&
            !source.capture(a) &&
            matches!(source.apply(&owner), Err(CutError::Invalid)), 1099);
        finish(1098)
    }
    if !pair_workload() { let foreign = context();
    require(matches!(source.apply(black_box(&foreign)),
        Err(CutError::Invalid)), 1094); }
    let receipt = source.apply(&owner)
        .unwrap_or_else(|_| {
            require(source.history.driver.closed && source.history.primary[1].received() == 3 &&
                matches!(source.history.primary[1].state(), State::Terminal(_)) && source.generated.reader.is_some() &&
                source.generated.worker.is_some() && source.generated.writer.is_none() &&
                matches!(source.application.reserve_terminal(&[Member { attempt: 0, phase: 2 }]), Err(CutError::Closed)), 1099);
            if cfg!(terminal_drop_capture) { require(source.application.effect(0).is_none(), 1099); finish(1096) }
            require(source.application.effect(0).is_some_and(|(token, state)| state == 1 && token[7] == 6), 1099); finish(1097)
        });
    require(source.application.inspect(&receipt).is_ok_and(|r| r.serial == 3 && r.journal == 3 &&
        r.before == [1, 1] && r.after == [1, 2] && r.effects == 1) &&
        source.application.effect(0).is_some_and(|(actual, state)| state == 1 && actual.iter()
            .zip([1, 2, 3, 3, 0, 5, 1, 8, 7, 1].iter()).fold(0, |d, (a, b)| d | (a ^ b)) == 0), 1093);
    require(!source.capture(a) && matches!(source.apply(&owner), Err(CutError::Invalid)), 1093);
    drop(source); if cfg!(native_pair_teardown) || cfg!(provider_skip_owner) || cfg!(provider_skip_seal) || cfg!(provider_interrupt) || cfg!(native_cleaned) || cfg!(cleaned_skip_resources) || cfg!(cleaned_skip_transition) || cfg!(native_issued_reclaim) || cfg!(reclaim_skip_token) || cfg!(reclaim_early_ack) || cfg!(reclaim_keep_reader) || cfg!(reclaim_keep_worker) || cfg!(reclaim_close_error) || cfg!(reclaim_worker_error) { if cfg!(reclaim_close_error) { accepted(a.close(generated.reader.unwrap()), 1107); } if cfg!(reclaim_worker_error) { reclaim(a, generated.worker.unwrap()); } run_issued_reclaim(a, &mut history, &mut generated, retained, &mut application); if cfg!(native_pair_teardown) || cfg!(provider_skip_owner) || cfg!(provider_skip_seal) || cfg!(provider_interrupt) || cfg!(native_cleaned) || cfg!(cleaned_skip_resources) || cfg!(cleaned_skip_transition) { let cleaned = run_cleaned(&mut history, &mut generated, retained, &mut application, &receipt); if cfg!(native_pair_teardown) || cfg!(provider_skip_owner) || cfg!(provider_skip_seal) || cfg!(provider_interrupt) { let terminal = provider_terminal(a, &mut history, &mut application, &first, &cleaned); provider_reclaim(a, &mut history, &mut application, &first); provider_cleaned(&mut history, &mut application, &terminal); require(a.clean(), 1115); ordinary(a, 0); require(a.clean(), 1115); finish(100); } } dispose_bound(a, &mut history.driver, 0); ordinary(a, 0); require(a.clean(), 1107); finish(100); }
    fixture_finish(a, generated.reader.unwrap(), generated.worker.unwrap());
    generated.reader = None; generated.worker = None;
    dispose_bound(a, &mut history.driver, 0); ordinary(a, 0);
    require(history.driver.reads == 3 && history.primary[1].received() == 3 &&
        matches!(history.primary[1].state(), State::Terminal(_)) && application.effect(0).is_some() && a.clean(), 1093);
    finish(100)
}

const RECLAIM_TOKEN: [u64; 10] = [1, 2, 3, 3, 0, 5, 1, 8, 7, 1];
struct IssuedReclaim<'a> {
    key: EffectKey<'a>, started: bool, close_return: Option<Raw>, reclaim_return: Option<Raw>,
}
impl IssuedReclaim<'_> {
    #[inline(never)]
    fn perform(&mut self, a: &mut Adapter, history: &mut History<'_>, owner: &Context,
        generated: &mut GeneratedLaunch<'_>, retained: &RetainedEffect<'_>, application: &mut Application<'_>) -> bool {
        if self.started || !application.invocation_started(&self.key, &RECLAIM_TOKEN) ||
            !generated_source(history, owner, generated, retained, application) ||
            history.primary[1].received() != 3 || !matches!(history.primary[1].state(), State::Terminal(_)) { return false; }
        let result = self.execute(a, &mut generated.reader, &mut generated.worker, application, &RECLAIM_TOKEN);
        if !result { history.driver.closed = true; }
        result
    }
    #[inline(never)]
    fn execute(&mut self, a: &mut Adapter, reader: &mut Option<Reader>, worker: &mut Option<Worker>, application: &mut Application<'_>, expected: &[u64; 10]) -> bool {
        if self.started || reader.is_none() || worker.is_none() || !application.invocation_started(&self.key, expected) { return false; }
        self.started = true;
        self.close_return = Some(a.close_return(reader.unwrap()));
        if self.close_return.unwrap().rax == 0 && !cfg!(reclaim_keep_reader) { *reader = None; }
        if self.close_return.unwrap().rax != 0 || reader.is_some() {
            let _ = application.effect_unknown(&self.key); return false;
        }
        self.reclaim_return = Some(a.reclaim_return(worker.unwrap()));
        if application.effect_returned(&self.key).is_err() {
            let _ = application.effect_unknown(&self.key); return false;
        }
        if self.reclaim_return.unwrap().rax == 0 && !cfg!(reclaim_keep_worker) { *worker = None; }
        if self.reclaim_return.unwrap().rax != 0 || worker.is_some() || application.effect_applied(&self.key).is_err() {
            let _ = application.effect_unknown(&self.key); return false;
        }
        true
    }
}
#[inline(never)]
fn run_issued_reclaim(a: &mut Adapter, history: &mut History<'_>, generated: &mut GeneratedLaunch<'_>,
    retained: &RetainedEffect<'_>, application: &mut Application<'_>) {
    let owner = history.driver.owner;
    require(generated_source(history, owner, generated, retained, application) && history.primary[1].received() == 3 &&
        matches!(history.primary[1].state(), State::Terminal(_)), 1107);
    if !pair_workload() { let mut wrong = RECLAIM_TOKEN; wrong[9] += 1;
    require(matches!(application.start_effect(0, black_box(&wrong)), Err(CutError::Invalid)), 1100); }
    let key = application.start_effect(0, &RECLAIM_TOKEN).unwrap_or_else(|_| finish(1107));
    if !pair_workload() { require(application.acknowledge_effect(&key) == Err(CutError::Invalid), 1101); }
    let mut effect = IssuedReclaim { key, started: false, close_return: None, reclaim_return: None };
    if !pair_workload() { let foreign = context();
    require(!effect.perform(a, history, black_box(&foreign), generated, retained, application) &&
        !effect.started && effect.close_return.is_none() && effect.reclaim_return.is_none(), 1107); }
    if !effect.perform(a, history, owner, generated, retained, application) {
        require(history.driver.closed && application.effect(0).is_some_and(|(token, state)| token == RECLAIM_TOKEN && state == 6) &&
            application.acknowledge_effect(&effect.key) == Err(CutError::Closed) &&
            !effect.perform(a, history, owner, generated, retained, application), 1107);
        if cfg!(reclaim_close_error) {
            require(effect.close_return.is_some_and(|r| r.rax == -13) && effect.reclaim_return.is_none() &&
                generated.reader.is_some() && generated.worker.is_some(), 1107); finish(1104)
        }
        if cfg!(reclaim_keep_reader) {
            require(effect.close_return.is_some_and(|r| r.rax == 0) && effect.reclaim_return.is_none() &&
                generated.reader.is_some() && generated.worker.is_some(), 1107); finish(1102)
        }
        require(effect.close_return.is_some_and(|r| r.rax == 0) && generated.reader.is_none() && generated.worker.is_some(), 1107);
        if cfg!(reclaim_worker_error) { require(effect.reclaim_return.is_some_and(|r| r.rax == -9), 1107); finish(1105) }
        require(effect.reclaim_return.is_some_and(|r| r.rax == 0), 1107); finish(1103)
    }
    require(effect.close_return.is_some_and(|r| r.rax == 0) && effect.reclaim_return.is_some_and(|r| r.rax == 0) &&
        generated.reader.is_none() && generated.worker.is_none() && generated.writer.is_none() &&
        application.effect(0).is_some_and(|(token, state)| token == RECLAIM_TOKEN && state == 4), 1107);
    require(application.acknowledge_effect(&effect.key).is_ok() &&
        (pair_workload() || (application.acknowledge_effect(&effect.key) == Err(CutError::Invalid) &&
        !effect.perform(a, history, owner, generated, retained, application) &&
        matches!(application.start_effect(0, &RECLAIM_TOKEN), Err(CutError::Invalid)))) &&
        application.effect(0).is_some_and(|(token, state)| token == RECLAIM_TOKEN && state == 5), 1107);
    require(history.driver.reads == 3 && history.primary[1].received() == 3 &&
        matches!(history.primary[1].state(), State::Terminal(_)), 1107);
}

fn cleaned_ready(history: &History<'_>, generated: &GeneratedLaunch<'_>, retained: &RetainedEffect<'_>, application: &Application<'_>) -> bool {
    !history.driver.closed && history.driver.pending.is_none() && history.primary[1].received() == 3 &&
        matches!(history.primary[1].state(), State::Terminal(_)) && application.retained_by(retained, &generated.key) &&
        generated.channel == ChannelPhase::Applied && generated.launch == ChannelPhase::Applied && generated.error.is_none() &&
        (cfg!(cleaned_skip_resources) || (generated.reader.is_none() && generated.worker.is_none() && generated.writer.is_none()))
}
#[inline(never)]
fn run_cleaned<'a>(history: &mut History<'_>, generated: &mut GeneratedLaunch<'_>, retained: &RetainedEffect<'_>,
    application: &mut Application<'a>, terminal: &Applied<'_>) -> Applied<'a> {
    if !pair_workload() { generated.reader = history.driver.records[0].as_ref().unwrap().reader;
    require(generated.reader.is_some() && !cleaned_ready(history, generated, retained, application), 1108);
    generated.reader = None; }
    require(cleaned_ready(history, generated, retained, application), 1110);
    let effect = application.completed_effect(0, &RECLAIM_TOKEN).unwrap_or_else(|_| finish(1110));
    let mut reclaimed = None;
    require(application.retire_effect(terminal, &effect, &mut reclaimed).is_ok(), 1110);
    let reclaimed = reclaimed.as_ref().unwrap_or_else(|| finish(1110));
    let key = application.reserve_cleaned(Member { attempt: 1, phase: 3 }, reclaimed, &effect).unwrap_or_else(|_| finish(1110));
    let receipt = application.apply_cleaned(&key, reclaimed, &effect).unwrap_or_else(|_| {
        history.driver.closed = true;
        require(matches!(application.reserve_cleaned(Member { attempt: 1, phase: 3 }, reclaimed, &effect), Err(CutError::Closed)) &&
            application.effect(0).is_none() && generated.reader.is_none() && generated.worker.is_none(), 1110);
        finish(1109)
    });
    require(application.inspect(&receipt).is_ok_and(|r| r.serial == 4 && r.journal == 4 && r.before == [1, 2] && r.after == [1, 3] && r.effects == 0) &&
        application.inspect(terminal).is_ok_and(|r| r.after == [1, 2] && r.effects == 1) && application.effect(0).is_none() &&
        application.apply_cleaned(&key, reclaimed, &effect).is_ok() &&
        matches!(application.reserve_cleaned(Member { attempt: 1, phase: 3 }, reclaimed, &effect), Err(CutError::Invalid)), 1110);
    receipt
}

const PROVIDER_RECLAIM: [u64; 10] = [1, 2, 3, 5, 0, 4, 1, 8, 7, 1];
#[inline(never)]
fn provider_source(history: &History<'_>, owner: &Context, application: &Application<'_>, launched: &Applied<'_>) -> bool {
    let Some(worker) = history.driver.records[0].as_ref().and_then(|r| r.worker) else { return false; };
    let owner = if cfg!(provider_skip_owner) { history.driver.owner } else { owner };
    history.driver.pending.is_none() && qualify_launch(history, owner, &[LaunchRequest {
        member: Member { attempt: 0, phase: 1 }, token: ISSUED[0], worker }]).is_ok() &&
        application.inspect(launched).is_ok_and(|r| r.serial == 1 && r.before == [0, 0] && r.after == [1, 0] && r.effects == 1)
}
#[inline(never)]
fn provider_qualified(history: &History<'_>, owner: &Context, application: &Application<'_>, launched: &Applied<'_>) -> bool {
    provider_source(history, owner, application, launched) && (cfg!(provider_skip_seal) ||
        (history.primary[0].received() == 3 && matches!(history.primary[0].state(), State::Terminal(_))))
}
#[inline(never)]
fn provider_terminal<'a>(a: &Adapter, history: &mut History<'_>, application: &mut Application<'a>,
    launched: &Applied<'_>, dependent_cleaned: &Applied<'_>) -> Applied<'a> {
    let owner = history.driver.owner; let foreign = context();
    require(!provider_source(history, black_box(&foreign), application, launched), 1111);
    require(provider_source(history, owner, application, launched) && history.primary[0].received() == 0 &&
        history.primary[0].state() == State::Awaiting && application.inspect(dependent_cleaned).is_ok_and(|r| r.after == [1, 3]) &&
        application.retire_empty(dependent_cleaned).is_ok(), 1115);
    require(!provider_qualified(history, owner, application, launched), 1112);
    let worker = history.driver.records[0].as_ref().unwrap().worker.unwrap();
    for position in 0..3 {
        if cfg!(provider_interrupt) && position == 2 {
            history.primary[0].interrupt(); history.driver.closed = true;
            require(history.primary[0].received() == 2 && history.driver.reads == 5 &&
                history.primary[0].state() == State::Failed(Failure::Local(Cause::Interrupted)) &&
                !provider_source(history, owner, application, launched), 1115); finish(1113)
        }
        require(provider_source(history, owner, application, launched), 1115);
        let raw = if position == 1 { a.raw_worker_status(worker) } else { a.raw_observe(worker) };
        history.driver.reads += 1;
        if !history.primary[0].push(raw) || !matches!(history.primary[0].state(), State::Awaiting | State::Terminal(_)) {
            history.driver.closed = true; finish(1115)
        }
    }
    require(provider_qualified(history, owner, application, launched), 1115);
    let key = application.reserve_terminal(&[Member { attempt: 0, phase: 2 }]).unwrap_or_else(|_| finish(1115));
    let receipt = application.apply_terminal(&key).unwrap_or_else(|_| { history.driver.closed = true; finish(1115) });
    require(application.inspect(&receipt).is_ok_and(|r| r.serial == 5 && r.before == [1, 3] && r.after == [2, 3] && r.effects == 1) &&
        application.effect(0).is_some_and(|(t, s)| t == PROVIDER_RECLAIM && s == 1), 1115);
    receipt
}
#[inline(never)]
fn provider_reclaim(a: &mut Adapter, history: &mut History<'_>, application: &mut Application<'_>, launched: &Applied<'_>) {
    require(provider_source(history, history.driver.owner, application, launched) &&
        history.primary[0].received() == 3 && matches!(history.primary[0].state(), State::Terminal(_)), 1115);
    let key = application.start_effect(0, &PROVIDER_RECLAIM).unwrap_or_else(|_| finish(1115));
    let mut effect = IssuedReclaim { key, started: false, close_return: None, reclaim_return: None };
    let record = history.driver.records[0].as_mut().unwrap();
    if !effect.execute(a, &mut record.reader, &mut record.worker, application, &PROVIDER_RECLAIM) {
        history.driver.closed = true; finish(1115)
    }
    require(effect.close_return.is_some_and(|r| r.rax == 0) && effect.reclaim_return.is_some_and(|r| r.rax == 0) &&
        record.reader.is_none() && record.worker.is_none() && record.writer.is_none() &&
        application.acknowledge_effect(&effect.key).is_ok() &&
        !effect.execute(a, &mut record.reader, &mut record.worker, application, &PROVIDER_RECLAIM), 1115);
}
#[inline(never)]
fn provider_cleaned(history: &mut History<'_>, application: &mut Application<'_>, terminal: &Applied<'_>) {
    let record = history.driver.records[0].as_ref().unwrap();
    require(!history.driver.closed && record.reader.is_none() && record.worker.is_none() && record.writer.is_none() &&
        history.primary[0].received() == 3 && matches!(history.primary[0].state(), State::Terminal(_)), 1115);
    let effect = application.completed_effect(0, &PROVIDER_RECLAIM).unwrap_or_else(|_| finish(1115));
    let mut retained = None; require(application.retire_effect(terminal, &effect, &mut retained).is_ok(), 1115);
    let retained = retained.as_ref().unwrap();
    let key = application.reserve_cleaned(Member { attempt: 0, phase: 3 }, retained, &effect).unwrap_or_else(|_| finish(1115));
    let receipt = application.apply_cleaned(&key, retained, &effect).unwrap_or_else(|_| { history.driver.closed = true; finish(1115) });
    require(application.inspect(&receipt).is_ok_and(|r| r.serial == 6 && r.before == [2, 3] && r.after == [3, 3] && r.effects == 0) &&
        application.apply_cleaned(&key, retained, &effect).is_ok() && application.effect(0).is_none() &&
        application.inspect(terminal).is_ok_and(|r| r.after == [2, 3] && r.effects == 1) &&
        history.driver.reads == 6 && history.primary[1].received() == 3 &&
        matches!(history.primary[1].state(), State::Terminal(_)), 1115);
}

const fn pair_workload() -> bool { cfg!(native_pair_teardown) || cfg!(provider_skip_owner) || cfg!(provider_skip_seal) || cfg!(provider_interrupt) }
