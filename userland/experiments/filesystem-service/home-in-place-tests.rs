// SPDX-License-Identifier: BSD-2-Clause
//! Host-only poisoned storage and real service operations; no native fit claim.
use super::*;
use core::mem::MaybeUninit;
use filesystem_fd_protocol::{Connection, FileWriteResult};
use filesystem_remote_descriptors::{HomeAccess, NativeIdentity, ProcessFiles, Seek};

#[derive(Default)]
struct Counts {
    receives: usize,
    sends: usize,
    closes: usize,
    drops: usize,
}
struct Script {
    frames: VecDeque<Result<Message, i64>>,
    counts: Arc<Mutex<Counts>>,
}
impl Channel for Script {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        self.counts.lock().unwrap().receives += 1;
        *out = self.frames.pop_front().unwrap_or(Err(-777))?;
        Ok(())
    }
    fn send(&mut self, _: &Message) -> Result<(), i64> {
        self.counts.lock().unwrap().sends += 1;
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.counts.lock().unwrap().closes += 1;
        [i64::MIN, i64::MAX]
    }
}
impl Drop for Script {
    fn drop(&mut self) {
        self.counts.lock().unwrap().drops += 1;
    }
}
fn greeting(token: u64) -> Message {
    let mut f = message(91, 0);
    put(&mut f, 3, token);
    put(&mut f, 4, 1);
    f
}
fn script(frames: Vec<Result<Message, i64>>) -> (Script, Arc<Mutex<Counts>>) {
    let counts = Arc::new(Mutex::new(Counts::default()));
    (
        Script {
            frames: frames.into(),
            counts: counts.clone(),
        },
        counts,
    )
}
#[repr(C)]
struct Guard<T> {
    before: u64,
    slot: MaybeUninit<T>,
    after: u64,
}
fn poisoned<T>() -> Guard<T> {
    let mut g: Guard<T> = Guard {
        before: 17,
        slot: MaybeUninit::uninit(),
        after: 31,
    };
    // SAFETY: exclusive uninitialized storage only, exactly its typed extent.
    unsafe {
        core::ptr::write_bytes(
            g.slot.as_mut_ptr().cast::<u8>(),
            0xa5,
            core::mem::size_of::<T>(),
        )
    };
    g
}
fn identity(slot: u8) -> NativeIdentity {
    NativeIdentity::admitted(slot.into(), 1, 0xb0000101 + u64::from(slot)).unwrap()
}

#[test]
fn client_two_grants_next_token_and_exact_drop() {
    let mut entry = message(91, 0);
    put(&mut entry, 3, 3);
    put(&mut entry, 4, 2);
    put(&mut entry, 5, 4);
    let (io, counts) = script(vec![Ok(greeting(1)), Ok(greeting(2)), Ok(entry)]);
    let mut g = poisoned();
    let c = Client::connect_home_in_place(&mut g.slot, io, 91).expect("HOME_INIT_TWO_GRANTS");
    assert_eq!(counts.lock().unwrap().receives, 2, "HOME_INIT_TWO_GRANTS");
    assert!(
        c.lookup(c.home().unwrap(), b"data", 6).is_ok(),
        "HOME_INIT_NEXT"
    );
    assert_eq!(c.abort(), [i64::MIN, i64::MAX]);
    assert_eq!((g.before, g.after), (17, 31));
    // SAFETY: successful constructor initialized this whole slot; borrow ended.
    unsafe { g.slot.assume_init_drop() };
    let seen = counts.lock().unwrap();
    assert_eq!((seen.closes, seen.drops), (1, 1), "HOME_INIT_DROP");
}

#[test]
fn both_greeting_failure_stages_preserve_cleanup_and_reuse_slot() {
    for stage in 0..2 {
        for change in 0..14 {
            let mut bad = greeting(stage + 1);
            match change {
                0 => bad[0] ^= 1,
                1 => put(&mut bad, 1, (-5i64) as u64),
                2 => put(&mut bad, 2, 92),
                3 => put(&mut bad, 3, 9),
                4 => put(&mut bad, 4, 2),
                5 => put(&mut bad, 4, 3),
                6 => put(&mut bad, 6, 1),
                7 => put(&mut bad, 7, 1),
                8 => put(&mut bad, 1, 1),
                9 => put(&mut bad, 4, 0),
                10 => put(&mut bad, 3, 0),
                12 => bad = message(91, (-5i64) as u64),
                13 => bad = message(91, (-28i64) as u64),
                _ => (),
            }
            let mut frames = vec![];
            if stage == 1 {
                frames.push(Ok(greeting(1)));
            }
            frames.push(if change == 11 { Err(i64::MIN) } else { Ok(bad) });
            let (io, counts) = script(frames);
            let mut g = poisoned();
            let e = ProcessFiles::connect_home_in_place(&mut g.slot, io, 91)
                .err()
                .expect("HOME_INIT_REJECT");
            assert_eq!(e.cleanup, [i64::MIN, i64::MAX], "HOME_INIT_CLOSES");
            let expected = match change {
                11 => Error::Transport(i64::MIN),
                12 => Error::Remote(-5),
                13 => Error::Remote(-28),
                _ => Error::Protocol,
            };
            assert_eq!(e.error, expected, "HOME_INIT_ORIGINAL_ERROR");
            let s = counts.lock().unwrap();
            assert_eq!(
                (s.receives, s.sends, s.closes, s.drops),
                ((stage + 1) as usize, 0, 1, 1),
                "HOME_INIT_FAILURE_DROP"
            );
            drop(s);
            let (fresh, counts) =
                script(vec![Ok(greeting(1)), Ok(greeting(2)), Ok(message(91, 0))]);
            let f = ProcessFiles::connect_home_in_place(&mut g.slot, fresh, 91)
                .expect("HOME_INIT_REUSE");
            assert_eq!(f.disconnect(), Ok([i64::MIN, i64::MAX]));
            // SAFETY: only this fresh successful construction initialized slot.
            unsafe { g.slot.assume_init_drop() };
            assert_eq!(counts.lock().unwrap().drops, 1, "HOME_INIT_REUSE");
            assert_eq!((g.before, g.after), (17, 31));
        }
    }
}

#[test]
fn zero_epoch_and_old_constructors_never_receive_home_frames() {
    for old in [false, true] {
        let (io, counts) = script(vec![Ok(greeting(1)), Ok(greeting(2))]);
        let mut slot = MaybeUninit::uninit();
        let e = if old {
            ProcessFiles::connect_in_place(&mut slot, io, 91)
        } else {
            ProcessFiles::connect_home_in_place(&mut slot, io, 0)
        }
        .err()
        .unwrap();
        assert_eq!(e.error, Error::Invalid);
        let s = counts.lock().unwrap();
        assert_eq!(
            (s.receives, s.sends, s.closes, s.drops),
            (0, 0, 1, 1),
            "HOME_INIT_NO_RECEIVE"
        );
    }
}

#[test]
fn all_poisoned_views_are_empty_and_real_file_write_receipt_works() {
    let (io, join, state, _, _) = start();
    let mut g = poisoned();
    let f = ProcessFiles::connect_home_in_place(&mut g.slot, io, 91).expect("HOME_INIT_PROCESS");
    let p = f.admitted_shell(identity(1), 7).expect("HOME_INIT_RECORDS");
    for slot in 2..=4 {
        let child = f
            .inherited_child(p, identity(slot), 9)
            .expect("HOME_INIT_RECORDS");
        assert_eq!(f.file_view_v1(child), Ok((0, 0)), "HOME_INIT_RECORDS");
        for fd in 0..16 {
            assert!(f.position(child, fd).is_err(), "HOME_INIT_EMPTY_FDS");
        }
        f.settled(child).unwrap();
    }
    assert_eq!(f.file_view_v1(p), Ok((0, 0)));
    for fd in 0..16 {
        assert!(f.position(p, fd).is_err(), "HOME_INIT_EMPTY_FDS");
    }
    let fd = f
        .open_home_file(p, b"data", HomeAccess::ReadWrite, false)
        .expect("HOME_INIT_HOME_RIGHTS");
    let mut c = Connection::bind(p, 31).unwrap();
    let mut raw = [0; 64];
    raw[..8].copy_from_slice(filesystem_fd_protocol::MAGIC);
    for (i, v) in [11, 31, 1, fd as u64, 4, 0, 0].into_iter().enumerate() {
        put(&mut raw, i + 1, v);
    }
    let mut w = [0; 4096];
    w[..4].copy_from_slice(b"home");
    let r = c.prepare(f, &raw, 64, &mut w).unwrap();
    let copy = r.write_receipt().unwrap();
    r.delivered();
    assert!(
        matches!(copy.result, FileWriteResult::Completed { offset:0, completion } if completion.bytes == 4)
    );
    assert_eq!(f.position(p, fd), Ok(4));
    f.seek(p, fd, Seek::Set(0)).unwrap();
    assert_eq!(f.read(p, fd, 4, &mut w), Ok(4));
    assert_eq!(&w[..4], b"home");
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    // SAFETY: successful fully initialized slot with no live borrows.
    unsafe { g.slot.assume_init_drop() };
    assert_eq!((g.before, g.after), (17, 31));
    assert_eq!(join.join().unwrap().stop, Stop::Disconnected);
    assert_eq!(state.lock().unwrap().writes, 1);
}

#[test]
fn poisoned_in_place_uses_all_thirteen_descriptions_and_sixteen_aliases() {
    let mut frames = vec![Ok(greeting(1)), Ok(greeting(2))];
    for token in 3..=15 {
        let mut f = message(91, 0);
        put(&mut f, 3, token);
        put(&mut f, 4, 2);
        put(&mut f, 5, 4);
        frames.push(Ok(f));
    }
    for _ in 0..14 {
        frames.push(Ok(message(91, 0)));
    }
    let (io, counts) = script(frames);
    let mut g = poisoned();
    let f = ProcessFiles::connect_home_in_place(&mut g.slot, io, 91).unwrap();
    let p = f.admitted_shell(identity(1), 7).unwrap();
    for fd in 0..13 {
        assert_eq!(
            f.open_home_file(p, b"data", HomeAccess::ReadWrite, false),
            Ok(fd),
            "HOME_INIT_ALL_DESCRIPTIONS"
        );
    }
    let before = counts.lock().unwrap().sends;
    assert!(
        f.open_home_file(p, b"data", HomeAccess::ReadWrite, false)
            .is_err(),
        "HOME_INIT_CAPACITY"
    );
    assert_eq!(counts.lock().unwrap().sends, before, "HOME_INIT_CAPACITY");
    for fd in 13..16 {
        assert_eq!(
            f.duplicate(p, 0, fd, false),
            Ok(fd),
            "HOME_INIT_ALL_ALIASES"
        );
    }
    assert!(f.duplicate(p, 0, 0, false).is_err(), "HOME_INIT_CAPACITY");
    f.settled(p).unwrap();
    f.disconnect().unwrap();
    // SAFETY: one successful fully initialized slot, now settled and disconnected.
    unsafe { g.slot.assume_init_drop() };
    let seen = counts.lock().unwrap();
    assert_eq!(
        (seen.receives, seen.closes, seen.drops),
        (29, 1, 1),
        "HOME_INIT_ALL_DESCRIPTIONS"
    );
    assert_eq!((g.before, g.after), (17, 31));
}
