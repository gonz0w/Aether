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

pub type Pipe = SharedPipe<2>;
pub type PipelinePipe = SharedPipe<4>;
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
        if let Some(generation) = generation {
            if !self.active || self.generation != generation {
                return Err(EBADF);
            }
        }
        Ok(())
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

#[cfg(test)]
#[path = "exec_fds.rs"]
mod exec_fds;

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::VecDeque;

    fn create() -> [u8; 32] {
        let mut frame = [0; 32];
        put(&mut frame, 0, 82);
        put(&mut frame, 4, FACTORY);
        put(&mut frame, 8, 1);
        frame
    }

    fn data(op: u32, generation: u32, end: u32, n: u32) -> [u8; 32] {
        let mut frame = [0; 32];
        put(&mut frame, 0, op);
        put(&mut frame, 4, 0x78000000 | (generation << 8) | end);
        put(&mut frame, 8, end + 2);
        put(&mut frame, 12, n);
        frame
    }

    fn result(outcome: Outcome) -> [u8; 32] {
        match outcome {
            Outcome::Reply(frame) => frame,
            Outcome::Pending => panic!("expected completed reply"),
        }
    }

    fn opened() -> Pipe {
        let mut pipe = Pipe::new();
        let response = result(pipe.request(Caller::Parent, &create()));
        assert_eq!(
            response,
            [
                0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 120, 2, 1, 0, 120, 3, 0, 0, 0, 4, 0, 0, 0, 0, 1,
                0, 0, 16, 0, 0, 0
            ]
        );
        pipe
    }

    #[test]
    fn exec_plan_keeps_writer_alias_and_peer_reader_until_last_close() {
        let mut pipe = opened();
        pipe.stage_child(1, [true; 2]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(pipe.request(Caller::Parent, &data(3, 1, 2, 0)), reply(0));
        let mut table = [0; 64];
        table[4..8].copy_from_slice(&[4, 0, 1, 0]); // dup2(writer, stdout)
        table[12..16].copy_from_slice(&[3, 1, 1, 0]);
        table[16..20].copy_from_slice(&[4, 1, 1, 0]);
        let users = [0, 0, 0, 1, 2];
        let before = format!("{pipe:?}");
        let plan = exec_fds::prepare_pipe(&table, &users).unwrap();
        assert_eq!(plan.users, [0, 0, 0, 0, 1]);
        assert_eq!(plan.release, [false, false, false, true, false]);
        assert_eq!(format!("{pipe:?}"), before); // Failed admission can discard plan.
        pipe.commit_exec(
            Caller::Child(1),
            1,
            [users[3] != 0, users[4] != 0],
            [plan.users[3] != 0, plan.users[4] != 0],
        )
        .unwrap();
        assert_eq!(pipe.holders, [[true, false], [false, true]]);
        assert_eq!(
            pipe.request(Caller::Parent, &data(1, 1, 1, 16)),
            Outcome::Pending
        );
        let mut write = data(2, 1, 2, 4);
        write[16..20].copy_from_slice(b"exec");
        assert_eq!(pipe.request(Caller::Child(1), &write), reply(4));
        assert_eq!(pipe.request(Caller::Child(1), &data(3, 1, 2, 0)), reply(0));
        let read = result(pipe.request(Caller::Parent, &data(1, 1, 1, 16)));
        assert_eq!(word(&read, 0), 4);
        assert_eq!(&read[16..20], b"exec");
        assert_eq!(pipe.request(Caller::Parent, &data(1, 1, 1, 16)), reply(0));
        // Exec did not consume the child identity or terminal record.
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
    }

    #[test]
    fn exec_last_reader_discards_bytes_but_peer_writer_survives() {
        let mut pipe = opened();
        pipe.stage_child(1, [false, true]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(
            pipe.request(Caller::Child(1), &data(2, 1, 2, 16)),
            reply(16)
        );
        pipe.commit_exec(Caller::Parent, 1, [true; 2], [false; 2])
            .unwrap();
        assert_eq!(pipe.len, 0);
        assert_eq!(pipe.bytes, [0; CAPACITY]);
        assert_eq!(pipe.holders, [[false; 2], [false, true]]);
        assert_eq!(
            pipe.request(Caller::Child(1), &data(2, 1, 2, 1)),
            reply(EPIPE)
        );
        assert!(!pipe.retire_if_idle([false; 2]));
    }

    #[test]
    fn exec_rejects_stale_or_amplified_plans_without_effects() {
        let mut pipe = opened();
        pipe.stage_child(1, [true; 2]).unwrap();
        for (caller, generation, before, after, error) in [
            (Caller::Child(1), 1, [true; 2], [false; 2], EACCES), // Not ready.
            (Caller::Parent, 0, [true; 2], [false; 2], EBADF),
            (Caller::Parent, 2, [true; 2], [false; 2], EBADF),
            (Caller::Parent, 1, [false, true], [false; 2], EACCES),
        ] {
            let snapshot = format!("{pipe:?}");
            assert_eq!(
                pipe.commit_exec(caller, generation, before, after),
                Err(error)
            );
            assert_eq!(format!("{pipe:?}"), snapshot);
        }
        pipe.finish_child_copy(1, true).unwrap();
        pipe.commit_exec(Caller::Child(1), 1, [true; 2], [true, false])
            .unwrap();
        let snapshot = format!("{pipe:?}");
        // Cannot restore the closed writer, even with an accurate precondition.
        assert_eq!(
            pipe.commit_exec(Caller::Child(1), 1, [true, false], [true; 2]),
            Err(EACCES)
        );
        // Nor can a stale descriptor snapshot drop the remaining reader.
        assert_eq!(
            pipe.commit_exec(Caller::Child(1), 1, [true; 2], [false; 2]),
            Err(EACCES)
        );
        assert_eq!(format!("{pipe:?}"), snapshot);
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
        pipe.stage_child(2, [true; 2]).unwrap();
        pipe.finish_child_copy(2, true).unwrap();
        let snapshot = format!("{pipe:?}");
        assert_eq!(
            pipe.commit_exec(Caller::Child(1), 1, [true; 2], [false; 2]),
            Err(EACCES)
        );
        assert_eq!(format!("{pipe:?}"), snapshot);
    }

    #[test]
    fn exec_old_pipe_generation_cannot_close_reused_endpoints() {
        let mut pipe = opened();
        pipe.commit_exec(Caller::Parent, 1, [true; 2], [false; 2])
            .unwrap();
        assert!(pipe.retire_if_idle([false; 2]));
        let snapshot = format!("{pipe:?}");
        assert_eq!(
            pipe.commit_exec(Caller::Parent, 1, [false; 2], [false; 2]),
            Err(EBADF)
        );
        assert_eq!(format!("{pipe:?}"), snapshot);
        result(pipe.request(Caller::Parent, &create()));
        let snapshot = format!("{pipe:?}");
        assert_eq!(
            pipe.commit_exec(Caller::Parent, 1, [true; 2], [false; 2]),
            Err(EBADF)
        );
        assert_eq!(format!("{pipe:?}"), snapshot);
        pipe.confirmed_terminal(Caller::Parent).unwrap();
        assert_eq!(
            pipe.commit_exec(Caller::Parent, 2, [false; 2], [false; 2]),
            Err(EACCES)
        );
    }

    fn unchanged(pipe: &mut Pipe, caller: Caller, frame: &[u8; 32], expected: Outcome) {
        let before = format!("{pipe:?}");
        assert_eq!(pipe.request(caller, frame), expected);
        assert_eq!(
            format!("{pipe:?}"),
            before,
            "rejected/pending request changed state"
        );
    }

    #[test]
    fn factory_rejection_never_consumes_generation() {
        let mut pipe = Pipe::new();
        let mut frame = create();
        put(&mut frame, 4, FACTORY + 1);
        unchanged(&mut pipe, Caller::Parent, &frame, reply(EACCES));
        for offset in 8..32 {
            frame = create();
            frame[offset] ^= 0x80;
            unchanged(&mut pipe, Caller::Parent, &frame, reply(EINVAL));
        }
        pipe.stage_child(1, [false; 2]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        unchanged(&mut pipe, Caller::Child(1), &create(), reply(EACCES));
        let response = result(pipe.request(Caller::Parent, &create()));
        assert_eq!(word(&response, 4), 1);
        unchanged(&mut pipe, Caller::Parent, &create(), reply(ENFILE));
    }

    #[test]
    fn malformed_and_wrong_authority_leave_all_state_unchanged() {
        let mut pipe = opened();
        for frame in [
            data(0, 1, 1, 0),
            data(4, 1, 1, 0),
            data(1, 1, 1, 17),
            data(3, 1, 2, 1),
        ] {
            unchanged(&mut pipe, Caller::Parent, &frame, reply(EINVAL));
        }
        for offset in 16..32 {
            let mut frame = data(1, 1, 1, 16);
            frame[offset] = 1;
            unchanged(&mut pipe, Caller::Parent, &frame, reply(EINVAL));
        }
        for frame in [
            data(1, 1, 2, 1),
            data(2, 1, 1, 1),
            data(1, 0, 1, 1),
            data(1, 2, 1, 1),
            data(1, 1, 3, 1),
        ] {
            unchanged(&mut pipe, Caller::Parent, &frame, reply(EACCES));
        }
        for offset in [4, 6, 7, 8, 9, 10, 11] {
            let mut frame = data(1, 1, 1, 1);
            frame[offset] ^= 0x80;
            unchanged(&mut pipe, Caller::Parent, &frame, reply(EACCES));
        }
        unchanged(
            &mut pipe,
            Caller::Child(1),
            &data(1, 1, 1, 1),
            reply(EACCES),
        );
        let mut frame = data(2, 1, 2, 1);
        frame[17] = 1;
        unchanged(&mut pipe, Caller::Parent, &frame, reply(EINVAL));
    }

    #[test]
    fn fifo_wraparound_matches_independent_byte_queue() {
        let mut pipe = opened();
        let mut expected = VecDeque::new();
        for turn in 0..900usize {
            let n = turn % 16 + 1;
            let mut frame = data(2, 1, 2, n as u32);
            for (index, byte) in frame[16..16 + n].iter_mut().enumerate() {
                *byte = (turn + index) as u8;
            }
            if expected.len() + n <= CAPACITY {
                assert_eq!(pipe.request(Caller::Parent, &frame), reply(n as i32));
                expected.extend(&frame[16..16 + n]);
            } else {
                unchanged(&mut pipe, Caller::Parent, &frame, Outcome::Pending);
            }
            let wanted = (turn * 7) % 16 + 1;
            if expected.is_empty() {
                unchanged(
                    &mut pipe,
                    Caller::Parent,
                    &data(1, 1, 1, wanted as u32),
                    Outcome::Pending,
                );
            } else {
                let response = result(pipe.request(Caller::Parent, &data(1, 1, 1, wanted as u32)));
                let count = expected.len().min(wanted);
                assert_eq!(word(&response, 0), count as u32);
                assert_eq!(&response[4..16], &[0; 12]);
                for byte in &response[16..16 + count] {
                    assert_eq!(Some(*byte), expected.pop_front());
                }
                assert!(response[16 + count..].iter().all(|byte| *byte == 0));
            }
            assert_eq!(pipe.len, expected.len());
        }
    }

    #[test]
    fn full_write_waits_without_partial_enqueue_then_reader_makes_progress() {
        let mut pipe = opened();
        pipe.stage_child(1, [true; 2]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        let mut write = data(2, 1, 2, 16);
        write[16..].fill(0xa5);
        for _ in 0..16 {
            assert_eq!(pipe.request(Caller::Child(1), &write), reply(16));
        }
        unchanged(&mut pipe, Caller::Child(1), &write, Outcome::Pending);
        assert_eq!(
            word(&result(pipe.request(Caller::Parent, &data(1, 1, 1, 15))), 0),
            15
        );
        unchanged(&mut pipe, Caller::Child(1), &write, Outcome::Pending);
        assert_eq!(
            word(&result(pipe.request(Caller::Parent, &data(1, 1, 1, 1))), 0),
            1
        );
        assert_eq!(pipe.request(Caller::Child(1), &write), reply(16));
        assert_eq!(pipe.len, 256);
    }

    #[test]
    fn staged_writer_prevents_early_eof_but_cannot_issue_requests() {
        let mut pipe = opened();
        pipe.stage_child(1, [false, true]).unwrap();
        assert_eq!(pipe.request(Caller::Parent, &data(3, 1, 2, 0)), reply(0));
        unchanged(
            &mut pipe,
            Caller::Parent,
            &data(1, 1, 1, 1),
            Outcome::Pending,
        );
        unchanged(
            &mut pipe,
            Caller::Child(1),
            &data(2, 1, 2, 1),
            reply(EACCES),
        );
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(pipe.request(Caller::Child(1), &data(2, 1, 2, 1)), reply(1));
        assert_eq!(
            word(&result(pipe.request(Caller::Parent, &data(1, 1, 1, 1))), 0),
            1
        );
    }

    #[test]
    fn failed_copy_preserves_parent_data_and_allows_known_safe_retry() {
        let mut pipe = opened();
        assert_eq!(pipe.request(Caller::Parent, &data(2, 1, 2, 3)), reply(3));
        let before = format!("{pipe:?}");
        pipe.stage_child(1, [true; 2]).unwrap();
        assert_eq!(pipe.finish_child_copy(2, false), Err(EBADF));
        pipe.finish_child_copy(1, false).unwrap();
        assert_eq!(format!("{pipe:?}"), before);
        pipe.stage_child(1, [true; 2]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(pipe.stage_child(2, [true; 2]), Err(EACCES));
    }

    #[test]
    fn terminal_writer_leaves_buffered_data_then_eof_without_wait_collection() {
        let mut pipe = opened();
        pipe.stage_child(1, [false, true]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(pipe.request(Caller::Parent, &data(3, 1, 2, 0)), reply(0));
        let mut write = data(2, 1, 2, 4);
        write[16..20].copy_from_slice(b"pipe");
        assert_eq!(pipe.request(Caller::Child(1), &write), reply(4));
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
        let response = result(pipe.request(Caller::Parent, &data(1, 1, 1, 16)));
        assert_eq!(word(&response, 0), 4);
        assert_eq!(&response[16..20], b"pipe");
        assert_eq!(pipe.request(Caller::Parent, &data(1, 1, 1, 16)), reply(0));
        unchanged(&mut pipe, Caller::Child(1), &write, reply(EACCES));
    }

    #[test]
    fn last_reader_causes_epipe_without_enqueue_and_zero_length_stays_zero() {
        let mut pipe = opened();
        pipe.stage_child(1, [true, false]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(pipe.request(Caller::Parent, &data(3, 1, 1, 0)), reply(0));
        let mut write = data(2, 1, 2, 16);
        write[16..].fill(0xad);
        assert_eq!(pipe.request(Caller::Parent, &write), reply(16));
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
        assert_eq!(pipe.len, 0);
        assert_eq!(pipe.bytes, [0; CAPACITY]);
        unchanged(&mut pipe, Caller::Parent, &data(2, 1, 2, 1), reply(EPIPE));
        unchanged(&mut pipe, Caller::Parent, &data(2, 1, 2, 0), reply(0));
        unchanged(&mut pipe, Caller::Parent, &data(1, 1, 1, 0), reply(EACCES));
    }

    #[test]
    fn zero_length_never_waits_but_still_checks_framing_and_direction() {
        let mut pipe = opened();
        unchanged(&mut pipe, Caller::Parent, &data(1, 1, 1, 0), reply(0));
        unchanged(&mut pipe, Caller::Parent, &data(2, 1, 2, 0), reply(0));
        unchanged(&mut pipe, Caller::Parent, &data(1, 1, 2, 0), reply(EACCES));
        let mut frame = data(2, 1, 2, 0);
        frame[16] = 1;
        unchanged(&mut pipe, Caller::Parent, &frame, reply(EINVAL));
    }

    #[test]
    fn old_terminal_cannot_release_replacement_holders_or_widen_inheritance() {
        let mut pipe = opened();
        pipe.stage_child(1, [true; 2]).unwrap();
        pipe.finish_child_copy(1, true).unwrap();
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
        pipe.stage_child(2, [true; 2]).unwrap();
        pipe.finish_child_copy(2, true).unwrap();
        let before = format!("{pipe:?}");
        assert_eq!(pipe.confirmed_terminal(Caller::Child(1)), Err(EBADF));
        assert_eq!(pipe.finish_child_copy(1, false), Err(EBADF));
        assert_eq!(format!("{pipe:?}"), before);
        pipe.confirmed_terminal(Caller::Child(2)).unwrap();
        assert_eq!(pipe.stage_child(1, [true; 2]), Err(EACCES));
        assert_eq!(pipe.stage_child(4, [true; 2]), Err(EACCES));
        assert_eq!(pipe.request(Caller::Parent, &data(3, 1, 2, 0)), reply(0));
        assert_eq!(pipe.stage_child(3, [true; 2]), Err(EACCES));
        pipe.stage_child(3, [true, false]).unwrap();
    }

    #[test]
    fn retirement_waits_for_holders_and_pending_references_then_zeroes_reuse() {
        let mut pipe = opened();
        assert!(!pipe.retire_if_idle([false; 2]));
        for generation in 1..=3 {
            let mut write = data(2, generation, 2, 16);
            write[16..].fill(0xad);
            assert_eq!(pipe.request(Caller::Parent, &write), reply(16));
            assert_eq!(
                pipe.request(Caller::Parent, &data(3, generation, 1, 0)),
                reply(0)
            );
            assert_eq!(
                pipe.request(Caller::Parent, &data(3, generation, 2, 0)),
                reply(0)
            );
            for pending in [[true, false], [false, true], [true; 2]] {
                assert!(!pipe.retire_if_idle(pending));
                unchanged(&mut pipe, Caller::Parent, &create(), reply(ENFILE));
            }
            assert!(pipe.retire_if_idle([false; 2]));
            assert_eq!(pipe.bytes, [0; CAPACITY]);
            unchanged(
                &mut pipe,
                Caller::Parent,
                &data(1, generation, 1, 16),
                reply(EBADF),
            );
            if generation < 3 {
                assert_eq!(
                    word(&result(pipe.request(Caller::Parent, &create())), 4),
                    generation + 1
                );
                unchanged(
                    &mut pipe,
                    Caller::Parent,
                    &data(3, generation, 2, 0),
                    reply(EBADF),
                );
                unchanged(
                    &mut pipe,
                    Caller::Parent,
                    &data(1, generation + 1, 1, 16),
                    Outcome::Pending,
                );
            }
        }
        unchanged(&mut pipe, Caller::Parent, &create(), reply(ENFILE));
    }

    #[test]
    fn parent_terminal_preserves_child_holders_and_staged_terminal_is_cleanup() {
        let mut pipe = opened();
        pipe.stage_child(1, [true; 2]).unwrap();
        pipe.confirmed_terminal(Caller::Parent).unwrap();
        assert!(!pipe.retire_if_idle([false; 2]));
        unchanged(&mut pipe, Caller::Parent, &create(), reply(EACCES));
        pipe.finish_child_copy(1, true).unwrap();
        assert_eq!(pipe.request(Caller::Child(1), &data(2, 1, 2, 1)), reply(1));
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
        assert!(pipe.retire_if_idle([false; 2]));
        let mut pipe = opened();
        pipe.stage_child(1, [true; 2]).unwrap();
        pipe.confirmed_terminal(Caller::Child(1)).unwrap();
        assert_eq!(pipe.holders, [[true; 2], [false; 2]]);
        assert_eq!(pipe.finish_child_copy(1, true), Err(EBADF));
    }

    fn participant(slot: usize, generation: u32) -> Caller {
        Caller::Participant { slot, generation }
    }
    fn pipeline() -> PipelinePipe {
        let mut pipe = PipelinePipe::new();
        assert_eq!(word(&result(pipe.request(Caller::Parent, &create())), 0), 0);
        pipe
    }
    fn admit_peer(pipe: &mut PipelinePipe, slot: usize, generation: u32, ends: [bool; 2]) {
        pipe.stage_participant(slot, generation, ends).unwrap();
        pipe.finish_participant_copy(slot, generation, true)
            .unwrap();
    }
    fn release_parent(pipe: &mut PipelinePipe) {
        for end in 1..=2 {
            assert_eq!(pipe.request(Caller::Parent, &data(3, 1, end, 0)), reply(0));
        }
    }
    #[test]
    fn pipeline_eof_waits_for_ready_and_staged_writers() {
        let mut pipe = pipeline();
        admit_peer(&mut pipe, 1, 1, [false, true]);
        pipe.stage_participant(2, 1, [false, true]).unwrap();
        admit_peer(&mut pipe, 3, 1, [true, false]);
        release_parent(&mut pipe);
        assert_eq!(
            pipe.request(participant(3, 1), &data(1, 1, 1, 16)),
            Outcome::Pending
        );
        let mut write = data(2, 1, 2, 3);
        write[16..19].copy_from_slice(b"ABC");
        assert_eq!(pipe.request(participant(1, 1), &write), reply(3));
        assert_eq!(pipe.request(participant(1, 1), &data(3, 1, 2, 0)), reply(0));
        let read = result(pipe.request(participant(3, 1), &data(1, 1, 1, 16)));
        assert_eq!(word(&read, 0), 3);
        assert_eq!(&read[16..19], b"ABC");
        assert_eq!(
            pipe.request(participant(3, 1), &data(1, 1, 1, 16)),
            Outcome::Pending
        );
        // Known failed copy removes only its reservation; it never gained I/O.
        assert_eq!(pipe.request(participant(2, 1), &write), reply(EACCES));
        pipe.finish_participant_copy(2, 1, false).unwrap();
        assert_eq!(
            pipe.request(participant(3, 1), &data(1, 1, 1, 16)),
            reply(0)
        );
    }
    #[test]
    fn pipeline_epipe_waits_for_last_reader_and_exec_cannot_widen() {
        let mut pipe = pipeline();
        admit_peer(&mut pipe, 1, 1, [false, true]);
        admit_peer(&mut pipe, 2, 1, [true, false]);
        admit_peer(&mut pipe, 3, 1, [true, false]);
        release_parent(&mut pipe);
        assert_eq!(pipe.request(participant(2, 1), &data(3, 1, 1, 0)), reply(0));
        let write = data(2, 1, 2, 16);
        assert_eq!(pipe.request(participant(1, 1), &write), reply(16));
        let before = format!("{pipe:?}");
        assert_eq!(
            pipe.commit_exec(participant(1, 1), 1, [false, true], [true; 2]),
            Err(EACCES)
        );
        assert_eq!(format!("{pipe:?}"), before);
        pipe.commit_exec(participant(3, 1), 1, [true, false], [false; 2])
            .unwrap();
        assert_eq!(pipe.bytes, [0; CAPACITY]);
        assert_eq!(pipe.request(participant(1, 1), &write), reply(EPIPE));
        assert_eq!(pipe.request(participant(1, 1), &data(2, 1, 2, 0)), reply(0));
        assert_eq!(
            pipe.request(participant(3, 1), &data(1, 1, 1, 1)),
            reply(EACCES)
        );
    }
    #[test]
    fn pipeline_peer_generation_is_independent_and_stale_operations_are_atomic() {
        let mut pipe = pipeline();
        admit_peer(&mut pipe, 2, 1, [true, false]);
        admit_peer(&mut pipe, 3, 1, [false, true]);
        pipe.confirmed_terminal(participant(2, 1)).unwrap();
        assert_eq!(pipe.stage_participant(2, 1, [true, false]), Err(EACCES));
        admit_peer(&mut pipe, 2, 2, [true, false]);
        for caller in [
            participant(2, 1),
            participant(0, 0),
            participant(4, 1),
            participant(usize::MAX, 1),
        ] {
            let before = format!("{pipe:?}");
            assert_eq!(pipe.request(caller, &data(1, 1, 1, 1)), reply(EACCES));
            assert_eq!(pipe.confirmed_terminal(caller), Err(EBADF));
            assert_eq!(format!("{pipe:?}"), before);
        }
        let before = format!("{pipe:?}");
        assert_eq!(pipe.stage_participant(4, 1, [true; 2]), Err(EACCES));
        assert_eq!(pipe.finish_participant_copy(0, 0, true), Err(EBADF));
        assert_eq!(pipe.finish_participant_copy(3, 2, true), Err(EBADF));
        assert_eq!(pipe.request(participant(3, 1), &create()), reply(EACCES));
        assert_eq!(format!("{pipe:?}"), before);
        let mut write = data(2, 1, 2, 1);
        write[16] = b'Q';
        assert_eq!(pipe.request(participant(3, 1), &write), reply(1));
        let read = result(pipe.request(participant(2, 2), &data(1, 1, 1, 1)));
        assert_eq!(word(&read, 0), 1);
        assert_eq!(read[16], b'Q');
    }
    #[test]
    fn pipeline_staged_terminal_releases_only_the_confirmed_peer() {
        let mut pipe = pipeline();
        admit_peer(&mut pipe, 1, 1, [true, false]);
        pipe.stage_participant(2, 1, [false, true]).unwrap();
        pipe.stage_participant(3, 2, [false, true]).unwrap();
        release_parent(&mut pipe);
        let read = data(1, 1, 1, 1);
        assert_eq!(pipe.request(participant(1, 1), &read), Outcome::Pending);
        pipe.confirmed_terminal(participant(2, 1)).unwrap();
        let before = format!("{pipe:?}");
        assert_eq!(pipe.confirmed_terminal(participant(3, 1)), Err(EBADF));
        assert_eq!(pipe.finish_participant_copy(2, 1, true), Err(EBADF));
        assert_eq!(format!("{pipe:?}"), before);
        assert_eq!(pipe.request(participant(1, 1), &read), Outcome::Pending);
        pipe.confirmed_terminal(participant(3, 2)).unwrap();
        assert_eq!(pipe.request(participant(1, 1), &read), reply(0));
    }
    #[test]
    fn pipeline_retirement_waits_for_every_participant_and_pending_slot() {
        let mut pipe = pipeline();
        for slot in 1..4 {
            admit_peer(&mut pipe, slot, 1, [true; 2]);
        }
        let mut write = data(2, 1, 2, 16);
        write[16..].fill(0xaa);
        assert_eq!(pipe.request(participant(3, 1), &write), reply(16));
        release_parent(&mut pipe);
        for slot in 1..4 {
            assert!(!pipe.retire_if_idle([false; 4]));
            pipe.confirmed_terminal(participant(slot, 1)).unwrap();
        }
        for slot in 0..4 {
            let mut pending = [false; 4];
            pending[slot] = true;
            let before = format!("{pipe:?}");
            assert!(!pipe.retire_if_idle(pending));
            assert_eq!(format!("{pipe:?}"), before);
        }
        assert!(pipe.retire_if_idle([false; 4]));
        assert_eq!(pipe.bytes, [0; CAPACITY]);
        let created = result(pipe.request(Caller::Parent, &create()));
        assert_eq!(word(&created, 4), 2);
        assert_eq!(pipe.request(Caller::Parent, &data(3, 2, 2, 0)), reply(0));
        assert_eq!(pipe.request(Caller::Parent, &data(1, 2, 1, 16)), reply(0));
    }
}

#[cfg(test)]
mod session_tests {
    use super::*;

    fn frame(op: u32, generation: u32, end: u32, data: &[u8]) -> [u8; 32] {
        let mut frame = [0; 32];
        put(&mut frame, 0, op);
        put(&mut frame, 4, 0x78000000 | (generation << 8) | end);
        put(&mut frame, 8, end + 2);
        put(&mut frame, 12, data.len() as u32);
        if op == 2 {
            frame[16..16 + data.len()].copy_from_slice(data);
        }
        frame
    }

    fn create(pipe: &mut SessionPipe) -> Outcome {
        let mut frame = [0; 32];
        put(&mut frame, 0, 82);
        put(&mut frame, 4, FACTORY);
        put(&mut frame, 8, 1);
        pipe.request(Caller::Parent, &frame)
    }

    fn code(result: Outcome) -> i32 {
        let Outcome::Reply(frame) = result else {
            panic!("unexpected pending")
        };
        word(&frame, 0) as i32
    }

    #[test]
    fn session_nine_creations_preserve_pending_barriers_and_zeroing() {
        let mut pipe = SessionPipe::new();
        for generation in 1..=9 {
            assert_eq!(code(create(&mut pipe)), 0);
            assert_eq!(pipe.generation, generation);
            assert_eq!(pipe.bytes, [0; CAPACITY]);
            assert_eq!(pipe.len, 0);
            let before = pipe.clone();
            assert_eq!(code(create(&mut pipe)), ENFILE);
            for old in 1..generation {
                for (end, op) in [(1, 1), (2, 2), (1, 3), (2, 3)] {
                    assert_eq!(
                        code(pipe.request(Caller::Parent, &frame(op, old, end, &[]))),
                        EBADF
                    );
                }
            }
            assert_eq!(pipe, before);
            pipe.stage_participant(1, generation, [true; 2]).unwrap();
            let child = Caller::Participant {
                slot: 1,
                generation,
            };
            assert_eq!(
                code(pipe.request(child, &frame(2, generation, 2, b"x"))),
                EACCES
            );
            pipe.finish_participant_copy(1, generation, true).unwrap();
            assert_eq!(
                code(pipe.request(child, &frame(2, generation, 2, b"secret"))),
                6
            );
            for end in 1..=2 {
                assert_eq!(
                    code(pipe.request(Caller::Parent, &frame(3, generation, end, &[]))),
                    0
                );
            }
            assert!(!pipe.retire_if_idle([false; 4]));
            pipe.confirmed_terminal(child).unwrap();
            assert_eq!(pipe.bytes, [0; CAPACITY]);
            for slot in 0..4 {
                let mut pending = [false; 4];
                pending[slot] = true;
                assert!(!pipe.retire_if_idle(pending));
            }
            assert!(pipe.retire_if_idle([false; 4]));
            assert_eq!(
                code(pipe.request(child, &frame(2, generation, 2, b"x"))),
                EACCES
            );
        }
        let before = pipe.clone();
        assert_eq!(code(create(&mut pipe)), ENFILE);
        assert_eq!(pipe, before);
    }

    #[test]
    fn session_fifteen_participants_are_independent_of_pipe_epoch() {
        let mut pipe = SessionPipe::new();
        assert_eq!(code(create(&mut pipe)), 0);
        for generation in 1..=15 {
            let caller = Caller::Participant {
                slot: 3,
                generation,
            };
            pipe.stage_participant(3, generation, [true; 2]).unwrap();
            // A known failed copy releases its reservation without burning an epoch.
            pipe.finish_participant_copy(3, generation, false).unwrap();
            pipe.stage_participant(3, generation, [true; 2]).unwrap();
            pipe.finish_participant_copy(3, generation, true).unwrap();
            let before = pipe.clone();
            for old in 1..generation {
                let stale = Caller::Participant {
                    slot: 3,
                    generation: old,
                };
                assert_eq!(code(pipe.request(stale, &frame(2, 1, 2, b"x"))), EACCES);
                assert_eq!(pipe.confirmed_terminal(stale), Err(EBADF));
                assert_eq!(pipe.stage_participant(3, old, [true; 2]), Err(EACCES));
            }
            assert_eq!(pipe, before);
            assert_eq!(code(pipe.request(caller, &frame(2, 1, 2, b"x"))), 1);
            assert_eq!(code(pipe.request(Caller::Parent, &frame(1, 1, 1, b"x"))), 1);
            pipe.confirmed_terminal(caller).unwrap();
            assert_eq!(
                pipe.stage_participant(3, generation, [false; 2]),
                Err(EACCES)
            );
        }
        let before = pipe.clone();
        assert_eq!(pipe.stage_participant(3, 16, [true; 2]), Err(EACCES));
        assert_eq!(pipe, before);
        // Exhausting one participant does not exhaust another or recreate the pipe.
        pipe.stage_participant(2, 1, [true; 2]).unwrap();
        assert_eq!(pipe.generation, 1);
    }
}
