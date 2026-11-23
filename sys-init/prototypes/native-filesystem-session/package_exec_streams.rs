// SPDX-License-Identifier: BSD-2-Clause
//! Retire the direct child's inherited stream holders at actual image commit.
use fd_startup::Plan;
use fork_streams::{Caller, State};

pub fn commit_files_only(streams: &mut State, caller: Caller, old: &mut Plan) -> Result<(), i32> {
    for binding in &mut old.bindings {
        if matches!(binding.kind, 1 | 2) {
            binding.cloexec = 1;
        }
    }
    streams.commit_exec(caller, old)
}

#[cfg(test)]
mod tests {
    use super::*;
    use abi29_dispatch_core::startup::Identity;
    use fd_startup::{Binding, ForkStreams, Source};
    use fork_streams::{Outcome, SessionPipe};

    #[test]
    fn committed_child_loses_raw_console_while_parent_keeps_it() {
        let sources = [
            Source { reference: 0x7a000001, selector: 0, rights: 1, bound: 16 },
            Source { reference: 0x7a010001, selector: 1, rights: 2, bound: 16 },
        ];
        let mut streams = State::new([Some(sources[0]), Some(sources[1]), None], [SessionPipe::new(), SessionPipe::new()]).unwrap();
        let mut plan = Plan {
            identity: Identity::admitted(1, 1, 0xb0000102).unwrap(),
            shell: 1, parent: 0, generation: 31,
            bindings: [Binding::default(); 16], sources: [Source::default(); 7], history: [0; 2],
        };
        for i in 0..2 {
            plan.bindings[i] = Binding { kind: 1, selector: i as u8, cloexec: 0 };
            plan.sources[i] = sources[i];
        }
        streams.stage_child(10, &plan).unwrap();
        streams.child_ready(10).unwrap();
        commit_files_only(&mut streams, Caller::Child(1), &mut plan).unwrap();
        assert!(plan.sources.iter().all(|source| *source == Source::default()));
        assert!(plan.bindings.iter().all(|binding| *binding == Binding::default()));
        for selector in 0..2 {
            let mut request = [0u8; 32];
            request[..4].copy_from_slice(&(if selector == 0 { 1u32 } else { 2u32 }).to_le_bytes());
            request[4..8].copy_from_slice(&sources[selector].reference.to_le_bytes());
            request[8..12].copy_from_slice(&(selector as u32).to_le_bytes());
            request[12..16].copy_from_slice(&1u32.to_le_bytes());
            if selector == 1 { request[16] = b'x'; }
            let Outcome::Reply(denied) = streams.request(Caller::Child(1), &request, |_, _| panic!("child raw serial reached")) else { panic!("expected denial"); };
            assert_eq!(i32::from_le_bytes(denied[..4].try_into().unwrap()), -13);
            let mut observed = false;
            let Outcome::Reply(allowed) = streams.request(Caller::Parent, &request, |_, bytes| { observed = true; bytes[0] = b'x'; 1 }) else { panic!("expected parent reply"); };
            assert!(observed);
            assert_eq!(i32::from_le_bytes(allowed[..4].try_into().unwrap()), 1);
        }
    }
}
