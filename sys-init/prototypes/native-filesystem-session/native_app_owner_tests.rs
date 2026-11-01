// SPDX-License-Identifier: BSD-2-Clause
//! First executable definitions for the selected private shared transfer seam.
//! These use the production Steps/transfer implementation, never a second loop.
//! Host boundary replies are scripted; no native timing or authority is inferred.
#[path = "stream_transport.rs"]
mod stream_transport;
use af07_transport::Kernel;
use native_app_runtime::{AppControl, Runtime};
use owner_control::{Control, Deadline, Status};
use std::collections::VecDeque;
use std::{cell::RefCell, collections::BTreeMap, rc::Rc};
use stream_transport::{Steps, transfer};

#[derive(Default)]
struct Boundary {
    results: VecDeque<i64>,
    waits: VecDeque<i64>,
    requests: Vec<(bool, Vec<u8>)>,
    waited: Vec<bool>,
    confirmed: Vec<u8>,
}

impl Boundary {
    fn replies(results: &[i64], waits: &[i64]) -> Self {
        Self {
            results: results.iter().copied().collect(),
            waits: waits.iter().copied().collect(),
            ..Self::default()
        }
    }
}

impl Steps for Boundary {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        assert!(!bytes.is_empty() && bytes.len() <= 16, "BOUNDED_CHUNK");
        self.requests.push((writing, bytes.to_vec()));
        let result = self.results.pop_front().expect("UNPLANNED_TRANSFER");
        if result > 0 && result as usize <= bytes.len() {
            let count = result as usize;
            if writing {
                self.confirmed.extend_from_slice(&bytes[..count]);
            } else {
                for byte in &mut bytes[..count] {
                    *byte = self.confirmed.len() as u8;
                    self.confirmed.push(*byte);
                }
            }
        }
        result
    }

    fn wait(&mut self, writing: bool) -> i64 {
        self.waited.push(writing);
        self.waits.pop_front().expect("UNPLANNED_WAIT")
    }
}

#[test]
fn shared_transfer_short_writes_advance_only_confirmed_prefix() {
    let mut boundary = Boundary::replies(&[3, 7, 6, 8], &[]);
    let mut bytes = *b"abcdefghijklmnopQRSTUVWX";
    assert_eq!(transfer(&mut boundary, &mut bytes, true), Ok(()));
    assert_eq!(boundary.confirmed, bytes, "EXACT_ONCE_OUTPUT_PREFIX");
    assert_eq!(boundary.requests.len(), 4);
    for ((writing, request), (offset, length)) in
        boundary
            .requests
            .iter()
            .zip([(0, 16), (3, 16), (10, 14), (16, 8)])
    {
        assert!(*writing);
        assert_eq!(request, &bytes[offset..offset + length]);
    }
    assert!(boundary.waited.is_empty());
    assert!(boundary.results.is_empty());
}

#[test]
fn shared_transfer_short_reads_publish_exact_initialized_bytes() {
    let mut boundary = Boundary::replies(&[1, 15, 8], &[]);
    let mut bytes = [0xa5; 24];
    assert_eq!(transfer(&mut boundary, &mut bytes, false), Ok(()));
    assert_eq!(bytes, core::array::from_fn::<_, 24, _>(|i| i as u8));
    assert!(boundary.requests.iter().all(|(writing, _)| !writing));
    assert!(boundary.waited.is_empty());
}

#[test]
fn shared_transfer_eagain_wait_zero_is_only_readiness() {
    for writing in [false, true] {
        let mut boundary = Boundary::replies(&[-11, 2], &[0]);
        let mut bytes = [7, 9];
        assert_eq!(transfer(&mut boundary, &mut bytes, writing), Ok(()));
        assert_eq!(boundary.requests.len(), 2, "REAL_IO_AFTER_WAIT");
        assert_eq!(boundary.waited, [writing]);
        assert_eq!(boundary.confirmed.len(), 2, "WAIT_IS_NOT_PROGRESS");
    }
}

#[test]
fn shared_transfer_wait_failure_has_no_effect_or_replay() {
    for status in [-110, -13, 1] {
        let mut boundary = Boundary::replies(&[-11], &[status]);
        let mut bytes = [1, 2];
        assert_eq!(
            transfer(&mut boundary, &mut bytes, true),
            Err(if status < 0 { status } else { -5 })
        );
        assert!(boundary.confirmed.is_empty());
        assert_eq!(boundary.requests.len(), 1);
        assert_eq!(boundary.waited, [true]);
    }
}

#[test]
fn shared_transfer_zero_oversized_and_transport_errors_reject() {
    for (result, expected) in [(0, -5), (3, -5), (-32, -32), (-5, -5)] {
        let mut boundary = Boundary::replies(&[result], &[]);
        let mut bytes = [1, 2];
        assert_eq!(transfer(&mut boundary, &mut bytes, true), Err(expected));
        assert!(boundary.confirmed.is_empty());
        assert_eq!(boundary.requests.len(), 1);
        assert!(boundary.waited.is_empty());
    }
}

#[test]
fn shared_transfer_error_after_progress_never_replays_effect() {
    let mut boundary = Boundary::replies(&[3, -32], &[]);
    let mut bytes = *b"abcdefgh";
    assert_eq!(transfer(&mut boundary, &mut bytes, true), Err(-32));
    assert_eq!(boundary.confirmed, b"abc", "CONFIRMED_PREFIX_RETAINED");
    assert_eq!(boundary.requests.len(), 2);
    assert_eq!(boundary.requests[1].1, b"defgh");
    assert!(boundary.waited.is_empty());
}

#[test]
fn shared_transfer_empty_span_does_not_call_boundary() {
    let mut boundary = Boundary::default();
    assert_eq!(transfer(&mut boundary, &mut [], true), Ok(()));
    assert!(boundary.requests.is_empty() && boundary.waited.is_empty());
}

#[derive(Clone)]
struct NativeBoundary(Rc<RefCell<Observed>>);
struct Observed {
    created: usize,
    fail_create: usize,
    launch_error: i64,
    launched: bool,
    record: Option<[u8; 320]>,
    launch_ends: [u64; 2],
    tick: u64,
    tick_step: u64,
    observations: usize,
    calls: usize,
    yields: usize,
    ready: bool,
    ready_at: u64,
    ready_observed: Option<u64>,
    stop_error: bool,
    query_error: bool,
    app_final: Status,
    engine_final: Status,
    engine_terminal_at: u64,
    stopped: [bool; 2],
    reclaimed: [bool; 2],
    reclaim_calls: usize,
    received: VecDeque<u8>,
    transmitted: Vec<u8>,
    fail_write_at: usize,
    serial_results: VecDeque<i64>,
    output: Vec<u8>,
    serial_calls: usize,
    closes: BTreeMap<u64, usize>,
    close_error: u64,
    console: usize,
    terminal: usize,
    halted: usize,
}
fn fixture() -> NativeBoundary {
    NativeBoundary(Rc::new(RefCell::new(Observed {
        created: 0,
        fail_create: 0,
        launch_error: 0,
        launched: false,
        record: None,
        launch_ends: [0; 2],
        tick: 10,
        tick_step: 0,
        observations: 0,
        calls: 0,
        yields: 0,
        ready: true,
        ready_at: 0,
        ready_observed: None,
        stop_error: false,
        query_error: false,
        app_final: (1, 0, 1),
        engine_final: (1, 0, 1),
        engine_terminal_at: 0,
        stopped: [false; 2],
        reclaimed: [false; 2],
        reclaim_calls: 0,
        received: VecDeque::new(),
        transmitted: Vec::new(),
        fail_write_at: usize::MAX,
        serial_results: VecDeque::new(),
        output: Vec::new(),
        serial_calls: 0,
        closes: BTreeMap::new(),
        close_error: 0,
        console: 0,
        terminal: 0,
        halted: 0,
    })))
}
fn cap(object: u64, end: u64) -> u64 {
    0xd1000000 | object << 16 | 1 << 8 | end
}
impl Kernel for NativeBoundary {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        assert_eq!(
            endpoint,
            if writing { cap(1, 2) } else { cap(0, 1) },
            "INIT_MUST_NOT_CONSUME_NAMESPACE_GREETING"
        );
        if writing {
            if seen.transmitted.len() >= seen.fail_write_at {
                return -5;
            }
            let count = bytes.len().min(seen.fail_write_at - seen.transmitted.len());
            seen.transmitted.extend_from_slice(&bytes[..count]);
            count as i64
        } else {
            let count = bytes.len().min(seen.received.len());
            for byte in &mut bytes[..count] {
                *byte = seen.received.pop_front().unwrap();
            }
            count as i64
        }
    }
    fn wait(&mut self, _: u64) -> i64 {
        panic!("NO_BLOCKING_CHANNEL_WAIT");
    }
    fn close(&mut self, endpoint: u64) -> i64 {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        *seen.closes.entry(endpoint).or_default() += 1;
        if seen.close_error == endpoint { -5 } else { 0 }
    }
}
impl Control for NativeBoundary {
    fn observe_events(&mut self) -> Status {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        seen.observations += 1;
        let tick = seen.tick;
        seen.tick += seen.tick_step;
        (0, 1, tick)
    }
    fn park_events(&mut self, _: u64, _: Option<Deadline>) -> Status {
        panic!("NO_PARKED_DEADLINE_SUBSTITUTE");
    }
    fn ctl(&mut self, op: u64, handle: u64, _: u64) -> Status {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        match op {
            0x24000 => {
                seen.created += 1;
                assert_eq!(handle, if seen.created <= 2 { 0xd002 } else { 0xd001 });
                if seen.created == seen.fail_create {
                    return (-12, 0, 0);
                }
                let object = [10, 11, 0, 1][seen.created - 1];
                (cap(object, 1) as i64, cap(object, 2), 0)
            }
            0x1fffe => {
                seen.yields += 1;
                (0, 0, 0)
            }
            0x20001 => {
                let index = usize::from(handle == 0xb0000101);
                assert!(handle == 0xb0000101 || handle == 0xb0000102);
                if seen.query_error {
                    return (-13, 0, 0);
                }
                if seen.reclaimed[index] {
                    (-9, 0, 0)
                } else if seen.stopped[index] {
                    (144, 0, 3)
                } else if index == 1 && !seen.launched {
                    let tick = seen.tick.saturating_sub(seen.tick_step);
                    let ready = seen.ready && tick >= seen.ready_at;
                    if ready {
                        seen.ready_observed = Some(tick);
                    }
                    (0, u64::from(ready), 0)
                } else if index == 1 {
                    if seen.tick.saturating_sub(seen.tick_step) < seen.engine_terminal_at {
                        return (0, 0, 0);
                    }
                    seen.engine_final
                } else {
                    seen.app_final
                }
            }
            0x20007 => {
                if seen.stop_error {
                    return (-5, 0, 0);
                }
                seen.stopped[usize::from(handle == 0xb0000101)] = true;
                (0, 0, 0)
            }
            0x20002 => {
                seen.reclaimed[usize::from(handle == 0xb0000101)] = true;
                seen.reclaim_calls += 1;
                (0, 0, 0)
            }
            0x26002 => {
                assert_eq!(handle, 0xf001);
                seen.console += 1;
                (0, 0, 0)
            }
            0x100e7 => {
                assert_eq!(handle, 125);
                seen.terminal += 1;
                (0, 0, 0)
            }
            0x2a002 => {
                assert_eq!(handle, 0xf002);
                seen.halted += 1;
                (0, 0, 0)
            }
            _ => panic!("UNSELECTED_CONTROL {op:x}"),
        }
    }
    fn engine(&mut self, reader: u64, writer: u64) -> i64 {
        assert_eq!([reader, writer], [cap(10, 1), cap(11, 2)]);
        self.0.borrow_mut().calls += 1;
        0xb0000101
    }
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64 {
        assert_eq!(engine, 0xb0000101);
        assert_eq!(*region, [8, 2097152, 7]);
        self.0.borrow_mut().calls += 1;
        0
    }
    fn launch(&mut self, _: &[u8; 272], _: u64, _: u64) -> i64 {
        panic!("OLD_LAUNCH_FORBIDDEN");
    }
    fn copy(&mut self, _: u64, _: u32, _: u64, _: u64, _: u64) -> i64 {
        panic!("COPY_FORBIDDEN");
    }
    fn serial(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        assert!(writing && bytes.len() <= 16, "OUTPUT_ONLY");
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        seen.serial_calls += 1;
        let result = seen
            .serial_results
            .pop_front()
            .unwrap_or(bytes.len() as i64);
        if result > 0 && result as usize <= bytes.len() {
            seen.output.extend_from_slice(&bytes[..result as usize]);
        }
        result
    }
    fn exec(&mut self, _: u64, _: u64, _: &[u8; 272]) -> i64 {
        panic!("EXEC_FORBIDDEN");
    }
    fn receipt(&mut self, _: u64) -> Status {
        panic!("RECEIPT_FORBIDDEN");
    }
    fn publish(&mut self, _: u64, _: u64) -> i64 {
        panic!("PUBLISH_FORBIDDEN");
    }
}
impl AppControl for NativeBoundary {
    fn launch_app(&mut self, record: &[u8; 320], reader: u64, writer: u64) -> i64 {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        seen.record = Some(*record);
        seen.launch_ends = [reader, writer];
        if seen.launch_error != 0 {
            seen.launch_error
        } else {
            seen.launched = true;
            0xb0000102
        }
    }
}
fn frame(op: u32, selector: u32, bytes: &[u8]) -> [u8; 32] {
    let mut raw = [0; 32];
    for (at, word) in [
        (0, op),
        (4, 0x7a000001 | selector << 16),
        (8, selector),
        (12, bytes.len() as u32),
    ] {
        raw[at..at + 4].copy_from_slice(&word.to_le_bytes());
    }
    raw[16..16 + bytes.len()].copy_from_slice(bytes);
    raw
}
fn workload(boundary: &NativeBoundary) {
    let mut seen = boundary.0.borrow_mut();
    for raw in [
        frame(2, 1, b"out\n"),
        frame(2, 2, b"err\n"),
        frame(3, 1, b""),
        frame(3, 2, b""),
    ] {
        seen.received.extend(raw);
    }
}

#[test]
fn partial_provision_owns_first_pair() {
    let boundary = fixture();
    boundary.0.borrow_mut().fail_create = 2;
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.provision(&mut [0; 4096]), Err(-12));
    assert_eq!(
        runtime.snapshot().ends.iter().filter(|e| e.owned).count(),
        2,
        "FIRST_PAIR_RETAINED"
    );
    let _ = runtime.contain();
    let seen = boundary.0.borrow();
    assert_eq!(
        seen.closes,
        BTreeMap::from([(cap(10, 1), 1), (cap(10, 2), 1)])
    );
    assert_eq!((seen.console, seen.terminal, seen.halted), (1, 1, 0));
}

#[test]
fn launch_rejection_retains_four_app_ends_and_exact_cleanup_reserve() {
    let boundary = fixture();
    boundary.0.borrow_mut().launch_error = -13;
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.provision(&mut [0; 4096]), Err(-13));
    assert_eq!(
        runtime.snapshot().ends.iter().filter(|e| e.owned).count(),
        6,
        "APP_ENDS_RETAINED"
    );
    let _ = runtime.contain();
    assert_eq!(runtime.snapshot().reserved, 0, "EXACT_OWNER_RESERVE");
    let seen = boundary.0.borrow();
    assert_eq!(seen.closes.len(), 6);
    assert!(seen.closes.values().all(|n| *n == 1));
    assert!(!seen.closes.contains_key(&cap(10, 1)) && !seen.closes.contains_key(&cap(11, 2)));
}

#[test]
fn handoff_preserves_both_greetings_and_publishes_exact_startup() {
    let boundary = fixture();
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    runtime.provision(&mut [0; 4096]).unwrap();
    let seen = boundary.0.borrow();
    let raw = seen.record.unwrap();
    assert_eq!(&raw[..8], b"AENAP001");
    assert_eq!(u64::from_le_bytes(raw[8..16].try_into().unwrap()), 320);
    assert_eq!(u64::from_le_bytes(raw[16..24].try_into().unwrap()), 3);
    assert_eq!(raw[24], 1);
    assert_eq!(&raw[32..39], b"mktemp\0");
    assert_eq!(&raw[64..67], b"-d\0");
    assert_eq!(&raw[96..111], b"/home/t.XXXXXX\0");
    assert_eq!(&raw[160..169], b"LC_ALL=C\0");
    assert_eq!(
        u64::from_le_bytes(raw[288..296].try_into().unwrap()),
        0xb0000101
    );
    assert_eq!(
        u64::from_le_bytes(raw[296..304].try_into().unwrap()),
        cap(11, 1)
    );
    assert_eq!(
        u64::from_le_bytes(raw[304..312].try_into().unwrap()),
        cap(10, 2)
    );
    assert_eq!(&raw[312..], &[0; 8]);
    assert_eq!(seen.launch_ends, [cap(1, 1), cap(0, 2)]);
    assert_eq!(seen.transmitted.len(), 304);
    assert_eq!(&seen.transmitted[..8], b"AEFDB001");
    assert_eq!(&seen.transmitted[48..56], b"AEFDT001");
    assert_eq!(
        u64::from_le_bytes(seen.transmitted[56..64].try_into().unwrap()),
        cap(0, 1)
    );
    assert_eq!(
        &seen.transmitted[112..124],
        &[0, 0, 0, 0, 1, 1, 0, 0, 1, 2, 0, 0]
    );
    assert_eq!(&seen.transmitted[288..296], &[0; 8]);
    assert_eq!(
        runtime.snapshot().ends.iter().filter(|e| e.owned).count(),
        2
    );
}

#[test]
fn actual_stream_owner_routes_distinct_outputs_and_requires_independent_settlement() {
    let boundary = fixture();
    workload(&boundary);
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5)); // Returned halt sentinel.
    let seen = boundary.0.borrow();
    assert_eq!(seen.output, b"out\nerr\n");
    assert_eq!(
        (seen.halted, seen.terminal, seen.console, seen.reclaim_calls),
        (1, 0, 1, 2)
    );
    assert_eq!(
        seen.closes,
        BTreeMap::from([(cap(0, 1), 1), (cap(1, 2), 1)])
    );
}

#[test]
fn app_zero_engine_failure_rejected() {
    let boundary = fixture();
    workload(&boundary);
    boundary.0.borrow_mut().engine_final = (2, 0, 2);
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(
        runtime.run(&mut [0; 4096]),
        Err(-5),
        "ENGINE_EXPORT_FAILURE_REJECTED"
    );
    assert_eq!(boundary.0.borrow().halted, 0, "NO_FALSE_CLEAN_HALT");
    let _ = runtime.contain();
    assert_eq!(boundary.0.borrow().terminal, 1);
}

#[test]
fn app_success_waits_for_engine_terminal_within_the_absolute_deadline() {
    for (engine_terminal_at, settled) in [(2000, true), (6000, false)] {
        let boundary = fixture();
        workload(&boundary);
        {
            let mut seen = boundary.0.borrow_mut();
            seen.tick_step = 1;
            seen.ready_at = 600;
            seen.engine_terminal_at = engine_terminal_at;
        }
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(
            runtime.run(&mut [0; 4096]),
            Err(if settled { -5 } else { -110 }) // Returned halt sentinel or timeout.
        );
        let seen = boundary.0.borrow();
        assert_eq!(seen.output, b"out\nerr\n");
        assert_eq!(runtime.snapshot().observed_terminal[0], Some((1, 0, 1)));
        assert!(seen.reclaimed[0], "APP_SUCCESS_PRECEDES_ENGINE_SETTLEMENT");
        assert_eq!(seen.reclaimed[1], settled);
        assert_eq!(seen.halted, usize::from(settled));
        assert_eq!(seen.terminal, 0);
        assert_eq!(seen.stopped, [false; 2]);
        if settled {
            assert!(seen.tick > engine_terminal_at && seen.tick < 6000);
            assert_eq!(runtime.snapshot().observed_terminal[1], Some((1, 0, 1)));
        } else {
            assert_eq!(seen.tick, 6001, "DEADLINE_TIE_PRECEDES_ENGINE_SUCCESS");
            assert_eq!(runtime.snapshot().observed_terminal[1], None);
        }
    }
}

#[test]
fn delayed_engine_readiness_keeps_the_absolute_writer_deadline() {
    let boundary = fixture();
    {
        let mut seen = boundary.0.borrow_mut();
        seen.tick_step = 1;
        seen.ready_at = 600;
    }
    // Continuous output cannot renew the absolute writer deadline.
    for _ in 0..2000 {
        boundary.0.borrow_mut().received.extend(frame(2, 1, b"ok"));
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-110));
    let seen = boundary.0.borrow();
    let ready_tick = seen.ready_observed.expect("DELAYED_READY_REACHED");
    assert!(ready_tick >= 600 && seen.launched && seen.serial_calls > 0);
    assert_eq!(seen.tick, 6001, "ABSOLUTE_DEADLINE_NOT_RENEWED");
    assert_eq!(seen.halted, 0);
}

#[test]
fn late_engine_readiness_cannot_extend_the_absolute_writer_ceiling() {
    let boundary = fixture();
    {
        let mut seen = boundary.0.borrow_mut();
        seen.tick = 5700;
        seen.tick_step = 1;
        seen.ready_at = 5800;
        for _ in 0..2000 {
            seen.received.extend(frame(2, 1, b"ok"));
        }
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-110));
    let seen = boundary.0.borrow();
    assert!(seen.launched && seen.serial_calls > 0);
    assert_eq!(seen.tick, 6001, "ABSOLUTE_CEILING_NOT_RENEWED");
    assert_eq!(seen.halted, 0);
}

#[test]
fn absolute_startup_deadline_rejects_the_exact_tie_before_effects() {
    let boundary = fixture();
    boundary.0.borrow_mut().tick = 6000;
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.provision(&mut [0; 4096]), Err(-110));
    let seen = boundary.0.borrow();
    assert_eq!(seen.created, 0);
    assert!(!seen.launched);
}

#[test]
fn continuous_progress_expires_fixed_deadline() {
    let boundary = fixture();
    {
        let mut seen = boundary.0.borrow_mut();
        seen.tick_step = 1;
        for _ in 0..2000 {
            seen.received.extend(frame(2, 1, b"ok"));
        }
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(
        runtime.run(&mut [0; 4096]),
        Err(-110),
        "FIXED_DEADLINE_NOT_RENEWED"
    );
    assert!(boundary.0.borrow().serial_calls > 0);
    let _ = runtime.contain();
    assert_eq!(boundary.0.borrow().halted, 0);
}

#[test]
fn expired_cleanup_never_replays_or_reclaims_live() {
    let boundary = fixture();
    {
        let mut seen = boundary.0.borrow_mut();
        seen.tick_step = 1;
        seen.ready = false;
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-110));
    {
        let mut seen = boundary.0.borrow_mut();
        seen.stop_error = true;
        seen.query_error = true;
    }
    let _ = runtime.contain();
    let calls = boundary.0.borrow().calls;
    let _ = runtime.contain();
    let seen = boundary.0.borrow();
    assert_eq!(seen.reclaim_calls, 0, "NO_UNKNOWN_RECLAIM");
    assert_eq!(seen.calls, calls, "NO_CLEANUP_REPLAY");
    assert_eq!((seen.terminal, seen.halted), (1, 0));
}

#[test]
fn partial_reply_unknown_never_replayed() {
    let boundary = fixture();
    workload(&boundary);
    boundary.0.borrow_mut().fail_write_at = 309;
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
    assert_eq!(runtime.snapshot().reply_bytes, 5, "PARTIAL_REPLY_RETAINED");
    assert_eq!(boundary.0.borrow().serial_calls, 1);
    assert_eq!(boundary.0.borrow().output, b"out\n");
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-16));
    assert_eq!(
        boundary.0.borrow().serial_calls,
        1,
        "WRITE_EFFECT_NOT_REPLAYED"
    );
}

#[test]
fn stream_only_rejects_other_families_before_effects() {
    let mut exec = [0; 32];
    exec[..8].copy_from_slice(b"AEEXEC02");
    for raw in [
        frame(1, 1, b""),
        frame(82, 1, b""),
        frame(68, 1, b""),
        frame(2, 0, b"x"),
        frame(2, 3, b"x"),
        exec,
    ] {
        let boundary = fixture();
        boundary.0.borrow_mut().received.extend(raw);
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(runtime.run(&mut [0; 4096]), Err(-22));
        assert_eq!(boundary.0.borrow().serial_calls, 0, "DENIED_BEFORE_EFFECT");
        assert_eq!(
            runtime.snapshot().request_bytes,
            16,
            "DENIED_WITHOUT_TAIL_READ"
        );
    }
}

#[test]
fn retained_ready_does_not_change_terminal_exit_status_contract() {
    let boundary = fixture();
    workload(&boundary);
    boundary.0.borrow_mut().app_final = (1, 1, 1);
    boundary.0.borrow_mut().engine_final = (1, 1, 1);
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    let _ = runtime.run(&mut [0; 4096]);
    assert_eq!(
        boundary.0.borrow().halted,
        1,
        "READY_BIT_IS_NOT_EXIT_STATUS"
    );
    for engine in [false, true] {
        let boundary = fixture();
        workload(&boundary);
        if engine {
            boundary.0.borrow_mut().engine_final = (8, 1, 1);
        } else {
            boundary.0.borrow_mut().app_final = (8, 1, 1);
        }
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(
            runtime.run(&mut [0; 4096]),
            Err(-5),
            "NONZERO_EXIT_REJECTED"
        );
        assert_eq!(boundary.0.borrow().halted, 0, "NO_FALSE_EXIT_ZERO");
    }
}

#[test]
fn owner_reserve_covers_post_admission_fault_and_close_errors() {
    let boundary = fixture();
    workload(&boundary);
    {
        let mut seen = boundary.0.borrow_mut();
        seen.app_final = (2, 0, 2);
        seen.close_error = cap(0, 1);
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
    let _ = runtime.contain();
    let snapshot = runtime.snapshot();
    assert_eq!(snapshot.reserved, 0, "POST_APP_EXACT_RESERVE");
    assert!(snapshot.cleanup_started && snapshot.terminal_attempted);
    assert!(
        snapshot
            .cleanup_attempted
            .iter()
            .flatten()
            .all(|attempted| *attempted)
    );
    assert_eq!(
        snapshot
            .ends
            .iter()
            .find(|e| e.cap == cap(0, 1))
            .unwrap()
            .status,
        -5,
        "RAW_CLOSE_ERROR_RETAINED"
    );
    let before = boundary.0.borrow().calls;
    let _ = runtime.contain();
    assert_eq!(boundary.0.borrow().calls, before, "CONTAINMENT_ONCE_ENTRY");
}
