/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_REPLACE_H
#define AETHER_FD_REPLACE_H
#include "fd-table.h"
/* Stream-only chosen-target replacement; FILE endpoints return -38.
 * Same exclusive/nonreentrant map/client/adapter contracts as mixed close.
 * Distinct success resets target cloexec; self preserves it. Consumed close
 * error leaves target empty; unknown retires admission with prior metadata.
 * Not atomic POSIX dup2 or native capability duplication. */
int64_t aefd_stream_replace(struct aefd_bindings *, struct aefd_client *,
                            const struct aefd_stream_closer *, int source,
                            int target);
#ifdef AEFD_DUP2_WIRE
/* Exact selected mixed-table replacement under the context guard. Unknown
 * outcomes retire; public binding must terminate rather than resume. */
int64_t aefd_dup2(struct aefd_bindings *, struct aefd_client *,
                  const struct aefd_stream_closer *, int source, int target);
#endif
#endif
