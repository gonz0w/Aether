/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-note-create.h"
#include <assert.h>
#include <stdio.h>
static unsigned cases;
static void header(unsigned char h[64], int64_t status, uint64_t fd)
{
    memset(h, 0, 64);
    memcpy(h, AEFD_MAGIC, 8);
    aefd_put(h, 1, (uint64_t)status);
    aefd_put(h, 2, 7);
    aefd_put(h, 3, 9);
    aefd_put(h, 4, fd);
    aefd_put(h, 5, 64);
}
static void good(unsigned char h[64], unsigned char b[64])
{
    struct aefd_note_create_receipt r;
    assert(aefd_note_create_decode(h, b, 64, 7, 9, &r));
    ++cases;
}
static void bad(unsigned char h[64], unsigned char b[64])
{
    struct aefd_note_create_receipt r;
    memset(&r, 0xa5, sizeof r);
    struct aefd_note_create_receipt before = r;
    assert(!aefd_note_create_decode(h, b, 64, 7, 9, &r));
    assert(!memcmp(&before, &r, sizeof r));
    ++cases;
}
int main(void)
{
    unsigned char h[64], b[64] = {0};
    header(h, 0, 3);
    aefd_put(b, 0, 6);
    aefd_put(b, 1, 91);
    good(h, b);
    for (uint64_t k = 1; k <= 9; k++) {
        int64_t status;
        assert(aefd_write_status(k, 0, &status));
        memset(b, 0, 64);
        header(h, status, 0);
        aefd_put(b, 2, k);
        good(h, b);
    }
    for (uint64_t tag = 1; tag <= 5; tag++) {
        memset(b, 0, 64);
        header(h, -5, 0);
        aefd_put(b, 0, tag | 16);
        if (tag == 2 || tag == 3)
            aefd_put(b, 1, 91);
        aefd_put(b, 2, tag == 5 ? 10 : 12);
        aefd_put(b, 3, tag == 5 ? 0 : (uint64_t)-5);
        aefd_put(b, 4, (uint64_t)INT64_MIN);
        aefd_put(b, 5, INT64_MAX);
        good(h, b);
    }
    memset(b, 0, 64);
    header(h, -2147483647, 0);
    aefd_put(b, 0, 17);
    aefd_put(b, 2, 12);
    aefd_put(b, 3, (uint64_t)-2147483647);
    good(h, b);
    aefd_put(b, 0, 18);
    aefd_put(b, 1, 0);
    header(h, -5, 0);
    aefd_put(b, 3, (uint64_t)-5);
    good(h, b);
    for (uint64_t k = 1; k <= 12; k++) {
        int64_t val = k == 11 ? INT64_MIN : k == 12 ? -13 : 0, status;
        assert(aefd_write_status(k, val, &status));
        memset(b, 0, 64);
        header(h, status, 0);
        aefd_put(b, 0, 22);
        aefd_put(b, 1, 91);
        aefd_put(b, 6, k);
        aefd_put(b, 7, (uint64_t)val);
        good(h, b);
    }
    memset(b, 0, 64);
    header(h, 0, 3);
    aefd_put(b, 0, 6);
    aefd_put(b, 1, 91);
    unsigned char hc[64], bc[64];
    for (unsigned word = 0; word < 8; word++) {
        memcpy(hc, h, 64);
        memcpy(bc, b, 64);
        aefd_put(hc, word, aefd_word(hc, word) ^ UINT64_C(0x8000000000000000));
        bad(hc, bc);
    }
    for (unsigned word = 0; word < 8; word++) {
        memcpy(bc, b, 64);
        aefd_put(bc, word, aefd_word(bc, word) ^ (word == 1 ? 91 : 8));
        bad(h, bc);
    }
    memset(b, 0, 64);
    header(h, -5, 0);
    bad(h, b);
    aefd_put(b, 0, 23);
    bad(h, b);
    aefd_put(b, 0, 14);
    aefd_put(b, 1, 91);
    bad(h, b);
    puts("note create codec canonical states and corruption controls pass");
    assert(cases >= 40);
    return 0;
}
