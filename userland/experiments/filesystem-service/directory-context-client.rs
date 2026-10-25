// SPDX-License-Identifier: BSD-2-Clause
//! AF08 directory observations. Parent never supplies authority outside root.
use super::*;
impl<T: Channel> Client<T> {
    pub(super) fn directory_binding(&self, handle: Handle) -> Result<Binding> {
        let (_, binding) = self.binding(handle)?;
        if binding.entry.kind != Kind::Directory {
            return Err(Error::Remote(-20));
        }
        if binding.rights & 3 != 3 {
            return Err(Error::Invalid);
        }
        Ok(binding)
    }
    /// Returns the borrowed root or a new owned non-root parent handle.
    pub fn parent_directory(&mut self, handle: Handle) -> Result<Entry> {
        self.directory_binding(handle)?;
        let root = self.root()?;
        let free = if handle == root {
            None
        } else {
            Some(
                self.bindings
                    .iter()
                    .position(Option::is_none)
                    .ok_or(Error::Full)?,
            )
        };
        let next = if handle == root {
            self.next
        } else {
            self.next.checked_add(1).ok_or(Error::Full)?
        };
        let reply = self.exchange(&self.request(13, handle.token))?;
        if word(&reply, 3) == root.token {
            let entry = self.entry(&reply, root.token)?;
            if entry.kind != Kind::Directory {
                return self.fatal(Error::Protocol);
            }
            self.bindings[0] = Some(Binding { entry, rights: 3 });
            return Ok(entry);
        }
        let Some(free) = free else {
            return self.fatal(Error::Protocol);
        };
        let entry = self.entry(&reply, self.next)?;
        if entry.kind != Kind::Directory {
            return self.fatal(Error::Protocol);
        }
        self.bindings[free] = Some(Binding { entry, rights: 3 });
        self.next = next;
        Ok(entry)
    }
    /// Physical path including NUL; no caller bytes are published on failure.
    pub fn directory_path(&mut self, handle: Handle, out: &mut [u8; 256]) -> Result<usize> {
        out.fill(0);
        self.directory_binding(handle)?;
        let reply = self.exchange(&self.request(14, handle.token))?;
        let length = word(&reply, 5) as usize;
        if word(&reply, 3) != 0
            || word(&reply, 4) != 0
            || !(2..=256).contains(&length)
            || reply[48..].iter().any(|b| *b != 0)
        {
            return self.fatal(Error::Protocol);
        }
        let received = (|| {
            for offset in (0..length).step_by(FRAME) {
                let frame = self.receive()?;
                let count = (length - offset).min(FRAME);
                if frame[count..].iter().any(|b| *b != 0) {
                    return self.fatal(Error::Protocol);
                }
                out[offset..offset + count].copy_from_slice(&frame[..count]);
            }
            if (out[..length] == *b"/\0") != (handle == self.root()?)
                || out[0] != b'/'
                || out[length - 1] != 0
                || out[..length - 1].contains(&0)
                || (length > 2
                    && out[1..length - 1]
                        .split(|b| *b == b'/')
                        .any(|p| p.is_empty() || p == b"." || p == b".."))
            {
                return self.fatal(Error::Protocol);
            }
            Ok(length)
        })();
        if received.is_err() {
            out.fill(0);
        }
        received
    }
}
