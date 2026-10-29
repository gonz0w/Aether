// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Selected one-app native leaves. No Client/FD ancestor is stored or borrowed.
use core::{
    cell::UnsafeCell,
    ffi::c_void,
    ptr,
    sync::atomic::{AtomicBool, Ordering},
};
use mktemp_namespace::{Bootstrap, Callbacks};

const TOTAL: u32 = 100_000;
const RESERVE: u32 = 5;
const WINDOW: u64 = 5_000_000_000;
const RECORD: u64 = 0x0800e200;

#[derive(Clone, Copy)]
struct Budget {
    left: u32,
    deadline: u64,
    last: u64,
    clock: u64,
    initialized: bool,
    error: i64,
}
#[derive(Clone, Copy, Default)]
struct End {
    cap: u64,
    owned: bool,
    attempted: bool,
    result: i64,
}
#[derive(Clone, Copy)]
struct Ledger {
    ends: [End; 4],
    reserve: u32,
    failed: bool,
    terminal: bool,
}
#[derive(Clone, Copy)]
struct Transport {
    reader: u64,
    writer: u64,
}
struct State {
    budget: UnsafeCell<Budget>,
    ledger: UnsafeCell<Ledger>,
    transport: UnsafeCell<Transport>,
    admission: AtomicBool,
    io_busy: AtomicBool,
    finished: AtomicBool,
}
// SAFETY: selected single-context app, no asynchronous handler reentry. Mutable
// borrows are short and disjoint, end before every raw leaf; public callbacks
// guard transport reentry. No mutable ancestor Client/FD pointer is held here.
unsafe impl Sync for State {}
static STATE: State = State {
    budget: UnsafeCell::new(Budget {
        left: TOTAL - RESERVE,
        deadline: 0,
        last: 0,
        clock: 0,
        initialized: false,
        error: 0,
    }),
    ledger: UnsafeCell::new(Ledger {
        ends: [End {
            cap: 0,
            owned: false,
            attempted: false,
            result: -9,
        }; 4],
        reserve: RESERVE,
        failed: false,
        terminal: false,
    }),
    transport: UnsafeCell::new(Transport {
        reader: 0,
        writer: 0,
    }),
    admission: AtomicBool::new(false),
    io_busy: AtomicBool::new(false),
    finished: AtomicBool::new(false),
};
const HOME: [u8; 6] = *b"/home/";

#[repr(C)]
#[derive(Clone, Copy, Default)]
pub struct Receipt {
    pub status: [i64; 4],
    pub attempted: u32,
    pub owned: u32,
    pub failure: i64,
    pub terminal: u32,
    pub reserved: u32,
}

#[cfg(all(amk_native_host, any(target_os = "none", not(test))))]
compile_error!("native app host trap requires host tests only");

#[cfg(target_os = "none")]
#[inline(never)]
fn raw(op: u64, args: [u64; 6]) -> i64 {
    let result: i64;
    // SAFETY: scalar grants and synchronous initialized bounded caller buffers;
    // int81 is a leaf. No Rust reference survives this boundary. All volatile
    // outputs/clobbers are declared; no nomem/preserves_flags assertion.
    unsafe {
        core::arch::asm!("int 0x81",inlateout("rax")op=>result,
        in("rdi")args[0],in("rsi")args[1],inlateout("rdx")args[2]=>_,
        in("r10")args[3],inlateout("r8")args[4]=>_,in("r9")args[5],lateout("rcx")_,lateout("r11")_);
    }
    result
}
#[cfg(all(not(target_os = "none"), amk_native_host, test))]
fn raw(op: u64, args: [u64; 6]) -> i64 {
    tests::raw(op, args)
}
#[cfg(all(not(target_os = "none"), not(all(amk_native_host, test))))]
fn raw(_: u64, _: [u64; 6]) -> i64 {
    -38
}

fn fail(error: i64) -> i64 {
    let error = if error < 0 { error } else { -5 };
    // SAFETY: no live budget/ledger borrow, single-context contract above.
    unsafe {
        let b = &mut *STATE.budget.get();
        if b.error == 0 {
            b.error = error;
        }
        (*STATE.ledger.get()).failed = true;
    }
    error
}
fn spend() -> Result<(), i64> {
    if STATE.finished.load(Ordering::Acquire) {
        return Err(-9);
    }
    // SAFETY: this borrow ends before returning to any leaf or callback.
    let status = unsafe {
        let b = &mut *STATE.budget.get();
        if !b.initialized {
            -9
        } else if b.error != 0 {
            b.error
        } else if b.left == 0 {
            -110
        } else {
            b.left -= 1;
            0
        }
    };
    if status == 0 {
        Ok(())
    } else {
        Err(fail(status))
    }
}
fn observe() -> Result<u64, i64> {
    spend()?;
    let cap = unsafe { (*STATE.budget.get()).clock };
    let value = raw(0x28012, [cap, 0, 0, 0, 0, 0]);
    if value < 0 {
        return Err(fail(value));
    }
    let value = value as u64;
    let status = unsafe {
        let b = &mut *STATE.budget.get();
        if value < b.last {
            -5
        } else if b.deadline != 0 && value >= b.deadline {
            -110
        } else {
            b.last = value;
            0
        }
    };
    if status != 0 {
        Err(fail(status))
    } else {
        Ok(value)
    }
}
fn forward(op: u64, args: [u64; 6]) -> i64 {
    if let Err(error) = observe().and_then(|_| spend()) {
        return error;
    }
    raw(op, args)
}
fn endpoint(cap: u64, end: u64, first: u64, limit: u64) -> bool {
    cap >> 24 == 0xd1
        && cap & 255 == end
        && ((cap >> 8) & 255) > 0
        && ((cap >> 8) & 255) <= if first == 10 { 3 } else { 15 }
        && ((cap >> 16) & 255) >= first
        && ((cap >> 16) & 255) < limit
}
fn word(raw: &[u8; 64], offset: usize) -> u64 {
    u64::from_le_bytes(raw[offset..offset + 8].try_into().unwrap())
}

/// # Safety
/// Copied bytes and output are aligned, initialized, stable, disjoint C storage.
/// source is the actual auxv0xa003 pointer checked before the C copy. Native
/// caller owns the kernel-authored record and process auxv; labels alone confer
/// no authority. No object can move after callback state is exposed.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn amk_native_initialize(
    bytes: *const u8,
    source: u64,
    memory: u64,
    input: u64,
    output: u64,
    out: *mut Bootstrap,
) -> i64 {
    if source != RECORD
        || bytes.is_null()
        || !(bytes as usize).is_multiple_of(8)
        || out.is_null()
        || !out.is_aligned()
    {
        return -22;
    }
    // SAFETY: caller supplies64 initialized readable bytes; pointer validity and
    // disjointness are the FFI contract and null/alignment were checked above.
    let record = unsafe { *(bytes.cast::<[u8; 64]>()) };
    let clock = word(&record, 16);
    let reader = word(&record, 24);
    let writer = word(&record, 32);
    let epoch = word(&record, 40);
    let generation = (memory >> 8) & 255;
    let slot = (memory & 255).wrapping_sub(1);
    let caps = [reader, writer, input, output];
    if record[..8] != *b"AENAP001"
        || word(&record, 8) != 64
        || record[48..56] != *b"/home/\0\0"
        || word(&record, 56) != 0
        || slot != 1
        || generation == 0
        || generation > 15
        || memory != 0x40000000 | generation << 8 | (slot + 1)
        || clock != 0x3600000000000000 | slot << 32 | generation
        || !endpoint(reader, 1, 10, 12)
        || !endpoint(writer, 2, 10, 12)
        || reader >> 16 == writer >> 16
        || epoch != writer & !255 | 1
        || !endpoint(input, 1, 0, 10)
        || !endpoint(output, 2, 0, 10)
        || input >> 16 == output >> 16
        || caps
            .iter()
            .enumerate()
            .any(|(i, cap)| caps[..i].contains(cap))
    {
        return -22;
    }
    if STATE
        .admission
        .compare_exchange(false, true, Ordering::Acquire, Ordering::Relaxed)
        .is_err()
    {
        return -16;
    }
    // SAFETY: once-only admission, all fields are disjoint static scalar storage;
    // record accepted obligations before the first fallible clock observation.
    unsafe {
        *STATE.budget.get() = Budget {
            left: TOTAL - RESERVE,
            deadline: 0,
            last: 0,
            clock,
            initialized: true,
            error: 0,
        };
        *STATE.ledger.get() = Ledger {
            ends: caps.map(|cap| End {
                cap,
                owned: true,
                attempted: false,
                result: -5,
            }),
            reserve: RESERVE,
            failed: false,
            terminal: false,
        };
        *STATE.transport.get() = Transport { reader, writer };
    }
    let first = match observe() {
        Ok(value) => value,
        Err(error) => return error,
    };
    let Some(deadline) = first
        .checked_add(WINDOW)
        .filter(|value| *value <= i64::MAX as u64)
    else {
        return fail(-75);
    };
    // SAFETY: scalar once-only initialization; no budget borrow spans a leaf.
    unsafe {
        (*STATE.budget.get()).deadline = deadline;
    }
    let bootstrap = Bootstrap {
        io: Callbacks {
            state: STATE.transport.get().cast(),
            transfer: Some(ns_transfer),
            wait: Some(ns_wait),
            close: Some(ns_close),
        },
        epoch,
        parent_prefix: HOME.as_ptr(),
        parent_prefix_length: HOME.len(),
    };
    // SAFETY: caller owns aligned writable Bootstrap storage disjoint from the
    // copied record and static callback state for this synchronous constructor.
    unsafe {
        out.write(bootstrap);
    }
    0
}

struct IoGuard;
impl Drop for IoGuard {
    fn drop(&mut self) {
        STATE.io_busy.store(false, Ordering::Release);
    }
}
fn enter_io(state: *mut c_void) -> Result<IoGuard, i64> {
    if state != STATE.transport.get().cast() {
        return Err(-22);
    }
    STATE
        .io_busy
        .compare_exchange(false, true, Ordering::Acquire, Ordering::Relaxed)
        .map_err(|_| -16)?;
    Ok(IoGuard)
}
unsafe extern "C" fn ns_transfer(
    state: *mut c_void,
    writing: u32,
    bytes: *mut u8,
    count: usize,
) -> i64 {
    let _guard = match enter_io(state) {
        Ok(guard) => guard,
        Err(error) => return error,
    };
    if writing > 1 || bytes.is_null() || count == 0 || count > 16 {
        return -22;
    }
    // SAFETY: admission initialized scalar transport, protected by io_busy;
    // copying ends the short borrow before forward can enter a raw leaf.
    let caps = unsafe { *STATE.transport.get() };
    forward(
        if writing == 0 { 0x24001 } else { 0x24002 },
        [
            if writing == 0 {
                caps.reader
            } else {
                caps.writer
            },
            bytes as u64,
            count as u64,
            0,
            0,
            0,
        ],
    )
}
unsafe extern "C" fn ns_wait(state: *mut c_void, writing: u32) -> i64 {
    let _guard = match enter_io(state) {
        Ok(guard) => guard,
        Err(error) => return error,
    };
    if writing > 1 {
        return -22;
    }
    forward(0x1fffe, [0; 6])
}
unsafe extern "C" fn ns_close(state: *mut c_void, out: *mut i64) {
    if state != STATE.transport.get().cast() || out.is_null() || !out.is_aligned() {
        return;
    }
    // SAFETY: only a copied scalar snapshot; caller's Client borrow is disjoint.
    let caps = unsafe { *STATE.transport.get() };
    let results = [close_raw(caps.reader), close_raw(caps.writer)];
    // SAFETY: Close's callback contract supplies two writable disjoint i64s;
    // the local initialized results cannot overlap that caller-owned output.
    unsafe {
        ptr::copy_nonoverlapping(results.as_ptr(), out, 2);
    }
}

fn close_raw(cap: u64) -> i64 {
    // SAFETY: only short ledger access; mark attempt and reserve BEFORE leaf.
    let action = unsafe {
        let ledger = &mut *STATE.ledger.get();
        let Some(index) = ledger
            .ends
            .iter()
            .position(|end| end.owned && end.cap == cap)
        else {
            return -13;
        };
        if ledger.ends[index].attempted {
            return ledger.ends[index].result;
        }
        if ledger.reserve <= 1 {
            ledger.failed = true;
            None
        } else {
            ledger.reserve -= 1;
            ledger.ends[index].attempted = true;
            Some(index)
        }
    };
    let Some(index) = action else {
        fault();
    };
    let result = raw(0x24003, [cap, 0, 0, 0, 0, 0]);
    // SAFETY: fresh short borrow after leaf return; the validated fixed index
    // identifies the entry whose attempt was committed before the call.
    unsafe {
        let ledger = &mut *STATE.ledger.get();
        ledger.ends[index].result = result;
        ledger.failed |= result != 0;
    }
    result
}
fn close_remaining() {
    for index in 0..4 {
        // SAFETY: copied scalar entry, fixed index0..4 and no live ledger borrow
        // when close_raw commits another independent short operation.
        let end = unsafe { (*STATE.ledger.get()).ends[index] };
        if end.owned && !end.attempted {
            let _ = close_raw(end.cap);
        }
    }
}
fn terminal(status: u64, fatal: bool) -> ! {
    // SAFETY: latch terminal before any cleanup. No ledger/client/FD borrow
    // remains while a raw close or terminal leaf executes.
    unsafe {
        let ledger = &mut *STATE.ledger.get();
        if ledger.terminal {
            fault();
        }
        ledger.terminal = true;
        ledger.failed |= fatal;
    }
    close_remaining();
    // SAFETY: a separate fresh scalar borrow; every close receipt is retained.
    let exit = unsafe {
        let ledger = &mut *STATE.ledger.get();
        if ledger.reserve == 0 {
            fault();
        }
        ledger.reserve -= 1;
        if fatal {
            125
        } else if ledger.failed && status == 0 {
            1
        } else {
            status.min(255)
        }
    };
    let _ = raw(0x100e7, [exit, 0, 0, 0, 0, 0]);
    fault()
}
fn fault() -> ! {
    #[cfg(all(amk_native_host, test))]
    {
        tests::fault()
    }
    #[cfg(not(all(amk_native_host, test)))]
    {
        #[cfg(target_arch = "x86_64")]
        // SAFETY: deliberate nonreturning fault boundary; never returns/unwinds
        // across a live foreign callback or attempts to reenter any owner.
        unsafe {
            core::arch::asm!("ud2", options(noreturn));
        }
        #[cfg(target_arch = "aarch64")]
        // SAFETY: same deliberate nonreturning fault boundary on this host ISA.
        unsafe {
            core::arch::asm!("brk #0", options(noreturn));
        }
        #[cfg(not(any(target_arch = "x86_64", target_arch = "aarch64")))]
        loop {
            core::hint::spin_loop();
        }
    }
}

/// Selected aefd callback. Fatal terminal interception MUST precede all ordinary
/// refusal/guards: actual leave has already attempted its two process closes.
#[unsafe(no_mangle)]
pub extern "C" fn amk_native_call(
    _: *mut c_void,
    op: u64,
    cap: u64,
    a: u64,
    b: u64,
    c: u64,
) -> i64 {
    if op == 0x100e7 {
        terminal(125, true);
    }
    if op == 0x24003 {
        return close_raw(cap);
    }
    if matches!(op, 0x24001 | 0x24002 | 0x24004) {
        // aefd owns only the accepted process pair; namespace operations have
        // their own disjoint callbacks. Deny foreign labels before any clock.
        // SAFETY: disjoint stable ledger copied before any forward clock/trap.
        let ledger = unsafe { *STATE.ledger.get() };
        let index = if op == 0x24001 { 2 } else { 3 };
        if op == 0x24004 {
            if !ledger.ends[2..]
                .iter()
                .any(|end| end.owned && !end.attempted && end.cap == cap)
            {
                return -13;
            }
            return forward(0x1fffe, [0; 6]);
        }
        if !ledger.ends[index].owned
            || ledger.ends[index].attempted
            || ledger.ends[index].cap != cap
        {
            return -13;
        }
        if b > 16 || (a == 0 && b != 0) || c != 0 {
            return -22;
        }
    }
    if !matches!(op, 0x1000e | 0x10027 | 0x1006e | 0x24001 | 0x24002) {
        return -38;
    }
    forward(op, [cap, a, b, c, 0, 0])
}
#[unsafe(no_mangle)]
pub extern "C" fn amk_native_clock() -> i64 {
    observe().map_or_else(|error| error, |value| value as i64)
}

/// # Safety
/// Same stable callback state as the namespace entry; the caller owns the
/// exclusive Client borrow. This only accesses separate transport/budget state.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn amk_native_verify(state: *mut c_void) -> i64 {
    let _guard = match enter_io(state) {
        Ok(guard) => guard,
        Err(error) => return error,
    };
    // SAFETY: io_busy admits this verifier only; copied scalar transport ends
    // the borrow before the raw observation leaves.
    let caps = unsafe { *STATE.transport.get() };
    for writing in [false, true] {
        loop {
            let mut byte = [0u8];
            let result = forward(
                if writing { 0x24002 } else { 0x24001 },
                [
                    if writing { caps.writer } else { caps.reader },
                    byte.as_mut_ptr() as u64,
                    1,
                    0,
                    0,
                    0,
                ],
            );
            if result == -11 {
                let wait = forward(0x1fffe, [0; 6]);
                if wait != 0 {
                    return if wait < 0 { wait } else { -5 };
                }
            } else if result == if writing { -32 } else { 0 } {
                break;
            } else {
                return fail(if result < 0 { result } else { -5 });
            }
        }
    }
    0
}
/// # Safety
/// out is aligned, writable disjoint Receipt storage. No logical owner access.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn amk_native_finish_raw(out: *mut Receipt) -> i64 {
    if out.is_null() || !out.is_aligned() {
        return -22;
    }
    if !STATE.admission.load(Ordering::Acquire) {
        return -9;
    }
    close_remaining();
    STATE.finished.store(true, Ordering::Release);
    // SAFETY: cleanup leaves have returned; read disjoint scalar snapshots.
    let (ledger, budget) = unsafe { (*STATE.ledger.get(), *STATE.budget.get()) };
    let mut receipt = Receipt {
        failure: budget.error,
        terminal: u32::from(ledger.terminal),
        ..Receipt::default()
    };
    for (i, end) in ledger.ends.iter().enumerate() {
        receipt.status[i] = end.result;
        receipt.owned |= u32::from(end.owned) << i;
        receipt.attempted |= u32::from(end.attempted) << i;
    }
    if receipt.failure == 0 && ledger.failed {
        receipt.failure = -5;
    }
    // SAFETY: validated writable disjoint Receipt output under the FFI contract.
    unsafe {
        out.write(receipt);
    }
    if receipt.failure == 0 {
        0
    } else {
        receipt.failure
    }
}
#[unsafe(no_mangle)]
pub extern "C" fn amk_native_terminal(status: u32) -> ! {
    terminal(u64::from(status), false)
}

#[cfg(target_os = "none")]
#[panic_handler]
fn panic(_: &core::panic::PanicInfo<'_>) -> ! {
    // A panic may occur while a foreign callback borrow is live. Fault rather
    // than reenter any ledger/client owner; sys-init retains containment duty.
    fault()
}

#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "native-tests.rs"]
mod tests;
