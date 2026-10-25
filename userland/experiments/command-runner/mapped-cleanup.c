/* SPDX-License-Identifier: BSD-2-Clause */
/* Local report-failure control, not failed remote close: release succeeds
 * first. */
#include "runner-result.h"
#include <errno.h>
#include <unistd.h>
static unsigned failed_close;
int __real_close(int fd);
int __wrap_close(int fd);
unsigned __real_ar_terminal_exit(const struct ar_reply *reply, int complete);
unsigned __wrap_ar_terminal_exit(const struct ar_reply *reply, int complete);
int __wrap_close(int fd)
{
    int result = __real_close(fd);
    if (fd == 4) {
        if (result || failed_close++)
            _exit(91);
        errno = EIO;
        return -1;
    }
    return result;
}
unsigned __wrap_ar_terminal_exit(const struct ar_reply *reply, int complete)
{
    if (failed_close != 1 || complete != 0 || !reply || reply->error ||
        reply->kind != 1 || reply->detail != 0 ||
        (reply->receipt != 0x73000001u && reply->receipt != 0x73000002u))
        _exit(91);
    return __real_ar_terminal_exit(reply, complete);
}
