// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
//! Separately linked ABI31 ordinary-app owner; no filesystem greeting consumer.
use af07_transport::native::Native;
use native_app_runtime::Runtime;
pub use owner_entry::_start;

#[unsafe(no_mangle)]
pub extern "C" fn owner_main(
    abi: u64,
    factory: u64,
    block: u64,
    image: u64,
    channels: u64,
    cleanup: u64,
    base: u64,
    bytes: u64,
) -> ! {
    let result = (|| {
        let binding = owner_region::validate_stack([
            abi, factory, block, image, channels, cleanup, base, bytes,
        ])?;
        // SAFETY: sole ABI31 entry, actual kernel-owned zeroed mapping, no
        // reentry/unmap or second owner. Runtime owns all scalar close receipts.
        let region = unsafe { owner_region::claim(binding)? };
        let (slot, workspace, _) = region.partition::<Runtime<Native>>()?.into_parts();
        let runtime = Runtime::new(Native).map_err(|_| owner_region::Error::Binding)?;
        let runtime = slot.write(runtime);
        if runtime.run(workspace).is_err() {
            let _ = runtime.contain();
        }
        Err::<(), _>(owner_region::Error::Binding)
    })();
    let _ = result;
    fault()
}
fn fault() -> ! {
    // SAFETY: intentional nonreturning containment fallback; no borrowed frame
    // is unwound and a returned terminal/halt is never retried.
    unsafe {
        core::arch::asm!("ud2", options(noreturn));
    }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo<'_>) -> ! {
    fault()
}
