// SPDX-License-Identifier: BSD-2-Clause
//! Private imported-root readiness wrapper, not a discovery or supervision API.
#![no_std]
#[cfg(not(fs_home_activation))]
use filesystem_policy::Rights;
use filesystem_policy::{Backend, Clock, Owner};
use filesystem_service::{word, Channel, Message, Report, MAGIC};

const _: () = assert!(
    !matches!(filesystem_service::MAGIC, b"AFSRPC09") || cfg!(fs_home_activation),
    "home service requires a separately integrated consumer"
);

#[cfg(not(fs_home_activation))]
struct Activated<T, P> {
    inner: T,
    publish: P,
    epoch: u64,
    first: bool,
    failed: bool,
}
#[cfg(not(fs_home_activation))]
impl<T: Channel, P: FnMut() -> i64> Channel for Activated<T, P> {
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        self.inner.receive(frame)
    }
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        if self.failed {
            return Err(-5);
        }
        if self.first {
            self.first = false;
            // Only the owner-generated validated-root greeting reaches here.
            // No peer input or merely linked object can publish readiness.
            if frame[..8] != MAGIC[..]
                || self.epoch == 0
                || word(frame, 1) != 0
                || word(frame, 2) != self.epoch
                || word(frame, 3) != 1
                || word(frame, 4) != 1
                || frame[48..].iter().any(|byte| *byte != 0)
            {
                self.failed = true;
                return Err(-22);
            }
            // A64-byte greeting on a32-byte queue needs a consuming client.
            // Publish validated-root readiness before waiting for that client.
            let status = (self.publish)();
            if status != 0 {
                self.failed = true;
                return Err(if status < 0 { status } else { -5 });
            }
        }
        let result = self.inner.send(frame);
        self.failed = result.is_err();
        result
    }
    fn close(&mut self) -> [i64; 2] {
        self.inner.close()
    }
}

/// Importer supplies the original owner, authenticated peer/epoch/rights and
/// a single scalar native-ready publication. No new authority is derived here.
/// Report.ready still means greeting completion, not retained kernel readiness.
/// Publication can precede greeting loss: consumers must reject terminal/stale
/// instances even when the retained ready bit remains set. No automatic replay.
#[cfg(not(fs_home_activation))]
pub fn run<B: Backend, C: Clock, T: Channel, P: FnMut() -> i64>(
    owner: Owner<B, C>,
    channel: T,
    peer: u64,
    rights: Rights,
    epoch: u64,
    publish: P,
) -> Report {
    filesystem_service::run(
        owner,
        Activated {
            inner: channel,
            publish,
            epoch,
            first: true,
            failed: false,
        },
        peer,
        rights,
        epoch,
    )
}

#[cfg(all(test, not(fs_home_activation)))]
#[path = "activation-tests.rs"]
mod tests;

#[cfg(fs_home_activation)]
#[path = "home-activation.rs"]
mod home;
#[cfg(fs_home_activation)]
pub use home::run_home;
#[cfg(fs_home_activation)]
const _: () = assert!(
    matches!(filesystem_service::MAGIC, b"AFSRPC09"),
    "home activation requires matching AFSRPC09 dependencies"
);
