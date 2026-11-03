/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-zsh-external.h"
#include "fd-libc.h"
#include "fd-exec.h"
#if !defined(AEFD_ZSH_PROCESS_BINDINGS) || !defined(AEFD_ZSH_HELPER_ENTRY) ||  \
    defined(AEFD_ZSH_DIAGNOSTIC)
#error                                                                         \
    "helper requires its fresh selected process entry without parent diagnostic"
#endif
extern int __real_main(int, char **);
_Noreturn void __real__exit(int);
int __wrap_main(int argc, char **argv)
{
    if (aefd_shell_start() || aefd_shell_role() != 2 || aefd_shell_ready())
        __real__exit(143);
    /* CRT arguments/environment come from the exact committed exec record. */
    __wrap__exit(__real_main(argc, argv));
}
