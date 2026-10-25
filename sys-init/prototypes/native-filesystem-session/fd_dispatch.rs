// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! One complete selected FILE exchange on an authenticated peer channel.
use filesystem_fd_protocol::{Connection, Error as ProtocolError, FRAME};
pub use filesystem_fd_protocol::{FILE_SLOTS_16, MAGIC};
use filesystem_remote_descriptors::{MAX_READ, Process, ProcessFiles};
use filesystem_service::Channel;

// Build selection only. Old sealed protocols need no new symbol or method.
const _: () = assert!(
    cfg!(fs_file_write_wire) == matches!(filesystem_fd_protocol::MAGIC, b"AEFW0001"),
    "FILE peer requires an explicit matched write-observation selection"
);

#[cfg(fs_file_write_wire)]
#[path = "file_write_observations.rs"]
mod observations;
#[cfg(fs_file_write_wire)]
pub use observations::{Exchange, ObservedWrite};

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    Closed,
    Transport(i64),
    Protocol(ProtocolError),
}
#[derive(Debug, PartialEq, Eq)]
pub struct BindError {
    pub cause: ProtocolError,
    pub cleanup: [i64; 2],
}

pub struct Peer<C: Channel> {
    channel: C,
    connection: Connection,
    cleanup: Option<[i64; 2]>,
}
impl<C: Channel> Peer<C> {
    /// Actual image receipt/CLOEXEC settlement must precede this trusted call.
    /// Retain the same sole endpoint obligations; no Drop/reconnect or replay.
    pub fn rebind_after_exec(&mut self, process: Process, generation: u64) -> Result<(), Error> {
        if self.cleanup.is_some() {
            return Err(Error::Closed);
        }
        self.connection
            .rebind_after_exec(process, generation)
            .map_err(Error::Protocol)
    }
    /// Caller authenticates admission/holder/channel and nonreused generation.
    /// This takes both channel-close obligations, including failed binding.
    pub fn bind(mut channel: C, process: Process, generation: u64) -> Result<Self, BindError> {
        match Connection::bind(process, generation) {
            Ok(connection) => Ok(Self {
                channel,
                connection,
                cleanup: None,
            }),
            Err(cause) => Err(BindError {
                cause,
                cleanup: channel.close(),
            }),
        }
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.cleanup
    }
    /// Scoped access for the trusted mixed-channel router, under Owner admission.
    /// It neither rebinds Process/generation nor authenticates an endpoint. Safe
    /// callback borrows cannot escape; closure effects/partial progress are owned
    /// by the caller and must fail-stop rather than replay another protocol.
    pub fn with_channel<R>(&mut self, operation: impl FnOnce(&mut C) -> R) -> Result<R, Error> {
        if self.cleanup.is_some() {
            return Err(Error::Closed);
        }
        Ok(operation(&mut self.channel))
    }
    /// Local endpoint closure only; caller separately settles process/file view.
    pub fn close(&mut self) -> [i64; 2] {
        if let Some(result) = self.cleanup {
            return result;
        }
        let result = self.channel.close();
        self.cleanup = Some(result);
        result
    }
    fn fail<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        workspace: &mut [u8; MAX_READ],
        error: Error,
    ) -> Result<(), Error> {
        workspace.fill(0);
        self.connection.abort(files);
        self.close();
        Err(error)
    }
    #[cfg(not(fs_file_write_wire))]
    pub fn serve_one<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        workspace: &mut [u8; MAX_READ],
    ) -> Result<(), Error> {
        workspace.fill(0);
        if self.cleanup.is_some() {
            return Err(Error::Closed);
        }
        let mut header = [0; FRAME];
        if let Err(error) = self.channel.receive(&mut header) {
            return self.fail(files, workspace, Error::Transport(error));
        }
        self.serve_received(files, &header, workspace)
    }
    /// A complete64-byte header already received on THIS authenticated channel
    /// under exclusive routing admission. The unchanged Connection validates all
    /// fields before body reads/effects; this does not accept caller-selected keys.
    #[cfg(not(fs_file_write_wire))]
    pub fn serve_received<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        header: &[u8; FRAME],
        workspace: &mut [u8; MAX_READ],
    ) -> Result<(), Error> {
        self.serve_inner(files, header, workspace)
    }
    fn serve_inner<T: Channel>(
        &mut self,
        files: &mut ProcessFiles<T>,
        header: &[u8; FRAME],
        workspace: &mut [u8; MAX_READ],
        #[cfg(fs_file_write_wire)] observation: &mut Option<ObservedWrite>,
    ) -> Result<(), Error> {
        workspace.fill(0);
        if self.cleanup.is_some() {
            return Err(Error::Closed);
        }
        let needed = match self.connection.input_length(files, header) {
            Ok(needed) => needed,
            Err(error) => return self.fail(files, workspace, Error::Protocol(error)),
        };
        if needed > MAX_READ || !needed.is_multiple_of(FRAME) {
            return self.fail(files, workspace, Error::Protocol(ProtocolError::Protocol));
        }
        for chunk in workspace[..needed].as_chunks_mut::<FRAME>().0 {
            if let Err(error) = self.channel.receive(chunk) {
                return self.fail(files, workspace, Error::Transport(error));
            }
        }
        // Keep the guard until every response byte is confirmed. Its Drop also
        // retires unknown outcomes; the failure path below handles peer endpoints.
        #[cfg(fs_file_write_wire)]
        let process = self.connection.bound_process();
        let result = match self.connection.prepare(files, header, needed, workspace) {
            Err(error) => Err(Error::Protocol(error)),
            Ok(reply) => {
                #[cfg(fs_file_write_wire)]
                {
                    *observation = reply
                        .write_receipt()
                        .map(|receipt| ObservedWrite { process, receipt });
                }
                let sent = (|| {
                    self.channel
                        .send(reply.header())
                        .map_err(Error::Transport)?;
                    for chunk in reply.body().as_chunks::<FRAME>().0 {
                        self.channel.send(chunk).map_err(Error::Transport)?;
                    }
                    Ok(())
                })();
                if sent.is_ok() {
                    reply.delivered();
                } else {
                    drop(reply);
                }
                sent
            }
        };
        match result {
            Ok(()) => {
                #[cfg(fs_file_write_wire)]
                if files.cleanup().is_some() {
                    self.close();
                }
                Ok(())
            }
            Err(error) => self.fail(files, workspace, error),
        }
    }
}
impl<C: Channel> Drop for Peer<C> {
    fn drop(&mut self) {
        self.close();
    }
}
