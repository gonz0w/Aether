/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual shrink implementation, deterministic original-API fault doubles. */
#include "zpl-resize-common.inc"
#include "zpl-resize-adapter.inc"
#include "zpl-resize-setup.inc"

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    int mode = atoi(argv[1]);
    setup();
    aether_zpl_view *view = NULL;
    CHECK(!aether_zpl_open_write(&pool, "test/files", &view) && view);
    step = 0;
    fault = 0;
    uint64_t object = 4, generation = 8, size = 2, seconds = 1234, nanos = 5678;
    int expected_error = 0;
    switch (mode) {
    case 0:
        break;
    case 1:
        size = 0;
        break;
    case 2:
        size = 6;
        break;
    case 3:
        nodes[4].size = 1048582;
        memset(disk + 6, 0xa5, 1048576);
        size = 6;
        break;
    case 10:
        size = 7;
        expected_error = ENOTSUP;
        break;
    case 11:
        size = UINT64_MAX;
        expected_error = EFBIG;
        break;
    case 12:
        seconds = UINT64_MAX;
        expected_error = EINVAL;
        break;
    case 13:
        nanos = 1000000000;
        expected_error = EINVAL;
        break;
    case 14:
        generation = 7;
        expected_error = ESTALE;
        break;
    case 15:
        object = 3;
        generation = 7;
        expected_error = EISDIR;
        break;
    case 16:
    case 17:
        nodes[4].mode |= mode == 16 ? S_ISUID : S_ISGID;
        expected_error = ENOTSUP;
        break;
    case 18:
    case 19:
    case 20:
        nodes[4].flags = mode == 18   ? ZFS_IMMUTABLE
                         : mode == 19 ? ZFS_APPENDONLY
                                      : ZFS_READONLY;
        expected_error = EPERM;
        break;
    case 21:
        nodes[4].flags = ZFS_XATTR;
        expected_error = ENOTSUP;
        break;
    case 22:
        nodes[4].links = 0;
        expected_error = ENOENT;
        break;
    case 23:
        nodes[4].gen = 0;
        expected_error = EIO;
        break;
    case 24:
        nodes[4].size = (uint64_t)INT64_MAX + 1;
        expected_error = EFBIG;
        break;
    case 25:
        metadata_size_error = 1;
        expected_error = EIO;
        break;
    case 26:
        pool.writable = 0;
        expected_error = EROFS;
        break;
    case 27:
    case 28:
        expected_error = EINVAL;
        break;
    case 29:
        size = 6;
        nodes[4].flags = ZFS_IMMUTABLE;
        expected_error = EPERM;
        break;
    case 30:
        nodes[4].size = 1048579;
        expected_error = EFBIG;
        break;
    case 31:
        nodes[4].mode = S_IFLNK | 0777;
        expected_error = ENOTSUP;
        break;
    case 32:
        nodes[4].bonus = 0;
        expected_error = ENOTSUP;
        break;
    case 60:
    case 61:
    case 62:
    case 63:
    case 64:
    case 65:
        stage = mode - 59;
        expected_error = stage == 1 ? ENOMEM : stage == 2 ? ENOSPC : EIO;
        break;
    case 66:
        stage = 10;
        expected_error = ENXIO;
        break;
#ifdef AETHER_ZPL_ORDERED_WRITE
    case 68:
    case 69:
    case 70:
        stage = mode - 61;
        expected_error = stage == 7 ? EIO : stage == 8 ? EXDEV : EALREADY;
        break;
#endif
    default:
        CHECK(mode >= 50 && mode < 55);
        fault = mode - 49;
        expected_error = EIO;
    }
    uint64_t old_size = nodes[4].size;
    aether_zpl_write_result result;
    memset(&result, 0xa5, sizeof(result));
    int error =
        aether_zpl_shrink(mode == 27 ? NULL : view, object, generation, size,
                          seconds, nanos, mode == 28 ? NULL : &result);
    CHECK(error == expected_error);
    CHECK(!handles && !tx_live && !writes);
    if (mode != 28) {
        CHECK(result.state ==
              (commits ? (error ? AETHER_ZPL_COMMITTED : AETHER_ZPL_SYNCED)
                       : AETHER_ZPL_UNASSIGNED));
        CHECK(result.txg == (commits && stage != 3 ? 42 : 0));
        CHECK(!result.bytes_staged);
    }
    if (shrink_frees) {
        CHECK(shrink_frees == 1 && free_calls == 1);
        for (uint64_t i = size; i < old_size; ++i)
            CHECK(disk[i] == 0);
        CHECK(!memcmp(disk, "abcdef", size < 6 ? size : 6));
    } else {
        CHECK(!memcmp(disk, "abcdef", 6));
    }
    if (!error && mode != 2) {
        CHECK(shrink_frees == 1 && nodes[4].size == size);
        CHECK(modified[0] == seconds && modified[1] == nanos &&
              changed[0] == seconds && changed[1] == nanos);
        CHECK(nodes[4].flags == (ZFS_ARCHIVE | ZFS_AV_MODIFIED));
        CHECK(commits == 1 && !aborts && updates == 1 && waits == 1 &&
              last_checks == 1 && netfree == 1);
    }
    if (mode == 2) {
        CHECK(nodes[4].size == 6 && !creates && !commits && !shrink_frees &&
              !updates && !waits && !netfree && !modified[0] && !changed[0]);
    }
    if (!commits)
        CHECK(!shrink_frees && !updates && !waits && !last_checks);
    if (stage == 2)
        CHECK(aborts == 1 && !commits);
    if (stage == 3 || stage == 4 || stage == 10)
        CHECK(commits == 1 && !aborts && !waits);
    if (stage == 10)
        CHECK(free_calls == 1 && !shrink_frees && !updates &&
              nodes[4].size == 6);
    if (stage == 4)
        CHECK(shrink_frees == 1 && updates == 1 && error);
#ifdef AETHER_ZPL_ORDERED_WRITE
    CHECK(joins == (commits && stage != 3 ? 1 : 0));
    if (stage >= 7 && stage <= 9)
        CHECK(commits == 1 && !free_calls && !updates && !waits);
#endif
    aether_zpl_close(&view);
    CHECK(!view && !owned && !allocated && !handles && !tx_live);
    CHECK(allocations == frees);
    return 0;
}
