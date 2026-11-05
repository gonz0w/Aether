/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual C result predicate; no filesystem, engine or guest execution. */
#include "home-native.h"
#include <assert.h>
#include <string.h>
static struct aether_fs_home_result active(void)
{
    struct aether_fs_home_result h = {0};
    h.version = 1;
    h.bytes = 320;
    h.flags = 63;
#ifdef AETHER_FS_HOME_COLD_REOPEN
    h.flags &= ~UINT64_C(2);
#endif
    h.service.ready = 1;
    h.service.requests = 20;
    return h;
}
static int valid(struct aether_fs_home_result h)
{
    int protocol = 0;
    int order = aether_fs_home_order_required(&h, &protocol);
#ifndef AETHER_FS_HOME_COLD_REOPEN
    assert(order || !(h.flags & AETHER_FS_HOME_ACTIVATION));
#else
    assert(order || !protocol);
#endif
    return !protocol;
}
int main(void)
{
    struct aether_fs_home_result h = active();
#ifdef AETHER_FS_HOME_COLD_REOPEN
    assert(valid(h));
    for (unsigned i = 0; i < 2; ++i) {
        for (unsigned byte = 0; byte < sizeof(h.mkdir); ++byte) {
            h = active();
            unsigned char *r = (unsigned char *)(i ? &h.create : &h.mkdir);
            r[byte] = 1;
            assert(!valid(h));
        }
    }
    for (unsigned calls = 1; calls <= 9; ++calls) {
        h = active();
        h.mutation_attempts = calls;
        assert(!valid(h));
    }
    const unsigned phases[] = {2, 3, 5, 7, 8};
    for (unsigned i = 0; i < sizeof(phases) / sizeof(phases[0]); ++i) {
        memset(&h, 0, sizeof(h));
        h.version = 1;
        h.bytes = 320;
        h.flags = 60;
        h.phase = phases[i];
        h.error_kind = 10;
        h.error_value = 5;
        assert(valid(h));
        h.flags |= AETHER_FS_HOME_ORDER_REQUIRED;
        assert(!valid(h));
    }
    for (unsigned p = 4; p <= 6; p += 2) {
        memset(&h, 0, sizeof(h));
        h.version = 1;
        h.bytes = 320;
        h.flags = 60;
        h.phase = p;
        h.error_kind = 10;
        h.error_value = 5;
        assert(!valid(h));
    }
#else
    assert(
        !valid(h)); /* Cold carrier cannot be relabelled as old activation. */
#endif
    h = active();
    h.mutation_attempts = 7;
    h.mkdir = (struct aether_fs_bootstrap_receipt){.provider = 1,
                                                   .returned = 1,
                                                   .returned_txg = 788,
                                                   .returned_state = 2,
                                                   .provider_txg = 788,
                                                   .provider_state = 2};
    h.create = h.mkdir;
    h.create.returned_txg = h.create.provider_txg = 789;
#ifdef AETHER_FS_HOME_COLD_REOPEN
    assert(!valid(h));
#else
    assert(valid(h));
#endif
    return 0;
}
