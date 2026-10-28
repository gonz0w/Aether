// SPDX-License-Identifier: BSD-2-Clause
//! Actual AF09 client/service and typed C provider, separate hostile-wire cases.
use super::*;
use filesystem_service::Message;
#[cfg(test)]
use filesystem_service::{message, put};
#[cfg(test)]
use std::vec;
use std::{collections::VecDeque, vec::Vec};

pub mod fixture {
    use super::*;
    use std::{ptr::NonNull, sync::mpsc, thread, time::Duration};
    unsafe extern "C" {
        fn mixed_reset(mode: u32);
        fn mixed_count(index: u32) -> u32;
    }
    pub struct Wire {
        replies: VecDeque<Result<Message, i64>>,
        receive_bytes: VecDeque<u8>,
        send_bytes: Vec<u8>,
        pub sent: Vec<Message>,
        pub closes: usize,
        pub close_values: [i64; 2],
        live: Option<(Option<mpsc::Sender<Message>>, mpsc::Receiver<Message>)>,
    }
    #[cfg(test)]
    pub fn greeting(token: u64) -> Message {
        let mut frame = message(91, 0);
        put(&mut frame, 3, token);
        put(&mut frame, 4, 1);
        put(&mut frame, 5, 2);
        frame
    }
    #[cfg(test)]
    pub fn reply(code: i64, txg: u64, state: u64) -> Message {
        let mut frame = message(91, code as u64);
        put(&mut frame, 4, txg);
        put(&mut frame, 6, state);
        frame
    }
    impl Wire {
        pub fn scripted(replies: Vec<Result<Message, i64>>) -> Self {
            Self {
                replies: replies.into(),
                receive_bytes: VecDeque::new(),
                send_bytes: Vec::new(),
                sent: Vec::new(),
                closes: 0,
                close_values: [0, 0],
                live: None,
            }
        }
        #[cfg(test)]
        pub fn normal(mutation: Result<Message, i64>) -> Self {
            Self::scripted(vec![
                Ok(greeting(1)),
                Ok(greeting(2)),
                mutation,
                Ok(message(91, 0)),
            ])
        }
        pub fn bootstrap(&mut self) -> Bootstrap {
            Bootstrap {
                io: Callbacks {
                    state: ptr::from_mut(self).cast(),
                    transfer: Some(transfer),
                    wait: Some(wait),
                    close: Some(close),
                },
                epoch: 91,
                parent_prefix: b"/work/".as_ptr(),
                parent_prefix_length: 6,
            }
        }
    }
    unsafe extern "C" fn transfer(
        state: *mut c_void,
        writing: u32,
        pointer: *mut u8,
        length: usize,
    ) -> i64 {
        if length == 0 || length > 16 || writing > 1 {
            return -5;
        }
        // SAFETY: adapter owns a bounded synchronous initialized chunk. State is
        // the exclusive caller-owned Wire and never reenters the adapter.
        let wire = unsafe { &mut *state.cast::<Wire>() };
        let count = length.min(7);
        if writing == 1 {
            let bytes = unsafe { slice::from_raw_parts(pointer, count) };
            wire.send_bytes.extend_from_slice(bytes);
            if wire.send_bytes.len() == 64 {
                let mut frame = [0; 64];
                frame.copy_from_slice(&wire.send_bytes);
                wire.send_bytes.clear();
                wire.sent.push(frame);
                if let Some((sender, _)) = &wire.live
                    && sender
                        .as_ref()
                        .is_none_or(|sender| sender.send(frame).is_err())
                {
                    return -32;
                }
            }
        } else {
            if wire.receive_bytes.is_empty() {
                let next = if let Some((_, receiver)) = &wire.live {
                    receiver
                        .recv_timeout(Duration::from_secs(2))
                        .map_err(|_| -32)
                } else {
                    wire.replies.pop_front().unwrap_or(Err(-32))
                };
                match next {
                    Ok(frame) => wire.receive_bytes.extend(frame),
                    Err(error) => return error,
                }
            }
            let count = count.min(wire.receive_bytes.len());
            let bytes = unsafe { slice::from_raw_parts_mut(pointer, count) };
            for byte in bytes {
                *byte = wire.receive_bytes.pop_front().unwrap_or(0);
            }
            return count as i64;
        }
        count as i64
    }
    unsafe extern "C" fn wait(_state: *mut c_void, _writing: u32) -> i64 {
        0
    }
    unsafe extern "C" fn close(state: *mut c_void, output: *mut i64) {
        // SAFETY: actual adapter supplies exactly two initialized output cells.
        let wire = unsafe { &mut *state.cast::<Wire>() };
        wire.closes += 1;
        if let Some((sender, _)) = &mut wire.live {
            sender.take();
        }
        unsafe {
            output.write(wire.close_values[0]);
            output.add(1).write(wire.close_values[1]);
        }
    }
    struct Server {
        send: Option<mpsc::Sender<Message>>,
        receive: mpsc::Receiver<Message>,
    }
    impl filesystem_service::Channel for Server {
        fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
            *out = self
                .receive
                .recv_timeout(Duration::from_secs(2))
                .map_err(|_| -32)?;
            Ok(())
        }
        fn send(&mut self, frame: &Message) -> Result<(), i64> {
            self.send.as_ref().ok_or(-32)?.send(*frame).map_err(|_| -32)
        }
        fn close(&mut self) -> [i64; 2] {
            self.send.take();
            [0, 0]
        }
    }
    pub struct Actual {
        pub wire: Wire,
        join: thread::JoinHandle<filesystem_service::Report>,
        pub baseline_attempts: u32,
    }
    impl Actual {
        #[cfg(test)]
        pub fn start(collision: bool) -> Self {
            Self::start_named(if collision {
                Some(b"dir".to_vec())
            } else {
                None
            })
        }
        pub fn start_named(collision: Option<Vec<u8>>) -> Self {
            let (client_send, server_receive) = mpsc::channel();
            let (server_send, client_receive) = mpsc::channel();
            let server = Server {
                send: Some(server_send),
                receive: server_receive,
            };
            let (ready_send, ready_receive) = mpsc::channel();
            // Host tests are serial; each executable owns the typed fixture.
            let join = thread::spawn(move || {
                unsafe { mixed_reset(100) };
                let mut marker = 0u64;
                // SAFETY: exclusive typed host SPA/context, no disk/native claim.
                let mut spa =
                    unsafe { filesystem_bridge::Spa::from_raw(NonNull::from(&mut marker).cast()) };
                let mut owner = filesystem_policy::Owner::new(
                    spa.open(c"testpool_zstd/x86_64").unwrap(),
                    filesystem_bridge::RuntimeUtc,
                    91,
                )
                .unwrap()
                .with_namespace_identity(filesystem_policy::Identity::new(1000, 1000).unwrap());
                let source = owner.attach(7, filesystem_policy::Rights::ALL).unwrap();
                owner
                    .namespace(
                        7,
                        source.session,
                        source.root.handle,
                        filesystem_policy::Mutation::MakeDirectory(b"home"),
                    )
                    .unwrap();
                let home = owner
                    .lookup(
                        7,
                        source.session,
                        source.root.handle,
                        b"home",
                        filesystem_policy::Rights::ALL,
                    )
                    .unwrap();
                if let Some(name) = collision {
                    owner
                        .namespace(
                            7,
                            source.session,
                            home.handle,
                            filesystem_policy::Mutation::MakeDirectory(&name),
                        )
                        .unwrap();
                }
                let baseline = unsafe { mixed_count(9) };
                let _ = ready_send.send(baseline);
                filesystem_service::run_home(owner, server, 7, source.session, home.handle, 8, 91)
            });
            let mut wire = Wire::scripted(Vec::new());
            wire.live = Some((Some(client_send), client_receive));
            let baseline_attempts = ready_receive
                .recv_timeout(Duration::from_secs(2))
                .unwrap_or(u32::MAX);
            Self {
                wire,
                join,
                baseline_attempts,
            }
        }
        #[cfg(test)]
        pub fn finish(self) -> (filesystem_service::Report, u32, u32, u32) {
            self.try_finish().unwrap()
        }
        pub fn try_finish(self) -> Result<(filesystem_service::Report, u32, u32, u32), ()> {
            let report = self.join.join().map_err(|_| ())?;
            // SAFETY: service finished and its sole typed C context was dropped.
            unsafe { Ok((report, mixed_count(9), mixed_count(0), mixed_count(1))) }
        }
    }
}

#[cfg(test)]
#[derive(Clone)]
enum Step {
    Mkdir(&'static [u8], u32),
    Finish,
    Nested,
}
#[cfg(test)]
struct Application {
    steps: Vec<Step>,
    returns: Vec<i32>,
    mutations: Vec<Mutation>,
    finishes: Vec<Finish>,
    nested: Option<Bootstrap>,
    nested_result: Option<Run>,
    status: i32,
}
#[cfg(test)]
impl Application {
    fn new(steps: Vec<Step>) -> Self {
        Self {
            steps,
            returns: vec![],
            mutations: vec![],
            finishes: vec![],
            nested: None,
            nested_result: None,
            status: 0,
        }
    }
}
#[cfg(test)]
unsafe extern "C" fn entry(context: *mut Namespace, application: *mut c_void) -> i32 {
    // SAFETY: this callback receives stable disjoint Application storage. Calls
    // are sequential from entry, never from a transport callback or expired data.
    let app = unsafe { &mut *application.cast::<Application>() };
    for step in app.steps.clone() {
        match step {
            Step::Mkdir(name, mode) => {
                let mut out = Mutation::default();
                let result =
                    unsafe { amk_mkdir(context, name.as_ptr(), name.len(), mode, &mut out) };
                app.returns.push(result);
                app.mutations.push(out);
            }
            Step::Finish => {
                let mut out = Finish::default();
                let result = unsafe { amk_finish(context, &mut out) };
                app.returns.push(result);
                app.finishes.push(out);
            }
            Step::Nested => {
                if let Some(bootstrap) = app.nested {
                    let mut out = Run::default();
                    let result = unsafe {
                        amk_with_namespace(&bootstrap, Some(empty_entry), ptr::null_mut(), &mut out)
                    };
                    app.returns.push(result);
                    app.nested_result = Some(out);
                }
            }
        }
    }
    app.status
}
#[cfg(test)]
unsafe extern "C" fn empty_entry(_context: *mut Namespace, _application: *mut c_void) -> i32 {
    0
}
#[cfg(test)]
fn run(wire: &mut fixture::Wire, app: &mut Application) -> (i32, Run) {
    let bootstrap = wire.bootstrap();
    let mut out = Run::default();
    // SAFETY: serial callback scope; valid disjoint Wire/Application/report.
    let result =
        unsafe { amk_with_namespace(&bootstrap, Some(entry), ptr::from_mut(app).cast(), &mut out) };
    (result, out)
}

#[test]
fn layouts_and_default_records_are_exact() {
    assert_eq!(
        (
            mem::size_of::<Mutation>(),
            mem::size_of::<Admission>(),
            mem::size_of::<Finish>(),
            mem::size_of::<Run>(),
            mem::size_of::<Bootstrap>()
        ),
        (40, 24, 48, 128, 56),
        "AMK_LAYOUT"
    );
    assert_eq!(
        (Mutation::default().outcome, Mutation::default().progress),
        (0, 4),
        "AMK_LAYOUT"
    );
    for (error, kind, errno) in [
        (Error::Invalid, 1, 22),
        (Error::Closed, 2, 9),
        (Error::Full, 3, 24),
        (Error::Protocol, 4, 5),
        (Error::Remote(-17), 6, 17),
        (Error::Transport(i64::MIN), 5, 5),
    ] {
        let p = project(error);
        assert_eq!((p.kind, p.errno), (kind, errno), "AMK_LAYOUT");
    }
}
#[test]
fn invalid_bootstrap_never_accepts_endpoints() {
    let mut wire = fixture::Wire::normal(Ok(fixture::reply(0, 7, 2)));
    let base = wire.bootstrap();
    for bootstrap in [
        Bootstrap { epoch: 0, ..base },
        Bootstrap {
            parent_prefix_length: 26,
            ..base
        },
        Bootstrap {
            io: Callbacks {
                close: None,
                ..base.io
            },
            ..base
        },
        Bootstrap {
            parent_prefix: b"wrong".as_ptr(),
            parent_prefix_length: 5,
            ..base
        },
    ] {
        let mut out = Run::default();
        let result =
            unsafe { amk_with_namespace(&bootstrap, Some(empty_entry), ptr::null_mut(), &mut out) };
        assert_eq!(
            (
                result,
                out.admission.phase,
                out.admission.endpoints_accepted,
                wire.closes
            ),
            (-22, 1, 0, 0),
            "AMK_ADMISSION"
        );
    }
    assert!(wire.sent.is_empty(), "AMK_ADMISSION");
}
#[test]
fn actual_client_service_and_typed_c_mkdir_complete() {
    let mut actual = fixture::Actual::start(false);
    assert_eq!(actual.baseline_attempts, 1, "AMK_ACTUAL_MKDIR");
    let mut app = Application::new(vec![Step::Mkdir(b"dir", 0o700), Step::Finish]);
    let (status, out) = run(&mut actual.wire, &mut app);
    assert_eq!(
        (
            status,
            out.final_status,
            app.returns.clone(),
            actual.wire.closes
        ),
        (0, 0, vec![0, 0], 1),
        "AMK_ACTUAL_MKDIR"
    );
    assert_eq!(
        (out.mutation.outcome, out.mutation.progress),
        (3, 2),
        "AMK_ACTUAL_MKDIR"
    );
    assert!(out.mutation.txg > 0, "AMK_ACTUAL_MKDIR");
    let (report, created, opens, closes) = actual.finish();
    assert_eq!(
        (report.stop, created, opens == closes),
        (filesystem_service::Stop::Disconnected, 2, true),
        "AMK_ACTUAL_MKDIR"
    );
}
#[test]
fn one_collision_retires_without_replay() {
    let mut actual = fixture::Actual::start(true);
    assert_eq!(actual.baseline_attempts, 2, "AMK_COLLISION");
    let mut app = Application::new(vec![
        Step::Mkdir(b"dir", 0o700),
        Step::Mkdir(b"other", 0o700),
        Step::Finish,
    ]);
    let (_, out) = run(&mut actual.wire, &mut app);
    assert_eq!(app.returns, vec![-17, -9, 0], "AMK_COLLISION");
    assert_eq!(
        (
            out.mutation.outcome,
            out.mutation.progress,
            out.mutation.errno_value
        ),
        (1, 0, 17),
        "AMK_COLLISION"
    );
    assert_eq!(out.finalization.disconnect_attempted, 0, "AMK_COLLISION");
    let mutation_headers = actual
        .wire
        .sent
        .iter()
        .filter(|f| &f[..8] == filesystem_service::MAGIC && filesystem_service::word(f, 1) == 10)
        .count();
    assert_eq!(
        (mutation_headers, actual.wire.closes),
        (1, 1),
        "AMK_COLLISION"
    );
    let (_, created, opens, closes) = actual.finish();
    assert_eq!((created, opens == closes), (3, true), "AMK_COLLISION");
}
#[test]
fn progress_and_error_matrix_survives_finish() {
    for (reply, kind, errno, outcome, progress_tag, txg) in [
        (Ok(fixture::reply(-17, 0, 0)), 6, 17, 1, 0, 0),
        (Ok(fixture::reply(-28, 0, 1)), 6, 28, 1, 1, 0),
        (Ok(fixture::reply(-13, 9, 2)), 6, 13, 1, 2, 9),
        (Ok(fixture::reply(-5, 0, 3)), 6, 5, 1, 3, 0),
        (Err(-32), 5, 32, 2, 3, 0),
        (Ok(fixture::reply(0, 7, 2)), 0, 0, 3, 2, 7),
    ] {
        let mut wire = fixture::Wire::normal(reply);
        if kind != 0 {
            wire.close_values = [-9, -5];
        }
        let mut app = Application::new(vec![Step::Mkdir(b"dir", 0o700), Step::Finish]);
        let (_, out) = run(&mut wire, &mut app);
        assert_eq!(
            (
                out.mutation.error_kind,
                out.mutation.errno_value,
                out.mutation.outcome,
                out.mutation.progress,
                out.mutation.txg
            ),
            (kind, errno, outcome, progress_tag, txg),
            "AMK_PROGRESS"
        );
        assert_eq!(out.mutation, app.mutations[0], "AMK_PROGRESS");
        assert_eq!(wire.closes, 1, "AMK_PROGRESS");
        if kind != 0 {
            assert_eq!(
                (
                    out.finalization.reader_close,
                    out.finalization.writer_close,
                    out.finalization.disconnect_attempted
                ),
                (-9, -5, 0),
                "AMK_PROGRESS"
            );
        }
    }
}
#[test]
fn malformed_reply_becomes_unknown_and_closes_once() {
    let mut wire = fixture::Wire::normal(Ok(fixture::reply(0, 0, 2)));
    let mut app = Application::new(vec![Step::Mkdir(b"dir", 0o700), Step::Finish]);
    let (_, out) = run(&mut wire, &mut app);
    assert_eq!(
        (
            out.mutation.outcome,
            out.mutation.progress,
            out.mutation.error_kind,
            out.mutation.errno_value
        ),
        (2, 3, 4, 5),
        "AMK_UNKNOWN"
    );
    assert_eq!(
        (wire.closes, out.finalization.disconnect_attempted),
        (1, 0),
        "AMK_UNKNOWN"
    );
}
#[test]
fn local_leaf_mode_and_single_call_admission_have_no_effect() {
    let mut wire = fixture::Wire::normal(Ok(fixture::reply(0, 7, 2)));
    let mut app = Application::new(vec![
        Step::Mkdir(b".", 0o700),
        Step::Mkdir(b"../x", 0o700),
        Step::Mkdir(b"x\0y", 0o700),
        Step::Mkdir(b"x", 0o755),
        Step::Mkdir(b"abcdefghijklmnopqrstuvwxyz", 0o700),
        Step::Mkdir(b"dir", 0o700),
        Step::Mkdir(b"again", 0o700),
    ]);
    let (_, out) = run(&mut wire, &mut app);
    assert_eq!(
        app.returns,
        vec![-22, -22, -22, -22, -22, 0, -9],
        "AMK_PREFLIGHT"
    );
    assert_eq!(out.mutation.outcome, 3, "AMK_PREFLIGHT");
    assert_eq!(wire.sent.iter().filter(|f|&f[..8]==filesystem_service::MAGIC && filesystem_service::word(f,1)==10).count(),1,"AMK_PREFLIGHT");
}
#[test]
fn active_finish_validates_disconnect_and_preserves_raw_closes() {
    let mut bad_ack = message(91, 0);
    bad_ack[24] = 1;
    let mut wire = fixture::Wire::scripted(vec![
        Ok(fixture::greeting(1)),
        Ok(fixture::greeting(2)),
        Ok(fixture::reply(0, 7, 2)),
        Ok(bad_ack),
    ]);
    wire.close_values = [-9, -5];
    let mut app = Application::new(vec![Step::Mkdir(b"dir", 0o700), Step::Finish]);
    let (_, out) = run(&mut wire, &mut app);
    assert_eq!(
        (
            out.finalization.disconnect_attempted,
            out.finalization.error_kind,
            out.finalization.errno_value,
            out.finalization.reader_close,
            out.finalization.writer_close
        ),
        (1, 4, 5, -9, -5),
        "AMK_DISCONNECT"
    );
    assert_eq!(
        (out.final_status, out.mutation.outcome, wire.closes),
        (1, 3, 1),
        "AMK_DISCONNECT"
    );
}
#[test]
fn finished_live_context_and_second_finish_are_inert() {
    let mut wire = fixture::Wire::normal(Ok(fixture::reply(0, 7, 2)));
    let mut app = Application::new(vec![
        Step::Mkdir(b"dir", 0o700),
        Step::Finish,
        Step::Mkdir(b"again", 0o700),
        Step::Finish,
    ]);
    let (_, out) = run(&mut wire, &mut app);
    assert_eq!(app.returns, vec![0, 0, -9, 0], "AMK_FINISH_ONCE");
    assert_eq!(app.finishes[0], app.finishes[1], "AMK_FINISH_ONCE");
    assert_eq!(
        (out.mutation.outcome, wire.closes),
        (3, 1),
        "AMK_FINISH_ONCE"
    );
}
#[test]
fn connect_failure_closes_both_once_without_entry() {
    for close_values in [[0, 0], [-9, -5]] {
        let mut bad = fixture::greeting(2);
        bad[0] ^= 1;
        let mut wire = fixture::Wire::scripted(vec![Ok(fixture::greeting(1)), Ok(bad)]);
        wire.close_values = close_values;
        let mut app = Application::new(vec![Step::Mkdir(b"dir", 0o700)]);
        let (status, out) = run(&mut wire, &mut app);
        assert_eq!(
            (
                status,
                out.admission.phase,
                out.admission.endpoints_accepted,
                wire.closes
            ),
            (-5, 2, 1, 1),
            "AMK_CONNECT_FAILURE"
        );
        assert_eq!(
            (out.finalization.reader_close, out.finalization.writer_close),
            (close_values[0], close_values[1]),
            "AMK_CONNECT_FAILURE"
        );
        assert!(
            app.returns.is_empty() && wire.sent.is_empty(),
            "AMK_CONNECT_FAILURE"
        );
    }
}
#[test]
fn entry_nonzero_and_cleanup_failure_keep_nonzero_status() {
    let mut wire = fixture::Wire::normal(Ok(fixture::reply(0, 7, 2)));
    wire.close_values = [0, -5];
    let mut app = Application::new(vec![Step::Mkdir(b"dir", 0o700)]);
    app.status = 64;
    let (_, out) = run(&mut wire, &mut app);
    assert_eq!(
        (
            out.command_status,
            out.final_status,
            out.mutation.outcome,
            out.finalization.writer_close
        ),
        (64, 64, 3, -5),
        "AMK_STATUS"
    );
}
#[test]
fn nested_entry_denied_before_endpoint_transfer() {
    let mut wire = fixture::Wire::scripted(vec![
        Ok(fixture::greeting(1)),
        Ok(fixture::greeting(2)),
        Ok(message(91, 0)),
    ]);
    let bootstrap = wire.bootstrap();
    let mut app = Application::new(vec![Step::Nested]);
    app.nested = Some(bootstrap);
    let (_, out) = run(&mut wire, &mut app);
    let nested = app.nested_result.unwrap();
    assert_eq!(
        (
            app.returns,
            nested.admission.endpoints_accepted,
            wire.closes,
            out.final_status
        ),
        (vec![-16], 0, 1, 0),
        "AMK_NESTED"
    );
}
