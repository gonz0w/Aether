// SPDX-License-Identifier: BSD-2-Clause
//! Private fixed connection framing. Transport binding is trusted provisioning;
//! request bytes never select a peer, session, provider epoch or backend object.
use super::{Backend, Entry, Error, Handle, Kind, MAX_READ, Owner, Rights, Session};

pub const FRAME: usize = 64;
pub const PAYLOAD: usize = 24;
pub type Message = [u8; FRAME];

pub fn word(message: &Message, index: usize) -> u64 {
    u64::from_le_bytes(message[index * 8..index * 8 + 8].try_into().unwrap())
}

pub fn put(message: &mut Message, index: usize, value: u64) {
    message[index * 8..index * 8 + 8].copy_from_slice(&value.to_le_bytes());
}

fn entry(value: Entry) -> Message {
    let mut reply = [0; FRAME];
    put(&mut reply, 1, value.handle.epoch);
    put(&mut reply, 2, value.handle.serial);
    put(
        &mut reply,
        3,
        if value.kind == Kind::Directory { 1 } else { 2 },
    );
    put(&mut reply, 4, value.size);
    reply
}

fn failure(error: Error) -> Message {
    let code: i64 = match error {
        Error::Denied => -13,
        Error::Stale | Error::Closed => -9,
        Error::Full => -28,
        Error::Invalid => -22,
        Error::NotDirectory => -20,
        Error::IsDirectory => -21,
        _ => -5,
    };
    let mut reply = [0; FRAME];
    put(&mut reply, 0, code as u64);
    reply
}

pub struct Binding {
    peer: u64,
    session: Session,
    root: Entry,
    closed: bool,
}

impl Binding {
    /// Trusted service administration only. `endpoint` must be the retained
    /// kernel-authenticated reader binding, never a message field or client ID.
    /// Its sole writer is provisioned to the client before service admission.
    pub fn new<B: Backend>(owner: &mut Owner<B>, endpoint: u64) -> Result<Self, Error> {
        let attachment = owner.attach(endpoint, Rights::ALL)?;
        Ok(Self {
            peer: endpoint,
            session: attachment.session,
            root: attachment.root,
            closed: false,
        })
    }

    pub fn greeting(&self) -> Message {
        entry(self.root)
    }

    pub fn closed(&self) -> bool {
        self.closed
    }

    /// Exactly one complete frame; transport owns partial assembly and EOF.
    /// No request can attach, change this binding, or address a raw C object.
    pub fn request<B: Backend>(&mut self, owner: &mut Owner<B>, raw: &Message) -> Message {
        if self.closed {
            return failure(Error::Closed);
        }
        let handle = Handle {
            epoch: word(raw, 1),
            serial: word(raw, 2),
        };
        let result = (|| match word(raw, 0) {
            1 => {
                let length = usize::try_from(word(raw, 4)).map_err(|_| Error::Invalid)?;
                let bits = u8::try_from(word(raw, 3)).map_err(|_| Error::Invalid)?;
                if length == 0 || length > PAYLOAD || raw[40 + length..].iter().any(|b| *b != 0) {
                    return Err(Error::Invalid);
                }
                let value = owner.lookup(
                    self.peer,
                    self.session,
                    handle,
                    &raw[40..40 + length],
                    Rights::new(bits)?,
                )?;
                Ok(entry(value))
            }
            2 => {
                let count = usize::try_from(word(raw, 4)).map_err(|_| Error::Invalid)?;
                if count > PAYLOAD || raw[40..].iter().any(|b| *b != 0) {
                    return Err(Error::Invalid);
                }
                let mut bytes = [0; MAX_READ];
                let count = owner.read(
                    self.peer,
                    self.session,
                    handle,
                    word(raw, 3),
                    count,
                    &mut bytes,
                )?;
                let mut reply = [0; FRAME];
                put(&mut reply, 4, count as u64);
                reply[40..40 + count].copy_from_slice(&bytes[..count]);
                Ok(reply)
            }
            3 => {
                if raw[24..].iter().any(|b| *b != 0) {
                    return Err(Error::Invalid);
                }
                owner.close(self.peer, self.session, handle)?;
                Ok([0; FRAME])
            }
            4 => {
                if raw[8..].iter().any(|b| *b != 0) {
                    return Err(Error::Invalid);
                }
                owner.disconnect(self.peer, self.session)?;
                self.closed = true;
                Ok([0; FRAME])
            }
            _ => Err(Error::Invalid),
        })();
        result.unwrap_or_else(failure)
    }
}
