/* SPDX-License-Identifier: BSD-2-Clause */
/* Local typed transport and native-mask doubles; no native admission. */
#include "fd-context.h"
#include <assert.h>
#include <stdio.h>
#ifdef AEFD_NOTE_PROVIDER_TEST
#define c (aefd_shell_external_startup()->context)
#else
static struct aefd_context c;
#endif
static struct {
    unsigned char request[128], reply[128];
    size_t sent, read, length;
    unsigned requests, closes, next;
    uint64_t mask;
    int mode;
} f;
static void answer(void)
{
    unsigned char *h = f.reply, *b = h + 64;
    uint64_t op = aefd_word(f.request, 1);
    memset(h, 0, 128);
    memcpy(h, AEFD_MAGIC, 8);
    aefd_put(h, 2, 31);
    aefd_put(h, 3, aefd_word(f.request, 3));
    f.length = 64;
    if (op == 12) {
        assert(aefd_word(f.request, 4) <= 1 && aefd_word(f.request, 5) == 10);
        assert(aefd_word(f.request, 6) == 0600 && !aefd_word(f.request, 7));
        assert(!memcmp(f.request + 64, "/home/note", 10));
        for (unsigned i = 74; i < 128; i++)
            assert(!f.request[i]);
        aefd_put(h, 4, 3);
        aefd_put(h, 5, 64);
        aefd_put(b, 0, 6);
        aefd_put(b, 1, 91);
        f.length = 128;
        if (f.mode == 3) {
            aefd_put(h, 1, (uint64_t)-13);
            aefd_put(h, 4, 0);
            aefd_put(b, 0, 22);
            aefd_put(b, 4, (uint64_t)INT64_MIN);
            aefd_put(b, 5, INT64_MAX);
            aefd_put(b, 6, 12);
            aefd_put(b, 7, (uint64_t)-13);
        }
        if (f.mode == 1)
            aefd_put(h, 3, 999);
    } else if (op == 4) {
        assert(aefd_word(f.request, 4) >= 3);
        aefd_put(h, 4, f.next++);
        if (f.mode == 5)
            aefd_put(h, 3, 999);
    } else if (op == 11) {
        assert(aefd_word(f.request, 4) == 4 && aefd_word(f.request, 5) == 16);
        assert(!memcmp(f.request + 64, "AETHER-HOME-158\n", 16));
        for (unsigned i = 80; i < 128; i++)
            assert(!f.request[i]);
        aefd_put(h, 4, 16);
        aefd_put(h, 5, 64);
        aefd_put(b, 0, 14);
        aefd_put(b, 2, 92);
        aefd_put(b, 3, 16);
        f.length = 128;
    } else {
        assert(op == 5);
        if (f.mode == 6)
            aefd_put(h, 1, (uint64_t)-13);
    }
    f.requests++;
    f.read = 0;
}
static int64_t native(void *unused, uint64_t op, uint64_t cap, uint64_t a,
                      uint64_t b, uint64_t d)
{
    (void)unused;
    assert(!d || op == 0x1000e);
    if (op == 0x1000e) {
        assert(d == 8);
        if (!cap) {
            *(uint64_t *)(uintptr_t)b = f.mask;
            f.mask = UINT64_MAX;
        } else {
            assert(cap == 2);
            f.mask = *(uint64_t *)(uintptr_t)a;
        }
        return 0;
    }
    if (op == 0x24003) {
        assert(cap == 71 || cap == 72);
        f.closes++;
        return cap == 71 ? -17 : 23;
    }
    assert(op == 0x24001 || op == 0x24002);
    assert(f.mask == UINT64_MAX && b <= 16);
    assert(cap == (op == 0x24001 ? 71 : 72));
    size_t n = b < 7 ? (size_t)b : 7;
    if (op == 0x24002) {
        assert(f.sent + n <= 128);
        memcpy(f.request + f.sent, (void *)(uintptr_t)a, n);
        f.sent += n;
        if (f.sent >= 64) {
            uint64_t opcode = aefd_word(f.request, 1);
            if (f.sent == (opcode == 12 || opcode == 11 ? 128U : 64U))
                answer();
        }
    } else {
        if (f.mode == 2 && f.read >= 70)
            return 0;
        assert(f.read < f.length);
        if (n > f.length - f.read)
            n = f.length - f.read;
        memcpy((void *)(uintptr_t)a, f.reply + f.read, n);
        f.read += n;
        if (f.read == f.length)
            f.sent = 0;
    }
    return (int64_t)n;
}
static void setup(int mode)
{
    memset(&c, 0, sizeof c);
    memset(&f, 0, sizeof f);
    f.mask = 0x1234;
    f.mode = mode;
    f.next = 4;
    unsigned char raw[128] = {0};
    memcpy(raw, AEFD_MAP_MAGIC, 8);
    aefd_put(raw, 1, 31);
    aefd_put(raw, 2, 16);
    struct aefd_native_source sources[7] = {{0}};
    for (unsigned i = 0; i < 3; i++) {
        raw[64 + i * 4] = AEFD_BIND_TERMINAL;
        raw[65 + i * 4] = (unsigned char)i;
        sources[i] = (struct aefd_native_source){
            UINT32_C(0x7a000001) | (i << 16), i, i ? 2U : 1U, 16};
    }
    unsigned history[2] = {0};
    assert(!aefd_context_init(&c, native, NULL, 71, 72, raw, 128, 31, sources,
                              history, 0));
}
static int create(void)
{
    return (int)aefd_context_create_note(
        &c, (const unsigned char *)"/home/note", 10, 1, 0600);
}
static void close_client(void)
{
    aefd_client_abort(&c.client);
    assert(f.closes == 2);
    assert(f.mask == 0x1234);
}
int main(void)
{
    setup(0);
    assert(create() == 3);
    assert(c.note_create.observation == AEFD_WRITE_REMOTE);
    struct aefd_note_create_result kept = c.note_create;
    assert(c.note_create.remote.txg == 91 && c.note_create.remote.fd == 3);
    unsigned before = f.requests;
    assert(create() == -16 && f.requests == before);
    assert(aefd_context_note_replace(&c, 3, 3) == 3 &&
           c.map.slots[3].cloexec == 1);
    c.map.slots[4] = (struct aefd_binding){AEFD_BIND_FILE, 9, 0, 0};
    assert(aefd_context_note_replace(&c, 3, 4) == -38 && f.requests == before);
    memset(&c.map.slots[4], 0, sizeof c.map.slots[4]);
    unsigned char untouched = 99;
    assert(aefd_context_read(&c, 3, &untouched, 1) == -9 && untouched == 99);
    assert(aefd_context_seek(&c, 3, 0, 0) == -9 && f.requests == before);
    assert(aefd_context_dup(&c, 1, 10, 1) == 10); /* save actual terminal */
    assert(aefd_context_note_replace(&c, 3, 1) == 1);
    assert(c.note_redirect.committed);
    assert(c.map.slots[1].selector == 4 && !c.map.slots[1].cloexec);
    struct aefd_binding binding;
    unsigned rights;
    assert(!aefd_context_describe(&c, 1, &binding, &rights) && rights == 2);
    assert(!aefd_context_close(&c, 3));
    assert(aefd_context_write(&c, 1, (const unsigned char *)"AETHER-HOME-158\n",
                              16) == 16);
    struct aefd_write_result write = c.note_write;
    assert(write.remote.txg == 92 && write.remote.offset == 0);
    assert(aefd_context_write(&c, 1, (const unsigned char *)"x", 1) == -16);
    assert(aefd_context_note_replace(&c, 10, 1) == 1);
    assert(!c.note_writers);
    assert(c.map.slots[1].kind == AEFD_BIND_TERMINAL &&
           c.map.slots[1].selector == 1);
    assert(!memcmp(&kept, &c.note_create, sizeof kept));
    assert(!memcmp(&write, &c.note_write, sizeof write));
    assert(!aefd_context_close(&c, 10));
    close_client();
    for (int mode = 1; mode <= 3; mode++) {
        setup(mode);
        assert(create() < 0);
        assert(c.map.slots[3].kind == AEFD_BIND_EMPTY);
        assert(!c.client.live && f.closes == 2 && c.note_create.file_closed);
        assert(c.note_create.file_cleanup.input == -17 &&
               c.note_create.file_cleanup.output == 23);
        if (mode == 3) {
            assert(c.note_create.observation == AEFD_WRITE_REMOTE &&
                   c.note_create.remote.txg == 91);
            assert(c.note_create.remote.post_kind == 12 &&
                   c.note_create.remote.post_value == -13);
            assert(c.note_create.remote.source_cleanup.input == INT64_MIN);
        } else
            assert(c.note_create.observation == AEFD_WRITE_UNKNOWN &&
                   !c.note_create.remote.txg);
    }
    setup(4);
    c.map.slots[9] = (struct aefd_binding){AEFD_BIND_FILE, 3, 0, 0};
    assert(create() == -5 && c.note_create.observation == AEFD_WRITE_REMOTE);
    assert(c.note_create.remote.txg == 91 &&
           c.note_create.installation_status == -5);
    assert(c.note_create.file_closed && f.closes == 2);
    setup(5);
    assert(create() == 3);
    assert(aefd_context_note_replace(&c, 3, 1) == -5);
    assert(c.note_redirect.unknown && c.note_redirect.unresolved &&
           !c.client.live && !c.note_writers);
    setup(6);
    assert(create() == 3);
    assert(aefd_context_note_replace(&c, 1, 3) == -13);
    assert(c.note_redirect.target_attempted && !c.note_redirect.committed &&
           !c.client.live);
    assert(c.note_redirect.target_status == -13 && f.closes == 2);
    setup(0);
    for (unsigned i = 3; i < 16; i++)
        c.map.slots[i] = (struct aefd_binding){AEFD_BIND_TERMINAL, 1, 0, 0};
    assert(create() == -24 && !f.requests &&
           c.note_create.observation == AEFD_WRITE_NOT_SENT);
    close_client();
    puts("note context create/alias/redirect/restore/unknown containment pass");
    return 0;
}
