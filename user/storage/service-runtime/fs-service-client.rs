// SPDX-License-Identifier: BSD-2-Clause
//! Fixed AFSRPC01 separate-domain client; not sys-init or POSIX policy.
#[cfg(not(namespace_wait))]
#[path = "../namespace-channel.rs"]
mod channel;
#[cfg(namespace_wait)]
#[path = "../namespace-wait-channel.rs"]
mod channel;
use super::check;

#[inline(never)]
fn call(op: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64) {
    // SAFETY: this wrapper is used below only for scalar control/close/create.
    unsafe { channel::trap(op, a, b, c, d) }
}
#[inline(always)]
fn get(bytes: &[u8; 64], index: usize) -> u64 {
    u64::from_le_bytes(bytes[index * 8..index * 8 + 8].try_into().unwrap())
}
#[inline(always)]
fn put(bytes: &mut [u8; 64], index: usize, value: u64) {
    bytes[index * 8..index * 8 + 8].copy_from_slice(&value.to_le_bytes());
}

pub struct Connection {
    request: u64,
    send: u64,
    receive: u64,
    reply: u64,
}

impl Connection {
    pub fn new() -> Self {
        let request = call(0x24000, 0xd001, 0, 0, 0);
        let reply = call(0x24000, 0xd001, 0, 0, 0);
        check(request.0 > 0 && reply.0 > 0);
        Self {
            request: request.0 as u64,
            send: request.1,
            receive: reply.0 as u64,
            reply: reply.1,
        }
    }

    pub fn admit(&self, factory: u64) -> i64 {
        // The unchanged readonly fixture retains the complete admission matrix.
        // This composition checks its actual holder/direction boundary directly.
        check(call(0x24000, 0xd001, 0, 0, 0).0 == -16);
        check(call(0x20008, factory + 1, 0, self.request, self.reply).0 == -13);
        check(call(0x20008, factory, 1, self.request, self.reply).0 == -12);
        check(call(0x20008, factory, 0, self.send, self.reply).0 == -13);
        let owner = call(0x20008, factory, 0, self.request, self.reply).0;
        check(owner > 0);
        check(call(0x24003, self.request, 0, 0, 0).0 == -13);
        check(call(0x24003, self.reply, 0, 0, 0).0 == -13);
        owner
    }

    #[inline(never)]
    #[cfg(not(fs_mixed))]
    fn exchange(&self, mut request: [u8; 64], status: i64) -> [u8; 64] {
        check(channel::frame(self.send, &mut request, true).is_ok());
        let mut reply = [0; 64];
        check(channel::frame(self.receive, &mut reply, false).is_ok());
        #[cfg(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove))]
        check(get(&reply, 0) == u64::from_le_bytes(*b"AFSRPC02"));
        #[cfg(not(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove)))]
        check(get(&reply, 0) == u64::from_le_bytes(*b"AFSRPC01"));
        check(get(&reply, 1) as i64 == status && get(&reply, 2) == self.request);
        if status != 0 {
            check(reply[24..].iter().all(|b| *b == 0));
        }
        reply
    }
    #[inline(never)]
    #[cfg(not(fs_mixed))]
    fn message(&self, op: u64, token: u64, field: u64, length: u64) -> [u8; 64] {
        let mut raw = [0; 64];
        #[cfg(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove))]
        raw[..8].copy_from_slice(b"AFSRPC02");
        #[cfg(not(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove)))]
        raw[..8].copy_from_slice(b"AFSRPC01");
        put(&mut raw, 1, op);
        put(&mut raw, 2, self.request);
        put(&mut raw, 3, token);
        put(&mut raw, 4, field);
        put(&mut raw, 5, length);
        raw
    }
    #[inline(never)]
    #[cfg(not(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove)))]
    #[cfg(not(fs_mixed))]
    fn lookup(&self, rights: u64) -> u64 {
        let mut raw = self.message(1, 1, rights, 4);
        raw[48..52].copy_from_slice(b"zstd");
        let reply = self.exchange(raw, 0);
        check(get(&reply, 4) == 2 && get(&reply, 5) == 780248);
        check(reply[48..].iter().all(|b| *b == 0));
        get(&reply, 3)
    }
    #[inline(never)]
    #[cfg(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove))]
    #[cfg(not(fs_mixed))]
    pub fn exercise(&self) {
        let mut root = [0; 64];
        check(channel::frame(self.receive, &mut root, false).is_ok());
        check(
            get(&root, 0) == u64::from_le_bytes(*b"AFSRPC02")
                && get(&root, 1) == 0
                && get(&root, 2) == self.request
                && get(&root, 3) == 1
                && get(&root, 4) == 1,
        );
        #[cfg(fs_namespace_create)]
        let (op, from, to): (u64, &[u8], &[u8]) = (7, b"new", b"");
        #[cfg(fs_namespace_rename)]
        let (op, from, to): (u64, &[u8], &[u8]) = (8, b"new", b"renamed");
        #[cfg(fs_namespace_remove)]
        let (op, from, to): (u64, &[u8], &[u8]) = (9, b"renamed", b"");
        let mut request = self.message(op, 1, 0, from.len() as u64 | ((to.len() as u64) << 32));
        request[48..48 + from.len()].copy_from_slice(from);
        request[48 + from.len()..48 + from.len() + to.len()].copy_from_slice(to);
        let mut invalid = request;
        invalid[..8].copy_from_slice(b"AFSRPC01");
        self.exchange(invalid, -22);
        invalid = request;
        put(&mut invalid, 2, self.request + 1);
        self.exchange(invalid, -9);
        invalid = request;
        put(&mut invalid, 3, 99);
        self.exchange(invalid, -9);
        invalid = request;
        invalid[48] = b'/';
        self.exchange(invalid, -22);
        #[cfg(fs_lost_reply)]
        {
            check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
            check(channel::frame(self.send, &mut request, true).is_ok());
            return;
        }
        #[cfg(not(fs_lost_reply))]
        {
            let reply = self.exchange(request, 0);
            check(
                get(&reply, 3) == 0
                    && get(&reply, 4) > 782
                    && get(&reply, 5) == 0
                    && get(&reply, 6) == 2
                    && get(&reply, 7) == 0,
            );
        }
    }

    #[inline(never)]
    #[cfg(not(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove)))]
    #[cfg(not(fs_mixed))]
    pub fn exercise(&self) {
        let mut scratch = [0; 1];
        // SAFETY: initialized live one-byte scratch. Holder is valid but each
        // operation deliberately selects the wrong endpoint direction.
        check(
            unsafe { channel::trap(0x24001, self.send, scratch.as_mut_ptr() as u64, 1, 0) }.0 == -9,
        );
        check(
            unsafe { channel::trap(0x24002, self.receive, scratch.as_mut_ptr() as u64, 1, 0) }.0
                == -9,
        );
        let mut root = [0; 64];
        check(channel::frame(self.receive, &mut root, false).is_ok());
        check(
            get(&root, 0) == u64::from_le_bytes(*b"AFSRPC01")
                && get(&root, 1) == 0
                && get(&root, 2) == self.request,
        );
        check(get(&root, 3) == 1 && get(&root, 4) == 1 && root[48..].iter().all(|b| *b == 0));
        let writable = self.lookup(4);
        let readable = self.lookup(2);
        let before = self.exchange(self.message(2, readable, 0, 16), 0);
        check(get(&before, 5) == 16 && get(&before, 6) == 0x0001_0102_464c_457f);
        let mut write = self.message(5, readable, 37, 16);
        for (i, b) in write[48..].iter_mut().enumerate() {
            *b = (i as u8).wrapping_mul(17).wrapping_add(91);
        }
        self.exchange(write, -13);
        put(&mut write, 3, writable);
        #[cfg(fs_lost_reply)]
        {
            // Close before the complete write request is sent: even a fast
            // provider cannot transfer a full reply or cause a replay here.
            check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
            check(channel::frame(self.send, &mut write, true).is_ok());
            return;
        }
        #[cfg(not(fs_lost_reply))]
        self.complete(write, writable, readable);
    }

    #[cfg(all(
        not(fs_lost_reply),
        not(fs_eight_writes),
        not(any(fs_namespace_create, fs_namespace_rename, fs_namespace_remove))
    ))]
    #[inline(never)]
    #[cfg(not(fs_mixed))]
    fn complete(&self, write: [u8; 64], writable: u64, readable: u64) {
        let done = self.exchange(write, 0);
        check(
            get(&done, 3) == 0
                && get(&done, 4) > 782
                && get(&done, 5) == 16
                && get(&done, 6) == 2
                && get(&done, 7) == 0,
        );
        let after = self.exchange(self.message(2, readable, 37, 16), 0);
        check(
            get(&after, 5) == 16
                && get(&after, 6) == get(&write, 6)
                && get(&after, 7) == get(&write, 7),
        );
        let stat = self.exchange(self.message(6, readable, 0, 0), 0);
        check(
            get(&stat, 3) == readable
                && get(&stat, 4) == 2
                && get(&stat, 5) == 780248
                && stat[48..].iter().all(|b| *b == 0),
        );
        let eof = self.exchange(self.message(2, readable, 780248, 16), 0);
        check(eof[24..].iter().all(|b| *b == 0));
        self.exchange(write, -28);
        self.exchange(self.message(3, writable, 0, 0), 0);
        #[cfg(fs_partial_request)]
        {
            let mut prefix = self.message(4, 0, 0, 0);
            // One16-byte prefix cannot dispatch a64-byte disconnect. Sealing
            // input forces EOF after the service consumes exactly this prefix.
            check(
                unsafe { channel::trap(0x24002, self.send, prefix.as_mut_ptr() as u64, 16, 0) }.0
                    == 16,
            );
            check(call(0x24003, self.send, 0, 0, 0).0 == 0);
        }
        #[cfg(not(fs_partial_request))]
        self.disconnect();
    }

    #[cfg(all(not(fs_lost_reply), fs_eight_writes))]
    #[inline(never)]
    #[cfg(not(fs_mixed))]
    fn complete(&self, mut write: [u8; 64], writable: u64, readable: u64) {
        let mut previous = 782;
        for part in 0..8 {
            put(&mut write, 4, 37 + part * 16);
            for (i, b) in write[48..].iter_mut().enumerate() {
                *b = (part as u8 * 16)
                    .wrapping_add(i as u8)
                    .wrapping_mul(17)
                    .wrapping_add(91);
            }
            let done = self.exchange(write, 0);
            check(
                get(&done, 3) == 0
                    && get(&done, 4) > previous
                    && get(&done, 5) == 16
                    && get(&done, 6) == 2
                    && get(&done, 7) == 0,
            );
            previous = get(&done, 4);
            let after = self.exchange(self.message(2, readable, 37 + part * 16, 16), 0);
            check(
                get(&after, 5) == 16
                    && get(&after, 6) == get(&write, 6)
                    && get(&after, 7) == get(&write, 7),
            );
            let stat = self.exchange(self.message(6, readable, 0, 0), 0);
            check(
                get(&stat, 3) == readable
                    && get(&stat, 4) == 2
                    && get(&stat, 5) == 780248
                    && stat[48..].iter().all(|b| *b == 0),
            );
            let eof = self.exchange(self.message(2, readable, 780248, 16), 0);
            check(eof[24..].iter().all(|b| *b == 0));
        }
        self.exchange(write, -28);
        self.exchange(self.message(3, writable, 0, 0), 0);
        #[cfg(fs_partial_request)]
        {
            let mut prefix = self.message(4, 0, 0, 0);
            // SAFETY: fixed initialized readable16-byte prefix, scalar retained
            // endpoint; incomplete64-byte input must not dispatch on the service.
            check(
                unsafe { channel::trap(0x24002, self.send, prefix.as_mut_ptr() as u64, 16, 0) }.0
                    == 16,
            );
            check(call(0x24003, self.send, 0, 0, 0).0 == 0);
        }
        #[cfg(not(fs_partial_request))]
        self.disconnect();
    }

    #[cfg(not(any(
        fs_partial_request,
        fs_lost_reply,
        fs_namespace_create,
        fs_namespace_rename,
        fs_namespace_remove
    )))]
    #[cfg(not(fs_mixed))]
    fn disconnect(&self) {
        let disconnected = self.exchange(self.message(4, 0, 0, 0), 0);
        check(disconnected[24..].iter().all(|b| *b == 0));
    }

    pub fn finish(self, _healthy: bool) -> u64 {
        let mut scratch = [0; 1];
        // SAFETY: worker terminal closes its ends; these one-byte buffers remain
        // valid during the EOF/EPIPE checks. No copied capability grants rights.
        check(
            unsafe { channel::trap(0x24001, self.receive, scratch.as_mut_ptr() as u64, 1, 0) }.0
                == if cfg!(fs_lost_reply) && _healthy {
                    -13
                } else {
                    0
                },
        );
        check(
            unsafe { channel::trap(0x24002, self.send, scratch.as_mut_ptr() as u64, 1, 0) }.0
                == if cfg!(fs_partial_request) && _healthy {
                    -13
                } else {
                    -32
                },
        );
        check(
            call(0x24003, self.send, 0, 0, 0).0
                == if cfg!(fs_partial_request) && _healthy {
                    -13
                } else {
                    0
                },
        );
        check(
            call(0x24003, self.receive, 0, 0, 0).0
                == if cfg!(fs_lost_reply) && _healthy {
                    -13
                } else {
                    0
                },
        );
        check(call(0x24003, self.send, 0, 0, 0).0 == -13);
        self.send
    }
}

pub fn stale(value: u64) {
    check(call(0x24003, value, 0, 0, 0).0 == -13);
}

pub fn exhausted() {
    check(call(0x24000, 0xd001, 0, 0, 0).0 == -28);
}

#[cfg(all(fs_mixed, not(fs_bulk)))]
#[path = "fs-mixed-client.rs"]
mod mixed;

#[cfg(all(fs_bulk, not(fs_runtime)))]
#[path = "fs-bulk-client.rs"]
mod bulk;

#[cfg(all(fs_runtime, not(fs_directories)))]
#[path = "fs-runtime-client.rs"]
mod runtime;

#[cfg(fs_directories)]
#[path = "fs-directories-client.rs"]
mod runtime;
