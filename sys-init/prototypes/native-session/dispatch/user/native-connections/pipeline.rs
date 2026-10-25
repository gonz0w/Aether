// SPDX-License-Identifier: BSD-2-Clause
//! Private two-pipe routing. The dispatcher owns both cores and authenticates
//! Caller independently of frame bytes. This adds no authority or holder ledger.
#[cfg(test)]
use crate::dispatch::pipe::PipelinePipe;
use crate::dispatch::pipe::{Caller, Outcome, SharedPipe};
#[path = "exec_fds.rs"]
mod descriptors;

pub use descriptors::Plan;

fn held(users: &[u8; 7], object: usize) -> [bool; 2] {
    [users[3 + 2 * object] != 0, users[4 + 2 * object] != 0]
}

fn atomic<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    mut change: impl FnMut(usize, &mut SharedPipe<4, SESSION>) -> Result<(), i32>,
) -> Result<(), i32> {
    let mut next = pipes.clone();
    for (index, pipe) in next.iter_mut().enumerate() {
        change(index, pipe)?;
    }
    *pipes = next;
    Ok(())
}

/// Owner has quiesced the source and authenticated the copied descriptor table.
/// Fork retains CLOEXEC aliases; only exec filters them.
pub fn stage_fork<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    slot: usize,
    peer_generation: u32,
    generations: [Option<u32>; 2],
    table: &[u8; 64],
    users: &[u8; 7],
) -> Result<(), i32> {
    descriptors::prepare_pipeline(table, users).map_err(|_| -22)?;
    atomic(pipes, |index, pipe| {
        pipe.check_bindings(Caller::Parent, generations[index], held(users, index))?;
        pipe.stage_participant(slot, peer_generation, held(users, index))
    })
}

/// Call only after actual image admission and while the caller's I/O is quiesced.
/// Recompute from the current frozen table; no cached plan authorizes mutation.
pub fn commit_exec<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    caller: Caller,
    generations: [Option<u32>; 2],
    table: &[u8; 64],
    users: &[u8; 7],
) -> Result<Plan<7>, i32> {
    let plan = descriptors::prepare_pipeline(table, users).map_err(|_| -22)?;
    atomic(pipes, |index, pipe| {
        let before = held(users, index);
        pipe.check_bindings(caller, generations[index], before)?;
        if let Some(generation) = generations[index] {
            pipe.commit_exec(caller, generation, before, held(&plan.users, index))?;
        }
        Ok(())
    })?;
    Ok(plan)
}

/// Ready requires validated copy readiness; false requires known failed copy.
/// Ambiguous outcomes require confirmed terminal, never assumed failure.
pub fn finish_copy<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    slot: usize,
    generation: u32,
    ready: bool,
) -> Result<(), i32> {
    atomic(pipes, |_, pipe| {
        pipe.finish_participant_copy(slot, generation, ready)
    })
}

/// The dispatcher must independently observe this exact caller's terminal.
pub fn confirmed_terminal<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    caller: Caller,
) -> Result<(), i32> {
    atomic(pipes, |_, pipe| pipe.confirmed_terminal(caller))
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Object {
    First,
    Second,
}

impl Object {
    pub const fn index(self) -> usize {
        match self {
            Self::First => 0,
            Self::Second => 1,
        }
    }
}

fn word(frame: &[u8; 32], offset: usize) -> u32 {
    u32::from_le_bytes(frame[offset..offset + 4].try_into().unwrap())
}

fn put(frame: &mut [u8; 32], offset: usize, value: u32) {
    frame[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
}

fn error(code: i32) -> Outcome {
    let mut reply = [0; 32];
    put(&mut reply, 0, code as u32);
    Outcome::Reply(reply)
}

fn reference(object: Object, generation: u32, end: u32) -> u32 {
    0x79000000 | ((object.index() as u32) << 16) | (generation << 8) | end
}

fn binding(object: Object, end: u32) -> u32 {
    2 + 2 * object.index() as u32 + end
}

/// Object selection is the owner's allocation decision, not a wire operation.
/// On uncertain reply delivery retain the completed reply; do not create again.
pub fn create<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    object: Object,
    caller: Caller,
    frame: &[u8; 32],
) -> Outcome {
    if word(frame, 0) != 82 {
        return error(-22);
    }
    let outcome = pipes[object.index()].request(caller, frame);
    let Outcome::Reply(mut reply) = outcome else {
        return outcome;
    };
    if word(&reply, 0) == 0 {
        let generation = word(&reply, 4);
        for end in 1..=2 {
            put(
                &mut reply,
                4 + end as usize * 4,
                reference(object, generation, end),
            );
            put(&mut reply, 12 + end as usize * 4, binding(object, end));
        }
    }
    Outcome::Reply(reply)
}

/// Only data/close frames reach this path. Routing selects an object; its core
/// still enforces caller readiness, endpoint possession and operation rights.
/// Keep the original external frame on Pending, not the local translated copy.
pub fn request<const SESSION: bool>(
    pipes: &mut [SharedPipe<4, SESSION>; 2],
    caller: Caller,
    frame: &[u8; 32],
) -> Outcome {
    if !(1..=3).contains(&word(frame, 0)) {
        return error(-22);
    }
    let handle = word(frame, 4);
    let object = if handle & 0x10000 == 0 {
        Object::First
    } else {
        Object::Second
    };
    let generation = (handle >> 8) & 0xff;
    let end = handle & 0xff;
    if !(1..=SharedPipe::<4, SESSION>::creation_limit()).contains(&generation)
        || !(1..=2).contains(&end)
        || handle != reference(object, generation, end)
        || word(frame, 8) != binding(object, end)
    {
        return error(-13);
    }
    let mut local = *frame;
    put(&mut local, 4, 0x78000000 | (generation << 8) | end);
    put(&mut local, 8, 2 + end);
    pipes[object.index()].request(caller, &local)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::dispatch::pipe::{CAPACITY, FACTORY, REQUEST_BOUND};

    fn factory() -> [u8; 32] {
        let mut frame = [0; 32];
        put(&mut frame, 0, 82);
        put(&mut frame, 4, FACTORY);
        put(&mut frame, 8, 1);
        frame
    }

    fn frame(object: Object, generation: u32, end: u32, op: u32, bytes: &[u8]) -> [u8; 32] {
        let mut frame = [0; 32];
        put(&mut frame, 0, op);
        put(&mut frame, 4, reference(object, generation, end));
        put(&mut frame, 8, binding(object, end));
        put(&mut frame, 12, bytes.len() as u32);
        if op == 2 {
            frame[16..16 + bytes.len()].copy_from_slice(bytes);
        }
        frame
    }

    fn reply(outcome: Outcome) -> [u8; 32] {
        match outcome {
            Outcome::Reply(reply) => reply,
            Outcome::Pending => panic!("unexpected Pending"),
        }
    }

    fn code(outcome: Outcome) -> i32 {
        word(&reply(outcome), 0) as i32
    }

    fn opened() -> [PipelinePipe; 2] {
        let mut pipes = [PipelinePipe::new(), PipelinePipe::new()];
        for object in [Object::First, Object::Second] {
            assert_eq!(
                code(create(&mut pipes, object, Caller::Parent, &factory())),
                0
            );
        }
        pipes
    }

    fn close(pipes: &mut [PipelinePipe; 2], object: Object, generation: u32, end: u32) {
        assert_eq!(
            code(request(
                pipes,
                Caller::Parent,
                &frame(object, generation, end, 3, &[])
            )),
            0
        );
    }

    fn descriptors() -> ([u8; 64], [u8; 7]) {
        let mut table = [0; 64];
        for binding in 0..7 {
            table[binding * 4..binding * 4 + 4].copy_from_slice(&[binding as u8, 0, 1, 0]);
        }
        // A second alias for the first reader at FD10 survives CLOEXEC on FD3.
        table[40..44].copy_from_slice(&[3, 0, 1, 0]);
        table[13] = 1;
        table[21] = 1;
        (table, [1, 1, 1, 2, 1, 1, 1])
    }

    #[test]
    fn session_routes_and_exec_preserve_independent_epochs() {
        use crate::dispatch::pipe::SessionPipe;
        let mut pipes = [SessionPipe::new(), SessionPipe::new()];
        let (table, users) = descriptors();
        // Reuse both pipes nine times while advancing authenticated peer identity.
        for generation in 1..=9 {
            for object in [Object::First, Object::Second] {
                assert_eq!(
                    code(create(&mut pipes, object, Caller::Parent, &factory())),
                    0
                );
            }
            let peer = generation + 6;
            let caller = Caller::Participant {
                slot: 1,
                generation: peer,
            };
            stage_fork(&mut pipes, 1, peer, [Some(generation); 2], &table, &users).unwrap();
            finish_copy(&mut pipes, 1, peer, true).unwrap();
            let before = pipes.clone();
            assert_eq!(
                commit_exec(
                    &mut pipes,
                    caller,
                    [Some(generation), Some(generation + 1)],
                    &table,
                    &users
                ),
                Err(-9)
            );
            assert_eq!(pipes, before);
            commit_exec(&mut pipes, caller, [Some(generation); 2], &table, &users).unwrap();
            assert_eq!(
                code(request(
                    &mut pipes,
                    caller,
                    &frame(Object::First, generation, 2, 2, b"x")
                )),
                1
            );
            // Exec dropped the second reader but cannot affect the first FIFO.
            assert_eq!(
                code(request(
                    &mut pipes,
                    caller,
                    &frame(Object::Second, generation, 1, 1, b"x")
                )),
                -13
            );
            for old in 1..generation {
                assert_eq!(
                    code(request(
                        &mut pipes,
                        Caller::Parent,
                        &frame(Object::First, old, 2, 2, b"x")
                    )),
                    -9
                );
            }
            confirmed_terminal(&mut pipes, caller).unwrap();
            for object in [Object::First, Object::Second] {
                for end in 1..=2 {
                    assert_eq!(
                        code(request(
                            &mut pipes,
                            Caller::Parent,
                            &frame(object, generation, end, 3, &[])
                        )),
                        0
                    );
                }
                assert!(pipes[object.index()].retire_if_idle([false; 4]));
            }
        }
        let before = pipes.clone();
        assert_eq!(
            code(create(
                &mut pipes,
                Object::First,
                Caller::Parent,
                &factory()
            )),
            -23
        );
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::Second, 10, 1, 1, b"x")
            )),
            -13
        );
        assert_eq!(pipes, before);
    }

    #[test]
    fn seven_binding_fork_retains_cloexec_and_exec_drops_only_last_alias() {
        let mut pipes = opened();
        let (table, users) = descriptors();
        stage_fork(&mut pipes, 1, 1, [Some(1); 2], &table, &users).unwrap();
        finish_copy(&mut pipes, 1, 1, true).unwrap();
        let plan = commit_exec(&mut pipes, Caller::Child(1), [Some(1); 2], &table, &users).unwrap();
        assert_eq!(plan.users, [1, 1, 1, 1, 1, 0, 1]);
        assert_eq!(
            plan.release,
            [false, false, false, false, false, true, false]
        );
        assert_eq!(&plan.table[40..44], &[3, 0, 1, 0]);
        assert_eq!(&plan.table[20..24], &[0; 4]);
        // Child loses second reader; parent keeps it and its independent writer.
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Child(1),
                &frame(Object::Second, 1, 1, 1, &[])
            )),
            -13
        );
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::Second, 1, 2, 2, b"q")
            )),
            1
        );
        confirmed_terminal(&mut pipes, Caller::Child(1)).unwrap();
        assert_eq!(
            reply(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::Second, 1, 1, 1, b"x")
            ))[16],
            b'q'
        );
    }

    #[test]
    fn failed_second_exec_preserves_first_fifo_and_all_holders() {
        let mut pipes = opened();
        let mut table = [0; 64];
        for binding in 3..7 {
            table[binding * 4..binding * 4 + 4].copy_from_slice(&[binding as u8, 1, 1, 0]);
        }
        let users = [0, 0, 0, 1, 1, 1, 1];
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::First, 1, 2, 2, b"keep")
            )),
            4
        );
        let before = pipes.clone();
        assert_eq!(
            commit_exec(
                &mut pipes,
                Caller::Parent,
                [Some(1), Some(2)],
                &table,
                &users
            ),
            Err(-9)
        );
        assert_eq!(pipes, before);
        let result = reply(request(
            &mut pipes,
            Caller::Parent,
            &frame(Object::First, 1, 1, 1, b"xxxx"),
        ));
        assert_eq!(&result[16..20], b"keep");
    }

    #[test]
    fn failed_second_stage_readiness_and_terminal_leave_first_unchanged() {
        let mut pipes = opened();
        let (table, users) = descriptors();
        pipes[1].stage_participant(1, 1, [true; 2]).unwrap();
        let before = pipes.clone();
        assert_eq!(
            stage_fork(&mut pipes, 1, 1, [Some(1); 2], &table, &users),
            Err(-13)
        );
        assert_eq!(pipes, before);
        pipes[1].finish_participant_copy(1, 1, false).unwrap();
        pipes[0].stage_participant(1, 1, [true; 2]).unwrap();
        let before = pipes.clone();
        assert_eq!(finish_copy(&mut pipes, 1, 1, true), Err(-9));
        assert_eq!(pipes, before);
        assert_eq!(finish_copy(&mut pipes, 1, 1, false), Err(-9));
        assert_eq!(pipes, before);
        assert_eq!(confirmed_terminal(&mut pipes, Caller::Child(1)), Err(-9));
        assert_eq!(pipes, before);
    }

    #[test]
    fn invalid_tables_counts_and_live_generations_never_stage() {
        let mut pipes = opened();
        let (table, users) = descriptors();
        let before = pipes.clone();
        for bad in [[7, 0, 1, 0], [6, 2, 1, 0], [6, 0, 1, 1], [6, 0, 0, 0]] {
            let mut invalid = table;
            invalid[60..64].copy_from_slice(&bad);
            assert_eq!(
                stage_fork(&mut pipes, 2, 1, [Some(1); 2], &invalid, &users),
                Err(-22)
            );
            assert_eq!(
                commit_exec(&mut pipes, Caller::Parent, [Some(1); 2], &invalid, &users),
                Err(-22)
            );
        }
        assert_eq!(
            stage_fork(&mut pipes, 2, 1, [Some(1); 2], &table, &[0; 7]),
            Err(-22)
        );
        assert_eq!(
            stage_fork(&mut pipes, 2, 1, [Some(1), None], &table, &users),
            Err(-13)
        );
        assert_eq!(
            stage_fork(&mut pipes, 2, 1, [Some(1), Some(2)], &table, &users),
            Err(-9)
        );
        assert_eq!(
            stage_fork(&mut pipes, 2, 1, [Some(1); 2], &[0; 64], &[0; 7]),
            Err(-13)
        );
        assert_eq!(pipes, before);
    }

    #[test]
    fn fork_before_second_creation_and_known_failure_preserve_lifetimes() {
        let mut pipes = [PipelinePipe::new(), PipelinePipe::new()];
        assert_eq!(
            code(create(
                &mut pipes,
                Object::First,
                Caller::Parent,
                &factory()
            )),
            0
        );
        let mut table = [0; 64];
        table[0..4].copy_from_slice(&[3, 1, 1, 0]);
        table[4..8].copy_from_slice(&[4, 0, 1, 0]);
        let users = [0, 0, 0, 1, 1, 0, 0];
        stage_fork(&mut pipes, 1, 1, [Some(1), None], &table, &users).unwrap();
        finish_copy(&mut pipes, 1, 1, false).unwrap();
        stage_fork(&mut pipes, 1, 1, [Some(1), None], &table, &users).unwrap();
        finish_copy(&mut pipes, 1, 1, true).unwrap();
        commit_exec(
            &mut pipes,
            Caller::Child(1),
            [Some(1), None],
            &table,
            &users,
        )
        .unwrap();
        assert_eq!(
            code(create(
                &mut pipes,
                Object::Second,
                Caller::Parent,
                &factory()
            )),
            0
        );
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Child(1),
                &frame(Object::Second, 1, 2, 2, b"x")
            )),
            -13
        );
        confirmed_terminal(&mut pipes, Caller::Child(1)).unwrap();
        let before = pipes.clone();
        assert_eq!(confirmed_terminal(&mut pipes, Caller::Child(1)), Err(-9));
        assert_eq!(pipes, before);
    }

    #[test]
    fn equal_generations_have_distinct_references_and_bindings() {
        let mut pipes = [PipelinePipe::new(), PipelinePipe::new()];
        for object in [Object::First, Object::Second] {
            let result = reply(create(&mut pipes, object, Caller::Parent, &factory()));
            let base = if object == Object::First {
                0x79000100
            } else {
                0x79010100
            };
            assert_eq!(word(&result, 0), 0);
            assert_eq!(word(&result, 4), 1);
            assert_eq!(word(&result, 8), base | 1);
            assert_eq!(word(&result, 12), base | 2);
            assert_eq!(word(&result, 16), 3 + 2 * object.index() as u32);
            assert_eq!(word(&result, 20), 4 + 2 * object.index() as u32);
            assert_eq!(word(&result, 24), CAPACITY as u32);
            assert_eq!(word(&result, 28), REQUEST_BOUND as u32);
        }
    }

    #[test]
    fn equal_generation_data_remains_in_its_object() {
        let mut pipes = opened();
        for (object, bytes) in [(Object::First, b"one"), (Object::Second, b"two")] {
            assert_eq!(
                code(request(
                    &mut pipes,
                    Caller::Parent,
                    &frame(object, 1, 2, 2, bytes)
                )),
                3
            );
        }
        for (object, expected) in [(Object::Second, b"two"), (Object::First, b"one")] {
            let result = reply(request(
                &mut pipes,
                Caller::Parent,
                &frame(object, 1, 1, 1, b"xxx"),
            ));
            assert_eq!(word(&result, 0), 3);
            assert_eq!(&result[16..19], expected);
        }
    }

    #[test]
    fn route_and_binding_do_not_grant_another_objects_holder_rights() {
        let mut pipes = opened();
        for (index, ends) in [(0, [false, true]), (1, [true, false])] {
            pipes[index].stage_participant(1, 1, ends).unwrap();
            pipes[index].finish_participant_copy(1, 1, true).unwrap();
        }
        let before = format!("{pipes:?}");
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Child(1),
                &frame(Object::Second, 1, 2, 2, b"x")
            )),
            -13
        );
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Child(1),
                &frame(Object::First, 1, 1, 1, b"x")
            )),
            -13
        );
        assert_eq!(format!("{pipes:?}"), before);
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Child(1),
                &frame(Object::First, 1, 2, 2, b"x")
            )),
            1
        );
    }

    #[test]
    fn malformed_routes_and_bindings_reject_without_mutation() {
        let mut pipes = opened();
        let before = format!("{pipes:?}");
        let valid = frame(Object::Second, 1, 2, 2, b"x");
        for handle in [
            0, 0x78000102, 0x79020102, 0x79010002, 0x79010402, 0x79010103, 0x79010182, 0xf9010102,
        ] {
            let mut bad = valid;
            put(&mut bad, 4, handle);
            assert_eq!(code(request(&mut pipes, Caller::Parent, &bad)), -13);
        }
        for id in [0, 1, 2, 3, 4, 5, 7, u32::MAX] {
            let mut bad = valid;
            put(&mut bad, 8, id);
            assert_eq!(code(request(&mut pipes, Caller::Parent, &bad)), -13);
        }
        let mut bad = valid;
        bad[31] = 1;
        assert_eq!(code(request(&mut pipes, Caller::Parent, &bad)), -22);
        assert_eq!(format!("{pipes:?}"), before);
    }

    #[test]
    fn reuse_rejects_old_object_without_affecting_other_pipe() {
        let mut pipes = opened();
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::Second, 1, 2, 2, b"live")
            )),
            4
        );
        close(&mut pipes, Object::First, 1, 1);
        close(&mut pipes, Object::First, 1, 2);
        assert!(!pipes[0].retire_if_idle([false, false, false, true]));
        assert!(pipes[0].retire_if_idle([false; 4]));
        assert_eq!(
            word(
                &reply(create(
                    &mut pipes,
                    Object::First,
                    Caller::Parent,
                    &factory()
                )),
                4
            ),
            2
        );
        let before = format!("{pipes:?}");
        for (end, op) in [(1, 1), (2, 2), (1, 3), (2, 3)] {
            assert_eq!(
                code(request(
                    &mut pipes,
                    Caller::Parent,
                    &frame(Object::First, 1, end, op, &[])
                )),
                -9
            );
        }
        assert_eq!(format!("{pipes:?}"), before);
        assert_eq!(
            request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::First, 2, 1, 1, b"x")
            ),
            Outcome::Pending
        );
        let result = reply(request(
            &mut pipes,
            Caller::Parent,
            &frame(Object::Second, 1, 1, 1, b"xxxx"),
        ));
        assert_eq!(&result[16..20], b"live");
    }

    #[test]
    fn creation_is_parent_only_explicit_and_bounded() {
        let mut pipes = [PipelinePipe::new(), PipelinePipe::new()];
        for generation in 1..=3 {
            let result = reply(create(
                &mut pipes,
                Object::First,
                Caller::Parent,
                &factory(),
            ));
            assert_eq!(word(&result, 4), generation);
            let before = format!("{pipes:?}");
            assert_eq!(
                code(create(
                    &mut pipes,
                    Object::First,
                    Caller::Parent,
                    &factory()
                )),
                -23
            );
            assert_eq!(
                code(create(
                    &mut pipes,
                    Object::Second,
                    Caller::Child(1),
                    &factory()
                )),
                -13
            );
            assert_eq!(code(request(&mut pipes, Caller::Parent, &factory())), -22);
            assert_eq!(
                code(create(
                    &mut pipes,
                    Object::Second,
                    Caller::Parent,
                    &frame(Object::First, 1, 2, 3, &[])
                )),
                -22
            );
            assert_eq!(format!("{pipes:?}"), before);
            close(&mut pipes, Object::First, generation, 1);
            close(&mut pipes, Object::First, generation, 2);
            assert!(pipes[0].retire_if_idle([false; 4]));
        }
        assert_eq!(
            code(create(
                &mut pipes,
                Object::First,
                Caller::Parent,
                &factory()
            )),
            -23
        );
        assert_eq!(
            word(
                &reply(create(
                    &mut pipes,
                    Object::Second,
                    Caller::Parent,
                    &factory()
                )),
                4
            ),
            1
        );
    }

    #[test]
    fn eof_epipe_and_pending_are_object_local() {
        let mut pipes = opened();
        close(&mut pipes, Object::First, 1, 2);
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::First, 1, 1, 1, b"x")
            )),
            0
        );
        assert_eq!(
            request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::Second, 1, 1, 1, b"x")
            ),
            Outcome::Pending
        );
        close(&mut pipes, Object::Second, 1, 1);
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Parent,
                &frame(Object::Second, 1, 2, 2, b"x")
            )),
            -32
        );
    }

    #[test]
    fn staged_and_stale_participants_cannot_use_valid_routes() {
        let mut pipes = opened();
        pipes[1].stage_participant(3, 1, [true, true]).unwrap();
        let caller = Caller::Participant {
            slot: 3,
            generation: 1,
        };
        let write = frame(Object::Second, 1, 2, 2, b"z");
        let before = format!("{pipes:?}");
        assert_eq!(code(request(&mut pipes, caller, &write)), -13);
        assert_eq!(format!("{pipes:?}"), before);
        pipes[1].finish_participant_copy(3, 1, true).unwrap();
        assert_eq!(code(request(&mut pipes, caller, &write)), 1);
        pipes[1].confirmed_terminal(caller).unwrap();
        pipes[1].stage_participant(3, 2, [true, true]).unwrap();
        pipes[1].finish_participant_copy(3, 2, true).unwrap();
        let before = format!("{pipes:?}");
        assert_eq!(code(request(&mut pipes, caller, &write)), -13);
        assert_eq!(
            code(request(
                &mut pipes,
                Caller::Participant {
                    slot: 4,
                    generation: 2
                },
                &write
            )),
            -13
        );
        assert_eq!(format!("{pipes:?}"), before);
        let read = frame(Object::Second, 1, 1, 1, b"x");
        assert_eq!(
            reply(request(
                &mut pipes,
                Caller::Participant {
                    slot: 3,
                    generation: 2
                },
                &read
            ))[16],
            b'z'
        );
    }
}
