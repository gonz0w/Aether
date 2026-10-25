// SPDX-License-Identifier: BSD-2-Clause
// Owner-side lifecycle witness only; this does not implement runner CLI policy.
use super::*;

pub fn run(factory: u64, first: u64, second: u64) -> ! {
    for generation in 1..=2 {
        let service = launch(factory, second, 1);
        let mut hello = [0; 32];
        check(
            transfer(service.reader, &mut hello, false) == 1 && get(&hello, 8) == 0xf002,
            953,
        );
        let a = backend(service, 1, 0xf001, 0, 1, b"hello.sh");
        check(get(&a, 0) == 0 && get(&a, 8) == 6, 953);
        let b = backend(service, 5, 0xf002, 0, 3, b"output");
        check(get(&b, 0) == 0, 953);
        let handles = [get(&a, 4), get(&b, 4)];
        let parent = launch(factory, first, 0);
        bootstrap(parent, 0, generation);
        let mut live = [true; 2];
        let mut frame = [0u8; 32];
        let mut used = 0;
        let mut exited = false;
        for _ in 0..200000 {
            let status = ctl(0x20001, parent.child);
            check(status.0 >= 0, 1200);
            if status.0 > 0 {
                check(status.0 == 1 && status.2 == 1, 1200);
                let mut pending = [0u8; 1];
                check(
                    used == 0
                        && call(
                            0x24001,
                            parent.reader,
                            pending.as_mut_ptr() as u64,
                            1,
                            0,
                            0,
                            0,
                        )
                        .0 == 0,
                    1202,
                );
                check(live == [false; 2], 1201);
                exited = true;
                break;
            }
            // The mutable frame is live only for this synchronous trap. No alias
            // survives it; each transfer is bounded by the remaining frame space.
            let n = call(
                0x24001,
                parent.reader,
                frame[used..].as_mut_ptr() as u64,
                (32 - used).min(16) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 || n == 0 {
                ctl(0x1fffe, 0);
                continue;
            }
            check(n > 0 && n as usize <= (32 - used).min(16), 1202);
            used += n as usize;
            if used != 32 {
                continue;
            }
            check(
                get(&frame, 0) == 3 && frame[12..].iter().all(|v| *v == 0),
                1202,
            );
            let fd = get(&frame, 8);
            check(fd == 3 || fd == 4, 1203);
            let j = (fd - 3) as usize;
            check(
                live[j] && get(&frame, 4) == reference(0, j, generation),
                1203,
            );
            let data = backend(service, 2, handles[j], 0, 16, &[]);
            check(
                if j == 0 {
                    get(&data, 0) == 6 && &data[16..22] == b"abcdef"
                } else {
                    get(&data, 0) == 0
                },
                1204,
            );
            check(
                get(&backend(service, 3, handles[j], 0, 0, &[]), 0) == 0,
                1205,
            );
            check(
                get(&backend(service, 2, handles[j], 0, 1, &[]), 0) as i32 == -9,
                1205,
            );
            live[j] = false;
            frame = [0; 32];
            check(transfer(parent.writer, &mut frame, true) == 1, 990);
            used = 0;
        }
        check(exited, 1206);
        check(
            ctl(0x24003, parent.reader).0 == 0
                && ctl(0x24003, parent.writer).0 == 0
                && ctl(0x20002, parent.child).0 == 0,
            976,
        );
        check(
            ctl(0x24003, service.writer).0 == 0
                && terminal(service.child) == (17, 1)
                && ctl(0x24003, service.reader).0 == 0
                && ctl(0x20002, service.child).0 == 0,
            976,
        );
        if cfg!(local_premature) {
            end(100);
        }
    }
    end(100)
}
