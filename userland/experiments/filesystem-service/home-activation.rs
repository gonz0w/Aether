// SPDX-License-Identifier: BSD-2-Clause
//! One readiness publication after both home grants attach, before queue writes.
use super::*;
use filesystem_policy::{Handle, Session};

#[derive(Clone, Copy)]
enum Stage {
    Root,
    Home,
    Ready,
    Failed,
}
struct HomeActivated<T, P> {
    inner: T,
    publish: P,
    epoch: u64,
    stage: Stage,
}
impl<T: Channel, P: FnMut() -> i64> HomeActivated<T, P> {
    fn fail(&mut self, error: i64) -> Result<(), i64> {
        self.stage = Stage::Failed;
        Err(error)
    }
}
impl<T: Channel, P: FnMut() -> i64> Channel for HomeActivated<T, P> {
    #[cfg(fs_af09_drain)]
    fn af09_counts(&mut self, mutations: u64, requests: u64) -> Result<(), i64> {
        if !matches!(self.stage, Stage::Ready) {
            return self.fail(-5);
        }
        match self.inner.af09_counts(mutations, requests) {
            Ok(()) => Ok(()),
            Err(error) => self.fail(error),
        }
    }

    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        self.inner.receive(frame)
    }
    fn send(&mut self, frame: &Message) -> Result<(), i64> {
        let (token, next) = match self.stage {
            Stage::Root => (Some(1), Stage::Home),
            Stage::Home => (Some(2), Stage::Ready),
            Stage::Ready => (None, Stage::Ready),
            Stage::Failed => return Err(-5),
        };
        if let Some(token) = token {
            if frame[..8] != MAGIC[..]
                || self.epoch == 0
                || word(frame, 1) != 0
                || word(frame, 2) != self.epoch
                || word(frame, 3) != token
                || word(frame, 4) != 1
                || frame[48..].iter().any(|byte| *byte != 0)
            {
                return self.fail(-22);
            }
            if matches!(self.stage, Stage::Root) {
                // run_home attached BOTH grants before entering send. Publish
                // before the64-byte first frame waits on the32-byte native queue.
                let status = (self.publish)();
                if status != 0 {
                    return self.fail(if status < 0 { status } else { -5 });
                }
            }
        }
        match self.inner.send(frame) {
            Ok(()) => {
                self.stage = next;
                Ok(())
            }
            Err(error) => self.fail(error),
        }
    }
    fn close(&mut self) -> [i64; 2] {
        self.inner.close()
    }
}

/// Trusted importer supplies a live authorized source home and actual recipient
/// binding. Existing service delegation completes before the first callback.
/// The callback retains existing UTC/readiness policy and must be bounded,
/// nonreentrant and non-panicking. Publication does not complete either greeting;
/// Report.ready requires both sends. Later loss never authorizes replay/recovery.
// Mirror the existing seven producer parameters plus its readiness callback.
#[allow(clippy::too_many_arguments)]
pub fn run_home<B: Backend, C: Clock, T: Channel, P: FnMut() -> i64>(
    owner: Owner<B, C>,
    channel: T,
    source_peer: u64,
    source_session: Session,
    home: Handle,
    peer: u64,
    epoch: u64,
    publish: P,
) -> Report {
    filesystem_service::run_home(
        owner,
        HomeActivated {
            inner: channel,
            publish,
            epoch,
            stage: Stage::Root,
        },
        source_peer,
        source_session,
        home,
        peer,
        epoch,
    )
}

#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "home-activation-tests.rs"]
mod tests;
