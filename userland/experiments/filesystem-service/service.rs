// SPDX-License-Identifier: BSD-2-Clause
//! Private bounded AFSRPC01 connection. Transport identity is trusted provisioning.
#![no_std]
use filesystem_policy::{
    Backend, Clock, Entry, Error, Handle, Kind, Owner, Rights, MAX_HANDLES, MAX_READ,
};

#[cfg(all(fs_wait, not(all(fs_namespace, fs_lifetimes, fs_mixed))))]
compile_error!("fs_wait requires the separate mixed service selection");

#[cfg(all(fs_af09_drain, fs_home_probe_three))]
compile_error!("AF09 drain is incompatible with fs_home_probe_three");
#[cfg(all(
    fs_af09_drain,
    not(all(
        fs_namespace,
        fs_lifetimes,
        fs_mixed,
        fs_wait,
        fs_bulk,
        fs_runtime,
        fs_activation,
        fs_names,
        fs_directories,
        fs_metadata,
        fs_directory_contexts,
        fs_home,
        fs_home_wire,
        fs_home_native,
        fs_home_activation
    ))
))]
compile_error!("AF09 drain requires the complete HOME feature closure");

pub const FRAME: usize = 64;
pub const PAYLOAD: usize = 16;
pub const REQUESTS: usize = if cfg!(fs_home_native) {
    96
} else if cfg!(fs_runtime) {
    usize::MAX
} else {
    64
};
#[cfg(fs_home_native)]
const _: () = assert!(filesystem_policy::MUTATION_LIMIT == 9);
#[cfg(not(fs_namespace))]
pub const MAGIC: &[u8; 8] = b"AFSRPC01";
#[cfg(all(fs_namespace, not(fs_mixed)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC02";
#[cfg(all(fs_mixed, not(fs_bulk)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC03";
#[cfg(all(fs_bulk, not(fs_names)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC04";
#[cfg(all(fs_runtime, not(fs_bulk)))]
compile_error!("fs_runtime requires the separate bulk wait selection");
#[cfg(all(fs_bulk, not(all(fs_wait, fs_mixed, fs_namespace, fs_lifetimes))))]
compile_error!("fs_bulk requires the separate mixed-wait selection");
pub type Message = [u8; FRAME];
pub mod channel;

/// Complete-frame operations only. An error may follow partial transfer. The
/// implementation must discard partial input, never replay output, and return
/// boundedly. close attempts BOTH endpoint closes, preserving both outcomes.
pub trait Channel {
    /// Actual selected disconnect counters, before ACK; never a protocol frame.
    #[cfg(fs_af09_drain)]
    fn af09_counts(&mut self, mutations: u64, requests: u64) -> Result<(), i64>;
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64>;
    fn send(&mut self, frame: &Message) -> Result<(), i64>;
    fn close(&mut self) -> [i64; 2];
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stop {
    Disconnected,
    Provision(Error),
    Receive(i64),
    ReplyLost(i64),
    Retired,
    Limit,
    #[cfg(fs_namespace)]
    NamespaceComplete,
}

/// A clean disconnect requires both closes to succeed as well. Ready means the
/// complete greeting was transferred, not supervisor acceptance or durability.
#[derive(Debug, PartialEq, Eq)]
pub struct Report {
    pub stop: Stop,
    pub ready: bool,
    pub requests: usize,
    pub cleanup: [i64; 2],
    pub last_write: Option<filesystem_policy::Completion>,
    /// Includes bootstrap and request-loop attempts in the same Owner ledger.
    #[cfg(fs_home_native)]
    pub mutation_attempts: usize,
}

pub fn word(frame: &Message, index: usize) -> u64 {
    // Every caller uses a constant index0..7 in a fixed64-byte frame.
    u64::from_le_bytes(frame[index * 8..index * 8 + 8].try_into().unwrap())
}

pub fn put(frame: &mut Message, index: usize, value: u64) {
    frame[index * 8..index * 8 + 8].copy_from_slice(&value.to_le_bytes());
}

pub fn message(epoch: u64, operation: u64) -> Message {
    let mut frame = [0; FRAME];
    frame[..8].copy_from_slice(MAGIC);
    put(&mut frame, 1, operation);
    put(&mut frame, 2, epoch);
    frame
}

fn failure(epoch: u64, error: Error) -> Message {
    let code = match error {
        #[cfg(fs_metadata)]
        Error::Unsupported => 95,
        Error::Invalid => 22,
        Error::Denied => 13,
        Error::Stale | Error::Closed => 9,
        Error::Full | Error::WriteLimit => 28,
        Error::NotDirectory => 20,
        Error::IsDirectory => 21,
        Error::Backend(code) if code > 0 => i64::from(code),
        Error::WriteFailed(value) => i64::from(value.error),
        _ => 5,
    };
    let mut reply = message(epoch, (-code) as u64);
    match error {
        Error::WriteFailed(value) => {
            put(&mut reply, 4, value.txg);
            put(&mut reply, 5, value.bytes_staged);
            put(&mut reply, 6, value.state);
        }
        Error::Uncertain | Error::InvalidCompletion => put(&mut reply, 6, 3),
        _ => (),
    }
    reply
}

#[derive(Clone, Copy)]
struct Token {
    id: u64,
    handle: Handle,
}

struct Binding {
    peer: u64,
    epoch: u64,
    attachment: filesystem_policy::Attachment,
    tokens: [Option<Token>; MAX_HANDLES],
    next: u64,
    disconnected: bool,
}

impl Binding {
    fn new<B: Backend, C: Clock>(
        owner: &mut Owner<B, C>,
        peer: u64,
        rights: Rights,
        epoch: u64,
    ) -> Result<Self, Error> {
        if epoch == 0 {
            return Err(Error::Invalid);
        }
        let attachment = owner.attach(peer, rights)?;
        let mut tokens = [None; MAX_HANDLES];
        tokens[0] = Some(Token {
            id: 1,
            handle: attachment.root.handle,
        });
        Ok(Self {
            peer,
            epoch,
            attachment,
            tokens,
            next: 2,
            disconnected: false,
        })
    }

    fn entry(&self, id: u64, entry: Entry) -> Message {
        let mut reply = message(self.epoch, 0);
        put(&mut reply, 3, id);
        put(
            &mut reply,
            4,
            if entry.kind == Kind::Directory { 1 } else { 2 },
        );
        put(&mut reply, 5, entry.size);
        reply
    }

    fn request<B: Backend, C: Clock>(&mut self, owner: &mut Owner<B, C>, raw: &Message) -> Message {
        self.execute(owner, raw)
            .unwrap_or_else(|e| failure(self.epoch, e))
    }

    fn execute<B: Backend, C: Clock>(
        &mut self,
        owner: &mut Owner<B, C>,
        raw: &Message,
    ) -> Result<Message, Error> {
        if raw[..8] != MAGIC[..] {
            return Err(Error::Invalid);
        }
        if word(raw, 2) != self.epoch {
            return Err(Error::Stale);
        }
        let opcode = word(raw, 1);
        if opcode == 4 {
            if raw[24..].iter().any(|b| *b != 0) {
                return Err(Error::Invalid);
            }
            owner.disconnect(self.peer, self.attachment.session)?;
            self.disconnected = true;
            return Ok(message(self.epoch, 0));
        }
        #[cfg(fs_names)]
        if matches!(opcode, 1 | 7..=9) {
            // Named requests must pass complete body framing in bulk::run.
            return Err(Error::Invalid);
        }
        let index = self
            .tokens
            .iter()
            .position(|t| t.is_some_and(|t| t.id == word(raw, 3)))
            .ok_or(Error::Stale)?;
        let handle = self.tokens[index].ok_or(Error::Stale)?.handle;
        let session = self.attachment.session;
        let mut reply = message(self.epoch, 0);
        match opcode {
            1 => {
                let length = usize::try_from(word(raw, 5)).map_err(|_| Error::Invalid)?;
                let bits = u8::try_from(word(raw, 4)).map_err(|_| Error::Invalid)?;
                if length == 0 || length > PAYLOAD || raw[48 + length..].iter().any(|b| *b != 0) {
                    return Err(Error::Invalid);
                }
                let slot = self
                    .tokens
                    .iter()
                    .position(Option::is_none)
                    .ok_or(Error::Full)?;
                let next = self.next.checked_add(1).ok_or(Error::Full)?;
                let entry = owner.lookup(
                    self.peer,
                    session,
                    handle,
                    &raw[48..48 + length],
                    Rights::new(bits)?,
                )?;
                let id = self.next;
                self.next = next;
                self.tokens[slot] = Some(Token {
                    id,
                    handle: entry.handle,
                });
                Ok(self.entry(id, entry))
            }
            #[cfg(not(fs_bulk))]
            2 | 5 => {
                let length = usize::try_from(word(raw, 5)).map_err(|_| Error::Invalid)?;
                if length > PAYLOAD
                    || raw[48 + if opcode == 5 { length } else { 0 }..]
                        .iter()
                        .any(|b| *b != 0)
                {
                    return Err(Error::Invalid);
                }
                if opcode == 2 {
                    let mut bytes = [0; MAX_READ];
                    let count =
                        owner.read(self.peer, session, handle, word(raw, 4), length, &mut bytes)?;
                    put(&mut reply, 5, count as u64);
                    reply[48..48 + count].copy_from_slice(&bytes[..count]);
                } else {
                    let written = owner.write(
                        self.peer,
                        session,
                        handle,
                        word(raw, 4),
                        &raw[48..48 + length],
                    )?;
                    put(&mut reply, 4, written.assigned_txg.unwrap_or(0));
                    put(&mut reply, 5, written.bytes as u64);
                    put(
                        &mut reply,
                        6,
                        if written.assigned_txg.is_some() { 2 } else { 0 },
                    );
                }
                Ok(reply)
            }
            3 | 6 => {
                if raw[32..].iter().any(|b| *b != 0) {
                    return Err(Error::Invalid);
                }
                if opcode == 3 {
                    owner.close(self.peer, session, handle)?;
                    self.tokens[index] = None;
                    Ok(reply)
                } else {
                    Ok(self.entry(word(raw, 3), owner.stat(self.peer, session, handle)?))
                }
            }
            #[cfg(fs_namespace)]
            7..=9 => {
                let length = word(raw, 5) as u32 as usize;
                let second = (word(raw, 5) >> 32) as usize;
                if word(raw, 4) != 0
                    || length == 0
                    || length > PAYLOAD
                    || second > PAYLOAD
                    || length + second > PAYLOAD
                    || (opcode == 8) != (second > 0)
                    || raw[48 + length + second..].iter().any(|b| *b != 0)
                {
                    return Err(Error::Invalid);
                }
                let name = &raw[48..48 + length];
                let operation = match opcode {
                    7 => filesystem_policy::Mutation::Create(name),
                    8 => filesystem_policy::Mutation::Rename(
                        name,
                        &raw[48 + length..48 + length + second],
                    ),
                    _ => filesystem_policy::Mutation::Remove(name),
                };
                let result = owner.namespace(self.peer, session, handle, operation)?;
                put(&mut reply, 4, result.txg);
                put(&mut reply, 6, result.state);
                Ok(reply)
            }
            _ => Err(Error::Invalid),
        }
    }
}

/// Trusted caller supplies retained authenticated endpoint identity, attenuated
/// rights and a nonreused service generation. No request selects these values.
/// This function consumes the owner: no path can return a replayable context.
#[cfg(not(fs_bulk))]
pub fn run<B: Backend, C: Clock, T: Channel>(
    mut owner: Owner<B, C>,
    mut channel: T,
    peer: u64,
    rights: Rights,
    epoch: u64,
) -> Report {
    let mut ready = false;
    let mut requests = 0;
    let mut last_write = None;
    let stop = (|| {
        let mut binding = match Binding::new(&mut owner, peer, rights, epoch) {
            Ok(value) => value,
            Err(error) => return Stop::Provision(error),
        };
        if let Err(code) = channel.send(&binding.entry(1, binding.attachment.root)) {
            return Stop::ReplyLost(code);
        }
        ready = true;
        for _ in 0..REQUESTS {
            let mut raw = [0; FRAME];
            if let Err(code) = channel.receive(&mut raw) {
                return Stop::Receive(code);
            }
            requests += 1;
            #[cfg(fs_mixed)]
            let before = owner.mutation_attempts();
            let reply = binding.request(&mut owner, &raw);
            #[cfg(fs_mixed)]
            let dispatched = owner.mutation_attempts() != before;
            #[cfg(not(fs_mixed))]
            let dispatched = false;
            if dispatched
                || ((word(&raw, 1) == 5
                    || (cfg!(fs_namespace) && (7..=9).contains(&word(&raw, 1))))
                    && (word(&reply, 6) != 0 || word(&reply, 5) != 0))
            {
                last_write = Some(filesystem_policy::Completion {
                    error: (-(word(&reply, 1) as i64)) as i32,
                    txg: word(&reply, 4),
                    bytes_staged: word(&reply, 5),
                    state: word(&reply, 6),
                });
            }
            if let Err(code) = channel.send(&reply) {
                return Stop::ReplyLost(code);
            }
            if word(&reply, 1) != 0 && word(&reply, 6) != 0 {
                return Stop::Retired;
            }
            #[cfg(fs_namespace)]
            if owner.namespace_finished() {
                return if word(&reply, 1) == 0 {
                    Stop::NamespaceComplete
                } else {
                    Stop::Retired
                };
            }
            if binding.disconnected {
                return Stop::Disconnected;
            }
        }
        Stop::Limit
    })();
    // Revoke ALL aliases and consume C context before releasing either endpoint.
    // This also handles complete or partial reply loss after any backend effect.
    #[cfg(fs_home_native)]
    let mutation_attempts = owner.mutation_attempts();
    owner.shutdown();
    Report {
        stop,
        ready,
        requests,
        cleanup: channel.close(),
        last_write,
        #[cfg(fs_home_native)]
        mutation_attempts,
    }
}

#[cfg(test)]
extern crate std;
#[cfg(all(test, not(fs_home_wire)))]
#[path = "service-tests.rs"]
mod tests;

#[cfg(fs_bulk)]
#[cfg_attr(
    fs_names,
    expect(
        dead_code,
        reason = "Retain the old AF04 run verbatim; AF05 shares its checked body/data helpers."
    )
)]
#[path = "bulk-service.rs"]
mod bulk;
#[cfg(all(fs_names, not(fs_home_wire)))]
pub use bulk::names::run;
#[cfg(all(fs_bulk, not(fs_names)))]
pub use bulk::run;
#[cfg(all(fs_names, not(fs_directories)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC05";
#[cfg(all(fs_names, not(fs_activation)))]
compile_error!("fs_names requires the separate activation selection");

#[cfg(all(fs_directories, not(fs_metadata)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC06";
#[cfg(all(fs_metadata, not(fs_directory_contexts)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC07";

#[cfg(all(fs_directory_contexts, not(fs_metadata)))]
compile_error!("fs_directory_contexts requires fs_metadata");
#[cfg(all(fs_directory_contexts, not(fs_home_wire)))]
pub const MAGIC: &[u8; 8] = b"AFSRPC08";

#[cfg(all(fs_home_wire, not(fs_home)))]
compile_error!("fs_home_wire requires fs_home");
#[cfg(fs_home_wire)]
pub const MAGIC: &[u8; 8] = b"AFSRPC09";
#[cfg(fs_home_wire)]
#[path = "home-service.rs"]
mod home_service;
#[cfg(fs_home_wire)]
pub use home_service::run_home;
