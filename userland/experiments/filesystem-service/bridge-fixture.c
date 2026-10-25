/* SPDX-License-Identifier: BSD-2-Clause */
/* Typed host ABI provider, never the original engine or a native witness. */
#include "zpl-write.h"
#include "utc.h"
#include "native-probe.h"
#include <assert.h>
#include <stddef.h>
#include <string.h>

_Static_assert(sizeof(aether_zpl_node) == 32 && _Alignof(aether_zpl_node) == 8,
               "node");
_Static_assert(offsetof(aether_zpl_node, mode) == 24, "mode");
_Static_assert(sizeof(aether_zpl_write_result) == 24 &&
                   _Alignof(aether_zpl_write_result) == 8,
               "result");
_Static_assert(offsetof(aether_zpl_write_result, bytes_staged) == 8, "staged");
_Static_assert(offsetof(aether_zpl_write_result, state) == 16, "state");
_Static_assert(sizeof(struct timespec) == 16 && _Alignof(struct timespec) == 8,
               "time");
_Static_assert(offsetof(struct timespec, tv_nsec) == 8 && sizeof(int) == 4,
               "scalar ABI");

_Static_assert(sizeof(aether_fs_probe_result) == 24 &&
                   _Alignof(aether_fs_probe_result) == 8,
               "probe");
_Static_assert(offsetof(aether_fs_probe_result, state) == 16, "probe state");

struct aether_zpl_view {
    int live;
};
static struct aether_zpl_view context;
static unsigned mode, probe_mode, calls[7];
static unsigned char content[780248];
static size_t size;
#ifdef FS_LIFETIMES
static unsigned retire_calls, retire_error_at, reopen_error_at;
#endif

void fixture_reset(unsigned selected)
{
    assert(!context.live);
    memset(calls, 0, sizeof(calls));
    memset(content, 0, sizeof(content));
    memcpy(content, "abcd", 4);
    probe_mode = selected >= 20;
    size = probe_mode ? sizeof(content) : 4;
    mode = selected % 20;
}
unsigned fixture_count(unsigned index)
{
    assert(index < 7);
    return calls[index];
}

int aether_zpl_open_write(struct spa *spa, const char *dataset,
                          aether_zpl_view **out)
{
    ++calls[0];
    assert(spa && dataset && out && !*out && !context.live);
    assert(!strcmp(dataset, "testpool_zstd/x86_64"));
    if (mode == 2)
        return 0;
#ifdef FS_LIFETIMES
    if (reopen_error_at && calls[0] == reopen_error_at) {
        context.live = 1;
        *out = &context;
        return 5;
    }
#endif
    context.live = 1;
    *out = &context;
    if (mode == 1)
        return 5;
    if (mode == 3)
        return -5;
    return 0;
}
void aether_zpl_close(aether_zpl_view **out)
{
    ++calls[1];
    assert(out && *out == &context && context.live);
    context.live = 0;
    if (mode != 9)
        *out = NULL;
}
int aether_zpl_root(aether_zpl_view *view, aether_zpl_node *out)
{
    ++calls[2];
    assert(view == &context && view->live && out);
    assert(!out->object && !out->generation && !out->size && !out->mode);
    *out = (aether_zpl_node){34, mode == 4 ? 0 : 45, 0, 0040755};
    return mode == 13 ? 5 : 0;
}
int aether_zpl_lookup(aether_zpl_view *view, uint64_t object,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    ++calls[3];
    assert(view == &context && view->live && object == 34 && generation == 45);
    assert(name && length == 4 &&
           !memcmp(name, probe_mode ? "zstd" : "file", 4));
    assert(out && !out->object && !out->generation && !out->size && !out->mode);
    *out = (aether_zpl_node){2, 47, size, 0100644};
    return mode == 14 ? -5 : 0;
}
int aether_zpl_read(aether_zpl_view *view, uint64_t object, uint64_t generation,
                    uint64_t offset, void *buffer, size_t length, size_t *count)
{
    ++calls[4];
    assert(view == &context && view->live && object == 2 && generation == 47);
    assert(buffer && count && !*count && length <= 4096);
    for (size_t i = 0; i < length; ++i)
        assert(!((unsigned char *)buffer)[i]);
    if (mode == 5 || mode == 6) {
        memset(buffer, 0xa5, length);
        *count = length + 1;
        return mode == 5 ? 5 : 0;
    }
    *count =
        offset >= size ? 0 : (size - offset < length ? size - offset : length);
    if (*count)
        memcpy(buffer, content + offset, *count);
    return 0;
}
int aether_zpl_write(aether_zpl_view *view, uint64_t object,
                     uint64_t generation, uint64_t offset, const void *buffer,
                     size_t length, uint64_t seconds, uint64_t nanoseconds,
                     aether_zpl_write_result *out)
{
    ++calls[5];
    assert(view == &context && view->live && object == 2 && generation == 47);
    assert(buffer && offset <= size && length <= 4096 &&
           offset + length <= sizeof(content));
    assert(seconds == 1792300000 && nanoseconds == 123);
    assert(out && !out->txg && !out->bytes_staged && !out->state);
    if (mode == 15)
        return 28;
    if (mode == 8)
        return -5;
    memcpy(content + offset, buffer, length);
    if (offset + length > size)
        size = offset + length;
    uint64_t txg = 788;
#ifdef FS_LIFETIMES
    txg += calls[5] - 1;
#endif
    *out = (aether_zpl_write_result){txg, length, mode == 7 ? 1 : 2};
    return mode == 7 ? 5 : 0;
}
int aether_utc_read(struct timespec *out)
{
    ++calls[6];
    assert(out && !out->tv_sec && !out->tv_nsec);
    out->tv_sec = mode == 11 ? -1 : 1792300000;
    out->tv_nsec = mode == 12 ? 1000000000 : 123;
    return mode == 10 ? 5 : 0;
}

#ifdef FS_LIFETIMES
void lifetime_reset(unsigned selected, unsigned retirement, unsigned reopen)
{
    fixture_reset(20 + selected);
    retire_calls = 0;
    retire_error_at = retirement;
    reopen_error_at = reopen;
}
unsigned lifetime_retire_count(void) { return retire_calls; }
int aether_pool_service16_retire(int error, uint64_t target, uint64_t staged,
                                 uint64_t state)
{
    assert(!context.live && calls[0] == calls[1]);
    assert(!error && staged == 16 && state == 2 &&
           target == 788 + retire_calls);
    ++retire_calls;
    return retire_calls == retire_error_at ? 16 : 0;
}
#endif
