// SPDX-License-Identifier: BSD-2-Clause
//! Bounded scratch backend. Expose only on the delegated owner's connection.
//! Offsets and alias holders belong to the connections owner, not this backend.
#[derive(Debug, PartialEq, Eq)]
pub struct Scratch {
    generation: u32,
    name: [u8; 16],
    data: [u8; 64],
    length: usize,
    sequence: [u32; 2],
    mode: [u32; 2],
}
fn word(frame: &[u8; 32], offset: usize) -> u32 {
    u32::from_le_bytes(frame[offset..offset + 4].try_into().unwrap())
}
fn put(frame: &mut [u8; 32], offset: usize, value: u32) {
    frame[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
}
impl Scratch {
    pub fn new(generation: u32) -> Self {
        assert!((1..=255).contains(&generation));
        Self {
            generation,
            name: [0; 16],
            data: [0; 64],
            length: 0,
            sequence: [0; 2],
            mode: [0; 2],
        }
    }
    pub fn root(&self) -> u32 {
        0xfb000000 | self.generation
    }
    fn handle(&self, slot: usize) -> u32 {
        0xfa000000 | (self.generation << 16) | (self.sequence[slot] << 8) | (slot as u32 + 1)
    }
    pub fn is_closed(&self) -> bool {
        self.mode == [0; 2]
    }
    pub fn request(&mut self, frame: &[u8; 32]) -> [u8; 32] {
        let mut reply = [0; 32];
        let result = self.apply(frame, &mut reply);
        put(&mut reply, 0, result as u32);
        reply
    }
    fn apply(&mut self, frame: &[u8; 32], reply: &mut [u8; 32]) -> i32 {
        let (op, reference, offset, count) = (
            word(frame, 0),
            word(frame, 4),
            word(frame, 8),
            word(frame, 12),
        );
        if op == 1 {
            if reference != self.root() {
                return -13;
            }
            if offset != 0 {
                return -22;
            }
            if count != 1 && count != 14 {
                return -95;
            }
            let Some(end) = frame[16..].iter().position(|b| *b == 0) else {
                return -22;
            };
            if frame[16 + end..].iter().any(|b| *b != 0) {
                return -22;
            }
            let name = &frame[16..16 + end];
            if name != b"/scratch/leak" && name != b"/scratch/data" {
                return if name == b"/inputs/denied" { -13 } else { -2 };
            }
            let exists = self.name[0] != 0;
            let matches = self.name == frame[16..];
            if count == 1 && !matches {
                return -2;
            }
            if count == 14 && exists && !matches {
                return -28;
            }
            let Some(slot) = (0..2).find(|i| self.mode[*i] == 0 && self.sequence[*i] < 3) else {
                return -23;
            };
            // Reserve before any mutation: ENFILE must never truncate existing bytes.
            self.sequence[slot] += 1;
            self.mode[slot] = count;
            if count == 14 {
                self.name.copy_from_slice(&frame[16..]);
                self.data.fill(0);
                self.length = 0;
            }
            put(reply, 4, self.handle(slot));
            put(reply, 8, self.length as u32);
            return 0;
        }
        if !(2..=4).contains(&op) {
            return -95;
        }
        let Some(slot) = (0..2).find(|i| self.mode[*i] != 0 && self.handle(*i) == reference) else {
            return -9;
        };
        if op == 3 {
            if frame[8..].iter().any(|b| *b != 0) {
                return -22;
            }
            self.mode[slot] = 0;
            return 0;
        }
        if count > 16 {
            return -22;
        }
        let count = count as usize;
        if frame[16 + if op == 2 { 0 } else { count }..]
            .iter()
            .any(|b| *b != 0)
        {
            return -22;
        }
        if (op == 2 && self.mode[slot] != 1) || (op == 4 && self.mode[slot] != 14) {
            return -13;
        }
        if op == 2 {
            let start = (offset as usize).min(self.length);
            let count = count.min(self.length - start);
            reply[16..16 + count].copy_from_slice(&self.data[start..start + count]);
            return count as i32;
        }
        if offset > 64 || count > 64 - offset as usize {
            return -28;
        }
        if count != 0 {
            let start = offset as usize;
            if start > self.length {
                self.data[self.length..start].fill(0);
            }
            self.data[start..start + count].copy_from_slice(&frame[16..16 + count]);
            self.length = self.length.max(start + count);
        }
        count as i32
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn frame(op: u32, handle: u32, offset: u32, count: u32, data: &[u8]) -> [u8; 32] {
        let mut f = [0; 32];
        for (i, value) in [op, handle, offset, count].into_iter().enumerate() {
            put(&mut f, 4 * i, value);
        }
        f[16..16 + data.len()].copy_from_slice(data);
        f
    }
    fn open(s: &mut Scratch, mode: u32) -> u32 {
        let r = s.request(&frame(1, s.root(), 0, mode, b"/scratch/data"));
        assert_eq!(word(&r, 0), 0);
        word(&r, 4)
    }
    fn reject(s: &mut Scratch, f: [u8; 32], error: i32) {
        let before = format!("{s:?}");
        let r = s.request(&f);
        assert_eq!(word(&r, 0) as i32, error);
        assert_eq!(r[4..], [0; 28]);
        assert_eq!(before, format!("{s:?}"));
    }
    #[test]
    fn write_close_reopen_and_read_bounds() {
        let mut s = Scratch::new(1);
        let h = open(&mut s, 14);
        assert_eq!(word(&s.request(&frame(4, h, 0, 2, b"AB")), 0), 2);
        assert_eq!(word(&s.request(&frame(3, h, 0, 0, b"")), 0), 0);
        assert!(s.is_closed());
        let h = open(&mut s, 1);
        let r = s.request(&frame(2, h, 0, 16, b""));
        assert_eq!(word(&r, 0), 2);
        assert_eq!(&r[16..18], b"AB");
        assert_eq!(r[18..], [0; 14]);
        assert_eq!(word(&s.request(&frame(2, h, u32::MAX, 16, b"")), 0), 0);
        assert_eq!(word(&s.request(&frame(2, h, 1, 16, b"")), 0), 1);
    }
    #[test]
    fn exhaustion_cannot_truncate() {
        let mut s = Scratch::new(1);
        let h = open(&mut s, 14);
        s.request(&frame(4, h, 0, 2, b"AB"));
        let read = open(&mut s, 1);
        let root = s.root();
        reject(&mut s, frame(1, root, 0, 14, b"/scratch/data"), -23);
        let r = s.request(&frame(2, read, 0, 16, b""));
        assert_eq!(&r[16..18], b"AB");
    }
    #[test]
    fn rights_and_invalid_requests_preserve_state() {
        let mut s = Scratch::new(1);
        let root = s.root();
        reject(&mut s, frame(1, root ^ 1, 0, 14, b"/scratch/data"), -13);
        reject(&mut s, frame(1, root, 0, 14, b"/inputs/denied"), -13);
        reject(&mut s, frame(1, root, 0, 1, b"/scratch/data"), -2);
        reject(&mut s, frame(1, root, 0, 3, b"/scratch/data"), -95);
        reject(&mut s, frame(1, root, 0, 14, b"/scratch/data\0x"), -22);
        reject(&mut s, frame(1, root, 0, 14, b"0123456789abcdef"), -22);
        let write = open(&mut s, 14);
        let read = open(&mut s, 1);
        reject(&mut s, frame(2, write, 0, 1, b""), -13);
        reject(&mut s, frame(4, read, 0, 1, b"X"), -13);
        reject(&mut s, frame(4, write, 0, u32::MAX, b""), -22);
        reject(&mut s, frame(4, write, u32::MAX, 1, b"X"), -28);
        reject(&mut s, frame(4, write, 0, 1, b"XY"), -22);
        reject(&mut s, frame(2, read, 0, 1, b"X"), -22);
        reject(&mut s, frame(3, write, 1, 0, b""), -22);
        reject(&mut s, frame(5, write, 0, 0, b""), -95);
        reject(&mut s, frame(1, root, 0, 14, b"/scratch/leak"), -28);
    }
    #[test]
    fn holes_zero_writes_and_successful_truncation() {
        let mut s = Scratch::new(1);
        let write = open(&mut s, 14);
        s.request(&frame(4, write, 4, 1, b"X"));
        let read = open(&mut s, 1);
        let r = s.request(&frame(2, read, 0, 16, b""));
        assert_eq!(word(&r, 0), 5);
        assert_eq!(&r[16..21], b"\0\0\0\0X");
        assert_eq!(word(&s.request(&frame(4, write, 64, 0, b"")), 0), 0);
        assert_eq!(s.length, 5);
        reject(&mut s, frame(4, write, 64, 1, b"X"), -28);
        s.request(&frame(3, write, 0, 0, b""));
        open(&mut s, 14);
        assert_eq!(word(&s.request(&frame(2, read, 0, 16, b"")), 0), 0);
        assert_eq!(s.data, [0; 64]);
    }
    #[test]
    fn stale_handles_and_retired_slots_never_reopen() {
        let mut s = Scratch::new(1);
        let mut old = 0;
        for _ in 0..6 {
            let h = open(&mut s, 14);
            reject(&mut s, frame(4, old, 0, 1, b"X"), -9);
            s.request(&frame(3, h, 0, 0, b""));
            reject(&mut s, frame(3, h, 0, 0, b""), -9);
            old = h;
        }
        assert!(s.is_closed());
        let root = s.root();
        reject(&mut s, frame(1, root, 0, 14, b"/scratch/data"), -23);
    }
    #[test]
    fn replacement_rejects_old_authority_and_starts_empty() {
        let mut old = Scratch::new(1);
        let h = open(&mut old, 14);
        old.request(&frame(4, h, 0, 6, b"secret"));
        let mut s = Scratch::new(2);
        reject(&mut s, frame(1, old.root(), 0, 14, b"/scratch/data"), -13);
        reject(&mut s, frame(2, h, 0, 6, b""), -9);
        let root = s.root();
        reject(&mut s, frame(1, root, 0, 1, b"/scratch/data"), -2);
        let new = open(&mut s, 14);
        assert_ne!(new, h);
        assert_eq!(s.data, [0; 64]);
        assert_eq!(s.length, 0);
    }
}
