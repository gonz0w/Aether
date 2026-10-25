/* SPDX-License-Identifier: BSD-2-Clause */
#include "four-role.h"
#include "runner-result.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#undef ar_roles_decode
#undef ar_admission
#undef ar_collection
#undef ar_terminal_exit
int ar_roles_decode(const unsigned char *, size_t, uint32_t, struct ar_roles *);
enum ar_reply_action ar_admission(const unsigned char *, size_t, uint32_t,
                                  struct ar_reply *);
enum ar_reply_action ar_collection(const unsigned char *, size_t, uint32_t,
                                   struct ar_reply *);
unsigned ar_terminal_exit(const struct ar_reply *, int);
static void put(unsigned char *p, uint32_t x)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (unsigned char)(x >> (8 * i));
}
static void roles(unsigned char *p, uint32_t epoch)
{
    const uint32_t refs[] = {0x75010000, 0x75020000, 0x71000000, 0x71010000};
    const uint32_t rights[] = {2, 2, 1, 3};
    const uint32_t caps[] = {512, 256, 6, 64};
    memset(p, 0, 160);
    memcpy(p, "AERIO002", 8);
    put(p + 8, 4);
    put(p + 12, epoch);
    for (unsigned i = 0; i < 4; ++i) {
        unsigned char *r = p + 32 + i * 32;
        put(r, i + 1);
        put(r + 4, refs[i] | epoch);
        put(r + 8, i + 1);
        put(r + 12, rights[i]);
        put(r + 16, caps[i]);
    }
}
int main(void)
{
    unsigned char p[160], reply[32];
    struct ar_roles bindings, untouched;
    struct ar_reply out, sentinel;
    memset(&untouched, 0xa5, sizeof untouched);
    memset(&sentinel, 0xa5, sizeof sentinel);
    for (uint32_t epoch = 1; epoch <= 65535; ++epoch) {
        roles(p, epoch);
        assert(ar_roles_decode_sustained_v2(p, 160, epoch, &bindings));
        assert(bindings.refs[3] == (0x71010000u | epoch));
        bindings = untouched;
        assert(!ar_roles_decode(p, 160, epoch, &bindings));
        assert(!memcmp(&bindings, &untouched, sizeof bindings));
        p[7] = '1';
        assert(!ar_roles_decode_sustained_v2(p, 160, epoch, &bindings));
        assert(!memcmp(&bindings, &untouched, sizeof bindings));
        if (epoch <= 2)
            assert(ar_roles_decode(p, 160, epoch, &bindings));
        memset(reply, 0, sizeof reply);
        uint32_t receipt = 0x7b000000u | epoch;
        put(reply + 4, receipt);
        assert(ar_admission_sustained_v2(reply, 32, epoch, &out) ==
               AR_REPLY_ADMITTED);
        out = sentinel;
        assert(ar_admission(reply, 32, epoch, &out) == AR_REPLY_INVALID);
        assert(!memcmp(&out, &sentinel, sizeof out));
        put(reply + 8, 17);
        put(reply + 12, 1);
        assert(ar_collection_sustained_v2(reply, 32, receipt, &out) ==
               AR_REPLY_COLLECTED);
        assert(ar_terminal_exit_sustained_v2(&out, 1) == 17);
        assert(ar_terminal_exit(&out, 1) == 1);
        out = sentinel;
        assert(ar_collection(reply, 32, receipt, &out) == AR_REPLY_INVALID);
        assert(!memcmp(&out, &sentinel, sizeof out));
        if (epoch > 1) {
            assert(ar_collection_sustained_v2(reply, 32, receipt - 1, &out) ==
                   AR_REPLY_INVALID);
            assert(!memcmp(&out, &sentinel, sizeof out));
        }
    }
    for (uint32_t epoch = 1; epoch <= 2; ++epoch) {
        memset(reply, 0, sizeof reply);
        uint32_t old = 0x73000000u | epoch;
        put(reply + 4, old);
        assert(ar_admission(reply, 32, epoch, &out) == AR_REPLY_ADMITTED);
        out = sentinel;
        assert(ar_admission_sustained_v2(reply, 32, epoch, &out) ==
               AR_REPLY_INVALID);
        assert(!memcmp(&out, &sentinel, sizeof out));
        put(reply + 8, 17);
        put(reply + 12, 1);
        assert(ar_collection(reply, 32, old, &out) == AR_REPLY_COLLECTED);
        assert(ar_terminal_exit(&out, 1) == 17);
        assert(ar_terminal_exit_sustained_v2(&out, 1) == 1);
        out = sentinel;
        assert(ar_collection_sustained_v2(reply, 32, old, &out) ==
               AR_REPLY_INVALID);
        assert(!memcmp(&out, &sentinel, sizeof out));
    }
    const uint32_t bad[] = {0, 65536, 0x0fffffff, UINT32_MAX};
    for (unsigned i = 0; i < sizeof bad / sizeof bad[0]; ++i) {
        roles(p, bad[i]);
        bindings = untouched;
        assert(!ar_roles_decode_sustained_v2(p, 160, bad[i], &bindings));
        assert(!memcmp(&bindings, &untouched, sizeof bindings));
        out = sentinel;
        assert(ar_admission_sustained_v2(reply, 32, bad[i], &out) ==
               AR_REPLY_INVALID);
        assert(!memcmp(&out, &sentinel, sizeof out));
    }
    puts("PASS: 65535 epochs, stale replies, old/new rejection and overflow");
    return 0;
}
