/* SPDX-License-Identifier: BSD-2-Clause */
#define _POSIX_C_SOURCE 200809L
#include "../command-runner/filesystem-runner.h"
#include "fd-exec.h"
#include "fd-libc.h"
#include <unistd.h>

#if !defined(AEFD_FILESYSTEM_RUNNER_BINDINGS) || \
    !defined(AEFD_ZSH_PROCESS_BINDINGS) || !defined(AEFD_EXTERNAL_STARTUP) || \
    defined(AEFD_ZSH_HELPER_ENTRY) || defined(AEFD_ZSH_DIAGNOSTIC)
#error "native runner requires the closed external process entry"
#endif

_Noreturn void __real__exit(int);

/* Copy from the bounded CRT argument strings before running the parser. */
static int carrier(unsigned char out[AR_CARRIER_SIZE], int argc,
                   char *const argv[])
{
    if (argc != 2 || !argv || !argv[0] || !argv[1] || argv[2])
        return 0;
    size_t program_length = strnlen(argv[0], AR_SLOT_SIZE);
    size_t command_length = strnlen(argv[1], AR_SLOT_SIZE);
    if (program_length != sizeof("aether-run") - 1 ||
        command_length != sizeof("probe") - 1 ||
        memcmp(argv[0], "aether-run", program_length) ||
        memcmp(argv[1], "probe", command_length))
        return 0;
    memcpy(out, "AERUN001", 8);
    out[8] = (unsigned char)argc;
    memcpy(out + 32, argv[0], program_length);
    memcpy(out + 64, argv[1], command_length);
    return 1;
}

static int exact_streams(const struct aefd_context *session)
{
    if (session->state != 1 || !session->client.live ||
        session->native.retired || session->native.closed ||
        session->map.generation != session->client.generation)
        return 0;
    for (unsigned fd = 0; fd < AEFD_BINDINGS_COUNT; ++fd) {
        const struct aefd_binding *slot = &session->map.slots[fd];
        if (slot->kind != (fd < 2 ? AEFD_BIND_TERMINAL : AEFD_BIND_EMPTY) ||
            slot->selector != (fd < 2 ? fd : 0) || slot->cloexec ||
            slot->reserved)
            return 0;
    }
    for (unsigned i = 0; i < 7; ++i) {
        const struct aefd_native_source *source = &session->native.sources[i];
        if (source->reference != (i < 2 ? UINT32_C(0x7a000001) | i << 16 : 0) ||
            source->selector != (i < 2 ? i : 0) ||
            source->rights != (i < 2 ? i + 1 : 0) ||
            source->bound != (i < 2 ? 16U : 0U))
            return 0;
    }
    return 1;
}

static enum ar_fs_delivery admit(void *context,
                                 const struct ar_invocation *invocation,
                                 const struct ar_fs_io *io,
                                 struct ar_fs_child *child)
{
    struct aefd_context *session = context;
    if (!exact_streams(session) ||
        io->input_read != session->native.sources[0].reference ||
        io->output_write != session->native.sources[1].reference)
        return AR_FS_DENIED;
    pid_t pid = fork();
    if (pid == 0) {
        struct ar_invocation command = *invocation;
        char *args[] = {command.args[0], NULL};
        char *env[] = {command.environment, NULL};
        (void)execve("/home/probe", args, env);
        __real__exit(126);
    }
    if (pid < 10 || pid > 108 || (pid - 3) % 7 != 0)
        return AR_FS_UNKNOWN;
    *child = (struct ar_fs_child){2, (uint32_t)(pid - 3) / 7};
    return AR_FS_ADMITTED;
}

static int collect(void *context, struct ar_fs_child child,
                   struct ar_fs_terminal *terminal)
{
    struct aefd_context *session = context;
    int pid = (int)child.generation * 7 + 3;
    int status = -1;
    if (__aether_waitpid(pid, &status, 0) != pid || status < 0 ||
        status > 0xff00 || (status & 0xff))
        return 0;
    *terminal = (struct ar_fs_terminal){.child = child,
                                        .kind = 1,
                                        .detail = (unsigned)status >> 8};
    /* The live exact map gives stdout a single alias. Its successful close
     * consumes a real Owner reply after collection and clears the source. */
    if (terminal->detail == 23 && exact_streams(session) &&
        aefd_context_close(session, 1) == 0 &&
        session->map.slots[1].kind == AEFD_BIND_EMPTY &&
        !session->native.sources[1].reference)
        terminal->cleanup_complete = 1;
    return 1;
}

int main(int argc, char **argv)
{
    unsigned char startup[AR_CARRIER_SIZE] = {0};
    if (!carrier(startup, argc, argv) || aefd_shell_start() ||
        aefd_shell_role() != 1)
        __real__exit(1);
    struct aefd_context *session = &aefd_shell_external_startup()->context;
    if (!exact_streams(session) || aefd_shell_ready())
        __real__exit(1);
    const struct ar_fs_io io = {session->native.sources[0].reference,
                                 session->native.sources[1].reference};
    const struct ar_fs_owner owner = {admit, collect};
    struct ar_fs_run run = {0};
    ar_fs_run(&run, startup, sizeof(startup), &io, &owner, session);
    if (run.state != AR_FS_COMPLETE || run.exit_status != 23)
        /* Containment owns any uncertain operation. Finalization could
         * submit a logical close again through the same context. */
        __real__exit(1);
    __wrap__exit((int)run.exit_status);
}
