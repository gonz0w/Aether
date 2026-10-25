// SPDX-License-Identifier: BSD-2-Clause
use super::super::*;
use filesystem_policy::{Backend, Clock, Completion, Lost, Namespace, Node, Owner, Rights, Utc};
use filesystem_service::{put, word, Message, MAGIC};
use std::{
    sync::{mpsc, Arc, Mutex},
    thread,
    time::Duration,
    vec::Vec,
};
#[derive(Default)]
pub(super) struct Seen {
    pub(super) size: u64,
    pub(super) sent: Vec<Message>,
    pub(super) closes: usize,
    pub(super) reads: usize,
    pub(super) lookups: usize,
    pub(super) drops: usize,
    pub(super) deny_read: bool,
}
type Shared = Arc<Mutex<Seen>>;
#[derive(Clone, Copy, PartialEq)]
pub(super) enum Fault {
    None,
    ReadBody,
    Count,
    Close,
}
pub(super) struct Pipe {
    tx: Option<mpsc::SyncSender<Message>>,
    rx: Option<mpsc::Receiver<Message>>,
    seen: Shared,
    fault: Fault,
    last: u64,
    body: bool,
    cleanup: [i64; 2],
}
impl Channel for Pipe {
    fn send(&mut self, frame: &Message) -> core::result::Result<(), i64> {
        self.seen.lock().unwrap().sent.push(*frame);
        if frame[..8] == MAGIC[..] {
            self.last = word(frame, 1);
        }
        self.tx.as_ref().unwrap().send(*frame).map_err(|_| -32)
    }
    fn receive(&mut self, out: &mut Message) -> core::result::Result<(), i64> {
        if (self.fault == Fault::ReadBody && self.body)
            || (self.fault == Fault::Close && self.last == 3)
        {
            return Err(-32);
        }
        *out = self
            .rx
            .as_ref()
            .unwrap()
            .recv_timeout(Duration::from_secs(2))
            .map_err(|_| -32)?;
        if self.last == 2 && out[..8] == MAGIC[..] && word(out, 1) == 0 {
            self.body = word(out, 5) > 0;
            if self.fault == Fault::Count {
                put(out, 5, 4097);
            }
        }
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.lock().unwrap().closes += 1;
        self.tx.take();
        self.rx.take();
        self.cleanup
    }
}
struct Storage(Shared);
impl Drop for Storage {
    fn drop(&mut self) {
        self.0.lock().unwrap().drops += 1;
    }
}
impl Backend for Storage {
    fn root(&mut self) -> core::result::Result<Node, filesystem_policy::Error> {
        Ok(Node::new(1, 1, 1, filesystem_policy::Kind::Directory))
    }
    fn directory(&mut self, node: Node) -> core::result::Result<Node, filesystem_policy::Error> {
        Ok(node)
    }
    fn lookup(
        &mut self,
        _: Node,
        name: &[u8],
    ) -> core::result::Result<Node, filesystem_policy::Error> {
        self.0.lock().unwrap().lookups += 1;
        match name {
            b"file" | b"alias" => Ok(Node::new(
                2,
                1,
                self.0.lock().unwrap().size.max(6),
                filesystem_policy::Kind::File,
            )),
            b"dir" => Ok(Node::new(3, 1, 0, filesystem_policy::Kind::Directory)),
            _ => Err(filesystem_policy::Error::Backend(2)),
        }
    }
    fn read(
        &mut self,
        _: Node,
        offset: u64,
        out: &mut [u8],
    ) -> core::result::Result<usize, filesystem_policy::Error> {
        let mut seen = self.0.lock().unwrap();
        seen.reads += 1;
        if seen.deny_read {
            out.fill(0x55);
            return Err(filesystem_policy::Error::Backend(13));
        }
        let count = seen
            .size
            .max(6)
            .saturating_sub(offset)
            .min(out.len() as u64) as usize;
        for (i, b) in out[..count].iter_mut().enumerate() {
            *b = b'a'.wrapping_add((offset + i as u64) as u8);
        }
        Ok(count)
    }
    fn write(
        &mut self,
        _: Node,
        _: u64,
        _: &[u8],
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("write forbidden")
    }
    fn mutate(
        &mut self,
        _: Node,
        _: Namespace<'_>,
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("mutate forbidden")
    }
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> core::result::Result<Utc, filesystem_policy::Error> {
        panic!("clock forbidden")
    }
}
pub(super) struct Harness {
    pub(super) fds: Option<ProcessFiles<Pipe>>,
    worker: Option<thread::JoinHandle<filesystem_service::Report>>,
    pub(super) storage: Shared,
    pub(super) local: Shared,
}
impl Harness {
    pub(super) fn new(fault: Fault, cleanup: [i64; 2]) -> Self {
        let (server_tx, server_rx) = mpsc::sync_channel(128);
        let (client_tx, client_rx) = mpsc::sync_channel(128);
        let storage = Shared::default();
        let observed = storage.clone();
        let local = Shared::default();
        let worker = thread::spawn(move || {
            let owner = Owner::new(Storage(observed), Time, 72).unwrap();
            filesystem_service::run(
                owner,
                Pipe {
                    tx: Some(client_tx),
                    rx: Some(server_rx),
                    seen: Shared::default(),
                    fault: Fault::None,
                    last: 0,
                    body: false,
                    cleanup: [0; 2],
                },
                17,
                Rights::new(3).unwrap(),
                91,
            )
        });
        let fds = ProcessFiles::connect(
            Pipe {
                tx: Some(server_tx),
                rx: Some(client_rx),
                seen: local.clone(),
                fault,
                last: 0,
                body: false,
                cleanup,
            },
            91,
        )
        .ok()
        .unwrap();
        Self {
            fds: Some(fds),
            worker: Some(worker),
            storage,
            local,
        }
    }
    pub(super) fn opcodes(&self) -> Vec<u64> {
        self.local
            .lock()
            .unwrap()
            .sent
            .iter()
            .filter(|f| f[..8] == MAGIC[..])
            .map(|f| word(f, 1))
            .collect()
    }
}
impl Drop for Harness {
    fn drop(&mut self) {
        self.fds.take();
        if let Some(w) = self.worker.take() {
            w.join().unwrap();
        }
    }
}
