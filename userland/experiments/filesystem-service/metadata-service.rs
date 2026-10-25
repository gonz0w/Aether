// SPDX-License-Identifier: BSD-2-Clause
//! AF07 copied metadata, explicit little-endian fields, no backend identities.
use super::*;

pub(super) fn request<B: Backend, C: Clock>(
    binding: &Binding,
    owner: &mut Owner<B, C>,
    raw: &Message,
    body: &mut [u8; MAX_READ],
) -> Result<Message, Error> {
    body.fill(0);
    if raw[..8] != MAGIC[..] || raw[32..].iter().any(|byte| *byte != 0) {
        return Err(Error::Invalid);
    }
    if word(raw, 2) != binding.epoch {
        return Err(Error::Stale);
    }
    let token = binding
        .tokens
        .iter()
        .flatten()
        .find(|token| token.id == word(raw, 3))
        .ok_or(Error::Stale)?;
    let value = owner.metadata(binding.peer, binding.attachment.session, token.handle)?;
    // Fixed raw observations: no narrowing, POSIX interpretation or authority.
    let values = [
        value.node.size,
        value.node.mode,
        value.links,
        value.uid,
        value.gid,
        value.flags,
        value.atime.seconds as u64,
        value.atime.nanoseconds,
        value.mtime.seconds as u64,
        value.mtime.nanoseconds,
        value.ctime.seconds as u64,
        value.ctime.nanoseconds,
        value.birthtime.seconds as u64,
        value.birthtime.nanoseconds,
    ];
    for (index, field) in values.iter().enumerate() {
        body[index * 8..index * 8 + 8].copy_from_slice(&field.to_le_bytes());
    }
    let mut reply = message(binding.epoch, 0);
    put(&mut reply, 5, 112);
    Ok(reply)
}
