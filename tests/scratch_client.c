/* SPDX-License-Identifier: BSD-2-Clause */
/* Host transport witness; not native authority or libc conformance. */
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(condition)                                                       \
    do {                                                                       \
        if (!(condition)) {                                                    \
            fprintf(stderr, "CHECK failed: %s\n", #condition);                 \
            exit(90);                                                          \
        }                                                                      \
    } while (0)
#define BINDINGS 5
struct startup_fd {
    unsigned binding;
    int flags, present;
};
static struct startup_fd startup_fds[16];
static unsigned startup_users[5], refs[5], fds[5], rights[5];
static int live[5], startup_ready, poisoned;
static unsigned char grant[32];
static int calls, response, masked, masks, restores;
static unsigned get(const unsigned char *b, unsigned i)
{
    unsigned v;
    memcpy(&v, b + i, 4);
    return v;
}
static void put(unsigned char *b, unsigned i, unsigned v)
{
    memcpy(b + i, &v, 4);
}
static long memtrap(unsigned long op, unsigned long a, unsigned long b,
                    unsigned long c, unsigned long d)
{
    (void)a;
    (void)b;
    (void)c;
    (void)d;
    CHECK(op == 0x20005);
    return 7;
}
static long startup_mask_enter(uint64_t *p)
{
    CHECK(!masked);
    masked = 1;
    ++masks;
    *p = 77;
    return 0;
}
static void startup_mask_leave(uint64_t p)
{
    CHECK(masked && p == 77);
    masked = 0;
    ++restores;
}
static int startup_error(int e)
{
    errno = e;
    return -1;
}
static int move(unsigned char *b, unsigned n, int writing)
{
    CHECK(masked && n == 32 && !writing);
    memcpy(b, grant, 32);
    return 1;
}
static int exchange(unsigned char *b, unsigned n)
{
    CHECK(masked && n == 32);
    ++calls;
    CHECK(get(b, 0) == 6 && get(b, 4) == 0xfd010701 && !get(b, 8));
    CHECK(get(b, 12) == 1 || get(b, 12) == 14);
    CHECK(!memcmp(b + 16, "/scratch/data\0\0\0", 16));
    memset(b, 0, 32);
    if (response == 5)
        return 0;
    if (response == 1) {
        put(b, 0, (unsigned)-ENOENT);
        return 1;
    }
    put(b, 4, 0xfc010711);
    put(b, 8, response == 3 ? 99 : 3);
    if (response == 2)
        b[31] = 1;
    return 1;
}
#include "../user/native-connections/scratch-client.h"
#include "../user/native-connections/scratch-restore.h"
#include "../user/native-connections/scratch-fork.h"
static void reset(void)
{
    memset(startup_fds, 0, sizeof startup_fds);
    memset(startup_users, 0, sizeof startup_users);
    memset(refs, 0, sizeof refs);
    memset(fds, 0, sizeof fds);
    memset(rights, 0, sizeof rights);
    memset(live, 0, sizeof live);
    startup_ready = 1;
    poisoned = 0;
    scratch_root = 0;
    calls = response = masked = masks = restores = 0;
    memset(grant, 0, 32);
    memcpy(grant, "AESFD001", 8);
    put(grant, 8, 0xfd010701);
    put(grant, 12, 7);
    put(grant, 16, 3);
    put(grant, 20, 2);
    for (unsigned i = 0; i < 3; ++i)
        startup_fds[i] = (struct startup_fd){i, 0, 1};
}
static void accepted(void)
{
    reset();
    CHECK(scratch_accept());
}
static void restore_setup(unsigned char table[64], unsigned char records[32])
{
    accepted();
    memset(table, 0, 64);
    memset(records, 0, 32);
    for (unsigned j = 0; j < 3; ++j) {
        live[j] = startup_users[j] = 1;
        refs[j] = 0x76000007u + (j << 16);
        fds[j] = j;
        rights[j] = j ? 2 : 1;
        table[j * 4] = j;
        table[j * 4 + 2] = 1;
    }
    table[36] = table[44] = 3;
    table[38] = table[46] = 1;
    table[60] = 4;
    table[62] = 1;
    put(records, 0, 0xfc010711);
    put(records, 4, 14);
    put(records, 8, 2);
    put(records, 16, 0xfc010722);
    put(records, 20, 1);
    put(records, 24, 1);
}
static void restore_reject(unsigned char table[64], unsigned char records[32])
{
    unsigned char before[sizeof startup_fds];
    unsigned before_users[5], before_refs[5], before_rights[5], before_fds[5];
    int before_live[5];
    memcpy(before, startup_fds, sizeof before);
    memcpy(before_users, startup_users, sizeof before_users);
    memcpy(before_refs, refs, sizeof before_refs);
    memcpy(before_rights, rights, sizeof before_rights);
    memcpy(before_fds, fds, sizeof before_fds);
    memcpy(before_live, live, sizeof before_live);
    errno = ERANGE;
    CHECK(!scratch_restore(table, records));
    CHECK(poisoned && !calls && !masked && masks == restores &&
          errno == ERANGE);
    CHECK(!memcmp(before, startup_fds, sizeof before));
    CHECK(!memcmp(before_users, startup_users, sizeof before_users));
    CHECK(!memcmp(before_refs, refs, sizeof before_refs));
    CHECK(!memcmp(before_rights, rights, sizeof before_rights));
    CHECK(!memcmp(before_fds, fds, sizeof before_fds));
    CHECK(!memcmp(before_live, live, sizeof before_live));
}
static void restore_checks(void)
{
    unsigned char table[64], records[32];
    restore_setup(table, records);
    CHECK(scratch_restore(table, records));
    CHECK(startup_users[3] == 2 && startup_users[4] == 1);
    CHECK(refs[3] == 0xfc010711 && refs[4] == 0xfc010722);
    CHECK(rights[3] == 2 && rights[4] == 1 && live[3] && live[4]);
    CHECK(startup_fds[9].binding == 3 && startup_fds[11].binding == 3);
    CHECK(!startup_fds[10].present && !calls && !poisoned);
    restore_reject(table, records); /* Cannot overwrite live bindings. */
    for (unsigned fault = 0; fault < 13; ++fault) {
        restore_setup(table, records);
        switch (fault) {
        case 0:
            table[37] = 1;
            break; /* CLOEXEC is already removed by owner. */
        case 1:
            records[1] ^= 1;
            break; /* Previous process generation. */
        case 2:
            records[2] ^= 1;
            break; /* Wrong owner generation. */
        case 3:
            records[0] ^= 8;
            break; /* Wrong authenticated peer. */
        case 4:
            records[0] ^= 3;
            break; /* Wrong binding slot. */
        case 5:
            put(records, 8, 1);
            break;
        case 6:
            put(records, 20, 2);
            break;
        case 7:
            records[31] = 1;
            break;
        case 8:
            table[39] = 1;
            break;
        case 9:
            table[36] = 5;
            break;
        case 10:
            table[38] = 2;
            break;
        case 11:
            table[16] = 3;
            break; /* Noncanonical absent FD. */
        case 12:
            scratch_root ^= 0x100;
            break;
        }
        restore_reject(table, records);
    }
    restore_setup(table, records);
    scratch_root = 0xfd010702;
    records[0] |= 8;
    records[16] |= 8;
    CHECK(scratch_restore(table, records));
    CHECK(refs[3] == 0xfc010719 && refs[4] == 0xfc01072a);
    restore_setup(table, records);
    scratch_root = 0xfd010702;
    restore_reject(table, records); /* Copied parent references in child. */
    restore_setup(table, records);
    memset(table, 0, 64);
    memset(records, 0, 32);
    CHECK(scratch_restore(table, records));
    for (unsigned j = 0; j < 5; ++j)
        CHECK(!startup_users[j] && !live[j] && !refs[j] && !rights[j]);
    restore_setup(table, records);
    memset(table + 60, 0, 4);
    restore_reject(table, records); /* No orphan description grant. */
    restore_setup(table, records);
    memset(table, 0, 64);
    memset(records, 0, 32);
    for (unsigned i = 0; i < 16; ++i) {
        table[i * 4] = 3;
        table[i * 4 + 2] = 1;
    }
    put(records, 0, 0xfc010761);
    put(records, 4, 14);
    put(records, 8, 16);
    CHECK(scratch_restore(table, records));
    CHECK(startup_users[3] == 16 && !startup_users[0] && !live[0]);
}
static void fork_setup(void)
{
    unsigned char table[64], records[32];
    restore_setup(table, records);
    CHECK(scratch_restore(table, records));
    startup_fds[11].flags = FD_CLOEXEC;
    memset(grant, 0, sizeof grant);
    memcpy(grant, "AESFC001", 8);
    put(grant, 8, 0xfd010702);
    put(grant, 12, 7);
    put(grant, 16, 0xfc010719);
    put(grant, 20, 0xfc01072a);
}
static void fork_checks(void)
{
    fork_setup();
    unsigned counts[5] = {1, 1, 1, 2, 1};
    CHECK(scratch_fork_valid(7, counts));
    counts[3] = 1;
    CHECK(!scratch_fork_valid(7, counts));
    counts[3] = 2;
    CHECK(!scratch_fork_valid(8, counts));
    uint64_t saved;
    CHECK(!startup_mask_enter(&saved));
    CHECK(scratch_fork_rebind());
    startup_mask_leave(saved);
    CHECK(refs[3] == 0xfc010719 && refs[4] == 0xfc01072a);
    CHECK(scratch_root == 0xfd010702 && startup_users[3] == 2 &&
          startup_users[4] == 1 && startup_fds[11].flags == FD_CLOEXEC);
    CHECK(!scratch_fork_valid(7, counts)); /* Nested fork is not admitted. */
    for (unsigned fault = 0; fault < 7; ++fault) {
        fork_setup();
        switch (fault) {
        case 0:
            grant[31] = 1;
            break;
        case 1:
            grant[8] = 1;
            break;
        case 2:
            grant[9] = 8;
            break;
        case 3:
            grant[16] ^= 8;
            break;
        case 4:
            grant[20] ^= 8;
            break;
        case 5:
            grant[18] ^= 1;
            break;
        case 6:
            grant[0] = 'X';
            break;
        }
        unsigned before_refs[5];
        memcpy(before_refs, refs, sizeof before_refs);
        CHECK(!startup_mask_enter(&saved));
        CHECK(!scratch_fork_rebind());
        startup_mask_leave(saved);
        CHECK(!memcmp(before_refs, refs, sizeof before_refs) &&
              scratch_root == 0xfd010701);
        CHECK(startup_users[3] == 2 && startup_fds[11].flags == FD_CLOEXEC);
    }
    fork_setup();
    scratch_root = 0xfd010601;
    refs[3] = 0xfc010611;
    refs[4] = 0xfc010622;
    CHECK(scratch_fork_valid(6, counts));
    CHECK(!startup_mask_enter(&saved));
    CHECK(scratch_fork_rebind());
    startup_mask_leave(saved);
    CHECK(refs[3] == 0xfc010719 && refs[4] == 0xfc01072a);
    for (unsigned fault = 0; fault < 8; ++fault) {
        fork_setup();
        switch (fault) {
        case 0:
            rights[3] = 3;
            break;
        case 1:
            refs[3] ^= 0x10000;
            break;
        case 2:
            refs[3] = 0xfc010701;
            break;
        case 3:
            refs[3] = 0xfc010771;
            break;
        case 4:
            live[3] = 2;
            break;
        case 5:
            fds[4] = 3;
            break;
        case 6:
            counts[3] = 17;
            break;
        case 7:
            refs[4] ^= 8;
            break;
        }
        CHECK(!scratch_fork_valid(7, counts));
        counts[3] = 2;
    }
    fork_setup();
    live[4] = startup_users[4] = 0;
    startup_fds[15].present = 0;
    counts[4] = 0;
    put(grant, 20, 0);
    CHECK(scratch_fork_valid(7, counts)); /* Closed metadata grants nothing. */
    CHECK(!startup_mask_enter(&saved));
    CHECK(scratch_fork_rebind());
    startup_mask_leave(saved);
    CHECK(!refs[4] && !fds[4] && !rights[4]);
    CHECK(!calls && !masked && masks == restores);
}
int main(void)
{
    fork_checks();
    restore_checks();
    accepted();
    errno = 19;
    CHECK(open("/scratch/data", O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC,
               0600) == 3);
    CHECK(calls == 1 && !poisoned && live[3] && startup_users[3] == 1);
    CHECK(startup_fds[3].binding == 3 && startup_fds[3].flags == FD_CLOEXEC);
    CHECK(rights[3] == 2 && refs[3] == 0xfc010711 && fds[3] == 3);
    CHECK(!masked && masks == restores && errno == 19);
    accepted();
    CHECK(open64("/scratch/data", O_RDONLY) == 3);
    CHECK(rights[3] == 1);
    accepted();
    CHECK(open("/scratch/data", O_RDWR) == -1 && errno == ENOTSUP && !calls);
    accepted();
    for (unsigned i = 3; i < 16; ++i)
        startup_fds[i].present = 1;
    CHECK(open("/scratch/data", O_WRONLY | O_CREAT | O_TRUNC) == -1 &&
          errno == EMFILE && !calls);
    accepted();
    live[3] = live[4] = 1;
    CHECK(open("/scratch/data", O_RDONLY) == -1 && errno == ENFILE && !calls);
    accepted();
    response = 1;
    CHECK(open("/scratch/data", O_RDONLY) == -1 && errno == ENOENT &&
          !poisoned && !live[3]);
    for (int mode = 2; mode <= 5; ++mode) {
        accepted();
        response = mode;
        if (mode == 4) {
            live[3] = 1;
            startup_users[3] = 2;
            refs[3] = 123;
        }
        CHECK(open("/scratch/data", O_RDONLY) == -1 && errno == EIO &&
              poisoned);
        if (mode == 4)
            CHECK(refs[3] == 123 && startup_users[3] == 2);
        CHECK(calls == 1 && !startup_fds[3].present);
        CHECK(open("/scratch/data", O_RDONLY) == -1 && calls == 1);
        CHECK(!masked && masks == restores);
    }
    reset();
    grant[31] = 1;
    CHECK(!scratch_accept() && poisoned && !scratch_root);
    reset();
    put(grant, 12, 8);
    CHECK(!scratch_accept() && poisoned);
    reset();
    CHECK(open("/scratch/data", O_RDONLY) == -1 && errno == EACCES && !calls);
    puts("scratch adapter checks passed");
    return 0;
}
