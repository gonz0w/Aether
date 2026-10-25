// SPDX-License-Identifier: BSD-2-Clause
//! Reservation-only logic. Synthetic indices are not native source provenance.
#![allow(dead_code)]
#[derive(Debug)]
pub(super) struct Owner { identity: u8 }
impl Owner { pub(super) fn new() -> Self { Self { identity: 0 } } }
#[derive(Clone, Copy, Debug)]
pub(super) struct Key<'a> { owner: &'a Owner, serial: u64 }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(C)]
pub(super) struct Member { pub(super) attempt: u8, pub(super) phase: u8 }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(C)]
struct Record {
    serial: u64, journal: u64, members: [Member; 2],
    before: [u8; 2], after: [u8; 2], count: u8, state: u8, effects: u8, retired: u8,
}
const EMPTY_MEMBER: Member = Member { attempt: 0, phase: 0 };
const EMPTY: Record = Record { serial: 0, journal: 0, members: [EMPTY_MEMBER; 2],
    before: [0; 2], after: [0; 2], count: 0, state: 0, effects: 0, retired: 0 };
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(C)]
struct Effect { token: [u64; 10], disposition: u8 }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(C)]
struct Storage {
    records: [Record; 6], effects: [Effect; 20],
    next: u64, next_journal: u64, used: u8, occupied: u8, active: u8, closed: u8,
}
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Error { Invalid, Busy, Full, Closed }
#[derive(Debug, PartialEq, Eq)]
pub(super) struct Inspection { pub(super) serial: u64, pub(super) journal: u64,
    pub(super) members: [Member; 2], pub(super) count: u8, pub(super) cancelled: bool }
pub(super) struct Reservations<'a> { owner: &'a Owner, storage: Storage }
impl<'a> Reservations<'a> {
    #[inline(never)]
    pub(super) fn new(owner: &'a mut Owner) -> Self {
        // A constant zero value avoids nested aggregate temporaries on the native stack.
        const ZERO: Storage = Storage { records: [EMPTY; 6],
            effects: [Effect { token: [0; 10], disposition: 0 }; 20],
            next: 0, next_journal: 0, used: 0, occupied: 0, active: 0, closed: 0 };
        let mut result = Self { owner, storage: ZERO };
        result.storage.next = 1; result.storage.next_journal = 1;
        result
    }
    #[inline(always)]
    pub(super) fn reserve(&mut self, members: &[Member]) -> Result<Key<'a>, Error> {
        self.reserve_phase::<1>(members)
    }
    #[inline(never)]
    fn reserve_phase<const PHASE: u8>(&mut self, members: &[Member]) -> Result<Key<'a>, Error> {
        if self.storage.closed != 0 { return Err(Error::Closed); }
        #[cfg(reservation_partial)] { self.storage.occupied = 20; }
        if !(1..=2).contains(&members.len()) || members.iter().any(|m| m.attempt > 1 || m.phase != PHASE)
            || members.windows(2).any(|m| m[0].attempt >= m[1].attempt) {
            return Err(Error::Invalid);
        }
        if self.storage.active != 0 {
            let r = self.storage.records.get((self.storage.active - 1) as usize).ok_or(Error::Invalid)?;
            return if r.state == 1 && r.count as usize == members.len() &&
                members.iter().enumerate().all(|(i, m)| r.members.get(i) == Some(m)) {
                Ok(Key { owner: self.owner, serial: r.serial })
            } else { Err(Error::Busy) };
        }
        if self.storage.used >= 6 || self.storage.occupied != 0 || self.storage.next == u64::MAX
            || self.storage.next_journal == u64::MAX { return Err(Error::Full); }
        let mut record = EMPTY;
        record.serial = self.storage.next; record.journal = self.storage.next_journal;
        for (index, member) in members.iter().enumerate() {
            *record.members.get_mut(index).ok_or(Error::Invalid)? = *member;
        }
        record.count = members.len() as u8; record.state = 1;
        // No fallible step after mutation begins; exclusive borrow covers both reservations.
        *self.storage.records.get_mut(self.storage.used as usize).ok_or(Error::Full)? = record;
        self.storage.used += 1; self.storage.active = self.storage.used;
        self.storage.occupied = 20;
        self.storage.next += 1; self.storage.next_journal += 1;
        Ok(Key { owner: self.owner, serial: record.serial })
    }
    fn index(&self, key: &Key<'_>) -> Result<usize, Error> {
        if !core::ptr::eq(key.owner, self.owner) { return Err(Error::Invalid); }
        self.storage.records.iter()
            .position(|r| r.state != 0 && r.serial == key.serial).ok_or(Error::Invalid)
    }
    #[inline(never)]
    pub(super) fn inspect(&self, key: &Key<'_>) -> Result<Inspection, Error> {
        let r = self.storage.records.get(self.index(key)?).ok_or(Error::Invalid)?;
        Ok(Inspection { serial: r.serial, journal: r.journal, members: r.members,
            count: r.count, cancelled: r.state == 2 })
    }
    #[inline(never)]
    pub(super) fn cancel(&mut self, key: &Key<'_>) -> Result<(), Error> {
        let index = self.index(key)?;
        if self.storage.closed != 0 { return Err(Error::Closed); }
        let record = self.storage.records.get_mut(index).ok_or(Error::Invalid)?;
        if self.storage.active as usize != index + 1 || record.state != 1 {
            return Err(Error::Invalid);
        }
        record.state = 2;
        self.storage.active = 0; self.storage.occupied = 0;
        #[cfg(reservation_reuse)] { self.storage.next -= 1; self.storage.next_journal -= 1; }
        #[cfg(reservation_forget)] { *record = EMPTY; }
        Ok(())
    }
}
const _: () = assert!(core::mem::size_of::<Storage>() == 1976);
const _: () = assert!(core::mem::size_of::<Reservations<'_>>() == 1984);
const _: () = assert!(core::mem::align_of::<Storage>() == 8);

#[cfg(test)]
mod tests {
    use super::*;
    const A: Member = Member { attempt: 0, phase: 1 };
    const B: Member = Member { attempt: 1, phase: 1 };
    #[test]
    fn duplicate_and_busy() {
        let mut owner = Owner::new(); let mut r = Reservations::new(&mut owner);
        let k = r.reserve(&[A, B]).unwrap(); let before = r.storage;
        assert_eq!(r.reserve(&[A, B]).unwrap().serial, k.serial);
        assert!(matches!(r.reserve(&[B]), Err(Error::Busy)));
        assert_eq!(r.storage, before);
        assert_eq!(r.inspect(&k).unwrap(), Inspection { serial: 1, journal: 1,
            members: [A, B], count: 2, cancelled: false });
        assert_eq!(r.storage.occupied, 20);
    }
    #[test]
    fn invalid_is_atomic() {
        for members in [&[][..], &[B, A], &[A, A], &[A, B, A],
            &[Member { attempt: 2, phase: 1 }], &[Member { attempt: 0, phase: 0 }],
            &[Member { attempt: 0, phase: 2 }], &[Member { attempt: 0, phase: 255 }]] {
            let mut owner = Owner::new(); let mut r = Reservations::new(&mut owner);
            let before = r.storage; assert!(matches!(r.reserve(members), Err(Error::Invalid)));
            assert_eq!(r.storage, before, "denial must not reserve credits");
        }
    }
    #[test]
    fn cancel_retains_history_and_serials() {
        let mut owner = Owner::new(); let mut r = Reservations::new(&mut owner);
        let k = r.reserve(&[A]).unwrap(); r.cancel(&k).unwrap();
        assert_eq!(r.inspect(&k).ok(), Some(Inspection { serial: 1, journal: 1,
            members: [A, EMPTY_MEMBER], count: 1, cancelled: true }), "cancelled history must survive");
        let before = r.storage; assert_eq!(r.cancel(&k), Err(Error::Invalid)); assert_eq!(r.storage, before);
        let next = r.reserve(&[A]).unwrap();
        assert_eq!(next.serial, 2, "cancel must not reuse serials");
        assert_eq!(r.inspect(&next).unwrap().journal, 2);
    }
    #[test]
    fn foreign_keys_deny() {
        let mut a = Owner::new(); let mut b = Owner::new();
        let mut one = Reservations::new(&mut a); let mut two = Reservations::new(&mut b);
        let first = one.reserve(&[A]).unwrap(); let other = two.reserve(&[A]).unwrap();
        let before = one.storage; assert_eq!(one.cancel(&other), Err(Error::Invalid));
        assert_eq!(one.inspect(&other), Err(Error::Invalid));
        let altered = Key { owner: first.owner, serial: 55 };
        assert_eq!(one.cancel(&altered), Err(Error::Invalid)); assert_eq!(one.storage, before);
    }
    #[test]
    fn exhaustion_and_closure() {
        let mut owner = Owner::new(); let mut r = Reservations::new(&mut owner);
        for _ in 0..6 { let k = r.reserve(&[A]).unwrap(); r.cancel(&k).unwrap(); }
        let before = r.storage; assert!(matches!(r.reserve(&[A]), Err(Error::Full))); assert_eq!(r.storage, before);
        for field in 0..4 {
            let mut owner = Owner::new(); let mut r = Reservations::new(&mut owner);
            match field { 0 => r.storage.next = u64::MAX, 1 => r.storage.next_journal = u64::MAX,
                2 => r.storage.occupied = 1, _ => r.storage.closed = 1 }
            let before = r.storage;
            assert!(matches!(r.reserve(&[A]), Err(Error::Full) | Err(Error::Closed)));
            assert_eq!(r.storage, before);
        }
    }
}

// Fixed policy/application layer; no native provenance or effect execution API.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(super) enum Profile { Independent, StartedDependency }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Policy { started: [u8; 2], pending: [bool; 2], profile: Profile }
impl Policy {
    fn new(profile: Profile) -> Self {
        Self { started: [0; 2], pending: [true, profile == Profile::Independent], profile }
    }
    fn admits(&self, record: &Record) -> bool {
        record.count != 0 && record.count <= 2 && record.members.iter().take(record.count as usize)
            .all(|m| m.phase == 1 && self.started.get(m.attempt as usize) == Some(&0)
                && self.pending.get(m.attempt as usize) == Some(&true))
    }
    fn apply(&mut self, record: &Record) -> Option<u8> {
        // The enclosing transaction preflights every member before this mutation.
        for member in record.members.iter().take(record.count as usize) {
            if !cfg!(application_skip_transition) {
                if let Some(state) = self.started.get_mut(member.attempt as usize) { *state = 1; }
                if let Some(pending) = self.pending.get_mut(member.attempt as usize) { *pending = false; }
            }
        }
        if self.profile == Profile::StartedDependency && self.started[0] == 1 && self.started[1] == 0 && !self.pending[1] {
            self.pending[1] = true;
            Some(1)
        } else { None }
    }
}

pub(super) struct Application<'a> { reservations: Reservations<'a>, policy: Policy }
pub(super) struct Applied<'a> { key: Key<'a> }
#[derive(Debug, PartialEq, Eq)]
pub(super) struct AppliedInspection {
    pub(super) serial: u64, pub(super) journal: u64,
    pub(super) before: [u8; 2], pub(super) after: [u8; 2], pub(super) effects: usize,
}
impl<'a> Application<'a> {
    pub(super) fn new(owner: &'a mut Owner, profile: Profile) -> Self {
        Self { reservations: Reservations::new(owner), policy: Policy::new(profile) }
    }
    pub(super) fn reserve(&mut self, members: &[Member]) -> Result<Key<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        if members.iter().any(|m| self.policy.started.get(m.attempt as usize) != Some(&0)
            || self.policy.pending.get(m.attempt as usize) != Some(&true)) { return Err(Error::Invalid); }
        self.reservations.reserve(members)
    }
    pub(super) fn cancel(&mut self, key: &Key<'_>) -> Result<(), Error> { self.reservations.cancel(key) }
    #[inline(never)]
    pub(super) fn apply(&mut self, key: &Key<'_>) -> Result<Applied<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        let index = self.reservations.index(key)?;
        let record = *self.reservations.storage.records.get(index).ok_or(Error::Invalid)?;
        let own_key = Key { owner: self.reservations.owner, serial: record.serial };
        if record.state == 3 { return Ok(Applied { key: own_key }); }
        if record.state != 1 || self.reservations.storage.active as usize != index + 1 ||
            !self.policy.admits(&record) { return Err(Error::Invalid); }
        let before = self.policy;
        let mut expected = before;
        for member in record.members.iter().take(record.count as usize) {
            *expected.started.get_mut(member.attempt as usize).ok_or(Error::Invalid)? = 1;
            *expected.pending.get_mut(member.attempt as usize).ok_or(Error::Invalid)? = false;
        }
        let obligation = before.profile == Profile::StartedDependency && before.started[0] == 0
            && expected.started[0] == 1 && expected.started[1] == 0;
        if obligation { expected.pending[1] = true; }
        // Unknown is durable in this owner before any policy mutation is attempted.
        let storage = &mut self.reservations.storage;
        storage.closed = 1; storage.active = 0;
        let retained = storage.records.get_mut(index).ok_or(Error::Invalid)?;
        retained.state = 4; retained.before = before.started;
        let generated = self.policy.apply(&record);
        retained.after = self.policy.started;
        if let Some(attempt) = generated {
            if !cfg!(application_drop_capture) {
                let effect = storage.effects.get_mut(0).ok_or(Error::Closed)?;
                // Position-preserving symbols; full occurrence identity, never a hash.
                effect.token = [1, 2, 3, record.journal, 0, 4 + attempt as u64, 1, 6, 7, 1];
                effect.disposition = 1;
                if cfg!(application_corrupt_capture) { effect.token[9] += 1; }
            }
        }
        let expected_token = [1, 2, 3, record.journal, 0, 5, 1, 6, 7, 1];
        let captured = storage.effects.iter().filter(|e| e.disposition != 0).count();
        let complete = captured == usize::from(obligation) && storage.effects.iter().enumerate()
            .all(|(i, e)| if obligation && i == 0 { e.disposition == 1 && e.token.iter().zip(expected_token.iter()).fold(0, |difference, (a, b)| difference | (a ^ b)) == 0 }
                 else { e.disposition == 0 });
        if self.policy != expected || generated != obligation.then_some(1) || !complete {
            if cfg!(application_reopen) { storage.closed = 0; }
            return Err(Error::Closed);
        }
        let retained = storage.records.get_mut(index).ok_or(Error::Closed)?;
        retained.effects = captured as u8; retained.state = 3;
        storage.closed = 0;
        Ok(Applied { key: own_key })
    }
    #[inline(never)]
    pub(super) fn inspect(&self, receipt: &Applied<'_>) -> Result<AppliedInspection, Error> {
        let index = self.reservations.index(&receipt.key)?;
        let record = self.reservations.storage.records.get(index).ok_or(Error::Invalid)?;
        if record.state != 3 { return Err(Error::Invalid); }
        Ok(AppliedInspection { serial: record.serial, journal: record.journal,
            before: record.before, after: record.after,
            effects: if cfg!(retire_forget_count) { self.reservations.storage.effects.iter().filter(|e| e.disposition != 0).count() }
                else { record.effects as usize } })
    }
}

#[cfg(test)]
mod application_tests {
    use super::*;
    const A: Member = Member { attempt: 0, phase: 1 };
    const B: Member = Member { attempt: 1, phase: 1 };
    #[test]
    fn dependency_transition_and_complete_capture() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let key = a.reserve(&[A]).unwrap(); let receipt = a.apply(&key).expect("complete transition and capture required");
        assert_eq!(a.policy.started, [1, 0]); assert_eq!(a.policy.pending, [false, true]);
        assert_eq!(a.inspect(&receipt), Ok(AppliedInspection { serial: 1, journal: 1, before: [0, 0], after: [1, 0], effects: 1 }));
        assert_eq!(a.reservations.storage.effects[0], Effect { token: [1, 2, 3, 1, 0, 5, 1, 6, 7, 1], disposition: 1 });
        assert!(a.reservations.storage.effects[1..].iter().all(|e| e.disposition == 0));
        let storage = a.reservations.storage; let policy = a.policy;
        let replay = a.apply(&key).unwrap(); assert_eq!(a.inspect(&receipt), a.inspect(&replay));
        assert_eq!(a.reservations.storage, storage); assert_eq!(a.policy, policy);
        assert_eq!(a.cancel(&key), Err(Error::Invalid));
        assert!(matches!(a.reserve(&[B]), Err(Error::Full)), "captured effects must block new admission");
    }
    #[test]
    fn empty_effect_cut_still_retains_credits() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::Independent);
        let key = a.reserve(&[A]).unwrap(); let receipt = a.apply(&key).unwrap();
        assert_eq!(a.inspect(&receipt).unwrap().effects, 0);
        assert_eq!(a.policy.started, [1, 0]); assert_eq!(a.reservations.storage.occupied, 20);
        assert!(matches!(a.reserve(&[B]), Err(Error::Full)));
    }
    #[test]
    fn two_members_preflight_and_apply_once() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::Independent);
        let key = a.reserve(&[A, B]).unwrap(); let receipt = a.apply(&key).unwrap();
        assert_eq!(a.inspect(&receipt).unwrap().after, [1, 1]); assert_eq!(a.policy.pending, [false, false]);
        assert_eq!(a.inspect(&receipt).unwrap().effects, 0);
    }
    #[test]
    fn all_member_denial_preserves_policy_and_storage() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let before = a.reservations.storage; let policy = a.policy;
        for members in [&[B][..], &[A, B], &[B, A], &[A, A], &[], &[Member { attempt: 255, phase: 1 }]] {
            assert!(matches!(a.reserve(members), Err(Error::Invalid)));
            assert_eq!(a.reservations.storage, before); assert_eq!(a.policy, policy);
        }
        let key = a.reserve(&[A]).unwrap(); assert_eq!(key.serial, 1);
    }
    #[test]
    fn foreign_and_cancelled_keys_deny() {
        let mut one = Owner::new(); let mut two = Owner::new();
        let mut a = Application::new(&mut one, Profile::Independent);
        let mut b = Application::new(&mut two, Profile::Independent);
        let key = a.reserve(&[A]).unwrap(); let foreign = b.reserve(&[A]).unwrap();
        let before = a.reservations.storage;
        assert!(matches!(a.apply(&foreign), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
        let receipt = b.apply(&foreign).unwrap(); assert_eq!(a.inspect(&receipt), Err(Error::Invalid));
        a.cancel(&key).unwrap(); assert!(matches!(a.apply(&key), Err(Error::Invalid)));
        let next = a.reserve(&[A]).unwrap(); let receipt = a.apply(&next).unwrap();
        assert_eq!(a.inspect(&receipt).unwrap().serial, 2); assert_eq!(a.inspect(&receipt).unwrap().journal, 2);
    }
    #[test]
    fn preflight_revalidates_policy() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::Independent);
        let key = a.reserve(&[A]).unwrap(); a.policy.pending[0] = false;
        let storage = a.reservations.storage; let policy = a.policy;
        assert!(matches!(a.apply(&key), Err(Error::Invalid)));
        assert_eq!(a.reservations.storage, storage); assert_eq!(a.policy, policy);
    }
    #[test]
    fn failed_verification_retains_unknown_and_capture() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let key = a.reserve(&[A]).unwrap();
        // Inject a malformed occupied tail slot before mutation; capture must not erase it.
        a.reservations.storage.effects[19] = Effect { token: [99; 10], disposition: 1 };
        assert!(matches!(a.apply(&key), Err(Error::Closed)));
        assert_eq!(a.policy.started, [1, 0]); assert_eq!(a.state(&key), Ok(ApplicationState::Unknown));
        assert_eq!(a.effect(19), Some(([99; 10], 1))); assert_eq!(a.effect(20), None);
        assert_eq!(a.reservations.storage.effects[0].token, [1, 2, 3, 1, 0, 5, 1, 6, 7, 1]);
        assert_eq!(a.reservations.storage.effects[19].token, [99; 10]);
        assert_eq!(a.reservations.storage.closed, 1, "ambiguous application must stay closed");
        let storage = a.reservations.storage;
        assert!(matches!(a.apply(&key), Err(Error::Closed))); assert_eq!(a.cancel(&key), Err(Error::Closed));
        assert!(matches!(a.reserve(&[B]), Err(Error::Closed))); assert_eq!(a.reservations.storage, storage);
    }
}

#[derive(Debug, PartialEq, Eq)]
pub(super) enum ApplicationState { Reserved, Cancelled, Applied, Unknown }
impl Application<'_> {
    pub(super) fn state(&self, key: &Key<'_>) -> Result<ApplicationState, Error> {
        let index = self.reservations.index(key)?;
        match self.reservations.storage.records.get(index).ok_or(Error::Invalid)?.state {
            1 => Ok(ApplicationState::Reserved), 2 => Ok(ApplicationState::Cancelled),
            3 => Ok(ApplicationState::Applied), 4 => Ok(ApplicationState::Unknown), _ => Err(Error::Invalid),
        }
    }
    // Diagnostic metadata grants no execution/acknowledgment authority.
    pub(super) fn effect(&self, index: usize) -> Option<([u64; 10], u8)> {
        self.reservations.storage.effects.get(index)
            .filter(|effect| effect.disposition != 0).map(|effect| (effect.token, effect.disposition))
    }
}
const _: () = assert!(core::mem::size_of::<Application<'_>>() == 1992);

// Invocation identity refers to the retained occurrence, never an external grant.
pub(super) struct EffectKey<'a> { owner: &'a Owner, index: usize, token: [u64; 10] }
impl<'a> Application<'a> {
    pub(super) fn start_effect(&mut self, index: usize, expected: &[u64; 10]) -> Result<EffectKey<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        let effect = self.reservations.storage.effects.get_mut(index).ok_or(Error::Invalid)?;
        if effect.disposition != 1 || (!(cfg!(effect_skip_token) || cfg!(reclaim_skip_token)) &&
            effect.token.iter().zip(expected.iter()).fold(0, |d, (a, b)| d | (a ^ b)) != 0) {
            return Err(Error::Invalid);
        }
        effect.disposition = 2;
        Ok(EffectKey { owner: self.reservations.owner, index, token: effect.token })
    }
    fn effect_transition(&mut self, key: &EffectKey<'_>, before: u8, after: u8) -> Result<(), Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        if !core::ptr::eq(key.owner, self.reservations.owner) { return Err(Error::Invalid); }
        let effect = self.reservations.storage.effects.get_mut(key.index).ok_or(Error::Invalid)?;
        if effect.token.iter().zip(key.token.iter()).fold(0, |d, (a, b)| d | (a ^ b)) != 0 ||
            (!((cfg!(effect_early_ack) || cfg!(reclaim_early_ack)) && after == 5) && effect.disposition != before) {
            return Err(Error::Invalid);
        }
        effect.disposition = after;
        Ok(())
    }
    pub(super) fn effect_returned(&mut self, key: &EffectKey<'_>) -> Result<(), Error> {
        self.effect_transition(key, 2, 3)
    }
    pub(super) fn effect_applied(&mut self, key: &EffectKey<'_>) -> Result<(), Error> {
        self.effect_transition(key, 3, 4)
    }
    pub(super) fn acknowledge_effect(&mut self, key: &EffectKey<'_>) -> Result<(), Error> {
        self.effect_transition(key, 4, 5)
    }
    pub(super) fn effect_unknown(&mut self, key: &EffectKey<'_>) -> Result<(), Error> {
        let before = self.reservations.storage.effects.get(key.index).ok_or(Error::Invalid)?.disposition;
        if !(2..=4).contains(&before) { return Err(Error::Invalid); }
        self.effect_transition(key, before, 6)?;
        self.reservations.storage.closed = 1;
        Ok(())
    }
}

#[cfg(test)]
mod effect_tests {
    use super::*;
    const A: Member = Member { attempt: 0, phase: 1 };
    const TOKEN: [u64; 10] = [1, 2, 3, 1, 0, 5, 1, 6, 7, 1];
    fn prepared(owner: &mut Owner) -> Application<'_> {
        let mut a = Application::new(owner, Profile::StartedDependency);
        let key = a.reserve(&[A]).unwrap(); a.apply(&key).unwrap(); a
    }
    #[test]
    fn full_token_and_stage_order() {
        let mut owner = Owner::new(); let mut a = prepared(&mut owner);
        let initial = a.reservations.storage;
        for field in 0..10 {
            let mut wrong = TOKEN; wrong[field] += 1;
            assert!(matches!(a.start_effect(0, &wrong), Err(Error::Invalid)), "every occurrence field must match");
            assert_eq!(a.reservations.storage, initial);
        }
        assert!(matches!(a.start_effect(20, &TOKEN), Err(Error::Invalid)));
        let key = a.start_effect(0, &TOKEN).unwrap();
        assert_eq!(a.acknowledge_effect(&key), Err(Error::Invalid), "ack requires an applied return");
        assert_eq!(a.effect_applied(&key), Err(Error::Invalid));
        assert_eq!(a.effect(0), Some((TOKEN, 2)));
        a.effect_returned(&key).unwrap(); assert_eq!(a.acknowledge_effect(&key), Err(Error::Invalid));
        a.effect_applied(&key).unwrap(); a.acknowledge_effect(&key).unwrap();
        let final_storage = a.reservations.storage;
        assert_eq!(a.effect(0), Some((TOKEN, 5)));
        assert!(matches!(a.start_effect(0, &TOKEN), Err(Error::Invalid)));
        assert_eq!(a.acknowledge_effect(&key), Err(Error::Invalid));
        assert_eq!(a.effect_unknown(&key), Err(Error::Invalid));
        assert_eq!(a.reservations.storage, final_storage);
        assert!(matches!(a.reserve(&[Member { attempt: 1, phase: 1 }]), Err(Error::Full)));
    }
    #[test]
    fn foreign_and_altered_keys_preserve_inventory() {
        let mut one = Owner::new(); let mut two = Owner::new();
        let mut a = prepared(&mut one); let mut b = prepared(&mut two);
        let key = a.start_effect(0, &TOKEN).unwrap(); let foreign = b.start_effect(0, &TOKEN).unwrap();
        let before = a.reservations.storage;
        assert!(a.invocation_started(&key, &TOKEN));
        assert!(!a.invocation_started(&foreign, &TOKEN));
        assert!(!b.invocation_started(&key, &TOKEN));
        assert_eq!(a.effect_returned(&foreign), Err(Error::Invalid));
        for field in 0..10 {
            let mut changed = key.token; changed[field] += 1;
            let fake = EffectKey { owner: key.owner, index: key.index, token: changed };
            assert!(!a.invocation_started(&fake, &TOKEN));
            assert!(!a.invocation_started(&key, &changed));
            assert_eq!(a.effect_returned(&fake), Err(Error::Invalid));
        }
        assert_eq!(a.reservations.storage, before);
    }
    #[test]
    fn unknown_closes_and_retains_each_partial_stage() {
        for stage in 2..=4 {
            let mut owner = Owner::new(); let mut a = prepared(&mut owner);
            let key = a.start_effect(0, &TOKEN).unwrap();
            if stage >= 3 { a.effect_returned(&key).unwrap(); }
            if stage >= 4 { a.effect_applied(&key).unwrap(); }
            a.effect_unknown(&key).unwrap();
            assert_eq!(a.effect(0), Some((TOKEN, 6)));
            let before = a.reservations.storage;
            assert!(matches!(a.start_effect(0, &TOKEN), Err(Error::Closed)));
            assert_eq!(a.effect_returned(&key), Err(Error::Closed));
            assert_eq!(a.effect_applied(&key), Err(Error::Closed));
            assert_eq!(a.acknowledge_effect(&key), Err(Error::Closed));
            assert_eq!(a.reservations.storage, before);
        }
    }
}

impl Application<'_> {
    pub(super) fn invocation_started(&self, key: &EffectKey<'_>, expected: &[u64; 10]) -> bool {
        self.reservations.storage.closed == 0 && core::ptr::eq(key.owner, self.reservations.owner) &&
            self.reservations.storage.effects.get(key.index).is_some_and(|effect|
                effect.disposition == 2 && effect.token.iter().zip(key.token.iter()).zip(expected.iter())
                    .fold(0, |d, ((a, b), c)| d | (a ^ b) | (a ^ c)) == 0)
    }
}
const _: () = assert!(core::mem::size_of::<EffectKey<'_>>() == 96);


// Retained metadata is not native authority. The original generated return must
// independently qualify before this occurrence can support a Launched input.
pub(super) struct RetainedEffect<'a> { owner: &'a Owner, token: [u64; 10], serial: u64 }
impl RetainedEffect<'_> {
    pub(super) fn matches(&self, key: &EffectKey<'_>) -> bool {
        core::ptr::eq(self.owner, key.owner) && key.index == 0 &&
            self.token.iter().zip(key.token.iter()).fold(0, |d, (a, b)| d | (a ^ b)) == 0
    }
}
impl<'a> Application<'a> {
    pub(super) fn retained_by(&self, retained: &RetainedEffect<'_>, key: &EffectKey<'_>) -> bool {
        core::ptr::eq(retained.owner, self.reservations.owner) && retained.matches(key)
    }
    fn retirement_index(&self, receipt: &Applied<'_>, effects: u8) -> Result<usize, Error> {
        let storage = &self.reservations.storage;
        if storage.closed != 0 { return Err(Error::Closed); }
        let index = self.reservations.index(&receipt.key)?;
        let record = storage.records.get(index).ok_or(Error::Invalid)?;
        if storage.active != 0 || storage.occupied != 20 || index + 1 != storage.used as usize ||
            record.state != 3 || record.retired != 0 || record.effects != effects { return Err(Error::Invalid); }
        Ok(index)
    }
    #[inline(never)]
    pub(super) fn retire_effect(&mut self, receipt: &Applied<'_>, key: &EffectKey<'_>,
        output: &mut Option<RetainedEffect<'a>>) -> Result<(), Error> {
        let index = self.retirement_index(receipt, 1)?;
        let storage = &mut self.reservations.storage;
        let record = storage.records.get_mut(index).ok_or(Error::Invalid)?;
        let effect = &storage.effects[0];
        if output.is_some() || !core::ptr::eq(key.owner, self.reservations.owner) || key.index != 0 ||
            (!cfg!(retire_skip_ack) && effect.disposition != 5) ||
            effect.token.iter().zip(key.token.iter()).fold(0, |d, (a, b)| d | (a ^ b)) != 0 ||
            effect.token[3] != record.journal ||
            storage.effects[1..].iter().any(|e| e.disposition != 0) { return Err(Error::Invalid); }
        if !cfg!(retire_skip_retain) {
            *output = Some(RetainedEffect { owner: self.reservations.owner, token: effect.token,
                serial: record.serial });
        }
        if !output.as_ref().is_some_and(|r| r.matches(key) && r.serial == record.serial) {
            storage.closed = 1; return Err(Error::Closed);
        }
        // Retention above precedes the only capacity-release mutation.
        record.retired = 1;
        storage.effects[0].disposition = 0;
        storage.occupied = 0;
        Ok(())
    }
    pub(super) fn retire_empty(&mut self, receipt: &Applied<'_>) -> Result<(), Error> {
        let index = self.retirement_index(receipt, 0)?;
        let storage = &mut self.reservations.storage;
        let record = storage.records.get_mut(index).ok_or(Error::Invalid)?;
        if storage.effects.iter().any(|e| e.disposition != 0) { return Err(Error::Invalid); }
        record.retired = 1; storage.occupied = 0;
        Ok(())
    }
}

#[cfg(test)]
mod retirement_tests {
    use super::*;
    const A: Member = Member { attempt: 0, phase: 1 };
    const B: Member = Member { attempt: 1, phase: 1 };
    const TOKEN: [u64; 10] = [1, 2, 3, 1, 0, 5, 1, 6, 7, 1];
    #[test]
    fn retain_before_release_and_apply_dependent_once() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let first = a.reserve(&[A]).unwrap(); let receipt = a.apply(&first).unwrap();
        let original = a.inspect(&receipt).unwrap();
        let key = a.start_effect(0, &TOKEN).unwrap();
        a.effect_returned(&key).unwrap(); a.effect_applied(&key).unwrap(); a.acknowledge_effect(&key).unwrap();
        let mut retained = None;
        assert_eq!(a.retire_effect(&receipt, &key, &mut retained), Ok(()), "retention must precede release");
        assert!(retained.as_ref().unwrap().matches(&key));
        assert_eq!(a.inspect(&receipt).unwrap(), original, "historical count must survive retirement");
        assert_eq!(a.acknowledge_effect(&key), Err(Error::Invalid));
        assert!(matches!(a.start_effect(0, &TOKEN), Err(Error::Invalid)));
        assert_eq!(a.retire_effect(&receipt, &key, &mut None), Err(Error::Invalid));
        let second = a.reserve(&[B]).unwrap(); let dependent = a.apply(&second).unwrap();
        assert_eq!(a.inspect(&dependent), Ok(AppliedInspection { serial: 2, journal: 2,
            before: [1, 0], after: [1, 1], effects: 0 }));
        assert_eq!(a.policy.pending, [false, false]); assert_eq!(a.effect(0), None);
        let before = a.reservations.storage;
        assert_eq!(a.retire_effect(&receipt, &key, &mut None), Err(Error::Invalid));
        assert_eq!(a.retire_empty(&receipt), Err(Error::Invalid)); assert_eq!(a.reservations.storage, before);
        a.retire_empty(&dependent).unwrap(); assert_eq!(a.reservations.storage.occupied, 0);
        assert_eq!(a.retire_empty(&dependent), Err(Error::Invalid));
        let replay = a.apply(&first).unwrap(); assert_eq!(a.inspect(&replay).unwrap(), original);
        assert_eq!(a.inspect(&receipt).unwrap(), original);
        assert_eq!(a.reservations.inspect(&first).unwrap().members[0], A);
        assert_eq!(a.reservations.inspect(&second).unwrap().members[0], B);
        assert!(retained.unwrap().matches(&key));
    }
    #[test]
    fn retirement_requires_ack_and_exact_owner_occurrence() {
        let mut owner = Owner::new(); let mut foreign_owner = Owner::new();
        let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let mut b = Application::new(&mut foreign_owner, Profile::StartedDependency);
        let first = a.reserve(&[A]).unwrap(); let receipt = a.apply(&first).unwrap();
        let other = b.reserve(&[A]).unwrap(); let foreign_receipt = b.apply(&other).unwrap();
        let foreign = b.start_effect(0, &TOKEN).unwrap();
        let key = a.start_effect(0, &TOKEN).unwrap();
        for stage in 2..=4 {
            let before = a.reservations.storage;
            assert_eq!(a.retire_effect(&receipt, &key, &mut None), Err(Error::Invalid), "retirement requires acknowledgment");
            assert_eq!(a.reservations.storage, before);
            if stage == 2 { a.effect_returned(&key).unwrap(); }
            if stage == 3 { a.effect_applied(&key).unwrap(); }
        }
        a.acknowledge_effect(&key).unwrap(); let before = a.reservations.storage;
        assert_eq!(a.retire_effect(&foreign_receipt, &key, &mut None), Err(Error::Invalid));
        assert_eq!(a.retire_effect(&receipt, &foreign, &mut None), Err(Error::Invalid));
        for field in 0..10 {
            let mut token = TOKEN; token[field] += 1;
            let fake = EffectKey { owner: key.owner, index: 0, token };
            assert_eq!(a.retire_effect(&receipt, &fake, &mut None), Err(Error::Invalid));
        }
        let fake = EffectKey { owner: key.owner, index: 1, token: TOKEN };
        assert_eq!(a.retire_effect(&receipt, &fake, &mut None), Err(Error::Invalid));
        assert_eq!(a.reservations.storage, before);
        let mut existing = Some(RetainedEffect { owner: foreign.owner, token: TOKEN, serial: 1 });
        assert!(!a.retained_by(existing.as_ref().unwrap(), &foreign));
        assert_eq!(a.retire_effect(&receipt, &key, &mut existing), Err(Error::Invalid));
        assert!(existing.as_ref().unwrap().matches(&foreign));
        assert_eq!(a.reservations.storage, before);
        a.reservations.storage.effects[19].disposition = 1; let before = a.reservations.storage;
        assert_eq!(a.retire_effect(&receipt, &key, &mut None), Err(Error::Invalid));
        assert_eq!(a.reservations.storage, before);
    }
    #[test]
    fn closed_unknown_preserves_effect() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let first = a.reserve(&[A]).unwrap(); let receipt = a.apply(&first).unwrap();
        let key = a.start_effect(0, &TOKEN).unwrap(); a.effect_unknown(&key).unwrap();
        let before = a.reservations.storage;
        assert_eq!(a.retire_effect(&receipt, &key, &mut None), Err(Error::Closed));
        assert_eq!(a.retire_empty(&receipt), Err(Error::Closed)); assert_eq!(a.reservations.storage, before);
    }
}


impl<'a> Application<'a> {
    fn terminal_admits(&self, members: &[Member]) -> bool {
        self.policy.profile == Profile::StartedDependency && members.len() == 1 &&
            self.policy.started.iter().all(|phase| matches!(phase, 1 | 2 | 3)) &&
            members.iter().all(|m| m.phase == 2 && self.policy.started.get(m.attempt as usize) == Some(&1))
    }
    pub(super) fn reserve_terminal(&mut self, members: &[Member]) -> Result<Key<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        if !self.terminal_admits(members) { return Err(Error::Invalid); }
        self.reservations.reserve_phase::<2>(members)
    }
    #[inline(never)]
    pub(super) fn apply_terminal(&mut self, key: &Key<'_>) -> Result<Applied<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        let index = self.reservations.index(key)?;
        let record = *self.reservations.storage.records.get(index).ok_or(Error::Invalid)?;
        if record.count != 1 || record.members[0].phase != 2 { return Err(Error::Invalid); }
        let own_key = Key { owner: self.reservations.owner, serial: record.serial };
        if record.state == 3 { return Ok(Applied { key: own_key }); }
        if record.state != 1 || self.reservations.storage.active as usize != index + 1 ||
            !self.terminal_admits(&record.members[..1]) { return Err(Error::Invalid); }
        let before = self.policy.started;
        let attempt = record.members[0].attempt as usize;
        let mut expected = before;
        *expected.get_mut(attempt).ok_or(Error::Invalid)? = 2;
        let expected_token = [1, 2, 3, record.journal, 0, 4 + attempt as u64, 1, 8, 7, 1];
        let storage = &mut self.reservations.storage;
        storage.closed = 1; storage.active = 0;
        let retained = storage.records.get_mut(index).ok_or(Error::Closed)?;
        retained.state = 4; retained.before = before;
        if !cfg!(terminal_skip_transition) {
            *self.policy.started.get_mut(attempt).ok_or(Error::Closed)? = 2;
        }
        retained.after = self.policy.started;
        if !cfg!(terminal_drop_capture) {
            // Actual capture is independent of the expected token above.
            storage.effects[0] = Effect { token: [1, 2, 3, record.journal, 0,
                4 + record.members[0].attempt as u64, 1, 8, 7, 1], disposition: 1 };
            if cfg!(terminal_corrupt_capture) { storage.effects[0].token[7] = 6; }
        }
        let complete = storage.effects.iter().enumerate().all(|(i, effect)|
            if i == 0 { effect.disposition == 1 && effect.token.iter().zip(expected_token.iter())
                .fold(0, |d, (a, b)| d | (a ^ b)) == 0 } else { effect.disposition == 0 });
        if self.policy.started != expected || !complete {
            if cfg!(terminal_reopen) { storage.closed = 0; }
            return Err(Error::Closed);
        }
        retained.effects = 1; retained.state = 3; storage.closed = 0;
        Ok(Applied { key: own_key })
    }
}

#[cfg(test)]
mod terminal_application_tests {
    use super::*;
    const A: Member = Member { attempt: 0, phase: 1 };
    const B: Member = Member { attempt: 1, phase: 1 };
    const TA: Member = Member { attempt: 0, phase: 2 };
    const TB: Member = Member { attempt: 1, phase: 2 };
    fn acknowledge_and_retire<'a>(a: &mut Application<'a>, receipt: &Applied<'_>) -> RetainedEffect<'a> {
        let token = a.effect(0).unwrap().0;
        let key = a.start_effect(0, &token).unwrap();
        a.effect_returned(&key).unwrap(); a.effect_applied(&key).unwrap(); a.acknowledge_effect(&key).unwrap();
        let mut retained = None; a.retire_effect(receipt, &key, &mut retained).unwrap(); retained.unwrap()
    }
    fn launched(a: &mut Application<'_>) {
        let key = a.reserve(&[A]).unwrap(); let receipt = a.apply(&key).unwrap();
        let _retained = acknowledge_and_retire(a, &receipt);
        let key = a.reserve(&[B]).unwrap(); let receipt = a.apply(&key).unwrap(); a.retire_empty(&receipt).unwrap();
    }
    #[test]
    fn each_terminal_order_captures_exact_reclaim_once() {
        for order in [[TA, TB], [TB, TA]] {
            let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
            launched(&mut a); let launch_records = a.reservations.storage.records;
            let mut expected = [1, 1];
            for (position, member) in order.iter().enumerate() {
                let key = a.reserve_terminal(&[*member]).unwrap();
                let storage = a.reservations.storage;
                assert!(matches!(a.apply(&key), Err(Error::Invalid)));
                assert_eq!(a.reservations.storage, storage);
                let receipt = a.apply_terminal(&key).expect("terminal transition and reclaim capture required");
                let before = expected; expected[member.attempt as usize] = 2;
                let inspected = AppliedInspection { serial: 3 + position as u64, journal: 3 + position as u64,
                    before, after: expected, effects: 1 };
                assert_eq!(a.inspect(&receipt), Ok(inspected));
                assert_eq!(a.effect(0), Some(([1, 2, 3, 3 + position as u64, 0,
                    4 + member.attempt as u64, 1, 8, 7, 1], 1)));
                assert!(a.reservations.storage.effects[1..].iter().all(|e| e.disposition == 0));
                assert_eq!(a.policy.pending, [false, false]);
                let storage = a.reservations.storage;
                let replay = a.apply_terminal(&key).unwrap(); assert_eq!(a.inspect(&replay), a.inspect(&receipt));
                assert_eq!(a.reservations.storage, storage);
                assert!(matches!(a.reserve_terminal(&[*member]), Err(Error::Invalid)));
                assert_eq!(a.cancel(&key), Err(Error::Invalid));
                let _retained = acknowledge_and_retire(&mut a, &receipt);
                assert_eq!(a.inspect(&receipt).unwrap().effects, 1);
            }
            assert_eq!(a.policy.started, [2, 2]); assert_eq!(a.reservations.storage.used, 4);
            assert_eq!(&a.reservations.storage.records[..2], &launch_records[..2]);
        }
    }
    #[test]
    fn early_foreign_cancelled_and_invalid_members_deny_atomically() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        let initial = a.reservations.storage;
        assert!(matches!(a.reserve_terminal(&[TA]), Err(Error::Invalid))); assert_eq!(a.reservations.storage, initial);
        let key = a.reserve(&[A]).unwrap(); let receipt = a.apply(&key).unwrap();
        let _retained = acknowledge_and_retire(&mut a, &receipt); let before = a.reservations.storage;
        assert!(matches!(a.reserve_terminal(&[TA]), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
        let key = a.reserve(&[B]).unwrap(); let receipt = a.apply(&key).unwrap(); a.retire_empty(&receipt).unwrap();
        let before = a.reservations.storage;
        for members in [&[][..], &[A], &[TA, TB], &[TB, TA], &[TA, TA], &[Member { attempt: 2, phase: 2 }], &[Member { attempt: 0, phase: 3 }]] {
            assert!(matches!(a.reserve_terminal(members), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
        }
        assert!(matches!(a.apply_terminal(&key), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
        let mut foreign_owner = Owner::new(); let mut foreign = Application::new(&mut foreign_owner, Profile::StartedDependency);
        launched(&mut foreign); let foreign_key = foreign.reserve_terminal(&[TA]).unwrap();
        assert!(matches!(a.apply_terminal(&foreign_key), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
        let key = a.reserve_terminal(&[TA]).unwrap(); a.cancel(&key).unwrap(); let before = a.reservations.storage;
        assert!(matches!(a.apply_terminal(&key), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
        assert_eq!(a.reserve_terminal(&[TA]).unwrap().serial, 4);
    }
    #[test]
    fn terminal_preflight_rechecks_policy_and_capacity() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        launched(&mut a); let key = a.reserve_terminal(&[TA]).unwrap();
        assert!(matches!(a.reserve_terminal(&[TB]), Err(Error::Busy)));
        assert_eq!(a.reserve_terminal(&[TA]).unwrap().serial, key.serial);
        a.policy.started[0] = 2; let before = a.reservations.storage;
        assert!(matches!(a.apply_terminal(&key), Err(Error::Invalid))); assert_eq!(a.reservations.storage, before);
    }
    #[test]
    fn ambiguous_terminal_preserves_actual_state_and_effect_inventory() {
        let mut owner = Owner::new(); let mut a = Application::new(&mut owner, Profile::StartedDependency);
        launched(&mut a); let key = a.reserve_terminal(&[TA]).unwrap();
        a.reservations.storage.effects[19] = Effect { token: [99; 10], disposition: 1 };
        assert!(matches!(a.apply_terminal(&key), Err(Error::Closed)));
        assert_eq!(a.policy.started, [2, 1]); assert_eq!(a.state(&key), Ok(ApplicationState::Unknown));
        assert_eq!(a.effect(0), Some(([1, 2, 3, 3, 0, 4, 1, 8, 7, 1], 1)));
        assert_eq!(a.effect(19), Some(([99; 10], 1)));
        assert_eq!(a.reservations.storage.closed, 1, "ambiguous terminal must stay closed");
        let before = a.reservations.storage;
        assert!(matches!(a.apply_terminal(&key), Err(Error::Closed)));
        assert!(matches!(a.reserve_terminal(&[TB]), Err(Error::Closed))); assert_eq!(a.cancel(&key), Err(Error::Closed));
        assert_eq!(a.reservations.storage, before);
    }
}

impl<'a> Application<'a> {
    pub(super) fn completed_effect(&self, index: usize, expected: &[u64; 10]) -> Result<EffectKey<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        let effect = self.reservations.storage.effects.get(index).ok_or(Error::Invalid)?;
        if effect.disposition != 5 || effect.token != *expected { return Err(Error::Invalid); }
        Ok(EffectKey { owner: self.reservations.owner, index, token: effect.token })
    }
    fn cleaned_source(&self, member: Member, retained: &RetainedEffect<'_>, effect: &EffectKey<'_>) -> bool {
        self.retained_by(retained, effect) && member.attempt < 2 && member.phase == 3 &&
            retained.token[5] == 4 + member.attempt as u64 && retained.token[7] == 8 &&
            self.reservations.storage.records.iter().any(|r| r.serial == retained.serial && r.state == 3 && r.retired == 1 &&
                r.count == 1 && r.members[0] == (Member { attempt: member.attempt, phase: 2 }) &&
                r.journal == retained.token[3] && r.effects == 1)
    }
    pub(super) fn reserve_cleaned(&mut self, member: Member, retained: &RetainedEffect<'_>, effect: &EffectKey<'_>) -> Result<Key<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        if !self.cleaned_source(member, retained, effect) || self.policy.started[member.attempt as usize] != 2 { return Err(Error::Invalid); }
        self.reservations.reserve_phase::<3>(&[member])
    }
    #[inline(never)]
    pub(super) fn apply_cleaned(&mut self, key: &Key<'_>, retained: &RetainedEffect<'_>, effect: &EffectKey<'_>) -> Result<Applied<'a>, Error> {
        if self.reservations.storage.closed != 0 { return Err(Error::Closed); }
        let index = self.reservations.index(key)?;
        let record = self.reservations.storage.records[index];
        if record.count != 1 || !self.cleaned_source(record.members[0], retained, effect) { return Err(Error::Invalid); }
        let own_key = Key { owner: self.reservations.owner, serial: record.serial };
        if record.state == 3 { return Ok(Applied { key: own_key }); }
        let attempt = record.members[0].attempt as usize;
        if record.state != 1 || self.reservations.storage.active as usize != index + 1 || self.policy.started[attempt] != 2 { return Err(Error::Invalid); }
        let before = self.policy.started; let mut expected = before; expected[attempt] = 3;
        let storage = &mut self.reservations.storage; storage.closed = 1; storage.active = 0;
        let r = &mut storage.records[index]; r.state = 4; r.before = before;
        if !cfg!(cleaned_skip_transition) { self.policy.started[attempt] = 3; }
        r.after = self.policy.started;
        if self.policy.started != expected || storage.effects.iter().any(|e| e.disposition != 0) { return Err(Error::Closed); }
        r.effects = 0; r.state = 3; storage.closed = 0;
        Ok(Applied { key: own_key })
    }
}

#[cfg(test)]
mod cleaned_tests {
    use super::*;
    fn prepared(owner: &mut Owner) -> Application<'_> {
        let mut a = Application::new(owner, Profile::StartedDependency);
        let key = a.reserve(&[Member { attempt: 0, phase: 1 }]).unwrap(); let receipt = a.apply(&key).unwrap();
        let token = a.effect(0).unwrap().0; let effect = a.start_effect(0, &token).unwrap();
        a.effect_returned(&effect).unwrap(); a.effect_applied(&effect).unwrap(); a.acknowledge_effect(&effect).unwrap();
        let mut retired = None; a.retire_effect(&receipt, &effect, &mut retired).unwrap();
        let key = a.reserve(&[Member { attempt: 1, phase: 1 }]).unwrap(); let receipt = a.apply(&key).unwrap(); a.retire_empty(&receipt).unwrap(); a
    }
    fn reclaimed<'a>(a: &mut Application<'a>) -> (Applied<'a>, EffectKey<'a>, RetainedEffect<'a>) {
        let key = a.reserve_terminal(&[Member { attempt: 1, phase: 2 }]).unwrap(); let terminal = a.apply_terminal(&key).unwrap();
        let token = a.effect(0).unwrap().0; let effect = a.start_effect(0, &token).unwrap();
        a.effect_returned(&effect).unwrap(); a.effect_applied(&effect).unwrap(); a.acknowledge_effect(&effect).unwrap();
        let mut retained = None; a.retire_effect(&terminal, &effect, &mut retained).unwrap(); (terminal, effect, retained.unwrap())
    }
    #[test]
    fn both_services_complete_six_cuts_without_erasing_history() {
        let mut owner = Owner::new(); let mut a = prepared(&mut owner);
        for attempt in [1, 0] {
            let key = a.reserve_terminal(&[Member { attempt, phase: 2 }]).expect("Launched peer may finish after Cleaned");
            let terminal = a.apply_terminal(&key).unwrap();
            let token = a.effect(0).unwrap().0; let effect = a.start_effect(0, &token).unwrap();
            a.effect_returned(&effect).unwrap(); a.effect_applied(&effect).unwrap(); a.acknowledge_effect(&effect).unwrap();
            let mut retained = None; a.retire_effect(&terminal, &effect, &mut retained).unwrap(); let retained = retained.unwrap();
            let key = a.reserve_cleaned(Member { attempt, phase: 3 }, &retained, &effect).unwrap();
            let cleaned = a.apply_cleaned(&key, &retained, &effect).unwrap(); a.retire_empty(&cleaned).unwrap();
        }
        assert_eq!(a.policy.started, [3, 3]); assert_eq!(a.reservations.storage.used, 6);
        let expected = [([0, 0], [1, 0], 1), ([1, 0], [1, 1], 0), ([1, 1], [1, 2], 1),
                        ([1, 2], [1, 3], 0), ([1, 3], [2, 3], 1), ([2, 3], [3, 3], 0)];
        for (index, (before, after, effects)) in expected.into_iter().enumerate() {
            let r = a.reservations.storage.records[index];
            assert_eq!((r.serial, r.journal), ((index + 1) as u64, (index + 1) as u64));
            assert_eq!((r.before, r.after, r.effects, r.state, r.retired), (before, after, effects, 3, 1));
        }
        let before = a.reservations.storage;
        assert!(matches!(a.reserve_terminal(&[Member { attempt: 0, phase: 2 }]), Err(Error::Invalid)));
        assert_eq!(a.reservations.storage, before);
        assert!(matches!(a.reservations.reserve(&[Member { attempt: 0, phase: 1 }]), Err(Error::Full)));
    }
    #[test]
    fn foreign_and_wrong_cleaned_sources_deny_without_mutation() {
        let mut owner = Owner::new(); let mut a = prepared(&mut owner);
        let (_, effect, retained) = reclaimed(&mut a); let before = a.reservations.storage;
        let foreign_owner = Owner::new(); let foreign = EffectKey { owner: &foreign_owner, index: 0, token: effect.token };
        assert!(matches!(a.reserve_cleaned(Member { attempt: 1, phase: 3 }, &retained, &foreign), Err(Error::Invalid)));
        for member in [Member { attempt: 2, phase: 3 }, Member { attempt: 1, phase: 2 }, Member { attempt: 0, phase: 3 }] {
            assert!(matches!(a.reserve_cleaned(member, &retained, &effect), Err(Error::Invalid)));
        }
        assert_eq!(a.reservations.storage, before);
    }
    #[test]
    fn ambiguous_cleaned_preserves_unknown_and_actual_inventory() {
        let mut owner = Owner::new(); let mut a = prepared(&mut owner);
        let (_, effect, retained) = reclaimed(&mut a);
        let key = a.reserve_cleaned(Member { attempt: 1, phase: 3 }, &retained, &effect).unwrap();
        a.reservations.storage.effects[19] = Effect { token: [99; 10], disposition: 1 };
        assert!(matches!(a.apply_cleaned(&key, &retained, &effect), Err(Error::Closed)));
        assert_eq!(a.state(&key), Ok(ApplicationState::Unknown)); assert_eq!(a.policy.started, [1, 3]);
        assert_eq!(a.effect(19), Some(([99; 10], 1))); let before = a.reservations.storage;
        assert!(matches!(a.apply_cleaned(&key, &retained, &effect), Err(Error::Closed)));
        assert_eq!(a.reservations.storage, before);
    }
    #[test]
    fn cleaned_requires_acknowledged_retired_reclaim_and_replays() {
        let mut owner = Owner::new(); let mut a = prepared(&mut owner);
        let key = a.reserve_terminal(&[Member { attempt: 1, phase: 2 }]).unwrap(); let terminal = a.apply_terminal(&key).unwrap();
        let token = a.effect(0).unwrap().0;
        assert!(matches!(a.completed_effect(0, &token), Err(Error::Invalid)));
        let effect = a.start_effect(0, &token).unwrap(); a.effect_returned(&effect).unwrap(); a.effect_applied(&effect).unwrap();
        assert!(matches!(a.completed_effect(0, &token), Err(Error::Invalid)));
        a.acknowledge_effect(&effect).unwrap(); let effect = a.completed_effect(0, &token).unwrap();
        let mut retained = None; a.retire_effect(&terminal, &effect, &mut retained).unwrap(); let retained = retained.unwrap();
        let before = a.reservations.storage;
        assert!(matches!(a.reserve_cleaned(Member { attempt: 0, phase: 3 }, &retained, &effect), Err(Error::Invalid)));
        assert_eq!(a.reservations.storage, before);
        let key = a.reserve_cleaned(Member { attempt: 1, phase: 3 }, &retained, &effect).unwrap();
        let result = a.apply_cleaned(&key, &retained, &effect).expect("Cleaned must apply after acknowledged reclaim");
        assert_eq!(a.inspect(&result).unwrap().after, [1, 3]); assert!(a.effect(0).is_none());
        let before = a.reservations.storage; assert!(a.apply_cleaned(&key, &retained, &effect).is_ok()); assert_eq!(a.reservations.storage, before);
        assert_eq!(a.inspect(&terminal).unwrap().after, [1, 2]);
    }
}
