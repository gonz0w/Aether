// SPDX-License-Identifier: BSD-2-Clause
//! AF05 names borrow the existing bulk scratch; never retain client buffers.
use super::*;
#[cfg(fs_directory_contexts)]
#[path = "directory-context-service.rs"]
mod directory_context_service;
#[cfg(fs_metadata)]
#[path = "metadata-service.rs"]
mod metadata_service;

pub(super) fn lengths(binding: &Binding, raw: &Message) -> Result<(usize, usize), Error> {
    if raw[..8] != MAGIC[..] || raw[48..].iter().any(|byte| *byte != 0) {
        return Err(Error::Invalid);
    }
    if word(raw, 2) != binding.epoch {
        return Err(Error::Stale);
    }
    let opcode = word(raw, 1);
    let first = word(raw, 5) as u32 as usize;
    let second = (word(raw, 5) >> 32) as usize;
    if first == 0
        || first > 255
        || second > 255
        || (opcode == 8) != (second != 0)
        || first.checked_add(second).is_none_or(|total| total > 510)
        || (opcode != 1 && word(raw, 4) != 0)
    {
        return Err(Error::Invalid);
    }
    Ok((first, second))
}

pub(super) fn request<B: Backend, C: Clock>(
    binding: &mut Binding,
    owner: &mut Owner<B, C>,
    raw: &Message,
    body: &[u8; MAX_READ],
    (first, second): (usize, usize),
) -> Result<Message, Error> {
    // Header and the complete padded body are validated by the sole caller.
    // Policy validates both lexical names before any provider effect.
    let handle = binding
        .tokens
        .iter()
        .flatten()
        .find(|token| token.id == word(raw, 3))
        .ok_or(Error::Stale)?
        .handle;
    let name = &body[..first];
    if word(raw, 1) == 1 {
        let bits = u8::try_from(word(raw, 4)).map_err(|_| Error::Invalid)?;
        let slot = binding
            .tokens
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Full)?;
        let next = binding.next.checked_add(1).ok_or(Error::Full)?;
        let entry = owner.lookup(
            binding.peer,
            binding.attachment.session,
            handle,
            name,
            Rights::new(bits)?,
        )?;
        let id = binding.next;
        binding.next = next;
        binding.tokens[slot] = Some(Token {
            id,
            handle: entry.handle,
        });
        return Ok(binding.entry(id, entry));
    }
    let operation = match word(raw, 1) {
        #[cfg(fs_directories)]
        10 => filesystem_policy::Mutation::MakeDirectory(name),
        #[cfg(fs_directories)]
        11 => filesystem_policy::Mutation::RemoveDirectory(name),
        7 => filesystem_policy::Mutation::Create(name),
        8 => filesystem_policy::Mutation::Rename(name, &body[first..first + second]),
        9 => filesystem_policy::Mutation::Remove(name),
        _ => return Err(Error::Invalid),
    };
    let value = owner.namespace(binding.peer, binding.attachment.session, handle, operation)?;
    let mut reply = message(binding.epoch, 0);
    put(&mut reply, 4, value.txg);
    put(&mut reply, 6, value.state);
    Ok(reply)
}

/// AF05 loop; shares original checked data/frame helpers without changing AF04.
#[cfg(not(fs_home_wire))]
pub fn run<B: Backend, C: Clock, T: Channel>(
    owner: Owner<B, C>,
    channel: T,
    peer: u64,
    rights: Rights,
    epoch: u64,
) -> Report {
    run_bound(owner, channel, epoch, |owner| {
        Binding::new(owner, peer, rights, epoch).map(|binding| (binding, None))
    })
}

pub(crate) fn run_bound<B: Backend, C: Clock, T: Channel>(
    mut owner: Owner<B, C>,
    mut channel: T,
    epoch: u64,
    provision: impl FnOnce(&mut Owner<B, C>) -> Result<(Binding, Option<Entry>), Error>,
) -> Report {
    let mut ready = false;
    let mut requests = 0usize;
    let mut last_write = None;
    let mut body = [0; MAX_READ];
    let stop = (|| {
        let (mut binding, home) = match provision(&mut owner) {
            Ok(value) => value,
            Err(error) => return Stop::Provision(error),
        };
        if let Err(code) = channel.send(&binding.entry(1, binding.attachment.root)) {
            return Stop::ReplyLost(code);
        }
        if let Some(home) = home {
            if let Err(code) = channel.send(&binding.entry(2, home)) {
                return Stop::ReplyLost(code);
            }
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
            } else if matches!(opcode, 1 | 3 | 4 | 6..=9)
                || (cfg!(fs_directories) && matches!(opcode, 10 | 11))
                || (cfg!(fs_metadata) && opcode == 12)
                || (cfg!(fs_directory_contexts) && matches!(opcode, 13 | 14))
            {
                0
            } else {
                if let Err(code) = channel.send(&failure(epoch, Error::Invalid)) {
                    return Stop::ReplyLost(code);
                }
                return Stop::Receive(-22);
            };
            let names = if matches!(opcode, 1 | 7..=9)
                || (cfg!(fs_directories) && matches!(opcode, 10 | 11))
            {
                match self::lengths(&binding, &raw) {
                    Ok(lengths) => Some(lengths),
                    Err(error) => {
                        let rejection = failure(epoch, error);
                        if let Err(code) = channel.send(&rejection) {
                            return Stop::ReplyLost(code);
                        }
                        return Stop::Receive(word(&rejection, 1) as i64);
                    }
                }
            } else {
                None
            };
            if let Some((first, second)) = names {
                if let Err(code) = receive_body(&mut channel, &mut body, first + second) {
                    return Stop::Receive(code);
                }
            }
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
            let reply = if cfg!(fs_directory_contexts) && matches!(opcode, 13 | 14) {
                #[cfg(fs_directory_contexts)]
                {
                    directory_context_service::request(&mut binding, &mut owner, &raw, &mut body)
                        .unwrap_or_else(|error| failure(epoch, error))
                }
                #[cfg(not(fs_directory_contexts))]
                {
                    failure(epoch, Error::Invalid)
                }
            } else if cfg!(fs_metadata) && opcode == 12 {
                #[cfg(fs_metadata)]
                {
                    metadata_service::request(&binding, &mut owner, &raw, &mut body)
                        .unwrap_or_else(|error| failure(epoch, error))
                }
                #[cfg(not(fs_metadata))]
                {
                    failure(epoch, Error::Invalid)
                }
            } else if data {
                data_request(&binding, &mut owner, &raw, &mut body, length)
                    .unwrap_or_else(|error| failure(epoch, error))
            } else {
                if let Some(lengths) = names {
                    self::request(&mut binding, &mut owner, &raw, &body, lengths)
                        .unwrap_or_else(|error| failure(epoch, error))
                } else {
                    binding.request(&mut owner, &raw)
                }
            };
            let dispatched = owner.mutation_attempts() != before;
            if dispatched
                || ((opcode == 5
                    || (7..=if cfg!(fs_directories) { 11 } else { 9 }).contains(&opcode))
                    && (word(&reply, 6) != 0 || word(&reply, 5) != 0))
            {
                last_write = Some(filesystem_policy::Completion {
                    error: (-(word(&reply, 1) as i64)) as i32,
                    txg: word(&reply, 4),
                    bytes_staged: word(&reply, 5),
                    state: word(&reply, 6),
                });
            }
            #[cfg(fs_af09_drain)]
            if binding.disconnected && word(&reply, 1) == 0 {
                if let Err(code) =
                    channel.af09_counts(owner.mutation_attempts() as u64, requests as u64)
                {
                    return Stop::ReplyLost(code);
                }
            }
            if let Err(code) = channel.send(&reply) {
                return Stop::ReplyLost(code);
            }
            if (opcode == 2
                || (cfg!(fs_metadata) && opcode == 12)
                || (cfg!(fs_directory_contexts) && opcode == 14))
                && word(&reply, 1) == 0
            {
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
