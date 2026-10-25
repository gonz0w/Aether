/* SPDX-License-Identifier: BSD-2-Clause */
/* Typed host provider failures; not original disk decoding or native execution.
 */
#include "metadata-fixture.c"
#include "zpl-context.h"
static unsigned selected;
void context_reset(unsigned mode_value)
{
    mixed_reset(0);
    selected = mode_value;
}
int aether_zpl_context(aether_zpl_view *view, uint64_t root,
                       uint64_t root_generation, uint64_t object,
                       uint64_t generation, unsigned char *path, size_t *length,
                       aether_zpl_node *parent)
{
    REQUIRE(context(view) && root == 34 && root_generation == 45 &&
            object == 34 && generation == 45);
    REQUIRE(path && length && parent);
    memset(path, 0, 256);
    path[0] = '/';
    *length = 2;
    *parent = nodes[0].value;
    switch (selected) {
    case 1:
        path[0] = 'x';
        return EIO;
    case 2:
        return -EIO;
    case 3:
        *length = 257;
        break;
    case 4:
        parent->object = 0;
        break;
    case 5:
        parent->mode = 0100600;
        break;
    case 6:
        path[0] = 'x';
        break;
    case 7:
        path[255] = 1;
        break;
    case 8:
        parent->generation++;
        break;
    case 9:
        *length = 0;
        break;
    default:
        break;
    }
    return 0;
}
