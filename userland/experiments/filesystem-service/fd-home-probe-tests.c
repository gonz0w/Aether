/* SPDX-License-Identifier: BSD-2-Clause */
/* Real context/native/table/facade and codec with a typed host transport only.
 */
#include "fd-home-probe-adapter.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(value, marker)                                                   \
    do {                                                                       \
        if (!(value)) {                                                        \
            fprintf(stderr, "%s:%d\n", marker, __LINE__);                      \
            exit(1);                                                           \
        }                                                                      \
    } while (0)
struct fixture {
    struct aefd_context context;
    unsigned char request[128], reply[128], contents[16];
    size_t received, sent, reply_size, position;
    unsigned calls, blocks, restores, rpcs, writes, closes, mode, next;
    uint64_t current;
};
static void response(struct fixture *f)
{
    const unsigned char payload[] = "AF09-HOME-WRITE\n";
    uint64_t operation = aefd_word(f->request, 1);
    memset(f->reply, 0, sizeof(f->reply));
    memcpy(f->reply, AEFD_MAGIC, 8);
    aefd_put(f->reply, 2, 31);
    aefd_put(f->reply, 3, aefd_word(f->request, 3));
    f->reply_size = 64;
    ++f->rpcs;
    if (operation == 1 || operation == 10) {
        CHECK(!memcmp(f->request + 64, operation == 1 ? "/zstd" : "probe", 5),
              "HOME_PROBE_NAME");
        f->current = f->mode == 3 ? 0 : f->next++;
        f->position = 0;
        aefd_put(f->reply, 4, f->current);
    } else if (operation == 11) {
        CHECK(aefd_word(f->request, 5) == 16 &&
                  !memcmp(f->request + 64, payload, 16),
              "HOME_PROBE_PAYLOAD");
        aefd_put(f->reply, 5, 64);
        f->reply_size = 128;
        if (f->current >= 2) {
            aefd_put(f->reply, 1, (uint64_t)-22);
            aefd_put(f->reply + 64, 0, 8);
            aefd_put(f->reply + 64, 6, 7);
        } else {
            ++f->writes;
            memcpy(f->contents, payload, 16);
            f->position = 16;
            aefd_put(f->reply, 4, 16);
            aefd_put(f->reply + 64, 0, 14);
            if (f->mode == 6)
                aefd_put(f->reply + 64, 1, 1);
            aefd_put(f->reply + 64, 2, 790);
            aefd_put(f->reply + 64, 3, f->mode == 4 ? 15 : 16);
        }
    } else if (operation == 2) {
        size_t n = f->position < 16 ? 16 - f->position : 0;
        if (n > aefd_word(f->request, 5))
            n = (size_t)aefd_word(f->request, 5);
        if (f->mode == 8 && !n)
            n = 1;
        if (f->mode == 9 && n == 16)
            n = 15;
        aefd_put(f->reply, 4, n);
        if (n) {
            aefd_put(f->reply, 5, n);
            if (f->position < 16)
                memcpy(f->reply + 64, f->contents + f->position, n);
            if (f->mode == 7)
                f->reply[64] ^= 1;
            f->reply_size = 128;
            f->position += n;
        }
    } else if (operation == 5) {
        ++f->closes;
        if (f->mode == 5)
            aefd_put(f->reply, 1, (uint64_t)-5);
    } else
        CHECK(0, "HOME_PROBE_OPCODE");
}
static int64_t call(void *owner, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t tail)
{
    struct fixture *f = owner;
    ++f->calls;
    if (op == 0x1000e) {
        CHECK(tail == 8, "HOME_PROBE_MASK");
        if (!cap) {
            ++f->blocks;
            *(uint64_t *)(uintptr_t)b = 123;
            return f->mode == 1 ? -14 : 0;
        }
        CHECK(cap == 2 && *(uint64_t *)(uintptr_t)a == 123, "HOME_PROBE_MASK");
        ++f->restores;
        return 0;
    }
    if (op == 0x24003) {
        CHECK(cap == 71 || cap == 72, "HOME_PROBE_TRANSPORT_CLOSE");
        return 0;
    }
    CHECK(f->context.native.active && f->context.native.busy &&
              f->blocks == f->restores + 1,
          "HOME_PROBE_GUARD");
    CHECK(!tail && a && b && b <= 16, "HOME_PROBE_TRANSFER");
    if (op == 0x24002) {
        CHECK(cap == 72 && f->received + b <= 128, "HOME_PROBE_REQUEST");
        memcpy(f->request + f->received, (void *)(uintptr_t)a, (size_t)b);
        f->received += (size_t)b;
        uint64_t operation = aefd_word(f->request, 1);
        if (f->received ==
            ((operation == 1 || operation == 10 || operation == 11) ? 128U
                                                                    : 64U))
            response(f);
        return (int64_t)b;
    }
    CHECK(op == 0x24001 && cap == 71 && f->sent + b <= f->reply_size,
          "HOME_PROBE_REPLY");
    memcpy((void *)(uintptr_t)a, f->reply + f->sent, (size_t)b);
    f->sent += (size_t)b;
    if (f->sent == f->reply_size) {
        f->sent = f->received = f->reply_size = 0;
        memset(f->request, 0, sizeof(f->request));
    }
    return (int64_t)b;
}
static void init(struct fixture *f, unsigned mode)
{
    memset(f, 0, sizeof(*f));
    f->mode = mode;
    unsigned char raw[128] = {0};
    memcpy(raw, AEFD_MAP_MAGIC, 8);
    aefd_put(raw, 1, 31);
    aefd_put(raw, 2, 16);
    const struct aefd_native_source sources[7] = {{0}};
    const unsigned history[2] = {0};
    CHECK(!aefd_context_init(&f->context, call, f, 71, 72, raw, 128, 31,
                             sources, history, 0),
          "HOME_PROBE_CONTEXT");
}
int main(void)
{
    struct fixture f;
    init(&f, 0);
    CHECK(aefd_home_probe_run(&f.context) == 0 && f.writes == 1 &&
              f.closes == 3,
          "HOME_PROBE_WORKLOAD");
    CHECK(f.blocks == f.restores && !f.context.native.active,
          "HOME_PROBE_BALANCED");
    for (unsigned i = 0; i < 16; ++i)
        CHECK(f.context.map.slots[i].kind == 0, "HOME_PROBE_MAP_EMPTY");
    init(&f, 1);
    CHECK(aefd_home_probe_run(&f.context) != 0 && !f.rpcs,
          "HOME_PROBE_MASK_DENIAL");
    init(&f, 0);
    f.context.native.active = 1;
    CHECK(aefd_home_probe_run(&f.context) != 0 && !f.calls,
          "HOME_PROBE_REENTRY");
    init(&f, 0);
    f.context.map.generation = 99;
    CHECK(aefd_home_probe_run(&f.context) != 0 && !f.rpcs,
          "HOME_PROBE_MAP_GENERATION");
    init(&f, 3);
    f.context.map.slots[7] = (struct aefd_binding){AEFD_BIND_FILE, 0, 0, 0};
    CHECK(aefd_home_probe_run(&f.context) != 0 &&
              f.context.map.slots[7].kind == AEFD_BIND_FILE && !f.closes,
          "HOME_PROBE_ALIAS");
    init(&f, 4);
    CHECK(aefd_home_probe_run(&f.context) != 0 && f.writes == 1,
          "HOME_PROBE_RECEIPT");
    init(&f, 5);
    CHECK(aefd_home_probe_run(&f.context) != 0 &&
              f.context.map.slots[0].kind == AEFD_BIND_FILE && f.closes == 1,
          "HOME_PROBE_FINAL_CLOSE");
    for (unsigned mode = 6; mode <= 9; ++mode) {
        init(&f, mode);
        CHECK(aefd_home_probe_run(&f.context) != 0 && f.writes == 1,
              "HOME_PROBE_OFFSET_READ_EOF");
    }
    puts("11 real guarded home probe scenarios pass");
    return 0;
}
