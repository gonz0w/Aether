// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use af07_transport::Kernel;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity};
use fixture::{Fault, Harness};
use fork_gate::{GateError, Owner, Phase};
use fork_streams::{SessionPipe, State};
use std::panic::{AssertUnwindSafe, catch_unwind};
fn id() -> Identity {
    Identity::admitted(1, 1, 0xb0000102).unwrap()
}
fn native(slot: u32) -> NativeIdentity {
    NativeIdentity::admitted(slot, 1, 0xb0000100 | (slot as u64 + 1)).unwrap()
}
fn state() -> State {
    State::new([None; 3], [SessionPipe::new(), SessionPipe::new()]).unwrap()
}
fn plan() -> Plan {
    Plan {
        identity: id(),
        shell: 1,
        parent: 7,
        generation: 1,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [0; 2],
    }
}
fn frame(sequence: u64) -> [u8; 304] {
    let mut raw = [0; 304];
    fd_startup::encode(&plan(), &mut raw).unwrap();
    raw[..8].copy_from_slice(fork_frames::MAGIC);
    raw[296..].copy_from_slice(&sequence.to_le_bytes());
    raw
}
struct Wire {
    bytes: [u8; 304],
    position: usize,
    limit: usize,
    chunk: usize,
    calls: usize,
    eagain: bool,
    wait: i64,
    fault: i64,
    panic_at: Option<usize>,
    waits: usize,
}
impl Wire {
    fn new(sequence: u64) -> Self {
        Self {
            bytes: frame(sequence),
            position: 0,
            limit: 304,
            chunk: 7,
            calls: 0,
            eagain: false,
            wait: 0,
            fault: 0,
            panic_at: None,
            waits: 0,
        }
    }
}
impl Kernel for Wire {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        assert_eq!(endpoint, 71);
        assert!(!writing);
        assert!(!bytes.is_empty() && bytes.len() <= 16);
        self.calls += 1;
        assert_ne!(self.panic_at, Some(self.position), "transport unwind");
        if self.eagain && self.calls % 2 == 1 {
            return -11;
        }
        if self.position == self.limit {
            return self.fault;
        }
        let n = bytes.len().min(self.chunk).min(self.limit - self.position);
        bytes[..n].copy_from_slice(&self.bytes[self.position..self.position + n]);
        self.position += n;
        n as i64
    }
    fn wait(&mut self, endpoint: u64) -> i64 {
        assert_eq!(endpoint, 71);
        self.waits += 1;
        self.wait
    }
    fn close(&mut self, _: u64) -> i64 {
        panic!("capture never closes native endpoints")
    }
}
#[test]
fn complete_capture_accepts_actual_gapped_sequence_and_preserves_refusal_flow() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let mut f = h.fds.take().unwrap();
    let p = f.admitted_shell(native(1), 7).unwrap();
    let mut g = Owner::new(f, state());
    for sequence in [7, u64::MAX] {
        let mut wire = Wire::new(sequence);
        wire.eagain = true;
        let (mut raw, mut scratch) = ([0xa5; 304], [0x5a; 304]);
        let mut budget = 1000;
        let parsed = fork_transport::receive(
            &mut g,
            &mut wire,
            71,
            (id(), 7, 1),
            &mut budget,
            &mut raw,
            &mut scratch,
        )
        .unwrap();
        assert_eq!(g.sequence(), sequence);
        assert_eq!(g.phase(), Phase::Capturing);
        assert_eq!(raw, [0; 304]);
        assert_eq!(scratch, [0; 304]);
        assert_eq!(wire.position, 304);
        assert!(wire.waits > 0);
        assert!(h.opcodes().is_empty());
        assert_eq!(h.storage.lock().unwrap().lookups, 0);
        g.copy(sequence, p, native(2), 9, &parsed, |_| {
            CopyAttempt::Refused(-12)
        })
        .unwrap()
        .unwrap_err();
        g.resolve_refusal(sequence, -12, |_| Ok(-11))
            .unwrap()
            .unwrap();
        g.refusal_delivered(sequence, -12).unwrap();
    }
    g.retire();
    drop(g);
    drop(h);
}
#[test]
fn every_short_body_and_bad_header_stays_closed_without_source_effect() {
    for limit in 0..304 {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let f = h.fds.take().unwrap();
        let mut g = Owner::new(f, state());
        let mut wire = Wire::new(1);
        wire.limit = limit;
        let mut budget = 1000;
        let (mut raw, mut scratch) = ([9; 304], [9; 304]);
        assert_eq!(
            fork_transport::receive(
                &mut g,
                &mut wire,
                71,
                (id(), 7, 1),
                &mut budget,
                &mut raw,
                &mut scratch
            )
            .err(),
            Some(GateError::Capture(-5))
        );
        assert_eq!(wire.position, limit);
        assert_eq!(raw, [0; 304]);
        assert_eq!(scratch, [0; 304]);
        assert_eq!(g.phase(), Phase::Rejected);
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(g.cleanup(), None);
        assert!(h.opcodes().is_empty());
        assert_eq!(h.local.lock().unwrap().closes, 0);
        g.retire();
        drop(g);
        drop(h);
    }
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let mut g = Owner::new(h.fds.take().unwrap(), state());
    let mut wire = Wire::new(1);
    wire.bytes[0] ^= 1;
    let mut budget = 1000;
    let (mut raw, mut scratch) = ([9; 304], [9; 304]);
    assert_eq!(
        fork_transport::receive(
            &mut g,
            &mut wire,
            71,
            (id(), 7, 1),
            &mut budget,
            &mut raw,
            &mut scratch
        )
        .err(),
        Some(GateError::Capture(-22))
    );
    assert_eq!(wire.position, 16);
    assert_eq!(raw, [0; 304]);
    assert_eq!(scratch, [0; 304]);
    g.retire();
    drop(g);
    drop(h);
}
#[test]
fn malformed_body_sequence_and_wait_or_budget_failure_never_reopen() {
    for mode in 0..9 {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let mut g = Owner::new(h.fds.take().unwrap(), state());
        let mut wire = Wire::new(1);
        let mut budget = 1000;
        match mode {
            0 => wire.bytes[296..].fill(0),
            1 => wire.bytes[72] = 1,
            2 => wire.bytes[40] ^= 1,
            3 => {
                wire.eagain = true;
                wire.wait = -9;
            }
            4 => {
                wire.eagain = true;
                wire.wait = 1;
            }
            5 => budget = 0,
            6 => {
                wire.chunk = 0;
                wire.limit = 0;
                wire.fault = -4;
            }
            7 => budget = 1,
            _ => {
                wire.limit = 0;
                wire.fault = 17;
            }
        }
        let (mut raw, mut scratch) = ([9; 304], [9; 304]);
        let r = fork_transport::receive(
            &mut g,
            &mut wire,
            71,
            (id(), 7, 1),
            &mut budget,
            &mut raw,
            &mut scratch,
        );
        let expected = match mode {
            0 | 1 => GateError::Capture(-22),
            2 => GateError::Capture(-9),
            3 => GateError::Capture(-9),
            4 => GateError::Capture(-5),
            6 => GateError::Capture(-4),
            8 => GateError::Capture(-5),
            _ => GateError::Capture(-110),
        };
        assert_eq!(r.err(), Some(expected));
        assert_eq!(g.phase(), Phase::Rejected);
        assert_eq!(g.sequence(), 0);
        assert_eq!(raw, [0; 304]);
        assert_eq!(scratch, [0; 304]);
        assert!(h.opcodes().is_empty());
        g.retire();
        drop(g);
        drop(h);
    }
}
#[test]
fn capture_unwind_blocks_copy_and_clears_buffers() {
    for known in [false, true] {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let mut f = h.fds.take().unwrap();
        let parent = f.admitted_shell(native(1), 7).unwrap();
        let mut g = Owner::new(f, state());
        let (mut raw, mut scratch) = ([9; 304], [9; 304]);
        let r = catch_unwind(AssertUnwindSafe(|| {
            if known {
                let _: Result<(), _> = g.begin(1, |_, _| panic!("known capture"));
            } else {
                let mut wire = Wire::new(1);
                wire.panic_at = Some(16);
                wire.chunk = 16;
                let mut budget = 1000;
                let _ = fork_transport::receive(
                    &mut g,
                    &mut wire,
                    71,
                    (id(), 7, 1),
                    &mut budget,
                    &mut raw,
                    &mut scratch,
                );
            }
        }));
        assert!(r.is_err());
        assert_eq!(g.phase(), Phase::Receiving);
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        assert_eq!(
            g.copy(g.sequence(), parent, native(2), 9, &plan(), |_| panic!(
                "copy after failed capture"
            )),
            Err(GateError::Closed)
        );
        if !known {
            assert_eq!(raw, [0; 304]);
            assert_eq!(scratch, [0; 304]);
        }
        g.retire();
        drop(g);
        drop(h);
    }
}
#[test]
fn replay_and_zero_capture_reject_without_advancing_watermark() {
    for sequence in [0, 5, 6] {
        let mut h = Harness::new(Fault::None, [-9, -5]);
        let mut f = h.fds.take().unwrap();
        let parent = f.admitted_shell(native(1), 7).unwrap();
        let mut g = Owner::new(f, state());
        g.begin(6, |_, _| ()).unwrap();
        g.copy(6, parent, native(2), 9, &plan(), |_| {
            CopyAttempt::Refused(-12)
        })
        .unwrap()
        .unwrap_err();
        g.resolve_refusal(6, -12, |_| Ok(-11)).unwrap().unwrap();
        g.refusal_delivered(6, -12).unwrap();
        assert_eq!(
            g.capture(|_, _| Ok((sequence, ()))),
            Err(GateError::Sequence)
        );
        assert_eq!(g.sequence(), 6);
        assert_eq!(g.phase(), Phase::Rejected);
        assert_eq!(g.admit(|_, _| ()), Err(GateError::Closed));
        g.retire();
        drop(g);
        drop(h);
    }
}
