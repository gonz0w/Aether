/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed explicit FILE diagnostic; no general libc/routed write activation. */
#include "fd-home-probe-adapter.h"
static const unsigned char payload[] = "AF09-HOME-WRITE\n";
_Static_assert(sizeof(payload) - 1 == 16, "fixed home payload");
static int completed(const struct aefd_write_result *r)
{
    return r->observation == AEFD_WRITE_REMOTE && !r->status &&
           r->requested == 16 && !r->file_closed && !r->file_cleanup.input &&
           !r->file_cleanup.output && !r->remote.status &&
           r->remote.count == 16 && r->remote.flags == 14 &&
           !r->remote.offset && r->remote.txg && r->remote.staged == 16 &&
           !r->remote.error_kind && !r->remote.error_value &&
           !r->remote.source_cleanup.input && !r->remote.source_cleanup.output;
}
int aefd_home_probe_run(struct aefd_context *c)
{
    int64_t fd =
        aefd_home_probe_open(c, (const unsigned char *)"probe", 5, 1, 1);
    if (fd < 0)
        return 81;
    struct aefd_write_result written;
    if (aefd_home_probe_write(c, (int)fd, payload, sizeof(payload) - 1,
                              &written) != 16 ||
        !completed(&written))
        return 82;
    if (aefd_context_close(c, (int)fd))
        return 83;
    fd = aefd_home_probe_open(c, (const unsigned char *)"probe", 5, 0, 1);
    if (fd < 0)
        return 84;
    unsigned char bytes[16];
    int result = aefd_context_read(c, (int)fd, bytes, sizeof(bytes)) != 16 ||
                         memcmp(bytes, payload, sizeof(bytes)) ||
                         aefd_context_read(c, (int)fd, bytes, 1) != 0
                     ? 85
                     : 0;
    if (aefd_context_close(c, (int)fd) && !result)
        result = 86;
    if (result)
        return result;
    fd = aefd_context_open(c, (const unsigned char *)"/zstd", 5, 1);
    if (fd < 0)
        return 87;
    struct aefd_write_result denied;
    /* The retained read-only root FILE fails before an AF09 provider call.
     * The separate result keeps the successful home receipt unchanged. */
    result = aefd_home_probe_write(c, (int)fd, payload, sizeof(payload) - 1,
                                   &denied) != -22 ||
                     denied.observation != AEFD_WRITE_REMOTE ||
                     denied.status != -22 || denied.remote.status != -22 ||
                     denied.remote.count || denied.remote.flags != 8 ||
                     denied.remote.offset || denied.remote.txg ||
                     denied.remote.staged || denied.remote.error_kind != 7 ||
                     denied.remote.error_value || denied.file_closed ||
                     denied.remote.source_cleanup.input ||
                     denied.remote.source_cleanup.output ||
                     denied.file_cleanup.input || denied.file_cleanup.output
                 ? 88
                 : 0;
    if (aefd_context_close(c, (int)fd) && !result)
        result = 89;
    return result;
}
#ifndef AEFD_HOME_PROBE_HOST_TEST
#include "fd-fork-stage.h"
#include <unistd.h>
int main(int argc, char **argv);
int main(int argc, char **argv)
{
    (void)argv;
    if (argc != 2)
        return 80;
    struct aefd_fork *fork = aefd_shell_fork_context();
    if (!fork || fork->boot.phase != 2)
        return 90;
    int result = aefd_home_probe_run(&fork->boot.context);
    if (result)
        return result;
    return write(1, "AF09-HOME-WR\n", 13) == 13 ? 7 : 91;
}
#endif
