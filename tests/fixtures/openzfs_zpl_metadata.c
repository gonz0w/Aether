/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual reader + metadata body; API doubles, not disk-decoder qualification.
 */
#define main reader_main
#define sa_bulk_lookup reader_sa_bulk_lookup
#include "openzfs_zpl_read.c"
#undef sa_bulk_lookup
#undef main
#include "zpl-metadata.h"

enum {
    ZPL_UID = 0,
    ZPL_GID = 1,
    ZPL_ATIME = 2,
    ZPL_MTIME = 3,
    ZPL_CTIME = 9,
    ZPL_CRTIME = 10
};
#define EXPECT(c)                                                              \
    do {                                                                       \
        if (!(c)) {                                                            \
            fprintf(stderr, "HOST METADATA oracle95 line%d\n", __LINE__);      \
            exit(95);                                                          \
        }                                                                      \
    } while (0)

static uint64_t raw_links = 1, raw_uid = 1001, raw_gid = 42, raw_flags = 0;
static aether_zpl_time times[4] = {
    {-9, 17}, {INT64_MIN, 0}, {INT64_MAX, 999999999}, {0, 999}};
static int missing;
static int sa_bulk_lookup(sa_handle_t *p, sa_bulk_attr_t *attrs, int n)
{
    EXPECT(p == &handle && handles == 1 && n == 8);
    const int ids[] = {ZPL_LINKS, ZPL_UID,   ZPL_GID,   ZPL_FLAGS,
                       ZPL_ATIME, ZPL_MTIME, ZPL_CTIME, ZPL_CRTIME};
    const uint64_t scalars[] = {raw_links, raw_uid, raw_gid, raw_flags};
    int error = fail();
    for (int i = 0; i < n; ++i) {
        EXPECT(attrs[i].attr == mapping[ids[i]]);
        EXPECT(attrs[i].bytes == (i < 4 ? 8 : 16));
        memcpy(attrs[i].value,
               i < 4 ? (const void *)&scalars[i] : (const void *)&times[i - 4],
               attrs[i].bytes);
        /* A failed lookup may have partially copied attributes. */
        if (i == 1 && (error || missing))
            return missing ? ENOENT : error;
    }
    return 0;
}

#include "metadata.inc"

int main(int argc, char **argv)
{
    EXPECT(argc == 3);
    int mode = atoi(argv[1]);
    setup();
    aether_zpl_view *view = NULL;
    EXPECT(!aether_zpl_open(&pool, "test/files", &view));
    uint64_t object = 4, generation = 8;
    int expected = 0;
    switch (mode) {
    case 0:
        break;
    case 1:
        object = 3;
        generation = 7;
        raw_links = 2;
        break;
    case 2:
        nodes[4].links = raw_links = 3;
        break;
    case 3:
        raw_uid = UINT64_MAX;
        raw_gid = UINT64_C(0x8000000012345678);
        break;
    case 4:
        nodes[4].mode |= S_ISUID | S_ISGID | S_ISVTX;
        break;
    case 5:
        times[0].nanoseconds = 999999999;
        break;
    case 6:
        expected = EINVAL;
        break;
    case 7:
        expected = EINVAL;
        break;
    case 8:
        object = 0;
        expected = EINVAL;
        break;
    case 9:
        generation = 0;
        expected = EINVAL;
        break;
    case 10:
        generation++;
        expected = ESTALE;
        break;
    case 11:
        nodes[4].bonus++;
        expected = ENOTSUP;
        break;
    case 12:
        nodes[4].mode = S_IFLNK | 0777;
        expected = ENOTSUP;
        break;
    case 13:
        nodes[4].type = DMU_OT_DIRECTORY_CONTENTS;
        expected = EIO;
        break;
    case 14:
        nodes[4].links = 0;
        expected = ENOENT;
        break;
    case 15:
        nodes[4].flags = ZFS_XATTR;
        expected = ENOTSUP;
        break;
    case 16:
    case 17:
    case 18:
    case 19:
        times[mode - 16].nanoseconds = 1000000000;
        expected = EIO;
        break;
    case 20:
        missing = 1;
        expected = ENOENT;
        break;
    case 21:
        nodes[4].gen = 0;
        expected = EIO;
        break;
    case 22:
        nodes[4].parent = 0;
        expected = EIO;
        break;
    case 23:
        raw_links = 0;
        expected = ENOENT;
        break;
    case 24:
        raw_flags = ZFS_XATTR;
        expected = ENOTSUP;
        break;
    case 25:
        raw_flags = UINT64_C(0xf000000000000000);
        break;
    default:
        EXPECT(0);
    }
    step = 0;
    fault = atoi(argv[2]);
    if (fault)
        expected = EIO;
    aether_zpl_metadata out;
    memset(&out, 0xa5, sizeof(out));
    int result = aether_zpl_getattr(mode == 6 ? NULL : view, object, generation,
                                    mode == 7 ? NULL : &out);
    EXPECT(result == expected && !handles && allocated == 1 && owned == 1);
    if (mode == 7) {
        const unsigned char *bytes = (const unsigned char *)&out;
        for (size_t i = 0; i < sizeof(out); ++i)
            EXPECT(bytes[i] == 0xa5);
    } else if (expected) {
        EXPECT(zero(&out, sizeof(out)));
    } else {
        EXPECT(out.node.object == object && out.node.generation == generation);
        EXPECT(out.node.size == nodes[object].size &&
               out.node.mode == nodes[object].mode);
        EXPECT(out.parent == nodes[object].parent && out.links == raw_links);
        EXPECT(out.uid == raw_uid && out.gid == raw_gid &&
               out.flags == raw_flags);
        EXPECT(!memcmp(&out.atime, times, sizeof(times)));
    }
    printf("METADATA PASS calls=%d\n", step);
    aether_zpl_close(&view);
    EXPECT(!view && !allocated && !owned && !handles && !reads);
    return 0;
}
