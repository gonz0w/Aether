// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Trusted owner-side mechanisms. Labels never confer native authority.
use af07_transport::Kernel;
pub type Status = (i64, u64, u64);
/// Delivered-interrupt ticks only; zero must never disable an armed deadline.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Deadline(core::num::NonZeroU64);
impl Deadline {
    pub fn after(tick: u64, allowance: u64) -> Result<Self, i64> {
        if allowance == 0 {
            return Err(-22);
        }
        tick.checked_add(allowance)
            .and_then(core::num::NonZeroU64::new)
            .map(Self)
            .ok_or(-22)
    }
    pub fn get(self) -> u64 {
        self.0.get()
    }
    /// Error auxiliary registers are never interpreted as an observation.
    pub fn check(self, raw: Status) -> Result<u64, i64> {
        let seen = Observation::checked(raw)?;
        if seen.tick >= self.get() {
            Err(-110)
        } else {
            Ok(seen.sequence)
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Observation {
    pub sequence: u64,
    pub tick: u64,
}
impl Observation {
    pub fn checked(raw: Status) -> Result<Self, i64> {
        if raw.0 != 0 {
            return Err(if raw.0 < 0 { raw.0 } else { -5 });
        }
        if raw.1 == u64::MAX {
            return Err(-28);
        }
        Ok(Self {
            sequence: raw.1,
            tick: raw.2,
        })
    }
}
pub trait Control: Kernel + Clone {
    fn observe_events(&mut self) -> Status {
        self.ctl(0x2a000, 0xe002, 0)
    }
    fn park_events(&mut self, sequence: u64, deadline: Option<Deadline>) -> Status;
    /// Selected holder-only, nonblocking physical transmitter observation.
    fn transmitter_empty(&mut self) -> i64 {
        self.ctl(0x26004, 0xf001, 0).0
    }

    fn ctl(&mut self, op: u64, handle: u64, argument: u64) -> Status;
    fn engine(&mut self, reader: u64, writer: u64) -> i64;
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64;
    fn launch(&mut self, arguments: &[u8; 272], reader: u64, writer: u64) -> i64;
    fn copy(&mut self, parent: u64, slot: u32, token: u64, reader: u64, writer: u64) -> i64;
    fn serial(&mut self, writing: bool, bytes: &mut [u8]) -> i64;
    fn exec(&mut self, process: u64, token: u64, arguments: &[u8; 272]) -> i64;
    fn receipt(&mut self, process: u64) -> Status;
    fn publish(&mut self, process: u64, token: u64) -> i64;
}
/// Additive selected one-app seam; existing Control implementors are unchanged.
pub trait AppControl: Control {
    fn launch_app(&mut self, record: &[u8; 320], reader: u64, writer: u64) -> i64;
}
#[cfg(all(owner_control_host_trap, any(target_os = "none", not(test))))]
compile_error!("owner control host trap requires host tests and forbids native target");
#[cfg(any(target_os = "none", all(owner_control_host_trap, test)))]
#[path = "native_owner_control.rs"]
mod native;

#[cfg(test)]
extern crate std;
#[cfg(all(owner_control_host_trap, test, not(target_os = "none")))]
mod host_trap {
    use super::*;
    use std::cell::RefCell;
    std::thread_local! { static LAST: RefCell<Option<(u64,[u64;6])>> = const {RefCell::new(None)}; }
    #[derive(Clone)]
    pub struct Native;
    impl Kernel for Native {
        fn transfer(&mut self, _: u64, _: &mut [u8], _: bool) -> i64 {
            panic!("host trap forbids native transfer")
        }
        fn wait(&mut self, _: u64) -> i64 {
            panic!("host trap forbids native wait")
        }
        fn close(&mut self, _: u64) -> i64 {
            panic!("host trap forbids native close")
        }
    }
    pub fn call(op: u64, args: [u64; 6]) -> Status {
        LAST.with(|cell| *cell.borrow_mut() = Some((op, args)));
        (0, 19, 20)
    }
    #[test]
    fn actual_native_transmitter_query_is_scalar_holder_only_with_zero_tail() {
        let mut native = Native;
        assert_eq!(native.transmitter_empty(), 0);
        LAST.with(|cell| {
            assert_eq!(
                *cell.borrow(),
                Some((0x26004, [0xf001, 0, 0, 0, 0, 0])),
                "TYPED_TEMT_QUERY_ARGUMENTS"
            )
        });
    }
    #[test]
    fn actual_native_park_routes_deadline_in_rdx_and_preserves_generic_ctl() {
        let mut native = Native;
        let deadline = Deadline::after(100, 500).unwrap();
        assert_eq!(native.park_events(42, Some(deadline)), (0, 19, 20));
        LAST.with(|cell| {
            assert_eq!(
                *cell.borrow(),
                Some((0x2a001, [0xe002, 42, 600, 0, 0, 0])),
                "TYPED_PARK_RDX"
            )
        });
        native.park_events(42, None);
        LAST.with(|cell| assert_eq!(*cell.borrow(), Some((0x2a001, [0xe002, 42, 0, 0, 0, 0]))));
        native.ctl(0x2a001, 0xe002, 42);
        LAST.with(|cell| {
            assert_eq!(
                *cell.borrow(),
                Some((0x2a001, [0xe002, 42, 0, 0, 0, 0])),
                "GENERIC_CTL_UNCHANGED"
            )
        });
        native.observe_events();
        LAST.with(|cell| assert_eq!(*cell.borrow(), Some((0x2a000, [0xe002, 0, 0, 0, 0, 0]))));
    }
    #[test]
    fn actual_native_app_launch_uses_exact_record_and_four_endpoint_seam() {
        let mut native = Native;
        let record = [0u8; 320];
        assert_eq!(native.launch_app(&record, 0xd1010101, 0xd1000102), 0);
        LAST.with(|cell| {
            assert_eq!(
                *cell.borrow(),
                Some((
                    0x2300a,
                    [
                        0xa001,
                        0xc002,
                        1,
                        record.as_ptr() as u64,
                        0xd1010101,
                        0xd1000102
                    ]
                )),
                "ACTUAL_APP_LAUNCH_REGISTERS"
            )
        });
    }
    #[test]
    fn observation_and_deadline_errors_ignore_aux_and_keep_tie_precedence() {
        assert_eq!(core::mem::size_of::<Option<Deadline>>(), 8);
        assert_eq!(Deadline::after(0, 0), Err(-22));
        assert_eq!(Deadline::after(u64::MAX, 500), Err(-22));
        let d = Deadline::after(10, 500).unwrap();
        for error in [-13, -110, -125] {
            assert_eq!(d.check((error, u64::MAX, u64::MAX)), Err(error));
        }
        assert_eq!(d.check((1, 0, 0)), Err(-5));
        assert_eq!(d.check((0, u64::MAX, 0)), Err(-28));
        assert_eq!(d.check((0, 7, 509)), Ok(7));
        assert_eq!(d.check((0, 8, 510)), Err(-110));
    }
}
