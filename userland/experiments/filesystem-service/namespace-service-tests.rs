// SPDX-License-Identifier: BSD-2-Clause
//! Actual Rust entry and typed C context fixture; no native authentication claim.
use super::*;
use filesystem_service::{message, put, word, Message};
use std::{cell::RefCell, collections::VecDeque, vec::Vec};
const READER: u64 = 0x10001;
const WRITER: u64 = 0x20002;
unsafe extern "C" {
    fn namespace_reset(mode: u32);
    fn namespace_count() -> u32;
    fn namespace_kind() -> u32;
    fn fixture_count(index: u32) -> u32;
}
#[derive(Default)]
struct State {
    input: VecDeque<u8>,
    output: Vec<u8>,
    close: Vec<u64>,
    fail_after: Option<usize>,
    close_error: bool,
    context_live_at_reply: bool,
}
std::thread_local! { static STATE: RefCell<State> = RefCell::new(State::default()); }
pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64) -> i64 {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        match op {
            0x24001 => {
                assert_eq!(endpoint, READER);
                assert!(length <= 16);
                if s.input.is_empty() {
                    return 0;
                }
                let count = (length as usize).min(7).min(s.input.len());
                // SAFETY: real Framed caller retains exclusive live output chunk.
                let bytes = unsafe { core::slice::from_raw_parts_mut(pointer as *mut u8, count) };
                for b in bytes {
                    *b = s.input.pop_front().unwrap();
                }
                count as i64
            }
            0x24002 => {
                assert_eq!(endpoint, WRITER);
                assert!(length <= 16);
                if s.fail_after.is_some_and(|limit| s.output.len() >= limit) {
                    return -32;
                }
                // Mutation closes before the first byte of its response.
                if unsafe { namespace_count() } != 0 {
                    s.context_live_at_reply |=
                        unsafe { fixture_count(0) } != unsafe { fixture_count(1) };
                }
                let count = (length as usize).min(7);
                // SAFETY: real Framed caller owns this initialized readable chunk.
                let bytes = unsafe { core::slice::from_raw_parts(pointer as *const u8, count) };
                s.output.extend_from_slice(bytes);
                count as i64
            }
            0x24003 => {
                // SAFETY: serial fixture, valid fixed counter indexes. Every owned
                // success/error context must be consumed before endpoint closure.
                assert_eq!(unsafe { fixture_count(1) }, unsafe { fixture_count(0) });
                s.close.push(endpoint);
                if s.close_error {
                    -5
                } else {
                    0
                }
            }
            0x1fffe => 0,
            _ => panic!("unexpected trap"),
        }
    })
}

fn reset(mode: u32, frames: &[Message]) {
    // SAFETY: single-threaded tests; previous call consumed all owned C contexts.
    unsafe { namespace_reset(mode) };
    STATE.with(|s| {
        *s.borrow_mut() = State {
            input: frames.iter().flatten().copied().collect(),
            ..State::default()
        }
    });
}
fn calls() -> u32 {
    // SAFETY: serialized scalar fixture counter.
    unsafe { namespace_count() }
}
fn count(index: u32) -> u32 {
    // SAFETY: fixed valid counter index, no concurrent fixture operation.
    unsafe { fixture_count(index) }
}
fn mutation(op: u64) -> Message {
    let mut m = message(READER, op);
    put(&mut m, 3, 1);
    put(&mut m, 5, if op == 8 { 3 | (3 << 32) } else { 3 });
    m[48..51].copy_from_slice(if op == 7 { b"new" } else { b"old" });
    if op == 8 {
        m[51..54].copy_from_slice(b"new");
    }
    m
}
fn lookup() -> Message {
    let mut m = message(READER, 1);
    put(&mut m, 3, 1);
    put(&mut m, 4, 2);
    put(&mut m, 5, 3);
    m[48..51].copy_from_slice(b"old");
    m
}
fn invoke(rights: u64, uid: u64, gid: u64) -> (i32, ServiceResult) {
    let mut marker = 0u64;
    let mut out = ServiceResult::default();
    // SAFETY: separate retained SPA marker, immutable exact dataset/result and
    // fixed endpoint bindings. C and traps are typed host-only substitutions.
    let code = unsafe {
        aether_fs_namespace_run(
            (&mut marker as *mut u64).cast(),
            c"testpool_zstd/x86_64".as_ptr().cast(),
            20,
            READER,
            WRITER,
            rights,
            uid,
            gid,
            &mut out,
        )
    };
    (code, out)
}
fn replies() -> Vec<Message> {
    STATE.with(|s| {
        let state = s.borrow();
        let (frames, tail) = state.output.as_chunks::<64>();
        assert!(tail.is_empty());
        frames.to_vec()
    })
}
#[test]
fn three_operations_consume_context_before_one_reply_and_never_dispatch_a_second() {
    for op in 7..=9 {
        reset(0, &[mutation(op), mutation(op)]);
        let (code, out) = invoke(9, 1000, 1001);
        assert_eq!((code, out.requests, out.stop, out.error), (0, 1, 6, 0));
        assert_eq!((out.txg, out.bytes_staged, out.state), (788, 0, 2));
        assert_eq!((calls(), count(0), count(1)), (1, 1, 1));
        // SAFETY: serialized fixture scalar after completed entry.
        assert_eq!(unsafe { namespace_kind() }, op as u32 - 6);
        let frames = replies();
        assert_eq!(frames.len(), 2);
        assert_eq!(word(&frames[1], 4), 788);
        STATE.with(|s| {
            let s = s.borrow();
            assert_eq!(s.input.len(), 64);
            assert!(!s.context_live_at_reply);
            assert_eq!(s.close, [READER, WRITER]);
        });
    }
}
#[test]
fn directory_mutation_authority_is_distinct_and_identity_is_bootstrap_only() {
    for rights in [1, 2, 3, 4, 5, 6, 7, 8] {
        reset(0, &[mutation(7), message(READER, 4)]);
        let (code, out) = invoke(rights, 1000, 1001);
        assert_eq!((code, out.stop, calls()), (0, 0, 0));
        assert_eq!(word(&replies()[1], 1) as i64, -13);
    }
    for (uid, gid) in [(u64::MAX, 1001), (1000, i32::MAX as u64 + 1)] {
        reset(0, &[mutation(7)]);
        let (code, out) = invoke(9, uid, gid);
        assert_eq!((code, out.stop, out.error), (22, 4, -22));
        assert_eq!((count(0), count(1), calls()), (0, 0, 0));
        STATE.with(|s| assert!(s.borrow().close.is_empty()));
    }
}
#[test]
fn names_versions_unused_fields_and_epochs_reject_before_provider() {
    let base = mutation(7);
    let mut bad = Vec::new();
    for bytes in [b".".as_slice(), b"..", b"a/b", b"a\0b"] {
        let mut m = base;
        m[48..].fill(0);
        m[48..48 + bytes.len()].copy_from_slice(bytes);
        put(&mut m, 5, bytes.len() as u64);
        bad.push(m);
    }
    for (index, value) in [
        (2, READER + 1),
        (3, 99),
        (4, 1000),
        (5, 0),
        (5, 17),
        (5, 3 | (1 << 32)),
    ] {
        let mut m = base;
        put(&mut m, index, value);
        bad.push(m);
    }
    let mut m = base;
    m[..8].copy_from_slice(b"AFSRPC01");
    bad.push(m);
    let mut m = base;
    m[63] = 1;
    bad.push(m);
    let mut m = mutation(8);
    m[51..54].copy_from_slice(b"old");
    bad.push(m);
    let mut m = mutation(8);
    put(&mut m, 5, 3);
    m[51..].fill(0);
    bad.push(m);
    for frame in bad {
        reset(0, &[frame, message(READER, 4)]);
        let (code, out) = invoke(9, 1000, 1001);
        assert_eq!((code, out.stop, out.requests, calls()), (0, 0, 2, 0));
        assert_ne!(word(&replies()[1], 1), 0);
    }
}
#[test]
fn remove_rejects_live_alias_until_close_and_never_uses_client_object_ids() {
    let mut close = message(READER, 3);
    put(&mut close, 3, 2);
    reset(0, &[lookup(), mutation(9), close, mutation(9), mutation(9)]);
    let (code, out) = invoke(11, 1000, 1001);
    assert_eq!((code, out.stop, out.requests, calls()), (0, 6, 4, 1));
    assert_eq!(word(&replies()[2], 1) as i64, -13);
}
#[test]
fn all_original_progress_classes_are_retained_or_rejected_without_replay() {
    for mode in 1..=8 {
        reset(mode, &[mutation(7), mutation(7)]);
        let (code, out) = invoke(9, 1000, 1001);
        assert_eq!(
            (code, out.requests, out.stop, calls(), count(1)),
            (5, 1, 5, 1, 1)
        );
        if mode == 1 {
            assert_eq!((out.txg, out.bytes_staged, out.state), (0, 0, 0));
        } else if mode == 2 || mode == 3 {
            assert_eq!(
                (out.txg, out.bytes_staged, out.state),
                (if mode == 3 { 0 } else { 788 }, 0, 1)
            );
        } else if mode == 7 || mode == 8 {
            assert_eq!((out.txg, out.bytes_staged, out.state), (788, 0, 2));
        } else {
            assert_eq!(out.state, 3);
        }
    }
}
#[test]
fn lost_partial_replies_and_endpoint_errors_do_not_replay_or_erase_mutation() {
    for sent in [64, 71, 127] {
        reset(0, &[mutation(7), mutation(7)]);
        STATE.with(|s| s.borrow_mut().fail_after = Some(sent));
        let (code, out) = invoke(9, 1000, 1001);
        assert_eq!(
            (code, out.stop, out.error, out.txg, out.state, calls()),
            (5, 2, -32, 788, 2, 1)
        );
        assert_eq!(count(1), 1);
    }
    reset(0, &[mutation(7)]);
    STATE.with(|s| s.borrow_mut().close_error = true);
    let (code, out) = invoke(9, 1000, 1001);
    assert_eq!(
        (
            code,
            out.stop,
            out.error,
            out.reader_close,
            out.writer_close
        ),
        (5, 6, -5, -5, -5)
    );
    assert_eq!((out.txg, out.state, calls()), (788, 2, 1));
    for prefix in 0..64 {
        reset(0, &[]);
        STATE.with(|s| {
            s.borrow_mut()
                .input
                .extend(mutation(7)[..prefix].iter().copied())
        });
        let (code, out) = invoke(9, 1000, 1001);
        assert_eq!((code, out.stop, out.requests, calls()), (5, 1, 0, 0));
        assert_eq!(count(1), 1);
    }
}
#[test]
fn setup_clock_and_lookup_failures_leave_no_context_or_provider_escape() {
    for mode in [9, 10, 11, 12] {
        reset(
            mode,
            &[mutation(if mode == 10 { 9 } else { 7 }), message(READER, 4)],
        );
        let (code, out) = invoke(9, 1000, 1001);
        assert_eq!(calls(), 0);
        assert_eq!(count(0), count(1));
        if mode >= 11 {
            assert_eq!((code, out.stop), (5, 4));
        } else {
            assert_eq!((code, out.stop), (0, 0));
        }
    }
}
#[test]
fn policy_checks_all_connections_and_shared_write_budget_without_ambient_identity() {
    use filesystem_bridge::policy::{Error, Identity, Kind, Mutation};
    reset(0, &[]);
    let mut marker = 0u64;
    // SAFETY: unique retained marker/context backed by typed serialized fixture.
    let mut spa = unsafe { Spa::from_raw(NonNull::new((&mut marker as *mut u64).cast()).unwrap()) };
    let backend = spa.open(c"testpool_zstd/x86_64").unwrap();
    let mut owner = Owner::new(backend, RuntimeUtc, READER).unwrap();
    let first = owner.attach(101, Rights::ALL).unwrap();
    assert_eq!(
        owner.namespace(
            101,
            first.session,
            first.root.handle,
            Mutation::Create(b"new")
        ),
        Err(Error::Denied)
    );
    let mut owner = owner.with_namespace_identity(Identity::new(1000, 1001).unwrap());
    let second = owner.attach(202, Rights::ALL).unwrap();
    let alias = owner
        .lookup(
            202,
            second.session,
            second.root.handle,
            b"old",
            Rights::READ,
        )
        .unwrap();
    assert_eq!(alias.kind, Kind::File);
    assert_eq!(
        owner.namespace(
            101,
            first.session,
            first.root.handle,
            Mutation::Remove(b"old")
        ),
        Err(Error::Denied)
    );
    assert_eq!(
        owner.namespace(
            202,
            first.session,
            first.root.handle,
            Mutation::Create(b"new")
        ),
        Err(Error::Denied)
    );
    owner.close(202, second.session, alias.handle).unwrap();
    let file = owner
        .lookup(
            101,
            first.session,
            first.root.handle,
            b"zstd",
            Rights::WRITE,
        )
        .unwrap();
    owner
        .write(101, first.session, file.handle, 37, b"abcdefghijklmnop")
        .unwrap();
    assert_eq!(
        owner.namespace(
            101,
            first.session,
            first.root.handle,
            Mutation::Create(b"new")
        ),
        Err(Error::WriteLimit)
    );
    assert_eq!(calls(), 0);
    owner.shutdown();
    assert_eq!(
        owner.stat(101, first.session, first.root.handle),
        Err(Error::Closed)
    );
}
