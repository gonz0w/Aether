// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
//! Selected ABI30/31 boot composition. Linking is not native acceptance.
use af07_transport::{Endpoints, native::Native};
use filesystem_service::channel::Framed;
use owner_runtime::{Runtime, provision};

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
        let scalars = [abi, factory, block, image, channels, cleanup, base, bytes];
        let binding = if cfg!(owner_stack) {
            owner_region::validate_stack(scalars)?
        } else {
            owner_region::validate(scalars)?
        };
        // SAFETY: sole kernel entry captured all selected ABI30/31 registers before ordinary
        // calls. The selected native profile must supply the unique live zeroed
        // RW/NX mapping. There is no reentry, unmap, alias or second claim.
        let region = unsafe { owner_region::claim(binding)? };
        let (slot, workspace, _) = region.partition::<Runtime<Native>>()?.into_parts();
        let mut kernel = Native;
        let mut remaining = 1_000_000;
        let (engine, pair) =
            provision(&mut kernel, &mut remaining).map_err(|_| owner_region::Error::Binding)?;
        let endpoints = Endpoints::new(kernel.clone(), pair[2], pair[1])
            .map_err(|_| owner_region::Error::Binding)?;
        #[cfg(not(fs_home_owner))]
        let owner =
            Runtime::connect_in_place(slot, kernel, engine, Framed(endpoints), pair[0], remaining)
                .map_err(|_| owner_region::Error::Binding)?;
        #[cfg(fs_home_owner)]
        let owner = Runtime::connect_home_in_place(
            slot,
            kernel,
            engine,
            Framed(endpoints),
            pair[0],
            remaining,
        )
        .map_err(|_| owner_region::Error::Binding)?;
        owner
            .run(workspace)
            .map_err(|_| owner_region::Error::Binding)
    })();
    // Both error and an impossible returned halt fault the owner. No automatic
    // retry or clean export/reclaim claim may follow an unknown disposition.
    let _ = result;
    fault()
}

fn fault() -> ! {
    // SAFETY: intentional terminal trap; no memory access or returning control.
    unsafe { core::arch::asm!("ud2", options(noreturn)) }
}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo<'_>) -> ! {
    fault()
}
