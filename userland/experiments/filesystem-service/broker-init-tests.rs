// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_service::{message, put, Message};
use std::{cell::RefCell, collections::VecDeque, rc::Rc, vec::Vec};

#[derive(Default)]
struct Seen {
    receives: usize,
    sends: usize,
    closes: usize,
    drops: usize,
}
struct Script {
    frames: VecDeque<core::result::Result<Message, i64>>,
    seen: Rc<RefCell<Seen>>,
    cleanup: [i64; 2],
}
impl Channel for Script {
    fn receive(&mut self, out: &mut Message) -> core::result::Result<(), i64> {
        self.seen.borrow_mut().receives += 1;
        *out = self.frames.pop_front().unwrap_or(Err(-32))?;
        Ok(())
    }
    fn send(&mut self, _: &Message) -> core::result::Result<(), i64> {
        self.seen.borrow_mut().sends += 1;
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.seen.borrow_mut().closes += 1;
        self.cleanup
    }
}
impl Drop for Script {
    fn drop(&mut self) {
        self.seen.borrow_mut().drops += 1;
    }
}
fn greeting() -> Message {
    let mut frame = message(91, 0);
    put(&mut frame, 3, 1);
    put(&mut frame, 4, 1);
    frame
}
fn script(frames: Vec<core::result::Result<Message, i64>>) -> (Script, Rc<RefCell<Seen>>) {
    let seen = Rc::new(RefCell::new(Seen::default()));
    (
        Script {
            frames: frames.into(),
            seen: seen.clone(),
            cleanup: [-7, -9],
        },
        seen,
    )
}
#[test]
fn nonzero_backing_has_one_initialized_ledger_and_one_greeting() {
    #[repr(C)]
    struct Guard {
        before: u64,
        slot: core::mem::MaybeUninit<ProcessFiles<Script>>,
        after: u64,
    }
    let mut guard = Guard {
        before: 17,
        slot: core::mem::MaybeUninit::uninit(),
        after: 31,
    };
    // SAFETY: only bytes in the exclusive uninitialized slot are poisoned.
    unsafe {
        core::ptr::write_bytes(
            guard.slot.as_mut_ptr().cast::<u8>(),
            0xa5,
            core::mem::size_of::<ProcessFiles<Script>>(),
        )
    };
    let (channel, seen) = script(std::vec![Ok(greeting())]);
    let files = ProcessFiles::connect_in_place(&mut guard.slot, channel, 91).unwrap();
    assert_eq!(files.epoch, 91);
    for record in &files.records {
        assert_eq!(record.last_generation, 0);
        assert!(record.process.is_none());
        #[cfg(fs_cwd)]
        assert!(record.cwd.is_none());
    }
    let parent = files
        .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
        .unwrap();
    assert_eq!(files.file_view_v1(parent), Ok((0, 0)));
    for slot in 2..=4 {
        let child = files
            .inherited_child(
                parent,
                NativeIdentity::admitted(slot, 1, 0xb0000100 | (slot as u64 + 1)).unwrap(),
                9,
            )
            .unwrap();
        assert_eq!(files.file_view_v1(child), Ok((0, 0)));
        files.settled(child).unwrap();
    }
    files.settled(parent).unwrap();
    assert_eq!(seen.borrow().receives, 1);
    assert_eq!(seen.borrow().sends, 0);
    files.abort();
    assert_eq!(files.cleanup(), Some([-7, -9]));
    assert_eq!(guard.before, 17);
    assert_eq!(guard.after, 31);
    // SAFETY: successful construction initialized the entire slot; no live
    // reference is used after this point. Dropping performs no second close.
    unsafe { guard.slot.assume_init_drop() };
    assert_eq!(seen.borrow().closes, 1);
    assert_eq!(seen.borrow().drops, 1);
}
#[test]
fn nested_greeting_failures_close_and_drop_once_without_replay() {
    let mut malformed = greeting();
    malformed[0] ^= 1;
    let mut epoch = greeting();
    put(&mut epoch, 2, 92);
    let mut file = greeting();
    put(&mut file, 4, 2);
    for frame in [Err(-32), Ok(malformed), Ok(epoch), Ok(file)] {
        let (channel, seen) = script(std::vec![frame]);
        let failure = {
            let mut slot = core::mem::MaybeUninit::uninit();
            ProcessFiles::connect_in_place(&mut slot, channel, 91)
                .err()
                .unwrap()
        };
        assert_eq!(failure.cleanup, [-7, -9]);
        assert_eq!(seen.borrow().receives, 1);
        assert_eq!(seen.borrow().sends, 0);
        assert_eq!(seen.borrow().closes, 1);
        assert_eq!(seen.borrow().drops, 1);
    }
}
#[test]
fn invalid_epoch_rejects_before_greeting_and_preserves_cleanup() {
    let (channel, seen) = script(std::vec![Ok(greeting())]);
    let mut slot = core::mem::MaybeUninit::uninit();
    let failure = ProcessFiles::connect_in_place(&mut slot, channel, 0)
        .err()
        .unwrap();
    assert_eq!(failure.error, filesystem_client::Error::Invalid);
    assert_eq!(failure.cleanup, [-7, -9]);
    assert_eq!(seen.borrow().receives, 0);
    assert_eq!(seen.borrow().closes, 1);
    assert_eq!(seen.borrow().drops, 1);
}
#[test]
fn successful_disconnect_then_drop_has_no_duplicate_close() {
    let (channel, seen) = script(std::vec![Ok(greeting()), Ok(message(91, 0))]);
    let mut slot = core::mem::MaybeUninit::uninit();
    let files = ProcessFiles::connect_in_place(&mut slot, channel, 91).unwrap();
    assert_eq!(files.disconnect(), Ok([-7, -9]));
    assert_eq!(seen.borrow().receives, 2);
    assert_eq!(seen.borrow().sends, 1);
    // SAFETY: successful initialized owner; the returned borrow ends here.
    unsafe { slot.assume_init_drop() };
    assert_eq!(seen.borrow().closes, 1);
    assert_eq!(seen.borrow().drops, 1);
}
