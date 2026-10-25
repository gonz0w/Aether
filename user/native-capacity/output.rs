// SPDX-License-Identifier: BSD-2-Clause
//! Private bounded capture granted only to the final pipeline participant.
pub struct Output {
    generation: u32,
    #[cfg(not(pipeline_serial))]
    bytes: [u8; 32],
    #[cfg(not(pipeline_serial))]
    used: usize,
    holders: [bool; 4],
    #[cfg(not(pipeline_serial))]
    denied: usize,
    #[cfg(pipeline_stdio)]
    standard: Standard,
}
fn word(frame: &[u8; 32], offset: usize) -> u32 {
    u32::from_le_bytes(frame[offset..offset + 4].try_into().unwrap())
}
// Frame storage stays live for this synchronous trap; no pointer is retained.
#[cfg(pipeline_serial)]
#[inline(never)]
fn serial(read: bool, pointer: u64, length: usize) -> i32 {
    let result = super::call(
        if read { 0x26000 } else { 0x26001 },
        if cfg!(pipeline_serial_bad_grant) {
            0xf002
        } else {
            0xf001
        },
        pointer,
        length.min(1) as u64, // Exercise real short-count handling without a queue.
        0,
        0,
        0,
    )
    .0;
    super::check(
        result == -11 || (result >= 0 && result as usize <= length),
        2795,
    );
    super::check(!read || length == 0 || result != 0, 2795);
    result as i32
}
impl Output {
    pub fn new(generation: u32) -> Self {
        Self {
            generation,
            #[cfg(not(pipeline_serial))]
            bytes: [0; 32],
            #[cfg(not(pipeline_serial))]
            used: 0,
            holders: if cfg!(pipeline_stdout_inherit) {
                [true, false, false, false]
            } else {
                [false, false, false, true]
            },
            #[cfg(not(pipeline_serial))]
            denied: 0,
            #[cfg(pipeline_stdio)]
            standard: Standard::new(),
        }
    }
    pub fn request(&mut self, participant: usize, frame: &[u8; 32]) -> [u8; 32] {
        self.request_as(participant + 1, frame)
    }
    pub fn close_parent(&mut self, frame: &[u8; 32]) -> [u8; 32] {
        self.request_as(0, frame)
    }
    pub fn stage(&mut self, slot: usize, inherited: bool) -> bool {
        if !(1..4).contains(&slot) || self.holders[slot] || inherited != self.holders[0] {
            return false;
        }
        self.holders[slot] = inherited;
        true
    }
    pub fn commit(&mut self, slot: usize, before: bool, after: bool) -> bool {
        if !(1..4).contains(&slot) || self.holders[slot] != before || (after && !before) {
            return false;
        }
        self.holders[slot] = after || (cfg!(pipeline_stdout_retain) && slot == 1);
        true
    }
    fn request_as(&mut self, who: usize, frame: &[u8; 32]) -> [u8; 32] {
        #[cfg(pipeline_stdio)]
        if word(frame, 8) != 1 {
            return self.standard.request(who, self.generation, frame);
        }
        let op = word(frame, 0);
        let n = word(frame, 12) as usize;
        let result: i32 = if who >= 4
            || !self.holders[who]
            || word(frame, 4) != 0x7a010000 | self.generation
            || word(frame, 8) != 1
        {
            #[cfg(not(pipeline_serial))]
            {
                self.denied += 1;
            }
            -13
        } else if !(op == 2 || op == 3)
            || n > 16
            || (op == 3 && n != 0)
            || frame[16 + n..] != [0; 16][..16 - n]
        {
            -22
        } else if op == 3 {
            self.holders[who] = false;
            0
        } else {
            #[cfg(pipeline_serial)]
            {
                // Deliberate test-only corruption; the host must reject real UART bytes.
                #[cfg(pipeline_serial_bad_byte)]
                let byte = if frame[16] == b'p' { b'P' } else { frame[16] };
                #[cfg(pipeline_serial_bad_byte)]
                let pointer = &byte as *const u8 as u64;
                #[cfg(not(pipeline_serial_bad_byte))]
                let pointer = frame[16..].as_ptr() as u64;
                serial(false, pointer, n)
            }
            #[cfg(not(pipeline_serial))]
            {
                if n > self.bytes.len() - self.used {
                    -28
                } else {
                    if n > 0 && !cfg!(pipeline_stdout_drop) {
                        self.bytes[self.used..self.used + n].copy_from_slice(&frame[16..16 + n]);
                        self.used += n;
                    }
                    n as i32
                }
            }
        };
        let mut reply = [0; 32];
        reply[..4].copy_from_slice(&result.to_le_bytes());
        reply
    }
    #[cfg(pipeline_exec_overlap_stop)]
    pub(super) fn stopped_reader(&mut self) {
        // Caller has confirmed slot4 terminal; no live request borrows these grants.
        self.holders[3] = false;
        self.standard.holders[3] = [false; 2];
    }

    pub fn complete(&self) -> bool {
        #[cfg(pipeline_stdio)]
        if !self.standard.complete() {
            return false;
        }
        #[cfg(pipeline_serial)]
        {
            return self.holders == [false; 4];
        }
        #[cfg(not(pipeline_serial))]
        {
            if cfg!(pipeline_shell_early) {
                return self.holders == [false; 4]
                    && self.used == 9
                    && self.bytes[..9] == *b"epipe ok\n"
                    && self.bytes[9..] == [0; 23]
                    && self.denied == 0;
            }
            self.holders == [false; 4]
                && self.used
                    == if cfg!(pipeline_exec_overlap_stop) {
                        0
                    } else {
                        10
                    }
                && self.bytes[..10]
                    == if cfg!(pipeline_exec_overlap_stop) {
                        [0; 10]
                    } else {
                        *b"pipe data\n"
                    }
                && self.bytes[10..] == [0; 22]
                && self.denied == if cfg!(pipeline_dash_parent) { 0 } else { 1 }
        }
    }
}

#[cfg(pipeline_stdio)]
impl Output {
    pub fn stage_standard(&mut self, slot: usize, before: [bool; 2]) -> bool {
        if !(1..4).contains(&slot)
            || self.standard.holders[slot] != [false; 2]
            || before != self.standard.holders[0]
        {
            return false;
        }
        self.standard.holders[slot] = before;
        true
    }
    pub fn commit_standard(&mut self, slot: usize, before: [bool; 2], after: [bool; 2]) -> bool {
        if !(1..4).contains(&slot)
            || self.standard.holders[slot] != before
            || (0..2).any(|i| after[i] && !before[i])
        {
            return false;
        }
        self.standard.holders[slot] = after;
        if cfg!(pipeline_stdin_retain) && slot == 2 {
            self.standard.holders[slot][0] = true;
        }
        true
    }
}
#[cfg(pipeline_stdio)]
struct Standard {
    holders: [[bool; 2]; 4],
    #[cfg(not(pipeline_serial))]
    input_pos: usize,
    #[cfg(not(pipeline_serial))]
    eof: bool,
    #[cfg(not(pipeline_serial))]
    errors: [u8; 32],
    #[cfg(not(pipeline_serial))]
    used: usize,
    #[cfg(not(pipeline_serial))]
    denied: usize,
}
#[cfg(pipeline_stdio)]
impl Standard {
    fn new() -> Self {
        Self {
            holders: [[true; 2], [false; 2], [false; 2], [false; 2]],
            #[cfg(not(pipeline_serial))]
            input_pos: 0,
            #[cfg(not(pipeline_serial))]
            eof: false,
            #[cfg(not(pipeline_serial))]
            errors: [0; 32],
            #[cfg(not(pipeline_serial))]
            used: 0,
            #[cfg(not(pipeline_serial))]
            denied: 0,
        }
    }
    fn request(&mut self, who: usize, generation: u32, frame: &[u8; 32]) -> [u8; 32] {
        let op = word(frame, 0);
        let binding = word(frame, 8);
        let end = (binding / 2) as usize;
        let n = word(frame, 12) as usize;
        let mut reply = [0; 32];
        let result: i32 = if who >= 4
            || !(binding == 0 || binding == 2)
            || word(frame, 4) != (0x7a000000 | (binding << 16) | generation)
            || !self.holders[who][end]
        {
            #[cfg(not(pipeline_serial))]
            {
                self.denied += 1;
            }
            -13
        } else if n > 16
            || !(op == 3 || (binding == 0 && op == 1) || (binding == 2 && op == 2))
            || (op == 3 && n != 0)
            || frame[16 + if op == 2 { n } else { 0 }..]
                .iter()
                .any(|b| *b != 0)
        {
            -22
        } else if op == 3 {
            self.holders[who][end] = false;
            0
        } else if binding == 0 {
            #[cfg(pipeline_serial)]
            {
                serial(true, reply[16..].as_mut_ptr() as u64, n)
            }
            #[cfg(not(pipeline_serial))]
            {
                let count = n.min(10 - self.input_pos);
                reply[16..16 + count]
                    .copy_from_slice(&b"pipe data\n"[self.input_pos..self.input_pos + count]);
                self.input_pos += count;
                if n > 0 && count == 0 {
                    self.eof = true;
                }
                count as i32
            }
        } else {
            #[cfg(pipeline_serial)]
            {
                serial(false, frame[16..].as_ptr() as u64, n)
            }
            #[cfg(not(pipeline_serial))]
            {
                if n > 32 - self.used {
                    -28
                } else {
                    if n > 0 && !cfg!(pipeline_stderr_drop) {
                        self.errors[self.used..self.used + n].copy_from_slice(&frame[16..16 + n]);
                        self.used += n;
                    }
                    n as i32
                }
            }
        };
        reply[..4].copy_from_slice(&result.to_le_bytes());
        reply
    }
    fn complete(&self) -> bool {
        #[cfg(pipeline_serial)]
        {
            return self.holders == [[false; 2]; 4];
        }
        #[cfg(not(pipeline_serial))]
        {
            if cfg!(pipeline_dash_parent) {
                return self.holders == [[false; 2]; 4]
                    && self.input_pos == 0
                    && !self.eof
                    && self.denied == 0
                    && self.used == 0
                    && self.errors == [0; 32];
            }
            self.holders == [[false; 2]; 4]
                && self.input_pos == 10
                && self.eof
                && self.denied == 1
                && self.used
                    == if cfg!(pipeline_exec_overlap_stop) {
                        2
                    } else {
                        3
                    }
                && (if cfg!(pipeline_exec_overlap_stop) {
                    &b"23"[..]
                } else {
                    &b"234"[..]
                })
                .iter()
                .all(|b| self.errors[..3].contains(b))
                && self.errors[3..] == [0; 29]
        }
    }
}
