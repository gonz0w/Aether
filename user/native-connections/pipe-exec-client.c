/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded replacement writer; no pipe factory or executable authority. */
#define CAT_ROLES
#define SHELL_STARTUP
#define FORK_PIPE
#include "../native-command/transport.h"

static _Thread_local volatile unsigned cookie = 79;
#ifdef PIPE_EXEC_CONSUMER
int consumer_helper_main(int, char **);
#endif

int main(int argc, char **argv)
{
    unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
    if (cookie != 79 ||
#ifdef PIPE_EXEC_CONSUMER
        argc != 4 || strcmp(argv[0], "/inputs/helper") ||
#else
        argc != 1 || strcmp(argv[0], "/next") ||
#endif
        gen < 1 || gen > 2 || !startup_begin())
        return 227;
    unsigned char table[64] = {0}, grant[32] = {0}, mask[32] = {0};
    if (!move(table, sizeof table, 0) || !move(grant, sizeof grant, 0) ||
        !move(mask, sizeof mask, 0))
        return 227;
    unsigned char expected[64] = {0};
    expected[2] = 1;
    expected[4] = 4;
    expected[6] = 1;
    expected[8] = 2;
    expected[10] = 1;
    unsigned char expected_grant[32] = {0};
    memcpy(expected_grant, "AEPEX001", 8);
    put(expected_grant, 8, gen);
    unsigned pipe_gen = 1;
#ifdef PIPE_EXEC_SERIAL
    pipe_gen = gen;
#endif
    put(expected_grant, 12, pipe_gen);
    put(expected_grant, 16, 0x78000001 + (pipe_gen << 8));
    put(expected_grant, 20, 0x78000002 + (pipe_gen << 8));
    unsigned char expected_mask[32] = {0};
    memcpy(expected_mask, "AEEMSK01", 8);
    uint64_t current = 0;
    if (memcmp(table, expected, sizeof table) ||
        memcmp(grant, expected_grant, sizeof grant) ||
        memcmp(mask, expected_mask, sizeof mask) ||
        memtrap(0x1000e, 0, 0, (uintptr_t)&current, 8) ||
        current != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
        return 227;
    memset(startup_fds, 0, sizeof startup_fds);
    memset(startup_users, 0, sizeof startup_users);
    memset(live, 0, sizeof live);
    for (unsigned j = 0; j < 3; j++)
        refs[j] = 0x77000000u + (j << 16) + gen;
    for (unsigned j = 3; j < 5; j++) {
        refs[j] = get(grant, 16 + (j - 3) * 4);
        fds[j] = j;
        rights[j] = j == 3 ? 1 : 2;
    }
    for (unsigned fd = 0; fd < 16; fd++) {
        if (!table[fd * 4 + 2])
            continue;
        unsigned binding = table[fd * 4];
        startup_fds[fd] = (struct startup_fd){binding, 0, 1};
        startup_users[binding]++;
        live[binding] = 1;
    }
    startup_mask_leave(0);
    errno = 0;
    if (fcntl(10, F_GETFD) != -1 || errno != EBADF)
        return 227;
    errno = 0;
    if (fcntl(11, F_GETFD) != -1 || errno != EBADF || fcntl(1, F_GETFD) != 0)
        return 227;
#ifdef PIPE_EXEC_CONSUMER
    int result = 0;
#ifndef PIPE_EXEC_SKIP_HELPER
    result = consumer_helper_main(argc, argv);
#endif
#else
    int result = write(1, "pipe\n", 5) == 5 ? 0 : 227;
#endif
    if (close(0) || close(1) || close(2))
        return 227;
    return result;
}
