/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_NATIVE_H
#define AETHER_FD_NATIVE_H
#include "fd-session.h"

struct aefd_native_source {
    uint32_t reference, selector, rights, bound;
};
/* Native-call injection is for qualification only. Production uses the x86-64
 * int81 backend. Endpoints/records must come from authenticated owner startup;
 * this constructor validates labels and never authenticates or consumes
 * greeting. Fresh zeroed, stable exclusive storage, disjoint borrows, no
 * reinitialization.
 */
typedef int64_t (*aefd_native_call)(void *, uint64_t, uint64_t, uint64_t,
                                    uint64_t, uint64_t);
struct aefd_native {
    aefd_native_call call;
    void *context;
    uint64_t input, output, saved_mask;
    struct aefd_native_source sources[7];
    unsigned generations[2];
    uint32_t factory;
    int initialized, retired, active, busy, closed;
    struct aefd_close_result receipt;
};
int aefd_native_init(struct aefd_native *, aefd_native_call, void *, uint64_t,
                     uint64_t, const struct aefd_native_source[7],
                     const unsigned generations[2], uint32_t factory);
struct aefd_io aefd_native_io(struct aefd_native *);
struct aefd_adapters aefd_native_adapters(struct aefd_native *);
/* Guard the ENTIRE session operation, including all redirect prepare/cleanup
 * RPCs, snapshot/finish where relevant. No per-callback substitute. A failed
 * enter performs no command. Leave restores mask even after retirement; restore
 * failure closes transport and exits125 (trap if native exit returns).
 */
int64_t aefd_native_enter(struct aefd_native *);
void aefd_native_leave(struct aefd_native *);
/* Target-only implementation; native authority remains enforced by
 * kernel/owner. */
int64_t aefd_native_trap(void *, uint64_t, uint64_t, uint64_t, uint64_t,
                         uint64_t);
#endif
