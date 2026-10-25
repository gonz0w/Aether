/* SPDX-License-Identifier: BSD-2-Clause */
/* Typed host doubles, not original OpenZFS or native authentication evidence.
 */
#define aether_zpl_lookup fixture_lookup_base
#include "bridge-fixture.c"
#undef aether_zpl_lookup
#include "zpl-mutate.h"
static unsigned ns_mode, ns_calls, ns_kind;
void namespace_reset(unsigned selected)
{
    fixture_reset(selected == 9    ? 30
                  : selected == 11 ? 21
                  : selected == 12 ? 24
                                   : 20);
    ns_mode = selected;
    ns_calls = ns_kind = 0;
}
unsigned namespace_count(void) { return ns_calls; }
unsigned namespace_kind(void) { return ns_kind; }
int aether_zpl_lookup(aether_zpl_view *view, uint64_t directory,
                      uint64_t generation, const unsigned char *name,
                      size_t length, aether_zpl_node *out)
{
    if (length == 4 && !memcmp(name, "zstd", 4))
        return fixture_lookup_base(view, directory, generation, name, length,
                                   out);
    ++calls[3];
    assert(view == &context && view->live && directory == 34 &&
           generation == 45);
    assert(name && length == 3 &&
           (!memcmp(name, "old", 3) || !memcmp(name, "new", 3)));
    assert(out && !out->object && !out->generation && !out->size && !out->mode);
    if (ns_mode == 10)
        return 5;
    *out = (aether_zpl_node){90, 800, 0, 0100600};
    return 0;
}
static int mutation(aether_zpl_view *view, uint64_t directory,
                    uint64_t generation, uint64_t seconds, uint64_t nanos,
                    unsigned kind, aether_zpl_write_result *out)
{
    assert(view == &context && view->live && directory == 34 &&
           generation == 45);
    assert(seconds == 1792300000 && nanos == 123 && !ns_calls++);
    assert(out && !out->txg && !out->bytes_staged && !out->state);
    ns_kind = kind;
    if (ns_mode == 1)
        return 17;
    *out = (aether_zpl_write_result){ns_mode == 3 || ns_mode == 5 ? 0 : 788,
                                     ns_mode == 4 ? 16 : 0,
                                     ns_mode == 2 || ns_mode == 3 ? 1 : 2};
    return ns_mode == 6                                   ? -5
           : ns_mode == 2 || ns_mode == 3 || ns_mode == 7 ? 5
                                                          : 0;
}
int aether_zpl_create(aether_zpl_view *view, uint64_t directory,
                      uint64_t generation, const unsigned char *name,
                      size_t length, uint64_t uid, uint64_t gid,
                      uint64_t seconds, uint64_t nanos,
                      aether_zpl_node *created, aether_zpl_write_result *out)
{
    assert(name && length == 3 && !memcmp(name, "new", 3) && uid == 1000 &&
           gid == 1001);
    assert(created && !created->object && !created->generation &&
           !created->size && !created->mode);
    int error = mutation(view, directory, generation, seconds, nanos, 1, out);
    if (!error)
        *created =
            (aether_zpl_node){90, 800, 0, ns_mode == 8 ? 040755 : 0100600};
    return error;
}
int aether_zpl_rename(aether_zpl_view *view, uint64_t directory,
                      uint64_t generation, const unsigned char *from,
                      size_t from_length, const unsigned char *to,
                      size_t to_length, uint64_t object,
                      uint64_t object_generation, uint64_t seconds,
                      uint64_t nanos, aether_zpl_write_result *out)
{
    assert(from && to && from_length == 3 && to_length == 3);
    assert(!memcmp(from, "old", 3) && !memcmp(to, "new", 3) && object == 90 &&
           object_generation == 800);
    return mutation(view, directory, generation, seconds, nanos, 2, out);
}
int aether_zpl_remove(aether_zpl_view *view, uint64_t directory,
                      uint64_t generation, const unsigned char *name,
                      size_t length, uint64_t object,
                      uint64_t object_generation, uint64_t seconds,
                      uint64_t nanos, aether_zpl_write_result *out)
{
    assert(name && length == 3 && !memcmp(name, "old", 3) && object == 90 &&
           object_generation == 800);
    return mutation(view, directory, generation, seconds, nanos, 3, out);
}
