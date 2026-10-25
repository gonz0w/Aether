/* SPDX-License-Identifier: BSD-2-Clause */
/* Parent application entry; process/copy/exec module remains a required input.
 */
#include "fd-libc.h"
#include <stdlib.h>
#ifdef AEFD_EXEC_BINDINGS
#include "fd-exec.h"
#endif
extern int __real_main(int, char **);
_Noreturn void __real__exit(int);
int __wrap_main(int, char **);
int __wrap_main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    if (aefd_shell_start() || aefd_shell_role() != 1)
        __real__exit(143);
#ifdef AEFD_EXEC_BINDINGS
    if (aefd_shell_ready())
        __real__exit(143);
#endif
    char *arguments[] = {"sh", "-i", "+m", NULL};
    int status = __real_main(3, arguments);
    __wrap__exit(status);
}
