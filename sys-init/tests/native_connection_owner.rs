// SPDX-License-Identifier: BSD-2-Clause
#[path = "../prototypes/native-supervisor/service_owner.rs"] mod service_owner;
#[path = "../prototypes/native-supervisor/connection_owner.rs"] mod connection_owner;
use service_owner::{Error, Fault, Identity, Phase};
use connection_owner::{Backend, Connection, Role, Terminal};
#[derive(Default)]
struct Fake { trace: Vec<(u8,u8)>, fail: Option<(usize,bool)>, channels: u8, terminal: Option<Terminal> }
impl Fake {
    fn step(&mut self, op:u8, handle:u8) -> Result<(),Fault<u8>> {
        self.trace.push((op,handle));
        if let Some((at,unknown))=self.fail {
            if self.trace.len()==at { return Err(if unknown { Fault::Unknown(op) } else { Fault::Known(op) }); }
        }
        Ok(())
    }
    fn failure(&mut self, after:usize, unknown:bool) { self.fail=Some((self.trace.len()+after,unknown)); }
}
impl Backend for Fake {
    type Reader=u8; type Writer=u8; type Worker=u8; type Error=u8;
    fn channel(&mut self)->Result<(u8,u8),Fault<u8>> { self.step(1,0)?;self.channels+=1;Ok((self.channels*2,self.channels*2+1)) }
    fn launch(&mut self,role:Role,request:u8,reply:u8)->Result<u8,Fault<u8>> { assert_eq!((request,reply),(2,5));self.step(2,role as u8)?;Ok(9) }
    fn observe(&mut self,w:u8)->Result<Option<Terminal>,Fault<u8>> {self.step(3,w)?;Ok(self.terminal)}
    fn stop(&mut self,w:u8)->Result<(),Fault<u8>> {self.step(4,w)}
    fn close_reader(&mut self,r:u8)->Result<(),Fault<u8>> {self.step(5,r)}
    fn close_writer(&mut self,w:u8)->Result<(),Fault<u8>> {self.step(6,w)}
    fn reclaim(&mut self,w:u8)->Result<(),Fault<u8>> {self.step(7,w)}
}
fn exited()->Terminal {Terminal{detail:134,kind:2}}
#[test]
fn each_partial_start_retains_exact_ownership() {
    for failure in 1..=3 {
        let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Runner,2);let mut b=Fake::default();b.failure(failure,false);
        assert!(matches!(c.start(&mut b),Err(Error::Backend(Fault::Known(_)))));
        let expected=match failure {1=>([false,false],[false,false],false),2=>([true,false],[true,false],false),_=>([true,true],[true,true],false)};
        assert_eq!(c.resources(),expected);let key=c.key();assert_eq!(c.handles(&key),Err(Error::Busy));
        assert_eq!(c.start(&mut b),Err(Error::Busy));b.fail=None;let at=b.trace.len();c.cleanup(&mut b,&key).unwrap();
        let expected: &[(u8,u8)]=match failure {1=>&[],2=>&[(6,3),(5,2)],_=>&[(6,3),(5,2),(6,5),(5,4)]};assert_eq!(&b.trace[at..],expected);
        assert_eq!(c.resources(),([false;2],[false;2],false));
    }
}
#[test]
fn successful_transfer_and_cached_terminal_cleanup() {
    for role in [Role::Runner,Role::Backend,Role::Command] {
        let mut id=Identity::new();let mut c=Connection::new(&mut id,role,1);let mut b=Fake::default();c.start(&mut b).unwrap();let key=c.key();
        assert_eq!(c.handles(&key),Ok((4,3,9)));assert_eq!(c.resources(),([false,true],[true,false],true));
        assert_eq!(c.cleanup(&mut b,&key),Err(Error::Busy));b.terminal=Some(exited());assert_eq!(c.observe(&mut b,&key),Ok(Some(exited())));
        let at=b.trace.len();assert_eq!(c.handles(&key),Err(Error::Busy));c.cleanup(&mut b,&key).unwrap();
        assert_eq!(&b.trace[at..],&[(6,3),(5,4),(7,9)]);assert_eq!(c.phase(),Phase::Idle);
        assert_eq!(c.start(&mut b),Err(Error::Exhausted));assert_eq!(c.cleanup(&mut b,&key),Err(Error::Invalid));
        assert_eq!(c.observe(&mut b,&key),Ok(Some(exited())));
    }
}
#[test]
fn backend_eof_precedes_terminal_without_repeated_close() {
    let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Backend,1);let mut b=Fake::default();c.start(&mut b).unwrap();let key=c.key();let at=b.trace.len();
    assert_eq!(c.observe(&mut b,&key),Ok(None));assert_eq!(&b.trace[at..],&[(3,9)]);
    c.backend_eof(&mut b,&key).unwrap();assert_eq!(c.handles(&key),Err(Error::Busy));
    assert_eq!(c.cleanup(&mut b,&key),Err(Error::Busy));c.backend_eof(&mut b,&key).unwrap();b.terminal=Some(Terminal{detail:17,kind:1});c.cleanup(&mut b,&key).unwrap();
    assert_eq!(&b.trace[at..],&[(3,9),(6,3),(3,9),(3,9),(5,4),(7,9)]);
}
#[test]
fn known_cleanup_failures_resume_only_outstanding_effects() {
    for failure in 1..=3 {
        let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Runner,1);let mut b=Fake::default();c.start(&mut b).unwrap();let key=c.key();b.terminal=Some(exited());c.observe(&mut b,&key).unwrap();b.failure(failure,false);
        assert!(matches!(c.cleanup(&mut b,&key),Err(Error::Backend(Fault::Known(_)))));
        let expected=match failure {1=>([false,true],[true,false],true),2=>([false,true],[false,false],true),_=>([false,false],[false,false],true)};assert_eq!(c.resources(),expected);
        b.fail=None;let at=b.trace.len();c.cleanup(&mut b,&key).unwrap();assert_eq!(&b.trace[at..],&[(6,3),(5,4),(7,9)][failure-1..]);
    }
}
#[test]
fn partial_launch_cleanup_failures_retain_transfer_ends() {
    for failure in 1..=4 {
        let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Command,1);let mut b=Fake::default();b.failure(3,false);assert!(c.start(&mut b).is_err());let key=c.key();b.failure(failure,false);assert!(c.cleanup(&mut b,&key).is_err());
        b.fail=None;let at=b.trace.len();c.cleanup(&mut b,&key).unwrap();assert_eq!(&b.trace[at..],&[(6,3),(5,2),(6,5),(5,4)][failure-1..]);assert_eq!(c.errors().0,Some(Fault::Known(2)));
    }
}
#[test]
fn unknown_effects_block_all_replay() {
    // Allocation, launch, observation, explicit EOF, stop and every cleanup effect.
    for stage in 0..10 {
        let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Backend,2);let mut b=Fake::default();
        if stage<3 {b.failure(stage+1,true);assert!(c.start(&mut b).is_err());}
        else {
            c.start(&mut b).unwrap();let k=c.key();
            match stage {
                3=>{b.failure(1,true);assert!(c.observe(&mut b,&k).is_err());},
                4=>{b.failure(1,true);assert!(c.backend_eof(&mut b,&k).is_err());},
                5=>{b.failure(2,true);assert!(c.request_stop(&mut b,&k).is_err());},
                _=>{b.terminal=Some(exited());b.failure(stage-5,true);assert!(c.cleanup(&mut b,&k).is_err());}
            }
        }
        let key=c.key();let at=b.trace.len();assert_eq!(c.phase(),Phase::Unknown);
        assert_eq!(c.start(&mut b),Err(Error::Closed));assert_eq!(c.cleanup(&mut b,&key),Err(Error::Closed));assert_eq!(c.observe(&mut b,&key),Err(Error::Closed));assert_eq!(c.backend_eof(&mut b,&key),Err(Error::Closed));assert_eq!(c.request_stop(&mut b,&key),Err(Error::Closed));assert_eq!(c.handles(&key),Err(Error::Closed));assert_eq!(at,b.trace.len());
    }
}
#[test]
fn stop_acknowledgment_is_not_terminal_or_eof() {
    {
        let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Runner,1);let mut b=Fake::default();c.start(&mut b).unwrap();let key=c.key();
        b.failure(1,false);assert_eq!(c.observe(&mut b,&key),Err(Error::Backend(Fault::Known(3))));assert_eq!(c.phase(),Phase::Live);
        b.failure(2,false);assert_eq!(c.request_stop(&mut b,&key),Err(Error::Backend(Fault::Known(4))));assert_eq!(c.phase(),Phase::Live);
        b.fail=None;c.request_stop(&mut b,&key).unwrap();assert_eq!(c.errors(),(Some(Fault::Known(3)),Some(Fault::Known(4))));
        assert_eq!(c.cleanup(&mut b,&key),Err(Error::Busy));b.terminal=Some(exited());c.cleanup(&mut b,&key).unwrap();
        assert_eq!(c.request_stop(&mut b,&key),Err(Error::Invalid));
    }
    let mut id=Identity::new();let mut c=Connection::new(&mut id,Role::Backend,1);let mut b=Fake::default();c.start(&mut b).unwrap();let key=c.key();
    b.failure(1,false);assert!(c.backend_eof(&mut b,&key).is_err());b.fail=None;c.request_stop(&mut b,&key).unwrap();let at=b.trace.len();c.request_stop(&mut b,&key).unwrap();assert_eq!(at,b.trace.len());
    assert_eq!(c.cleanup(&mut b,&key),Err(Error::Busy));b.terminal=Some(Terminal{detail:144,kind:3});c.cleanup(&mut b,&key).unwrap();assert_eq!(b.trace.iter().filter(|x| x.0==4).count(),1);
}
#[test]
fn stale_foreign_keys_and_wrong_role_have_no_effects() {
    let mut id=Identity::new();let mut other=Identity::new();let mut c=Connection::new(&mut id,Role::Runner,2);let mut d=Connection::new(&mut other,Role::Runner,1);let mut b=Fake::default();c.start(&mut b).unwrap();let old=c.key();let mut f=Fake::default();d.start(&mut f).unwrap();
    b.terminal=Some(exited());c.cleanup(&mut b,&old).unwrap();b.channels=0;b.terminal=None;c.start(&mut b).unwrap();
    for key in [old,d.key()] {let at=b.trace.len();assert_eq!(c.cleanup(&mut b,&key),Err(Error::Invalid));assert_eq!(c.observe(&mut b,&key),Err(Error::Invalid));assert_eq!(c.request_stop(&mut b,&key),Err(Error::Invalid));assert_eq!(c.backend_eof(&mut b,&key),Err(Error::Invalid));assert_eq!(c.handles(&key),Err(Error::Invalid));assert_eq!(at,b.trace.len());}
    let at=b.trace.len();assert_eq!(c.backend_eof(&mut b,&c.key()),Err(Error::Invalid));assert_eq!(at,b.trace.len());
}
