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
    input: VecDeque<u8>,
    serial_calls: usize,
    closes: BTreeMap<u64, usize>,
    close_error: u64,
    console: usize,
    terminal: usize,
    halted: usize,
    mode_live: bool,
    tx: VecDeque<i64>,
    tx_default: i64,
    tx_queries: usize,
    tx_output_lengths: Vec<usize>,
    #[cfg(native_tty_mode_probe)]
    mode_parks: Vec<u64>,
    #[cfg(native_tty_mode_probe)]
    mode_park_error: i64,
    #[cfg(native_tty_mode_probe)]
    mode_die_on_park: bool,
    mode_query_tick: Option<u64>,
    fail_write_code: i64,
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
        input: VecDeque::new(),
        serial_calls: 0,
        closes: BTreeMap::new(),
        close_error: 0,
        console: 0,
        terminal: 0,
        halted: 0,
        mode_live: false,
        tx: VecDeque::new(),
        tx_default: 0,
        tx_queries: 0,
        tx_output_lengths: Vec::new(),
        #[cfg(native_tty_mode_probe)]
        mode_parks: Vec::new(),
        #[cfg(native_tty_mode_probe)]
        mode_park_error: 0,
        #[cfg(native_tty_mode_probe)]
        mode_die_on_park: false,
        mode_query_tick: None,
        fail_write_code: -5,
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
                return seen.fail_write_code;
            }
            let count = bytes.len().min(seen.fail_write_at - seen.transmitted.len());
            seen.transmitted.extend_from_slice(&bytes[..count]);
            count as i64
        } else {
            let count = bytes.len().min(seen.received.len());
            if count == 0 {
                seen.mode_live = false;
            }
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
    fn transmitter_empty(&mut self) -> i64 {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        seen.tx_queries += 1;
        let length = seen.output.len();
        seen.tx_output_lengths.push(length);
        if let Some(tick) = seen.mode_query_tick {
            seen.tick = tick;
        }
        let default = seen.tx_default;
        seen.tx.pop_front().unwrap_or(default)
    }
    #[cfg(not(native_tty_mode_probe))]
    fn park_events(&mut self, _: u64, _: Option<Deadline>) -> Status {
        panic!("NO_PARKED_DEADLINE_SUBSTITUTE");
    }
    #[cfg(native_tty_mode_probe)]
    fn park_events(&mut self, _: u64, deadline: Option<Deadline>) -> Status {
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        let tick = deadline.unwrap().get();
        seen.mode_parks.push(tick);
        if seen.mode_die_on_park {
            seen.mode_live = false;
            seen.app_final = (2, 0, 1);
        }
        if seen.mode_park_error != 0 {
            return (seen.mode_park_error, u64::MAX, u64::MAX);
        }
        seen.tick = tick;
        (-110, u64::MAX, u64::MAX)
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
                } else if seen.mode_live {
                    (0, 0, 0)
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
        assert!(
            bytes.len() <= 16
                && (writing
                    || cfg!(any(
                        native_tty_byte_probe,
                        native_tty_descriptor_probe,
                        any(native_tty_duplex_probe, native_tty_mode_probe)
                    ))),
            "SELECTED_DIRECTION"
        );
        let mut seen = self.0.borrow_mut();
        seen.calls += 1;
        seen.serial_calls += 1;
        let result = seen.serial_results.pop_front().unwrap_or(if writing {
            bytes.len() as i64
        } else {
            bytes.len().min(seen.input.len()) as i64
        });
        if result > 0 && result as usize <= bytes.len() {
            if writing {
                seen.output.extend_from_slice(&bytes[..result as usize]);
            } else {
                for byte in &mut bytes[..result as usize] {
                    *byte = seen.input.pop_front().expect("PLANNED_INPUT");
                }
            }
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
    if cfg!(any(
        native_tty_byte_probe,
        native_tty_descriptor_probe,
        any(native_tty_duplex_probe, native_tty_mode_probe)
    )) {
        seen.received.extend(frame(3, 0, b""));
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
#[cfg(not(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
)))]
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
#[cfg(not(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
)))]
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

#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
#[test]
fn selected_startup_admits_exact_three_sources_and_no_mode() {
    let boundary = fixture();
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    runtime.provision(&mut [0; 4096]).unwrap();
    let seen = boundary.0.borrow();
    assert_eq!(
        &seen.transmitted[112..124],
        if cfg!(any(
            native_tty_descriptor_probe,
            any(native_tty_duplex_probe, native_tty_mode_probe)
        )) {
            &[4, 0, 0, 0, 4, 1, 0, 0, 4, 2, 0, 0]
        } else {
            &[1, 0, 0, 0, 1, 1, 0, 0, 1, 2, 0, 0]
        }
    );
    for selector in 0..3usize {
        let at = 176 + selector * 16;
        let source: Vec<u32> = seen.transmitted[at..at + 16]
            .as_chunks::<4>()
            .0
            .iter()
            .map(|word| u32::from_le_bytes(*word))
            .collect();
        assert_eq!(
            source,
            [
                0x7a000001 | (selector as u32) << 16,
                selector as u32,
                if selector == 0 { 1 } else { 2 },
                16
            ]
        );
    }
    assert_eq!(&seen.transmitted[224..296], &[0; 72]);
}
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
#[test]
fn selected_binary_nul_short_read_pending_and_three_closes_settle() {
    let boundary = fixture();
    {
        let mut seen = boundary.0.borrow_mut();
        seen.input.extend([0, 13, 10, 128, 255]);
        seen.serial_results.extend([-11, 1, 4]);
        seen.received.extend(frame(1, 0, &[0; 5]));
        seen.received.extend(frame(1, 0, &[0; 4]));
    }
    workload(&boundary);
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
    let seen = boundary.0.borrow();
    assert_eq!(seen.transmitted[304..308], 1u32.to_le_bytes());
    assert_eq!(seen.transmitted[320], 0, "NUL_IS_ONE_DATA_BYTE");
    assert_eq!(seen.transmitted[336..340], 4u32.to_le_bytes());
    assert_eq!(&seen.transmitted[352..356], &[13, 10, 128, 255]);
    assert!(seen.input.is_empty());
    assert_eq!((seen.reclaim_calls, seen.halted), (2, 1));
    assert!(seen.yields > 0);
}
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
#[test]
fn selected_direction_zero_and_closed_alias_denials_have_no_serial_effect() {
    let boundary = fixture();
    {
        let mut seen = boundary.0.borrow_mut();
        for raw in [
            frame(1, 1, &[0]),
            frame(2, 0, b"x"),
            frame(1, 0, b""),
            frame(2, 1, b""),
            frame(3, 0, b""),
            frame(1, 0, &[0]),
        ] {
            seen.received.extend(raw);
        }
        for selector in [1, 2] {
            seen.received.extend(frame(3, selector, b""));
        }
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
    let seen = boundary.0.borrow();
    let results: Vec<i32> = seen.transmitted[304..]
        .as_chunks::<32>()
        .0
        .iter()
        .map(|raw| i32::from_le_bytes(raw[..4].try_into().unwrap()))
        .collect();
    assert_eq!(results, [-13, -13, 0, 0, 0, -13, 0, 0]);
    assert_eq!(seen.serial_calls, 0);
    assert_eq!(seen.halted, 1);
}
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
#[test]
fn selected_unknown_serial_completion_never_sends_fabricated_reply_or_replays() {
    for raw in [17, -4096, i64::MAX] {
        let boundary = fixture();
        boundary.0.borrow_mut().serial_results.push_back(raw);
        boundary
            .0
            .borrow_mut()
            .received
            .extend(frame(1, 0, &[0; 16]));
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
        assert_eq!(
            boundary.0.borrow().transmitted.len(),
            304,
            "NO_KNOWN_UNKNOWN_REPLY"
        );
        assert_eq!(boundary.0.borrow().serial_calls, 1);
        assert_eq!(runtime.contain(), Err(-5));
        assert!(runtime.run(&mut [0; 4096]).is_err());
        assert_eq!(boundary.0.borrow().serial_calls, 1);
    }
}
#[cfg(any(
    native_tty_byte_probe,
    native_tty_descriptor_probe,
    any(native_tty_duplex_probe, native_tty_mode_probe)
))]
#[test]
fn selected_foreign_stale_and_wrong_family_headers_deny_before_effect() {
    for mut raw in [frame(1, 0, &[0]), frame(2, 1, b"x")] {
        raw[4] ^= 1;
        let boundary = fixture();
        boundary.0.borrow_mut().received.extend(raw);
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(runtime.run(&mut [0; 4096]), Err(-22));
        assert_eq!(boundary.0.borrow().serial_calls, 0);
        assert_eq!(runtime.snapshot().request_bytes, 16);
    }
    let boundary = fixture();
    for selector in [1, 2] {
        boundary
            .0
            .borrow_mut()
            .received
            .extend(frame(3, selector, b""));
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
    assert_eq!(
        boundary.0.borrow().halted,
        0,
        "STDIN_MUST_CLOSE_BEFORE_PROCESS_EOF"
    );
}

#[cfg(any(native_tty_duplex_probe, native_tty_mode_probe))]
#[test]
fn selected_duplex_attestation_checks_real_terminal_caller_generation_rights_and_source() {
    use serial_tty::{Caller, Mode, Rights, Terminal};
    let caller = Caller {
        identity: 77,
        generation: 1,
    };
    let rights = [
        if cfg!(native_tty_mode_probe) {
            Rights::READ.union(Rights::MODE)
        } else {
            Rights::READ
        },
        Rights::WRITE,
        Rights::WRITE,
    ];
    let (mut terminal, refs) = Terminal::admit(41, caller, rights, Mode::IMMEDIATE).unwrap();
    let sources = core::array::from_fn(|i| fd_startup::Source {
        reference: 0x7a000001 | (i as u32) << 16,
        selector: i as u32,
        rights: if i == 0 { 1 } else { 2 },
        bound: 16,
    });
    assert_eq!(
        native_app_runtime::validate_terminal_sources(&terminal, &refs, caller, &sources),
        Ok(())
    );
    for bad in [
        Caller {
            identity: 78,
            ..caller
        },
        Caller {
            generation: 2,
            ..caller
        },
    ] {
        assert!(
            native_app_runtime::validate_terminal_sources(&terminal, &refs, bad, &sources).is_err()
        );
    }
    let (other, _) = Terminal::admit(42, caller, rights, Mode::IMMEDIATE).unwrap();
    assert!(
        native_app_runtime::validate_terminal_sources(&other, &refs, caller, &sources).is_err()
    );
    for bad_rights in [
        [Rights::WRITE, Rights::WRITE, Rights::WRITE],
        [Rights::READ, Rights::READ, Rights::WRITE],
        [
            if cfg!(native_tty_mode_probe) {
                Rights::READ
            } else {
                Rights::READ.union(Rights::MODE)
            },
            Rights::WRITE,
            Rights::WRITE,
        ],
    ] {
        let (wrong, b) = Terminal::admit(41, caller, bad_rights, Mode::IMMEDIATE).unwrap();
        assert_eq!(
            native_app_runtime::validate_terminal_sources(&wrong, &b, caller, &sources),
            Err(-13),
            "ACTUAL_REFERENCE_RIGHTS_DENIED"
        );
    }
    let mut bad_sources = sources;
    bad_sources[1].reference ^= 1;
    assert_eq!(
        native_app_runtime::validate_terminal_sources(&terminal, &refs, caller, &bad_sources),
        Err(-13)
    );
    terminal.close(caller, refs.stdin).unwrap();
    assert!(
        native_app_runtime::validate_terminal_sources(&terminal, &refs, caller, &sources).is_err()
    );
}

#[cfg(native_tty_mode_probe)]
fn control_frame(op: u32, revision: u64, bits: u32, action: u32) -> [u8; 32] {
    let mut raw = [0; 32];
    raw[..4].copy_from_slice(&op.to_le_bytes());
    raw[4..8].copy_from_slice(&native_app_runtime::tty_mode::CONTROL.to_le_bytes());
    raw[8..12].copy_from_slice(&action.to_le_bytes());
    raw[16..24].copy_from_slice(&revision.to_le_bytes());
    if op == 0x11 {
        raw[24..28].copy_from_slice(&bits.to_le_bytes());
        raw[28] = 1;
    }
    raw
}
#[cfg(native_tty_mode_probe)]
fn mode_workload(boundary: &NativeBoundary, requests: &[[u8; 32]]) {
    let mut seen = boundary.0.borrow_mut();
    seen.mode_live = true;
    for request in requests {
        seen.received.extend(request);
    }
}
#[cfg(native_tty_mode_probe)]
#[test]
fn mode_busy_drain_rechecks_parks_serializes_and_restores_actual_cr() {
    let boundary = fixture();
    mode_workload(
        &boundary,
        &[
            frame(2, 1, b"before"),
            control_frame(0x10, 0, 0, 0),
            control_frame(0x11, 1, 1, 1),
            frame(2, 1, b"after"),
            frame(1, 0, &[0; 2]),
            control_frame(0x11, 2, 0, 1),
            frame(1, 0, &[0; 2]),
            frame(3, 0, b""),
            frame(3, 1, b""),
            frame(3, 2, b""),
        ],
    );
    {
        let mut seen = boundary.0.borrow_mut();
        seen.tx.extend([-11, -11, 0]);
        seen.input.extend(b"\rX\rY");
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
    let seen = boundary.0.borrow();
    assert_eq!(seen.mode_parks.len(), 1);
    assert_eq!(seen.tx_queries, 4);
    assert_eq!(&seen.tx_output_lengths[..3], &[6, 6, 6]);
    assert_eq!(seen.output, b"beforeafter");
    assert_eq!(
        &seen.transmitted[304 + 4 * 32 + 16..304 + 4 * 32 + 18],
        b"\nX"
    );
    assert_eq!(
        &seen.transmitted[304 + 6 * 32 + 16..304 + 6 * 32 + 18],
        b"\rY"
    );
    assert_eq!(runtime.snapshot().mode_cleanup, Some(0));
}
#[cfg(native_tty_mode_probe)]
#[test]
fn mode_busy_observe_ready_avoids_park_and_host_interrupt_has_no_commit() {
    for interrupt in [false, true] {
        let boundary = fixture();
        mode_workload(
            &boundary,
            &[
                control_frame(0x10, 0, 0, 0),
                control_frame(0x11, 1, 1, 1),
                control_frame(0x10, 0, 0, 0),
                frame(3, 0, b""),
                frame(3, 1, b""),
                frame(3, 2, b""),
            ],
        );
        boundary
            .0
            .borrow_mut()
            .tx
            .extend(if interrupt { [-4, 0] } else { [-11, 0] });
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(runtime.run(&mut [0; 4096]), Err(-5));
        let seen = boundary.0.borrow();
        assert!(seen.mode_parks.is_empty());
        let status = i32::from_le_bytes(seen.transmitted[336..340].try_into().unwrap());
        assert_eq!(status, if interrupt { -4 } else { 0 });
        assert_eq!(seen.transmitted[304 + 2 * 32 + 24], u8::from(!interrupt));
        assert_eq!(runtime.snapshot().mode_cleanup, Some(0));
    }
}
#[cfg(native_tty_mode_probe)]
#[test]
fn mode_deadline_equality_busy_expiry_and_peer_death_precede_commit_cleanup_is_local() {
    for case in 0..3 {
        let boundary = fixture();
        mode_workload(&boundary, &[control_frame(0x11, 1, 1, 1)]);
        {
            let mut seen = boundary.0.borrow_mut();
            if case == 0 {
                seen.mode_query_tick = Some(6000);
            } else {
                seen.tx_default = -11;
            }
            if case == 2 {
                seen.mode_die_on_park = true;
            }
        }
        let mut runtime = Runtime::new(boundary.clone()).unwrap();
        assert_eq!(
            runtime.run(&mut [0; 4096]),
            Err(if case == 2 { -125 } else { -110 })
        );
        assert_eq!(
            runtime.snapshot().mode_state,
            Some((false, 1)),
            "DRAIN_BEFORE_SINGLE_COMMIT"
        );
        assert!(
            runtime.snapshot().left > 900_000,
            "ORIGINAL_ABSOLUTE_DEADLINE_NOT_ATTEMPT_EXHAUSTION"
        );
        assert!(
            boundary
                .0
                .borrow()
                .mode_parks
                .iter()
                .all(|tick| *tick <= 6000),
            "ORIGINAL_ABSOLUTE_DEADLINE_NEVER_RENEWS"
        );
        let queries = boundary.0.borrow().tx_queries;
        assert_eq!(runtime.contain(), Err(-5));
        assert_eq!(runtime.snapshot().mode_cleanup, Some(0));
        assert_eq!(
            boundary.0.borrow().tx_queries,
            queries,
            "NO_CLEANUP_DRAIN_AFTER_STOP"
        );
    }
}
#[cfg(native_tty_mode_probe)]
#[test]
fn mode_commit_with_lost_reply_is_known_server_state_never_a_fabricated_eintr_reply() {
    let boundary = fixture();
    mode_workload(
        &boundary,
        &[control_frame(0x10, 0, 0, 0), control_frame(0x11, 1, 1, 0)],
    );
    {
        let mut seen = boundary.0.borrow_mut();
        seen.fail_write_at = 336;
        seen.fail_write_code = -4;
    }
    let mut runtime = Runtime::new(boundary.clone()).unwrap();
    assert_eq!(runtime.run(&mut [0; 4096]), Err(-4));
    assert_eq!(
        runtime.snapshot().mode_state,
        Some((true, 2)),
        "COMMIT_RETAINED_AFTER_UNKNOWN_REPLY"
    );
    assert_eq!(boundary.0.borrow().transmitted.len(), 336);
    assert_eq!(runtime.contain(), Err(-5));
    assert_eq!(runtime.snapshot().mode_cleanup, Some(0));
    assert_eq!(runtime.snapshot().mode_state, Some((false, 3)));
}
