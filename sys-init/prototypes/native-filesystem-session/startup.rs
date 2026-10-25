// SPDX-License-Identifier: BSD-2-Clause
//! AEFSH001 encoder for trusted ABI29 dispatcher admission records, not grants.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Identity {
    pub slot: u32,
    pub epoch: u32,
    pub handle: u64,
    pub pid: u32,
    pub memory: u64,
}

impl Identity {
    /// Caller must already own the kernel-admitted instance and its channel.
    pub fn admitted(slot: u32, epoch: u32, handle: u64) -> Result<Self, i32> {
        if !(1..=4).contains(&slot) || !(1..=15).contains(&epoch) {
            return Err(-22);
        }
        let suffix = ((epoch as u64) << 8) | (slot as u64 + 1);
        if handle != 0xb0000000 | suffix {
            return Err(-9);
        }
        Ok(Self {
            slot,
            epoch,
            handle,
            pid: epoch * 7 + slot + 1,
            memory: 0x40000000 | suffix,
        })
    }
}

/// Send only on this exact instance's authenticated channel, before the FD table.
/// Parent is a trusted observation, never a substituted shell/owner label.
pub fn greeting(identity: Identity, shell: u32, parent: u32) -> Result<[u8; 32], i32> {
    if Identity::admitted(identity.slot, identity.epoch, identity.handle)? != identity {
        return Err(-9);
    }
    if !(1..=3).contains(&shell) {
        return Err(-22);
    }
    if identity.slot == 1 {
        if identity.epoch != shell || parent != 7 {
            return Err(-9);
        }
    } else if parent != shell * 7 + 2 {
        return Err(-9);
    }
    let mut frame = [0; 32];
    frame[..8].copy_from_slice(b"AEFSH001");
    for (field, value) in frame[8..].as_chunks_mut::<4>().0.iter_mut().zip([
        29,
        7,
        identity.slot,
        identity.epoch,
        parent,
        shell,
    ]) {
        field.copy_from_slice(&value.to_le_bytes());
    }
    Ok(frame)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn id(slot: u32, epoch: u32) -> Identity {
        Identity::admitted(
            slot,
            epoch,
            0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
        )
        .unwrap()
    }
    #[test]
    fn actual_boot_parent_and_all_copied_child_identities() {
        for shell in 1..=3 {
            let parent = id(1, shell);
            let frame = greeting(parent, shell, 7).unwrap();
            assert_eq!(&frame[..8], b"AEFSH001");
            assert_eq!(parent.pid, shell * 7 + 2);
            assert_eq!(&frame[24..28], &7u32.to_le_bytes());
            for epoch in 1..=15 {
                for slot in 2..=4 {
                    let child = id(slot, epoch);
                    let frame = greeting(child, shell, parent.pid).unwrap();
                    assert_eq!(&frame[16..20], &slot.to_le_bytes());
                    assert_eq!(&frame[20..24], &epoch.to_le_bytes());
                    assert_eq!(&frame[24..28], &parent.pid.to_le_bytes());
                }
            }
        }
    }
    #[test]
    fn invalid_and_forged_admissions_do_not_produce_startup() {
        for slot in [0, 5, 6, u32::MAX] {
            assert!(Identity::admitted(slot, 1, 0).is_err());
        }
        for epoch in [0, 16, u32::MAX] {
            assert!(Identity::admitted(1, epoch, 0).is_err());
        }
        let valid = id(1, 1);
        for bad in [
            Identity { handle: 0, ..valid },
            Identity { pid: 8, ..valid },
            Identity {
                memory: 0x40000101,
                ..valid
            },
        ] {
            assert_eq!(greeting(bad, 1, 7), Err(-9));
        }
        for parent in [0, 9, 14, 21, 28, u32::MAX] {
            assert_eq!(greeting(valid, 1, parent), Err(-9));
        }
        assert_eq!(greeting(valid, 2, 7), Err(-9));
        for shell in [0, 4, u32::MAX] {
            assert_eq!(greeting(valid, shell, 7), Err(-22));
        }
        assert_eq!(greeting(id(2, 1), 1, 7), Err(-9));
    }
}
