// SPDX-License-Identifier: BSD-2-Clause
//! Fixed owned attempt: explicit busy-error routing and one cleanup-gated retry.
use super::{accepted, reclaim, require, terminal};
use super::adapter::{Adapter, Completion, Error, InterruptTick, Reader, Result, Wait, WaitState, Worker, Writer, finish, probes};

struct Attempt {
    generation: u64,
    reader: Option<Reader>,
    writer: Option<Writer>,
    worker: Option<Worker>,
    error: Option<Error>,
    wait: Option<Wait>,
    retried: bool,
    cancelled: bool,
}
impl Attempt {
    fn acquire(a: &mut Adapter, generation: u64) -> Result<Self> {
        let (reader, writer) = a.channel()?;
        Ok(Self { generation, reader: Some(reader), writer: Some(writer), worker: None,
                  error: None, wait: None, retried: false, cancelled: false })
    }
    fn launch(&mut self, a: &mut Adapter, slot: usize) -> Result<()> {
        self.launch_mode(a, slot, b"exit")
    }
    fn launch_mode(&mut self, a: &mut Adapter, slot: usize, mode: &[u8]) -> Result<()> {
        if self.cancelled { return Err(Error { operation: 0, errno: 13 }); }
        if self.error.is_some() || self.worker.is_some() {
            return Err(Error { operation: 0, errno: 16 });
        }
        let writer = self.writer.ok_or(Error { operation: 0, errno: 9 })?;
        match a.launch(slot, writer, mode) {
            Ok(worker) => { self.worker = Some(worker); self.writer = None; Ok(()) }
            Err(error) => { self.error = Some(error); Err(error) }
        }
    }
    fn clean(&self) -> bool {
        self.reader.is_none() && self.writer.is_none() && self.worker.is_none() && self.wait.is_none()
    }
    fn register_wait(&mut self, a: &mut Adapter) -> Result<()> {
        if self.wait.is_some() { return Err(Error { operation: 0, errno: 16 }); }
        let worker = self.worker.ok_or(Error { operation: 0, errno: 9 })?;
        let snapshot = a.observe(worker)?;
        let end = a.clock()?.after(100000)?;
        self.register_at(a, snapshot.revision, end)
    }
    fn register_at(&mut self, a: &mut Adapter, revision: u64, end: InterruptTick) -> Result<()> {
        if self.wait.is_some() { return Err(Error { operation: 0, errno: 16 }); }
        let worker = self.worker.ok_or(Error { operation: 0, errno: 9 })?;
        self.wait = Some(a.register(worker, revision, end)?);
        Ok(())
    }
    fn wait_status(&self, a: &Adapter) -> Result<Completion> {
        let wait = self.wait.ok_or(Error { operation: 0, errno: 9 })?;
        let completion = a.status(wait)?;
        if cfg!(attempt_bad_precedence) && completion.state == WaitState::Timeout {
            return Ok(Completion { state: WaitState::Changed, ..completion });
        }
        Ok(completion)
    }
    fn cancel_service(&mut self, a: &Adapter) -> Result<()> {
        if !cfg!(attempt_bad_intent) { self.cancelled = true; }
        if let Some(worker) = self.worker {
            if let Err(error) = a.stop(worker) {
                if cfg!(attempt_stop_forget) { self.cancelled = false; self.worker = None; }
                return Err(error);
            }
        }
        Ok(())
    }
    fn cancel_wait(&mut self, a: &Adapter) -> Result<Completion> {
        let wait = self.wait.ok_or(Error { operation: 0, errno: 9 })?;
        let completion = a.cancel(wait)?;
        if cfg!(attempt_wait_forget) { self.wait = None; }
        Ok(completion)
    }
    fn release_wait(&mut self, a: &mut Adapter) -> Result<()> {
        let wait = self.wait.ok_or(Error { operation: 0, errno: 9 })?;
        if let Err(error) = a.release(wait) {
            if cfg!(attempt_release_forget) { self.wait = None; }
            return Err(error);
        }
        self.wait = None;
        Ok(())
    }
    fn cleanup(&mut self, a: &mut Adapter) -> Result<()> {
        if let Some(writer) = self.writer {
            if !cfg!(attempt_bad_writer) { a.close_writer(writer)?; self.writer = None; }
        }
        if let Some(reader) = self.reader {
            if let Err(error) = a.close(reader) {
                if cfg!(attempt_reader_forget) { self.reader = None; }
                return Err(error);
            }
            self.reader = None;
        }
        if let Some(worker) = self.worker {
            if cfg!(attempt_partial_forget) { self.worker = None; }
            a.reclaim(worker)?;
            self.worker = None;
        }
        if self.wait.is_some() && !cfg!(attempt_wait_skip_release) { self.release_wait(a)?; }
        Ok(())
    }
    fn retry(&mut self, a: &mut Adapter) -> Result<Self> {
        if self.cancelled { return Err(Error { operation: 0, errno: 13 }); }
        if !cfg!(attempt_bad_guard) && !self.clean() {
            return Err(Error { operation: 0, errno: 16 });
        }
        if self.generation != 1 || self.retried ||
           self.error != Some(Error { operation: 0x23001, errno: 16 }) {
            return Err(Error { operation: 0, errno: 28 });
        }
        let next = Self::acquire(a, 2)?;
        self.retried = true;
        Ok(next)
    }
}

pub fn run(a: &mut Adapter) -> ! {
    let (blocker_reader, blocker_writer) = accepted(a.channel(), 960);
    let blocker = accepted(a.launch(0, blocker_writer, b"exit"), 960);
    let mut failed = accepted(Attempt::acquire(a, 1), 960);
    let busy = Error { operation: 0x23001, errno: 16 };
    require(failed.launch(a, 0) == Err(busy), 960);
    require(failed.error == Some(busy) && failed.reader.is_some() &&
            failed.writer.is_some() && failed.worker.is_none(), 960);
    require(matches!(failed.retry(a), Err(Error { operation: 0, errno: 16 })), 963);
    require(!failed.retried && !failed.clean(), 963);
    accepted(failed.cleanup(a), 961); require(failed.clean(), 961);
    terminal(a, blocker, 18);
    accepted(a.close(blocker_reader), 962); reclaim(a, blocker);
    require(a.clean(), 962);
    let mut replacement = accepted(failed.retry(a), 964);
    require(replacement.generation == 2 && failed.retried, 964);
    accepted(replacement.launch(a, 0), 964);
    terminal(a, replacement.worker.unwrap(), 18);
    accepted(replacement.cleanup(a), 964);
    require(replacement.clean() && a.clean(), 964);
    require(matches!(failed.retry(a), Err(Error { operation: 0, errno: 28 })), 964);
    let (reader, writer) = accepted(a.channel(), 964);
    let worker = accepted(a.launch(1, writer, b"exit"), 964);
    terminal(a, worker, 18); accepted(a.close(reader), 964); reclaim(a, worker);
    require(a.clean(), 964);
    finish(100)
}


pub fn run_wait(a: &mut Adapter) -> ! {
    for (index, slot) in [0, 1, 0].into_iter().enumerate() {
        let mut attempt = accepted(Attempt::acquire(a, index as u64 + 1), 970);
        require(attempt.register_wait(a) == Err(Error { operation: 0, errno: 9 }), 970);
        accepted(attempt.launch(a, slot), 970);
        terminal(a, attempt.worker.unwrap(), 18);
        accepted(attempt.register_wait(a), 970);
        let token = attempt.wait.unwrap();
        require(accepted(a.status(token), 970).state == WaitState::Pending, 970);
        require(attempt.register_wait(a) == Err(Error { operation: 0, errno: 16 }), 972);
        require(accepted(attempt.cancel_wait(a), 971).state == WaitState::Cancelled, 971);
        require(attempt.wait.is_some(), 971);
        require(accepted(attempt.cancel_wait(a), 971).state == WaitState::Cancelled, 971);
        require(accepted(a.status(token), 971).state == WaitState::Cancelled, 971);
        accepted(attempt.cleanup(a), 973);
        require(attempt.clean() && a.clean(), 973);
        require(probes::released(token), 974);
        require(attempt.release_wait(a) == Err(Error { operation: 0, errno: 9 }), 974);
    }
    finish(100)
}


pub fn run_deadline(a: &mut Adapter) -> ! {
    for (index, slot) in [0, 1, 0].into_iter().enumerate() {
        let mut attempt = accepted(Attempt::acquire(a, index as u64 + 1), 980);
        accepted(attempt.launch(a, slot), 980);
        terminal(a, attempt.worker.unwrap(), 18);
        let snapshot = accepted(a.observe(attempt.worker.unwrap()), 980);
        let now = accepted(a.clock(), 980);
        let end = if index == 0 { now } else { accepted(now.after(100000), 980) };
        let revision = if index == 2 { snapshot.revision } else { 0 };
        accepted(attempt.register_at(a, revision, end), 980);
        let expected = if index == 0 { WaitState::Timeout } else if index == 1 {
            WaitState::Changed } else { WaitState::Pending };
        require(accepted(attempt.wait_status(a), 980).state == expected, 980);
        let selected = if index == 2 { WaitState::Cancelled } else { expected };
        require(accepted(attempt.cancel_wait(a), 980).state == selected, 980);
        require(attempt.wait.is_some() && !attempt.cancelled, 980);
        accepted(attempt.cleanup(a), 980); require(attempt.clean() && a.clean(), 980);
    }
    finish(100)
}

pub fn run_intent(a: &mut Adapter) -> ! {
    let (reader, writer) = accepted(a.channel(), 981);
    let blocker = accepted(a.launch(0, writer, b"exit"), 981);
    let mut failed = accepted(Attempt::acquire(a, 1), 981);
    require(failed.launch(a, 0) == Err(Error { operation: 0x23001, errno: 16 }), 981);
    accepted(failed.cancel_service(a), 981);
    accepted(failed.cleanup(a), 981);
    terminal(a, blocker, 18); accepted(a.close(reader), 981); reclaim(a, blocker);
    require(matches!(failed.retry(a), Err(Error { operation: 0, errno: 13 })), 981);
    require(failed.launch(a, 0) == Err(Error { operation: 0, errno: 13 }), 981);
    require(a.clean(), 981);
    let mut live = accepted(Attempt::acquire(a, 1), 982);
    accepted(live.launch_mode(a, 0, b"live"), 982);
    require(accepted(a.observe(live.worker.unwrap()), 982).terminal == 0, 982);
    accepted(live.register_wait(a), 982);
    accepted(live.cancel_service(a), 982);
    require(live.cancelled && live.worker.is_some() && live.reader.is_some() &&
            live.wait.is_some() && !live.clean(), 982);
    terminal(a, live.worker.unwrap(), 144);
    accepted(live.cleanup(a), 982); require(live.clean() && a.clean(), 982);
    let (reader, writer) = accepted(a.channel(), 982);
    let worker = accepted(a.launch(1, writer, b"exit"), 982);
    terminal(a, worker, 18); accepted(a.close(reader), 982); reclaim(a, worker);
    require(a.clean(), 982); finish(100)
}


pub fn run_partial_cleanup(a: &mut Adapter) -> ! {
    let mut attempt = accepted(Attempt::acquire(a, 1), 990);
    accepted(attempt.launch_mode(a, 0, b"live"), 990);
    // The helper must finish its startup write before we deliberately close its reader.
    for _ in 0..100000 {
        if accepted(a.observe(attempt.worker.unwrap()), 990).historical_ready { break; }
        super::adapter::yield_now();
    }
    require(accepted(a.observe(attempt.worker.unwrap()), 990).historical_ready, 990);
    accepted(attempt.register_wait(a), 990);
    require(attempt.cleanup(a) == Err(Error { operation: 0x20002, errno: 16 }), 990);
    require(attempt.reader.is_none() && attempt.worker.is_some() && attempt.wait.is_some()
            && !attempt.clean() && !attempt.cancelled, 990);
    require(matches!(attempt.retry(a), Err(Error { operation: 0, errno: 16 })), 990);
    accepted(attempt.cancel_service(a), 990);
    terminal(a, attempt.worker.unwrap(), 144);
    accepted(attempt.cleanup(a), 990); require(attempt.clean() && a.clean(), 990);
    for slot in [1, 0] {
        let (reader, writer) = accepted(a.channel(), 990);
        let worker = accepted(a.launch(slot, writer, b"exit"), 990);
        terminal(a, worker, 18); accepted(a.close(reader), 990); reclaim(a, worker);
    }
    require(a.clean(), 990); finish(100)
}

pub fn run_stop_error(a: &mut Adapter) -> ! {
    for slot in [0, 1] {
        let (reader, writer) = accepted(a.channel(), 991);
        let worker = accepted(a.launch(slot, writer, b"exit"), 991);
        terminal(a, worker, 18); accepted(a.close(reader), 991); reclaim(a, worker);
    }
    let mut unresolved = accepted(Attempt::acquire(a, 1), 991);
    accepted(unresolved.launch(a, 0), 991);
    terminal(a, unresolved.worker.unwrap(), 18);
    // Fixture-only ownership loss: bypass Attempt while retaining its old worker.
    accepted(a.close(unresolved.reader.unwrap()), 991); unresolved.reader = None;
    reclaim(a, unresolved.worker.unwrap());
    require(unresolved.cancel_service(a) == Err(Error { operation: 0x20007, errno: 9 }), 991);
    require(unresolved.cancelled && unresolved.worker.is_some() && !unresolved.clean(), 991);
    require(matches!(unresolved.retry(a), Err(Error { operation: 0, errno: 13 })), 991);
    // No more acquisition: this is retained unresolved state, not Attempt cleanup.
    require(a.clean(), 991); finish(100)
}


pub fn run_reader_error(a: &mut Adapter) -> ! {
    for slot in [0, 1] {
        let (reader, writer) = accepted(a.channel(), 992);
        let worker = accepted(a.launch(slot, writer, b"exit"), 992);
        terminal(a, worker, 18); accepted(a.close(reader), 992); reclaim(a, worker);
    }
    let mut unresolved = accepted(Attempt::acquire(a, 1), 992);
    accepted(unresolved.launch(a, 0), 992);
    terminal(a, unresolved.worker.unwrap(), 18);
    accepted(unresolved.register_wait(a), 992);
    // Fixture-only ownership loss; retain the stale reader in Attempt.
    accepted(a.close(unresolved.reader.unwrap()), 992);
    require(unresolved.cleanup(a) == Err(Error { operation: 0x24003, errno: 13 }), 992);
    require(unresolved.reader.is_some() && unresolved.worker.is_some() &&
            unresolved.wait.is_some() && !unresolved.clean() && !a.clean(), 992);
    require(matches!(unresolved.retry(a), Err(Error { operation: 0, errno: 16 })), 992);
    // Fixture teardown only: Attempt remains unresolved, no more acquisition.
    reclaim(a, unresolved.worker.unwrap());
    accepted(a.release(unresolved.wait.unwrap()), 992);
    require(!unresolved.clean() && a.clean(), 992); finish(100)
}

pub fn run_release_error(a: &mut Adapter) -> ! {
    for slot in [0, 1] {
        let (reader, writer) = accepted(a.channel(), 993);
        let worker = accepted(a.launch(slot, writer, b"exit"), 993);
        terminal(a, worker, 18); accepted(a.close(reader), 993); reclaim(a, worker);
    }
    let mut unresolved = accepted(Attempt::acquire(a, 1), 993);
    accepted(unresolved.launch(a, 0), 993);
    terminal(a, unresolved.worker.unwrap(), 18);
    accepted(unresolved.register_wait(a), 993);
    // Fixture-only release outside Attempt; its reference stays unresolved.
    accepted(a.release(unresolved.wait.unwrap()), 993);
    require(unresolved.cleanup(a) == Err(Error { operation: 0x25005, errno: 9 }), 993);
    require(unresolved.reader.is_none() && unresolved.worker.is_none() &&
            unresolved.wait.is_some() && !unresolved.clean() && a.clean(), 993);
    require(matches!(unresolved.retry(a), Err(Error { operation: 0, errno: 16 })), 993);
    require(unresolved.release_wait(a) == Err(Error { operation: 0x25005, errno: 9 }), 993);
    require(unresolved.wait.is_some() && !unresolved.clean() && a.clean(), 993);
    finish(100)
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum EventKind { Launched, LaunchFailed(Error), Terminal(u64), Cleaned }
#[derive(Clone, Copy, PartialEq, Eq)]
struct Event { generation: u64, kind: EventKind }
struct RoutedAttempt { attempt: Attempt, pending: Option<Event>, outcome_delivered: bool }
impl RoutedAttempt {
    fn cancel_service(&mut self, a: &Adapter) -> Result<()> {
        let result = self.attempt.cancel_service(a);
        if result.is_err() && cfg!(route_error_drop) { self.pending = None; }
        if result.is_err() && cfg!(route_error_swallow) { return Ok(()); }
        if cfg!(route_cancel_drop) { self.pending = None; }
        if result.is_ok() && cfg!(route_stop_event) {
            self.pending = Some(Event { generation: self.attempt.generation, kind: EventKind::Terminal(144) });
        }
        if result.is_ok() && cfg!(route_stop_ack) { self.outcome_delivered = true; }
        result
    }
    fn launch(&mut self, a: &mut Adapter, slot: usize) -> Result<()> {
        self.launch_mode(a, slot, b"exit")
    }
    fn launch_mode(&mut self, a: &mut Adapter, slot: usize, mode: &[u8]) -> Result<()> {
        if self.pending.is_some() { return Err(Error { operation: 0, errno: 16 }); }
        match self.attempt.launch_mode(a, slot, mode) {
            Ok(()) => {
                let generation = if cfg!(route_old_generation) && self.attempt.generation == 2 { 1 } else { self.attempt.generation };
                self.pending = Some(Event { generation, kind: EventKind::Launched });
                Ok(())
            }
            Err(error) => {
                if error == (Error { operation: 0x23001, errno: 16 }) && self.attempt.error == Some(error) {
                    let reported = if cfg!(event_wrong_error) { Error { operation: error.operation, errno: 13 } } else { error };
                    self.pending = Some(Event { generation: self.attempt.generation, kind: EventKind::LaunchFailed(reported) });
                }
                Err(error)
            }
        }
    }
    fn observe(&mut self, a: &Adapter) -> Result<()> {
        let worker = self.attempt.worker.ok_or(Error { operation: 0, errno: 9 })?;
        let value = a.observe(worker)?.terminal;
        if value == 0 { return Ok(()); }
        let event = Event { generation: self.attempt.generation, kind: EventKind::Terminal(value) };
        if let Some(old) = self.pending {
            if old != event && old.kind != EventKind::Launched {
                return Err(Error { operation: 0, errno: 16 });
            }
            if cfg!(event_keep_launch) && old.kind == EventKind::Launched { return Ok(()); }
        }
        self.pending = Some(event); Ok(())
    }
    fn deliver(&mut self, inbox: &mut Option<Event>) -> bool {
        if inbox.is_some() {
            if cfg!(event_drop_busy) { self.pending = None; }
            return false;
        }
        if let Some(event) = self.pending {
            *inbox = Some(event);
            if cfg!(route_cancel_reset) && event.kind == EventKind::Cleaned { self.attempt.cancelled = false; }
            if matches!(event.kind, EventKind::Terminal(_) | EventKind::LaunchFailed(_)) { self.outcome_delivered = true; }
            self.pending = None; return true;
        }
        false
    }
    fn cleanup(&mut self, a: &mut Adapter) -> Result<()> {
        let omit_gate = cfg!(event_failure_early) && self.attempt.error.is_some();
        if !omit_gate && (!self.outcome_delivered || self.pending.is_some()) {
            return Err(Error { operation: 0, errno: 16 });
        }
        if let Err(error) = self.attempt.cleanup(a) {
            if cfg!(route_cleanup_event) {
                self.pending = Some(Event { generation: self.attempt.generation, kind: EventKind::Cleaned });
            }
            if cfg!(route_cleanup_forget) { self.attempt.wait = None; }
            return Err(error);
        }
        if !self.attempt.clean() { return Err(Error { operation: 0, errno: 16 }); }
        self.pending = Some(Event { generation: self.attempt.generation, kind: EventKind::Cleaned });
        Ok(())
    }
    fn eligible(&self) -> bool { self.attempt.clean() && self.pending.is_none() }
    fn retry(&mut self, a: &mut Adapter) -> Result<Self> {
        if !cfg!(route_skip_delivery) && !self.eligible() {
            return Err(Error { operation: 0, errno: 16 });
        }
        let attempt = self.attempt.retry(a)?;
        Ok(Self { attempt, pending: None, outcome_delivered: false })
    }
}

pub fn run_events(a: &mut Adapter) -> ! {
    for generation in 1..=3 {
        let mut route = RoutedAttempt { attempt: accepted(Attempt::acquire(a, generation), 994), pending: None, outcome_delivered: false };
        accepted(route.launch(a, 0), 994);
        let launched = Some(Event { generation, kind: EventKind::Launched });
        require(route.pending == launched, 994);
        let sentinel = Some(Event { generation: 0, kind: EventKind::Cleaned });
        let mut inbox = sentinel;
        require(!route.deliver(&mut inbox) && inbox == sentinel && route.pending == launched, 994);
        require(route.cleanup(a) == Err(Error { operation: 0, errno: 16 }), 994);
        if generation == 3 {
            inbox = None;
            require(route.deliver(&mut inbox) && inbox == launched, 994);
            require(route.cleanup(a) == Err(Error { operation: 0, errno: 16 }), 994);
        }
        terminal(a, route.attempt.worker.unwrap(), 18);
        accepted(route.observe(a), 995); accepted(route.observe(a), 995);
        let ended = Some(Event { generation, kind: EventKind::Terminal(18) });
        require(route.pending == ended, 995);
        require(route.cleanup(a) == Err(Error { operation: 0, errno: 16 }), 995);
        inbox = None;
        require(route.deliver(&mut inbox) && inbox == ended && route.pending.is_none(), 995);
        require(!route.deliver(&mut inbox) && inbox == ended, 995);
        accepted(route.cleanup(a), 996);
        let cleaned = Some(Event { generation, kind: EventKind::Cleaned });
        require(route.pending == cleaned && !route.eligible() && a.clean(), 996);
        require(!route.deliver(&mut inbox) && inbox == ended && route.pending == cleaned, 996);
        inbox = None;
        require(route.deliver(&mut inbox) && inbox == cleaned && route.eligible(), 996);
    }
    require(a.clean(), 996); finish(100)
}


pub fn run_rejected_events(a: &mut Adapter) -> ! {
    let (reader, writer) = accepted(a.channel(), 997);
    let blocker = accepted(a.launch(0, writer, b"exit"), 997);
    let mut route = RoutedAttempt { attempt: accepted(Attempt::acquire(a, 1), 997), pending: None, outcome_delivered: false };
    let busy = Error { operation: 0x23001, errno: 16 };
    require(route.launch(a, 0) == Err(busy), 997);
    let failed = Some(Event { generation: 1, kind: EventKind::LaunchFailed(busy) });
    require(route.pending == failed && route.attempt.error == Some(busy), 997);
    require(route.attempt.reader.is_some() && route.attempt.writer.is_some() && route.attempt.worker.is_none(), 997);
    let sentinel = Some(Event { generation: 0, kind: EventKind::Cleaned });
    let mut inbox = sentinel;
    require(!route.deliver(&mut inbox) && inbox == sentinel && route.pending == failed, 997);
    require(route.observe(a) == Err(Error { operation: 0, errno: 9 }) && route.pending == failed, 997);
    require(route.cleanup(a) == Err(Error { operation: 0, errno: 16 }), 998);
    require(route.attempt.reader.is_some() && route.attempt.writer.is_some(), 998);
    inbox = None;
    require(route.deliver(&mut inbox) && inbox == failed && route.pending.is_none(), 998);
    require(route.launch(a, 0) == Err(Error { operation: 0, errno: 16 }) && route.pending.is_none(), 998);
    accepted(route.cleanup(a), 999);
    let cleaned = Some(Event { generation: 1, kind: EventKind::Cleaned });
    require(route.attempt.clean() && route.pending == cleaned && !route.eligible(), 999);
    require(!route.deliver(&mut inbox) && inbox == failed && route.pending == cleaned, 999);
    inbox = None;
    require(route.deliver(&mut inbox) && inbox == cleaned && route.eligible() && route.attempt.error == Some(busy), 999);
    terminal(a, blocker, 18); accepted(a.close(reader), 999); reclaim(a, blocker);
    for slot in [0, 1] {
        let (reader, writer) = accepted(a.channel(), 999);
        let worker = accepted(a.launch(slot, writer, b"exit"), 999);
        terminal(a, worker, 18); accepted(a.close(reader), 999); reclaim(a, worker);
    }
    require(a.clean(), 999); finish(100)
}


pub fn run_routed_replacement(a: &mut Adapter) -> ! {
    let (reader, writer) = accepted(a.channel(), 1001);
    let blocker = accepted(a.launch(0, writer, b"exit"), 1001);
    let mut failed = RoutedAttempt { attempt: accepted(Attempt::acquire(a, 1), 1001), pending: None, outcome_delivered: false };
    let old_reader = failed.attempt.reader;
    let busy = Error { operation: 0x23001, errno: 16 };
    require(failed.launch(a, 0) == Err(busy), 1001);
    if !cfg!(replacement_events) && !cfg!(route_old_generation) {
        require(matches!(failed.retry(a), Err(Error { operation: 0, errno: 16 })), 1001);
    }
    let mut inbox = None;
    require(failed.deliver(&mut inbox), 1001);
    accepted(failed.cleanup(a), 1001);
    let cleaned = Some(Event { generation: 1, kind: EventKind::Cleaned });
    if !cfg!(replacement_events) && !cfg!(route_old_generation) {
    require(matches!(failed.retry(a), Err(Error { operation: 0, errno: 16 })), 1001);
    require(!failed.attempt.retried && failed.pending == cleaned, 1001);
    require(!failed.deliver(&mut inbox) && failed.pending == cleaned, 1001);
    }
    inbox = None;
    require(failed.deliver(&mut inbox) && inbox == cleaned && failed.eligible(), 1001);
    terminal(a, blocker, 18); accepted(a.close(reader), 1001); reclaim(a, blocker);
    let mut next = accepted(failed.retry(a), 1002);
    require(next.attempt.generation == 2 && next.attempt.reader != old_reader &&
            next.attempt.error.is_none() && next.pending.is_none() && !next.outcome_delivered &&
            failed.attempt.retried && failed.attempt.error == Some(busy), 1002);
    if !cfg!(replacement_events) && !cfg!(route_old_generation) {
        require(matches!(failed.retry(a), Err(Error { operation: 0, errno: 28 })), 1002);
    }
    accepted(next.launch(a, 0), 1002);
    if cfg!(replacement_events) || cfg!(route_old_generation) {
    let launched = Some(Event { generation: 2, kind: EventKind::Launched });
    require(next.pending == launched && next.attempt.worker != Some(blocker), 1002);
    require(!next.deliver(&mut inbox) && inbox == cleaned && next.pending == launched, 1002);
    terminal(a, next.attempt.worker.unwrap(), 18); accepted(next.observe(a), 1003);
    inbox = None;
    require(next.deliver(&mut inbox) && inbox == Some(Event { generation: 2, kind: EventKind::Terminal(18) }), 1003);
    accepted(next.cleanup(a), 1003);
    inbox = None;
    require(next.deliver(&mut inbox) && inbox == Some(Event { generation: 2, kind: EventKind::Cleaned }) && next.eligible(), 1003);

    } else {
        terminal(a, next.attempt.worker.unwrap(), 18);
        accepted(next.attempt.cleanup(a), 1003);
        require(next.attempt.clean(), 1003);
    }
    let (reader, writer) = accepted(a.channel(), 1003);
    let worker = accepted(a.launch(1, writer, b"exit"), 1003);
    terminal(a, worker, 18); accepted(a.close(reader), 1003); reclaim(a, worker);
    require(a.clean(), 1003); finish(100)
}


fn check_route_cancel(route: &mut RoutedAttempt, a: &Adapter) {
    let pending = route.pending;
    let outcome = route.outcome_delivered;
    accepted(route.cancel_service(a), 1005); accepted(route.cancel_service(a), 1005);
    require(route.attempt.cancelled && route.pending == pending && route.outcome_delivered == outcome, 1005);
}

pub fn run_routed_cancellation(a: &mut Adapter) -> ! {
    for phase in 0..3 {
        let (reader, writer) = accepted(a.channel(), 1004);
        let blocker = accepted(a.launch(0, writer, b"exit"), 1004);
        let mut route = RoutedAttempt { attempt: accepted(Attempt::acquire(a, 1), 1004), pending: None, outcome_delivered: false };
        let busy = Error { operation: 0x23001, errno: 16 };
        require(route.launch(a, 0) == Err(busy), 1004);
        if phase == 0 { check_route_cancel(&mut route, a); }
        let mut inbox = None;
        require(route.deliver(&mut inbox) && inbox == Some(Event { generation: 1, kind: EventKind::LaunchFailed(busy) }), 1004);
        accepted(route.cleanup(a), 1004);
        let cleaned = Some(Event { generation: 1, kind: EventKind::Cleaned });
        if phase == 1 { check_route_cancel(&mut route, a); }
        require(matches!(route.retry(a), Err(Error { operation: 0, errno: 16 })), 1004);
        require(!route.deliver(&mut inbox) && route.pending == cleaned, 1004);
        inbox = None;
        require(route.deliver(&mut inbox) && inbox == cleaned && route.eligible(), 1004);
        if phase == 2 { check_route_cancel(&mut route, a); }
        require(route.attempt.cancelled, 1004);
        require(matches!(route.retry(a), Err(Error { operation: 0, errno: 13 })), 1004);
        require(route.launch(a, 0) == Err(Error { operation: 0, errno: 13 }), 1004);
        require(!route.attempt.retried && route.attempt.error == Some(busy) && route.pending.is_none(), 1004);
        terminal(a, blocker, 18); accepted(a.close(reader), 1004); reclaim(a, blocker);
        require(a.clean(), 1004);
    }
    finish(100)
}


pub fn run_routed_live_stop(a: &mut Adapter) -> ! {
    for generation in 1..=3 {
        let mut route = RoutedAttempt { attempt: accepted(Attempt::acquire(a, generation), 1006), pending: None, outcome_delivered: false };
        accepted(route.launch_mode(a, 0, b"live"), 1006);
        let worker = route.attempt.worker.unwrap();
        require(accepted(a.observe(worker), 1006).terminal == 0, 1006);
        accepted(route.attempt.register_wait(a), 1006);
        let mut inbox = None;
        if generation == 2 { require(route.deliver(&mut inbox), 1006); }
        let pending = route.pending;
        accepted(route.cancel_service(a), 1006);
        require(route.pending == pending && route.attempt.cancelled &&
                route.attempt.worker == Some(worker) && route.attempt.reader.is_some() &&
                route.attempt.wait.is_some(), 1006);
        require(!route.outcome_delivered, 1007);
        require(route.cleanup(a) == Err(Error { operation: 0, errno: 16 }), 1007);
        terminal(a, worker, 144); accepted(route.observe(a), 1007);
        let ended = Some(Event { generation, kind: EventKind::Terminal(144) });
        require(route.pending == ended, 1007);
        inbox = Some(Event { generation: 0, kind: EventKind::Cleaned });
        require(!route.deliver(&mut inbox) && route.pending == ended, 1007);
        inbox = None;
        require(route.deliver(&mut inbox) && inbox == ended, 1007);
        accepted(route.cleanup(a), 1008);
        let cleaned = Some(Event { generation, kind: EventKind::Cleaned });
        require(route.attempt.clean() && a.clean() && route.pending == cleaned && !route.eligible(), 1008);
        require(!route.deliver(&mut inbox) && route.pending == cleaned, 1008);
        inbox = None;
        require(route.deliver(&mut inbox) && inbox == cleaned && route.eligible(), 1008);
        require(matches!(route.retry(a), Err(Error { operation: 0, errno: 13 })), 1008);
    }
    require(a.clean(), 1008); finish(100)
}


pub fn run_routed_stop_error(a: &mut Adapter) -> ! {
    for slot in [0, 1] {
        let (reader, writer) = accepted(a.channel(), 1009);
        let worker = accepted(a.launch(slot, writer, b"exit"), 1009);
        terminal(a, worker, 18); accepted(a.close(reader), 1009); reclaim(a, worker);
    }
    let mut route = RoutedAttempt { attempt: accepted(Attempt::acquire(a, 1), 1009), pending: None, outcome_delivered: false };
    accepted(route.launch(a, 0), 1009);
    let worker = route.attempt.worker.unwrap();
    terminal(a, worker, 18); accepted(route.observe(a), 1009);
    let ended = Some(Event { generation: 1, kind: EventKind::Terminal(18) });
    require(route.pending == ended, 1009);
    // Fixture-only ownership loss: leave the worker unresolved in Attempt.
    accepted(a.close(route.attempt.reader.unwrap()), 1009); route.attempt.reader = None;
    reclaim(a, worker);
    for _ in 0..2 {
        require(route.cancel_service(a) == Err(Error { operation: 0x20007, errno: 9 }), 1010);
        require(route.attempt.cancelled && route.attempt.worker == Some(worker) &&
                route.pending == ended && !route.outcome_delivered && !route.eligible(), 1009);
    }
    require(route.cleanup(a) == Err(Error { operation: 0, errno: 16 }), 1009);
    require(matches!(route.retry(a), Err(Error { operation: 0, errno: 16 })), 1009);
    let mut inbox = None;
    require(route.deliver(&mut inbox) && inbox == ended, 1011);
    require(route.cleanup(a) == Err(Error { operation: 0x25001, errno: 9 }), 1011);
    require(route.attempt.worker == Some(worker) && route.attempt.cancelled &&
            route.pending.is_none() && !route.eligible() && a.clean(), 1011);
    require(matches!(route.retry(a), Err(Error { operation: 0, errno: 16 })), 1011);
    // No more acquisition; successful fixture accounting is not route recovery.
    finish(100)
}


pub fn run_routed_partial_cleanup(a: &mut Adapter) -> ! {
    for slot in [0, 1] {
        let (reader, writer) = accepted(a.channel(), 1012);
        let worker = accepted(a.launch(slot, writer, b"exit"), 1012);
        terminal(a, worker, 18); accepted(a.close(reader), 1012); reclaim(a, worker);
    }
    let mut route = RoutedAttempt { attempt: accepted(Attempt::acquire(a, 1), 1012), pending: None, outcome_delivered: false };
    accepted(route.launch(a, 0), 1012);
    terminal(a, route.attempt.worker.unwrap(), 18);
    accepted(route.attempt.register_wait(a), 1012);
    accepted(route.observe(a), 1012);
    let ended = Some(Event { generation: 1, kind: EventKind::Terminal(18) });
    let mut inbox = None;
    require(route.deliver(&mut inbox) && inbox == ended, 1012);
    // Fixture-only wait disposal; keep its unresolved reference in Attempt.
    accepted(a.release(route.attempt.wait.unwrap()), 1012);
    for _ in 0..2 {
        require(route.cleanup(a) == Err(Error { operation: 0x25005, errno: 9 }), 1012);
        require(route.pending.is_none() && inbox == ended, 1012);
        require(route.attempt.reader.is_none() && route.attempt.worker.is_none() &&
                route.attempt.wait.is_some() && route.outcome_delivered && !route.eligible() && a.clean(), 1013);
    }
    inbox = None;
    require(!route.deliver(&mut inbox) && inbox.is_none(), 1012);
    require(matches!(route.retry(a), Err(Error { operation: 0, errno: 16 })), 1013);
    // No acquisitions after failure, and no assertion of Attempt recovery.
    finish(100)
}
