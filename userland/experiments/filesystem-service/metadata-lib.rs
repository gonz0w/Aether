// SPDX-License-Identifier: BSD-2-Clause
//! Separate no_std wrapper retaining the qualified borrowed binding unchanged.
#![no_std]
#[path = "metadata.rs"]
mod binding;
pub use binding::*;
