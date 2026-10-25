// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
//! Trusted owner-side mechanisms. Labels never confer native authority.
use af07_transport::Kernel;
pub type Status = (i64, u64, u64);
pub trait Control: Kernel + Clone {
    fn ctl(&mut self, op: u64, handle: u64, argument: u64) -> Status;
    fn engine(&mut self, reader: u64, writer: u64) -> i64;
    fn delegate(&mut self, engine: u64, region: &[u64; 3]) -> i64;
    fn launch(&mut self, arguments: &[u8; 272], reader: u64, writer: u64) -> i64;
    fn copy(&mut self, parent: u64, slot: u32, token: u64, reader: u64, writer: u64) -> i64;
    fn serial(&mut self, writing: bool, bytes: &mut [u8]) -> i64;
    fn exec(&mut self, process: u64, token: u64, arguments: &[u8; 272]) -> i64;
    fn receipt(&mut self, process: u64) -> Status;
    fn publish(&mut self, process: u64, token: u64) -> i64;
}
#[cfg(target_os = "none")]
#[path = "native_owner_control.rs"]
mod native;
