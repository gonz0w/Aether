    // SPDX-License-Identifier: BSD-2-Clause
    // Only the selected AF07 controller includes this borrowed frame decoder.
    fn metadata_body(&self, header: &[u8; 64], selection: u8) {
        check((get(header, 3) | get(header, 4) | get(header, 6) | get(header, 7)) == 0
            && get(header, 5) == 112);
        let mut bytes = [0u8; 128];
        for frame in bytes.as_chunks_mut::<64>().0 {
            check(channel::frame(self.receive, frame, false).is_ok());
        }
        check(bytes[112..].iter().all(|b| *b == 0));
        let mut values = [0u64; 14];
        for (i, value) in values.iter_mut().enumerate() {
            *value = u64::from_le_bytes(bytes[i*8..i*8+8].try_into().unwrap());
        }
        let (size, mode, links, uid) = match selection {
            0 => (0, 0o100600, 1, 1000),
            1 => (4096, 0o100600, 1, 1000),
            2 => (780248, 0o100755, 1, 0),
            3 => (5, 0o040755, 4, 0),
            _ => { check(false); return; }
        };
        check(values[0] == size && values[1] == mode && values[2] == links
            && values[3] == uid && values[4] == uid);
        // ZFS_ARCHIVE | ZFS_AV_MODIFIED. ACL/execute flags vary with mode;
        // a0600 created file must not be required to allow everyone execute.
        check(values[5] & 0x0000040800000000 == 0x0000040800000000);
        for i in [7, 9, 11, 13] { check(values[i] < 1_000_000_000); }
        if selection == 2 {
            check(values[5] == 0x840800000104 && values[6] == 1621447692
                && values[8] == 1620802862 && values[10] == 1620802862
                && values[12] == 1620802862);
        } else {
            for i in [8, 10] { check((1791290040..=1791290100).contains(&values[i])); }
            if selection != 3 {
                for i in [6, 12] { check((1791290040..=1791290100).contains(&values[i])); }
                check((values[8], values[9]) >= (values[12], values[13]));
                check((values[10], values[11]) >= (values[8], values[9]));
            } else {
                check(values[6] == 1621447687 && values[12] == 1620802853);
            }
        }
    }
