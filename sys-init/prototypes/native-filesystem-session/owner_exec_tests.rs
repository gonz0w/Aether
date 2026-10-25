// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_remote_descriptors::{ProcessFiles, Seek};
use filesystem_service::{message, put};
use fork_gate::{ForkStreams, GateError, Phase, Routed};
use std::{cell::RefCell, rc::Rc, vec::Vec};
#[derive(Default)]
struct Seen {
    fs: Vec<u8>,
    at: usize,
    startup: Vec<u8>,
    reply: Vec<u8>,
    events: Vec<u64>,
    receipt: (i64, u64, u64),
    exec_raw: i64,
    wrong_receipt: bool,
    fail_publish: bool,
    fail_write: bool,
    not_ready: bool,
    terminal_ready: bool,
}
#[derive(Clone)]
struct Mock(Rc<RefCell<Seen>>);
impl af07_transport::Kernel for Mock {
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], writing: bool) -> i64 {
        let mut s = self.0.borrow_mut();
        if writing {
            if endpoint == 103 {
                if s.fail_write {
                    return -32;
                }
                if s.exec_raw < 0 {
                    s.reply.extend_from_slice(bytes);
                } else {
                    s.startup.extend_from_slice(bytes);
                }
            } else {
                assert_eq!(endpoint, 101);
            }
            return bytes.len() as i64;
        }
        assert_eq!(endpoint, 100);
        let at = s.at;
        let n = bytes.len();
        assert!(at + n <= s.fs.len());
        bytes.copy_from_slice(&s.fs[at..at + n]);
        s.at += n;
        n as i64
    }
    fn wait(&mut self, _: u64) -> i64 {
        panic!("unexpected channel wait")
    }
    fn close(&mut self, _: u64) -> i64 {
        0
    }
}
impl Control for Mock {
    fn ctl(&mut self, op: u64, handle: u64, arg: u64) -> owner_control::Status {
        let mut s = self.0.borrow_mut();
        s.events.push(op);
        match op {
            0x2a000 => {
                assert_eq!(handle, 0xe002);
                (0, 88, 0)
            }
            0x2a001 => {
                assert_eq!((handle, arg), (0xe002, 88));
                (0, 0, 0)
            }
            0x23004 => {
                assert_eq!(handle, 0xb0000103);
                (55, 0, 0)
            }
            0x23005 => {
                assert_eq!((handle, arg), (0xb0000103, 55));
                (0, 0, 0)
            }
            0x20001 => {
                assert_eq!(handle, 0xb0000103);
                assert_eq!(s.startup.len(), 304);
                if s.terminal_ready {
                    (1, 1, 1)
                } else {
                    (0, u64::from(!s.not_ready), 0)
                }
            }
            _ => panic!("unexpected ctl {op:x}"),
        }
    }
    fn engine(&mut self, _: u64, _: u64) -> i64 {
        panic!("engine")
    }
    fn delegate(&mut self, _: u64, _: &[u64; 3]) -> i64 {
        panic!("delegate")
    }
    fn launch(&mut self, _: &[u8; 272], _: u64, _: u64) -> i64 {
        panic!("launch")
    }
    fn copy(&mut self, _: u64, _: u32, _: u64, _: u64, _: u64) -> i64 {
        panic!("copy")
    }
    fn serial(&mut self, _: bool, _: &mut [u8]) -> i64 {
        panic!("serial")
    }
    fn exec(&mut self, id: u64, token: u64, args: &[u8; 272]) -> i64 {
        assert_eq!((id, token), (0xb0000103, 55));
        assert_eq!(args[0], 1);
        let mut s = self.0.borrow_mut();
        s.events.push(0x23007);
        if s.exec_raw == 0 {
            s.receipt = (if s.wrong_receipt { 54 } else { 55 }, 0xc003, 1);
        }
        s.exec_raw
    }
    fn receipt(&mut self, id: u64) -> owner_control::Status {
        assert_eq!(id, 0xb0000103);
        let mut s = self.0.borrow_mut();
        s.events.push(0x23008);
        s.receipt
    }
    fn publish(&mut self, id: u64, token: u64) -> i64 {
        assert_eq!((id, token), (0xb0000103, 55));
        let mut s = self.0.borrow_mut();
        s.events.push(0x23009);
        if s.fail_publish {
            -5
        } else {
            s.receipt.2 = 0;
            0
        }
    }
}
type Setup = (
    Mock,
    ProcessFiles<Channel<Mock>>,
    State,
    Peer<Channel<Mock>>,
    Instance,
    Plan,
    Process,
);
fn setup() -> Setup {
    let mut greet = message(77, 0);
    put(&mut greet, 3, 1);
    put(&mut greet, 4, 1);
    let mut lookup = message(77, 0);
    put(&mut lookup, 3, 2);
    put(&mut lookup, 4, 2);
    put(&mut lookup, 5, 12);
    let kernel = Mock(Rc::new(RefCell::new(Seen {
        fs: [greet, lookup].concat(),
        ..Seen::default()
    })));
    let fs = Framed(Endpoints::new(kernel.clone(), 100, 101).ok().unwrap());
    let mut files = ProcessFiles::connect(fs, 77).ok().unwrap();
    let parent = files
        .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
        .unwrap();
    assert_eq!(
        files.open_read(parent, b"file", true),
        Ok(filesystem_remote_descriptors::FIRST_FILE_FD)
    );
    files
        .seek(
            parent,
            filesystem_remote_descriptors::FIRST_FILE_FD,
            Seek::Set(5),
        )
        .unwrap();
    let id = Identity::admitted(2, 1, 0xb0000103).unwrap();
    let child_id = native(id).unwrap();
    let child = files
        .copy_inherit_serialized_v1(parent, child_id, 9, || CopyAttempt::<i64>::Copied {
            identity: child_id,
            parent_pid: 9,
        })
        .unwrap();
    let console = core::array::from_fn(|i| {
        Some(Source {
            reference: 101 + i as u32,
            selector: i as u32,
            rights: if i == 0 { 1 } else { 2 },
            bound: 16,
        })
    });
    let mut streams = State::new(console, [SessionPipe::new(), SessionPipe::new()]).unwrap();
    let mut plan = Plan {
        identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
        shell: 1,
        parent: 7,
        generation: 9,
        bindings: [Binding::default(); 16],
        sources: core::array::from_fn(|i| {
            if i < 3 {
                console[i].unwrap()
            } else {
                Source::default()
            }
        }),
        history: [0; 2],
    };
    for i in 0..3 {
        plan.bindings[i] = Binding {
            kind: 1,
            selector: i as u8,
            cloexec: u8::from(i == 0),
        };
    }
    plan.bindings[3] = Binding {
        kind: 3,
        selector: filesystem_remote_descriptors::FIRST_FILE_FD as u8,
        cloexec: 1,
    };
    streams.stage_child(id.pid, &plan).unwrap();
    streams.child_ready(id.pid).unwrap();
    plan.identity = id;
    plan.parent = 9;
    let peer = Peer::bind(
        Framed(Endpoints::new(kernel.clone(), 102, 103).ok().unwrap()),
        child,
        9,
    )
    .unwrap();
    let record = Instance {
        identity: Some(id),
        epoch: 1,
        generation: 9,
        writer: 103,
        ..Instance::empty()
    };
    (kernel, files, streams, peer, record, plan, parent)
}
#[test]
fn actual_exec_commit_controls_flags_holders_binding_publication_and_failure() {
    for lane in 0..7 {
        let (mut kernel, files, streams, mut peer, mut record, mut plan, parent) = setup();
        {
            let mut s = kernel.0.borrow_mut();
            match lane {
                1 => s.exec_raw = -13,
                2 => s.exec_raw = 7,
                3 => s.wrong_receipt = true,
                4 => s.fail_publish = true,
                5 => s.fail_write = true,
                6 => s.not_ready = true,
                _ => {}
            }
        }
        let mut owner = Owner::new(files, streams);
        let mut extra = [0; 304];
        extra[..14].copy_from_slice(b"/inputs/helper");
        extra[32] = 1;
        let mut remaining = 150;
        let result = owner.route(|files, streams| {
            execute(
                &mut kernel,
                files,
                streams,
                &mut peer,
                &mut record,
                (&mut plan, 1, &extra),
                &mut remaining,
            )?;
            Ok(Routed::<()>::Complete)
        });
        let child_key = native(record.identity.unwrap()).unwrap();
        if lane == 0 || lane == 1 {
            assert!(result.is_ok());
            assert_eq!(owner.phase(), Phase::Idle);
            owner
                .admit(|files, _| {
                    let child = files.current(child_key).unwrap();
                    assert_eq!(
                        files.file_view_v1(child),
                        Ok(if lane == 0 {
                            (0, 0)
                        } else {
                            (
                                1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                                1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                            )
                        })
                    );
                    assert_eq!(
                        files.file_view_v1(parent),
                        Ok((
                            1u16 << filesystem_remote_descriptors::FIRST_FILE_FD,
                            1u16 << filesystem_remote_descriptors::FIRST_FILE_FD
                        ))
                    );
                    assert_eq!(
                        files.seek(
                            parent,
                            filesystem_remote_descriptors::FIRST_FILE_FD,
                            Seek::Current(0)
                        ),
                        Ok(5)
                    );
                })
                .unwrap();
            let s = kernel.0.borrow();
            if lane == 0 {
                assert_eq!(record.generation, 10);
                assert_eq!(&s.startup[..8], fd_startup::MAGIC);
                assert_eq!(&s.startup[112..116], &[0; 4]);
                assert_eq!(&s.startup[176..192], &[0; 16]);
                assert!(s.events.contains(&0x23009));
            } else {
                assert_eq!(record.generation, 9);
                assert_eq!(&s.reply[..8], b"AEEXR001");
                assert_eq!(i64::from_le_bytes(s.reply[16..24].try_into().unwrap()), -13);
                assert!(s.events.contains(&0x23005));
                assert!(!s.events.contains(&0x23009));
            }
        } else {
            assert!(result.is_err());
            assert_ne!(owner.phase(), Phase::Idle);
            assert_eq!(owner.admit(|_, _| ()), Err(GateError::Closed));
            if lane == 2 || lane == 3 {
                assert!(!kernel.0.borrow().events.contains(&0x23009));
            }
            assert!(!kernel.0.borrow().events.contains(&0x23005));
        }
        owner.retire();
        drop(peer);
        drop(owner);
    }
}

#[test]
fn stale_context_or_forged_sources_cannot_reach_native_exec() {
    for lane in 0..3 {
        let (mut kernel, mut files, mut streams, mut peer, mut record, mut plan, _) = setup();
        match lane {
            0 => record.exec_sequence = 1,
            1 => plan.generation = 8,
            _ => plan.sources[0].reference = 999,
        }
        let mut extra = [0; 304];
        extra[..14].copy_from_slice(b"/inputs/helper");
        extra[32] = 1;
        assert!(
            execute(
                &mut kernel,
                &mut files,
                &mut streams,
                &mut peer,
                &mut record,
                (&mut plan, 1, &extra),
                &mut 100
            )
            .is_err()
        );
        assert!(kernel.0.borrow().events.is_empty());
    }
}
#[test]
fn terminal_worker_cannot_establish_startup_readiness() {
    let (mut kernel, _, _, _, _, _, _) = setup();
    {
        let mut s = kernel.0.borrow_mut();
        s.startup.resize(304, 0);
        s.terminal_ready = true;
    }
    assert_eq!(ready(&mut kernel, 0xb0000103, &mut 100), Err(-5));
}
#[test]
fn exec_decoder_rejects_incompatible_and_noncanonical_complete_frames() {
    let (_, _, _, _, record, plan, _) = setup();
    let id = record.identity.unwrap();
    let mut raw = [0; 608];
    fd_startup::encode(&plan, (&mut raw[..304]).try_into().unwrap()).unwrap();
    raw[..8].copy_from_slice(exec_frames::MAGIC);
    raw[12..16].copy_from_slice(&608u32.to_le_bytes());
    raw[296..304].copy_from_slice(&1u64.to_le_bytes());
    raw[304..318].copy_from_slice(b"/inputs/helper");
    raw[336] = 1;
    assert!(exec_frames::request(&raw, (id, 9, 9), &mut [0; 304]).is_ok());
    for index in [
        0, 8, 12, 16, 24, 28, 32, 36, 40, 44, 56, 64, 72, 104, 111, 127, 320, 345, 353,
    ] {
        let mut bad = raw;
        bad[index] ^= 1;
        assert!(
            exec_frames::request(&bad, (id, 9, 9), &mut [0; 304]).is_err(),
            "index {index}"
        );
    }
    let mut bad = raw;
    bad[296..304].fill(0);
    assert!(exec_frames::request(&bad, (id, 9, 9), &mut [0; 304]).is_err());
    assert!(exec_frames::request(&raw, (id, 9, 10), &mut [0; 304]).is_err());
}
