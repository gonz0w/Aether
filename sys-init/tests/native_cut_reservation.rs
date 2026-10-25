// SPDX-License-Identifier: BSD-2-Clause
//! Host logic tests and native-target compile entry; no native consumer invocation.
#![cfg_attr(not(test), no_std)]
#[path = "../prototypes/native-supervisor/cut_reservation.rs"]
mod cut_reservation;
