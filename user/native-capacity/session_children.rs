// SPDX-License-Identifier: BSD-2-Clause
//! Three session child records. The dispatcher supplies authenticated native
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
            pid: generation as i32 * 6 + slot as i32 + 1,
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
