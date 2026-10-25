// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! One mixed-channel exchange under sole-owner admission; native ownership external.
use abi29_dispatch_core::startup::Identity;
use fd_dispatch::Peer;
use fd_startup::{BYTES, Plan};
use filesystem_remote_descriptors::ProcessFiles;
use filesystem_service::{
    Channel,
    channel::{Framed, Io},
};
use fork_gate::{GateError, Owner, Phase, Routed};

struct Workspace<'a>(&'a mut [u8; 4096]);
impl Drop for Workspace<'_> {
    fn drop(&mut self) {
        self.0.fill(0);
    }
}
/// Exact transfer on the SAME owned Io as the FILE Peer. Every call and readiness
/// wait consumes the caller's finite budget. No borrowed slice survives a call.
fn transfer(
    io: &mut impl Io,
    bytes: &mut [u8],
    budget: &mut u32,
    writing: bool,
) -> Result<(), i64> {
    let mut at = 0;
    while at < bytes.len() {
        if *budget == 0 {
            return Err(-110);
        }
        *budget -= 1;
        let count = (bytes.len() - at).min(16);
        let result = io.transfer(writing, &mut bytes[at..at + count]);
        if result == -11 {
            if *budget == 0 {
                return Err(-110);
            }
            *budget -= 1;
            let status = io.wait(writing);
            if status != 0 {
                return Err(if status < 0 { status } else { -5 });
            }
        } else if result <= 0 || result as u64 > count as u64 {
            return Err(if result < 0 { result } else { -5 });
        } else {
            at += result as usize;
        }
    }
    Ok(())
}
fn receive<I: Io>(
    peer: &mut Peer<Framed<I>>,
    bytes: &mut [u8],
    budget: &mut u32,
) -> Result<(), i64> {
    peer.with_channel(|channel| transfer(&mut channel.0, bytes, budget, false))
        .map_err(|_| -9)?
}
/// Deliver a real stream/pipe/wait reply once, on the same authenticated Peer.
/// A caller must retain/fail-stop after partial failure, never replay an effect.
pub fn reply<I: Io>(
    peer: &mut Peer<Framed<I>>,
    bytes: &mut [u8; 32],
    budget: &mut u32,
) -> Result<(), i64> {
    peer.with_channel(|channel| transfer(&mut channel.0, bytes, budget, true))
        .map_err(|_| -9)?
}
fn word(bytes: &[u8], at: usize) -> u32 {
    u32::from_le_bytes(bytes[at..at + 4].try_into().unwrap())
}
fn stream_header(header: &[u8; 64], parent: bool) -> bool {
    match word(header, 0) {
        1..=3 => word(header, 4) != 0 && word(header, 8) < 7 && word(header, 12) <= 16,
        82 => {
            parent && word(header, 4) == 0x76050001 && word(header, 8) == 1 && word(header, 12) == 0
        }
        68 => {
            parent
                && (word(header, 4) == u32::MAX || (1..=110).contains(&word(header, 4)))
                && word(header, 8) <= 1
                && word(header, 12) == 0
        }
        _ => false,
    }
}
/// A callback may defer only a request that has applied NO effects. The caller
/// retains that exact frame in its existing per-process slot, never a new queue.
#[derive(Debug, PartialEq, Eq)]
pub enum Completion {
    Replied,
    Pending,
}
/// A classified FILE exchange survives failed outer admission and retirement.
#[cfg(fs_file_write_wire)]
#[derive(Debug, PartialEq, Eq)]
pub struct FileEvent {
    pub exchange: fd_dispatch::Exchange,
    pub admission: Result<(), GateError>,
}
pub enum Event {
    #[cfg(fs_file_write_wire)]
    File(FileEvent),
    Idle,
    Complete,
    Fork(Plan),
    Pending([u8; 32]),
    Eof,
}
/// The owner supplies authenticated current process identity/parent/generation.
/// Stream callback MUST validate actual source/holder/rights and complete its
/// bounded32-byte reply before success. No default handler, authority or exec wire.
/// Some(plan) leaves the owner Capturing; None completed an ordinary exchange or
/// found an idle peer before consuming any byte. Only the latter may skip a wait.
#[cfg(not(fs_file_write_wire))]
pub fn dispatch<T: Channel, I: Io, S>(
    owner: &mut Owner<T, S>,
    peer: &mut Peer<Framed<I>>,
    expected: (Identity, u32, u64),
    budget: &mut u32,
    workspace: &mut [u8; 4096],
    stream: impl FnOnce(
        &mut ProcessFiles<T>,
        &mut S,
        &mut Peer<Framed<I>>,
        &[u8; 32],
        &mut u32,
    ) -> Result<(), i64>,
) -> Result<Option<Plan>, GateError> {
    match dispatch_inner(
        owner,
        peer,
        expected,
        budget,
        workspace,
        (false, false),
        |files, streams, peer, request, budget| {
            let Request::Stream(frame) = request else {
                return Err(-22);
            };
            stream(files, streams, peer, frame, budget)?;
            Ok(Completion::Replied)
        },
    )? {
        Event::Fork(plan) => Ok(Some(plan)),
        Event::Idle | Event::Complete => Ok(None),
        Event::Pending(_) | Event::Eof => unreachable!(),
    }
}
/// Pending is distinct from delivered effects. Initial EOF grants no authority:
/// the caller must freshly observe this exact native terminal before settlement.
pub fn poll<T: Channel, I: Io, S>(
    owner: &mut Owner<T, S>,
    peer: &mut Peer<Framed<I>>,
    expected: (Identity, u32, u64),
    budget: &mut u32,
    workspace: &mut [u8; 4096],
    stream: impl FnOnce(
        &mut ProcessFiles<T>,
        &mut S,
        &mut Peer<Framed<I>>,
        &[u8; 32],
        &mut u32,
    ) -> Result<Completion, i64>,
) -> Result<Event, GateError> {
    dispatch_inner(
        owner,
        peer,
        expected,
        budget,
        workspace,
        (true, false),
        |files, streams, peer, request, budget| {
            let Request::Stream(frame) = request else {
                return Err(-22);
            };
            stream(files, streams, peer, frame, budget)
        },
    )
}
pub enum Request<'a> {
    Stream(&'a [u8; 32]),
    Exec(&'a mut Plan, u64, &'a [u8; 304]),
}
/// Explicit current exec wire. One callback keeps the same gate closed through
/// native commit, startup publication and readiness, without aliased handlers.
pub fn poll_exec<T: Channel, I: Io, S>(
    owner: &mut Owner<T, S>,
    peer: &mut Peer<Framed<I>>,
    expected: (Identity, u32, u64),
    budget: &mut u32,
    workspace: &mut [u8; 4096],
    operation: impl FnOnce(
        &mut ProcessFiles<T>,
        &mut S,
        &mut Peer<Framed<I>>,
        Request<'_>,
        &mut u32,
    ) -> Result<Completion, i64>,
) -> Result<Event, GateError> {
    dispatch_inner(
        owner,
        peer,
        expected,
        budget,
        workspace,
        (true, true),
        operation,
    )
}
fn dispatch_inner<T: Channel, I: Io, S>(
    owner: &mut Owner<T, S>,
    peer: &mut Peer<Framed<I>>,
    expected: (Identity, u32, u64),
    budget: &mut u32,
    workspace: &mut [u8; 4096],
    mode: (bool, bool),
    operation: impl FnOnce(
        &mut ProcessFiles<T>,
        &mut S,
        &mut Peer<Framed<I>>,
        Request<'_>,
        &mut u32,
    ) -> Result<Completion, i64>,
) -> Result<Event, GateError> {
    let (polling, exec_enabled) = mode;
    let workspace = Workspace(workspace);
    workspace.0.fill(0);
    if owner.phase() != Phase::Idle {
        return Err(GateError::Closed);
    }
    let mut event = Event::Complete;
    #[cfg(fs_file_write_wire)]
    let mut file_event = None;
    let result = owner.route(|files, streams| {
        let mut header = [0; 64];
        if *budget == 0 {
            return Err(-110);
        }
        *budget -= 1;
        let first = peer
            .with_channel(|channel| channel.0.transfer(false, &mut header[..16]))
            .map_err(|_| -9)?;
        if first == -11 {
            event = Event::Idle;
            return Ok(Routed::Complete);
        }
        if first == 0 && polling {
            event = Event::Eof;
            return Ok(Routed::Complete);
        }
        if first <= 0 || first > 16 {
            return Err(if first < 0 { first } else { -5 });
        }
        receive(peer, &mut header[first as usize..16], budget)?;
        if &header[..8] == fd_dispatch::MAGIC {
            receive(peer, &mut header[16..], budget)?;
            #[cfg(fs_file_write_wire)]
            {
                let exchange = peer.serve_received_observed(files, &header, workspace.0);
                let delivery_error = exchange.delivery.as_ref().err().map(|error| match error {
                    fd_dispatch::Error::Transport(raw) => *raw,
                    fd_dispatch::Error::Closed => -9,
                    fd_dispatch::Error::Protocol(_) => -5,
                });
                file_event = Some(FileEvent {
                    exchange,
                    admission: Ok(()),
                });
                if let Some(raw) = delivery_error {
                    return Err(raw);
                }
            }
            #[cfg(not(fs_file_write_wire))]
            peer.serve_received(files, &header, workspace.0)
                .map_err(|error| match error {
                    fd_dispatch::Error::Transport(raw) => raw,
                    fd_dispatch::Error::Closed => -9,
                    fd_dispatch::Error::Protocol(_) => -5,
                })?;
            Ok(Routed::Complete)
        } else if exec_enabled && exec_frames::header(&header[..16]) {
            let (raw, tail) = workspace.0.split_at_mut(exec_frames::BYTES);
            let raw: &mut [u8; 608] = raw.try_into().unwrap();
            raw[..16].copy_from_slice(&header[..16]);
            receive(peer, &mut raw[16..], budget)?;
            let (mut plan, sequence) =
                exec_frames::request(raw, expected, (&mut tail[..304]).try_into().unwrap())
                    .map_err(i64::from)?;
            if operation(
                files,
                streams,
                peer,
                Request::Exec(&mut plan, sequence, raw[304..].try_into().unwrap()),
                budget,
            )? != Completion::Replied
            {
                return Err(-5);
            }
            Ok(Routed::Complete)
        } else if fork_frames::header(&header[..16]) {
            let (raw, tail) = workspace.0.split_at_mut(BYTES);
            let raw: &mut [u8; BYTES] = raw.try_into().unwrap();
            let scratch: &mut [u8; BYTES] = (&mut tail[..BYTES]).try_into().unwrap();
            raw[..16].copy_from_slice(&header[..16]);
            receive(peer, &mut raw[16..], budget)?;
            let (plan, sequence) =
                fork_frames::request(raw, expected.0, expected.1, expected.2, scratch)
                    .map_err(i64::from)?;
            Ok(Routed::Fork {
                sequence,
                request: plan,
            })
        } else if stream_header(&header, expected.0.slot == 1) {
            receive(peer, &mut header[16..32], budget)?;
            let completion = operation(
                files,
                streams,
                peer,
                Request::Stream((&header[..32]).try_into().unwrap()),
                budget,
            )?;
            if completion == Completion::Pending {
                event = Event::Pending(header[..32].try_into().unwrap());
            }
            Ok(Routed::Complete)
        } else {
            Err(-22)
        }
    });
    if result.is_err() {
        owner.retire();
        peer.close();
    }
    #[cfg(fs_file_write_wire)]
    if let Some(mut file) = file_event {
        file.admission = result.map(|_| ());
        file.exchange.cleanup = peer.cleanup();
        return Ok(Event::File(file));
    }
    result.map(|fork| match fork {
        Some(plan) => Event::Fork(plan),
        None => event,
    })
}

const _: () = assert!(fd_startup::FILE_SLOTS_16 == fd_dispatch::FILE_SLOTS_16);
