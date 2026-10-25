// SPDX-License-Identifier: BSD-2-Clause
//! Actual connection settlement against fixed closed-reader syscall outcomes.
use std::cell::Cell;
std::thread_local! {
    static HEALTHY:Cell<bool>=const{Cell::new(true)};
    static CLOSES:Cell<usize>=const{Cell::new(0)};
}
struct Connection {
    send: u64,
    receive: u64,
}
fn check(ok: bool) {
    assert!(ok, "AF07_FINISH_ORACLE");
}
fn call(op: u64, cap: u64, _: u64, _: u64, _: u64) -> (i64, u64) {
    assert_eq!(op, 0x24003);
    CLOSES.with(|n| {
        let index = n.get();
        n.set(index + 1);
        assert_eq!(cap, [11, 22, 11][index]);
        (
            if index == 2 || (index == 1 && HEALTHY.with(Cell::get)) {
                -13
            } else {
                0
            },
            0,
        )
    })
}
mod channel {
    use super::*;
    pub unsafe fn trap(op: u64, cap: u64, _: u64, length: u64, _: u64) -> (i64, u64) {
        assert_eq!(length, 1);
        if op == 0x24001 {
            assert_eq!(cap, 22);
            (if HEALTHY.with(Cell::get) { -13 } else { 0 }, 0)
        } else {
            assert_eq!((op, cap), (0x24002, 11));
            (-32, 0)
        }
    }
}
impl Connection {
    // FINISH_METHOD
}
#[test]
fn metadata_loss_and_later_generation_settle_exactly_once() {
    for healthy in [true, false] {
        HEALTHY.with(|v| v.set(healthy));
        CLOSES.with(|v| v.set(0));
        assert_eq!(
            Connection {
                send: 11,
                receive: 22
            }
            .finish(healthy),
            11
        );
        CLOSES.with(|v| assert_eq!(v.get(), 3));
    }
}
