// SPDX-License-Identifier: BSD-2-Clause
use core::mem::MaybeUninit;
use filesystem_remote_descriptors::NativeIdentity;
use filesystem_service::{Message, message, put};
use fork_gate::{Owner, Phase};
use owner_region::{BYTES, Region};
use std::{cell::Cell, rc::Rc};
struct Stream(Rc<Cell<usize>>);
impl Drop for Stream {
    fn drop(&mut self) {
        self.0.set(self.0.get() + 1);
    }
}
struct Script {
    calls: Rc<Cell<usize>>,
    closes: Rc<Cell<usize>>,
    bad: bool,
}
impl filesystem_service::Channel for Script {
    fn receive(&mut self, out: &mut Message) -> Result<(), i64> {
        self.calls.set(self.calls.get() + 1);
        *out = message(if self.bad { 92 } else { 91 }, 0);
        put(out, 3, 1);
        put(out, 4, 1);
        Ok(())
    }
    fn send(&mut self, _: &Message) -> Result<(), i64> {
        panic!("unexpected source request")
    }
    fn close(&mut self) -> [i64; 2] {
        self.closes.set(self.closes.get() + 1);
        [-7, -9]
    }
}
#[repr(C, align(4096))]
struct Pages([MaybeUninit<u8>; BYTES]);
#[test]
fn mapped_owner_initializes_once_and_keeps_workspace_disjoint() {
    let mut pages = Pages([MaybeUninit::new(0xa5); BYTES]);
    let (slot, workspace, spare) = Region::from_storage(&mut pages.0)
        .unwrap()
        .partition::<Owner<Script, Stream>>()
        .unwrap()
        .into_parts();
    let calls = Rc::new(Cell::new(0));
    let closes = Rc::new(Cell::new(0));
    let drops = Rc::new(Cell::new(0));
    let owner = Owner::connect_in_place(
        slot,
        Script {
            calls: calls.clone(),
            closes: closes.clone(),
            bad: false,
        },
        91,
        Stream(drops.clone()),
    )
    .unwrap();
    assert_eq!(owner.phase(), Phase::Idle);
    assert_eq!(owner.sequence(), 0);
    owner
        .admit(|files, _| {
            let parent = files
                .admitted_shell(NativeIdentity::admitted(1, 1, 0xb0000102).unwrap(), 7)
                .unwrap();
            assert_eq!(files.file_view_v1(parent), Ok((0, 0)));
            files.settled(parent).unwrap();
        })
        .unwrap();
    assert_eq!(calls.get(), 1);
    assert_eq!(closes.get(), 0);
    assert!(workspace.iter().all(|b| *b == 0));
    assert!(spare.iter().all(|b| *b == 0));
    owner.retire();
    assert_eq!(owner.cleanup(), Some([-7, -9]));
    // SAFETY: construction succeeded and all borrows end; drop the sole owner once.
    unsafe { slot.assume_init_drop() };
    assert_eq!(closes.get(), 1);
    assert_eq!(drops.get(), 1);
}
#[test]
fn failed_nested_connect_drops_streams_and_closes_once_without_owner() {
    let mut slot = MaybeUninit::<Owner<Script, Stream>>::uninit();
    let calls = Rc::new(Cell::new(0));
    let closes = Rc::new(Cell::new(0));
    let drops = Rc::new(Cell::new(0));
    let error = Owner::connect_in_place(
        &mut slot,
        Script {
            calls: calls.clone(),
            closes: closes.clone(),
            bad: true,
        },
        91,
        Stream(drops.clone()),
    )
    .err()
    .unwrap();
    assert_eq!(error.cleanup, [-7, -9]);
    assert_eq!(calls.get(), 1);
    assert_eq!(closes.get(), 1);
    assert_eq!(drops.get(), 1);
}
