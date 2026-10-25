# SPDX-License-Identifier: BSD-2-Clause
"""Execute the actual activation partial client; native recovery stays independent."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'user/storage/service-runtime/fs-runtime-client.rs'
HARNESS = r'''#![allow(dead_code)]
use std::{cell::RefCell, collections::VecDeque};
#[derive(Default)]
struct State {
    queue: usize, op: u64, sent: Vec<u8>, closed: usize,
    transfers: usize, waits: usize, spurious: usize, stalled: bool,
    counts: VecDeque<i64>, statuses: VecDeque<i64>,
}
std::thread_local! {static STATE: RefCell<State> = RefCell::new(State::default());}
struct Connection {request: u64, send: u64, receive: u64}
fn get(b: &[u8;64], i: usize) -> u64 {u64::from_le_bytes(b[i*8..i*8+8].try_into().unwrap())}
fn put(b: &mut [u8;64], i: usize, n: u64) {b[i*8..i*8+8].copy_from_slice(&n.to_le_bytes());}
fn check(ok: bool) {assert!(ok, "PREFIX_FAIL_CLOSED");}
fn call(op: u64, endpoint: u64, _: u64, _: u64, _: u64) -> (i64,u64) {
    assert_eq!((op,endpoint), (0x24003,77));
    STATE.with(|s| {let mut s=s.borrow_mut();
        assert_eq!(s.sent, (11..27).collect::<Vec<_>>(), "PREFIX_CLOSE_BEFORE_COMPLETE");
        s.closed += 1;
    }); (0,0)
}
mod channel {
    use super::*;
    pub fn frame(_: u64, b: &mut [u8;64], writing: bool) -> Result<(),i64> {
        STATE.with(|state| {let mut s=state.borrow_mut(); if writing {s.op=get(b,1);} else {
            b.fill(0); b[..8].copy_from_slice(b"AFSRPC04"); put(b,2,17);
            if s.op==7 {put(b,4,788); put(b,6,2);} else {
                assert_eq!(s.op,1); put(b,3,2); put(b,4,2);
            }
        }}); Ok(())
    }
    pub unsafe fn trap(op: u64, endpoint: u64, pointer: u64, length: u64, _: u64) -> (i64,u64) {
        assert_eq!(endpoint,77);
        STATE.with(|state| {let mut s=state.borrow_mut();
            if op==0x24004 {
                assert_eq!((pointer,length),(0,0)); s.waits+=1;
                if s.spurious!=0 {s.spurious-=1;} else if !s.stalled {s.queue=0;}
                return (s.statuses.pop_front().unwrap_or(0),0);
            }
            assert_eq!(op,0x24002); assert!((1..=16).contains(&length));
            s.transfers+=1;
            let count=s.counts.pop_front().unwrap_or_else(|| {
                if s.stalled || s.queue==32 {-11} else {(length as usize).min(32-s.queue) as i64}
            });
            if count>0 && count<=length as i64 {
                s.sent.extend_from_slice(unsafe {std::slice::from_raw_parts(pointer as *const u8,count as usize)});
                s.queue+=count as usize;
            }
            (count,0)
        })
    }
}
#[path="BODY"] mod actual;
fn connection() -> Connection {Connection{request:17,send:77,receive:88}}
fn prefix() -> [u8;64] {let mut b=[0;64]; for (i,x) in b[..16].iter_mut().enumerate(){*x=11+i as u8;} b}
fn partial() {let mut b=[0;64]; b[..8].copy_from_slice(b"AFSRPC04"); put(&mut b,1,7); connection().bulk_partial(b);}
#[test]
fn full_short_and_spurious_queue_progress_preserves_exact_prefix_and_close() {
    for queue in [0,16,24,32] {
        STATE.with(|s| *s.borrow_mut()=State{queue,spurious:2,..State::default()});
        partial();
        STATE.with(|s| {let s=s.borrow(); assert_eq!(s.sent,(11..27).collect::<Vec<_>>());
            assert_eq!(s.closed,1); assert_eq!(s.waits,if queue<24 {0} else {3});});
    }
}
#[test]
fn several_short_transfers_resume_the_unsent_suffix() {
    STATE.with(|s| *s.borrow_mut()=State{counts:[3,-11,1,-11,12].into(),..State::default()});
    partial();
    STATE.with(|s| {let s=s.borrow(); assert_eq!(s.sent,(11..27).collect::<Vec<_>>());
        assert_eq!((s.transfers,s.waits,s.closed),(5,2,1));});
}
#[test]
fn fatal_zero_oversized_and_wait_errors_never_close() {
    for (counts,statuses,expected) in [(vec![0],vec![],-5),(vec![-9],vec![],-9),
        (vec![17],vec![],-5),(vec![-11],vec![-9],-9),(vec![-11],vec![1],-5),
        (vec![8,9],vec![],-5)] {
        let reset=|| STATE.with(|s| *s.borrow_mut()=State {
            counts:counts.iter().copied().collect(),statuses:statuses.iter().copied().collect(),..State::default()});
        reset(); assert_eq!(connection().bulk_prefix(&mut prefix()),Err(expected));
        reset(); assert!(std::panic::catch_unwind(partial).is_err(),"PREFIX_ERROR_ACCEPTED");
        STATE.with(|s| assert_eq!(s.borrow().closed,0));
    }
}
#[test]
fn transfer_exhaustion_uses_the_fixed_attempt_bound() {
    STATE.with(|s| *s.borrow_mut()=State{stalled:true,..State::default()});
    assert_eq!(connection().bulk_prefix(&mut prefix()),Err(-110));
    STATE.with(|s| {let s=s.borrow(); assert_eq!((s.transfers,s.waits,s.closed),(100_000,100_000,0));
        assert!(s.sent.is_empty());});
}
'''


class PartialPrefix(unittest.TestCase):
    def compile(self, directory, text, name):
        body = directory / (name + '-body.rs')
        # Only visibility changes; execute both actual transfer and actual caller.
        for method in ('bulk_prefix', 'bulk_partial'):
            old = '    fn ' + method + '('
            self.assertEqual(text.count(old), 1)
            text = text.replace(old, '    pub(super) fn ' + method + '(', 1)
        body.write_text(text)
        source = directory / (name + '.rs')
        source.write_text(HARNESS.replace('BODY', str(body)))
        binary = directory / name
        argv = ['rustc', '+1.98.0', '--edition=2024', '-Dwarnings', '--cfg',
                'fs_partial_request', '--cfg', 'fs_activation', '--test', str(source), '-o', str(binary)]
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return binary

    def test_actual_prefix_and_close_under_legal_backpressure_and_failures(self):
        with tempfile.TemporaryDirectory(prefix='aether-fs-prefix-') as tmp:
            binary = self.compile(Path(tmp), SOURCE.read_text(), 'positive')
            result = subprocess.run([str(binary), '--test-threads=1'], capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('4 passed; 0 failed', result.stdout)

    def test_compiling_transfer_omissions_fail_the_named_oracles(self):
        cases = [
            ('offset', 'offset += count as usize;', 'offset = count as usize;',
             'several_short_transfers_resume_the_unsent_suffix'),
            ('wait', 'unsafe { channel::trap(0x24004, self.send, 0, 0, 0) }.0', '0',
             'fatal_zero_oversized_and_wait_errors_never_close'),
            ('bounds', 'count <= 0 || count as usize > remaining', 'count <= 0',
             'fatal_zero_oversized_and_wait_errors_never_close'),
            ('early', 'if offset == 16 {', 'if offset != 0 {',
             'several_short_transfers_resume_the_unsent_suffix'),
            ('ceiling', 'for _ in 0..100_000 {', 'for _ in 0..100_001 {',
             'transfer_exhaustion_uses_the_fixed_attempt_bound'),
        ]
        with tempfile.TemporaryDirectory(prefix='aether-fs-prefix-omissions-') as tmp:
            for name, old, new, test in cases:
                with self.subTest(name=name):
                    text = SOURCE.read_text(); self.assertEqual(text.count(old), 1)
                    binary = self.compile(Path(tmp), text.replace(old, new, 1), name)
                    result = subprocess.run([str(binary), '--exact', test, '--test-threads=1'],
                                            capture_output=True, text=True, timeout=60)
                    self.assertEqual(result.returncode, 101, result.stdout + result.stderr)
                    self.assertIn(test + ' ... FAILED', result.stdout)


if __name__ == '__main__':
    unittest.main()
