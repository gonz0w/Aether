/* SPDX-License-Identifier: BSD-2-Clause */
#include "extend-common.inc"
#include "extend-adapter.inc"
#include "extend-setup.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    int mode = atoi(argv[1]);
    setup();
    memset(disk + 6, 0xa5, sizeof(disk) - 6);
    memset(expected, 0, sizeof(expected));
    aether_zpl_view *view = NULL;
    CHECK(!aether_zpl_open_write(&pool, "test/files", &view));
    step = 0;
    fault = 0;
    uint64_t object = 4, gen = 8, size = 4102, sec = 1234, ns = 5678;
    int want = 0;
    if (mode == 1)
        size = 7;
    if (mode == 2)
        size = 6;
    if (mode == 3) {
        size = 5;
        want = ENOTSUP;
    }
    if (mode == 4) {
        size = 4103;
        want = EFBIG;
    }
    if (mode == 5) {
        size = UINT64_MAX;
        want = EFBIG;
    }
    if (mode == 6) {
        gen = 7;
        want = ESTALE;
    }
    if (mode == 7) {
        pool.writable = 0;
        want = EROFS;
    }
    if (mode == 8) {
        sec = UINT64_MAX;
        want = EINVAL;
    }
    if (mode == 9) {
        ns = 1000000000;
        want = EINVAL;
    }
    if (mode == 10) {
        nodes[4].flags = ZFS_IMMUTABLE;
        want = EPERM;
    }
    if (mode == 11) {
        nodes[4].mode |= S_ISUID;
        want = ENOTSUP;
    }
    if (mode == 12) {
        object = 3;
        gen = 7;
        size = nodes[3].size + 1;
        want = EISDIR;
    }
    if (mode == 13) {
        metadata_size_error = 1;
        want = EIO;
    }
    if (mode == 14) {
        nodes[4].size = UINT64_MAX;
        want = EFBIG;
    }
    if (mode >= 20 && mode <= 28) {
        stage = mode - 19;
        want = stage == 1   ? ENOMEM
               : stage == 2 ? ENOSPC
               : stage == 8 ? EXDEV
               : stage == 9 ? EALREADY
                            : EIO;
    }
    if (mode >= 101) {
        fault = mode - 100;
        want = EIO;
    }
    aether_zpl_write_result result = {99, 99, 99};
    int error = aether_zpl_extend(view, object, gen, size, sec, ns, &result);
    CHECK(error == want && !handles && !tx_live);
    if (mode == 2)
        CHECK(!creates && !writes && !result.txg && !result.state);
    else if (!error) {
        CHECK(result.txg == 42 && result.state == AETHER_ZPL_SYNCED &&
              result.bytes_staged == size - 6);
        CHECK(nodes[4].size == size && !memcmp(disk, "abcdef", 6));
        for (uint64_t i = 6; i < size; ++i)
            CHECK(disk[i] == 0);
        for (uint64_t i = size; i < sizeof(disk); ++i)
            CHECK(disk[i] == 0xa5);
        CHECK(modified[0] == sec && changed[0] == sec && modified[1] == ns &&
              changed[1] == ns);
    }
    if (creates && stage >= 3)
        CHECK(commits == 1 && !aborts && result.state == AETHER_ZPL_COMMITTED);
    if (writes)
        CHECK(result.bytes_staged == size - 6 && commits == 1);
    if (!creates)
        CHECK(!result.txg && !result.state && !result.bytes_staged);
    int calls = step;
    aether_zpl_close(&view);
    CHECK(!view && !owned && !allocated && allocations == frees);
    printf("calls=%d\n", calls);
    return 0;
}
