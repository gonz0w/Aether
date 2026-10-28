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
    #[cfg(fs_metadata)]
    fn metadata_retired_expected() -> u32;
    #[cfg(fs_metadata)]
    fn metadata_reset(mode: u32);
}
fn count(index: u32) -> u32 {
    // SAFETY: fixed valid scalar fixture index, serial host tests.
    unsafe { mixed_count(index) }
}
#[derive(Default)]
struct State {
    #[cfg(fs_activation)]
    publications: usize,
    #[cfg(fs_activation)]
    publication_status: i64,
    #[cfg(fs_activation)]
    bad_activation: bool,
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
        #[cfg(fs_activation)]
        if op == 0x24001 || op == 0x24002 {
            s.bad_activation |= s.publications != 1 || s.publication_status != 0;
        }
        match op {
            #[cfg(fs_activation)]
            0x20004 => {
                s.bad_activation |= (endpoint, pointer, length) != (0, 0, 0)
                    || !s.output.is_empty()
                    || s.read_transferred != 0
                    || count(0) != 1
                    || count(5) != 1
                    || count(2) != 0;
                s.publications += 1;
                s.publication_status
            }
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
                #[cfg(fs_metadata)]
                // SAFETY: serial host-only scalar fixture query; no retain.
                if unsafe { metadata_retired_expected() } != 0 {
                    s.bad_lifetime |= count(5) != 0;
                }
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
#[cfg(fs_names)]
fn named(op: u64, first: &[u8], second: &[u8]) -> Command {
    let mut c = request(op, 1);
    put(&mut c.header, 4, if op == 1 { 6 } else { 0 });
    put(
        &mut c.header,
        5,
        first.len() as u64 | ((second.len() as u64) << 32),
    );
    c.data.extend(first);
    c.data.extend(second);
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
    #[cfg(fs_metadata)]
    // SAFETY: serial host fixture; previous call returned with no live context.
    unsafe {
        metadata_reset(0)
    };
    // SAFETY: serial host tests; previous native entry consumed its context.
    unsafe { mixed_reset(mode) };
    let mut bytes = VecDeque::new();
    for c in commands {
        bytes.extend(c.header);
        if word(&c.header, 1) == 5 || (cfg!(fs_names) && matches!(word(&c.header, 1), 1 | 7..=11)) {
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
        assert_eq!(&ready[..8], filesystem_service::MAGIC);
        let mut offset = 64;
        let mut result = Vec::new();
        for c in commands {
            if offset == bytes.len() {
                break;
            }
            assert!(offset + 64 <= bytes.len());
            let header: Message = bytes[offset..offset + 64].try_into().unwrap();
            offset += 64;
            assert_eq!(&header[..8], filesystem_service::MAGIC);
            assert_eq!(word(&header, 2), READER);
            let mut data = Vec::new();
            if (word(&c.header, 1) == 2 || (cfg!(fs_metadata) && word(&c.header, 1) == 12))
                && word(&header, 1) == 0
            {
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
        #[cfg(fs_activation)]
        assert!(!s.bad_activation, "ACTIVATION_ENTRY_ORDER");
    });
}
fn at(op: u64, token: u64, name: &[u8], second: &[u8], rights: u64) -> Command {
    let mut c = named(op, name, second);
    put(&mut c.header, 3, token);
    put(&mut c.header, 4, rights);
    c
}
fn directory_commands() -> Vec<Command> {
    let digest = [b'a'; 64];
    let mut renamed = digest;
    renamed[63] = b'b';
    vec![
        at(10, 1, b"files", b"", 0),
        request(6, 1),
        at(1, 1, b"files", b"", 15),
        request(6, 2),
        at(10, 1, b"state", b"", 0),
        at(1, 1, b"state", b"", 15),
        at(10, 3, b"packages", b"", 0),
        at(1, 3, b"packages", b"", 15),
        at(7, 2, &digest, b"", 0),
        request(6, 2),
        at(1, 2, &digest, b"", 6),
        data(5, 5, 0, 4096, 71),
        data(2, 5, 0, 4096, 71),
        at(8, 2, &digest, &renamed, 0),
        request(6, 2),
        at(11, 1, b"files", b"", 0).denied(-13),
        at(9, 2, &renamed, b"", 0).denied(-13),
        request(3, 5),
        at(9, 2, &renamed, b"", 0),
        request(6, 2),
        request(3, 2),
        at(11, 1, b"files", b"", 0),
        request(3, 4),
        at(11, 3, b"packages", b"", 0),
        request(6, 3),
        request(6, 1),
        request(3, 3),
    ]
}
#[test]
fn full_nine_mutation_hierarchy_96_requests_preserves_parent_alias_sizes_and_data() {
    let mut c = directory_commands();
    while c.len() < 95 {
        c.push(request(6, 1));
    }
    c.push(request(4, 0));
    reset(0, &c);
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        s.backpressure = true;
        s.spurious = 3;
    });
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop, out.requests, out.ready), (0, 0, 96, 1));
    assert_eq!((count(2), count(3)), (9, 9));
    let rows = decoded(&c);
    assert_eq!(rows.len(), 96);
    for (command, (header, _)) in c.iter().zip(&rows) {
        assert_eq!(word(header, 1) as i64, command.expected);
    }
    for (i, size) in [(1, 3), (3, 2), (9, 3), (14, 3), (19, 2), (24, 2), (25, 3)] {
        assert_eq!(
            word(&rows[i].0, 5),
            size,
            "DIRECTORY_PARENT_ALIAS index={i}"
        );
        assert_eq!(word(&rows[i].0, 4), 1);
    }
    assert_eq!(rows[12].1, pattern(4096, 71));
    assert_eq!(out.txg, 796);
    assert_eq!(out.bytes_staged, 0);
    assert_eq!(out.state, 2);
    clean();
}
#[test]
fn directory_rights_and_root_scope_are_never_widened() {
    for rights in [1, 3, 7] {
        let c = [at(10, 1, b"files", b"", 0).denied(-13), request(4, 0)];
        reset(0, &c);
        assert_eq!(invoke(rights, 1000, 1000).0, 0);
        assert_eq!(word(&decoded(&c)[0].0, 1) as i64, -13);
        assert_eq!(count(2), 0);
        clean();
    }
    let c = [
        at(10, 1, b"files", b"", 0),
        at(1, 1, b"files", b"", 3),
        at(10, 2, b"nested", b"", 0).denied(-13),
        at(1, 2, b"missing", b"", 15).denied(-13),
        request(4, 0),
    ];
    reset(0, &c);
    assert_eq!(invoke(15, 1000, 1000).0, 0);
    let r = decoded(&c);
    assert_eq!(word(&r[2].0, 1) as i64, -13);
    assert_eq!(word(&r[3].0, 1) as i64, -13);
    assert_eq!(count(2), 1);
    clean();
}
#[test]
fn rmdir_live_aliases_deny_then_empty_removal_and_stale_tokens_stay_dead() {
    let c = [
        at(10, 1, b"files", b"", 0),
        at(1, 1, b"files", b"", 15),
        at(1, 1, b"files", b"", 1),
        at(11, 1, b"files", b"", 0).denied(-13),
        request(3, 2),
        at(11, 1, b"files", b"", 0).denied(-13),
        request(3, 3),
        at(11, 1, b"files", b"", 0),
        at(10, 2, b"stale", b"", 0).denied(-9),
        request(4, 0),
    ];
    reset(0, &c);
    assert_eq!(invoke(15, 1000, 1000).0, 0);
    for (a, b) in c.iter().zip(decoded(&c)) {
        assert_eq!(word(&b.0, 1) as i64, a.expected);
    }
    assert_eq!((count(2), count(3)), (2, 2));
    clean();
}
#[test]
fn nonempty_rmdir_retains_failure_and_never_dispatches_the_following_mutation() {
    let c = [
        at(10, 1, b"files", b"", 0),
        at(1, 1, b"files", b"", 15),
        at(7, 2, b"p", b"", 0),
        request(3, 2),
        at(11, 1, b"files", b"", 0),
        at(10, 1, b"no-retry", b"", 0),
    ];
    reset(0, &c);
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop, out.requests), (5, 5, 5));
    assert_eq!((count(2), count(3)), (2, 2)); // rejected before assignment
    let rows = decoded(&c);
    assert_eq!(word(&rows[4].0, 1) as i64, -39);
    clean();
}
#[test]
fn refresh_corruption_and_each_irreversible_failure_permanently_retire() {
    for mode in 1..=7 {
        let c = [at(10, 1, b"files", b"", 0), at(10, 1, b"no-retry", b"", 0)];
        reset(mode, &c);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.requests), (5, 5, 1), "mode={mode}");
        assert_eq!(count(2), 1);
        assert_eq!(decoded(&c).len(), 1);
        if mode == 4 {
            assert_eq!((out.txg, out.state), (0, 0));
        } else {
            assert_eq!(out.txg, 788);
            assert_ne!(out.state, 0);
        }
        assert_eq!(count(3), if mode <= 3 { 1 } else { 0 });
        clean();
    }
}
#[test]
fn all_mkdir_and_rmdir_name_body_prefixes_and_padding_fail_before_mutation() {
    for op in [10, 11] {
        let c = at(op, 1, &[b'x'; 255], b"", 0);
        for prefix in [0, 1, 16, 63, 64, 127, 128, 191, 192, 254, 255] {
            reset(0, core::slice::from_ref(&c));
            STATE.with(|s| s.borrow_mut().input.truncate(64 + prefix));
            let (code, out) = invoke(15, 1000, 1000);
            assert_eq!((code, out.stop, out.requests), (5, 1, 0));
            assert_eq!(count(2), 0);
            clean();
        }
        reset(0, &[c]);
        STATE.with(|s| *s.borrow_mut().input.back_mut().unwrap() = 1);
        assert_eq!(invoke(15, 1000, 1000).0, 5);
        assert_eq!(count(2), 0);
        clean();
    }
}
#[test]
fn lexical_names_and_old_wire_versions_never_gain_directory_authority() {
    for op in [10, 11] {
        for name in [&b"."[..], b"..", b"a/b", b"a\0b"] {
            let c = [at(op, 1, name, b"", 0).denied(-22), request(4, 0)];
            reset(0, &c);
            assert_eq!(invoke(15, 1000, 1000).0, 0);
            assert_eq!(word(&decoded(&c)[0].0, 1) as i64, -22);
            assert_eq!(count(2), 0);
            clean();
        }
        let mut c = at(op, 1, b"files", b"", 0);
        c.header[48] = 1;
        reset(0, &[c]);
        assert_eq!(invoke(15, 1000, 1000).0, 5);
        assert_eq!(count(2), 0);
        clean();
        for version in b'1'..=b'5' {
            let mut c = at(op, 1, b"files", b"", 0);
            c.header[7] = version;
            reset(0, &[c]);
            let (code, out) = invoke(15, 1000, 1000);
            assert_eq!((code, out.stop, out.requests), (5, 1, 0));
            assert_eq!(count(2), 0);
            clean();
        }
    }
}
#[test]
fn every_mkdir_reply_loss_keeps_one_transaction_without_replay() {
    for prefix in 0..64 {
        let c = [at(10, 1, b"files", b"", 0), at(10, 1, b"no-retry", b"", 0)];
        reset(0, &c);
        STATE.with(|s| s.borrow_mut().fail_after = Some(64 + prefix));
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.requests), (5, 2, 1));
        assert_eq!((count(2), count(3)), (1, 1));
        assert_eq!((out.txg, out.state), (788, 2));
        clean();
    }
}
#[test]
fn both_endpoint_close_failures_keep_real_service_failure() {
    for errors in [[-13, 0], [0, -13], [-13, -13]] {
        let c = [request(4, 0)];
        reset(0, &c);
        STATE.with(|s| s.borrow_mut().close_errors = errors);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop, out.error), (5, 0, -13));
        assert_eq!([out.reader_close, out.writer_close], errors);
        clean();
    }
}

#[test]
fn wait_failure_with_partial_directory_body_keeps_no_effect_and_exact_cleanup() {
    let c = [at(10, 1, &[b'x'; 255], b"", 0)];
    reset(0, &c);
    STATE.with(|s| {
        let mut s = s.borrow_mut();
        s.backpressure = true;
        s.wait_read_after = Some((80, -5));
    });
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop, out.requests), (5, 1, 0));
    assert_eq!(out.error, -5);
    assert_eq!(count(2), 0);
    clean();
}
#[test]
fn every_data_length_uses_checked_retirement_within_a_directory() {
    for length in [1, 16, 17, 63, 64, 65, 255, 4095, 4096] {
        let c = [
            at(10, 1, b"files", b"", 0),
            at(1, 1, b"files", b"", 15),
            at(7, 2, b"p", b"", 0),
            at(1, 2, b"p", b"", 6),
            data(5, 3, 0, length, 71),
            data(2, 3, 0, length, 71),
            request(4, 0),
        ];
        reset(0, &c);
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!((code, out.stop), (0, 0));
        assert_eq!(out.bytes_staged, length as u64);
        assert_eq!(decoded(&c)[5].1, pattern(length, 71));
        assert_eq!(count(3), 3);
        clean();
    }
}
#[test]
fn host_only_checked_counters_cross_old_caps_without_growing_the_live_table() {
    // Host stress only. The selected native experiment still uses exactly9/96.
    let mut c = Vec::new();
    for _ in 0..129 {
        c.push(at(10, 1, b"reuse", b"", 0));
        c.push(at(11, 1, b"reuse", b"", 0));
    }
    c.push(request(4, 0));
    reset(0, &c);
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop, out.requests), (0, 0, 259));
    assert_eq!((count(2), count(3)), (258, 258));
    clean();
}
#[test]
fn newly_attached_root_and_all_directory_aliases_observe_the_correct_parent() {
    use filesystem_bridge::{
        policy,
        policy::{Identity, Mutation},
        RuntimeUtc, Spa,
    };
    reset(0, &[]);
    let mut marker = 0u64;
    // SAFETY: exclusive typed host fixture SPA, serialized lifetimes, immutable
    // dataset and no export/mutation until the owner consumes its only context.
    let mut spa = unsafe { Spa::from_raw(NonNull::from(&mut marker).cast()) };
    let mut owner = Owner::new(spa.open(c"testpool_zstd/x86_64").unwrap(), RuntimeUtc, 7)
        .unwrap()
        .with_namespace_identity(Identity::new(1000, 1000).unwrap());
    let a = owner.attach(8, Rights::ALL).unwrap();
    assert_eq!(
        owner.namespace(
            99,
            a.session,
            a.root.handle,
            Mutation::MakeDirectory(b"foreign")
        ),
        Err(Error::Denied)
    );
    owner
        .namespace(
            8,
            a.session,
            a.root.handle,
            Mutation::MakeDirectory(b"files"),
        )
        .unwrap();
    let b = owner.attach(9, Rights::ALL).unwrap();
    assert_eq!(b.root.size, 3, "DIRECTORY_ROOT_CACHE");
    let x = owner
        .lookup(8, a.session, a.root.handle, b"files", Rights::ALL)
        .unwrap();
    let y = owner
        .lookup(
            9,
            b.session,
            b.root.handle,
            b"files",
            Rights::new(1).unwrap(),
        )
        .unwrap();
    owner
        .namespace(8, a.session, x.handle, Mutation::MakeDirectory(b"nested"))
        .unwrap();
    assert_eq!(owner.stat(9, b.session, y.handle).unwrap().size, 3);
    assert_eq!(owner.stat(8, a.session, a.root.handle).unwrap().size, 3);
    assert_eq!(
        owner.namespace(9, b.session, y.handle, Mutation::MakeDirectory(b"denied")),
        Err(Error::Denied)
    );
    owner.shutdown();
    assert_eq!(owner.attach(8, Rights::ALL), Err(policy::Error::Closed));
    assert_eq!(
        (count(0), count(1), count(2), count(3), count(5)),
        (3, 3, 2, 2, 0)
    );
}
#[cfg(runtime_request_probe)]
#[test]
fn request_counter_exhaustion_closes_before_next_provider_effect() {
    let c = [request(6, 1), request(6, 1), request(4, 0)];
    reset(0, &c);
    let (code, out) = invoke(15, 1000, 1000);
    assert_eq!((code, out.stop), (5, 3), "RUNTIME_REQUEST_OVERFLOW");
    assert_eq!(count(2), 0);
    clean();
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

#[cfg(fs_activation)]
#[test]
fn activation_publication_failure_consumes_without_greeting_or_requests() {
    for status in [-13, -9, 1] {
        reset(0, &[at(10, 1, b"files", b"", 0)]);
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            s.publication_status = status;
            s.close_errors = [-13, -32];
        });
        let (code, out) = invoke(15, 1000, 1000);
        assert_eq!(
            (code, out.ready, out.requests, out.stop, out.error),
            (5, 0, 0, 2, if status < 0 { status } else { -5 }),
            "ACTIVATION_ENTRY_FAILURE"
        );
        assert_eq!([out.reader_close, out.writer_close], [-13, -32]);
        assert_eq!(count(2), 0);
        STATE.with(|s| {
            let s = s.borrow();
            assert_eq!(s.publications, 1);
            assert!(s.output.is_empty());
            assert_eq!(s.read_transferred, 0);
        });
        clean();
    }
}

#[cfg(fs_metadata)]
#[path = "metadata-service-tests.rs"]
mod metadata_tests;

#[path = "created-identity-tests.rs"]
mod created_identity;
