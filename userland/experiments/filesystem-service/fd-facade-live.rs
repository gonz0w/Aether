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
    if mode == "full" {
        h.storage.lock().unwrap().size = 5003;
    }
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
        if mode == "header" {
            let mut broken = *response.header();
            broken[16] ^= 1;
            outgoing.write_all(&broken).unwrap();
            drop(response);
            break;
        }
        outgoing.write_all(response.header()).unwrap();
        if mode == "body-loss" && opcode == 2 {
            assert_eq!(response.body().len(), 64);
            outgoing.write_all(&response.body()[..prefix]).unwrap();
            drop(response);
            break;
        }
        if mode == "padding" && opcode == 2 {
            let mut broken = response.body().to_vec();
            assert_eq!(broken.len(), 64);
            broken[2] = 1;
            outgoing.write_all(&broken).unwrap();
            drop(response);
            break;
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
    let status = child.wait().unwrap();
    assert!(status.success(), "C consumer failed: {mode}/{prefix}");
    let seen = h.storage.lock().unwrap();
    let opcodes = h.opcodes();
    match mode {
        "local" => {
            assert_eq!(count, 0);
            assert_eq!(seen.lookups, 0);
            assert_eq!(seen.reads, 0);
            assert!(opcodes.is_empty());
        }
        "happy" | "bytewise" => {
            assert_eq!(count, 14);
            assert_eq!(seen.lookups, 2);
            // Three data reads plus the explicit nonzero-length EOF request.
            assert_eq!(seen.reads, 4);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 1);
        }
        "denied" => {
            assert_eq!(count, 4);
            assert_eq!(seen.reads, 2);
        }
        "full" => {
            assert_eq!(count, 4);
            assert_eq!(seen.reads, 2);
        }
        "header" => {
            assert_eq!(count, 1);
            assert_eq!(seen.lookups, 1);
            assert_eq!(seen.reads, 0);
        }
        "source-close" => {
            assert_eq!(count, 2);
            assert_eq!(seen.reads, 0);
            assert_eq!(opcodes.iter().filter(|&&op| op == 3).count(), 1);
        }
        _ => {
            assert_eq!(count, 2);
            assert_eq!(seen.lookups, 1);
            assert_eq!(seen.reads, 1);
            assert_eq!(opcodes.iter().filter(|&&op| op == 2).count(), 1);
        }
    }
    drop(seen);
    let storage = h.storage.clone();
    let local = h.local.clone();
    drop(h);
    assert_eq!(storage.lock().unwrap().drops, 1);
    assert_eq!(local.lock().unwrap().closes, 1);
}
