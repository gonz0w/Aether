/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded parent-side pipe factory and child collection for the native witness.
 */
#include <sys/wait.h>
static unsigned factory, created;
int pipe(int pair[2])
{
    if (!pair)
        return startup_error(EFAULT);
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return startup_error(EIO);
    int error = 0, slots[2] = {-1, -1};
    unsigned count = 0;
    for (int fd = 0; fd < 16 && count < 2; ++fd)
        if (!startup_fds[fd].present)
            slots[count++] = fd;
    if (!startup_ready || poisoned || !factory)
        error = EIO;
    else if (count != 2)
        error = EMFILE;
    else if (created == 2)
        error = ENFILE;
    else {
        unsigned char frame[32] = {0};
        put(frame, 0, 82);
        put(frame, 4, factory);
        put(frame, 8, 1);
        if (!exchange(frame, sizeof frame) || get(frame, 0) ||
            get(frame, 4) != generation ||
            get(frame, 8) !=
                (0x79000001U | (created << 16) | (generation << 8)) ||
            get(frame, 12) !=
                (0x79000002U | (created << 16) | (generation << 8)) ||
            get(frame, 16) != 3 + created * 2 ||
            get(frame, 20) != 4 + created * 2 || get(frame, 24) != 256 ||
            get(frame, 28) != 16)
            error = EIO;
        else {
            for (unsigned end = 0; end < 2; ++end) {
                unsigned binding = 3 + created * 2 + end;
                refs[binding] = get(frame, 8 + end * 4);
                fds[binding] = binding;
                rights[binding] = end ? 2 : 1;
                live[binding] = 1;
                startup_users[binding] = 1;
                startup_fds[slots[end]] = (struct startup_fd){binding, 0, 1};
            }
            ++created;
            pair[0] = slots[0];
            pair[1] = slots[1];
        }
    }
    if (error == EIO)
        poisoned = 1;
    startup_mask_leave(previous);
    return error ? startup_error(error) : 0;
}
static long capacity_wait(int pid, int *status, int options)
{
#ifdef PIPE_WAIT_ANY
    if ((pid != -1 && pid <= 0) || !status ||
        (options != 0 && options != WNOHANG))
        return -EINVAL;
#else
    if (pid <= 0 || !status || options)
        return -EINVAL;
#endif
    unsigned char frame[32] = {0};
    put(frame, 0, 68);
    put(frame, 4, (unsigned)pid);
#ifdef PIPE_WAIT_ANY
    put(frame, 8, (unsigned)options);
#endif
    if (!exchange(frame, sizeof frame))
        return -EIO;
    int result = (int32_t)get(frame, 0);
#ifdef PIPE_WAIT_ANY
    int child =
        result >= (int)generation * 6 + 3 && result <= (int)generation * 6 + 5;
    if ((result > 0 && (!child || (pid != -1 && result != pid))) ||
        (result == 0 && options != WNOHANG) ||
        (result < 0 && result != -ECHILD) || (result <= 0 && get(frame, 4)))
        return -EIO;
#else
    if ((result != pid && result != -ECHILD) ||
        (result == -ECHILD && get(frame, 4)))
        return -EIO;
#endif
    for (unsigned i = 8; i < 32; ++i)
        if (frame[i])
            return -EIO;
    if (result > 0)
        *status = (int)get(frame, 4);
    return result;
}

long __aether_waitpid(int pid, int *status, int options)
{
#ifdef PIPE_WAIT_ANY
    if (poisoned)
        return -EIO;
    uint64_t previous;
    if (startup_mask_enter(&previous))
        return -EIO;
    long result = capacity_wait(pid, status, options);
    if (result == -EIO)
        poisoned = 1;
    startup_mask_leave(previous);
    return result;
#else
    return capacity_wait(pid, status, options);
#endif
}
