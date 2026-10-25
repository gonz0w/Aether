    // SPDX-License-Identifier: BSD-2-Clause
    // Fixed loss points over the existing32-byte channel, not a runtime API.
    fn metadata_loss(&self, stage: u8) {
        check(stage <= 2);
        let mut raw = self.directory_message(12, 1);
        if stage == 0 {
            check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
            self.directory_send(&mut raw, 0, 0);
            return;
        }
        self.directory_send(&mut raw, 0, 0);
        self.directory_receive(&mut raw, 0);
        check(
            (get(&raw, 3) | get(&raw, 4) | get(&raw, 6) | get(&raw, 7)) == 0 && get(&raw, 5) == 112,
        );
        if stage == 2 {
            check(channel::frame(self.receive, &mut raw, false).is_ok());
            check(
                get(&raw, 0) == 5
                    && get(&raw, 1) == 0o040755
                    && get(&raw, 2) == 4
                    && get(&raw, 3) == 0
                    && get(&raw, 4) == 0
                    && get(&raw, 5) & 0x0000040800000000 == 0x0000040800000000
                    && get(&raw, 6) == 1621447687
                    && get(&raw, 7) < 1_000_000_000,
            );
        }
        let mut prefix = [0; 16];
        check(self.metadata_prefix(&mut prefix).is_ok());
        let first = u64::from_le_bytes(prefix[..8].try_into().unwrap());
        let second = u64::from_le_bytes(prefix[8..].try_into().unwrap());
        check(if stage == 1 {
            first == 5 && second == 0o040755
        } else {
            (1791290040..=1791290100).contains(&first) && second < 1_000_000_000
        });
        check(call(0x24003, self.receive, 0, 0, 0).0 == 0);
    }

    fn metadata_prefix(&self, bytes: &mut [u8; 16]) -> Result<(), i64> {
        let mut offset = 0;
        for _ in 0..100_000 {
            let remaining = bytes.len() - offset;
            // SAFETY: this initialized exclusive suffix stays live throughout
            // the synchronous copy. Kernel copies at most16 bytes, retaining
            // no pointer on success, partial progress, error or EAGAIN.
            let count = unsafe {
                channel::trap(
                    0x24001,
                    self.receive,
                    bytes[offset..].as_mut_ptr() as u64,
                    remaining as u64,
                    0,
                )
            }
            .0;
            if count == -11 {
                // SAFETY: scalar owned endpoint; recheck after readiness and
                // never read again into bytes already accepted.
                let status = unsafe { channel::trap(0x24004, self.receive, 0, 0, 0) }.0;
                if status != 0 {
                    return Err(if status < 0 { status } else { -5 });
                }
            } else if count <= 0 || count as usize > remaining {
                return Err(if count < 0 { count } else { -5 });
            } else {
                offset += count as usize;
                if offset == bytes.len() {
                    return Ok(());
                }
            }
        }
        Err(-110)
    }
