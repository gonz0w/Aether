/* SPDX-License-Identifier: BSD-2-Clause */
#include "startup-fixture.h"
#include <string.h>
#ifdef STARTUP_MISSING
/* Keep the required ELF TLS view when this early rejection makes all of the
 * ordinary client's worker/TLS code unreachable to the compiler. */
static _Thread_local volatile unsigned startup_cookie = 23;
#endif
static int startup_probe(void)
{
#ifdef STARTUP_MISSING
    if (startup_cookie != 23)
        return 833;
    /* An actual required consumer must fail before publishing a fallback. */
    aether_zfs_hostid();
    return 831;
#else
    struct aether_zfs_startup supplied = startup_fixture;
#ifdef STARTUP_VERSION
    supplied.version = 2;
#endif
#ifdef STARTUP_CACHE
    supplied.cache_policy = 2;
#endif
    if (aether_zfs_startup_bind(&supplied))
        return 830;
    /* Caller mutation cannot change the bound owner snapshot. */
    supplied.hostid = 0;
    memset(supplied.nodename, 0, sizeof(supplied.nodename));
    struct utsname observed;
    memset(&observed, 0xa5, sizeof(observed));
    aether_zfs_uname(&observed);
    aether_zfs_empty_cache();
    return aether_zfs_hostid() == startup_fixture.hostid &&
                   !strcmp(observed.sysname, startup_fixture.sysname) &&
                   !strcmp(observed.nodename, startup_fixture.nodename) &&
                   !strcmp(observed.release, startup_fixture.release) &&
                   !strcmp(observed.version, startup_fixture.version_label) &&
                   !strcmp(observed.machine, startup_fixture.machine) &&
                   aether_zfs_startup_bind(&startup_fixture) == EALREADY
               ? 0
               : 832;
#endif
}
