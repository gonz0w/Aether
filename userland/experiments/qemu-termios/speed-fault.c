/* SPDX-License-Identifier: BSD-2-Clause */
#include <errno.h>
#include <termios.h>
#include <unistd.h>

int __real_cfsetispeed(struct termios *settings, speed_t speed);

int __wrap_cfsetispeed(struct termios *settings, speed_t speed)
{
    static const char marker[] = "speed-wrapper-called\n";
    if (write(STDERR_FILENO, marker, sizeof(marker) - 1) !=
        sizeof(marker) - 1) {
        _exit(90);
    }
#if INJECT_FAILURE
    (void)settings;
    (void)speed;
    errno = EINVAL;
    return -1;
#else
    return __real_cfsetispeed(settings, speed);
#endif
}
