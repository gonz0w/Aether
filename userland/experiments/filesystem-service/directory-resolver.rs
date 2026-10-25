// SPDX-License-Identifier: BSD-2-Clause
//! Bounded component-wise POSIX path subset; unsupported node kinds stay errors.
use super::*;

#[derive(Debug, PartialEq, Eq)]
pub enum ResolvedDirectory {
    /// The caller's retained base or the client's root; no new close obligation.
    Borrowed(Entry),
    /// Newly opened directory; caller owns its close.
    Owned(Entry),
}
impl ResolvedDirectory {
    pub fn entry(&self) -> Entry {
        match *self {
            Self::Borrowed(entry) | Self::Owned(entry) => entry,
        }
    }
}
struct Walk {
    entry: Entry,
    owned: bool,
}
impl<T: Channel> Client<T> {
    fn resolved_walk(&mut self, base: Handle, path: &[u8], file: bool) -> Result<Walk> {
        let root = self.root()?;
        if path.is_empty() || path.len() > 255 || path.contains(&0) {
            return Err(Error::Invalid);
        }
        let base = if path.starts_with(b"/") { root } else { base };
        let binding = self.directory_binding(base)?;
        let count = path
            .split(|b| *b == b'/')
            .filter(|part| !part.is_empty() && *part != b".")
            .count();
        let root_only = base == root
            && path
                .split(|b| *b == b'/')
                .all(|part| part.is_empty() || part == b"." || part == b"..");
        if !root_only && count != 0 {
            let needed = if count == 1 { 1 } else { 2 };
            if self.bindings.iter().filter(|b| b.is_none()).count() < needed
                || self.next.checked_add(count as u64).is_none()
            {
                return Err(Error::Full);
            }
        }
        let parts = path.split(|b| *b == b'/').filter(|part| !part.is_empty());
        let total = parts.clone().count();
        let trailing = path.ends_with(b"/");
        let mut at = Walk {
            entry: binding.entry,
            owned: false,
        };
        for (index, part) in parts.enumerate() {
            if part == b"." {
                continue;
            }
            let next = if part == b".." {
                if at.entry.handle == root {
                    continue;
                }
                self.parent_directory(at.entry.handle)
            } else {
                self.lookup(
                    at.entry.handle,
                    part,
                    if file && index + 1 == total && !trailing {
                        2
                    } else {
                        3
                    },
                )
            };
            if self.cleanup().is_some() {
                return next.map(|entry| Walk { entry, owned: true });
            }
            if at.owned {
                self.close(at.entry.handle)?;
            }
            let entry = next?;
            at = Walk {
                entry,
                owned: entry.handle != root,
            };
            if (index + 1 != total || trailing) && entry.kind != Kind::Directory {
                if at.owned {
                    self.close(entry.handle)?;
                }
                return Err(Error::Remote(-20));
            }
        }
        Ok(at)
    }
    pub fn resolve_directory_from(
        &mut self,
        base: Handle,
        path: &[u8],
    ) -> Result<ResolvedDirectory> {
        let result = self.resolved_walk(base, path, false)?;
        if result.entry.kind != Kind::Directory {
            if result.owned {
                self.close(result.entry.handle)?;
            }
            return Err(Error::Remote(-20));
        }
        Ok(if result.owned {
            ResolvedDirectory::Owned(result.entry)
        } else {
            ResolvedDirectory::Borrowed(result.entry)
        })
    }
    pub fn resolve_file_from(&mut self, base: Handle, path: &[u8]) -> Result<Entry> {
        let result = self.resolved_walk(base, path, true)?;
        if result.entry.kind != Kind::File {
            if result.owned {
                self.close(result.entry.handle)?;
            }
            return Err(Error::Remote(-21));
        }
        Ok(result.entry)
    }
}
