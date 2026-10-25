// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use policy::{Owner, Rights};

unsafe extern "C" {
    fn fixture_reset(mode: u32);
    fn fixture_count(index: u32) -> u32;
}
fn reset(mode: u32) {
    // SAFETY: tests run serially, with every prior context dropped before reset.
    unsafe { fixture_reset(mode) };
}
fn count(index: u32) -> u32 {
    // SAFETY: fixed in-range indices; fixture has no outstanding concurrent call.
    unsafe { fixture_count(index) }
}
fn token(marker: &mut u64) -> Spa<'_> {
    // SAFETY: host fixture uses this live distinct marker as its opaque SPA;
    // its compiled C provider implements the pinned ABI throughout this borrow.
    unsafe { Spa::from_raw(NonNull::from(marker).cast()) }
}
fn dataset() -> &'static CStr {
    c"testpool_zstd/x86_64"
}

#[test]
fn c_open_outcomes_consume_owned_errors_once() {
    for (mode, error, closes) in [
        (1, Error::Backend(5), 1),
        (2, Error::InvalidCompletion, 0),
        (3, Error::InvalidCompletion, 1),
    ] {
        reset(mode);
        let mut marker = 0;
        let mut spa = token(&mut marker);
        assert!(matches!(spa.open(dataset()), Err(e) if e == error));
        assert_eq!((count(0), count(1)), (1, closes));
    }
}

#[test]
fn malformed_metadata_and_provider_status_do_not_escape() {
    for (mode, expected) in [(4, Error::InvalidMetadata), (13, Error::Backend(5))] {
        reset(mode);
        let mut marker = 0;
        let mut spa = token(&mut marker);
        let result = Owner::new(spa.open(dataset()).unwrap(), RuntimeUtc, 1);
        assert!(matches!(result, Err(e) if e == expected));
        assert_eq!(count(1), 1);
    }
    reset(14);
    let mut marker = 0;
    let mut spa = token(&mut marker);
    let mut backend = spa.open(dataset()).unwrap();
    let root = backend.root().unwrap();
    assert!(matches!(
        backend.lookup(root, b"file"),
        Err(Error::InvalidCompletion)
    ));
}

#[test]
fn c_read_error_or_oversized_completion_clears_entire_borrow() {
    for mode in [5, 6] {
        reset(mode);
        let mut marker = 0;
        let mut spa = token(&mut marker);
        let mut backend = spa.open(dataset()).unwrap();
        let mut bytes = [0xcc; 16];
        let result = backend.read(Node::new(2, 47, 4, Kind::File), 0, &mut bytes);
        assert_eq!(
            result,
            Err(if mode == 5 {
                Error::Backend(5)
            } else {
                Error::InvalidCompletion
            })
        );
        assert!(bytes.iter().all(|b| *b == 0));
    }
}

#[test]
fn policy_write_read_alias_utc_and_retirement_cross_real_c_abi() {
    for mode in [0, 7, 8] {
        reset(mode);
        let mut marker = 0;
        let mut spa = token(&mut marker);
        let mut owner = Owner::new(spa.open(dataset()).unwrap(), RuntimeUtc, 1).unwrap();
        let a = owner.attach(11, Rights::ALL).unwrap();
        let b = owner.attach(12, Rights::new(3).unwrap()).unwrap();
        let writer = owner
            .lookup(11, a.session, a.root.handle, b"file", Rights::WRITE)
            .unwrap();
        let alias = owner
            .lookup(12, b.session, b.root.handle, b"file", Rights::READ)
            .unwrap();
        assert_eq!(
            owner.write(12, b.session, writer.handle, 4, b"EF"),
            Err(Error::Denied)
        );
        assert_eq!((count(5), count(6)), (0, 0));
        let result = owner.write(11, a.session, writer.handle, 4, b"EF");
        if mode == 0 {
            assert_eq!(result.unwrap().assigned_txg, Some(788));
            assert_eq!(owner.stat(12, b.session, alias.handle).unwrap().size, 6);
            let mut out = [0xcc; MAX_READ];
            assert_eq!(
                owner.read(12, b.session, alias.handle, 0, 16, &mut out),
                Ok(6)
            );
            assert_eq!(&out[..6], b"abcdEF");
            assert!(out[6..].iter().all(|b| *b == 0));
            assert_eq!(
                owner.write(11, a.session, writer.handle, 0, b"XX"),
                Err(Error::WriteLimit)
            );
        } else {
            assert!(matches!(
                result,
                Err(Error::WriteFailed(_)) | Err(Error::InvalidCompletion)
            ));
            assert_eq!(
                owner.stat(12, b.session, alias.handle),
                Err(Error::Poisoned)
            );
            assert_eq!(count(1), 1);
        }
        owner.shutdown();
        drop(owner);
        assert_eq!((count(0), count(1), count(5), count(6)), (1, 1, 1, 1));
    }
}

#[test]
fn unavailable_or_invalid_shared_utc_never_reaches_c_writer() {
    for mode in [10, 11, 12] {
        reset(mode);
        let mut marker = 0;
        let mut spa = token(&mut marker);
        let mut owner = Owner::new(spa.open(dataset()).unwrap(), RuntimeUtc, 1).unwrap();
        let a = owner.attach(11, Rights::ALL).unwrap();
        let f = owner
            .lookup(11, a.session, a.root.handle, b"file", Rights::WRITE)
            .unwrap();
        assert_eq!(
            owner.write(11, a.session, f.handle, 0, b"XX"),
            Err(Error::Clock)
        );
        assert_eq!(count(5), 0);
    }
}

#[test]
fn raw_bridge_bounds_prevent_invalid_ffi_borrows() {
    reset(0);
    let mut marker = 0;
    let mut spa = token(&mut marker);
    let mut backend = spa.open(dataset()).unwrap();
    let file = Node::new(2, 47, 4, Kind::File);
    let mut out = [0xcc; MAX_READ + 1];
    assert_eq!(backend.read(file, 0, &mut out), Err(Error::Invalid));
    assert!(out.iter().all(|b| *b == 0));
    let utc = Utc {
        seconds: 1,
        nanoseconds: 0,
    };
    assert_eq!(backend.write(file, u64::MAX, b"X", utc).unwrap().state, 0);
    assert_eq!(backend.write(file, 0, &out, utc).unwrap().error, 22);
    assert_eq!((count(4), count(5)), (0, 0));
}

#[test]
#[should_panic(expected = "ZPL close did not consume context")]
fn close_contract_violation_is_fail_stop() {
    reset(9);
    let mut marker = 0;
    let mut spa = token(&mut marker);
    drop(spa.open(dataset()).unwrap());
}

#[test]
fn producer_callback_reports_committed_and_uncertain_progress_truthfully() {
    use filesystem_probe::{aether_fs_policy_write_probe, ProbeResult};
    for (mode, code, txg, staged, state) in [
        (20, 0, 788, 16, 2),
        (27, 5, 788, 16, 1),
        (28, 5, 0, 0, 3),
        (35, 28, 0, 0, 0),
        (25, 5, 788, 16, 2),
    ] {
        reset(mode);
        let mut marker: u64 = 0;
        let mut result = ProbeResult {
            txg: 99,
            bytes_staged: 99,
            state: 99,
        };
        // SAFETY: serial fixture callback with a distinct live marker and output;
        // C provider and shared UTC fixture remain initialized through return.
        let returned = unsafe {
            aether_fs_policy_write_probe(NonNull::from(&mut marker).cast().as_ptr(), &mut result)
        };
        assert_eq!(
            (returned, result.txg, result.bytes_staged, result.state),
            (code, txg, staged, state)
        );
        assert_eq!((count(0), count(1), count(5)), (1, 1, 1));
    }
}

#[test]
fn callback_rejects_null_inputs_before_open_and_initializes_valid_output() {
    use filesystem_probe::{aether_fs_policy_write_probe, ProbeResult};
    reset(0);
    let mut result = ProbeResult {
        txg: 99,
        bytes_staged: 99,
        state: 99,
    };
    // SAFETY: rejection paths validate null before use; the nonnull result is
    // separate valid writable storage. No SPA operation can run in these cases.
    unsafe {
        assert_eq!(
            aether_fs_policy_write_probe(core::ptr::null_mut(), &mut result),
            22
        );
        assert_eq!(
            aether_fs_policy_write_probe(core::ptr::null_mut(), core::ptr::null_mut()),
            22
        );
    }
    assert_eq!(
        (result.txg, result.bytes_staged, result.state, count(0)),
        (0, 0, 0, 0)
    );
}
