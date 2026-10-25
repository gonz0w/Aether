// SPDX-License-Identifier: BSD-2-Clause
use std::sync::Mutex;
static MODEL: Mutex<Model> = Mutex::new(Model {
    mode: 0,
    calls: 0,
    offset: 0,
    yields: 0,
});
struct Model {
    mode: u8,
    calls: usize,
    offset: usize,
    yields: usize,
}
unsafe fn trap(op: u64, cap: u64, pointer: u64, count: u64, extra: u64) -> (i64, u64) {
    let mut model = MODEL.lock().unwrap();
    assert_eq!(extra, 0);
    if op == 0x1fffe {
        model.yields += 1;
        return (0, 0);
    }
    assert_eq!(cap, 71);
    assert!(op == 0x24001 || op == 0x24002);
    assert_eq!(count as usize, (64 - model.offset).min(16), "FRAME_BOUNDS");
    model.calls += 1;
    if model.mode == 4 || (model.mode == 0 && model.calls % 3 == 1) {
        return (-11, 0);
    }
    if model.offset == 3 && model.mode != 0 {
        return (
            match model.mode {
                1 => 0,
                2 => -13,
                3 => 17,
                _ => unreachable!(),
            },
            0,
        );
    }
    let length = (count as usize).min(3);
    // SAFETY: production frame loop supplies a live initialized exclusive slice
    // of at least `count` bytes throughout this synchronous model call.
    let bytes = unsafe { std::slice::from_raw_parts_mut(pointer as *mut u8, length) };
    for (i, byte) in bytes.iter_mut().enumerate() {
        let expected = (model.offset + i + 1) as u8;
        if op == 0x24001 {
            *byte = expected;
        } else {
            assert_eq!(*byte, expected, "FRAME_ORDER");
        }
    }
    model.offset += length;
    (length as i64, 0)
}
fn reset(mode: u8) {
    *MODEL.lock().unwrap() = Model {
        mode,
        calls: 0,
        offset: 0,
        yields: 0,
    };
}
#[test]
fn short_transfers_and_backpressure_preserve_order_in_both_directions() {
    for writing in [false, true] {
        reset(0);
        let mut bytes = [0; 64];
        if writing {
            for (i, b) in bytes.iter_mut().enumerate() {
                *b = (i + 1) as u8;
            }
        }
        assert_eq!(frame(71, &mut bytes, writing), Ok(()));
        for (i, b) in bytes.iter().enumerate() {
            assert_eq!(*b, (i + 1) as u8, "FRAME_ORDER");
        }
        let model = MODEL.lock().unwrap();
        assert_eq!(model.offset, 64);
        assert!(model.yields > 1);
    }
}
#[test]
fn terminal_or_invalid_completion_erases_partial_frame() {
    for mode in 1..=3 {
        reset(mode);
        let mut bytes = [0xa5; 64];
        assert!(frame(71, &mut bytes, false).is_err(), "FRAME_TERMINAL");
        assert_eq!(bytes, [0; 64], "FRAME_CLEAR");
        assert_eq!(MODEL.lock().unwrap().offset, 3);
    }
}
#[test]
fn stalled_peer_has_a_finite_budget_and_no_partial_publication() {
    reset(4);
    let mut bytes = [0xa5; 64];
    assert_eq!(frame(71, &mut bytes, false), Err(-110));
    assert_eq!(bytes, [0; 64]);
    let model = MODEL.lock().unwrap();
    assert_eq!((model.calls, model.yields), (100_000, 100_000));
}
