/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed three-step namespace experiment, not service policy. The host admits
 * each later writer only from the preceding fully qualified fresh reader. */
#if MNS_READER
#include "zpl-read.c"
#else
#include "zpl-mutate.c"
#endif
#include <sys/sha2.h>
#include <sys/zfs_acl.h>
#include <sys/spa_impl.h>
#include <time.h>

#define MNS_CREATED "aether-created"
#define MNS_RENAMED "aether-renamed"
extern void aether_engine_utc_phase(unsigned char);

static int namespace_error(unsigned char stage, int error)
{
    aether_engine_utc_phase('E');
    aether_engine_utc_phase(stage);
    for (unsigned i = 0; i < 4; ++i)
        aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
    return error;
}

static int namespace_original(aether_zpl_view *view)
{
    aether_zpl_node file;
    int error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",
                                  4, &file);
    if (!error && (file.object != 2 || file.generation != 47 ||
                   file.size != 780248 || file.mode != 0100755))
        error = EIO;
    SHA2_CTX hash;
    SHA2Init(SHA256, &hash);
    unsigned char buffer[4096], digest[32];
    uint64_t offset = 0;
    while (!error && offset < 780248) {
        size_t count = 0;
        error = aether_zpl_read(view, 2, 47, offset, buffer, sizeof(buffer),
                                &count);
        if (!error && count != MIN(sizeof(buffer), 780248 - offset))
            error = EIO;
        if (!error) {
            SHA2Update(&hash, buffer, count);
            offset += count;
        }
    }
    SHA2Final(digest, &hash);
    static const unsigned char expected[32] = {
        0xcc, 0x9b, 0xfd, 0xde, 0xdd, 0x66, 0x4b, 0x9a, 0x53, 0x34, 0x58,
        0x1a, 0xf7, 0x86, 0x51, 0x6d, 0x14, 0x9c, 0x3f, 0xbd, 0x2c, 0x7e,
        0x65, 0x73, 0x59, 0x85, 0xac, 0xf1, 0x7b, 0xce, 0x59, 0x35};
    if (!error && memcmp(digest, expected, sizeof(expected)))
        error = EIO;
    size_t count = 99;
    if (!error)
        error = aether_zpl_read(view, 2, 47, 780248, buffer, sizeof(buffer),
                                &count);
    return error ? error : count ? EIO : 0;
}

static int namespace_absent(aether_zpl_view *view, const char *name)
{
    aether_zpl_node node;
    int error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)name,
                                  strlen(name), &node);
    return error == ENOENT ? 0 : error ? error : EEXIST;
}

static int namespace_objects(aether_zpl_view *view, uint64_t extra)
{
    /* Independent original-zdb inventory: no unpublished/orphan file can hide
     * behind name absence. Original xattr objects3/4 must remain allocated. */
    static const uint64_t original[9] = {1, 2, 3, 4, 32, 33, 34, 35, 36};
    unsigned mask = 0, added = 0;
    uint64_t object = 0;
    for (unsigned count = 0; count < 16; ++count) {
        int error = dmu_object_next(view->os, &object, B_FALSE, 0);
        if (error == ESRCH)
            return mask == 511 && added == !!extra ? 0 : EIO;
        if (error)
            return error;
        if (!object || object > 4096)
            return EIO;
        unsigned i;
        for (i = 0; i < 9; ++i)
            if (object == original[i]) {
                if (mask & (1U << i))
                    return EIO;
                mask |= 1U << i;
                break;
            }
        if (i == 9) {
            if (object != extra || added)
                return EIO;
            added = 1;
        }
    }
    return EIO;
}

static int namespace_metadata(aether_zpl_view *view, uint64_t object, int file)
{
    sa_handle_t *handle = NULL;
    int error = sa_handle_get(view->os, object, NULL, SA_HDL_PRIVATE, &handle);
    if (error)
        return error;
    uint64_t flags = 0, links = 0, parent = 0, uid = 0, gid = 0, size = 99,
             project = 99, acl_count = 0;
    uint64_t mtime[2] = {0}, ctime[2] = {0}, crtime[2] = {0}, atime[2] = {0};
    zfs_ace_hdr_t acl[3] = {{0}};
    sa_bulk_attr_t attrs[14];
    int n = 0;
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_FLAGS], NULL, &flags, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_LINKS], NULL, &links, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PARENT], NULL, &parent, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_UID], NULL, &uid, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_GID], NULL, &gid, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_SIZE], NULL, &size, 8);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_MTIME], NULL, mtime, 16);
    SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CTIME], NULL, ctime, 16);
    if (file) {
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_PROJID], NULL, &project,
                         8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_CRTIME], NULL, crtime,
                         16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_ATIME], NULL, atime,
                         16);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_COUNT], NULL,
                         &acl_count, 8);
        SA_ADD_BULK_ATTR(attrs, n, view->attributes[ZPL_DACL_ACES], NULL, acl,
                         sizeof(acl));
    }
    error = sa_bulk_lookup(handle, attrs, n);
    sa_handle_destroy(handle);
    if (error)
        return error;
    if (parent != 34 || links != (file ? 1 : 2) || uid != (file ? 1000 : 0) ||
        gid != (file ? 1000 : 0) ||
        (flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) !=
            (ZFS_ARCHIVE | ZFS_AV_MODIFIED) ||
        ctime[0] < 1791290040 || ctime[0] > 1791290100 ||
        ctime[1] >= 1000000000)
        return EIO;
    if (!file)
        return memcmp(mtime, ctime, 16) ? EIO : 0;
    if (size || project || acl_count != 3 ||
        (flags & (ZFS_ACL_TRIVIAL | ZFS_ACL_PROTECTED | ZFS_PROJID)) !=
            (ZFS_ACL_TRIVIAL | ZFS_ACL_PROTECTED | ZFS_PROJID) ||
        mtime[0] < 1791290040 || mtime[0] > 1791290100 ||
        mtime[1] >= 1000000000 || memcmp(mtime, crtime, 16) ||
        memcmp(mtime, atime, 16) || acl[0].z_type ||
        acl[0].z_flags != ACE_OWNER ||
        acl[0].z_access_mask != UINT32_C(0x1e019f) || acl[1].z_type ||
        acl[1].z_flags != (ACE_GROUP | ACE_IDENTIFIER_GROUP) ||
        acl[1].z_access_mask != UINT32_C(0x120088) || acl[2].z_type ||
        acl[2].z_flags != ACE_EVERYONE ||
        acl[2].z_access_mask != UINT32_C(0x120088))
        return EIO;
#if MNS_KIND == 1
    if (memcmp(mtime, ctime, 16))
        return EIO;
#endif
    return 0;
}

static int namespace_check(aether_zpl_view *view, int phase, uint64_t *object,
                           uint64_t *generation)
{
    /* phase0 pristine,1 created,2 renamed,3 removed; constant independent
     * state. */
    aether_zpl_node root, file;
    int error = aether_zpl_root(view, &root);
    if (!error &&
        (root.object != 34 || root.generation != 45 || root.mode != 040755 ||
         root.size != ((phase == 1 || phase == 2) ? 4 : 3)))
        error = EIO;
    uint64_t count = 0;
    if (!error)
        error = zap_count(view->os, 34, &count);
    if (!error && count != ((phase == 1 || phase == 2) ? 2 : 1))
        error = EIO;
    if (!error)
        error = namespace_original(view);
    if (!error)
        error = namespace_absent(view, phase == 1 ? MNS_RENAMED : MNS_CREATED);
    if (!error && (phase == 0 || phase == 3))
        error = namespace_absent(view, MNS_RENAMED);
    uint64_t extra = 0;
    if (!error && (phase == 1 || phase == 2)) {
        const char *name = phase == 1 ? MNS_CREATED : MNS_RENAMED;
        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)name,
                                  strlen(name), &file);
        if (!error &&
            (!file.object || file.object == 2 || file.generation <= 782 ||
             file.size || file.mode != 0100600))
            error = EIO;
        if (!error && *object &&
            (*object != file.object || *generation != file.generation))
            error = EIO;
        if (!error) {
            extra = file.object;
            *object = file.object;
            *generation = file.generation;
            unsigned char byte = 0;
            size_t got = 99;
            error = aether_zpl_read(view, file.object, file.generation, 0,
                                    &byte, 1, &got);
            if (!error && got)
                error = EIO;
            if (!error)
                error = namespace_metadata(view, file.object, 1);
        }
    }
    if (!error && phase)
        error = namespace_metadata(view, 34, 0);
    if (!error)
        error = namespace_objects(view, extra);
    return error;
}

#if MNS_READER
int aether_pool_namespace_recover(spa_t *spa)
{
    if (!spa || spa_writeable(spa))
        return namespace_error(1, EROFS);
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open(spa, "testpool_zstd/x86_64", &view);
    if (error)
        return namespace_error(2, error);
    uint64_t object = 0, generation = 0;
    error = namespace_check(view, MNS_KIND, &object, &generation);
    aether_zpl_close(&view);
    return error ? namespace_error(9, error) : 0;
}
#else
int aether_pool_namespace_write(spa_t *spa, uint64_t *assigned)
{
    if (!assigned)
        return EINVAL;
    *assigned = 0;
    if (!spa || !spa_writeable(spa))
        return EROFS;
    aether_zpl_view *view = NULL;
    int error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    if (error)
        return namespace_error(1, error);
    unsigned char stage = 4;
    uint64_t object = 0, generation = 0;
    error = namespace_check(view, MNS_KIND - 1, &object, &generation);
    struct timespec utc = {0};
    if (!error) {
        stage = 5;
        if (clock_gettime(CLOCK_REALTIME, &utc))
            error = EIO;
    }
    if (!error &&
        (utc.tv_sec < 0 || utc.tv_nsec < 0 || utc.tv_nsec >= 1000000000))
        error = EINVAL;
    aether_zpl_write_result result = {0};
#if MNS_KIND == 1
    aether_zpl_node created = {0};
#endif
    if (!error) {
        stage = 6;
#if MNS_KIND == 1
        error =
            aether_zpl_create(view, 34, 45, (const unsigned char *)MNS_CREATED,
                              sizeof(MNS_CREATED) - 1, 1000, 1000, utc.tv_sec,
                              utc.tv_nsec, &created, &result);
        object = created.object;
        generation = created.generation;
#elif MNS_KIND == 2
        error = aether_zpl_rename(
            view, 34, 45, (const unsigned char *)MNS_CREATED,
            sizeof(MNS_CREATED) - 1, (const unsigned char *)MNS_RENAMED,
            sizeof(MNS_RENAMED) - 1, object, generation, utc.tv_sec,
            utc.tv_nsec, &result);
#else
        error =
            aether_zpl_remove(view, 34, 45, (const unsigned char *)MNS_RENAMED,
                              sizeof(MNS_RENAMED) - 1, object, generation,
                              utc.tv_sec, utc.tv_nsec, &result);
#endif
        *assigned = result.txg;
    }
    if (!error) {
        stage = 7;
        if (!result.txg || result.bytes_staged ||
            result.state != AETHER_ZPL_SYNCED)
            error = EIO;
    }
    aether_zpl_close(&view);
    if (!error) {
        stage = 8;
        error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
    }
    if (!error) {
        stage = 9;
        error = namespace_check(view, MNS_KIND, &object, &generation);
    }
    if (view)
        aether_zpl_close(&view);
    return error ? namespace_error(stage, error) : 0;
}
#endif
