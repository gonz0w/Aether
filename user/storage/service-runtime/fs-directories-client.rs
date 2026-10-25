// SPDX-License-Identifier: BSD-2-Clause
//! Fixed AF06 directory witness, nine mutations/96 requests, no pathname policy.
use super::*;
const MAGIC: &[u8; 8] = b"AFSRPC06";
const FIRST: &[u8] = b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
const SECOND: &[u8] = b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b856";
fn name(tag: u8) -> &'static [u8] {
    match tag {
        b'f' => b"files",
        b's' => b"state",
        b'k' => b"packages",
        b't' => b"stage",
        b'p' => FIRST,
        b'q' => SECOND,
        b'.' => b".",
        b'/' => b"/",
        0 => b"\0",
        _ => {
            check(false);
            b""
        }
    }
}
// op, parent/file token, name/offset, destination/rights, size/kind, errno.
#[cfg(not(fs_partial_request))]
const JOBS: [[u8; 6]; 26] = [
    [10, 1, b'f', 0, 0, 0],
    [1, 1, b'f', 15, 1, 0],
    [7, 2, b'p', 0, 0, 0],
    [1, 2, b'p', 6, 2, 0],
    [5, 3, 0, 0, 0, 0],
    [2, 3, 0, 0, 0, 0],
    [8, 2, b'p', b'q', 0, 0],
    [1, 2, b'q', 2, 2, 0],
    [3, 3, 0, 0, 0, 0],
    [3, 4, 0, 0, 0, 0],
    [10, 1, b's', 0, 0, 0],
    [1, 1, b's', 15, 1, 0],
    [10, 5, b'k', 0, 0, 0],
    [1, 5, b'k', 15, 1, 0],
    [11, 5, b'k', 0, 0, 13],
    [3, 6, 0, 0, 0, 0],
    [11, 5, b'k', 0, 0, 0],
    [7, 5, b't', 0, 0, 0],
    [1, 5, b't', 6, 2, 0],
    [3, 7, 0, 0, 0, 0],
    [9, 5, b't', 0, 0, 0],
    [6, 2, 0, 0, 3, 0],
    [6, 5, 0, 0, 2, 0],
    [6, 1, 0, 0, 5, 0],
    [3, 5, 0, 0, 0, 0],
    [3, 2, 0, 0, 0, 0],
];
#[cfg(fs_storage_lifetime)]
#[path = "fs-storage-lifecycle.rs"]
mod storage_lifecycle;
#[cfg(fs_storage_lifetime)]
const fn lifecycle_jobs() -> [[u8; 6]; 27] {
    let mut jobs = [[0; 6]; 27];
    let mut input = 0;
    let mut output = 0;
    while input < JOBS.len() {
        // Keep READ alias4 alive; close writer3 at its original position.
        if input != 9 {
            jobs[output] = JOBS[input];
            output += 1;
        }
        input += 1;
    }
    jobs[25] = [2, 4, 0, 0, 0, 0];
    jobs[26] = [3, 4, 0, 0, 0, 0];
    jobs
}
impl Connection {
    fn directory_message(&self, op: u64, token: u64) -> [u8; 64] {
        let mut h = [0; 64];
        h[..8].copy_from_slice(MAGIC);
        put(&mut h, 1, op);
        put(&mut h, 2, self.request);
        put(&mut h, 3, token);
        h
    }
    fn directory_send(&self, raw: &mut [u8; 64], a: u8, b: u8) {
        let op = get(raw, 1);
        if matches!(op, 1 | 7..=11) {
            let first = name(a);
            let second = if op == 8 { name(b) } else { b"" };
            put(raw, 5, first.len() as u64 | ((second.len() as u64) << 32));
            check(channel::frame(self.send, raw, true).is_ok());
            let mut frame = [0; 64];
            let mut length = 0;
            for byte in first.iter().chain(second) {
                frame[length] = *byte;
                length += 1;
                if length == 64 {
                    check(channel::frame(self.send, &mut frame, true).is_ok());
                    frame.fill(0);
                    length = 0;
                }
            }
            if length != 0 {
                check(channel::frame(self.send, &mut frame, true).is_ok());
            }
        } else {
            check(channel::frame(self.send, raw, true).is_ok());
        }
    }
    fn directory_receive(&self, raw: &mut [u8; 64], errno: u8) {
        check(channel::frame(self.receive, raw, false).is_ok());
        check(
            get(raw, 0) == u64::from_le_bytes(*MAGIC)
                && get(raw, 1) as i64 == -i64::from(errno)
                && get(raw, 2) == self.request,
        );
        if errno != 0 {
            check(raw[24..].iter().all(|b| *b == 0));
        }
    }
    #[cfg(not(any(fs_partial_request, fs_lost_reply)))]
    fn directory_data(&self, writing: bool) {
        let mut frame = [0; 64];
        let mut seed = 71u8;
        for _ in 0..64 {
            if !writing {
                check(channel::frame(self.receive, &mut frame, false).is_ok());
            }
            for byte in &mut frame {
                if writing {
                    *byte = seed;
                } else {
                    check(*byte == seed);
                }
                seed = seed.wrapping_add(1);
            }
            if writing {
                check(channel::frame(self.send, &mut frame, true).is_ok());
            }
        }
    }
    pub fn exercise(&self) {
        let mut raw = [0; 64];
        self.directory_receive(&mut raw, 0);
        check(
            get(&raw, 3) == 1
                && get(&raw, 4) == 1
                && get(&raw, 5) == 3
                && raw[48..].iter().all(|b| *b == 0),
        );
        for tag in [b'.', b'/', 0] {
            raw = self.directory_message(10, 1);
            self.directory_send(&mut raw, tag, 0);
            self.directory_receive(&mut raw, 22);
        }
        for token in [99, 100] {
            raw = self.directory_message(10, token);
            self.directory_send(&mut raw, b'f', 0);
            self.directory_receive(&mut raw, 9);
        }
        #[cfg(fs_partial_request)]
        self.directory_partial();
        #[cfg(not(fs_partial_request))]
        {
            #[cfg(not(fs_lost_reply))]
            let (mut txg, mut token) = (782, 2);
            #[cfg(not(fs_storage_lifetime))]
            let jobs = JOBS;
            #[cfg(fs_storage_lifetime)]
            let jobs = lifecycle_jobs();
            for [op, parent, a, b, kind, errno] in jobs {
                #[cfg(fs_storage_lifetime)]
                if op == 7 && parent == 5 {
                    check(storage_lifecycle::idle());
                }
                raw = self.directory_message(op as u64, parent as u64);
                if op == 1 {
                    put(&mut raw, 4, b as u64);
                }
                if op == 2 || op == 5 {
                    put(&mut raw, 5, 4096);
                }
                #[cfg(fs_lost_reply)]
                {
                    let _ = (kind, errno);
                    check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
                    self.directory_send(&mut raw, a, b);
                    return;
                }
                #[cfg(not(fs_lost_reply))]
                {
                    self.directory_send(&mut raw, a, b);
                    if op == 5 {
                        self.directory_data(true);
                    }
                    self.directory_receive(&mut raw, errno);
                    if errno != 0 {
                        continue;
                    }
                    match op {
                        1 => {
                            check(
                                get(&raw, 3) == token
                                    && get(&raw, 4) == kind as u64
                                    && get(&raw, 5)
                                        == if kind == 1 {
                                            2
                                        } else if a == b'q' {
                                            4096
                                        } else {
                                            0
                                        }
                                    && raw[48..].iter().all(|b| *b == 0),
                            );
                            token += 1;
                        }
                        6 => {
                            check(
                                get(&raw, 3) == parent as u64
                                    && get(&raw, 4) == 1
                                    && get(&raw, 5) == kind as u64
                                    && raw[48..].iter().all(|b| *b == 0),
                            );
                        }
                        2 => {
                            check(
                                (get(&raw, 3) | get(&raw, 4) | get(&raw, 6) | get(&raw, 7)) == 0
                                    && get(&raw, 5) == 4096,
                            );
                            self.directory_data(false);
                        }
                        5 | 7..=11 => {
                            check(
                                get(&raw, 3) == 0
                                    && get(&raw, 4) > txg
                                    && get(&raw, 5) == if op == 5 { 4096 } else { 0 }
                                    && get(&raw, 6) == 2
                                    && get(&raw, 7) == 0,
                            );
                            txg = get(&raw, 4);
                        }
                        _ => check(raw[24..].iter().all(|b| *b == 0)),
                    }
                }
            }
            #[cfg(not(fs_lost_reply))]
            {
                check(token == 8 && txg > 790);
                for _ in 0..if cfg!(fs_storage_lifetime) { 63 } else { 64 } {
                    raw = self.directory_message(6, 1);
                    self.directory_send(&mut raw, 0, 0);
                    self.directory_receive(&mut raw, 0);
                    check(
                        get(&raw, 3) == 1
                            && get(&raw, 4) == 1
                            && get(&raw, 5) == 5
                            && raw[48..].iter().all(|b| *b == 0),
                    );
                }
                raw = self.directory_message(4, 0);
                self.directory_send(&mut raw, 0, 0);
                self.directory_receive(&mut raw, 0);
                check(raw[24..].iter().all(|b| *b == 0));
            }
        }
    }
    #[cfg(fs_partial_request)]
    fn directory_partial(&self) {
        let mut raw = self.directory_message(10, 1);
        self.directory_send(&mut raw, b'f', 0);
        self.directory_receive(&mut raw, 0);
        check(get(&raw, 4) > 782 && get(&raw, 5) == 0 && get(&raw, 6) == 2);
        raw = self.directory_message(1, 1);
        put(&mut raw, 4, 15);
        self.directory_send(&mut raw, b'f', 0);
        self.directory_receive(&mut raw, 0);
        check(get(&raw, 3) == 2 && get(&raw, 4) == 1 && get(&raw, 5) == 2);
        raw = self.directory_message(7, 2);
        put(&mut raw, 5, 64);
        check(channel::frame(self.send, &mut raw, true).is_ok());
        for (i, byte) in raw[..16].iter_mut().enumerate() {
            *byte = FIRST[i];
        }
        check(self.directory_prefix(&mut raw).is_ok());
        check(call(0x24003, self.send, 0, 0, 0).0 == 0);
    }
    #[cfg(fs_partial_request)]
    fn directory_prefix(&self, bytes: &mut [u8; 64]) -> Result<(), i64> {
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
}
