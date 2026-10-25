// SPDX-License-Identifier: BSD-2-Clause
// Fixture identity and connection-scoped cwd follow AECAT003, not path lookup.
use super::*;
pub fn bootstrap(source: Connection, boot: &mut [u8; 128], generation: u32) {
    boot[..8].copy_from_slice(b"AECAT003");
    send(source, boot);
    let mut identity = [0; 32];
    for i in 0..4 {
        put(&mut identity, i * 4, 1000);
    }
    put(&mut identity, 16, 1);
    send(source, &mut identity);
    let mut cwd = [0; 32];
    for (i, value) in [0x76030000 + generation, 1, 1, generation]
        .iter()
        .enumerate()
    {
        put(&mut cwd, i * 4, *value);
    }
    send(source, &mut cwd);
    boot[..8].copy_from_slice(b"AECAT001");
}
pub fn directory_reply(source: Connection, request: &[u8; 32], generation: u32) {
    let op = get(request, 0);
    let reference = get(request, 4);
    let n = get(request, 12) as usize;
    let mut reply = [0; 32];
    let result: i32 = if get(request, 8) != 3 {
        -13
    } else if reference != 0x76030000 + generation {
        if generation > 1 && reference == 0x76030000 + generation - 1 {
            -9
        } else {
            -13
        }
    } else if op == 4 {
        if n != 0 || request[16..] != [0; 16] {
            -22
        } else {
            reply[16..22].copy_from_slice(b"/work\0");
            6
        }
    } else if n > 15 {
        -36
    } else if n == 0
        || request[16..16 + n].contains(&0)
        || request[16 + n..].iter().any(|b| *b != 0)
    {
        -22
    } else if &request[16..16 + n] == b"." || &request[16..16 + n] == b"/work" {
        put(&mut reply, 16, 100 + generation);
        put(&mut reply, 20, 1);
        put(&mut reply, 24, 0o40500);
        0
    } else if request[16] == b'/' || &request[16..16 + n] == b".." {
        -13
    } else {
        -2
    };
    put(&mut reply, 0, result as u32);
    send(source, &mut reply);
}
