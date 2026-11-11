/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

pid_t runner_fixture_fork(void);
int runner_fixture_exec(const char *, char *const[], char *const[]);
int runner_fixture_main(int, char **);
#define fork runner_fixture_fork
#define execve runner_fixture_exec
#define main runner_fixture_main
#include "filesystem-runner-native.c"
#undef main
#undef execve
#undef fork

static struct aefd_startup boot;
static jmp_buf finished;
static int outcome, wrapped, start_calls, fork_calls, wait_calls, close_calls;
static int ready_failure, fork_failure, wait_failure, close_failure, stale_close;

int64_t aefd_shell_start(void)
{
    ++start_calls;
    return 0;
}

int64_t aefd_shell_role(void) { return 1; }
int64_t aefd_shell_ready(void) { return ready_failure; }
struct aefd_startup *aefd_shell_external_startup(void) { return &boot; }

pid_t runner_fixture_fork(void)
{
    ++fork_calls;
    return fork_failure ? -1 : 10;
}

int runner_fixture_exec(const char *path, char *const args[], char *const env[])
{
    (void)path;
    (void)args;
    (void)env;
    assert(0 && "parent host case never executes a child");
    return -1;
}

long __aether_waitpid(int pid, int *status, int flags)
{
    assert(pid == 10 && flags == 0);
    ++wait_calls;
    *status = 23 << 8;
    return wait_failure ? -1 : pid;
}

int64_t aefd_context_close(struct aefd_context *session, int fd)
{
    assert(session == &boot.context && fd == 1 && wait_calls == 1);
    ++close_calls;
    if (close_failure)
        return -5;
    if (!stale_close) {
        session->map.slots[1] = (struct aefd_binding){0};
        session->native.sources[1] = (struct aefd_native_source){0};
    }
    return 0;
}

_Noreturn void __real__exit(int status)
{
    outcome = status;
    longjmp(finished, 1);
}

_Noreturn void __wrap__exit(int status)
{
    ++wrapped;
    __real__exit(status);
}

static void reset(void)
{
    memset(&boot, 0, sizeof boot);
    outcome = wrapped = start_calls = fork_calls = wait_calls = close_calls = 0;
    ready_failure = fork_failure = wait_failure = close_failure = stale_close = 0;
    boot.context.state = 1;
    boot.context.client.live = 1;
    boot.context.client.generation = boot.context.map.generation = 1;
    for (unsigned fd = 0; fd < 2; ++fd) {
        boot.context.map.slots[fd] = (struct aefd_binding){
            .kind = AEFD_BIND_TERMINAL, .selector = (uint8_t)fd};
        boot.context.native.sources[fd] = (struct aefd_native_source){
            .reference = UINT32_C(0x7a000001) | fd << 16,
            .selector = fd, .rights = fd + 1, .bound = 16};
    }
}

static void check(char *command, int status, int starts, int forks, int waits,
                  int closes)
{
    char program[] = "aether-run";
    char *argv[] = {program, command, NULL};
    if (!setjmp(finished)) {
        (void)runner_fixture_main(2, argv);
        assert(0 && "selected entry must exit");
    }
    assert(outcome == status && wrapped == (status == 23));
    assert(start_calls == starts && fork_calls == forks &&
           wait_calls == waits && close_calls == closes);
}

int main(void)
{
    char probe[] = "probe", wrong[] = "other";
    reset();
    check(probe, 23, 1, 1, 1, 1);
    reset();
    check(wrong, 1, 0, 0, 0, 0);
    reset();
    boot.context.map.slots[2] = boot.context.map.slots[1];
    check(probe, 1, 1, 0, 0, 0);
    reset();
    boot.context.native.sources[1].rights = 1;
    check(probe, 1, 1, 0, 0, 0);
    reset();
    ready_failure = 1;
    check(probe, 1, 1, 0, 0, 0);
    reset();
    fork_failure = 1;
    check(probe, 1, 1, 1, 0, 0);
    reset();
    wait_failure = 1;
    check(probe, 1, 1, 1, 1, 0);
    reset();
    close_failure = 1;
    check(probe, 1, 1, 1, 1, 1);
    reset();
    stale_close = 1;
    check(probe, 1, 1, 1, 1, 1);
    puts("PASS: 9 native runner entry host cases");
}
