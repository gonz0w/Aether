// SPDX-License-Identifier: BSD-2-Clause
//! Consumed-context success-only retirement; no failed record reset or replay.
use super::*;

unsafe extern "C" {
    #[cfg(fs_bulk)]
    fn aether_pool_service_bytes_retire(
        error: i32,
        target: u64,
        staged: u64,
        state: u64,
        expected: u64,
    ) -> i32;
    fn aether_pool_namespace0_retire(error: i32, target: u64, staged: u64, state: u64) -> i32;
}

impl Zpl<'_> {
    pub(super) fn finish_mixed(
        &mut self,
        raw: &RawWrite,
        written: Option<(Node, u64, &[u8])>,
    ) -> i32 {
        let verified = match written {
            Some((file, offset, bytes)) => {
                let mut check = [0u8; 16];
                #[cfg(not(fs_bulk))]
                let verified =
                    matches!(self.read(file, offset, &mut check), Ok(16)) && check == bytes;
                #[cfg(fs_bulk)]
                let verified = bytes.chunks(16).enumerate().all(|(part, expected)| {
                    let Some(at) = offset.checked_add((part * 16) as u64) else {
                        return false;
                    };
                    let out = &mut check[..expected.len()];
                    matches!(self.read(file, at, out), Ok(n) if n == expected.len())
                        && out == expected
                });
                verified
            }
            None => true,
        };
        let mut owned = self.pointer.as_ptr();
        self.consumed = true;
        // SAFETY: exclusive context; all slice borrows/calls have returned. C
        // consumes/nulls it. SPA/dataset remain retained until all original drains.
        unsafe { aether_zpl_close(&mut owned) };
        assert!(owned.is_null(), "ZPL close did not consume context");
        if !verified {
            return 5;
        }
        // SAFETY: original successful progress and consumed context. Typed entry
        // is selected by the trusted operation, never by caller staging fields.
        // Original observer guards preserve every borrow/epoch/permanent outcome.
        let retired = unsafe {
            if let Some((_, _, bytes)) = written {
                #[cfg(not(fs_bulk))]
                let _ = bytes;
                #[cfg(not(fs_bulk))]
                let result = aether_pool_service16_retire(0, raw.txg, raw.bytes_staged, raw.state);
                #[cfg(fs_bulk)]
                let result = aether_pool_service_bytes_retire(
                    0,
                    raw.txg,
                    raw.bytes_staged,
                    raw.state,
                    bytes.len() as u64,
                );
                result
            } else {
                aether_pool_namespace0_retire(0, raw.txg, raw.bytes_staged, raw.state)
            }
        };
        if retired != 0 {
            return if retired > 0 { retired } else { 5 };
        }
        let mut next = core::ptr::null_mut();
        // SAFETY: same exclusive live SPA and exact immutable NUL dataset;
        // initialized separate output, no other live provider context.
        let reopened =
            unsafe { aether_zpl_open_write(self.spa.as_ptr(), self.dataset.as_ptr(), &mut next) };
        if reopened != 0 || next.is_null() {
            if !next.is_null() {
                // SAFETY: consume the only valid owned factory-error output.
                unsafe { aether_zpl_close(&mut next) };
                assert!(next.is_null(), "ZPL error close did not consume context");
            }
            return if reopened > 0 { reopened } else { 5 };
        }
        self.pointer = NonNull::new(next).unwrap();
        self.consumed = false;
        0
    }
}
