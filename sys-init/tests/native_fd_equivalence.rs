// SPDX-License-Identifier: BSD-2-Clause
use filesystem_remote_descriptors::NativeIdentity;
use filesystem_service::{Message, put, word};
use fixture::{Fault, Harness};

#[derive(Debug, PartialEq, Eq)]
struct Trace {
    replies: Vec<(Message, Vec<u8>)>,
    errors: Vec<String>,
    source: Vec<Message>,
    closes: usize,
    cleanup: Option<[i64; 2]>,
}
fn request(op: u64, sequence: u64, a: u64, b: u64, c: u64) -> Message {
    let mut r = [0; 64];
    r[..8].copy_from_slice(b"AEFD0001");
    for (i, v) in [op, 77, sequence, a, b, c, 0].into_iter().enumerate() {
        put(&mut r, i + 1, v);
    }
    r
}
fn program() -> Vec<(Message, Vec<u8>)> {
    let mut operations = vec![
        (1, 1, 4, 0, b"file".to_vec()),
        (4, 3, 10, 1, vec![]),
        (2, 10, 2, 0, vec![]),
        (3, 3, (-1i64) as u64, 1, vec![]),
        (2, 10, 4096, 0, vec![]),
        (6, 10, 0, 0, vec![]),
        (3, 10, (-2i64) as u64, 2, vec![]),
        (2, 10, 2, 0, vec![]),
        (5, 3, 0, 0, vec![]),
        (5, 10, 0, 0, vec![]),
        (77, 0, 0, 0, vec![]),
        (2, 3, 1, 0, vec![]),
        (1, 0, 7, 0, b"missing".to_vec()),
        (1, 0, 3, 0, b"dir".to_vec()),
    ];
    operations
        .drain(..)
        .enumerate()
        .map(|(i, (op, a, b, c, name))| (request(op, i as u64 + 1, a, b, c), name))
        .collect()
}
// Both modules are real protocol sources. Native observations are still injected.
// The previous crate is compiled only from its verified immutable Git object.
macro_rules! run {
    ($module:ident, $name:ident) => {
        fn $name(fault: Fault, drop_at: usize, corrupt: bool) -> Trace {
            let mut h = Harness::new(fault, [-9, -5]);
            let files = h.fds.as_mut().unwrap();
            let key = files
                .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
                .unwrap();
            let mut connection = $module::Connection::bind(key, 77).unwrap();
            let mut trace = Trace {
                replies: vec![],
                errors: vec![],
                source: vec![],
                closes: 0,
                cleanup: None,
            };
            let mut workspace = [0xa5; 4096];
            for (i, (header, name)) in program().into_iter().enumerate() {
                workspace.fill(0);
                let needed = match connection.input_length(files, &header) {
                    Ok(n) => n,
                    Err(e) => {
                        trace.errors.push(format!("input:{e:?}"));
                        break;
                    }
                };
                workspace[..name.len()].copy_from_slice(&name);
                if corrupt && i == 0 {
                    workspace[63] = 1;
                }
                match connection.prepare(files, &header, needed, &mut workspace) {
                    Ok(reply) => {
                        trace.replies.push((*reply.header(), reply.body().to_vec()));
                        if i == drop_at {
                            drop(reply);
                        } else {
                            reply.delivered();
                        }
                    }
                    Err(e) => {
                        trace.errors.push(format!("prepare:{e:?}"));
                    }
                }
                assert!(workspace.iter().all(|b| *b == 0));
                if files.cleanup().is_some() {
                    // A second request cannot replay or reopen the retired source.
                    let before = h.local.lock().unwrap().sent.len();
                    assert!(connection.input_length(files, &header).is_err());
                    let after = h.local.lock().unwrap().sent.len();
                    assert_eq!(after, before);
                    break;
                }
            }
            trace.cleanup = files.cleanup();
            files.abort();
            let local = h.local.lock().unwrap();
            trace.source = local.sent.clone();
            trace.closes = local.closes;
            trace
        }
    };
}
run!(filesystem_fd_protocol, current);
run!(filesystem_fd_protocol_previous, previous);

#[test]
fn real_protocols_match_all_operations_errors_lost_delivery_and_source_failures() {
    for fault in [Fault::None, Fault::ReadBody, Fault::Count, Fault::Close] {
        for drop_at in [usize::MAX, 0, 2, 8] {
            for corrupt in [false, true] {
                assert_eq!(
                    current(fault, drop_at, corrupt),
                    previous(fault, drop_at, corrupt)
                );
            }
        }
    }
    let healthy = current(Fault::None, usize::MAX, false);
    assert_eq!(healthy.replies.len(), 14);
    assert!(healthy.errors.is_empty());
    assert_eq!(healthy.cleanup, None);
    assert_eq!(healthy.closes, 1);
    assert_eq!(word(&healthy.replies[1].0, 4), 10);
    assert_eq!(&healthy.replies[2].1[..2], b"ab");
    assert_eq!(&healthy.replies[4].1[..5], b"bcdef");
    assert_eq!(&healthy.replies[7].1[..2], b"ef");
    assert_eq!(word(&healthy.replies[10].0, 1) as i64, -38);
    assert_eq!(word(&healthy.replies[11].0, 1) as i64, -9);
    assert_eq!(word(&healthy.replies[12].0, 1) as i64, -2);
    assert_eq!(word(&healthy.replies[13].0, 1) as i64, -21);
}
