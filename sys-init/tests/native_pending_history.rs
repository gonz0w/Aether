// SPDX-License-Identifier: BSD-2-Clause
//! Synthetic host comparison tests; private native minting is qualified on target.
#[path = "../prototypes/native-supervisor/pending_history.rs"]
mod pending_history;
#[path = "../prototypes/native-supervisor/sample_receipts.rs"]
mod sample_receipts;
use pending_history::{Replay, View};
use sample_receipts::{Raw, Sample};
fn terminal() -> Sample {
    let mut sample = Sample::new();
    for raw in [
        Raw {
            rax: 7,
            rdx: 18,
            r8: 1,
        },
        Raw {
            rax: 18,
            rdx: 1,
            r8: 1,
        },
        Raw {
            rax: 7,
            rdx: 18,
            r8: 1,
        },
    ] {
        assert!(sample.push(raw));
    }
    sample
}
#[test]
fn duplicate_preserves_exact_sample() {
    let owner = 4u64;
    let token = [1u64; 10];
    let sample = terminal();
    let before = sample.clone();
    let view = View::terminal(&owner, &token, 0, 0xb0000101u64, &sample).unwrap();
    for _ in 0..3 {
        assert_eq!(
            view.replay(&owner, &token, 0, 0xb0000101),
            Replay::Duplicate
        );
    }
    assert!(core::ptr::eq(view.sample(), &sample));
    assert_eq!(view.sample(), &before);
}
#[test]
fn every_identity_field_denies() {
    let owner = 4u64;
    let foreign = std::hint::black_box(4u64);
    let token = [1u64; 10];
    let sample = terminal();
    let view = View::terminal(&owner, &token, 0, 0xb0000101u64, &sample).unwrap();
    for field in 0..10 {
        let mut wrong = token;
        wrong[field] += 1;
        assert_eq!(
            view.replay(&owner, &wrong, 0, 0xb0000101),
            Replay::Denied,
            "every token field must deny substitution"
        );
    }
    assert_eq!(view.replay(&foreign, &token, 0, 0xb0000101), Replay::Denied);
    assert_eq!(view.replay(&owner, &token, 1, 0xb0000101), Replay::Denied);
    assert_eq!(view.replay(&owner, &token, 0, 0xb0000102), Replay::Denied);
    assert_eq!(view.replay(&owner, &token, 0, 0xb0000201), Replay::Denied);
    assert_eq!(view.sample(), &sample);
}
#[test]
fn nonterminal_cannot_mint() {
    let owner = 4u64;
    let token = [1u64; 10];
    let mut empty = Sample::new();
    let mut live = Sample::new();
    live.push(Raw {
        rax: 0,
        rdx: 0,
        r8: 0,
    });
    let mut failed = Sample::new();
    failed.push(Raw {
        rax: -9,
        rdx: 0,
        r8: 0,
    });
    let mut partial = Sample::new();
    partial.push(Raw {
        rax: 7,
        rdx: 18,
        r8: 1,
    });
    for sample in [&empty, &live, &failed, &partial] {
        assert!(View::terminal(&owner, &token, 0, 0xb0000101u64, sample).is_none());
    }
    assert!(partial.interrupt());
    assert!(View::terminal(&owner, &token, 0, 0xb0000101u64, &partial).is_none());
    // Sample's terminal seal refuses writes before the view is constructed.
    empty = terminal();
    let before = empty.clone();
    assert!(!empty.push(Raw {
        rax: 99,
        rdx: 0,
        r8: 0
    }));
    assert_eq!(empty, before);
}

use pending_history::{Held, Offer};
use std::cell::Cell;
fn qualified(revision: i64, result: u64, kind: u64, ready: bool) -> Sample {
    let mut sample = Sample::new();
    for raw in [
        Raw {
            rax: revision,
            rdx: result,
            r8: ready as u64,
        },
        Raw {
            rax: result as i64,
            rdx: ready as u64,
            r8: kind,
        },
        Raw {
            rax: revision,
            rdx: result,
            r8: ready as u64,
        },
    ] {
        assert!(sample.push(raw));
    }
    assert!(matches!(
        sample.state(),
        sample_receipts::State::Terminal(_)
    ));
    sample
}
#[test]
fn independent_duplicate_keeps_primary() {
    let owner = 4u64;
    let token = [1u64; 10];
    let first = terminal();
    let other = terminal();
    let mut held = Held::new(View::terminal(&owner, &token, 0, 1u64, &first).unwrap());
    for _ in 0..3 {
        assert_eq!(
            held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
                &owner, &token, 0, 1, &other
            )),
            Offer::Duplicate
        );
    }
    assert!(core::ptr::eq(held.primary(), &first));
    assert_eq!(held.primary(), &other);
    assert!(held.diagnostic().is_none() && !held.is_closed());
}
#[test]
fn conflicts_preserve_first_and_candidate() {
    let owner = 4u64;
    let token = [1u64; 10];
    let first = terminal();
    for candidate in [
        qualified(8, 18, 1, true),
        qualified(7, 19, 1, true),
        qualified(7, 135, 2, true),
        qualified(7, 18, 1, false),
    ] {
        let mut held = Held::new(View::terminal(&owner, &token, 0, 1u64, &first).unwrap());
        assert_eq!(
            held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
                &owner, &token, 0, 1, &candidate
            )),
            Offer::Conflict,
            "different qualified history must conflict"
        );
        assert!(
            core::ptr::eq(held.primary(), &first),
            "first history must never be replaced"
        );
        assert_eq!(held.primary(), &first);
        assert!(core::ptr::eq(held.diagnostic().unwrap(), &candidate));
        assert_eq!(held.diagnostic(), Some(&candidate));
        assert!(held.is_closed(), "conflict must close the local store");
    }
}
#[test]
fn closed_store_does_not_produce() {
    let owner = 4u64;
    let token = [1u64; 10];
    let first = terminal();
    let conflict = qualified(7, 19, 1, true);
    let later = qualified(9, 20, 1, true);
    let mut held = Held::new(View::terminal(&owner, &token, 0, 1u64, &first).unwrap());
    assert_eq!(
        held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
            &owner, &token, 0, 1, &conflict
        )),
        Offer::Conflict
    );
    let calls = Cell::new(0);
    for sample in [&first, &conflict, &later] {
        let outcome = held.offer_synthetic(&owner, &token, 0, 1, || {
            calls.set(calls.get() + 1);
            View::terminal(&owner, &token, 0, 1, sample)
        });
        assert_eq!(
            calls.get(),
            0,
            "closed store must deny before candidate production"
        );
        assert_eq!(outcome, Offer::Closed);
        assert_eq!(held.primary(), &first);
        assert_eq!(held.diagnostic(), Some(&conflict));
    }
}
#[test]
fn wrong_request_denies_before_production() {
    let owner = 4u64;
    let foreign = std::hint::black_box(4u64);
    let token = [1u64; 10];
    let first = terminal();
    let mut held = Held::new(View::terminal(&owner, &token, 0, 0xb0000101u64, &first).unwrap());
    let calls = Cell::new(0);
    let mut deny = |owner: &u64, token: &[u64; 10], index, worker| {
        assert_eq!(
            held.offer_synthetic(owner, token, index, worker, || {
                calls.set(calls.get() + 1);
                None
            }),
            Offer::Denied
        );
    };
    for field in 0..10 {
        let mut wrong = token;
        wrong[field] += 1;
        deny(&owner, &wrong, 0, 0xb0000101);
    }
    deny(&foreign, &token, 0, 0xb0000101);
    deny(&owner, &token, 1, 0xb0000101);
    deny(&owner, &token, 2, 0xb0000101);
    deny(&owner, &token, 0, 0xb0000102);
    deny(&owner, &token, 0, 0xb0000201);
    assert_eq!(calls.get(), 0);
    assert!(held.diagnostic().is_none() && !held.is_closed());
    assert!(core::ptr::eq(held.primary(), &first));
}
#[test]
fn produced_identity_and_absent_view_deny() {
    let owner = 4u64;
    let foreign = std::hint::black_box(4u64);
    let token = [1u64; 10];
    let first = terminal();
    let different = qualified(7, 19, 1, true);
    let mut held = Held::new(View::terminal(&owner, &token, 0, 1u64, &first).unwrap());
    assert_eq!(
        held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
            &foreign, &token, 0, 1, &different
        )),
        Offer::Denied
    );
    for field in 0..10 {
        let mut wrong = token;
        wrong[field] += 1;
        // A separate store keeps the candidate token's borrow inside this iteration.
        let mut scoped = Held::new(View::terminal(&owner, &token, 0, 1u64, &first).unwrap());
        assert_eq!(
            scoped.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
                &owner, &wrong, 0, 1, &different
            )),
            Offer::Denied
        );
        assert!(scoped.diagnostic().is_none() && !scoped.is_closed());
    }
    for (index, worker) in [(1, 1), (0, 2)] {
        assert_eq!(
            held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
                &owner, &token, index, worker, &different
            )),
            Offer::Denied
        );
    }
    let partial = Sample::new();
    assert_eq!(
        held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
            &owner, &token, 0, 1, &partial
        )),
        Offer::Denied
    );
    assert!(held.diagnostic().is_none() && !held.is_closed());
    assert_eq!(held.primary(), &first);
}

#[test]
fn equal_result_different_kind_conflicts() {
    let owner = 4u64;
    let token = [1u64; 10];
    for (kind, result) in [(2, 135), (3, 144)] {
        let first = qualified(7, result, 1, true);
        let other = qualified(7, result, kind, true);
        let mut held = Held::new(View::terminal(&owner, &token, 0, 1u64, &first).unwrap());
        assert_eq!(
            held.offer_synthetic(&owner, &token, 0, 1, || View::terminal(
                &owner, &token, 0, 1, &other
            )),
            Offer::Conflict
        );
        assert_eq!(held.primary(), &first);
        assert_eq!(held.diagnostic(), Some(&other));
        assert!(held.is_closed());
    }
}
