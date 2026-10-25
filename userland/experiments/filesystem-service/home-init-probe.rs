// SPDX-License-Identifier: BSD-2-Clause
//! Concrete constructor measurement root. Linked objects are never executed.
#![no_std]
use core::mem::MaybeUninit;
use filesystem_client::ConnectFailure;
use filesystem_remote_descriptors::ProcessFiles;
use filesystem_service::channel::Framed;
use home_init_transport::{native::Native, Endpoints};
type Channel = Framed<Endpoints<Native>>;
type Broker = ProcessFiles<Channel>;

#[no_mangle]
pub fn home_init(
    slot: &mut MaybeUninit<Broker>,
    channel: Channel,
    epoch: u64,
) -> Result<(), ConnectFailure> {
    ProcessFiles::connect_home_in_place(slot, channel, epoch).map(|_| ())
}
#[used]
#[no_mangle]
#[link_section = ".rodata.home_init_layout"]
pub static HOME_INIT_LAYOUT: [u64; 2] = [
    core::mem::size_of::<Broker>() as u64,
    core::mem::align_of::<Broker>() as u64,
];
