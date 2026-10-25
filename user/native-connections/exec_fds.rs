// SPDX-License-Identifier: BSD-2-Clause
// Pure preparation of the existing bounded descriptor snapshot, not authority.
#[derive(Debug, PartialEq, Eq)]
pub struct Plan<const BINDINGS: usize = 3> {
    pub table: [u8; 64],
    pub users: [u8; BINDINGS],
    // Drop this process's holder only; other processes may retain the backend.
    pub release: [bool; BINDINGS],
}

#[derive(Debug, PartialEq, Eq)]
pub enum Invalid {
    Record,
    Counts,
}

pub fn prepare(table: &[u8; 64], users: &[u8; 3]) -> Result<Plan, Invalid> {
    prepare_bindings(table, users)
}

/// Five local bindings: stdin/stdout/stderr plus one pipe reader and writer.
/// A plan describes alias removal only; it grants no endpoint or exec authority.
pub fn prepare_pipe(table: &[u8; 64], users: &[u8; 5]) -> Result<Plan<5>, Invalid> {
    prepare_bindings(table, users)
}

/// Three standard streams and two pipe endpoint pairs. This prepares alias
/// filtering only; live object generations and holder authority remain separate.
pub fn prepare_pipeline(table: &[u8; 64], users: &[u8; 7]) -> Result<Plan<7>, Invalid> {
    prepare_bindings(table, users)
}

/// Four local bindings: standard streams and one separately authorized null object.
/// Validation grants no authority; the caller must check live owner-held counts.
/// Like the other plans, release applies only to the replacing process's holder.
pub fn prepare_null(table: &[u8; 64], users: &[u8; 4]) -> Result<Plan<4>, Invalid> {
    prepare_bindings(table, users)
}

/// Three streams and two separately authorized scratch open descriptions.
/// Counts must come from the frozen local table and be checked against live
/// owner-held bindings by the caller. Preparation neither inherits nor closes.
pub fn prepare_files(table: &[u8; 64], users: &[u8; 5]) -> Result<Plan<5>, Invalid> {
    prepare_bindings(table, users)
}

pub fn prepare_bindings<const BINDINGS: usize>(
    table: &[u8; 64],
    users: &[u8; BINDINGS],
) -> Result<Plan<BINDINGS>, Invalid> {
    let mut original = [0u8; BINDINGS];
    let mut plan = Plan {
        table: [0; 64],
        users: [0; BINDINGS],
        release: [false; BINDINGS],
    };
    for (index, record) in table.chunks_exact(4).enumerate() {
        let [binding, flags, present, reserved] = <[u8; 4]>::try_from(record).unwrap();
        if present == 0 {
            if record != [0; 4] {
                return Err(Invalid::Record);
            }
            continue;
        }
        if present != 1 || reserved != 0 || binding as usize >= BINDINGS || flags > 1 {
            return Err(Invalid::Record);
        }
        let binding = binding as usize;
        original[binding] += 1;
        if flags == 0 {
            plan.table[index * 4..index * 4 + 4].copy_from_slice(record);
            plan.users[binding] += 1;
        }
    }
    if original != *users {
        return Err(Invalid::Counts);
    }
    for binding in 0..BINDINGS {
        plan.release[binding] = original[binding] != 0 && plan.users[binding] == 0;
    }
    Ok(plan)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn files_keep_independent_bindings_and_reject_forged_snapshots() {
        let mut table = [0; 64];
        table[36..40].copy_from_slice(&[3, 0, 1, 0]);
        table[40..44].copy_from_slice(&[3, 1, 1, 0]);
        table[60..64].copy_from_slice(&[4, 1, 1, 0]);
        let before = table;
        let plan = prepare_files(&table, &[0, 0, 0, 2, 1]).unwrap();
        assert_eq!(plan.users, [0, 0, 0, 1, 0]);
        assert_eq!(plan.release, [false, false, false, false, true]);
        let mut expected = [0; 64];
        expected[36..40].copy_from_slice(&[3, 0, 1, 0]);
        assert_eq!(plan.table, expected);
        assert_eq!(table, before);
        for counts in [[0; 5], [0, 0, 0, 1, 2], [0, 0, 0, 2, 0]] {
            assert_eq!(prepare_files(&table, &counts), Err(Invalid::Counts));
        }
        for bad in [
            [5, 0, 1, 0],
            [4, 2, 1, 0],
            [3, 0, 1, 1],
            [4, 0, 0, 0],
            [3, 0, 2, 0],
        ] {
            for fd in 0..16 {
                let mut invalid = [0; 64];
                invalid[fd * 4..fd * 4 + 4].copy_from_slice(&bad);
                let original = invalid;
                assert_eq!(prepare_files(&invalid, &[0; 5]), Err(Invalid::Record));
                assert_eq!(invalid, original);
            }
        }
    }

    #[test]
    fn file_aliases_cover_all_positions_flags_and_capacity() {
        assert_eq!(
            prepare_files(&[0; 64], &[0; 5]).unwrap().release,
            [false; 5]
        );
        for binding in [3, 4] {
            for first in 0..16 {
                for second in 0..16 {
                    if first == second {
                        continue;
                    }
                    for flags in 0..4 {
                        let mut table = [0; 64];
                        table[first * 4..first * 4 + 4].copy_from_slice(&[
                            binding,
                            flags & 1,
                            1,
                            0,
                        ]);
                        table[second * 4..second * 4 + 4].copy_from_slice(&[
                            binding,
                            flags >> 1,
                            1,
                            0,
                        ]);
                        let original = table;
                        let mut users = [0; 5];
                        users[binding as usize] = 2;
                        let plan = prepare_files(&table, &users).unwrap();
                        let survivors = 2 - (flags & 1) - (flags >> 1);
                        assert_eq!(plan.users[binding as usize], survivors);
                        assert_eq!(plan.release[binding as usize], survivors == 0);
                        for fd in 0..16 {
                            let record = &original[fd * 4..fd * 4 + 4];
                            assert_eq!(
                                &plan.table[fd * 4..fd * 4 + 4],
                                if record[1] == 1 { &[0; 4] } else { record }
                            );
                        }
                        assert_eq!(table, original);
                        assert_eq!(prepare(&table, &[0; 3]), Err(Invalid::Record));
                    }
                }
            }
            for flags in 0..2 {
                let mut table = [0; 64];
                for record in table.chunks_exact_mut(4) {
                    record.copy_from_slice(&[binding, flags, 1, 0]);
                }
                let mut users = [0; 5];
                users[binding as usize] = 16;
                let plan = prepare_files(&table, &users).unwrap();
                assert_eq!(
                    plan.users[binding as usize],
                    if flags == 0 { 16 } else { 0 }
                );
                assert_eq!(plan.release[binding as usize], flags == 1);
                assert_eq!(plan.table, if flags == 0 { table } else { [0; 64] });
            }
        }
    }

    #[test]
    fn null_aliases_preserve_exact_survivors_at_every_descriptor_pair() {
        for first in 0..16 {
            for second in 0..16 {
                if first == second {
                    continue;
                }
                for flags in 0..4 {
                    let mut table = [0; 64];
                    table[first * 4..first * 4 + 4].copy_from_slice(&[3, flags & 1, 1, 0]);
                    table[second * 4..second * 4 + 4].copy_from_slice(&[3, flags >> 1, 1, 0]);
                    let original = table;
                    let mut expected = table;
                    if flags & 1 != 0 {
                        expected[first * 4..first * 4 + 4].fill(0);
                    }
                    if flags & 2 != 0 {
                        expected[second * 4..second * 4 + 4].fill(0);
                    }
                    let users = [0, 0, 0, 2];
                    let plan = prepare_null(&table, &users).unwrap();
                    assert_eq!(plan.table, expected);
                    assert_eq!(plan.users, [0, 0, 0, 2 - (flags & 1) - (flags >> 1)]);
                    assert_eq!(plan.release, [false, false, false, flags == 3]);
                    assert_eq!(table, original);
                    assert_eq!(users, [0, 0, 0, 2]);
                    assert_eq!(prepare(&table, &[0; 3]), Err(Invalid::Record));
                }
            }
        }
    }

    #[test]
    fn background_exec_releases_only_child_original_input_and_keeps_null() {
        // FD0 now names null; FD10 still aliases the copied original input.
        let mut table = [0; 64];
        table[..12].copy_from_slice(&[3, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0]);
        table[40..44].copy_from_slice(&[0, 1, 1, 0]);
        let original = table;
        let users = [1, 1, 1, 1];
        let plan = prepare_null(&table, &users).unwrap();
        let mut expected = table;
        expected[40..44].fill(0);
        assert_eq!(plan.table, expected);
        assert_eq!(plan.users, [0, 1, 1, 1]);
        assert_eq!(plan.release, [true, false, false, false]);
        // Discarding the plan after denied admission leaves live inputs unchanged.
        drop(plan);
        assert_eq!(table, original);
        assert_eq!(users, [1, 1, 1, 1]);
    }

    #[test]
    fn null_preparation_rejects_invalid_records_and_invented_counts() {
        for bad in [
            [4, 0, 1, 0],
            [3, 2, 1, 0],
            [3, 0, 1, 1],
            [3, 0, 0, 0],
            [3, 0, 2, 0],
        ] {
            for fd in 0..16 {
                let mut table = [0; 64];
                table[fd * 4..fd * 4 + 4].copy_from_slice(&bad);
                let original = table;
                assert_eq!(prepare_null(&table, &[0; 4]), Err(Invalid::Record));
                assert_eq!(table, original);
            }
        }
        let mut table = [0; 64];
        table[..4].copy_from_slice(&[3, 0, 1, 0]);
        for users in [[0; 4], [0, 0, 0, 2], [1, 0, 0, 1]] {
            assert_eq!(prepare_null(&table, &users), Err(Invalid::Counts));
        }
        assert_eq!(prepare_null(&[0; 64], &[0, 0, 0, 1]), Err(Invalid::Counts));
    }

    #[test]
    fn null_last_alias_release_and_full_table_are_bounded() {
        assert_eq!(prepare_null(&[0; 64], &[0; 4]).unwrap().release, [false; 4]);
        for fd in 0..16 {
            let mut table = [0; 64];
            table[fd * 4..fd * 4 + 4].copy_from_slice(&[3, 1, 1, 0]);
            let plan = prepare_null(&table, &[0, 0, 0, 1]).unwrap();
            assert_eq!(plan.table, [0; 64]);
            assert_eq!(plan.users, [0; 4]);
            assert_eq!(plan.release, [false, false, false, true]);
        }
        for flags in 0..2 {
            let mut table = [0; 64];
            for record in table.chunks_exact_mut(4) {
                record.copy_from_slice(&[3, flags, 1, 0]);
            }
            let plan = prepare_null(&table, &[0, 0, 0, 16]).unwrap();
            assert_eq!(plan.users, [0, 0, 0, if flags == 0 { 16 } else { 0 }]);
            assert_eq!(plan.release, [false, false, false, flags == 1]);
            assert_eq!(plan.table, if flags == 0 { table } else { [0; 64] });
        }
    }

    #[test]
    fn pipe_alias_flags_at_every_pair_of_descriptors() {
        for binding in [3, 4] {
            for first in 0..16 {
                for second in 0..16 {
                    if first == second {
                        continue;
                    }
                    for flags in 0..4 {
                        let mut table = [0; 64];
                        table[first * 4..first * 4 + 4].copy_from_slice(&[
                            binding,
                            flags & 1,
                            1,
                            0,
                        ]);
                        table[second * 4..second * 4 + 4].copy_from_slice(&[
                            binding,
                            flags >> 1,
                            1,
                            0,
                        ]);
                        let original = table;
                        let mut users = [0; 5];
                        users[binding as usize] = 2;
                        let plan = prepare_pipe(&table, &users).unwrap();
                        let survivors = 2 - (flags & 1) - (flags >> 1);
                        assert_eq!(plan.users[binding as usize], survivors);
                        assert_eq!(plan.release[binding as usize], survivors == 0);
                        for fd in 0..16 {
                            let record = &original[fd * 4..fd * 4 + 4];
                            assert_eq!(
                                &plan.table[fd * 4..fd * 4 + 4],
                                if record[1] == 1 { &[0; 4] } else { record }
                            );
                        }
                        assert_eq!(table, original);
                        assert_eq!(users[binding as usize], 2);
                        // This same table must remain invalid in the old profile.
                        assert_eq!(prepare(&table, &[0; 3]), Err(Invalid::Record));
                    }
                }
            }
        }
    }

    #[test]
    fn pipe_preparation_rejects_noncanonical_records_and_counts() {
        for bad in [[5, 0, 1, 0], [4, 2, 1, 0], [3, 0, 1, 1], [4, 0, 0, 0]] {
            for fd in 0..16 {
                let mut table = [0; 64];
                table[fd * 4..fd * 4 + 4].copy_from_slice(&bad);
                let before = table;
                assert_eq!(prepare_pipe(&table, &[0; 5]), Err(Invalid::Record));
                assert_eq!(table, before);
            }
        }
        let mut table = [0; 64];
        table[12..16].copy_from_slice(&[3, 0, 1, 0]);
        for users in [[0; 5], [0, 0, 0, 2, 0], [0, 0, 0, 1, 1]] {
            assert_eq!(prepare_pipe(&table, &users), Err(Invalid::Counts));
        }
    }

    #[test]
    fn shared_alias_survives_without_backend_release() {
        let mut table = [0; 64];
        table[..12].copy_from_slice(&[0, 0, 1, 0, 1, 1, 1, 0, 2, 0, 1, 0]);
        table[40..44].copy_from_slice(&[0, 1, 1, 0]);
        let original = table;
        let plan = prepare(&table, &[2, 1, 1]).unwrap();
        let mut expected = [0; 64];
        expected[..4].copy_from_slice(&[0, 0, 1, 0]);
        expected[8..12].copy_from_slice(&[2, 0, 1, 0]);
        assert_eq!(plan.table, expected);
        assert_eq!(plan.users, [1, 0, 1]);
        assert_eq!(plan.release, [false, true, false]);
        assert_eq!(table, original); // Rejected admission can discard the plan.
    }

    #[test]
    fn each_descriptor_can_be_the_last_local_alias() {
        for fd in 0..16 {
            let mut table = [0; 64];
            table[fd * 4..fd * 4 + 4].copy_from_slice(&[2, 1, 1, 0]);
            let plan = prepare(&table, &[0, 0, 1]).unwrap();
            assert_eq!(plan.table, [0; 64]);
            assert_eq!(plan.users, [0; 3]);
            assert_eq!(plan.release, [false, false, true]);
        }
    }

    #[test]
    fn empty_full_and_multiple_closed_aliases() {
        assert_eq!(prepare(&[0; 64], &[0; 3]).unwrap().release, [false; 3]);
        let mut table = [0; 64];
        for record in table.chunks_exact_mut(4) {
            record.copy_from_slice(&[1, 0, 1, 0]);
        }
        let plan = prepare(&table, &[0, 16, 0]).unwrap();
        assert_eq!(plan.table, table);
        assert_eq!(plan.users, [0, 16, 0]);
        assert_eq!(plan.release, [false; 3]);
        for record in table.chunks_exact_mut(4) {
            record[1] = 1;
        }
        let plan = prepare(&table, &[0, 16, 0]).unwrap();
        assert_eq!(plan.users, [0; 3]);
        assert_eq!(plan.release, [false, true, false]);
    }

    #[test]
    fn malformed_records_reject_without_changing_input() {
        for bad in [
            [0, 0, 2, 0],
            [0, 2, 1, 0],
            [3, 0, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
        ] {
            for fd in 0..16 {
                let mut table = [0; 64];
                table[fd * 4..fd * 4 + 4].copy_from_slice(&bad);
                let original = table;
                assert_eq!(prepare(&table, &[0; 3]), Err(Invalid::Record));
                assert_eq!(table, original);
            }
        }
    }

    #[test]
    fn count_mismatch_never_produces_a_candidate() {
        let mut table = [0; 64];
        table[..4].copy_from_slice(&[0, 1, 1, 0]);
        for users in [[0, 0, 0], [2, 0, 0], [1, 1, 0], [255, 0, 0]] {
            assert_eq!(prepare(&table, &users), Err(Invalid::Counts));
        }
    }
}
