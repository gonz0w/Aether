// SPDX-License-Identifier: BSD-2-Clause
//! Integer-only private AF09 carriers, shared by the entry and executable owner.
pub const ACTIVATION: u64 = 1;
pub const ORDERED: u64 = 2;
pub const ACCEPTED: u64 = 4;
pub const CLOSE_ATTEMPTED: u64 = 8;
pub const CALLBACK: u64 = 16;
pub const ENTRY: u64 = 32;
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct BootstrapReceipt {
    pub provider: u64,
    pub returned: u64,
    pub error_kind: u64,
    pub error_value: i64,
    pub returned_error: i64,
    pub returned_txg: u64,
    pub returned_staged: u64,
    pub returned_state: u64,
    pub provider_error: i64,
    pub provider_txg: u64,
    pub provider_staged: u64,
    pub provider_state: u64,
}
impl BootstrapReceipt {
    pub fn is_zero(&self) -> bool {
        self.provider
            | self.returned
            | self.error_kind
            | self.returned_txg
            | self.returned_staged
            | self.returned_state
            | self.provider_txg
            | self.provider_staged
            | self.provider_state
            == 0
            && self.error_value == 0
            && self.returned_error == 0
            && self.provider_error == 0
    }
    pub fn requires_ordering(&self) -> bool {
        match self.provider {
            0 => false,
            1 => {
                !(self.provider_error > 0
                    && self.provider_error <= 4095
                    && self.provider_txg == 0
                    && self.provider_staged == 0
                    && self.provider_state == 0)
            }
            _ => true,
        }
    }
    pub fn valid(&self) -> bool {
        if self.returned == 0 {
            return self.is_zero();
        }
        if self.provider > 2 || self.returned > 2 || self.error_kind > 16 {
            return false;
        }
        if self.provider != 1
            && (self.provider_error != 0
                || self.provider_txg | self.provider_staged | self.provider_state != 0)
        {
            return false;
        }
        if self.returned == 1 {
            return self.provider == 1
                && self.error_kind == 0
                && self.error_value == 0
                && self.returned_error == 0
                && self.returned_txg != 0
                && self.returned_staged == 0
                && self.returned_state == 2
                && self.returned_txg == self.provider_txg
                && self.provider_error == 0
                && self.provider_staged == 0
                && self.provider_state == 2;
        }
        if self.error_kind == 0 || (self.error_kind != 10 && self.error_value != 0) {
            return false;
        }
        if self.error_kind != 15
            && (self.returned_error != 0
                || self.returned_txg | self.returned_staged | self.returned_state != 0)
        {
            return false;
        }
        if self.error_kind == 10 && i32::try_from(self.error_value).is_err() {
            return false;
        }
        match self.provider {
            0 => !matches!(self.error_kind, 9 | 14 | 15),
            2 => self.error_kind == 14,
            1 => {
                if self.provider_staged != 0 {
                    return self.error_kind == 9;
                }
                if self.provider_error == 0 && self.provider_state == 2 && self.provider_txg != 0 {
                    return self.error_kind == 15
                        && self.returned_error == 5
                        && self.returned_txg == self.provider_txg
                        && self.returned_staged == 0
                        && self.returned_state == 2;
                }
                if (1..=4095).contains(&self.provider_error) {
                    if self.provider_state == 0 && self.provider_txg == 0 {
                        return self.error_kind == 10 && self.error_value == self.provider_error;
                    }
                    if self.provider_state == 1
                        || self.provider_state == 2 && self.provider_txg != 0
                    {
                        return self.error_kind == 15
                            && self.returned_error == self.provider_error
                            && self.returned_txg == self.provider_txg
                            && self.returned_staged == 0
                            && self.returned_state == self.provider_state;
                    }
                }
                self.error_kind == 9
            }
            _ => false,
        }
    }
}
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct ServiceResult {
    pub ready: u64,
    pub requests: u64,
    pub stop: u64,
    pub reader_close: i64,
    pub writer_close: i64,
    pub error: i64,
    pub txg: u64,
    pub bytes_staged: u64,
    pub state: u64,
}
impl ServiceResult {
    pub fn is_zero(&self) -> bool {
        self.ready | self.requests | self.stop | self.txg | self.bytes_staged | self.state == 0
            && self.reader_close == 0
            && self.writer_close == 0
            && self.error == 0
    }
}
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct HomeResult {
    pub version: u64,
    pub bytes: u64,
    pub phase: u64,
    pub error_kind: u64,
    pub error_value: i64,
    pub flags: u64,
    pub mutation_attempts: u64,
    pub mkdir: BootstrapReceipt,
    pub create: BootstrapReceipt,
    pub service: ServiceResult,
}
impl HomeResult {
    pub const fn initial() -> Self {
        Self {
            version: 1,
            bytes: 320,
            phase: 0,
            error_kind: 0,
            error_value: 0,
            flags: 0,
            mutation_attempts: 0,
            mkdir: BootstrapReceipt {
                provider: 0,
                returned: 0,
                error_kind: 0,
                error_value: 0,
                returned_error: 0,
                returned_txg: 0,
                returned_staged: 0,
                returned_state: 0,
                provider_error: 0,
                provider_txg: 0,
                provider_staged: 0,
                provider_state: 0,
            },
            create: BootstrapReceipt {
                provider: 0,
                returned: 0,
                error_kind: 0,
                error_value: 0,
                returned_error: 0,
                returned_txg: 0,
                returned_staged: 0,
                returned_state: 0,
                provider_error: 0,
                provider_txg: 0,
                provider_staged: 0,
                provider_state: 0,
            },
            service: ServiceResult {
                ready: 0,
                requests: 0,
                stop: 0,
                reader_close: 0,
                writer_close: 0,
                error: 0,
                txg: 0,
                bytes_staged: 0,
                state: 0,
            },
        }
    }
    pub fn canonical_initial(&self, callback_allowed: bool) -> bool {
        self.version == 1
            && self.bytes == 320
            && self.phase == 0
            && self.error_kind == 0
            && self.error_value == 0
            && (self.flags == 0 || callback_allowed && self.flags == CALLBACK)
            && self.mutation_attempts == 0
            && self.mkdir.is_zero()
            && self.create.is_zero()
            && self.service.is_zero()
    }
    pub fn canonical_unaccepted(&self) -> bool {
        self.version == 1
            && self.bytes == 320
            && self.phase == 1
            && self.error_kind == 1
            && self.error_value == 0
            && matches!(self.flags, ENTRY | 48)
            && self.mutation_attempts == 0
            && self.mkdir.is_zero()
            && self.create.is_zero()
            && self.service.is_zero()
    }
    pub fn requires_ordering(&self) -> bool {
        self.flags & ACTIVATION != 0
            || self.mkdir.requires_ordering()
            || self.create.requires_ordering()
    }
    pub fn valid(&self) -> bool {
        if self.canonical_unaccepted() {
            return true;
        }
        if self.version != 1
            || self.bytes != 320
            || self.flags & !63 != 0
            || self.flags & (ENTRY | ACCEPTED | CLOSE_ATTEMPTED)
                != ENTRY | ACCEPTED | CLOSE_ATTEMPTED
            || self.phase > 9
            || self.error_kind > 16
            || self.mutation_attempts > 9
            || !self.mkdir.valid()
            || !self.create.valid()
        {
            return false;
        }
        if self.phase == 0 && (self.error_kind != 0 || self.error_value != 0)
            || self.phase != 0 && self.error_kind == 0
            || self.error_kind != 10 && self.error_value != 0
        {
            return false;
        }
        if self.create.returned != 0 && self.mkdir.returned != 1 {
            return false;
        }
        let attempts = u64::from(self.mkdir.provider != 0) + u64::from(self.create.provider != 0);
        if self.mutation_attempts < attempts
            || self.requires_ordering() != (self.flags & ORDERED != 0)
        {
            return false;
        }
        let active = self.flags & ACTIVATION != 0;
        let phase_valid = match self.phase {
            0 => active && self.service.stop != 4,
            2 | 3 => !active && self.mkdir.is_zero() && self.create.is_zero(),
            4 => {
                !active
                    && self.mkdir.returned == 2
                    && self.create.is_zero()
                    && self.error_kind == self.mkdir.error_kind
                    && self.error_value == self.mkdir.error_value
            }
            5 => !active && self.mkdir.returned == 1 && self.create.is_zero(),
            6 => {
                !active
                    && self.mkdir.returned == 1
                    && self.create.returned == 2
                    && self.error_kind == self.create.error_kind
                    && self.error_value == self.create.error_value
            }
            7 | 8 => !active && self.mkdir.returned == 1 && self.create.returned == 1,
            9 => active && self.service.stop == 4,
            _ => false,
        };
        if !phase_valid
            || (!active && self.mutation_attempts != attempts)
            || self.error_kind == 10 && i32::try_from(self.error_value).is_err()
        {
            return false;
        }
        if self.flags & ACTIVATION != 0 {
            if self.mkdir.returned != 1 || self.create.returned != 1 || !matches!(self.phase, 0 | 9)
            {
                return false;
            }
        } else if self.service.ready
            | self.service.requests
            | self.service.stop
            | self.service.txg
            | self.service.bytes_staged
            | self.service.state
            != 0
            || self.service.error != 0
        {
            return false;
        }
        if self.service.ready > 1
            || self.service.requests > 96
            || self.service.stop > 6
            || self.service.bytes_staged > 4096
            || self.service.state > 3
            || self.service.state == 0 && (self.service.txg != 0 || self.service.bytes_staged != 0)
            || self.service.state == 2 && self.service.txg == 0
            || self.service.state != 0 && (self.service.ready != 1 || self.service.requests == 0)
            || self.service.state == 1
                && (!matches!(self.service.stop, 2 | 5) || self.service.error == 0)
            || self.service.ready == 0 && self.service.requests != 0
            || active && self.mutation_attempts > 2 + self.service.requests
            || self.service.stop == 3 && self.service.requests != 96
            || self.service.state == 3
                && (self.service.ready != 1
                    || self.service.requests == 0
                    || !matches!(self.service.stop, 2 | 5)
                    || self.service.error == 0
                    || self.service.txg != 0
                    || self.service.bytes_staged != 0)
        {
            return false;
        }
        true
    }
}
#[repr(C)]
#[derive(Default)]
pub struct HomeLaunchState {
    pub version: u64,
    pub bytes: u64,
    pub reader: u64,
    pub writer: u64,
    pub phases: u64,
    pub engine_error: i64,
    pub home: HomeResult,
    pub startup_reader_close: i64,
    pub startup_writer_close: i64,
}
const _: () = assert!(
    core::mem::size_of::<BootstrapReceipt>() == 96
        && core::mem::align_of::<BootstrapReceipt>() == 8
);
const _: () = assert!(core::mem::size_of::<ServiceResult>() == 72);
const _: () =
    assert!(core::mem::size_of::<HomeResult>() == 320 && core::mem::align_of::<HomeResult>() == 8);
const _: () = assert!(
    core::mem::offset_of!(HomeResult, mkdir) == 56
        && core::mem::offset_of!(HomeResult, create) == 152
        && core::mem::offset_of!(HomeResult, service) == 248
);
const _: () = assert!(
    core::mem::size_of::<HomeLaunchState>() == 384 && core::mem::align_of::<HomeLaunchState>() == 8
);
const _: () = assert!(
    core::mem::offset_of!(HomeLaunchState, home) == 48
        && core::mem::offset_of!(HomeLaunchState, startup_reader_close) == 368
        && core::mem::offset_of!(HomeLaunchState, startup_writer_close) == 376
);
