// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_fd_protocol::Connection;
use std::io::{ErrorKind, Read, Write};
use std::process::{Command, Stdio};
#[path = "fd-wire-fixture.rs"]
mod fixture;
use fixture::{Fault, Harness};
fn word(raw: &[u8], index: usize) -> u64 {
    u64::from_le_bytes(raw[index * 8..index * 8 + 8].try_into().unwrap())
}
pub(super) fn run(executable: &str, mode: &str, prefix: usize) {
    let fault = match mode {
        "source-body" => Fault::ReadBody,
        "source-count" => Fault::Count,
        "source-close" => Fault::Close,
        _ => Fault::None,
    };
    let mut h = Harness::new(fault, [0; 2]);
    let process = h
        .fds
        .as_mut()
        .unwrap()
        .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
        .unwrap();
    let mut connection = Connection::bind(process, 77).unwrap();
    let mut child = Command::new(executable)
        .arg(mode)
        .arg(prefix.to_string())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let mut incoming = child.stdout.take().unwrap();
    let mut outgoing = child.stdin.take().unwrap();
    let mut workspace = [0; MAX_READ];
    let mut requests = Vec::new();
    loop {
        let mut header = [0; 64];
        if let Err(error) = incoming.read_exact(&mut header) {
            assert_eq!(error.kind(), ErrorKind::UnexpectedEof);
            break;
        }
        let opcode = word(&header, 1);
        let fd = word(&header, 4);
        requests.push((opcode, fd));
        let length = connection
            .input_length(h.fds.as_mut().unwrap(), &header)
            .unwrap();
        incoming.read_exact(&mut workspace[..length]).unwrap();
        let response =
            match connection.prepare(h.fds.as_mut().unwrap(), &header, length, &mut workspace) {
                Ok(value) => value,
                Err(_) => {
                    assert!(mode.starts_with("source-"));
                    break;
                }
            };
        let lost = (mode == "dup-loss" && opcode == 4)
            || (mode == "target-loss" && opcode == 5 && fd == 4)
            || (mode == "cleanup-loss" && opcode == 5 && fd == 5);
        if lost {
            outgoing.write_all(&response.header()[..prefix]).unwrap();
            drop(response);
            break;
        }
        let mut reply = *response.header();
        if mode == "collision" && opcode == 4 {
            reply[32..40].copy_from_slice(&3_u64.to_le_bytes());
        }
        if outgoing.write_all(&reply).is_err() || outgoing.write_all(response.body()).is_err() {
            drop(response);
            break;
        }
        response.delivered();
        assert!(workspace.iter().all(|&byte| byte == 0));
        if mode == "cleanup-stale" && opcode == 4 {
            h.fds.as_mut().unwrap().close(process, 5).unwrap();
        }
    }
    drop(outgoing);
    connection.abort(h.fds.as_mut().unwrap());
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([0; 2]));
    assert!(
        child.wait().unwrap().success(),
        "C consumer failed: {mode}/{prefix}"
    );
    let first_dup = requests.iter().position(|&(op, _)| op == 4);
    if mode == "file-self"
        || mode == "stream-file"
        || mode == "source-body"
        || mode == "source-count"
    {
        assert!(first_dup.is_none());
    } else {
        let at = first_dup.unwrap();
        assert!(requests[..at].iter().all(|&(op, _)| op != 5));
        if mode == "dup-loss" || mode == "collision" || mode.starts_with("target-unknown-") {
            assert_eq!(
                requests.len(),
                at + 1,
                "no cleanup/replay after uncertain duplicate/target"
            );
        }
        if mode == "target-loss" || mode == "source-close" {
            assert_eq!(&requests[at + 1..], &[(5, 4)]);
        }
        if mode == "cleanup-loss" || mode == "cleanup-stale" {
            assert_eq!(&requests[at + 1..], &[(5, 5)]);
        }
        if mode == "remote-full" {
            assert_eq!(requests.iter().filter(|&&(op, _)| op == 1).count(), 13);
        }
    }
    let underlying = h.opcodes();
    let uncertain = mode.ends_with("-loss")
        || mode.starts_with("target-unknown-")
        || mode.starts_with("source-")
        || mode == "cleanup-stale"
        || mode == "collision";
    if !uncertain {
        assert_eq!(
            underlying.iter().filter(|&&op| op == 3).count(),
            if mode == "remote-full" {
                13
            } else if mode == "alias-file" {
                1
            } else {
                2
            }
        );
    }
    let seen = h.storage.lock().unwrap();
    assert_eq!(
        seen.lookups,
        if mode == "remote-full" {
            13
        } else if mode == "alias-file" {
            1
        } else {
            2
        }
    );
    drop(seen);
    let storage = h.storage.clone();
    let local = h.local.clone();
    drop(h);
    assert_eq!(storage.lock().unwrap().drops, 1);
    assert_eq!(local.lock().unwrap().closes, 1);
}
