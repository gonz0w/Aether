// SPDX-License-Identifier: BSD-2-Clause
//! Host integration of unchanged AEFD0001 policy and prepared-duplicate redirection.
use filesystem_remote_descriptors::{NativeIdentity, ProcessFiles, MAX_READ};
use filesystem_service::Channel;
#[path = "fd-redirect-live.rs"]
mod live;
fn main() {
    let executable = std::env::args().nth(1).unwrap();
    for mode in [
        "file-file",
        "bytewise",
        "file-empty",
        "file-stream",
        "stream-file",
        "file-self",
        "alias-file",
        "local-full",
        "remote-full",
        "target-denied",
        "target-consumed",
        "target-unknown-open",
        "target-unknown-closed",
        "missing-adapter",
        "stale-target",
        "cleanup-stale",
        "collision",
        "stale-source",
        "source-body",
        "source-count",
        "source-close",
    ] {
        live::run(&executable, mode, 0);
    }
    for mode in ["dup-loss", "target-loss", "cleanup-loss"] {
        for prefix in 0..64 {
            live::run(&executable, mode, prefix);
        }
    }
    println!("213 live C/Rust redirection cases pass");
}
