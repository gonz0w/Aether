// SPDX-License-Identifier: BSD-2-Clause
//! C header ABI/provider doubles, not real ZPL/crypto/native execution evidence.
use super::*;
unsafe extern "C" {
    fn test_reset(mode: i32, failure: i32);
    fn test_spa() -> *mut c_void;
    fn test_counter(field: i32) -> i32;
    fn test_composed_probe() -> i32;
}

// Tests run with --test-threads=1, keeping this explicitly synthetic C state local.
fn reset(mode: i32, failure: i32) -> NonNull<c_void> {
    unsafe {
        test_reset(mode, failure);
        NonNull::new(test_spa()).unwrap()
    }
}
fn balanced() {
    unsafe {
        assert_eq!(
            test_counter(1),
            test_counter(2),
            "FFI_CLOSE all contexts consumed"
        );
        assert_eq!(test_counter(3), 0, "FFI_CLOSE no duplicate close");
        assert_eq!(test_counter(4), 0, "FFI_CLOSE no live context");
    }
}

#[test]
fn ffi_complete_probe_preserves_stream_and_two_context_cleanup() {
    reset(0, 0);
    assert_eq!(
        unsafe { test_composed_probe() },
        0,
        "FFI_STREAM composition"
    );
    balanced();
    unsafe {
        assert_eq!(test_counter(1), 2);
        assert_eq!(test_counter(5), 193);
        assert_eq!(test_counter(6), 5);
        assert_eq!(test_counter(7), 191, "FFI_STREAM complete prefix updates");
    }
}

#[test]
fn ffi_each_reachable_provider_failure_consumes_owned_context() {
    reset(0, 0);
    assert_eq!(unsafe { test_composed_probe() }, 0);
    let steps = unsafe { test_counter(0) };
    assert!(steps > 200);
    for failure in 1..=steps {
        reset(0, failure);
        assert_ne!(
            unsafe { test_composed_probe() },
            0,
            "FFI_PROVIDER failure must reject"
        );
        balanced();
    }
}

#[test]
fn ffi_open_status_null_and_error_output_ownership() {
    for (mode, expected) in [
        (1, Error::Backend(5)),
        (2, Error::InvalidCompletion),
        (3, Error::Backend(5)),
        (4, Error::InvalidCompletion),
    ] {
        let spa = reset(mode, 0);
        assert!(
            matches!(unsafe { Zpl::open(spa) }, Err(error) if error == expected),
            "FFI_STATUS"
        );
        balanced();
    }
    assert_eq!(
        unsafe { aether_namespace_owner_probe(core::ptr::null_mut(), core::ptr::null_mut()) },
        22
    );
}

#[test]
fn ffi_metadata_and_negative_status_never_publish_nodes() {
    for mode in [5, 6, 7, 8, 12, 13, 14] {
        reset(mode, 0);
        assert_ne!(unsafe { test_composed_probe() }, 0, "FFI_METADATA");
        balanced();
    }
    assert_eq!(core::mem::size_of::<RawNode>(), 32);
    assert_eq!(core::mem::align_of::<RawNode>(), 8);
    assert_eq!(core::mem::offset_of!(RawNode, mode), 24);
}

#[test]
fn ffi_read_failures_counts_and_partial_bytes_are_not_success() {
    for mode in [9, 10, 11, 15] {
        let spa = reset(mode, 0);
        let backend = unsafe { Zpl::open(spa) }.unwrap();
        let mut owner = Owner::new(backend, 9).unwrap();
        let a = owner.attach(71, Rights::ALL).unwrap();
        let f = owner
            .lookup(71, a.session, a.root.handle, b"zstd", Rights::READ)
            .unwrap();
        let mut reply = [0xa5; MAX_READ];
        assert!(
            owner
                .read(71, a.session, f.handle, 0, 4096, &mut reply)
                .is_err(),
            "FFI_COUNT"
        );
        assert_eq!(reply, [0; MAX_READ], "FFI_REPLY clear failed prefix");
        owner.shutdown();
        balanced();
    }
}

#[test]
fn ffi_suppressed_hash_update_must_fail_final_digest() {
    reset(16, 0);
    assert_ne!(
        unsafe { test_composed_probe() },
        0,
        "FFI_DIGEST omitted update must reject"
    );
    balanced();
}
