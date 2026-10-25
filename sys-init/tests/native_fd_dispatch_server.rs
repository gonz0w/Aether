// SPDX-License-Identifier: BSD-2-Clause
// Host-only live C/dispatcher/service composition; fixture module supplied by build.
use fd_dispatch::{Error, Peer};
use filesystem_remote_descriptors::NativeIdentity;
use fixture::{Fault, Harness};
use std::io::{Read, Write};
struct App {
    writes: usize,
    fail_body: bool,
    closed: bool,
}
impl Channel for App {
    fn receive(&mut self, out: &mut [u8; 64]) -> Result<(), i64> {
        std::io::stdin().read_exact(out).map_err(|_| -32)
    }
    fn send(&mut self, input: &[u8; 64]) -> Result<(), i64> {
        self.writes += 1;
        if self.fail_body && self.writes == 3 {
            return Err(-32);
        }
        let mut out = std::io::stdout().lock();
        out.write_all(input)
            .and_then(|()| out.flush())
            .map_err(|_| -32)
    }
    fn close(&mut self) -> [i64; 2] {
        assert!(!self.closed);
        self.closed = true;
        [0; 2]
    }
}
pub fn run() {
    let negative = std::env::args().nth(1).as_deref() == Some("lost-body");
    // Keep every sealed fault arm compiled without suppressing dead-code checks.
    let fault = match std::env::var("FD_TEST_SOURCE_FAULT").as_deref() {
        Ok("body") => Fault::ReadBody,
        Ok("count") => Fault::Count,
        Ok("close") => Fault::Close,
        _ => Fault::None,
    };
    let mut h = Harness::new(fault, [0; 2]);
    let files = h.fds.as_mut().unwrap();
    let id = NativeIdentity::admitted(1, 1, 0xb0000102).unwrap();
    let key = files.admitted_shell(id, 7).unwrap();
    let mut peer = Peer::bind(
        App {
            writes: 0,
            fail_body: negative,
            closed: false,
        },
        key,
        77,
    )
    .unwrap_or_else(|e| panic!("{e:?}"));
    let mut workspace = Box::new([0; 4096]);
    peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace)
        .unwrap();
    if negative {
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace),
            Err(Error::Transport(-32))
        );
        assert_eq!(peer.cleanup(), Some([0; 2]));
        assert!(workspace.iter().all(|b| *b == 0));
        assert!(h.fds.as_ref().unwrap().cleanup().is_some());
        assert_eq!(h.opcodes(), [1, 2]);
    } else {
        for _ in 1..10 {
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace)
                .unwrap();
        }
        assert!(workspace.iter().all(|b| *b == 0));
        assert_eq!(h.opcodes(), [1, 2, 2, 3]);
        h.fds.as_mut().unwrap().settled(key).unwrap();
        assert_eq!(h.fds.as_mut().unwrap().disconnect(), Ok([0; 2]));
        assert_eq!(peer.close(), [0; 2]);
    }
    assert_eq!(h.storage.lock().unwrap().lookups, 1);
    assert_eq!(h.local.lock().unwrap().closes, 1);
    drop(peer);
    drop(h);
    eprintln!(
        "live Rust dispatcher: {}",
        if negative {
            "lost body retired"
        } else {
            "10 complete exchanges/source disconnected"
        }
    );
}
