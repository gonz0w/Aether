// SPDX-License-Identifier: BSD-2-Clause
use super::*;

const BOOT: [u64; 6] = [29, 0xa001, 0xf101, 0xc002, 0xd001, 0xc003];
const ENGINE: u64 = 0xb0000101;
const PROCESS: u64 = 0xb0000102;
#[derive(Default)]
struct Mock {
    fault: &'static str,
    events: Vec<&'static str>,
    channels: usize,
    input: usize,
    output: Vec<u8>,
    transfers: usize,
    reclaimed: Vec<u64>,
}
impl Mock {
    fn with(fault: &'static str) -> Self {
        Self {
            fault,
            ..Self::default()
        }
    }
}
impl Kernel for Mock {
    fn ctl(&mut self, op: u64, handle: u64) -> Status {
        match op {
            0x1fffe => (0, 0, 0),
            0x20001 if self.reclaimed.contains(&handle) => {
                if self.fault == "stale-reclaim" {
                    (0, 0, 0)
                } else {
                    (-9, 0, 0)
                }
            }
            0x20001 if handle == ENGINE && self.input < 128 => {
                self.events.push("ready");
                match self.fault {
                    "terminal-ready" => (1, 1, 1),
                    "stale-ready" => (-9, 1, 0),
                    "malformed-ready" => (0, 2, 0),
                    "never-ready" => (0, 0, 0),
                    "died-after-greeting" if self.input == 64 => (1, 1, 1),
                    _ => (0, 1, 0),
                }
            }
            0x20001 => {
                self.events.push(if handle == PROCESS {
                    "process-terminal"
                } else {
                    "engine-terminal"
                });
                match self.fault {
                    "process-wait" if handle == PROCESS => (0, 0, 0),
                    "engine-wait" if handle == ENGINE => (0, 0, 0),
                    "process-failed" if handle == PROCESS => (8, 0, 1),
                    "process-signaled" if handle == PROCESS => (144, 0, 3),
                    "engine-failed" if handle == ENGINE => (6, 1, 1),
                    "engine-signal" if handle == ENGINE => (144, 1, 3),
                    _ if handle == ENGINE => (1, 1, 1),
                    _ => (1, 0, 1),
                }
            }
            0x20002 => {
                self.events.push(if handle == PROCESS {
                    "process-reclaim"
                } else {
                    "engine-reclaim"
                });
                if self.fault == "reclaim" || (self.fault == "engine-reclaim" && handle == ENGINE) {
                    return (-16, 0, 0);
                }
                self.reclaimed.push(handle);
                (0, 0, 0)
            }
            0x24003 => {
                self.events.push(if handle == 11 {
                    "close-send"
                } else {
                    "close-receive"
                });
                if self.fault == "close-send" || (self.fault == "close-receive" && handle == 20) {
                    (-13, 0, 0)
                } else {
                    (0, 0, 0)
                }
            }
            0x26002 => {
                assert_eq!(handle, 0xf001);
                self.events.push("console-close");
                (if self.fault == "console" { -16 } else { 0 }, 0, 0)
            }
            0x2a002 => {
                assert_eq!(handle, 0xf002);
                self.events.push("halt");
                (if self.fault == "halt-return" { -16 } else { 0 }, 0, 0)
            }
            _ => panic!("unexpected operation {op:x}/{handle:x}"),
        }
    }
    fn channel(&mut self) -> Status {
        self.events.push("channel");
        self.channels += 1;
        if self.fault == "channel" {
            return (-16, 0, 0);
        }
        if self.channels == 1 || self.fault == "duplicate-channels" {
            (10, 11, 0)
        } else {
            (20, 21, 0)
        }
    }
    fn engine(&mut self, reader: u64, writer: u64) -> i64 {
        assert_eq!((reader, writer), (10, 21));
        self.events.push("engine-admit");
        if self.fault == "engine-admit" {
            -13
        } else {
            ENGINE as i64
        }
    }
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64 {
        assert_eq!(engine, ENGINE);
        assert_eq!(*region, [8, 2097152, 7]);
        self.events.push("block-delegate");
        if self.fault == "block" { -13 } else { 0 }
    }
    fn process(&mut self, args: &[u8; 272]) -> i64 {
        let mut expected = [0; 272];
        expected[0] = 1;
        expected[16] = b'p';
        assert_eq!(*args, expected);
        assert_eq!(self.input, 64);
        assert!(self.output.is_empty());
        self.events.push("process-admit");
        if self.fault == "process-admit" {
            -13
        } else {
            PROCESS as i64
        }
    }
    fn transfer(&mut self, endpoint: u64, bytes: &mut [u8], write: bool) -> i64 {
        assert!(!bytes.is_empty() && bytes.len() <= 16);
        assert_eq!(endpoint, if write { 11 } else { 20 });
        if self.input == 128 && bytes.len() == 1 {
            self.events.push(if write { "epipe" } else { "eof" });
            return if self.fault == "endpoint-live" {
                1
            } else if write {
                -32
            } else {
                0
            };
        }
        self.transfers += 1;
        if self.fault == "transfer-wait" {
            return -11;
        }
        if self.fault == "oversize" {
            return bytes.len() as i64 + 1;
        }
        if self.fault == "early-eof" {
            return 0;
        }
        if self.transfers.is_multiple_of(3) {
            return -11;
        }
        let count = bytes.len().min(7); // Real policy must retain partial offsets.
        if write {
            assert!(self.reclaimed.contains(&PROCESS));
            self.output.extend_from_slice(&bytes[..count]);
            if self.fault == "partial-send" && self.output.len() >= 32 {
                return -32;
            }
        } else {
            if self.input >= 64 {
                assert_eq!(self.output.len(), 64);
                if self.fault == "lost-reply" {
                    return -32;
                }
            }
            let mut frame = [0; 64];
            frame[..8].copy_from_slice(b"AFSRPC07");
            frame[16..24].copy_from_slice(&10u64.to_le_bytes());
            if self.input < 64 {
                frame[24..32].copy_from_slice(&1u64.to_le_bytes());
                frame[32..40].copy_from_slice(&1u64.to_le_bytes());
                frame[40..48].copy_from_slice(&3u64.to_le_bytes());
            }
            match self.fault {
                "wrong-magic" => frame[0] ^= 1,
                "old-greeting" if self.input < 64 => frame[7] = b'6',
                "future-greeting" if self.input < 64 => frame[7] = b'8',
                "old-disconnect" if self.input >= 64 => frame[7] = b'6',
                "future-disconnect" if self.input >= 64 => frame[7] = b'8',
                "wrong-generation" => frame[16] ^= 1,
                "wrong-status" => frame[8] = 5,
                "tail" => frame[63] = 1,
                "bad-root" if self.input < 64 => frame[24] = 0,
                "bad-kind" if self.input < 64 => frame[32] = 2,
                "bad-disconnect" if self.input >= 64 => frame[24] = 1,
                _ => (),
            }
            bytes[..count].copy_from_slice(&frame[self.input % 64..self.input % 64 + count]);
            self.input += count;
        }
        count as i64
    }
}
#[test]
fn settled_order_and_disconnect_bytes() {
    let mut k = Mock::default();
    assert_eq!(run(&mut k, BOOT, 5000), Err(Failed));
    let meaningful: Vec<_> = k.events.iter().copied().filter(|e| *e != "ready").collect();
    assert_eq!(
        meaningful,
        [
            "channel",
            "channel",
            "engine-admit",
            "block-delegate",
            "process-admit",
            "process-terminal",
            "process-reclaim",
            "engine-terminal",
            "eof",
            "epipe",
            "close-send",
            "close-receive",
            "engine-reclaim",
            "console-close",
            "halt"
        ]
    );
    assert_eq!(k.reclaimed, [PROCESS, ENGINE]);
    assert_eq!(&k.output[..8], b"AFSRPC07");
    assert_eq!(word(k.output.as_slice().try_into().unwrap(), 1), 4);
    assert_eq!(word(k.output.as_slice().try_into().unwrap(), 2), 10);
    assert!(k.output[24..].iter().all(|b| *b == 0));
}
#[test]
fn bootstrap_precedes_all_effects() {
    for field in 0..6 {
        let mut boot = BOOT;
        boot[field] ^= 1;
        let mut k = Mock::default();
        assert_eq!(run(&mut k, boot, 5000), Err(Failed));
        assert!(k.events.is_empty());
    }
}
#[test]
fn failures_never_halt_or_replay() {
    for fault in [
        "channel",
        "duplicate-channels",
        "engine-admit",
        "block",
        "terminal-ready",
        "stale-ready",
        "malformed-ready",
        "never-ready",
        "died-after-greeting",
        "wrong-magic",
        "old-greeting",
        "future-greeting",
        "old-disconnect",
        "future-disconnect",
        "wrong-generation",
        "wrong-status",
        "tail",
        "bad-root",
        "bad-kind",
        "oversize",
        "early-eof",
        "process-admit",
        "process-wait",
        "engine-wait",
        "transfer-wait",
        "process-failed",
        "process-signaled",
        "reclaim",
        "stale-reclaim",
        "partial-send",
        "lost-reply",
        "bad-disconnect",
        "engine-failed",
        "engine-signal",
        "endpoint-live",
        "close-send",
        "close-receive",
        "engine-reclaim",
        "console",
    ] {
        let mut k = Mock::with(fault);
        assert_eq!(run(&mut k, BOOT, 5000), Err(Failed), "{fault}");
        assert!(!k.events.contains(&"halt"), "{fault}");
        assert!(k.events.iter().filter(|e| **e == "engine-admit").count() <= 1);
        assert!(k.output.len() <= 64, "{fault}");
        if matches!(fault, "old-disconnect" | "future-disconnect") {
            assert_eq!(k.reclaimed, [PROCESS]);
            assert!(!k.events.contains(&"engine-terminal"));
            assert_eq!(k.output.len(), 64);
        }
        if matches!(
            fault,
            "terminal-ready" | "stale-ready" | "malformed-ready" | "never-ready"
        ) {
            assert_eq!(
                k.input, 0,
                "{fault}: invalid readiness must stop before greeting IO"
            );
        }
        if matches!(
            fault,
            "terminal-ready"
                | "stale-ready"
                | "malformed-ready"
                | "never-ready"
                | "died-after-greeting"
                | "wrong-generation"
                | "wrong-magic"
                | "old-greeting"
                | "future-greeting"
                | "bad-root"
                | "bad-kind"
        ) {
            assert!(!k.events.contains(&"process-admit"), "{fault}");
        }
    }
}
#[test]
fn budgets_and_returned_halt_fail_closed() {
    let mut k = Mock::with("transfer-wait");
    assert_eq!(run(&mut k, BOOT, 1_000_000), Err(Failed));
    assert_eq!(k.transfers, 100_000);
    assert!(!k.events.contains(&"process-admit"));
    let mut k = Mock::default();
    assert_eq!(run(&mut k, BOOT, 0), Err(Failed));
    assert!(!k.events.contains(&"process-admit"));
    let mut k = Mock::with("halt-return");
    assert_eq!(run(&mut k, BOOT, 5000), Err(Failed));
    assert_eq!(k.events.last(), Some(&"halt"));
}
