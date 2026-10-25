/* SPDX-License-Identifier: BSD-2-Clause */
/* Typed host substitute only: no original disk decoding or native execution. */
#define aether_zpl_mkdir fixture_mkdir
#define aether_zpl_create fixture_create
#define aether_zpl_lookup fixture_lookup
#define aether_zpl_directory fixture_directory
#define aether_utc_read fixture_utc
#include "metadata-fixture.c"
#undef aether_zpl_mkdir
#undef aether_zpl_create
#undef aether_zpl_lookup
#undef aether_zpl_directory
#undef aether_utc_read
#include "zpl-context.h"
static unsigned home_mode, home_clock_after;
static uint64_t home_seconds, home_nanos;
static int home_clock_script;
void home_clock(uint64_t seconds, uint64_t nanos, unsigned after);
void home_clock(uint64_t seconds, uint64_t nanos, unsigned after)
{
    home_seconds = seconds;
    home_nanos = nanos;
    home_clock_after = after;
    home_clock_script = 1;
}
void home_reset(unsigned value)
{
    mixed_reset(0);
    metadata_reset(0);
    home_mode = value;
    home_clock_script = 0;
}
unsigned home_count(unsigned index) { return mixed_count(index); }
int aether_zpl_mkdir(aether_zpl_view *view, uint64_t parent,
                     uint64_t generation, const unsigned char *name,
                     size_t length, uint64_t uid, uint64_t gid,
                     uint64_t seconds, uint64_t nanos, aether_zpl_node *node,
                     aether_zpl_write_result *out)
{
    if (home_mode == 1) {
        REQUIRE(context(view) && parent == 34 && generation == 45 &&
                length == 4 && !memcmp(name, "home", 4) && out && node);
        ++calls;
        *node = (aether_zpl_node){0};
        *out = (aether_zpl_write_result){0};
        return EEXIST;
    }
    /* The original typed graph fixture accepts one constant timestamp. Verify
     * the actual entry-supplied scripted UTC, then adapt only that host model.
     */
    if (home_clock_script && calls >= home_clock_after) {
        REQUIRE(seconds == home_seconds && nanos == home_nanos);
        seconds = 1791290040;
        nanos = 123;
    }
    return fixture_mkdir(view, parent, generation, name, length, uid, gid,
                         seconds, nanos, node, out);
}
int aether_zpl_create(aether_zpl_view *view, uint64_t parent,
                      uint64_t generation, const unsigned char *name,
                      size_t length, uint64_t uid, uint64_t gid,
                      uint64_t seconds, uint64_t nanos, aether_zpl_node *node,
                      aether_zpl_write_result *out)
{
    if (home_mode == 15 && calls >= 2) {
        REQUIRE(context(view) && parent == 97 && generation == 788 && out &&
                node);
        ++calls;
        *node = (aether_zpl_node){0};
        *out = (aether_zpl_write_result){0, 0, 9};
        return EIO;
    }
    if (home_mode >= 2 && home_mode <= 6) {
        REQUIRE(context(view) && parent == 97 && generation == 788 &&
                length == 5 && !memcmp(name, "probe", 5) && out && node);
        ++calls;
        *node = (aether_zpl_node){0};
        *out = (aether_zpl_write_result){0};
        if (home_mode == 2)
            return EEXIST;
        if (home_mode == 3) {
            out->state = 1;
            return EIO;
        }
        if (home_mode == 4) {
            *out = (aether_zpl_write_result){789, 0, 2};
            return EIO;
        }
        if (home_mode == 5)
            return -1;
        out->state = 9;
        return EIO;
    }
    if (home_clock_script && calls >= home_clock_after) {
        REQUIRE(seconds == home_seconds && nanos == home_nanos);
        seconds = 1791290040;
        nanos = 123;
    }
    return fixture_create(view, parent, generation, name, length, uid, gid,
                          seconds, nanos, node, out);
}
int aether_zpl_lookup(aether_zpl_view *view, uint64_t parent,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    int error = fixture_lookup(view, parent, generation, name, length, out);
    if (!error && length == 4 && !memcmp(name, "home", 4) && home_mode == 10)
        *out = nodes[0].value;
    if (!error && length == 4 && !memcmp(name, "home", 4) && home_mode == 14)
        out->mode = 0100600;
    if (!error && length == 5 && !memcmp(name, "probe", 5)) {
        if (home_mode == 11)
            out->mode = 0040700;
        if (home_mode == 12)
            out->size = 1;
    }
    return error;
}
int aether_zpl_directory(aether_zpl_view *view, uint64_t object,
                         uint64_t generation, aether_zpl_node *out)
{
    if (home_mode == 9 && calls == 2)
        return EIO;
    return fixture_directory(view, object, generation, out);
}
int aether_utc_read(struct timespec *out)
{
    if ((home_mode == 7 && !calls) || (home_mode == 8 && calls == 1) ||
        (home_mode == 13 && calls == 2))
        return EIO;
    int result = fixture_utc(out);
    if (!result && home_clock_script && calls >= home_clock_after) {
        out->tv_sec = (time_t)home_seconds;
        out->tv_nsec = (long)home_nanos;
    }
    return result;
}
int aether_zpl_context(aether_zpl_view *view, uint64_t root,
                       uint64_t root_generation, uint64_t object,
                       uint64_t generation, unsigned char *path, size_t *length,
                       aether_zpl_node *parent)
{
    REQUIRE(context(view) && root == 34 && root_generation == 45 && path &&
            length && parent);
    struct fixture_node *node = find(object, generation);
    REQUIRE(node);
    memset(path, 0, 256);
    if (object == root) {
        path[0] = '/';
        *length = 2;
        *parent = nodes[0].value;
    } else {
        REQUIRE(node->parent == root && node->length < 254);
        path[0] = '/';
        memcpy(path + 1, node->name, node->length);
        *length = node->length + 2;
        *parent = nodes[0].value;
    }
    return 0;
}

/* This is the actual independent C consumer, linked into the Rust host tests.
 */
#include "home-native.h"
int home_validate(const struct aether_fs_home_result *result, int *protocol)
{
    return aether_fs_home_order_required(result, protocol);
}
