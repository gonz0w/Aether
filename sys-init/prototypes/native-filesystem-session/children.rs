// SPDX-License-Identifier: BSD-2-Clause
//! Three ABI29 session child records. The dispatcher supplies authenticated native
//! admission/terminal observations and owns transport, holders and reclamation.
//! PID is a selector within these records, never native authority.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Identity {
    pub slot: usize,
    pub generation: u32,
    pub handle: u64,
    pub pid: i32,
}

impl Identity {
    pub fn admitted(slot: usize, generation: u32, handle: u64) -> Result<Self, i32> {
        if !(2..=4).contains(&slot) || !(1..=15).contains(&generation) {
            return Err(-22);
        }
        if handle != 0xb0000000 | ((generation as u64) << 8) | (slot as u64 + 1) {
            return Err(-9);
        }
        Ok(Self {
            slot,
            generation,
            handle,
            pid: generation as i32 * 7 + slot as i32 + 1,
        })
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum State {
    Empty,
    Running,
    Terminal(i32),
    Reserved(i32),
    Collected,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Child {
    identity: Option<Identity>,
    last_generation: u32,
    state: State,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Wait {
    Pending,
    NoChange,
    NoChild,
    Ready { identity: Identity, status: i32 },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Children {
    records: [Child; 3],
}

impl Default for Children {
    fn default() -> Self {
        Self::new()
    }
}

impl Children {
    pub const fn new() -> Self {
        Self {
            records: [Child {
                identity: None,
                last_generation: 0,
                state: State::Empty,
            }; 3],
        }
    }

    /// Only after native copy returned this exact canonical handle.
    pub fn admit(&mut self, identity: Identity) -> Result<(), i32> {
        Identity::admitted(identity.slot, identity.generation, identity.handle).and_then(
            |canonical| {
                if canonical == identity {
                    Ok(())
                } else {
                    Err(-9)
                }
            },
        )?;
        let child = &mut self.records[identity.slot - 2];
        if child.state != State::Empty || identity.generation != child.last_generation + 1 {
            return Err(-16);
        }
        child.identity = Some(identity);
        child.last_generation = identity.generation;
        child.state = State::Running;
        Ok(())
    }

    fn exact(&mut self, identity: Identity) -> Result<&mut Child, i32> {
        if !(2..=4).contains(&identity.slot) {
            return Err(-9);
        }
        let child = &mut self.records[identity.slot - 2];
        if child.identity != Some(identity) {
            return Err(-9);
        }
        Ok(child)
    }

    /// `status` is already translated from an observed native terminal record.
    /// Normal exit occupies the upper byte; a supported signal the low seven bits.
    pub fn terminal(&mut self, identity: Identity, status: i32) -> Result<(), i32> {
        if !(0..=0xff7f).contains(&status) || (status & 0xff != 0 && status & !0x7f != 0) {
            return Err(-22);
        }
        let child = self.exact(identity)?;
        if child.state != State::Running {
            return Err(-16);
        }
        child.state = State::Terminal(status);
        Ok(())
    }

    /// Closed selected parent/helper flags. Stop/continue bits are accepted but
    /// this profile has no such events; status still comes only from terminal().
    pub fn wait_flags(&mut self, pid: i32, flags: u32) -> Result<Wait, i32> {
        if flags & !11 != 0 { return Err(-22); }
        self.wait(pid, flags & 1 != 0)
    }
    pub fn reclaimed_exact(&self, identity: Identity) -> bool {
        if identity.slot != 2 { return false; }
        let child = &self.records[0];
        child.identity.is_none() && child.state == State::Empty
            && child.last_generation == identity.generation
    }
    /// At most one parent wait reply is outstanding on its authenticated channel.
    /// The dispatcher retries its cached reply until delivery is confirmed; a new
    /// wait call while that reservation exists is rejected.
    pub fn wait(&mut self, pid: i32, nohang: bool) -> Result<Wait, i32> {
        if pid != -1 && pid <= 0 {
            return Err(-22);
        }
        if self
            .records
            .iter()
            .any(|c| matches!(c.state, State::Reserved(_)))
        {
            return Err(-16);
        }
        let mut live = false;
        for child in &mut self.records {
            let Some(identity) = child.identity else {
                continue;
            };
            if pid != -1 && pid != identity.pid {
                continue;
            }
            match child.state {
                State::Running => live = true,
                State::Terminal(status) => {
                    child.state = State::Reserved(status);
                    return Ok(Wait::Ready { identity, status });
                }
                _ => (),
            }
        }
        Ok(if !live {
            Wait::NoChild
        } else if nohang {
            Wait::NoChange
        } else {
            Wait::Pending
        })
    }

    /// The caller retains the entire reply while transport delivery is partial.
    pub fn delivered(&mut self, identity: Identity) -> Result<(), i32> {
        let child = self.exact(identity)?;
        if !matches!(child.state, State::Reserved(_)) {
            return Err(-16);
        }
        child.state = State::Collected;
        Ok(())
    }

    /// Also used if the parent is confirmed terminal before consuming its reply.
    /// This is owner cleanup, not a successful wait delivery to the dead parent.
    pub fn abandon_after_parent_terminal(&mut self, identity: Identity) -> Result<(), i32> {
        let child = self.exact(identity)?;
        if !matches!(child.state, State::Terminal(_) | State::Reserved(_)) {
            return Err(-16);
        }
        child.state = State::Collected;
        Ok(())
    }

    /// Only after holder/transport disposal and native reclaim have completed.
    pub fn reclaimed(&mut self, identity: Identity) -> Result<(), i32> {
        let child = self.exact(identity)?;
        if child.state != State::Collected {
            return Err(-16);
        }
        child.identity = None;
        child.state = State::Empty;
        Ok(())
    }
}

/// Input ownership is independent of wait eligibility. A terminal child keeps
/// the lease through known wait delivery and native/transport/ref settlement.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum ReadLease {
    #[default]
    Parent,
    Child(Identity),
    Contained,
}
impl ReadLease {
    pub fn give_child(&mut self, identity: Identity, parent_read_pending: bool) -> Result<(), i32> {
        Identity::admitted(identity.slot, identity.generation, identity.handle)?;
        if *self != Self::Parent || identity.slot != 2 || parent_read_pending { return Err(-16); }
        *self = Self::Child(identity); Ok(())
    }
    pub fn restore_parent(&mut self, identity: Identity, children: &Children) -> Result<(), i32> {
        if *self != Self::Child(identity) || !children.reclaimed_exact(identity) { return Err(-16); }
        *self = Self::Parent; Ok(())
    }
    pub fn child_read(&self, identity: Identity, canonical: bool, isig: bool) -> Result<(), i32> {
        if *self != Self::Child(identity) { return Err(-13); }
        if canonical || isig { return Err(-95); }
        Ok(())
    }
    pub fn contain(&mut self) { *self = Self::Contained; }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn id(slot: usize, generation: u32) -> Identity {
        Identity::admitted(
            slot,
            generation,
            0xb0000000 | ((generation as u64) << 8) | (slot as u64 + 1),
        )
        .unwrap()
    }

    #[test]
    fn seven_domain_pid_selectors_require_actual_membership() {
        for generation in 1..=15 {
            for slot in 2..=4 {
                assert_eq!(
                    id(slot, generation).pid,
                    generation as i32 * 7 + slot as i32 + 1
                );
            }
        }
        let mut children = Children::new();
        let child = id(2, 1);
        assert_eq!(child.pid, 10);
        children.admit(child).unwrap();
        assert_eq!(children.wait(9, false), Ok(Wait::NoChild));
        assert_eq!(children.wait(10, true), Ok(Wait::NoChange));
        assert_eq!(children.wait(11, true), Ok(Wait::NoChild));
    }

    #[test]
    fn repeated_jobs_preserve_child_identity_and_delivery_barriers() {
        let mut children = Children::new();
        for generation in 1..=15 {
            let current = id(2, generation);
            children.admit(current).unwrap();
            assert_eq!(children.wait(-1, false), Ok(Wait::Pending));
            assert_eq!(children.wait(-1, true), Ok(Wait::NoChange));
            let before = children.clone();
            for old in 1..generation {
                let old = id(2, old);
                assert_eq!(children.wait(old.pid, false), Ok(Wait::NoChild));
                assert_eq!(children.terminal(old, 0), Err(-9));
                assert_eq!(children.delivered(old), Err(-9));
                assert_eq!(children.reclaimed(old), Err(-9));
            }
            assert_eq!(children, before);
            assert_eq!(children.reclaimed(current), Err(-16));
            children.terminal(current, 42 << 8).unwrap();
            assert_eq!(
                children.wait(current.pid, false),
                Ok(Wait::Ready {
                    identity: current,
                    status: 42 << 8
                })
            );
            let before = children.clone();
            assert_eq!(children.wait(-1, false), Err(-16));
            assert_eq!(children.reclaimed(current), Err(-16));
            assert_eq!(children.admit(current), Err(-16));
            assert_eq!(children, before);
            children.delivered(current).unwrap();
            assert_eq!(children.wait(current.pid, false), Ok(Wait::NoChild));
            assert_eq!(children.delivered(current), Err(-16));
            children.reclaimed(current).unwrap();
            assert_eq!(children.admit(current), Err(-16));
        }
        assert_eq!(Identity::admitted(2, 16, 0xb0001003), Err(-22));
    }

    #[test]
    fn waits_do_not_consume_other_children_or_fabricate_completion() {
        let mut children = Children::new();
        let first = id(2, 1);
        let second = id(3, 1);
        children.admit(first).unwrap();
        children.admit(second).unwrap();
        children.terminal(second, 15).unwrap();
        assert_eq!(children.wait(first.pid, true), Ok(Wait::NoChange));
        assert_eq!(children.wait(first.pid, false), Ok(Wait::Pending));
        assert_eq!(children.wait(999, false), Ok(Wait::NoChild));
        assert_eq!(
            children.wait(-1, false),
            Ok(Wait::Ready {
                identity: second,
                status: 15
            })
        );
        assert_eq!(children.abandon_after_parent_terminal(first), Err(-16));
        children.abandon_after_parent_terminal(second).unwrap();
        children.reclaimed(second).unwrap();
        children.terminal(first, 0).unwrap();
        assert_eq!(
            children.wait(-1, false),
            Ok(Wait::Ready {
                identity: first,
                status: 0
            })
        );
    }

    #[test]
    fn malformed_admission_and_status_leave_ledger_unchanged() {
        let mut children = Children::new();
        let original = children.clone();
        let canonical = id(2, 1);
        for bad in [
            Identity {
                pid: 7,
                ..canonical
            },
            Identity {
                handle: 0,
                ..canonical
            },
            Identity {
                slot: 1,
                ..canonical
            },
            Identity {
                generation: 0,
                ..canonical
            },
            id(2, 2),
        ] {
            assert!(children.admit(bad).is_err());
            assert_eq!(children, original);
        }
        children.admit(canonical).unwrap();
        let before = children.clone();
        for status in [-1, 128, 256 | 15, 65536] {
            assert_eq!(children.terminal(canonical, status), Err(-22));
            assert_eq!(children, before);
        }
        for pid in [0, -2, i32::MIN] {
            assert_eq!(children.wait(pid, false), Err(-22));
            assert_eq!(children, before);
        }
    }
}

#[cfg(test)]
mod selected_lease_tests {
    use super::*;
    fn child() -> Identity { Identity::admitted(2, 1, 0xb0000103).unwrap() }
    #[test]
    fn real_wait_delivery_collection_reclaim_precede_parent_read_lease() {
        let id = child(); let mut children = Children::new(); let mut lease = ReadLease::Parent;
        assert!(lease.give_child(id, true).is_err()); lease.give_child(id, false).unwrap(); children.admit(id).unwrap();
        assert_eq!(children.wait_flags(-1, 11).unwrap(), Wait::NoChange);
        children.terminal(id, 1792).unwrap();
        assert!(lease.restore_parent(id, &children).is_err());
        assert_eq!(children.wait_flags(-1, 11).unwrap(), Wait::Ready { identity: id, status: 1792 });
        assert!(children.reclaimed(id).is_err()); assert!(lease.restore_parent(id, &children).is_err());
        children.delivered(id).unwrap(); assert!(lease.restore_parent(id, &children).is_err());
        children.reclaimed(id).unwrap(); lease.restore_parent(id, &children).unwrap();
        assert_eq!(lease, ReadLease::Parent); assert_eq!(children.wait_flags(-1, 0).unwrap(), Wait::NoChild);
    }
    #[test]
    fn child_canonical_or_isig_read_is_refused_and_unknown_is_sticky() {
        let id = child(); let mut lease = ReadLease::Parent; lease.give_child(id, false).unwrap();
        assert_eq!(lease.child_read(id, true, false), Err(-95)); assert_eq!(lease.child_read(id, false, true), Err(-95));
        assert_eq!(lease.child_read(id, false, false), Ok(()));
        assert_eq!(lease.child_read(Identity::admitted(2, 2, 0xb0000203).unwrap(), false, false), Err(-13));
        lease.contain(); assert!(lease.give_child(id, false).is_err()); assert!(lease.child_read(id, false, false).is_err());
        let mut children = Children::new(); assert_eq!(children.wait_flags(-1, 4), Err(-22));
        assert_eq!(children.wait_flags(0, 0), Err(-22));
    }
}
