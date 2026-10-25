// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! One bounded fork request on an authenticated owner endpoint; no cleanup/thaw.
use abi29_dispatch_core::startup::Identity;
use af07_transport::Kernel;
use fd_startup::{BYTES, Plan};
use filesystem_service::Channel;
use fork_gate::{ForkStreams, GateError, Owner, Phase};
struct Buffers<'a> {
    raw: &'a mut [u8; BYTES],
    scratch: &'a mut [u8; BYTES],
}
impl Drop for Buffers<'_> {
    fn drop(&mut self) {
        self.raw.fill(0);
        self.scratch.fill(0);
    }
}
/// The gate closes BEFORE the first read, including when the sequence is unknown.
/// Both caller-owned buffers clear on return/error/host unwind. Native panic-abort
/// does not unwind; the failed owner remains responsible for native obligations.
pub fn receive<T: Channel, S>(
    owner: &mut Owner<T, S>,
    kernel: &mut impl Kernel,
    endpoint: u64,
    expected: (Identity, u32, u64),
    remaining: &mut u32,
    raw: &mut [u8; BYTES],
    scratch: &mut [u8; BYTES],
) -> Result<Plan, GateError> {
    let buffers = Buffers { raw, scratch };
    buffers.raw.fill(0);
    buffers.scratch.fill(0);
    owner.capture(|_, _| {
        request(
            kernel,
            endpoint,
            expected,
            remaining,
            buffers.raw,
            buffers.scratch,
        )
    })
}

/// Same bounded byte-channel mechanism as AF07, with exact fork frame lengths.
/// All counts consume the one caller-owned budget, including EAGAIN/wait retries.
fn read(
    kernel: &mut impl Kernel,
    endpoint: u64,
    bytes: &mut [u8],
    remaining: &mut u32,
) -> Result<(), i64> {
    transfer(kernel, endpoint, bytes, remaining, false)
}

/// Bounded synchronous transfer for the trusted native owner. Endpoint labels
/// must already belong to the actual caller; no pointer survives the operation.
pub fn transfer(
    kernel: &mut impl Kernel,
    endpoint: u64,
    bytes: &mut [u8],
    remaining: &mut u32,
    writing: bool,
) -> Result<(), i64> {
    let mut offset = 0;
    while offset < bytes.len() {
        if *remaining == 0 {
            return Err(-110);
        }
        *remaining -= 1;
        let count = (bytes.len() - offset).min(16);
        let n = kernel.transfer(endpoint, &mut bytes[offset..offset + count], writing);
        if n == -11 {
            // Budget bounds a stream of zero readiness hints as well as reads.
            if *remaining == 0 {
                return Err(-110);
            }
            *remaining -= 1;
            let status = kernel.wait(endpoint);
            if status != 0 {
                return Err(if status < 0 { status } else { -5 });
            }
        } else if n <= 0 || n as u64 > count as u64 {
            return Err(if n < 0 { n } else { -5 });
        } else {
            offset += n as usize;
        }
    }
    Ok(())
}

/// Inert labels supplied only by the actual copy/channel owner. Startup is the
/// exact child plan derived from the captured parent and admitted copy result.
/// Neither these labels nor shape validation authenticates native endpoints.
pub struct Publication<'a> {
    pub sequence: u64,
    pub startup: &'a Plan,
    pub child_writer: u64,
    pub child_reader: u64,
    pub parent_writer: u64,
}
#[derive(Debug, PartialEq, Eq)]
pub enum PublishError {
    Admission(GateError),
    Startup(i32),
    Transport(i64),
    Ready,
    Activation(GateError),
}
struct Scratch<'a>(&'a mut [u8; BYTES]);
impl Drop for Scratch<'_> {
    fn drop(&mut self) {
        self.0.fill(0);
    }
}
/// AFTER actual copy and local FILE publication, while normal admission is closed.
/// All endpoints must be authenticated owned observations, never request labels.
/// Errors after admission retire the source but do not settle native children,
/// holders or endpoints. There is no negative reply, thaw, replay or implicit close.
pub fn publish<T: Channel, S: ForkStreams>(
    owner: &mut Owner<T, S>,
    kernel: &mut impl Kernel,
    request: Publication<'_>,
    remaining: &mut u32,
    scratch: &mut [u8; BYTES],
) -> Result<(), PublishError> {
    let scratch = Scratch(scratch);
    scratch.0.fill(0);
    let pid = request.startup.identity.pid;
    if owner.sequence() != request.sequence || owner.phase() != (Phase::Bound { pid }) {
        return Err(PublishError::Admission(GateError::Mismatch));
    }
    let result = (|| {
        if request.child_writer == 0
            || request.child_reader == 0
            || request.parent_writer == 0
            || request.child_writer == request.child_reader
            || request.child_writer == request.parent_writer
            || request.child_reader == request.parent_writer
        {
            return Err(PublishError::Transport(-9));
        }
        if !(2..=4).contains(&request.startup.identity.slot) {
            return Err(PublishError::Startup(-9));
        }
        fd_startup::encode(request.startup, scratch.0).map_err(PublishError::Startup)?;
        transfer(kernel, request.child_writer, scratch.0, remaining, true)
            .map_err(PublishError::Transport)?;
        scratch.0.fill(0);
        read(
            kernel,
            request.child_reader,
            &mut scratch.0[..32],
            remaining,
        )
        .map_err(PublishError::Transport)?;
        if !fork_frames::ready(&scratch.0[..32], request.sequence, pid) {
            return Err(PublishError::Ready);
        }
        owner
            .context_ready(request.sequence, pid)
            .map_err(PublishError::Activation)?;
        let reply = fork_frames::disposition(request.sequence, i64::from(pid))
            .map_err(PublishError::Startup)?;
        scratch.0[..32].copy_from_slice(&reply);
        transfer(
            kernel,
            request.parent_writer,
            &mut scratch.0[..32],
            remaining,
            true,
        )
        .map_err(PublishError::Transport)?;
        owner
            .parent_delivered(request.sequence, pid)
            .map_err(PublishError::Activation)
    })();
    if result.is_err() {
        owner.retire();
    }
    result
}

/// Known no-child refusal AFTER actual reservation cleanup/token-matched thaw-11
/// has been recorded by resolve_refusal. `error` is the original copy errno,
/// distinct from raw thaw. No new thaw/rollback/retry/endpoint close is performed.
pub fn refuse<T: Channel, S>(
    owner: &mut Owner<T, S>,
    kernel: &mut impl Kernel,
    sequence: u64,
    error: i64,
    parent_writer: u64,
    remaining: &mut u32,
    scratch: &mut [u8; BYTES],
) -> Result<(), PublishError> {
    let scratch = Scratch(scratch);
    scratch.0.fill(0);
    if owner.sequence() != sequence || owner.phase() != (Phase::RefusalSettled { error }) {
        return Err(PublishError::Admission(GateError::Mismatch));
    }
    let result = (|| {
        if parent_writer == 0 {
            return Err(PublishError::Transport(-9));
        }
        let reply = fork_frames::disposition(sequence, error).map_err(PublishError::Startup)?;
        scratch.0[..32].copy_from_slice(&reply);
        transfer(kernel, parent_writer, &mut scratch.0[..32], remaining, true)
            .map_err(PublishError::Transport)?;
        owner
            .refusal_delivered(sequence, error)
            .map_err(PublishError::Activation)
    })();
    if result.is_err() {
        owner.retire();
    }
    result
}
/// Invoke only inside Owner.capture, after authenticating the parent endpoint.
/// Endpoint is an owned native observation; request labels never select it.
/// On failure both buffers are cleared; the outer capture gate remains closed.
/// The caller must still observe/reconcile an already parked parent's real token.
fn request(
    kernel: &mut impl Kernel,
    endpoint: u64,
    expected: (Identity, u32, u64),
    remaining: &mut u32,
    raw: &mut [u8; BYTES],
    scratch: &mut [u8; BYTES],
) -> Result<(u64, Plan), i64> {
    if endpoint == 0 {
        return Err(-9);
    }
    read(kernel, endpoint, &mut raw[..16], remaining)?;
    if !fork_frames::header(&raw[..16]) {
        return Err(-22);
    }
    read(kernel, endpoint, &mut raw[16..], remaining)?;
    let (plan, sequence) = fork_frames::request(raw, expected.0, expected.1, expected.2, scratch)
        .map_err(i64::from)?;
    Ok((sequence, plan))
}
