// SPDX-License-Identifier: BSD-2-Clause
//! Synchronous checked original ZPL context; no output on a failed call.
use super::*;
unsafe extern "C" {
    fn aether_zpl_context(
        view: *mut c_void,
        root: u64,
        root_generation: u64,
        object: u64,
        generation: u64,
        path: *mut u8,
        length: *mut usize,
        parent: *mut RawNode,
    ) -> i32;
}
impl Zpl<'_> {
    pub(super) fn read_directory_context(
        &mut self,
        root: Node,
        directory: Node,
        out: &mut [u8; 256],
    ) -> Result<(Node, usize), Error> {
        out.fill(0);
        if self.consumed {
            return Err(Error::Closed);
        }
        let (root, root_generation) = root.identity();
        let (object, generation) = directory.identity();
        let mut parent = RawNode::default();
        let mut length = 0;
        // SAFETY: this exclusive live view retains the SPA borrow. Policy supplies
        // authorized root/directory identities; these initialized disjoint outputs
        // stay valid until return. C excludes mutation/export, retains no pointer
        // and implements the bounded256-byte ABI. No ownership is transferred.
        let code = unsafe {
            aether_zpl_context(
                self.pointer.as_ptr(),
                root,
                root_generation,
                object,
                generation,
                out.as_mut_ptr(),
                &mut length,
                &mut parent,
            )
        };
        let result = status(code).and_then(|()| {
            let parent = node(parent)?;
            if parent.kind() != Kind::Directory || !(2..=256).contains(&length) {
                return Err(Error::InvalidMetadata);
            }
            Ok((parent, length))
        });
        if result.is_err() {
            out.fill(0);
        }
        result
    }
}
