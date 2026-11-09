// SPDX-License-Identifier: BSD-2-Clause
//! Focused actual Runtime fixtures with a mocked native boundary and real AF09
//! Client/service, descriptor cores, pipes and child ledger. No native execution.
//! Compile native_app_runtime.rs with rustc --test and its existing selected
//! dependency rlibs; the qualified private invocation is retained in #143 evidence.
use super::*;
use af07_transport::Kernel;
use filesystem_policy as p;
use filesystem_service::Channel;
use std::{
    boxed::Box,
    cell::RefCell,
    collections::{BTreeMap, VecDeque},
    rc::Rc,
    sync::mpsc,
    thread,
    time::Duration,
    vec::Vec,
};
#[cfg(native_zsh_home_redirection)]
const NOTE_PATH: &[u8] = if cfg!(native_zsh_login_startup) {
    b"/home/.zprofile"
} else {
    b"/home/note"
};
#[cfg(native_zsh_home_redirection)]
const NOTE_NAME: &[u8] = if cfg!(native_zsh_login_startup) {
    b".zprofile"
} else {
    b"note"
};
#[cfg(native_zsh_home_redirection)]
const NOTE_BYTES: &[u8] = if cfg!(native_zsh_login_startup) {
    b"setopt no_beep;\n"
} else {
    b"AETHER-HOME-158\n"
};
const NSR: u64 = 0xd1000101;
const NSW: u64 = 0xd1000102;
const PR: u64 = 0xd1010101;
const PW: u64 = 0xd1010102;
const PARENT: u64 = 0xb0000102;
const CHILD: u64 = 0xb0000103;
#[cfg(native_zsh_file_exec)]
const FILE_EXEC_TEST_IMAGE: &[u8] = FILE_EXEC_ELF;
#[cfg(not(native_zsh_file_exec))]
const FILE_EXEC_TEST_IMAGE: &[u8] = &[];
#[derive(Default)]
struct Storage {
    made: [bool; 3],
    data: Vec<u8>,
    probe: Vec<u8>,
    #[cfg(native_zsh_home_redirection)]
    note: Option<Vec<u8>>,
    probe_failure: u8,
    mutations: u64,
}
fn node(id: u64, size: usize) -> p::Node {
    p::Node::new(
        id,
        1,
        size as u64,
        if matches!(id, 5 | 6)
            || (cfg!(native_zsh_home_redirection) && id == 7)
            || (cfg!(native_zsh_operator_note) && id == 8)
        {
            p::Kind::File
        } else {
            p::Kind::Directory
        },
    )
}
impl p::Backend for Storage {
    #[cfg(native_zsh_home_cwd)]
    fn directory_context(
        &mut self,
        root: p::Node,
        at: p::Node,
        out: &mut [u8; 256],
    ) -> Result<(p::Node, usize), p::Error> {
        let path: &[u8] = if at.identity().0 == root.identity().0 {
            b"/\0"
        } else {
            b"/home\0"
        };
        out[..path.len()].copy_from_slice(path);
        Ok((root, path.len()))
    }

    fn root(&mut self) -> Result<p::Node, p::Error> {
        Ok(node(1, 0))
    }
    fn directory(&mut self, n: p::Node) -> Result<p::Node, p::Error> {
        Ok(n)
    }
    fn lookup(&mut self, n: p::Node, s: &[u8]) -> Result<p::Node, p::Error> {
        let id = match (n.identity().0, s) {
            (1, b"home") => 2,
            (2, b".terminfo") if self.made[0] => 3,
            (2, b"probe") => 6,
            #[cfg(native_zsh_home_redirection)]
            (2, name) if name == NOTE_NAME && self.note.is_some() => 7,
            #[cfg(native_zsh_operator_note)]
            (2, b"note") => 8,
            (3, b"v") if self.made[1] => 4,
            (4, b"vt100") if self.made[2] => 5,
            _ => return Err(p::Error::Backend(2)),
        };
        Ok(node(
            id,
            match id {
                5 => self.data.len(),
                6 => self.probe.len(),
                #[cfg(native_zsh_home_redirection)]
                7 => self.note.as_ref().unwrap().len(),
                _ => 0,
            },
        ))
    }
    fn read(&mut self, node: p::Node, at: u64, out: &mut [u8]) -> Result<usize, p::Error> {
        #[cfg(native_zsh_home_redirection)]
        if node.identity().0 == 7 {
            let data = self.note.as_ref().unwrap();
            let at = (at as usize).min(data.len());
            let count = out.len().min(data.len() - at);
            out[..count].copy_from_slice(&data[at..at + count]);
            return Ok(count);
        }
        let data = if node.identity().0 == 6 {
            &self.probe
        } else {
            &self.data
        };
        let at = (at as usize).min(data.len());
        let n = out.len().min(data.len() - at);
        out[..n].copy_from_slice(&data[at..at + n]);
        Ok(n)
    }
    fn write(
        &mut self,
        n: p::Node,
        at: u64,
        bytes: &[u8],
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        assert_eq!(at, 0);
        self.mutations += 1;
        match n.identity().0 {
            5 => self.data = bytes.to_vec(),
            #[cfg(native_zsh_home_redirection)]
            7 => self.note = Some(bytes.to_vec()),
            6 => {
                assert_eq!(
                    bytes,
                    if cfg!(native_zsh_file_exec) {
                        FILE_EXEC_TEST_IMAGE
                    } else {
                        b"AETHER-ZSH-HOME\n"
                    },
                    "EXACT_SELECTED_PROBE_PROVISION"
                );
                if self.probe_failure == 2 {
                    return Err(p::Lost);
                }
                if self.probe_failure == 1 {
                    return Ok(p::Completion {
                        error: 5,
                        txg: self.mutations,
                        bytes_staged: 0,
                        state: 2,
                    });
                }
                self.probe = bytes.to_vec();
            }
            _ => panic!("NO_OTHER_WRITE_OBJECT"),
        }
        Ok(p::Completion {
            error: 0,
            txg: self.mutations,
            bytes_staged: bytes.len() as u64,
            state: 2,
        })
    }
    fn mutate(
        &mut self,
        n: p::Node,
        op: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        #[cfg(native_zsh_home_redirection)]
        if matches!(
            (n.identity().0, &op),
            (2, p::Namespace::Create { name, .. }) if *name == NOTE_NAME
        ) {
            assert!(self.note.is_none());
            self.note = Some(Vec::new());
            self.mutations += 1;
            return Ok(p::Completion {
                error: 0,
                txg: self.mutations,
                bytes_staged: 0,
                state: 2,
            });
        }
        let i = match (n.identity().0, op) {
            (
                2,
                p::Namespace::MakeDirectory {
                    name: b".terminfo", ..
                },
            ) => 0,
            (3, p::Namespace::MakeDirectory { name: b"v", .. }) => 1,
            (4, p::Namespace::Create { name: b"vt100", .. }) => 2,
            _ => panic!("UNAUTHORIZED_MUTATION"),
        };
        assert!(!self.made[i]);
        self.made[i] = true;
        self.mutations += 1;
        Ok(p::Completion {
            error: 0,
            txg: self.mutations,
            bytes_staged: 0,
            state: 2,
        })
    }
}
struct Time;
impl p::Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        Ok(p::Utc {
            seconds: 1,
            nanoseconds: 0,
        })
    }
}
struct ServicePipe {
    tx: mpsc::Sender<[u8; 64]>,
    rx: mpsc::Receiver<[u8; 64]>,
}
impl Channel for ServicePipe {
    fn send(&mut self, b: &[u8; 64]) -> Result<(), i64> {
        self.tx.send(*b).map_err(|_| -32)
    }
    fn receive(&mut self, b: &mut [u8; 64]) -> Result<(), i64> {
        *b = self
            .rx
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        [0; 2]
    }
}
struct Host {
    tx: Option<mpsc::Sender<[u8; 64]>>,
    rx: mpsc::Receiver<[u8; 64]>,
    send: [u8; 64],
    send_at: usize,
    receive: [u8; 64],
    receive_at: usize,
    input: BTreeMap<u64, VecDeque<u8>>,
    output: BTreeMap<u64, Vec<u8>>,
    calls: Vec<(u64, u64, u64)>,
    closed: Vec<u64>,
    pair: u64,
    copy_result: i64,
    child: u64,
    exec_result: i64,
    receipt: Status,
    ready: bool,
    terminal: Option<Status>,
    gone: bool,
    parent_terminal: bool,
    parent_gone: bool,
    stop_result: Status,
    stop_observation: Status,
    #[cfg(native_zsh_operator)]
    event: Status,
    #[cfg(native_zsh_operator)]
    observations: VecDeque<Status>,
    #[cfg(native_zsh_operator)]
    parks: Vec<(u64, u64)>,
    #[cfg(native_zsh_operator)]
    wake: Status,
    #[cfg(native_zsh_operator)]
    engine_state: Status,
    #[cfg(native_zsh_operator)]
    parent_state: Option<Status>,
    #[cfg(native_zsh_operator)]
    output_blocked: bool,
    #[cfg(native_zsh_operator)]
    export_on_park: bool,
    serial_reads: usize,
    serial_output: Vec<u8>,
    fail_write: Option<(u64, usize)>,
    written: usize,
    #[cfg(native_zsh_file_exec)]
    fail_namespace_opcode: Option<u64>,
    #[cfg(native_zsh_file_exec)]
    file_receipt_tag: u64,
    #[cfg(native_zsh_file_exec)]
    last_namespace_opcode: u64,
}
#[derive(Clone)]
struct Mock(Rc<RefCell<Host>>);
impl Kernel for Mock {
    fn transfer(&mut self, cap: u64, bytes: &mut [u8], writing: bool) -> i64 {
        let mut h = self.0.borrow_mut();
        #[cfg(native_zsh_operator)]
        if h.export_on_park && h.last_namespace_opcode == 4 && bytes.len() == 1 {
            return if cap == NSR && !writing { 0 } else { -32 };
        }
        if cap == NSW && writing {
            let at = h.send_at;
            h.send[at..at + bytes.len()].copy_from_slice(bytes);
            h.send_at += bytes.len();
            if h.send_at == 64 {
                #[cfg(native_zsh_file_exec)]
                if h.send[..8] == *b"AFSRPC09" {
                    h.last_namespace_opcode = u64::from_le_bytes(h.send[8..16].try_into().unwrap());
                }
                h.tx.as_ref().unwrap().send(h.send).unwrap();
                h.send_at = 0;
            }
            return bytes.len() as i64;
        }
        if cap == NSR && !writing {
            if h.receive_at == 64 {
                h.receive = h.rx.recv_timeout(Duration::from_secs(2)).unwrap();
                h.receive_at = 0;
            }
            #[cfg(native_zsh_file_exec)]
            if h.fail_namespace_opcode == Some(h.last_namespace_opcode) {
                h.fail_namespace_opcode = None;
                return -5;
            }
            let at = h.receive_at;
            bytes.copy_from_slice(&h.receive[at..at + bytes.len()]);
            h.receive_at += bytes.len();
            return bytes.len() as i64;
        }
        if writing {
            if let Some((target, limit)) = h.fail_write {
                if cap == target && h.written >= limit {
                    return -5;
                }
            }
            h.output.entry(cap).or_default().extend_from_slice(bytes);
            h.written += bytes.len();
            return bytes.len() as i64;
        }
        let q = h.input.entry(cap).or_default();
        if q.is_empty() {
            return -11;
        }
        let n = bytes.len().min(q.len());
        for b in &mut bytes[..n] {
            *b = q.pop_front().unwrap();
        }
        n as i64
    }
    fn wait(&mut self, _: u64) -> i64 {
        0
    }
    fn close(&mut self, cap: u64) -> i64 {
        let mut h = self.0.borrow_mut();
        assert!(!h.closed.contains(&cap), "NO_CLOSE_REPLAY");
        h.closed.push(cap);
        if cap == NSW {
            h.tx = None;
        }
        0
    }
}
impl Control for Mock {
    fn observe_events(&mut self) -> Status {
        #[cfg(native_zsh_operator)]
        {
            let mut h = self.0.borrow_mut();
            if let Some(next) = h.observations.pop_front() {
                h.event = next;
            }
            return h.event;
        }
        #[cfg(not(native_zsh_operator))]
        (0, 1, 1)
    }
    fn park_events(&mut self, sequence: u64, deadline: Option<Deadline>) -> Status {
        #[cfg(native_zsh_operator)]
        {
            let mut h = self.0.borrow_mut();
            h.parks.push((sequence, deadline.unwrap().get()));
            if h.wake.0 == 0 {
                h.event = h.wake;
            }
            if h.export_on_park {
                h.engine_state = (1, 1, 1);
            }
            return h.wake;
        }
        #[cfg(not(native_zsh_operator))]
        {
            let _ = (sequence, deadline);
            (0, 1, 1)
        }
    }
    fn ctl(&mut self, op: u64, cap: u64, arg: u64) -> Status {
        let mut h = self.0.borrow_mut();
        h.calls.push((op, cap, arg));
        match op {
            #[cfg(native_zsh_operator)]
            0x20001 if cap == 0xb0000101 => {
                let state = h.engine_state;
                if h.export_on_park {
                    h.event = (0, 8, 2);
                }
                state
            }
            0x24000 => {
                let id = h.pair;
                h.pair += 1;
                ((0xd1000101 | id << 16) as i64, 0xd1000102 | id << 16, 0)
            }
            0x23004 => (101, 0, 0),
            0x23005 | 0x1fffe => (0, 0, 0),
            0x20001 if cap == PARENT => {
                #[cfg(native_zsh_operator)]
                if let Some(state) = h.parent_state {
                    return state;
                }
                if h.parent_gone {
                    (-9, 0, 0)
                } else if h.parent_terminal {
                    (144, 0, 3)
                } else {
                    (0, 1, 0)
                }
            }
            0x20007 if cap == PARENT => {
                h.parent_terminal = true;
                (0, 0, 0)
            }
            0x20002 if cap == PARENT => {
                assert!(h.parent_terminal);
                h.parent_gone = true;
                (0, 0, 0)
            }
            0x20007 if cap == h.child => {
                if h.stop_result.0 == 0 && h.terminal.is_none() {
                    h.terminal = Some(h.stop_observation);
                }
                h.stop_result
            }
            0x26002 if cap == 0xf001 => (0, 0, 0),
            0x100e7 if cap == 125 => (0, 0, 0),
            0x20001 if cap == h.child => {
                if h.gone {
                    (-9, 0, 0)
                } else {
                    h.terminal.unwrap_or((0, u64::from(h.ready), 0))
                }
            }
            0x20002 if cap == h.child => {
                h.gone = true;
                (0, 0, 0)
            }
            _ => panic!("UNEXPECTED_NATIVE_CONTROL {op:x} {cap:x} {arg:x}"),
        }
    }
    fn engine(&mut self, _: u64, _: u64) -> i64 {
        panic!("NO_ENGINE_LAUNCH")
    }
    fn delegate(&mut self, _: u64, _: &[u64; 3]) -> i64 {
        panic!("NO_DELEGATION")
    }
    fn launch(&mut self, _: &[u8; 272], _: u64, _: u64) -> i64 {
        panic!("NO_LEGACY_LAUNCH")
    }
    fn copy(&mut self, parent: u64, slot: u32, token: u64, reader: u64, writer: u64) -> i64 {
        let mut h = self.0.borrow_mut();
        assert_eq!((parent, slot, token), (PARENT, 2, 101));
        h.calls.push((0x23006, reader, writer));
        #[cfg(native_zsh_repeat_exec)]
        if h.copy_result > 1 {
            h.child = h.copy_result as u64;
            h.ready = false;
            h.terminal = None;
            h.gone = false;
            h.receipt = (0, 0, 0);
        }
        h.copy_result
    }
    fn serial(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        let mut h = self.0.borrow_mut();
        if writing {
            #[cfg(native_zsh_operator)]
            if h.output_blocked {
                return -11;
            }
            h.serial_output.extend_from_slice(bytes);
            bytes.len() as i64
        } else {
            h.serial_reads += 1;
            -11
        }
    }
    fn exec(&mut self, process: u64, token: u64, args: &[u8; 272]) -> i64 {
        assert!(!cfg!(native_zsh_file_exec), "NO_BOOT_HELPER_FALLBACK");
        assert_eq!((process, token), (self.0.borrow().child, 101));
        let mut h = self.0.borrow_mut();
        h.calls.push((0x23007, process, token));
        assert_eq!(u64::from_le_bytes(args[..8].try_into().unwrap()), 2);
        if h.exec_result == 0 {
            h.receipt = (101, 0xc003, 1);
            h.ready = false;
        }
        h.exec_result
    }
    #[cfg(native_zsh_file_exec)]
    fn exec_file(&mut self, process: u64, token: u64, args: &[u8; 272], image: &[u8]) -> i64 {
        assert_eq!((process, token), (self.0.borrow().child, 101));
        assert_eq!(
            args[..8],
            1u64.to_le_bytes(),
            "SAVED_ARGUMENTS_SURVIVE_FILE_READ"
        );
        assert_eq!(&args[16..27], b"/home/probe");
        assert!(args[27..].iter().all(|byte| *byte == 0));
        assert_eq!(image, FILE_EXEC_ELF, "ACTUAL_ACQUIRED_FILE_SNAPSHOT");
        let mut h = self.0.borrow_mut();
        h.calls.push((0x2300b, process, token));
        if h.exec_result == 0 {
            h.receipt = (101, h.file_receipt_tag, 1);
            h.ready = false;
        }
        h.exec_result
    }
    fn receipt(&mut self, process: u64) -> Status {
        assert_eq!(process, self.0.borrow().child);
        self.0.borrow().receipt
    }
    fn publish(&mut self, process: u64, token: u64) -> i64 {
        assert_eq!((process, token), (self.0.borrow().child, 101));
        self.0.borrow_mut().calls.push((0x23009, process, token));
        0
    }
}
impl AppControl for Mock {
    fn launch_app(&mut self, _: &[u8; 320], _: u64, _: u64) -> i64 {
        panic!("NO_NEW_APP")
    }
}
struct Fixture {
    runtime: Box<Runtime<Mock>>,
    host: Mock,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
}
impl Fixture {
    fn new() -> Self {
        Self::with_probe_failure(0)
    }
    fn with_probe_failure(probe_failure: u8) -> Self {
        let (a, b) = mpsc::channel();
        let (c, d) = mpsc::channel();
        let worker = thread::spawn(move || {
            let mut owner = p::Owner::new(
                Storage {
                    probe_failure,
                    #[cfg(native_zsh_home_redirection_reader)]
                    note: Some(NOTE_BYTES.to_vec()),
                    #[cfg(native_zsh_cold_reopen)]
                    made: [true; 3],
                    #[cfg(native_zsh_cold_reopen)]
                    data: TERMINFO.to_vec(),
                    #[cfg(native_zsh_cold_reopen)]
                    probe: FILE_EXEC_TEST_IMAGE.to_vec(),
                    ..Storage::default()
                },
                Time,
                91,
            )
            .unwrap()
            .with_namespace_identity(p::Identity::new(1000, 1000).unwrap());
            let attached = owner.attach(7, p::Rights::new(15).unwrap()).unwrap();
            let home = owner
                .lookup(
                    7,
                    attached.session,
                    attached.root.handle,
                    b"home",
                    p::Rights::new(15).unwrap(),
                )
                .unwrap();
            filesystem_service::run_home(
                owner,
                ServicePipe { tx: c, rx: b },
                7,
                attached.session,
                home.handle,
                8,
                91,
            )
        });
        let host = Mock(Rc::new(RefCell::new(Host {
            tx: Some(a),
            rx: d,
            send: [0; 64],
            send_at: 0,
            receive: [0; 64],
            receive_at: 64,
            input: BTreeMap::new(),
            output: BTreeMap::new(),
            calls: Vec::new(),
            closed: Vec::new(),
            pair: 2,
            copy_result: CHILD as i64,
            child: CHILD,
            exec_result: 0,
            receipt: (0, 0, 0),
            ready: false,
            terminal: None,
            gone: false,
            parent_terminal: false,
            parent_gone: false,
            stop_result: (0, 0, 0),
            stop_observation: (144, 0, 3),
            #[cfg(native_zsh_operator)]
            event: (0, 1, 1),
            #[cfg(native_zsh_operator)]
            observations: VecDeque::new(),
            #[cfg(native_zsh_operator)]
            parks: Vec::new(),
            #[cfg(native_zsh_operator)]
            wake: (0, 1, 1),
            #[cfg(native_zsh_operator)]
            engine_state: (0, 1, 0),
            #[cfg(native_zsh_operator)]
            parent_state: None,
            #[cfg(native_zsh_operator)]
            output_blocked: false,
            #[cfg(native_zsh_operator)]
            export_on_park: false,
            serial_reads: 0,
            serial_output: Vec::new(),
            fail_write: None,
            written: 0,
            #[cfg(native_zsh_file_exec)]
            fail_namespace_opcode: None,
            #[cfg(native_zsh_file_exec)]
            file_receipt_tag: 0xc004,
            #[cfg(native_zsh_file_exec)]
            last_namespace_opcode: 0,
        })));
        let mut runtime = Box::new(Runtime::new(host.clone()).unwrap());
        runtime.app = PARENT;
        runtime.identity = Some(Identity::admitted(1, 1, PARENT).unwrap());
        runtime.endpoints = Some(ManuallyDrop::new(
            Endpoints::new(host.clone(), PR, PW).ok().unwrap(),
        ));
        let caller = serial_tty::Caller {
            identity: PARENT,
            generation: 1,
        };
        let (mut tty, refs) = Terminal::admit(
            PARENT,
            caller,
            [
                Rights::READ.union(Rights::MODE),
                Rights::WRITE,
                Rights::WRITE,
            ],
            Mode::IMMEDIATE,
        )
        .unwrap();
        runtime.mode = Some(tty_mode::State::admit(&mut tty, &refs, caller).unwrap());
        runtime.tty = Some((tty, refs, caller));
        for (end, cap) in runtime.ends[..2].iter_mut().zip([NSR, NSW]) {
            *end = End {
                cap,
                owned: true,
                ..End::default()
            };
        }
        // These are the two Owner-held Parent process endpoints. Child cleanup
        // must not borrow their existing global close/reclaim reserve.
        for (end, cap) in runtime.ends[2..4].iter_mut().zip([PR, PW]) {
            *end = End {
                cap,
                owned: true,
                ..End::default()
            };
        }
        runtime.namespace_prepaid = [NSR, NSW];
        let binding = filesystem_readonly::Binding {
            slot: 1,
            epoch: 1,
            handle: PARENT,
            generation: PR,
        };
        let mut channel = Namespace::new(host.clone(), NSR, NSW);
        // SAFETY: disjoint loans remain fixed through synchronous final-slot connect.
        unsafe {
            channel
                .arm(
                    &mut runtime.bound,
                    &mut runtime.ends,
                    &mut runtime.filesystem_requests,
                    &mut runtime.namespace_prepaid,
                )
                .unwrap();
        }
        filesystem_readonly::Files::connect_in_place(&mut runtime.files, channel, 91, binding)
            .unwrap()
            .configure(|io| {
                io.disarm();
                Ok(())
            })
            .unwrap();
        runtime.files_live = true;
        runtime.file_binding = Some(binding);
        #[cfg(not(native_zsh_cold_reopen))]
        runtime
            .with_files(|files| files.provision(TERMINFO, &mut [0; 4096]))
            .unwrap();
        #[cfg(native_zsh_cold_reopen)]
        runtime
            .with_files(|files| files.reopen(TERMINFO, &mut [0; 4096]))
            .unwrap();
        #[cfg(all(native_zsh_file_exec, not(native_zsh_cold_reopen)))]
        runtime
            .with_files(|files| files.provision_file_exec(FILE_EXEC_ELF))
            .unwrap();
        #[cfg(native_zsh_cold_reopen)]
        runtime
            .with_files(|files| files.reopen_file_exec(FILE_EXEC_ELF, &mut [0; 4096]))
            .unwrap();
        #[cfg(native_zsh_home_redirection_reader)]
        runtime
            .with_files(|files| files.reopen_note(&mut [0; 4096]))
            .unwrap();
        #[cfg(native_zsh_operator_login)]
        runtime
            .with_files(|files| files.initialize_home_cwd(&mut [0; 4096]))
            .unwrap();
        Self {
            runtime,
            host,
            worker: Some(worker),
        }
    }
    fn feed(&self, cap: u64, bytes: &[u8]) {
        self.host
            .0
            .borrow_mut()
            .input
            .entry(cap)
            .or_default()
            .extend(bytes);
    }
    fn output(&self, cap: u64) -> Vec<u8> {
        self.host
            .0
            .borrow()
            .output
            .get(&cap)
            .cloned()
            .unwrap_or_default()
    }
    fn clear(&self) {
        self.host.0.borrow_mut().output.clear();
        self.host.0.borrow_mut().written = 0;
    }
    fn snapshot(&self, pipe: bool) -> [u8; 336] {
        let r = &self.runtime;
        let id = r.identity.unwrap();
        let mut p = Plan {
            identity: id,
            shell: 1,
            parent: 7,
            generation: PR,
            bindings: [Binding::default(); 16],
            sources: [Source::default(); 7],
            history: [0; 2],
        };
        for i in 0..3 {
            p.bindings[i] = Binding {
                kind: 4,
                selector: i as u8,
                cloexec: 0,
            };
            p.sources[i] = console(i as u32);
        }
        if pipe {
            p.history[0] = 1;
            for i in 3..5 {
                p.bindings[i] = Binding {
                    kind: 2,
                    selector: i as u8,
                    cloexec: 1,
                };
                p.sources[i] = Source {
                    reference: 0x79000101 + (i as u32 - 3),
                    selector: i as u32,
                    rights: if i == 3 { 1 } else { 2 },
                    bound: 16,
                };
            }
        }
        let mut out = [0; 336];
        fd_startup::encode(&p, &mut out).unwrap();
        out
    }
    fn fork(&mut self, pipe: bool) -> [u8; 336] {
        if pipe {
            let q = frame(82, 0x76050001, 1, 0);
            assert!(self.runtime.zsh_stream(false, &q).unwrap());
            self.clear();
        }
        let raw = self.snapshot(pipe);
        let mut request = [0; 368];
        zsh_process_frames::encode_fork(
            &raw,
            self.runtime.zsh_expected(false).unwrap(),
            1,
            &mut request,
        )
        .unwrap();
        let mut work = [0; 4096];
        work[..368].copy_from_slice(&request);
        self.runtime.zsh_fork(&mut work).unwrap();
        let child_writer = self.runtime.process.ends[3].cap;
        let child: [u8; 336] = self.output(child_writer).try_into().unwrap();
        self.clear();
        let ready = zsh_process_frames::receipt(b"AEZFC001", 1, 10).unwrap();
        self.runtime.zsh_child_ready(&ready).unwrap();
        assert_eq!(
            zsh_process_frames::decode_receipt(&self.output(PW), b"AEZFR001", 1).unwrap(),
            10
        );
        self.clear();
        child
    }
    #[cfg(native_zsh_home_write)]
    fn home_file_request(
        &mut self,
        op: u64,
        sequence: u64,
        a: u64,
        body: &[u8],
    ) -> Result<Vec<u8>, i64> {
        let binding = self.runtime.process.binding.unwrap();
        let mut header = [0; 64];
        header[..8].copy_from_slice(filesystem_readonly::MAGIC);
        for (index, value) in [op, binding.generation, sequence, a, body.len() as u64, 0, 0]
            .into_iter()
            .enumerate()
        {
            header[(index + 1) * 8..(index + 2) * 8].copy_from_slice(&value.to_le_bytes());
        }
        self.runtime.file_header = header;
        let cap = self.runtime.process.ends[0].cap;
        let mut padded = [0; 64];
        padded[..body.len()].copy_from_slice(body);
        if !body.is_empty() {
            self.feed(cap, &padded);
        }
        self.clear();
        let writer = self.runtime.process.ends[3].cap;
        self.runtime.file_request(&mut [0; 4096], true)?;
        Ok(self.output(writer))
    }
    #[cfg(native_zsh_home_write)]
    fn open_home_write(&mut self, sequence: u64) -> i32 {
        let reply = self
            .home_file_request(12, sequence, 0, b"/home/probe")
            .unwrap();
        assert_eq!(
            i64::from_le_bytes(reply[8..16].try_into().unwrap()),
            0,
            "HOME_WRITE_OPEN_STATUS"
        );
        let fd = u64::from_le_bytes(reply[32..40].try_into().unwrap());
        assert!((3..16).contains(&fd), "HOME_WRITE_OPEN");
        fd as i32
    }
    #[cfg(native_zsh_home_write)]
    fn complete_home_write(&mut self, sequence: u64) {
        let fd = self.open_home_write(sequence);
        let reply = self
            .home_file_request(11, sequence + 1, fd as u64, b"AETHER-ZSH-HOME\n")
            .unwrap();
        assert_eq!(i64::from_le_bytes(reply[8..16].try_into().unwrap()), 0);
        assert_eq!(u64::from_le_bytes(reply[32..40].try_into().unwrap()), 16);
        assert_eq!(reply.len(), 128);
        assert!(
            !self
                .runtime
                .with_files(|f| Ok(f.home_write_complete()))
                .unwrap()
        );
        let reply = self
            .home_file_request(5, sequence + 2, fd as u64, b"")
            .unwrap();
        assert_eq!(i64::from_le_bytes(reply[8..16].try_into().unwrap()), 0);
        assert!(
            self.runtime
                .with_files(|f| Ok(f.home_write_complete()))
                .unwrap()
        );
    }
    #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
    fn helper_ready(&mut self) {
        let raw = self.fork(false);
        let mut request = self.exec_request(&raw);
        self.runtime.zsh_exec(&mut request).unwrap();
        self.host.0.borrow_mut().ready = true;
        self.runtime.zsh_terminal().unwrap();
        assert!(self.runtime.process.exec_ready);
    }
    #[cfg(native_zsh_home_write)]
    fn collect_helper_zero(&mut self) {
        self.host.0.borrow_mut().terminal = Some((1, 1, 1));
        self.runtime.zsh_terminal().unwrap();
        self.clear();
        assert!(
            self.runtime
                .zsh_stream(false, &frame(68, u32::MAX, 0, 0))
                .unwrap()
        );
        assert_eq!(
            (result(&self.output(PW)), result(&self.output(PW)[4..])),
            (10, 0)
        );
    }
    #[cfg(any(native_zsh_home_write, native_zsh_file_exec))]
    fn prepare_healthy_oracle(&mut self) {
        self.runtime.cleanup_mode().unwrap();
        self.runtime
            .with_files(|files| files.disconnect_checked(|_| Ok(())).map(|_| ()))
            .unwrap();
        self.runtime.close_owned().unwrap();
        // Synthetic terminal observations isolate the final machine-row guard;
        // real target terminal/export proof remains a separate native gate.
        self.runtime.observed_terminal = [Some((1, 1, 1)); 2];
        self.runtime.app = 0;
        self.runtime.engine = 0;
    }
    fn exec_request(&self, raw: &[u8; 336]) -> [u8; 4096] {
        let mut work = [0; 4096];
        work[..8].copy_from_slice(b"AEZEX001");
        put(&mut work, 8, 1);
        put(&mut work, 12, 672);
        work[16..24].copy_from_slice(&2u64.to_le_bytes());
        work[32..368].copy_from_slice(raw);
        if cfg!(native_zsh_file_exec) {
            work[368..379].copy_from_slice(b"/home/probe");
            work[400..408].copy_from_slice(&1u64.to_le_bytes());
            work[416..427].copy_from_slice(b"/home/probe");
        } else {
            work[368..382].copy_from_slice(b"/inputs/helper");
            work[400..408].copy_from_slice(&2u64.to_le_bytes());
            work[416..430].copy_from_slice(b"/inputs/helper");
            let argument = if cfg!(native_zsh_home_write) {
                b"home-write".as_slice()
            } else {
                b"status".as_slice()
            };
            work[448..448 + argument.len()].copy_from_slice(argument);
        }
        work
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = self.runtime.with_files(|files| {
            assert_eq!(files.abort(), [0; 2]);
            Ok(())
        });
        self.host.0.borrow_mut().tx = None;
        self.worker.take().unwrap().join().unwrap();
    }
}
fn put(raw: &mut [u8], at: usize, n: u32) {
    raw[at..at + 4].copy_from_slice(&n.to_le_bytes());
}
fn frame(op: u32, reference: u32, selector: u32, n: u32) -> [u8; 32] {
    let mut q = [0; 32];
    for (at, v) in [(0, op), (4, reference), (8, selector), (12, n)] {
        put(&mut q, at, v);
    }
    q
}
fn result(raw: &[u8]) -> i32 {
    i32::from_le_bytes(raw[..4].try_into().unwrap())
}
#[test]
fn unknown_header_is_fatal_before_tail_consumption() {
    let mut h = Fixture::new();
    let mut q = [0xa5; 32];
    q[..16].fill(0);
    put(&mut q, 0, 0x9911);
    h.feed(PR, &q);
    assert_eq!(
        h.runtime.zsh_poll(false, &mut [0; 4096]),
        Err(-22),
        "UNKNOWN_HEADER_MUST_NOT_RESYNC"
    );
    assert_eq!(h.host.0.borrow().input[&PR].len(), 16);
    assert!(h.output(PW).is_empty());
}
#[test]
fn exact_helper_arguments_are_known_refusal_before_exec() {
    for changed in [0, 1, 2, 3] {
        let mut h = Fixture::new();
        let raw = h.fork(false);
        let mut work = h.exec_request(&raw);
        match changed {
            0 => {
                if cfg!(native_zsh_file_exec) {
                    work[416..448].fill(0);
                    work[416..430].copy_from_slice(b"/inputs/helper");
                } else {
                    work[448] = b'x';
                }
            }
            1 => {
                work[408..416].copy_from_slice(&1u64.to_le_bytes());
                work[544..548].copy_from_slice(b"X=1\0");
            }
            2 => work[416] = b'x',
            _ => {
                work[400..408].copy_from_slice(
                    &(if cfg!(native_zsh_file_exec) {
                        2u64
                    } else {
                        1u64
                    })
                    .to_le_bytes(),
                );
                work[448..480].fill(0);
                if cfg!(native_zsh_file_exec) {
                    work[448..454].copy_from_slice(b"status");
                }
            }
        }
        h.runtime.zsh_exec(&mut work).unwrap();
        assert!(
            !h.host
                .0
                .borrow()
                .calls
                .iter()
                .any(|x| matches!(x.0, 0x23007 | 0x2300b)),
            "EXACT_HELPER_VECTOR_BEFORE_NATIVE_EXEC"
        );
        let writer = h.runtime.process.ends[3].cap;
        assert_eq!(
            zsh_process_frames::decode_receipt(&h.output(writer), b"AEZER001", 2).unwrap(),
            -13
        );
        assert!(!h.runtime.process.committed);
        assert_eq!(
            h.runtime.process.binding.unwrap().generation,
            h.runtime.process.ends[0].cap
        );
        assert!(h.host.0.borrow().calls.contains(&(0x23005, CHILD, 101)));
    }
}
#[test]
fn real_pipe_exec_ready_wait_delivery_reclaim_and_parent_lease() {
    let mut h = Fixture::new();
    let raw = h.fork(true);
    let pipe_read = frame(1, 0x79000101, 3, 1);
    let mut pipe_write = frame(2, 0x79000102, 4, 1);
    pipe_write[16] = b'!';
    assert!(!h.runtime.zsh_stream(false, &pipe_read).unwrap());
    assert!(h.runtime.zsh_stream(true, &pipe_write).unwrap());
    assert!(h.runtime.zsh_stream(false, &pipe_read).unwrap());
    assert_eq!(&h.output(PW)[16..17], b"!");
    h.clear();
    let input = frame(1, 0x7a000001, 0, 1);
    assert!(!h.runtime.zsh_stream(false, &input).unwrap());
    assert_eq!(h.host.0.borrow().serial_reads, 0);
    let mut work = h.exec_request(&raw);
    h.runtime.zsh_exec(&mut work).unwrap();
    assert!(!h.runtime.process.exec_ready);
    let writer = h.runtime.process.ends[3].cap;
    let fresh: [u8; 336] = h.output(writer).try_into().unwrap();
    assert_eq!(&fresh[112 + 3 * 4..112 + 5 * 4], &[0; 8]);
    assert_eq!(h.runtime.process.identity().unwrap().handle, CHILD);
    assert_eq!(
        u64::from_le_bytes(fresh[56..64].try_into().unwrap()),
        h.runtime.process.ends[0].cap + 1
    );
    h.runtime.zsh_terminal().unwrap();
    assert!(!h.runtime.process.exec_ready);
    h.host.0.borrow_mut().ready = true;
    h.runtime.zsh_terminal().unwrap();
    assert!(h.runtime.process.exec_ready);
    #[cfg(native_zsh_home_write)]
    h.complete_home_write(1);
    h.host.0.borrow_mut().terminal = Some((
        if cfg!(native_zsh_file_exec) {
            24
        } else if cfg!(native_zsh_home_write) {
            1
        } else {
            8
        },
        1,
        1,
    ));
    h.runtime.zsh_terminal().unwrap();
    assert_eq!(
        h.runtime.process.lease,
        ReadLease::Child(h.runtime.process.child().unwrap())
    );
    h.clear();
    let wait = frame(68, u32::MAX, 0, 0);
    assert!(h.runtime.zsh_stream(false, &wait).unwrap());
    let reply = h.output(PW);
    let expected = if cfg!(native_zsh_file_exec) {
        5888
    } else if cfg!(native_zsh_home_write) {
        0
    } else {
        1792
    };
    assert_eq!((result(&reply), result(&reply[4..])), (10, expected));
    assert_eq!(&reply[8..], &[0; 24]);
    assert_eq!(h.runtime.process.wait_status, Some(expected));
    assert_eq!(h.runtime.process.lease, ReadLease::Parent);
    assert!(h.runtime.process.reclaimed);
    assert!(h.host.0.borrow().gone);
    assert!(h.runtime.process.binding.is_none());
    assert_eq!(h.runtime.bound.reserved, RESERVED);
    h.clear();
    assert!(h.runtime.zsh_stream(false, &wait).unwrap());
    assert_eq!(result(&h.output(PW)), -10);
}
#[test]
fn child_canonical_read_and_mode_are_rejected_without_input() {
    let mut h = Fixture::new();
    h.fork(false);
    let (tty, refs, caller) = h.runtime.tty.as_mut().unwrap();
    let mut saved = tty.snapshot(*caller, &refs.stdin).unwrap();
    tty.apply_now(
        *caller,
        &refs.stdin,
        &mut saved,
        serial_tty::ModeRequest {
            mode: Mode::CANONICAL,
            action: serial_tty::ApplyWhen::Now,
        },
    )
    .unwrap();
    let reader = frame(1, 0x7a000001, 0, 1);
    assert!(h.runtime.zsh_stream(true, &reader).unwrap());
    let writer = h.runtime.process.ends[3].cap;
    assert_eq!(result(&h.output(writer)), -95);
    assert_eq!(h.host.0.borrow().serial_reads, 0);
    h.clear();
    let mode = frame(0x10, tty_mode::CONTROL, 0, 0);
    assert!(h.runtime.zsh_stream(true, &mode).unwrap());
    assert_eq!(result(&h.output(writer)), -95);
}
#[test]
fn known_exec_refusal_preserves_old_context_and_unknown_exec_never_publishes() {
    for error in [-2, 1] {
        let mut h = Fixture::new();
        let raw = h.fork(true);
        h.host.0.borrow_mut().exec_result = error;
        let old = h.runtime.process.binding;
        let mut work = h.exec_request(&raw);
        let observed = h.runtime.zsh_exec(&mut work);
        if error < 0 {
            assert_eq!(observed, Ok(()));
            let writer = h.runtime.process.ends[3].cap;
            assert_eq!(
                zsh_process_frames::decode_receipt(&h.output(writer), b"AEZER001", 2).unwrap(),
                -2
            );
            assert!(
                h.runtime
                    .zsh_stream(true, &frame(2, 0x79000102, 4, 0))
                    .unwrap()
            );
        } else {
            assert_eq!(observed, Err(-5));
            assert!(!h.host.0.borrow().calls.contains(&(0x23005, CHILD, 101)));
        }
        assert_eq!(h.runtime.process.binding, old);
        assert!(!h.runtime.process.committed);
        assert!(!h.host.0.borrow().calls.iter().any(|r| r.0 == 0x23009));
    }
}
#[test]
fn failed_wait_delivery_keeps_reserved_status_child_lease_and_no_reclaim() {
    let mut h = Fixture::new();
    let raw = h.fork(false);
    let mut work = h.exec_request(&raw);
    h.runtime.zsh_exec(&mut work).unwrap();
    h.host.0.borrow_mut().ready = true;
    h.runtime.zsh_terminal().unwrap();
    h.host.0.borrow_mut().terminal = Some((8, 1, 1));
    h.runtime.zsh_terminal().unwrap();
    h.clear();
    h.host.0.borrow_mut().fail_write = Some((PW, 16));
    let wait = frame(68, u32::MAX, 1, 0);
    assert_eq!(h.runtime.zsh_stream(false, &wait), Err(-5));
    assert_eq!(h.output(PW).len(), 16);
    assert_eq!(h.runtime.process.wait_status, None);
    assert!(!h.host.0.borrow().gone);
    assert!(!h.runtime.process.reclaimed);
    assert_ne!(h.runtime.process.lease, ReadLease::Parent);
    assert_eq!(h.runtime.process.children.wait(-1, true), Err(-16));
}
#[test]
fn stale_malformed_copy_unknown_and_reserve_exhaustion_have_no_fabricated_commit() {
    for mode in 0..4 {
        let mut h = Fixture::new();
        let raw = h.snapshot(false);
        let expected = h.runtime.zsh_expected(false).unwrap();
        let mut fork = [0; 368];
        zsh_process_frames::encode_fork(&raw, expected, 1, &mut fork).unwrap();
        match mode {
            0 => fork[32 + 56] ^= 1,
            1 => fork[24] = 1,
            2 => h.runtime.bound.left = 5,
            _ => h.host.0.borrow_mut().copy_result = 1,
        }
        let mut work = [0; 4096];
        work[..368].copy_from_slice(&fork);
        assert!(h.runtime.zsh_fork(&mut work).is_err());
        assert_eq!(h.runtime.bound.reserved, RESERVED);
        if mode < 3 {
            assert!(!h.host.0.borrow().calls.iter().any(|v| v.0 == 0x23006));
        } else {
            assert_eq!(h.runtime.process.ends.iter().filter(|e| e.owned).count(), 2);
            assert!(h.host.0.borrow().closed.is_empty());
        }
    }
}
#[test]
fn full_duplex_snapshot_keeps_byte3_and_aggregate_cloexec_projection() {
    let h = Fixture::new();
    let mut raw = h.snapshot(false);
    raw[112..116].copy_from_slice(&[5, 0, 1, 16]);
    raw[116..120].fill(0);
    let expected = h.runtime.zsh_expected(false).unwrap();
    let plan = zsh_stream_plan(&raw, expected).unwrap();
    assert_eq!(plan.bindings[0].kind, 1);
    assert_eq!(plan.bindings[1].kind, 1);
    assert_eq!(raw[115], 16);
    let id = Identity::admitted(2, 1, CHILD).unwrap();
    zsh_rebind_snapshot(&mut raw, id, 9, 700).unwrap();
    assert_eq!(raw[115], 16);
    zsh_exec_snapshot(&mut raw).unwrap();
    assert_eq!(&raw[112..120], &[0; 8]);
}

#[test]
fn fixed_catalog_missing_and_all_other_nonhelper_paths_preserve_old_image() {
    for (path, code) in [
        (b"/inputs/missing".as_slice(), -2),
        (b"/inputs/denied".as_slice(), -13),
        (b"/inputs/other".as_slice(), -13),
    ] {
        let mut h = Fixture::new();
        let raw = h.fork(false);
        let mut work = h.exec_request(&raw);
        work[368..400].fill(0);
        work[368..368 + path.len()].copy_from_slice(path);
        h.runtime.zsh_exec(&mut work).unwrap();
        assert!(
            !h.host
                .0
                .borrow()
                .calls
                .iter()
                .any(|x| matches!(x.0, 0x23007 | 0x2300b))
        );
        let writer = h.runtime.process.ends[3].cap;
        assert_eq!(
            zsh_process_frames::decode_receipt(&h.output(writer), b"AEZER001", 2).unwrap(),
            if cfg!(native_zsh_file_exec) {
                -13
            } else {
                code
            }
        );
        assert!(!h.runtime.process.committed);
    }
}
#[test]
fn known_copy_refusal_closes_only_owner_ends_thaws_and_preserves_parent_lease() {
    let mut h = Fixture::new();
    h.host.0.borrow_mut().copy_result = -11;
    let raw = h.snapshot(false);
    let mut fork = [0; 368];
    zsh_process_frames::encode_fork(&raw, h.runtime.zsh_expected(false).unwrap(), 1, &mut fork)
        .unwrap();
    let mut work = [0; 4096];
    work[..368].copy_from_slice(&fork);
    h.runtime.zsh_fork(&mut work).unwrap();
    assert_eq!(
        zsh_process_frames::decode_receipt(&h.output(PW), b"AEZFR001", 1).unwrap(),
        -11
    );
    assert_eq!(h.host.0.borrow().closed.len(), 4);
    assert!(
        h.runtime
            .process
            .ends
            .iter()
            .all(|e| e.attempted && e.status == 0)
    );
    assert_eq!(h.runtime.process.lease, ReadLease::Parent);
    assert!(h.runtime.process.binding.is_none());
    assert_eq!(h.runtime.bound.reserved, RESERVED);
    assert!(h.host.0.borrow().calls.contains(&(0x23005, PARENT, 101)));
}
#[test]
fn selected_header_shapes_and_partial_poll_preserve_frame_boundaries() {
    for q in [
        frame(1, 0x7a000001, 0, 16),
        frame(2, 0x79000102, 4, 1),
        frame(3, 0x79000101, 3, 0),
        frame(82, 0x76050001, 1, 0),
        frame(68, u32::MAX, 11, 0),
        frame(0x10, tty_mode::CONTROL, 0, 0),
    ] {
        assert!(zsh_small_header(&q, false));
    }
    for q in [
        frame(4, 0x7a000001, 0, 0),
        frame(1, 0x79000001, 3, 1),
        frame(1, 0x79000a01, 3, 1),
        frame(1, 0x7a000001, 0, 17),
        frame(3, 0x7a000001, 0, 1),
        frame(82, 0x76050001, 0, 0),
        frame(68, 9, 0, 0),
        frame(68, 10, 4, 0),
        frame(0x13, tty_mode::CONTROL, 0, 0),
    ] {
        assert!(!zsh_small_header(&q, false));
    }
    assert!(!zsh_small_header(&frame(68, 10, 0, 0), true));
    assert!(!zsh_small_header(&frame(82, 0x76050001, 1, 0), true));
    let mut h = Fixture::new();
    let q = frame(2, 0x7a010001, 1, 0);
    h.feed(PR, &q[..8]);
    assert_eq!(h.runtime.zsh_poll(false, &mut [0; 4096]), Ok(Some(true)));
    assert_eq!(h.runtime.process.parent_at, 8);
    assert_eq!(h.runtime.zsh_poll(false, &mut [0; 4096]), Ok(None));
    h.feed(PR, &q[8..]);
    assert_eq!(h.runtime.zsh_poll(false, &mut [0; 4096]), Ok(Some(true)));
    assert_eq!(h.runtime.process.parent_at, 0);
    assert_eq!(h.output(PW), [0; 32]);
}

// Full fatal path: each branch uses the real Runtime body and the same child
// credits debited before copy. Mocked ctl outputs are explicit observations;
// an unknown query is deliberately not converted to a terminal/reclaim proof.
#[test]
fn contain_live_and_unknown_copy_settle_known_child_once_without_replay() {
    for unknown_copy in [false, true] {
        let mut h = Fixture::new();
        if unknown_copy {
            h.host.0.borrow_mut().copy_result = 1;
            let raw = h.snapshot(false);
            let mut request = [0; 368];
            zsh_process_frames::encode_fork(
                &raw,
                h.runtime.zsh_expected(false).unwrap(),
                1,
                &mut request,
            )
            .unwrap();
            let mut work = [0; 4096];
            work[..368].copy_from_slice(&request);
            assert_eq!(h.runtime.zsh_fork(&mut work), Err(-5));
            assert!(h.runtime.process.endpoints.is_none());
        } else {
            h.fork(false);
        }
        let child_ends = h.runtime.process.ends.map(|end| end.cap);
        assert_eq!(h.runtime.process.prepaid, 6);
        assert_eq!(h.runtime.bound.reserved, RESERVED);
        h.runtime.bound.left = 0;
        h.runtime.bound.failed = -110;
        let calls_before = h.host.0.borrow().calls.len();
        assert_eq!(h.runtime.contain(), Err(-5));
        let host = h.host.0.borrow();
        let child_calls: Vec<_> = host.calls[calls_before..]
            .iter()
            .copied()
            .filter(|(_, cap, _)| *cap == CHILD)
            .collect();
        assert_eq!(
            child_calls,
            [
                (0x20007, CHILD, 0),
                (0x20001, CHILD, 0),
                (0x20002, CHILD, 0),
                (0x20001, CHILD, 0)
            ]
        );
        assert!(host.gone);
        assert!(host.parent_gone);
        assert_eq!(
            host.closed,
            [child_ends[0], child_ends[3], NSR, NSW, PR, PW]
        );
        assert!(
            !host.closed.contains(&child_ends[1]) && !host.closed.contains(&child_ends[2]),
            "TRANSFERRED_ENDS_ARE_NOT_OWNER_CLOSES"
        );
        assert_eq!(
            host.calls.iter().filter(|call| call.0 == 0x23006).count(),
            1
        );
        assert!(
            !host
                .calls
                .iter()
                .any(|call| matches!(call.0, 0x23007 | 0x2300b | 0x23009))
        );
        assert_eq!(
            host.calls
                .iter()
                .filter(|call| call.0 == 0x20007 && call.1 == CHILD)
                .count(),
            1
        );
        let calls = host.calls.clone();
        let closes = host.closed.clone();
        drop(host);
        assert_eq!(h.runtime.process.prepaid, 0);
        assert_eq!(h.runtime.process.cleanup_attempted, 15);
        assert_eq!(h.runtime.process.cleanup_last, (-9, 0, 0));
        assert_eq!(h.runtime.process.lease, ReadLease::Contained);
        assert_eq!(h.runtime.process.wait_status, None);
        assert!(!h.runtime.process.exec_ready && !h.runtime.process.reclaimed);
        assert_eq!(h.runtime.bound.left, 0);
        // Four original Parent lifecycle calls + its two physical-end closes +
        // console close + terminal failure leaf use8. Child's6 use no reserve.
        assert_eq!(h.runtime.bound.reserved, RESERVED - 8);
        assert_eq!(h.runtime.cleanup_attempted[0], [true; 4]);
        assert_eq!(h.runtime.cleanup_attempted[1], [false; 4]);
        assert_eq!(h.runtime.contain(), Err(-5));
        assert_eq!(h.host.0.borrow().calls, calls);
        assert_eq!(h.host.0.borrow().closed, closes);
    }
}
#[test]
fn contain_unknown_copy_unknown_terminal_never_reclaims_or_restores_parent_lease() {
    let mut h = Fixture::new();
    h.host.0.borrow_mut().copy_result = 1;
    let raw = h.snapshot(false);
    let mut request = [0; 368];
    zsh_process_frames::encode_fork(
        &raw,
        h.runtime.zsh_expected(false).unwrap(),
        1,
        &mut request,
    )
    .unwrap();
    let mut work = [0; 4096];
    work[..368].copy_from_slice(&request);
    assert_eq!(h.runtime.zsh_fork(&mut work), Err(-5));
    h.host.0.borrow_mut().stop_observation = (-5, 0, 0);
    let child_ends = h.runtime.process.ends.map(|end| end.cap);
    let before = h.host.0.borrow().calls.len();
    assert_eq!(h.runtime.contain(), Err(-5));
    let host = h.host.0.borrow();
    let child_calls: Vec<_> = host.calls[before..]
        .iter()
        .copied()
        .filter(|(_, cap, _)| *cap == CHILD)
        .collect();
    assert_eq!(child_calls, [(0x20007, CHILD, 0), (0x20001, CHILD, 0)]);
    assert!(!host.gone, "UNKNOWN_TERMINAL_MUST_NOT_RECLAIM");
    assert_eq!(
        host.closed,
        [child_ends[0], child_ends[3], NSR, NSW, PR, PW]
    );
    assert_eq!(
        host.calls.iter().filter(|call| call.0 == 0x23006).count(),
        1
    );
    assert!(
        !host
            .calls
            .iter()
            .any(|call| matches!(call.0, 0x23007 | 0x2300b | 0x23009))
    );
    let calls = host.calls.clone();
    let closes = host.closed.clone();
    drop(host);
    assert_eq!(h.runtime.process.cleanup_attempted, 3);
    assert_eq!(h.runtime.process.cleanup_last, (-5, 0, 0));
    assert_eq!(
        h.runtime.process.prepaid, 2,
        "UNUSED_PREPAID_IS_NOT_REFUNDED_OR_RENEWED"
    );
    assert_eq!(h.runtime.bound.reserved, RESERVED - 8);
    assert_eq!(h.runtime.process.lease, ReadLease::Contained);
    assert_eq!(h.runtime.process.wait_status, None);
    assert!(h.runtime.process.binding.is_some());
    assert!(!h.runtime.process.reclaimed);
    assert_eq!(h.runtime.contain(), Err(-5));
    assert_eq!(h.host.0.borrow().calls, calls);
    assert_eq!(h.host.0.borrow().closed, closes);
}

#[cfg(not(native_zsh_file_exec))]
#[test]
fn fixed_helper_arguments_follow_selected_workload() {
    let mut raw = [0; 272];
    raw[..8].copy_from_slice(&2u64.to_le_bytes());
    raw[16..30].copy_from_slice(b"/inputs/helper");
    for argument in [
        b"status".as_slice(),
        b"home-write",
        b"home-writ",
        b"home-write-extra",
    ] {
        raw[48..].fill(0);
        raw[48..48 + argument.len()].copy_from_slice(argument);
        assert_eq!(
            zsh_helper_arguments(&raw),
            argument
                == if cfg!(native_zsh_home_write) {
                    b"home-write".as_slice()
                } else {
                    b"status".as_slice()
                },
            "SELECTED_HELPER_ARGUMENT"
        );
    }
    raw[48..].fill(0);
    let selected = if cfg!(native_zsh_home_write) {
        b"home-write".as_slice()
    } else {
        b"status".as_slice()
    };
    raw[48..48 + selected.len()].copy_from_slice(selected);
    for byte in [8, 30, 80, 271] {
        raw[byte] = 1;
        assert!(!zsh_helper_arguments(&raw), "SELECTED_HELPER_PADDING");
        raw[byte] = 0;
    }
}

#[cfg(native_zsh_home_write)]
#[test]
fn actual_ready_arms_only_executed_helper_and_completed_write_close_gates_v3() {
    let mut h = Fixture::new();
    let raw = h.fork(false);
    let binding = h.runtime.process.binding.unwrap();
    assert!(
        h.runtime
            .with_files(|f| f.admit_home_write(binding))
            .is_err(),
        "NO_PREEXEC_WRITE_ADMISSION"
    );
    let mut request = h.exec_request(&raw);
    h.runtime.zsh_exec(&mut request).unwrap();
    h.runtime.zsh_terminal().unwrap();
    assert!(!h.runtime.process.exec_ready);
    let denied = h.home_file_request(12, 1, 0, b"/home/probe").unwrap();
    assert!(
        i64::from_le_bytes(denied[8..16].try_into().unwrap()) < 0,
        "NO_WRITE_BEFORE_NATIVE_READY"
    );
    h.host.0.borrow_mut().ready = true;
    h.runtime.zsh_terminal().unwrap();
    // The denied pre-READY request consumed FILE sequence1 without a namespace effect.
    h.complete_home_write(2);
    h.collect_helper_zero();
    h.prepare_healthy_oracle();
    // SAFETY: fixture owns the successfully initialized Runtime final slot.
    assert!(unsafe { h.runtime.files.assume_init_ref() }.home_write_complete());
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
    let bytes = &h.host.0.borrow().serial_output;
    assert!(
        bytes
            .windows(b"child_status=0".len())
            .any(|s| s == b"child_status=0")
    );
    assert!(
        bytes
            .windows(b"write_bytes=16 write_closed=1".len())
            .any(|s| s == b"write_bytes=16 write_closed=1")
    );
}
#[cfg(native_zsh_home_write)]
#[test]
fn no_write_completion_cannot_emit_v3_after_other_healthy_cleanup() {
    let mut h = Fixture::new();
    h.helper_ready();
    h.collect_helper_zero();
    h.prepare_healthy_oracle();
    assert_eq!(
        h.runtime.write_native_oracle(&mut [0; 4096]),
        Err(-5),
        "HOME_WRITE_FACTS_BEFORE_ORACLE"
    );
    assert!(h.host.0.borrow().serial_output.is_empty());
}
#[cfg(native_zsh_home_write)]
#[test]
fn retired_write_source_delivers_one_retained_error_then_contains_without_replay() {
    for failure in [1, 2] {
        let mut h = Fixture::with_probe_failure(failure);
        h.helper_ready();
        let fd = h.open_home_write(1);
        assert_eq!(
            h.home_file_request(11, 2, fd as u64, b"AETHER-ZSH-HOME\n"),
            Err(-5),
            "NO_RESUME_AFTER_SOURCE_CLOSE"
        );
        let out = h.output(h.runtime.process.ends[3].cap);
        assert_eq!(out.len(), 128, "RETAINED_ERROR_RECEIPT_DELIVERED");
        assert_eq!(i64::from_le_bytes(out[8..16].try_into().unwrap()), -5);
        assert_eq!(u64::from_le_bytes(out[40..48].try_into().unwrap()), 64);
        // SAFETY: fixture still owns the initialized slot after source close.
        assert!(!unsafe { h.runtime.files.assume_init_ref() }.home_write_complete());
        // SAFETY: same initialized final slot; only retained cleanup is read.
        assert!(
            unsafe { h.runtime.files.assume_init_ref() }
                .cleanup()
                .is_some()
        );
        assert!(h.host.0.borrow().serial_output.is_empty());
        assert!(!h.runtime.process.reclaimed);
    }
}

#[cfg(native_zsh_file_exec)]
#[test]
fn file_exec_requires_exact_single_argument_and_no_environment_or_padding() {
    let mut args = [0; 272];
    args[..8].copy_from_slice(&1u64.to_le_bytes());
    args[16..27].copy_from_slice(b"/home/probe");
    assert!(zsh_helper_arguments(&args), "SINGLE_FILE_EXEC_ARGUMENT");
    for at in [0, 8, 16, 27, 48, 144, 271] {
        args[at] ^= 1;
        assert!(!zsh_helper_arguments(&args), "CLOSED_FILE_EXEC_VECTOR");
        args[at] ^= 1;
    }
}
#[cfg(native_zsh_file_exec)]
#[test]
fn file_exec_acquisition_failure_never_calls_kernel_or_replays_close() {
    for opcode in [2, 3] {
        let mut h = Fixture::new();
        let raw = h.fork(false);
        let old = h.runtime.process.binding;
        h.host.0.borrow_mut().fail_namespace_opcode = Some(opcode);
        let mut work = h.exec_request(&raw);
        assert_eq!(
            h.runtime.zsh_exec(&mut work),
            Err(-5),
            "NO_EXEC_AFTER_UNKNOWN_ACQUISITION"
        );
        assert_eq!(h.runtime.process.binding, old);
        assert!(!h.runtime.process.committed);
        assert!(work.iter().all(|byte| *byte == 0));
        assert!(
            !h.host
                .0
                .borrow()
                .calls
                .iter()
                .any(|call| matches!(call.0, 0x23007 | 0x2300b | 0x23009)),
            "NO_FILE_EXEC_AFTER_FAILED_CLOSE"
        );
        let calls = h.host.0.borrow().calls.clone();
        let closes = h.host.0.borrow().closed.clone();
        assert_eq!(
            h.runtime
                .with_files(|files| files.acquire_file_exec(old.unwrap(), &mut work)),
            Err(-5)
        );
        assert_eq!(h.host.0.borrow().calls, calls);
        assert_eq!(
            h.host.0.borrow().closed,
            closes,
            "NO_ACQUISITION_CLOSE_REPLAY"
        );
    }
}

#[cfg(native_zsh_file_exec)]
#[test]
fn file_exec_wrong_source_receipt_never_rebinds_or_publishes() {
    let mut h = Fixture::new();
    let raw = h.fork(false);
    let old = h.runtime.process.binding;
    h.host.0.borrow_mut().file_receipt_tag = 0xc003;
    let mut work = h.exec_request(&raw);
    assert_eq!(
        h.runtime.zsh_exec(&mut work),
        Err(-5),
        "FILESYSTEM_SOURCE_RECEIPT_REQUIRED"
    );
    assert_eq!(h.runtime.process.binding, old);
    assert!(!h.runtime.process.committed);
    assert!(!h.host.0.borrow().calls.iter().any(|call| call.0 == 0x23009));
}
#[cfg(native_zsh_file_exec)]
#[test]
fn file_exec_v4_requires_actual_ready_and_exact_closed_acquisition() {
    let mut h = Fixture::new();
    h.helper_ready();
    h.host.0.borrow_mut().terminal = Some((24, 1, 1));
    h.runtime.zsh_terminal().unwrap();
    h.clear();
    assert!(
        h.runtime
            .zsh_stream(false, &frame(68, u32::MAX, 0, 0))
            .unwrap()
    );
    assert_eq!(result(&h.output(PW)[4..]), 5888);
    h.prepare_healthy_oracle();
    h.runtime.process.exec_ready = false;
    assert_eq!(
        h.runtime.write_native_oracle(&mut [0; 4096]),
        Err(-5),
        "ACTUAL_READY_BEFORE_FILE_EXEC_ORACLE"
    );
    assert!(h.host.0.borrow().serial_output.is_empty());
    h.runtime.process.exec_ready = true;
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
    let row = h.host.0.borrow().serial_output.clone();
    let expected = std::format!(
        "file_exec_bytes={:04} file_exec_closed=1 image_receipt=49156",
        FILE_EXEC_ELF.len()
    );
    assert!(
        row.windows(expected.len())
            .any(|bytes| bytes == expected.as_bytes()),
        "ACTUAL_CLOSED_ACQUISITION_FACTS"
    );
    assert!(
        row.windows(b"child_status=5888".len())
            .any(|bytes| bytes == b"child_status=5888")
    );
}

#[cfg(native_zsh_cold_reopen)]
#[test]
fn only_idle_exit_profile_accepts_a_pristine_no_child_shutdown() {
    let mut h = Fixture::new();
    h.prepare_healthy_oracle();
    let result = h.runtime.write_native_oracle(&mut [0; 4096]);
    let host = h.host.0.borrow();
    if cfg!(native_zsh_idle_exit) {
        assert_eq!(result, Ok(()), "PRISTINE_UNUSED_HELPER_EXIT");
        let expected = std::format!(
            "\nAETHER ZSH OWNER v=5 requests={:02} child=none helper_unused_closed=1 mode_cleanup=0\n",
            h.runtime.filesystem_requests
        );
        assert_eq!(host.serial_output, expected.as_bytes());
    } else {
        assert_eq!(result, Err(-5));
        assert!(host.serial_output.is_empty());
    }
}

#[cfg(native_zsh_idle_exit)]
#[test]
fn idle_exit_rejects_a_used_or_incomplete_child_lane() {
    let mut h = Fixture::new();
    h.host.0.borrow_mut().copy_result = -11;
    let raw = h.snapshot(false);
    let mut work = [0; 4096];
    zsh_process_frames::encode_fork(
        &raw,
        h.runtime.zsh_expected(false).unwrap(),
        1,
        (&mut work[..368]).try_into().unwrap(),
    )
    .unwrap();
    h.runtime.zsh_fork(&mut work).unwrap();
    assert!(h.runtime.process.binding.is_none());
    assert_eq!(h.runtime.process.epoch, 0);
    h.prepare_healthy_oracle();
    assert_eq!(h.runtime.write_native_oracle(&mut work), Err(-5));
    assert!(h.host.0.borrow().serial_output.is_empty());

    let mut h = Fixture::new();
    h.prepare_healthy_oracle();
    for dirty in 0..6 {
        h.runtime.process = ZshProcess::new();
        match dirty {
            0 => h.runtime.process.at = 1,
            1 => h.runtime.process.parent_at = 1,
            2 => h.runtime.process.wait_status = Some(5888),
            3 => h.runtime.process.exec_ready = true,
            4 => h.runtime.process.lease.contain(),
            _ => h
                .runtime
                .process
                .children
                .admit(ChildIdentity::admitted(2, 1, CHILD).unwrap())
                .unwrap(),
        }
        assert_eq!(
            h.runtime.write_native_oracle(&mut work),
            Err(-5),
            "dirty lane {dirty}"
        );
    }
    assert!(h.host.0.borrow().serial_output.is_empty());
}

#[cfg(native_zsh_idle_exit)]
#[test]
fn idle_exit_rejects_unconfirmed_engine_terminal_after_other_healthy_cleanup() {
    let mut h = Fixture::new();
    h.prepare_healthy_oracle();
    for terminal in [None, Some((6, 1, 1)), Some((1, 1, 2))] {
        h.runtime.observed_terminal[1] = terminal;
        assert_eq!(h.runtime.write_native_oracle(&mut [0; 4096]), Err(-5));
    }
    assert!(h.host.0.borrow().serial_output.is_empty());
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_phase_changes_check_the_outgoing_exclusive_deadline() {
    let mut h = Fixture::new();
    h.host.0.borrow_mut().event = (0, 1, 5999);
    h.runtime.operator_dispatch().unwrap();
    assert_eq!(h.runtime.bound.deadline.get(), 24000);
    h.host.0.borrow_mut().event = (0, 2, 23999);
    h.runtime.operator_teardown().unwrap();
    assert_eq!(h.runtime.bound.deadline.get(), 29999);
    for (deadline, tick, teardown) in [(6000, 6000, false), (24000, 24000, true)] {
        let mut h = Fixture::new();
        h.runtime.bound.deadline = Deadline::after(0, deadline).unwrap();
        h.host.0.borrow_mut().event = (0, 1, tick);
        assert_eq!(
            if teardown {
                h.runtime.operator_teardown()
            } else {
                h.runtime.operator_dispatch()
            },
            Err(-110)
        );
        assert_eq!(h.runtime.bound.deadline.get(), deadline);
    }
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_pending_read_parks_with_the_pre_rescan_sequence() {
    let mut h = Fixture::new();
    h.runtime.engine = 0xb0000101;
    h.runtime.process.parent_at = 32;
    h.host
        .0
        .borrow_mut()
        .observations
        .extend([(0, 7, 10), (0, 8, 11)]);
    h.host.0.borrow_mut().wake = (0, 8, 7001);
    h.runtime.bound.deadline = Deadline::after(0, 24000).unwrap();
    let before = h.runtime.bound.left;
    assert!(
        !h.runtime
            .zsh_stream(false, &frame(1, 0x7a000001, 0, 1))
            .unwrap()
    );
    assert_eq!(h.host.0.borrow().parks, [(7, 24000)]);
    assert_eq!(h.runtime.bound.last_tick, 7001);
    assert!(
        before - h.runtime.bound.left < 40,
        "idle wake does not spend per idle tick"
    );
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_pending_read_rejects_bad_wakes_or_peer_terminal() {
    for wake in [
        (-110, 1, 1),
        (1, 1, 1),
        (0, 0, 1),
        (0, 1, 0),
        (0, u64::MAX, 1),
        (0, 1, 24000),
    ] {
        let mut h = Fixture::new();
        h.runtime.engine = 0xb0000101;
        h.runtime.process.parent_at = 32;
        h.runtime.bound.deadline = Deadline::after(0, 24000).unwrap();
        h.host.0.borrow_mut().wake = wake;
        assert!(
            h.runtime
                .zsh_stream(false, &frame(1, 0x7a000001, 0, 1))
                .is_err(),
            "wake {wake:?}"
        );
    }
    for parent in [true, false] {
        let mut h = Fixture::new();
        h.runtime.engine = 0xb0000101;
        h.runtime.process.parent_at = 32;
        if parent {
            h.host.0.borrow_mut().parent_state = Some((1, 1, 1));
        } else {
            h.host.0.borrow_mut().engine_state = (1, 1, 1);
        }
        assert_eq!(
            h.runtime.zsh_stream(false, &frame(1, 0x7a000001, 0, 1)),
            Err(-5)
        );
        assert!(h.host.0.borrow().parks.is_empty());
    }
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_invalid_or_partial_reads_do_not_park() {
    for (reference, n, at) in [
        (0x7a000002, 1, 32),
        (0x7a000001, 0, 32),
        (0x7a000001, 1, 16),
    ] {
        let mut h = Fixture::new();
        h.runtime.engine = 0xb0000101;
        h.runtime.process.parent_at = at;
        let _ = h
            .runtime
            .zsh_stream(false, &frame(1, reference, 0, n))
            .unwrap();
        assert!(h.host.0.borrow().parks.is_empty());
    }
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_pending_output_keeps_the_timed_transmit_path() {
    let mut h = Fixture::new();
    h.runtime.engine = 0xb0000101;
    h.runtime.process.parent_at = 32;
    let (terminal, refs, caller) = h.runtime.tty.as_mut().unwrap();
    let mut saved = terminal.snapshot(*caller, &refs.stdin).unwrap();
    terminal
        .apply_now(
            *caller,
            &refs.stdin,
            &mut saved,
            serial_tty::ModeRequest {
                mode: Mode::CANONICAL,
                action: serial_tty::ApplyWhen::Now,
            },
        )
        .unwrap();
    assert_eq!(
        terminal.write(*caller, &refs.stdout, b"x", |_, _| Completion {
            count: 0,
            stop: Stop::WouldBlock,
        }),
        Ok(1)
    );
    assert!(terminal.output_pending());
    h.host.0.borrow_mut().output_blocked = true;
    assert!(
        !h.runtime
            .zsh_stream(false, &frame(1, 0x7a000001, 0, 1))
            .unwrap()
    );
    assert!(h.host.0.borrow().parks.is_empty());
    assert_eq!(h.host.0.borrow().serial_reads, 0);
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_export_wait_keeps_the_pre_terminal_query_sequence() {
    let mut h = Fixture::new();
    h.runtime.bound.deadline = Deadline::after(0, 24000).unwrap();
    h.host.0.borrow_mut().event = (0, 7, 1);
    h.host.0.borrow_mut().wake = (0, 8, 2);
    h.host.0.borrow_mut().export_on_park = true;
    let engine = 0xb0000101;
    h.runtime
        .with_files(|files| {
            files
                .disconnect_checked(|io| io.verify_disconnect(engine))
                .map(|_| ())
        })
        .unwrap();
    assert_eq!(h.host.0.borrow().parks, [(7, 24000)]);
}

#[cfg(native_zsh_operator)]
#[test]
fn operator_pending_read_rejects_new_frame_and_terminal_after_wake() {
    let mut h = Fixture::new();
    h.runtime.engine = 0xb0000101;
    h.runtime.process.parent_at = 32;
    h.feed(PR, b"x");
    assert_eq!(
        h.runtime.zsh_stream(false, &frame(1, 0x7a000001, 0, 1)),
        Err(-5)
    );
    assert!(h.host.0.borrow().parks.is_empty());
    let mut h = Fixture::new();
    h.runtime.engine = 0xb0000101;
    h.runtime.process.parent_at = 32;
    h.host.0.borrow_mut().export_on_park = true;
    h.host.0.borrow_mut().wake = (0, 8, 2);
    assert_eq!(
        h.runtime.zsh_stream(false, &frame(1, 0x7a000001, 0, 1)),
        Err(-5)
    );
    assert_eq!(h.host.0.borrow().parks.len(), 1);
}

#[cfg(native_zsh_home_redirection)]
impl Fixture {
    fn note_request(
        &mut self,
        op: u64,
        sequence: u64,
        args: [u64; 4],
        body: &[u8],
    ) -> Result<Vec<u8>, i64> {
        let binding = self.runtime.file_binding.unwrap();
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(filesystem_readonly::MAGIC);
        for (index, value) in [
            op,
            binding.generation,
            sequence,
            args[0],
            args[1],
            args[2],
            args[3],
        ]
        .into_iter()
        .enumerate()
        {
            raw[(index + 1) * 8..(index + 2) * 8].copy_from_slice(&value.to_le_bytes());
        }
        self.runtime.file_header = raw;
        if !body.is_empty() {
            let mut padded = [0; 64];
            padded[..body.len()].copy_from_slice(body);
            self.feed(PR, &padded);
        }
        self.clear();
        self.runtime.file_request(&mut [0; 4096], false)?;
        Ok(self.output(PW))
    }
}
#[cfg(all(native_zsh_home_redirection, not(native_zsh_home_redirection_reader)))]
#[test]
fn note_live_alias_refuses_fork_before_freeze_or_native_copy() {
    let mut h = Fixture::new();
    let r = h
        .note_request(12, 1, [0, NOTE_PATH.len() as u64, 0o600, 0], NOTE_PATH)
        .unwrap();
    assert_eq!(i64::from_le_bytes(r[8..16].try_into().unwrap()), 0);
    let raw = h.snapshot(false);
    let mut work = [0; 4096];
    zsh_process_frames::encode_fork(
        &raw,
        h.runtime.zsh_expected(false).unwrap(),
        1,
        (&mut work[..368]).try_into().unwrap(),
    )
    .unwrap();
    let before = h.host.0.borrow().calls.len();
    assert_eq!(h.runtime.zsh_fork(&mut work), Err(-16));
    assert_eq!(h.host.0.borrow().calls.len(), before);
}
#[cfg(native_zsh_home_redirection)]
#[test]
fn note_incomplete_session_cannot_emit_success_oracle() {
    let mut h = Fixture::new();
    assert!(
        !h.runtime
            .with_files(|files| Ok(files.note_complete()))
            .unwrap()
    );
    h.prepare_healthy_oracle();
    assert_eq!(h.runtime.write_native_oracle(&mut [0; 4096]), Err(-5));
    assert!(h.host.0.borrow().serial_output.is_empty());
}

#[cfg(native_zsh_home_redirection)]
#[test]
fn note_explicit_read_close_allows_healthy_existing_no_child_marker() {
    let mut h = Fixture::new();
    let mut seq = 1;
    #[cfg(not(native_zsh_home_redirection_reader))]
    {
        let r = h
            .note_request(12, seq, [0, NOTE_PATH.len() as u64, 0o600, 0], NOTE_PATH)
            .unwrap();
        seq += 1;
        let fd = u64::from_le_bytes(r[32..40].try_into().unwrap());
        let r = h.note_request(11, seq, [fd, 16, 0, 0], NOTE_BYTES).unwrap();
        seq += 1;
        assert_eq!(i64::from_le_bytes(r[8..16].try_into().unwrap()), 0);
        h.note_request(5, seq, [fd, 0, 0, 0], b"").unwrap();
        seq += 1;
    }
    let r = h
        .note_request(1, seq, [0, NOTE_PATH.len() as u64, 0, 0], NOTE_PATH)
        .unwrap();
    seq += 1;
    let fd = u64::from_le_bytes(r[32..40].try_into().unwrap());
    let r = h.note_request(2, seq, [fd, 16, 0, 0], b"").unwrap();
    seq += 1;
    assert_eq!(&r[64..80], NOTE_BYTES);
    h.note_request(5, seq, [fd, 0, 0, 0], b"").unwrap();
    assert!(
        h.runtime
            .with_files(|files| Ok(files.note_complete()))
            .unwrap()
    );
    h.prepare_healthy_oracle();
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
    let host = h.host.0.borrow();
    assert!(
        host.serial_output
            .windows(8)
            .any(|bytes| bytes == b"child=no")
    );
}

#[cfg(native_zsh_home_redirection)]
#[test]
fn note_launch_codec_matches_actual_login_selection_without_false_cwd() {
    let mut raw = [0u8; 320];
    encode_launch(&mut raw, 1, 2, 3).unwrap();
    let values: [&[u8]; 8] = if cfg!(native_zsh_login_startup) {
        [
            b"zsh",
            b"-d",
            b"-il",
            b"+m",
            b"TERM=vt100",
            b"LC_ALL=C",
            b"HOME=/home",
            b"PWD=/",
        ]
    } else {
        [
            b"zsh",
            b"-f",
            b"-i",
            b"+m",
            b"TERM=vt100",
            b"LC_ALL=C",
            b"HOME=/",
            b"PWD=/",
        ]
    };
    assert_eq!(u64::from_le_bytes(raw[16..24].try_into().unwrap()), 4);
    assert_eq!(u64::from_le_bytes(raw[24..32].try_into().unwrap()), 4);
    for (i, value) in values.iter().enumerate() {
        let slot = &raw[32 + i * 32..64 + i * 32];
        assert_eq!(&slot[..value.len()], *value);
        assert!(slot[value.len()..].iter().all(|v| *v == 0));
    }
}

#[cfg(all(native_zsh_home_cwd, not(native_zsh_home_cwd_exec)))]
#[test]
fn note_cwd_profile_refuses_fork_before_any_native_copy_or_freeze() {
    let mut h = Fixture::new();
    let before = h.host.0.borrow().calls.len();
    assert_eq!(h.runtime.zsh_fork(&mut [0; 4096]), Err(-95));
    assert_eq!(h.host.0.borrow().calls.len(), before);
    assert!(h.runtime.process.pristine());
}
#[cfg(native_zsh_home_cwd)]
#[test]
fn note_cwd_runtime_dispatch_observes_home_and_relative_read() {
    let mut h = Fixture::new();
    let r = h
        .note_request(1, 1, [0, NOTE_PATH.len() as u64, 0, 0], NOTE_PATH)
        .unwrap();
    let fd = u64::from_le_bytes(r[32..40].try_into().unwrap());
    h.note_request(2, 2, [fd, 16, 0, 0], b"").unwrap();
    h.note_request(5, 3, [fd, 0, 0, 0], b"").unwrap();
    let r = h.note_request(13, 4, [0, 5, 0, 0], b"/home").unwrap();
    assert_eq!(i64::from_le_bytes(r[8..16].try_into().unwrap()), 0);
    let r = h.note_request(9, 5, [0; 4], b"").unwrap();
    assert_eq!(u64::from_le_bytes(r[40..48].try_into().unwrap()), 6);
    assert_eq!(&r[64..70], b"/home\0");
    let r = h.note_request(1, 6, [0, 9, 0, 0], b".zprofile").unwrap();
    let fd = u64::from_le_bytes(r[32..40].try_into().unwrap());
    h.note_request(2, 7, [fd, 16, 0, 0], b"").unwrap();
    h.note_request(5, 8, [fd, 0, 0, 0], b"").unwrap();
    assert!(
        h.runtime
            .with_files(|files| Ok(files.note_complete()))
            .unwrap()
    );
}

#[cfg(native_zsh_home_redirection)]
#[test]
fn note_namespace_only_selected_zero_body_directory_observation_is_admitted() {
    let mut h = Fixture::new();
    let before = h.runtime.filesystem_requests;
    h.runtime
        .with_files(|files| {
            files.configure(|io| {
                for opcode in [12u64, 13, 14, 15] {
                    if cfg!(native_zsh_home_cwd) && opcode == 14 {
                        continue;
                    }
                    let mut raw = [0; 64];
                    raw[..8].copy_from_slice(b"AFSRPC09");
                    raw[8..16].copy_from_slice(&opcode.to_le_bytes());
                    assert_eq!(io.send(&raw), Err(-22));
                }
                let mut raw = [0; 64];
                raw[..8].copy_from_slice(b"AFSRPC09");
                raw[8..16].copy_from_slice(&14u64.to_le_bytes());
                raw[40..48].copy_from_slice(&1u64.to_le_bytes());
                assert_eq!(io.send(&raw), Err(-22));
                Ok(())
            })
        })
        .unwrap();
    assert_eq!(h.runtime.filesystem_requests, before);
}

#[cfg(native_zsh_home_cwd_exec)]
impl Fixture {
    fn note_source_for_fork(&mut self) {
        let r = self
            .note_request(1, 1, [0, NOTE_PATH.len() as u64, 0, 0], NOTE_PATH)
            .unwrap();
        let fd = u64::from_le_bytes(r[32..40].try_into().unwrap());
        self.note_request(2, 2, [fd, 16, 0, 0], b"").unwrap();
        self.note_request(5, 3, [fd, 0, 0, 0], b"").unwrap();
        assert!(
            self.runtime
                .with_files(|files| Ok(files.note_fork_ready()))
                .unwrap()
        );
    }
    fn note_child_cwd_request(&mut self) -> Vec<u8> {
        let binding = self.runtime.process.binding.unwrap();
        let mut raw = [0; 64];
        raw[..8].copy_from_slice(filesystem_readonly::MAGIC);
        raw[8..16].copy_from_slice(&9u64.to_le_bytes());
        raw[16..24].copy_from_slice(&binding.generation.to_le_bytes());
        raw[24..32].copy_from_slice(&1u64.to_le_bytes());
        self.runtime.file_header = raw;
        self.clear();
        self.runtime.file_request(&mut [0; 4096], true).unwrap();
        self.output(self.runtime.process.ends[3].cap)
    }
}
#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn note_cwd_exec_fork_child_dispatch_observes_inherited_home() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.note_request(13, 4, [0, 5, 0, 0], b"/home").unwrap();
    let before = h.runtime.filesystem_requests;
    h.fork(false);
    assert_eq!(h.runtime.process.binding.unwrap().slot, 2);
    let r = h.note_child_cwd_request();
    assert_eq!(i64::from_le_bytes(r[8..16].try_into().unwrap()), 0);
    assert_eq!(u64::from_le_bytes(r[40..48].try_into().unwrap()), 6);
    assert_eq!(&r[64..70], b"/home\0");
    assert!(h.runtime.filesystem_requests > before);
    assert_eq!(h.runtime.process.epoch, 1);
}
#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn note_cwd_exec_unsettled_fork_refuses_before_native_effects() {
    // Initial phase5 and live read6 cannot be treated as a completed profile.
    for reading in [false, true] {
        let mut h = Fixture::new();
        if reading {
            h.note_request(1, 1, [0, NOTE_PATH.len() as u64, 0, 0], NOTE_PATH)
                .unwrap();
        }
        let raw = h.snapshot(false);
        let mut work = [0; 4096];
        zsh_process_frames::encode_fork(
            &raw,
            h.runtime.zsh_expected(false).unwrap(),
            1,
            (&mut work[..368]).try_into().unwrap(),
        )
        .unwrap();
        let before = h.host.0.borrow().calls.len();
        assert_eq!(h.runtime.zsh_fork(&mut work), Err(-16));
        assert_eq!(h.host.0.borrow().calls.len(), before);
        assert!(h.runtime.process.pristine());
    }
}
#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn note_cwd_exec_known_copy_refusal_does_not_publish_child_directory() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.note_request(13, 4, [0, 5, 0, 0], b"/home").unwrap();
    h.host.0.borrow_mut().copy_result = -11;
    let raw = h.snapshot(false);
    let mut work = [0; 4096];
    zsh_process_frames::encode_fork(
        &raw,
        h.runtime.zsh_expected(false).unwrap(),
        1,
        (&mut work[..368]).try_into().unwrap(),
    )
    .unwrap();
    h.clear();
    h.runtime.zsh_fork(&mut work).unwrap();
    assert_eq!(
        zsh_process_frames::decode_receipt(&h.output(PW), b"AEZFR001", 1).unwrap(),
        -11
    );
    assert!(h.runtime.process.binding.is_none());
    assert!(
        h.runtime
            .with_files(|files| Ok(files.note_fork_ready()))
            .unwrap()
    );
    assert_eq!(h.runtime.process.lease, ReadLease::Parent);
}

#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn note_cwd_exec_actual_exec_wait_settlement_restores_parent_directory() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.note_request(13, 4, [0, 5, 0, 0], b"/home").unwrap();
    let raw = h.fork(false);
    let mut work = h.exec_request(&raw);
    h.runtime.zsh_exec(&mut work).unwrap();
    let r = h.note_child_cwd_request();
    assert_eq!(&r[64..70], b"/home\0");
    h.host.0.borrow_mut().ready = true;
    h.runtime.zsh_terminal().unwrap();
    h.host.0.borrow_mut().terminal = Some((24, 1, 1));
    h.runtime.zsh_terminal().unwrap();
    h.clear();
    assert!(
        h.runtime
            .zsh_stream(false, &frame(68, u32::MAX, 0, 0))
            .unwrap()
    );
    assert_eq!(h.runtime.process.wait_status, Some(5888));
    assert!(h.runtime.process.reclaimed);
    assert_eq!(h.runtime.process.lease, ReadLease::Parent);
    assert!(h.runtime.process.binding.is_none());
    let r = h.note_request(9, 5, [0; 4], b"").unwrap();
    assert_eq!(&r[64..70], b"/home\0");
}
#[cfg(native_zsh_home_cwd_exec)]
#[test]
fn note_cwd_exec_unknown_copy_has_no_published_files_child() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.host.0.borrow_mut().copy_result = 1;
    let raw = h.snapshot(false);
    let mut work = [0; 4096];
    zsh_process_frames::encode_fork(
        &raw,
        h.runtime.zsh_expected(false).unwrap(),
        1,
        (&mut work[..368]).try_into().unwrap(),
    )
    .unwrap();
    h.clear();
    assert_eq!(h.runtime.zsh_fork(&mut work), Err(-5));
    assert!(h.runtime.process.binding.is_some());
    let child = h.runtime.process.binding.unwrap();
    assert!(
        h.runtime
            .with_files(|files| Ok(files.file_view(child).is_err()))
            .unwrap()
    );
    assert!(!h.runtime.process.committed);
    assert!(h.output(h.runtime.process.ends[3].cap).is_empty());
}

#[cfg(native_zsh_repeat_exec)]
impl Fixture {
    fn repeat_collect(&mut self) {
        self.host.0.borrow_mut().ready = true;
        self.runtime.zsh_terminal().unwrap();
        self.host.0.borrow_mut().terminal = Some((24, 1, 1));
        self.runtime.zsh_terminal().unwrap();
        self.clear();
        assert!(
            self.runtime
                .zsh_stream(false, &frame(68, u32::MAX, 0, 0))
                .unwrap()
        );
        assert_eq!(self.runtime.process.wait_status, Some(5888));
        assert!(self.runtime.process.reclaimed);
        assert_eq!(self.runtime.process.lease, ReadLease::Parent);
        assert!(self.runtime.process.binding.is_none());
    }
    fn repeat_fork(&mut self) -> [u8; 336] {
        let epoch = self.runtime.process.epoch + 1;
        let handle = 0xb0000000 | u64::from(epoch) << 8 | 3;
        let pid = 3 + 7 * u32::from(epoch);
        self.host.0.borrow_mut().copy_result = handle as i64;
        let sequence = self.runtime.process.fork_sequence + 1;
        let mut work = self.repeat_fork_work();
        self.clear();
        self.runtime.zsh_fork(&mut work).unwrap();
        let child_writer = self.runtime.process.ends[3].cap;
        let child = self.output(child_writer).try_into().unwrap();
        self.clear();
        self.runtime
            .zsh_child_ready(
                &zsh_process_frames::receipt(b"AEZFC001", sequence, i64::from(pid)).unwrap(),
            )
            .unwrap();
        self.clear();
        child
    }
    fn repeat_fork_work(&self) -> [u8; 4096] {
        let raw = self.snapshot(false);
        let mut work = [0; 4096];
        zsh_process_frames::encode_fork(
            &raw,
            self.runtime.zsh_expected(false).unwrap(),
            self.runtime.process.fork_sequence + 1,
            (&mut work[..368]).try_into().unwrap(),
        )
        .unwrap();
        work
    }
    fn repeat_exec(&mut self, raw: &[u8; 336]) -> Result<(), i64> {
        let mut work = self.repeat_exec_request(raw);
        self.runtime.zsh_exec(&mut work)
    }
    fn repeat_exec_request(&self, raw: &[u8; 336]) -> [u8; 4096] {
        let mut work = self.exec_request(raw);
        work[16..24].copy_from_slice(&(self.runtime.process.sequence + 1).to_le_bytes());
        work
    }
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_two_actual_exec_wait_lifetimes_keep_saved_request_and_parent() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.note_request(13, 4, [0, 5, 0, 0], b"/home").unwrap();
    for epoch in 1..=2 {
        let raw = h.repeat_fork();
        let mut work = h.repeat_exec_request(&raw);
        h.runtime.zsh_exec(&mut work).unwrap();
        assert_eq!(h.runtime.process.binding.unwrap().epoch, epoch);
        h.repeat_collect();
    }
    assert_eq!(
        h.host
            .0
            .borrow()
            .calls
            .iter()
            .filter(|x| x.0 == 0x2300b)
            .count(),
        2
    );
    let before = h.host.0.borrow().calls.len();
    let mut third = h.repeat_fork_work();
    assert_eq!(h.runtime.zsh_fork(&mut third), Err(-16));
    assert_eq!(
        h.host.0.borrow().calls.len(),
        before,
        "THIRD_DENIED_BEFORE_NATIVE_EFFECTS"
    );
    let r = h.note_request(9, 5, [0; 4], b"").unwrap();
    assert_eq!(&r[64..70], b"/home\0");
    h.prepare_healthy_oracle();
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
}

#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_first_success_and_full_settlement_are_required_before_effects() {
    for case in 0..7 {
        let mut h = Fixture::new();
        h.note_source_for_fork();
        let raw = h.repeat_fork();
        let mut work = h.repeat_exec_request(&raw);
        h.runtime.zsh_exec(&mut work).unwrap();
        h.repeat_collect();
        match case {
            0 => h.runtime.process.committed = false,
            1 => h.runtime.process.exec_ready = false,
            2 => h.runtime.process.terminal = Some(0),
            3 => h.runtime.process.wait_status = None,
            4 => h.runtime.process.reclaimed = false,
            5 => {
                h.runtime.process.ends[0].owned = true;
                h.runtime.process.ends[0].attempted = false;
            }
            _ => {
                h.runtime.process.ends[0].owned = true;
                h.runtime.process.ends[0].attempted = true;
                h.runtime.process.ends[0].status = -5;
            }
        }
        let mut work = h.repeat_fork_work();
        let before = h.host.0.borrow().calls.len();
        assert_eq!(h.runtime.zsh_fork(&mut work), Err(-16));
        assert_eq!(h.host.0.borrow().calls.len(), before);
        assert_eq!(h.runtime.process.epoch, 1);
    }
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_known_native_refusal_cannot_rearm_the_second_exec() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    let raw = h.repeat_fork();
    h.repeat_exec(&raw).unwrap();
    h.repeat_collect();
    let raw = h.repeat_fork();
    h.host.0.borrow_mut().exec_result = -11;
    h.repeat_exec(&raw).unwrap();
    assert!(!h.runtime.process.committed);
    assert!(
        h.runtime
            .with_files(|f| Ok(f.file_exec_repeated()))
            .unwrap()
    );
    let count = h
        .host
        .0
        .borrow()
        .calls
        .iter()
        .filter(|x| x.0 == 0x2300b)
        .count();
    assert!(h.repeat_exec(&raw).is_err());
    assert_eq!(
        h.host
            .0
            .borrow()
            .calls
            .iter()
            .filter(|x| x.0 == 0x2300b)
            .count(),
        count
    );
    assert!(!h.runtime.process.committed);
}
#[cfg(native_zsh_repeat_exec)]
#[test]
fn repeat_final_oracle_rejects_pristine_or_only_first_success() {
    for count in 0..2 {
        let mut h = Fixture::new();
        h.note_source_for_fork();
        if count == 1 {
            let raw = h.repeat_fork();
            h.repeat_exec(&raw).unwrap();
            h.repeat_collect();
        }
        h.prepare_healthy_oracle();
        assert_eq!(h.runtime.write_native_oracle(&mut [0; 4096]), Err(-5));
        assert!(h.host.0.borrow().serial_output.is_empty());
    }
}

#[cfg(all(native_zsh_home_cwd_exec, not(native_zsh_repeat_exec)))]
#[test]
fn note_cwd_exec_pristine_after_profile_retains_optional_idle_oracle() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    assert!(h.runtime.process.pristine());
    h.prepare_healthy_oracle();
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
    let expected = std::format!(
        "\nAETHER ZSH OWNER v=5 requests={:02} child=none helper_unused_closed=1 mode_cleanup=0\n",
        h.runtime.filesystem_requests
    );
    assert_eq!(h.host.0.borrow().serial_output, expected.as_bytes());
}

#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_three_actual_cycles_keep_parent_and_saved_exec_request() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    for epoch in 1..=3 {
        let before = h.runtime.filesystem_requests;
        let raw = h.repeat_fork();
        h.repeat_exec(&raw).unwrap();
        assert_eq!(
            h.runtime.filesystem_requests - before,
            if epoch == 1 { 5 } else { 9 }
        );
        assert_eq!(h.runtime.process.binding.unwrap().epoch, epoch);
        h.repeat_collect();
    }
    h.prepare_healthy_oracle();
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_startup_publishes_home_pwd() {
    let mut out = [0; 320];
    encode_launch(&mut out, 1, 2, 3).unwrap();
    assert_eq!(&out[256..265], b"PWD=/home");
}

#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_zero_one_or_three_clean_exits_and_dirty_last_rejection() {
    for count in [0, 1, 3] {
        let mut h = Fixture::new();
        h.note_source_for_fork();
        for _ in 0..count {
            let raw = h.repeat_fork();
            h.repeat_exec(&raw).unwrap();
            h.repeat_collect();
        }
        h.prepare_healthy_oracle();
        h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
        let row = h.host.0.borrow().serial_output.clone();
        assert!(row.starts_with(if count == 0 {
            b"\nAETHER ZSH OWNER v=5"
        } else {
            b"\nAETHER ZSH OWNER v=4"
        }));
        if count > 0 {
            h.clear();
            h.host.0.borrow_mut().serial_output.clear();
            h.runtime.process.reclaimed = false;
            assert_eq!(h.runtime.write_native_oracle(&mut [0; 4096]), Err(-5));
            assert!(h.host.0.borrow().serial_output.is_empty());
        }
    }
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_resource_refusal_thaws_parent_correlates_and_preserves_last_child() {
    for count in [0, 1, 3] {
        let mut h = Fixture::new();
        h.note_source_for_fork();
        for _ in 0..count {
            let raw = h.repeat_fork();
            h.repeat_exec(&raw).unwrap();
            h.repeat_collect();
        }
        let epoch = h.runtime.process.epoch;
        let sequence = h.runtime.process.fork_sequence + 1;
        h.runtime.filesystem_requests = 90;
        let before = h.host.0.borrow().calls.len();
        let mut work = h.repeat_fork_work();
        h.clear();
        h.runtime.zsh_fork(&mut work).unwrap();
        assert_eq!(
            zsh_process_frames::decode_receipt(&h.output(PW), b"AEZFR001", sequence),
            Ok(-28)
        );
        assert_eq!(h.runtime.process.fork_sequence, sequence);
        assert_eq!(h.runtime.process.epoch, epoch);
        assert_eq!(h.runtime.filesystem_requests, 90);
        let calls = h.host.0.borrow().calls[before..].to_vec();
        assert!(calls.contains(&(0x23004, PARENT, 0)));
        assert!(calls.contains(&(0x23005, PARENT, 101)));
        assert!(
            !calls
                .iter()
                .any(|v| matches!(v.0, 0x24000 | 0x23006 | 0x2300b))
        );
        assert!(h.runtime.process.binding.is_none());
        assert_eq!(h.runtime.process.lease, ReadLease::Parent);
        // A new request consumes a fresh sequence; replay is rejected.
        assert!(h.runtime.zsh_fork(&mut work).is_err());
        h.prepare_healthy_oracle();
        h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
    }
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_epoch_limit_refuses_without_child_effects() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    let raw = h.repeat_fork();
    h.repeat_exec(&raw).unwrap();
    h.repeat_collect();
    // Isolate the actual generation ceiling after proving a real settled lane.
    h.runtime.process.epoch = 15;
    let mut work = h.repeat_fork_work();
    // The authenticated FileExec epoch remains1, so a forged ceiling cannot
    // bypass the complete prior-generation guard or cause a freeze/copy.
    let before = h.host.0.borrow().calls.len();
    assert_eq!(h.runtime.zsh_fork(&mut work), Err(-16));
    assert_eq!(h.host.0.borrow().calls.len(), before);
}

#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_actual_file_dispatch_preserves_reserved_shutdown_and_profile_completion() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.runtime.filesystem_requests = 93;
    let r = h.note_request(13, 4, [0, 1, 0, 0], b"/").unwrap();
    assert_eq!(u64::from_le_bytes(r[8..16].try_into().unwrap()) as i64, -28);
    assert_eq!(h.runtime.filesystem_requests, 93);
    assert!(h.runtime.with_files(|f| Ok(f.note_fork_ready())).unwrap());
    h.prepare_healthy_oracle();
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
    assert_eq!(h.runtime.filesystem_requests, 96);
}
#[cfg(native_zsh_operator_login)]
#[test]
fn operator_login_fixed_control_shortage_refuses_before_channel_or_copy() {
    let mut h = Fixture::new();
    h.note_source_for_fork();
    h.runtime.bound.left = 31;
    let mut work = h.repeat_fork_work();
    h.clear();
    h.runtime.zsh_fork(&mut work).unwrap();
    assert_eq!(
        zsh_process_frames::decode_receipt(&h.output(PW), b"AEZFR001", 1),
        Ok(-28)
    );
    assert_eq!(h.runtime.process.epoch, 0);
    assert!(
        !h.host
            .0
            .borrow()
            .calls
            .iter()
            .any(|v| matches!(v.0, 0x24000 | 0x23006))
    );
}

#[cfg(native_zsh_operator_note)]
#[test]
fn operator_note_fork_refuses_with_a_live_description_and_recovers_after_close() {
    let mut h = Fixture::new();
    let profile = h
        .note_request(1, 1, [0, NOTE_PATH.len() as u64, 0, 0], NOTE_PATH)
        .unwrap();
    let profile_fd = u64::from_le_bytes(profile[32..40].try_into().unwrap());
    h.note_request(2, 2, [profile_fd, 16, 0, 0], b"").unwrap();
    h.note_request(2, 3, [profile_fd, 1, 0, 0], b"").unwrap();
    h.note_request(5, 4, [profile_fd, 0, 0, 0], b"").unwrap();
    let path = b"/home/note";
    let r = h
        .note_request(1, 5, [0, path.len() as u64, 0, 0], path)
        .unwrap();
    assert_eq!(i64::from_le_bytes(r[8..16].try_into().unwrap()), 0);
    let fd = u64::from_le_bytes(r[32..40].try_into().unwrap());
    let mut raw = h.snapshot(false);
    raw[124..128].copy_from_slice(&[3, fd as u8, 0, 0]);
    let mut work = [0; 4096];
    zsh_process_frames::encode_fork(
        &raw,
        h.runtime.zsh_expected(false).unwrap(),
        1,
        (&mut work[..368]).try_into().unwrap(),
    )
    .unwrap();
    let before = h.runtime.filesystem_requests;
    let calls = h.host.0.borrow().calls.len();
    h.clear();
    h.runtime.zsh_fork(&mut work).unwrap();
    assert_eq!(
        zsh_process_frames::decode_receipt(&h.output(PW), b"AEZFR001", 1),
        Ok(-16)
    );
    assert_eq!(h.runtime.filesystem_requests, before);
    assert_eq!(h.runtime.process.epoch, 0);
    assert!(
        !h.host.0.borrow().calls[calls..]
            .iter()
            .any(|v| matches!(v.0, 0x24000 | 0x23006))
    );
    h.note_request(5, 6, [fd, 0, 0, 0], b"").unwrap();
    let child = h.repeat_fork();
    h.repeat_exec(&child).unwrap();
    h.repeat_collect();
    h.prepare_healthy_oracle();
    h.runtime.write_native_oracle(&mut [0; 4096]).unwrap();
}
