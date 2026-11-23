// SPDX-License-Identifier: BSD-2-Clause
//! Real Client/AF09 exchange over synthetic storage for the closed package view.
use super::*;
use filesystem_policy as policy;
use std::{
    collections::BTreeMap,
    sync::{Arc, Mutex, mpsc},
    thread,
    time::Duration,
    vec::Vec,
};

#[derive(Clone, Default)]
struct StorageState {
    files: BTreeMap<u64, Vec<u8>>,
    mutations: usize,
    writes: usize,
}
struct Storage(Arc<Mutex<StorageState>>);
fn node(id: u64, size: usize) -> policy::Node {
    policy::Node::new(
        id,
        1,
        size as u64,
        if id < 3 {
            policy::Kind::Directory
        } else {
            policy::Kind::File
        },
    )
}
fn object(name: &[u8]) -> Result<u64, policy::Error> {
    match name {
        b"bytecount" => Ok(3),
        b"input" => Ok(4),
        b"output" => Ok(5),
        _ => Err(policy::Error::Backend(2)),
    }
}
impl policy::Backend for Storage {
    fn root(&mut self) -> Result<policy::Node, policy::Error> {
        Ok(node(1, 0))
    }
    fn directory(&mut self, directory: policy::Node) -> Result<policy::Node, policy::Error> {
        Ok(directory)
    }
    fn lookup(
        &mut self,
        directory: policy::Node,
        name: &[u8],
    ) -> Result<policy::Node, policy::Error> {
        if directory.identity().0 == 1 && name == b"pkg" {
            return Ok(node(2, 0));
        }
        if directory.identity().0 != 2 {
            return Err(policy::Error::Backend(13));
        }
        let id = object(name)?;
        let state = self.0.lock().unwrap();
        Ok(node(
            id,
            state.files.get(&id).ok_or(policy::Error::Backend(2))?.len(),
        ))
    }
    fn read(
        &mut self,
        file: policy::Node,
        offset: u64,
        out: &mut [u8],
    ) -> Result<usize, policy::Error> {
        let state = self.0.lock().unwrap();
        let bytes = state.files.get(&file.identity().0).unwrap();
        let start = (offset as usize).min(bytes.len());
        let count = (bytes.len() - start).min(out.len());
        out[..count].copy_from_slice(&bytes[start..start + count]);
        Ok(count)
    }
    fn write(
        &mut self,
        file: policy::Node,
        offset: u64,
        bytes: &[u8],
        _: policy::Utc,
    ) -> Result<policy::Completion, policy::Lost> {
        let mut state = self.0.lock().unwrap();
        let data = state.files.get_mut(&file.identity().0).unwrap();
        assert!(offset as usize <= data.len());
        data.resize(data.len().max(offset as usize + bytes.len()), 0);
        data[offset as usize..offset as usize + bytes.len()].copy_from_slice(bytes);
        state.mutations += 1;
        state.writes += 1;
        Ok(policy::Completion {
            error: 0,
            txg: state.mutations as u64,
            bytes_staged: bytes.len() as u64,
            state: 2,
        })
    }
    fn mutate(
        &mut self,
        directory: policy::Node,
        operation: policy::Namespace<'_>,
        _: policy::Utc,
    ) -> Result<policy::Completion, policy::Lost> {
        assert_eq!(directory.identity().0, 2);
        let policy::Namespace::Create { name, .. } = operation else {
            panic!("only fixed creates");
        };
        let mut state = self.0.lock().unwrap();
        assert!(
            state
                .files
                .insert(object(name).unwrap(), Vec::new())
                .is_none()
        );
        state.mutations += 1;
        Ok(policy::Completion {
            error: 0,
            txg: state.mutations as u64,
            bytes_staged: 0,
            state: 2,
        })
    }
}
struct Time;
impl policy::Clock for Time {
    fn utc(&mut self) -> Result<policy::Utc, policy::Error> {
        Ok(policy::Utc {
            seconds: 1,
            nanoseconds: 0,
        })
    }
}
struct Pipe {
    tx: Option<mpsc::Sender<[u8; 64]>>,
    rx: mpsc::Receiver<[u8; 64]>,
}
impl Channel for Pipe {
    fn send(&mut self, frame: &[u8; 64]) -> Result<(), i64> {
        self.tx.as_ref().ok_or(-32)?.send(*frame).map_err(|_| -32)
    }
    fn receive(&mut self, frame: &mut [u8; 64]) -> Result<(), i64> {
        *frame = self
            .rx
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.tx.take();
        [0; 2]
    }
}
fn parent() -> Binding {
    Binding {
        slot: 1,
        epoch: 1,
        handle: 0xb0000102,
        generation: 31,
    }
}
fn child() -> Binding {
    Binding {
        slot: 2,
        epoch: 1,
        handle: 0xb0000103,
        generation: 32,
    }
}
struct Harness {
    slot: MaybeUninit<Files<Pipe>>,
    state: Arc<Mutex<StorageState>>,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
}
impl Harness {
    fn new(state: StorageState) -> Self {
        let state = Arc::new(Mutex::new(state));
        let shared = state.clone();
        let (tx, inbound) = mpsc::channel();
        let (outbound, rx) = mpsc::channel();
        let worker = thread::spawn(move || {
            let mut owner = policy::Owner::new(Storage(shared), Time, 91)
                .unwrap()
                .with_namespace_identity(policy::Identity::new(1000, 1000).unwrap());
            let admin = owner.attach(7, policy::Rights::new(15).unwrap()).unwrap();
            let pkg = owner
                .lookup(
                    7,
                    admin.session,
                    admin.root.handle,
                    b"pkg",
                    policy::Rights::new(15).unwrap(),
                )
                .unwrap();
            filesystem_service::run_home(
                owner,
                Pipe {
                    tx: Some(outbound),
                    rx: inbound,
                },
                7,
                admin.session,
                pkg.handle,
                8,
                91,
            )
        });
        let mut slot = MaybeUninit::uninit();
        Files::connect_in_place(&mut slot, Pipe { tx: Some(tx), rx }, 91, parent())
            .ok()
            .unwrap();
        Self {
            slot,
            state,
            worker: Some(worker),
        }
    }
    fn files(&mut self) -> &mut Files<Pipe> {
        unsafe { self.slot.assume_init_mut() }
    }
    fn exec(&mut self, image: &[u8]) -> Binding {
        self.files().inherit_child(parent(), child()).unwrap();
        let mut snapshot = [0x7f; 48 * 1024];
        assert_eq!(
            self.files().acquire_package_bytecount(
                child(),
                image,
                &mut snapshot,
                &mut [0; PAYLOAD]
            ),
            Ok(image.len())
        );
        assert_eq!(&snapshot[..image.len()], image);
        assert!(snapshot[image.len()..].iter().all(|b| *b == 0));
        let next = self.files().exec_child(child(), 33).unwrap();
        self.files().bind_package_stdio(next).unwrap();
        next
    }
    fn rpc(
        &mut self,
        binding: Binding,
        op: u64,
        fd: u64,
        bytes: &[u8],
        requested: usize,
    ) -> ([u8; 64], Vec<u8>) {
        let files = self.files();
        let mut frame = [0; 64];
        frame[..8].copy_from_slice(MAGIC);
        put(&mut frame, 1, op);
        put(&mut frame, 2, binding.generation);
        put(&mut frame, 3, files.sequence(files.view(binding).unwrap()));
        put(&mut frame, 4, fd);
        put(&mut frame, 5, requested as u64);
        let mut block = [0; PAYLOAD];
        block[..bytes.len()].copy_from_slice(bytes);
        let length = files.body_length(binding, &frame).unwrap();
        let mut reply = files.prepare(binding, &frame, length, &mut block).unwrap();
        let raw = *reply.header();
        let body = reply.body_mut().to_vec();
        reply.delivered();
        (raw, body)
    }
}
impl Drop for Harness {
    fn drop(&mut self) {
        self.files().abort();
        if let Some(worker) = self.worker.take() {
            worker.join().unwrap();
        }
    }
}
fn image() -> Vec<u8> {
    (0..42_904).map(|i| (i % 251) as u8).collect()
}

#[test]
fn seed_exec_real_file_input_and_exact_once_stdout_then_cold_reopen() {
    let image = image();
    let mut seed = Harness::new(StorageState::default());
    seed.files()
        .stage_package_bytecount(&image, &mut [0; PAYLOAD], true)
        .unwrap();
    assert_eq!(seed.state.lock().unwrap().mutations, 15);
    let child = seed.exec(&image);
    let (read, body) = seed.rpc(child, 2, 3, &[], 4096);
    assert_eq!((word(&read, 1), word(&read, 4)), (0, 6));
    assert_eq!(&body[..6], b"abcdef");
    let (eof, _) = seed.rpc(child, 2, 3, &[], 4096);
    assert_eq!((word(&eof, 1), word(&eof, 4)), (0, 0));
    let (denied, _) = seed.rpc(parent(), 11, 4, b"6\n", 2);
    assert_eq!(word(&denied, 1) as i64, -9);
    let (wrong, _) = seed.rpc(child, 11, 4, b"7\n", 2);
    assert_eq!(word(&wrong, 1) as i64, -9);
    let (written, receipt) = seed.rpc(child, 11, 4, b"6\n", 2);
    assert_eq!((word(&written, 1), word(&written, 4)), (0, 2));
    assert_eq!(word(receipt.as_slice().try_into().unwrap(), 0), 14);
    let (repeat, _) = seed.rpc(child, 11, 4, b"6\n", 2);
    assert_eq!(word(&repeat, 1) as i64, -9);
    seed.files().settle_child(child).unwrap();
    seed.files()
        .verify_package_output(&mut [0; PAYLOAD])
        .unwrap();
    let mut saved = seed.state.lock().unwrap().clone();
    assert_eq!(saved.mutations, 16); // The engine's /pkg mkdir is separate.
    saved.mutations = 0;
    saved.writes = 0;
    let mut cold = Harness::new(saved);
    cold.files()
        .stage_package_bytecount(&image, &mut [0; PAYLOAD], false)
        .unwrap();
    assert_eq!(cold.state.lock().unwrap().mutations, 0);
    let child = cold.exec(&image);
    let (written, _) = cold.rpc(child, 11, 4, b"6\n", 2);
    assert_eq!((word(&written, 1), word(&written, 4)), (0, 2));
    cold.files().settle_child(child).unwrap();
    cold.files()
        .verify_package_output(&mut [0; PAYLOAD])
        .unwrap();
    assert_eq!(cold.state.lock().unwrap().mutations, 1);
}
#[test]
fn tampered_executable_retires_without_exec_and_clears_snapshot() {
    let image = image();
    let mut h = Harness::new(StorageState::default());
    h.files()
        .stage_package_bytecount(&image, &mut [0; PAYLOAD], true)
        .unwrap();
    h.state.lock().unwrap().files.get_mut(&3).unwrap()[4096] ^= 1;
    h.files().inherit_child(parent(), child()).unwrap();
    let mut snapshot = [0x7f; 48 * 1024];
    assert_eq!(
        h.files()
            .acquire_package_bytecount(child(), &image, &mut snapshot, &mut [0; PAYLOAD]),
        Err(Error::Protocol)
    );
    assert!(snapshot.iter().all(|b| *b == 0));
    assert!(h.files().cleanup().is_some());
}
#[test]
fn cold_output_mismatch_rejects_before_mutation() {
    let image = image();
    let mut h = Harness::new(StorageState::default());
    h.files()
        .stage_package_bytecount(&image, &mut [0; PAYLOAD], true)
        .unwrap();
    let mut saved = h.state.lock().unwrap().clone();
    saved.files.insert(5, b"7\n".to_vec());
    saved.mutations = 0;
    let mut cold = Harness::new(saved);
    assert_eq!(
        cold.files()
            .stage_package_bytecount(&image, &mut [0; PAYLOAD], false),
        Err(Error::Protocol)
    );
    assert_eq!(cold.state.lock().unwrap().mutations, 0);
}
