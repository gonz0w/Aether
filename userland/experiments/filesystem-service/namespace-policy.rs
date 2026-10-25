// SPDX-License-Identifier: BSD-2-Clause
//! Private one-attempt namespace policy; credentials are trusted labels only.
use super::*;

#[derive(Clone, Copy)]
pub struct Identity {
    pub(crate) uid: u64,
    pub(crate) gid: u64,
}
impl Identity {
    pub fn new(uid: u64, gid: u64) -> Result<Self, Error> {
        if uid > i32::MAX as u64 || gid > i32::MAX as u64 {
            return Err(Error::Invalid);
        }
        Ok(Self { uid, gid })
    }
}

/// Exact Owner result and typed backend result before Owner normalization.
#[cfg(fs_home_native)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NamespaceObservation {
    pub result: Result<Completion, Error>,
    pub provider: Option<Result<Completion, Lost>>,
}

pub enum Mutation<'a> {
    Create(&'a [u8]),
    #[cfg(fs_directories)]
    MakeDirectory(&'a [u8]),
    #[cfg(fs_directories)]
    RemoveDirectory(&'a [u8]),
    Rename(&'a [u8], &'a [u8]),
    Remove(&'a [u8]),
}

/// Trusted synchronous provider input; client fields never contain these IDs.
pub enum Namespace<'a> {
    Create {
        name: &'a [u8],
        uid: u64,
        gid: u64,
    },
    #[cfg(fs_directories)]
    MakeDirectory {
        name: &'a [u8],
        uid: u64,
        gid: u64,
    },
    #[cfg(fs_directories)]
    RemoveDirectory {
        name: &'a [u8],
        directory: Node,
    },
    Rename {
        from: &'a [u8],
        to: &'a [u8],
        file: Node,
    },
    Remove {
        name: &'a [u8],
        file: Node,
    },
}

fn name(value: &[u8]) -> Result<(), Error> {
    if value.is_empty()
        || value.len() > if cfg!(fs_names) { 255 } else { 16 }
        || value == b"."
        || value == b".."
        || value.contains(&0)
        || value.contains(&b'/')
    {
        return Err(Error::Invalid);
    }
    Ok(())
}

impl<B: Backend, C: Clock> Owner<B, C> {
    /// Trusted bootstrap configuration, never an opcode or authority source.
    pub fn with_namespace_identity(mut self, identity: Identity) -> Self {
        self.identity = Some(identity);
        self
    }

    #[cfg(fs_mixed)]
    pub fn mutation_attempts(&self) -> MutationCount {
        self.writes
    }

    pub fn namespace_finished(&self) -> bool {
        self.poisoned || self.backend.is_none()
    }

    pub fn namespace(
        &mut self,
        peer: u64,
        session: Session,
        directory: Handle,
        operation: Mutation<'_>,
    ) -> Result<Completion, Error> {
        self.namespace_inner::<false>(peer, session, directory, operation, &mut None)
    }

    /// Trusted bootstrap diagnostic. The provider observation is copied before
    /// Owner validation/parent refresh; it supplies no retry or authority.
    #[cfg(fs_home_native)]
    pub fn namespace_observed(
        &mut self,
        peer: u64,
        session: Session,
        directory: Handle,
        operation: Mutation<'_>,
    ) -> NamespaceObservation {
        let mut provider = None;
        let result =
            self.namespace_inner::<true>(peer, session, directory, operation, &mut provider);
        NamespaceObservation { result, provider }
    }

    #[inline]
    fn namespace_inner<const OBSERVED: bool>(
        &mut self,
        peer: u64,
        session: Session,
        directory: Handle,
        operation: Mutation<'_>,
        provider: &mut Option<Result<Completion, Lost>>,
    ) -> Result<Completion, Error> {
        let index = self.open(peer, session, directory)?;
        let parent = self.handles[index].ok_or(Error::Stale)?;
        if !parent.rights.contains(Rights::LOOKUP) || !parent.rights.contains(Rights::MUTATE_DIR) {
            return Err(Error::Denied);
        }
        if parent.node.kind != Kind::Directory {
            return Err(Error::NotDirectory);
        }
        let identity = self.identity.ok_or(Error::Denied)?;
        let (source, destination, removing) = match operation {
            Mutation::Create(value) => (value, None, false),
            #[cfg(fs_directories)]
            Mutation::MakeDirectory(value) => (value, None, false),
            #[cfg(fs_directories)]
            Mutation::RemoveDirectory(value) => (value, None, true),
            Mutation::Rename(from, to) => (from, Some(to), false),
            Mutation::Remove(value) => (value, None, true),
        };
        name(source)?;
        if let Some(to) = destination {
            name(to)?;
            if source == to || source.len() + to.len() > if cfg!(fs_names) { 510 } else { 16 } {
                return Err(Error::Invalid);
            }
        }
        #[cfg(fs_mixed)]
        {
            if self.writes == MUTATION_LIMIT {
                return Err(Error::WriteLimit);
            }
            // This finite mixed profile mutates only its provisioned root.
            // Never refresh a child directory through an unrelated root lookup.
            #[cfg(not(fs_directories))]
            if self.root.identity() != parent.node.identity() {
                return Err(Error::Denied);
            }
        }
        if self.write_used {
            return Err(Error::WriteLimit);
        }
        let creating = match operation {
            Mutation::Create(_) => true,
            #[cfg(fs_directories)]
            Mutation::MakeDirectory(_) => true,
            _ => false,
        };
        let expected_kind = Kind::File;
        #[cfg(fs_directories)]
        let expected_kind = if matches!(operation, Mutation::RemoveDirectory(_)) {
            Kind::Directory
        } else {
            expected_kind
        };
        let file = if creating {
            None
        } else {
            let file = self
                .backend
                .as_mut()
                .ok_or(Error::Closed)?
                .lookup(parent.node, source)?;
            if !file.valid() || file.kind != expected_kind {
                return Err(Error::InvalidMetadata);
            }
            if removing
                && self
                    .handles
                    .iter()
                    .flatten()
                    .any(|open| open.node.identity() == file.identity())
            {
                return Err(Error::Denied);
            }
            Some(file)
        };
        let operation = match operation {
            #[cfg(fs_directories)]
            Mutation::MakeDirectory(name) => Namespace::MakeDirectory {
                name,
                uid: identity.uid,
                gid: identity.gid,
            },
            #[cfg(fs_directories)]
            Mutation::RemoveDirectory(name) => Namespace::RemoveDirectory {
                name,
                directory: file.ok_or(Error::InvalidMetadata)?,
            },
            Mutation::Create(name) => Namespace::Create {
                name,
                uid: identity.uid,
                gid: identity.gid,
            },
            Mutation::Rename(from, to) => Namespace::Rename {
                from,
                to,
                file: file.ok_or(Error::InvalidMetadata)?,
            },
            Mutation::Remove(name) => Namespace::Remove {
                name,
                file: file.ok_or(Error::InvalidMetadata)?,
            },
        };
        let utc = self.clock.utc()?;
        if utc.seconds > i64::MAX as u64 || utc.nanoseconds >= 1_000_000_000 {
            return Err(Error::Clock);
        }
        self.write_used = true;
        #[cfg(fs_mixed)]
        {
            self.writes += 1;
        }
        let result =
            self.backend
                .as_mut()
                .ok_or(Error::Closed)?
                .mutate(parent.node, operation, utc);
        if OBSERVED {
            *provider = Some(result);
        }
        // The old one-attempt profile consumes all aliases before its reply.
        // Mixed bridge success already consumed/retired/reopened the C context;
        // only coherent, validated identities may continue in that variant.
        #[cfg(not(fs_mixed))]
        self.retire();
        #[cfg(fs_mixed)]
        if matches!(
            result,
            Ok(Completion {
                error: 0,
                state: 2,
                txg: 1..,
                bytes_staged: 0
            })
        ) {
            #[cfg(not(fs_directories))]
            let root = self.backend.as_mut().ok_or(Error::Closed)?.root();
            #[cfg(fs_directories)]
            let root = self
                .backend
                .as_mut()
                .ok_or(Error::Closed)?
                .directory(parent.node);
            match root {
                Ok(root)
                    if root.valid()
                        && root.kind == Kind::Directory
                        && root.identity() == parent.node.identity() =>
                {
                    if self.root.identity() == root.identity() {
                        self.root = root;
                    }
                    for open in self.handles.iter_mut().flatten() {
                        if open.node.identity() == root.identity() {
                            open.node = root;
                        }
                    }
                    self.write_used = false;
                }
                _ => {
                    self.retire();
                    let mut progress = result.map_err(|Lost| Error::Uncertain)?;
                    progress.error = 5;
                    return Err(Error::WriteFailed(progress));
                }
            }
        } else {
            self.retire();
        }
        let completion = result.map_err(|Lost| Error::Uncertain)?;
        if completion.bytes_staged != 0 {
            return Err(Error::InvalidCompletion);
        }
        if completion.error == 0 && completion.state == 2 && completion.txg > 0 {
            return Ok(completion);
        }
        if (1..=4095).contains(&completion.error) {
            if completion.state == 0 && completion.txg == 0 {
                return Err(Error::Backend(completion.error));
            }
            // The original C mutator explicitly retains COMMITTED with TXG0
            // on assignment anomalies; never erase this irreversible outcome.
            if completion.state == 1 || (completion.state == 2 && completion.txg > 0) {
                return Err(Error::WriteFailed(completion));
            }
        }
        Err(Error::InvalidCompletion)
    }
}
