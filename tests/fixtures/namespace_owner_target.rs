// SPDX-License-Identifier: BSD-2-Clause
//! Unlinked native compilation/layout probe, not an original-ZPL provider.
#![no_std]

#[path = "../../user/storage/namespace.rs"]
pub mod namespace;
use namespace::{Backend, Error, Kind, MAX_READ, Node, Owner, Rights};

pub struct Fixture;
impl Backend for Fixture {
    fn root(&mut self) -> Result<Node, Error> {
        Ok(Node::new(34, 45, 1, Kind::Directory))
    }
    fn lookup(&mut self, _directory: Node, name: &[u8]) -> Result<Node, Error> {
        if name == b"file" {
            Ok(Node::new(2, 47, 64, Kind::File))
        } else {
            Err(Error::Backend(2))
        }
    }
    fn read(&mut self, _file: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error> {
        let count = 64u64.saturating_sub(offset).min(buffer.len() as u64) as usize;
        buffer[..count].fill(17);
        Ok(count)
    }
}

const _: () = assert!(core::mem::size_of::<Owner<Fixture>>() <= 2048);
const _: () = assert!(core::mem::align_of::<Owner<Fixture>>() == 8);

#[unsafe(no_mangle)]
pub static NAMESPACE_OWNER_LAYOUT: [u64; 4] = [
    core::mem::size_of::<Owner<Fixture>>() as u64,
    core::mem::align_of::<Owner<Fixture>>() as u64,
    core::mem::size_of::<namespace::Session>() as u64,
    core::mem::size_of::<namespace::Handle>() as u64,
];

// Rust ABI probe, not an exported service or C client contract. Instantiate the
// optimized owner against this explicitly synthetic provider for native codegen.
#[unsafe(no_mangle)]
pub fn namespace_owner_compile(
    peer: u64,
    offset: u64,
    length: usize,
    reply: &mut [u8; MAX_READ],
) -> Result<usize, Error> {
    let mut owner = Owner::new(Fixture, 1)?;
    let attachment = owner.attach(peer, Rights::ALL)?;
    let file = owner.lookup(
        peer,
        attachment.session,
        attachment.root.handle,
        b"file",
        Rights::READ,
    )?;
    let result = owner.read(peer, attachment.session, file.handle, offset, length, reply);
    owner.close(peer, attachment.session, file.handle)?;
    owner.disconnect(peer, attachment.session)?;
    owner.shutdown();
    result
}
