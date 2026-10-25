// SPDX-License-Identifier: BSD-2-Clause
use abi29_dispatch_core::startup::Identity;
#[cfg(test)]
use fd_startup::{BYTES, encode};
use fd_startup::{Binding, Plan, Source};
pub fn plan(slot: u32, epoch: u32, shell: u32) -> Plan {
    let mut p = Plan {
        identity: Identity::admitted(
            slot,
            epoch,
            0xb0000000 | (epoch as u64) << 8 | (slot as u64 + 1),
        )
        .unwrap(),
        shell,
        parent: if slot == 1 { 7 } else { shell * 7 + 2 },
        generation: u64::MAX - 17,
        bindings: [Binding::default(); 16],
        sources: [Source::default(); 7],
        history: [5, 9],
    };
    for i in 0..7 {
        p.bindings[i] = Binding {
            kind: if i < 3 { 1 } else { 2 },
            selector: i as u8,
            cloexec: (i % 2) as u8,
        };
        p.sources[i] = Source {
            reference: if i < 3 {
                0x10101 + i as u32
            } else {
                0x79000000
                    | (((i - 3) / 2) as u32) << 16
                    | p.history[(i - 3) / 2] << 8
                    | ((i - 3) % 2 + 1) as u32
            },
            selector: i as u32,
            rights: if i == 0 || i == 3 || i == 5 { 1 } else { 2 },
            bound: 16,
        };
    }
    p.bindings[7] = Binding {
        kind: 3,
        selector: 3,
        cloexec: 1,
    };
    p.bindings[8] = Binding {
        kind: 3,
        selector: 4,
        cloexec: 0,
    };
    p.bindings[9] = p.bindings[3];
    p
}
#[test]
fn all_identities_and_wire_fields() {
    for shell in 1..=3 {
        let mut ids = vec![(1, shell)];
        for epoch in 1..=15 {
            for slot in 2..=4 {
                ids.push((slot, epoch));
            }
        }
        for (slot, epoch) in ids {
            let p = plan(slot, epoch, shell);
            let mut out = [0xa5; BYTES];
            encode(&p, &mut out).unwrap();
            assert_eq!(&out[..8], b"AEFDB001");
            assert_eq!(&out[8..12], &1u32.to_le_bytes());
            assert_eq!(&out[12..16], &304u32.to_le_bytes());
            assert_eq!(&out[48..56], b"AEFDT001");
            assert_eq!(&out[56..64], &p.generation.to_le_bytes());
            assert_eq!(&out[64..72], &16u64.to_le_bytes());
            assert!(out[72..112].iter().all(|v| *v == 0));
            assert!(out[300..].iter().all(|v| *v == 0));
            assert_eq!(&out[288..292], &5u32.to_le_bytes());
            assert_eq!(&out[292..296], &9u32.to_le_bytes());
            assert_eq!(
                &out[296..300],
                &(if slot == 1 { 0x76050001u32 } else { 0 }).to_le_bytes()
            );
        }
    }
}
#[test]
fn invalid_plans_preserve_output() {
    let mut bad = Vec::new();
    let mut p = plan(1, 1, 1);
    p.parent = 14;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.identity.pid = 8;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.generation = 0;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.history[1] = 10;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.bindings[10] = p.bindings[7];
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.bindings[10] = Binding {
        kind: 0,
        selector: 1,
        cloexec: 0,
    };
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.bindings[7].cloexec = 2;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.sources[3].reference ^= 0x100;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.sources[0].reference = p.sources[1].reference;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.sources[1].rights = 1;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.sources[2].bound = 17;
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.sources[0] = Source::default();
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.bindings[0] = Binding::default();
    bad.push(p);
    let mut p = plan(1, 1, 1);
    p.sources[0].reference = 0;
    bad.push(p);
    for p in bad {
        let mut out = [0xa5; BYTES];
        assert!(encode(&p, &mut out).is_err());
        assert_eq!(out, [0xa5; BYTES]);
    }
}
#[test]
fn histories_survive_absent_pipes_and_labels_are_opaque() {
    let mut p = plan(2, 15, 3);
    for b in &mut p.bindings {
        if b.kind == 2 {
            *b = Binding::default();
        }
    }
    p.sources[3..].fill(Source::default());
    p.generation = 77;
    p.sources[0].reference = 0x12345678;
    let mut out = [0; BYTES];
    encode(&p, &mut out).unwrap();
    assert_eq!(&out[288..296], &[5, 0, 0, 0, 9, 0, 0, 0]);
    assert_eq!(&out[176..180], &0x12345678u32.to_le_bytes());
}
