// SPDX-License-Identifier: BSD-2-Clause
//! Actual Rust bridge ABI over a typed C provider. Serial, host-only.
use core::ptr::NonNull;
use filesystem_bridge::Spa;
use filesystem_policy::{Clock, Error, Owner, Rights, Utc};
unsafe extern "C" {
    fn context_reset(mode: u32);
    fn mixed_count(index: u32) -> u32;
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> Result<Utc, Error> {
        panic!("no mutation")
    }
}
#[test]
fn typed_c_outputs_errors_and_cleanup_cross_real_bridge() {
    for mode in 0..=9 {
        // SAFETY: serial loop; previous owner dropped its sole C context before reset.
        unsafe { context_reset(mode) };
        let mut marker = 0u64;
        // SAFETY: live exclusive SPA marker for this host fixture, borrowed until
        // its exact context is consumed; no target authority or pointer escapes.
        let mut spa = unsafe { Spa::from_raw(NonNull::from(&mut marker).cast()) };
        let mut owner = Owner::new(spa.open(c"testpool_zstd/x86_64").unwrap(), Time, 71).unwrap();
        let a = owner.attach(17, Rights::new(3).unwrap()).unwrap();
        let mut out = [0xa5; 256];
        let result = owner.directory_context(17, a.session, a.root.handle, &mut out);
        match mode {
            0 => {
                assert_eq!(result.unwrap().1, 2);
                assert_eq!(&out[..2], b"/\0");
            }
            1 => assert!(matches!(result, Err(Error::Backend(5)))),
            2 => assert!(matches!(result, Err(Error::InvalidCompletion))),
            _ => assert!(matches!(result, Err(Error::InvalidMetadata)), "mode{mode}"),
        }
        if mode != 0 {
            assert_eq!(out, [0; 256]);
        }
        owner.shutdown();
        // SAFETY: valid scalar counter indices after synchronous teardown, no concurrent reset.
        unsafe {
            assert_eq!(mixed_count(0), 1);
            assert_eq!(mixed_count(1), 1);
            assert_eq!(mixed_count(5), 0);
        }
    }
}
