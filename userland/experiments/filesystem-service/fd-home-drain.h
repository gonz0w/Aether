/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_HOME_DRAIN_H
#define AETHER_FD_HOME_DRAIN_H
#include "fd-exec.h"
#include "fd-home-probe-adapter.h"

/* Private diagnostic IDs, matching NATIVE-AF09-DRAIN.md; never peer authority.
 */
#define AEFD_DRAIN_FILE_PREFIX 1U
#define AEFD_DRAIN_EXEC_PREFIX 2U
#define AEFD_DRAIN_FORK_PREFIX 3U
#define AEFD_DRAIN_STREAM 4U
#define AEFD_DRAIN_NO_ACK 5U
#define AEFD_DRAIN_PARTIAL_ACK 6U
#define AEFD_DRAIN_EXIT_DEADLINE 7U
#define AEFD_DRAIN_PENDING_FRAGMENT 8U

/* Stable private process storage, inherited by the actual copy. Full reference
 * bytes remain initialized and retained; only bytes[0..32] are ever submitted.
 * The fork reference is captured from the real parent before fork, and never
 * claims that child slot2 has nested-fork authority. */
struct aefd_home_drain {
    unsigned char bytes[608];
    size_t length;
};
/* Build from one live admitted context and its actual observations/FDs. A fork
 * reference requires parent slot1; all other references require child slot2.
 * This is inert data construction, not request dispatch or authority admission.
 * Storage/FD pair must be disjoint from the stable fork aggregate. */
int aefd_home_drain_reference(struct aefd_fork *, struct aefd_home_drain *,
                              unsigned case_id, int file, const int pair[2],
                              struct aefd_startup_auxv);
/* Ordinary pipe/fork, explicit native READY, exactly two checked write16 calls.
 * Success never returns: parent exits directly and child yields indefinitely.
 * Nonzero means fixture failure; caller must fail-stop, not claim settlement.
 */
int aefd_home_drain_run(struct aefd_fork *, unsigned case_id);
#endif
