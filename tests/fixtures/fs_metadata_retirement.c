/* SPDX-License-Identifier: BSD-2-Clause */
/* Execute the actual generated retirement tail with explicit host-only doubles.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef void spa_t;
typedef void nvlist_t;
#define FTAG NULL
#define B_FALSE 0
static unsigned char phases[32];
static unsigned count, mode, closes, waits, exports, frees, enters, exits,
    orders;
#define CHECK(x)                                                               \
    do {                                                                       \
        if (!(x)) {                                                            \
            fputs("AF07_RETIREMENT_ORACLE96\n", stderr);                       \
            exit(96);                                                          \
        }                                                                      \
    } while (0)
static void aether_engine_utc_phase(unsigned char phase)
{
    CHECK(count < sizeof(phases));
    phases[count++] = phase;
}
static void spa_close(spa_t *spa, void *tag)
{
    (void)spa;
    (void)tag;
    ++closes;
}
static void dmu_buf_user_evict_wait(void)
{
    CHECK(count == 9 && phases[8] == 'S');
    ++waits;
}
static int spa_export(const char *name, nvlist_t **out, int force, int hard)
{
    CHECK(name && !*out && !force && !hard && waits == 1);
    CHECK(count == 10 && phases[9] == 'D');
    ++exports;
    return mode == 1 ? 5 : 0;
}
static void nvlist_free(nvlist_t *out)
{
    (void)out;
    ++frees;
}
static void spa_namespace_enter(void *tag)
{
    (void)tag;
    ++enters;
}
static spa_t *spa_next(spa_t *spa)
{
    (void)spa;
    return mode == 2 ? (void *)1 : NULL;
}
static void spa_namespace_exit(void *tag)
{
    (void)tag;
    ++exits;
}
static int aether_pool_hooks_check_ordered(void)
{
    ++orders;
    return mode == 3;
}
static int probe(void)
{
    spa_t *spa = NULL;
    uint64_t target = mode == 5 ? 0 : 796;
    int error = mode == 4 ? 5 : 0;
    /* RETIREMENT_TAIL */
}
int main(void)
{
    for (mode = 0; mode < 6; ++mode) {
        count = closes = waits = exports = frees = enters = exits = orders = 0;
        int result = probe();
        CHECK(result == (mode ? 873 : 0));
        CHECK(closes == 1);
        if (mode >= 4) {
            CHECK(!count && !waits && !exports && !frees && !enters && !exits &&
                  !orders);
            continue;
        }
        CHECK(waits == 1 && exports == 1 && frees == 1);
        CHECK(count == (mode ? 10U : 11U));
        CHECK(phases[0] == 28 && phases[1] == 3);
        if (!mode)
            CHECK(phases[10] == 'J');
        CHECK(enters == (mode != 1) && exits == enters);
        CHECK(orders == (mode == 0 || mode == 3));
    }
    return 0;
}
