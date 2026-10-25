// SPDX-License-Identifier: BSD-2-Clause
//! Native acceptance of the reusable owner; all failure injections stay here.
use super::{adapter::{self, Adapter, Reader, Writer, Worker}, require};
use super::service_owner::{Backend, Error, Fault, Identity, Phase, Service};
struct Native<'a> { adapter: &'a mut Adapter, deny: bool, close_error: bool }
impl Backend for Native<'_> {
    type Reader=Reader; type Writer=Writer; type Worker=Worker; type Error=adapter::Error;
    fn channel(&mut self)->Result<(Reader,Writer),Fault<Self::Error>> {
        self.adapter.channel().map_err(Fault::Unknown)
    }
    fn launch(&mut self, slot:u8, writer:Writer)->Result<Worker,Fault<Self::Error>> {
        if self.deny {
            // The adapter rejects slot 2 before a trap; ownership is unchanged.
            return self.adapter.launch(2,writer,b"terminal-exit17").map_err(Fault::Known);
        }
        self.adapter.launch(usize::from(slot),writer,b"terminal-exit17").map_err(Fault::Unknown)
    }
    fn stop(&mut self,worker:Worker)->Result<(),Fault<Self::Error>> { self.adapter.stop(worker).map_err(Fault::Unknown) }
    fn terminal(&mut self,worker:Worker)->Result<bool,Fault<Self::Error>> {
        let observed=self.adapter.observe(worker).map_err(Fault::Unknown)?;
        if observed.terminal==0 { return Ok(false); }
        let status=self.adapter.worker_status(worker).map_err(Fault::Unknown)?;
        require(observed.terminal==18 && status.result==18 && status.kind==1,1124);
        Ok(true)
    }
    fn close_reader(&mut self,reader:Reader)->Result<(),Fault<Self::Error>> {
        if self.close_error {
            self.adapter.close(reader).map_err(Fault::Unknown)?;
            // Actual stale-handle error after an intentionally external close.
            // The owner cannot infer completion and must retain/freeze its record.
        }
        self.adapter.close(reader).map_err(Fault::Unknown)
    }
    fn close_writer(&mut self,writer:Writer)->Result<(),Fault<Self::Error>> {
        self.adapter.close_writer(writer).map_err(Fault::Unknown)
    }
    fn reclaim(&mut self,worker:Worker)->Result<(),Fault<Self::Error>> {
        self.adapter.reclaim(worker).map_err(Fault::Unknown)
    }
}
pub fn run(adapter:&mut Adapter)->! {
    let mut identity=Identity::new(); let mut native=Native { adapter,deny:cfg!(owner_launch_denial),close_error:cfg!(owner_close_error) };
    let mut service=Service::<Native<'_>>::new(&mut identity,0,if native.deny {4} else {3});
    if native.deny {
        require(matches!(service.start(&mut native),Err(Error::Backend(Fault::Known(_)))),1120);
        require(service.resources()==(true,true,false),1120);
        require(service.cleanup(&mut native,&service.key()).is_ok() && native.adapter.clean(),1120);
        native.deny=false;
    }
    for _ in 0..3 {
        let stale=service.key(); require(service.start(&mut native).is_ok(),1120);
        require(matches!(service.cleanup(&mut native,&stale),Err(Error::Invalid)),1121);
        let key=service.key(); let mut done=false;
        for _ in 0..100000 {
            match service.cleanup(&mut native,&key) {
                Ok(())=>{done=true;break;},
                Err(Error::Busy)=>adapter::yield_now(),
                Err(Error::Backend(Fault::Unknown(error))) if cfg!(owner_close_error)=> {
                    require(error.operation==0x24003 && error.errno==13 && service.phase()==Phase::Unknown &&
                        service.resources()==(true,false,true),1123);
                    require(matches!(service.start(&mut native),Err(Error::Closed)) &&
                        matches!(service.cleanup(&mut native,&key),Err(Error::Closed)),1123);
                    adapter::finish(1122);
                },
                _=>adapter::finish(1123),
            }
        }
        require(done && service.phase()==Phase::Idle && service.resources()==(false,false,false) && native.adapter.clean(),1120);
    }
    require(matches!(service.start(&mut native),Err(Error::Exhausted)),1120);
    adapter::finish(100)
}
