// SPDX-License-Identifier: BSD-2-Clause
//! Private directory-only C borrow over the existing AF09 mutation client.
#![no_std]
use core::{
    ffi::c_void,
    mem, ptr, slice,
    sync::atomic::{AtomicBool, Ordering},
};
use filesystem_client::{
    Client, Error, Handle, MutationOutcome, MutationProgress, NamespaceMutation,
};
use filesystem_service::channel::{Framed, Io};

#[cfg(not(all(fs_home_wire, fs_wait)))]
compile_error!("mktemp namespace requires the selected home wire and wait client");
#[cfg(fs_af09_drain)]
compile_error!("mktemp namespace does not select native drain counters");

pub type Transfer = unsafe extern "C" fn(*mut c_void, u32, *mut u8, usize) -> i64;
pub type Wait = unsafe extern "C" fn(*mut c_void, u32) -> i64;
pub type Close = unsafe extern "C" fn(*mut c_void, *mut i64);
pub type Entry = unsafe extern "C" fn(*mut Namespace, *mut c_void) -> i32;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Callbacks {
    pub state: *mut c_void,
    pub transfer: Option<Transfer>,
    pub wait: Option<Wait>,
    pub close: Option<Close>,
}
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Bootstrap {
    pub io: Callbacks,
    pub epoch: u64,
    pub parent_prefix: *const u8,
    pub parent_prefix_length: usize,
}
#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Mutation {
    pub outcome: u32,
    pub progress: u32,
    pub error_kind: u32,
    pub errno_value: u32,
    pub error_value: i64,
    pub txg: u64,
    pub bytes_staged: u64,
}
impl Default for Mutation {
    fn default() -> Self {
        Self {
            outcome: 0,
            progress: 4,
            error_kind: 0,
            errno_value: 0,
            error_value: 0,
            txg: 0,
            bytes_staged: 0,
        }
    }
}
#[repr(C)]
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
pub struct Admission {
    pub phase: u32,
    pub error_kind: u32,
    pub error_value: i64,
    pub errno_value: u32,
    pub endpoints_accepted: u32,
}
#[repr(C)]
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
pub struct Finish {
    pub phase: u32,
    pub disconnect_attempted: u32,
    pub error_kind: u32,
    pub errno_value: u32,
    pub error_value: i64,
    pub cleanup_present: u32,
    pub cleanup_uncertain: u32,
    pub reader_close: i64,
    pub writer_close: i64,
}
#[repr(C)]
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
pub struct Run {
    pub phase: u32,
    pub command_status: u32,
    pub final_status: u32,
    pub reserved_zero: u32,
    pub admission: Admission,
    pub mutation: Mutation,
    pub finalization: Finish,
}
const _: () = {
    assert!(mem::size_of::<Callbacks>() == 32 && mem::align_of::<Callbacks>() == 8);
    assert!(mem::size_of::<Bootstrap>() == 56 && mem::align_of::<Bootstrap>() == 8);
    assert!(mem::offset_of!(Bootstrap, epoch) == 32);
    assert!(mem::offset_of!(Bootstrap, parent_prefix) == 40);
    assert!(mem::offset_of!(Bootstrap, parent_prefix_length) == 48);
    assert!(mem::size_of::<Mutation>() == 40 && mem::align_of::<Mutation>() == 8);
    assert!(mem::offset_of!(Mutation, error_value) == 16);
    assert!(mem::offset_of!(Mutation, txg) == 24);
    assert!(mem::offset_of!(Mutation, bytes_staged) == 32);
    assert!(mem::size_of::<Admission>() == 24 && mem::align_of::<Admission>() == 8);
    assert!(mem::offset_of!(Admission, error_value) == 8);
    assert!(mem::offset_of!(Admission, errno_value) == 16);
    assert!(mem::size_of::<Finish>() == 48 && mem::align_of::<Finish>() == 8);
    assert!(mem::offset_of!(Finish, error_value) == 16);
    assert!(mem::offset_of!(Finish, cleanup_present) == 24);
    assert!(mem::offset_of!(Finish, reader_close) == 32);
    assert!(mem::offset_of!(Finish, writer_close) == 40);
    assert!(mem::size_of::<Run>() == 128 && mem::align_of::<Run>() == 8);
    assert!(mem::offset_of!(Run, admission) == 16);
    assert!(mem::offset_of!(Run, mutation) == 40);
    assert!(mem::offset_of!(Run, finalization) == 80);
};

#[derive(Clone, Copy)]
struct Projection {
    kind: u32,
    errno: u32,
    raw: i64,
}
fn project(error: Error) -> Projection {
    let (kind, errno, raw) = match error {
        Error::Invalid => (1, 22, 0),
        Error::Closed => (2, 9, 0),
        // Private binding-capacity projection, not an allocated FD claim.
        Error::Full => (3, 24, 0),
        Error::Protocol => (4, 5, 0),
        Error::Transport(raw) | Error::Remote(raw) => (
            if matches!(error, Error::Transport(_)) {
                5
            } else {
                6
            },
            if (-4095..=-1).contains(&raw) {
                (-raw) as u32
            } else {
                5
            },
            raw,
        ),
    };
    Projection { kind, errno, raw }
}
fn rejected(error: Error) -> Mutation {
    let p = project(error);
    Mutation {
        error_kind: p.kind,
        errno_value: p.errno,
        error_value: p.raw,
        ..Mutation::default()
    }
}
fn progress(out: &mut Mutation, value: MutationProgress) {
    match value {
        MutationProgress::Unassigned => out.progress = 0,
        MutationProgress::Committed { txg, bytes_staged } => {
            out.progress = 1;
            out.txg = txg;
            out.bytes_staged = bytes_staged as u64;
        }
        MutationProgress::Completed { txg, bytes_staged } => {
            out.progress = 2;
            out.txg = txg;
            out.bytes_staged = bytes_staged as u64;
        }
        MutationProgress::Unknown => out.progress = 3,
    }
}
struct CallbackIo {
    callbacks: Callbacks,
    receipt: Option<[i64; 2]>,
}
impl Io for CallbackIo {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64 {
        let callbacks = self.callbacks;
        let Some(call) = callbacks.transfer else {
            return -5;
        };
        // SAFETY: admitted callbacks own disjoint live state; Framed borrows an
        // initialized chunk<=16 synchronously. Callback retains/reenters nothing.
        unsafe {
            call(
                callbacks.state,
                u32::from(writing),
                bytes.as_mut_ptr(),
                bytes.len(),
            )
        }
    }
    fn wait(&mut self, writing: bool) -> i64 {
        let callbacks = self.callbacks;
        let Some(call) = callbacks.wait else {
            return -5;
        };
        // SAFETY: scalar readiness callback on the same admitted live state.
        unsafe { call(callbacks.state, u32::from(writing)) }
    }
    fn close(&mut self) -> [i64; 2] {
        if let Some(receipt) = self.receipt {
            return receipt;
        }
        let callbacks = self.callbacks;
        let mut receipt = [-5; 2];
        if let Some(call) = callbacks.close {
            // SAFETY: initialized disjoint two-element output borrowed only for
            // this call. Callback consumes both endpoints independently once.
            unsafe { call(callbacks.state, receipt.as_mut_ptr()) };
        }
        self.receipt = Some(receipt);
        receipt
    }
}
/// Opaque C borrow. C cannot construct, copy or inspect the Rust Context.
#[repr(C)]
pub struct Namespace {
    _private: [u8; 0],
}
struct Context {
    client: Option<Client<Framed<CallbackIo>>>,
    parent: Handle,
    prefix_length: usize,
    report: *mut Run,
    attempted: bool,
    busy: bool,
    finished: Option<Finish>,
}
// Admission serialization only, not mutable authority or a second object table.
static ACTIVE: AtomicBool = AtomicBool::new(false);
struct Active;
impl Drop for Active {
    fn drop(&mut self) {
        ACTIVE.store(false, Ordering::Release);
    }
}

unsafe fn finish_context(context: *mut Context) -> Finish {
    // SAFETY: caller holds a live exclusive synchronous opaque borrow; no other
    // operation or foreign callback can access it during these field accesses.
    if let Some(cached) = unsafe { (*context).finished } {
        return cached;
    }
    let mut out = Finish {
        phase: 1,
        ..Finish::default()
    };
    // End the Context borrow BEFORE Client invokes disjoint foreign callbacks.
    let client = unsafe { (*context).client.take() };
    if let Some(mut client) = client {
        if client.cleanup().is_none() {
            out.disconnect_attempted = 1;
            if let Err(error) = client.disconnect() {
                let p = project(error);
                out.error_kind = p.kind;
                out.errno_value = p.errno;
                out.error_value = p.raw;
            }
        }
        if let Some([reader, writer]) = client.cleanup() {
            out.cleanup_present = 1;
            out.reader_close = reader;
            out.writer_close = writer;
            out.cleanup_uncertain = u32::from(reader != 0 || writer != 0 || out.errno_value != 0);
        } else {
            out.cleanup_uncertain = 1;
        }
        // Client shutdown already holds its local receipt: Drop sends nothing.
        drop(client);
    } else {
        out.cleanup_uncertain = 1;
    }
    if out.cleanup_uncertain != 0 && out.errno_value == 0 {
        out.errno_value = 5;
    }
    // SAFETY: admitted report is still valid, no Rust reference was retained
    // across callbacks. Mutation fields are deliberately left untouched.
    unsafe {
        (*context).finished = Some(out);
        (*(*context).report).finalization = out;
        (*(*context).report).phase = 3;
        if out.errno_value != 0 && (*(*context).report).final_status == 0 {
            (*(*context).report).final_status = 1;
        }
    }
    out
}

/// # Safety
/// See namespace.h: initialized aligned caller pointers, disjoint stable state,
/// bounded synchronous callbacks, no reentry/unwind/longjmp, and report lifetime
/// through finalization. Preflight rejection leaves endpoint ownership outside.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn amk_with_namespace(
    bootstrap: *const Bootstrap,
    entry: Option<Entry>,
    application: *mut c_void,
    out: *mut Run,
) -> i32 {
    if out.is_null() || !out.is_aligned() {
        return -22;
    }
    // SAFETY: caller grants writable initialized/aligned output storage.
    unsafe { out.write(Run::default()) };
    let reject = |error: Error| {
        let p = project(error);
        // SAFETY: out remains exclusively borrowed during this local preflight.
        unsafe {
            (*out).phase = 1;
            (*out).admission = Admission {
                phase: 1,
                error_kind: p.kind,
                error_value: p.raw,
                errno_value: p.errno,
                endpoints_accepted: 0,
            };
            (*out).final_status = 1;
        }
        -(p.errno as i32)
    };
    let Some(entry) = entry else {
        return reject(Error::Invalid);
    };
    if bootstrap.is_null() || !bootstrap.is_aligned() {
        return reject(Error::Invalid);
    }
    // SAFETY: caller keeps the complete bootstrap and prefix stable/disjoint.
    let bootstrap = unsafe { bootstrap.read() };
    if bootstrap.epoch == 0
        || bootstrap.io.transfer.is_none()
        || bootstrap.io.wait.is_none()
        || bootstrap.io.close.is_none()
        || bootstrap.parent_prefix.is_null()
        || bootstrap.parent_prefix_length == 0
        || bootstrap.parent_prefix_length > 25
    {
        return reject(Error::Invalid);
    }
    let prefix =
        unsafe { slice::from_raw_parts(bootstrap.parent_prefix, bootstrap.parent_prefix_length) };
    if prefix.first() != Some(&b'/') || prefix.contains(&0) || prefix.last() != Some(&b'/') {
        return reject(Error::Invalid);
    }
    if ACTIVE
        .compare_exchange(false, true, Ordering::Acquire, Ordering::Relaxed)
        .is_err()
    {
        // Busy is an adapter preflight result, never a synthetic Client error.
        unsafe {
            (*out).phase = 1;
            (*out).admission.phase = 1;
            (*out).admission.errno_value = 16;
            (*out).final_status = 1;
        }
        return -16;
    }
    let _active = Active;
    unsafe {
        (*out).phase = 1;
        (*out).admission.endpoints_accepted = 1;
    }
    let client = Client::connect_home(
        Framed(CallbackIo {
            callbacks: bootstrap.io,
            receipt: None,
        }),
        bootstrap.epoch,
    );
    let mut client = match client {
        Ok(client) => client,
        Err(failure) => {
            let p = project(failure.error);
            unsafe {
                (*out).admission = Admission {
                    phase: 2,
                    error_kind: p.kind,
                    error_value: p.raw,
                    errno_value: p.errno,
                    endpoints_accepted: 1,
                };
                (*out).finalization = Finish {
                    phase: 1,
                    cleanup_present: 1,
                    cleanup_uncertain: u32::from(failure.cleanup != [0, 0]),
                    errno_value: if failure.cleanup == [0, 0] { 0 } else { 5 },
                    reader_close: failure.cleanup[0],
                    writer_close: failure.cleanup[1],
                    ..Finish::default()
                };
                (*out).phase = 3;
                (*out).final_status = 1;
            }
            return -(p.errno as i32);
        }
    };
    // connect_home publishes home only after both exact greetings validate.
    let parent = match client.home() {
        Ok(parent) => parent,
        Err(error) => {
            let p = project(error);
            let cleanup = client.abort();
            // SAFETY: even an unexpected local admission failure preserves the
            // initialized caller report and both already-consumed raw closes.
            unsafe {
                (*out).admission = Admission {
                    phase: 2,
                    error_kind: p.kind,
                    error_value: p.raw,
                    errno_value: p.errno,
                    endpoints_accepted: 1,
                };
                (*out).finalization = Finish {
                    phase: 1,
                    cleanup_present: 1,
                    cleanup_uncertain: u32::from(cleanup != [0, 0]),
                    errno_value: if cleanup == [0, 0] { 0 } else { 5 },
                    reader_close: cleanup[0],
                    writer_close: cleanup[1],
                    ..Finish::default()
                };
                (*out).phase = 3;
                (*out).final_status = 1;
            }
            return -(p.errno as i32);
        }
    };
    let mut context = Context {
        client: Some(client),
        parent,
        prefix_length: bootstrap.parent_prefix_length,
        report: out,
        attempted: false,
        busy: false,
        finished: None,
    };
    unsafe {
        (*out).admission.phase = 3;
        (*out).phase = 2;
    }
    let pointer = ptr::addr_of_mut!(context);
    // SAFETY: the local Context address is stable until entry/finish completes.
    // No &mut Context or report lives across C. C must finalize before _exit;
    // terminal exit cannot depend on this frame's Drop or unwind through it.
    let status = unsafe { entry(pointer.cast::<Namespace>(), application) };
    unsafe { finish_context(pointer) };
    unsafe {
        (*out).command_status = if (0..=255).contains(&status) {
            status as u32
        } else {
            1
        };
        if (*out).command_status != 0 {
            (*out).final_status = (*out).command_status;
        }
    }
    0
}

/// # Safety
/// Context must be the live callback borrow; pointers are initialized aligned
/// disjoint storage. No expired object or foreign I/O callback reentry is valid.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn amk_mkdir(
    context: *mut Namespace,
    leaf: *const u8,
    length: usize,
    mode: u32,
    out: *mut Mutation,
) -> i32 {
    let context = context.cast::<Context>();
    if out.is_null() || !out.is_aligned() {
        return -22;
    }
    unsafe { out.write(Mutation::default()) };
    if context.is_null() || !context.is_aligned() {
        unsafe { out.write(rejected(Error::Invalid)) };
        return -22;
    }
    let deny = if unsafe { (*context).finished.is_some() || (*context).attempted } {
        Some(Error::Closed)
    } else if unsafe { (*context).busy } {
        Some(Error::Invalid)
    } else {
        None
    };
    if let Some(error) = deny {
        let value = rejected(error);
        unsafe { out.write(value) };
        return -(value.errno_value as i32);
    }
    let prefix_length = unsafe { (*context).prefix_length };
    if leaf.is_null() || length == 0 || length > 255 || length > 31 - prefix_length || mode != 0o700
    {
        unsafe { out.write(rejected(Error::Invalid)) };
        return -22;
    }
    let name = unsafe { slice::from_raw_parts(leaf, length) };
    if name == b"." || name == b".." || name.iter().any(|b| *b == 0 || *b == b'/') {
        unsafe { out.write(rejected(Error::Invalid)) };
        return -22;
    }
    // Move the client out: no exclusive Context/report borrow spans callbacks.
    unsafe {
        (*context).busy = true;
        (*context).attempted = true;
    }
    let client = unsafe { (*context).client.take() };
    let mut value = Mutation::default();
    if let Some(mut client) = client {
        let parent = unsafe { (*context).parent };
        match client.namespace(parent, NamespaceMutation::MakeDirectory(name)) {
            Ok(completion) => {
                value.outcome = 3;
                value.progress = 2;
                value.txg = completion.txg;
                value.bytes_staged = completion.bytes as u64;
            }
            Err(failure) => {
                value = rejected(failure.error);
                match failure.outcome {
                    MutationOutcome::NotSent => (),
                    MutationOutcome::Unknown => {
                        value.outcome = 2;
                        value.progress = 3;
                    }
                    MutationOutcome::Reported(observed) => {
                        value.outcome = 1;
                        progress(&mut value, observed);
                    }
                }
            }
        }
        unsafe { (*context).client = Some(client) };
    } else {
        value = rejected(Error::Closed);
    }
    unsafe {
        (*context).busy = false;
        (*(*context).report).mutation = value;
        out.write(value);
    }
    -(value.errno_value as i32)
}

/// # Safety
/// Same live borrow/output obligations as amk_mkdir; never call on expired data.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn amk_finish(context: *mut Namespace, out: *mut Finish) -> i32 {
    let context = context.cast::<Context>();
    if out.is_null() || !out.is_aligned() {
        return -22;
    }
    unsafe { out.write(Finish::default()) };
    if context.is_null() || !context.is_aligned() {
        return -22;
    }
    if unsafe { (*context).busy } {
        return -16;
    }
    unsafe { (*context).busy = true };
    let value = unsafe { finish_context(context) };
    unsafe {
        (*context).busy = false;
        out.write(value)
    };
    -(value.errno_value as i32)
}

#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "namespace-tests.rs"]
mod tests;
