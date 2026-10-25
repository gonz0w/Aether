// SPDX-License-Identifier: BSD-2-Clause
//! Host transcript driver for the actual native directory controller.
use std::{cell::RefCell, collections::VecDeque};
struct Connection {
    request: u64,
    send: u64,
    receive: u64,
}
fn get(b: &[u8; 64], i: usize) -> u64 {
    u64::from_le_bytes(b[i * 8..i * 8 + 8].try_into().unwrap())
}
fn put(b: &mut [u8; 64], i: usize, v: u64) {
    b[i * 8..i * 8 + 8].copy_from_slice(&v.to_le_bytes());
}
fn check(ok: bool) {
    assert!(ok, "DIRECTORY_CLIENT_CHECK");
}
#[derive(Default)]
struct State {
    input: VecDeque<[u8; 64]>,
    output: Vec<[u8; 64]>,
    #[cfg(fs_partial_request)]
    prefix: Vec<u8>,
    closed: Vec<u64>,
    #[cfg(fs_partial_request)]
    stalled: bool,
}
std::thread_local! {static STATE:RefCell<State>=RefCell::new(State::default());}
#[cfg(any(fs_lost_reply, fs_partial_request))]
fn call(op: u64, a: u64, _: u64, _: u64, _: u64) -> (i64, u64) {
    assert_eq!(op, 0x24003);
    STATE.with(|s| s.borrow_mut().closed.push(a));
    (0, 0)
}
mod channel {
    use super::*;
    pub fn frame(endpoint: u64, bytes: &mut [u8; 64], writing: bool) -> Result<(), i64> {
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            if writing {
                assert_eq!(endpoint, 11);
                s.output.push(*bytes);
                Ok(())
            } else {
                assert_eq!(endpoint, 22);
                *bytes = s.input.pop_front().ok_or(-5)?;
                Ok(())
            }
        })
    }
    #[cfg(fs_partial_request)]
    pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64, _: u64) -> (i64, u64) {
        assert_eq!(endpoint, 11);
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            if op == 0x24004 {
                assert!(s.stalled);
                s.stalled = false;
                return (0, 0);
            }
            assert_eq!(op, 0x24002);
            if s.stalled {
                return (-11, 0);
            }
            assert_eq!(length as usize, 16 - s.prefix.len());
            let count = (length as usize).min(7);
            // SAFETY: actual controller retains this initialized exclusive prefix suffix.
            s.prefix.extend_from_slice(unsafe {
                core::slice::from_raw_parts(pointer as *const u8, count)
            });
            s.stalled = true;
            (count as i64, 0)
        })
    }
}
#[path = "CONTROLLER"]
mod client;
fn reply(status: i64) -> [u8; 64] {
    let mut h = [0; 64];
    h[..8].copy_from_slice(b"AFSRPC06");
    put(&mut h, 1, status as u64);
    put(&mut h, 2, 77);
    h
}
fn entry(token: u64, kind: u64, size: u64) -> [u8; 64] {
    let mut h = reply(0);
    put(&mut h, 3, token);
    put(&mut h, 4, kind);
    put(&mut h, 5, size);
    h
}
#[cfg(not(fs_partial_request))]
fn mutation(txg: u64, staged: u64) -> [u8; 64] {
    let mut h = reply(0);
    put(&mut h, 4, txg);
    put(&mut h, 5, staged);
    put(&mut h, 6, 2);
    h
}
fn setup() -> Connection {
    let mut s = State::default();
    s.input.push_back(entry(1, 1, 3));
    for error in [22, 22, 22, 9, 9] {
        s.input.push_back(reply(-error));
    }
    #[cfg(not(fs_partial_request))]
    {
        s.input.extend([
            mutation(788, 0),
            entry(2, 1, 2),
            mutation(789, 0),
            entry(3, 2, 0),
            mutation(790, 4096),
        ]);
        let mut h = reply(0);
        put(&mut h, 5, 4096);
        s.input.push_back(h);
        for offset in (0..4096).step_by(64) {
            let mut body = [0; 64];
            for (i, b) in body.iter_mut().enumerate() {
                *b = (71 + offset + i) as u8;
            }
            s.input.push_back(body);
        }
        s.input.extend([
            mutation(791, 0),
            entry(4, 2, 4096),
            reply(0),
            reply(0),
            mutation(792, 0),
            entry(5, 1, 2),
            mutation(793, 0),
            entry(6, 1, 2),
            reply(-13),
            reply(0),
            mutation(794, 0),
            mutation(795, 0),
            entry(7, 2, 0),
            reply(0),
            mutation(796, 0),
            entry(2, 1, 3),
            entry(5, 1, 2),
            entry(1, 1, 5),
            reply(0),
            reply(0),
        ]);
        for _ in 0..64 {
            s.input.push_back(entry(1, 1, 5));
        }
        s.input.push_back(reply(0));
    }
    #[cfg(fs_partial_request)]
    {
        let mut h = reply(0);
        put(&mut h, 4, 788);
        put(&mut h, 6, 2);
        s.input.extend([h, entry(2, 1, 2)]);
    }
    STATE.with(|state| *state.borrow_mut() = s);
    Connection {
        request: 77,
        send: 11,
        receive: 22,
    }
}
#[cfg(not(any(fs_lost_reply, fs_partial_request)))]
#[test]
fn complete_transcript_has_exact_96_requests_nine_effects_and_delegated_components() {
    setup().exercise();
    STATE.with(|s| {
        let s = s.borrow();
        assert!(s.input.is_empty());
        assert!(s.closed.is_empty());
        let mut frames = s.output.iter();
        let mut requests = Vec::new();
        while let Some(h) = frames.next() {
            assert_eq!(&h[..8], b"AFSRPC06");
            assert_eq!(get(h, 2), 77);
            assert!(h[48..].iter().all(|b| *b == 0));
            let op = get(h, 1);
            let count = if op == 5 {
                4096
            } else if matches!(op, 1 | 7..=11) {
                get(h, 5) as u32 as usize + (get(h, 5) >> 32) as usize
            } else {
                0
            };
            let mut body = Vec::new();
            for chunk in (0..count).step_by(64) {
                let f = frames.next().unwrap();
                let n = (count - chunk).min(64);
                body.extend_from_slice(&f[..n]);
                assert!(f[n..].iter().all(|b| *b == 0));
            }
            requests.push((op, get(h, 3), body));
        }
        assert_eq!(requests.len(), 96);
        assert_eq!(
            requests[..5].iter().map(|r| (r.0, r.1)).collect::<Vec<_>>(),
            [(10, 1), (10, 1), (10, 1), (10, 99), (10, 100)]
        );
        assert_eq!(
            requests[..5]
                .iter()
                .map(|r| r.2.as_slice())
                .collect::<Vec<_>>(),
            [
                &b"."[..],
                &b"/"[..],
                &b"\0"[..],
                &b"files"[..],
                &b"files"[..]
            ]
        );
        let effect_requests: Vec<_> = requests
            .iter()
            .skip(5)
            .filter(|r| matches!(r.0, 5 | 7..=11))
            .collect();
        assert_eq!(
            effect_requests
                .iter()
                .map(|r| (r.0, r.1))
                .collect::<Vec<_>>(),
            [
                (10, 1),
                (7, 2),
                (5, 3),
                (8, 2),
                (10, 1),
                (10, 5),
                (11, 5),
                (11, 5),
                (7, 5),
                (9, 5)
            ]
        );
        assert_eq!(effect_requests[0].2, b"files");
        assert_eq!(effect_requests[1].2.len(), 64);
        assert_eq!(
            &effect_requests[1].2,
            b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(
            effect_requests[2].2,
            (0..4096).map(|i| (71 + i) as u8).collect::<Vec<_>>()
        );
        assert_eq!(effect_requests[3].2.len(), 128);
        assert_eq!(effect_requests[3].2[..64], effect_requests[1].2);
        assert_eq!(effect_requests[3].2[127], b'6');
        assert_eq!(effect_requests[4].2, b"state");
        for r in &effect_requests[5..8] {
            assert_eq!(r.2, b"packages");
        }
        for r in &effect_requests[8..] {
            assert_eq!(r.2, b"stage");
        }
    });
}
#[cfg(not(any(fs_lost_reply, fs_partial_request)))]
#[test]
fn corrupted_reply_epoch_final_data_byte_or_parent_size_is_rejected() {
    for mode in 0..3 {
        let c = setup();
        STATE.with(|s| {
            let mut s = s.borrow_mut();
            match mode {
                0 => put(&mut s.input[1], 2, 78),
                1 => s.input[75][63] ^= 1,
                _ => put(&mut s.input[93], 5, 99),
            }
        });
        assert!(
            std::panic::catch_unwind(|| c.exercise()).is_err(),
            "DIRECTORY_CLIENT_CORRUPTION mode={mode}"
        );
    }
}
#[cfg(fs_lost_reply)]
#[test]
fn lost_reply_closes_reader_and_sends_only_first_mkdir() {
    setup().exercise();
    STATE.with(|s| {
        let s = s.borrow();
        assert_eq!(s.closed, [22]);
        assert_eq!(s.output.len(), 12);
        assert_eq!(get(&s.output[10], 1), 10);
        assert_eq!(&s.output[11][..5], b"files");
    });
}
#[cfg(fs_partial_request)]
#[test]
fn partial_create_transfers_exact_initialized_sixteen_byte_prefix_across_waits() {
    setup().exercise();
    STATE.with(|s| {
        let s = s.borrow();
        assert!(s.input.is_empty());
        assert_eq!(s.closed, [11]);
        assert_eq!(s.prefix, b"e3b0c44298fc1c14");
        assert_eq!(s.output.len(), 15);
        assert_eq!(get(&s.output[14], 1), 7);
        assert_eq!(get(&s.output[14], 3), 2);
        assert_eq!(get(&s.output[14], 5), 64);
    });
}
