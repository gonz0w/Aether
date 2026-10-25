// SPDX-License-Identifier: BSD-2-Clause
//! Private retained-instance readiness gate, not supervision or retry policy.
#[cfg(not(test))]
fn observe(owner: u64) -> (i64, u64) {
    let status: i64;
    let ready: u64;
    // SAFETY: existing scalar owner-local status operation, no pointers retained.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") 0x20001u64 => status,
            in("rdi") owner, in("rsi") 0u64, lateout("rdx") ready,
            lateout("rcx") _, lateout("r8") _, lateout("r9") _,
            lateout("r10") _, lateout("r11") _);
    }
    (status, ready)
}
#[cfg(not(test))]
fn yield_now() {
    // SAFETY: existing scalar yield; no buffer, endpoint or authority transfer.
    unsafe {
        core::arch::asm!("int 0x81", inlateout("rax") 0x1fffeu64 => _,
            in("rdi") 0u64, in("rsi") 0u64, lateout("rdx") _,
            lateout("rcx") _, lateout("r8") _, lateout("r9") _,
            lateout("r10") _, lateout("r11") _);
    }
}

/// Only the exact instance handle returned by authenticated admission is valid.
/// Share the original supervisor poll budget across readiness and completion.
/// Ready on a terminal, stale or foreign instance never admits a dependent.
/// This observation is not atomic with a later user-space admission decision.
pub fn ready(owner: u64, remaining: &mut u32) -> bool {
    if owner == 0 {
        return false;
    }
    while *remaining != 0 {
        *remaining -= 1;
        let (status, ready) = observe(owner);
        if status != 0 || ready > 1 {
            return false;
        }
        if ready == 1 {
            return true;
        }
        yield_now();
    }
    false
}

#[cfg(test)]
use tests::{observe, yield_now};
#[cfg(test)]
mod tests {
    use super::ready;
    use std::{cell::RefCell, collections::VecDeque};
    std::thread_local! {static INPUT: RefCell<VecDeque<(i64,u64)>> = RefCell::new(VecDeque::new());
    static CALLS: RefCell<(usize,usize)> = const { RefCell::new((0,0)) };}
    pub fn observe(owner: u64) -> (i64, u64) {
        assert_eq!(owner, 0xb0000101, "ACTIVATION_IDENTITY");
        CALLS.with(|c| c.borrow_mut().0 += 1);
        INPUT.with(|q| q.borrow_mut().pop_front().expect("ACTIVATION_EXTRA_POLL"))
    }
    pub fn yield_now() {
        CALLS.with(|c| c.borrow_mut().1 += 1);
    }
    fn run(input: &[(i64, u64)], budget: u32) -> (bool, u32, (usize, usize)) {
        INPUT.with(|q| *q.borrow_mut() = input.iter().copied().collect());
        CALLS.with(|c| *c.borrow_mut() = (0, 0));
        let mut remaining = budget;
        let accepted = ready(0xb0000101, &mut remaining);
        let calls = CALLS.with(|c| *c.borrow());
        (accepted, remaining, calls)
    }
    #[test]
    fn pending_then_ready_keeps_the_completion_budget() {
        assert_eq!(run(&[(0, 0), (0, 0), (0, 1)], 7), (true, 4, (3, 2)));
    }
    #[test]
    fn terminal_stale_foreign_and_malformed_ready_never_admit() {
        for status in [1, 6, -9, -13, -22] {
            assert_eq!(run(&[(status, 1)], 7), (false, 6, (1, 0)));
        }
        assert_eq!(run(&[(0, 2)], 7), (false, 6, (1, 0)));
        assert!(!ready(0, &mut 7));
    }
    #[test]
    fn exhaustion_does_not_reset_or_poll_again() {
        assert_eq!(run(&[(0, 0), (0, 0)], 2), (false, 0, (2, 2)));
        assert_eq!(run(&[], 0), (false, 0, (0, 0)));
    }
}
