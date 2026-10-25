// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
use core::mem::MaybeUninit;
use fd_startup::{Binding, Plan, Source};
use filesystem_remote_descriptors::{CopyAttempt, NativeIdentity};
use fixture::{Fault, Harness};
use fork_gate::Owner;
use fork_streams::{SessionPipe, State};
use owner_region::{BASE, BYTES, Error, Placed, Region};
#[repr(C, align(4096))]
struct Pages([MaybeUninit<u8>; BYTES]);
fn entry() -> [u64; 8] {
    [
        30,
        0xa001,
        0xf101,
        0xc002,
        0xd001,
        0xc003,
        BASE as u64,
        BYTES as u64,
    ]
}
#[test]
fn every_entry_scalar_is_checked_and_does_not_grant_authority() {
    assert!(owner_region::validate(entry()).is_ok());
    for i in 0..8 {
        let mut e = entry();
        e[i] ^= 1;
        assert!(matches!(owner_region::validate(e), Err(Error::Binding)));
    }
    let mut old = entry();
    old[0] = 29;
    assert!(matches!(owner_region::validate(old), Err(Error::Binding)));
    let mut selected = entry();
    selected[0] = 31;
    // SESSION excludes native-service-lifetime; the real r9 expression is c003.
    assert!(owner_region::validate_stack(selected).is_ok());
    assert!(owner_region::validate(selected).is_err());
    assert!(owner_region::validate_stack(entry()).is_err());
    for i in 0..8 {
        let mut wrong = selected;
        wrong[i] ^= 1;
        assert!(owner_region::validate_stack(wrong).is_err());
    }
    // Never call native claim on these inert observations in a host process.
}
#[test]
fn rejects_dirty_short_unaligned_and_oversize_without_initializing() {
    let mut bytes = Pages([MaybeUninit::new(0); BYTES]);
    assert!(matches!(
        Region::from_storage(&mut bytes.0[..BYTES - 1]),
        Err(Error::Bytes)
    ));
    #[repr(C, align(4096))]
    struct Dirty([u8; BYTES]);
    let mut extra = Dirty([0; BYTES]);
    extra.0[BYTES - 1] = 1;
    assert!(matches!(
        owner_region::check_zeroed(&extra.0),
        Err(Error::Dirty)
    ));
    #[repr(C, align(4096))]
    struct Offset([MaybeUninit<u8>; BYTES + 1]);
    let mut offset = Offset([MaybeUninit::new(0); BYTES + 1]);
    assert!(matches!(
        Region::from_storage(&mut offset.0[1..]),
        Err(Error::Alignment)
    ));
    let mut large = Pages([MaybeUninit::new(0); BYTES]);
    assert!(matches!(
        Region::from_storage(&mut large.0)
            .unwrap()
            .partition::<[u8; 4097]>(),
        Err(Error::Layout)
    ));
    assert!(matches!(
        Region::from_storage(&mut bytes.0)
            .unwrap()
            .partition::<()>(),
        Err(Error::Layout)
    ));
}
#[test]
fn initialized_owner_workspace_and_tail_are_disjoint_and_exact() {
    let mut bytes = Pages([MaybeUninit::new(0); BYTES]);
    let placed = Region::from_storage(&mut bytes.0)
        .unwrap()
        .partition::<u64>()
        .unwrap()
        .initialize(0x12345678);
    assert_eq!(*placed.owner, 0x12345678);
    assert_eq!(placed.workspace.len(), 4096);
    assert_eq!(placed.spare.len(), BYTES - 4096 - 8);
    placed.workspace.fill(0xa5);
    placed.spare.fill(0x5a);
    assert_eq!(*placed.owner, 0x12345678);
    assert_eq!(
        placed.workspace.as_ptr() as usize,
        placed.owner as *const u64 as usize + 8
    );
    assert_eq!(
        placed.spare.as_ptr() as usize,
        placed.workspace.as_ptr() as usize + 4096
    );
    let mut exact = Pages([MaybeUninit::new(0); BYTES]);
    let exact = Region::from_storage(&mut exact.0)
        .unwrap()
        .partition::<[u8; 4096]>()
        .unwrap()
        .initialize([3; 4096]);
    assert!(exact.spare.is_empty());
    assert_eq!(exact.owner[4095], 3);
    assert_eq!(exact.workspace[0], 0);
    let mut nonzero = Pages([MaybeUninit::new(0); BYTES]);
    let live = Region::from_storage(&mut nonzero.0)
        .unwrap()
        .partition::<core::num::NonZeroU64>()
        .unwrap()
        .initialize(core::num::NonZeroU64::new(7).unwrap());
    assert_eq!(live.owner.get(), 7);
    #[repr(C)]
    struct Padded {
        first: u8,
        second: u64,
    }
    let mut padded = Pages([MaybeUninit::uninit(); BYTES]);
    {
        let p = Region::from_storage(&mut padded.0)
            .unwrap()
            .partition::<Padded>()
            .unwrap()
            .initialize(Padded {
                first: 3,
                second: 5,
            });
        assert_eq!((p.owner.first, p.owner.second), (3, 5));
    }
    // No u8 access to former T padding. Reinitialization writes MaybeUninit.
    let p = Region::from_storage(&mut padded.0)
        .unwrap()
        .partition::<u64>()
        .unwrap()
        .initialize(9);
    assert_eq!(*p.owner, 9);
}
#[test]
fn actual_gate_moves_once_into_region_and_keeps_shared_file_offsets() {
    let mut h = Harness::new(Fault::None, [-9, -5]);
    let mut f = h.fds.take().unwrap();
    let id = |slot: u32| NativeIdentity::admitted(slot, 1, 0xb0000100 | (slot as u64 + 1)).unwrap();
    let parent = f.admitted_shell(id(1), 7).unwrap();
    let fd = f.open_read(parent, b"file", true).unwrap();
    assert_eq!(fd, filesystem_remote_descriptors::FIRST_FILE_FD);
    let streams = State::new([None; 3], [SessionPipe::new(), SessionPipe::new()]).unwrap();
    let mut bytes = Pages([MaybeUninit::new(0); BYTES]);
    let base = bytes.0.as_ptr() as usize;
    let slots = Region::from_storage(&mut bytes.0)
        .unwrap()
        .partition::<Owner<_, State>>()
        .unwrap();
    let (slot, workspace, spare) = slots.into_parts();
    let placed = Placed {
        owner: Owner::initialize(slot, f, streams),
        workspace,
        spare,
    };
    assert_eq!(placed.owner as *const _ as usize, base);
    let p = Plan {
        identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
        shell: 1,
        parent: 7,
        generation: 1,
        bindings: core::array::from_fn(|i| {
            if i == 5 {
                Binding {
                    kind: 3,
                    selector: filesystem_remote_descriptors::FIRST_FILE_FD as u8,
                    cloexec: 1,
                }
            } else {
                Binding::default()
            }
        }),
        sources: [Source::default(); 7],
        history: [0; 2],
    };
    placed.owner.begin(1, |_, _| ()).unwrap();
    placed
        .owner
        .copy(1, parent, id(2), 9, &p, |_| CopyAttempt::Refused(-12))
        .unwrap()
        .unwrap_err();
    placed
        .owner
        .resolve_refusal(1, -12, |_| Ok(-11))
        .unwrap()
        .unwrap();
    placed.owner.refusal_delivered(1, -12).unwrap();
    placed
        .owner
        .admit(|f, _| {
            assert_eq!(f.read(parent, fd, 2, placed.workspace), Ok(2));
            assert_eq!(&placed.workspace[..2], b"ab");
            assert_eq!(f.position(parent, fd), Ok(2));
            f.close(parent, fd).unwrap();
            f.settled(parent).unwrap();
            f.disconnect().unwrap();
        })
        .unwrap();
    assert_eq!(h.storage.lock().unwrap().lookups, 1);
    assert_eq!(h.local.lock().unwrap().closes, 1);
    assert_eq!(h.opcodes(), [1, 2, 3, 4]);
    assert_eq!(placed.owner.cleanup(), Some([-9, -5]));
    // Boot lifetime has no automatic native settlement; the explicit operations above did it.
    drop(h);
}
