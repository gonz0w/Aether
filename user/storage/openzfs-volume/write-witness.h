/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_PHYSICAL_WRITE_WITNESS_H
#define AETHER_PHYSICAL_WRITE_WITNESS_H
/* Private single-outstanding-operation fixture, not a filesystem API. The
 * owner arms before write and reads only after original ZIO waits. Callback
 * and provider borrows settle before copying/clearing this owner-local record.
 * Identity pointers are compared, never dereferenced or exposed in output. */
struct aether_write_witness {
    unsigned writes, flushes, callbacks;
    int write_error, flush_error, invalid;
};
void aether_physical_write_begin(void *leaf);
void aether_physical_flush_callback(void *leaf, int flush_type);
void aether_physical_write_end(struct aether_write_witness *out);
#endif
