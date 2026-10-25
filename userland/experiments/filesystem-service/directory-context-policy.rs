// SPDX-License-Identifier: BSD-2-Clause
//! Root-constrained physical context observations over retained directory rights.
use super::*;

pub fn valid_path(path: &[u8]) -> bool {
    path.len() >= 2
        && path.len() <= 256
        && path[0] == b'/'
        && path.last() == Some(&0)
        && !path[..path.len() - 1].contains(&0)
        && (path == b"/\0"
            || path[1..path.len() - 1]
                .split(|b| *b == b'/')
                .all(|part| !part.is_empty() && part != b"." && part != b".."))
}
impl<B: Backend, C: Clock> Owner<B, C> {
    pub fn directory_context(
        &mut self,
        peer: u64,
        session: Session,
        handle: Handle,
        out: &mut [u8; 256],
    ) -> Result<(Node, usize), Error> {
        out.fill(0);
        let index = self.open(peer, session, handle)?;
        let opened = self.handles[index].ok_or(Error::Stale)?;
        if !opened.rights.contains(Rights::LOOKUP) || !opened.rights.contains(Rights::READ) {
            return Err(Error::Denied);
        }
        if opened.node.kind != Kind::Directory {
            return Err(Error::NotDirectory);
        }
        let result = self
            .backend
            .as_mut()
            .ok_or(Error::Closed)?
            .directory_context(self.root, opened.node, out);
        let result = result.and_then(|(parent, length)| {
            if !parent.valid()
                || parent.kind != Kind::Directory
                || length > out.len()
                || !valid_path(&out[..length])
                || out[length..].iter().any(|b| *b != 0)
                || ((out[..length] == *b"/\0") != (opened.node.identity() == self.root.identity()))
                || (opened.node.identity() == self.root.identity()
                    && parent.identity() != self.root.identity())
            {
                return Err(Error::InvalidMetadata);
            }
            Ok((parent, length))
        });
        if let Err(error) = result {
            out.fill(0);
            if matches!(error, Error::InvalidMetadata | Error::InvalidCompletion) {
                self.retire();
            }
        }
        result
    }
    pub fn parent_directory(
        &mut self,
        peer: u64,
        session: Session,
        handle: Handle,
        out: &mut [u8; 256],
    ) -> Result<Entry, Error> {
        let index = self.open(peer, session, handle)?;
        let current = self.handles[index].ok_or(Error::Stale)?;
        let root = self
            .handles
            .iter()
            .flatten()
            .find(|open| {
                open.session == session.serial && open.node.identity() == self.root.identity()
            })
            .copied()
            .ok_or(Error::Stale)?;
        // A non-root parent needs a slot unless it resolves to the root. Reserve
        // conservatively before any provider operation, without spending serials.
        let free = if current.node.identity() == self.root.identity() {
            None
        } else {
            Some(
                self.handles
                    .iter()
                    .position(Option::is_none)
                    .ok_or(Error::Full)?,
            )
        };
        if self.next_serial == 0 {
            return Err(Error::Full);
        }
        let (parent, _) = self.directory_context(peer, session, handle, out)?;
        if parent.identity() == self.root.identity() {
            return Ok(self.entry(root.serial, parent));
        }
        let free = free.ok_or(Error::InvalidMetadata)?;
        let serial = self.issue(1)?;
        self.handles[free] = Some(Open {
            serial,
            session: session.serial,
            node: parent,
            rights: Rights::new(3)?,
        });
        Ok(self.entry(serial, parent))
    }
}
