/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only typed engine substitute. Does not decode disks or qualify I/O. */
#include "zpl-directories.h"
#include "pool-bulk-lifetime.h"
#include "utc.h"
#include <errno.h>
#include <string.h>

struct fixture_node {
    aether_zpl_node value;
    uint64_t parent;
    size_t length;
    unsigned char name[255], bytes[8192];
};
static struct fixture_node nodes[12];
static unsigned mode, opens, closes, calls, retired, active, next;
static uint64_t pending, staged;
static int cookie;
#define REQUIRE(c)                                                             \
    do {                                                                       \
        if (!(c))                                                              \
            return EIO;                                                        \
    } while (0)
void mixed_reset(unsigned value)
{
    memset(nodes, 0, sizeof(nodes));
    mode = value;
    opens = closes = calls = retired = active = 0;
    next = 1;
    pending = staged = 0;
    nodes[0].value = (aether_zpl_node){34, 45, 2, 0040755};
    nodes[0].parent = 34;
}
unsigned mixed_count(unsigned index)
{
    switch (index) {
    case 0:
        return opens;
    case 1:
        return closes;
    case 2:
        return calls;
    case 3:
        return retired;
    case 5:
        return active;
    default:
        return 0;
    }
}
static struct fixture_node *find(uint64_t object, uint64_t generation)
{
    for (unsigned i = 0; i < next; ++i)
        if (nodes[i].value.object == object &&
            nodes[i].value.generation == generation)
            return &nodes[i];
    return NULL;
}
static struct fixture_node *named(uint64_t directory, const unsigned char *name,
                                  size_t length)
{
    for (unsigned i = 1; i < next; ++i)
        if (nodes[i].value.object && nodes[i].parent == directory &&
            nodes[i].length == length && !memcmp(nodes[i].name, name, length))
            return &nodes[i];
    return NULL;
}
static int context(aether_zpl_view *view)
{
    return view == (aether_zpl_view *)&cookie && active;
}
int aether_zpl_open_write(struct spa *spa, const char *dataset,
                          aether_zpl_view **out)
{
    REQUIRE(spa && dataset && !strcmp(dataset, "testpool_zstd/x86_64") && out &&
            !*out && !active && !pending);
    ++opens;
    active = 1;
    *out = (aether_zpl_view *)&cookie;
    return 0;
}
void aether_zpl_close(aether_zpl_view **out)
{
    if (out && *out) {
        *out = NULL;
        active = 0;
        ++closes;
    }
}
int aether_zpl_root(aether_zpl_view *view, aether_zpl_node *out)
{
    REQUIRE(context(view) && out);
    *out = nodes[0].value;
    return 0;
}
int aether_zpl_directory(aether_zpl_view *view, uint64_t object,
                         uint64_t generation, aether_zpl_node *out)
{
    REQUIRE(context(view) && out);
    struct fixture_node *n = find(object, generation);
    if (!n)
        return ESTALE;
    if ((n->value.mode & 0170000) != 0040000)
        return ENOTDIR;
    *out = n->value;
    if (mode == 1 && calls)
        ++out->generation;
    if (mode == 2 && calls)
        out->mode = 0100600;
    if (mode == 3 && calls)
        return EIO;
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *view, uint64_t parent,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    REQUIRE(context(view) && out && name && length && length <= 255);
    struct fixture_node *p = find(parent, generation);
    if (!p)
        return ESTALE;
    if ((p->value.mode & 0170000) != 0040000)
        return ENOTDIR;
    struct fixture_node *n = named(parent, name, length);
    if (!n)
        return ENOENT;
    *out = n->value;
    return 0;
}
static int begin(aether_zpl_write_result *out, uint64_t bytes)
{
    REQUIRE(active && !pending && out);
    ++calls;
    if (mode == 4)
        return ENOSPC;
    pending = 787 + calls;
    staged = bytes;
    *out = (aether_zpl_write_result){pending, bytes, 2};
    return 0;
}
static int create(aether_zpl_view *view, uint64_t parent, uint64_t generation,
                  const unsigned char *name, size_t length, uint64_t uid,
                  uint64_t gid, uint64_t seconds, uint64_t nanos,
                  aether_zpl_node *out, aether_zpl_write_result *result,
                  int directory)
{
    REQUIRE(context(view) && name && length && length <= 255 && uid == 1000 &&
            gid == 1000 && seconds == 1791290040 && nanos == 123 && out &&
            result);
    *out = (aether_zpl_node){0};
    *result = (aether_zpl_write_result){0};
    struct fixture_node *p = find(parent, generation);
    if (!p)
        return ESTALE;
    if (named(parent, name, length))
        return EEXIST;
    int error = begin(result, 0);
    if (error)
        return error;
    unsigned slot = 1;
    while (slot < next && nodes[slot].value.object)
        ++slot;
    if (slot == 12)
        return ENOSPC;
    if (slot == next)
        ++next;
    struct fixture_node *n = &nodes[slot];
    memset(n, 0, sizeof(*n));
    n->value = (aether_zpl_node){96 + slot, pending, directory ? 2 : 0,
                                 directory ? 0040700 : 0100600};
    n->parent = parent;
    n->length = length;
    memcpy(n->name, name, length);
    ++p->value.size;
    *out = n->value;
    if (mode == 5) {
        result->state = 1;
        return EIO;
    }
    if (mode == 6)
        out->mode = 0;
    return 0;
}
#define CREATE_ENTRY(entry, isdir)                                             \
    int entry(aether_zpl_view *v, uint64_t p, uint64_t g,                      \
              const unsigned char *n, size_t l, uint64_t u, uint64_t group,    \
              uint64_t s, uint64_t ns, aether_zpl_node *out,                   \
              aether_zpl_write_result *result)                                 \
    {                                                                          \
        return create(v, p, g, n, l, u, group, s, ns, out, result, isdir);     \
    }
CREATE_ENTRY(aether_zpl_create, 0)
CREATE_ENTRY(aether_zpl_mkdir, 1)
static int remove_node(aether_zpl_view *view, uint64_t parent,
                       uint64_t generation, const unsigned char *name,
                       size_t length, uint64_t object,
                       uint64_t child_generation, uint64_t seconds,
                       uint64_t nanos, aether_zpl_write_result *result,
                       int directory)
{
    REQUIRE(context(view) && result && seconds == 1791290040 && nanos == 123);
    *result = (aether_zpl_write_result){0};
    struct fixture_node *p = find(parent, generation),
                        *n = named(parent, name, length);
    if (!p || !n || n->value.object != object ||
        n->value.generation != child_generation)
        return ESTALE;
    if (((n->value.mode & 0170000) == 0040000) != directory)
        return EINVAL;
    if (directory && n->value.size != 2)
        return 39; /* Selected native musl errno, not macOS ENOTEMPTY66. */
    int error = begin(result, 0);
    if (error)
        return error;
    n->value.object = 0;
    --p->value.size;
    return 0;
}
#define REMOVE_ENTRY(entry, isdir)                                             \
    int entry(aether_zpl_view *v, uint64_t p, uint64_t g,                      \
              const unsigned char *n, size_t l, uint64_t o, uint64_t og,       \
              uint64_t s, uint64_t ns, aether_zpl_write_result *result)        \
    {                                                                          \
        return remove_node(v, p, g, n, l, o, og, s, ns, result, isdir);        \
    }
REMOVE_ENTRY(aether_zpl_remove, 0)
REMOVE_ENTRY(aether_zpl_rmdir, 1)
int aether_zpl_rename(aether_zpl_view *view, uint64_t parent,
                      uint64_t generation, const unsigned char *from,
                      size_t from_length, const unsigned char *to,
                      size_t to_length, uint64_t object,
                      uint64_t child_generation, uint64_t seconds,
                      uint64_t nanos, aether_zpl_write_result *result)
{
    REQUIRE(context(view) && result && to && to_length && to_length <= 255 &&
            seconds == 1791290040 && nanos == 123);
    *result = (aether_zpl_write_result){0};
    struct fixture_node *n = named(parent, from, from_length);
    if (!find(parent, generation) || !n || n->value.object != object ||
        n->value.generation != child_generation)
        return ESTALE;
    if (named(parent, to, to_length))
        return EEXIST;
    int error = begin(result, 0);
    if (error)
        return error;
    n->length = to_length;
    memcpy(n->name, to, to_length);
    return 0;
}
int aether_zpl_write(aether_zpl_view *view, uint64_t object,
                     uint64_t generation, uint64_t offset, const void *bytes,
                     size_t length, uint64_t seconds, uint64_t nanos,
                     aether_zpl_write_result *out)
{
    REQUIRE(context(view) && out && bytes && length && length <= 4096 &&
            seconds == 1791290040 && nanos == 123);
    *out = (aether_zpl_write_result){0};
    struct fixture_node *n = find(object, generation);
    if (!n)
        return ESTALE;
    if (offset > n->value.size || offset > 8192 || length > 8192 - offset)
        return EINVAL;
    int error = begin(out, length);
    if (error)
        return error;
    memcpy(n->bytes + offset, bytes, length);
    if (offset + length > n->value.size)
        n->value.size = offset + length;
    return 0;
}
int aether_zpl_read(aether_zpl_view *view, uint64_t object, uint64_t generation,
                    uint64_t offset, void *out, size_t length, size_t *count)
{
    REQUIRE(context(view) && out && count && length <= 4096);
    *count = 0;
    memset(out, 0, length);
    struct fixture_node *n = find(object, generation);
    if (!n)
        return ESTALE;
    if (offset >= n->value.size)
        return 0;
    *count = length < n->value.size - offset ? length : n->value.size - offset;
    memcpy(out, n->bytes + offset, *count);
    return 0;
}
static int retire(int error, uint64_t txg, uint64_t bytes, uint64_t state,
                  uint64_t expected)
{
    REQUIRE(!active && !error && txg == pending && txg && bytes == staged &&
            bytes == expected && state == 2);
    if (mode == 7)
        return EBUSY;
    ++retired;
    pending = staged = 0;
    return 0;
}
int aether_pool_namespace0_retire(int e, uint64_t t, uint64_t b, uint64_t s)
{
    return retire(e, t, b, s, 0);
}
int aether_pool_service_bytes_retire(int e, uint64_t t, uint64_t b, uint64_t s,
                                     uint64_t expected)
{
    return retire(e, t, b, s, expected);
}
int aether_utc_read(struct timespec *out)
{
    REQUIRE(out);
    out->tv_sec = 1791290040;
    out->tv_nsec = 123;
    return 0;
}
