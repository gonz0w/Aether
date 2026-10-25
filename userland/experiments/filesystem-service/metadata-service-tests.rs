// SPDX-License-Identifier: BSD-2-Clause
//! Host-only actual AF07 entry, C getter substitute and injected native traps.
use super::*;
use filesystem_policy as policy;
unsafe extern "C" {
    fn metadata_reset(mode: u32);
    fn metadata_count() -> u32;
}
fn select(mode: u32, commands: &[Command]) {
    reset(0, commands);
    // SAFETY: serial tests; prior entry returned and consumed its context.
    unsafe { metadata_reset(mode) };
}
fn gets() -> u32 {
    // SAFETY: fixed scalar counter getter with no concurrent fixture mutation.
    unsafe { metadata_count() }
}
fn values(bytes: &[u8]) -> Vec<u64> {
    bytes
        .as_chunks::<8>()
        .0
        .iter()
        .map(|b| u64::from_le_bytes(*b))
        .collect()
}

#[test]
fn exact_root_metadata_keeps_high_labels_special_bits_and_signed_time() {
    let commands = [request(12, 1), request(4, 0)];
    select(0, &commands);
    let (code, out) = invoke(16, 1000, 1000);
    assert_eq!((code, out.stop, out.requests), (0, 0, 2));
    let replies = decoded(&commands);
    assert_eq!(word(&replies[0].0, 5), 112);
    assert_eq!(
        values(&replies[0].1),
        [
            2,
            0o046755,
            3,
            0x8000000100000002,
            u64::MAX,
            0x2000000000000000,
            i64::MIN as u64,
            999999999,
            (-5i64) as u64,
            123,
            0,
            456,
            i64::MAX as u64,
            789
        ]
    );
    assert_eq!(gets(), 1);
    assert_eq!(count(2), 0);
    clean();
}

#[test]
fn metadata_observes_current_file_and_parent_sizes_after_actual_write() {
    let commands = [
        at(7, 1, b"file", b"", 0),
        at(1, 1, b"file", b"", 22),
        data(5, 2, 0, 3, 71),
        request(12, 2),
        request(12, 1),
        data(2, 2, 0, 3, 0),
        request(4, 0),
    ];
    select(0, &commands);
    assert_eq!(invoke(31, 1000, 1000).0, 0);
    let replies = decoded(&commands);
    assert_eq!(values(&replies[3].1)[..3], [3, 0o106600, 3]);
    assert_eq!(values(&replies[4].1)[..3], [3, 0o046755, 3]);
    assert_eq!(replies[5].1, pattern(3, 71));
    assert_eq!(gets(), 2);
    assert_eq!(count(2), 2);
    clean();
}

#[test]
fn metadata_right_is_explicit_and_attenuated_across_lookup() {
    for rights in [1, 2, 4, 8, 15] {
        let commands = [request(12, 1), request(4, 0)];
        select(0, &commands);
        assert_eq!(invoke(rights, 1000, 1000).0, 0);
        let replies = decoded(&commands);
        assert_eq!(word(&replies[0].0, 1) as i64, -13);
        assert!(replies[0].1.is_empty());
        assert_eq!(gets(), 0);
        clean();
    }
    let commands = [
        at(7, 1, b"file", b"", 0),
        at(1, 1, b"file", b"", 2),
        request(12, 2),
        at(1, 1, b"file", b"", 16),
        request(12, 3),
        request(4, 0),
    ];
    select(0, &commands);
    assert_eq!(invoke(31, 1000, 1000).0, 0);
    let replies = decoded(&commands);
    assert_eq!(word(&replies[2].0, 1) as i64, -13);
    assert_eq!(values(&replies[4].1)[..3], [0, 0o106600, 3]);
    assert_eq!(gets(), 1);
    assert_eq!(count(2), 1);
    clean();
}

#[test]
fn old_version_reserved_fields_and_closed_tokens_never_call_getter() {
    for field in [0, 2, 4, 5, 6, 7] {
        let mut bad = request(12, 1);
        match field {
            0 => bad.header[7] = b'6',
            2 => put(&mut bad.header, 2, READER + 1),
            _ => put(&mut bad.header, field, 1),
        }
        let commands = [bad, request(4, 0)];
        select(0, &commands);
        assert_eq!(invoke(31, 1000, 1000).0, 0);
        assert_ne!(word(&decoded(&commands)[0].0, 1), 0);
        assert_eq!(gets(), 0);
        clean();
    }
    let commands = [request(3, 1), request(12, 1), request(4, 0)];
    select(0, &commands);
    assert_eq!(invoke(31, 1000, 1000).0, 0);
    assert_eq!(word(&decoded(&commands)[1].0, 1) as i64, -9);
    assert_eq!(gets(), 0);
    clean();
}

#[test]
fn provider_failures_never_publish_partial_metadata_or_dispatch_after_retirement() {
    for mode in 1..=7 {
        let commands = [request(12, 1), request(4, 0)];
        select(mode, &commands);
        let (code, out) = invoke(31, 1000, 1000);
        assert_eq!(code, if mode == 1 { 0 } else { 5 });
        assert_eq!(out.requests, if mode == 1 { 2 } else { 1 });
        let reply = decoded(&commands);
        assert_eq!(word(&reply[0].0, 1) as i64, -5);
        assert!(reply[0].0[24..48].iter().all(|b| *b == 0));
        assert!(reply[0].1.is_empty());
        assert_eq!(gets(), 1);
        assert_eq!(count(2), 0);
        clean();
    }
}

#[test]
fn every_metadata_reply_prefix_loss_ends_without_replay_or_mutation() {
    for prefix in 0..192 {
        let commands = [request(12, 1), request(12, 1), request(4, 0)];
        select(0, &commands);
        STATE.with(|s| s.borrow_mut().fail_after = Some(64 + prefix));
        let (code, out) = invoke(31, 1000, 1000);
        assert_eq!((code, out.stop, out.requests), (5, 2, 1));
        assert_eq!(gets(), 1);
        assert_eq!(count(2), 0);
        clean();
    }
}

#[test]
fn policy_rejects_foreign_session_before_getter() {
    select(0, &[]);
    let mut marker = 0u64;
    // SAFETY: live distinct fixture SPA marker, exact typed C ABI, exclusive
    // context retained by the owner until shutdown; no native authority claim.
    let mut spa = unsafe { Spa::from_raw(NonNull::from(&mut marker).cast()) };
    let mut owner = Owner::new(spa.open(c"testpool_zstd/x86_64").unwrap(), RuntimeUtc, 71).unwrap();
    let a = owner.attach(101, Rights::new(16).unwrap()).unwrap();
    let b = owner.attach(102, Rights::new(16).unwrap()).unwrap();
    assert!(matches!(
        owner.metadata(102, a.session, a.root.handle),
        Err(policy::Error::Denied)
    ));
    assert!(matches!(
        owner.metadata(102, b.session, a.root.handle),
        Err(policy::Error::Denied)
    ));
    assert_eq!(gets(), 0);
    owner.disconnect(101, a.session).unwrap();
    assert!(matches!(
        owner.metadata(101, a.session, a.root.handle),
        Err(policy::Error::Stale)
    ));
    assert_eq!(gets(), 0);
    owner.shutdown();
    assert_eq!(count(0), count(1));
}

#[test]
fn backend_without_metadata_support_fails_explicitly() {
    struct Unsupported;
    impl policy::Backend for Unsupported {
        fn root(&mut self) -> Result<policy::Node, policy::Error> {
            Ok(policy::Node::new(34, 45, 2, policy::Kind::Directory))
        }
        fn lookup(&mut self, _: policy::Node, _: &[u8]) -> Result<policy::Node, policy::Error> {
            Err(policy::Error::Invalid)
        }
        fn read(&mut self, _: policy::Node, _: u64, _: &mut [u8]) -> Result<usize, policy::Error> {
            Err(policy::Error::Invalid)
        }
        fn write(
            &mut self,
            _: policy::Node,
            _: u64,
            _: &[u8],
            _: policy::Utc,
        ) -> Result<policy::Completion, policy::Lost> {
            Err(policy::Lost)
        }
        fn mutate(
            &mut self,
            _: policy::Node,
            _: policy::Namespace<'_>,
            _: policy::Utc,
        ) -> Result<policy::Completion, policy::Lost> {
            Err(policy::Lost)
        }
    }
    let mut owner = Owner::new(Unsupported, RuntimeUtc, 1).unwrap();
    let a = owner.attach(1, Rights::new(16).unwrap()).unwrap();
    assert!(matches!(
        owner.metadata(1, a.session, a.root.handle),
        Err(policy::Error::Unsupported)
    ));
}
