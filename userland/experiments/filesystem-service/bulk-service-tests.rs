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
    read_transferred: usize,
    wait_read_after: Option<(usize, i64)>,
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
                s.read_transferred += n;
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
                if !writing {
                    if let Some((after, error)) = s.wait_read_after {
                        if s.read_transferred >= after {
                            return error;
                        }
                    }
                }
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

#[derive(Clone)]
struct Command {
    header: Message,
    data: Vec<u8>,
    expected: i64,
}
impl Command {
    fn denied(mut self, error: i64) -> Self {
        self.expected = error;
        self
    }
}
fn request(op: u64, token: u64) -> Command {
    let mut header = message(READER, op);
    put(&mut header, 3, token);
    Command {
        header,
        data: Vec::new(),
        expected: 0,
    }
}
fn namespace(op: u64, from: u8, to: Option<u8>) -> Command {
    let mut c = request(op, 1);
    put(&mut c.header, 5, 1 | if to.is_some() { 1 << 32 } else { 0 });
    c.header[48] = from;
    if let Some(to) = to {
        c.header[49] = to;
    }
    c
}
fn lookup(name: u8, rights: u64) -> Command {
    let mut c = request(1, 1);
    put(&mut c.header, 4, rights);
    put(&mut c.header, 5, 1);
    c.header[48] = name;
    c
}
fn pattern(length: usize, seed: u8) -> Vec<u8> {
    (0..length).map(|i| seed.wrapping_add(i as u8)).collect()
}
fn data(op: u64, token: u64, offset: u64, length: usize, seed: u8) -> Command {
    let mut c = request(op, token);
    put(&mut c.header, 4, offset);
    put(&mut c.header, 5, length as u64);
    if op == 5 || seed != 0 {
        c.data = pattern(length, seed);
    }
    c
}
fn reset(mode: u32, commands: &[Command]) {
    // SAFETY: serial host tests; previous native entry consumed its context.
    unsafe { mixed_reset(mode) };
    let mut bytes = VecDeque::new();
    for c in commands {
        bytes.extend(c.header);
        if word(&c.header, 1) == 5 {
            for chunk in c.data.chunks(64) {
                let mut frame = [0; 64];
                frame[..chunk.len()].copy_from_slice(chunk);
                bytes.extend(frame);
            }
        }
    }
    STATE.with(|s| {
        *s.borrow_mut() = State {
            input: bytes,
            ..State::default()
        }
    });
}
fn decoded(commands: &[Command]) -> Vec<(Message, Vec<u8>)> {
    STATE.with(|s| {
        let s = s.borrow();
        let bytes = &s.output;
        assert!(bytes.len() >= 64);
        let ready: Message = bytes[..64].try_into().unwrap();
        assert_eq!(&ready[..8], b"AFSRPC04");
        let mut offset = 64;
        let mut result = Vec::new();
        for c in commands {
            if offset == bytes.len() {
                break;
            }
            assert!(offset + 64 <= bytes.len());
            let header: Message = bytes[offset..offset + 64].try_into().unwrap();
            offset += 64;
            assert_eq!(&header[..8], b"AFSRPC04");
            assert_eq!(word(&header, 2), READER);
            let mut data = Vec::new();
            if word(&c.header, 1) == 2 && word(&header, 1) == 0 {
                assert_eq!(
                    word(&header, 3) | word(&header, 4) | word(&header, 6) | word(&header, 7),
                    0,
                    "BULK_READ_HEADER"
                );
                let count = word(&header, 5) as usize;
                assert!(count <= 4096, "BULK_READ_LENGTH");
                for at in (0..count).step_by(64) {
                    assert!(offset + 64 <= bytes.len());
                    let n = (count - at).min(64);
                    data.extend(&bytes[offset..offset + n]);
                    assert!(
                        bytes[offset + n..offset + 64].iter().all(|b| *b == 0),
                        "BULK_PADDING"
                    );
                    offset += 64;
                }
            }
            result.push((header, data));
        }
        assert_eq!(offset, bytes.len(), "BULK_NO_EXTRA_BODY");
        result
    })
}
fn workload(disconnect: bool) -> Vec<Command> {
    let mut c = vec![
        namespace(7, b'p', None),
        request(6, 1),
        lookup(b'p', 6),
        data(5, 2, 0, 4096, 11),
        data(5, 2, 4096, 4096, 31),
        namespace(8, b'p', Some(b'q')),
        request(6, 1),
        request(6, 2),
        data(2, 2, 0, 4096, 11),
        data(5, 2, 8192, 4096, 51),
        namespace(9, b'q', None).denied(-13),
        lookup(b'q', 2),
        request(3, 2),
        namespace(9, b'q', None).denied(-13),
        request(3, 3),
        namespace(9, b'q', None),
        request(6, 1),
        namespace(7, b'p', None),
        request(6, 1),
        data(2, 2, 0, 4096, 0).denied(-9),
        lookup(b'p', 6),
        data(5, 4, 0, 4096, 71),
        request(6, 4),
        data(2, 4, 0, 4096, 71),
        data(2, 4, 4096, 4096, 0),
        namespace(7, b'r', None).denied(-28),
        data(5, 4, 0, 4096, 91).denied(-28),
        request(3, 4),
    ];
    if disconnect {
        c.push(request(4, 0));
    }
    c
}
fn simple(length: usize) -> Vec<Command> {
    vec![
        namespace(7, b'p', None),
        lookup(b'p', 6),
        data(5, 2, 0, length, 71),
        data(2, 2, 0, length, 71),
        data(2, 2, length as u64, 1, 0),
        request(4, 0),
    ]
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
fn bulk_eight_attempts_full_bodies_root_aliases_rename_sizes_eof_and_no_ninth() {
    let commands = workload(true);
    reset(0, &commands);
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!(
        (code, out.stop, out.requests),
        (0, 0, commands.len() as u64),
        "BULK_SEQUENCE"
    );
    assert_eq!((out.txg, out.bytes_staged, out.state), (795, 4096, 2));
    assert_eq!((count(2), count(3), count(6), count(7)), (8, 8, 4, 4));
    let replies = decoded(&commands);
    assert_eq!(replies.len(), commands.len());
    let mut present = false;
    for (command, (reply, bytes)) in commands.iter().zip(replies) {
        assert_eq!(word(&reply, 1) as i64, command.expected, "BULK_AUTHORITY");
        let op = word(&command.header, 1);
        if command.expected == 0 {
            if op == 7 {
                present = true;
            }
            if op == 9 {
                present = false;
            }
            if op == 6 && word(&command.header, 3) == 1 {
                assert_eq!(
                    word(&reply, 5),
                    if present { 2 } else { 1 },
                    "BULK_ROOT_CACHE"
                );
            }
            if op == 6 && word(&command.header, 3) != 1 {
                assert_eq!(
                    word(&reply, 5),
                    if word(&command.header, 3) == 2 {
                        8192
                    } else {
                        4096
                    }
                );
            }
            if op == 2 {
                assert_eq!(bytes, command.data, "BULK_CONTENT");
            }
        }
    }
    assert_eq!(count(9), 4096);
    clean();
}
#[test]
fn all_boundary_lengths_bind_retirement_and_padding_to_the_actual_request() {
    for length in [1, 63, 64, 65, 4095, 4096] {
        let commands = simple(length);
        reset(0, &commands);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (code, out.stop, out.bytes_staged, out.state),
            (0, 0, length as u64, 2),
            "BULK_LENGTH_RETIRE"
        );
        assert_eq!(count(9), length as u32);
        let replies = decoded(&commands);
        assert_eq!(replies[3].1, pattern(length, 71));
        assert!(replies[4].1.is_empty());
        clean();
    }
}
fn boundaries() -> Vec<usize> {
    let mut b: Vec<_> = (0..4096).step_by(64).collect();
    b.extend([1, 15, 16, 63, 65, 4095]);
    b.sort_unstable();
    b.dedup();
    b
}
#[test]
fn every_body_frame_boundary_and_short_prefix_prevents_write_dispatch() {
    for prefix in boundaries() {
        reset(0, &[namespace(7, b'p', None), lookup(b'p', 6)]);
        let write = data(5, 2, 0, 4096, 71);
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            s.input.extend(write.header);
            s.input.extend(&write.data[..prefix]);
        });
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (code, out.stop, out.requests, count(2)),
            (5, 1, 2, 1),
            "BULK_PARTIAL_NO_DISPATCH"
        );
        assert_eq!((out.txg, out.bytes_staged, out.state), (788, 0, 2));
        clean();
    }
}
#[test]
fn malformed_data_headers_and_unknown_opcodes_never_reinterpret_a_tail() {
    for variant in 0..7 {
        reset(0, &[namespace(7, b'p', None), lookup(b'p', 6)]);
        let mut bad = data(5, 2, 0, 4096, 71).header;
        match variant {
            0 => put(&mut bad, 5, 4097),
            1 => put(&mut bad, 5, 0),
            2 => put(&mut bad, 4, u64::MAX),
            3 => bad[48] = 1,
            4 => bad[7] = b'3',
            5 => put(&mut bad, 2, READER + 1),
            _ => put(&mut bad, 1, 99),
        };
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            s.input.extend(bad);
            s.input.extend(namespace(8, b'p', Some(b'q')).header);
            s.input.extend(request(4, 0).header);
        });
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (code, out.stop, out.requests, count(2)),
            (5, 1, 2, 1),
            "BULK_HEADER_NO_EFFECT"
        );
        assert_eq!(out.error, if variant == 5 { -9 } else { -22 });
        clean();
    }
}
#[test]
fn nonzero_last_frame_padding_is_not_dispatched() {
    for length in [1, 63, 65, 4095] {
        let commands = simple(length);
        reset(0, &commands);
        STATE.with(|s| s.borrow_mut().input[3 * 64 + length] = 0xa5);
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.error, out.requests, count(2)),
            (1, -22, 2, 1),
            "BULK_PADDING_NO_EFFECT"
        );
        clean();
    }
}
#[test]
fn every_first_mutation_reply_prefix_preserves_the_original_commit_without_replay() {
    for prefix in 0..64 {
        reset(
            0,
            &[namespace(7, b'p', None), namespace(8, b'p', Some(b'q'))],
        );
        STATE.with(|s| s.borrow_mut().fail_after = Some(64 + prefix));
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.requests, out.txg, out.state, count(2)),
            (2, 1, 788, 2, 1),
            "BULK_REPLY_NO_REPLAY"
        );
        clean();
    }
}
#[test]
fn read_body_reply_loss_retains_prior_write_and_never_dispatches_the_next_request() {
    for prefix in boundaries() {
        let commands = vec![
            namespace(7, b'p', None),
            lookup(b'p', 6),
            data(5, 2, 0, 4096, 71),
            data(2, 2, 0, 4096, 71),
            data(5, 2, 4096, 4096, 91),
        ];
        reset(0, &commands);
        STATE.with(|s| s.borrow_mut().fail_after = Some(320 + prefix));
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (
                out.stop,
                out.requests,
                out.txg,
                out.bytes_staged,
                out.state,
                count(2)
            ),
            (2, 4, 789, 4096, 2, 2),
            "BULK_LOST_BODY_NO_REPLAY"
        );
        clean();
    }
}
#[test]
fn actual_entry_waits_both_directions_preserve_every_byte_after_spurious_hints() {
    let commands = simple(4096);
    reset(0, &commands);
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        s.backpressure = true;
        s.stalls = [true; 2];
        s.spurious = 3;
    });
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop), (0, 0), "BULK_WAIT_SEQUENCE");
    STATE.with(|s| assert!(s.borrow().waits.iter().all(|n| *n > 500), "BULK_WAIT_BOTH"));
    assert_eq!(
        decoded(&commands)[3].1,
        pattern(4096, 71),
        "BULK_WAIT_OFFSET"
    );
    clean();
}
#[test]
fn wait_failures_in_a_partial_body_and_after_commit_keep_exact_error_and_cleanup() {
    for error in [-9, -13, -32, -38, -110, 7] {
        reset(0, &simple(4096));
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            s.backpressure = true;
            s.stalls = [true; 2];
            s.wait_read_after = Some((320, error));
        });
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.error, out.requests, count(2)),
            (1, if error < 0 { error } else { -5 }, 2, 1),
            "BULK_BODY_WAIT_ERROR"
        );
        clean();
        reset(0, &simple(4096));
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            s.backpressure = true;
            s.stalls = [true; 2];
            s.wait_error = Some((true, 64, error));
        });
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.error, out.txg, out.state, count(2)),
            (2, if error < 0 { error } else { -5 }, 788, 2, 1),
            "BULK_COMMIT_WAIT_ERROR"
        );
        clean();
    }
}
#[test]
fn original_failed_namespace_write_and_later_retirement_progress_survive() {
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
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (out.stop, out.requests, out.txg, out.state, count(2)),
            (5, 1, txg, state, 1),
            "BULK_NAMESPACE_PROGRESS"
        );
        clean();
    }
    for (mode, txg, bytes, state) in [
        (16, 789, 4096, 2),
        (17, 0, 0, 0),
        (18, 0, 4096, 1),
        (19, 789, 4096, 2),
    ] {
        reset(mode, &simple(4096));
        let (_, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (
                out.stop,
                out.requests,
                out.txg,
                out.bytes_staged,
                out.state,
                count(2)
            ),
            (5, 3, txg, bytes, state, 2),
            "BULK_ORIGINAL_PROGRESS"
        );
        clean();
    }
    reset(20, &workload(true));
    let (_, out) = invoke(15, 1000, 1000);
    assert_eq!(
        (out.stop, out.txg, out.state, count(2), count(3)),
        (5, 791, 2, 4, 3)
    );
    clean();
}
#[test]
fn both_endpoint_close_outcomes_follow_consumed_provider() {
    for errors in [[-13, 0], [0, -32], [-13, -32]] {
        reset(0, &simple(4096));
        STATE.with(|s| s.borrow_mut().close_errors = errors);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.txg, out.state), (5, 0, 789, 2));
        assert_eq!([out.reader_close, out.writer_close], errors);
        assert_eq!(
            out.error,
            if errors[0] != 0 { errors[0] } else { errors[1] }
        );
        clean();
    }
}
#[test]
fn namespace_rights_identity_clock_factory_and_all_old_wire_versions_are_denied() {
    for rights in [1, 2, 3, 4, 8] {
        reset(0, &[namespace(7, b'p', None), request(4, 0)]);
        let (_, out) = invoke(rights, 1000, 1000);
        assert_eq!((out.stop, count(2)), (0, 0));
        clean();
    }
    for magic in [b"AFSRPC01", b"AFSRPC02", b"AFSRPC03"] {
        let mut c = namespace(7, b'p', None);
        c.header[..8].copy_from_slice(magic);
        reset(0, &[c, request(4, 0)]);
        assert_eq!(invoke(15, 1000, 1000).0, 0);
        assert_eq!(count(2), 0);
        clean();
    }
    for mode in [9, 11, 12] {
        reset(mode, &simple(4096));
        let _ = invoke(15, 1000, 1000);
        assert_eq!(count(2), 0);
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
fn sixty_four_complete_denials_reach_the_request_cap_without_provider_effects() {
    let mut bad = namespace(7, b'p', None);
    bad.header[48] = b'/';
    reset(0, &vec![bad; 64]);
    let (_, out) = invoke(15, 1000, 1000);
    assert_eq!(
        (out.stop, out.error, out.requests, count(2)),
        (3, -28, 64, 0),
        "BULK_REQUEST_BUDGET"
    );
    clean();
}
#[test]
fn malformed_read_count_sends_no_body_and_never_exposes_previous_buffer_contents() {
    let commands = simple(4096);
    reset(23, &commands);
    let (code, out) = invoke(15, 1000, 1000);
    // Invalid provider completion keeps the established uncertainty state and
    // stops the stream; no EOF or disconnect command is consumed afterwards.
    assert_eq!((code, out.stop, out.requests), (5, 5, 4));
    let result = decoded(&commands);
    assert_eq!(result.len(), 4);
    assert_eq!(word(&result[3].0, 1) as i64, -5);
    assert_eq!(word(&result[3].0, 6), 3);
    assert!(result[3].1.is_empty());
    assert!(result[3].0[24..48].iter().all(|b| *b == 0));
    assert!(result[3].0[56..].iter().all(|b| *b == 0));
    clean();
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
