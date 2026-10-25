// SPDX-License-Identifier: BSD-2-Clause
//! Actual raw-return capture; standalone fixture, not Driver/journal integration.
use super::{accepted, reclaim, require, terminal};
use super::adapter::{Adapter, Reader, Worker, finish};
use super::sample_receipts::{Sample, State, Failure};
#[inline(never)]
fn launch(a: &mut Adapter, slot: usize) -> (Reader, Worker) {
    let (reader, writer) = accepted(a.channel(), 1043);
    (reader, accepted(a.launch(slot, writer, b"exit"), 1043))
}
#[inline(never)]
fn dispose(a: &mut Adapter, reader: Reader, worker: Worker) {
    terminal(a, worker, 18); accepted(a.close(reader), 1043); reclaim(a, worker);
}
#[inline(never)]
fn ordinary(a: &mut Adapter, slot: usize) {
    let (reader, worker) = launch(a, slot); dispose(a, reader, worker);
}
pub fn run(a: &mut Adapter) -> ! {
    let (reader, worker) = launch(a, 0);
    terminal(a, worker, 18);
    let mut sample = Sample::new();
    if cfg!(raw_terminal) {
        let first = a.raw_observe(worker);
        require(sample.push(first), 1042);
        let status = a.raw_worker_status(worker);
        require(sample.push(status), 1042);
        let last = a.raw_observe(worker);
        require(sample.push(last), 1042);
        require(sample.receipts() == &[Some(first), Some(status), Some(last)] && sample.received() == 3, 1042);
        match sample.state() {
            State::Terminal(fact) => require(fact.revision > 0 && fact.result == 18 &&
                fact.kind == 1 && fact.historical_ready, 1042),
            _ => finish(1042),
        }
        require(!sample.push(first) && sample.receipts()[2] == Some(last), 1042);
        dispose(a, reader, worker); ordinary(a, 0); ordinary(a, 1);
    } else {
        let count = if cfg!(raw_first_stale) { 0 } else if cfg!(raw_observe_stale) { 2 } else { 1 };
        let first = if count > 0 {
            let raw = a.raw_observe(worker); require(sample.push(raw), 1042); Some(raw)
        } else { None };
        let status = if count == 2 {
            let raw = a.raw_worker_status(worker); require(sample.push(raw), 1042); Some(raw)
        } else { None };
        // Deliberate fixture lifecycle interference. Original wrapper is diagnostic
        // after this positively known reclaim; no production mutation is authorized.
        dispose(a, reader, worker);
        let (reader, replacement) = launch(a, 0);
        require(replacement.matches_target(0xb0000201), 1043);
        let raw = if count == 1 { a.raw_worker_status(worker) } else { a.raw_observe(worker) };
        require(raw.rax == -9 && sample.push(raw), 1042);
        let operation = if count == 1 { 0x20001 } else { 0x25001 };
        require(sample.received() == count + 1 &&
                sample.state() == State::Failed(Failure::Native { operation, errno: 9 }) &&
                sample.receipts()[count] == Some(raw), 1042);
        require((count == 0 || sample.receipts()[0] == first) &&
                (count != 2 || sample.receipts()[1] == status), 1042);
        require(!sample.push(raw) && sample.receipts()[count] == Some(raw), 1042);
        dispose(a, reader, replacement); ordinary(a, 1);
    }
    require(a.clean(), 1043); finish(100)
}
