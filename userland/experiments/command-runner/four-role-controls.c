/* SPDX-License-Identifier: BSD-2-Clause */
#include "four-role.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void put(unsigned char *p, unsigned value)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (unsigned char)(value >> (i * 8));
}
int main(void)
{
    unsigned count = 0;
    for (unsigned gen = 1; gen <= 2; ++gen) {
        unsigned char frame[160] = {0};
        const unsigned modes[4] = {2, 2, 1, 3};
        const unsigned caps[4] = {512, 256, 6, 64};
        memcpy(frame, "AERIO001", 8);
        put(frame + 8, 4);
        put(frame + 12, gen);
        for (unsigned i = 0; i < 4; ++i) {
            unsigned char *p = frame + 32 + i * 32;
            put(p, i + 1);
            put(p + 4, (i < 2 ? 0x75000000u + ((i + 1) << 16)
                              : 0x71000000u + ((i - 2) << 16)) +
                           gen);
            put(p + 8, i + 1);
            put(p + 12, modes[i]);
            put(p + 16, caps[i]);
        }
        struct ar_roles result, sentinel;
        memset(&sentinel, 0xa5, sizeof sentinel);
        assert(ar_roles_decode(frame, sizeof frame, gen, &result));
        assert(result.refs[2] == 0x71000000u + gen);
        ++count;
        for (unsigned i = 0; i < sizeof frame; ++i) {
            frame[i] ^= 1;
            result = sentinel;
            assert(!ar_roles_decode(frame, sizeof frame, gen, &result));
            assert(!memcmp(&result, &sentinel, sizeof result));
            frame[i] ^= 1;
            ++count;
        }
        for (unsigned n = 0; n < sizeof frame; ++n) {
            result = sentinel;
            assert(!ar_roles_decode(frame, n, gen, &result));
            assert(!memcmp(&result, &sentinel, sizeof result));
            ++count;
        }
        assert(!ar_roles_decode(frame, 161, gen, &result));
        assert(!ar_roles_decode(frame, 160, 0, &result));
        assert(!ar_roles_decode(frame, 160, 3, &result));
        count += 3;
    }
    printf("four-role cases=%u pass\n", count);
    return 0;
}
