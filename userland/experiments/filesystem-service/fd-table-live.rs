// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_fd_protocol::Connection;
use std::io::{ErrorKind, Read, Write};
use std::process::{Command, Stdio};
#[path = "fd-wire-fixture.rs"]
mod fixture;
use fixture::{Fault, Harness};
fn word(frame: &[u8], index: usize) -> u64 {
    u64::from_le_bytes(frame[index * 8..index * 8 + 8].try_into().unwrap())
}
pub(super) fn run(executable: &str, mode: &str, prefix: usize) {
    let fault = match mode {
        "source-body" => Fault::ReadBody,
        "source-count" => Fault::Count,
        "source-close" => Fault::Close,
        _ => Fault::None,
    };
    let mut h = Harness::new(fault, [0; 2]);
    h.storage.lock().unwrap().deny_read = mode == "denied";
    let process = h
        .fds
        .as_mut()
        .unwrap()
        .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
        .unwrap();
    let mut connection = Connection::bind(process, 77).unwrap();
    let mut child = Command::new(executable)
        .arg(mode)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let mut incoming = child.stdout.take().unwrap();
    let mut outgoing = child.stdin.take().unwrap();
    let mut workspace = [0; MAX_READ];
    let mut count = 0;
    loop {
        let mut header = [0; 64];
        if let Err(error) = incoming.read_exact(&mut header) {
            assert_eq!(error.kind(), ErrorKind::UnexpectedEof);
            break;
        }
        let body = connection
            .input_length(h.fds.as_mut().unwrap(), &header)
            .unwrap();
        incoming.read_exact(&mut workspace[..body]).unwrap();
        count += 1;
        let response =
            match connection.prepare(h.fds.as_mut().unwrap(), &header, body, &mut workspace) {
                Ok(response) => response,
                Err(_) => {
                    assert!(mode.starts_with("source-"));
                    break;
                }
            };
        let opcode = word(&header, 1);
        let lost = match mode {
            "open-loss" => opcode == 1,
            "close-loss" => opcode == 5,
            "dup-loss" => opcode == 4,
            "flags-loss" => opcode == 6,
            _ => false,
        };
        if lost {
            outgoing.write_all(&response.header()[..prefix]).unwrap();
            drop(response);
            break;
        }
        if mode == "collision" && opcode == 4 {
            let mut broken = *response.header();
            broken[32..40].copy_from_slice(&3_u64.to_le_bytes());
            outgoing.write_all(&broken).unwrap();
        } else {
            outgoing.write_all(response.header()).unwrap();
        }
        outgoing.write_all(response.body()).unwrap();
        response.delivered();
        assert!(workspace.iter().all(|&byte| byte == 0));
        if mode == "denied" && opcode == 2 {
            h.storage.lock().unwrap().deny_read = false;
        }
    }
    drop(outgoing);
    connection.abort(h.fds.as_mut().unwrap());
    assert_eq!(h.fds.as_ref().unwrap().cleanup(), Some([0; 2]));
    assert!(
        child.wait().unwrap().success(),
        "C consumer failed: {mode}/{prefix}"
    );
    let seen = h.storage.lock().unwrap();
    let opcodes = h.opcodes();
    match mode {
        "happy" | "bytewise" => {
            assert_eq!(count, 9);
            assert_eq!(seen.lookups, 1);
            assert_eq!(seen.reads, 2);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 1);
        }
        "full" | "table-stale" => {
            assert_eq!(count, 0);
            assert!(opcodes.is_empty());
        }
        "dup-full" => {
            assert_eq!(count, 2);
            assert_eq!(seen.lookups, 1);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 1);
        }
        "stale-source" => {
            assert_eq!(count, 3);
            assert!(opcodes.is_empty());
        }
        "capacity" => {
            assert_eq!(count, 27);
            assert_eq!(seen.lookups, 13);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 13);
        }
        "hole" => {
            assert_eq!(count, 3);
            assert_eq!(seen.reads, 0);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 1);
        }
        "denied" => {
            assert_eq!(count, 5);
            assert_eq!(seen.reads, 2);
        }
        "open-loss" => {
            assert_eq!(count, 1);
            assert_eq!(seen.lookups, 1);
        }
        "collision" | "dup-loss" => {
            assert_eq!(count, 2);
            assert_eq!(seen.lookups, 1);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 0);
        }
        "close-loss" | "source-close" => {
            assert_eq!(count, 2);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 1);
        }
        _ => {
            assert_eq!(count, 2);
            assert_eq!(seen.lookups, 1);
        }
    }
    drop(seen);
    let storage = h.storage.clone();
    let local = h.local.clone();
    drop(h);
    assert_eq!(storage.lock().unwrap().drops, 1);
    assert_eq!(local.lock().unwrap().closes, 1);
}
