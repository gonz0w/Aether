// SPDX-License-Identifier: BSD-2-Clause
//! Inert policy for the one supported ABI22 topology; never a grant source.
use super::Role;
#[derive(Clone, Copy)]
pub struct Service {
    pub role: Role,
    pub image_slot: usize,
    pub order: usize,
    pub retries: u8,
}
// Ordering is tied to the existing protocol: provider, runner, admitted command.
// Only the explicit supervised profile permits one pre-effect command retry.
pub const SERVICES: [Service; 3] = validated([
    Service { role: Role::Backend, image_slot: 1, order: 0, retries: 0 },
    Service { role: Role::Runner, image_slot: 0, order: 1, retries: 0 },
    Service { role: Role::Command, image_slot: 2, order: 2, retries: if cfg!(init_supervised) { 1 } else { 0 } },
]);
pub const fn validated(services: [Service; 3]) -> [Service; 3] {
    let mut i = 0;
    while i < services.len() {
        let slot = match services[i].role {
            Role::Backend => 1,
            Role::Runner => 0,
            Role::Command => 2,
        };
        let order = match services[i].role {
            Role::Backend => 0,
            Role::Runner => 1,
            Role::Command => 2,
        };
        assert!(services[i].image_slot == slot, "role/image mismatch");
        assert!(services[i].order == i && order == i, "unsupported service order");
        let maximum = if cfg!(init_supervised) && matches!(services[i].role, Role::Command) { 1 } else { 0 };
        assert!(services[i].retries <= maximum, "unsupported automatic retry budget");
        i += 1;
    }
    services
}
pub fn image_slot(role: Role) -> usize {
    // Membership is established at compile time; no external input enters here.
    let order = match role { Role::Backend => 0, Role::Runner => 1, Role::Command => 2 };
    SERVICES[order].image_slot
}
