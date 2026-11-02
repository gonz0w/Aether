// SPDX-License-Identifier: BSD-2-Clause
//! Loan/journal controls use the production namespace framing and Client.
use super::*;
use af07_transport::Kernel;
use filesystem_service::Channel;
use std::{cell::RefCell, collections::VecDeque, rc::Rc, vec::Vec};
#[derive(Default)]
struct State {
    input: VecDeque<u8>,
    closes: Vec<u64>,
    close_results: VecDeque<i64>,
    transfers: usize,
    tick: u64,
    terminal: VecDeque<Status>,
    parked: Vec<u64>,
    write_status: Option<i64>,
    read_status: Option<i64>,
    full: bool,
    service_pair: usize,
    process_pair: usize,
    startup: Vec<u8>,
    launch_namespace_unread: bool,
    stopped: Vec<u64>,
    reclaimed: Vec<u64>,
}
#[derive(Clone, Default)]
struct Mock(Rc<RefCell<State>>);
impl Kernel for Mock {
    fn transfer(&mut self, _endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        let mut state = self.0.borrow_mut();
        state.transfers += 1;
        if writing && state.full && _endpoint == 0xd1010102 {
            state.startup.extend_from_slice(bytes);
            return bytes.len() as i64;
        }
        if writing {
            return state.write_status.unwrap_or(bytes.len() as i64);
        }
        if let Some(status) = state.read_status {
            return status;
        }
        let count = bytes.len().min(state.input.len());
        for out in &mut bytes[..count] {
            *out = state.input.pop_front().unwrap();
        }
        count as i64
    }
    fn wait(&mut self, _: u64) -> i64 {
        0
    }
    fn close(&mut self, cap: u64) -> i64 {
        let mut s = self.0.borrow_mut();
        s.closes.push(cap);
        s.close_results.pop_front().unwrap_or(0)
    }
}
impl Control for Mock {
    fn ctl(&mut self, op: u64, cap: u64, _: u64) -> Status {
        let mut state = self.0.borrow_mut();
        if state.full {
            match op {
                0x24000 => {
                    let index = if cap == 0xd002 {
                        let index = state.service_pair;
                        state.service_pair += 1;
                        10 + index
                    } else {
                        let index = state.process_pair;
                        state.process_pair += 1;
                        index
                    };
                    return (
                        (0xd1000101u64 | (index as u64) << 16) as i64,
                        0xd1000102 | (index as u64) << 16,
                        0,
                    );
                }
                0x20001 => {
                    return if state.reclaimed.contains(&cap) {
                        (-9, 0, 0)
                    } else if state.stopped.contains(&cap) {
                        (126, 0, 3)
                    } else {
                        (0, 1, 0)
                    };
                }
                0x20007 => {
                    state.stopped.push(cap);
                    return (0, 0, 0);
                }
                0x20002 => {
                    state.reclaimed.push(cap);
                    return (0, 0, 0);
                }
                _ => {}
            }
        }
        match op {
            0x2a000 => (0, 4, state.tick),
            0x20001 => state.terminal.pop_front().unwrap_or((1, 1, 1)),
            _ => (0, 0, 0),
        }
    }
    fn park_events(&mut self, _: u64, deadline: Option<Deadline>) -> Status {
        self.0.borrow_mut().parked.push(deadline.unwrap().get());
        (0, 0, 0)
    }
    fn engine(&mut self, _: u64, _: u64) -> i64 {
        if self.0.borrow().full {
            0xb0000101
        } else {
            -38
        }
    }
    fn delegate(&mut self, _: u64, _: &[u64; 3]) -> i64 {
        if self.0.borrow().full { 0 } else { -38 }
    }
    fn launch(&mut self, _: &[u8; 272], _: u64, _: u64) -> i64 {
        -38
    }
    fn copy(&mut self, _: u64, _: u32, _: u64, _: u64, _: u64) -> i64 {
        -38
    }
    fn serial(&mut self, _: bool, _: &mut [u8]) -> i64 {
        -38
    }
    fn exec(&mut self, _: u64, _: u64, _: &[u8; 272]) -> i64 {
        -38
    }
    fn receipt(&mut self, _: u64) -> Status {
        (-38, 0, 0)
    }
    fn publish(&mut self, _: u64, _: u64) -> i64 {
        -38
    }
}
impl AppControl for Mock {
    fn launch_app(&mut self, record: &[u8; 320], _: u64, _: u64) -> i64 {
        let mut s = self.0.borrow_mut();
        if !s.full {
            return -38;
        }
        assert_eq!(&record[..8], b"AENAP002");
        s.launch_namespace_unread = s.transfers == 0;
        0xb0000102
    }
}
fn bound() -> Bound {
    Bound {
        left: ATTEMPTS - RESERVED,
        reserved: RESERVED,
        deadline: Deadline::after(0, WRITER_DEADLINE_TICK).unwrap(),
        sequence: 0,
        last_tick: 0,
        failed: 0,
    }
}
fn ends() -> [End; 8] {
    let mut ends = [End::default(); 8];
    for (i, cap) in [41, 42].into_iter().enumerate() {
        ends[i] = End {
            cap,
            owned: true,
            ..End::default()
        };
    }
    ends
}
fn binding() -> filesystem_readonly::Binding {
    filesystem_readonly::Binding {
        slot: 1,
        epoch: 1,
        handle: 0xb0000102,
        generation: 31,
    }
}
fn greetings() -> Vec<u8> {
    let mut bytes = Vec::new();
    for token in [1u64, 2] {
        let mut frame = [0; 64];
        frame[..8].copy_from_slice(b"AFSRPC09");
        frame[16..24].copy_from_slice(&1u64.to_le_bytes());
        frame[24..32].copy_from_slice(&token.to_le_bytes());
        frame[32..40].copy_from_slice(&1u64.to_le_bytes());
        bytes.extend_from_slice(&frame);
    }
    bytes
}
#[test]
fn zsh_unarmed_namespace_fails_without_native_call() {
    let kernel = Mock::default();
    let mut io = Namespace::new(kernel.clone(), 41, 42);
    assert_eq!(io.receive(&mut [0; 64]), Err(-9));
    assert_eq!(io.close(), [-9; 2]);
    assert_eq!(kernel.0.borrow().transfers, 0);
    assert!(kernel.0.borrow().closes.is_empty());
}
#[test]
fn zsh_constructor_greeting_failures_preserve_each_raw_close_once() {
    for prefix in [0, 64, 80, 128] {
        for results in [[0, 0], [-9, 0], [0, -5], [-9, -5]] {
            let kernel = Mock::default();
            let mut input = greetings();
            input.truncate(prefix);
            if prefix == 128 {
                input[64 + 48] = 1;
            }
            kernel.0.borrow_mut().input = input.into();
            kernel.0.borrow_mut().close_results = results.into();
            let mut bound = bound();
            bound.spend().unwrap();
            bound.spend().unwrap();
            let mut ends = ends();
            let mut requests = 0;
            let mut prepaid = [41, 42];
            let mut io = Namespace::new(kernel.clone(), 41, 42);
            unsafe { io.arm(&mut bound, &mut ends, &mut requests, &mut prepaid) }.unwrap();
            let mut slot = MaybeUninit::uninit();
            let error = filesystem_readonly::Files::connect_in_place(&mut slot, io, 1, binding())
                .err()
                .unwrap();
            assert_eq!(error.cleanup, results);
            assert_eq!(kernel.0.borrow().closes, [41, 42]);
            assert_eq!(prepaid, [0; 2]);
            assert_eq!(bound.reserved, 12);
            assert!(ends[..2].iter().all(|end| end.attempted));
            assert_eq!([ends[0].status, ends[1].status], results);
        }
    }
}
#[test]
fn zsh_successful_constructor_disarm_midoperation_failure_and_abort() {
    let kernel = Mock::default();
    kernel.0.borrow_mut().input = greetings().into();
    let mut bound = bound();
    bound.spend().unwrap();
    bound.spend().unwrap();
    let mut ends = ends();
    let mut requests = 0;
    let mut prepaid = [41, 42];
    let mut io = Namespace::new(kernel.clone(), 41, 42);
    unsafe { io.arm(&mut bound, &mut ends, &mut requests, &mut prepaid) }.unwrap();
    let mut slot = MaybeUninit::uninit();
    let files = filesystem_readonly::Files::connect_in_place(&mut slot, io, 1, binding())
        .ok()
        .unwrap();
    files
        .configure(|io| {
            io.disarm();
            Ok(())
        })
        .unwrap();
    assert_eq!(requests, 0);
    assert!(!ends[0].attempted);
    kernel.0.borrow_mut().write_status = Some(-32);
    files
        .configure(|io| unsafe { io.arm(&mut bound, &mut ends, &mut requests, &mut prepaid) })
        .unwrap();
    assert!(files.provision(b"asset", &mut [0; 4096]).is_err());
    assert_eq!(files.cleanup(), Some([0; 2]));
    assert_eq!(kernel.0.borrow().closes, [41, 42]);
    assert_eq!(requests, 1);
    assert_eq!(files.abort(), [0; 2]);
    assert_eq!(kernel.0.borrow().closes, [41, 42]);
    unsafe {
        slot.assume_init_drop();
    }
}
#[test]
fn zsh_prepaid_closes_survive_exhausted_failed_ordinary_bound() {
    for failed in [0, -110] {
        let kernel = Mock::default();
        let mut bound = bound();
        bound.spend().unwrap();
        bound.spend().unwrap();
        bound.left = 0;
        bound.failed = failed;
        let mut ends = ends();
        let mut requests = 0;
        let mut prepaid = [41, 42];
        let mut io = Namespace::new(kernel.clone(), 41, 42);
        unsafe { io.arm(&mut bound, &mut ends, &mut requests, &mut prepaid) }.unwrap();
        let mut slot = MaybeUninit::uninit();
        let error = filesystem_readonly::Files::connect_in_place(&mut slot, io, 1, binding())
            .err()
            .unwrap();
        assert_eq!(error.cleanup, [0; 2]);
        assert_eq!(bound.left, 0);
        assert_eq!(bound.reserved, 12);
        assert_eq!(kernel.0.borrow().closes, [41, 42]);
        assert_eq!(prepaid, [0; 2]);
    }
}
#[test]
fn zsh_count_complete_requests_and_preserve_one_disconnect() {
    let kernel = Mock::default();
    let mut bound = bound();
    let mut ends = ends();
    let mut requests = 94;
    let mut prepaid = [41, 42];
    let mut io = Namespace::new(kernel.clone(), 41, 42);
    unsafe { io.arm(&mut bound, &mut ends, &mut requests, &mut prepaid) }.unwrap();
    let mut frame = [0; 64];
    frame[..8].copy_from_slice(b"AFSRPC09");
    frame[8..16].copy_from_slice(&1u64.to_le_bytes());
    frame[40..48].copy_from_slice(&21u64.to_le_bytes());
    assert_eq!(io.send(&frame), Ok(()));
    assert_eq!(io.send(&[0; 64]), Ok(()));
    frame[8..16].copy_from_slice(&6u64.to_le_bytes());
    assert_eq!(io.send(&frame), Err(-28));
    frame[8..16].copy_from_slice(&4u64.to_le_bytes());
    assert_eq!(io.send(&frame), Ok(()));
    assert_eq!(io.send(&frame), Err(-28));
    io.disarm();
    assert_eq!(requests, 96);
    assert!(kernel.0.borrow().closes.is_empty());
}
#[test]
fn zsh_disconnect_verifies_engine_terminal_and_actual_quiescence() {
    for defect in 0..5 {
        let kernel = Mock::default();
        {
            let mut s = kernel.0.borrow_mut();
            s.terminal = [(0, 1, 0), (1, 1, 1)].into();
            s.read_status = Some(if defect == 1 { 1 } else { 0 });
            s.write_status = Some(if defect == 2 { 0 } else { -32 });
            if defect == 3 {
                s.terminal = [(2, 1, 1)].into();
            }
            if defect == 4 {
                s.tick = 6000;
            }
        }
        let mut bound = bound();
        let mut ends = ends();
        let mut requests = 12;
        let mut prepaid = [41, 42];
        let mut io = Namespace::new(kernel.clone(), 41, 42);
        unsafe { io.arm(&mut bound, &mut ends, &mut requests, &mut prepaid) }.unwrap();
        let result = io.verify_disconnect(0xb0000101);
        if defect == 0 {
            assert_eq!(result, Ok(()));
        } else {
            assert!(result.is_err());
        }
        assert_eq!(io.close(), [0; 2]);
        assert_eq!(kernel.0.borrow().closes, [41, 42]);
        assert_eq!(requests, 12);
        assert!(kernel.0.borrow().parked.iter().all(|d| *d == 6000));
    }
}
#[test]
fn zsh_selected_startup_launch_and_runtime_layout() {
    let mut raw = [0; 320];
    encode_launch(&mut raw, 0xb0000101, 41, 42).unwrap();
    assert_eq!(&raw[..8], b"AENAP002");
    assert_eq!(&raw[16..24], &4u64.to_le_bytes());
    assert_eq!(&raw[24..32], &4u64.to_le_bytes());
    for (i, text) in [
        b"zsh".as_slice(),
        b"-f",
        b"-i",
        b"+m",
        b"TERM=vt100",
        b"LC_ALL=C",
        b"HOME=/",
        b"PWD=/",
    ]
    .iter()
    .enumerate()
    {
        assert_eq!(&raw[32 + i * 32..][..text.len()], *text);
        assert_eq!(raw[32 + i * 32 + text.len()], 0);
    }
    let mut bindings = [Binding::default(); 16];
    let mut sources = [Source::default(); 7];
    for i in 0..3 {
        bindings[i] = Binding {
            kind: 4,
            selector: i as u8,
            cloexec: 0,
        };
        sources[i] = console(i as u32);
    }
    let plan = Plan {
        identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
        shell: 1,
        parent: 7,
        generation: 31,
        bindings,
        sources,
        history: [0; 2],
    };
    let mut bytes = [0xa5; fd_startup::BYTES];
    fd_startup::encode(&plan, &mut bytes).unwrap();
    assert_eq!(bytes.len(), 336);
    assert_eq!(&bytes[..8], b"AEFDB008");
    assert_eq!(&bytes[48..56], b"AEFDT008");
    assert_eq!(&bytes[296..300], &[0; 4]);
    for offset in [304, 308, 312, 316] {
        assert_eq!(&bytes[offset..offset + 4], &1000u32.to_le_bytes());
    }
    assert_eq!(&bytes[320..324], &1u32.to_le_bytes());
    assert_eq!(&bytes[324..], &[0; 12]);
    assert!(core::mem::size_of::<Runtime<Mock>>() <= 4096);
}

fn provisioning_replies() -> Vec<u8> {
    let mut bytes = greetings();
    for frame in bytes.as_chunks_mut::<64>().0 {
        frame[16..24].copy_from_slice(&0xd10a0101u64.to_le_bytes());
    }
    let frame = |token: u64, kind: u64, size: u64| {
        let mut f = [0; 64];
        f[..8].copy_from_slice(b"AFSRPC09");
        f[16..24].copy_from_slice(&0xd10a0101u64.to_le_bytes());
        f[24..32].copy_from_slice(&token.to_le_bytes());
        f[32..40].copy_from_slice(&kind.to_le_bytes());
        f[40..48].copy_from_slice(&size.to_le_bytes());
        f
    };
    let mutation = |size: u64| {
        let mut f = frame(0, 1, size);
        f[48..56].copy_from_slice(&2u64.to_le_bytes());
        f
    };
    for f in [
        mutation(0),
        frame(3, 1, 0),
        mutation(0),
        frame(4, 1, 0),
        mutation(0),
        frame(5, 2, 0),
        mutation(TERMINFO.len() as u64),
        frame(5, 2, TERMINFO.len() as u64),
        frame(0, 0, TERMINFO.len() as u64),
    ] {
        bytes.extend_from_slice(&f);
    }
    bytes.extend_from_slice(TERMINFO);
    bytes.resize(bytes.len().div_ceil(64) * 64, 0);
    for f in [frame(0, 0, 0), frame(0, 0, 0), frame(0, 0, 0)] {
        bytes.extend_from_slice(&f);
    }
    bytes
}
#[test]
fn zsh_runtime_retains_namespace_and_publishes_startup_only_after_readback() {
    let kernel = Mock::default();
    {
        let mut s = kernel.0.borrow_mut();
        s.full = true;
        s.input = provisioning_replies().into();
    }
    let mut runtime = Runtime::new(kernel.clone()).unwrap();
    runtime.provision(&mut [0; 4096]).unwrap();
    assert!(kernel.0.borrow().launch_namespace_unread);
    assert_eq!(kernel.0.borrow().startup.len(), 336);
    assert_eq!(&kernel.0.borrow().startup[..8], b"AEFDB008");
    assert_eq!(runtime.snapshot().filesystem_requests, 12);
    assert_eq!(runtime.namespace_prepaid, [0xd10b0101, 0xd10a0102]);
    for cap in [0xd10b0101, 0xd10a0102] {
        assert!(
            runtime
                .snapshot()
                .ends
                .iter()
                .any(|end| end.cap == cap && end.owned && !end.attempted)
        );
    }
    runtime.contain().unwrap_err();
    assert_eq!(runtime.snapshot().reserved, 0);
    assert_eq!(kernel.0.borrow().stopped, [0xb0000102, 0xb0000101]);
    assert_eq!(kernel.0.borrow().reclaimed, [0xb0000102, 0xb0000101]);
    for cap in [0xd10b0101, 0xd10a0102] {
        assert_eq!(
            kernel
                .0
                .borrow()
                .closes
                .iter()
                .filter(|seen| **seen == cap)
                .count(),
            1
        );
    }
}
#[test]
fn zsh_runtime_provisioning_failure_contains_admitted_unready_app() {
    for input in [Vec::new(), provisioning_replies()[..128].to_vec()] {
        let kernel = Mock::default();
        {
            let mut s = kernel.0.borrow_mut();
            s.full = true;
            s.input = input.into();
        }
        let mut runtime = Runtime::new(kernel.clone()).unwrap();
        assert!(runtime.provision(&mut [0; 4096]).is_err());
        assert!(kernel.0.borrow().launch_namespace_unread);
        assert!(kernel.0.borrow().startup.is_empty());
        runtime.contain().unwrap_err();
        assert_eq!(runtime.snapshot().reserved, 0);
        assert_eq!(kernel.0.borrow().stopped, [0xb0000102, 0xb0000101]);
        assert_eq!(kernel.0.borrow().reclaimed, [0xb0000102, 0xb0000101]);
        assert_eq!(runtime.namespace_prepaid, [0; 2]);
    }
}

#[test]
fn zsh_runtime_all_twelve_provisioning_receipt_failures_keep_false_ready_and_close_once() {
    let data_start = 11 * 64;
    let data_end = data_start + TERMINFO.len().div_ceil(64) * 64;
    for request in 0..12 {
        let kernel = Mock::default();
        let mut input = provisioning_replies();
        let offset = if request < 9 {
            (2 + request) * 64
        } else {
            data_end + (request - 9) * 64
        };
        input[offset..offset + 64].fill(0);
        input[offset..offset + 8].copy_from_slice(b"AFSRPC09");
        input[offset + 8..offset + 16].copy_from_slice(&(-5i64).to_le_bytes());
        input[offset + 16..offset + 24].copy_from_slice(&0xd10a0101u64.to_le_bytes());
        {
            let mut s = kernel.0.borrow_mut();
            s.full = true;
            s.input = input.into();
        }
        let mut runtime = Runtime::new(kernel.clone()).unwrap();
        assert!(
            runtime.provision(&mut [0; 4096]).is_err(),
            "PROVISION_RECEIPT_{request}"
        );
        assert!(kernel.0.borrow().startup.is_empty());
        assert_eq!(runtime.filesystem_requests, request as u32 + 1);
        if [0, 2, 4, 6].contains(&request) {
            // SAFETY: both greetings succeeded before any failed operation.
            let failure = unsafe { runtime.files.assume_init_ref() }
                .mutation_failure()
                .unwrap();
            assert_eq!(failure.error, filesystem_readonly::Error::Remote(-5));
        }
        runtime.contain().unwrap_err();
        for cap in [0xd10b0101, 0xd10a0102] {
            assert_eq!(
                kernel
                    .0
                    .borrow()
                    .closes
                    .iter()
                    .filter(|v| **v == cap)
                    .count(),
                1
            );
        }
        assert_eq!(runtime.bound.reserved, 0);
    }
}

#[test]
fn zsh_in_place_constructor_matches_new_and_performs_no_native_effects() {
    let kernel = Mock::default();
    let old = Runtime::new(kernel.clone()).unwrap();
    let mut slot = MaybeUninit::uninit();
    let address = slot.as_ptr();
    let runtime = Runtime::initialize_in_place(&mut slot, kernel.clone()).unwrap();
    assert!(core::ptr::eq(address, runtime));
    assert_eq!(runtime.snapshot(), old.snapshot());
    assert!(!runtime.started && !runtime.files_live);
    assert_eq!(runtime.file_binding, None);
    assert_eq!(runtime.file_header, [0; 64]);
    assert_eq!(runtime.namespace_prepaid, [0; 2]);
    assert_eq!(runtime.request, [0; 32]);
    assert_eq!(runtime.reply, [0; 32]);
    assert_eq!(runtime.closed, [false; 3]);
    assert!(
        runtime.endpoints.is_none()
            && runtime.identity.is_none()
            && runtime.tty.is_none()
            && runtime.mode.is_none()
    );
    assert_eq!(runtime.streams.console_closed(0), Ok(()));
    assert_eq!(runtime.streams.console_closed(0), Err(-9));
    assert!(kernel.0.borrow().closes.is_empty());
    assert_eq!(kernel.0.borrow().transfers, 0);
    // SAFETY: successful constructor initialized every Runtime field, files is
    // inert MaybeUninit and no native resources were admitted by this test.
    unsafe {
        slot.assume_init_drop();
    }
}
#[test]
fn zsh_in_place_runtime_uses_actual_engine_endpoint_epoch_and_same_cleanup() {
    let kernel = Mock::default();
    {
        let mut s = kernel.0.borrow_mut();
        s.full = true;
        s.input = provisioning_replies().into();
    }
    let mut slot = MaybeUninit::uninit();
    let runtime = Runtime::initialize_in_place(&mut slot, kernel.clone()).unwrap();
    runtime.provision(&mut [0; 4096]).unwrap();
    assert!(kernel.0.borrow().launch_namespace_unread);
    assert_eq!(runtime.filesystem_requests, 12);
    assert_eq!(kernel.0.borrow().startup.len(), 336);
    let namespace_epoch = 0xd10a0101u64;
    let mut observation = [0; 64];
    observation[..8].copy_from_slice(b"AFSRPC09");
    observation[16..24].copy_from_slice(&namespace_epoch.to_le_bytes());
    observation[24..32].copy_from_slice(&3u64.to_le_bytes());
    observation[32..40].copy_from_slice(&1u64.to_le_bytes());
    kernel.0.borrow_mut().input.extend(observation);
    let binding = runtime.file_binding.unwrap();
    let actual = runtime
        .with_files(|files| {
            let mut header = [0; 64];
            header[..8].copy_from_slice(filesystem_readonly::MAGIC);
            for (index, value) in [
                (1, 10u64),
                (2, binding.generation),
                (3, 1),
                (5, filesystem_readonly::DIRECTORY.len() as u64),
            ] {
                header[index * 8..index * 8 + 8].copy_from_slice(&value.to_le_bytes());
            }
            let mut workspace = [0; 4096];
            workspace[..filesystem_readonly::DIRECTORY.len()]
                .copy_from_slice(filesystem_readonly::DIRECTORY);
            let mut reply = files.prepare(binding, &header, 64, &mut workspace)?;
            let epoch = u64::from_le_bytes(reply.body_mut()[24..32].try_into().unwrap());
            reply.delivered();
            Ok(epoch)
        })
        .unwrap();
    assert_eq!(actual, namespace_epoch);
    assert_eq!(runtime.filesystem_requests, 13);
    runtime.contain().unwrap_err();
    assert_eq!(runtime.bound.reserved, 0);
    for cap in [0xd10b0101, 0xd10a0102] {
        assert_eq!(
            kernel
                .0
                .borrow()
                .closes
                .iter()
                .filter(|seen| **seen == cap)
                .count(),
            1
        );
    }
    // SAFETY: final slot was initialized once; containment consumed all native
    // close obligations and nested Files is intentionally MaybeUninit storage.
    unsafe {
        slot.assume_init_drop();
    }
}
