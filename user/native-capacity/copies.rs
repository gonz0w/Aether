// SPDX-License-Identifier: BSD-2-Clause
//! Authenticated, frozen parent snapshot intake for the native copy witness.
use super::{call, check, ctl, pipe::PipelinePipe, pipeline};

// Callers keep the borrowed buffer alive through this one synchronous trap.
// Zero means EAGAIN only; EOF and invalid counts fail instead of advancing state.
#[inline(never)]
pub(super) fn transfer_once(channel: u64, pointer: u64, remaining: usize, write: bool) -> usize {
    let limit = remaining.min(if write { 7 } else { 16 });
    let count = call(
        if write { 0x24002 } else { 0x24001 },
        channel,
        pointer,
        limit as u64,
        0,
        0,
        0,
    )
    .0;
    if count == -11 {
        return 0;
    }
    check(
        count > 0 && count as usize <= limit,
        if write { 2734 } else { 2730 },
    );
    count as usize
}

#[inline(never)]
fn transfer(channel: u64, mut pointer: u64, mut remaining: usize, write: bool) {
    for _ in 0..100000 {
        let count = transfer_once(channel, pointer, remaining, write);
        remaining -= count;
        pointer += count as u64;
        if remaining == 0 {
            return;
        }
        if count == 0 {
            ctl(0x1fffe, 0);
        }
    }
    super::end(if write { 2734 } else { 2730 })
}
fn receive(reader: u64, bytes: &mut [u8]) {
    transfer(reader, bytes.as_mut_ptr() as u64, bytes.len(), false);
}

#[cfg(pipeline_dash_main)]
#[inline(never)]
pub(super) fn shell_startup(generation: u32, writer: u64) {
    let mut frame = [0; 64];
    for (chunk, value) in frame.chunks_exact_mut(4).zip([
        1000,
        1000,
        1000,
        1000,
        1,
        0,
        0,
        0,
        0x76030000 + generation,
        1,
        1,
        generation,
        0,
        0,
        0,
        0,
    ]) {
        chunk.copy_from_slice(&value.to_le_bytes());
    }
    send(writer, &frame);
}

fn counts(table: &[u8; 64]) -> [u8; 7] {
    let mut users = [0; 7];
    for record in table.chunks_exact(4) {
        if record[2] == 0 {
            continue;
        }
        check(
            (3..7).contains(&record[0])
                || (cfg!(pipeline_stdout_inherit) && record[0] == 1)
                || (cfg!(pipeline_stdio) && record[0] < 3),
            2731,
        );
        users[record[0] as usize] += 1;
    }
    // The shared descriptor validator checks canonical fields and flags;
    // stage/commit independently check the live holder sets on both objects.
    users
}

pub fn stage(
    objects: &mut [PipelinePipe; 2],
    _stdout: &mut super::output::Output,
    generation: u32,
    slot: usize,
    parent: u64,
    reader: u64,
    _writer: u64,
) -> u64 {
    if slot == 2 {
        let mut report = [0; 16];
        receive(reader, &mut report);
        check(
            report[..8] == (generation as u64 * 6 + 1).to_le_bytes()
                && report[8..] == 1u64.to_le_bytes(),
            2730,
        );
    }
    #[cfg(pipeline_factory)]
    if slot == 2 {
        let mut grant = [0; 8];
        grant[..4].copy_from_slice(&super::pipe::FACTORY.to_le_bytes());
        grant[4..].copy_from_slice(&2u32.to_le_bytes());
        send(_writer, &grant);
        #[cfg(pipeline_stdout_inherit)]
        {
            let mut description = [0; 16];
            for (chunk, value) in
                description
                    .chunks_exact_mut(4)
                    .zip([0x7a010000 | generation, 1, 2, 32])
            {
                chunk.copy_from_slice(&value.to_le_bytes());
            }
            send(_writer, &description);
            #[cfg(pipeline_stdio)]
            for binding in [0u32, 2] {
                for (chunk, value) in description.chunks_exact_mut(4).zip([
                    0x7a000000 | (binding << 16) | generation,
                    binding,
                    if binding == 0 { 1 } else { 2 },
                    if binding == 0 { 10 } else { 32 },
                ]) {
                    chunk.copy_from_slice(&value.to_le_bytes());
                }
                send(_writer, &description);
            }
        }
        if !cfg!(pipeline_interleave) {
            for object in [pipeline::Object::First, pipeline::Object::Second] {
                let mut request = [0; 32];
                receive(reader, &mut request);
                let super::pipe::Outcome::Reply(reply) =
                    pipeline::create(objects, object, super::pipe::Caller::Parent, &request)
                else {
                    super::end(2737)
                };
                check(reply[..4] == [0; 4], 2737);
                send(_writer, &reply);
            }
        }
    }
    #[cfg(pipeline_dash_parent)]
    if slot == 2 {
        shell_startup(generation, _writer);
    }
    #[cfg(pipeline_interleave)]
    construction(objects, _stdout, slot, reader, _writer, generation);
    let mut table = [0; 64];
    receive(reader, &mut table);
    let mut expected = [0; 64];
    for binding in 0..7 {
        expected[binding * 4..binding * 4 + 4].copy_from_slice(&[binding as u8, 0, 1, 0]);
    }
    expected[40..44].copy_from_slice(&[3, 1, 1, 0]);
    if !cfg!(pipeline_live) {
        check(table == expected, 2731);
    }
    let mut sequence = 0;
    for _ in 0..100000 {
        let observed = ctl(0x23004, parent).0;
        check(observed >= 0, 2730);
        if observed > 0 {
            sequence = observed as u64;
            break;
        }
        ctl(0x1fffe, 0);
    }
    check(sequence == (slot - 1) as u64, 2730);
    let mut users = if cfg!(pipeline_live) {
        counts(&table)
    } else {
        [1, 1, 1, 2, 1, 1, 1]
    };
    if cfg!(pipeline_bad_snapshot) {
        users[3] = 1;
    }
    check(
        pipeline::stage_fork(
            objects,
            slot - 1,
            generation,
            if cfg!(pipeline_interleave) && (slot == 2 || cfg!(pipeline_shell_early)) {
                [Some(generation), None]
            } else {
                [Some(generation); 2]
            },
            &table,
            &users,
        )
        .is_ok(),
        2731,
    );
    #[cfg(pipeline_stdout_inherit)]
    check(_stdout.stage(slot - 1, users[1] != 0), 2744);
    #[cfg(pipeline_stdio)]
    check(
        _stdout.stage_standard(slot - 1, [users[0] != 0, users[2] != 0]),
        2745,
    );
    sequence
}

#[cfg(pipeline_exec)]
fn send(writer: u64, bytes: &[u8]) {
    transfer(writer, bytes.as_ptr() as u64, bytes.len(), true);
}

#[cfg(all(pipeline_exec, not(pipeline_natural_fds)))]
#[inline(never)]
fn validate_replacement_table(slot: usize, table: &[u8; 64], filtered: &mut [u8; 64]) {
    let mut expected = [0; 64];
    *filtered = [0; 64];
    for binding in 0..7 {
        if cfg!(pipeline_interleave)
            && !match slot {
                2 => (3..5).contains(&binding),
                3 => binding == 3 || binding == 5 || binding == 6,
                _ => binding == 5,
            }
        {
            continue;
        }
        if cfg!(pipeline_live) && binding < 3 {
            continue;
        }
        let keep = (binding < 3 && !cfg!(pipeline_libc))
            || match slot {
                2 => binding == 4,
                3 => binding == 3 || binding == 6,
                _ => binding == 5,
            };
        expected[binding * 4..binding * 4 + 4].copy_from_slice(&[
            binding as u8,
            u8::from(!keep),
            1,
            0,
        ]);
        if keep {
            filtered[binding * 4..binding * 4 + 4].copy_from_slice(&[binding as u8, 0, 1, 0]);
        }
    }
    if !cfg!(pipeline_live) {
        expected[40..44].copy_from_slice(&[3, 1, 1, 0]);
    }
    if cfg!(pipeline_stdout_inherit) {
        expected[4..8].copy_from_slice(&[1, u8::from(slot != 4), 1, 0]);
        if slot == 4 {
            filtered[4..8].copy_from_slice(&[1, 0, 1, 0]);
        }
    }
    if cfg!(pipeline_stdio) {
        expected[..4].copy_from_slice(&[0, u8::from(slot != 2), 1, 0]);
        expected[8..12].copy_from_slice(&[2, 0, 1, 0]);
        if slot == 2 {
            filtered[..4].copy_from_slice(&[0, 0, 1, 0]);
        }
        filtered[8..12].copy_from_slice(&[2, 0, 1, 0]);
    }
    #[cfg(pipeline_exec_io)]
    if slot >= 3 {
        expected[..4].fill(0); // Source closed inherited stdin before exec intake.
    }
    #[cfg(pipeline_exec_remap)]
    {
        let reader = if slot == 3 { 3 } else { 5 };
        expected[..4].copy_from_slice(&[reader as u8, 0, 1, 0]);
        filtered[..4].copy_from_slice(&[reader as u8, 0, 1, 0]);
        expected[reader * 4 + 1] = 1;
        filtered[reader * 4..reader * 4 + 4].fill(0);
        expected[40..44].copy_from_slice(&[reader as u8, 1, 1, 0]);
        if slot == 3 {
            expected[4..8].copy_from_slice(&[6, 0, 1, 0]);
            filtered[4..8].copy_from_slice(&[6, 0, 1, 0]);
            expected[25] = 1;
            filtered[24..28].fill(0);
        }
    }
    check(*table == expected, 2733);
}

#[cfg(all(pipeline_exec, pipeline_natural_fds))]
#[inline(never)]
fn validate_replacement_table(slot: usize, table: &[u8; 64], filtered: &mut [u8; 64]) {
    // Descriptor numbers are local; binding identity survives dup/close.
    *filtered = [0; 64];
    filtered[..4].copy_from_slice(&[
        if cfg!(pipeline_shell_early) {
            if slot == 2 { 0 } else { 3 }
        } else if slot == 3 {
            3
        } else {
            5
        },
        0,
        1,
        0,
    ]);
    filtered[4..8].copy_from_slice(&[
        if cfg!(pipeline_shell_early) {
            if slot == 2 { 4 } else { 1 }
        } else if slot == 3 {
            6
        } else {
            1
        },
        0,
        1,
        0,
    ]);
    filtered[8..12].copy_from_slice(&[2, 0, 1, 0]);
    check(
        (if cfg!(pipeline_shell_early) {
            2..4
        } else {
            3..5
        })
        .contains(&slot)
            && table == filtered,
        2733,
    );
}

// Caller has observed this authenticated child frozen at sequence1.
#[cfg(pipeline_exec)]
#[inline(never)]
fn admit_replacement(generation: u32, handle: u64, slot: usize) {
    #[cfg(pipeline_helper_args)]
    let args = {
        let _ = (generation, slot); // Identity remains native; it is not helper argv.
        let mut args = super::args(b"/inputs/helper");
        args.argc = 2;
        args.strings[1][..4].copy_from_slice(if cfg!(pipeline_shell_early) {
            if slot == 2 { b"pump" } else { b"one\0" }
        } else {
            b"copy"
        });
        #[cfg(pipeline_dash_parent)]
        {
            args.envc = 4;
            for (destination, value) in args.strings[4..].iter_mut().zip([
                &b"PWD=/work"[..],
                &b"WITNESS=value"[..],
                &b"LC_ALL=C"[..],
                &b"PATH=/nonexistent"[..],
            ]) {
                destination[..value.len()].copy_from_slice(value);
            }
        }
        args
    };
    #[cfg(not(pipeline_helper_args))]
    let mut args = super::args(b"replacement");
    #[cfg(not(pipeline_helper_args))]
    {
        args.argc = 3;
        args.strings[1][0] = b'0' + slot as u8;
        args.strings[2][0] = b'0' + generation as u8;
    }
    let pointer = &args as *const super::Args as u64;
    check(
        call(0x23007, 0xa001, handle, 0xffff, 1, pointer, 0).0 == -13,
        2733,
    );
    check(call(0x23008, 0xa001, handle, 0, 0, 0, 0) == (0, 0, 0), 2733);
    check(
        call(0x23007, 0xa001, handle, 0xc002, 1, pointer, 0).0 == 0,
        2733,
    );
    check(
        call(0x23008, 0xa001, handle, 0, 0, 0, 0) == (1, 0xc002, 1),
        2733,
    );
    check(
        ctl(0x20001, handle).1 == 0 && ctl(0x23004, handle).0 == 1,
        2733,
    );
}

// Admission must still be pending. Commit holdings before publishing execution;
// an acknowledgment or completed channel write is not native publication.
#[cfg(pipeline_exec)]
#[inline(never)]
fn commit_replacement(
    objects: &mut [PipelinePipe; 2],
    _stdout: &mut super::output::Output,
    generation: u32,
    handle: u64,
    slot: usize,
    table: &[u8; 64],
    filtered: &[u8; 64],
) {
    let caller = super::pipe::Caller::Participant {
        slot: slot - 1,
        generation,
    };
    let before = if cfg!(pipeline_live) {
        counts(table)
    } else {
        [1, 1, 1, 2, 1, 1, 1]
    };
    let plan = pipeline::commit_exec(
        objects,
        caller,
        [
            Some(generation),
            if cfg!(pipeline_shell_early) {
                None
            } else {
                Some(generation)
            },
        ],
        table,
        &before,
    );
    check(
        plan.as_ref().is_ok_and(|plan| plan.table == *filtered),
        2733,
    );
    #[cfg(pipeline_stdout_inherit)]
    check(
        _stdout.commit(
            slot - 1,
            before[1] != 0,
            plan.as_ref().unwrap().users[1] != 0,
        ),
        2744,
    );
    #[cfg(pipeline_stdio)]
    {
        let after = &plan.as_ref().unwrap().users;
        check(
            _stdout.commit_standard(
                slot - 1,
                [before[0] != 0, before[2] != 0],
                [after[0] != 0, after[2] != 0],
            ),
            2745,
        );
    }
    check(call(0x23009, 0xa001, handle, 0, 0, 0, 0).0 == -9, 2733);
    check(call(0x23009, 0xa001, handle, 1, 0, 0, 0).0 == 0, 2733);
}

// State belongs to one authenticated child. The driver must not change its
// slot/handle/generation or route this channel to I/O before Done.
#[cfg(pipeline_exec)]
#[derive(Clone, Copy, PartialEq)]
enum Phase {
    Request,
    Token,
    Table,
    Freeze,
    Admit,
    Commit,
    Filtered,
    Stdout,
    Stdin,
    Stderr,
    Report,
    Ready,
    Done,
    Cancelled,
}

#[cfg(pipeline_exec)]
pub(super) struct Replacement {
    phase: Phase,
    generation: u32,
    handle: u64,
    slot: usize,
    reader: u64,
    writer: u64,
    #[cfg(pipeline_exec_request)]
    request: super::exec_request::ExecRequest,
    used: usize,
    frame: [u8; 64],
    table: [u8; 64],
    filtered: [u8; 64],
}

#[cfg(pipeline_exec)]
impl Replacement {
    pub(super) fn new(generation: u32, handle: u64, slot: usize, reader: u64, writer: u64) -> Self {
        Self {
            generation,
            handle,
            slot,
            reader,
            writer,
            #[cfg(pipeline_exec_request)]
            request: super::exec_request::ExecRequest::new(),
            phase: if cfg!(pipeline_exec_request) {
                Phase::Request
            } else {
                Phase::Token
            },
            used: 0,
            frame: [0; 64],
            table: [0; 64],
            filtered: [0; 64],
        }
    }

    #[cfg(pipeline_exec_overlap)]
    pub(super) fn done(&self) -> bool {
        self.phase == Phase::Done
    }

    #[cfg(pipeline_exec_overlap)]
    pub(super) fn partial_denial(&self) -> bool {
        self.phase == Phase::Request && self.request.partial_denial()
    }

    #[cfg(pipeline_exec_io)]
    pub(super) fn accepts_io(&self) -> bool {
        self.phase == Phase::Request && self.request.awaiting()
    }

    #[cfg(pipeline_exec_io)]
    pub(super) fn accept_request(&mut self, frame: [u8; 32]) {
        check(self.accepts_io(), 2746);
        self.request.accept(self.generation, self.slot, frame);
    }

    #[cfg(pipeline_exec_overlap_stop)]
    pub(super) fn stop_boundary(&self) -> bool {
        self.slot == 4
            && if cfg!(pipeline_exec_overlap_stop_admit) {
                self.phase == Phase::Commit && self.used == 0
            } else {
                self.phase == Phase::Filtered && self.used == 7
            }
    }

    // Observe the bound instance before discarding any partially sent state.
    #[cfg(pipeline_exec_overlap_stop)]
    #[inline(never)]
    pub(super) fn stopped(&mut self) -> bool {
        check(self.stop_boundary(), 2771);
        let status = ctl(0x20001, self.handle);
        if status.0 == 0 {
            return false;
        }
        check(status.0 == 144 && status.2 == 3 && status.1 == 0, 2771);
        #[cfg(pipeline_exec_overlap_stop_admit)]
        check(
            call(0x23009, 0xa001, self.handle, 1, 0, 0, 0).0 == -16,
            2771,
        );
        if !cfg!(pipeline_exec_overlap_keep_frame) {
            self.advance(Phase::Cancelled);
            self.table = [0; 64];
            self.filtered = [0; 64];
            self.request = super::exec_request::ExecRequest::new();
        }
        check(
            self.phase == Phase::Cancelled
                && self.used == 0
                && self.frame == [0; 64]
                && self.table == [0; 64]
                && self.filtered == [0; 64],
            2772,
        );
        true
    }

    fn advance(&mut self, phase: Phase) {
        self.phase = phase;
        self.used = 0;
        self.frame = [0; 64];
    }

    // A single synchronous trap borrows the current frame; no pointer is retained.
    // Partial progress and EAGAIN return to the driver with the phase unchanged.
    fn transfer(&mut self, channel: u64, length: usize, write: bool, failure: u64) -> bool {
        let limit = (length - self.used).min(if write {
            7
        } else if self.phase == Phase::Report {
            3
        } else {
            16
        });
        let count = call(
            if write { 0x24002 } else { 0x24001 },
            channel,
            self.frame[self.used..].as_mut_ptr() as u64,
            limit as u64,
            0,
            0,
            0,
        )
        .0;
        if count == -11 {
            return false;
        }
        check(count > 0 && count as usize <= limit, failure);
        self.used += count as usize;
        self.used == length
    }

    #[inline(never)]
    pub(super) fn poll(
        &mut self,
        objects: &mut [PipelinePipe; 2],
        stdout: &mut super::output::Output,
    ) {
        let (generation, handle, slot, reader, writer) = (
            self.generation,
            self.handle,
            self.slot,
            self.reader,
            self.writer,
        );
        use Phase::*;
        match self.phase {
            Request => {
                #[cfg(pipeline_exec_io)]
                if self.request.awaiting() {
                    return; // Dispatcher owns ordinary and exec request intake.
                }
                #[cfg(pipeline_exec_request)]
                if self.request.poll(generation, slot, reader, writer) {
                    self.advance(Table);
                }
            }
            Token => {
                self.frame[0] = 2;
                if self.transfer(writer, 1, true, 2734) {
                    self.advance(Table);
                }
            }
            Table => {
                if !self.transfer(reader, 64, false, 2730) {
                    return;
                }
                self.table = self.frame;
                validate_replacement_table(slot, &self.table, &mut self.filtered);
                self.advance(Freeze);
            }
            Freeze => {
                let state = ctl(0x23004, handle).0;
                check(state == 0 || state == 1, 2733);
                if state == 1 {
                    self.advance(Admit);
                }
            }
            Admit => {
                admit_replacement(generation, handle, slot);
                self.advance(if cfg!(pipeline_exec_stop_admit) && slot == 2 {
                    Cancelled
                } else {
                    Commit
                });
            }
            Commit => {
                commit_replacement(
                    objects,
                    stdout,
                    generation,
                    handle,
                    slot,
                    &self.table,
                    &self.filtered,
                );
                if cfg!(pipeline_exec_leak) {
                    self.filtered[40..44].copy_from_slice(&[3, 1, 1, 0]);
                }
                self.advance(Filtered);
                self.frame = self.filtered;
            }
            Filtered => {
                let cancelling = cfg!(pipeline_exec_stop_table) && slot == 2;
                if !self.transfer(writer, if cancelling { 7 } else { 64 }, true, 2734) {
                    return;
                }
                if cancelling {
                    check(ctl(0x20001, handle).1 == 0, 2735);
                    self.advance(Cancelled);
                } else {
                    self.advance(Stdout);
                }
            }
            Stdout | Stdin | Stderr => {
                let binding = match self.phase {
                    Stdout => 1,
                    Stdin => 0,
                    _ => 2,
                };
                let granted = if binding == 1 {
                    cfg!(pipeline_stdout) && slot == if cfg!(pipeline_shell_early) { 3 } else { 4 }
                } else {
                    cfg!(pipeline_stdio) && (binding == 2 || slot == 2)
                };
                if granted {
                    if self.used == 0 {
                        let reference = (0x7a000000 | (binding << 16) | generation)
                            ^ if binding == 1 && cfg!(pipeline_stdout_grant) {
                                1
                            } else {
                                0
                            };
                        for (chunk, value) in self.frame[..16].chunks_exact_mut(4).zip([
                            reference,
                            binding,
                            if binding == 0 { 1 } else { 2 },
                            if binding == 0 { 10 } else { 32 },
                        ]) {
                            chunk.copy_from_slice(&value.to_le_bytes());
                        }
                    }
                    if !self.transfer(writer, 16, true, 2734) {
                        return;
                    }
                }
                self.advance(match self.phase {
                    Stdout => Stdin,
                    Stdin => Stderr,
                    _ => Report,
                });
            }
            Report => {
                check(ctl(0x20001, handle).0 == 0, 2734);
                if !self.transfer(reader, 16, false, 2734) {
                    return;
                }
                check(
                    self.frame[..8] == (generation as u64 * 6 + slot as u64 + 1).to_le_bytes()
                        && self.frame[8..16] == (slot as u64 + 1).to_le_bytes(),
                    2734,
                );
                self.advance(Ready);
            }
            Ready => {
                let status = ctl(0x20001, handle);
                check(status.0 == 0, 2734);
                if status.1 == 1 {
                    self.advance(Done);
                }
            }
            Done | Cancelled => {}
        }
    }
}

#[cfg(pipeline_exec)]
pub fn replace(
    objects: &mut [PipelinePipe; 2],
    stdout: &mut super::output::Output,
    generation: u32,
    handles: &[u64; 5],
    readers: &[u64; 5],
    writers: &[u64; 5],
) -> bool {
    for slot in (if cfg!(pipeline_builtin) { 3 } else { 2 })..5 {
        let mut state = Replacement::new(
            generation,
            handles[slot],
            slot,
            readers[slot],
            writers[slot],
        );
        for _ in 0..100000 {
            state.poll(objects, stdout);
            if state.phase == Phase::Cancelled {
                cancel(
                    objects,
                    generation,
                    handles,
                    &mut state.table,
                    &mut state.filtered,
                );
                // No reader remains after confirmed-stop cancellation.
                state.frame = [0; 64];
                return true;
            }
            if state.phase == Phase::Done {
                break;
            }
            ctl(0x1fffe, 0);
        }
        let timeout = match state.phase {
            Phase::Request => 2746,
            Phase::Table => 2730,
            Phase::Freeze => 2733,
            _ => 2734,
        };
        check(state.phase == Phase::Done, timeout);
    }
    false
}

#[cfg(pipeline_exec)]
fn cancel(
    objects: &mut [PipelinePipe; 2],
    generation: u32,
    handles: &[u64; 5],
    table: &mut [u8; 64],
    filtered: &mut [u8; 64],
) {
    for handle in &handles[2..] {
        check(ctl(0x20007, *handle).0 == 0, 2735);
    }
    for handle in &handles[2..] {
        let mut stopped = false;
        for _ in 0..100000 {
            let status = ctl(0x20001, *handle);
            if status.0 != 0 {
                check(status.0 == 144 && status.2 == 3, 2735);
                stopped = true;
                break;
            }
            ctl(0x1fffe, 0);
        }
        check(stopped, 2735);
    }
    check(call(0x23009, 0xa001, handles[2], 1, 0, 0, 0).0 == -16, 2735);
    // All affected domains are now terminal; no table sender/reader remains live.
    for slot in 2..5 {
        if cfg!(pipeline_exec_keep_holder) && slot == 2 {
            continue;
        }
        let caller = super::pipe::Caller::Participant {
            slot: slot - 1,
            generation,
        };
        check(pipeline::confirmed_terminal(objects, caller).is_ok(), 2735);
    }
    *table = [0; 64];
    *filtered = [0; 64];
    check(
        objects
            .iter_mut()
            .all(|object| object.retire_if_idle([false; 4])),
        2736,
    );
}

#[cfg(pipeline_factory)]
pub fn close_parent(
    objects: &mut [PipelinePipe; 2],
    _stdout: &mut super::output::Output,
    reader: u64,
    writer: u64,
) {
    #[cfg(pipeline_stdout_inherit)]
    {
        let mut frame = [0; 32];
        receive(reader, &mut frame);
        check(frame[..4] == 3u32.to_le_bytes(), 2744);
        check(_stdout.close_parent(&frame) == [0; 32], 2744);
        send(writer, &[0; 32]);
    }
    #[cfg(pipeline_stdio)]
    for _ in 0..2 {
        let mut frame = [0; 32];
        receive(reader, &mut frame);
        check(frame[..4] == 3u32.to_le_bytes(), 2745);
        check(_stdout.close_parent(&frame) == [0; 32], 2745);
        send(writer, &[0; 32]);
    }
    let mut seen = [false; 4];
    for _ in 0..if cfg!(pipeline_interleave) { 1 } else { 4 } {
        let mut frame = [0; 32];
        receive(reader, &mut frame);
        let binding = u32::from_le_bytes(frame[8..12].try_into().unwrap()) as usize;
        check(
            frame[..4] == 3u32.to_le_bytes() && (3..7).contains(&binding),
            2737,
        );
        check(!seen[binding - 3], 2737);
        check(
            pipeline::request(objects, super::pipe::Caller::Parent, &frame)
                == super::pipe::Outcome::Reply([0; 32]),
            2737,
        );
        seen[binding - 3] = true;
        send(writer, &[0; 32]);
    }
}

#[cfg(pipeline_factory)]
pub fn collect(_generation: u32, handles: &[u64; 5], reader: u64, writer: u64) {
    let mut collected = [false; 3];
    for attempt in 0..4 {
        let mut request = [0; 32];
        receive(reader, &mut request);
        check(
            request[..4] == 68u32.to_le_bytes() && request[8..] == [0; 24],
            2738,
        );
        let pid = u32::from_le_bytes(request[4..8].try_into().unwrap());
        let slot = (2..5)
            .find(|&slot| child_pid(handles[slot], slot) == pid as i32)
            .unwrap_or(0);
        let mut reply = [0; 32];
        if !(2..5).contains(&slot) || collected[slot - 2] {
            reply[..4].copy_from_slice(&(-10i32).to_le_bytes());
        } else {
            let terminal = ctl(0x20001, handles[slot]);
            check(terminal.0 > 0 && terminal.2 == 1, 2738);
            let status = ((terminal.0 - 1) as u32) << 8;
            reply[..4].copy_from_slice(&pid.to_le_bytes());
            reply[4..8].copy_from_slice(
                &(status
                    + if cfg!(pipeline_wait_status) && attempt == 2 {
                        256
                    } else {
                        0
                    })
                .to_le_bytes(),
            );
            collected[slot - 2] = true;
        }
        send(writer, &reply);
    }
    check(collected == [true; 3], 2738);
}

#[cfg(pipeline_interleave)]
fn construction(
    objects: &mut [PipelinePipe; 2],
    _stdout: &mut super::output::Output,
    slot: usize,
    reader: u64,
    writer: u64,
    _generation: u32,
) {
    let mut created = false;
    for _ in 0..if cfg!(pipeline_serial) {
        100000
    } else if cfg!(pipeline_dash_parent) {
        16
    } else {
        5
    } {
        let mut frame = [0; 32];
        receive(reader, &mut frame);
        match u32::from_le_bytes(frame[..4].try_into().unwrap()) {
            #[cfg(pipeline_serial)]
            1 | 2 => {
                let mut delivered = false;
                for _ in 0..100000 {
                    let reply = _stdout.close_parent(&frame);
                    if reply[..4] == (-11i32).to_le_bytes() {
                        ctl(0x1fffe, 0);
                        continue;
                    }
                    send(writer, &reply);
                    delivered = true;
                    break;
                }
                check(delivered, 2796);
            }
            #[cfg(pipeline_dash_parent)]
            4 | 5 => {
                let reply = super::startup::directory(0, _generation, &frame);
                send(writer, &reply);
            }
            83 => {
                check(
                    frame[4..8] == 64u32.to_le_bytes() && frame[8..] == [0; 24],
                    2739,
                );
                check(
                    created == (slot < if cfg!(pipeline_shell_early) { 3 } else { 4 }),
                    2739,
                );
                return;
            }
            82 => {
                check(slot < 4 && !created, 2739);
                let object = if slot == 2 {
                    pipeline::Object::First
                } else {
                    pipeline::Object::Second
                };
                let super::pipe::Outcome::Reply(reply) =
                    pipeline::create(objects, object, super::pipe::Caller::Parent, &frame)
                else {
                    super::end(2739)
                };
                check(reply[..4] == [0; 4], 2739);
                created = true;
                send(writer, &reply);
            }
            3 => {
                if !(cfg!(pipeline_keep_parent) && slot == 3 && frame[8..12] == 4u32.to_le_bytes())
                {
                    check(
                        pipeline::request(objects, super::pipe::Caller::Parent, &frame)
                            == super::pipe::Outcome::Reply([0; 32]),
                        2739,
                    );
                }
                send(writer, &[0; 32]);
            }
            _ => super::end(2739),
        }
    }
    super::end(2739)
}

/// Authenticated parent only; numeric PID never selects outside handles[2..5].
#[cfg(pipeline_wait_any)]
pub fn wait_any(generation: u32, handles: &[u64; 5], reader: u64, writer: u64, early: bool) {
    let mut collected = [false; 3];
    for attempt in 0..if early { 3 } else { 4 } {
        let mut request = [0; 32];
        receive(reader, &mut request);
        let pid = i32::from_le_bytes(request[4..8].try_into().unwrap());
        let options = u32::from_le_bytes(request[8..12].try_into().unwrap());
        check(
            request[..4] == 68u32.to_le_bytes()
                && request[12..] == [0; 20]
                && (pid == -1 || pid > 0)
                && options <= 1,
            2740,
        );
        let mut reply = [0; 32];
        let mut complete = false;
        for _ in 0..100000 {
            let mut live = false;
            let mut found = None;
            for slot in 2..5 {
                let child = child_pid(handles[slot], slot);
                if collected[slot - 2] || (pid != -1 && pid != child) {
                    continue;
                }
                let terminal = ctl(0x20001, handles[slot]);
                check(terminal.0 >= 0, 2740);
                if early {
                    check(terminal.0 == 0, 2740);
                }
                if terminal.0 == 0 {
                    live = true;
                    continue;
                }
                check(terminal.2 == 1, 2740);
                found = Some((slot, child, ((terminal.0 - 1) as u32) << 8));
                break;
            }
            if let Some((slot, child, status)) = found {
                reply[..4].copy_from_slice(&child.to_le_bytes());
                reply[4..8].copy_from_slice(&status.to_le_bytes());
                collected[slot - 2] = true;
            } else if !live {
                reply[..4].copy_from_slice(&(-10i32).to_le_bytes());
            } else if options == 0 {
                ctl(0x1fffe, 0);
                continue;
            }
            complete = true;
            break;
        }
        check(complete, 2740);
        if cfg!(pipeline_wait_early) && early && attempt == 1 {
            reply[..4].copy_from_slice(&child_pid(handles[2], 2).to_le_bytes());
        }
        send(writer, &reply);
    }
    check(collected == [!early; 3], 2740);
}

#[cfg(pipeline_wait_any)]
pub fn release(writer: u64) {
    send(writer, &[1]);
}

/// The handle is owner-retained from native admission, never supplied by waitpid.
pub(super) fn child_pid(handle: u64, slot: usize) -> i32 {
    match super::session_children::Identity::admitted(slot, ((handle >> 8) & 0xff) as u32, handle) {
        Ok(identity) => identity.pid,
        Err(_) => super::end(2750),
    }
}
