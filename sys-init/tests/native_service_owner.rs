// SPDX-License-Identifier: BSD-2-Clause
#[path = "../prototypes/native-supervisor/service_owner.rs"]
mod service_owner;
use service_owner::*;
#[derive(Default)]
struct Fake { calls: Vec<u8>, fail: Option<(u8, Fault<u8>)>, live: bool }
impl Fake {
    fn call(&mut self, op: u8) -> Result<(), Fault<u8>> {
        self.calls.push(op);
        if let Some((selected, error)) = self.fail { if selected == op { return Err(error); } }
        Ok(())
    }
}
impl Backend for Fake {
    type Reader=u8; type Writer=u8; type Worker=u8; type Error=u8;
    fn channel(&mut self)->Result<(u8,u8),Fault<u8>> { self.call(1)?; Ok((10,11)) }
    fn launch(&mut self,slot:u8,w:u8)->Result<u8,Fault<u8>> { assert_eq!(slot,0); assert_eq!(w,11); self.call(2)?; Ok(12) }
    fn stop(&mut self,w:u8)->Result<(),Fault<u8>> { assert_eq!(w,12); self.call(7) }
    fn terminal(&mut self,w:u8)->Result<bool,Fault<u8>> { assert_eq!(w,12); self.call(3)?; Ok(!self.live) }
    fn close_reader(&mut self,r:u8)->Result<(),Fault<u8>> { assert_eq!(r,10); self.call(4) }
    fn close_writer(&mut self,w:u8)->Result<(),Fault<u8>> { assert_eq!(w,11); self.call(5) }
    fn reclaim(&mut self,w:u8)->Result<(),Fault<u8>> { assert_eq!(w,12); self.call(6) }
}
#[test]
fn repeated_cycles_and_budget() {
    let mut id=Identity::new(); let mut s=Service::<Fake>::new(&mut id,0,100); let mut b=Fake::default();
    let size=std::mem::size_of_val(&s);
    for generation in 1..=100 {
        let old=s.key(); s.start(&mut b).unwrap(); assert_eq!(s.generation(),generation);
        let before=b.calls.len(); assert_eq!(s.cleanup(&mut b,&old),Err(Error::Invalid)); assert_eq!(b.calls.len(),before);
        s.cleanup(&mut b,&s.key()).unwrap(); assert_eq!(s.resources(),(false,false,false));
        assert_eq!(s.phase(),Phase::Idle); assert_eq!(std::mem::size_of_val(&s),size);
    }
    assert_eq!(b.calls, [1,2,3,4,6].repeat(100));
    assert_eq!(s.start(&mut b),Err(Error::Exhausted)); assert_eq!(s.generation(),100);
    assert_eq!(b.calls.len(),500);
}
#[test]
fn channel_and_launch_failure_cleanup() {
    for op in [1,2] {
        let mut id=Identity::new(); let mut s=Service::<Fake>::new(&mut id,0,2);
        let mut b=Fake { fail:Some((op,Fault::Known(9))),..Default::default() };
        assert_eq!(s.start(&mut b),Err(Error::Backend(Fault::Known(9))));
        if op==2 {
            assert_eq!(s.resources(),(true,true,false)); assert_eq!(s.start(&mut b),Err(Error::Busy));
            b.fail=None; s.cleanup(&mut b,&s.key()).unwrap(); assert_eq!(b.calls,vec![1,2,5,4]);
        } else { assert_eq!(s.phase(),Phase::Idle); assert_eq!(b.calls,vec![1]); }
        assert_eq!(s.errors(),(Some(Fault::Known(9)),Some(Fault::Known(9))));
        assert_eq!(s.resources(),(false,false,false));
    }
}
#[test]
fn cleanup_errors_retain_exact_remaining_resources() {
    for (op,remaining) in [(3,(true,false,true)),(4,(true,false,true)),(6,(false,false,true))] {
        let mut id=Identity::new(); let mut s=Service::<Fake>::new(&mut id,0,2); let mut b=Fake::default();
        s.start(&mut b).unwrap(); b.fail=Some((op,Fault::Known(op)));
        assert_eq!(s.cleanup(&mut b,&s.key()),Err(Error::Backend(Fault::Known(op))));
        assert_eq!(s.resources(),remaining); assert_eq!(s.start(&mut b),Err(Error::Busy));
        b.fail=None; s.cleanup(&mut b,&s.key()).unwrap(); assert_eq!(s.resources(),(false,false,false));
        if op==6 { assert_eq!(b.calls.iter().filter(|&&v|v==4).count(),1); }
        assert_eq!(s.errors().0,Some(Fault::Known(op)));
    }
}
#[test]
fn failed_launch_writer_cleanup_retains_first_error() {
    let mut id=Identity::new(); let mut s=Service::<Fake>::new(&mut id,0,2);
    let mut b=Fake { fail:Some((2,Fault::Known(2))),..Default::default() };
    assert!(s.start(&mut b).is_err()); b.fail=Some((5,Fault::Known(5)));
    assert!(s.cleanup(&mut b,&s.key()).is_err()); assert_eq!(s.resources(),(true,true,false));
    assert_eq!(s.errors(),(Some(Fault::Known(2)),Some(Fault::Known(5))));
    b.fail=None; s.cleanup(&mut b,&s.key()).unwrap(); assert_eq!(b.calls,vec![1,2,5,5,4]);
}
#[test]
fn unknown_never_replays() {
    for op in 1..=6 {
        let mut id=Identity::new(); let mut s=Service::<Fake>::new(&mut id,0,2); let mut b=Fake::default();
        if op<=2 { b.fail=Some((op,Fault::Unknown(op))); assert!(s.start(&mut b).is_err()); }
        else {
            if op==5 { b.fail=Some((2,Fault::Known(2))); assert!(s.start(&mut b).is_err()); }
            else { s.start(&mut b).unwrap(); }
            b.fail=Some((op,Fault::Unknown(op))); assert!(s.cleanup(&mut b,&s.key()).is_err());
        }
        assert_eq!(s.phase(),Phase::Unknown); let count=b.calls.len(); let refs=s.resources();
        b.fail=None; assert_eq!(s.start(&mut b),Err(Error::Closed));
        assert_eq!(s.cleanup(&mut b,&s.key()),Err(Error::Closed));
        assert_eq!(b.calls.len(),count); assert_eq!(s.resources(),refs);
    }
}
#[test]
fn foreign_owner_and_live_worker_deny_cleanup() {
    let mut a=Identity::new(); let mut c=Identity::new();
    let mut s=Service::<Fake>::new(&mut a,0,1); let mut other=Service::<Fake>::new(&mut c,0,1); let mut b=Fake::default();
    s.start(&mut b).unwrap(); other.start(&mut b).unwrap(); let before=b.calls.len();
    assert_eq!(s.cleanup(&mut b,&other.key()),Err(Error::Invalid)); assert_eq!(before,b.calls.len());
    b.live=true; assert_eq!(s.cleanup(&mut b,&s.key()),Err(Error::Busy));
    assert_eq!(s.resources(),(true,false,true)); assert_eq!(b.calls.last(),Some(&3));
}
#[test]
fn stop_acknowledgment_is_not_cleanup_and_keys_stay_exact() {
    let mut id=Identity::new(); let mut foreign=Identity::new();
    let mut s=Service::<Fake>::new(&mut id,0,2); let mut other=Service::<Fake>::new(&mut foreign,0,1);
    let mut b=Fake {live:true,..Default::default()};
    s.start(&mut b).unwrap(); other.start(&mut b).unwrap(); let before=b.calls.len();
    assert_eq!(s.request_stop(&mut b,&other.key()),Err(Error::Invalid)); assert_eq!(b.calls.len(),before);
    let old=s.key(); s.request_stop(&mut b,&old).unwrap(); assert_eq!(s.phase(),Phase::Stopping);
    s.request_stop(&mut b,&old).unwrap(); assert_eq!(b.calls.iter().filter(|&&v|v==7).count(),1);
    assert_eq!(s.cleanup(&mut b,&old),Err(Error::Busy)); assert_eq!(s.resources(),(true,false,true));
    b.live=false; s.cleanup(&mut b,&old).unwrap(); s.start(&mut b).unwrap(); let before=b.calls.len();
    assert_eq!(s.request_stop(&mut b,&old),Err(Error::Invalid)); assert_eq!(b.calls.len(),before);
}
#[test]
fn stop_failure_preserves_state_and_unknown_blocks_replay() {
    for fault in [Fault::Known(7),Fault::Unknown(7)] {
        let mut id=Identity::new(); let mut s=Service::<Fake>::new(&mut id,0,1);
        let mut b=Fake {live:true,fail:Some((7,fault)),..Default::default()}; s.start(&mut b).unwrap();
        assert_eq!(s.request_stop(&mut b,&s.key()),Err(Error::Backend(fault)));
        assert_eq!(s.resources(),(true,false,true)); assert_eq!(s.errors().0,Some(fault));
        b.fail=None;
        if matches!(fault,Fault::Unknown(_)) {
            let before=b.calls.len(); assert_eq!(s.request_stop(&mut b,&s.key()),Err(Error::Closed));
            assert_eq!(s.cleanup(&mut b,&s.key()),Err(Error::Closed)); assert_eq!(b.calls.len(),before);
        } else { s.request_stop(&mut b,&s.key()).unwrap(); assert_eq!(s.phase(),Phase::Stopping); }
    }
}
