// SPDX-License-Identifier: BSD-2-Clause
//! Two fixed grants from trusted owner provisioning; never request-selected.
use super::*;

/// Consumes the owner and both endpoint-close obligations. Source grants remain
/// in the existing ledger until owner shutdown; no extra capacity is implied.
/// The caller authenticates both peers and supplies a nonreused service epoch.
pub fn run_home<B: Backend, C: Clock, T: Channel>(
    owner: Owner<B, C>,
    channel: T,
    source_peer: u64,
    source_session: filesystem_policy::Session,
    home: Handle,
    peer: u64,
    epoch: u64,
) -> Report {
    bulk::names::run_bound(owner, channel, epoch, |owner| {
        if epoch == 0 {
            return Err(Error::Invalid);
        }
        let delegated = owner.attach_home(source_peer, source_session, home, peer)?;
        let mut tokens = [None; MAX_HANDLES];
        tokens[0] = Some(Token {
            id: 1,
            handle: delegated.root.handle,
        });
        tokens[1] = Some(Token {
            id: 2,
            handle: delegated.home.handle,
        });
        Ok((
            Binding {
                peer,
                epoch,
                attachment: filesystem_policy::Attachment {
                    session: delegated.session,
                    root: delegated.root,
                },
                tokens,
                next: 3,
                disconnected: false,
            },
            Some(delegated.home),
        ))
    })
}
