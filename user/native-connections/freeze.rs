// SPDX-License-Identifier: BSD-2-Clause
// Cooperating process parking only; no copied process or POSIX fork success.
use super::*;
fn pending(h: u64, expected: i64) {
    for _ in 0..10000 {
        let state = ctl(0x23004, h).0;
        if state == expected {
            return;
        }
        check(state == 0, 1710);
        ctl(0x1fffe, 0);
    }
    end(1710)
}
fn retire(c: Connection, status: (u32, u32)) {
    check(terminal(c.child) == status, 1713);
    check(
        ctl(0x24003, c.reader).0 == 0 && ctl(0x24003, c.writer).0 == 0,
        1714,
    );
    check(ctl(0x20002, c.child).0 == 0, 1714);
}
pub fn run(factory: u64, first: u64, second: u64) -> ! {
    let disabled = cfg!(freeze_disabled);
    let unsupported = cfg!(freeze_unsupported);
    let mut old = 0;
    for _ in 0..2 {
        let parent = launch(factory, first, 0);
        if !disabled {
            check(ctl(0x23003, 0).0 == -13, 1715);
            check(ctl(0x23004, 0).0 == -9, 1715);
            check(call(0x23004, parent.child, 1, 0, 0, 0, 0).0 == -22, 1715);
            check(call(0x23005, parent.child, 1, 1, 0, 0, 0).0 == -22, 1715);
            if old != 0 {
                check(ctl(0x23004, old).0 == -9, 1715);
                check(call(0x23005, old, 1, 0, 0, 0, 0).0 == -9, 1715);
            }
        }
        if !disabled && !unsupported {
            for sequence in 1..=2 {
                pending(parent.child, sequence);
                for _ in 0..32 {
                    ctl(0x1fffe, 0);
                    check(ctl(0x23004, parent.child).0 == sequence, 1711);
                    check(ctl(0x20001, parent.child).0 == 0, 1711);
                }
                check(
                    call(0x23005, parent.child, (sequence - 1) as u64, 0, 0, 0, 0).0 == -9,
                    1712,
                );
                check(ctl(0x23004, parent.child).0 == sequence, 1712);
                if cfg!(freeze_stop) {
                    check(ctl(0x20007, parent.child).0 == 0, 1716);
                    check(ctl(0x23004, parent.child).0 == -16, 1716);
                    check(
                        call(0x23005, parent.child, sequence as u64, 0, 0, 0, 0).0 == -16,
                        1716,
                    );
                    break;
                }
                check(
                    call(0x23005, parent.child, sequence as u64, 0, 0, 0, 0).0 == 0,
                    1712,
                );
            }
        }
        retire(parent, if cfg!(freeze_stop) { (143, 3) } else { (29, 1) });
        old = parent.child;
        if !disabled {
            check(ctl(0x23004, old).0 == -9, 1715);
        }
        for slot in 1..=if unsupported { 1 } else { 2 } {
            let peer = launch(factory, second, slot);
            retire(peer, (29, 1));
        }
    }
    end(100)
}
