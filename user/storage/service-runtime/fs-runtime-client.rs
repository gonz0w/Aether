// SPDX-License-Identifier: BSD-2-Clause
//! Fixed nine-transaction/96-request AFSRPC04 controller; no installed client policy.
use super::*;
#[cfg(fs_names)]
#[path = "fs-names-client.rs"]
mod names;
#[cfg(not(fs_names))]
const WIRE_MAGIC: &[u8; 8] = b"AFSRPC04";
#[cfg(fs_names)]
const WIRE_MAGIC: &[u8; 8] = b"AFSRPC05";

// Opcode, token/name, offset/rights/destination, data/expected-size, denied errno.
// No branches can append another transaction or manufacture an engine identity.
#[cfg(not(fs_partial_request))]
const JOBS: [[u8; 5]; 26] = [
    [7, b'p', 0, 0, 0],
    [1, b'p', 6, 0, 0],
    [5, 2, 0, 11, 0],
    [5, 2, 1, 31, 0],
    [8, b'p', b'q', 0, 0],
    [6, 2, 0, 2, 0],
    [2, 2, 0, 11, 0],
    [5, 2, 2, 51, 0],
    [9, b'q', 0, 0, 13],
    [1, b'q', 2, 3, 0],
    [3, 2, 0, 0, 0],
    [9, b'q', 0, 0, 13],
    [3, 3, 0, 0, 0],
    [9, b'q', 0, 0, 0],
    [7, b'p', 0, 0, 0],
    [2, 2, 0, 0, 9],
    [1, b'p', 6, 0, 0],
    [5, 4, 0, 71, 0],
    [6, 4, 0, 1, 0],
    [2, 4, 0, 71, 0],
    [2, 4, 1, 0, 0],
    [5, 4, 1, 91, 0],
    [2, 4, 1, 91, 0],
    [6, 4, 65, 2, 0],
    [2, 4, 2, 0, 0],
    [3, 4, 0, 0, 0],
];

impl Connection {
    #[inline(never)]
    fn bulk_message(&self, op: u64) -> [u8; 64] {
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(WIRE_MAGIC);
        put(&mut raw, 1, op);
        put(&mut raw, 2, self.request);
        raw
    }
    #[inline(never)]
    fn bulk_exchange(&self, raw: &mut [u8; 64], status: i64, seed: u8) {
        #[cfg(not(fs_partial_request))]
        let op = get(raw, 1);
        #[cfg(fs_partial_request)]
        let _ = seed;
        #[cfg(not(fs_names))]
        check(channel::frame(self.send, raw, true).is_ok());
        #[cfg(fs_names)]
        check(names::send(self.send, raw));
        #[cfg(not(fs_partial_request))]
        if op == 5 {
            self.bulk_data(true, seed);
        }
        // Send retained no pointer; full receive overwrites every byte, and
        // frame clears all bytes on any partial/error return. Reuse one buffer.
        check(channel::frame(self.receive, raw, false).is_ok());
        check(get(raw, 0) == u64::from_le_bytes(*WIRE_MAGIC));
        check(get(raw, 1) as i64 == status && get(raw, 2) == self.request);
        if status != 0 {
            check(raw[24..].iter().all(|b| *b == 0));
        }
        #[cfg(not(fs_partial_request))]
        if op == 2 && status == 0 {
            check(get(raw, 5) == if seed == 0 { 0 } else { 4096 });
            check((get(raw, 3) | get(raw, 4) | get(raw, 6) | get(raw, 7)) == 0);
            if seed != 0 {
                self.bulk_data(false, seed);
            }
        }
    }
    #[cfg(not(fs_partial_request))]
    #[inline(always)]
    fn bulk_data(&self, writing: bool, mut seed: u8) {
        let mut body = [0; 64];
        for _ in 0..64 {
            if !writing {
                check(channel::frame(self.receive, &mut body, false).is_ok());
            }
            for b in &mut body {
                if writing {
                    *b = seed;
                } else {
                    check(*b == seed);
                }
                seed = seed.wrapping_add(1);
            }
            if writing {
                check(channel::frame(self.send, &mut body, true).is_ok());
            }
        }
    }
    #[inline(never)]
    pub fn exercise(&self) {
        let mut ready = [0; 64];
        check(channel::frame(self.receive, &mut ready, false).is_ok());
        check(
            get(&ready, 0) == u64::from_le_bytes(*WIRE_MAGIC)
                && get(&ready, 1) == 0
                && get(&ready, 2) == self.request
                && get(&ready, 3) == 1
                && get(&ready, 4) == 1,
        );
        let mut base = self.bulk_message(7);
        put(&mut base, 3, 1);
        put(&mut base, 5, 1);
        base[48] = b'p';
        #[cfg(not(fs_names))]
        for version in [b'1', b'2', b'3'] {
            let mut bad = base;
            bad[7] = version;
            self.bulk_exchange(&mut bad, -22, 0);
        }
        #[cfg(fs_names)]
        for name in [b'.', b'/', 0] {
            let mut bad = base;
            bad[48] = name;
            self.bulk_exchange(&mut bad, -22, 0);
        }
        let mut bad = base;
        put(&mut bad, 3, 99);
        self.bulk_exchange(&mut bad, -9, 0);
        bad = base;
        #[cfg(not(fs_names))]
        put(&mut bad, 2, self.request + 1);
        #[cfg(fs_names)]
        put(&mut bad, 3, 100);
        self.bulk_exchange(&mut bad, -9, 0);
        #[cfg(fs_partial_request)]
        {
            self.bulk_partial(base);
        }
        #[cfg(not(fs_partial_request))]
        {
            #[cfg(not(fs_lost_reply))]
            let (mut last_txg, mut next_token) = (782, 2);
            #[cfg(not(fs_lost_reply))]
            let (mut index, mut repeated) = (0, 0);
            #[cfg(fs_lost_reply)]
            let index = 0;
            while index < JOBS.len() {
                let [op, a, b, seed, errno] = JOBS[index];
                // One interpreter loop, retaining the complete response checks.
                // Only stat's otherwise-unused offset byte encodes repetition.
                #[cfg(not(fs_lost_reply))]
                {
                    repeated += 1;
                    if op != 6 || repeated >= b {
                        index += 1;
                        repeated = 0;
                    }
                }
                let mut raw = self.bulk_message(op as u64);
                match op {
                    1 => {
                        put(&mut raw, 3, 1);
                        put(&mut raw, 4, b as u64);
                        put(&mut raw, 5, 1);
                        raw[48] = a;
                    }
                    2 | 5 => {
                        put(&mut raw, 3, a as u64);
                        put(&mut raw, 4, (b as u64) * 4096);
                        put(&mut raw, 5, 4096);
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
                    let _ = (seed, errno);
                    check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
                    #[cfg(not(fs_names))]
                    check(channel::frame(self.send, &mut raw, true).is_ok());
                    #[cfg(fs_names)]
                    check(names::send(self.send, &mut raw));
                    return;
                }
                #[cfg(not(fs_lost_reply))]
                {
                    self.bulk_exchange(&mut raw, -i64::from(errno), seed);
                    let reply = &raw;
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
                                    && get(&reply, 5) == (seed as u64) * 4096
                                    && reply[48..].iter().all(|b| *b == 0),
                            );
                        }
                        // bulk_exchange already verifies the complete read
                        // header, declared count and every body byte.
                        2 => {}
                        5 | 7..=9 => {
                            check(
                                get(&reply, 3) == 0
                                    && get(&reply, 4) > last_txg
                                    && get(&reply, 5) == if op == 5 { 4096 } else { 0 }
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
                let mut end = self.bulk_message(4);
                #[cfg(not(fs_partial_request))]
                {
                    let _ = &mut end;
                    self.bulk_exchange(&mut end, 0, 0);
                    let reply = &end;
                    check(reply[24..].iter().all(|b| *b == 0));
                }
            }
        }
    }
    #[cfg(all(fs_activation, fs_partial_request))]
    fn bulk_prefix(&self, bytes: &mut [u8; 64]) -> Result<(), i64> {
        let mut offset = 0;
        for _ in 0..100_000 {
            let remaining = 16 - offset;
            // SAFETY: live initialized exclusive suffix of the16-byte prefix;
            // synchronous transfer retains no pointer, including on EAGAIN.
            let count = unsafe {
                channel::trap(
                    0x24002,
                    self.send,
                    bytes[offset..].as_mut_ptr() as u64,
                    remaining as u64,
                    0,
                )
            }
            .0;
            if count == -11 {
                // SAFETY: scalar owned endpoint only. Recheck after any hint;
                // never resend bytes already accepted or extend the prefix.
                let status = unsafe { channel::trap(0x24004, self.send, 0, 0, 0) }.0;
                if status != 0 {
                    return Err(if status < 0 { status } else { -5 });
                }
            } else if count <= 0 || count as usize > remaining {
                return Err(if count < 0 { count } else { -5 });
            } else {
                offset += count as usize;
                if offset == 16 {
                    return Ok(());
                }
            }
        }
        Err(-110)
    }
    #[cfg(fs_partial_request)]
    fn bulk_partial(&self, mut create: [u8; 64]) {
        self.bulk_exchange(&mut create, 0, 0);
        let done = &create;
        check(
            get(&done, 3) == 0
                && get(&done, 4) > 782
                && get(&done, 5) == 0
                && get(&done, 6) == 2
                && get(&done, 7) == 0,
        );
        let mut raw = self.bulk_message(1);
        put(&mut raw, 3, 1);
        put(&mut raw, 4, 6);
        put(&mut raw, 5, 1);
        raw[48] = b'p';
        self.bulk_exchange(&mut raw, 0, 0);
        let found = &raw;
        check(
            get(&found, 3) == 2
                && get(&found, 4) == 2
                && get(&found, 5) == 0
                && found[48..].iter().all(|b| *b == 0),
        );
        raw = self.bulk_message(5);
        put(&mut raw, 3, 2);
        put(&mut raw, 5, 4096);
        check(channel::frame(self.send, &mut raw, true).is_ok());
        for (i, b) in raw[..16].iter_mut().enumerate() {
            *b = 11 + i as u8;
        }
        // SAFETY: initialized16-byte body prefix, synchronous transfer; closing
        // input makes the remaining4080 bytes absent, so no write may dispatch.
        #[cfg(not(fs_activation))]
        check(unsafe { channel::trap(0x24002, self.send, raw.as_mut_ptr() as u64, 16, 0) }.0 == 16);
        #[cfg(fs_activation)]
        check(self.bulk_prefix(&mut raw).is_ok());
        check(call(0x24003, self.send, 0, 0, 0).0 == 0);
    }
}
