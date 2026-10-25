/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-protocol.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef AEFD_PATH_WIRE
#define OPEN_NAME "/dir/file"
#else
#define OPEN_NAME "file"
#endif
#ifdef AEFD_DUP2_WIRE
#define OPERATIONS 12U
static const uint64_t operations[OPERATIONS] = {1, 2, 4, 7, 5, 2,
                                                3, 2, 6, 5, 5, 99};
static const uint64_t arguments[OPERATIONS][4] = {
    {0, sizeof OPEN_NAME - 1, 0, 0},
    {0, 2, 0, 0},
    {0, 0, 0, 0},
    {1, 15, 0, 0},
    {0, 0, 0, 0},
    {15, 2, 0, 0},
    {1, UINT64_MAX, 2, 0},
    {15, 8, 0, 0},
    {15, 1, 0, 0},
    {1, 0, 0, 0},
    {15, 0, 0, 0},
    {0, 0, 0, 0}};
static const uint64_t expected[OPERATIONS] = {0, 2, 1, 15, 0, 2,
                                              5, 1, 0, 0,  0, 0};
#else
#define OPERATIONS 10U
static const uint64_t operations[OPERATIONS] = {1, 2, 4, 5, 2, 3, 2, 6, 5, 99};
static const uint64_t arguments[OPERATIONS][4] = {
    {0, sizeof OPEN_NAME - 1, 0, 0},
    {3, 2, 0, 0},
    {3, 0, 0, 0},
    {3, 0, 0, 0},
    {4, 2, 0, 0},
    {4, UINT64_MAX, 2, 0},
    {4, 8, 0, 0},
    {4, 1, 0, 0},
    {4, 0, 0, 0},
    {0, 0, 0, 0}};
static const uint64_t expected[OPERATIONS] = {3, 2, 4, 0, 2, 5, 1, 0, 0, 0};
#endif
static void names(void)
{
    unsigned char out[256], full[256];
    const char *valid[] = {"file",
                           "..suffix",
                           ".hidden"
#ifdef AEFD_PATH_WIRE
                           ,
                           "/",
                           "/dir/file",
                           "dir/file",
                           "/.hidden/file"
#endif
    };
    const char *invalid[] = {"",
                             ".",
                             "..",
                             "a//b",
                             "a/./b",
                             "a/../b",
                             "//file",
                             "a/"
#ifndef AEFD_PATH_WIRE
                             ,
                             "/",
                             "/dir/file",
                             "dir/file"
#endif
    };
    for (size_t i = 0; i < sizeof valid / sizeof *valid; ++i) {
        size_t length = strlen(valid[i]);
        memset(out, 0x77, sizeof out);
        assert(aefd_name(out, (const unsigned char *)valid[i], length));
        assert(!memcmp(out, valid[i], length));
        for (size_t j = length; j < sizeof out; ++j)
            assert(!out[j]);
        assert(aefd_name(out, out, length));
    }
    for (size_t i = 0; i < sizeof invalid / sizeof *invalid; ++i) {
        memset(out, 0x77, sizeof out);
        assert(!aefd_name(out, (const unsigned char *)invalid[i],
                          strlen(invalid[i])));
        for (size_t j = 0; j < sizeof out; ++j)
            assert(!out[j]);
    }
    memset(full, 'x', sizeof full);
    assert(aefd_name(out, full, 255));
    assert(out[254] == 'x' && !out[255]);
    assert(!aefd_name(out, full, 256));
    for (size_t i = 0; i < sizeof out; ++i)
        assert(!out[i]);
    full[3] = 0;
    assert(!aefd_name(out, full, 255));
    for (size_t i = 0; i < sizeof out; ++i)
        assert(!out[i]);
}

static int emit(void)
{
    for (size_t i = 0; i < OPERATIONS; ++i) {
        unsigned char frame[AEFD_FRAME];
        assert(aefd_request(frame, 77, i + 1, operations[i], arguments[i]));
        assert(fwrite(frame, 1, sizeof(frame), stdout) == sizeof(frame));
        if (i == 0) {
            unsigned char body[256];
            assert(aefd_name(body, (const unsigned char *)OPEN_NAME,
                             sizeof OPEN_NAME - 1));
            assert(fwrite(body, 1, 64, stdout) == 64);
        }
    }
    return 0;
}
static int verify(const char *path)
{
    FILE *stream = fopen(path, "rb");
    assert(stream);
    unsigned rejected = 0;
    for (size_t i = 0; i < OPERATIONS; ++i) {
        unsigned char frame[AEFD_FRAME];
        assert(fread(frame, 1, sizeof(frame), stream) == sizeof(frame));
        struct aefd_reply reply = {7, 8, 9};
        assert(aefd_decode(frame, sizeof(frame), 77, i + 1, operations[i],
                           (size_t)arguments[i][1], &reply));
        assert(reply.status == (i == OPERATIONS - 1U ? -38 : 0));
        assert(reply.result == expected[i]);
        unsigned char opposite[AEFD_FRAME];
        memcpy(opposite, frame, sizeof opposite);
#ifdef AEFD_DUP2_WIRE
        memcpy(opposite, "AEFP0001", 8);
#elif defined(AEFD_PATH_WIRE)
        memcpy(opposite, "AEFD0001", 8);
#else
        memcpy(opposite, "AEFP0001", 8);
#endif
        struct aefd_reply sentinel = {7, 8, 9};
        assert(!aefd_decode(opposite, sizeof opposite, 77, i + 1, operations[i],
                            (size_t)arguments[i][1], &sentinel));
        assert(sentinel.status == 7 && sentinel.result == 8 &&
               sentinel.body == 9);
        for (unsigned field = 0; field < 8; ++field) {
            unsigned char bad[AEFD_FRAME];
            memcpy(bad, frame, sizeof(bad));
            if (field == 4 || field == 5)
                aefd_put(bad, field, UINT64_MAX);
            else if (field == 1)
                aefd_put(bad, field, 1);
            else
                bad[field * 8U] ^= 0x40;
            struct aefd_reply sentinel = {7, 8, 9};
            assert(!aefd_decode(bad, sizeof(bad), 77, i + 1, operations[i],
                                (size_t)arguments[i][1], &sentinel));
            assert(sentinel.status == 7 && sentinel.result == 8 &&
                   sentinel.body == 9);
            ++rejected;
        }
        if (reply.body) {
            unsigned char raw[AEFD_READ_MAX], out[AEFD_READ_MAX];
            size_t padded = (reply.body + 63U) / 64U * 64U;
            assert(fread(raw, 1, padded, stream) == padded);
            memset(out, 0x77, sizeof(out));
            assert(aefd_body(out, raw, padded, reply.body));
            const char *bytes = i == 1 ? "ab" : (reply.body == 2 ? "cd" : "f");
            assert(memcmp(out, bytes, reply.body) == 0);
            assert(aefd_body(out, out, padded, reply.body));
            assert(memcmp(out, bytes, reply.body) == 0);
            for (size_t j = reply.body; j < sizeof(out); ++j)
                assert(out[j] == 0);
            raw[reply.body] = 1;
            assert(!aefd_body(out, raw, padded, reply.body));
            for (size_t j = 0; j < sizeof(out); ++j)
                assert(out[j] == 0);
        }
    }
    assert(fgetc(stream) == EOF && !ferror(stream));
    assert(fclose(stream) == 0);
    unsigned char full[AEFD_READ_MAX];
    memset(full, 0x55, sizeof(full));
    assert(aefd_body(full, full, sizeof(full), sizeof(full)));
    for (size_t i = 0; i < sizeof(full); ++i)
        assert(full[i] == 0x55);
    assert(!aefd_body(full, full, sizeof(full), AEFD_READ_MAX + 1U));
    for (size_t i = 0; i < sizeof(full); ++i)
        assert(full[i] == 0);
    memset(full, 0x77, sizeof(full));
    assert(aefd_body(full, NULL, 0, 0));
    for (size_t i = 0; i < sizeof(full); ++i)
        assert(full[i] == 0);
    assert(rejected == OPERATIONS * 8U);
    printf("%u actual Rust replies / %u malformed headers / 3 padded-body "
           "denials pass\n",
           OPERATIONS, rejected);
    return 0;
}
int main(int argc, char **argv)
{
    names();
    if (argc == 2 && strcmp(argv[1], "emit") == 0)
        return emit();
    if (argc == 3 && strcmp(argv[1], "verify") == 0)
        return verify(argv[2]);
    return 64;
}
