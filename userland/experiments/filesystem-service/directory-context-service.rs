// SPDX-License-Identifier: BSD-2-Clause
//! AF08 parent/path calls share existing scratch and authenticated token state.
use super::*;

pub(super) fn request<B: Backend, C: Clock>(
    binding: &mut Binding,
    owner: &mut Owner<B, C>,
    raw: &Message,
    body: &mut [u8; MAX_READ],
) -> Result<Message, Error> {
    body.fill(0);
    if !matches!(word(raw, 1), 13 | 14)
        || raw[..8] != MAGIC[..]
        || word(raw, 2) != binding.epoch
        || raw[32..].iter().any(|b| *b != 0)
    {
        return Err(Error::Invalid);
    }
    let token = binding
        .tokens
        .iter()
        .flatten()
        .find(|token| token.id == word(raw, 3))
        .copied()
        .ok_or(Error::Stale)?;
    let mut path = [0; 256];
    if word(raw, 1) == 14 {
        let (_, length) = owner.directory_context(
            binding.peer,
            binding.attachment.session,
            token.handle,
            &mut path,
        )?;
        body[..length].copy_from_slice(&path[..length]);
        let mut reply = message(binding.epoch, 0);
        put(&mut reply, 5, length as u64);
        return Ok(reply);
    }
    let free = if token.id == 1 {
        None
    } else {
        Some(
            binding
                .tokens
                .iter()
                .position(Option::is_none)
                .ok_or(Error::Full)?,
        )
    };
    let next = if token.id == 1 {
        binding.next
    } else {
        binding.next.checked_add(1).ok_or(Error::Full)?
    };
    let entry = owner.parent_directory(
        binding.peer,
        binding.attachment.session,
        token.handle,
        &mut path,
    )?;
    if entry.handle == binding.attachment.root.handle {
        return Ok(binding.entry(1, entry));
    }
    let free = free.ok_or(Error::InvalidMetadata)?;
    let id = binding.next;
    binding.next = next;
    binding.tokens[free] = Some(Token {
        id,
        handle: entry.handle,
    });
    Ok(binding.entry(id, entry))
}
