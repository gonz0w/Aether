// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Sole-owner admission across serialized copy and handshake, not a native lock.
use fd_startup::{Binding, Plan};
use filesystem_remote_descriptors::{
    CopyAttempt, CopyInheritanceError, NativeIdentity, Process, ProcessError, ProcessFiles,
};
use filesystem_service::Channel;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Phase {
    Idle,
    Dispatching,
    Receiving,
    Capturing,
    Copying,
    Rejected,
    Bound { pid: u32 },
    Activating,
    Ready { pid: u32 },
    Refused { error: i64 },
    Resolving,
    RefusalSettled { error: i64 },
    Retired,
}
#[derive(Debug, PartialEq, Eq)]
pub enum GateError {
    Closed,
    Sequence,
    Mismatch,
    FileView(ProcessError),
    Streams(i32),
    Capture(i64),
}
/// Trusted owner state, not native authentication. Validation must inspect
/// authoritative state without effects. Activation follows exact context-ready.
pub trait ForkStreams {
    fn validate_fork(&self, plan: &Plan) -> Result<(), i32>;
    fn child_ready(&mut self, pid: u32) -> Result<(), i32>;
}
/// One ordinary exchange, or a fully decoded fork under the SAME admission.
/// Request labels are inert; the caller authenticates the actual process channel.
pub enum Routed<R> {
    Complete,
    Fork { sequence: u64, request: R },
}
/// Own the sole ledger/source and authoritative stream state. No out-of-band
/// aliases/mutation may bypass this gate. Native authentication remains external.
pub struct Owner<T: Channel, S> {
    files: ProcessFiles<T>,
    streams: S,
    phase: Phase,
    sequence: u64,
}
impl<T: Channel, S> Owner<T, S> {
    pub fn new(files: ProcessFiles<T>, streams: S) -> Self {
        Self {
            files,
            streams,
            phase: Phase::Idle,
            sequence: 0,
        }
    }
    /// Construct directly in an exclusive uninitialized slot; no full-gate
    /// stack temporary. Writing fields cannot invoke user Drop or unwind.
    pub fn initialize(
        slot: &mut core::mem::MaybeUninit<Self>,
        files: ProcessFiles<T>,
        streams: S,
    ) -> &mut Self {
        let pointer = slot.as_mut_ptr();
        // SAFETY: slot is aligned, valid exclusive storage for Self. Raw field
        // addresses create no uninitialized Self reference. Every field receives
        // a valid moved value exactly once; no fallible/user operation intervenes.
        // Only after all fields are initialized is the Self reference created.
        unsafe {
            core::ptr::addr_of_mut!((*pointer).files).write(files);
            core::ptr::addr_of_mut!((*pointer).streams).write(streams);
            core::ptr::addr_of_mut!((*pointer).phase).write(Phase::Idle);
            core::ptr::addr_of_mut!((*pointer).sequence).write(0);
            slot.assume_init_mut()
        }
    }
    /// Construct the sole broker in its final field, then move stream ownership.
    /// On returned failure streams is dropped normally and no Owner is exposed.
    #[cfg(all(fs_in_place, not(fs_home_owner)))]
    pub fn connect_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
        streams: S,
    ) -> Result<&mut Self, filesystem_client::ConnectFailure> {
        Self::connect_selected(slot, channel, epoch, streams)
    }
    /// Explicit two-grant construction in the final owner field.
    #[cfg(fs_home_owner)]
    pub fn connect_home_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
        streams: S,
    ) -> Result<&mut Self, filesystem_client::ConnectFailure> {
        Self::connect_selected(slot, channel, epoch, streams)
    }
    #[cfg(fs_in_place)]
    fn connect_selected(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
        streams: S,
    ) -> Result<&mut Self, filesystem_client::ConnectFailure> {
        let pointer = slot.as_mut_ptr();
        // SAFETY: unique aligned uninitialized Owner storage. This projects only
        // its uninitialized FILE field, without creating an Owner reference.
        let files = unsafe {
            &mut *core::ptr::addr_of_mut!((*pointer).files)
                .cast::<core::mem::MaybeUninit<ProcessFiles<T>>>()
        };
        #[cfg(not(fs_home_owner))]
        ProcessFiles::connect_in_place(files, channel, epoch)?;
        #[cfg(fs_home_owner)]
        ProcessFiles::connect_home_in_place(files, channel, epoch)?;
        // SAFETY: FILE success initialized its entire field. The remaining writes
        // move valid values without user callbacks, Drop, allocation or failure.
        // Only after every field is valid is the enclosing Owner published.
        Ok(unsafe {
            core::ptr::addr_of_mut!((*pointer).streams).write(streams);
            core::ptr::addr_of_mut!((*pointer).phase).write(Phase::Idle);
            core::ptr::addr_of_mut!((*pointer).sequence).write(0);
            slot.assume_init_mut()
        })
    }
    pub fn phase(&self) -> Phase {
        self.phase
    }
    pub fn sequence(&self) -> u64 {
        self.sequence
    }
    /// Close before the first mixed-channel prefix. Ordinary completion reopens;
    /// fork completion retains exclusive capture with its actual decoded sequence.
    pub fn route<R>(
        &mut self,
        receive: impl FnOnce(&mut ProcessFiles<T>, &mut S) -> Result<Routed<R>, i64>,
    ) -> Result<Option<R>, GateError> {
        if self.phase != Phase::Idle {
            return Err(GateError::Closed);
        }
        if self.files.cleanup().is_some() {
            self.phase = Phase::Retired;
            return Err(GateError::Closed);
        }
        self.phase = Phase::Receiving;
        match receive(&mut self.files, &mut self.streams) {
            Ok(Routed::Complete) => {
                if self.files.cleanup().is_some() {
                    self.phase = Phase::Retired;
                    return Err(GateError::Closed);
                }
                self.phase = Phase::Idle;
                Ok(None)
            }
            Ok(Routed::Fork { sequence, request }) => {
                if self.files.cleanup().is_some() {
                    self.phase = Phase::Retired;
                    return Err(GateError::Closed);
                }
                if sequence == 0 || sequence <= self.sequence {
                    self.phase = Phase::Rejected;
                    return Err(GateError::Sequence);
                }
                self.sequence = sequence;
                self.phase = Phase::Capturing;
                Ok(Some(request))
            }
            Err(error) => {
                self.phase = if self.files.cleanup().is_some() {
                    Phase::Retired
                } else {
                    Phase::Rejected
                };
                Err(GateError::Capture(error))
            }
        }
    }
    /// All normal file/stream/finish/exec/second-fork admissions go here.
    pub fn admit<R>(
        &mut self,
        operation: impl FnOnce(&mut ProcessFiles<T>, &mut S) -> R,
    ) -> Result<R, GateError> {
        if self.phase != Phase::Idle {
            return Err(GateError::Closed);
        }
        if self.files.cleanup().is_some() {
            self.phase = Phase::Retired;
            return Err(GateError::Closed);
        }
        self.phase = Phase::Dispatching;
        let result = operation(&mut self.files, &mut self.streams);
        self.phase = if self.files.cleanup().is_some() {
            Phase::Retired
        } else {
            Phase::Idle
        };
        Ok(result)
    }
    /// Acquire BEFORE reading/accepting a snapshot. Capture/validate under this
    /// exclusive borrow; keep it as immutable owner data through copy/handshake.
    pub fn begin<R>(
        &mut self,
        sequence: u64,
        capture: impl FnOnce(&mut ProcessFiles<T>, &mut S) -> R,
    ) -> Result<R, GateError> {
        if self.phase != Phase::Idle {
            return Err(GateError::Closed);
        }
        if self.files.cleanup().is_some() {
            self.phase = Phase::Retired;
            return Err(GateError::Closed);
        }
        if sequence == 0 || sequence <= self.sequence {
            return Err(GateError::Sequence);
        }
        self.sequence = sequence;
        self.phase = Phase::Receiving;
        let result = capture(&mut self.files, &mut self.streams);
        self.phase = Phase::Capturing;
        Ok(result)
    }
    /// Close admission before reading a request whose sequence is still in its
    /// body. Decoder returns a private immutable result and its actual sequence.
    pub fn capture<R>(
        &mut self,
        decode: impl FnOnce(&mut ProcessFiles<T>, &mut S) -> Result<(u64, R), i64>,
    ) -> Result<R, GateError> {
        if self.phase != Phase::Idle {
            return Err(GateError::Closed);
        }
        if self.files.cleanup().is_some() {
            self.phase = Phase::Retired;
            return Err(GateError::Closed);
        }
        self.phase = Phase::Receiving;
        let (sequence, result) = match decode(&mut self.files, &mut self.streams) {
            Ok(decoded) => decoded,
            Err(error) => {
                self.phase = Phase::Rejected;
                return Err(GateError::Capture(error));
            }
        };
        if sequence == 0 || sequence <= self.sequence {
            self.phase = Phase::Rejected;
            return Err(GateError::Sequence);
        }
        self.sequence = sequence;
        self.phase = Phase::Capturing;
        Ok(result)
    }
    /// Read-only current FILE key while the full snapshot remains captured.
    /// This neither opens admission nor authenticates a caller-supplied label.
    pub fn captured_process(&self, observed: NativeIdentity) -> Result<Process, GateError> {
        if self.phase != Phase::Capturing {
            return Err(GateError::Closed);
        }
        self.files.current(observed).map_err(GateError::FileView)
    }
    /// Caller already owns the gate before snapshot admission, authenticates
    /// freeze/token/target/channels and supplies only actual native observations.
    /// No snapshot may be reread from resumed parent memory after this point.
    pub fn copy(
        &mut self,
        sequence: u64,
        parent: Process,
        target: NativeIdentity,
        parent_pid: u32,
        plan: &Plan,
        copy: impl FnOnce(&mut S) -> CopyAttempt<i64>,
    ) -> Result<Result<Process, CopyInheritanceError<i64>>, GateError>
    where
        S: ForkStreams,
    {
        if self.phase != Phase::Capturing {
            return Err(GateError::Closed);
        }
        if sequence != self.sequence {
            return Err(GateError::Sequence);
        }
        // Derive from the complete captured map, never from client-supplied masks.
        // No callback/file mutation occurs between comparison and local clone.
        let claimed = match file_claim(&plan.bindings) {
            Some(view) => view,
            None => {
                self.phase = Phase::Rejected;
                return Err(GateError::Mismatch);
            }
        };
        match self.files.file_view_v1(parent) {
            Ok(actual) if actual == claimed => {}
            Ok(_) => {
                self.phase = Phase::Rejected;
                return Err(GateError::Mismatch);
            }
            Err(error) => {
                self.phase = Phase::Rejected;
                return Err(GateError::FileView(error));
            }
        }
        if let Err(error) = self.streams.validate_fork(plan) {
            self.phase = Phase::Rejected;
            return Err(GateError::Streams(error));
        }
        self.phase = Phase::Copying;
        let streams = &mut self.streams;
        let result = self
            .files
            .copy_inherit_serialized_v1(parent, target, parent_pid, || copy(streams));
        self.phase = match &result {
            Ok(_) => Phase::Bound { pid: target.pid },
            Err(CopyInheritanceError::Refused(error)) if (-4095..=-1).contains(error) => {
                Phase::Refused { error: *error }
            }
            _ => {
                self.files.abort();
                Phase::Retired
            }
        };
        Ok(result)
    }
    /// Only the authenticated bound child's exact complete context-ready frame.
    pub fn context_ready(&mut self, sequence: u64, pid: u32) -> Result<(), GateError>
    where
        S: ForkStreams,
    {
        if sequence != self.sequence || self.phase != (Phase::Bound { pid }) {
            return Err(GateError::Mismatch);
        }
        self.phase = Phase::Activating;
        if let Err(error) = self.streams.child_ready(pid) {
            self.retire();
            return Err(GateError::Streams(error));
        }
        self.phase = Phase::Ready { pid };
        Ok(())
    }
    /// Call only AFTER complete successful positive parent disposition delivery.
    pub fn parent_delivered(&mut self, sequence: u64, pid: u32) -> Result<(), GateError> {
        if sequence != self.sequence || self.phase != (Phase::Ready { pid }) {
            return Err(GateError::Mismatch);
        }
        self.phase = Phase::Idle;
        Ok(())
    }
    /// Only known refusal can reconcile staged stream holdings and actual thaw.
    /// No normal admissions are exposed. Return and retain the actual raw result;
    /// uncertain/failed cleanup closes admission without compensating retry.
    pub fn resolve_refusal(
        &mut self,
        sequence: u64,
        error: i64,
        resolve: impl FnOnce(&mut S) -> Result<i64, i64>,
    ) -> Result<Result<i64, i64>, GateError> {
        self.reconcile_refusal(sequence, error, -11, resolve)
    }
    /// Native supervisor-side cancellation result: only raw0 confirms cancellation.
    /// Parent resumes with-11 by the kernel contract, not as an observed callback
    /// value. Staged holdings/reservations must be settled by the caller first.
    /// Preserve and return the actual supervisor result; never normalize it.
    pub fn resolve_native_refusal(
        &mut self,
        sequence: u64,
        error: i64,
        resolve: impl FnOnce(&mut S) -> Result<i64, i64>,
    ) -> Result<Result<i64, i64>, GateError> {
        self.reconcile_refusal(sequence, error, 0, resolve)
    }
    fn reconcile_refusal(
        &mut self,
        sequence: u64,
        error: i64,
        expected: i64,
        resolve: impl FnOnce(&mut S) -> Result<i64, i64>,
    ) -> Result<Result<i64, i64>, GateError> {
        if sequence != self.sequence || self.phase != (Phase::Refused { error }) {
            return Err(GateError::Mismatch);
        }
        self.phase = Phase::Resolving;
        let result = resolve(&mut self.streams);
        if result == Ok(expected) {
            self.phase = Phase::RefusalSettled { error };
        } else {
            self.retire();
        }
        Ok(result)
    }
    /// Only after successful resolution and complete correlated negative reply.
    pub fn refusal_delivered(&mut self, sequence: u64, error: i64) -> Result<(), GateError> {
        if sequence != self.sequence || self.phase != (Phase::RefusalSettled { error }) {
            return Err(GateError::Mismatch);
        }
        self.phase = Phase::Idle;
        Ok(())
    }
    pub fn cleanup(&self) -> Option<[i64; 2]> {
        self.files.cleanup()
    }
    /// Native/resource-owner reconciliation after retirement. No reopening or
    /// file-view settlement is inferred; retain actual native obligations.
    pub fn retired_streams<R>(&mut self, settle: impl FnOnce(&mut S) -> R) -> Result<R, GateError> {
        if self.phase != Phase::Retired {
            return Err(GateError::Closed);
        }
        Ok(settle(&mut self.streams))
    }
    /// Lost/partial handshake or unknown native outcome: stop all admissions.
    pub fn retire(&mut self) {
        self.files.abort();
        self.phase = Phase::Retired;
    }
}

/// Validate map-domain shape while deriving remote FILE bits. Full source/rights/
/// history validation still belongs to request decoding and actual stream capture.
fn file_claim(bindings: &[Binding; 16]) -> Option<(u16, u16)> {
    let (mut presence, mut cloexec) = (0u16, 0u16);
    for binding in bindings {
        if binding.cloexec > 1 {
            return None;
        }
        match binding.kind {
            0 if binding.selector == 0 && binding.cloexec == 0 => {}
            1 if binding.selector <= 2 => {}
            2 if (3..=6).contains(&binding.selector) => {}
            3 if (fd_startup::FIRST_FILE_FD..=15).contains(&binding.selector) => {
                let bit = 1u16 << binding.selector;
                if presence & bit != 0 {
                    return None;
                }
                presence |= bit;
                if binding.cloexec == 1 {
                    cloexec |= bit;
                }
            }
            _ => return None,
        }
    }
    Some((presence, cloexec))
}

const _: () = assert!(fd_startup::FILE_SLOTS_16 == filesystem_remote_descriptors::FILE_SLOTS_16);

#[cfg(fs_home_owner)]
const _: () = assert!(
    cfg!(fs_in_place) && cfg!(fs_home_in_place) && cfg!(fs_home_wire) && cfg!(fs_file_write_wire),
    "home owner requires matched home/in-place/write selections"
);
