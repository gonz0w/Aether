// SPDX-License-Identifier: BSD-2-Clause
use std::{cell::RefCell, collections::VecDeque};
thread_local! {
    static FRAMES: RefCell<VecDeque<[u8;64]>> = const { RefCell::new(VecDeque::new()) };
    static CALLS: RefCell<usize> = const { RefCell::new(0) };
    static FAULT: RefCell<usize> = const { RefCell::new(0) };
}
fn check(ok: bool) {
    assert!(ok, "metadata decoder oracle");
}
fn get(bytes: &[u8; 64], index: usize) -> u64 {
    u64::from_le_bytes(bytes[index * 8..index * 8 + 8].try_into().unwrap())
}
mod channel {
    pub fn frame(_: u64, bytes: &mut [u8; 64], writing: bool) -> Result<(), i32> {
        assert!(!writing);
        let count = super::CALLS.with(|v| {
            *v.borrow_mut() += 1;
            *v.borrow()
        });
        if super::FAULT.with(|v| *v.borrow() == count) {
            return Err(-5);
        }
        *bytes = super::FRAMES
            .with(|v| v.borrow_mut().pop_front())
            .expect("fixture frame");
        Ok(())
    }
}
struct Connection {
    receive: u64,
}
// The Python test inserts the actual maintained decoder into this impl.

fn invoke(header: &[u8; 64], bytes: &[u8; 128], selected: u8, fault: usize) -> bool {
    FRAMES.with(|v| *v.borrow_mut() = bytes.as_chunks::<64>().0.iter().copied().collect());
    CALLS.with(|v| *v.borrow_mut() = 0);
    FAULT.with(|v| *v.borrow_mut() = fault);
    let result =
        std::panic::catch_unwind(|| Connection { receive: 7 }.metadata_body(header, selected));
    assert!(CALLS.with(|v| *v.borrow() <= 2));
    result.is_ok()
}
#[test]
fn actual_frame_decoder_and_corruptions() {
    std::panic::set_hook(Box::new(|info| {
        if info.to_string().contains("metadata corruption accepted")
            || info.to_string().contains("metadata positive rejected")
        {
            eprintln!("{info}");
        }
    }));
    let mut header = [0u8; 64];
    header[40..48].copy_from_slice(&112u64.to_le_bytes());
    for selected in 0..4 {
        let (size, mode, links, uid) = match selected {
            0 => (0, 0o100600, 1, 1000),
            1 => (4096, 0o100600, 1, 1000),
            2 => (780248, 0o100755, 1, 0),
            _ => (5, 0o040755, 4, 0),
        };
        let mut values: [u64; 14] = [
            size,
            mode,
            links,
            uid,
            uid,
            0x840800000014,
            1791290040,
            1,
            1791290040,
            2,
            1791290040,
            3,
            1791290040,
            1,
        ];
        if selected == 2 {
            values[5] = 0x840800000104;
            for (i, s) in [
                (6, 1621447692),
                (8, 1620802862),
                (10, 1620802862),
                (12, 1620802862),
            ] {
                values[i] = s;
            }
        } else if selected == 3 {
            values[5] = 0x840800000144;
            values[6] = 1621447687;
            values[12] = 1620802853;
        }
        let mut bytes = [0u8; 128];
        for (i, v) in values.iter().enumerate() {
            bytes[i * 8..i * 8 + 8].copy_from_slice(&v.to_le_bytes());
        }
        assert!(
            invoke(&header, &bytes, selected, 0),
            "metadata positive rejected"
        );
        for field in 0..14 {
            let mut wrong = bytes;
            let value = values[field]
                ^ if field == 5 {
                    0x0000000800000000
                } else {
                    1u64 << 63
                };
            wrong[field * 8..field * 8 + 8].copy_from_slice(&value.to_le_bytes());
            assert!(
                !invoke(&header, &wrong, selected, 0),
                "metadata corruption accepted field={field}"
            );
        }
        for index in 112..128 {
            let mut wrong = bytes;
            wrong[index] = 1;
            assert!(
                !invoke(&header, &wrong, selected, 0),
                "metadata corruption accepted padding={index}"
            );
        }
        for field in [3, 4, 5, 6, 7] {
            let mut wrong = header;
            wrong[field * 8] ^= 1;
            assert!(
                !invoke(&wrong, &bytes, selected, 0),
                "metadata corruption accepted header={field}"
            );
            assert_eq!(CALLS.with(|v| *v.borrow()), 0);
        }
        for fault in 1..=2 {
            assert!(
                !invoke(&header, &bytes, selected, fault),
                "metadata corruption accepted fault={fault}"
            );
            assert_eq!(CALLS.with(|v| *v.borrow()), fault);
        }
    }
}
