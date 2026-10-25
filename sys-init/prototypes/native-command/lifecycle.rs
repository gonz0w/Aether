// SPDX-License-Identifier: BSD-2-Clause
//! ABI9 boundary used only by the bounded command integration fixture.
use super::*;
#[path = "service_owner.rs"]
pub mod service_owner;
#[path = "connection_owner.rs"]
pub mod connection_owner;
use connection_owner::{Backend, Role, Terminal};
use service_owner::Fault;
use core::num::NonZeroU64 as Handle;
#[derive(Clone, Copy, Debug)]
pub struct NativeError { pub operation: u64, pub value: i64 }
pub struct Native { pub factory: u64, pub images: [u64; 3], pub startup: Args }
fn decoded(op: u64, value: i64) -> Result<u64, Fault<NativeError>> {
    if value < 0 { Err(Fault::Known(NativeError { operation: op, value })) }
    else { Ok(value as u64) }
}
fn closed(op: u64, handle: u64) -> Result<(), Fault<NativeError>> {
    let result = ctl(op, handle).0;
    if result == 0 { Ok(()) }
    else { Err(Fault::Unknown(NativeError { operation: op, value: result })) }
}
impl Backend for Native {
    type Reader = Handle;
    type Writer = Handle;
    type Worker = Handle;
    type Error = NativeError;
    fn channel(&mut self) -> Result<(Handle, Handle), Fault<NativeError>> {
        let result = ctl(0x24000, 0xd001);
        let reader = decoded(0x24000, result.0)?;
        if reader == 0 || result.1 == 0 { return Err(Fault::Unknown(NativeError { operation: 0x24000, value: 0 })); }
        Ok((Handle::new(reader).unwrap(), Handle::new(result.1).unwrap()))
    }
    fn launch(&mut self, role: Role, request: Handle, reply: Handle) -> Result<Handle, Fault<NativeError>> {
        #[cfg(init_service_table)]
        let slot = super::service_table::image_slot(role);
        #[cfg(not(init_service_table))]
        let slot = match role { Role::Runner => 0, Role::Backend => 1, Role::Command => 2 };
        self.launch_at(slot, request, reply)
    }
    fn observe(&mut self, worker: Handle) -> Result<Option<Terminal>, Fault<NativeError>> {
        let result = ctl(0x20001, worker.get());
        let value = decoded(0x20001, result.0)?;
        if value == 0 { return Ok(None); }
        if !(1..=3).contains(&result.2) { return Err(Fault::Unknown(NativeError { operation: 0x20001, value: result.2 as i64 })); }
        Ok(Some(Terminal { detail: value - 1, kind: result.2 }))
    }
    fn stop(&mut self, worker: Handle) -> Result<(), Fault<NativeError>> {
        let value = decoded(0x20007, ctl(0x20007, worker.get()).0)?;
        if value == 0 { Ok(()) } else { Err(Fault::Unknown(NativeError { operation: 0x20007, value: value as i64 })) }
    }
    fn close_reader(&mut self, reader: Handle) -> Result<(), Fault<NativeError>> { closed(0x24003, reader.get()) }
    fn close_writer(&mut self, writer: Handle) -> Result<(), Fault<NativeError>> { closed(0x24003, writer.get()) }
    fn reclaim(&mut self, worker: Handle) -> Result<(), Fault<NativeError>> { closed(0x20002, worker.get()) }
}
impl Native {
    pub fn launch_at(&mut self, slot: usize, request: Handle, reply: Handle) -> Result<Handle, Fault<NativeError>> {
        let image = self.images.get(slot).ok_or(Fault::Known(NativeError { operation: 0x23002, value: -22 }))?;
        let worker = decoded(0x23002, call(0x23002, self.factory, *image, slot as u64,
            &self.startup as *const Args as u64, request.get(), reply.get()).0)?;
        if worker == 0 { return Err(Fault::Unknown(NativeError { operation: 0x23002, value: 0 })); }
        Ok(Handle::new(worker).unwrap())
    }
}
pub fn borrowed(owner: &connection_owner::Connection<'_, Native>) -> Connection {
    let (reader, writer, child) = owner.handles(&owner.key()).unwrap_or_else(|_| end(1406));
    Connection { reader: reader.get(), writer: writer.get(), child: child.get() }
}

#[path = "byte_compare.rs"]
mod byte_compare;
