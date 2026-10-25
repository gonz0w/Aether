// SPDX-License-Identifier: BSD-2-Clause
//! Fixed service bindings for the bounded AECAT004 script witness.
use super::*;
#[path = "lifecycle.rs"]
mod lifecycle;
use lifecycle::{Native, NativeError, connection_owner::{self, Backend, Role, Terminal}, service_owner::Fault};
use core::num::NonZeroU64 as Handle;
pub use lifecycle::service_owner::Identity;
pub type Owned<'a> = connection_owner::Connection<'a, BoundNative>;
pub struct BoundNative {
    inner: Native, slot: usize,
    #[cfg(script_channel_fail)]
    channel_calls: u8,
}
impl BoundNative {
    pub fn new(factory: u64, images: [u64; 3], slot: usize) -> Self {
        check(slot < 3, 1604);
        Self { inner: Native { factory, images, startup: args(if slot == 0 { b"client" } else { b"worker" }) }, slot,
            #[cfg(script_channel_fail)]
            channel_calls: 0,
        }
    }
}
impl Backend for BoundNative {
    type Reader = Handle;
    type Writer = Handle;
    type Worker = Handle;
    type Error = NativeError;
    fn channel(&mut self) -> Result<(Handle, Handle), Fault<NativeError>> {
        #[cfg(script_channel_fail)]
        {
            self.channel_calls += 1;
            let selected = if cfg!(script_fail_file) { 2 } else if cfg!(script_fail_stream) { 1 } else { 0 };
            if self.slot == selected && self.channel_calls == if cfg!(script_second_channel) { 2 } else { 1 } {
                // Real denied allocation: no channel can be created without its grant.
                let result = ctl(0x24000, 0);
                check(result.0 == -13, 1606);
                let error = NativeError { operation: 0x24000, value: result.0 };
                // Test-only ambiguous response; this is not a kernel Unknown witness.
                return Err(if cfg!(script_unknown_channel) { Fault::Unknown(error) } else { Fault::Known(error) });
            }
        }
        self.inner.channel()
    }
    fn launch(&mut self, role: Role, request: Handle, reply: Handle) -> Result<Handle, Fault<NativeError>> {
        if role != if self.slot == 0 { Role::Runner } else { Role::Backend } {
            return Err(Fault::Known(NativeError { operation: 0x23002, value: -22 }));
        }
        #[cfg(script_unknown_launch)]
        if self.slot == 0 {
            self.inner.startup.argc = 5;
            let error = self.inner.launch_at(self.slot, request, reply);
            check(matches!(error, Err(Fault::Known(NativeError { operation: 0x23002, value: -22 }))), 1606);
            return Err(Fault::Unknown(NativeError { operation: 0x23002, value: -22 }));
        }
        self.inner.launch_at(self.slot, request, reply)
    }
    fn observe(&mut self, worker: Handle) -> Result<Option<Terminal>, Fault<NativeError>> { self.inner.observe(worker) }
    fn stop(&mut self, worker: Handle) -> Result<(), Fault<NativeError>> { self.inner.stop(worker) }
    fn close_reader(&mut self, reader: Handle) -> Result<(), Fault<NativeError>> { self.inner.close_reader(reader) }
    fn close_writer(&mut self, writer: Handle) -> Result<(), Fault<NativeError>> { self.inner.close_writer(writer) }
    fn reclaim(&mut self, worker: Handle) -> Result<(), Fault<NativeError>> { self.inner.reclaim(worker) }
}
pub fn start(owner: &mut Owned<'_>, native: &mut BoundNative) -> Connection {
    owner.start(native).unwrap_or_else(|_| end(1604));
    let (reader, writer, child) = owner.handles(&owner.key()).unwrap_or_else(|_| end(1604));
    Connection { reader: reader.get(), writer: writer.get(), child: child.get() }
}
pub fn observe(owner: &mut Owned<'_>, native: &mut BoundNative) -> Option<Terminal> {
    owner.observe(native, &owner.key()).unwrap_or_else(|_| end(1604))
}
pub fn cleanup(owner: &mut Owned<'_>, native: &mut BoundNative) {
    owner.cleanup(native, &owner.key()).unwrap_or_else(|_| end(1604));
}
pub fn finish_backend(owner: &mut Owned<'_>, native: &mut BoundNative) {
    owner.backend_eof(native, &owner.key()).unwrap_or_else(|_| end(1604));
    for _ in 0..100000 {
        match owner.observe(native, &owner.key()) {
            Ok(Some(t)) => {
                check(t == Terminal { detail: 17, kind: 1 }, 1604);
                cleanup(owner, native);
                return;
            }
            Ok(None) => { ctl(0x1fffe, 0); }
            Err(_) => end(1604),
        }
    }
    end(1604)
}
pub fn roles() -> [Role; 3] { [Role::Runner, Role::Backend, Role::Backend] }

#[cfg(script_launch_probe)]
#[path = "script_launch_probe.rs"]
pub mod script_launch_probe;

/// Startup is sequential: earlier providers have validated greetings, and no
/// shell reference has been published before the last launch succeeds.
#[inline(never)]
pub fn start_next(owners: &mut [Owned<'_>; 3], bindings: &mut [BoundNative; 3], slot: usize) -> Connection {
    #[cfg(script_startup_fail)]
    if slot == if cfg!(script_fail_file) { 2 } else if cfg!(script_fail_stream) { 1 } else { 0 } {
        bindings[slot].inner.startup.argc = 5;
    }
    if let Err(error) = owners[slot].start(&mut bindings[slot]) {
        // Only confirmed no-transfer errors permit rollback. Unknown ownership
        // must remain retained; no provider is touched after that outcome.
        check(matches!(error, lifecycle::service_owner::Error::Backend(Fault::Known(_))), 1604);
        #[cfg(script_startup_fail)]
        check(matches!(error, lifecycle::service_owner::Error::Backend(Fault::Known(NativeError { operation: 0x23002, value: -22 }))), 1604);
        if !cfg!(script_startup_skip_cleanup) {
            cleanup(&mut owners[slot], &mut bindings[slot]);
        }
        check(owners[slot].resources() == ([false; 2], [false; 2], false), 1604);
        for provider in [1, 2] {
            if owners[provider].resources().2 {
                if provider == 1 && !cfg!(script_startup_skip_files) {
                    let (reader, writer, child) = owners[provider].handles(&owners[provider].key()).unwrap_or_else(|_| end(1604));
                    let connection = Connection { reader: reader.get(), writer: writer.get(), child: child.get() };
                    for handle in [0xf101, 0xf201, 0xf202] {
                        check(backend(connection, 3, handle, 0, 0, &[]) == [0; 32], 1604);
                        check(get(&backend(connection, 2, handle, 0, 1, &[]), 0) as i32 == -9, 1604);
                    }
                }
                finish_backend(&mut owners[provider], &mut bindings[provider]);
            }
        }
        check(owners.iter().all(|owner| owner.resources() == ([false; 2], [false; 2], false)), 1604);
        // Report failed startup only after confirmed rollback; never normal boot.
        end(1605)
    }
    let (reader, writer, child) = owners[slot].handles(&owners[slot].key()).unwrap_or_else(|_| end(1604));
    Connection { reader: reader.get(), writer: writer.get(), child: child.get() }
}
