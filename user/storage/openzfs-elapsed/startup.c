/* SPDX-License-Identifier: BSD-2-Clause */
#include "startup.h"
#include <errno.h>
#include <stdlib.h>
#include <string.h>

static struct aether_zfs_startup snapshot;
static int bound;

static int label(const char value[65])
{
    unsigned end = 0;
    while (end < 65 && value[end]) {
        if ((unsigned char)value[end] < 32 || (unsigned char)value[end] > 126)
            return 0;
        ++end;
    }
    if (!end || end == 65)
        return 0;
    for (unsigned i = end; i < 65; ++i)
        if (value[i])
            return 0;
    return 1;
}
int aether_zfs_startup_bind(const struct aether_zfs_startup *input)
{
    if (bound)
        return EALREADY;
    if (!input || input->version != 1 || input->bytes != sizeof(*input) ||
        !input->hostid)
        return EINVAL;
    if (input->cache_policy != AETHER_ZFS_EMPTY_CACHE)
        return ENOTSUP;
    for (unsigned i = 0; i < sizeof(input->reserved); ++i)
        if (input->reserved[i])
            return EINVAL;
    for (unsigned i = 0; i < sizeof(input->padding); ++i)
        if (input->padding[i])
            return EINVAL;
    if (!label(input->sysname) || !label(input->nodename) ||
        !label(input->release) || !label(input->version_label) ||
        !label(input->machine) || strcmp(input->sysname, "Aether") ||
        strcmp(input->machine, "x86_64"))
        return EINVAL;
    snapshot = *input;
    bound = 1;
    return 0;
}
unsigned long aether_zfs_hostid(void)
{
    if (!bound)
        _Exit(125);
    return snapshot.hostid;
}
void aether_zfs_uname(struct utsname *out)
{
    if (!bound || !out)
        _Exit(125);
    memset(out, 0, sizeof(*out));
    memcpy(out->sysname, snapshot.sysname, 65);
    memcpy(out->nodename, snapshot.nodename, 65);
    memcpy(out->release, snapshot.release, 65);
    memcpy(out->version, snapshot.version_label, 65);
    memcpy(out->machine, snapshot.machine, 65);
}
void aether_zfs_empty_cache(void)
{
    if (!bound || snapshot.cache_policy != AETHER_ZFS_EMPTY_CACHE)
        _Exit(125);
}
