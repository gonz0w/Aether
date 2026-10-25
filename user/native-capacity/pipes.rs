// SPDX-License-Identifier: BSD-2-Clause
//! Bounded native channel dispatcher for the two-pipe conformance workers.
use super::{call, check, ctl, pipe, pipeline};
use pipe::{Caller, Outcome, PipelinePipe};

fn put(frame: &mut [u8; 32], offset: usize, value: u32) {
    frame[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
}

pub fn create(objects: &mut [PipelinePipe; 2], generation: u32) {
    for object in [pipeline::Object::First, pipeline::Object::Second] {
        let mut frame = [0; 32];
        put(&mut frame, 0, 82);
        put(&mut frame, 4, pipe::FACTORY);
        put(&mut frame, 8, 1);
        let Outcome::Reply(reply) = pipeline::create(objects, object, Caller::Parent, &frame)
        else {
            super::end(2720)
        };
        check(
            reply[..4] == [0; 4]
                && u32::from_le_bytes(reply[4..8].try_into().unwrap()) == generation,
            2720,
        );
    }
}

pub fn prepare(objects: &mut [PipelinePipe; 2], generation: u32, handles: &[u64; 5]) {
    for handle in &handles[2..if cfg!(pipeline_shell_early) { 4 } else { 5 }] {
        let mut ready = false;
        for _ in 0..100000 {
            let state = ctl(0x20001, *handle);
            check(state.0 == 0, 2720);
            if state.1 == 1 {
                ready = true;
                break;
            }
            ctl(0x1fffe, 0);
        }
        check(ready, 2720);
    }
    if !cfg!(pipeline_copy) {
        create(objects, generation);
    }
    for participant in 1..if cfg!(pipeline_shell_early) { 3 } else { 4 } {
        if !cfg!(pipeline_copy) {
            objects[0]
                .stage_participant(
                    participant,
                    generation,
                    [participant == 2, participant == 1],
                )
                .unwrap();
            objects[1]
                .stage_participant(
                    participant,
                    generation,
                    [participant == 3, participant == 2],
                )
                .unwrap();
        }
        // Native readiness has been observed by the enclosing capacity owner.
        check(
            pipeline::finish_copy(objects, participant, generation, true).is_ok(),
            2720,
        );
    }
    if cfg!(pipeline_factory) {
        return;
    }
    for index in 0..2 {
        for end in 1..=2 {
            let mut frame = [0; 32];
            put(&mut frame, 0, 3);
            put(
                &mut frame,
                4,
                0x79000000 | (index << 16) | (generation << 8) | end,
            );
            put(&mut frame, 8, 2 + index * 2 + end);
            check(
                pipeline::request(objects, Caller::Parent, &frame) == Outcome::Reply([0; 32]),
                2720,
            );
        }
    }
}

pub fn dispatch(
    objects: &mut [PipelinePipe; 2],
    _stdout: &mut super::output::Output,
    generation: u32,
    handles: &[u64; 5],
    readers: &[u64; 5],
    writers: &[u64; 5],
) {
    #[cfg(pipeline_wait_io)]
    let mut wait = Wait::new();
    #[cfg(pipeline_exec_overlap)]
    let mut next_exec_slot = if cfg!(pipeline_shell_early) { 2 } else { 3 };
    #[cfg(pipeline_exec_overlap)]
    let mut replacement = super::copies::Replacement::new(
        generation,
        handles[next_exec_slot],
        next_exec_slot,
        readers[next_exec_slot],
        writers[next_exec_slot],
    );
    #[cfg(pipeline_exec_overlap)]
    let (mut held, mut overlapped, mut held_rounds) = (false, false, 0);
    #[cfg(pipeline_exec_overlap_stop)]
    let mut stop_rounds = 0;
    let mut frames = [[0u8; 32]; 3];
    let mut used = [0usize; 3];
    let mut replies: [Option<([u8; 32], usize)>; 3] = [None; 3];
    let mut dead = [false, false, cfg!(pipeline_shell_early)];
    let mut stopping = [false; 3];
    let mut reads = [0u32; 2];
    let mut writes = [0u32; 2];
    let mut eof = [0u32; 2];
    let mut broken = [0u32; 2];
    for _ in 0..100000 {
        #[cfg(pipeline_wait_io)]
        {
            wait.poll(
                generation, handles, readers[0], writers[0], objects, _stdout,
            );
            if !cfg!(pipeline_wait_natural) && !wait.started {
                ctl(0x1fffe, 0);
                continue;
            }
        }
        #[cfg(pipeline_exec_overlap)]
        {
            let mut hold = false;
            if !cfg!(pipeline_dash_parent)
                && next_exec_slot == 3
                && replacement.partial_denial()
                && !overlapped
            {
                if !held {
                    check(writes[0] == 0, 2761);
                    held = true;
                }
                if writes[0] == 0 {
                    held_rounds += 1;
                    if cfg!(pipeline_exec_starve) && held_rounds == 32 {
                        super::end(2760);
                    }
                    hold = true;
                } else {
                    overlapped = true;
                }
            }
            #[cfg(pipeline_exec_overlap_stop)]
            if next_exec_slot == 4 && replacement.stop_boundary() {
                if stop_rounds == 0 && !cfg!(pipeline_exec_overlap_skip_stop) {
                    check(ctl(0x20007, handles[4]).0 == 0, 2771);
                }
                stop_rounds += 1;
                hold = true;
                if replacement.stopped() {
                    check(
                        pipeline::confirmed_terminal(
                            objects,
                            Caller::Participant {
                                slot: 3,
                                generation,
                            },
                        )
                        .is_ok(),
                        2771,
                    );
                    _stdout.stopped_reader();
                    dead[2] = true;
                    next_exec_slot = 5;
                } else if stop_rounds == 32 {
                    super::end(2770);
                }
            }
            if next_exec_slot < if cfg!(pipeline_shell_early) { 4 } else { 5 } && !hold {
                replacement.poll(objects, _stdout);
                if replacement.done() {
                    next_exec_slot += 1;
                    if next_exec_slot < if cfg!(pipeline_shell_early) { 4 } else { 5 } {
                        // Reuse only after readiness: the completed route now
                        // belongs to the I/O decoder, never to both consumers.
                        replacement = super::copies::Replacement::new(
                            generation,
                            handles[next_exec_slot],
                            next_exec_slot,
                            readers[next_exec_slot],
                            writers[next_exec_slot],
                        );
                    }
                }
            }
            if cfg!(pipeline_exec_starve) && held && !overlapped {
                ctl(0x1fffe, 0);
                continue;
            }
        }
        for participant in 0..3 {
            if dead[participant] {
                continue;
            }
            #[cfg(pipeline_exec_overlap)]
            if participant + 2 >= next_exec_slot {
                #[cfg(pipeline_exec_io)]
                if participant + 2 == next_exec_slot && replacement.accepts_io() {
                    // One active replacement; dispatcher owns complete request intake.
                } else {
                    continue;
                }
                #[cfg(not(pipeline_exec_io))]
                continue;
            }
            #[cfg(pipeline_wait_stop)]
            if participant == 2 && !wait.cancelled {
                continue;
            }
            let slot = participant + 2;
            let caller = Caller::Participant {
                slot: participant + 1,
                generation,
            };
            let status = ctl(0x20001, handles[slot]);
            if status.0 != 0 {
                if stopping[participant] {
                    check(status.0 == 144 && status.2 == 3, 2726);
                    if cfg!(pipeline_stop_request) {
                        check(
                            used[participant] == 7 && replies[participant].is_none(),
                            2724,
                        );
                    } else {
                        check(
                            used[participant] == 32
                                && replies[participant].as_ref().unwrap().1 == 7,
                            2724,
                        );
                    }
                    // Stop acceptance alone is insufficient; the exact terminal
                    // record above makes cancellation and holder removal safe.
                    if !cfg!(pipeline_keep_frame) {
                        frames[participant] = [0; 32];
                        used[participant] = 0;
                        replies[participant] = None;
                    }
                } else {
                    check(
                        status.0
                            == if cfg!(pipeline_shell_early) && slot == 2 {
                                43
                            } else {
                                1
                            }
                            && status.2 == 1,
                        2726,
                    );
                }
                check(
                    used[participant] == 0 && replies[participant].is_none(),
                    2724,
                );
                check(pipeline::confirmed_terminal(objects, caller).is_ok(), 2724);
                dead[participant] = true;
                continue;
            }
            if replies[participant].is_none() {
                if used[participant] < 32 {
                    let n = call(
                        0x24001,
                        readers[slot],
                        frames[participant][used[participant]..].as_mut_ptr() as u64,
                        (32 - used[participant]).min(
                            if cfg!(pipeline_stop_request) && participant == 0 {
                                7
                            } else {
                                32
                            },
                        ) as u64,
                        0,
                        0,
                        0,
                    )
                    .0;
                    if n == -11 || n == 0 {
                        continue;
                    }
                    check(n > 0 && n as usize <= 32 - used[participant], 2721);
                    used[participant] += n as usize;
                    if cfg!(pipeline_stop_request) && participant == 0 {
                        check(used[participant] == 7, 2724);
                        check(ctl(0x20007, handles[slot]).0 == 0, 2728);
                        stopping[participant] = true;
                        continue;
                    }
                    if used[participant] < 32 {
                        continue;
                    }
                }
                #[cfg(pipeline_exec_io)]
                if slot == next_exec_slot {
                    check(replacement.accepts_io(), 2790);
                    if frames[participant][..4] == 84u32.to_le_bytes() {
                        replacement.accept_request(frames[participant]);
                        frames[participant] = [0; 32];
                        used[participant] = 0;
                        continue;
                    }
                    check(!cfg!(pipeline_exec_io_reject), 2790);
                }
                let mut request = frames[participant];
                if cfg!(pipeline_wrong_route) {
                    let reference = u32::from_le_bytes(request[4..8].try_into().unwrap());
                    if reference & 0x10000 != 0 {
                        put(&mut request, 4, reference & !0x10000);
                        // No second-pipe write can race the injected reader cancellation.
                        if cfg!(pipeline_exec_overlap_stop)
                            && participant == 1
                            && request[..4] == 2u32.to_le_bytes()
                            && u32::from_le_bytes(request[8..12].try_into().unwrap()) == 6
                            && !dead[2]
                        {
                            continue;
                        }
                        #[cfg(pipeline_exec_io)]
                        if !cfg!(pipeline_dash_parent)
                            && participant == 0
                            && !held
                            && request[..4] == 2u32.to_le_bytes()
                            && u32::from_le_bytes(request[8..12].try_into().unwrap()) == 4
                        {
                            continue;
                        }
                        let binding = u32::from_le_bytes(request[8..12].try_into().unwrap());
                        put(&mut request, 8, binding - 2);
                    }
                }
                // Force the early-reader witness past confirmed terminal cleanup.
                if cfg!(pipeline_early_reader)
                    && request[..4] == 2u32.to_le_bytes()
                    && ((participant == 1 && !dead[2])
                        || (participant == 0 && writes[0] == 10 && !dead[1]))
                {
                    continue;
                }
                // No second-pipe write can race the injected reader cancellation.
                if cfg!(pipeline_exec_overlap_stop)
                    && participant == 1
                    && request[..4] == 2u32.to_le_bytes()
                    && u32::from_le_bytes(request[8..12].try_into().unwrap()) == 6
                    && !dead[2]
                {
                    continue;
                }
                #[cfg(pipeline_exec_io)]
                if !cfg!(pipeline_dash_parent)
                    && participant == 0
                    && !held
                    && request[..4] == 2u32.to_le_bytes()
                    && u32::from_le_bytes(request[8..12].try_into().unwrap()) == 4
                {
                    continue;
                }
                let binding = u32::from_le_bytes(request[8..12].try_into().unwrap());
                let is_output = cfg!(pipeline_stdout)
                    && (binding == 1 || (cfg!(pipeline_stdio) && binding < 3));
                let is_directory = cfg!(pipeline_dash_main)
                    && matches!(u32::from_le_bytes(request[..4].try_into().unwrap()), 4 | 5);
                #[cfg(pipeline_stdout)]
                let outcome = if is_output {
                    let reply = _stdout.request(participant, &request);
                    if cfg!(pipeline_serial) && reply[..4] == (-11i32).to_le_bytes() {
                        continue; // Retry intake only before any UART bytes transferred.
                    }
                    Outcome::Reply(reply)
                } else {
                    #[cfg(pipeline_dash_main)]
                    if is_directory {
                        Outcome::Reply(super::startup::directory(slot, generation, &request))
                    } else {
                        pipeline::request(objects, caller, &request)
                    }
                    #[cfg(not(pipeline_dash_main))]
                    pipeline::request(objects, caller, &request)
                };
                #[cfg(not(pipeline_stdout))]
                let outcome = pipeline::request(objects, caller, &request);
                let Outcome::Reply(mut reply) = outcome else {
                    continue;
                };
                let count = i32::from_le_bytes(reply[..4].try_into().unwrap());

                let object =
                    ((u32::from_le_bytes(request[4..8].try_into().unwrap()) >> 16) & 1) as usize;
                let operation = u32::from_le_bytes(request[..4].try_into().unwrap());
                if is_directory {
                    check(
                        matches!(count, 0 | 6 | -9 | -13 | -22 | -36 | -38 | -2),
                        2793,
                    );
                } else if is_output {
                    check(
                        count >= 0
                            || ((participant == 0 || (cfg!(pipeline_stdio) && participant == 1))
                                && count == -13),
                        2742,
                    );
                } else if count < 0 {
                    check(
                        (cfg!(pipeline_early_reader)
                            || cfg!(pipeline_exec_overlap_stop)
                            || cfg!(pipeline_shell_early))
                            && count == -32
                            && operation == 2,
                        2723,
                    );
                    check(reply[4..] == [0; 28], 2723);
                    broken[object] += 1;
                    if cfg!(pipeline_wrong_errno) {
                        put(&mut reply, 0, (-5i32) as u32);
                    }
                } else {
                    match operation {
                        1 => {
                            reads[object] += count as u32;
                            if count == 0 {
                                eof[object] += 1;
                            }
                        }
                        2 => writes[object] += count as u32,
                        3 => (),
                        _ => super::end(2723),
                    }
                }
                replies[participant] = Some((reply, 0));
            }
            let (reply, sent) = replies[participant].as_mut().unwrap();
            if cfg!(pipeline_reapply)
                && *sent == 7
                && frames[participant][..4] == 2u32.to_le_bytes()
            {
                let _ = pipeline::request(objects, caller, &frames[participant]);
            }
            // Small sends deliberately retain completed effects across iterations.
            let n = call(
                0x24002,
                writers[slot],
                reply[*sent..].as_ptr() as u64,
                (32 - *sent).min(7) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 {
                continue;
            }
            check(n > 0 && n as usize <= (32 - *sent).min(7), 2722);
            *sent += n as usize;
            if cfg!(pipeline_stop_reply) && participant == 0 && *sent == 7 {
                check(ctl(0x20007, handles[slot]).0 == 0, 2728);
                stopping[participant] = true;
                continue;
            }
            if *sent == 32 {
                replies[participant] = None;
                frames[participant] = [0; 32];
                used[participant] = 0;
            }
        }
        if dead == [true; 3] {
            #[cfg(pipeline_exec_overlap)]
            check(cfg!(pipeline_dash_parent) || (held && overlapped), 2761);
            #[cfg(pipeline_wait_io)]
            if !wait.finished() {
                ctl(0x1fffe, 0);
                continue;
            }
            #[cfg(pipeline_stdout)]
            check(_stdout.complete(), 2743);
            if cfg!(pipeline_exec_overlap_stop) {
                check(
                    reads == [10, 0]
                        && writes == [10, 0]
                        && eof == [1, 0]
                        && broken[0] == 0
                        && broken[1] > 0,
                    2725,
                );
            } else if cfg!(pipeline_shell_early) {
                check(
                    reads == [1, 0]
                        && (1..=257).contains(&writes[0])
                        && writes[1] == 0
                        && eof == [0; 2]
                        && broken[0] > 0
                        && broken[1] == 0,
                    2725,
                );
            } else if cfg!(pipeline_early_reader) {
                check(
                    reads == [10, 0] && writes == [10, 0] && eof == [0; 2] && broken == [1; 2],
                    2725,
                );
            } else {
                let bytes = if cfg!(pipeline_stop_request) { 0 } else { 10 };
                check(
                    reads == [bytes; 2] && writes == [bytes; 2] && eof == [1; 2],
                    2725,
                );
                check(broken == [0; 2], 2725);
            }
            check(
                stopping
                    == [
                        cfg!(pipeline_stop_request) || cfg!(pipeline_stop_reply),
                        false,
                        false,
                    ],
                2728,
            );
            let pending = core::array::from_fn(|slot| {
                slot > 0 && (used[slot - 1] != 0 || replies[slot - 1].is_some())
            });
            check(
                objects[..if cfg!(pipeline_shell_early) { 1 } else { 2 }]
                    .iter_mut()
                    .all(|object| object.retire_if_idle(pending)),
                2725,
            );
            return;
        }
        ctl(0x1fffe, 0);
    }
    super::end(2727)
}

#[cfg(pipeline_wait_io)]
struct Wait {
    frame: [u8; 32],
    used: usize,
    replying: bool,
    collected: u8,
    completed: u8,
    started: bool,
    #[cfg(pipeline_dash_parent)]
    parent_closed: u8,
    #[cfg(pipeline_wait_stop)]
    cancelled: bool,
    #[cfg(pipeline_wait_stop)]
    stop_rounds: u8,
}
#[cfg(pipeline_wait_io)]
impl Wait {
    const REPLIES: u8 = if cfg!(pipeline_wait_probes) { 8 } else { 4 };
    fn new() -> Self {
        Self {
            frame: [0; 32],
            used: 0,
            replying: false,
            collected: 0,
            completed: 0,
            started: false,
            #[cfg(pipeline_dash_parent)]
            parent_closed: 0,
            #[cfg(pipeline_wait_stop)]
            cancelled: false,
            #[cfg(pipeline_wait_stop)]
            stop_rounds: 0,
        }
    }
    fn finished(&self) -> bool {
        #[cfg(pipeline_dash_parent)]
        if self.parent_closed != 7 {
            return false;
        }
        #[cfg(pipeline_wait_stop)]
        if self.cancelled {
            check(
                self.completed == 3
                    && self.collected.count_ones() == 1
                    && !self.replying
                    && self.used == 0
                    && self.frame == [0; 32],
                2782,
            );
            return true;
        }
        if cfg!(pipeline_wait_natural) {
            self.collected
                == if cfg!(pipeline_shell_early) {
                    0b01100
                } else {
                    0b11100
                }
                && !self.replying
                && self.used == 0
        } else {
            self.completed == Self::REPLIES
        }
    }

    #[cfg(pipeline_wait_stop)]
    #[inline(never)]
    fn cancel_reply(&mut self, generation: u32, handles: &[u64; 5]) {
        check(self.completed == 3 && self.replying && self.used == 7, 2781);
        let pid = u32::from_le_bytes(self.frame[..4].try_into().unwrap());
        let slot = (2..5)
            .find(|&slot| super::copies::child_pid(handles[slot], slot) == pid as i32)
            .unwrap_or(0);
        check((2..5).contains(&slot) && self.collected == 1 << slot, 2781);
        if self.stop_rounds == 0 {
            check(ctl(0x20001, handles[4]).0 == 0, 2781);
            if !cfg!(pipeline_wait_skip_stop) {
                check(ctl(0x20007, handles[0]).0 == 0, 2781);
            }
        }
        self.stop_rounds += 1;
        let status = ctl(0x20001, handles[0]);
        if status.0 == 0 {
            if self.stop_rounds == 32 {
                super::end(2780);
            }
            return;
        }
        check(status.0 == 144 && status.2 == 3, 2781);
        if cfg!(pipeline_wait_lose_collection) {
            self.collected = 0;
        }
        check(self.collected == 1 << slot, 2781);
        if !cfg!(pipeline_wait_keep_reply) {
            self.frame = [0; 32];
            self.used = 0;
            self.replying = false;
        }
        check(
            self.frame == [0; 32] && self.used == 0 && !self.replying,
            2782,
        );
        self.cancelled = true;
    }

    #[inline(never)]
    fn poll(
        &mut self,
        generation: u32,
        handles: &[u64; 5],
        reader: u64,
        writer: u64,
        _objects: &mut [PipelinePipe; 2],
        _stdout: &mut super::output::Output,
    ) {
        if self.finished() {
            return; // The enclosing owner verifies final parent status before reclaim.
        }
        #[cfg(pipeline_wait_stop)]
        if self.replying && self.used == 7 && self.collected != 0 {
            self.cancel_reply(generation, handles);
            return;
        }
        check(ctl(0x20001, handles[0]).0 == 0, 2750);
        // Test schedule: children must progress without the parent entering wait.
        if cfg!(pipeline_wait_late) && self.completed == 0 && self.used == 0 {
            for handle in &handles[2..] {
                if ctl(0x20001, *handle).0 == 0 {
                    return;
                }
            }
        }
        if !self.replying && self.used < 32 {
            let n = call(
                0x24001,
                reader,
                self.frame[self.used..].as_mut_ptr() as u64,
                (32 - self.used).min(16) as u64,
                0,
                0,
                0,
            )
            .0;
            if n == -11 {
                return;
            }
            check(n > 0 && n as usize <= (32 - self.used).min(16), 2750);
            self.used += n as usize;
            if self.used < 32 {
                return;
            }
        }
        #[cfg(pipeline_dash_parent)]
        if !self.replying && self.frame[..4] != 68u32.to_le_bytes() {
            let op = u32::from_le_bytes(self.frame[..4].try_into().unwrap());
            let binding = u32::from_le_bytes(self.frame[8..12].try_into().unwrap());
            if matches!(op, 4 | 5) {
                self.frame = super::startup::directory(0, generation, &self.frame);
            } else {
                check(
                    op == 3
                        || (cfg!(pipeline_serial) && matches!(op, 1 | 2))
                        || (cfg!(pipeline_shell_early) && op == 2 && binding == 1),
                    2794,
                );
                let reply = if binding < 3 {
                    let reply = _stdout.close_parent(&self.frame);
                    if cfg!(pipeline_serial) && reply[..4] == (-11i32).to_le_bytes() {
                        return; // Keep the complete blocking request; no effect occurred.
                    }
                    if op == 3 {
                        check(
                            reply == [0; 32] && self.parent_closed & (1 << binding) == 0,
                            2794,
                        );
                        self.parent_closed |= 1 << binding;
                    } else if !cfg!(pipeline_serial) {
                        check(
                            reply[..4] == self.frame[12..16] && reply[4..] == [0; 28],
                            2794,
                        );
                    }
                    reply
                } else {
                    let Outcome::Reply(reply) =
                        pipeline::request(_objects, Caller::Parent, &self.frame)
                    else {
                        super::end(2794)
                    };
                    reply
                };
                check(
                    op == 2 || (cfg!(pipeline_serial) && op == 1) || reply == [0; 32],
                    2794,
                );
                self.frame = reply;
            }
            self.used = 0;
            self.replying = true;
        }
        if !self.replying {
            let pid = i32::from_le_bytes(self.frame[4..8].try_into().unwrap());
            let options = u32::from_le_bytes(self.frame[8..12].try_into().unwrap());
            check(
                self.frame[..4] == 68u32.to_le_bytes()
                    && self.frame[12..] == [0; 20]
                    && (pid == -1 || pid > 0)
                    && options <= 1,
                2750,
            );
            let mut live = false;
            let mut found = None;
            for slot in 2..if cfg!(pipeline_shell_early) { 4 } else { 5 } {
                let child = super::copies::child_pid(handles[slot], slot);
                if self.collected & (1 << slot) != 0 || (pid != -1 && pid != child) {
                    continue;
                }
                let terminal = ctl(0x20001, handles[slot]);
                check(terminal.0 >= 0, 2750);
                if terminal.0 == 0 {
                    live = true;
                    continue;
                }
                let status = if cfg!(pipeline_exec_overlap_stop) && slot == 4 {
                    check(terminal.0 == 144 && terminal.2 == 3, 2750);
                    15 // Private native stop maps to SIGTERM, not exit143.
                } else {
                    check(terminal.2 == 1, 2750);
                    ((terminal.0 - 1) as u32) << 8
                };
                found = Some((slot, child, status));
                break;
            }
            if !self.started {
                if !cfg!(pipeline_wait_natural) || cfg!(pipeline_wait_require_live) {
                    check(found.is_none(), 2751);
                }
                self.started = cfg!(pipeline_wait_natural) || (live && options == 0);
            }
            if found.is_none() && live && options == 0 && !cfg!(pipeline_wait_zero) {
                return;
            }
            self.frame = [0; 32];
            if let Some((slot, child, status)) = found {
                put(&mut self.frame, 0, child as u32);
                put(&mut self.frame, 4, status);
                if !cfg!(pipeline_wait_recollect) {
                    self.collected |= 1 << slot;
                }
            } else if !live {
                put(
                    &mut self.frame,
                    0,
                    (if cfg!(pipeline_wait_scope_errno) {
                        -22i32
                    } else {
                        -10i32
                    }) as u32,
                );
            }
            self.used = 0;
            self.replying = true;
        }
        let n = call(
            0x24002,
            writer,
            self.frame[self.used..].as_ptr() as u64,
            (32 - self.used).min(7) as u64,
            0,
            0,
            0,
        )
        .0;
        if n == -11 {
            return;
        }
        check(n > 0 && n as usize <= (32 - self.used).min(7), 2750);
        self.used += n as usize;
        if self.used == 32 {
            self.used = 0;
            self.replying = false;
            if cfg!(pipeline_wait_natural) {
                // Only the forced-late schedule needs to know a reply happened.
                // Collection, never a probe counter, controls normal completion.
                self.completed = 1;
            } else {
                self.completed += 1;
                if self.completed == Self::REPLIES {
                    check(self.collected == 0b11100, 2750);
                }
            }
        }
    }
}
