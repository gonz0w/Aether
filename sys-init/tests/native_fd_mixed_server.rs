// SPDX-License-Identifier: BSD-2-Clause
// Included beside the existing host App/fixture; no target or native authority.
pub fn run_mixed() {
    let mode = std::env::args().nth(1).unwrap_or_else(|| "positive".into());
    let lost = mode == "lost-body";
    let early = mode == "stale-map" || mode.starts_with("unknown-close");
    let mut h = Harness::new(Fault::None, [0; 2]);
    let id = NativeIdentity::admitted(1, 1, 0xb0000102).unwrap();
    let key = h.fds.as_mut().unwrap().admitted_shell(id, 7).unwrap();
    let mut peer = Peer::bind(
        App {
            writes: 0,
            fail_body: lost,
            closed: false,
        },
        key,
        77,
    )
    .unwrap_or_else(|e| panic!("{e:?}"));
    let mut workspace = Box::new([0; 4096]);
    peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace)
        .unwrap();
    if lost || early {
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace),
            Err(Error::Transport(-32))
        );
        assert_eq!(peer.cleanup(), Some([0; 2]));
        assert!(h.fds.as_ref().unwrap().cleanup().is_some());
        assert_eq!(h.opcodes(), if lost { vec![1, 2] } else { vec![1] });
        assert_eq!(
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace),
            Err(Error::Closed)
        );
    } else {
        for _ in 1..9 {
            peer.serve_one(h.fds.as_mut().unwrap(), &mut workspace)
                .unwrap();
        }
        assert_eq!(h.opcodes(), [1, 2, 2, 2, 3]);
        h.fds.as_mut().unwrap().settled(key).unwrap();
        assert_eq!(h.fds.as_mut().unwrap().disconnect(), Ok([0; 2]));
        assert_eq!(peer.close(), [0; 2]);
    }
    assert!(workspace.iter().all(|b| *b == 0));
    assert_eq!(h.storage.lock().unwrap().lookups, 1);
    assert_eq!(h.local.lock().unwrap().closes, 1);
    drop(peer);
    drop(h);
    eprintln!("mixed Rust dispatcher: {mode} passed/source joined");
}
