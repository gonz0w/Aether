// SPDX-License-Identifier: BSD-2-Clause
#[path = "../prototypes/native-supervisor/service_owner.rs"] mod service_owner;
#[path = "../prototypes/native-supervisor/service_pair.rs"] mod service_pair;
use service_owner::*;
use service_pair::Pair;
struct Fake { log: Vec<(u8,u8)>, next:u8, slots:[u8;16], live:[bool;2], automatic:bool, fail:Option<(u8,Fault<u8>)> }
impl Default for Fake {
    fn default()->Self { Self {log:vec![],next:0,slots:[0;16],live:[false;2],automatic:true,fail:None} }
}
impl Fake {
    fn call(&mut self,op:u8,slot:u8)->Result<(),Fault<u8>> {
        self.log.push((op,slot));
        if let Some((selected,error))=self.fail { if selected==op {return Err(error);} }
        Ok(())
    }
}
impl Backend for Fake {
    type Reader=u8;type Writer=u8;type Worker=u8;type Error=u8;
    fn channel(&mut self)->Result<(u8,u8),Fault<u8>> {self.call(1,255)?;self.next+=1;Ok((self.next,self.next))}
    fn launch(&mut self,slot:u8,w:u8)->Result<u8,Fault<u8>> {
        self.call(2,slot)?;self.slots[w as usize]=slot;self.live[slot as usize]=true;Ok(w)
    }
    fn terminal(&mut self,w:u8)->Result<bool,Fault<u8>> {let s=self.slots[w as usize];self.call(3,s)?;Ok(!self.live[s as usize])}
    fn stop(&mut self,w:u8)->Result<(),Fault<u8>> {let s=self.slots[w as usize];self.call(7,s)?;if self.automatic {self.live[s as usize]=false;}Ok(())}
    fn close_reader(&mut self,r:u8)->Result<(),Fault<u8>> {self.call(4,self.slots[r as usize])}
    fn close_writer(&mut self,w:u8)->Result<(),Fault<u8>> {self.call(5,self.slots[w as usize])}
    fn reclaim(&mut self,w:u8)->Result<(),Fault<u8>> {self.call(6,self.slots[w as usize])}
}
#[test]
fn direct_start_restart_and_reverse_shutdown() {
    let(mut a,mut b)=(Identity::new(),Identity::new());let mut p=Pair::<Fake>::new(&mut a,&mut b,2,1);let mut f=Fake::default();
    assert_eq!(p.start_dependent(&mut f),Err(Error::Busy));assert!(f.log.is_empty());
    p.start_provider(&mut f).unwrap();p.restart_provider(&mut f).unwrap();p.start_dependent(&mut f).unwrap();
    let count=f.log.len();assert_eq!(p.restart_provider(&mut f),Err(Error::Busy));assert_eq!(f.log.len(),count);
    p.shutdown(&mut f).unwrap();assert_eq!(p.phases(),(Phase::Idle,Phase::Idle));
    assert_eq!(f.log,vec![(1,255),(2,0),(3,0),(7,0),(3,0),(4,0),(6,0),(1,255),(2,0),
        (3,0),(1,255),(2,1),(3,1),(7,1),(3,1),(4,1),(6,1),(3,0),(7,0),(3,0),(4,0),(6,0)]);
    let count=f.log.len();p.shutdown(&mut f).unwrap();assert_eq!(f.log.len(),count);
    assert_eq!(p.start_provider(&mut f),Err(Error::Closed));assert_eq!(p.start_dependent(&mut f),Err(Error::Closed));
}
#[test]
fn provider_loss_blocks_admission_until_clean_replacement() {
    let(mut a,mut b)=(Identity::new(),Identity::new());let mut p=Pair::<Fake>::new(&mut a,&mut b,2,1);let mut f=Fake::default();
    p.start_provider(&mut f).unwrap();f.live[0]=false;
    assert_eq!(p.start_dependent(&mut f),Err(Error::Busy));assert_eq!(f.next,1);assert_eq!(p.phases(),(Phase::Cleanup,Phase::Idle));
    p.restart_provider(&mut f).unwrap();assert_eq!(&f.log[3..],&[(3,0),(4,0),(6,0),(1,255),(2,0)]);
    p.start_dependent(&mut f).unwrap();p.shutdown(&mut f).unwrap();
}
#[test]
fn delayed_terminal_never_repeats_stop_or_stops_provider_early() {
    let(mut a,mut b)=(Identity::new(),Identity::new());let mut p=Pair::<Fake>::new(&mut a,&mut b,1,1);
    let mut f=Fake {automatic:false,..Default::default()};p.start_provider(&mut f).unwrap();p.start_dependent(&mut f).unwrap();
    assert_eq!(p.shutdown(&mut f),Err(Error::Busy));assert_eq!(p.phases(),(Phase::Live,Phase::Stopping));
    assert_eq!(p.shutdown(&mut f),Err(Error::Busy));assert_eq!(f.log.iter().filter(|&&x|x==(7,1)).count(),1);
    assert!(!f.log.contains(&(7,0)));f.live[1]=false;
    assert_eq!(p.shutdown(&mut f),Err(Error::Busy));assert_eq!(p.phases(),(Phase::Stopping,Phase::Idle));
    f.live[0]=false;p.shutdown(&mut f).unwrap();assert_eq!(f.log.iter().filter(|&&x|x==(7,0)).count(),1);
}
#[test]
fn stop_error_closes_admission_and_retains_order_on_retry() {
    let(mut a,mut b)=(Identity::new(),Identity::new());let mut p=Pair::<Fake>::new(&mut a,&mut b,1,1);let mut f=Fake::default();
    p.start_provider(&mut f).unwrap();p.start_dependent(&mut f).unwrap();f.fail=Some((7,Fault::Known(9)));
    assert_eq!(p.shutdown(&mut f),Err(Error::Backend(Fault::Known(9))));assert_eq!(p.phases(),(Phase::Live,Phase::Live));
    assert!(!f.log.contains(&(7,0)));assert!(!f.log.contains(&(4,1)));assert_eq!(p.start_provider(&mut f),Err(Error::Closed));
    f.fail=None;p.shutdown(&mut f).unwrap();assert_eq!(p.phases(),(Phase::Idle,Phase::Idle));
}
#[test]
fn unknown_dependent_cleanup_preserves_provider_and_blocks_replay() {
    let(mut a,mut b)=(Identity::new(),Identity::new());let mut p=Pair::<Fake>::new(&mut a,&mut b,1,1);let mut f=Fake::default();
    p.start_provider(&mut f).unwrap();p.start_dependent(&mut f).unwrap();f.fail=Some((4,Fault::Unknown(4)));
    assert_eq!(p.shutdown(&mut f),Err(Error::Backend(Fault::Unknown(4))));assert_eq!(p.phases(),(Phase::Live,Phase::Unknown));
    assert!(!f.log.contains(&(6,1)));assert!(!f.log.contains(&(7,0)));let count=f.log.len();
    f.fail=None;assert_eq!(p.shutdown(&mut f),Err(Error::Closed));assert_eq!(f.log.len(),count);
}
