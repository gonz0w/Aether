/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed importer-only faults over the original copied getter result.
 * Only the serialized importer thread calls the getter. No counter reset/rearm,
 * retained view/output pointer, worker invocation or filesystem mutation. */
#ifndef AF07_METADATA_FAULT
#error "Select a fixed AF07 metadata fault"
#endif
#if AF07_METADATA_FAULT < 0 || AF07_METADATA_FAULT > 4
#error "Invalid AF07 metadata fault"
#endif
static unsigned af07_gets;
static int af07_fault_error;
extern int __real_aether_zpl_getattr(aether_zpl_view *, uint64_t, uint64_t,
                                     aether_zpl_metadata *);
int __wrap_aether_zpl_getattr(aether_zpl_view *view, uint64_t object,
                              uint64_t generation, aether_zpl_metadata *out)
{
    if (af07_gets >= 5) {
        af07_fault_error = EIO;
        return EIO;
    }
    ++af07_gets;
    int error = __real_aether_zpl_getattr(view, object, generation, out);
    if (error) {
        af07_fault_error = error;
        return error;
    }
    if (af07_gets == 4) {
#if AF07_METADATA_FAULT == 1
        out->mtime.nanoseconds = UINT64_C(1000000000);
#elif AF07_METADATA_FAULT == 2
        out->node.object ^= 1;
#elif AF07_METADATA_FAULT == 3
        /* Deliberately violate zero-on-error to test the receiving boundary. */
        memset(out, 0xa5, sizeof(*out));
        return EIO;
#elif AF07_METADATA_FAULT == 4
        memset(out, 0xa5, sizeof(*out));
        return -EIO;
#endif
    }
    return 0;
}
