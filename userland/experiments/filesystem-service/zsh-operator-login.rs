// SPDX-License-Identifier: BSD-2-Clause
//! Local pre-effect credits from the actual sole description ledger; no wire lease.
use super::*;

impl<T: Channel> Files<T> {
    /// Every live source description closes once, independent of its aliases.
    /// The permanent terminfo object and disconnect need one request each.
    pub fn shutdown_budget(&self) -> u32 {
        2 + u32::from(self.file_exec_held())
            + self.descriptions.descriptions.iter().flatten().count() as u32
    }
    /// Caller has already authenticated the settled parent and previous child.
    /// A later snapshot reopens/validates in4 operations then acquires/closes in5.
    pub fn fork_budget(&self, epoch: u8) -> u32 {
        self.shutdown_budget() + if epoch == 0 { 5 } else { 9 }
    }
    pub(super) fn operation_budget(
        &self,
        view: usize,
        raw: &[u8; FRAME],
        workspace: &[u8; PAYLOAD],
    ) -> u32 {
        let op = word(raw, 1);
        let a = word(raw, 4);
        let b = word(raw, 5) as usize;
        // While a child is admitted, unrelated FILE/CWD calls cannot consume
        // the already-funded acquire/revalidation cycle. Its existing exact
        // binding and monotonic attempt marker own this outstanding credit.
        let shutdown = self.shutdown_budget() + self.file_exec_credit();
        // A close spends its own reserved source close, never an extra credit.
        if op == 5 {
            return shutdown;
        }
        let completion = self.note_completion_credit();
        let cost = match op {
            #[cfg(native_zsh_operator_note)]
            1 if workspace[..b] == *operator_note::ENTRY => 2,
            1 if workspace[..b] == *home_redirection::ENTRY || workspace[..b] == *b".zprofile" => {
                // Lookup, new description's close,16 one-byte reads and EOF.
                19
            }
            // Four canonical lookups and three intermediate closes; a wrong-kind
            // final object adds a close. ACCESS also closes a successful final file.
            1 => 9,
            8 => 9,
            2 if b == 0 => 0,
            2 if self.note_read_uses_credit(view, a as i32) => 0,
            2 | 9 | 10 | 13 => 1,
            3 if word(raw, 6) == 2 => 1,
            _ => 0,
        };
        shutdown + completion + cost
    }
}
