// SPDX-License-Identifier: BSD-2-Clause
//! Actual bridge near-overflow state with the same typed C fixture.
use super::*;
unsafe extern "C" {
    fn mixed_reset(mode: u32);
    fn mixed_count(index: u32) -> u32;
}
#[test]
fn bridge_last_namespace_retirement_keeps_the_counter_and_denies_further_calls() {
    // SAFETY: serial host tests, no previous context remains.
    unsafe { mixed_reset(0) };
    let mut marker = 0u64;
    // SAFETY: retained exclusive marker SPA and synchronous typed provider.
    let mut spa = unsafe { Spa::from_raw(NonNull::new((&mut marker as *mut u64).cast()).unwrap()) };
    let mut provider = spa.open(c"testpool_zstd/x86_64").unwrap();
    provider.writes = policy::MutationCount::MAX - 1;
    let time = Utc {
        seconds: 1791290040,
        nanoseconds: 123,
    };
    let directory = Node::new(34, 45, 1, Kind::Directory);
    let result = provider
        .namespace_mutation(
            directory,
            policy::Namespace::Create {
                name: b"p",
                uid: 1000,
                gid: 1000,
            },
            time,
        )
        .unwrap();
    assert_eq!((result.error, result.txg, result.state), (0, 788, 2));
    assert_eq!(
        provider.writes,
        policy::MutationCount::MAX,
        "RUNTIME_BRIDGE_COUNTER"
    );
    for _ in 0..3 {
        let result = provider
            .write(Node::new(99, 788, 0, Kind::File), 0, &[71; 16], time)
            .unwrap();
        assert_eq!(
            (result.error, result.txg, result.bytes_staged, result.state),
            (28, 0, 0, 0),
            "RUNTIME_BRIDGE_WRITE_OVERFLOW"
        );
        let result = provider
            .namespace_mutation(
                directory,
                policy::Namespace::Create {
                    name: b"p",
                    uid: 1000,
                    gid: 1000,
                },
                time,
            )
            .unwrap();
        assert_eq!(
            (result.error, result.txg, result.bytes_staged, result.state),
            (28, 0, 0, 0),
            "RUNTIME_BRIDGE_NAMESPACE_OVERFLOW"
        );
    }
    drop(provider);
    // SAFETY: read-only serial fixture counters, after consuming the context.
    unsafe {
        assert_eq!(mixed_count(2), 1);
        assert_eq!(mixed_count(4), 0);
        assert_eq!(mixed_count(5), 0);
        assert_eq!(mixed_count(0), mixed_count(1));
    }
}
