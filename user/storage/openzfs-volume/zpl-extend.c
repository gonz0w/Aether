/* SPDX-License-Identifier: BSD-2-Clause */
#include "zpl-resize.c"
#include "zpl-extend.h"

int aether_zpl_extend(aether_zpl_view *view, uint64_t object,
                      uint64_t generation, uint64_t size, uint64_t seconds,
                      uint64_t nanoseconds, aether_zpl_write_result *out)
{
    if (!out)
        return EINVAL;
    memset(out, 0, sizeof(*out));
    if (!view)
        return EINVAL;
    if (size > INT64_MAX)
        return EFBIG;
    aether_zpl_node node;
    uint64_t parent = 0;
    int error = aether_zpl_load(view, object, &node, &parent);
    if (error)
        return error;
    if (node.size > INT64_MAX)
        return EFBIG;
    if (size < node.size)
        return ENOTSUP;
    if (size - node.size > 4096)
        return EFBIG;
    /* Read-only source, not mutable shared state. The original writer owns a
     * stable initialized staging copy before any assigned transaction. */
    static const unsigned char zeros[4096] = {0};
    return aether_zpl_write(view, object, generation, node.size, zeros,
                            size - node.size, seconds, nanoseconds, out);
}
