// SPDX-License-Identifier: BSD-2-Clause
//! Metadata is observed through retained authority; labels confer no authority.
use super::*;

impl<B: Backend, C: Clock> Owner<B, C> {
    pub fn metadata(
        &mut self,
        peer: u64,
        session: Session,
        handle: Handle,
    ) -> Result<Metadata, Error> {
        let index = self.open(peer, session, handle)?;
        let opened = self.handles[index].ok_or(Error::Stale)?;
        if !opened.rights.contains(Rights::METADATA) {
            return Err(Error::Denied);
        }
        let result = self
            .backend
            .as_mut()
            .ok_or(Error::Closed)?
            .metadata(opened.node);
        let value = match result {
            Ok(value) => value,
            Err(error @ (Error::InvalidMetadata | Error::InvalidCompletion)) => {
                self.retire();
                return Err(error);
            }
            Err(error) => return Err(error),
        };
        let expected_mode = match opened.node.kind {
            Kind::Directory => 0o040000,
            Kind::File => 0o100000,
        };
        if (value.node.object, value.node.generation) != opened.node.identity()
            || value.node.mode & 0o170000 != expected_mode
            || value.node.size != opened.node.size
            || value.parent == 0
            || value.links == 0
            || value.flags & 1 != 0
            || [value.atime, value.mtime, value.ctime, value.birthtime]
                .iter()
                .any(|time| time.nanoseconds >= 1_000_000_000)
        {
            self.retire();
            return Err(Error::InvalidMetadata);
        }
        Ok(value)
    }
}
