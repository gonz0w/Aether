// SPDX-License-Identifier: BSD-2-Clause
//! Private shared stream mechanics. The caller owns bounds and authentication.

pub trait Steps {
    fn transfer(&mut self, writing: bool, bytes: &mut [u8]) -> i64;
    fn wait(&mut self, writing: bool) -> i64;
}

/// Advance only confirmed prefixes. A failed partial reply must never be replayed.
pub fn transfer(steps: &mut impl Steps, bytes: &mut [u8], writing: bool) -> Result<(), i64> {
    let mut at = 0;
    while at < bytes.len() {
        let count = (bytes.len() - at).min(16);
        let result = steps.transfer(writing, &mut bytes[at..at + count]);
        if result == -11 {
            let status = steps.wait(writing);
            if status != 0 {
                return Err(if status < 0 { status } else { -5 });
            }
        } else if result <= 0 || result as u64 > count as u64 {
            return Err(if result < 0 { result } else { -5 });
        } else {
            at += result as usize;
        }
    }
    Ok(())
}
