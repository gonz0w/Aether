// SPDX-License-Identifier: BSD-2-Clause
//! Separately selected bounded AF04 data bodies; one serialized connection.
use super::*;

/// Structural data framing is checked before any provider call. Policy denial
/// on a complete structurally valid body is canonical and may continue; malformed
/// framing cannot be resynchronized into another command.
fn data_length(binding: &Binding, raw: &Message) -> Result<usize, Error> {
    if raw[..8] != MAGIC[..] || raw[48..].iter().any(|b| *b != 0) {
        return Err(Error::Invalid);
    }
    if word(raw, 2) != binding.epoch {
        return Err(Error::Stale);
    }
    let length = usize::try_from(word(raw, 5)).map_err(|_| Error::Invalid)?;
    if length == 0
        || length > MAX_READ
        || word(raw, 4)
            .checked_add(length as u64)
            .is_none_or(|end| end > i64::MAX as u64)
    {
        return Err(Error::Invalid);
    }
    Ok(length)
}

fn receive_body<T: Channel>(
    channel: &mut T,
    body: &mut [u8; MAX_READ],
    length: usize,
) -> Result<(), i64> {
    body.fill(0);
    for offset in (0..length).step_by(FRAME) {
        let mut frame = [0; FRAME];
        if let Err(code) = channel.receive(&mut frame) {
            body.fill(0);
            return Err(code);
        }
        let count = (length - offset).min(FRAME);
        if frame[count..].iter().any(|b| *b != 0) {
            body.fill(0);
            return Err(-22);
        }
        body[offset..offset + count].copy_from_slice(&frame[..count]);
    }
    Ok(())
}

fn send_body<T: Channel>(channel: &mut T, body: &[u8]) -> Result<(), i64> {
    for chunk in body.chunks(FRAME) {
        let mut frame = [0; FRAME];
        frame[..chunk.len()].copy_from_slice(chunk);
        channel.send(&frame)?;
    }
    Ok(())
}

fn data_request<B: Backend, C: Clock>(
    binding: &Binding,
    owner: &mut Owner<B, C>,
    raw: &Message,
    body: &mut [u8; MAX_READ],
    length: usize,
) -> Result<Message, Error> {
    let token = binding
        .tokens
        .iter()
        .flatten()
        .find(|token| token.id == word(raw, 3))
        .ok_or(Error::Stale)?;
    let mut reply = message(binding.epoch, 0);
    if word(raw, 1) == 2 {
        body.fill(0);
        let count = owner.read(
            binding.peer,
            binding.attachment.session,
            token.handle,
            word(raw, 4),
            length,
            body,
        )?;
        put(&mut reply, 5, count as u64);
    } else {
        let value = owner.write(
            binding.peer,
            binding.attachment.session,
            token.handle,
            word(raw, 4),
            &body[..length],
        )?;
        put(&mut reply, 4, value.assigned_txg.unwrap_or(0));
        put(&mut reply, 5, value.bytes as u64);
        put(
            &mut reply,
            6,
            if value.assigned_txg.is_some() { 2 } else { 0 },
        );
    }
    Ok(reply)
}

/// Same trusted SPA/peer/rights/epoch ownership as the legacy run entry. Only
/// this candidate consumes AF04 body frames; no data becomes another request.
pub fn run<B: Backend, C: Clock, T: Channel>(
    mut owner: Owner<B, C>,
    mut channel: T,
    peer: u64,
    rights: Rights,
    epoch: u64,
) -> Report {
    let mut ready = false;
    let mut requests = 0usize;
    let mut last_write = None;
    let mut body = [0; MAX_READ];
    let stop = (|| {
        let mut binding = match Binding::new(&mut owner, peer, rights, epoch) {
            Ok(value) => value,
            Err(error) => return Stop::Provision(error),
        };
        if let Err(code) = channel.send(&binding.entry(1, binding.attachment.root)) {
            return Stop::ReplyLost(code);
        }
        ready = true;
        for _ in 0..REQUESTS {
            let mut raw = [0; FRAME];
            if let Err(code) = channel.receive(&mut raw) {
                return Stop::Receive(code);
            }
            let opcode = word(&raw, 1);
            let data = matches!(opcode, 2 | 5);
            let length = if data {
                match data_length(&binding, &raw) {
                    Ok(length) => length,
                    Err(error) => {
                        let rejection = failure(epoch, error);
                        if let Err(code) = channel.send(&rejection) {
                            return Stop::ReplyLost(code);
                        }
                        return Stop::Receive(word(&rejection, 1) as i64);
                    }
                }
            } else if matches!(opcode, 1 | 3 | 4 | 6..=9) {
                0
            } else {
                if let Err(code) = channel.send(&failure(epoch, Error::Invalid)) {
                    return Stop::ReplyLost(code);
                }
                return Stop::Receive(-22);
            };
            if opcode == 5 {
                if let Err(code) = receive_body(&mut channel, &mut body, length) {
                    return Stop::Receive(code);
                }
            }
            // Check before provider effects; no report/counter can wrap even at
            // representation exhaustion in the separately selected runtime.
            requests = match requests.checked_add(1) {
                Some(value) => value,
                None => return Stop::Limit,
            };
            let before = owner.mutation_attempts();
            let reply = if data {
                data_request(&binding, &mut owner, &raw, &mut body, length)
                    .unwrap_or_else(|error| failure(epoch, error))
            } else {
                binding.request(&mut owner, &raw)
            };
            let dispatched = owner.mutation_attempts() != before;
            if dispatched
                || ((opcode == 5 || (7..=9).contains(&opcode))
                    && (word(&reply, 6) != 0 || word(&reply, 5) != 0))
            {
                last_write = Some(filesystem_policy::Completion {
                    error: (-(word(&reply, 1) as i64)) as i32,
                    txg: word(&reply, 4),
                    bytes_staged: word(&reply, 5),
                    state: word(&reply, 6),
                });
            }
            if let Err(code) = channel.send(&reply) {
                return Stop::ReplyLost(code);
            }
            if opcode == 2 && word(&reply, 1) == 0 {
                if let Err(code) = send_body(&mut channel, &body[..word(&reply, 5) as usize]) {
                    return Stop::ReplyLost(code);
                }
            }
            body.fill(0);
            if word(&reply, 1) != 0 && word(&reply, 6) != 0 {
                return Stop::Retired;
            }
            if owner.namespace_finished() {
                return if word(&reply, 1) == 0 {
                    Stop::NamespaceComplete
                } else {
                    Stop::Retired
                };
            }
            if binding.disconnected {
                return Stop::Disconnected;
            }
        }
        Stop::Limit
    })();
    body.fill(0);
    #[cfg(fs_home_native)]
    let mutation_attempts = owner.mutation_attempts();
    owner.shutdown();
    Report {
        stop,
        ready,
        requests,
        cleanup: channel.close(),
        last_write,
        #[cfg(fs_home_native)]
        mutation_attempts,
    }
}

#[cfg(fs_names)]
#[path = "names-service.rs"]
pub(super) mod names;
