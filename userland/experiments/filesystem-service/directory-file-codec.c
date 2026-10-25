/* SPDX-License-Identifier: BSD-2-Clause */
/* C producer/consumer around the actual Rust FILE owner. No transport double.
 */
#include "fd-protocol.h"
#include <assert.h>
#include <stdio.h>
static void emit(FILE *f)
{
    unsigned char header[64], body[256];
    const uint64_t operations[4] = {8, 9, 8, 9};
    const char *paths[4] = {"/work//nested", NULL, "../..", NULL};
    for (unsigned i = 0; i < 4; ++i) {
        size_t length = paths[i] ? strlen(paths[i]) : 0;
        uint64_t args[4] = {0, length, 0, 0};
        assert(aefd_request(header, 31, i + 1, operations[i], args));
        assert(fwrite(header, 1, 64, f) == 64);
        if (length) {
            assert(aefd_name(body, (const unsigned char *)paths[i], length));
            assert(fwrite(body, 1, 64, f) == 64);
        }
    }
}
static void check(FILE *f)
{
    unsigned char header[64], body[256], out[4096];
    for (unsigned i = 0; i < 4; ++i) {
        assert(fread(header, 1, 64, f) == 64);
        struct aefd_reply reply;
        uint64_t op = i % 2 ? 9 : 8;
        assert(aefd_decode(header, 64, 31, i + 1, op, 0, &reply));
        assert(!reply.status);
        if (op == 9) {
            const char *expected = i == 1 ? "/work/nested" : "/";
            assert(reply.body == strlen(expected) + 1 &&
                   reply.result == reply.body);
            size_t padded = (reply.body + 63) / 64 * 64;
            assert(fread(body, 1, padded, f) == padded &&
                   aefd_body(out, body, padded, reply.body));
            assert(!memcmp(out, expected, reply.body));
        }
        for (unsigned field = 0; field < 8; ++field) {
            unsigned char bad[64];
            memcpy(bad, header, 64);
            if (field == 0)
                bad[7] = '2';
            else if (field == 1)
                aefd_put(bad, field, 1);
            else if (field == 4 || field == 5)
                aefd_put(bad, field, 257);
            else
                aefd_put(bad, field, UINT64_MAX);
            assert(!aefd_decode(bad, 64, 31, i + 1, op, 0, &reply));
        }
        for (size_t length = 0; length < 64; ++length)
            assert(!aefd_decode(header, length, 31, i + 1, op, 0, &reply));
    }
    assert(fgetc(f) == EOF);
}
int main(int argc, char **argv)
{
    assert(argc == 3);
    FILE *f = fopen(argv[2], !strcmp(argv[1], "emit") ? "wb" : "rb");
    assert(f);
    if (!strcmp(argv[1], "emit"))
        emit(f);
    else {
        assert(!strcmp(argv[1], "check"));
        check(f);
    }
    assert(!fclose(f));
    puts("AF08 public C/Rust/C codec passes");
}
