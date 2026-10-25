/* SPDX-License-Identifier: BSD-2-Clause */
#include "four-role.h"
#include <string.h>
static uint32_t word(const unsigned char *p)
{
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 |
           (uint32_t)p[3] << 24;
}
int ar_roles_decode(const unsigned char *p, size_t n, uint32_t generation,
                    struct ar_roles *out)
{
    const uint32_t rights[4] = {2, 2, 1, 3};
    const uint32_t capacities[4] = {512, 256, 6, 64};
    struct ar_roles candidate;
#ifdef NATIVE_SUSTAINED_V2
    if (!p || !out || n != 160 || !generation || generation > 65535 ||
        memcmp(p, "AERIO002", 8) || word(p + 8) != 4 ||
#else
    if (!p || !out || n != 160 || (generation != 1 && generation != 2) ||
        memcmp(p, "AERIO001", 8) || word(p + 8) != 4 ||
#endif
        word(p + 12) != generation)
        return 0;
    for (unsigned i = 16; i < 32; ++i)
        if (p[i])
            return 0;
    for (unsigned i = 0; i < 4; ++i) {
        const unsigned char *r = p + 32 + i * 32;
        uint32_t ref = i < 2 ? 0x75000000u + ((i + 1) << 16)
                             : 0x71000000u + ((i - 2) << 16);
        if (word(r) != i + 1 || word(r + 4) != ref + generation ||
            word(r + 8) != i + 1 || word(r + 12) != rights[i] ||
            word(r + 16) != capacities[i])
            return 0;
        for (unsigned j = 20; j < 32; ++j)
            if (r[j])
                return 0;
        candidate.refs[i] = word(r + 4);
    }
    *out = candidate;
    return 1;
}
