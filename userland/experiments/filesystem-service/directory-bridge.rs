// SPDX-License-Identifier: BSD-2-Clause
//! Typed directory FFI; no raw identities or SPA access in client messages.
use super::*;

unsafe extern "C" {
    fn aether_zpl_directory(
        view: *mut c_void,
        object: u64,
        generation: u64,
        out: *mut RawNode,
    ) -> i32;
    fn aether_zpl_mkdir(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        name: *const u8,
        length: usize,
        uid: u64,
        gid: u64,
        seconds: u64,
        nanos: u64,
        created: *mut RawNode,
        result: *mut RawWrite,
    ) -> i32;
    fn aether_zpl_rmdir(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        name: *const u8,
        length: usize,
        object: u64,
        object_generation: u64,
        seconds: u64,
        nanos: u64,
        result: *mut RawWrite,
    ) -> i32;
}

impl Zpl<'_> {
    pub(super) fn refresh_directory(&mut self, directory: Node) -> Result<Node, Error> {
        if self.consumed {
            return Err(Error::Closed);
        }
        let (object, generation) = directory.identity();
        let mut raw = RawNode::default();
        // SAFETY: exclusive live context, trusted retained identity, initialized
        // separate output. C retains no pointer and validates generation/type.
        status(unsafe {
            aether_zpl_directory(self.pointer.as_ptr(), object, generation, &mut raw)
        })?;
        let current = node(raw)?;
        if current.identity() != directory.identity() || current.kind() != Kind::Directory {
            return Err(Error::InvalidMetadata);
        }
        Ok(current)
    }

    #[allow(
        clippy::too_many_arguments,
        reason = "Mirrors the private typed C directory ABI."
    )]
    pub(super) fn make_directory(
        &mut self,
        directory: Node,
        name: &[u8],
        uid: u64,
        gid: u64,
        utc: Utc,
        result: &mut RawWrite,
    ) -> i32 {
        let (object, generation) = directory.identity();
        let mut created = RawNode::default();
        // SAFETY: namespace_mutation checked context and UTC; exact initialized
        // name borrow, disjoint initialized created/progress outputs, no escape.
        let error = unsafe {
            aether_zpl_mkdir(
                self.pointer.as_ptr(),
                object,
                generation,
                name.as_ptr(),
                name.len(),
                uid,
                gid,
                utc.seconds,
                utc.nanoseconds,
                &mut created,
                result,
            )
        };
        if error == 0
            && (created.object == 0
                || created.generation == 0
                || created.size != 2
                || created.mode != 0o040700)
        {
            5
        } else {
            error
        }
    }

    pub(super) fn remove_directory(
        &mut self,
        directory: Node,
        name: &[u8],
        child: Node,
        utc: Utc,
        result: &mut RawWrite,
    ) -> i32 {
        let (object, generation) = directory.identity();
        let (child, child_generation) = child.identity();
        // SAFETY: same serialized context/name/output borrows as mkdir. Expected
        // child comes from a validated lookup, never caller-selected raw IDs.
        unsafe {
            aether_zpl_rmdir(
                self.pointer.as_ptr(),
                object,
                generation,
                name.as_ptr(),
                name.len(),
                child,
                child_generation,
                utc.seconds,
                utc.nanoseconds,
                result,
            )
        }
    }
}
