// SPDX-License-Identifier: BSD-2-Clause
//! Bounded volatile descriptions. The dispatcher authenticates peer identities;
//! descriptor aliases collapse to one holder per peer before close.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
struct Description {
    reference: u32,
    offset: u8,
    rights: u8,
    holders: u8,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Scratch {
    descriptions: [Description; 2],
    data: [u8; 32],
    protected: [u8; 10],
    namespace: u8,
    sequence: u8,
    length: u8,
    pub denied: u8,
    pub read: u8,
    pub written: u8,
    pub eof: bool,
}
fn word(f: &[u8; 32], i: usize) -> u32 {
    u32::from_le_bytes(f[i..i + 4].try_into().unwrap())
}
fn put(f: &mut [u8; 32], i: usize, v: u32) {
    f[i..i + 4].copy_from_slice(&v.to_le_bytes());
}
impl Scratch {
    pub fn new(namespace: u8) -> Self {
        assert!((1..=3).contains(&namespace));
        let mut data = [0; 32];
        data[..20].copy_from_slice(b"stale scratch bytes\n");
        Self {
            descriptions: [Description::default(); 2],
            data,
            protected: *b"protected\n",
            namespace,
            sequence: 0,
            length: 20,
            denied: 0,
            read: 0,
            written: 0,
            eof: false,
        }
    }
    pub fn root(&self) -> u32 {
        0x77000000 | self.namespace as u32
    }
    pub fn binding(&self, peer: usize, index: usize) -> Option<(u32, u8)> {
        let d = self.descriptions.get(index)?;
        (peer < 4 && d.holders & (1 << peer) != 0).then_some((d.reference, d.rights))
    }
    pub fn idle(&self) -> bool {
        self.descriptions.iter().all(|d| d.holders == 0)
    }
    pub fn complete(&self) -> bool {
        self.idle()
            && self.length == 2
            && self.data[..2] == *b"AB"
            && self.data[2..] == [0; 30]
            && self.protected == *b"protected\n"
            && self.denied == 1
            && self.read == 2
            && self.written == 2
            && self.eof
    }
    pub fn check(&self, peer: usize, users: &[u8; 9]) -> Result<(), i32> {
        if peer >= 4 {
            return Err(-13);
        }
        for i in 0..2 {
            if (users[7 + i] != 0) != self.binding(peer, i).is_some() {
                return Err(-13);
            }
        }
        Ok(())
    }
    pub fn inherit(&mut self, parent: usize, child: usize, users: &[u8; 9]) -> Result<(), i32> {
        self.check(parent, users)?;
        if child >= 4 || child == parent || (0..2).any(|i| self.binding(child, i).is_some()) {
            return Err(-13);
        }
        for i in 0..2 {
            if users[7 + i] != 0 {
                self.descriptions[i].holders |= 1 << child;
            }
        }
        Ok(())
    }
    pub fn commit(&mut self, peer: usize, before: &[u8; 9], after: &[u8; 9]) -> Result<(), i32> {
        self.check(peer, before)?;
        if (7..9).any(|i| after[i] > before[i]) {
            return Err(-13);
        }
        for i in 0..2 {
            if after[7 + i] == 0 {
                self.release(peer, i);
            }
        }
        Ok(())
    }
    fn release(&mut self, peer: usize, i: usize) {
        let d = &mut self.descriptions[i];
        d.holders &= !(1 << peer);
        if d.holders == 0 {
            *d = Description::default();
        }
    }
    /// Only after confirmed terminal of the dispatcher's exact peer instance.
    pub fn terminal(&mut self, peer: usize) -> Result<(), i32> {
        if peer >= 4 {
            return Err(-13);
        }
        for i in 0..2 {
            self.release(peer, i);
        }
        Ok(())
    }
    pub fn request(&mut self, peer: usize, f: &[u8; 32]) -> [u8; 32] {
        self.handle(peer, f).unwrap_or_else(|e| {
            let mut r = [0; 32];
            put(&mut r, 0, e as u32);
            r
        })
    }
    fn handle(&mut self, peer: usize, f: &[u8; 32]) -> Result<[u8; 32], i32> {
        if peer >= 4 {
            return Err(-13);
        }
        let (op, reference, binding, count) = (word(f, 0), word(f, 4), word(f, 8), word(f, 12));
        let mut r = [0; 32];
        if op == 86 {
            if reference != self.root() {
                return Err(-13);
            }
            let end = f[16..].iter().position(|&v| v == 0).ok_or(-22)?;
            if binding != 0 || f[16 + end..].iter().any(|&v| v != 0) || ![1, 14].contains(&count) {
                return Err(-22);
            }
            match &f[16..16 + end] {
                b"/inputs/denied" => {
                    self.denied = self.denied.checked_add(1).ok_or(-28)?;
                    return Err(-13);
                }
                b"/scratch/data" => {}
                _ => return Err(-2),
            }
            let i = self
                .descriptions
                .iter()
                .position(|d| d.holders == 0)
                .ok_or(-23)?;
            if self.sequence == 15 {
                return Err(-28);
            }
            self.sequence += 1;
            let id = 0x78000000
                | ((self.namespace as u32) << 16)
                | ((self.sequence as u32) << 8)
                | (i as u32 + 1);
            let rights = if count == 1 { 1 } else { 2 };
            if count == 14 {
                self.data.fill(0);
                self.length = 0;
            }
            self.descriptions[i] = Description {
                reference: id,
                offset: 0,
                rights,
                holders: 1 << peer,
            };
            put(&mut r, 4, id);
            put(&mut r, 8, 7 + i as u32);
            put(&mut r, 12, rights as u32);
            return Ok(r);
        }
        if !(1..=3).contains(&op)
            || !(7..=8).contains(&binding)
            || count > 16
            || (op == 3 && count != 0)
            || f[16 + if op == 2 { count as usize } else { 0 }..]
                .iter()
                .any(|&v| v != 0)
        {
            return Err(-22);
        }
        let i = binding as usize - 7;
        let d = self.descriptions[i];
        if d.reference != reference || d.holders & (1 << peer) == 0 {
            return Err(-9);
        }
        if op == 3 {
            self.release(peer, i);
            return Ok(r);
        }
        if d.rights != if op == 1 { 1 } else { 2 } {
            return Err(-13);
        }
        let offset = d.offset as usize;
        if cfg!(scratch_skip_read) && op == 1 {
            return Ok(r);
        }
        if op == 1 {
            let n = (count as usize).min((self.length as usize).saturating_sub(offset));
            self.read = self.read.checked_add(n as u8).ok_or(-28)?;
            self.descriptions[i].offset += n as u8;
            if n == 0 && count != 0 {
                self.eof = true;
            }
            r[16..16 + n].copy_from_slice(&self.data[offset..offset + n]);
            if cfg!(scratch_bad_read) && n != 0 {
                r[16] ^= 1;
            }
            put(&mut r, 0, n as u32);
        } else {
            let n = count as usize;
            if n > 32 - offset || self.written.checked_add(n as u8).is_none() {
                return Err(-28);
            }
            self.data[offset..offset + n].copy_from_slice(&f[16..16 + n]);
            if cfg!(scratch_lose_b) && offset == 1 && n == 1 {
                self.data[1] = 0;
            }
            self.descriptions[i].offset += n as u8;
            self.length = self.length.max((offset + n) as u8);
            self.written += n as u8;
            put(&mut r, 0, n as u32);
        }
        Ok(r)
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn open(s: &Scratch, path: &[u8], mode: u32) -> [u8; 32] {
        let mut f = [0; 32];
        put(&mut f, 0, 86);
        put(&mut f, 4, s.root());
        put(&mut f, 12, mode);
        f[16..16 + path.len()].copy_from_slice(path);
        f
    }
    fn io(op: u32, r: &[u8; 32], bytes: &[u8], n: u32) -> [u8; 32] {
        let mut f = [0; 32];
        put(&mut f, 0, op);
        put(&mut f, 4, word(r, 4));
        put(&mut f, 8, word(r, 8));
        put(&mut f, 12, n);
        f[16..16 + bytes.len()].copy_from_slice(bytes);
        f
    }
    fn code(r: [u8; 32]) -> i32 {
        word(&r, 0) as i32
    }
    #[test]
    fn write_reopen_eof_and_denial() {
        let mut s = Scratch::new(1);
        let r = s.request(0, &open(&s, b"/scratch/data", 14));
        assert_eq!(code(s.request(0, &io(2, &r, b"A", 1))), 1);
        assert_eq!(code(s.request(0, &io(2, &r, b"B", 1))), 1);
        assert_eq!(code(s.request(0, &io(3, &r, b"", 0))), 0);
        assert_eq!(code(s.request(1, &open(&s, b"/inputs/denied", 14))), -13);
        let r = s.request(1, &open(&s, b"/scratch/data", 1));
        let got = s.request(1, &io(1, &r, b"", 16));
        assert_eq!(&got[16..18], b"AB");
        assert_eq!(word(&got, 0), 2);
        assert_eq!(code(s.request(1, &io(1, &r, b"", 16))), 0);
        s.terminal(1).unwrap();
        assert!(s.complete());
        assert!(core::mem::size_of::<Scratch>() <= 80);
    }
    #[test]
    fn holders_alias_counts_and_exec_release() {
        let mut s = Scratch::new(1);
        let r = s.request(0, &open(&s, b"/scratch/data", 14));
        let mut users = [0; 9];
        users[7] = 2;
        s.inherit(0, 1, &users).unwrap();
        let mut after = users;
        after[7] = 1;
        s.commit(0, &users, &after).unwrap();
        s.terminal(0).unwrap();
        assert_eq!(code(s.request(1, &io(2, &r, b"B", 1))), 1);
        assert_eq!(code(s.request(0, &io(2, &r, b"A", 1))), -9);
        s.commit(1, &users, &[0; 9]).unwrap();
        assert!(s.idle());
    }
    #[test]
    fn foreign_stale_typed_refs_and_namespace() {
        let mut s = Scratch::new(1);
        let old = s.request(0, &open(&s, b"/scratch/data", 14));
        assert_eq!(code(s.request(1, &io(2, &old, b"X", 1))), -9);
        s.terminal(0).unwrap();
        let new = s.request(0, &open(&s, b"/scratch/data", 14));
        let before = s.clone();
        assert_ne!(word(&old, 4), word(&new, 4));
        assert_eq!(code(s.request(0, &io(2, &old, b"X", 1))), -9);
        assert_eq!(s, before);
        let mut f = io(2, &new, b"X", 1);
        put(&mut f, 4, 0x79000101);
        assert_eq!(code(s.request(0, &f)), -9);
        assert_eq!(s, before);
        let mut fresh = Scratch::new(2);
        assert_eq!(code(fresh.request(0, &io(2, &new, b"X", 1))), -9);
    }
    #[test]
    fn truncate_under_live_reader_returns_eof_without_offset_underflow() {
        let mut s = Scratch::new(1);
        let reader = s.request(0, &open(&s, b"/scratch/data", 1));
        assert_eq!(code(s.request(0, &io(1, &reader, b"", 16))), 16);
        let writer = s.request(1, &open(&s, b"/scratch/data", 14));
        assert_eq!(code(writer), 0);
        assert_eq!(code(s.request(0, &io(1, &reader, b"", 16))), 0);
        assert_eq!(code(s.request(1, &io(2, &writer, b"AB", 2))), 2);
        assert_eq!(code(s.request(0, &io(1, &reader, b"", 16))), 0);
    }
    #[test]
    fn exhaustion_rejects_before_truncate() {
        let mut s = Scratch::new(1);
        for _ in 0..15 {
            let r = s.request(0, &open(&s, b"/scratch/data", 1));
            assert_eq!(code(r), 0);
            s.terminal(0).unwrap();
        }
        let before = s.clone();
        assert_eq!(code(s.request(0, &open(&s, b"/scratch/data", 14))), -28);
        assert_eq!(s, before);
    }
    #[test]
    fn malformed_and_rights_do_not_mutate() {
        let mut s = Scratch::new(1);
        let f = open(&s, b"/scratch/data", 1);
        for offset in [4, 8, 12, 31] {
            let mut bad = f;
            bad[offset] ^= 1;
            let before = s.clone();
            assert!(code(s.request(0, &bad)) < 0);
            assert_eq!(s, before);
        }
        let r = s.request(0, &f);
        let before = s.clone();
        assert_eq!(code(s.request(0, &io(2, &r, b"X", 1))), -13);
        assert_eq!(s, before);
        assert_eq!(code(s.request(4, &f)), -13);
        assert_eq!(s, before);
    }
}
