// SPDX-License-Identifier: BSD-2-Clause
//! One hard dependency; fixture protocol and policy are specified by decision 0019.
use super::{accepted, deadline, require, terminal, await_status, release, reclaim};
use super::adapter::{self, Adapter, Worker, Reader, InterruptTick, Read, WaitState};

#[derive(Clone, Copy)]
struct Service { worker: Worker, reader: Reader, generation: u64 }
#[derive(Clone, Copy)]
struct Evidence { owner: Service, byte: u8 }

struct Dependency { provider: Service, frame: Evidence, lost: bool }
impl Dependency {
    fn observe_loss(&mut self, a: &Adapter) {
        if accepted(a.observe(self.provider.worker), 942).terminal != 0 { self.lost = true; }
    }
    fn admits(&self, a: &Adapter, end: InterruptTick) -> bool {
        if cfg!(service_loss_bad_admission) { return true; }
        !self.lost && admissible(a, self.provider, self.frame, end)
    }
}

fn start(a: &mut Adapter, slot: usize, generation: u64) -> Service {
    start_mode(a, slot, generation, b"live")
}
fn start_mode(a: &mut Adapter, slot: usize, generation: u64, mode: &[u8]) -> Service {
    let (reader, writer) = accepted(a.channel(), 908);
    let worker = accepted(a.launch(slot, writer, mode), 908);
    Service { worker, reader, generation }
}
enum Readiness { Frame(Evidence), Deadline, Malformed, Closed, Budget }

fn poll_readiness(a: &Adapter, service: Service, end: InterruptTick) -> Readiness {
    for _ in 0..100000 {
        if accepted(a.clock(), 909) >= end { return Readiness::Deadline; }
        match accepted(a.read(service.reader), 909) {
            Read::Byte(byte) => {
                if byte != 42 { return Readiness::Malformed; }
                return Readiness::Frame(Evidence { owner: service, byte });
            }
            Read::Pending => adapter::yield_now(),
            Read::Eof => return Readiness::Closed,
        }
    }
    Readiness::Budget
}
fn receive(a: &Adapter, service: Service, end: InterruptTick) -> Evidence {
    match poll_readiness(a, service, end) {
        Readiness::Frame(evidence) => evidence,
        _ => adapter::finish(909),
    }
}
fn admissible(a: &Adapter, service: Service, evidence: Evidence, end: InterruptTick) -> bool {
    if !cfg!(service_bad_generation) &&
        (service.generation != evidence.owner.generation || service.worker != evidence.owner.worker ||
         service.reader != evidence.owner.reader) { return false; }
    if evidence.byte != 42 { return false; }
    let observation = accepted(a.observe(service.worker), 910);
    if !cfg!(service_bad_terminal) && observation.terminal != 0 { return false; }
    cfg!(service_bad_deadline) || accepted(a.clock(), 910) < end
}
fn dispose(a: &mut Adapter, service: Service) {
    accepted(a.close(service.reader), 911);
    reclaim(a, service.worker);
}
pub fn run(a: &mut Adapter) -> ! {
    let provider = start(a, 0, 1);
    let end = deadline(a, 100);
    let evidence = receive(a, provider, end);
    let expired = accepted(a.clock(), 901);
    require(!admissible(a, provider, evidence, expired), 901);
    require(admissible(a, provider, evidence, end), 905);
    // The exact predicate above authorizes this actual launch.
    let dependent = start(a, 1, 1);
    require(accepted(a.observe(dependent.worker), 905).terminal == 0, 905);
    let snapshot = accepted(a.observe(provider.worker), 906);
    let end = deadline(a, 100);
    let wait = accepted(a.register(provider.worker, snapshot.revision, end), 906);
    accepted(a.stop(provider.worker), 906);
    require(await_status(a, wait).state == WaitState::Changed, 906);
    terminal(a, provider.worker, 144); release(a, wait);
    require(!admissible(a, provider, evidence, deadline(a, 100)), 902);
    // Observed provider failure invalidates its dependent before reclamation.
    if !cfg!(service_bad_dependency) { accepted(a.stop(dependent.worker), 903); }
    require(accepted(a.observe(dependent.worker), 903).terminal == 144, 903);
    dispose(a, provider); dispose(a, dependent); require(a.clean(), 907);
    let replacement = start(a, 0, 2);
    require(replacement.worker != provider.worker && replacement.reader != provider.reader, 904);
    let end = deadline(a, 100);
    let fresh = receive(a, replacement, end);
    require(!admissible(a, replacement, evidence, end), 904);
    require(admissible(a, replacement, fresh, end), 905);
    accepted(a.stop(replacement.worker), 907); terminal(a, replacement.worker, 144);
    dispose(a, replacement); require(a.clean(), 907);
    adapter::finish(100)
}

pub fn run_return(a: &mut Adapter) -> ! {
    let provider = start(a, 0, 1);
    let end = deadline(a, 100);
    let evidence = receive(a, provider, end);
    require(admissible(a, provider, evidence, end), 912);
    if cfg!(service_return_early) {
        accepted(a.close(provider.reader), 912);
        terminal(a, provider.worker, 18);
    }
    require(accepted(a.observe(provider.worker), 912).terminal == 0, 912);
    let dependent = start(a, 1, 1);
    require(accepted(a.observe(dependent.worker), 913).terminal == 0, 913);

    let snapshot = accepted(a.observe(provider.worker), 913);
    let end = deadline(a, 100);
    let wait = accepted(a.register(provider.worker, snapshot.revision, end), 913);
    /* Reader closure is the post-admission stimulus observed by the worker. */
    accepted(a.close(provider.reader), 913);
    require(await_status(a, wait).state == WaitState::Changed, 913);
    terminal(a, provider.worker, 18); release(a, wait);
    require(!admissible(a, provider, evidence, deadline(a, 100)), 914);

    if !cfg!(service_return_bad_dependency) { accepted(a.stop(dependent.worker), 915); }
    require(accepted(a.observe(dependent.worker), 915).terminal == 144, 915);
    reclaim(a, provider.worker);
    dispose(a, dependent);
    require(a.clean(), 916);

    let replacement = start(a, 0, 2);
    let end = deadline(a, 100);
    let fresh = receive(a, replacement, end);
    require(!admissible(a, replacement, evidence, end), 917);
    require(admissible(a, replacement, fresh, end), 918);
    accepted(a.close(replacement.reader), 918);
    terminal(a, replacement.worker, 18);
    reclaim(a, replacement.worker);
    require(a.clean(), 916);
    adapter::finish(100)
}

pub fn run_readiness_failure(a: &mut Adapter) -> ! {
    let mode: &[u8] = if cfg!(service_silent) { b"silent" } else { b"malformed" };
    let provider = start_mode(a, 0, 1, mode);
    let end = deadline(a, 10);
    // Exercise the same readiness policy as successful dependent admission.
    match poll_readiness(a, provider, end) {
        Readiness::Deadline => adapter::finish(920),
        Readiness::Malformed => adapter::finish(921),
        Readiness::Closed => adapter::finish(922),
        Readiness::Budget => adapter::finish(924),
        Readiness::Frame(_) => adapter::finish(919),
    }
}

pub fn run_readiness_retry(a: &mut Adapter) -> ! {
    let silent = cfg!(service_retry_silent);
    let mode: &[u8] = if silent { b"silent" } else { b"malformed" };
    let failed = start_mode(a, 0, 1, mode);
    let rejected = poll_readiness(a, failed, deadline(a, 10));
    require(matches!((silent, rejected),
        (true, Readiness::Deadline) | (false, Readiness::Malformed)), 925);
    accepted(a.stop(failed.worker), 926);
    terminal(a, failed.worker, 144);
    if !cfg!(service_retry_bad_cleanup) { accepted(a.close(failed.reader), 926); }
    reclaim(a, failed.worker);
    require(a.clean(), 927);

    let replacement = start(a, 0, 2);
    require(replacement.worker != failed.worker && replacement.reader != failed.reader, 928);
    let end = deadline(a, 100);
    let readiness = if cfg!(service_retry_no_fresh) { None }
                    else { Some(receive(a, replacement, end)) };
    let fresh = match readiness { Some(frame) => frame, None => adapter::finish(929) };
    require(admissible(a, replacement, fresh, end), 929);
    // Only a fresh accepted frame authorizes this actual dependent launch.
    let dependent = start(a, 1, 2);
    require(accepted(a.observe(dependent.worker), 930).terminal == 0, 930);
    accepted(a.stop(dependent.worker), 930); terminal(a, dependent.worker, 144);
    dispose(a, dependent);
    accepted(a.stop(replacement.worker), 930); terminal(a, replacement.worker, 144);
    dispose(a, replacement); require(a.clean(), 930);
    adapter::finish(100)
}

struct AttemptBudget { used: u8, limit: u8 }
impl AttemptBudget {
    fn reserve(&mut self) -> bool {
        if self.used >= self.limit { return false; }
        self.used += 1;
        true
    }
}

pub fn run_retry_budget(a: &mut Adapter) -> ! {
    let silent = cfg!(service_budget_silent);
    let mode: &[u8] = if silent { b"silent" } else { b"malformed" };
    let mut budget = AttemptBudget { used: 0, limit: 3 };
    let mut previous: Option<Service> = None;
    let attempts = if cfg!(service_budget_short) { 2 } else { 3 };
    for _ in 0..attempts {
        require(budget.reserve(), 931);
        let provider = start_mode(a, 0, u64::from(budget.used), mode);
        if let Some(old) = previous {
            require(provider.worker != old.worker && provider.reader != old.reader, 933);
        }
        let result = poll_readiness(a, provider, deadline(a, 10));
        require(matches!((silent, result),
            (true, Readiness::Deadline) | (false, Readiness::Malformed)), 932);
        accepted(a.stop(provider.worker), 935); terminal(a, provider.worker, 144);
        dispose(a, provider); require(a.clean(), 935);
        previous = Some(provider);
    }
    require(budget.used == 3, 934);
    // Mutation changes admission, while the independent oracle stays at three.
    if cfg!(service_budget_extra) { budget.limit = 4; }
    require(!budget.reserve(), 931);
    require(budget.used == 3 && a.clean(), 935);
    adapter::finish(100)
}

struct Activation { budget: AttemptBudget, cancelled: bool }
impl Activation {
    fn new() -> Self {
        Self { budget: AttemptBudget { used: 0, limit: 3 }, cancelled: false }
    }
    fn cancel(&mut self) { self.cancelled = true; }
    fn reserve(&mut self) -> bool {
        if self.cancelled && !cfg!(service_cancel_bad_retry) { return false; }
        self.budget.reserve()
    }
    fn accepts(&self, a: &Adapter, service: Service, frame: Evidence, end: InterruptTick) -> bool {
        (!self.cancelled || cfg!(service_cancel_bad_ready)) && admissible(a, service, frame, end)
    }
}

pub fn run_retry_cancellation(a: &mut Adapter) -> ! {
    let ready = cfg!(service_cancel_ready) || cfg!(service_cancel_bad_ready);
    let mode: &[u8] = if ready { b"live" } else { b"malformed" };
    let mut previous: Option<(Service, Activation)> = None;
    for generation in 1..=3 {
        let mut activation = Activation::new();
        require(activation.reserve(), 936);
        let provider = start_mode(a, 0, generation, mode);
        if let Some((old, mut cancelled)) = previous.take() {
            require(old.worker != provider.worker && old.reader != provider.reader, 938);
            require(!cancelled.reserve() && cancelled.budget.used == 1, 936);
        }
        if ready {
            let end = deadline(a, 100);
            let frame = receive(a, provider, end);
            require(activation.accepts(a, provider, frame, end), 939);
            activation.cancel(); activation.cancel();
            // Cancellation wins while this exact frame's provider is still live.
            require(!activation.accepts(a, provider, frame, end), 937);
        } else {
            require(matches!(poll_readiness(a, provider, deadline(a, 10)),
                             Readiness::Malformed), 939);
        }
        accepted(a.stop(provider.worker), 939); terminal(a, provider.worker, 144);
        dispose(a, provider); require(a.clean(), 939);
        activation.cancel(); activation.cancel();
        require(!activation.reserve(), 936);
        require(!activation.reserve() && activation.budget.used == 1, 936);
        previous = Some((provider, activation));
    }
    require(a.clean(), 939);
    adapter::finish(100)
}

pub fn run_dependency_loss(a: &mut Adapter) -> ! {
    let provider = start(a, 0, 1);
    let end = deadline(a, 100);
    let frame = receive(a, provider, end);
    let mut binding = Dependency { provider, frame, lost: false };
    require(binding.admits(a, end), 942);
    let dependent = start(a, 1, 1);
    require(accepted(a.observe(dependent.worker), 942).terminal == 0, 942);
    if cfg!(service_loss_return) {
        accepted(a.close(provider.reader), 942);
        terminal(a, provider.worker, 18);
    } else {
        accepted(a.stop(provider.worker), 942);
        terminal(a, provider.worker, 144);
    }
    binding.observe_loss(a);
    require(binding.lost, 942);
    if cfg!(service_loss_bad_stop) { accepted(a.stop(dependent.worker), 940); }
    require(accepted(a.observe(dependent.worker), 940).terminal == 0, 940);
    require(!binding.admits(a, deadline(a, 100)), 941);
    if cfg!(service_loss_return) { reclaim(a, provider.worker); }
    else { dispose(a, provider); }
    require(accepted(a.observe(dependent.worker), 940).terminal == 0, 940);

    let replacement = start(a, 0, 2);
    require(replacement.worker != provider.worker && replacement.reader != provider.reader, 943);
    let end = deadline(a, 100);
    let fresh = receive(a, replacement, end);
    let recovered = Dependency { provider: replacement, frame: fresh, lost: false };
    require(!binding.admits(a, end) && recovered.admits(a, end), 943);
    require(accepted(a.observe(dependent.worker), 940).terminal == 0, 940);
    // Explicit stop is separate from the previously recorded provider loss.
    accepted(a.stop(dependent.worker), 944); terminal(a, dependent.worker, 144);
    dispose(a, dependent);
    accepted(a.stop(replacement.worker), 944); terminal(a, replacement.worker, 144);
    dispose(a, replacement); require(a.clean(), 944);
    adapter::finish(100)
}
