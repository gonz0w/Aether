// SPDX-License-Identifier: BSD-2-Clause
//! Bounded native ownership probes; not command/file protocol acceptance.
use super::*;
use lifecycle::{connection_owner::{Backend, Role, Terminal, Connection as Owned}, service_owner::{Identity, Fault, Error, Phase}, Native, NativeError};
use core::num::NonZeroU64 as Handle;
struct Probe { native: Native, deny_stop: bool, calls: usize }
impl Backend for Probe {
    type Reader=Handle; type Writer=Handle; type Worker=Handle; type Error=NativeError;
    fn channel(&mut self)->Result<(Handle,Handle),Fault<NativeError>> {self.calls+=1;self.native.channel()}
    fn launch(&mut self,r:Role,a:Handle,b:Handle)->Result<Handle,Fault<NativeError>> {self.calls+=1;self.native.launch(r,a,b)}
    fn observe(&mut self,w:Handle)->Result<Option<Terminal>,Fault<NativeError>> {self.calls+=1;self.native.observe(w)}
    fn stop(&mut self,w:Handle)->Result<(),Fault<NativeError>> {
        self.calls+=1;
        // Deliberately absent handle: actual kernel denial, not a fabricated errno.
        self.native.stop(if self.deny_stop {Handle::new(0xdead).unwrap()} else {w})
    }
    fn close_reader(&mut self,h:Handle)->Result<(),Fault<NativeError>> {self.calls+=1;self.native.close_reader(h)}
    fn close_writer(&mut self,h:Handle)->Result<(),Fault<NativeError>> {self.calls+=1;self.native.close_writer(h)}
    fn reclaim(&mut self,h:Handle)->Result<(),Fault<NativeError>> {self.calls+=1;self.native.reclaim(h)}
}
fn known<T>(r:Result<T,Error<NativeError>>,operation:u64,value:i64) {
    check(matches!(r,Err(Error::Backend(Fault::Known(e))) if e.operation==operation && e.value==value),1601);
}
fn empty(owner:&Owned<'_,Probe>) {check(owner.resources()==([false;2],[false;2],false),1601);}
fn stop(owner:&mut Owned<'_,Probe>,b:&mut Probe) {
    owner.request_stop(b,&owner.key()).unwrap_or_else(|_|end(1601));
    let calls=b.calls;owner.request_stop(b,&owner.key()).unwrap_or_else(|_|end(1601));check(b.calls==calls,1601);
    for _ in 0..100000 {
        if let Some(t)=owner.observe(b,&owner.key()).unwrap_or_else(|_|end(1601)) {
            check(t.detail==143 && t.kind==3,1601);return;
        }
        ctl(0x1fffe,0);
    }
    end(1601)
}
pub fn run(factory:u64,first:u64,second:u64,third:u64)->! {
    let mut id=Identity::new();let mut owner=Owned::new(&mut id,Role::Backend,3);
    let mut b=Probe{native:Native{factory,images:[first,second,third],startup:args(b"worker")},deny_stop:false,calls:0};
    if cfg!(probe_alloc) {
        let mut held=[(0u64,0u64);if cfg!(probe_alloc_first) {6} else {5}];
        for pair in &mut held {let(r,w)=b.channel().unwrap_or_else(|_|end(1601));*pair=(r.get(),w.get());}
        known(owner.start(&mut b),0x24000,-16);
        check(owner.resources()==(if cfg!(probe_alloc_first) {[false,false]} else {[true,false]},if cfg!(probe_alloc_first) {[false,false]} else {[true,false]},false),1601);
        if !cfg!(probe_skip_cleanup) {owner.cleanup(&mut b,&owner.key()).unwrap_or_else(|_|end(1601));}
        empty(&owner);
        for(r,w)in held {check(ctl(0x24003,r).0==0 && ctl(0x24003,w).0==0,1601);}
    }
    if cfg!(probe_launch) {
        b.native.startup.argc=5;known(owner.start(&mut b),0x23002,-22);
        check(owner.resources()==([true,true],[true,true],false),1601);
        owner.cleanup(&mut b,&owner.key()).unwrap_or_else(|_|end(1601));empty(&owner);b.native.startup=args(b"worker");
    }
    for _ in 0..2 {
        owner.start(&mut b).unwrap_or_else(|_|end(1601));
        if cfg!(probe_stop) {
            b.deny_stop=true;known(owner.request_stop(&mut b,&owner.key()),0x20007,-9);
            check(owner.phase()==Phase::Live && owner.resources()==([false,true],[true,false],true),1601);b.deny_stop=false;
        }
        let (reader,_,lifecycle_worker)=owner.handles(&owner.key()).unwrap_or_else(|_|end(1601));
        stop(&mut owner,&mut b);
        if cfg!(probe_reclaim) {
            let (_,_,worker)=owner.resources();check(worker,1601);
            // Deliberate external release after terminal; owner must retain Unknown.
            let child=lifecycle_worker;
            check(ctl(0x20002,child.get()).0==0,1601);
            check(matches!(owner.cleanup(&mut b,&owner.key()),Err(Error::Backend(Fault::Unknown(e))) if e.operation==0x20002 && e.value==-9),1601);
            check(owner.resources()==([false;2],[false;2],true) && owner.phase()==Phase::Unknown,1601);
            let calls=b.calls;check(matches!(owner.cleanup(&mut b,&owner.key()),Err(Error::Closed)) && b.calls==calls,1601);end(1603);
        }
        if cfg!(probe_close) {
            check(ctl(0x24003,reader.get()).0==0,1601);
            check(matches!(owner.cleanup(&mut b,&owner.key()),Err(Error::Backend(Fault::Unknown(e))) if e.operation==0x24003 && e.value==-13),1601);
            check(owner.phase()==Phase::Unknown && owner.resources()==([false,true],[false,false],true),1601);
            let calls=b.calls;
            check(matches!(owner.cleanup(&mut b,&owner.key()),Err(Error::Closed)) && matches!(owner.request_stop(&mut b,&owner.key()),Err(Error::Closed)) && matches!(owner.start(&mut b),Err(Error::Closed)),1601);
            check(b.calls==calls,1601);end(1602);
        }
        owner.cleanup(&mut b,&owner.key()).unwrap_or_else(|_|end(1601));empty(&owner);
        // Exercise the remaining two real slots, giving the profile's six-reclaim oracle.
        for role in [Role::Runner,Role::Command] {
            let mut other_id=Identity::new();let mut other=Owned::new(&mut other_id,role,1);
            b.native.startup=args(b"client");other.start(&mut b).unwrap_or_else(|_|end(1601));
            stop(&mut other,&mut b);other.cleanup(&mut b,&other.key()).unwrap_or_else(|_|end(1601));empty(&other);
        }
        b.native.startup=args(b"worker");
    }
    end(100)
}
