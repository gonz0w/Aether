// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Owned candidate stream state. Actual native grants/close observations external.
use fd_startup::{ForkStreams, Plan, Source};
#[path = "fork_pipe.rs"]
mod pipe;
pub use pipe::{Caller, Outcome, SessionPipe};
/// The owner's actual cores and live parent console records, not a mirror of
/// another dispatcher. All mutation/access must remain inside Owner admission.
pub struct State {
    console: [Option<Source>; 3],
    pipes: [SessionPipe; 2],
    console_held: [[bool; 3]; 4],
    peers: [Option<u32>; 4],
    ready: [bool; 4],
}
impl State {
    /// Sources must come from actual owned console endpoints, never client text.
    /// Pipe cores are moved in, not copied from another live dispatcher.
    pub fn new(console: [Option<Source>; 3], pipes: [SessionPipe; 2]) -> Result<Self, i32> {
        for (i, source) in console.iter().enumerate() {
            if let Some(s) = source
                && (s.reference == 0
                    || s.selector != i as u32
                    || s.rights != if i == 0 { 1 } else { 2 }
                    || s.bound != 16
                    || console[..i]
                        .iter()
                        .flatten()
                        .any(|old| old.reference == s.reference))
            {
                return Err(-22);
            }
        }
        let held = console.map(|s| s.is_some());
        Ok(Self {
            console,
            pipes,
            console_held: [held, [false; 3], [false; 3], [false; 3]],
            peers: [Some(0), None, None, None],
            ready: [true, false, false, false],
        })
    }
    /// Caller first confirms actual endpoint closure; this records its result.
    /// Unknown native close must retain the record and fail-stop instead.
    pub fn console_closed(&mut self, selector: usize) -> Result<(), i32> {
        let held = self.console_held[0].get_mut(selector).ok_or(-9)?;
        if !*held {
            return Err(-9);
        }
        *held = false;
        Ok(())
    }
    /// Sole owner operations: transport routing/authenticated caller is external.
    /// Existing core uses local 0x7800 references; tagged 0x7900 routing remains
    /// an owner responsibility. No external frame is silently normalized here.
    pub fn pipe_mut(&mut self, object: usize) -> Result<&mut SessionPipe, i32> {
        self.pipes.get_mut(object).ok_or(-9)
    }
}
impl ForkStreams for State {
    fn validate_fork(&self, plan: &Plan) -> Result<(), i32> {
        self.validate_context(Caller::Parent, plan)
    }
    fn child_ready(&mut self, pid: u32) -> Result<(), i32> {
        let (who, epoch) = target(pid)?;
        if self.peers[who].is_some_and(|g| g != epoch) || self.ready[who] {
            return Err(-9);
        }
        self.change_pipes(|pipe| pipe.finish_participant_copy(who, epoch, true))?;
        self.peers[who] = Some(epoch);
        self.ready[who] = true;
        Ok(())
    }
}
impl State {
    /// Caller is authenticated by the live native process/channel owner.
    pub fn validate_context(&self, caller: Caller, plan: &Plan) -> Result<(), i32> {
        let who = self.caller(caller)?;
        let mut used = [false; 7];
        for b in &plan.bindings {
            // The gate also checks complete binding shape before invoking us.
            match b.kind {
                0 | 3 => {}
                1 if b.selector <= 2 => used[b.selector as usize] = true,
                2 if (3..=6).contains(&b.selector) => used[b.selector as usize] = true,
                _ => return Err(-22),
            }
        }
        for (i, source) in self.console.iter().enumerate() {
            let expected = if self.console_held[who][i] {
                *source
            } else {
                None
            };
            if used[i] != expected.is_some() || plan.sources[i] != expected.unwrap_or_default() {
                return Err(-9);
            }
        }
        for object in 0..2 {
            let (history, held) = self.pipes[object].view_v1(caller)?;
            if plan.history[object] != history {
                return Err(-9);
            }
            for (end, owns) in held.iter().enumerate() {
                let selector = 3 + object * 2 + end;
                if used[selector] != *owns {
                    return Err(-9);
                }
                let expected = if *owns {
                    Source {
                        reference: 0x79000000
                            | (object as u32) << 16
                            | history << 8
                            | (end as u32 + 1),
                        selector: selector as u32,
                        rights: if end == 0 { 1 } else { 2 },
                        bound: 16,
                    }
                } else {
                    Source::default()
                };
                if plan.sources[selector] != expected {
                    return Err(-9);
                }
            }
        }
        Ok(())
    }
    fn caller(&self, caller: Caller) -> Result<usize, i32> {
        let (who, epoch) = match caller {
            Caller::Parent => (0, 0),
            Caller::Child(g) => (1, g),
            Caller::Participant { slot, generation } if slot > 0 && slot < 4 => (slot, generation),
            _ => return Err(-13),
        };
        if self.peers[who] != Some(epoch) || !self.ready[who] {
            return Err(-13);
        }
        Ok(who)
    }
    fn change_pipes(
        &mut self,
        mut change: impl FnMut(&mut SessionPipe) -> Result<(), i32>,
    ) -> Result<(), i32> {
        // Private atomic plan over these two owned cores, never a second live ledger.
        let mut next = self.pipes.clone();
        for pipe in &mut next {
            change(pipe)?;
        }
        self.pipes = next;
        Ok(())
    }
    /// Stage only after full decoded FILE/stream preflight under Owner capture.
    pub fn stage_child(&mut self, pid: u32, plan: &Plan) -> Result<(), i32> {
        self.validate_context(Caller::Parent, plan)?;
        let (who, epoch) = target(pid)?;
        if self.peers[who].is_some() {
            return Err(-16);
        }
        let mut held = [false; 7];
        for b in &plan.bindings {
            if b.kind == 1 || b.kind == 2 {
                held[b.selector as usize] = true;
            }
        }
        let mut object = 0;
        self.change_pipes(|pipe| {
            let i = object;
            object += 1;
            pipe.stage_participant(who, epoch, [held[3 + i * 2], held[4 + i * 2]])
        })?;
        self.console_held[who].copy_from_slice(&held[..3]);
        self.peers[who] = Some(epoch);
        self.ready[who] = false;
        Ok(())
    }
    /// Only after confirmed no child; never use for an unknown copy outcome.
    pub fn cancel_stage(&mut self, pid: u32) -> Result<(), i32> {
        let (who, epoch) = target(pid)?;
        if self.peers[who] != Some(epoch) || self.ready[who] {
            return Err(-9);
        }
        self.change_pipes(|pipe| pipe.finish_participant_copy(who, epoch, false))?;
        self.console_held[who] = [false; 3];
        self.peers[who] = None;
        Ok(())
    }
    /// A matched native terminal is required, not merely a stop acknowledgment.
    pub fn confirmed_terminal(&mut self, caller: Caller) -> Result<(), i32> {
        let (who, epoch) = match caller {
            Caller::Parent => (0, 0),
            Caller::Child(g) => (1, g),
            Caller::Participant { slot, generation } if slot > 0 && slot < 4 => (slot, generation),
            _ => return Err(-9),
        };
        if self.peers[who] != Some(epoch) {
            return Err(-9);
        }
        self.change_pipes(|pipe| pipe.confirmed_terminal(caller))?;
        self.console_held[who] = [false; 3];
        self.peers[who] = None;
        self.ready[who] = false;
        Ok(())
    }
    pub fn retire_idle(&mut self, pending: [bool; 4]) {
        for pipe in &mut self.pipes {
            pipe.retire_if_idle(pending);
        }
    }
    /// Actual image commit must precede this destructive holder change. Only
    /// retain sources in the prevalidated old context; never add a new holder.
    pub fn commit_exec(&mut self, caller: Caller, plan: &mut Plan) -> Result<(), i32> {
        self.validate_context(caller, plan)?;
        let who = self.caller(caller)?;
        let mut held = [[false; 7]; 2];
        for binding in &plan.bindings {
            if binding.kind == 1 || binding.kind == 2 {
                let selector = binding.selector as usize;
                held[0][selector] = true;
                if binding.cloexec == 0 {
                    held[1][selector] = true;
                }
            }
        }
        let mut object = 0;
        self.change_pipes(|pipe| {
            let i = object;
            object += 1;
            let old = [held[0][3 + i * 2], held[0][4 + i * 2]];
            if old == [false; 2] {
                return Ok(());
            }
            pipe.commit_exec(
                caller,
                plan.history[i],
                old,
                [held[1][3 + i * 2], held[1][4 + i * 2]],
            )
        })?;
        self.console_held[who].copy_from_slice(&held[1][..3]);
        for b in &mut plan.bindings {
            if b.cloexec == 1 {
                *b = fd_startup::Binding::default();
            }
        }
        for (i, source) in plan.sources.iter_mut().enumerate() {
            if !held[1][i] {
                *source = Source::default();
            }
        }
        Ok(())
    }
    /// Actual tagged pipe/console request. Pending guarantees no effects. The
    /// owner retains that frame; a Reply may have effects and must never replay.
    pub fn request(
        &mut self,
        caller: Caller,
        frame: &[u8; 32],
        mut serial: impl FnMut(bool, &mut [u8]) -> i64,
    ) -> Outcome {
        let who = match self.caller(caller) {
            Ok(w) => w,
            Err(e) => return reply(e),
        };
        let op = word(frame, 0);
        if op == 82 {
            if who != 0 {
                return reply(-13);
            }
            for object in 0..2 {
                let outcome = self.pipes[object].request(caller, frame);
                match outcome {
                    Outcome::Reply(mut raw) if word(&raw, 0) == 0 => {
                        let generation = word(&raw, 4);
                        for end in 0..2 {
                            put(
                                &mut raw,
                                8 + 4 * end,
                                0x79000000
                                    | (object as u32) << 16
                                    | generation << 8
                                    | (end as u32 + 1),
                            );
                            put(&mut raw, 16 + 4 * end, (3 + object * 2 + end) as u32);
                        }
                        return Outcome::Reply(raw);
                    }
                    Outcome::Reply(raw) if word(&raw, 0) as i32 == -23 => {}
                    other => return other,
                }
            }
            return reply(-23);
        }
        let selector = word(frame, 8) as usize;
        if selector >= 7 {
            return reply(-13);
        }
        if selector >= 3 {
            let object = (selector - 3) / 2;
            let end = (selector - 3) % 2;
            let reference = word(frame, 4);
            let generation = (reference >> 8) & 255;
            if reference
                != (0x79000000 | (object as u32) << 16 | generation << 8 | (end as u32 + 1))
            {
                return reply(-13);
            }
            let mut local = *frame;
            put(
                &mut local,
                4,
                0x78000000 | generation << 8 | (end as u32 + 1),
            );
            put(&mut local, 8, (end + 3) as u32);
            return self.pipes[object].request(caller, &local);
        }
        let Some(source) = self.console[selector] else {
            return reply(-13);
        };
        if !self.console_held[who][selector] || word(frame, 4) != source.reference {
            return reply(-13);
        }
        let n = word(frame, 12) as usize;
        if !(1..=3).contains(&op)
            || n > 16
            || (op == 3 && n != 0)
            || frame[16 + if op == 2 { n } else { 0 }..]
                .iter()
                .any(|b| *b != 0)
        {
            return reply(-22);
        }
        if op == 3 {
            self.console_held[who][selector] = false;
            return reply(0);
        }
        if (op == 1 && source.rights != 1) || (op == 2 && source.rights != 2) {
            return reply(-13);
        }
        if n == 0 {
            return reply(0);
        }
        let mut response = [0; 32];
        if op == 2 {
            response[16..16 + n].copy_from_slice(&frame[16..16 + n]);
        }
        let raw = serial(op == 2, &mut response[16..16 + n]);
        if raw == -11 {
            return Outcome::Pending;
        }
        if raw < -4095 || raw > n as i64 {
            return reply(-5);
        }
        if op == 2 || raw < 0 {
            response[16..].fill(0);
        } else {
            response[16 + raw as usize..].fill(0);
        }
        put(&mut response, 0, raw as i32 as u32);
        Outcome::Reply(response)
    }
}
fn target(pid: u32) -> Result<(usize, u32), i32> {
    let suffix = pid.checked_sub(1).ok_or(-9)?;
    let (slot, epoch) = (suffix % 7, suffix / 7);
    if !(2..=4).contains(&slot) || !(1..=15).contains(&epoch) {
        return Err(-9);
    }
    Ok(((slot - 1) as usize, epoch))
}
fn word(raw: &[u8; 32], at: usize) -> u32 {
    u32::from_le_bytes(raw[at..at + 4].try_into().unwrap())
}
fn put(raw: &mut [u8; 32], at: usize, value: u32) {
    raw[at..at + 4].copy_from_slice(&value.to_le_bytes());
}
fn reply(error: i32) -> Outcome {
    let mut raw = [0; 32];
    put(&mut raw, 0, error as u32);
    Outcome::Reply(raw)
}
