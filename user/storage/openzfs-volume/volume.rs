// SPDX-License-Identifier: BSD-2-Clause
// Private immutable native-volume view; filesystem policy stays above this seam.
#![no_std]
const EIO: i32 = 5;
const EACCES: i32 = 13;
const EINVAL: i32 = 22;
const EOVERFLOW: i32 = 75;
const MAX_IO: usize = 128 * 1024;
#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Volume {
    version: u32,
    bytes: u32,
    grant: u64,
    sectors: u64,
    rights: u64,
}
trait Backend {
    fn query(&mut self, grant: u64) -> Result<[u64; 4], i32>;
    fn sector(&mut self, grant: u64, write: bool, sector: u64, buffer: usize)
    -> Result<usize, i32>;
    fn flush(&mut self, grant: u64) -> Result<(), i32>;
}
fn bind(backend: &mut impl Backend, grant: u64) -> Result<Volume, i32> {
    let [size, sectors, rights, reserved] = backend.query(grant)?;
    if size != 512 || sectors == 0 || rights == 0 || rights & !7 != 0 || reserved != 0 {
        return Err(EIO);
    }
    if sectors > i64::MAX as u64 / 512 {
        return Err(EOVERFLOW);
    }
    Ok(Volume {
        version: 1,
        bytes: 32,
        grant,
        sectors,
        rights,
    })
}
fn validate(backend: &mut impl Backend, volume: Volume) -> Result<(), i32> {
    if volume.version != 1 || volume.bytes != 32 {
        return Err(EINVAL);
    }
    if bind(backend, volume.grant)? != volume {
        return Err(EIO);
    }
    Ok(())
}
fn transfer(
    backend: &mut impl Backend,
    volume: Volume,
    write: bool,
    offset: i64,
    buffer: usize,
    count: usize,
) -> (i32, usize) {
    let work = || -> Result<(), i32> {
        if offset < 0 || offset % 512 != 0 || count % 512 != 0 || count > MAX_IO {
            return Err(EINVAL);
        }
        if count != 0 && (buffer == 0 || buffer.checked_add(count).is_none()) {
            return Err(EOVERFLOW);
        }
        validate(backend, volume)?;
        if volume.rights & if write { 2 } else { 1 } == 0 {
            return Err(EACCES);
        }
        let start = offset as u64 / 512;
        let length = count as u64 / 512;
        if start > volume.sectors || length > volume.sectors - start {
            return Err(EINVAL);
        }
        Ok(())
    };
    let mut work = work;
    if let Err(error) = work() {
        return (error, 0);
    }
    let mut done = 0;
    while done < count {
        match backend.sector(
            volume.grant,
            write,
            offset as u64 / 512 + done as u64 / 512,
            buffer + done,
        ) {
            Ok(512) => done += 512,
            Ok(_) => return (EIO, done),
            Err(error) => return (error, done),
        }
    }
    (0, done)
}
fn flush(backend: &mut impl Backend, volume: Volume) -> Result<(), i32> {
    validate(backend, volume)?;
    if volume.rights & 4 == 0 {
        return Err(EACCES);
    }
    backend.flush(volume.grant)
}

#[cfg(not(test))]
mod native {
    use super::*;
    use core::arch::asm;
    fn call(op: u64, grant: u64, first: u64, second: u64, bytes: u64) -> Result<usize, i32> {
        let result: i64;
        // Synchronous scalar ABI. The native owner validates each forwarded
        // sector; no Rust reference/slice is formed from an I/O buffer pointer.
        unsafe {
            asm!("int 0x81", inlateout("rax") op => result, in("rdi") grant,
                 in("rsi") first, inlateout("rdx") second => _, in("r10") bytes,
                 lateout("rcx") _, lateout("r8") _, lateout("r9") _, lateout("r11") _);
        }
        if result < 0 {
            Err(i32::try_from(result.unsigned_abs()).unwrap_or(EIO))
        } else {
            Ok(result as usize)
        }
    }
    struct Native;
    impl Backend for Native {
        fn query(&mut self, grant: u64) -> Result<[u64; 4], i32> {
            let mut info = [0u64; 4];
            if call(0x27006, grant, info.as_mut_ptr() as u64, 32, 0)? != 0 {
                return Err(EIO);
            }
            Ok(info)
        }
        fn sector(
            &mut self,
            grant: u64,
            write: bool,
            sector: u64,
            buffer: usize,
        ) -> Result<usize, i32> {
            call(
                if write { 0x27001 } else { 0x27000 },
                grant,
                sector,
                buffer as u64,
                512,
            )
        }
        fn flush(&mut self, grant: u64) -> Result<(), i32> {
            if call(0x27002, grant, 0, 0, 0)? == 0 {
                Ok(())
            } else {
                Err(EIO)
            }
        }
    }
    fn aligned<T>(pointer: *const T) -> bool {
        !pointer.is_null() && (pointer as usize) % core::mem::align_of::<T>() == 0
    }
    // All metadata pointers refer to valid initialized in-process borrows.
    // Caller serializes binding/close and keeps buffers/records alive through return.
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn aether_volume_bind(grant: u64, out: *mut Volume) -> i32 {
        if !aligned(out) {
            return EINVAL;
        }
        match bind(&mut Native, grant) {
            Ok(volume) => {
                unsafe {
                    out.write(volume);
                }
                0
            }
            Err(error) => error,
        }
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn aether_volume_check(volume: *const Volume) -> i32 {
        if !aligned(volume) {
            return EINVAL;
        }
        validate(&mut Native, unsafe { volume.read() })
            .err()
            .unwrap_or(0)
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn aether_volume_io(
        volume: *const Volume,
        write: u32,
        offset: i64,
        buffer: *mut u8,
        count: usize,
        done: *mut usize,
    ) -> i32 {
        if !aligned(done) {
            return EINVAL;
        }
        unsafe {
            done.write(0);
        }
        if !aligned(volume) || write > 1 {
            return EINVAL;
        }
        let (error, completed) = transfer(
            &mut Native,
            unsafe { volume.read() },
            write != 0,
            offset,
            buffer as usize,
            count,
        );
        unsafe {
            done.write(completed);
        }
        error
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn aether_volume_flush(volume: *const Volume) -> i32 {
        if !aligned(volume) {
            return EINVAL;
        }
        flush(&mut Native, unsafe { volume.read() })
            .err()
            .unwrap_or(0)
    }
    #[panic_handler]
    fn panic(_: &core::panic::PanicInfo) -> ! {
        #[cfg(pool_diagnostics)]
        {
            unsafe extern "C" {
                fn aether_pool_failure_site(site: u32);
            }
            unsafe {
                aether_pool_failure_site(80);
            }
        }
        // No unwind crosses the C engine. Unexpected internal panic fails the owner.
        let _ = call(0x10000 + 231, 125, 0, 0, 0);
        loop {
            core::hint::spin_loop();
        }
    }
}

#[cfg(test)]
mod tests {
    extern crate std;
    use super::*;
    use std::vec::Vec;
    struct Fake {
        info: [u64; 4],
        error: i32,
        fail_at: Option<usize>,
        short: bool,
        flush_error: i32,
        calls: Vec<(bool, u64, usize)>,
        flushes: usize,
    }
    impl Fake {
        fn new() -> Self {
            Self {
                info: [512, 16, 7, 0],
                error: 0,
                fail_at: None,
                short: false,
                flush_error: 0,
                calls: Vec::new(),
                flushes: 0,
            }
        }
    }
    impl Backend for Fake {
        fn query(&mut self, grant: u64) -> Result<[u64; 4], i32> {
            if grant != 17 {
                Err(EACCES)
            } else if self.error != 0 {
                Err(self.error)
            } else {
                Ok(self.info)
            }
        }
        fn sector(
            &mut self,
            _: u64,
            write: bool,
            sector: u64,
            buffer: usize,
        ) -> Result<usize, i32> {
            self.calls.push((write, sector, buffer));
            if self.fail_at == Some(self.calls.len()) {
                Err(14)
            } else {
                Ok(if self.short { 511 } else { 512 })
            }
        }
        fn flush(&mut self, _: u64) -> Result<(), i32> {
            self.flushes += 1;
            if self.flush_error != 0 {
                Err(self.flush_error)
            } else {
                Ok(())
            }
        }
    }
    #[test]
    fn exact_geometry_and_native_denials_do_not_fabricate_bindings() {
        let mut b = Fake::new();
        assert_eq!(core::mem::size_of::<Volume>(), 32);
        assert_eq!(bind(&mut b, 18), Err(EACCES));
        for info in [
            [4096, 16, 7, 0],
            [512, 0, 7, 0],
            [512, 16, 0, 0],
            [512, 16, 8, 0],
            [512, 16, 7, 1],
        ] {
            b.info = info;
            assert_eq!(bind(&mut b, 17), Err(EIO));
        }
        b.info = [512, u64::MAX, 7, 0];
        assert_eq!(bind(&mut b, 17), Err(EOVERFLOW));
    }
    #[test]
    fn multi_sector_addresses_progress_and_exact_end_is_supported() {
        let mut b = Fake::new();
        let v = bind(&mut b, 17).unwrap();
        assert_eq!(transfer(&mut b, v, false, 14 * 512, 4096, 1024), (0, 1024));
        assert_eq!(b.calls, [(false, 14, 4096), (false, 15, 4608)]);
        assert_eq!(transfer(&mut b, v, true, 16 * 512, 0, 0), (0, 0));
    }
    #[test]
    fn malformed_ranges_and_pointer_overflow_never_reach_io() {
        let mut b = Fake::new();
        let v = bind(&mut b, 17).unwrap();
        for (offset, ptr, count) in [
            (-512, 4096, 512),
            (1, 4096, 512),
            (0, 4096, 513),
            (15 * 512, 4096, 1024),
            (i64::MAX, 4096, 512),
            (0, 4096, MAX_IO + 512),
        ] {
            assert_eq!(transfer(&mut b, v, true, offset, ptr, count), (EINVAL, 0));
        }
        for ptr in [0, usize::MAX - 511] {
            assert_eq!(transfer(&mut b, v, true, 0, ptr, 512), (EOVERFLOW, 0));
        }
        assert!(b.calls.is_empty());
    }
    #[test]
    fn source_change_close_and_missing_rights_reject_before_effects() {
        let mut b = Fake::new();
        let v = bind(&mut b, 17).unwrap();
        b.error = 9;
        assert_eq!(transfer(&mut b, v, true, 0, 4096, 512), (9, 0));
        b.error = 0;
        b.info[1] = 17;
        assert_eq!(transfer(&mut b, v, false, 0, 4096, 512), (EIO, 0));
        b.info = [512, 16, 1, 0];
        let ro = bind(&mut b, 17).unwrap();
        assert_eq!(transfer(&mut b, ro, true, 0, 4096, 512), (EACCES, 0));
        assert_eq!(flush(&mut b, ro), Err(EACCES));
        assert_eq!(b.flushes, 0);
        assert!(b.calls.is_empty());
    }
    #[test]
    fn partial_failure_and_unexpected_short_completion_never_count_as_full_success() {
        let mut b = Fake::new();
        let v = bind(&mut b, 17).unwrap();
        b.fail_at = Some(2);
        assert_eq!(transfer(&mut b, v, true, 0, 4096, 1536), (14, 512));
        assert_eq!(b.calls.len(), 2);
        b.fail_at = None;
        b.calls.clear();
        b.short = true;
        assert_eq!(transfer(&mut b, v, false, 0, 4096, 1024), (EIO, 0));
        assert_eq!(b.calls.len(), 1);
    }
    #[test]
    fn malformed_context_is_not_an_authorized_cached_view() {
        let mut b = Fake::new();
        let mut v = bind(&mut b, 17).unwrap();
        v.version = 2;
        assert_eq!(validate(&mut b, v), Err(EINVAL));
        v.version = 1;
        v.grant = 18;
        assert_eq!(flush(&mut b, v), Err(EACCES));
        assert_eq!(b.flushes, 0);
    }
    #[test]
    fn failed_device_flush_is_reported_once_without_replaying_completed_writes() {
        let mut b = Fake::new();
        let v = bind(&mut b, 17).unwrap();
        assert_eq!(transfer(&mut b, v, true, 0, 4096, 1024), (0, 1024));
        b.flush_error = EIO;
        assert_eq!(flush(&mut b, v), Err(EIO));
        assert_eq!(b.flushes, 1);
        assert_eq!(b.calls, [(true, 0, 4096), (true, 1, 4608)]);
        // This demonstrates a returned backend error only. Native issued-device
        // uncertainty currently panics; the model supplies no quiescence proof.
    }
}
