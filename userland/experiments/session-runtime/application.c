/* SPDX-License-Identifier: BSD-2-Clause */
/* Application startup and path policy; native authority stays with the owner.
 */
#include "session.h"
#include <stdlib.h>
#include <string.h>

extern int __real_main(int, char **);
extern char **environ;
_Noreturn void __real__exit(int);

int aether_session_exec_allowed(const char *path)
{
    return path && !strcmp(path, "/inputs/helper");
}

int __wrap_main(int argc, char **argv)
{
    unsigned role;
    if (aether_session_start(&role))
        __real__exit(143);
#ifdef SESSION_HELPER
#ifdef SESSION_FS_ABI29
    if (role == 1)
#else
    if (!role)
#endif
        __real__exit(143);
    __wrap__exit(__real_main(argc, argv));
#else
    (void)argc;
    (void)argv;

#ifdef SESSION_FS_ABI29
    if (role != 1)
#else
    if (role)
#endif
        __real__exit(143);
    char *environment[] = {"PWD=/work", "WITNESS=value", "LC_ALL=C",
                           "PATH=/nonexistent", NULL};
#ifdef SESSION_WRONG_ENV
    environment[1] = "WITNESS=wrong";
#endif
#ifdef SESSION_SERIAL
    char *arguments[] = {"sh", "-i", "+m", NULL};
#else
    char script[] = AETHER_SESSION_SCRIPT;
#ifdef SESSION_BAD_BYTE
    char *changed = strstr(script, "pipe data");
    if (!changed)
        __real__exit(145);
    *changed = 'P';
#endif
    char *arguments[] = {"sh", "-c", script, NULL};
#endif
    environ = environment;
    __wrap__exit(__real_main(3, arguments));
#endif
}
