// SPDX-License-Identifier: BSD-2-Clause
//! Selected005 local control policy. The private alias is never a public selector.
use super::tty_errno;
use serial_tty::{ApplyWhen, Bindings, Caller, Mode, ModeRequest, Reference, Snapshot, Terminal};
pub const CONTROL: u32 = 0x7d000001;
#[derive(Clone, Copy)]
pub struct Request {
    op: u32,
    drain: bool,
    revision: u64,
    mode: Mode,
}
impl Request {
    pub fn drain(self) -> bool {
        self.drain
    }
}
pub struct State {
    baseline: Option<Snapshot>,
    private: Option<Reference>,
    cleanup_result: Option<i64>,
}
impl State {
    pub fn admit(terminal: &mut Terminal, refs: &Bindings, caller: Caller) -> Result<Self, i64> {
        let baseline = terminal.snapshot(caller, &refs.stdin).map_err(tty_errno)?;
        let private = terminal.duplicate(caller, &refs.stdin).map_err(tty_errno)?;
        Ok(Self {
            baseline: Some(baseline),
            private: Some(private),
            cleanup_result: None,
        })
    }
    pub fn prepare(
        &self,
        terminal: &Terminal,
        refs: &Bindings,
        caller: Caller,
        raw: &[u8; 32],
    ) -> Result<Request, i64> {
        if self.cleanup_result.is_some() {
            return Err(-9);
        }
        let op = u32_at(raw, 0);
        let action = u32_at(raw, 8);
        let revision = u64::from_le_bytes(raw[16..24].try_into().unwrap());
        if !matches!(op, 0x10..=0x12) || u32_at(raw, 12) != 0 || raw[30..] != [0; 2] {
            return Err(-22);
        }
        if u32_at(raw, 4) != CONTROL {
            return Err(-13);
        }
        let (current, actual) = terminal
            .mode_state(caller, &refs.stdin)
            .map_err(tty_errno)?;
        if op == 0x10 {
            if raw[8..] != [0; 24] {
                return Err(-22);
            }
            return Ok(Request {
                op,
                drain: false,
                revision: actual,
                mode: current,
            });
        }
        if action > 1 {
            return Err(-95);
        }
        if self.baseline.is_none() || revision == 0 || revision != actual {
            return Err(-9);
        }
        if actual == u64::MAX {
            return Err(-5);
        }
        let mode = if op == 0x11 {
            if u32_at(raw, 24) > 1 || raw[28] != 1 || raw[29] != 0 {
                return Err(-95);
            }
            Mode {
                icrnl: raw[24] != 0,
                ..Mode::IMMEDIATE
            }
        } else {
            if raw[24..] != [0; 8] {
                return Err(-22);
            }
            current
        };
        Ok(Request {
            op,
            drain: action == 1,
            revision,
            mode,
        })
    }
    pub fn commit(
        &mut self,
        terminal: &mut Terminal,
        refs: &Bindings,
        caller: Caller,
        request: Request,
    ) -> Result<[u8; 32], i64> {
        if self.cleanup_result.is_some() {
            return Err(-9);
        }
        let (mut mode, mut revision) = terminal
            .mode_state(caller, &refs.stdin)
            .map_err(tty_errno)?;
        if request.op != 0x10 {
            if request.revision != revision {
                return Err(-9);
            }
            let baseline = self.baseline.as_mut().ok_or(-9)?;
            revision = if request.op == 0x11 {
                mode = request.mode;
                terminal
                    .apply_now(
                        caller,
                        &refs.stdin,
                        baseline,
                        ModeRequest {
                            mode,
                            action: ApplyWhen::Now,
                        },
                    )
                    .map_err(tty_errno)?
            } else {
                let rev = terminal
                    .restore(caller, &refs.stdin, baseline)
                    .map_err(tty_errno)?;
                mode = terminal
                    .mode_state(caller, &refs.stdin)
                    .map_err(tty_errno)?
                    .0;
                self.baseline = None;
                rev
            };
        }
        let mut out = [0; 32];
        out[4..8].copy_from_slice(&request.op.to_le_bytes());
        out[8..12].copy_from_slice(&16u32.to_le_bytes());
        out[16..24].copy_from_slice(&revision.to_le_bytes());
        out[24..28].copy_from_slice(&u32::from(mode.icrnl).to_le_bytes());
        out[28] = mode.vmin;
        out[29] = mode.vtime;
        Ok(out)
    }
    pub fn cleanup_result(&self) -> Option<i64> {
        self.cleanup_result
    }
    pub fn cleanup(
        &mut self,
        terminal: &mut Terminal,
        caller: Caller,
        stopped: bool,
    ) -> Result<(), i64> {
        if !stopped {
            return Err(-13);
        }
        if let Some(result) = self.cleanup_result {
            return if result == 0 { Ok(()) } else { Err(result) };
        }
        let result = (|| {
            let Some(reference) = self.private else {
                return Ok(());
            };
            if let Some(baseline) = self.baseline.as_mut() {
                // Trusted local reset remains safe after unknown byte I/O.
                terminal
                    .restore(caller, &reference, baseline)
                    .map_err(tty_errno)?;
                self.baseline = None;
            }
            terminal.close(caller, reference).map_err(tty_errno)?;
            self.private = None;
            Ok(())
        })();
        self.cleanup_result = Some(result.as_ref().err().copied().unwrap_or(0));
        result
    }
}
pub fn u32_at(raw: &[u8; 32], at: usize) -> u32 {
    u32::from_le_bytes(raw[at..at + 4].try_into().unwrap())
}
pub fn error(op: u32, status: i64) -> [u8; 32] {
    let mut out = [0; 32];
    let status = if (-4095..=-1).contains(&status) {
        status as i32
    } else {
        -5
    };
    out[..4].copy_from_slice(&status.to_le_bytes());
    out[4..8].copy_from_slice(&op.to_le_bytes());
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use serial_tty::{Completion, Error, ReadOutcome, Rights, Stop};
    const CALLER: Caller = Caller {
        identity: 7,
        generation: 1,
    };
    fn fixture() -> (Terminal, Bindings, State) {
        let (mut t, b) = Terminal::admit(
            41,
            CALLER,
            [
                Rights::READ.union(Rights::MODE),
                Rights::WRITE,
                Rights::WRITE,
            ],
            Mode::IMMEDIATE,
        )
        .unwrap();
        let s = State::admit(&mut t, &b, CALLER).unwrap();
        (t, b, s)
    }
    fn frame(op: u32, revision: u64, bits: u32, action: u32) -> [u8; 32] {
        let mut raw = [0; 32];
        raw[..4].copy_from_slice(&op.to_le_bytes());
        raw[4..8].copy_from_slice(&CONTROL.to_le_bytes());
        raw[8..12].copy_from_slice(&action.to_le_bytes());
        raw[16..24].copy_from_slice(&revision.to_le_bytes());
        if op == 0x11 {
            raw[24..28].copy_from_slice(&bits.to_le_bytes());
            raw[28] = 1;
        }
        raw
    }
    #[test]
    fn data_access_never_implies_mode_grant() {
        let (mut t, b) = Terminal::admit(
            41,
            CALLER,
            [Rights::READ, Rights::WRITE, Rights::WRITE],
            Mode::IMMEDIATE,
        )
        .unwrap();
        assert!(
            matches!(State::admit(&mut t, &b, CALLER), Err(-13)),
            "EXPLICIT_MODE_GRANT_REQUIRED"
        );
    }
    #[test]
    fn mode_codec_revision_and_actual_icrnl_then_posix_set_restore() {
        let (mut t, b, mut s) = fixture();
        assert_eq!(
            t.duplicate(CALLER, &b.stdin),
            Err(Error::Exhausted),
            "NO_FIFTH_ALIAS"
        );
        let get = s.prepare(&t, &b, CALLER, &frame(0x10, 0, 0, 0)).unwrap();
        let reply = s.commit(&mut t, &b, CALLER, get).unwrap();
        assert_eq!(u32_at(&reply, 8), 16);
        assert_eq!(&reply[16..24], &1u64.to_le_bytes());
        let change = s.prepare(&t, &b, CALLER, &frame(0x11, 1, 1, 0)).unwrap();
        s.commit(&mut t, &b, CALLER, change).unwrap();
        let mut bytes = [0; 2];
        assert_eq!(
            t.read(CALLER, &b.stdin, &mut bytes, |out| {
                out.copy_from_slice(b"\rX");
                Completion {
                    count: 2,
                    stop: Stop::Complete,
                }
            }),
            Ok(ReadOutcome::Bytes(2))
        );
        assert_eq!(&bytes, b"\nX");
        let saved = s.prepare(&t, &b, CALLER, &frame(0x11, 2, 0, 0)).unwrap();
        s.commit(&mut t, &b, CALLER, saved).unwrap();
        assert_eq!(
            t.mode_state(CALLER, &b.stdin).unwrap(),
            (Mode::IMMEDIATE, 3)
        );
        for reference in [b.stdin, b.stdout, b.stderr] {
            t.close(CALLER, reference).unwrap();
        }
        assert!(
            s.prepare(&t, &b, CALLER, &frame(0x10, 0, 0, 0)).is_err(),
            "PRIVATE_ALIAS_NEVER_AUTHORIZES_PUBLIC"
        );
        assert_eq!(s.cleanup(&mut t, CALLER, false), Err(-13));
        assert_eq!(s.cleanup_result(), None);
        assert_eq!(s.cleanup(&mut t, CALLER, true), Ok(()));
        assert_eq!(s.cleanup_result(), Some(0));
        assert_eq!(s.cleanup(&mut t, CALLER, true), Ok(()));
    }
    #[test]
    fn mode_rejects_token_lifetime_revision_and_unsupported_before_commit() {
        let (mut t, b, mut s) = fixture();
        let mut bad = frame(0x10, 0, 0, 0);
        bad[4] ^= 1;
        assert!(matches!(s.prepare(&t, &b, CALLER, &bad), Err(-13)));
        for raw in [
            frame(0x11, 0, 1, 0),
            frame(0x11, 2, 1, 0),
            frame(0x11, 1, 2, 0),
            frame(0x11, 1, 1, 2),
        ] {
            assert!(
                s.prepare(&t, &b, CALLER, &raw).is_err(),
                "PRE_DRAIN_REVISION_VALIDATION"
            );
        }
        assert!(
            s.prepare(
                &t,
                &b,
                Caller {
                    generation: 2,
                    ..CALLER
                },
                &frame(0x10, 0, 0, 0)
            )
            .is_err()
        );
        assert_eq!(
            t.mode_state(CALLER, &b.stdin).unwrap(),
            (Mode::IMMEDIATE, 1)
        );
        t.close(CALLER, b.stdin).unwrap();
        for op in [0x10, 0x11, 0x12] {
            assert!(
                s.prepare(
                    &t,
                    &b,
                    CALLER,
                    &frame(op, if op == 0x10 { 0 } else { 1 }, 0, 0)
                )
                .is_err()
            );
        }
        s.cleanup(&mut t, CALLER, true).unwrap();
    }
    #[test]
    fn explicit_restore_is_final_and_private_cleanup_caches_stale_failure() {
        let (mut t, b, mut s) = fixture();
        let set = s.prepare(&t, &b, CALLER, &frame(0x11, 1, 1, 0)).unwrap();
        s.commit(&mut t, &b, CALLER, set).unwrap();
        let restore = s.prepare(&t, &b, CALLER, &frame(0x12, 2, 0, 0)).unwrap();
        s.commit(&mut t, &b, CALLER, restore).unwrap();
        for op in [0x11, 0x12] {
            assert!(matches!(
                s.prepare(&t, &b, CALLER, &frame(op, 3, 0, 0)),
                Err(-9)
            ));
        }
        s.cleanup(&mut t, CALLER, true).unwrap();
        let (mut t, b, mut s) = fixture();
        let mut competing = t.snapshot(CALLER, &b.stdin).unwrap();
        t.apply_now(
            CALLER,
            &b.stdin,
            &mut competing,
            ModeRequest {
                mode: Mode {
                    icrnl: true,
                    ..Mode::IMMEDIATE
                },
                action: ApplyWhen::Now,
            },
        )
        .unwrap();
        assert_eq!(s.cleanup(&mut t, CALLER, true), Err(-9));
        assert_eq!(s.cleanup_result(), Some(-9));
        assert_eq!(s.cleanup(&mut t, CALLER, true), Err(-9));
        assert_eq!(t.mode_state(CALLER, &b.stdin).unwrap().1, 2);
    }
    #[test]
    fn unknown_byte_io_blocks_client_but_not_confirmed_stop_cleanup() {
        let (mut t, b, mut s) = fixture();
        let set = s.prepare(&t, &b, CALLER, &frame(0x11, 1, 1, 0)).unwrap();
        s.commit(&mut t, &b, CALLER, set).unwrap();
        t.write(CALLER, &b.stdout, b"x", |_, _| Completion {
            count: 0,
            stop: Stop::Unknown,
        })
        .unwrap_err();
        assert!(matches!(
            s.prepare(&t, &b, CALLER, &frame(0x10, 0, 0, 0)),
            Err(-5)
        ));
        for reference in [b.stdin, b.stdout, b.stderr] {
            t.close(CALLER, reference).unwrap();
        }
        assert_eq!(
            s.cleanup(&mut t, CALLER, true),
            Ok(()),
            "TRUSTED_PRIVATE_CLEANUP_AFTER_UNKNOWN"
        );
    }
}
