// SPDX-License-Identifier: BSD-2-Clause
//! The checker supplies the current native producer settlement block unchanged.
use super::*;
fn final_zero() -> HomeResult {
    HomeResult {
        flags: ENTRY | CALLBACK | ACCEPTED | CLOSE_ATTEMPTED | ORDERED | ACTIVATION,
        service: ServiceResult {
            ready: 1,
            requests: 20,
            ..ServiceResult::default()
        },
        ..HomeResult::initial()
    }
}
#[test]
fn producer_discharges_only_complete_healthy_zero_after_settlement() {
    let mut good = final_zero();
    assert!(!good.valid());
    settle(&mut good, true);
    assert!(good.valid() && !good.requires_ordering());
    assert_eq!(
        good.flags,
        ENTRY | CALLBACK | ACCEPTED | CLOSE_ATTEMPTED | ACTIVATION
    );
    for case in 0..8 {
        let mut bad = final_zero();
        match case {
            0 => bad.service.reader_close = -5,
            1 => bad.service.writer_close = -5,
            2 => bad.service.stop = 6,
            3 => bad.service.ready = 0,
            4 => bad.service.requests = 0,
            5 => bad.service.state = 3,
            6 => bad.mutation_attempts = 1,
            _ => bad.create.provider = 2,
        }
        let before = bad;
        settle(&mut bad, true);
        assert_eq!(bad, before, "PRODUCER_ORDER_CONSERVATIVE:{case}");
        assert!(bad.requires_ordering());
    }
    let mut unfinished = final_zero();
    let before = unfinished;
    settle(&mut unfinished, false);
    assert_eq!(unfinished, before);
}
