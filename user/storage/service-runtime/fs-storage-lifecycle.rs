// SPDX-License-Identifier: BSD-2-Clause
//! ABI27 owner-only idle witness; no endpoint, process or retry authority.
#[cfg(not(test))]
fn event(op: u64, sequence: u64, deadline: u64) -> (i64, u64, u64) {
    let status: i64;
    let next: u64;
    let tick: u64;
    // SAFETY: scalar self-observation/park on the explicitly granted owner
    // capability. No pointer, memory borrow or authority transfer survives park.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") op => status,
            in("rdi") 0xe002u64, in("rsi") sequence,
            inlateout("rdx") deadline => next, inlateout("r8") 0u64 => tick,
            in("r10") 0u64, in("r9") 0u64, lateout("rcx") _, lateout("r11") _);
    }
    (status, next, tick)
}

/// Reuse one fixed deadline across event hints, never the completion poll budget.
/// Thirty-two hints are a stricter local bound; exhaustion stops qualification.
pub fn idle() -> bool {
    let (status, mut sequence, start) = event(0x2a000, 0, 0);
    if status != 0 {
        return false;
    }
    let Some(deadline) = start.checked_add(6500) else {
        return false;
    };
    let mut previous = start;
    for _ in 0..32 {
        let (status, next, tick) = event(0x2a001, sequence, deadline);
        if !matches!(status, 0 | -110) || tick < previous || next < sequence {
            return false;
        }
        if tick >= deadline {
            return tick > 6000;
        }
        if status == -110 {
            return false;
        }
        previous = tick;
        sequence = next;
    }
    false
}

#[cfg(test)]
use tests::event;
#[cfg(test)]
mod tests {
    use super::idle;
    use std::{cell::RefCell, collections::VecDeque};
    type Sample = (i64, u64, u64);
    std::thread_local! {
        static INPUT: RefCell<VecDeque<Sample>> = RefCell::new(VecDeque::new());
        static CALLS: RefCell<Vec<(u64,u64,u64)>> = const { RefCell::new(Vec::new()) };
    }
    pub fn event(op: u64, sequence: u64, deadline: u64) -> Sample {
        CALLS.with(|c| c.borrow_mut().push((op, sequence, deadline)));
        INPUT.with(|q| q.borrow_mut().pop_front().expect("IDLE_EXTRA_POLL"))
    }
    fn run(samples: &[Sample]) -> (bool, Vec<(u64, u64, u64)>) {
        INPUT.with(|q| *q.borrow_mut() = samples.iter().copied().collect());
        CALLS.with(|c| c.borrow_mut().clear());
        (idle(), CALLS.with(|c| c.borrow().clone()))
    }
    #[test]
    fn fixed_deadline_survives_hints_and_crosses_old_ceiling() {
        let (ok, calls) = run(&[(0, 7, 400), (0, 8, 401), (0, 8, 6899), (-110, 8, 6900)]);
        assert!(ok);
        assert_eq!(
            calls,
            [
                (0x2a000, 0, 0),
                (0x2a001, 7, 6900),
                (0x2a001, 8, 6900),
                (0x2a001, 8, 6900)
            ]
        );
        assert!(run(&[(0, 0, 0), (0, 0, 6501)]).0);
    }
    #[test]
    fn errors_regression_early_deadline_and_exhaustion_stop() {
        for status in [-13, -38, -22, -28, 1] {
            assert!(!run(&[(status, 0, 0)]).0);
            assert!(!run(&[(0, 2, 10), (status, 2, 11)]).0);
        }
        for sample in [(0, 2, 9), (0, 1, 11), (-110, 2, 6509)] {
            assert!(!run(&[(0, 2, 10), sample]).0);
        }
        assert!(!run(&[(0, 2, 10), (0, 3, 12), (0, 3, 11)]).0);
        assert!(!run(&[(0, 2, u64::MAX - 6499)]).0);
        let mut hints = vec![(0, 2, 10)];
        hints.extend(std::iter::repeat_n((0, 2, 11), 32));
        let (ok, calls) = run(&hints);
        assert!(!ok);
        assert_eq!(calls.len(), 33);
    }
}
