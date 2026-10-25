/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_REDIRECT_H
#define AETHER_FD_REDIRECT_H
#include "fd-table.h"
struct aefd_redirect_result {
    int64_t status, target_status, cleanup_status;
    int prepared_selector;
    int committed, target_attempted, target_removed, cleanup_attempted;
    int unresolved, unknown;
};
/* Exclusive, serialized, nonreentrant canonical map/client and trusted closer.
 * FILE source needs one free remote selector; no spare logical slot required.
 * Unresolved may be an unnamed allocation after lost dup. Receipt is not a
 * grant or native cleanup evidence. No retry/rollback after unknown; not POSIX
 * dup2. */
struct aefd_redirect_result aefd_redirect(struct aefd_bindings *,
                                          struct aefd_client *,
                                          const struct aefd_stream_closer *,
                                          int source, int target);
#endif
