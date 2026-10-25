/* SPDX-License-Identifier: BSD-2-Clause */
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>

/* Internal prerequisite probe: no output, no authority inferred from PID. */
int dash_startup_probe(void)
{
    struct sigaction original, selected, observed;
    sigset_t oldmask, one, current;
    int result = 0, action_saved = 0, mask_saved = 0, duplicate = -1;
    pid_t pid = getpid();

    if (pid <= 0 || getpid() != pid)
        return 10;
    if (sigaction(SIGUSR1, NULL, &original) != 0)
        return 20;
    action_saved = 1;
    selected = original;
    selected.sa_handler = original.sa_handler == SIG_IGN ? SIG_DFL : SIG_IGN;
    selected.sa_flags = 0;
    if (sigemptyset(&selected.sa_mask) != 0 ||
        sigaction(SIGUSR1, &selected, NULL) != 0 ||
        sigaction(SIGUSR1, NULL, &observed) != 0 ||
        observed.sa_handler != selected.sa_handler) {
        result = 20;
        goto done;
    }
    if (sigprocmask(SIG_BLOCK, NULL, &oldmask) != 0) {
        result = 21;
        goto done;
    }
    mask_saved = 1;
    int was_blocked = sigismember(&oldmask, SIGUSR1);
    if (was_blocked < 0 || sigemptyset(&one) != 0 ||
        sigaddset(&one, SIGUSR1) != 0 ||
        sigprocmask(was_blocked ? SIG_UNBLOCK : SIG_BLOCK, &one, NULL) != 0 ||
        sigprocmask(SIG_BLOCK, NULL, &current) != 0 ||
        sigismember(&current, SIGUSR1) != !was_blocked) {
        result = 21;
        goto done;
    }
    for (int fd = 0; fd < 3; ++fd) {
        if (fcntl(fd, F_GETFD) < 0) {
            result = 30;
            goto done;
        }
    }
    duplicate = fcntl(0, F_DUPFD_CLOEXEC, 10);
    if (duplicate < 10) {
        result = 30;
        goto done;
    }
    int flags = fcntl(duplicate, F_GETFD);
    if (flags < 0 || !(flags & FD_CLOEXEC))
        result = 30;
done:
    /* Do not retry close when completion is uncertain. */
    if (duplicate >= 0 && close(duplicate) != 0 && result == 0)
        result = 40;
    if (mask_saved && sigprocmask(SIG_SETMASK, &oldmask, NULL) != 0 &&
        result == 0)
        result = 40;
    if (action_saved && sigaction(SIGUSR1, &original, NULL) != 0 && result == 0)
        result = 40;
    return result;
}

#ifndef DASH_STARTUP_TEST
int main(void) { return dash_startup_probe(); }
#endif
