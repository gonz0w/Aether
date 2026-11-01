// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Proposed AEFDB001 producer. Labels require actual owner admission/delegation.
use abi29_dispatch_core::startup::{Identity, greeting};
#[cfg(all(any(native_tty_descriptor_probe, native_tty_duplex_probe), fs_file16))]
compile_error!("terminal bindings cannot select file16 startup");
pub const DUPLEX_BINDINGS: bool = cfg!(native_tty_duplex_probe);
pub const TERMINAL_BINDINGS: bool = cfg!(any(native_tty_descriptor_probe, native_tty_duplex_probe));
pub const BYTES: usize = 304;
pub const FILE_SLOTS_16: bool = cfg!(fs_file16);
pub const FIRST_FILE_FD: u8 = if FILE_SLOTS_16 { 0 } else { 3 };
pub const MAGIC: &[u8; 8] = if DUPLEX_BINDINGS {
    b"AEFDB004"
} else if TERMINAL_BINDINGS {
    b"AEFDB003"
} else if FILE_SLOTS_16 {
    b"AEFDB002"
} else {
    b"AEFDB001"
};
pub const MAP_MAGIC: &[u8; 8] = if DUPLEX_BINDINGS {
    b"AEFDT004"
} else if TERMINAL_BINDINGS {
    b"AEFDT003"
} else if FILE_SLOTS_16 {
    b"AEFDT002"
} else {
    b"AEFDT001"
};
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Binding {
    pub kind: u8,
    pub selector: u8,
    pub cloexec: u8,
}
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Source {
    pub reference: u32,
    pub selector: u32,
    pub rights: u32,
    pub bound: u32,
}
pub struct Plan {
    pub identity: Identity,
    pub shell: u32,
    pub parent: u32,
    pub generation: u64,
    pub bindings: [Binding; 16],
    pub sources: [Source; 7],
    pub history: [u32; 2],
}
/// Trusted owner state, not native authentication. Validation must inspect
/// authoritative state without effects. Activation follows exact context-ready.
pub trait ForkStreams {
    fn validate_fork(&self, plan: &Plan) -> Result<(), i32>;
    fn child_ready(&mut self, pid: u32) -> Result<(), i32>;
}
/// The caller owns the admitted instance, authenticated channel and actual
/// source/factory rights. This validates labels only; no authority is acquired.
/// On any error output remains unchanged. Delivery/partial failure is external.
pub fn encode(plan: &Plan, output: &mut [u8; BYTES]) -> Result<(), i32> {
    let identity = greeting(plan.identity, plan.shell, plan.parent)?;
    if plan.generation == 0 || plan.history.iter().any(|g| *g > 9) {
        return Err(-22);
    }
    if DUPLEX_BINDINGS
        && (plan.history != [0; 2]
            || plan.bindings.iter().enumerate().any(|(fd, b)| {
                if fd < 3 {
                    b.kind != 4 || b.selector as usize != fd || b.cloexec != 0
                } else {
                    *b != Binding::default()
                }
            }))
    {
        return Err(-22);
    }
    let mut seen = [false; 7];
    for (i, binding) in plan.bindings.iter().enumerate() {
        if binding.cloexec > 1 {
            return Err(-22);
        }
        match binding.kind {
            0 if binding.selector == 0 && binding.cloexec == 0 => {}
            1 | 4 if binding.selector <= 2 && (binding.kind == 1 || TERMINAL_BINDINGS) => {
                if plan.bindings[..i].iter().any(|other| {
                    matches!(other.kind, 1 | 4)
                        && other.selector == binding.selector
                        && other.kind != binding.kind
                }) {
                    return Err(-22);
                }
                seen[binding.selector as usize] = true;
            }
            2 if (3..=6).contains(&binding.selector) => seen[binding.selector as usize] = true,
            3 if (FIRST_FILE_FD..=15).contains(&binding.selector) => {
                if plan.bindings[..i]
                    .iter()
                    .any(|other| other.kind == 3 && other.selector == binding.selector)
                {
                    return Err(-22);
                }
            }
            _ => return Err(-22),
        }
    }
    for (i, source) in plan.sources.iter().enumerate() {
        if source.reference == 0 {
            if *source != Source::default() || seen[i] {
                return Err(-22);
            }
            continue;
        }
        if DUPLEX_BINDINGS && i < 3 && source.reference != 0x7a000001 | (i as u32) << 16 {
            return Err(-22);
        }
        let rights = if i == 0 || i == 3 || i == 5 { 1 } else { 2 };
        if !seen[i] || source.selector != i as u32 || source.rights != rights || source.bound != 16
        {
            return Err(-22);
        }
        if plan.sources[..i]
            .iter()
            .any(|s| s.reference == source.reference)
        {
            return Err(-22);
        }
        if i >= 3 {
            let object = (i - 3) / 2;
            let end = (i - 3) % 2 + 1;
            let generation = plan.history[object];
            if generation == 0
                || source.reference
                    != 0x79000000 | (object as u32) << 16 | generation << 8 | end as u32
            {
                return Err(-22);
            }
        }
    }
    output.fill(0);
    output[..8].copy_from_slice(MAGIC);
    put(output, 8, 1);
    put(output, 12, BYTES as u32);
    output[16..48].copy_from_slice(&identity);
    output[48..56].copy_from_slice(MAP_MAGIC);
    output[56..64].copy_from_slice(&plan.generation.to_le_bytes());
    output[64..72].copy_from_slice(&16u64.to_le_bytes());
    for (i, b) in plan.bindings.iter().enumerate() {
        output[112 + i * 4..116 + i * 4].copy_from_slice(&[b.kind, b.selector, b.cloexec, 0]);
    }
    for (i, source) in plan.sources.iter().enumerate() {
        for (j, value) in [
            source.reference,
            source.selector,
            source.rights,
            source.bound,
        ]
        .iter()
        .enumerate()
        {
            put(output, 176 + i * 16 + j * 4, *value);
        }
    }
    put(output, 288, plan.history[0]);
    put(output, 292, plan.history[1]);
    put(
        output,
        296,
        if plan.identity.slot == 1 {
            0x76050001
        } else {
            0
        },
    );
    Ok(())
}
fn put(output: &mut [u8; BYTES], offset: usize, value: u32) {
    output[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
}
