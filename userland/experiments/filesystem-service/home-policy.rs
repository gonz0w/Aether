// SPDX-License-Identifier: BSD-2-Clause
//! Trusted home delegation within the existing owner connection/handle ledger.
use super::*;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HomeAttachment {
    pub session: Session,
    pub root: Entry,
    pub home: Entry,
}

impl<B: Backend, C: Clock> Owner<B, C> {
    /// Validate a live administrative source before bootstrap creates a file.
    /// No path/handle inequality can substitute for actual non-root identity.
    #[cfg(fs_home_native)]
    pub fn validate_home_source(
        &self,
        peer: u64,
        session: Session,
        handle: Handle,
    ) -> Result<(), Error> {
        let index = self.open(peer, session, handle)?;
        self.check_home(self.handles[index].ok_or(Error::Stale)?)
    }

    fn check_home(&self, home: Open) -> Result<(), Error> {
        if home.node.kind != Kind::Directory {
            return Err(Error::NotDirectory);
        }
        if home.node.identity() == self.root.identity() || !home.rights.contains(Rights::new(15)?) {
            return Err(Error::Denied);
        }
        Ok(())
    }

    /// Trusted administration only, never a client opcode. The caller supplies
    /// authenticated peer provenance. Owner administration grants system-root
    /// reads; the exact live source handle separately supplies home authority.
    /// No path, label or home handle implies authority to grant system access.
    /// Closing the source does not revoke these independent recipient handles.
    pub fn attach_home(
        &mut self,
        source_peer: u64,
        source_session: Session,
        home_handle: Handle,
        peer: u64,
    ) -> Result<HomeAttachment, Error> {
        let source = self.open(source_peer, source_session, home_handle)?;
        let home = self.handles[source].ok_or(Error::Stale)?;
        if peer == 0 {
            return Err(Error::Invalid);
        }
        self.check_home(home)?;
        let home_rights = Rights::new(15)?;
        let root_rights = Rights::new(3)?;
        let connection = self
            .connections
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Full)?;
        let mut free = self
            .handles
            .iter()
            .enumerate()
            .filter_map(|(index, handle)| handle.is_none().then_some(index));
        let root_slot = free.next().ok_or(Error::Full)?;
        let home_slot = free.next().ok_or(Error::Full)?;
        // Reserve all serials after capacity checks; publication below cannot
        // fail, call a provider or reenter this exclusively borrowed owner.
        let serial = self.issue(3)?;
        self.connections[connection] = Some(Connection { serial, peer });
        self.handles[root_slot] = Some(Open {
            serial: serial + 1,
            session: serial,
            node: self.root,
            rights: root_rights,
        });
        self.handles[home_slot] = Some(Open {
            serial: serial + 2,
            session: serial,
            node: home.node,
            rights: home_rights,
        });
        Ok(HomeAttachment {
            session: Session {
                epoch: self.epoch,
                serial,
            },
            root: self.entry(serial + 1, self.root),
            home: self.entry(serial + 2, home.node),
        })
    }
}
