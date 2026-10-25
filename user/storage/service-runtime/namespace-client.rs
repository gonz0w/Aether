// SPDX-License-Identifier: BSD-2-Clause
//! Private separate-domain conformance client, not sys-init or FD policy.
#[cfg(not(namespace_wait))]
#[path = "../namespace-channel.rs"]
mod channel;
#[cfg(namespace_wait)]
#[path = "../namespace-wait-channel.rs"]
mod channel;
use super::check;

fn call(op: u64, a: u64, b: u64, c: u64, d: u64) -> (i64, u64) {
    // SAFETY: this wrapper is used below only for scalar control/close/create.
    unsafe { channel::trap(op, a, b, c, d) }
}
fn get(bytes: &[u8; 64], index: usize) -> u64 {
    let mut value = 0;
    for i in 0..8 {
        value |= (bytes[index * 8 + i] as u64) << (i * 8);
    }
    value
}
fn put(bytes: &mut [u8; 64], index: usize, value: u64) {
    for i in 0..8 {
        bytes[index * 8 + i] = (value >> (i * 8)) as u8;
    }
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
        check(call(0x24000, 0xd001, 0, 0, 0).0 == -16);
        check(call(0x20008, factory + 1, 0, self.request, self.reply).0 == -13);
        check(call(0x20008, factory, 2, self.request, self.reply).0 == -22);
        check(call(0x20008, factory, 1, self.request, self.reply).0 == -12);
        check(call(0x20008, factory, 0, self.send, self.reply).0 == -13);
        check(call(0x20008, factory, 0, self.request, self.send).0 == -13);
        check(call(0x20008, factory, 0, self.request, self.receive).0 == -13);
        let mut poison = [0xa5u8; 1];
        // SAFETY: live exclusive initialized one-byte scratch, exact length.
        check(
            unsafe { channel::trap(0x24002, self.send, poison.as_mut_ptr() as u64, 1, 0) }.0 == 1,
        );
        check(call(0x20008, factory, 0, self.request, self.reply).0 == -13);
        // SAFETY: same live writable one-byte scratch, no concurrent borrow.
        check(
            unsafe { channel::trap(0x24001, self.request, poison.as_mut_ptr() as u64, 1, 0) }.0
                == 1,
        );
        check(poison[0] == 0xa5);
        let owner = call(0x20008, factory, 0, self.request, self.reply).0;
        check(owner > 0);
        check(call(0x24003, self.request, 0, 0, 0).0 == -13);
        check(call(0x24003, self.reply, 0, 0, 0).0 == -13);
        owner
    }

    fn exchange(&self, mut request: [u8; 64], status: i64) -> [u8; 64] {
        check(channel::frame(self.send, &mut request, true).is_ok());
        let mut reply = [0; 64];
        check(channel::frame(self.receive, &mut reply, false).is_ok());
        check(get(&reply, 0) as i64 == status);
        if status != 0 {
            check(reply[8..].iter().all(|b| *b == 0));
        }
        reply
    }

    fn lookup(&self, root: &[u8; 64], rights: u64) -> [u8; 64] {
        let mut request = [0; 64];
        put(&mut request, 0, 1);
        put(&mut request, 1, get(root, 1));
        put(&mut request, 2, get(root, 2));
        put(&mut request, 3, rights);
        put(&mut request, 4, 4);
        request[40..44].copy_from_slice(b"zstd");
        let reply = self.exchange(request, 0);
        check(get(&reply, 3) == 2 && get(&reply, 4) == 780248);
        reply
    }

    fn read(&self, file: &[u8; 64], offset: u64, status: i64) -> [u8; 64] {
        let mut request = [0; 64];
        put(&mut request, 0, 2);
        put(&mut request, 1, get(file, 1));
        put(&mut request, 2, get(file, 2));
        put(&mut request, 3, offset);
        put(&mut request, 4, 16);
        self.exchange(request, status)
    }

    pub fn exercise(&self) {
        let mut root = [0; 64];
        check(channel::frame(self.receive, &mut root, false).is_ok());
        check(get(&root, 0) == 0 && get(&root, 1) == self.request && get(&root, 3) == 1);
        let file = self.lookup(&root, 2);
        let reply = self.read(&file, 0, 0);
        check(get(&reply, 4) == 16 && &reply[40..48] == b"\x7fELF\x02\x01\x01\x00");
        check(reply[56..].iter().all(|b| *b == 0));
        check(self.read(&file, 780248, 0).iter().all(|b| *b == 0));
        let restricted = self.lookup(&root, 1);
        self.read(&restricted, 0, -13);
        let mut close = [0; 64];
        put(&mut close, 0, 3);
        put(&mut close, 1, get(&file, 1));
        put(&mut close, 2, get(&file, 2));
        self.exchange(close, 0);
        self.read(&file, 0, -9);
        let mut disconnect = [0; 64];
        put(&mut disconnect, 0, 4);
        check(self.exchange(disconnect, 0).iter().all(|b| *b == 0));
    }

    pub fn finish(self) -> u64 {
        let mut scratch = [0; 1];
        // SAFETY: worker terminal closes its ends; these one-byte buffers remain
        // valid during the EOF/EPIPE checks. No copied capability grants rights.
        check(
            unsafe { channel::trap(0x24001, self.receive, scratch.as_mut_ptr() as u64, 1, 0) }.0
                == 0,
        );
        check(
            unsafe { channel::trap(0x24002, self.send, scratch.as_mut_ptr() as u64, 1, 0) }.0
                == -32,
        );
        check(call(0x24003, self.send, 0, 0, 0).0 == 0);
        check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
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
