/* SPDX-License-Identifier: BSD-2-Clause */
/* Private replacement consuming the shared descriptor facade and musl I/O. */
#define PIPELINE_STREAMS
#define SHELL_STARTUP
#ifdef PIPE_SHELL_EARLY
#define STARTUP_PUBLIC_ACTION
#define CAPTURE_ROLE 3
#else
#define CAPTURE_ROLE 4
#endif
static int pipeline_bootstrap(void);
static void pipeline_install(void);
#include "../native-command/transport.h"
#ifdef PIPE_DASH_PARENT
#include <stdlib.h>
#endif

static _Thread_local volatile unsigned cookie = 83;
static unsigned role, generation;
#ifdef PIPE_DASH_PRINTF
/* Signatures and argument cursor from the pinned dash builtin interface. */
extern int printfcmd(int, char **);
extern void flushall(void);
extern char **argptr;
extern char *optptr;
#endif
#ifdef PIPE_STDIO
#include "standard-streams.h"
#endif
static unsigned char installed[64];
#ifdef PIPE_STDOUT
static unsigned stdout_reference;
#endif

static int pipeline_bootstrap(void)
{
    input = getauxval(0xa001);
    output = getauxval(0xa002);
    unsigned char expected[64] = {0};
    if (!input || !output || input == output || !move(installed, 64, 0))
        return 0;
    for (unsigned binding = 3; binding < 7; ++binding) {
        int keep = (role == 2 && binding == 4) ||
                   (role == 3 && (binding == 3 || binding == 6)) ||
                   (role == CAPTURE_ROLE && binding == 5);
        if (keep) {
            expected[binding * 4] = (unsigned char)binding;
            expected[binding * 4 + 2] = 1;
        }
    }
#ifdef PIPE_INHERITED_OUTPUT
    if (role == CAPTURE_ROLE) {
        expected[4] = 1;
        expected[6] = 1;
    }
#endif
#ifdef PIPE_STDIO
    if (role == 2)
        expected[2] = 1;
    expected[8] = 2;
    expected[10] = 1;
#endif
#ifdef PIPE_PREEXEC_REMAP
    memset(expected, 0, sizeof expected);
#ifdef PIPE_SHELL_EARLY
    expected[0] = role == 2 ? 0 : 3;
#else
    expected[0] = role == 3 ? 3 : 5;
#endif
    expected[2] = 1;
#ifdef PIPE_SHELL_EARLY
    expected[4] = role == 2 ? 4 : 1;
#else
    expected[4] = role == 3 ? 6 : 1;
#endif
    expected[6] = 1;
    expected[8] = 2;
    expected[10] = 1;
#endif
    if (memcmp(installed, expected, sizeof installed))
        return 0;
#ifdef PIPE_STDOUT
    if (role == CAPTURE_ROLE) {
        unsigned char grant[16];
        if (!move(grant, sizeof grant, 0) ||
            get(grant, 0) != (0x7a010000U | generation) || get(grant, 4) != 1 ||
            get(grant, 8) != 2 || get(grant, 12) != 32)
            return 0;
        stdout_reference = get(grant, 0);
    }
#endif
#ifdef PIPE_STDIO
    if ((role == 2 && !standard_description(0)) || !standard_description(2))
        return 0;
#endif
    return 1;
}

static void pipeline_install(void)
{
#ifdef PIPE_STDOUT
    if (role == CAPTURE_ROLE) {
        refs[1] = stdout_reference;
        fds[1] = 1;
        rights[1] = 2;
        live[1] = 1;
#ifndef PIPE_INHERITED_OUTPUT
        startup_fds[1] = (struct startup_fd){1, 0, 1};
        startup_users[1] = 1;
#endif
    }
#endif
    for (unsigned binding = 3; binding < 7; ++binding) {
        unsigned object = (binding - 3) / 2, end = (binding - 3) % 2 + 1;
        refs[binding] = 0x79000000U | (object << 16) | (generation << 8) | end;
        fds[binding] = binding;
        rights[binding] = end == 1 ? 1 : 2;
    }
    for (unsigned fd = 0; fd < 16; ++fd) {
        if (!installed[fd * 4 + 2])
            continue;
        unsigned binding = installed[fd * 4];
        startup_fds[fd] = (struct startup_fd){binding, 0, 1};
        ++startup_users[binding];
        live[binding] = 1;
    }
}

int main(int argc, char **argv)
{
#ifdef PIPE_HELPER_ARGS
    if (argc != 2 || strcmp(argv[0], "/inputs/helper") ||
        strcmp(argv[1],
#ifdef PIPE_SHELL_EARLY
               (getauxval(0xa000) & 255) == 3 ? "pump" : "one"
#else
               "copy"
#endif
        ) || cookie != 83)
        return 105;
#ifdef PIPE_DASH_PARENT
    if (!getenv("WITNESS") || strcmp(getenv("WITNESS"), "value") ||
        !getenv("PWD") || strcmp(getenv("PWD"), "/work") ||
        !getenv("LC_ALL") || strcmp(getenv("LC_ALL"), "C") ||
        !getenv("PATH") || strcmp(getenv("PATH"), "/nonexistent"))
        return 137;
#endif
    unsigned parent = (unsigned)getppid();
    generation = (parent - 1) / 6;
    unsigned long memory = getauxval(0xa000);
    role = (unsigned)(memory & 255) - 1;
    unsigned epoch = (unsigned)((memory >> 8) & 255);
    if (!epoch || epoch > 15 ||
        memory != (0x40000000UL | ((unsigned long)epoch << 8) | (role + 1)) ||
        (unsigned)getpid() != epoch * 6 + role + 1)
        return 105;
#else
    if (argc != 3 || strcmp(argv[0], "replacement") || cookie != 83)
        return 105;
    role = (unsigned)(argv[1][0] - '0');
    generation = (unsigned)(argv[2][0] - '0');
#endif
    if (role < 2 || role > 4 || generation < 1 || generation > 3 ||
        (unsigned)getpid() != generation * 6 + role + 1 ||
        (unsigned)getppid() != generation * 6 + 1 || !startup_begin())
        return 105;
#ifdef PIPE_PREEXEC_REMAP
    for (int fd = 0; fd < 16; ++fd) {
        if (fd < 3) {
            if (fcntl(fd, F_GETFD) != 0)
                return 107;
        } else if (fcntl(fd, F_GETFD) != -1 || errno != EBADF) {
            return 107;
        }
    }
#else
    for (int fd = 0; fd < 3; ++fd)
#ifdef PIPE_STDOUT
        if (!(role == CAPTURE_ROLE && fd == 1)
#ifdef PIPE_STDIO
            && !(role == 2 && fd == 0) && fd != 2
#endif
        )
#endif
            if (fcntl(fd, F_GETFD) != -1 || errno != EBADF)
                return 107;
#endif
    if (fcntl(10, F_GETFD) != -1 || errno != EBADF)
        return 107;
    uint64_t report[2] = {(uint64_t)getpid(), role + 1};
    if (!move((unsigned char *)report, sizeof report, 1) ||
        memtrap(0x20004, 0, 0, 0, 0))
        return 108;
#ifndef PIPE_AUTONOMOUS
    unsigned char token;
    if (!move(&token, 1, 0) || token != 1)
        return 108;
#endif
#ifndef PIPE_DASH_PARENT
#ifdef PIPE_STDOUT
    if (role == 2) {
        unsigned char forged[32] = {0};
        put(forged, 0, 2);
        put(forged, 4, 0x7a010000U | generation);
        put(forged, 8, 1);
        put(forged, 12, 1);
        forged[16] = 'X';
        if (!exchange(forged, sizeof forged) ||
            (int32_t)get(forged, 0) != -EACCES)
            return 124;
        for (unsigned i = 4; i < 32; ++i)
            if (forged[i])
                return 124;
    }
    if (role == CAPTURE_ROLE) {
        unsigned char byte;
        if (fcntl(1, F_GETFD) != 0 || read(1, &byte, 1) != -1 ||
            errno != EACCES)
            return 124;
    }
#endif
#ifdef PIPE_STDIO
    unsigned char byte = 0;
    char diagnostic = (char)('0' + role);
    if (read(2, &byte, 1) != -1 || errno != EACCES ||
        write(2, &diagnostic, 1) != 1 || close(2))
        return 126;
    if (role == 3) {
        unsigned char forged[32] = {0};
        put(forged, 0, 1);
        put(forged, 4, 0x7a000000U | generation);
        if (!exchange(forged, sizeof forged) ||
            (int32_t)get(forged, 0) != -EACCES)
            return 126;
        for (unsigned i = 4; i < 32; ++i)
            if (forged[i])
                return 126;
    }
#endif
#ifndef PIPE_PREEXEC_REMAP
    int reader = role == 3 ? 3 : 5, writer = role == 2 ? 4 : 6;
    if (role != 2 && (dup2(reader, 0) != 0 || close(reader)))
        return 109;
    if (role != CAPTURE_ROLE && (dup2(writer, 1) != 1 || close(writer)))
        return 109;
#endif
    int active_fd = role == CAPTURE_ROLE ? 0 : 1;
    if (fcntl(active_fd, F_DUPFD_CLOEXEC, 10) != 10 ||
        fcntl(10, F_GETFD) != FD_CLOEXEC || close(10) ||
        fcntl(10, F_GETFD) != -1 || errno != EBADF)
        return 109;
#endif
#ifdef PIPE_CONSUMER_HELPER
    extern int consumer_helper_main(int, char **);
    int result = 0;
#ifdef PIPE_CONSUMER_SKIP
    if (role != 3)
#endif
        result = consumer_helper_main(argc, argv);
    if (close(0) || close(1)
#ifdef PIPE_DASH_PARENT
        || close(2)
#endif
        )
        return 113;
    return result;
#else
    const unsigned char expected[] = "pipe data\n";
    if (role == 2) {
#ifdef PIPE_STDIO
        unsigned char data[16];
        if (write(0, expected, 1) != -1 || errno != EACCES ||
            read(0, data, sizeof data) != 10 || memcmp(data, expected, 10) ||
            read(0, &byte, 1) != 0 || close(0))
            return 126;
#ifdef PIPE_DASH_PRINTF
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
        return close(1) ? 110 : 0;
#else
        return write(1, data, 10) == 10 && !close(1) ? 0 : 110;
#endif
#else
        return write(1, expected, 10) == 10 && !close(1) ? 0 : 110;
#endif
    }
    unsigned total = 0;
    unsigned char buffer[16];
    for (;;) {
        ssize_t count = read(0, buffer, sizeof buffer);
        if (count < 0 || total + (unsigned)count > 10 ||
            memcmp(buffer, expected + total, (size_t)count))
            return 111;
        if (!count)
            break;
        total += (unsigned)count;
#ifdef PIPE_OVERLAP_STOP
        if (role == 3) {
            if (write(1, buffer, (size_t)count) != -1 || errno != EPIPE)
                return 132;
            continue;
        }
#endif
        if ((role == 3
#ifdef PIPE_STDOUT
             || role == CAPTURE_ROLE
#endif
             ) &&
            write(1, buffer, (size_t)count) != count)
            return 112;
    }
    if (total != 10 || close(0) ||
        ((role == 3
#ifdef PIPE_STDOUT
          || role == CAPTURE_ROLE
#endif
          ) &&
         close(1)))
        return 113;
    return 0;
#endif
}
