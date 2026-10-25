// SPDX-License-Identifier: BSD-2-Clause
//! Canonical walks from retained directories, not POSIX CWD resolution.
use super::{Channel, Client, Entry, Error, Kind, Result};

impl<T: Channel> Client<T> {
    /// At most two temporary handles; unknown cleanup retires the whole client.
    pub fn open_root_path(&mut self, path: &[u8]) -> Result<Entry> {
        let root = self.root()?;
        if path.is_empty() || path.len() > 255 || path.contains(&0) {
            return Err(Error::Invalid);
        }
        if path == b"/" {
            return Err(Error::Remote(-21));
        }
        self.open_file_from(root, path.strip_prefix(b"/").unwrap_or(path))
    }

    /// Open a new file handle relative to a borrowed live directory. Never
    /// interpret an absolute path or close the caller's directory handle.
    pub fn open_file_from(&mut self, directory: super::Handle, path: &[u8]) -> Result<Entry> {
        self.walk_from(directory, path, Kind::File)
    }

    /// Open a new LOOKUP|READ directory handle; the caller owns its close.
    /// For the borrowed delegated root use root(), not an empty or slash path.
    pub fn open_directory_from(&mut self, directory: super::Handle, path: &[u8]) -> Result<Entry> {
        self.walk_from(directory, path, Kind::Directory)
    }

    fn walk_from(&mut self, directory: super::Handle, path: &[u8], kind: Kind) -> Result<Entry> {
        self.active()?;
        if path.is_empty() || path.len() > 255 || path.contains(&0) {
            return Err(Error::Invalid);
        }
        if path
            .split(|b| *b == b'/')
            .any(|part| part.is_empty() || part == b"." || part == b"..")
        {
            return Err(Error::Invalid);
        }
        let (_, binding) = self.binding(directory)?;
        if binding.entry.kind != Kind::Directory {
            return Err(Error::Remote(-20));
        }
        if binding.rights & 3 != 3 {
            return Err(Error::Invalid);
        }
        let count = path.split(|b| *b == b'/').count();
        let needed = if count == 1 { 1 } else { 2 };
        if self.bindings.iter().filter(|b| b.is_none()).count() < needed
            || self.next.checked_add(count as u64).is_none()
        {
            return Err(Error::Full);
        }
        let mut temporary = None;
        for (index, part) in path.split(|b| *b == b'/').enumerate() {
            let final_part = index + 1 == count;
            let next = self.lookup(
                temporary.unwrap_or(directory),
                part,
                if final_part && kind == Kind::File {
                    2
                } else {
                    3
                },
            );
            // A fatal lookup already consumed endpoint obligations. Never send
            // another close on that retired connection or replace its error.
            if self.cleanup().is_some() {
                return next;
            }
            if let Some(previous) = temporary.take() {
                self.close(previous)?;
            }
            let entry = next?;
            if final_part {
                if entry.kind == kind {
                    return Ok(entry);
                }
                self.close(entry.handle)?;
                return Err(Error::Remote(if kind == Kind::File { -21 } else { -20 }));
            }
            if entry.kind != Kind::Directory {
                self.close(entry.handle)?;
                return Err(Error::Remote(-20));
            }
            temporary = Some(entry.handle);
        }
        // Validated nonempty components always return an entry or an error above.
        unreachable!()
    }
}
