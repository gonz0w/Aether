// SPDX-License-Identifier: BSD-2-Clause
//! Host-only mutable-table consumer over real C/Rust file transport.
use filesystem_remote_descriptors::{NativeIdentity, ProcessFiles, MAX_READ};
use filesystem_service::Channel;
#[path = "fd-table-live.rs"]
mod live;
fn main() {
    let executable = std::env::args().nth(1).unwrap();
    for mode in [
        "happy",
        "bytewise",
        "full",
        "dup-full",
        "denied",
        "stale-source",
        "table-stale",
        "hole",
        "capacity",
        "collision",
        "source-close",
        "source-body",
        "source-count",
    ] {
        live::run(&executable, mode, 0);
    }
    for mode in ["open-loss", "close-loss", "dup-loss", "flags-loss"] {
        for prefix in 0..64 {
            live::run(&executable, mode, prefix);
        }
    }
    println!("269 live C/Rust table cases pass");
}
