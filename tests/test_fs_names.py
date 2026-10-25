# SPDX-License-Identifier: BSD-2-Clause
"""Actual bounded AF05 fixture sender and selected native controller builds."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
import test_fs_activation as prior

ROOT = prior.ROOT
SOURCE = ROOT / 'user/storage/service-runtime/fs-names-client.rs'
HARNESS = r'''#![allow(dead_code)]
use std::cell::RefCell;
struct Connection;
fn get(b:&[u8;64],i:usize)->u64{u64::from_le_bytes(b[i*8..i*8+8].try_into().unwrap())}
fn put(b:&mut[u8;64],i:usize,n:u64){b[i*8..i*8+8].copy_from_slice(&n.to_le_bytes());}
std::thread_local!{static FRAMES:RefCell<(Vec<[u8;64]>,usize)>=RefCell::new((vec![],0));}
mod channel {use super::*;
 pub fn frame(endpoint:u64,bytes:&mut[u8;64],writing:bool)->Result<(),i64>{assert_eq!(endpoint,77);assert!(writing);
 FRAMES.with(|s|{let mut s=s.borrow_mut();s.0.push(*bytes);if s.0.len()==s.1 {Err(-32)}else{Ok(())}})}
}
#[path="BODY"]mod names;
fn raw(op:u64,a:u8,b:u8)->[u8;64]{let mut r=[0;64];r[..8].copy_from_slice(b"AFSRPC05");put(&mut r,1,op);r[48]=a;r[49]=b;r}
fn reset(fail:usize){FRAMES.with(|s|*s.borrow_mut()=(vec![],fail));}
#[test]fn exact_names_and_joined_rename_preserve_the_final_distinguishing_byte(){
 for op in [1,7,8,9]{reset(0);assert!(names::send(77,&mut raw(op,b'p',b'q')));
 FRAMES.with(|s|{let s=s.borrow();assert_eq!(s.0.len(),if op==8{3}else{2});let h=s.0[0];assert_eq!(&h[..8],b"AFSRPC05");
 assert_eq!(get(&h,5),64|if op==8{64<<32}else{0});assert!(h[48..].iter().all(|b|*b==0));
 assert_eq!(&s.0[1],b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
 if op==8{assert_eq!(s.0[1][..63],s.0[2][..63]);assert_eq!((s.0[1][63],s.0[2][63]),(b'5',b'6'));}});
 }
 for tag in [b'.',b'/',0]{reset(0);assert!(names::send(77,&mut raw(7,tag,0)));FRAMES.with(|s|{let s=s.borrow();assert_eq!(get(&s.0[0],5),1);assert_eq!(s.0[1][0],tag);assert!(s.0[1][1..].iter().all(|b|*b==0));});}
 reset(0);let mut r=raw(5,71,91);let old=r;assert!(names::send(77,&mut r));FRAMES.with(|s|assert_eq!(s.borrow().0,vec![old]));
}
#[test]fn errors_never_retry_and_short_rename_is_rejected_before_output(){
 for fail in [1,2,3]{reset(fail);assert!(!names::send(77,&mut raw(8,b'p',b'q')));FRAMES.with(|s|assert_eq!(s.borrow().0.len(),fail));}
 reset(0);assert!(!names::send(77,&mut raw(8,b'.',b'q')));FRAMES.with(|s|assert!(s.borrow().0.is_empty()));
}
'''


class Names(unittest.TestCase):
    def test_actual_sender_body_order_tail_and_no_retry(self):
        with tempfile.TemporaryDirectory(prefix='aether-fs-names-client-') as directory:
            source = Path(directory)/'test.rs'
            source.write_text(HARNESS.replace('BODY',str(SOURCE)))
            binary=Path(directory)/'test'
            result=subprocess.run(['rustc','+1.98.0','--edition=2024','-Dwarnings','--test',str(source),'-o',str(binary)],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=subprocess.run([str(binary),'--test-threads=1'],capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('2 passed; 0 failed',result.stdout)

    def test_all_actual_named_controllers_fit_existing_8k_without_statics(self):
        text=prior.Controller().driver()
        with tempfile.TemporaryDirectory(prefix='aether-fs-names-fit-') as directory:
            out=Path(directory);source=out/'supervisor.rs';source.write_text(text)
            for case in ['normal','lost-reply','partial-request','close-failure']:
                binary=out/(case+'.raw')
                argv=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-Dwarnings',
                      '-Copt-level=z','-Clto=fat','-Ccodegen-units=1','-Cpanic=abort','-Crelocation-model=static',
                      '-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld','-Clink-arg=--oformat=binary']
                for cfg in ['pool_create','pool_import','fs_mixed','namespace_wait','fs_bulk','fs_runtime','fs_activation','fs_names']:
                    argv+=['--cfg',cfg]
                if case in ('lost-reply','partial-request'):
                    argv+=['--cfg','fs_lost_reply' if case=='lost-reply' else 'fs_partial_request']
                argv+=[str(source),'-o',str(binary)]
                result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=60)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertLessEqual(binary.stat().st_size,8192)
                print('names controller',case,binary.stat().st_size,hashlib.sha256(binary.read_bytes()).hexdigest())


if __name__=='__main__':
    unittest.main()
