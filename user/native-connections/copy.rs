// SPDX-License-Identifier: BSD-2-Clause
// Native copied-continuation witness; not a POSIX process/descriptor service.
use super::*;
fn pending(h: u64) {
    for _ in 0..10000 {
        let r = ctl(0x23004, h).0;
        if r == 1 {
            return;
        }
        check(r == 0, 1800);
        ctl(0x1fffe, 0);
    }
    end(1800)
}
fn copy(factory: u64, parent: Connection, slot: u64, token: u64, reader: u64, writer: u64) -> i64 {
    call(0x23006, factory, parent.child, slot, token, reader, writer).0
}
fn close(c: Connection) {
    check(
        ctl(0x24003, c.reader).0 == 0 && ctl(0x24003, c.writer).0 == 0,
        1822,
    );
    check(ctl(0x20002, c.child).0 == 0, 1822);
}
fn receive(c: Connection, value: u8, failure: u64) {
    let mut b = [0u8; 1];
    check(
        transfer_bounded(c.reader, &mut b, false, 100000) == 1 && b[0] == value,
        failure,
    );
}
fn send(c: Connection, value: u8) {
    check(
        transfer_bounded(c.writer, &mut [value], true, 100000) == 1,
        1823,
    );
}
pub fn run(factory: u64, first: u64, second: u64) -> ! {
    let mut old_source = 0;
    for generation in 1..=2 {
        let parent = launch(factory, first, 0);
        let dummy = launch(factory, second, 1);
        check(terminal(dummy.child) == (29, 1), 1801);
        pending(parent.child);
        let req = ctl(0x24000, 0xd001);
        let rep = ctl(0x24000, 0xd001);
        check(req.0 > 0 && rep.0 > 0, 1802);
        let reader = req.0 as u64;
        let writer = rep.1;
        check(copy(0, parent, 2, 1, reader, writer) == -13, 1803);
        check(
            call(0x23006, factory, 0, 2, 1, reader, writer).0 == -9,
            1803,
        );
        if old_source != 0 {
            check(
                call(0x23006, factory, old_source, 2, 1, reader, writer).0 == -9,
                1803,
            );
        }
        check(copy(factory, parent, 0, 1, reader, writer) == -22, 1803);
        check(copy(factory, parent, 3, 1, reader, writer) == -22, 1803);
        check(copy(factory, parent, 1, 1, reader, writer) == -16, 1803);
        check(copy(factory, parent, 2, 0, reader, writer) == -9, 1803);
        check(copy(factory, parent, 2, 2, reader, writer) == -9, 1803);
        check(
            copy(factory, parent, 2, 1, req.1, rep.0 as u64) == -13,
            1803,
        );
        check(copy(factory, parent, 2, 1, reader, req.1) == -13, 1803);
        check(
            copy(factory, parent, 2, 1, parent.reader, writer) == -13,
            1803,
        );
        // A pending byte must not be silently inherited by a new connection.
        check(transfer_bounded(req.1, &mut [99], true, 1) == 1, 1803);
        check(copy(factory, parent, 2, 1, reader, writer) == -13, 1803);
        let mut discarded = [0];
        check(
            transfer_bounded(reader, &mut discarded, false, 1) == 1 && discarded == [99],
            1803,
        );
        let child = copy(factory, parent, 2, 1, reader, writer);
        if cfg!(copy_rollback) {
            check(child == -12 && ctl(0x23004, parent.child).0 == 1, 1810);
            let expected = 0xb0000000 | (generation << 8) | 3;
            check(ctl(0x20001, expected).0 == -9, 1810);
            check(
                call(0x24001, reader, 0, 0, 0, 0, 0).0 == 0
                    && call(0x24002, writer, 0, 0, 0, 0, 0).0 == 0,
                1810,
            );
            for cap in [reader, req.1, rep.0 as u64, writer] {
                check(ctl(0x24003, cap).0 == 0, 1810);
            }
            check(call(0x23005, parent.child, 1, 0, 0, 0, 0).0 == 0, 1810);
            receive(parent, 0x71, 1821);
            check(terminal(parent.child) == (71, 1), 1821);
            close(parent);
            close(dummy);
            let replacement = launch(factory, second, 2);
            check(
                replacement.child == expected && terminal(replacement.child) == (29, 1),
                1811,
            );
            close(replacement);
        } else {
            check(child == (0xb0000000 | (generation << 8) | 3) as i64, 1804);
            check(
                ctl(0x24003, reader).0 == -13 && ctl(0x24003, writer).0 == -13,
                1804,
            );
            let child = Connection {
                reader: rep.0 as u64,
                writer: req.1,
                child: child as u64,
            };
            // Exact terminal status distinguishes an early child failure from I/O timeout.
            let mut b = [0u8; 1];
            let mut ready = false;
            for _ in 0..100000 {
                let n = call(0x24001, child.reader, b.as_mut_ptr() as u64, 1, 0, 0, 0).0;
                if n == 1 {
                    ready = b[0] == 0x72;
                    break;
                }
                check(n == -11 && ctl(0x20001, child.child).0 == 0, 1820);
                ctl(0x1fffe, 0);
            }
            check(ready, 1820);
            send(parent, 0x61);
            receive(parent, 0x71, 1821);
            send(child, 0x62);
            check(terminal(child.child) == (72, 1), 1820);
            send(parent, 0x63);
            check(terminal(parent.child) == (71, 1), 1821);
            close(child);
            close(parent);
            close(dummy);
        }
        old_source = parent.child;
    }
    end(100)
}
