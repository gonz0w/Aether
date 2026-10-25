// SPDX-License-Identifier: BSD-2-Clause
//! Private open descriptions. Caller authenticates the parent/child connection.
//! Local aliases must be collapsed to a single holder before calling close.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Description {
    backend: u32,
    mode: u32,
    offset: u32,
    sequence: u32,
    held: [bool; 2],
}
const EMPTY: Description = Description {
    backend: 0,
    mode: 0,
    offset: 0,
    sequence: 0,
    held: [false; 2],
};
#[derive(Debug, PartialEq, Eq)]
pub struct Owner {
    generation: u32,
    peers: [u32; 2],
    sequence: u32,
    descriptions: [Description; 2],
    poisoned: bool,
}
fn word(b: &[u8; 32], i: usize) -> u32 {
    u32::from_le_bytes(b[i..i + 4].try_into().unwrap())
}
fn request(op: u32, handle: u32, offset: u32, count: u32, bytes: &[u8]) -> [u8; 32] {
    let mut b = [0; 32];
    for (i, v) in [op, handle, offset, count].iter().enumerate() {
        b[i * 4..i * 4 + 4].copy_from_slice(&v.to_le_bytes());
    }
    b[16..16 + bytes.len()].copy_from_slice(bytes);
    b
}
impl Owner {
    pub fn new(generation: u32) -> Self {
        assert!((1..=255).contains(&generation));
        Self {
            generation,
            peers: [generation, 0],
            sequence: 0,
            descriptions: [EMPTY; 2],
            poisoned: false,
        }
    }
    /// The caller selects peer from the authenticated connection.
    pub fn root(&self, peer: usize) -> Option<u32> {
        (peer < 2 && self.peers[peer] != 0).then(|| {
            0xfd000000 | (self.generation << 16) | (self.peers[peer] << 8) | (peer as u32 + 1)
        })
    }
    pub fn gateway(
        &mut self,
        peer: usize,
        frame: &[u8; 32],
        rpc: &mut impl FnMut(&[u8; 32]) -> Option<[u8; 32]>,
    ) -> [u8; 32] {
        let result = self.gateway_request(peer, frame, rpc);
        match result {
            Ok(reply) => reply,
            Err(error) => request(error as u32, 0, 0, 0, &[]),
        }
    }
    fn gateway_request(
        &mut self,
        peer: usize,
        frame: &[u8; 32],
        rpc: &mut impl FnMut(&[u8; 32]) -> Option<[u8; 32]>,
    ) -> Result<[u8; 32], i32> {
        if self.poisoned {
            return Err(-5);
        }
        let root = self.root(peer).ok_or(-13)?;
        let (op, reference, binding, count) = (
            word(frame, 0),
            word(frame, 4),
            word(frame, 8),
            word(frame, 12),
        );
        if op == 6 {
            if reference != root {
                return Err(-13);
            }
            if binding != 0 {
                return Err(-22);
            }
            let end = frame[16..].iter().position(|v| *v == 0).ok_or(-22)?;
            if frame[16 + end..].iter().any(|v| *v != 0) {
                return Err(-22);
            }
            let h = self.open(peer, &frame[16..16 + end], count, rpc)?;
            return Ok(request(0, h, (h & 7) + 2, 0, &[]));
        }
        if !(1..=3).contains(&op)
            || !(3..=4).contains(&binding)
            || (reference & 7) + 2 != binding
            || count > 16
            || (op == 3 && count != 0)
            || frame[16 + if op == 2 { count as usize } else { 0 }..]
                .iter()
                .any(|v| *v != 0)
        {
            return Err(-22);
        }
        if op == 3 {
            self.close(peer, reference, rpc)?;
            Ok([0; 32])
        } else {
            self.io(
                peer,
                reference,
                if op == 1 { 2 } else { 4 },
                count,
                if op == 2 {
                    &frame[16..16 + count as usize]
                } else {
                    &[]
                },
                rpc,
            )
        }
    }
    pub fn closed(&self) -> bool {
        self.descriptions.iter().all(|d| d.held == [false; 2])
    }
    pub fn poisoned(&self) -> bool {
        self.poisoned
    }
    fn reference(&self, slot: usize, peer: usize) -> u32 {
        0xfc000000
            | (self.generation << 16)
            | (self.peers[peer] << 8)
            | (self.descriptions[slot].sequence << 4)
            | ((peer as u32) << 3)
            | (slot as u32 + 1)
    }
    fn find(&self, peer: usize, reference: u32) -> Result<usize, i32> {
        if self.poisoned {
            return Err(-5);
        }
        if peer >= 2 {
            return Err(-13);
        }
        (0..2)
            .find(|i| self.descriptions[*i].held[peer] && self.reference(*i, peer) == reference)
            .ok_or(-9)
    }
    fn exchange(
        &mut self,
        frame: &[u8; 32],
        rpc: &mut impl FnMut(&[u8; 32]) -> Option<[u8; 32]>,
    ) -> Result<[u8; 32], i32> {
        if self.poisoned {
            return Err(-5);
        }
        let Some(reply) = rpc(frame) else {
            return self.uncertain();
        };
        let status = word(&reply, 0) as i32;
        if status < 0 {
            if !matches!(status, -2 | -9 | -13 | -22 | -23 | -28 | -95) || reply[4..] != [0; 28] {
                return self.uncertain();
            }
            return Err(status);
        }
        Ok(reply)
    }
    fn uncertain<T>(&mut self) -> Result<T, i32> {
        self.poisoned = true;
        Err(-5)
    }
    pub fn open(
        &mut self,
        peer: usize,
        name: &[u8],
        mode: u32,
        rpc: &mut impl FnMut(&[u8; 32]) -> Option<[u8; 32]>,
    ) -> Result<u32, i32> {
        if self.poisoned {
            return Err(-5);
        }
        if peer >= 2 || self.peers[peer] == 0 {
            return Err(-13);
        }
        if mode != 1 && mode != 14 {
            return Err(-95);
        }
        if name.len() >= 16 || name.contains(&0) {
            return Err(-22);
        }
        let slot = (0..2)
            .find(|i| self.descriptions[*i].held == [false; 2])
            .ok_or(-23)?;
        if self.sequence == 6 {
            return Err(-23);
        }
        let reply = self.exchange(
            &request(1, 0xfb000000 | self.generation, 0, mode, name),
            rpc,
        )?;
        let handle = word(&reply, 4);
        let base = 0xfa000000 | (self.generation << 16);
        let valid_handle =
            (1..=3).any(|seq| (1..=2).any(|slot| handle == base | (seq << 8) | slot));
        if word(&reply, 0) != 0
            || !valid_handle
            || word(&reply, 8) > 64
            || (mode == 14 && word(&reply, 8) != 0)
            || reply[12..] != [0; 20]
            || self
                .descriptions
                .iter()
                .any(|d| d.held != [false; 2] && d.backend == handle)
        {
            return self.uncertain();
        }
        self.sequence += 1;
        self.descriptions[slot] = Description {
            backend: handle,
            mode,
            offset: 0,
            sequence: self.sequence,
            held: [peer == 0, peer == 1],
        };
        Ok(self.reference(slot, peer))
    }
    /// Owner-only after validating the frozen FD snapshot and process admission.
    pub fn inherit(
        &mut self,
        generation: u32,
        parent: [Option<u32>; 2],
    ) -> Result<[Option<u32>; 2], i32> {
        if self.poisoned {
            return Err(-5);
        }
        if generation <= self.peers[1]
            || generation > 255
            || self.descriptions.iter().any(|d| d.held[1])
        {
            return Err(-22);
        }
        for (i, supplied) in parent.iter().enumerate() {
            let expected = self.descriptions[i].held[0].then(|| self.reference(i, 0));
            if *supplied != expected {
                return Err(-13);
            }
        }
        self.peers[1] = generation;
        let mut child = [None; 2];
        for (i, item) in child.iter_mut().enumerate() {
            if self.descriptions[i].held[0] {
                self.descriptions[i].held[1] = true;
                *item = Some(self.reference(i, 1));
            }
        }
        Ok(child)
    }
    /// Called only after authenticated parent freeze and successful native child
    /// admission. Stream holder validation belongs to that caller. No RPC occurs
    /// here: validate the unchanged snapshot before the single holder transition.
    #[cfg(any(shell_files, test))]
    pub fn inherit_files(
        &mut self,
        generation: u32,
        table: &[u8; 64],
        users: &[u8; 5],
        parent: [Option<u32>; 2],
    ) -> Result<[u8; 32], i32> {
        if self.poisoned {
            return Err(-5);
        }
        // Only use validation: fork keeps even the aliases marked CLOEXEC.
        exec_fds::prepare_files(table, users).map_err(|_| -22)?;
        for (slot, description) in self.descriptions.iter().enumerate() {
            if (users[slot + 3] != 0) != description.held[0] {
                return Err(-13);
            }
        }
        let child = self.inherit(generation, parent)?;
        let mut grant = [0; 32];
        grant[..8].copy_from_slice(b"AESFC001");
        for (i, value) in [
            self.root(1).unwrap(),
            generation,
            child[0].unwrap_or(0),
            child[1].unwrap_or(0),
        ]
        .iter()
        .enumerate()
        {
            grant[8 + i * 4..12 + i * 4].copy_from_slice(&value.to_le_bytes());
        }
        Ok(grant)
    }
    /// Encode only this peer's current holders for a validated survivor table.
    /// The caller freezes the peer and keeps ownership serialized until delivery.
    #[cfg(any(shell_files, test))]
    pub fn describe_files(&self, peer: usize, users: &[u8; 2]) -> Result<[u8; 32], i32> {
        if self.poisoned {
            return Err(-5);
        }
        if self.root(peer).is_none() {
            return Err(-13);
        }
        if users.iter().map(|n| *n as usize).sum::<usize>() > 16 {
            return Err(-22);
        }
        let mut records = [0; 32];
        for (slot, description) in self.descriptions.iter().enumerate() {
            if (users[slot] != 0) != description.held[peer] {
                return Err(-13);
            }
            if users[slot] != 0 {
                for (i, value) in [
                    self.reference(slot, peer),
                    description.mode,
                    users[slot] as u32,
                ]
                .iter()
                .enumerate()
                {
                    records[slot * 16 + i * 4..slot * 16 + i * 4 + 4]
                        .copy_from_slice(&value.to_le_bytes());
                }
            }
        }
        Ok(records)
    }
    pub fn io(
        &mut self,
        peer: usize,
        reference: u32,
        op: u32,
        count: u32,
        bytes: &[u8],
        rpc: &mut impl FnMut(&[u8; 32]) -> Option<[u8; 32]>,
    ) -> Result<[u8; 32], i32> {
        let slot = self.find(peer, reference)?;
        if count > 16
            || (op != 2 && op != 4)
            || (op == 2 && !bytes.is_empty())
            || (op == 4 && bytes.len() != count as usize)
        {
            return Err(-22);
        }
        let d = self.descriptions[slot];
        if (op == 2 && d.mode != 1) || (op == 4 && d.mode != 14) {
            return Err(-13);
        }
        let reply = self.exchange(&request(op, d.backend, d.offset, count, bytes), rpc)?;
        let used = word(&reply, 0);
        if used > count
            || reply[4..16] != [0; 12]
            || reply[16 + if op == 2 { used as usize } else { 0 }..]
                .iter()
                .any(|v| *v != 0)
            || used > 64 - d.offset
        {
            return self.uncertain();
        }
        if !cfg!(scratch_owner_drop_offset) {
            self.descriptions[slot].offset += used;
        }
        Ok(reply)
    }
    pub fn close(
        &mut self,
        peer: usize,
        reference: u32,
        rpc: &mut impl FnMut(&[u8; 32]) -> Option<[u8; 32]>,
    ) -> Result<(), i32> {
        let slot = self.find(peer, reference)?;
        let d = self.descriptions[slot];
        if cfg!(scratch_owner_early_close) || !d.held[1 - peer] {
            let reply = self.exchange(&request(3, d.backend, 0, 0, &[]), rpc)?;
            if reply != [0; 32] {
                return self.uncertain();
            }
        }
        self.descriptions[slot].held[peer] = false;
        Ok(())
    }
}
#[cfg(test)]
#[path = "../native-files/scratch.rs"]
mod backend;
#[cfg(any(shell_files, test))]
#[path = "exec_fds.rs"]
mod exec_fds;
#[cfg(test)]
mod tests {
    use super::*;
    fn open(o: &mut Owner, b: &mut backend::Scratch, mode: u32) -> u32 {
        o.open(0, b"/scratch/data", mode, &mut |f| Some(b.request(f)))
            .unwrap()
    }
    fn write(o: &mut Owner, b: &mut backend::Scratch, peer: usize, h: u32, bytes: &[u8]) {
        let r = o
            .io(peer, h, 4, bytes.len() as u32, bytes, &mut |f| {
                Some(b.request(f))
            })
            .unwrap();
        assert_eq!(word(&r, 0), bytes.len() as u32);
    }
    fn read(o: &mut Owner, b: &mut backend::Scratch, h: u32, n: u32) -> Vec<u8> {
        let r = o.io(0, h, 2, n, &[], &mut |f| Some(b.request(f))).unwrap();
        r[16..16 + word(&r, 0) as usize].to_vec()
    }
    fn close(o: &mut Owner, b: &mut backend::Scratch, peer: usize, h: u32) {
        o.close(peer, h, &mut |f| Some(b.request(f))).unwrap();
    }
    fn fork_table() -> [u8; 64] {
        let mut table = [0; 64];
        table[..12].copy_from_slice(&[0, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0]);
        table[36..40].copy_from_slice(&[3, 0, 1, 0]);
        table[40..44].copy_from_slice(&[0, 1, 1, 0]);
        table[44..48].copy_from_slice(&[3, 1, 1, 0]);
        table[60..64].copy_from_slice(&[4, 1, 1, 0]);
        table
    }
    #[test]
    fn replacement_records_use_only_live_peer_holders() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let writer = open(&mut o, &mut b, 14);
        assert_eq!(o.describe_files(1, &[1, 0]), Err(-13));
        o.inherit(7, [Some(writer), None]).unwrap();
        close(&mut o, &mut b, 0, writer);
        let records = o.describe_files(1, &[2, 0]).unwrap();
        assert_eq!(word(&records, 0), 0xfc010719);
        assert_eq!(word(&records, 4), 14);
        assert_eq!(word(&records, 8), 2);
        assert_eq!(&records[12..], &[0; 20]);
        let before = format!("{o:?}");
        for (peer, users, error) in [
            (0, [1, 0], -13),
            (2, [1, 0], -13),
            (1, [0, 0], -13),
            (1, [1, 1], -13),
            (1, [17, 0], -22),
        ] {
            assert_eq!(o.describe_files(peer, &users), Err(error));
            assert_eq!(format!("{o:?}"), before);
        }
        close(&mut o, &mut b, 1, word(&records, 0));
        assert_eq!(o.describe_files(1, &[0, 0]), Ok([0; 32]));
        assert!(b.is_closed());
        o.poisoned = true;
        assert_eq!(o.describe_files(1, &[0, 0]), Err(-5));
    }
    #[test]
    fn fork_grant_keeps_cloexec_aliases_and_shared_lifetime() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let writer = open(&mut o, &mut b, 14);
        write(&mut o, &mut b, 0, writer, b"A");
        let reader = open(&mut o, &mut b, 1);
        let table = fork_table();
        let grant = o
            .inherit_files(7, &table, &[2, 1, 1, 2, 1], [Some(writer), Some(reader)])
            .unwrap();
        assert_eq!(&grant[..8], b"AESFC001");
        assert_eq!(word(&grant, 8), 0xfd010702);
        assert_eq!(word(&grant, 12), 7);
        assert_eq!(word(&grant, 16), 0xfc010719);
        assert_eq!(word(&grant, 20), 0xfc01072a);
        assert_eq!(&grant[24..], &[0; 8]);
        assert_eq!(table, fork_table());
        // Even the reader whose only alias has CLOEXEC is inherited by fork.
        assert!(o.descriptions.iter().all(|d| d.held == [true, true]));
        close(&mut o, &mut b, 0, writer);
        close(&mut o, &mut b, 0, reader);
        assert!(!b.is_closed());
        write(&mut o, &mut b, 1, word(&grant, 16), b"B");
        let reply = o
            .io(1, word(&grant, 20), 2, 2, &[], &mut |f| Some(b.request(f)))
            .unwrap();
        assert_eq!(&reply[16..18], b"AB");
        close(&mut o, &mut b, 1, word(&grant, 16));
        close(&mut o, &mut b, 1, word(&grant, 20));
        assert!(o.closed() && b.is_closed());
    }
    #[test]
    fn fork_grant_rejects_invalid_snapshot_without_owner_mutation() {
        for case in 0..14 {
            let mut o = Owner::new(1);
            let mut b = backend::Scratch::new(1);
            let writer = open(&mut o, &mut b, 14);
            let reader = open(&mut o, &mut b, 1);
            let mut table = fork_table();
            let mut users = [2, 1, 1, 2, 1];
            let mut refs = [Some(writer), Some(reader)];
            let mut generation = 7;
            let expected = match case {
                0 => {
                    users[3] = 1;
                    -22
                }
                1 => {
                    table[37] = 2;
                    -22
                }
                2 => {
                    table[38] = 2;
                    -22
                }
                3 => {
                    table[39] = 1;
                    -22
                }
                4 => {
                    table[36] = 5;
                    -22
                }
                5 => {
                    table[16] = 1;
                    -22
                }
                6 => {
                    table[60..64].fill(0);
                    users[4] = 0;
                    -13
                }
                7 => {
                    refs[0] = Some(writer ^ 0x10000);
                    -13
                }
                8 => {
                    refs[1] = None;
                    -13
                }
                9 => {
                    generation = 0;
                    -22
                }
                10 => {
                    generation = 256;
                    -22
                }
                11 => {
                    o.inherit_files(7, &table, &users, refs).unwrap();
                    -22
                }
                12 => {
                    o.poisoned = true;
                    -5
                }
                13 => {
                    close(&mut o, &mut b, 0, reader);
                    refs[1] = None;
                    -13
                }
                _ => unreachable!(),
            };
            let before = format!("{o:?}");
            assert_eq!(
                o.inherit_files(generation, &table, &users, refs),
                Err(expected)
            );
            assert_eq!(format!("{o:?}"), before, "case {case}");
        }
    }
    #[test]
    fn fork_grant_empty_slots_and_retired_generation_have_no_authority() {
        let mut o = Owner::new(6);
        let mut b = backend::Scratch::new(6);
        let writer = open(&mut o, &mut b, 14);
        close(&mut o, &mut b, 0, writer);
        let grant = o.inherit_files(7, &[0; 64], &[0; 5], [None; 2]).unwrap();
        assert_eq!(word(&grant, 8), 0xfd060702);
        assert_eq!(&grant[16..], &[0; 16]);
        assert!(o.closed() && b.is_closed());
        for generation in [0, 6, 7, 256] {
            let before = format!("{o:?}");
            assert_eq!(
                o.inherit_files(generation, &[0; 64], &[0; 5], [None; 2]),
                Err(-22)
            );
            assert_eq!(format!("{o:?}"), before);
        }
        let next = o.inherit_files(8, &[0; 64], &[0; 5], [None; 2]).unwrap();
        assert_eq!(word(&next, 8), 0xfd060802);
        assert_eq!(&next[16..], &[0; 16]);
        assert_eq!(
            o.io(1, writer, 4, 0, &[], &mut |_| panic!(
                "stale backend access"
            )),
            Err(-9)
        );
    }
    #[test]
    fn exec_plan_releases_only_child_last_alias_and_denial_preserves_holders() {
        for flags in 0..4 {
            let mut o = Owner::new(1);
            let mut b = backend::Scratch::new(1);
            let writer = open(&mut o, &mut b, 14);
            write(&mut o, &mut b, 0, writer, b"A");
            let reader = open(&mut o, &mut b, 1);
            let child = o.inherit(2, [Some(writer), Some(reader)]).unwrap();
            let mut table = [0; 64];
            table[..12].copy_from_slice(&[0, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0]);
            table[36..40].copy_from_slice(&[3, flags & 1, 1, 0]);
            table[40..44].copy_from_slice(&[0, 1, 1, 0]);
            table[44..48].copy_from_slice(&[3, flags >> 1, 1, 0]);
            table[48..52].copy_from_slice(&[4, 1, 1, 0]);
            let original = table;
            let before = o.descriptions;
            // A denied admission discards this candidate without any close RPC.
            let denied = exec_fds::prepare_files(&table, &[2, 1, 1, 2, 1]).unwrap();
            drop(denied);
            assert_eq!(table, original);
            assert_eq!(o.descriptions, before);
            assert!(o.descriptions.iter().all(|d| d.held == [true, true]));
            let plan = exec_fds::prepare_files(&table, &[2, 1, 1, 2, 1]).unwrap();
            assert_eq!(&plan.table[40..44], &[0; 4]);
            assert!(!plan.release[0]);
            for slot in 0..2 {
                if plan.release[slot + 3] {
                    close(&mut o, &mut b, 1, child[slot].unwrap());
                }
            }
            // The child's CLOEXEC reader must not close the parent's description.
            assert_eq!(read(&mut o, &mut b, reader, 16), b"A");
            close(&mut o, &mut b, 0, reader);
            close(&mut o, &mut b, 0, writer);
            let expected: &[u8] = if flags == 3 {
                assert!(b.is_closed());
                assert_eq!(
                    o.io(1, child[0].unwrap(), 4, 1, b"B", &mut |_| panic!(
                        "stale holder reached backend"
                    )),
                    Err(-9)
                );
                b"A"
            } else {
                assert!(!b.is_closed());
                write(&mut o, &mut b, 1, child[0].unwrap(), b"B");
                close(&mut o, &mut b, 1, child[0].unwrap());
                b"AB"
            };
            assert!(o.closed());
            assert!(b.is_closed());
            let verify = open(&mut o, &mut b, 1);
            assert_eq!(read(&mut o, &mut b, verify, 16), expected);
            close(&mut o, &mut b, 0, verify);
            assert!(o.closed() && b.is_closed());
        }
    }

    #[test]
    fn shared_offset_and_last_holder_survive_parent_close() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let h = open(&mut o, &mut b, 14);
        write(&mut o, &mut b, 0, h, b"A");
        let child = o.inherit(1, [Some(h), None]).unwrap()[0].unwrap();
        assert_ne!(h, child);
        close(&mut o, &mut b, 0, h);
        assert!(!b.is_closed());
        write(&mut o, &mut b, 1, child, b"B");
        close(&mut o, &mut b, 1, child);
        assert!(b.is_closed());
        let h = open(&mut o, &mut b, 1);
        assert_eq!(read(&mut o, &mut b, h, 16), b"AB");
    }
    #[test]
    fn duplicate_reference_shares_offset_separate_open_does_not() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let h = open(&mut o, &mut b, 14);
        write(&mut o, &mut b, 0, h, b"A");
        write(&mut o, &mut b, 0, h, b"B");
        close(&mut o, &mut b, 0, h);
        let first = open(&mut o, &mut b, 1);
        let second = open(&mut o, &mut b, 1);
        assert_ne!(first, second);
        assert_eq!(read(&mut o, &mut b, first, 1), b"A");
        assert_eq!(read(&mut o, &mut b, first, 1), b"B");
        assert_eq!(read(&mut o, &mut b, second, 2), b"AB");
    }
    #[test]
    fn local_exhaustion_does_not_send_truncate() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let h = open(&mut o, &mut b, 14);
        write(&mut o, &mut b, 0, h, b"AB");
        let read_handle = open(&mut o, &mut b, 1);
        assert_eq!(
            o.open(0, b"/scratch/data", 14, &mut |_| panic!(
                "unexpected truncate"
            )),
            Err(-23)
        );
        assert_eq!(read(&mut o, &mut b, read_handle, 2), b"AB");
    }
    #[test]
    fn uncertain_write_never_replays() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let h = open(&mut o, &mut b, 14);
        assert_eq!(
            o.io(0, h, 4, 1, b"A", &mut |f| {
                b.request(f);
                None
            }),
            Err(-5)
        );
        assert!(o.poisoned());
        let mut no_rpc = |_: &[u8; 32]| panic!("replayed after ambiguous write");
        assert_eq!(o.io(0, h, 4, 1, b"A", &mut no_rpc), Err(-5));
        assert_eq!(o.open(0, b"/scratch/data", 14, &mut no_rpc), Err(-5));
        assert_eq!(o.close(0, h, &mut no_rpc), Err(-5));
        assert_eq!(o.inherit(1, [Some(h), None]), Err(-5));
    }
    #[test]
    fn child_epoch_and_inheritance_validation_are_atomic() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let h = open(&mut o, &mut b, 14);
        let before = format!("{o:?}");
        assert_eq!(o.inherit(1, [None, Some(h)]), Err(-13));
        assert_eq!(format!("{o:?}"), before);
        let old = o.inherit(1, [Some(h), None]).unwrap()[0].unwrap();
        assert_eq!(o.inherit(2, [Some(h), None]), Err(-22));
        close(&mut o, &mut b, 1, old);
        let new = o.inherit(2, [Some(h), None]).unwrap()[0].unwrap();
        assert_ne!(new, old);
        assert_eq!(
            o.io(1, old, 4, 1, b"X", &mut |_| panic!("stale request")),
            Err(-9)
        );
        assert_eq!(
            o.io(0, new, 4, 1, b"X", &mut |_| panic!("foreign request")),
            Err(-9)
        );
        write(&mut o, &mut b, 1, new, b"A");
        close(&mut o, &mut b, 1, new);
        assert_eq!(o.inherit(2, [Some(h), None]), Err(-22));
    }
    #[test]
    fn rights_and_canonical_backend_errors_preserve_position() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let h = open(&mut o, &mut b, 14);
        assert_eq!(
            o.io(0, h, 2, 1, &[], &mut |_| panic!("read write-only")),
            Err(-13)
        );
        for _ in 0..4 {
            write(&mut o, &mut b, 0, h, &[b'A'; 16]);
        }
        let before = format!("{o:?}");
        assert_eq!(
            o.io(0, h, 4, 1, b"B", &mut |f| Some(b.request(f))),
            Err(-28)
        );
        assert_eq!(format!("{o:?}"), before);
        assert_eq!(
            o.io(2, h, 4, 1, b"X", &mut |_| panic!("invalid peer")),
            Err(-13)
        );
    }
    #[test]
    fn malformed_reply_after_effect_poisons_owner() {
        for op in [1, 3, 4] {
            let mut o = Owner::new(1);
            let mut b = backend::Scratch::new(1);
            let h = if op != 1 { open(&mut o, &mut b, 14) } else { 0 };
            let mut corrupt = |f: &[u8; 32]| {
                let mut r = b.request(f);
                r[31] = 1;
                Some(r)
            };
            let error = match op {
                1 => o.open(0, b"/scratch/data", 14, &mut corrupt).map(|_| ()),
                3 => o.close(0, h, &mut corrupt),
                _ => o.io(0, h, 4, 1, b"A", &mut corrupt).map(|_| ()),
            };
            assert_eq!(error, Err(-5));
            assert!(o.poisoned());
        }
    }
    #[test]
    fn gateway_enforces_root_binding_and_shared_io() {
        let mut o = Owner::new(1);
        let mut b = backend::Scratch::new(1);
        let root = o.root(0).unwrap();
        assert_eq!(o.root(1), None);
        let mut denied =
            |_: &[u8; 32]| -> Option<[u8; 32]> { panic!("unauthorized backend request") };
        let bad = o.gateway(
            0,
            &request(6, root ^ 1, 0, 14, b"/scratch/data"),
            &mut denied,
        );
        assert_eq!(bad, request((-13i32) as u32, 0, 0, 0, &[]));
        let opened = o.gateway(0, &request(6, root, 0, 14, b"/scratch/data"), &mut |f| {
            Some(b.request(f))
        });
        assert_eq!(word(&opened, 0), 0);
        let h = word(&opened, 4);
        assert_eq!(word(&opened, 8), 3);
        assert_eq!(opened[12..], [0; 20]);
        assert_eq!(
            o.gateway(0, &request(2, h, 4, 1, b"X"), &mut denied),
            request((-22i32) as u32, 0, 0, 0, &[])
        );
        assert_eq!(
            word(
                &o.gateway(0, &request(2, h, 3, 2, b"AB"), &mut |f| Some(b.request(f))),
                0
            ),
            2
        );
        assert_eq!(
            o.gateway(0, &request(3, h, 3, 0, &[]), &mut |f| Some(b.request(f))),
            [0; 32]
        );
        let opened = o.gateway(0, &request(6, root, 0, 1, b"/scratch/data"), &mut |f| {
            Some(b.request(f))
        });
        let r = o.gateway(
            0,
            &request(1, word(&opened, 4), word(&opened, 8), 16, &[]),
            &mut |f| Some(b.request(f)),
        );
        assert_eq!(word(&r, 0), 2);
        assert_eq!(&r[16..18], b"AB");
    }
    #[test]
    fn gateway_canonical_rejection_and_peer_authority() {
        let mut o = Owner::new(1);
        let root = o.root(0).unwrap();
        let mut denied =
            |_: &[u8; 32]| -> Option<[u8; 32]> { panic!("malformed request reached backend") };
        for f in [
            request(6, root, 1, 14, b"/scratch/data"),
            request(6, root, 0, 14, b"/scratch/data\0x"),
            request(6, root, 0, 14, b"0123456789abcdef"),
        ] {
            assert_eq!(
                o.gateway(0, &f, &mut denied),
                request((-22i32) as u32, 0, 0, 0, &[])
            );
        }
        assert_eq!(
            o.gateway(1, &request(6, root, 0, 14, b"/scratch/data"), &mut denied),
            request((-13i32) as u32, 0, 0, 0, &[])
        );
        assert!(!o.poisoned());
    }
}
