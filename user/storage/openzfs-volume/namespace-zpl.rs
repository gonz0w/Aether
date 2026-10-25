// SPDX-License-Identifier: BSD-2-Clause
//! Private synchronous ZPL probe with an opt-in authenticated channel fixture.
#![no_std]

#[cfg(all(namespace_ipc, not(namespace_wait)))]
#[path = "../namespace-channel.rs"]
mod channel;
#[path = "../namespace.rs"]
pub mod owner;
use core::{ffi::c_void, ptr::NonNull};
use owner::{Backend, Error, Kind, MAX_READ, Node, Owner, Rights};

#[repr(C)]
#[derive(Default)]
struct RawNode {
    object: u64,
    generation: u64,
    size: u64,
    mode: u64,
}

const _: () = assert!(core::mem::size_of::<RawNode>() == 32);
const _: () = assert!(core::mem::align_of::<RawNode>() == 8);

unsafe extern "C" {
    fn aether_zpl_open(spa: *mut c_void, dataset: *const u8, out: *mut *mut c_void) -> i32;
    fn aether_zpl_close(owned: *mut *mut c_void);
    fn aether_zpl_root(view: *mut c_void, out: *mut RawNode) -> i32;
    fn aether_zpl_lookup(
        view: *mut c_void,
        directory: u64,
        generation: u64,
        name: *const u8,
        length: usize,
        out: *mut RawNode,
    ) -> i32;
    fn aether_zpl_read(
        view: *mut c_void,
        object: u64,
        generation: u64,
        offset: u64,
        buffer: *mut u8,
        length: usize,
        count: *mut usize,
    ) -> i32;
    fn aether_namespace_hash_update(hash: *mut c_void, bytes: *const u8, length: usize) -> i32;
}

fn status(code: i32) -> Result<(), Error> {
    match code {
        0 => Ok(()),
        1.. => Err(Error::Backend(code)),
        _ => Err(Error::InvalidCompletion),
    }
}

fn node(raw: RawNode) -> Result<Node, Error> {
    let kind = match raw.mode & 0o170000 {
        0o040000 => Kind::Directory,
        0o100000 => Kind::File,
        _ => return Err(Error::InvalidMetadata),
    };
    if raw.object == 0 || raw.generation == 0 {
        return Err(Error::InvalidMetadata);
    }
    Ok(Node::new(raw.object, raw.generation, raw.size, kind))
}

// NonNull is neither Send nor Sync. No cloning or public constructor permits
// transfer, duplication or escaping the sole private probe's live SPA borrow.
struct Zpl {
    view: NonNull<c_void>,
}

impl Zpl {
    /// SPA must remain valid, borrowed and readonly through this value's Drop.
    /// Every nonnull C output is an owned valid context, even on an error.
    /// The only production caller is the synchronous probe below; it cannot
    /// return this backend or its pointers to its C caller.
    unsafe fn open(spa: NonNull<c_void>) -> Result<Self, Error> {
        let mut view = core::ptr::null_mut();
        // SAFETY: fixed NUL-terminated dataset, valid borrowed SPA and exclusive
        // initialized output. No overlapping storage or retained Rust pointer.
        let code = unsafe {
            aether_zpl_open(
                spa.as_ptr(),
                c"testpool_zstd/x86_64".as_ptr().cast(),
                &mut view,
            )
        };
        let owned = NonNull::new(view).map(|view| Self { view });
        status(code)?; // Drops an unexpected owned error output as well.
        owned.ok_or(Error::InvalidCompletion)
    }
}

impl Drop for Zpl {
    fn drop(&mut self) {
        let mut view = self.view.as_ptr();
        // SAFETY: this is the unique live context, SPA is still borrowed, and
        // no operation is in flight. C consumes/nulls the owned context once.
        unsafe { aether_zpl_close(&mut view) };
    }
}

impl Backend for Zpl {
    fn root(&mut self) -> Result<Node, Error> {
        let mut raw = RawNode::default();
        // SAFETY: unique live context and separate initialized output.
        status(unsafe { aether_zpl_root(self.view.as_ptr(), &mut raw) })?;
        node(raw)
    }

    fn lookup(&mut self, directory: Node, name: &[u8]) -> Result<Node, Error> {
        let (object, generation) = directory.identity();
        let mut raw = RawNode::default();
        // SAFETY: owner already validated scope/name; slice and output remain
        // live, nonaliasing and unretained for the synchronous original C call.
        status(unsafe {
            aether_zpl_lookup(
                self.view.as_ptr(),
                object,
                generation,
                name.as_ptr(),
                name.len(),
                &mut raw,
            )
        })?;
        node(raw)
    }

    fn read(&mut self, file: Node, offset: u64, buffer: &mut [u8]) -> Result<usize, Error> {
        buffer.fill(0);
        if buffer.len() > MAX_READ || offset.checked_add(buffer.len() as u64).is_none() {
            return Err(Error::Invalid);
        }
        let (object, generation) = file.identity();
        let mut count = 0;
        // SAFETY: original C borrows the live context and exact writable slice;
        // count is separate initialized storage. Neither pointer is retained.
        let code = unsafe {
            aether_zpl_read(
                self.view.as_ptr(),
                object,
                generation,
                offset,
                buffer.as_mut_ptr(),
                buffer.len(),
                &mut count,
            )
        };
        if let Err(error) = status(code) {
            buffer.fill(0);
            return Err(error);
        }
        if count > buffer.len() {
            buffer.fill(0);
            return Err(Error::InvalidCompletion);
        }
        buffer[count..].fill(0);
        Ok(count)
    }
}

fn require(value: bool) -> Result<(), Error> {
    if value {
        Ok(())
    } else {
        Err(Error::InvalidCompletion)
    }
}

// Fixed labels below are test inputs inside one fresh engine, NOT transport
// authentication/provisioning evidence. No untrusted message reaches attach.
unsafe fn exercise(spa: NonNull<c_void>, hash: NonNull<c_void>) -> Result<(), Error> {
    // SAFETY: the private C entry keeps its SPA borrow through this entire call.
    let mut backend = unsafe { Zpl::open(spa) }?;
    let root = backend.root()?;
    require(root.identity() == (34, 45))?;
    let file = backend.lookup(root, b"zstd")?;
    require(file.identity() == (2, 47))?;
    let mut owner = Owner::new(backend, 1)?;
    let a = owner.attach(71, Rights::ALL)?;
    let b = owner.attach(72, Rights::LOOKUP)?;
    let f = owner.lookup(71, a.session, a.root.handle, b"zstd", Rights::READ)?;
    require(f.kind == Kind::File && f.size == 780248)?;
    let mut reply = [0xa5; MAX_READ];
    require(owner.read(72, a.session, f.handle, 0, 1, &mut reply) == Err(Error::Denied))?;
    require(reply.iter().all(|b| *b == 0))?;
    require(owner.read(72, b.session, f.handle, 0, 1, &mut reply) == Err(Error::Denied))?;
    require(
        owner.lookup(72, b.session, b.root.handle, b"zstd", Rights::READ) == Err(Error::Denied),
    )?;
    require(owner.read(71, a.session, a.root.handle, 0, 1, &mut reply) == Err(Error::IsDirectory))?;
    require(
        owner.lookup(71, a.session, a.root.handle, b"..", Rights::READ) == Err(Error::Invalid),
    )?;
    require(
        owner.lookup(71, a.session, a.root.handle, b"absent", Rights::READ)
            == Err(Error::Backend(2)),
    )?;
    let mut offset = 0;
    while offset < f.size {
        let count = owner.read(71, a.session, f.handle, offset, MAX_READ, &mut reply)?;
        require(count != 0 && reply[count..].iter().all(|b| *b == 0))?;
        // SAFETY: caller-owned SHA2 state stays valid through exercise; the
        // fixed helper consumes only this confirmed borrowed prefix, no retain.
        status(unsafe { aether_namespace_hash_update(hash.as_ptr(), reply.as_ptr(), count) })?;
        offset += count as u64;
    }
    require(offset == 780248)?;
    require(owner.read(71, a.session, f.handle, offset, MAX_READ, &mut reply) == Ok(0))?;
    require(reply.iter().all(|b| *b == 0))?;
    require(owner.read(71, a.session, f.handle, 0, 0, &mut reply) == Ok(0))?;
    owner.close(71, a.session, f.handle)?;
    let fresh = owner.lookup(71, a.session, a.root.handle, b"zstd", Rights::READ)?;
    require(owner.read(71, a.session, f.handle, 0, 1, &mut reply) == Err(Error::Stale))?;
    owner.disconnect(71, a.session)?;
    require(owner.read(71, a.session, fresh.handle, 0, 1, &mut reply) == Err(Error::Stale))?;
    let restricted = owner.lookup(72, b.session, b.root.handle, b"zstd", Rights::LOOKUP)?;
    require(owner.read(72, b.session, restricted.handle, 0, 1, &mut reply) == Err(Error::Denied))?;
    owner.shutdown();
    require(owner.read(72, b.session, restricted.handle, 0, 1, &mut reply) == Err(Error::Closed))?;
    // SAFETY: same still-live SPA, previous context already dropped. Epoch2 is
    // distinct inside this bounded local probe; it is not a boot authority API.
    let mut replacement = Owner::new(unsafe { Zpl::open(spa) }?, 2)?;
    let c = replacement.attach(71, Rights::ALL)?;
    require(
        replacement.lookup(71, a.session, c.root.handle, b"zstd", Rights::READ)
            == Err(Error::Stale),
    )?;
    require(replacement.read(71, c.session, fresh.handle, 0, 1, &mut reply) == Err(Error::Stale))?;
    replacement.shutdown();
    Ok(())
}

#[cfg(namespace_ipc)]
unsafe fn serve(spa: NonNull<c_void>) -> Result<(), Error> {
    unsafe extern "C" {
        fn getauxval(key: usize) -> usize;
    }
    // SAFETY: the selected musl startup owns its copied auxv. These values are
    // bootstrap bindings, not request data. Each actual operation still requires
    // a live kernel holder match; editing auxv cannot acquire another endpoint.
    let (reader, writer) = unsafe { (getauxval(0xa004) as u64, getauxval(0xa005) as u64) };
    require(reader & 0xff == 1 && writer & 0xff == 2 && reader >> 16 != writer >> 16)?;
    // SAFETY: close has only scalar arguments, including these foreign tokens.
    require(unsafe { channel::trap(0x24003, reader + 1, 0, 0, 0) }.0 == -13)?;
    require(unsafe { channel::trap(0x24003, writer - 1, 0, 0, 0) }.0 == -13)?;
    // This boot's request object/generation never repeats in the selected
    // three-lifetime profile. Tokens have no cross-boot validity. The C importer
    // retains its SPA borrow while this sole extra owned context is live.
    let mut owner = Owner::new(unsafe { Zpl::open(spa) }?, reader)?;
    let mut binding = owner::wire::Binding::new(&mut owner, reader)?;
    let outcome = (|| {
        channel::frame(writer, &mut binding.greeting(), true)
            .map_err(|_| Error::InvalidCompletion)?;
        for _ in 0..64 {
            let mut request = [0; owner::wire::FRAME];
            channel::frame(reader, &mut request, false).map_err(|_| Error::InvalidCompletion)?;
            let mut reply = binding.request(&mut owner, &request);
            channel::frame(writer, &mut reply, true).map_err(|_| Error::InvalidCompletion)?;
            if binding.closed() {
                return Ok(());
            }
        }
        Err(Error::Full)
    })();
    // Revoke before closing the original C context on all completion paths.
    owner.shutdown();
    // SAFETY: scalar endpoint closes, no borrowed memory or operation in flight.
    let a = unsafe { channel::trap(0x24003, reader, 0, 0, 0) }.0;
    let b = unsafe { channel::trap(0x24003, writer, 0, 0, 0) }.0;
    outcome?;
    require(a == 0 && b == 0)
}

/// # Safety
/// Private importer only: live borrowed readonly SPA and a separate writable
/// SHA2 state initialized by owner-probe.c, both valid until return. No unwind,
/// reentry, concurrent mutation or retention. This is not a client C interface.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn aether_namespace_owner_probe(spa: *mut c_void, hash: *mut c_void) -> i32 {
    let (Some(spa), Some(hash)) = (NonNull::new(spa), NonNull::new(hash)) else {
        return 22;
    };
    // SAFETY: upheld by the one private synchronous C importer caller.
    let outcome = unsafe { exercise(spa, hash) };
    #[cfg(namespace_ipc)]
    let outcome = outcome.and_then(|()| unsafe { serve(spa) });
    match outcome {
        Ok(()) => 0,
        Err(Error::Backend(code)) => code,
        Err(_) => 5,
    }
}

#[cfg(test)]
extern crate std;
#[cfg(test)]
#[path = "../../../tests/fixtures/namespace_zpl.rs"]
mod tests;

#[cfg(namespace_wait)]
#[path = "../namespace-wait-channel.rs"]
mod channel;
