// SPDX-License-Identifier: BSD-2-Clause
//! Native witnesses for fixed startup/restart/reverse shutdown, with labelled injections.
use super::{adapter::{self, Adapter, Reader, Writer, Worker}, require};
use super::service_owner::{Backend, Error, Fault, Identity, Phase};
use super::service_pair::Pair;
struct Native<'a> {
    adapter:&'a mut Adapter, workers:[Option<Worker>;2], stopped:[bool;2],
    first_exit:bool, stop_error:bool, close_error:bool,
}
impl Native<'_> {
    fn slot(&self,worker:Worker)->usize { self.workers.iter().position(|w|*w==Some(worker)).unwrap_or_else(||adapter::finish(1130)) }
}
impl Backend for Native<'_> {
    type Reader=Reader;type Writer=Writer;type Worker=Worker;type Error=adapter::Error;
    fn channel(&mut self)->Result<(Reader,Writer),Fault<Self::Error>> { self.adapter.channel().map_err(Fault::Unknown) }
    fn launch(&mut self,slot:u8,writer:Writer)->Result<Worker,Fault<Self::Error>> {
        let index=usize::from(slot);require(index<2,1130);
        let mode:&[u8]=if index==0 && self.first_exit {b"terminal-exit17"} else {b"silent"};
        let worker=self.adapter.launch(index,writer,mode).map_err(Fault::Unknown)?;
        self.workers[index]=Some(worker);self.stopped[index]=false;self.first_exit=false;Ok(worker)
    }
    fn terminal(&mut self,worker:Worker)->Result<bool,Fault<Self::Error>> {
        let observed=self.adapter.observe(worker).map_err(Fault::Unknown)?;
        if observed.terminal==0 {return Ok(false);}
        let status=self.adapter.worker_status(worker).map_err(Fault::Unknown)?;
        let(expected,kind)=if self.stopped[self.slot(worker)] {(144,3)} else {(18,1)};
        require(observed.terminal==expected && status.result==expected && status.kind==kind,1131);Ok(true)
    }
    fn stop(&mut self,worker:Worker)->Result<(),Fault<Self::Error>> {
        if self.stop_error {
            // Synthetic pre-call Known failure: no native stop is attempted.
            return Err(Fault::Known(adapter::Error {operation:0x20007,errno:13}));
        }
        self.adapter.stop(worker).map_err(Fault::Unknown)?;let index=self.slot(worker);self.stopped[index]=true;Ok(())
    }
    fn close_reader(&mut self,reader:Reader)->Result<(),Fault<Self::Error>> {
        if self.close_error {self.adapter.close(reader).map_err(Fault::Unknown)?;}
        self.adapter.close(reader).map_err(Fault::Unknown)
    }
    fn close_writer(&mut self,writer:Writer)->Result<(),Fault<Self::Error>> {self.adapter.close_writer(writer).map_err(Fault::Unknown)}
    fn reclaim(&mut self,worker:Worker)->Result<(),Fault<Self::Error>> {
        self.adapter.reclaim(worker).map_err(Fault::Unknown)?;let index=self.slot(worker);self.workers[index]=None;Ok(())
    }
}
pub fn run(adapter:&mut Adapter)->! {
    let(mut provider,mut dependent)=(Identity::new(),Identity::new());
    let mut pair=Pair::<Native<'_>>::new(&mut provider,&mut dependent,2,1);
    let mut native=Native {adapter,workers:[None;2],stopped:[false;2],first_exit:cfg!(pair_provider_loss),stop_error:false,close_error:false};
    require(matches!(pair.start_dependent(&mut native),Err(Error::Busy)) && native.adapter.clean(),1130);
    require(pair.start_provider(&mut native).is_ok(),1130);
    if cfg!(pair_provider_loss) {
        let mut lost=false;
        for _ in 0..100000 {
            match pair.provider_running(&mut native) {Ok(false)=>{lost=true;break;},Ok(true)=>adapter::yield_now(),_=>adapter::finish(1130)}
        }
        require(lost && matches!(pair.start_dependent(&mut native),Err(Error::Busy)),1130);
    }
    let mut restarted=false;
    for _ in 0..100000 {
        match pair.restart_provider(&mut native) {Ok(())=>{restarted=true;break;},Err(Error::Busy)=>adapter::yield_now(),_=>adapter::finish(1130)}
    }
    require(restarted && pair.start_dependent(&mut native).is_ok(),1130);
    require(matches!(pair.restart_provider(&mut native),Err(Error::Busy)),1130);
    native.stop_error=cfg!(pair_stop_error);native.close_error=cfg!(pair_cleanup_error);
    let mut complete=false;
    for _ in 0..100000 {
        match pair.shutdown(&mut native) {
            Ok(())=>{complete=true;break;},Err(Error::Busy)=>adapter::yield_now(),
            Err(Error::Backend(fault))=>{
                let provider=native.workers[0].unwrap_or_else(||adapter::finish(1130));
                require(native.adapter.observe(provider).is_ok_and(|o|o.terminal==0),1130);
                require(matches!(pair.start_provider(&mut native),Err(Error::Closed)) &&
                    matches!(pair.start_dependent(&mut native),Err(Error::Closed)),1130);
                match fault {
                    Fault::Known(e) if cfg!(pair_stop_error)=>{
                        require(e.operation==0x20007 && e.errno==13 && pair.phases()==(Phase::Live,Phase::Live),1130);
                        adapter::finish(1132);
                    },
                    Fault::Unknown(e) if cfg!(pair_cleanup_error)=>{
                        require(e.operation==0x24003 && e.errno==13 && pair.phases()==(Phase::Live,Phase::Unknown) &&
                            matches!(pair.shutdown(&mut native),Err(Error::Closed)),1130);
                        adapter::finish(1133);
                    },_=>adapter::finish(1130),
                }
            },_=>adapter::finish(1130),
        }
    }
    require(complete && pair.phases()==(Phase::Idle,Phase::Idle) && native.adapter.clean(),1130);
    require(pair.shutdown(&mut native).is_ok() && matches!(pair.start_provider(&mut native),Err(Error::Closed)),1130);
    adapter::finish(100)
}
