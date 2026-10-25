// SPDX-License-Identifier: BSD-2-Clause
//! Bounded ABI29 activation policy. Native admission remains kernel-authorized.
pub type Status = (i64, u64, u64);

pub trait Kernel {
    fn ctl(&mut self, op: u64, handle: u64) -> Status;
    fn channel(&mut self) -> Status;
    fn engine(&mut self, reader: u64, writer: u64) -> i64;
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64;
    fn process(&mut self, arguments: &[u8; 272]) -> i64;
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], write: bool) -> i64;
}

#[derive(Debug, PartialEq, Eq)]
pub struct Failed;
type Result<T> = core::result::Result<T, Failed>;
fn require(ok: bool) -> Result<()> {
    if ok { Ok(()) } else { Err(Failed) }
}
fn positive(value: i64) -> Result<u64> {
    require(value > 0)?;
    Ok(value as u64)
}
fn step(k: &mut impl Kernel, remaining: &mut u32) -> Result<()> {
    require(*remaining != 0)?;
    *remaining -= 1;
    require(k.ctl(0x1fffe, 0).0 == 0)
}
fn transfer(
    k: &mut impl Kernel,
    endpoint: u64,
    frame: &mut [u8],
    write: bool,
    remaining: &mut u32,
) -> Result<()> {
    let mut used = 0;
    let mut attempts = 100_000;
    while used < frame.len() {
        require(attempts != 0)?;
        attempts -= 1;
        step(k, remaining)?;
        let end = (used + 16).min(frame.len());
        let n = k.transfer(endpoint, &mut frame[used..end], write);
        if n == -11 {
            continue;
        }
        require(n > 0 && n as usize <= end - used)?;
        used += n as usize;
    }
    Ok(())
}
fn word(frame: &[u8; 64], n: usize) -> u64 {
    u64::from_le_bytes(frame[n * 8..n * 8 + 8].try_into().unwrap())
}
fn header(frame: &[u8; 64], generation: u64) -> Result<()> {
    require(&frame[..8] == b"AFSRPC06" && word(frame, 1) == 0 && word(frame, 2) == generation)
}
fn terminal(k: &mut impl Kernel, handle: u64, remaining: &mut u32) -> Result<()> {
    loop {
        step(k, remaining)?;
        let state = k.ctl(0x20001, handle);
        if state.0 == 0 {
            continue;
        }
        // rax is exit_status+1; rdx is the retained ready bit, not exit detail.
        // A normal engine exit may retain ready1. Only kind1/status0 can clean.
        return require(state.0 == 1 && state.2 == 1);
    }
}
fn reclaim(k: &mut impl Kernel, handle: u64) -> Result<()> {
    require(k.ctl(0x20002, handle).0 == 0)?;
    require(k.ctl(0x20001, handle).0 == -9)
}

/// On error do not infer cleanup or reuse any acquired handle. Native caller
/// fails stop; host callers retain their mock state for inspection.
pub fn run(k: &mut impl Kernel, boot: [u64; 6], mut remaining: u32) -> Result<()> {
    require(
        boot[0] == 29
            && boot[1] == 0xa001
            && boot[2] == 0xf101
            && boot[3] == 0xc002
            && boot[4] == 0xd001
            && boot[5] == 0xc003,
    )?;
    let request = k.channel();
    let reader = positive(request.0)?;
    let send = request.1;
    require(send != 0 && send != reader)?;
    let reply = k.channel();
    let receive = positive(reply.0)?;
    let writer = reply.1;
    require(
        writer != 0
            && writer != receive
            && receive != reader
            && writer != reader
            && send != receive
            && send != writer,
    )?;
    let engine = positive(k.engine(reader, writer))?;
    require(k.delegate(engine, &[8, 2097152, 7]) == 0)?;
    loop {
        step(k, &mut remaining)?;
        let state = k.ctl(0x20001, engine);
        require(state.0 == 0 && state.1 <= 1)?;
        if state.1 == 1 {
            break;
        }
    }
    let mut frame = [0; 64];
    transfer(k, receive, &mut frame, false, &mut remaining)?;
    header(&frame, reader)?;
    require(word(&frame, 3) == 1 && word(&frame, 4) == 1 && frame[48..].iter().all(|b| *b == 0))?;
    // Recheck the retained instance; never accept a terminal's old ready bit.
    let state = k.ctl(0x20001, engine);
    require(state.0 == 0 && state.1 == 1)?;
    // Immutable selected argv avoids runtime initialization and mutable statics.
    const ARGUMENTS: [u8; 272] = {
        let mut bytes = [0; 272];
        bytes[0] = 1;
        bytes[16] = b'p';
        bytes
    };
    let process = positive(k.process(&ARGUMENTS))?;
    require(process != engine)?;
    terminal(k, process, &mut remaining)?;
    reclaim(k, process)?;
    // No new dependent admission past this point. One disconnect, no replay.
    frame.fill(0);
    frame[..8].copy_from_slice(b"AFSRPC06");
    frame[8..16].copy_from_slice(&4u64.to_le_bytes());
    frame[16..24].copy_from_slice(&reader.to_le_bytes());
    transfer(k, send, &mut frame, true, &mut remaining)?;
    frame.fill(0);
    transfer(k, receive, &mut frame, false, &mut remaining)?;
    header(&frame, reader)?;
    require(frame[24..].iter().all(|b| *b == 0))?;
    terminal(k, engine, &mut remaining)?;
    let mut byte = [0];
    require(k.transfer(receive, &mut byte, false) == 0)?;
    require(k.transfer(send, &mut byte, true) == -32)?;
    require(k.ctl(0x24003, send).0 == 0)?;
    require(k.ctl(0x24003, receive).0 == 0)?;
    reclaim(k, engine)?;
    require(k.ctl(0x26002, 0xf001).0 == 0)?;
    // Successful native halt does not return. Any return is a failure.
    k.ctl(0x2a002, 0xf002);
    Err(Failed)
}

#[cfg(test)]
#[path = "tests.rs"]
mod tests;
