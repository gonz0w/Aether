/* SPDX-License-Identifier: BSD-2-Clause */
/* Live shared-facade snapshots; fixed pipe grants and scheduling remain
 * private. */
#define PIPELINE_STREAMS
#define SHELL_STARTUP
#define PIPE_LIVE_FDS
#ifdef PIPE_DASH_MAIN
#define STARTUP_IDENTITY
#define STARTUP_CWD
#define STARTUP_PUBLIC_ACTION
static unsigned startup_ids[4], startup_directory;
#endif
static int pipeline_bootstrap(void);
static void pipeline_install(void);
#include "../native-command/transport.h"
static unsigned generation;
#ifdef PIPE_STDIO
#include "standard-streams.h"
#endif
#ifdef PIPE_INHERITED_OUTPUT
static unsigned stdout_reference;
#endif
static _Thread_local volatile unsigned cookie = 53;
#ifdef PIPE_PARENT_OPS
#include "parent-ops.h"
#ifdef PIPE_WAIT_ANY
#include <sys/resource.h>
#endif
#endif

static int pipeline_bootstrap(void)
{
#ifdef PIPE_PARENT_OPS
    unsigned char grant[8];
    if (!move(grant, sizeof grant, 0) || get(grant, 0) != 0x76050001U ||
        get(grant, 4) != 2)
        return 0;
    factory = get(grant, 0);
#ifdef PIPE_INHERITED_OUTPUT
    unsigned char description[16];
    if (!move(description, sizeof description, 0) ||
        get(description, 0) != (0x7a010000U | generation) ||
        get(description, 4) != 1 || get(description, 8) != 2 ||
        get(description, 12) != 32)
        return 0;
    stdout_reference = get(description, 0);
#ifdef PIPE_STDIO
    if (!standard_description(0) || !standard_description(2))
        return 0;
#endif
#endif
#endif
    return input && output && input != output &&
           !memtrap(0x24001, input, 0, 0, 0) &&
           !memtrap(0x24002, output, 0, 0, 0);
}
static void pipeline_install(void)
{
#ifdef PIPE_INHERITED_OUTPUT
    refs[1] = stdout_reference;
    fds[1] = 1;
    rights[1] = 2;
    live[1] = 1;
    startup_users[1] = 1;
    startup_fds[1] = (struct startup_fd){1, 0, 1};
#ifdef PIPE_STDIO
    for (unsigned binding = 0; binding <= 2; binding += 2) {
        live[binding] = 1;
        startup_users[binding] = 1;
        startup_fds[binding] = (struct startup_fd){binding, 0, 1};
    }
#endif
#endif
#ifdef PIPE_PARENT_OPS
    return; /* pipe() publishes only after its complete validated create reply.
             */
#endif
    for (unsigned binding = 3; binding < 7; ++binding) {
        unsigned object = (binding - 3) / 2, end = (binding - 3) % 2 + 1;
        refs[binding] = 0x79000000U | (object << 16) | (generation << 8) | end;
        fds[binding] = binding;
        rights[binding] = end == 1 ? 1 : 2;
        live[binding] = 1;
        startup_users[binding] = 1;
        startup_fds[binding] = (struct startup_fd){binding, 0, 1};
    }
}
static int live_snapshot(void)
{
    unsigned char table[64] = {0};
    for (unsigned fd = 0; fd < 16; ++fd) {
        struct startup_fd value = startup_fds[fd];
        if (!value.present)
            continue;
        table[fd * 4] = (unsigned char)value.binding;
        table[fd * 4 + 1] = (unsigned char)value.flags;
        table[fd * 4 + 2] = (unsigned char)value.present;
    }
#ifdef PIPE_LIVE_BAD_SNAPSHOT
    table[24] = 4; /* Claim a second First writer while losing Second writer. */
#endif
    return move(table, sizeof table, 1);
}
#ifdef PIPE_DASH_PARENT
static void dash_copy_ready(void);
#endif
#include "fork-stage.h"
#ifdef PIPE_EXEC_REQUEST
#include "exec-request.h"
#endif

static int report(unsigned slot)
{
    uint64_t words[2] = {(uint64_t)getpid(), slot + 1};
    return move((unsigned char *)words, sizeof words, 1) &&
           !memtrap(0x20004, 0, 0, 0, 0);
}
#ifdef PIPE_DASH_PARENT
#include "dash-parent.h"
#endif
#ifdef PIPE_COPIED_BUILTIN
#if defined(PIPE_DASH_MAIN) && !defined(PIPE_DASH_PARENT)
extern int __real_main(int, char **);
extern char **environ;
_Noreturn void __real__exit(int);
_Noreturn void __wrap__exit(int status)
{
    if (cookie == 71 && startup_ready && !poisoned)
        for (int fd = 0; fd < 16; ++fd)
            if (startup_fds[fd].present && close(fd))
                __real__exit(132);
    __real__exit(status);
}
#endif
/* Direct pinned dash builtin entry; no shell main/init or image replacement. */
extern int printfcmd(int, char **);
extern void flushall(void);
extern char **argptr;
extern char *optptr;
static int copied_builtin(void)
{
    unsigned char byte, data[16];
#ifdef PIPE_DASH_MAIN
    unsigned char startup[64] = {0};
    if (!move(startup, sizeof startup, 0) || get(startup, 16) != 1 ||
        get(startup, 32) != 0x76030000U + generation ||
        get(startup, 36) != 1 || get(startup, 40) != 1 ||
        get(startup, 44) != generation)
        return 132;
    for (unsigned i = 20; i < 64; ++i)
        if ((i < 32 || i >= 48) && startup[i])
            return 132;
    const unsigned aux[] = {AT_UID, AT_EUID, AT_GID, AT_EGID};
    for (unsigned i = 0; i < 4; ++i)
        if (get(startup, i * 4) != 1000 || getauxval(aux[i]) != 1000)
            return 132;
    for (unsigned i = 0; i < 4; ++i)
        startup_ids[i] = get(startup, i * 4);
    startup_directory = get(startup, 32);
#endif
#ifndef PIPE_AUTONOMOUS
    unsigned char token;
    if (!move(&token, 1, 0) || token != 1)
        return 129;
#endif
    if (cookie != 71 || close(1) || close(3) || dup2(4, 1) != 1 || close(4))
        return 129;
    for (int fd = 3; fd < 16; ++fd)
        if (fcntl(fd, F_GETFD) != -1 || errno != EBADF)
            return 129;
    unsigned char forged[32] = {0};
    put(forged, 0, 2);
    put(forged, 4, 0x7a010000U | generation);
    put(forged, 8, 1);
    put(forged, 12, 1);
    forged[16] = 'X';
    if (!exchange(forged, sizeof forged) || (int32_t)get(forged, 0) != -EACCES)
        return 129;
    for (unsigned i = 4; i < 32; ++i)
        if (forged[i])
            return 129;
    char diagnostic = '2';
    if (read(2, &byte, 1) != -1 || errno != EACCES ||
        write(2, &diagnostic, 1) != 1 || close(2) || write(0, "X", 1) != -1 ||
        errno != EACCES || read(0, data, sizeof data) != 10 ||
        memcmp(data, "pipe data\n", 10) || read(0, &byte, 1) != 0 || close(0))
        return 129;
#ifdef PIPE_DASH_MAIN
    char cwd[16];
    unsigned directory = startup_directory;
    startup_directory = directory + 1;
    if (getcwd(cwd, sizeof cwd) || errno != EACCES)
        return 132;
    startup_directory = directory - 1;
    if (getcwd(cwd, sizeof cwd) || errno != EBADF)
        return 132;
    startup_directory = directory;
    if (getcwd(cwd, sizeof cwd) != cwd || strcmp(cwd, "/work") ||
        getuid() != 1000 || geteuid() != 1000 || getgid() != 1000 || getegid() != 1000)
        return 132;
    char *environment[] = {"PWD=/work", "LC_ALL=C", "PATH=/nonexistent", NULL};
    char *arguments[] = {"sh", "-c",
#ifdef PIPE_DASH_BAD_BYTE
                         "printf 'Pipe data\\n'",
#else
                         "printf 'pipe data\\n'",
#endif
                         NULL};
    environ = environment;
    __wrap__exit(__real_main(3, arguments));
#else
    char command[] = "printf";
#ifdef PIPE_DASH_BAD_BYTE
    char format[] = "Pipe data\n";
#else
    char format[] = "pipe data\n";
#endif
    char *arguments[] = {command, format, NULL};
    argptr = arguments + 1;
    optptr = NULL;
    if (printfcmd(2, arguments))
        return 128;
    flushall();
    return close(1) ? 129 : 0;
#endif
}
#endif
int main(int argc, char **argv)
{
    if (argc != 3 || cookie != 53)
        return 117;
    unsigned slot = (unsigned)(argv[1][0] - '0');
    generation = (unsigned)(argv[2][0] - '0');
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    if ((slot > 1
#ifdef PIPE_SHELL_EARLY
        && slot != 4
#endif
        ) || generation < 1 || generation > 3 ||
        (unsigned)getpid() != generation * 6 + slot + 1 || !report(slot))
        return 117;
#ifdef PIPE_SHELL_EARLY
    if (slot == 4) {
        unsigned char token = 0;
        return move(&token, 1, 0) && token == 1 ? 0 : 120;
    }
#endif
    if (slot == 0) {
        if (!startup_begin())
            return 117;
#ifdef PIPE_DASH_PARENT
        return dash_parent();
#endif
#if defined(PIPE_PARENT_OPS) && !defined(PIPE_INTERLEAVE)
        for (int object = 0; object < 2; ++object) {
            int pair[2];
            if (pipe(pair) || pair[0] != 0 || pair[1] != 1)
                return 121;
            for (int end = 0; end < 2; ++end) {
                int target = 3 + object * 2 + end;
                if (fcntl(pair[end], F_DUPFD, target) != target ||
                    close(pair[end]))
                    return 121;
            }
        }
        int exhausted[2] = {-1, -1};
        if (pipe(exhausted) != -1 || errno != ENFILE || exhausted[0] != -1 ||
            exhausted[1] != -1)
            return 121;
#endif
        for (unsigned child = 2; child <= 4; ++child) {
#ifdef PIPE_INTERLEAVE
            if (child == 3 && close(4))
                return 122;
#ifdef PIPE_NATURAL_FDS
            if (child == 4 && (close(3) || close(5)))
#else
            if (child == 4 && (close(3) || close(6)))
#endif
                return 122;
            if (child < 4) {
                int pair[2];
#ifndef PIPE_NATURAL_FDS
                int object = (int)child - 2;
#endif
#ifdef PIPE_STDIO
                if (pipe(pair) || pair[0] != (child == 2 ? 3 : 4) ||
                    pair[1] != (child == 2 ? 4 : 5))
                    return 126;
#ifndef PIPE_NATURAL_FDS
                for (int end = 0; end < 2; ++end)
                    if (fcntl(pair[end], F_DUPFD_CLOEXEC, 10 + end) != 10 + end)
                        return 126;
                if (close(pair[0]) || close(pair[1]))
                    return 126;
                for (int end = 0; end < 2; ++end) {
                    int target = 3 + object * 2 + end;
                    if (dup2(10 + end, target) != target || close(10 + end))
                        return 126;
                }
#endif
#else
                int second = 1;
#ifdef PIPE_INHERITED_OUTPUT
                second = 2;
#endif
                if (pipe(pair) || pair[0] != 0 || pair[1] != second)
                    return 122;
                for (int end = 0; end < 2; ++end) {
                    int target = 3 + object * 2 + end;
                    if (fcntl(pair[end], F_DUPFD, target) != target ||
                        close(pair[end]))
                        return 122;
                }
#endif
            }
#ifndef PIPE_NATURAL_FDS
            int source = child == 4 ? 5 : 3;
#endif
#else
            int source = 3;
#endif
#ifndef PIPE_NATURAL_FDS
            int alias = (int)child + 8;
            if (fcntl(source, F_DUPFD_CLOEXEC, alias) != alias)
                return 118;
#endif
            fork_input = input;
            fork_output = output;
            pid_t result = fork();
            if (gettid() != getpid() || cookie != 53
#ifndef PIPE_NATURAL_FDS
                || fcntl(alias, F_GETFD) != FD_CLOEXEC || close(alias) ||
                fcntl(alias, F_GETFD) != -1 || errno != EBADF
#endif
                )
                return 118;
            if (!result) {
                slot = child;
                cookie = 71;
                if ((unsigned)getpid() != generation * 6 + slot + 1 ||
                    (unsigned)getppid() != generation * 6 + 1 ||
                    input != getauxval(0xa001) || output != getauxval(0xa002) ||
                    !report(slot))
                    return 119;
                break;
            }
            if ((unsigned)result != generation * 6 + child + 1)
                return 119;
        }
    }
#if defined(PIPE_WAIT_ANY) && !defined(PIPE_WAIT_IO)
    if (slot == 0) {
        int status = 123;
        if (waitpid((int)generation * 6 + 2, &status, WNOHANG) != -1 ||
            errno != ECHILD || status != 123 ||
            wait3(&status, WNOHANG, NULL) != 0 || status != 123 ||
            waitpid((int)generation * 6 + 3, &status, WNOHANG) != 0 ||
            status != 123)
            return 123;
    }
#endif
#ifdef PIPE_COPIED_BUILTIN
    if (slot == 2)
        return copied_builtin();
#endif
    unsigned char token = 2;
#ifdef PIPE_EXEC_REQUEST
    if (slot < 2)
#endif
        if (!move(&token, 1, 0))
            return 120;
#ifdef PIPE_PARENT_OPS
    if (slot == 0) {
        if (token != 1)
            return 121;
#ifdef PIPE_INHERITED_OUTPUT
        if (close(1))
            return 125;
#ifdef PIPE_STDIO
        if (close(0) || close(2))
            return 126;
#endif
#endif
        for (int fd = 3; fd < 7; ++fd)
#ifdef PIPE_INTERLEAVE
            if (startup_fds[fd].present)
#endif
                if (close(fd))
                    return 121;
#ifdef PIPE_WAIT_NATURAL
        unsigned collected = 0;
        for (unsigned child = 0; child < 3; ++child) {
            int status = -1;
            int result = waitpid(-1, &status, 0);
            int slot = result - ((int)generation * 6 + 1);
            if (slot < 2 || slot > 4 || (collected & (1U << slot)) ||
                !WIFEXITED(status) || WEXITSTATUS(status))
                return 131;
            collected |= 1U << slot;
        }
        return collected == 0x1c ? 0 : 131;
#elif defined(PIPE_WAIT_PROBES)
        int probe_status = 123;
        if (waitpid((int)generation * 6 + 2, &probe_status, WNOHANG) != -1 ||
            errno != ECHILD || probe_status != 123 ||
            wait3(&probe_status, WNOHANG, NULL) != 0 || probe_status != 123 ||
            waitpid((int)generation * 6 + 3, &probe_status, WNOHANG) != 0 ||
            probe_status != 123)
            return 131;
        unsigned collected = 0;
        for (int child = 2; child <= 4; ++child) {
            int status = -1;
            int result = child == 2   ? wait3(&status, 0, NULL)
                         : child == 3 ? waitpid(-1, &status, 0)
                                      : wait4(-1, &status, 0, NULL);
            int slot = result - ((int)generation * 6 + 1);
            if (slot < 2 || slot > 4 || (collected & (1U << slot)) ||
#ifdef PIPE_OVERLAP_STOP
                (slot == 4 ? (!WIFSIGNALED(status) || WTERMSIG(status) != 15)
                           : (!WIFEXITED(status) || WEXITSTATUS(status))))
#else
                !WIFEXITED(status) || WEXITSTATUS(status))
#endif
                return 131;
            collected |= 1U << slot;
            if (child == 2) {
                status = 123;
                if (waitpid(result, &status, WNOHANG) != -1 ||
                    errno != ECHILD || status != 123)
                    return 131;
            }
        }
        if (collected != 0x1c)
            return 131;
#else
        for (int child = 2; child <= 4; ++child) {
            int status = -1, pid = (int)generation * 6 + child + 1;
#ifdef PIPE_WAIT_ANY
#ifdef PIPE_WAIT_IO
            int result = child == 4 ? wait4(pid, &status, 0, NULL)
                                    : waitpid(pid, &status, 0);
#else
            int result = child == 2   ? wait3(&status, WNOHANG, NULL)
                         : child == 3 ? waitpid(-1, &status, 0)
                                      : wait4(pid, &status, 0, NULL);
#endif
#else
            int result = waitpid(pid, &status, 0);
#endif
            if (result != pid || !WIFEXITED(status) || WEXITSTATUS(status))
                return 121;
        }
#endif
        int status = 123;
#ifdef PIPE_WAIT_ANY
        struct rusage usage;
        memset(&usage, 0x53, sizeof usage);
        if (wait4(-1, &status, WNOHANG, &usage) != -1 || errno != ENOTSUP ||
            status != 123)
            return 123;
        const unsigned char *bytes = (const unsigned char *)&usage;
        for (unsigned i = 0; i < sizeof usage; ++i)
            if (bytes[i] != 0x53)
                return 123;
        int exhausted = wait3(&status, WNOHANG, NULL);
#else
        int exhausted = waitpid((int)generation * 6 + 3, &status, 0);
#endif
        if (exhausted != -1 || errno != ECHILD || status != 123)
            return 121;
    }
#endif
    if (slot < 2)
        return token == 1 && cookie == 53 ? 0 : 120;
    if (token != 2)
        return 120;
#ifdef PIPE_PREEXEC_IO
    if (close(0))
        return 133;
#endif
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return 120;
#ifdef PIPE_INHERITED_OUTPUT
    if (fcntl(1, F_SETFD, slot == 4 ? 0 : FD_CLOEXEC))
        return 125;
#ifdef PIPE_STDIO
    if (
#ifndef PIPE_PREEXEC_IO
        fcntl(0, F_SETFD, slot == 2 ? 0 : FD_CLOEXEC) ||
#endif
        fcntl(2, F_SETFD, 0))
        return 126;
#endif
#endif
#ifndef PIPE_NATURAL_FDS
    for (int fd = 3; fd < 7; ++fd) {
#ifdef PIPE_INTERLEAVE
        if (!startup_fds[fd].present)
            continue;
#endif
        int keep = (slot == 2 && fd == 4) ||
                   (slot == 3 && (fd == 3 || fd == 6)) ||
                   (slot == 4 && fd == 5);
        if (fcntl(fd, F_SETFD, keep ? 0 : FD_CLOEXEC))
            return 120;
    }
#endif
#ifdef PIPE_PREEXEC_REMAP
#ifdef PIPE_NATURAL_FDS
    /* Local fd4 is the second reader, although its stable binding is5. */
    int reader = slot == 3 ? 3 : 4;
    if (dup2(reader, 0) != 0 || (slot == 3 && dup2(5, 1) != 1))
        return 134;
    for (int fd = 3; fd < 16; ++fd)
        if (startup_fds[fd].present && close(fd))
            return 134;
#ifdef PIPE_NATURAL_ALIAS
    if (fcntl(0, F_DUPFD, 10) != 10)
        return 134;
#endif
#else
    int reader = slot == 3 ? 3 : 5;
    if (dup2(reader, 0) != 0 || fcntl(reader, F_SETFD, FD_CLOEXEC) ||
        (slot == 3 && (dup2(6, 1) != 1 || fcntl(6, F_SETFD, FD_CLOEXEC))) ||
        fcntl(0,
#ifdef PIPE_REMAP_ALIAS
              F_DUPFD,
#else
              F_DUPFD_CLOEXEC,
#endif
              10) != 10)
        return 134;
#ifdef PIPE_REMAP_CLOEXEC
    if (fcntl(0, F_SETFD, FD_CLOEXEC))
        return 134;
#endif
#endif
#endif
#ifdef PIPE_EXEC_REQUEST
    execution_role = slot;
#ifdef PIPE_HELPER_ARGS
    char *arguments[] = {"/inputs/helper", "copy", NULL};
#else
    char role_text[] = {(char)('0' + slot), 0};
    char generation_text[] = {(char)('0' + generation), 0};
    char *arguments[] = {"replacement", role_text, generation_text, NULL};
#endif
    char *environment[] = {NULL};
#ifdef PIPE_HELPER_ARGS
    char *wrong_name[] = {"replacement", "copy", NULL};
    char *wrong_argument[] = {"/inputs/helper", "other", NULL};
    char *extra_argument[] = {"/inputs/helper", "copy", "extra", NULL};
    char *nonempty_environment[] = {"WITNESS=value", NULL};
    if (execve("/unknown", arguments, environment) != -1 || errno != ENOENT ||
        execve("/inputs/helper", wrong_name, environment) != -1 || errno != EINVAL ||
        execve("/inputs/helper", wrong_argument, environment) != -1 || errno != EINVAL ||
        execve("/inputs/helper", extra_argument, environment) != -1 || errno != EINVAL ||
        execve("/inputs/helper", arguments, nonempty_environment) != -1 || errno != EINVAL)
        return 127;
#endif
    int flags[16];
    for (int fd = 0; fd < 16; ++fd)
        flags[fd] = fcntl(fd, F_GETFD);
    if (execve("/denied", arguments, environment) != -1 || errno != EACCES)
        return 127;
    for (int fd = 0; fd < 16; ++fd)
        if (fcntl(fd, F_GETFD) != flags[fd])
            return 127;
    execve(
#ifdef PIPE_HELPER_ARGS
        "/inputs/helper",
#else
        "/replacement",
#endif
        arguments, environment);
    return 127;
#else
    if (!live_snapshot())
        return 120;
    memtrap(0x23003, 0, 0, 0, 0);
#endif
    return 120; /* Replacement must not return to the old image. */
}
