/* SPDX-License-Identifier: BSD-2-Clause */
/* Typed host-only provider. Synthetic graph state cannot qualify native I/O. */
#include "zpl-mutate.h"
#include "utc.h"
#include <errno.h>
#include <stdint.h>
#include <string.h>

static unsigned mode, opens, closes, calls, retired, violations, active, roots;
static unsigned zero_retired, write_retired, present, creations;
static uint64_t identity, generation, size, pending, pending_staged;
static unsigned char contents[64], current_name;
static unsigned cookie;
#define REQUIRE(value)                                                         \
    do {                                                                       \
        if (!(value)) {                                                        \
            violations = __LINE__;                                             \
            return EIO;                                                        \
        }                                                                      \
    } while (0)
void mixed_reset(unsigned value)
{
    mode = value;
    opens = closes = calls = retired = violations = active = roots = 0;
    zero_retired = write_retired = present = creations = 0;
    identity = generation = size = pending = pending_staged = 0;
    current_name = 0;
    memset(contents, 0, sizeof(contents));
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
    case 4:
        return violations;
    case 5:
        return active;
    case 6:
        return zero_retired;
    case 7:
        return write_retired;
    case 8:
        return roots;
    case 9:
        return creations;
    default:
        return 0;
    }
}
int aether_zpl_open_write(struct spa *spa, const char *dataset,
                          aether_zpl_view **out)
{
    REQUIRE(spa && dataset && !strcmp(dataset, "testpool_zstd/x86_64") && out &&
            !*out && !active);
    ++opens;
    active = 1;
    *out = (aether_zpl_view *)&cookie;
    if (mode == 11 || ((mode == 14 || mode == 107) && opens == 2))
        return EIO;
    REQUIRE(!pending);
    return 0;
}
void aether_zpl_close(aether_zpl_view **view)
{
    if (!view || !*view)
        return;
    if (*view != (aether_zpl_view *)&cookie || !active)
        violations = __LINE__;
    *view = NULL;
    active = 0;
    ++closes;
}
int aether_zpl_root(aether_zpl_view *view, aether_zpl_node *out)
{
    REQUIRE(view == (aether_zpl_view *)&cookie && active && out);
    ++roots;
    if (mode == 106 && opens > 1)
        return EIO;
    *out = (aether_zpl_node){34, (mode == 15 && opens > 1) ? 46 : 45,
                             present ? 2 : 1, mode == 12 ? 0 : 0040755};
    return 0;
}
int aether_zpl_lookup(aether_zpl_view *view, uint64_t directory,
                      uint64_t parent_generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    REQUIRE(view == (aether_zpl_view *)&cookie && active && directory == 34 &&
            parent_generation == 45 && name && out);
    if (mode == 10)
        return EIO;
    if (length == 4 && !memcmp(name, "zstd", 4)) {
        *out = (aether_zpl_node){2, 47, 780248, 0100755};
        return 0;
    }
    if (!present || length != 1 || *name != current_name)
        return ENOENT;
    *out = (aether_zpl_node){identity, generation, size, 0100600};
    if (mode == 101 && opens > 1)
        ++out->object;
    if (mode == 102 && opens > 1)
        ++out->generation;
    if (mode == 103 && opens > 1)
        out->mode = 0040700;
    if (mode == 104 && opens > 1)
        return ENOENT;
    return 0;
}
int aether_utc_read(struct timespec *out)
{
    REQUIRE(out);
    if (mode == 9 || (mode == 21 && calls))
        return EIO;
    *out = (struct timespec){1791290040, 123};
    return 0;
}
static int begin(aether_zpl_view *view, uint64_t directory,
                 uint64_t parent_generation, uint64_t seconds, uint64_t ns,
                 uint64_t staged, aether_zpl_write_result *out)
{
    REQUIRE(view == (aether_zpl_view *)&cookie && active && directory == 34 &&
            parent_generation == 45);
    REQUIRE(seconds == 1791290040 && ns == 123 && out && !out->txg &&
            !out->bytes_staged && !out->state && !pending);
    ++calls;
    REQUIRE(calls <= 8);
    *out = (aether_zpl_write_result){788 + calls - 1, staged, 2};
    pending = out->txg;
    pending_staged = staged;
    if (calls == 1) {
        if (mode == 1) {
            *out = (aether_zpl_write_result){0};
            return EEXIST;
        }
        if (mode == 2) {
            out->state = 1;
            return EIO;
        }
        if (mode == 3) {
            out->state = 1;
            out->txg = 0;
            return EIO;
        }
        if (mode == 4)
            out->bytes_staged = 16;
        if (mode == 5)
            out->txg = 0;
        if (mode == 6)
            return -1;
        if (mode == 7)
            return EIO;
    }
    if (staged && calls == 2 && mode == 17) {
        *out = (aether_zpl_write_result){0};
        return EIO;
    }
    if (staged && calls == 2 && mode == 18) {
        out->state = 1;
        out->txg = 0;
        return EIO;
    }
    return 0;
}
int aether_zpl_create(aether_zpl_view *view, uint64_t directory,
                      uint64_t parent_generation, const unsigned char *name,
                      size_t length, uint64_t uid, uint64_t gid,
                      uint64_t seconds, uint64_t ns, aether_zpl_node *created,
                      aether_zpl_write_result *out)
{
    ++creations;
    if (mode >= 100 && present && name && length == 1 &&
        *name == current_name) {
        *created = (aether_zpl_node){0};
        *out = (aether_zpl_write_result){0};
        return EEXIST;
    }
    REQUIRE(name && length == 1 && *name == 'p' && !present && uid == 1000 &&
            gid == 1000 && created);
    int error = begin(view, directory, parent_generation, seconds, ns, 0, out);
    if (!error) {
        present = 1;
        current_name = 'p';
        identity = 90;
        generation = 800 + calls;
        size = 0;
        *created = (aether_zpl_node){identity, generation, 0,
                                     mode == 8 ? 0040755 : 0100600};
        if (mode == 105)
            created->mode = 0;
        if (mode == 108)
            created->generation = 0;
        if (mode == 109)
            created->size = 1;
    }
    return error;
}
int aether_zpl_rename(aether_zpl_view *view, uint64_t directory,
                      uint64_t parent_generation, const unsigned char *from,
                      size_t from_length, const unsigned char *to,
                      size_t to_length, uint64_t object,
                      uint64_t file_generation, uint64_t seconds, uint64_t ns,
                      aether_zpl_write_result *out)
{
    REQUIRE(from && to && from_length == 1 && to_length == 1 && *from == 'p' &&
            *to == 'q' && current_name == 'p');
    REQUIRE(present && object == identity && file_generation == generation);
    int error = begin(view, directory, parent_generation, seconds, ns, 0, out);
    if (!error)
        current_name = 'q';
    return error;
}
int aether_zpl_remove(aether_zpl_view *view, uint64_t directory,
                      uint64_t parent_generation, const unsigned char *name,
                      size_t length, uint64_t object, uint64_t file_generation,
                      uint64_t seconds, uint64_t ns,
                      aether_zpl_write_result *out)
{
    REQUIRE(name && length == 1 && *name == 'q' && current_name == 'q' &&
            present && object == identity && file_generation == generation);
    int error = begin(view, directory, parent_generation, seconds, ns, 0, out);
    if (!error) {
        present = 0;
        size = 0;
    }
    return error;
}
int aether_zpl_write(aether_zpl_view *view, uint64_t object,
                     uint64_t file_generation, uint64_t offset,
                     const void *bytes, size_t length, uint64_t seconds,
                     uint64_t ns, aether_zpl_write_result *out)
{
    REQUIRE(present && object == identity && file_generation == generation &&
            length == 16 && bytes && offset <= size &&
            offset + length <= sizeof(contents));
    int error = begin(view, 34, 45, seconds, ns, length, out);
    if (!error) {
        memcpy(contents + offset, bytes, length);
        if (size < offset + length)
            size = offset + length;
    }
    return error;
}
int aether_zpl_read(aether_zpl_view *view, uint64_t object,
                    uint64_t file_generation, uint64_t offset, void *buffer,
                    size_t length, size_t *count)
{
    unsigned char *bytes = buffer;
    REQUIRE(view == (aether_zpl_view *)&cookie && active && present &&
            object == identity && file_generation == generation && bytes &&
            count);
    *count =
        offset >= size ? 0 : (length < size - offset ? length : size - offset);
    if (*count)
        memcpy(bytes, contents + offset, *count);
    if (mode == 16 && *count)
        bytes[0] ^= 1;
    return 0;
}
static int retire(int error, uint64_t target, uint64_t staged, uint64_t state,
                  unsigned expected)
{
    REQUIRE(!active && opens == closes && !error && state == 2 && target &&
            target == pending && staged == expected &&
            staged == pending_staged && retired + 1 == calls);
    if ((mode == 13 && !staged) || (mode == 19 && staged) ||
        (mode == 20 && calls == 4))
        return EIO;
    ++retired;
    if (expected)
        ++write_retired;
    else
        ++zero_retired;
    pending = 0;
    return 0;
}
int aether_pool_namespace0_retire(int error, uint64_t target, uint64_t staged,
                                  uint64_t state)
{
    return retire(error, target, staged, state, 0);
}
int aether_pool_service16_retire(int error, uint64_t target, uint64_t staged,
                                 uint64_t state)
{
    return retire(error, target, staged, state, 16);
}
