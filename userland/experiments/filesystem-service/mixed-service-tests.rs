// SPDX-License-Identifier: BSD-2-Clause
//! Actual mixed Rust entry with typed host C/transport substitutions only.
use super::*;
use filesystem_service::{message, put, word, Message};
use std::{cell::RefCell, collections::VecDeque, vec, vec::Vec};
const READER: u64 = 0x10001;
const WRITER: u64 = 0x20002;
unsafe extern "C" {
    fn mixed_reset(mode: u32);
    fn mixed_count(index: u32) -> u32;
}
fn count(index: u32) -> u32 {
    // SAFETY: fixed valid scalar fixture index, serial host tests.
    unsafe { mixed_count(index) }
}
#[derive(Default)]
struct State {
    input: VecDeque<u8>,
    output: Vec<u8>,
    closed: Vec<u64>,
    close_errors: [i64; 2],
    fail_after: Option<usize>,
    bad_lifetime: bool,
    #[cfg(fs_wait)]
    stalls: [bool; 2],
    #[cfg(fs_wait)]
    waits: [usize; 2],
    #[cfg(fs_wait)]
    spurious: usize,
    #[cfg(fs_wait)]
    backpressure: bool,
    #[cfg(fs_wait)]
    wait_error: Option<(bool, usize, i64)>,
}
std::thread_local! { static STATE: RefCell<State> = RefCell::new(State::default()); }
pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64) -> i64 {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        match op {
            0x24001 => {
                assert_eq!(endpoint, READER);
                assert!(length <= 16);
                #[cfg(fs_wait)]
                if s.stalls[0] {
                    return -11;
                }
                if s.input.is_empty() {
                    return 0;
                }
                let n = (length as usize).min(7).min(s.input.len());
                // SAFETY: real Framed retains initialized writable chunk.
                let bytes = unsafe { core::slice::from_raw_parts_mut(pointer as *mut u8, n) };
                for b in bytes {
                    *b = s.input.pop_front().unwrap();
                }
                #[cfg(fs_wait)]
                {
                    s.stalls[0] = s.backpressure;
                }
                n as i64
            }
            0x24002 => {
                assert_eq!(endpoint, WRITER);
                assert!(length <= 16);
                #[cfg(fs_wait)]
                if s.stalls[1] {
                    return -11;
                }
                if s.fail_after.is_some_and(|limit| s.output.len() >= limit) {
                    return -32;
                }
                // Never panic across the entry's C ABI for lifecycle mutants.
                // A successful old context must retire before any response byte;
                // failed/unknown attempts must instead consume every context.
                s.bad_lifetime |= count(2) > count(3) && count(5) != 0;
                let remaining = s
                    .fail_after
                    .map_or(usize::MAX, |limit| limit - s.output.len());
                let n = (length as usize).min(7).min(remaining);
                // SAFETY: real Framed retains initialized readable chunk.
                s.output.extend_from_slice(unsafe {
                    core::slice::from_raw_parts(pointer as *const u8, n)
                });
                #[cfg(fs_wait)]
                {
                    s.stalls[1] = s.backpressure;
                }
                n as i64
            }
            0x24003 => {
                s.bad_lifetime |= count(5) != 0 || count(0) != count(1);
                let index = s.closed.len();
                s.closed.push(endpoint);
                s.close_errors[index]
            }
            #[cfg(not(fs_wait))]
            0x1fffe => 0,
            #[cfg(fs_wait)]
            0x24004 => {
                assert_eq!((pointer, length), (0, 0), "WAIT_NO_POINTER");
                let writing = endpoint == WRITER;
                assert!(writing || endpoint == READER, "WAIT_ENDPOINT");
                let index = usize::from(writing);
                assert!(s.stalls[index], "WAIT_AFTER_EAGAIN");
                s.waits[index] += 1;
                if let Some((direction, after, error)) = s.wait_error {
                    if writing == direction && s.output.len() >= after {
                        return error;
                    }
                }
                if s.spurious != 0 {
                    s.spurious -= 1;
                } else {
                    s.stalls[index] = false;
                }
                0
            }
            _ => panic!("unexpected trap"),
        }
    })
}
fn reset(mode: u32, frames: &[Message]) {
    // SAFETY: serial tests, previous entry consumed its provider obligation.
    unsafe { mixed_reset(mode) };
    STATE.with(|s| {
        *s.borrow_mut() = State {
            input: frames.iter().flatten().copied().collect(),
            ..State::default()
        }
    });
}
fn request(op: u64, token: u64) -> Message {
    let mut m = message(READER, op);
    put(&mut m, 3, token);
    m
}
fn namespace(op: u64, from: u8, to: Option<u8>) -> Message {
    let mut m = request(op, 1);
    put(&mut m, 5, 1 | if to.is_some() { 1 << 32 } else { 0 });
    m[48] = from;
    if let Some(to) = to {
        m[49] = to;
    }
    m
}
fn lookup(name: u8, rights: u64) -> Message {
    let mut m = request(1, 1);
    put(&mut m, 4, rights);
    put(&mut m, 5, 1);
    m[48] = name;
    m
}
fn data(op: u64, token: u64, offset: u64, seed: u8) -> Message {
    let mut m = request(op, token);
    put(&mut m, 4, offset);
    put(&mut m, 5, 16);
    if op == 5 {
        for (i, b) in m[48..].iter_mut().enumerate() {
            *b = seed.wrapping_add(i as u8);
        }
    }
    m
}
fn workload(disconnect: bool) -> Vec<Message> {
    let mut frames = vec![
        namespace(7, b'p', None),
        lookup(b'p', 6),
        data(5, 2, 0, 11),
        data(5, 2, 16, 31),
        namespace(8, b'p', Some(b'q')),
        request(6, 2),
        data(2, 2, 0, 0),
        data(5, 2, 32, 51),
        namespace(9, b'q', None),
        lookup(b'q', 2),
        request(3, 2),
        namespace(9, b'q', None),
        request(3, 3),
        namespace(9, b'q', None),
        namespace(7, b'p', None),
        data(2, 2, 0, 0),
        lookup(b'p', 6),
        data(5, 4, 0, 71),
        request(6, 4),
        data(2, 4, 0, 0),
        data(2, 4, 16, 0),
        namespace(7, b'r', None),
        data(5, 4, 0, 91),
        request(3, 4),
    ];
    if disconnect {
        frames.push(message(READER, 4));
    }
    frames
}
fn invoke(rights: u64, uid: u64, gid: u64) -> (i32, ServiceResult) {
    let mut marker = 0u64;
    let mut out = ServiceResult::default();
    // SAFETY: independent initialized output, retained SPA/dataset and explicit
    // authenticated endpoint substitutes. Host C mock implements exact ABI.
    let code = unsafe {
        aether_fs_mixed_run(
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
    STATE.with(|s| s.borrow().output.as_chunks::<64>().0.to_vec())
}
fn clean() {
    assert_eq!(count(4), 0, "typed provider violation");
    assert_eq!(count(5), 0);
    assert_eq!(count(0), count(1));
    STATE.with(|s| {
        let s = s.borrow();
        assert_eq!(s.closed, [READER, WRITER]);
        assert!(!s.bad_lifetime);
    });
}
#[test]
fn eight_shared_attempts_aliases_rename_recreate_data_eof_and_no_ninth_dispatch() {
    let frames = workload(true);
    reset(0, &frames);
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop, out.requests), (0, 0, frames.len() as u64));
    assert_eq!((out.txg, out.bytes_staged, out.state), (795, 16, 2));
    assert_eq!((count(2), count(3), count(6), count(7)), (8, 8, 4, 4));
    assert_eq!((count(0), count(1)), (9, 9));
    clean();
    let r = replies();
    assert_eq!(r[0][..8], *b"AFSRPC03");
    for (i, frame) in frames.iter().enumerate() {
        let expected = if i == 8 || i == 11 {
            -13
        } else if i == 15 {
            -9
        } else if i == 21 || i == 22 {
            -28
        } else {
            0
        };
        assert_eq!(
            word(&r[i + 1], 1) as i64,
            expected,
            "opcode {} at{i}",
            word(frame, 1)
        );
    }
    assert_eq!(word(&r[6], 5), 32); // stat after rename, same original token.
    assert_eq!(r[7][48..], data(5, 2, 0, 11)[48..]);
    assert_eq!(word(&r[19], 5), 16);
    assert_eq!(r[20][48..], data(5, 4, 0, 71)[48..]);
    assert_eq!(word(&r[21], 5), 0);
}
#[test]
fn all_namespace_progress_classes_and_post_retirement_failures_are_retained() {
    for (mode, txg, state) in [
        (1, 0, 0),
        (2, 788, 1),
        (3, 0, 1),
        (4, 0, 3),
        (5, 0, 3),
        (6, 0, 3),
        (7, 788, 2),
        (8, 788, 2),
        (13, 788, 2),
        (14, 788, 2),
        (15, 788, 2),
    ] {
        reset(mode, &[namespace(7, b'p', None), namespace(7, b'p', None)]);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.requests), (5, 5, 1), "mode{mode}");
        assert_eq!((out.txg, out.state), (txg, state), "mode{mode}");
        assert_eq!(count(2), 1);
        clean();
    }
}
#[test]
fn failed_writes_preserve_current_zero_or_committed_progress_after_prior_create() {
    for (mode, txg, staged, state) in [
        (16, 789, 16, 2),
        (17, 0, 0, 0),
        (18, 0, 16, 1),
        (19, 789, 16, 2),
    ] {
        reset(
            mode,
            &[
                namespace(7, b'p', None),
                lookup(b'p', 6),
                data(5, 2, 0, 11),
                namespace(7, b'p', None),
            ],
        );
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.requests), (5, 5, 3), "mode{mode}");
        assert_eq!(
            (out.txg, out.bytes_staged, out.state),
            (txg, staged, state),
            "mode{mode}"
        );
        assert_eq!(count(2), 2);
        clean();
    }
}
#[test]
fn every_first_reply_loss_prefix_retires_without_another_dispatch() {
    for prefix in 0..64 {
        reset(0, &[namespace(7, b'p', None), lookup(b'p', 6)]);
        STATE.with(|s| s.borrow_mut().fail_after = Some(64 + prefix));
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (code, out.stop, out.requests, out.txg, out.state),
            (5, 2, 1, 788, 2)
        );
        assert_eq!((count(2), count(3)), (1, 1));
        clean();
    }
}
#[test]
fn every_partial_input_prefix_before_and_after_eight_transactions_never_dispatches() {
    for after in [false, true] {
        for prefix in 0..64 {
            let frames = if after { workload(false) } else { vec![] };
            reset(0, &frames);
            let partial = namespace(7, b'r', None);
            STATE.with(|s| s.borrow_mut().input.extend(&partial[..prefix]));
            let (code, out) = invoke(15, 1000, 1000);
            assert_eq!((code, out.stop, out.requests), (5, 1, frames.len() as u64));
            assert_eq!(count(2), if after { 8 } else { 0 });
            clean();
        }
    }
}
#[test]
fn endpoint_close_errors_remain_exact_after_provider_consumption() {
    for errors in [[-13, 0], [0, -32], [-13, -32]] {
        reset(0, &workload(true));
        STATE.with(|s| s.borrow_mut().close_errors = errors);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.txg, out.state), (5, 0, 795, 2));
        assert_eq!([out.reader_close, out.writer_close], errors);
        assert_eq!(
            out.error,
            if errors[0] != 0 { errors[0] } else { errors[1] }
        );
        clean();
    }
}
#[test]
fn malformed_old_wire_rights_identity_clock_and_factory_reject_without_effects() {
    for rights in [1, 2, 3, 4, 8] {
        reset(0, &[namespace(7, b'p', None), message(READER, 4)]);
        let (code, out) = invoke(rights, 1000, 1000);
        assert_eq!((code, out.stop, count(2)), (0, 0, 0));
        clean();
    }
    for magic in [b"AFSRPC01", b"AFSRPC02"] {
        let mut raw = namespace(7, b'p', None);
        raw[..8].copy_from_slice(magic);
        reset(0, &[raw, message(READER, 4)]);
        assert_eq!(invoke(15, 1000, 1000).0, 0);
        assert_eq!(count(2), 0);
        clean();
    }
    for mode in [9, 11, 12] {
        reset(mode, &[namespace(7, b'p', None), message(READER, 4)]);
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(count(2), 0);
        assert_eq!(out.state, 0);
        clean();
    }
    for (uid, gid) in [(1u64 << 31, 1000), (1000, 1u64 << 31)] {
        reset(0, &[]);
        assert_ne!(invoke(15, uid, gid).0, 0);
        assert_eq!(count(0), 0);
        STATE.with(|s| assert!(s.borrow().closed.is_empty()));
    }
}
#[test]
fn direct_owner_refreshes_every_root_alias_and_keeps_file_aliases_across_rename() {
    use filesystem_bridge::policy::{Identity, Mutation};
    reset(0, &[]);
    let mut marker = 0u64;
    // SAFETY: exclusive marker SPA and synchronous fixture provider.
    let mut spa = unsafe { Spa::from_raw(NonNull::new((&mut marker as *mut u64).cast()).unwrap()) };
    let provider = spa.open(c"testpool_zstd/x86_64").unwrap();
    let mut owner = Owner::new(provider, RuntimeUtc, 1)
        .unwrap()
        .with_namespace_identity(Identity::new(1000, 1000).unwrap());
    let a = owner.attach(7, Rights::new(15).unwrap()).unwrap();
    let b = owner.attach(8, Rights::new(15).unwrap()).unwrap();
    owner
        .namespace(7, a.session, a.root.handle, Mutation::Create(b"p"))
        .unwrap();
    assert_eq!(owner.stat(8, b.session, b.root.handle).unwrap().size, 2);
    let fresh = owner.attach(9, Rights::new(1).unwrap()).unwrap();
    assert_eq!(fresh.root.size, 2);
    let file = owner
        .lookup(7, a.session, a.root.handle, b"p", Rights::new(6).unwrap())
        .unwrap();
    let alias = owner
        .lookup(8, b.session, b.root.handle, b"p", Rights::new(2).unwrap())
        .unwrap();
    owner
        .write(7, a.session, file.handle, 0, &[11; 16])
        .unwrap();
    assert_eq!(owner.stat(8, b.session, alias.handle).unwrap().size, 16);
    owner
        .namespace(7, a.session, a.root.handle, Mutation::Rename(b"p", b"q"))
        .unwrap();
    let mut out = [0; 4096];
    assert_eq!(
        owner
            .read(8, b.session, alias.handle, 0, 16, &mut out)
            .unwrap(),
        16
    );
    assert_eq!(out[..16], [11; 16]);
    assert!(out[16..].iter().all(|b| *b == 0));
    assert_eq!(
        owner.namespace(7, a.session, a.root.handle, Mutation::Remove(b"q")),
        Err(Error::Denied)
    );
    assert_eq!(
        owner.namespace(8, a.session, a.root.handle, Mutation::Remove(b"q")),
        Err(Error::Denied)
    );
    owner.close(7, a.session, file.handle).unwrap();
    owner.close(8, b.session, alias.handle).unwrap();
    owner
        .namespace(7, a.session, a.root.handle, Mutation::Remove(b"q"))
        .unwrap();
    assert_eq!(owner.stat(8, b.session, b.root.handle).unwrap().size, 1);
    let c = owner.attach(10, Rights::new(1).unwrap()).unwrap();
    assert_eq!(c.root.size, 1);
    assert_eq!(owner.mutation_attempts(), 4);
    owner.shutdown();
    assert_eq!((count(4), count(5)), (0, 0));
    assert_eq!(count(0), count(1));
}
#[test]
fn later_namespace_retirement_failure_stops_with_original_progress_and_no_replay() {
    reset(20, &workload(true));
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!(
        (code, out.stop, out.requests, out.txg, out.state),
        (5, 5, 5, 791, 2)
    );
    assert_eq!((count(2), count(3)), (4, 3));
    clean();
}
#[test]
fn sixty_four_denied_frames_hit_original_request_ceiling_without_dispatch() {
    let mut bad = namespace(7, b'p', None);
    bad[48] = b'/';
    reset(0, &vec![bad; 64]);
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop, out.requests, count(2)), (5, 3, 64, 0));
    clean();
}

#[cfg(fs_wait)]
#[test]
fn waiting_mixed_entry_keeps_offsets_after_short_progress_and_spurious_hints() {
    reset(0, &workload(true));
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        s.backpressure = true;
        s.stalls = [true; 2];
        s.spurious = 3;
    });
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!(
        (code, out.stop, out.txg, out.bytes_staged, out.state),
        (0, 0, 795, 16, 2),
        "WAIT_MIXED_RESULT"
    );
    STATE.with(|s| {
        let s = s.borrow();
        assert!(s.waits.iter().all(|n| *n > 100), "WAIT_BOTH_DIRECTIONS");
    });
    let r = replies();
    assert_eq!(r[20][48..], data(5, 4, 0, 71)[48..], "WAIT_OFFSET");
    assert_eq!((count(2), count(3)), (8, 8));
    clean();
}
#[cfg(fs_wait)]
#[test]
fn wait_failure_before_request_or_after_commit_preserves_original_outcome_and_closes() {
    for error in [-9, -13, -32, -38, -110, 7] {
        for writing in [false, true] {
            reset(0, &workload(true));
            STATE.with(|s| {
                let mut s = s.borrow_mut();
                s.backpressure = true;
                s.stalls = [true; 2];
                s.wait_error = Some((writing, 64, error));
            });
            let (code, out) = invoke(15, 1000, 1000);
            assert_eq!(
                (code, out.stop, out.error),
                (
                    5,
                    if writing { 2 } else { 1 },
                    if error < 0 { error } else { -5 }
                ),
                "WAIT_ERROR"
            );
            assert_eq!(
                (out.requests, count(2), out.txg, out.state),
                if writing {
                    (1, 1, 788, 2)
                } else {
                    (0, 0, 0, 0)
                },
                "WAIT_NO_REPLAY"
            );
            clean();
        }
    }
}
#[cfg(fs_wait)]
#[test]
fn waiting_frame_erases_partial_input_on_error_and_bounds_spurious_hints() {
    use filesystem_service::{
        channel::{Framed, Io, POLLS},
        Channel,
    };
    struct Probe {
        progress: bool,
        waits: usize,
        status: i64,
    }
    impl Io for Probe {
        fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
            assert!(!writing);
            if self.progress {
                self.progress = false;
                bytes[..7].fill(0xa5);
                7
            } else {
                -11
            }
        }
        fn wait(&mut self, writing: bool) -> i64 {
            assert!(!writing);
            self.waits += 1;
            self.status
        }
        fn close(&mut self) -> [i64; 2] {
            [0, 0]
        }
    }
    for (status, error, expected) in [(-13, -13, 1), (9, -5, 1), (0, -110, POLLS - 1)] {
        let mut framed = Framed(Probe {
            progress: true,
            waits: 0,
            status,
        });
        let mut bytes = [0x99; 64];
        assert_eq!(framed.receive(&mut bytes), Err(error), "WAIT_TERMINAL");
        assert_eq!(bytes, [0; 64], "WAIT_CLEAR");
        assert_eq!(framed.0.waits, expected, "WAIT_BUDGET");
    }
}

#[path = "created-identity-tests.rs"]
mod created_identity;
