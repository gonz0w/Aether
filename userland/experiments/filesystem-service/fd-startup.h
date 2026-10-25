/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_STARTUP_H
#define AETHER_FD_STARTUP_H
#include "fd-context.h"
#include "startup-identity-vendor.h"
#define AEFD_STARTUP_BYTES 304U
struct aefd_startup_auxv {
    uint64_t memory, input, output;
};
/* Fresh zeroed, stable exclusive storage outside init stack. No other greeting
 * consumer. All supplied observations/transport must be actual delegated native
 * inputs; injected calls exist for host qualification only. No copy/rebase or
 * old-profile fallback. Successful startup transfers endpoint borrows to
 * context.
 */
struct aefd_startup {
    struct aefd_context context;
    struct aether_fs_session_identity identity;
    unsigned char scratch[AEFD_STARTUP_BYTES];
    int phase, close_attempted;
    int64_t status;
    struct aefd_close_result closed;
};
int64_t aefd_startup_start(struct aefd_startup *, aefd_native_call, void *,
                           struct aefd_startup_auxv);
/* Target entry obtains auxv and uses int81 PID/PPID/channel/mask observations.
 * This is not yet called by the selected ABI29 shell or a matching dispatcher.
 */
int64_t aefd_startup_native(struct aefd_startup *);
#endif
