// SPDX-License-Identifier: BSD-2-Clause
//! Pure bounded qualification of injected or captured register triples.
//! Driver retains storage by exclusive borrow; this validator carries no target authority.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Raw { pub rax: i64, pub rdx: u64, pub r8: u64 }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Fact { pub revision: u64, pub result: u64, pub kind: u64, pub historical_ready: bool }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cause { Boolean, ZeroRevision, Revision, Result, Readiness, KindPair, Interrupted }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Failure { Native { operation: u64, errno: u64 }, Local(Cause) }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State { Awaiting, Live, Terminal(Fact), Failed(Failure) }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Sample { receipts: [Option<Raw>; 3], received: usize, state: State }
impl Sample {
    #[inline(never)]
    pub const fn new() -> Self {
        Self { receipts: [None; 3], received: 0, state: State::Awaiting }
    }
    pub fn receipts(&self) -> &[Option<Raw>; 3] { &self.receipts }
    pub fn received(&self) -> usize { self.received }
    #[inline(always)]
    pub fn state(&self) -> State { self.state }
    fn fail(&mut self, cause: Cause) {
        self.state = if cfg!(receipt_invent_errno) && cause == Cause::Boolean {
            State::Failed(Failure::Native { operation: 0x25001, errno: 71 })
        } else { State::Failed(Failure::Local(cause)) };
    }
    /// True means this return was retained, including a return that closes sampling.
    /// False denies a later push and leaves all previously retained state untouched.
    #[inline(never)]
    pub fn push(&mut self, raw: Raw) -> bool {
        if self.state != State::Awaiting || self.received == 3 { return false; }
        let index = self.received;
        *self.receipts.get_mut(index).unwrap() = Some(raw);
        self.received += 1;
        if (cfg!(receipt_forget_prefix) || cfg!(raw_forget_prefix)) && index == 1 { self.receipts[0] = None; }
        let operation = if index == 1 { 0x20001 } else { 0x25001 };
        if raw.rax < 0 {
            self.state = State::Failed(Failure::Native { operation, errno: raw.rax.unsigned_abs() });
            return true;
        }
        let ready = if index == 1 { raw.rdx } else { raw.r8 };
        if ready > 1 { self.fail(Cause::Boolean); return true; }
        if index == 0 {
            if raw.rdx == 0 { self.state = State::Live; }
            else if raw.rax == 0 { self.fail(Cause::ZeroRevision); }
        } else if index == 2 {
            // All three slots exist by the private monotonic receipt invariant.
            let first = self.receipts[0].unwrap();
            let status = self.receipts[1].unwrap();
            if raw.rax != first.rax { self.fail(Cause::Revision); }
            else if raw.rdx != first.rdx || status.rax as u64 != first.rdx {
                self.fail(Cause::Result);
            } else if raw.r8 != first.r8 || status.rdx != first.r8 {
                self.fail(Cause::Readiness);
            } else if !matches!((status.r8, status.rax), (1, 1..=256) | (2, 135) | (3, 144)) {
                self.fail(Cause::KindPair);
            } else {
                self.state = State::Terminal(Fact { revision: first.rax as u64,
                    result: first.rdx, kind: status.r8, historical_ready: first.r8 == 1 });
            }
        }
        true
    }
    /// Explicitly synthetic local interruption, not a discarded native return.
    pub fn interrupt(&mut self) -> bool {
        if self.state != State::Awaiting || self.received == 0 { return false; }
        self.fail(Cause::Interrupted); true
    }
}
