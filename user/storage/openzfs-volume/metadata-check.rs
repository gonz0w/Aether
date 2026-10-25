// SPDX-License-Identifier: BSD-2-Clause
//! Separate READ-only disk consumer; fixture identities confer no client access.
use core::{ffi::c_void, ptr::NonNull};

// Source selection supplies the separately maintained userland module.
use crate::metadata;

/// # Safety
/// Caller holds the original view and SPA exclusively throughout; node identities
/// come from the original root/lookup in that view. No pointer or state escapes.
pub unsafe fn check(view: NonNull<c_void>, root: (u64, u64), file: (u64, u64)) -> bool {
    // SAFETY: the synchronous importer caller retains all borrows above.
    let (Ok(root), Ok(file)) = (unsafe { metadata::read(view, root.0, root.1) }, unsafe {
        metadata::read(view, file.0, file.1)
    }) else {
        return false;
    };
    let nodes = [root, file];
    for (index, value) in nodes.iter().enumerate() {
        let (object, generation, size, mode, links, flags, atime, birthtime) = if index == 0 {
            (
                34,
                45,
                3,
                0o040755,
                2,
                0x840800000144,
                1621447687,
                1620802853,
            )
        } else {
            (
                2,
                47,
                780248,
                0o100755,
                1,
                0x840800000104,
                1621447692,
                1620802862,
            )
        };
        if value.node
            != (metadata::Node {
                object,
                generation,
                size,
                mode,
            })
            || (value.parent, value.links, value.uid, value.gid, value.flags)
                != (34, links, 0, 0, flags)
            || [
                value.atime.seconds,
                value.mtime.seconds,
                value.ctime.seconds,
                value.birthtime.seconds,
            ] != [atime, 1620802862, 1620802862, birthtime]
        {
            return false;
        }
    }
    // SAFETY: same live exclusive view; only the fixed expected generation differs.
    (unsafe { metadata::read(view, file.node.object, file.node.generation - 1) })
        == Err(metadata::Error::Backend(116))
}
