/* SPDX-License-Identifier: BSD-2-Clause */
/* Private startup/copy adaptation; upstream dash owns job construction. */
extern int __real_main(int, char **);
extern char **environ;
_Noreturn void __real__exit(int);
static void dash_copy_ready(void)
{
    unsigned long memory = getauxval(0xa000);
    unsigned slot = (unsigned)(memory & 255) - 1;
    unsigned epoch = (unsigned)((memory >> 8) & 255);
    if (slot < 2 || slot > 4 || !epoch || epoch > 15 ||
        memory != (0x40000000UL | ((unsigned long)epoch << 8) | (slot + 1)) ||
        (unsigned)getpid() != epoch * 6 + slot + 1 ||
        input != getauxval(0xa001) ||
        output != getauxval(0xa002) || !report(slot))
        __real__exit(135);
#ifdef PIPE_PARENT_SERIAL
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -13)
        __real__exit(139);
#endif
    execution_role = slot;
    cookie = 71;
}
_Noreturn void __wrap__exit(int status)
{
    if (startup_ready && !poisoned)
        for (int fd = 0; fd < 16; ++fd)
            if (startup_fds[fd].present && close(fd))
                __real__exit(136);
    __real__exit(status);
}
static int dash_parent(void)
{
    unsigned char startup[64] = {0};
    if (!move(startup, sizeof startup, 0) || get(startup, 16) != 1 ||
        get(startup, 32) != 0x76030000U + generation || get(startup, 36) != 1 ||
        get(startup, 40) != 1 || get(startup, 44) != generation)
        return 132;
    for (unsigned i = 20; i < 64; ++i)
        if ((i < 32 || i >= 48) && startup[i])
            return 132;
    const unsigned aux[] = {AT_UID, AT_EUID, AT_GID, AT_EGID};
    for (unsigned i = 0; i < 4; ++i)
        if (get(startup, i * 4) != 1000 || getauxval(aux[i]) != 1000)
            return 132;
    for (unsigned i = 0; i < 4; ++i)
        startup_ids[i] = get(startup, i * 4);
    startup_directory = get(startup, 32);
    struct sigaction action;
    if (sigaction(SIGCHLD, NULL, &action))
        __real__exit(138);
    char *environment[] = {"PWD=/work", "WITNESS=value", "LC_ALL=C",
                           "PATH=/nonexistent", NULL};
#ifdef PIPE_PARENT_SERIAL
    if (memtrap(0x26000, 0xf001, 0, 0, 0) != -13)
        __real__exit(139);
    char *arguments[] = {"sh", "-i", "+m", NULL};
#else
    char script[] = AETHER_PIPELINE_SCRIPT;
#ifdef PIPE_PARENT_BAD_BYTE
    script[8] = 'P';
#endif
    char *arguments[] = {"sh", "-c", script, NULL};
#endif
    environ = environment;
    __wrap__exit(__real_main(3, arguments));
}
