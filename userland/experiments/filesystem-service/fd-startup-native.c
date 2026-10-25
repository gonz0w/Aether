/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-startup.h"
#include <sys/auxv.h>
int64_t aefd_startup_native(struct aefd_startup *b)
{
    struct aefd_startup_auxv observed = {getauxval(0xa000), getauxval(0xa001),
                                         getauxval(0xa002)};
    return aefd_startup_start(b, aefd_native_trap, NULL, observed);
}
