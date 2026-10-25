/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-libc.h"
#include "fd-exec.h"
extern int __real_main(int, char **);
_Noreturn void __real__exit(int);
int __wrap_main(int, char **);
int __wrap_main(int argc, char **argv)
{
    if (aefd_shell_start() || aefd_shell_role() < 2 || aefd_shell_role() > 4 ||
        aefd_shell_ready())
        __real__exit(143);
    __wrap__exit(__real_main(argc, argv));
}
