// SPDX-License-Identifier: BSD-2-Clause
//! Fixed eight-transaction AFSRPC03 controller; no installed client policy.
use super::*;

// Opcode, token/name, offset/rights/destination, data/expected-size, denied errno.
// No branches can append another transaction or manufacture an engine identity.
const JOBS: [[u8; 5]; 24] = [
    [7, b'p', 0, 0, 0],
    [1, b'p', 6, 0, 0],
    [5, 2, 0, 11, 0],
    [5, 2, 16, 31, 0],
    [8, b'p', b'q', 0, 0],
    [6, 2, 0, 32, 0],
    [2, 2, 0, 11, 0],
    [5, 2, 32, 51, 0],
    [9, b'q', 0, 0, 13],
    [1, b'q', 2, 48, 0],
    [3, 2, 0, 0, 0],
    [9, b'q', 0, 0, 13],
    [3, 3, 0, 0, 0],
    [9, b'q', 0, 0, 0],
    [7, b'p', 0, 0, 0],
    [2, 2, 0, 0, 9],
    [1, b'p', 6, 0, 0],
    [5, 4, 0, 71, 0],
    [6, 4, 0, 16, 0],
    [2, 4, 0, 71, 0],
    [2, 4, 16, 0, 0],
    [7, b'r', 0, 0, 28],
    [5, 4, 0, 91, 28],
    [3, 4, 0, 0, 0],
];

impl Connection {
    #[inline(never)]
    fn mixed_message(&self, op: u64) -> [u8; 64] {
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(b"AFSRPC03");
        put(&mut raw, 1, op);
        put(&mut raw, 2, self.request);
        raw
    }
    #[inline(never)]
    fn mixed_exchange(&self, mut raw: [u8; 64], status: i64) -> [u8; 64] {
        check(channel::frame(self.send, &mut raw, true).is_ok());
        // Send retained no pointer; full receive overwrites every byte, and
        // frame clears all bytes on any partial/error return. Reuse one buffer.
        check(channel::frame(self.receive, &mut raw, false).is_ok());
        check(get(&raw, 0) == u64::from_le_bytes(*b"AFSRPC03"));
        check(get(&raw, 1) as i64 == status && get(&raw, 2) == self.request);
        if status != 0 {
            check(raw[24..].iter().all(|b| *b == 0));
        }
        raw
    }
    #[inline(never)]
    pub fn exercise(&self) {
        let mut ready = [0; 64];
        check(channel::frame(self.receive, &mut ready, false).is_ok());
        check(
            get(&ready, 0) == u64::from_le_bytes(*b"AFSRPC03")
                && get(&ready, 1) == 0
                && get(&ready, 2) == self.request
                && get(&ready, 3) == 1
                && get(&ready, 4) == 1,
        );
        let mut base = self.mixed_message(7);
        put(&mut base, 3, 1);
        put(&mut base, 5, 1);
        base[48] = b'p';
        for version in [b'1', b'2'] {
            let mut bad = base;
            bad[7] = version;
            self.mixed_exchange(bad, -22);
        }
        let mut bad = base;
        put(&mut bad, 3, 99);
        self.mixed_exchange(bad, -9);
        bad = base;
        put(&mut bad, 2, self.request + 1);
        self.mixed_exchange(bad, -9);
        #[cfg(not(fs_lost_reply))]
        let (mut last_txg, mut next_token) = (782, 2);
        for [op, a, b, seed, errno] in JOBS {
            let mut raw = self.mixed_message(op as u64);
            match op {
                1 => {
                    put(&mut raw, 3, 1);
                    put(&mut raw, 4, b as u64);
                    put(&mut raw, 5, 1);
                    raw[48] = a;
                }
                2 | 5 => {
                    put(&mut raw, 3, a as u64);
                    put(&mut raw, 4, b as u64);
                    put(&mut raw, 5, 16);
                    if op == 5 {
                        for (i, value) in raw[48..].iter_mut().enumerate() {
                            *value = seed.wrapping_add(i as u8);
                        }
                    }
                }
                7..=9 => {
                    put(&mut raw, 3, 1);
                    put(&mut raw, 4, 0);
                    put(&mut raw, 5, 1 | if op == 8 { 1 << 32 } else { 0 });
                    raw[48] = a;
                    if op == 8 {
                        raw[49] = b;
                    }
                }
                _ => put(&mut raw, 3, a as u64),
            }
            #[cfg(fs_lost_reply)]
            {
                let _ = errno;
                check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
                check(channel::frame(self.send, &mut raw, true).is_ok());
                return;
            }
            #[cfg(not(fs_lost_reply))]
            {
                let reply = self.mixed_exchange(raw, -i64::from(errno));
                if errno != 0 {
                    continue;
                }
                match op {
                    1 | 6 => {
                        let token = if op == 1 {
                            let token = next_token;
                            next_token += 1;
                            token
                        } else {
                            a as u64
                        };
                        check(
                            get(&reply, 3) == token
                                && get(&reply, 4) == 2
                                && get(&reply, 5) == seed as u64
                                && reply[48..].iter().all(|b| *b == 0),
                        );
                    }
                    2 => {
                        check(get(&reply, 5) == if seed == 0 { 0 } else { 16 });
                        for (i, value) in reply[48..].iter().enumerate() {
                            check(
                                *value
                                    == if seed == 0 {
                                        0
                                    } else {
                                        seed.wrapping_add(i as u8)
                                    },
                            );
                        }
                    }
                    5 | 7..=9 => {
                        check(
                            get(&reply, 3) == 0
                                && get(&reply, 4) > last_txg
                                && get(&reply, 5) == if op == 5 { 16 } else { 0 }
                                && get(&reply, 6) == 2
                                && get(&reply, 7) == 0,
                        );
                        last_txg = get(&reply, 4);
                    }
                    _ => check(reply[24..].iter().all(|b| *b == 0)),
                }
            }
        }
        #[cfg(not(fs_lost_reply))]
        {
            let mut end = self.mixed_message(4);
            #[cfg(fs_partial_request)]
            {
                // SAFETY: initialized16-byte prefix; one synchronous scalar
                // write into the empty retained channel, no pointer retention.
                check(
                    unsafe { channel::trap(0x24002, self.send, end.as_mut_ptr() as u64, 16, 0) }.0
                        == 16,
                );
                check(call(0x24003, self.send, 0, 0, 0).0 == 0);
            }
            #[cfg(not(fs_partial_request))]
            {
                let _ = &mut end;
                let reply = self.mixed_exchange(end, 0);
                check(reply[24..].iter().all(|b| *b == 0));
            }
        }
    }
}
