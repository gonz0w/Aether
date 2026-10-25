// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#[cfg(scratch_backend)]
mod scratch;
unsafe extern "C" {
    fn bridge_read(p: *mut u8, n: usize) -> i64;
    fn bridge_write(p: *const u8, n: usize) -> i64;
    fn bridge_yield();
    fn bridge_close_output() -> i64;
    fn bridge_abort() -> !;
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { bridge_abort() }
}
fn get(b: &[u8; 32], i: usize) -> u32 {
    u32::from_le_bytes([b[i], b[i + 1], b[i + 2], b[i + 3]])
}
fn put(b: &mut [u8; 32], i: usize, v: u32) {
    b[i..i + 4].copy_from_slice(&v.to_le_bytes());
}
fn receive(b: &mut [u8; 32]) -> i32 {
    let mut n = 0;
    for _ in 0..100000 {
        let r = unsafe { bridge_read(b.as_mut_ptr().add(n), 32 - n) };
        if r == -11 {
            unsafe { bridge_yield() };
            continue;
        }
        if r == 0 {
            return if n == 0 { 0 } else { -1 };
        }
        if r < 0 || r as usize > 32 - n {
            return -1;
        }
        n += r as usize;
        if n == 32 {
            return 1;
        }
    }
    -1
}
fn send(b: &[u8; 32]) -> bool {
    let mut n = 0;
    for _ in 0..100000 {
        let r = unsafe { bridge_write(b.as_ptr().add(n), 32 - n) };
        if r == -11 {
            unsafe { bridge_yield() };
            continue;
        }
        if r <= 0 || r as usize > 32 - n {
            return false;
        }
        n += r as usize;
        if n == 32 {
            return true;
        }
    }
    false
}
fn bytes(index: usize) -> &'static [u8] {
    if cfg!(command_runner) && index == 0 {
        if cfg!(empty_input) { b"" } else { b"abcdef" }
    } else if index == 0 {
        b"printf 'hello\\n'\n"
    } else {
        b"hello from Aether\n"
    }
}
#[unsafe(no_mangle)]
pub extern "C" fn file_service() -> i32 {
    #[cfg(shell_console)]
    if cfg!(shell_console) {
        return console::run();
    }
    if cfg!(runner_streams) {
        return streams::run();
    }
    let mut opened = [false; 2];
    let mut generation = [0u32; 2];
    let mut file = [0usize; 2];
    let mut rights = [0u32; 2];
    let mut scratch = [0u8; 64];
    let mut scratch_len = 0usize;
    let mut scratch_name = [0u8; 16];
    let mut exists = false;
    let writable = cfg!(writable);
    let mut hello = [0u8; 32];
    put(&mut hello, 4, 0xf001);
    if writable {
        put(&mut hello, 8, 0xf002);
    }
    if !send(&hello) {
        return 120;
    }
    loop {
        let mut req = [0u8; 32];
        let got = receive(&mut req);
        if got == 0 {
            return 0;
        }
        if got < 0 {
            return 121;
        }
        let (op, handle, offset, len) = (get(&req, 0), get(&req, 4), get(&req, 8), get(&req, 12));
        let mut reply = [0u8; 32];
        let mut result: i32 = -22;
        if op == 1 || (writable && op == 5) {
            let write_root = writable && handle == 0xf002;
            if handle != 0xf001 && !write_root {
                result = -13;
            } else if (len != 1 && len != 3)
                || (len == 3 && !write_root)
                || (op == 5 && (!write_root || len != 3))
            {
                result = -13;
            } else if offset == 0 {
                if let Some(end) = req[16..].iter().position(|b| *b == 0) {
                    let name = &req[16..16 + end];
                    if !name.is_empty()
                        && name != b"."
                        && name != b".."
                        && !name.contains(&b'/')
                        && req[16 + end..].iter().all(|b| *b == 0)
                    {
                        let which = if name == b"hello.sh" {
                            Some(0)
                        } else if name == b"message.txt" {
                            Some(1)
                        } else if exists && req[16..] == scratch_name {
                            Some(2)
                        } else {
                            None
                        };
                        result = -2;
                        if op == 5 && which.is_some() {
                            result = -17;
                        } else if op == 5 && exists {
                            result = -28;
                        } else if which.is_some() || op == 5 {
                            let which = which.unwrap_or(2);
                            result = -13;
                            if which == 2 || len == 1 {
                                result = -24;
                                if let Some(slot) =
                                    (0..2).find(|i| !opened[*i] && generation[*i] < 3)
                                {
                                    if op == 5 {
                                        scratch_name.copy_from_slice(&req[16..]);
                                        scratch.fill(0);
                                        scratch_len = 0;
                                        exists = true;
                                    }
                                    opened[slot] = true;
                                    generation[slot] += 1;
                                    file[slot] = which;
                                    rights[slot] = len;
                                    put(
                                        &mut reply,
                                        4,
                                        0xf1000000 | (generation[slot] << 8) | (slot as u32 + 1),
                                    );
                                    put(
                                        &mut reply,
                                        8,
                                        if which == 2 {
                                            scratch_len as u32
                                        } else {
                                            bytes(which).len() as u32
                                        },
                                    );
                                    result = 0;
                                }
                            }
                        }
                    }
                }
            }
        } else if (2..=4).contains(&op) || (writable && op == 6) {
            let slot = (0..2).find(|i| {
                opened[*i] && handle == (0xf1000000 | (generation[*i] << 8) | (*i as u32 + 1))
            });
            result = -9;
            if let Some(slot) = slot {
                result = -22;
                if op == 4 || op == 6 {
                    if !writable {
                        if op == 4 && offset == 0 && len == 0 && req[16..].iter().all(|b| *b == 0) {
                            result = -13;
                        }
                    } else if file[slot] != 2 || (rights[slot] != 3 && !cfg!(ignore_write_rights)) {
                        result = -13;
                    } else if op == 4
                        && len <= 16
                        && req[16 + len as usize..].iter().all(|b| *b == 0)
                    {
                        result = -28;
                        if offset <= 64 && len <= 64 - offset {
                            if len > 0 {
                                let start = offset as usize;
                                let end = start + len as usize;
                                if start > scratch_len {
                                    scratch[scratch_len..start].fill(0);
                                }
                                scratch[start..end].copy_from_slice(&req[16..16 + len as usize]);
                                scratch_len = scratch_len.max(end);
                            }
                            result = len as i32;
                        }
                    } else if op == 6 && len == 0 && req[16..].iter().all(|b| *b == 0) {
                        result = -28;
                        if offset <= 64 {
                            let next = offset as usize;
                            #[cfg(not(skip_truncate_zero))]
                            scratch[next.min(scratch_len)..next.max(scratch_len)].fill(0);
                            scratch_len = next;
                            result = 0;
                        }
                    }
                } else if req[16..].iter().all(|b| *b == 0) {
                    if op == 2 && len <= 16 {
                        let data = if file[slot] == 2 {
                            &scratch[..scratch_len]
                        } else {
                            bytes(file[slot])
                        };
                        let start = (offset as usize).min(data.len());
                        let n = (len as usize).min(data.len() - start);
                        reply[16..16 + n].copy_from_slice(&data[start..start + n]);
                        #[cfg(wrong_data)]
                        if n > 0 {
                            reply[16] ^= 1;
                        }
                        result = n as i32;
                    } else if op == 3 && offset == 0 && len == 0 {
                        opened[slot] = false;
                        result = 0;
                    }
                }
            }
        }
        put(&mut reply, 0, result as u32);
        // Selected fixture mutation occurs after the operation has taken effect.
        if cfg!(shell_bad_reply)
            && op
                == if cfg!(shell_bad_read) {
                    2
                } else if cfg!(shell_bad_close) {
                    3
                } else {
                    1
                }
        {
            if cfg!(shell_reply_silent) {
                if cfg!(shell_reply_late) {
                    // Request EOF is a post-timeout phase witness, never another operation.
                    let mut byte = 0u8;
                    loop {
                        let n = unsafe { bridge_read(&mut byte, 1) };
                        if n == 0 {
                            break;
                        }
                        if n != -11 {
                            return 125;
                        }
                        unsafe { bridge_yield() };
                    }
                    if !send(&reply) {
                        return 124;
                    }
                }
                loop {
                    unsafe { bridge_yield() };
                }
            }
            if cfg!(shell_reply_eof) {
                // The hello has been consumed and this service is the only writer.
                // The synchronous trap borrows exactly16 initialized stack bytes.
                if cfg!(shell_reply_half) && unsafe { bridge_write(reply.as_ptr(), 16) } != 16 {
                    return 124;
                }
                if unsafe { bridge_close_output() } != 0 {
                    return 124;
                }
                // EOF closes delivery, not the service lifetime. The owner must stop us.
                loop {
                    unsafe { bridge_yield() };
                }
            }
            reply[12] = 1;
        }
        if !send(&reply) {
            return 122;
        }
    }
}

#[path = "streams.rs"]
mod streams;

#[cfg(shell_console)]
mod console;
