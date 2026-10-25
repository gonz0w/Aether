// SPDX-License-Identifier: BSD-2-Clause
// Image-only exec witness; there is no Unix descriptor table in these clients.
use super::*;
fn parked(h: u64, sequence: i64) {
    for _ in 0..10000 {
        let n = ctl(0x23004, h).0;
        if n == sequence {
            return;
        }
        check(n == 0, 2030);
        ctl(0x1fffe, 0);
    }
    end(2030)
}
fn retire(c: Connection, status: u32) {
    check(terminal(c.child) == (status, 1), 2034);
    check(
        ctl(0x24003, c.reader).0 == 0 && ctl(0x24003, c.writer).0 == 0,
        2034,
    );
    check(ctl(0x20002, c.child).0 == 0, 2034);
}
pub fn run(factory: u64, first: u64, second: u64, third: u64) -> ! {
    let parent_pid = ctl(0x10027, 0).0;
    check(parent_pid > 0 && parent_pid < 10, 2030);
    let mut old = 0;
    for generation in 1..=2u8 {
        let source = launch(factory, first, 0);
        parked(source.child, 1);
        let mut a = args(b"exec-image");
        a.argc = 3;
        a.envc = 1;
        a.strings[1][0] = b'0' + generation * 4 + 1;
        a.strings[2][0] = b'0' + parent_pid as u8;
        a.strings[4][..13].copy_from_slice(b"AETHER_EXEC=1");
        let ptr = &a as *const Args as u64;
        check(
            call(0x23008, factory, source.child, 0, 0, 0, 0) == (0, 0, 0),
            2030,
        );
        if old != 0 {
            check(call(0x23008, factory, old, 0, 0, 0, 0).0 == -9, 2032);
        }
        check(
            call(0x23007, 0, source.child, third, 1, ptr, 0).0 == -13,
            2032,
        );
        check(
            call(0x23007, factory, source.child, 0xffff, 1, ptr, 0).0 == -13,
            2032,
        );
        check(
            call(0x23007, factory, source.child, third, 0, ptr, 0).0 == -9,
            2032,
        );
        check(
            call(0x23007, factory, source.child, third, 1, 1, 0).0 == -14,
            2032,
        );
        a.argc = 0;
        check(
            call(0x23007, factory, source.child, third, 1, ptr, 0).0 == -22,
            2032,
        );
        a.argc = 3;
        check(ctl(0x23004, source.child).0 == 1, 2032);
        check(
            call(0x23008, factory, source.child, 0, 0, 0, 0) == (0, 0, 0),
            2032,
        );
        check(call(0x23005, source.child, 1, 0, 0, 0, 0).0 == 0, 2032);
        parked(source.child, 2); // Old client verified its TLS/stack before parking again.
        check(
            call(0x23007, factory, source.child, third, 2, ptr, 0).0 == 0,
            2032,
        );
        check(
            call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 1),
            2032,
        );
        check(call(0x23005, source.child, 2, 0, 0, 0, 0).0 == -16, 2032);
        check(
            call(0x23007, factory, source.child, third, 2, ptr, 0).0 == -16,
            2032,
        );
        let request = ctl(0x24000, 0xd001);
        let reply = ctl(0x24000, 0xd001);
        check(request.0 > 0 && reply.0 > 0, 2036);
        check(
            call(
                0x23006,
                factory,
                source.child,
                1,
                2,
                request.0 as u64,
                reply.1,
            )
            .0 == -16,
            2035,
        );
        for cap in [request.0 as u64, request.1, reply.0 as u64, reply.1] {
            check(ctl(0x24003, cap).0 == 0, 2036);
        }
        for _ in 0..32 {
            ctl(0x1fffe, 0);
            check(
                ctl(0x23004, source.child).0 == 2 && ctl(0x20001, source.child).0 == 0,
                2031,
            );
        }
        check(
            call(0x23009, factory, source.child, 1, 0, 0, 0).0 == -9,
            2032,
        );
        check(
            call(0x23009, factory, source.child, 2, 0, 0, 0).0 == 0,
            2032,
        );
        check(
            call(0x23008, factory, source.child, 0, 0, 0, 0) == (2, third, 0),
            2032,
        );
        retire(source, 61);
        old = source.child;
        for slot in 1..=2 {
            retire(launch(factory, second, slot), 29);
        }
    }
    end(100)
}
