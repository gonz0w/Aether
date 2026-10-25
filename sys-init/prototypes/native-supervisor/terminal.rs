// SPDX-License-Identifier: BSD-2-Clause
//! Bounded terminal sampler and standalone NT-01/02 probes; no journal acceptance.
use super::{accepted, reclaim, require, terminal};
use super::adapter::{Adapter, Reader, Worker, finish};
#[derive(Clone, Copy)]
pub(super) struct Fact { pub revision: u64, pub result: u64, pub kind: u64, pub historical_ready: bool }
pub(super) struct Sampler { pub reads: u8 }
impl Sampler {
    pub(super) fn sample(&mut self, a: &Adapter, worker: Worker) -> super::adapter::Result<Option<Fact>> {
        // One fresh sample per instance, three reads maximum. Fixture assertions
        // terminate on contradiction; raw partial retention and ongoing polling remain NT-04 through NT-07.
        require(self.reads == 0, 1037);
        self.reads += 1;
        let first = a.observe(worker)?;
        if first.terminal == 0 { return Ok(None); }
        require(first.revision > 0, 1037);
        self.reads += 1;
        let status = a.worker_status(worker)?;
        self.reads += 1;
        let last = a.observe(worker)?;
        require(first.revision == last.revision && first.terminal == last.terminal &&
                first.historical_ready == last.historical_ready &&
                status.result == first.terminal && status.historical_ready == first.historical_ready, 1037);
        let kind = if cfg!(terminal_ignore_kind) {
            if status.result == 135 { 2 } else if status.result == 144 { 3 } else { 1 }
        } else { status.kind };
        require(matches!((kind, status.result), (1, 1..=256) | (2, 135) | (3, 144)), 1037);
        Ok(Some(Fact { revision: first.revision, result: status.result, kind,
                    historical_ready: status.historical_ready }))
    }
}
#[inline(never)]
fn launch(a: &mut Adapter, slot: usize, mode: &[u8]) -> (Reader, Worker) {
    let (reader, writer) = accepted(a.channel(), 1038);
    (reader, accepted(a.launch(slot, writer, mode), 1038))
}
#[inline(never)]
fn sample_terminal(a: &Adapter, worker: Worker, result: u64, kind: u64, ready: bool) {
    terminal(a, worker, result);
    let mut sampler = Sampler { reads: 0 };
    let fact = accepted(sampler.sample(a, worker), 1037).unwrap();
    require(sampler.reads == 3 && fact.revision > 0 && fact.result == result &&
            fact.kind == kind && fact.historical_ready == ready, 1036);
}
#[inline(never)]
fn dispose(a: &mut Adapter, reader: Reader, worker: Worker) {
    accepted(a.close(reader), 1038); reclaim(a, worker);
}
pub fn run(a: &mut Adapter) -> ! {
    if cfg!(terminal_live) {
        let (reader, worker) = launch(a, 0, b"silent");
        let mut sampler = Sampler { reads: 0 };
        require(accepted(sampler.sample(a, worker), 1037).is_none() && sampler.reads == 1, 1037);
        accepted(a.stop(worker), 1038);
        sample_terminal(a, worker, 144, 3, false);
        dispose(a, reader, worker);
        for slot in [1, 0] {
            let (reader, worker) = launch(a, slot, b"terminal-exit17");
            sample_terminal(a, worker, 18, 1, true); dispose(a, reader, worker);
        }
    } else {
        let stopping = cfg!(terminal_stop_collision);
        let result = if stopping { 144 } else { 135 };
        let mode: &[u8] = if stopping { b"terminal-exit143" } else { b"terminal-exit134" };
        let (reader, worker) = launch(a, 0, mode);
        sample_terminal(a, worker, result, 1, true);
        dispose(a, reader, worker);
        let (reader, worker) = launch(a, 0, if stopping { b"hold" } else { b"terminal-fault" });
        if stopping { accepted(a.stop(worker), 1038); }
        // Stop may precede readiness; verify coherence without inferring readiness.
        if stopping {
            terminal(a, worker, result);
            let mut sampler = Sampler { reads: 0 };
            let fact = accepted(sampler.sample(a, worker), 1037).unwrap();
            require(sampler.reads == 3 && fact.kind == 3 && fact.result == result, 1036);
        } else { sample_terminal(a, worker, result, 2, true); }
        dispose(a, reader, worker);
        let (reader, worker) = launch(a, 1, b"terminal-exit17");
        sample_terminal(a, worker, 18, 1, true); dispose(a, reader, worker);
    }
    require(a.clean(), 1038); finish(100)
}
