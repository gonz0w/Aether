// SPDX-License-Identifier: BSD-2-Clause
#[path = "../prototypes/native-supervisor/sample_receipts.rs"]
mod receipts;
use receipts::{Cause, Fact, Failure, Raw, Sample, State};
fn raw(rax: i64, rdx: u64, r8: u64) -> Raw {
    Raw { rax, rdx, r8 }
}
fn complete(rows: [Raw; 3]) -> Sample {
    let mut s = Sample::new();
    for row in rows {
        assert!(s.push(row));
    }
    s
}
fn normal() -> [Raw; 3] {
    [raw(7, 18, 1), raw(18, 1, 1), raw(7, 18, 1)]
}
fn sealed(s: &mut Sample) {
    let old = s.clone();
    assert!(!s.push(raw(-9, 999, 999)));
    assert!(!s.interrupt());
    assert_eq!(*s, old);
}
#[test]
fn terminal_mapping_and_collisions() {
    for (kind, result) in [(1, 1), (1, 256), (1, 135), (2, 135), (1, 144), (3, 144)] {
        for ready in [0, 1] {
            let rows = [
                raw(7, result, ready),
                raw(result as i64, ready, kind),
                raw(7, result, ready),
            ];
            let mut s = complete(rows);
            assert_eq!(
                s.state(),
                State::Terminal(Fact {
                    revision: 7,
                    result,
                    kind,
                    historical_ready: ready == 1
                })
            );
            assert_eq!(s.receipts(), &rows.map(Some));
            assert_eq!(s.received(), 3);
            sealed(&mut s);
        }
    }
}
#[test]
fn live_is_one_receipt_without_fact() {
    for revision in [0, 7, i64::MAX] {
        let mut s = Sample::new();
        let row = raw(revision, 0, 0);
        assert!(s.push(row));
        assert_eq!(s.state(), State::Live);
        assert_eq!(s.receipts(), &[Some(row), None, None]);
        assert_eq!(s.received(), 1);
        sealed(&mut s);
    }
}
#[test]
fn prefix_survives_native_error() {
    for index in 0..3 {
        for errno in [9, 71, 1u64 << 63] {
            let mut rows = normal();
            rows[index] = raw(-(errno as i128) as i64, u64::MAX, u64::MAX);
            let mut s = Sample::new();
            for row in &rows[..=index] {
                assert!(s.push(*row));
            }
            let mut expected = [None; 3];
            for n in 0..=index {
                expected[n] = Some(rows[n]);
            }
            assert_eq!(
                s.receipts(),
                &expected,
                "received prefix must survive native rejection"
            );
            assert_eq!(
                s.state(),
                State::Failed(Failure::Native {
                    operation: if index == 1 { 0x20001 } else { 0x25001 },
                    errno
                })
            );
            assert_eq!(s.received(), index + 1);
            sealed(&mut s);
        }
    }
}
#[test]
fn invalid_booleans_are_local() {
    for index in 0..3 {
        for invalid in [2, u64::MAX] {
            let mut rows = normal();
            if index == 1 {
                rows[index].rdx = invalid;
            } else {
                rows[index].r8 = invalid;
            }
            let mut s = Sample::new();
            for row in &rows[..=index] {
                assert!(s.push(*row));
            }
            assert_eq!(
                s.state(),
                State::Failed(Failure::Local(Cause::Boolean)),
                "local rejection must not invent native errno"
            );
            assert_eq!(s.received(), index + 1);
            for (n, row) in rows.iter().enumerate() {
                assert_eq!(s.receipts()[n], if n <= index { Some(*row) } else { None });
            }
            sealed(&mut s);
        }
    }
}
#[test]
fn zero_terminal_revision_rejects_before_status() {
    let row = raw(0, 18, 1);
    let mut s = Sample::new();
    assert!(s.push(row));
    assert_eq!(
        s.state(),
        State::Failed(Failure::Local(Cause::ZeroRevision))
    );
    assert_eq!(s.receipts(), &[Some(row), None, None]);
    sealed(&mut s);
}
#[test]
fn incoherent_samples_preserve_all_receipts() {
    let mut variants = Vec::new();
    for revision in [0, 8] {
        let mut r = normal();
        r[2].rax = revision;
        variants.push((r, Cause::Revision));
    }
    for result in [0, 19] {
        let mut r = normal();
        r[1].rax = result;
        variants.push((r, Cause::Result));
        let mut r = normal();
        r[2].rdx = result as u64;
        variants.push((r, Cause::Result));
    }
    let mut r = normal();
    r[1].rdx = 0;
    variants.push((r, Cause::Readiness));
    let mut r = normal();
    r[2].r8 = 0;
    variants.push((r, Cause::Readiness));
    for (rows, cause) in variants {
        let mut s = complete(rows);
        assert_eq!(s.state(), State::Failed(Failure::Local(cause)));
        assert_eq!(s.receipts(), &rows.map(Some));
        sealed(&mut s);
    }
}
#[test]
fn unsupported_pairs_are_local_and_retained() {
    for (kind, result) in [
        (0, 18),
        (4, 18),
        (1, 257),
        (2, 18),
        (3, 135),
        (u64::MAX, 18),
    ] {
        let rows = [
            raw(7, result, 1),
            raw(result as i64, 1, kind),
            raw(7, result, 1),
        ];
        let mut s = complete(rows);
        assert_eq!(s.state(), State::Failed(Failure::Local(Cause::KindPair)));
        assert_eq!(s.receipts(), &rows.map(Some));
        sealed(&mut s);
    }
}
#[test]
fn synthetic_interruption_retains_only_received_prefix() {
    let mut empty = Sample::new();
    assert!(!empty.interrupt());
    assert_eq!(empty, Sample::new());
    for count in [1, 2] {
        let mut s = Sample::new();
        let rows = normal();
        for row in &rows[..count] {
            assert!(s.push(*row));
        }
        assert!(s.interrupt());
        assert_eq!(s.state(), State::Failed(Failure::Local(Cause::Interrupted)));
        for (n, row) in rows.iter().enumerate() {
            assert_eq!(s.receipts()[n], if n < count { Some(*row) } else { None });
        }
        assert_eq!(s.received(), count);
        sealed(&mut s);
    }
}
#[test]
fn signed_revision_and_wide_result_are_not_truncated() {
    let mut rows = normal();
    rows[0].rax = i64::MAX;
    rows[2].rax = i64::MAX;
    assert!(
        matches!(complete(rows).state(), State::Terminal(Fact { revision, .. }) if revision == i64::MAX as u64)
    );
    rows[0].rdx = u64::MAX;
    rows[2].rdx = u64::MAX;
    let s = complete(rows);
    assert_eq!(s.state(), State::Failed(Failure::Local(Cause::Result)));
    assert_eq!(s.receipts(), &rows.map(Some));
}
