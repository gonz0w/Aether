/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only C ABI/provider double; never opens a pool. */
#include "zpl-metadata.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int selected;
static unsigned calls;
void metadata_fixture_case(int value) { selected = value; }
unsigned metadata_fixture_calls(void) { return calls; }
size_t metadata_fixture_layout(unsigned i)
{
    const size_t values[] = {sizeof(aether_zpl_metadata),
                             _Alignof(aether_zpl_metadata),
                             offsetof(aether_zpl_metadata, parent),
                             offsetof(aether_zpl_metadata, atime),
                             offsetof(aether_zpl_metadata, birthtime),
                             offsetof(aether_zpl_time, nanoseconds)};
    return i < sizeof(values) / sizeof(values[0]) ? values[i] : 0;
}
int aether_zpl_getattr(aether_zpl_view *view, uint64_t object,
                       uint64_t generation, aether_zpl_metadata *out)
{
    ++calls;
    const unsigned char *bytes = (const unsigned char *)out;
    for (size_t i = 0; i < sizeof(*out); ++i)
        if (bytes[i] != 0) {
            fputs("metadata oracle: uninitialized output\n", stderr);
            exit(95);
        }
    if (!view)
        abort();
    *out = (aether_zpl_metadata){.node = {object, generation, 780248, 0106755},
                                 .parent = 34,
                                 .links = 3,
                                 .uid = UINT64_MAX,
                                 .gid = UINT64_C(0x8000000100000001),
                                 .flags = UINT64_C(0x8000000000000104),
                                 .atime = {INT64_MIN, 999999999},
                                 .mtime = {INT64_MAX, 1},
                                 .ctime = {-1, 2},
                                 .birthtime = {0, 3}};
    if (selected >= 14) {
        int root = object == 34;
        out->node = (aether_zpl_node){object, generation, root ? 3 : 780248,
                                      root ? 040755 : 0100755};
        out->links = root ? 2 : 1;
        out->uid = out->gid = 0;
        out->flags = root ? UINT64_C(0x840800000144) : UINT64_C(0x840800000104);
        out->atime = (aether_zpl_time){root ? 1621447687 : 1621447692, 7};
        out->mtime = out->ctime = (aether_zpl_time){1620802862, 8};
        out->birthtime = (aether_zpl_time){root ? 1620802853 : 1620802862, 9};
        if (selected == 15)
            out->uid = 1;
        if (selected == 16)
            ++out->mtime.seconds;
        if (selected == 17)
            out->flags ^= 4;
        if (!root && generation == 46)
            return selected == 18 ? 0 : 116;
        return 0;
    }
    switch (selected) {
    case 1:
        out->atime.nanoseconds = 1000000000;
        break;
    case 2:
        out->mtime.nanoseconds = 1000000000;
        break;
    case 3:
        out->ctime.nanoseconds = 1000000000;
        break;
    case 4:
        out->birthtime.nanoseconds = UINT64_MAX;
        break;
    case 5:
        ++out->node.object;
        break;
    case 6:
        ++out->node.generation;
        break;
    case 7:
        out->node.mode = 0120777;
        break;
    case 8:
        out->parent = 0;
        break;
    case 9:
        out->links = 0;
        break;
    case 10:
        out->flags |= 1;
        break;
    case 11:
        return 116; /* Even a partially copied failed result never escapes. */
    case 12:
        return -5;
    case 13:
        out->node.mode = 040755;
        break;
    default:
        break;
    }
    return 0;
}
