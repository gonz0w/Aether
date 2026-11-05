/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual generated importer/engine and selected order-check body; host stubs
 * observe lifecycle calls, never OpenZFS data or native I/O. */
#define main retained_lifecycle_main
#define aether_fs_home_launch_serve retained_callback
#define aether_pool_hooks_check_ordered retained_order_check
#include "home-native-lifecycle-tests.c"
#undef main
#undef aether_fs_home_launch_serve
#undef aether_pool_hooks_check_ordered
#include <assert.h>
#include <stdatomic.h>
#include "pool-witness.h"
#define POOL_GRAPH_SLOTS 64
static _Atomic uint64_t pool_synced, pool_completed, pool_epoch;
static struct {
    _Atomic uint64_t txg;
} pool_record;
static struct {
    _Atomic uintptr_t address;
} pool_nodes[POOL_GRAPH_SLOTS];
static int pool_exclusive(void) { return 1; }
static void pool_release(void) {}
unsigned aether_pool_hooks_check(uint64_t txg)
{
    (void)txg;
    return 0;
}
#define aether_pool_hooks_check_ordered selected_actual_order_check
#include "cold-selected-ordered-body.inc"
#undef aether_pool_hooks_check_ordered
unsigned aether_pool_hooks_check_ordered(void)
{
    assert(exported && closed);
    ++ordered;
    return selected_actual_order_check();
}
static unsigned cold_case;
static struct aether_fs_home_result healthy(void)
{
    struct aether_fs_home_result h = {0};
    h.version = 1;
    h.bytes = 320;
    h.flags = 61;
    h.service.ready = 1;
    h.service.requests = 20;
    return h;
}
#ifdef AETHER_FS_HOME_COLD_REOPEN
static void corrupt(struct aether_fs_home_result *h, unsigned which)
{
    switch (which) {
    case 1:
        h->mutation_attempts = 1;
        break;
    case 2:
        success(&h->mkdir);
        break;
    case 3:
        success(&h->create);
        break;
    case 4:
        h->service.txg = 800;
        break;
    case 5:
        h->service.bytes_staged = 1;
        break;
    case 6:
        h->service.state = 2;
        break;
    case 7:
        h->service.state = 1;
        break;
    case 8:
        h->service.stop = 2;
        h->service.error = -5;
        break;
    case 9:
        h->service.reader_close = -5;
        break;
    case 10:
        h->service.writer_close = -5;
        break;
    case 11:
        h->service.ready = 0;
        break;
    case 12:
        h->service.requests = 0;
        break;
    case 13:
        h->service.requests = 97;
        break;
    case 14:
        h->service.error = -5;
        break;
    case 15:
        h->phase = 9;
        h->error_kind = 11;
        break;
    case 16:
        h->error_kind = 11;
        break;
    case 17:
        h->error_value = 5;
        break;
    case 18:
        h->version = 2;
        break;
    case 19:
        h->bytes = 319;
        break;
    case 20:
        h->flags |= 64;
        break;
    case 21:
        h->flags &= ~UINT64_C(1);
        break;
    case 22:
        h->flags &= ~UINT64_C(4);
        break;
    case 23:
        h->flags &= ~UINT64_C(8);
        break;
    case 24:
        h->flags &= ~UINT64_C(16);
        break;
    case 25:
        h->flags &= ~UINT64_C(32);
        break;
    case 26:
        h->flags |= 2;
        break;
    case 27:
        memset(h, 0, sizeof(*h));
        h->version = 1;
        h->bytes = 320;
        h->flags = 60;
        h->phase = 5;
        h->error_kind = 10;
        h->error_value = 2;
        break;
    case 28:
        h->service.requests = 1;
        break;
    case 29:
        h->service.requests = 96;
        break;
    case 30:
        h->service.stop = 6;
        break;
    case 31:
        h->mutation_attempts = 9;
        break;
    case 32:
        h->service.state = 3;
        break;
    default:
        break;
    }
}
#endif
int aether_fs_home_launch_serve(void *spa,
                                struct aether_fs_home_launch_state *out)
{
    assert(spa == &pool);
    ++callback;
    out->home = healthy();
#ifdef AETHER_FS_HOME_COLD_REOPEN
    corrupt(&out->home, cold_case);
#else
    out->home.flags |= 2;
    out->home.mutation_attempts = 7;
    success(&out->home.mkdir);
    success(&out->home.create);
    out->home.service.state = 2;
    out->home.service.txg = 800;
    out->home.service.bytes_staged = 3548;
#endif
    return cold_case == 27 ? 5 : 0;
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    cold_case = (unsigned)strtoul(argv[1], NULL, 10);
#ifdef AETHER_FS_HOME_COLD_REOPEN
    for (unsigned i = 0; i <= 32; ++i) {
        struct aether_fs_home_result h = healthy();
        corrupt(&h, i);
        int protocol = 0;
        int needed = aether_fs_home_order_required(&h, &protocol);
        int good = i == 0 || i == 28 || i == 29;
        if (good) {
            assert(aether_fs_home_cold_final_zero(&h));
            assert(!needed && !protocol);
        } else if (i == 27) {
            assert(!needed && !protocol);
        } else {
            assert(needed);
        }
    }
#else
    /* A real writer still must satisfy the positive ordered witness. */
    if (cold_case == 0) {
        atomic_store(&pool_completed, 7);
        atomic_store(&pool_epoch, 7);
    }
#endif
    struct aether_fs_home_launch_state out = {.version = 1, .bytes = 384};
    int result = aether_fs_home_engine_run(1, &out);
#ifdef AETHER_FS_HOME_COLD_REOPEN
    int healthy_case = cold_case == 0 || cold_case == 28 || cold_case == 29;
    int clean = healthy_case || cold_case == 27;
    assert(result == (healthy_case ? 0 : 5));
    assert(ordered == (unsigned)!clean);
#else
    int clean = cold_case == 0;
    assert(result == (clean ? 0 : 5));
    assert(ordered == 1);
#endif
    assert(exported == 1 && closed == 1 && callback == 1);
    assert(stopped == (unsigned)clean && block_closed == (unsigned)clean);
    assert(utc_closed == (unsigned)clean &&
           runtime_finished == (unsigned)clean);
    assert(((out.phases & AETHER_FS_EXPORTED) != 0) == clean);
    assert(((out.phases & AETHER_FS_HELPERS_JOINED) != 0) == clean);
    printf("cold/order generated lifecycle case %u result=%d checker=%u "
           "exported=%u\n",
           cold_case, result, ordered, exported);
    return 0;
}
