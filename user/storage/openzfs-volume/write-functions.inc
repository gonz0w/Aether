/* SPDX-License-Identifier: BSD-2-Clause */
/* Only the writable physical fixture selects these transparent observers. */
static struct aether_write_witness write_witness;
static void *write_leaf;
static zfs_file_t *write_file;
static int write_armed;
void aether_physical_write_begin(void *leaf)
{
    memset(&write_witness, 0, sizeof(write_witness));
    write_leaf = leaf;
    write_file = NULL;
    write_armed = 1;
}
void aether_physical_flush_callback(void *leaf, int flush_type)
{
    if (!write_armed)
        return;
    ++write_witness.callbacks;
    if (leaf != write_leaf || !flush_type)
        write_witness.invalid = 1;
    if (aether_physical_io_phase)
        aether_physical_io_phase('c');
}
void aether_physical_write_end(struct aether_write_witness *out)
{
    *out = write_witness;
    write_armed = 0;
    write_leaf = NULL;
    write_file = NULL;
}
int zfs_file_pwrite(zfs_file_t *fp, const void *buf, size_t count, loff_t off,
                    uint8_t ashift, ssize_t *resid)
{
    int observed = write_armed && count == 512 && off == 1048576;
    if (observed && aether_physical_io_phase)
        aether_physical_io_phase('s');
    int error =
        aether_physical_pwrite_original(fp, buf, count, off, ashift, resid);
    if (observed) {
        ++write_witness.writes;
        if (write_file && write_file != fp)
            write_witness.invalid = 1;
        write_file = fp;
        write_witness.write_error = error;
        if (!resid || *resid)
            write_witness.invalid = 1;
        if (aether_physical_io_phase)
            aether_physical_io_phase(error ? 'x' : 't');
    }
    return error;
}
int zfs_file_fsync(zfs_file_t *fp, int flags)
{
    if (write_armed && aether_physical_io_phase)
        aether_physical_io_phase('f');
    int error = aether_physical_fsync_provider_original(fp, flags);
    if (write_armed) {
        ++write_witness.flushes;
        write_witness.flush_error = error;
        if (!write_file || write_file != fp)
            write_witness.invalid = 1;
        if (aether_physical_io_phase)
            aether_physical_io_phase(error ? 'e' : 'j');
    }
    return error;
}
