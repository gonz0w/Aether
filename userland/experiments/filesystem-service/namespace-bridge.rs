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
                let mut created = RawNode::default();
                let error = unsafe {
                    aether_zpl_create(
                        self.pointer.as_ptr(),
                        parent,
                        parent_generation,
                        name.as_ptr(),
                        name.len(),
                        uid,
                        gid,
                        utc.seconds,
                        utc.nanoseconds,
                        &mut created,
                        &mut raw,
                    )
                };
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
