// SPDX-License-Identifier: BSD-2-Clause
//! One owner-local read-only null object; caller identity comes from the connection.
#[derive(Debug, PartialEq, Eq)]
pub struct Null {
    generation: u32,
    sequence: u32,
    active: bool,
}
impl Null {
    pub fn new(generation: u32) -> Self {
        assert!((1..=255).contains(&generation));
        Self {
            generation,
            sequence: 0,
            active: false,
        }
    }
    pub fn factory(&self) -> u32 {
        0x76060000 | self.generation
    }
    pub fn reference(&self) -> u32 {
        0x79000000 | (self.generation << 8) | self.sequence
    }
    pub fn active(&self) -> bool {
        self.active
    }
    // Owner-only: call after confirmed terminal observation and stop serving this
    // connection. Normal client close remains a distinct operation.
    pub fn release_stopped(&mut self) {
        self.active = false;
    }
    pub fn request(&mut self, child: bool, frame: &[u8; 32]) -> [u8; 32] {
        let word = |n| u32::from_le_bytes(frame[n..n + 4].try_into().unwrap());
        let (op, reference, binding, count) = (word(0), word(4), word(8), word(12));
        let mut reply = [0; 32];
        let result: i32 = if !child {
            -13
        } else if binding != 3 {
            -22
        } else if op == 6 {
            if reference != self.factory() {
                -13
            } else if count != 0 || frame[16..25] != *b"/dev/null" || frame[25..] != [0; 7] {
                -22
            } else if self.active || self.sequence == 16 {
                -23
            } else {
                self.sequence += 1;
                self.active = true;
                reply[4..8].copy_from_slice(&self.reference().to_le_bytes());
                reply[8..12].copy_from_slice(&3u32.to_le_bytes());
                0
            }
        } else if !(1..=3).contains(&op) {
            -22
        } else if !self.active || reference != self.reference() {
            -9
        } else if count > 16 || (op == 3 && count != 0) || frame[16..] != [0; 16] {
            -22
        } else if op == 2 {
            -13
        } else {
            if op == 3 {
                self.active = false;
            }
            0
        };
        reply[..4].copy_from_slice(&result.to_le_bytes());
        reply
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn frame(op: u32, reference: u32, count: u32) -> [u8; 32] {
        let mut f = [0; 32];
        for (n, value) in [op, reference, 3, count].iter().enumerate() {
            f[n * 4..n * 4 + 4].copy_from_slice(&value.to_le_bytes());
        }
        if op == 6 {
            f[16..25].copy_from_slice(b"/dev/null");
        }
        f
    }
    fn result(reply: [u8; 32]) -> i32 {
        i32::from_le_bytes(reply[..4].try_into().unwrap())
    }
    #[test]
    fn authority_eof_close_stale_and_exhaustion() {
        let mut n = Null::new(1);
        let open = frame(6, n.factory(), 0);
        assert_eq!(result(n.request(false, &open)), -13);
        assert_eq!(result(n.request(true, &frame(6, n.factory() + 1, 0))), -13);
        assert!(!n.active());
        let mut old = 0;
        for _ in 0..16 {
            assert_eq!(result(n.request(true, &open)), 0);
            assert_eq!(result(n.request(true, &open)), -23);
            assert_eq!(result(n.request(true, &frame(1, old, 1))), -9);
            let handle = n.reference();
            assert_eq!(n.request(true, &frame(1, handle, 16)), [0; 32]);
            assert_eq!(result(n.request(false, &frame(1, handle, 1))), -13);
            assert_eq!(result(n.request(true, &frame(2, handle, 0))), -13);
            assert_eq!(result(n.request(true, &frame(3, handle, 0))), 0);
            assert_eq!(result(n.request(true, &frame(1, handle, 0))), -9);
            old = handle;
        }
        assert_eq!(result(n.request(true, &open)), -23);
        assert!(!n.active());
    }
    #[test]
    fn stopped_holder_release_preserves_other_generation() {
        let mut stopped = Null::new(1);
        let mut peer = Null::new(2);
        let open = frame(6, stopped.factory(), 0);
        assert_eq!(result(stopped.request(true, &open)), 0);
        let stale = stopped.reference();
        assert_eq!(result(peer.request(true, &frame(6, peer.factory(), 0))), 0);
        let live = peer.reference();
        stopped.release_stopped();
        stopped.release_stopped();
        assert!(!stopped.active());
        assert_eq!(stopped.reference(), stale);
        for op in 1..=3 {
            assert_eq!(result(stopped.request(true, &frame(op, stale, 0))), -9);
            assert_eq!(result(peer.request(true, &frame(op, stale, 0))), -9);
        }
        assert!(peer.active());
        assert_eq!(peer.request(true, &frame(1, live, 1)), [0; 32]);
    }
    #[test]
    fn invalid_frames_cannot_consume_or_publish() {
        let mut n = Null::new(2);
        let open = frame(6, n.factory(), 0);
        for offset in [8, 12, 16, 25, 31] {
            let mut bad = open;
            bad[offset] ^= 1;
            assert_eq!(result(n.request(true, &bad)), -22);
            assert!(!n.active());
        }
        assert_eq!(result(n.request(true, &open)), 0);
        let handle = n.reference();
        for (op, count) in [(1, 17), (3, 1), (4, 0)] {
            assert_eq!(result(n.request(true, &frame(op, handle, count))), -22);
            assert!(n.active());
        }
        let mut bad = frame(1, handle, 1);
        bad[31] = 1;
        assert_eq!(result(n.request(true, &bad)), -22);
        assert!(n.active());
        let mut other = Null::new(3);
        assert_eq!(
            result(other.request(true, &frame(6, other.factory(), 0))),
            0
        );
        assert_eq!(result(other.request(true, &frame(1, handle, 1))), -9);
    }
}
