/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only typed provider; no original disk or native holder enforcement. */
#include "directory-fixture.c"
#include "zpl-metadata.h"
static unsigned metadata_mode, metadata_calls;
void metadata_reset(unsigned selected)
{
    metadata_mode = selected;
    metadata_calls = 0;
}
unsigned metadata_count(void) { return metadata_calls; }
unsigned metadata_retired_expected(void)
{
    return metadata_calls && metadata_mode >= 2 && metadata_mode <= 7;
}
int aether_zpl_getattr(aether_zpl_view *view, uint64_t object,
                       uint64_t generation, aether_zpl_metadata *out)
{
    ++metadata_calls;
    REQUIRE(context(view) && out);
    struct fixture_node *n = find(object, generation);
    if (!n)
        return ESTALE;
    memset(out, 0, sizeof(*out));
    out->node = n->value;
    out->node.mode |= 06000;
    out->parent = n->parent;
    out->links = 3;
    out->uid = UINT64_C(0x8000000100000002);
    out->gid = UINT64_MAX;
    out->flags = UINT64_C(0x2000000000000000);
    out->atime = (aether_zpl_time){INT64_MIN, 999999999};
    out->mtime = (aether_zpl_time){-5, 123};
    out->ctime = (aether_zpl_time){0, 456};
    out->birthtime = (aether_zpl_time){INT64_MAX, 789};
    switch (metadata_mode) {
    case 1:
        return EIO; /* Deliberate partial-result error: Rust must discard. */
    case 2:
        return -EIO;
    case 3:
        ++out->node.object;
        break;
    case 4:
        ++out->node.generation;
        break;
    case 5:
        out->node.mode = 0100600;
        break;
    case 6:
        out->mtime.nanoseconds = 1000000000;
        break;
    case 7:
        ++out->node.size;
        break;
    default:
        break;
    }
    return 0;
}
