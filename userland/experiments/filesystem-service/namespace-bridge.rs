// SPDX-License-Identifier: BSD-2-Clause
//! Exact original zpl-mutate.h calls. No observer reset or retirement entry.
use super::*;
use policy::Namespace;

unsafe extern "C" {
    fn aether_zpl_create(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        name: *const u8,
        length: usize,
        uid: u64,
        gid: u64,
        seconds: u64,
        nanoseconds: u64,
        created: *mut RawNode,
        result: *mut RawWrite,
    ) -> i32;
    fn aether_zpl_rename(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        from: *const u8,
        from_length: usize,
        to: *const u8,
        to_length: usize,
        object: u64,
        object_generation: u64,
        seconds: u64,
        nanoseconds: u64,
        result: *mut RawWrite,
    ) -> i32;
    fn aether_zpl_remove(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        name: *const u8,
        length: usize,
        object: u64,
        object_generation: u64,
        seconds: u64,
        nanoseconds: u64,
        result: *mut RawWrite,
    ) -> i32;
}

impl Zpl<'_> {
    pub(super) fn namespace_mutation(
        &mut self,
        directory: Node,
        operation: Namespace<'_>,
        utc: Utc,
    ) -> Result<Completion, Lost> {
        if utc.seconds > i64::MAX as u64 || utc.nanoseconds >= 1_000_000_000 {
            return Ok(Completion {
                error: 22,
                txg: 0,
                bytes_staged: 0,
                state: 0,
            });
        }
        #[cfg(all(fs_namespace, not(fs_mixed)))]
        if core::mem::replace(&mut self.namespace_used, true) {
            return Ok(Completion {
                error: 28,
                txg: 0,
                bytes_staged: 0,
                state: 0,
            });
        }
        #[cfg(fs_mixed)]
        {
            if self.consumed || self.writes == policy::MUTATION_LIMIT {
                return Ok(Completion {
                    error: 28,
                    txg: 0,
                    bytes_staged: 0,
                    state: 0,
                });
            }
            self.writes += 1;
        }
        let (parent, parent_generation) = directory.identity();
        let mut raw = RawWrite::default();
        // SAFETY for every arm: exclusively borrowed live context and retained
        // SPA. Slices are exact initialized immutable borrows through this
        // synchronous call; raw/created outputs are initialized, aligned and
        // nonaliasing. Original C validates names, IDs, permissions/format and
        // UTC, retains no pointer and cannot unwind into Rust.
        let error = match operation {
            #[cfg(fs_directories)]
            Namespace::MakeDirectory { name, uid, gid } => {
                self.make_directory(directory, name, uid, gid, utc, &mut raw)
            }
            #[cfg(fs_directories)]
            Namespace::RemoveDirectory {
                name,
                directory: child,
            } => self.remove_directory(directory, name, child, utc, &mut raw),
            Namespace::Create { name, uid, gid } => {
                let (error, created) =
                    self.file_creation(directory, name, (uid, gid), utc, &mut raw);
                if error == 0
                    && (created.object == 0
                        || created.generation == 0
                        || created.size != 0
                        || created.mode != 0o100600)
                {
                    5
                } else {
                    error
                }
            }
            Namespace::Rename { from, to, file } => {
                let (object, generation) = file.identity();
                unsafe {
                    aether_zpl_rename(
                        self.pointer.as_ptr(),
                        parent,
                        parent_generation,
                        from.as_ptr(),
                        from.len(),
                        to.as_ptr(),
                        to.len(),
                        object,
                        generation,
                        utc.seconds,
                        utc.nanoseconds,
                        &mut raw,
                    )
                }
            }
            Namespace::Remove { name, file } => {
                let (object, generation) = file.identity();
                unsafe {
                    aether_zpl_remove(
                        self.pointer.as_ptr(),
                        parent,
                        parent_generation,
                        name.as_ptr(),
                        name.len(),
                        object,
                        generation,
                        utc.seconds,
                        utc.nanoseconds,
                        &mut raw,
                    )
                }
            }
        };
        #[cfg(fs_mixed)]
        let error = if error == 0 && raw.txg != 0 && raw.state == 2 && raw.bytes_staged == 0 {
            self.finish_mixed(&raw, None)
        } else {
            error
        };
        Ok(Completion {
            error,
            txg: raw.txg,
            bytes_staged: raw.bytes_staged,
            state: raw.state,
        })
    }
}

impl Zpl<'_> {
    fn file_creation(
        &mut self,
        directory: Node,
        name: &[u8],
        labels: (u64, u64),
        utc: Utc,
        result: &mut RawWrite,
    ) -> (i32, RawNode) {
        let (parent, generation) = directory.identity();
        let mut created = RawNode::default();
        // SAFETY: exclusive live context/SPA; exact initialized name borrow and
        // disjoint initialized node/progress outputs; synchronous, no escape.
        let error = unsafe {
            aether_zpl_create(
                self.pointer.as_ptr(),
                parent,
                generation,
                name.as_ptr(),
                name.len(),
                labels.0,
                labels.1,
                utc.seconds,
                utc.nanoseconds,
                &mut created,
                result,
            )
        };
        (error, created)
    }

    #[cfg(fs_mixed)]
    pub(super) fn create_with_identity(
        &mut self,
        directory: Node,
        creation: policy::Creation<'_>,
        identity: policy::Identity,
        utc: Utc,
    ) -> Result<policy::CreatedMutation, Lost> {
        let mut raw = RawWrite::default();
        if utc.seconds > i64::MAX as u64 || utc.nanoseconds >= 1_000_000_000 {
            return Ok(policy::CreatedMutation {
                completion: Completion {
                    error: 22,
                    txg: 0,
                    bytes_staged: 0,
                    state: 0,
                },
                created: None,
            });
        }
        if self.consumed || self.writes == policy::MUTATION_LIMIT {
            return Ok(policy::CreatedMutation {
                completion: Completion {
                    error: 28,
                    txg: 0,
                    bytes_staged: 0,
                    state: 0,
                },
                created: None,
            });
        }
        self.writes += 1;
        let (error, created, mode, size, kind) = match creation {
            policy::Creation::File(name) => {
                let (error, node) =
                    self.file_creation(directory, name, identity.credentials(), utc, &mut raw);
                (error, node, 0o100600, 0, Kind::File)
            }
            #[cfg(fs_directories)]
            policy::Creation::Directory(name) => {
                let (error, node) =
                    self.directory_creation(directory, name, identity.credentials(), utc, &mut raw);
                (error, node, 0o040700, 2, Kind::Directory)
            }
        };
        // Copy original provider progress before success retirement/reopen.
        let completion = Completion {
            error,
            txg: raw.txg,
            bytes_staged: raw.bytes_staged,
            state: raw.state,
        };
        let created = if error == 0
            && created.object != 0
            && created.generation != 0
            && created.mode == mode
            && created.size == size
        {
            Some(Node::new(
                created.object,
                created.generation,
                created.size,
                kind,
            ))
        } else {
            None
        };
        if error == 0 && raw.state == 2 && raw.txg > 0 && raw.bytes_staged == 0 && created.is_some()
        {
            // Keep the trusted identity even on reopen failure. finish_mixed
            // leaves consumed=true on failure; Owner must validate the reopened
            // backend before publication. Malformed metadata never retires a
            // successful observer record or reopens a context for reuse.
            let _ = self.finish_mixed(&raw, None);
        }
        Ok(policy::CreatedMutation {
            completion,
            created,
        })
    }
}
