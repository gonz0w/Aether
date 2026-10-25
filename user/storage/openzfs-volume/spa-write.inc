/* SPDX-License-Identifier: BSD-2-Clause */
/* Included only by the writable physical fixture. No TXG or pool is created.
 * Write ABD and completion record remain alive through zio_wait. The flush
 * witness ends only after the original root wait settles its child. */
#include "write-witness.h"
extern int zfs_nocacheflush;
static void aether_physical_write_done(zio_t *zio)
{
    struct aether_physical_completion *record = zio->io_private;
    ++record->count;
    record->error = zio->io_error;
    record->invalid =
        zio->io_spa != record->spa || zio->io_vd != record->vdev ||
        zio->io_abd != record->abd || zio->io_type != ZIO_TYPE_WRITE ||
        zio->io_size != 512 || zio->io_offset != 1048576;
    aether_engine_utc_phase('k');
}
static int aether_physical_write_probe(spa_t *spa, vdev_t *leaf, int mode)
    __attribute__((__noinline__));
static int aether_physical_write_probe(spa_t *spa, vdev_t *leaf, int mode)
{
    if (mode == 1)
        return 0; /* Fresh-VM read only, using the preceding write's image. */
    if (zfs_nocacheflush || leaf->vdev_nowritecache)
        return 872;
    unsigned char bytes[544];
    memset(bytes, 29, sizeof(bytes));
    for (unsigned i = 0; i < 512; ++i)
        bytes[16 + i] = (unsigned char)(i * 17 + 91);
    abd_t *abd = abd_get_from_buf(bytes + 16, 512);
    if (!abd)
        return 872;
    struct aether_physical_completion record = {
        .spa = spa, .vdev = leaf, .abd = abd};
    zio_flag_t flags = ZIO_FLAG_CANFAIL | ZIO_FLAG_DONT_RETRY |
                       ZIO_FLAG_DONT_AGGREGATE | ZIO_FLAG_SPECULATIVE |
                       ZIO_FLAG_CONFIG_WRITER;
    aether_physical_write_begin(leaf);
    aether_engine_utc_phase('q');
    int result = zio_wait(
        zio_write_phys(NULL, leaf, 1048576, 512, abd, ZIO_CHECKSUM_OFF,
                       mode == 5 ? NULL : aether_physical_write_done, &record,
                       ZIO_PRIORITY_SYNC_WRITE, flags, B_FALSE));
    aether_engine_utc_phase('h');
    abd_free(abd);
    if (result || record.invalid || record.error)
        return 872;
    for (unsigned i = 0; i < sizeof(bytes); ++i) {
        unsigned char expected =
            i < 16 || i >= 528 ? 29 : (unsigned char)((i - 16) * 17 + 91);
        if (bytes[i] != expected)
            return 872;
    }
    if (record.count != 1)
        return 871;
    if (mode == 4 && aether_volume_finish_probe())
        return 872;
    if (mode == 2)
        zfs_nocacheflush = 1; /* Original successful-no-flush bypass control. */
    zio_t *root = zio_root(spa, NULL, NULL, flags);
    aether_engine_utc_phase('g');
    zio_flush(root, leaf);
    result = zio_wait(root);
    aether_engine_utc_phase('i');
    struct aether_write_witness witness;
    aether_physical_write_end(&witness);
    if (result || witness.invalid || witness.writes != 1 || witness.write_error)
        return 872;
    if (!witness.flushes || !witness.callbacks)
        return 868;
    if (witness.flushes != 1 || witness.callbacks != 1)
        return 872;
    if (mode == 3 || mode == 4) {
        if (witness.flush_error != (mode == 3 ? EACCES : EBADF))
            return 872;
        return 869; /* Parent wait succeeded; actual provider flush failed. */
    }
    if (witness.flush_error || leaf->vdev_nowritecache || zfs_nocacheflush)
        return 872;
    aether_engine_utc_phase('p');
    return 0;
}
