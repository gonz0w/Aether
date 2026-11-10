/* SPDX-License-Identifier: BSD-2-Clause */
#include "filesystem-runner.h"
#include <string.h>

void ar_fs_run(struct ar_fs_run *run, const unsigned char *carrier, size_t size,
               const struct ar_fs_io *io, const struct ar_fs_owner *owner,
               void *context)
{
    if (!run || run->state != AR_FS_NEW)
        return;
    run->state = AR_FS_INVALID;
    run->exit_status = 1;
    struct ar_startup startup;
    struct ar_invocation invocation;
    if (!carrier || !ar_decode(carrier, size, &startup))
        return;
    enum ar_action action = ar_select(&startup, &invocation);
    if (action == AR_USAGE) {
        run->exit_status = 64;
        return;
    }
    if (action != AR_LAUNCH)
        return;
    if (strcmp(invocation.args[0], "probe") || invocation.count != 1 ||
        !io || !io->input_read || !io->output_write) {
        run->state = AR_FS_REJECTED;
        run->exit_status = 2;
        return;
    }
    if (!owner || !owner->admit || !owner->collect)
        return;
    run->state = AR_FS_ADMISSION_UNCERTAIN;
    struct ar_fs_child child = {0};
    enum ar_fs_delivery delivered =
        owner->admit(context, &invocation, io, &child);
    if (delivered == AR_FS_DENIED && !child.slot && !child.generation) {
        run->state = AR_FS_REJECTED;
        run->exit_status = 2;
        return;
    }
    run->child = child;
    if (delivered != AR_FS_ADMITTED || child.slot != 2 || !child.generation ||
        child.generation > 15)
        return;

    run->state = AR_FS_COLLECTION_UNCERTAIN;
    struct ar_fs_terminal terminal = {0};
    if (owner->collect(context, child, &terminal) != 1 ||
        terminal.child.slot != child.slot ||
        terminal.child.generation != child.generation ||
        terminal.kind < 1 || terminal.kind > 3)
        return;
    run->terminal = terminal;
    run->state = AR_FS_CLEANUP_FAILED;
    if (terminal.cleanup_complete != 1)
        return;
    run->state = AR_FS_COMPLETE;
    if (terminal.kind == 1 && terminal.detail <= 255)
        run->exit_status = terminal.detail;
}
