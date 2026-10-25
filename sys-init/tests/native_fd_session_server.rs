// SPDX-License-Identifier: BSD-2-Clause
// Included beside the existing host App/fixture; no native endpoint authority.
struct SessionApp {
    inner: App,
    lose_header: usize,
}
impl Channel for SessionApp {
    fn receive(&mut self, out: &mut [u8; 64]) -> Result<(), i64> {
        self.inner.receive(out)
    }
    fn send(&mut self, input: &[u8; 64]) -> Result<(), i64> {
        if self.inner.writes + 1 == self.lose_header {
            self.inner.writes += 1;
            return Err(-32);
        }
        self.inner.send(input)
    }
    fn close(&mut self) -> [i64; 2] {
        self.inner.close()
    }
}
pub fn run_session() {
    let mode = std::env::args().nth(1).unwrap_or_else(|| "positive".into());
    let lost_dup = mode == "lost-dup-header";
    let lost_cleanup = mode == "lost-cleanup-header";
    let unknown = mode.starts_with("unknown-close");
    let rollback = mode == "rollback";
    let mut h = Harness::new(Fault::None, [0; 2]);
    let id = NativeIdentity::admitted(1, 1, 0xb0000102).unwrap();
    let key = h.fds.as_mut().unwrap().admitted_shell(id, 7).unwrap();
    let mut peer = Peer::bind(
        SessionApp {
            inner: App {
                writes: 0,
                fail_body: false,
                closed: false,
            },
            lose_header: if lost_dup {
                2
            } else if lost_cleanup {
                3
            } else {
                0
            },
        },
        key,
        77,
    )
    .unwrap_or_else(|e| panic!("{e:?}"));
    let mut workspace = Box::new([0; 4096]);
    if lost_dup || lost_cleanup || unknown {
        let complete = if lost_dup { 1 } else { 2 };
        for _ in 0..complete {
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace)
                .unwrap();
        }
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace),
            Err(Error::Transport(-32))
        );
        assert_eq!(peer.cleanup(), Some([0; 2]));
        assert!(h.fds.as_ref().unwrap().cleanup().is_some());
        assert_eq!(h.opcodes(), [1]);
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace),
            Err(Error::Closed)
        );
    } else {
        let complete = if rollback { 6 } else { 8 };
        for _ in 0..complete {
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace)
                .unwrap();
        }
        assert_eq!(
            h.opcodes(),
            if rollback {
                vec![1, 2, 3]
            } else {
                vec![1, 2, 2, 2, 3]
            }
        );
        h.fds.as_mut().unwrap().settled(key).unwrap();
        assert_eq!(h.fds.as_mut().unwrap().disconnect(), Ok([0; 2]));
        assert_eq!(peer.close(), [0; 2]);
    }
    assert!(workspace.iter().all(|b| *b == 0));
    assert_eq!(h.storage.lock().unwrap().lookups, 1);
    assert_eq!(h.local.lock().unwrap().closes, 1);
    drop(peer);
    drop(h);
    eprintln!("session Rust dispatcher: {mode} passed/source joined");
}
