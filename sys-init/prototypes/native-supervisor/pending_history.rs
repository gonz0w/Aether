// SPDX-License-Identifier: BSD-2-Clause
//! Private immutable view. Only the parent binding module can mint native origin.
use crate::sample_receipts::{Sample, State};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(super) enum Replay { Denied, Duplicate }

pub(super) struct View<'a, O, T, W> {
    owner: &'a O,
    token: &'a T,
    index: usize,
    worker: W,
    sample: &'a Sample,
}
impl<'a, O, T: PartialEq, W: Copy + PartialEq> View<'a, O, T, W> {
    // Caller must bind these values from the same live session; no public API.
    pub(super) fn terminal(owner: &'a O, token: &'a T, index: usize,
                           worker: W, sample: &'a Sample) -> Option<Self> {
        if !matches!(sample.state(), State::Terminal(_)) { return None; }
        Some(Self { owner, token, index, worker, sample })
    }
    #[inline(always)]
    pub(super) fn replay(&self, owner: &O, token: &T, index: usize, worker: W) -> Replay {
        if !core::ptr::eq(self.owner, owner) || self.index != index || self.worker != worker ||
            (!cfg!(history_skip_token) && self.token != token) { return Replay::Denied; }
        // Replay refers to this exact immutable sample, not a caller-supplied Fact.
        Replay::Duplicate
    }
    pub(super) fn sample(&self) -> &Sample { self.sample }
}

/// Local comparison outcomes. None acknowledges journal application or cleanup.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(super) enum Offer { Denied, Duplicate, Conflict, Closed }

/// One primary and one diagnostic borrow; native Driver ownership is separate.
/// No method releases, resets or replaces a retained sample in the normal build.
pub(super) struct Held<'a, O, T, W> {
    primary: View<'a, O, T, W>,
    diagnostic: Option<&'a Sample>,
    closed: bool,
}
impl<'a, O, T: PartialEq, W: Copy + PartialEq> Held<'a, O, T, W> {
    pub(super) fn new(primary: View<'a, O, T, W>) -> Self {
        Self { primary, diagnostic: None, closed: false }
    }
    /// Trusted synthetic producer only; the eventual native guard must reserve
    /// actual diagnostic storage and propagate Conflict to Driver admission.
    #[inline(always)]
    pub(super) fn offer_synthetic(
        &mut self, owner: &O, token: &T, index: usize, worker: W,
        produce: impl FnOnce() -> Option<View<'a, O, T, W>>,
    ) -> Offer {
        if !cfg!(conflict_skip_guard) && !cfg!(guard_reoffer_produce) && (self.closed || self.diagnostic.is_some()) {
            return Offer::Closed;
        }
        if self.primary.replay(owner, token, index, worker) != Replay::Duplicate {
            return Offer::Denied;
        }
        let Some(mut candidate) = produce() else { return Offer::Denied; };
        if self.primary.replay(candidate.owner, candidate.token, candidate.index, candidate.worker)
            != Replay::Duplicate { return Offer::Denied; }
        if cfg!(conflict_ignore_contents) || self.primary.sample == candidate.sample {
            return Offer::Duplicate;
        }
        if cfg!(conflict_overwrite_primary) { core::mem::swap(&mut self.primary, &mut candidate); }
        self.diagnostic = Some(candidate.sample);
        if !cfg!(conflict_skip_close) { self.closed = true; }
        Offer::Conflict
    }
    pub(super) fn is_closed(&self) -> bool { self.closed }
    pub(super) fn primary(&self) -> &Sample { self.primary.sample }
    pub(super) fn diagnostic(&self) -> Option<&Sample> {
        self.diagnostic
    }
}
