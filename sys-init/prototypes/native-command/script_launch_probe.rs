// SPDX-License-Identifier: BSD-2-Clause
//! Native startup rollback before any shell/file operation is admitted.
use super::*;
use lifecycle::service_owner::{Error, Phase};

pub fn run(factory: u64, images: [u64; 3]) -> ! {
    let mut shell_id = Identity::new();
    let mut stream_id = Identity::new();
    let mut file_id = Identity::new();
    let roles = roles();
    let mut owners = [Owned::new(&mut shell_id, roles[0], 1), Owned::new(&mut stream_id, roles[1], 1), Owned::new(&mut file_id, roles[2], 1)];
    let mut bindings = [BoundNative::new(factory, images, 0), BoundNative::new(factory, images, 1), BoundNative::new(factory, images, 2)];
    let fail_slot = if cfg!(script_fail_file) { 2 } else if cfg!(script_fail_stream) { 1 } else { 0 };
    let mut started = [false; 3];
    let mut stream = None;
    for slot in [2, 1, 0] {
        if slot == fail_slot {
            // Actual kernel validation rejects argc5 before worker/endpoint transfer.
            bindings[slot].inner.startup.argc = 5;
            check(matches!(owners[slot].start(&mut bindings[slot]),
                Err(Error::Backend(Fault::Known(NativeError { operation: 0x23002, value: -22 })))), 1604);
            check(owners[slot].phase() == Phase::Cleanup
                && owners[slot].resources() == ([true; 2], [true; 2], false), 1604);
            if !cfg!(script_skip_failed_cleanup) {
                cleanup(&mut owners[slot], &mut bindings[slot]);
            }
            check(owners[slot].phase() == Phase::Idle
                && owners[slot].resources() == ([false; 2], [false; 2], false), 1604);
            // No shell was launched and no file request was issued. Providers have
            // only sent their greetings, so EOF can settle them without lost work.
            for provider in [1, 2] {
                if started[provider] {
                    if provider == 1 && !cfg!(script_skip_stream_files) {
                        // Startup already opened these empty stream files. No
                        // client received them, so retire them before request EOF.
                        let connection = stream.unwrap();
                        for handle in [0xf101, 0xf201, 0xf202] {
                            check(get(&backend(connection, 2, handle, 0, 1, &[]), 0) == 0, 1604);
                            check(get(&backend(connection, 3, handle, 0, 0, &[]), 0) == 0, 1604);
                            check(get(&backend(connection, 2, handle, 0, 1, &[]), 0) as i32 == -9, 1604);
                        }
                    }
                    finish_backend(&mut owners[provider], &mut bindings[provider]);
                }
            }
            check(owners.iter().all(|owner| owner.resources() == ([false; 2], [false; 2], false)), 1604);
            // The frozen profile accepts exactly six reclaims only. A distinct
            // expected rejection records successful rollback of this short prefix.
            end(1605)
        }
        let connection = start(&mut owners[slot], &mut bindings[slot]);
        started[slot] = true;
        let mut hello = [0; 32];
        check(transfer(connection.reader, &mut hello, false) == 1, 1604);
        if slot == 2 {
            let mut expected = [0; 32];
            put(&mut expected, 4, 0xf001);
            check(hello == expected, 1604);
        } else {
            stream = Some(connection);
            check((0..3).all(|j| get(&hello, 4 + j * 4) == [0xf101, 0xf201, 0xf202][j])
                && get(&hello, 16) == 0, 1604);
        }
    }
    end(1604)
}
