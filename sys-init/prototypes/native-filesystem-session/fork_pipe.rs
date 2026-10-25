// SPDX-License-Identifier: BSD-2-Clause
//! One private pipe owned by the connection dispatcher, not a transport or SDK.
//! Caller identity comes from the authenticated connection, never request bytes.
//! The dispatcher retains an unchanged frame on Pending and retains a completed
//! reply until delivery or confirmed termination; it must never reapply that I/O.

pub const CAPACITY: usize = 256;
pub const REQUEST_BOUND: usize = 16;
pub const FACTORY: u32 = 0x76050001;
const EACCES: i32 = -13;
const EBADF: i32 = -9;
const EINVAL: i32 = -22;
const ENFILE: i32 = -23;
const EPIPE: i32 = -32;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Caller {
    Parent,
    Child(u32),
    /// Authenticated dispatcher slot, never taken from an application frame.
    Participant {
        slot: usize,
        generation: u32,
    },
}

#[derive(Debug, PartialEq, Eq)]
pub enum Outcome {
    Reply([u8; 32]),
    Pending,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Child {
    Absent,
    Staged(u32),
    Ready(u32),
}

/// Owner-selected SESSION profile; never selected by an application request.
pub type SessionPipe = SharedPipe<4, true>;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SharedPipe<const PEERS: usize, const SESSION: bool = false> {
    bytes: [u8; CAPACITY],
    head: usize,
    len: usize,
    generation: u32,
    active: bool,
    holders: [[bool; 2]; PEERS],
    peers: [Child; PEERS],
    last_generation: [u32; PEERS],
}

fn word(frame: &[u8; 32], offset: usize) -> u32 {
    u32::from_le_bytes(frame[offset..offset + 4].try_into().unwrap())
}

fn put(frame: &mut [u8; 32], offset: usize, value: u32) {
    frame[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
}

fn reply(result: i32) -> Outcome {
    let mut frame = [0; 32];
    put(&mut frame, 0, result as u32);
    Outcome::Reply(frame)
}

impl<const PEERS: usize, const SESSION: bool> SharedPipe<PEERS, SESSION> {
    pub(crate) const fn creation_limit() -> u32 {
        if SESSION { 9 } else { 3 }
    }

    const fn participant_limit() -> u32 {
        if SESSION { 15 } else { 3 }
    }

    pub const fn new() -> Self {
        assert!(PEERS == 2 || PEERS == 4);
        assert!(!SESSION || PEERS == 4);
        let mut peers = [Child::Absent; PEERS];
        peers[0] = Child::Ready(0);
        Self {
            bytes: [0; CAPACITY],
            head: 0,
            len: 0,
            generation: 0,
            active: false,
            holders: [[false; 2]; PEERS],
            peers,
            last_generation: [0; PEERS],
        }
    }

    fn identity(caller: Caller) -> Option<(usize, u32)> {
        match caller {
            Caller::Parent => Some((0, 0)),
            Caller::Child(generation) => Some((1, generation)),
            Caller::Participant { slot, generation } if slot > 0 && slot < PEERS => {
                Some((slot, generation))
            }
            _ => None,
        }
    }
    fn caller(&self, caller: Caller) -> Option<usize> {
        let (slot, generation) = Self::identity(caller)?;
        (self.peers[slot] == Child::Ready(generation)).then_some(slot)
    }

    /// Private owner validation, not a wire grant. None represents no local
    /// endpoints; other callers may still hold an active object.
    pub(crate) fn check_bindings(
        &self,
        caller: Caller,
        generation: Option<u32>,
        held: [bool; 2],
    ) -> Result<(), i32> {
        let who = self.caller(caller).ok_or(EACCES)?;
        if self.holders[who] != held || (generation.is_none() && held != [false; 2]) {
            return Err(EACCES);
        }
        if let Some(generation) = generation
            && (!self.active || self.generation != generation)
        {
            return Err(EBADF);
        }
        Ok(())
    }

    /// Pure caller metadata for the tagged owner; generation is retained even
    /// when inactive/no endpoints. A terminated caller is never an empty view.
    pub(crate) fn view_v1(&self, caller: Caller) -> Result<(u32, [bool; 2]), i32> {
        let who = self.caller(caller).ok_or(EACCES)?;
        let held = self.holders[who];
        self.check_bindings(
            caller,
            held.iter().any(|value| *value).then_some(self.generation),
            held,
        )?;
        Ok((self.generation, held))
    }

    /// Commit local endpoint retention after successful exec admission. The
    /// dispatcher must quiesce this caller's I/O and validate its descriptor
    /// snapshot and replacement before calling; this is not a wire operation.
    /// `before` and `after` mean at least one local alias for reader/writer.
    /// Caller identity and pipe generation remain unchanged by exec.
    pub fn commit_exec(
        &mut self,
        caller: Caller,
        generation: u32,
        before: [bool; 2],
        after: [bool; 2],
    ) -> Result<(), i32> {
        let who = self.caller(caller).ok_or(EACCES)?;
        if !self.active || generation != self.generation {
            return Err(EBADF);
        }
        if self.holders[who] != before || (0..2).any(|end| after[end] && !before[end]) {
            return Err(EACCES);
        }
        self.holders[who] = after;
        self.discard_without_readers();
        Ok(())
    }

    /// The validated fork plan selects only endpoints actually held by parent.
    /// Staging reserves holders before copying, but grants no child I/O readiness.
    pub fn stage_child(&mut self, generation: u32, inherit: [bool; 2]) -> Result<(), i32> {
        self.stage_participant(1, generation, inherit)
    }

    pub fn stage_participant(
        &mut self,
        slot: usize,
        generation: u32,
        inherit: [bool; 2],
    ) -> Result<(), i32> {
        if slot == 0
            || slot >= PEERS
            || self.peers[0] != Child::Ready(0)
            || self.peers[slot] != Child::Absent
            || generation <= self.last_generation[slot]
            || generation > Self::participant_limit()
            || (0..2).any(|end| inherit[end] && !self.holders[0][end])
        {
            return Err(EACCES);
        }
        self.peers[slot] = Child::Staged(generation);
        self.holders[slot] = inherit;
        Ok(())
    }

    /// Only call after validated readiness, or a known failed copy with no child.
    /// An ambiguous copy is NOT a known failure: confirm termination instead.
    pub fn finish_child_copy(&mut self, generation: u32, ready: bool) -> Result<(), i32> {
        self.finish_participant_copy(1, generation, ready)
    }
    pub fn finish_participant_copy(
        &mut self,
        slot: usize,
        generation: u32,
        ready: bool,
    ) -> Result<(), i32> {
        if slot == 0 || slot >= PEERS || self.peers[slot] != Child::Staged(generation) {
            return Err(EBADF);
        }
        if ready {
            self.peers[slot] = Child::Ready(generation);
            self.last_generation[slot] = generation;
        } else {
            self.peers[slot] = Child::Absent;
            self.holders[slot] = [false; 2];
            self.discard_without_readers();
        }
        Ok(())
    }

    /// The owner must observe this exact process's terminal first. A stop request,
    /// timeout, lost reply or wait acknowledgment is not terminal evidence.
    pub fn confirmed_terminal(&mut self, caller: Caller) -> Result<(), i32> {
        let (slot, generation) = Self::identity(caller).ok_or(EBADF)?;
        if self.peers[slot] != Child::Ready(generation)
            && self.peers[slot] != Child::Staged(generation)
        {
            return Err(EBADF);
        }
        self.peers[slot] = Child::Absent;
        self.last_generation[slot] = generation;
        self.holders[slot] = [false; 2];
        self.discard_without_readers();
        Ok(())
    }

    /// `pending` includes partial requests and completed-but-undelivered replies
    /// that still reference this object in the dispatcher's existing frame slots.
    /// Clearing a slot after uncertain delivery requires confirmed caller stop.
    pub fn retire_if_idle(&mut self, pending: [bool; PEERS]) -> bool {
        if !self.active || self.holders != [[false; 2]; PEERS] || pending != [false; PEERS] {
            return false;
        }
        self.bytes.fill(0);
        self.head = 0;
        self.len = 0;
        self.active = false;
        true
    }

    fn has_holder(&self, end: usize) -> bool {
        self.holders.iter().any(|held| held[end])
    }

    fn discard_without_readers(&mut self) {
        if !self.has_holder(0) {
            self.bytes.fill(0);
            self.head = 0;
            self.len = 0;
        }
    }

    /// A Reply may have applied effects. Send/cache it once; never resubmit its
    /// request on reply failure. Only Pending guarantees no bytes were changed.
    pub fn request(&mut self, caller: Caller, frame: &[u8; 32]) -> Outcome {
        let Some(who) = self.caller(caller) else {
            return reply(EACCES);
        };
        let op = word(frame, 0);
        if op == 82 {
            if word(frame, 8) != 1 || frame[12..] != [0; 20] {
                return reply(EINVAL);
            }
            if who != 0 || word(frame, 4) != FACTORY {
                return reply(EACCES);
            }
            if self.active || self.generation >= Self::creation_limit() {
                return reply(ENFILE);
            }
            self.generation += 1;
            self.active = true;
            self.holders[0] = [true; 2];
            let mut response = [0; 32];
            put(&mut response, 4, self.generation);
            put(&mut response, 8, 0x78000001 | (self.generation << 8));
            put(&mut response, 12, 0x78000002 | (self.generation << 8));
            put(&mut response, 16, 3);
            put(&mut response, 20, 4);
            put(&mut response, 24, CAPACITY as u32);
            put(&mut response, 28, REQUEST_BOUND as u32);
            return Outcome::Reply(response);
        }
        let n = word(frame, 12) as usize;
        if !(1..=3).contains(&op)
            || n > REQUEST_BOUND
            || (op == 3 && n != 0)
            || frame[16 + if op == 2 { n } else { 0 }..]
                .iter()
                .any(|byte| *byte != 0)
        {
            return reply(EINVAL);
        }
        let reference = word(frame, 4);
        let generation = (reference >> 8) & 0xff;
        let end = match reference & 0xff {
            1 => 0,
            2 => 1,
            _ => return reply(EACCES),
        };
        if reference != 0x78000000 | (generation << 8) | (end as u32 + 1)
            || generation == 0
            || generation > self.generation
            || word(frame, 8) != end as u32 + 3
            || (op == 1 && end != 0)
            || (op == 2 && end != 1)
        {
            return reply(EACCES);
        }
        if !self.active || generation != self.generation {
            return reply(EBADF);
        }
        if !self.holders[who][end] {
            return reply(EACCES);
        }
        if op == 3 {
            self.holders[who][end] = false;
            self.discard_without_readers();
            return reply(0);
        }
        if n == 0 {
            return reply(0);
        }
        if op == 1 {
            if self.len == 0 && self.has_holder(1) {
                return Outcome::Pending;
            }
            let count = n.min(self.len);
            let mut response = [0; 32];
            put(&mut response, 0, count as u32);
            for out in &mut response[16..16 + count] {
                *out = self.bytes[self.head];
                self.bytes[self.head] = 0;
                self.head = (self.head + 1) % CAPACITY;
            }
            self.len -= count;
            Outcome::Reply(response)
        } else {
            if !self.has_holder(0) {
                return reply(EPIPE);
            }
            if n > CAPACITY - self.len {
                return Outcome::Pending;
            }
            for byte in &frame[16..16 + n] {
                self.bytes[(self.head + self.len) % CAPACITY] = *byte;
                self.len += 1;
            }
            reply(n as i32)
        }
    }
}
