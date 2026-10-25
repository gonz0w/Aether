/* SPDX-License-Identifier: BSD-2-Clause */
/* Private path/argument subset; the authenticated owner selects image grants.
 */
static unsigned execution_role;
int execve(const char *path, char *const argv[], char *const envp[])
{
#ifdef PIPE_HELPER_ARGS
#ifdef PIPE_DASH_PARENT
    const char *expected[] = {"PWD=/work", "WITNESS=value", "LC_ALL=C", "PATH=/nonexistent"};
    unsigned seen = 0;
    if (!envp)
        return startup_error(EINVAL);
    for (unsigned i = 0; i < 4; ++i) {
        if (!envp[i])
            return startup_error(EINVAL);
        unsigned match = 0;
        for (unsigned j = 0; j < 4; ++j)
            if (!strcmp(envp[i], expected[j]))
                match = 1U << j;
        if (!match || (seen & match))
            return startup_error(EINVAL);
        seen |= match;
    }
    if (envp[4] || seen != 15)
        return startup_error(EINVAL);
#endif
    if (!path || !argv || !envp ||
#ifndef PIPE_DASH_PARENT
        envp[0] ||
#endif
        !argv[0] || !argv[1] ||
        argv[2] || strcmp(argv[0], "/inputs/helper") || strcmp(argv[1],
#ifdef PIPE_SHELL_EARLY
            execution_role == 2 ? "pump" : "one"
#else
            "copy"
#endif
        ))
        return startup_error(EINVAL);
#else
    if (!path || !argv || !envp || envp[0] || !argv[0] || !argv[1] ||
        !argv[2] || argv[3] || strcmp(argv[0], "replacement") ||
        argv[1][0] != (char)('0' + execution_role) || argv[1][1] ||
        argv[2][0] != (char)('0' + generation) || argv[2][1])
        return startup_error(EINVAL);
#endif
    unsigned image;
    if (!strcmp(path, "/denied"))
        image = 0xffff;
    else if (!strcmp(path,
#ifdef PIPE_HELPER_ARGS
                     "/inputs/helper"
#else
                     "/replacement"
#endif
                     ))
        image = 0xc002;
    else
        return startup_error(ENOENT);
#ifdef PIPE_PARENT_ALIAS
    if (fcntl(0, F_DUPFD, 10) != 10)
        return startup_error(EIO);
#endif
    unsigned char frame[32] = {0};
    put(frame, 0, 84);
    put(frame, 4, image);
    put(frame, 8, execution_role);
    put(frame, 12, generation);
#ifdef PIPE_HELPER_ARGS
    /* argv0 is fixed by the granted image selector; transmit the bounded vector. */
    put(frame, 16, 2);
#ifdef PIPE_SHELL_EARLY
    memcpy(frame + 20, execution_role == 2 ? "pump" : "one", 4);
#else
    memcpy(frame + 20, "copy", 4);
#endif
#ifdef PIPE_DASH_PARENT
    put(frame, 24, 4);
    put(frame, 28, 1); /* Validated complete fixed environment profile. */
#ifdef PIPE_PARENT_ENV
    put(frame, 28, 2);
#endif
#endif
#ifdef PIPE_HELPER_BAD_WIRE
    frame[20] = 'x';
#endif
#endif
    if (!exchange(frame, sizeof frame))
        return startup_error(EIO);
    for (unsigned i = 4; i < 32; ++i)
        if (frame[i])
            return startup_error(EIO);
    int result = (int32_t)get(frame, 0);
    if (result)
        return startup_error(result == -EACCES ? EACCES : EIO);
    if (image != 0xc002 || !live_snapshot())
        return startup_error(EIO);
    memtrap(0x23003, 0, 0, 0, 0);
    return startup_error(
        EIO); /* A successful replacement cannot return here. */
}
