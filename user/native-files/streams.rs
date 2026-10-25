// SPDX-License-Identifier: BSD-2-Clause
// Separate, fixed-role backend. Authority is the caller's private channel.
use super::*;
pub fn run() -> i32 {
    #[cfg(scratch_backend)]
    let mut scratch = {
        let mut boot = [0; 32];
        if receive(&mut boot) != 1
            || boot[..8] != *b"AESCR001"
            || !(1..=255).contains(&get(&boot, 8))
            || boot[12..] != [0; 20]
        {
            return 125;
        }
        super::scratch::Scratch::new(if cfg!(scratch_old_epoch) {
            1
        } else {
            get(&boot, 8)
        })
    };
    let mut stdout = [0u8; 512];
    let mut stderr = [0u8; 256];
    const COUNT: usize = if cfg!(runner_denial) { 4 } else { 3 };
    let mut child_output = [0u8; 64];
    let mut lengths = [0usize; COUNT];
    let input: &[u8] = if cfg!(cat_roles) {
        if cfg!(cat_empty) {
            b""
        } else {
            include_bytes!("../native-command/cat-input.bin")
        }
    } else {
        b"abcdef"
    };
    lengths[0] = input.len();
    let mut empty_observed = false;
    let mut input_ready = false;
    let mut live = [true; COUNT];
    let handles = [0xf101, 0xf201, 0xf202, 0xf203];
    let mut hello = [0; 32];
    for j in 0..COUNT {
        put(&mut hello, 4 + j * 4, handles[j]);
    }
    #[cfg(scratch_backend)]
    {
        put(&mut hello, 16, scratch.root());
        put(&mut hello, 20, scratch.root() & 255);
        hello[24..].copy_from_slice(b"AESCR001");
    }
    if !send(&hello) {
        return 120;
    }
    #[cfg(inherit_backend_bad)]
    let mut injected = false;
    loop {
        let mut req = [0; 32];
        let got = receive(&mut req);
        if got == 0 {
            #[cfg(scratch_backend)]
            if !scratch.is_closed() {
                return 123;
            }
            return if live == [false; COUNT] { 0 } else { 123 };
        }
        if got != 1 {
            return 121;
        }
        #[cfg(inherit_backend_effect)]
        if injected {
            return 124;
        } // Any replay/cleanup traffic is forbidden after uncertainty.
        #[cfg(scratch_backend)]
        if matches!(get(&req, 4) >> 24, 0xfa | 0xfb) {
            let reply = if cfg!(scratch_drop_write) && get(&req, 0) == 4 {
                let mut reply = [0; 32];
                put(&mut reply, 0, get(&req, 12));
                reply
            } else {
                scratch.request(&req)
            };
            if !send(&reply) {
                return 122;
            }
            continue;
        }
        let mut reply = [0; 32];
        let mut result = -9i32;
        if let Some(j) = (0..COUNT).find(|j| live[*j] && get(&req, 4) == handles[*j]) {
            let (op, offset, n) = (get(&req, 0), get(&req, 8) as usize, get(&req, 12) as usize);
            result = -22;
            if op == 3 && offset == 0 && n == 0 && req[16..].iter().all(|b| *b == 0) {
                live[j] = false;
                result = 0;
            } else if op == 2 && n <= 16 && req[16..].iter().all(|b| *b == 0) {
                let data: &[u8] = match j {
                    0 => input,
                    1 => &stdout,
                    2 => &stderr,
                    _ => &child_output,
                };
                let start = offset.min(lengths[j]);
                let count = n.min(lengths[j] - start);
                reply[16..16 + count].copy_from_slice(&data[start..start + count]);
                result = count as i32;
                if cfg!(stream_pending) && j == 0 && n != 0 && !input_ready {
                    empty_observed = true;
                    reply[16..].fill(0);
                    result = if cfg!(pending_eof) { 0 } else { -11 };
                }
            } else if op == 4 && n <= 16 && req[16 + n..].iter().all(|b| *b == 0) {
                result = -13;
                if j != 0 {
                    let data: &mut [u8] = match j {
                        1 => &mut stdout,
                        2 => &mut stderr,
                        _ => &mut child_output,
                    };
                    result = -28;
                    let capacity = if cfg!(cat_roles) && j == 1 {
                        32
                    } else {
                        data.len()
                    };
                    if offset == lengths[j] && offset <= capacity && n <= capacity - offset {
                        if cfg!(stream_pending) && !empty_observed {
                            put(&mut reply, 0, (-11i32) as u32);
                            if !send(&reply) {
                                return 122;
                            }
                            continue;
                        }
                        data[offset..offset + n].copy_from_slice(&req[16..16 + n]);
                        lengths[j] += n;
                        result = n as i32;
                        input_ready = true;
                    }
                }
            }
        }
        put(&mut reply, 0, result as u32);
        #[cfg(inherit_backend_bad)]
        if !injected
            && get(&req, 0)
                == if cfg!(inherit_backend_close) {
                    3
                } else if cfg!(inherit_backend_write) {
                    4
                } else {
                    2
                }
            && result == if cfg!(inherit_backend_close) { 0 } else { 1 }
        {
            if cfg!(inherit_backend_incomplete) {
                // Short writes are permitted. Every pointer/length stays within
                // this live stack reply; no pointer survives the synchronous call.
                if cfg!(inherit_backend_partial) {
                    let mut sent = 0;
                    for _ in 0..256 {
                        let n = unsafe { bridge_write(reply.as_ptr().add(sent), 17 - sent) };
                        if n == -11 {
                            unsafe { bridge_yield() };
                            continue;
                        }
                        if n <= 0 || n as usize > 17 - sent {
                            return 122;
                        }
                        sent += n as usize;
                        if sent == 17 {
                            break;
                        }
                    }
                    if sent != 17 {
                        return 122;
                    }
                }
                loop {
                    unsafe { bridge_yield() };
                }
            }
            reply[4] = 1; // Deliberately uncertain backend reply, once per lifetime.
            injected = true;
        }
        if !send(&reply) {
            return 122;
        }
    }
}
