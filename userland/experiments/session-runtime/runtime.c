/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded AENMX008/ABI23 runtime extracted from the pinned SESSION client. */
#define PIPELINE_STREAMS
#define SHELL_STARTUP
#define STARTUP_IDENTITY
#define STARTUP_CWD
#define STARTUP_PUBLIC_ACTION
#ifdef SESSION_FS_ABI29
#if !defined(SESSION_CHANNEL_WAIT) || !defined(SESSION_SERIAL)
#error "ABI29 candidate requires explicit serial channel waiting"
#endif
#include "fs-identity.h"
#endif
static unsigned startup_ids[4], startup_directory;
static int pipeline_bootstrap(void);
static void pipeline_install(void);
#ifdef SESSION_CHANNEL_WAIT
#ifndef SESSION_SERIAL
#error "channel wait requires the explicit ABI24 serial session profile"
#endif
#include "wait-transport.h"
#else
#include "vendor/user/native-command/transport.h"
#endif
#include "session.h"
#include <stdlib.h>
#include <sys/wait.h>

#ifdef SESSION_SCRATCH
#include "vendor/user/native-capacity/session-scratch-client.h"
#endif
static unsigned role, epoch, shell_generation;
/* Required native TLS segment; checked after launch, copy and exec rebinding.
 */
static _Thread_local volatile unsigned session_tls = 0x73657373;
static unsigned char installed[64];
_Noreturn void __real__exit(int);

static int identity(void)
{
#ifdef SESSION_FS_ABI29
    unsigned char frame[32];
    struct aether_fs_session_identity observed;
    if (!move(frame, sizeof frame, 0) ||
        !aether_fs_session_decode(frame, sizeof frame, getauxval(0xa000),
                                  getpid(), getppid(), &observed))
        return 0;
    role = observed.slot;
    epoch = observed.epoch;
    shell_generation = observed.shell_generation;
    return 1;
#else
    unsigned char frame[16];
    if (!move(frame, sizeof frame, 0))
        return 0;
    role = get(frame, 0);
    epoch = get(frame, 4);
    shell_generation = get(frame, 12);
    unsigned long memory = getauxval(0xa000);
    if ((role != 0 && (role < 2 || role > 4)) || epoch < 1 || epoch > 15 ||
        shell_generation < 1 || shell_generation > 3 ||
        memory != (0x40000000UL | ((unsigned long)epoch << 8) | (role + 1)) ||
        (unsigned)getpid() != epoch * 6 + role + 1 ||
        (role && ((unsigned)getppid() != get(frame, 8) ||
                  get(frame, 8) != shell_generation * 6 + 1)))
        return 0;
    return 1;
#endif
}

static int ready(void)
{
    if (session_tls != 0x73657373)
        return 0;
    if (memtrap(0x2000a, 0xa001, 0, 176, 1) != -EACCES)
        return 0;
    if (memtrap(0x26000, 0xf001, 0, 0, 0) !=
#ifdef SESSION_SERIAL
        -EACCES
#else
        -ENOSYS
#endif
    )
        return 0;
#ifdef SESSION_SERIAL
    if (memtrap(0x26002, 0xf001, 0, 0, 0) != -EACCES)
        return 0;
#endif
    uint64_t report[2] = {(uint64_t)getpid(), (uint64_t)role + 1};
    return move((unsigned char *)report, sizeof report, 1) &&
           !memtrap(0x20004, 0, 0, 0, 0);
}

static int pipeline_bootstrap(void)
{
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    if (!input || !output || input == output || !identity() ||
        !move(installed, sizeof installed, 0))
        return 0;
    for (unsigned binding = 0; binding < BINDINGS; ++binding) {
        unsigned char frame[16];
        if (!move(frame, sizeof frame, 0))
            return 0;
        refs[binding] = get(frame, 0);
        fds[binding] = get(frame, 4);
        rights[binding] = get(frame, 8);
        unsigned bound = get(frame, 12);
        if (!refs[binding]) {
            if (fds[binding] || rights[binding] || bound)
                return 0;
        } else if (fds[binding] != binding ||
                   (binding < 7
                        ? rights[binding] !=
                              (binding == 0 || binding == 3 || binding == 5
                                   ? 1U
                                   : 2U)
                        : (rights[binding] != 1 && rights[binding] != 2)) ||
                   bound != 16) {
            return 0;
        }
    }
#ifdef SESSION_SCRATCH
    unsigned char root[16];
    if (!move(root, sizeof root, 0) ||
        get(root, 0) != (0x77000000U | shell_generation) || get(root, 4) ||
        get(root, 8) || get(root, 12))
        return 0;
    scratch_root = get(root, 0);
    for (unsigned binding = 7; binding < BINDINGS; ++binding) {
        if (!refs[binding])
            continue;
        unsigned sequence = (refs[binding] >> 8) & 255;
        if (sequence < 1 || sequence > 15 ||
            refs[binding] != (0x78000000U | (shell_generation << 16) |
                              (sequence << 8) | (binding - 6)))
            return 0;
    }
#endif
    for (unsigned i = 0; i < 4; ++i)
        startup_ids[i] = 1000;
    startup_directory = 0x76030000U + shell_generation;
    return 1;
}

static void pipeline_install(void)
{
    for (unsigned fd = 0; fd < 16; ++fd) {
        unsigned char *record = installed + fd * 4;
        if (!record[2]) {
            if (record[0] || record[1] || record[3])
                __real__exit(140);
            continue;
        }
        if (record[0] >= BINDINGS || record[1] || record[2] != 1 || record[3] ||
            !refs[record[0]])
            __real__exit(140);
        unsigned binding = record[0];
        startup_fds[fd] = (struct startup_fd){binding, 0, 1};
        ++startup_users[binding];
        live[binding] = 1;
    }
}

_Noreturn void __wrap__exit(int status)
{
    if (startup_ready && !poisoned)
        for (int fd = 0; fd < 16; ++fd)
            if (startup_fds[fd].present && close(fd))
                __real__exit(141);
    __real__exit(status);
}

#ifndef SESSION_HELPER
static int live_snapshot(void)
{
    unsigned char table[64] = {0};
    for (unsigned fd = 0; fd < 16; ++fd) {
        struct startup_fd value = startup_fds[fd];
        if (value.present) {
            table[fd * 4] = (unsigned char)value.binding;
            table[fd * 4 + 1] = (unsigned char)value.flags;
            table[fd * 4 + 2] = 1;
        }
    }
    return move(table, sizeof table, 1);
}
static void dash_copy_ready(void)
{
    if (!identity() ||
#ifdef SESSION_FS_ABI29
        role == 1 ||
#else
        !role ||
#endif
        !ready())
        __real__exit(142);
}
#define PIPE_DASH_PARENT
#define PIPE_LIVE_FDS
#define PIPE_INTERLEAVE
#if defined(SESSION_STALE_WAIT)
static unsigned forks;
static int first_collected;
long __aether_waitpid(int, int *, int);
#define __aether_fork_stage session_fork_stage
#endif
#include "vendor/user/native-capacity/fork-stage.h"
#ifdef SESSION_STALE_WAIT
#undef __aether_fork_stage
long __aether_fork_stage(void)
{
    long pid = session_fork_stage();
    if (pid > 0 && ++forks ==
#ifdef SESSION_FAILED_EXEC
                       2
#elif defined(SESSION_RECOVERY)
                       3
#else
                       4
#endif
    ) {
        int status = 0x12345678;
        if (!first_collected ||
            __aether_waitpid(first_collected, &status, WNOHANG) != -ECHILD ||
            status != 0x12345678)
            __wrap__exit(144);
    }
    return pid;
}
#endif

int pipe(int pair[2])
{
    if (!pair)
        return startup_error(EFAULT);
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return startup_error(EIO);
    int slots[2] = {-1, -1}, count = 0, error = 0;
    for (int fd = 0; fd < 16 && count < 2; ++fd)
        if (!startup_fds[fd].present)
            slots[count++] = fd;
    if (
#ifdef SESSION_FS_ABI29
        role != 1 ||
#else
        role ||
#endif
        !startup_ready || poisoned)
        error = EIO;
    else if (count != 2)
        error = EMFILE;
    else {
        unsigned char frame[32] = {0};
        put(frame, 0, 82);
        put(frame, 4, 0x76050001);
        put(frame, 8, 1);
        if (!exchange(frame, sizeof frame))
            error = EIO;
        else if (get(frame, 0))
            error = (int)get(frame, 0) == -ENFILE ? ENFILE : EIO;
        else {
            unsigned first = get(frame, 16), generation = get(frame, 4);
            unsigned object = first == 3 ? 0 : 1;
            if ((first != 3 && first != 5) || generation < 1 ||
                generation > 9 || get(frame, 20) != first + 1 ||
                get(frame, 24) != 256 || get(frame, 28) != 16 || live[first] ||
                live[first + 1] ||
                get(frame, 8) !=
                    (0x79000001U | object << 16 | generation << 8) ||
                get(frame, 12) !=
                    (0x79000002U | object << 16 | generation << 8))
                error = EIO;
            else
                for (unsigned end = 0; end < 2; ++end) {
                    unsigned binding = first + end;
                    refs[binding] = get(frame, 8 + end * 4);
                    fds[binding] = binding;
                    rights[binding] = end ? 2 : 1;
                    live[binding] = 1;
                    startup_users[binding] = 1;
                    startup_fds[slots[end]] =
                        (struct startup_fd){binding, 0, 1};
                    pair[end] = slots[end];
                }
        }
    }
#ifdef RECOVERY_RETAINED_READER
    if (!error && startup_fds[pair[0]].binding == 3 && refs[3] == 0x79000101U &&
        fcntl(pair[0], F_DUPFD_CLOEXEC, 10) != 10)
        error = EIO;
#endif
#ifdef SESSION_RETAINED_WRITER
    if (!error && startup_fds[pair[0]].binding == 3 && refs[3] == 0x79000101U &&
        fcntl(pair[1], F_DUPFD_CLOEXEC, 10) != 10)
        error = EIO;
#endif
    if (error == EIO)
        poisoned = 1;
    startup_mask_leave(previous);
    return error ? startup_error(error) : 0;
}

long __aether_waitpid(int pid, int *status, int options)
{
    if (
#ifdef SESSION_FS_ABI29
        role != 1 ||
#else
        role ||
#endif
        !status || (pid != -1 && pid <= 0) ||
        (options != 0 && options != WNOHANG))
        return -EINVAL;
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return -EIO;
    unsigned char frame[32] = {0};
    put(frame, 0, 68);
    put(frame, 4, (unsigned)pid);
    put(frame, 8, (unsigned)options);
    long result = -EIO;
    if (exchange(frame, sizeof frame)) {
        result = (int32_t)get(frame, 0);
#ifdef SESSION_FS_ABI29
        if ((result > 0 && (!aether_fs_session_child_pid(result) ||
                            (pid != -1 && result != pid))) ||
#else
        unsigned slot = result > 0 ? ((unsigned)result - 1) % 6 : 0;
        unsigned generation = result > 0 ? ((unsigned)result - 1) / 6 : 0;
        if ((result > 0 && (slot < 2 || slot > 4 || generation < 1 ||
                            generation > 15 || (pid != -1 && result != pid))) ||
#endif
            (result == 0 && options != WNOHANG) ||
            (result < 0 && result != -ECHILD) || (result <= 0 && get(frame, 4)))
            result = -EIO;
        for (unsigned i = 8; i < 32; ++i)
            if (frame[i])
                result = -EIO;
        if (result > 0)
            *status = (int)get(frame, 4);
    }
    if (result == -EIO)
        poisoned = 1;
    startup_mask_leave(previous);
#ifdef SESSION_STALE_WAIT
    if (result > 0 &&
#ifdef SESSION_FAILED_EXEC
        forks == 1 && !first_collected
#elif defined(SESSION_RECOVERY)
        forks == 2 && !first_collected
#else
        forks == 1
#endif
    )
        first_collected = (int)result;
#endif
    return result;
}

int execve(const char *path, char *const argv[], char *const envp[])
{
    if (!path || !argv || !envp ||
#ifdef SESSION_FS_ABI29
        role == 1
#else
        !role
#endif
    )
        return startup_error(EINVAL);
#ifndef SESSION_FAILED_EXEC
    if (!aether_session_exec_allowed(path))
        return startup_error(EACCES);
#endif
#ifdef SESSION_FD_LEAK
    if (argv[0] && argv[1] && !strcmp(argv[1], "closed") &&
        fcntl(1, F_DUPFD, 3) != 3)
        __wrap__exit(145);
#endif
#ifdef EXEC_SKIP_REQUEST
    if (!strcmp(path, "/inputs/missing"))
        return startup_error(ENOENT);
#endif
    unsigned char vector[272] = {0}, frame[32] = {0};
    for (unsigned which = 0; which < 2; ++which) {
        char *const *values = which ? envp : argv;
        unsigned count = 0;
        while (count < 4 && values[count]) {
            size_t length = strnlen(values[count], 32);
            if (length == 32)
                return startup_error(E2BIG);
            memcpy(vector + 16 + (which * 4 + count) * 32, values[count],
                   length);
            ++count;
        }
        if (values[count] || (!which && !count))
            return startup_error(E2BIG);
        put(vector, which * 8, count);
    }
#ifdef SESSION_FAILED_EXEC
    unsigned char target[32] = {0};
    size_t path_length = strnlen(path, sizeof target);
    if (!path_length || path_length == sizeof target)
        return startup_error(EINVAL);
    memcpy(target, path, path_length);
    put(frame, 0, 85);
    put(frame, 4, sizeof target);
#else
    put(frame, 0, 84);
    put(frame, 4, 0xc002);
#endif
    put(frame, 8, sizeof vector);
    if (!move(frame, sizeof frame, 1) ||
#ifdef SESSION_FAILED_EXEC
        !move(target, sizeof target, 1) ||
#endif
        !move(vector, sizeof vector, 1) || !move(frame, sizeof frame, 0))
        return startup_error(EIO);
    int result = (int32_t)get(frame, 0);
    for (unsigned i = 4; i < 32; ++i)
        if (frame[i])
            return startup_error(EIO);
    if (result)
        return startup_error(result == -EACCES ? EACCES :
#ifdef SESSION_FAILED_EXEC
                             result == -ENOENT ? ENOENT
                                               :
#endif
                                               EINVAL);
    if (!live_snapshot())
        return startup_error(EIO);
    memtrap(0x23003, 0, 0, 0, 0);
    return startup_error(EIO);
}
#endif

static int session_started;

int aether_session_start(unsigned *caller_role)
{
    if (!caller_role || session_started)
        return -1;
    session_started = 1;
    if (!startup_begin() || !ready())
        return -1;
    *caller_role = role;
    return 0;
}
