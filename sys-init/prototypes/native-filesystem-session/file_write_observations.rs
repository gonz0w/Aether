// SPDX-License-Identifier: BSD-2-Clause
//! Mutation completion and reply delivery are independent owned observations.
use super::*;
use filesystem_fd_protocol::FileWriteReceipt;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ObservedWrite {
    pub process: Process,
    pub receipt: FileWriteReceipt,
}
/// Retain with the authenticated endpoint/holder association. A completed source
/// write can coexist with failed delivery; neither cleanup tuple settles native
/// instances or authorizes replay/recovery. This is a normal-return contract;
/// callbacks must remain bounded and non-panicking.
#[must_use = "retain mutation observation and delivery/cleanup separately"]
#[derive(Debug, PartialEq, Eq)]
pub struct Exchange {
    pub observation: Option<ObservedWrite>,
    pub delivery: Result<(), Error>,
    pub cleanup: Option<[i64; 2]>,
}
impl<C: Channel> Peer<C> {
    fn observed_result(
        &self,
        observation: Option<ObservedWrite>,
        delivery: Result<(), Error>,
    ) -> Exchange {
        Exchange {
            observation,
            delivery,
            cleanup: self.cleanup(),
        }
    }
    pub fn serve_one_observed<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        workspace: &mut [u8; MAX_READ],
    ) -> Exchange {
        workspace.fill(0);
        if self.cleanup.is_some() {
            return self.observed_result(None, Err(Error::Closed));
        }
        let mut header = [0; FRAME];
        if let Err(error) = self.channel.receive(&mut header) {
            let delivery = self.fail(files, workspace, Error::Transport(error));
            return self.observed_result(None, delivery);
        }
        self.serve_received_observed(files, &header, workspace)
    }
    /// Header came from THIS authenticated channel under exclusive admission.
    /// Typed receipts, including local NotSent, are copied before any reply send.
    /// Return the copy even after guard/source/peer retirement and uncertain sends.
    pub fn serve_received_observed<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        header: &[u8; FRAME],
        workspace: &mut [u8; MAX_READ],
    ) -> Exchange {
        let mut observation = None;
        let delivery = self.serve_inner(files, header, workspace, &mut observation);
        self.observed_result(observation, delivery)
    }
}
