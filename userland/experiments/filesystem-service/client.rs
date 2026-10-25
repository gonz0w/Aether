// SPDX-License-Identifier: BSD-2-Clause
//! Capability-scoped AF07/08/09 client; authenticated provisioning is external.
#![no_std]
use filesystem_service::{put, word, Channel, Message, FRAME, MAGIC};

/// Build selection only; never peer negotiation or native authority.
pub const HOME_GRANTS: bool = cfg!(fs_home_wire);
const _: () = assert!(
    HOME_GRANTS == matches!(MAGIC, b"AFSRPC09"),
    "home client/service selection mismatch"
);
#[cfg(all(fs_home_wire, not(fs_directory_contexts)))]
compile_error!("fs_home_wire requires directory contexts");

#[cfg(all(fs_home_in_place, not(all(fs_home_wire, fs_in_place))))]
compile_error!("home in-place client requires home wire and in-place");

pub const MAX_READ: usize = 4096;
const SLOTS: usize = 16;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Invalid,
    Closed,
    Full,
    Protocol,
    Transport(i64),
    Remote(i64),
}
type Result<T> = core::result::Result<T, Error>;

/// Connection-scoped label, never native authority. Epochs must not be reused.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Handle {
    epoch: u64,
    token: u64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Directory,
    File,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Entry {
    pub handle: Handle,
    pub kind: Kind,
    pub size: u64,
}
#[derive(Clone, Copy)]
struct Binding {
    entry: Entry,
    rights: u8,
}
#[derive(Debug, PartialEq, Eq)]
pub struct ConnectFailure {
    pub error: Error,
    pub cleanup: [i64; 2],
}

/// Owns both endpoint-close obligations after entry, including bad provisioning.
/// Exclusive synchronous calls; no automatic reconnect, retransmit or live Owner.
/// Channel must bound each operation and close BOTH endpoints independently.
pub struct Client<T: Channel> {
    channel: T,
    epoch: u64,
    bindings: [Option<Binding>; SLOTS],
    next: u64,
    cleanup: Option<[i64; 2]>,
}
impl<T: Channel> Client<T> {
    pub fn connect(
        channel: T,
        epoch: u64,
        rights: u8,
    ) -> core::result::Result<Self, ConnectFailure> {
        let mut client = Self {
            channel,
            epoch,
            bindings: [None; SLOTS],
            next: 2,
            cleanup: None,
        };
        client.greet(rights)?;
        Ok(client)
    }

    fn greet(&mut self, rights: u8) -> core::result::Result<(), ConnectFailure> {
        let result = (|| {
            if cfg!(fs_home_wire)
                || self.epoch == 0
                || rights == 0
                || rights & !3 != 0
                || MAGIC
                    != if cfg!(fs_directory_contexts) {
                        b"AFSRPC08"
                    } else {
                        b"AFSRPC07"
                    }
            {
                return Err(Error::Invalid);
            }
            let frame = self.receive()?;
            self.status(&frame)?;
            let entry = self.entry(&frame, 1)?;
            if entry.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            self.bindings[0] = Some(Binding { entry, rights });
            Ok(())
        })();
        if let Err(error) = result {
            self.shutdown();
            // shutdown always records both close outcomes before returning.
            return Err(ConnectFailure {
                error,
                cleanup: self.cleanup.unwrap_or([-5; 2]),
            });
        }
        Ok(())
    }

    /// Initialize directly in exclusive uninitialized storage. On returned error
    /// both closes are attempted and the channel is dropped; Self is not usable.
    #[cfg(fs_in_place)]
    pub fn connect_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
        rights: u8,
    ) -> core::result::Result<&mut Self, ConnectFailure> {
        let client = Self::initialize_in_place(slot, channel, epoch, 2);
        if let Err(error) = client.greet(rights) {
            // SAFETY: every Client field is valid, greet already recorded both
            // close results, and no borrow escapes this failure. Drop T once.
            unsafe { core::ptr::drop_in_place(client) };
            return Err(error);
        }
        Ok(client)
    }

    // All fields are valid before this internal reference exists. Greeting
    // admission remains the public constructor's fallible publication boundary.
    #[cfg(fs_in_place)]
    fn initialize_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
        next: u64,
    ) -> &mut Self {
        let pointer = slot.as_mut_ptr();
        // SAFETY: exclusive aligned storage; raw projections form no Self
        // reference. Each array element and field is valid before publication.
        // Channel moves last, after infallible scalar writes; no owning field is
        // abandoned by a returned error. No padding is read as initialized bytes.
        unsafe {
            for index in 0..SLOTS {
                core::ptr::addr_of_mut!((*pointer).bindings)
                    .cast::<Option<Binding>>()
                    .add(index)
                    .write(None);
            }
            core::ptr::addr_of_mut!((*pointer).epoch).write(epoch);
            core::ptr::addr_of_mut!((*pointer).next).write(next);
            core::ptr::addr_of_mut!((*pointer).cleanup).write(None);
            core::ptr::addr_of_mut!((*pointer).channel).write(channel);
            slot.assume_init_mut()
        }
    }

    /// Trusted sole owner configures only its transport under exclusive admission.
    /// The callback cannot return a channel loan. No protocol operation, replay,
    /// authority change or reconnection is performed by this method.
    pub fn configure_channel(
        &mut self,
        configure: impl FnOnce(&mut T) -> Result<()>,
    ) -> Result<()> {
        self.active()?;
        configure(&mut self.channel)
    }
    fn active(&self) -> Result<()> {
        if self.cleanup.is_some() {
            Err(Error::Closed)
        } else {
            Ok(())
        }
    }
    fn shutdown(&mut self) {
        if self.cleanup.is_none() {
            self.bindings.fill(None);
            self.cleanup = Some(self.channel.close());
        }
    }
    fn fatal<R>(&mut self, error: Error) -> Result<R> {
        self.shutdown();
        Err(error)
    }
    /// Consume local endpoint obligations once, without a disconnect/replay.
    /// Does not establish server detach, export or native reclaim.
    pub fn abort(&mut self) -> [i64; 2] {
        self.shutdown();
        self.cleanup.unwrap_or([-5; 2])
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.cleanup
    }
    pub fn root(&self) -> Result<Handle> {
        self.active()?;
        self.bindings[0]
            .map(|b| b.entry.handle)
            .ok_or(Error::Closed)
    }
    fn binding(&self, handle: Handle) -> Result<(usize, Binding)> {
        self.active()?;
        self.bindings
            .iter()
            .enumerate()
            .find_map(|(i, b)| b.filter(|b| b.entry.handle == handle).map(|b| (i, b)))
            .ok_or(Error::Invalid)
    }
    fn request(&self, opcode: u64, token: u64) -> Message {
        let mut frame = [0; FRAME];
        frame[..8].copy_from_slice(MAGIC);
        put(&mut frame, 1, opcode);
        put(&mut frame, 2, self.epoch);
        put(&mut frame, 3, token);
        frame
    }
    fn send(&mut self, frame: &Message) -> Result<()> {
        match self.channel.send(frame) {
            Ok(()) => Ok(()),
            Err(code) => self.fatal(Error::Transport(code)),
        }
    }
    fn receive(&mut self) -> Result<Message> {
        let mut frame = [0; FRAME];
        match self.channel.receive(&mut frame) {
            Ok(()) => Ok(frame),
            Err(code) => self.fatal(Error::Transport(code)),
        }
    }
    fn status(&mut self, frame: &Message) -> Result<()> {
        if frame[..8] != MAGIC[..] || word(frame, 2) != self.epoch {
            return self.fatal(Error::Protocol);
        }
        let code = word(frame, 1) as i64;
        if code == 0 {
            return Ok(());
        }
        // The only nonzero error payload valid for these read-only operations
        // is the server's uncertain/invalid-completion marker3 on EIO.
        let uncertain = code == -5
            && word(frame, 6) == 3
            && frame[24..48].iter().all(|&b| b == 0)
            && frame[56..].iter().all(|&b| b == 0);
        if !(-i64::from(i32::MAX)..0).contains(&code)
            || (!uncertain && frame[24..].iter().any(|&b| b != 0))
        {
            return self.fatal(Error::Protocol);
        }
        if code == -5 || code == -9 {
            return self.fatal(Error::Remote(code));
        }
        Err(Error::Remote(code))
    }
    fn exchange(&mut self, frame: &Message) -> Result<Message> {
        self.send(frame)?;
        let reply = self.receive()?;
        self.status(&reply)?;
        Ok(reply)
    }
    fn entry(&mut self, frame: &Message, token: u64) -> Result<Entry> {
        let kind = match word(frame, 4) {
            1 => Kind::Directory,
            2 => Kind::File,
            _ => return self.fatal(Error::Protocol),
        };
        if word(frame, 3) != token || frame[48..].iter().any(|&b| b != 0) {
            return self.fatal(Error::Protocol);
        }
        Ok(Entry {
            handle: Handle {
                epoch: self.epoch,
                token,
            },
            kind,
            size: word(frame, 5),
        })
    }

    /// One component relative to a retained directory, attenuated to its grant.
    /// Old roots permit LOOKUP1/READ2; AF09 home also permits WRITE4/MUTATE_DIR8.
    pub fn lookup(&mut self, directory: Handle, name: &[u8], rights: u8) -> Result<Entry> {
        let (_, parent) = self.binding(directory)?;
        if parent.entry.kind != Kind::Directory
            || parent.rights & 1 == 0
            || rights == 0
            || rights & !parent.rights != 0
            || name.is_empty()
            || name.len() > 255
            || name == b"."
            || name == b".."
            || name.iter().any(|&b| b == 0 || b == b'/')
        {
            return Err(Error::Invalid);
        }
        let slot = self
            .bindings
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Full)?;
        let next = self.next.checked_add(1).ok_or(Error::Full)?;
        let mut request = self.request(1, directory.token);
        put(&mut request, 4, u64::from(rights));
        put(&mut request, 5, name.len() as u64);
        self.send(&request)?;
        for chunk in name.chunks(FRAME) {
            let mut frame = [0; FRAME];
            frame[..chunk.len()].copy_from_slice(chunk);
            self.send(&frame)?;
        }
        let reply = self.receive()?;
        self.status(&reply)?;
        let entry = self.entry(&reply, self.next)?;
        self.bindings[slot] = Some(Binding { entry, rights });
        self.next = next;
        Ok(entry)
    }
    pub fn stat(&mut self, handle: Handle) -> Result<Entry> {
        let (index, binding) = self.binding(handle)?;
        let reply = self.exchange(&self.request(6, handle.token))?;
        let entry = self.entry(&reply, handle.token)?;
        if entry.kind != binding.entry.kind {
            return self.fatal(Error::Protocol);
        }
        self.bindings[index] = Some(Binding { entry, ..binding });
        Ok(entry)
    }
    pub fn read(
        &mut self,
        handle: Handle,
        offset: u64,
        length: usize,
        out: &mut [u8; MAX_READ],
    ) -> Result<usize> {
        out.fill(0);
        let (_, binding) = self.binding(handle)?;
        if binding.entry.kind != Kind::File
            || binding.rights & 2 == 0
            || length > MAX_READ
            || offset
                .checked_add(length as u64)
                .is_none_or(|end| end > i64::MAX as u64)
        {
            return Err(Error::Invalid);
        }
        if length == 0 {
            return Ok(0);
        }
        let mut request = self.request(2, handle.token);
        put(&mut request, 4, offset);
        put(&mut request, 5, length as u64);
        let reply = self.exchange(&request)?;
        if word(&reply, 3) != 0
            || word(&reply, 4) != 0
            || word(&reply, 5) > length as u64
            || reply[48..].iter().any(|&b| b != 0)
        {
            return self.fatal(Error::Protocol);
        }
        let count = word(&reply, 5) as usize;
        let received = (|| {
            for offset in (0..count).step_by(FRAME) {
                let frame = self.receive()?;
                let bytes = (count - offset).min(FRAME);
                if frame[bytes..].iter().any(|&b| b != 0) {
                    return self.fatal(Error::Protocol);
                }
                out[offset..offset + bytes].copy_from_slice(&frame[..bytes]);
            }
            Ok(count)
        })();
        if received.is_err() {
            out.fill(0);
        }
        received
    }
    pub fn close(&mut self, handle: Handle) -> Result<()> {
        let (index, _) = self.binding(handle)?;
        if index == 0 || (cfg!(fs_home_wire) && index == 1) {
            return Err(Error::Invalid);
        }
        let reply = self.exchange(&self.request(3, handle.token));
        // Any failed final close leaves ownership unsuitable for continued use.
        let reply = match reply {
            Ok(value) => value,
            Err(error) => return self.fatal(error),
        };
        if reply[24..].iter().any(|&b| b != 0) {
            return self.fatal(Error::Protocol);
        }
        self.bindings[index] = None;
        Ok(())
    }
    /// After a validated disconnect acknowledgment, verify native export/channel
    /// quiescence under this exclusive borrow BEFORE closing either endpoint.
    /// The callback must not replay effects or reconnect. All outcomes close once;
    /// raw close results remain observable even when verification fails.
    pub fn disconnect_checked(
        &mut self,
        verify: impl FnOnce(&mut T) -> Result<()>,
    ) -> Result<[i64; 2]> {
        self.active()?;
        let result = (|| {
            let reply = self.exchange(&self.request(4, 0))?;
            if reply[24..].iter().any(|&b| b != 0) {
                return Err(Error::Protocol);
            }
            verify(&mut self.channel)
        })();
        self.shutdown();
        result?;
        Ok(self.cleanup.unwrap_or([-5; 2]))
    }
    pub fn disconnect(&mut self) -> Result<[i64; 2]> {
        self.active()?;
        let result = self.exchange(&self.request(4, 0));
        self.shutdown();
        let reply = result?;
        if reply[24..].iter().any(|&b| b != 0) {
            return Err(Error::Protocol);
        }
        // Both local results remain observable even when closure failed.
        Ok(self.cleanup.unwrap_or([-5; 2]))
    }
}
impl<T: Channel> Drop for Client<T> {
    fn drop(&mut self) {
        self.shutdown();
    }
}
#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "client-tests.rs"]
mod tests;

#[cfg(fs_paths)]
#[path = "paths.rs"]
mod paths;

#[cfg(fs_directory_contexts)]
#[path = "directory-context-client.rs"]
mod directory_context;

#[cfg(fs_directory_contexts)]
#[path = "directory-resolver.rs"]
mod directory_resolver;
#[cfg(fs_directory_contexts)]
pub use directory_resolver::ResolvedDirectory;

#[cfg(fs_home_wire)]
#[path = "home-client.rs"]
mod home_client;

#[cfg(fs_home_wire)]
#[path = "mutation-client.rs"]
mod mutation_client;
#[cfg(fs_home_wire)]
pub use mutation_client::{
    MutationCompletion, MutationFailure, MutationOutcome, MutationProgress, NamespaceMutation,
};
