// SPDX-License-Identifier: BSD-2-Clause
//! Host-only live C pipe consumer of actual Rust file/AF07 policy.
use filesystem_remote_descriptors::{NativeIdentity, ProcessFiles, MAX_READ};
use filesystem_service::Channel;
#[path = "fd-facade-live.rs"]
mod live;
fn main() {
    let executable = std::env::args().nth(1).unwrap();
    for mode in [
        "happy",
        "bytewise",
        "local",
        "header",
        "full",
        "denied",
        "padding",
        "source-body",
        "source-count",
        "source-close",
    ] {
        live::run(&executable, mode, 0);
    }
    for prefix in 0..64 {
        live::run(&executable, "body-loss", prefix);
    }
    println!("74 live C/Rust host cases pass");
}
