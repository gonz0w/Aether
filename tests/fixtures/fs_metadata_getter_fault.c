/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed wrapper semantics only; original storage decoding is a native gate. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "zpl-metadata.h"
static unsigned calls;
static int real_error;
static uint64_t marker;
static void check(int ok)
{
    if (!ok) {
        fputs("AF07_GETTER_ORACLE96\n", stderr);
        exit(96);
    }
}
int __real_aether_zpl_getattr(aether_zpl_view *view, uint64_t object,
                              uint64_t generation, aether_zpl_metadata *out)
{
    check(view == (aether_zpl_view *)&marker && object == 34 &&
          generation == 45);
    ++calls;
    memset(out, 0, sizeof(*out));
    if (real_error)
        return EIO;
    out->node.object = object;
    out->node.generation = generation;
    out->node.mode = 040755;
    out->node.size = 5;
    out->parent = 34;
    out->links = 4;
    out->atime.nanoseconds = 7;
    out->mtime.nanoseconds = 7;
    return 0;
}
#include "FAULT"
int main(int argc, char **argv)
{
    real_error = argc == 2 ? atoi(argv[1]) : 0;
    aether_zpl_metadata out;
    if (real_error) {
        check(__wrap_aether_zpl_getattr((aether_zpl_view *)&marker, 34, 45,
                                        &out) == EIO);
        check(calls == 1 && af07_gets == 1 && af07_fault_error == EIO);
        return 0;
    }
    for (unsigned i = 1; i <= 5; ++i) {
        int error =
            __wrap_aether_zpl_getattr((aether_zpl_view *)&marker, 34, 45, &out);
        check(calls == i && af07_gets == i && !af07_fault_error);
        if (i == 4 && AF07_METADATA_FAULT >= 3) {
            check(error == (AF07_METADATA_FAULT == 3 ? EIO : -EIO));
            const unsigned char *bytes = (const unsigned char *)&out;
            for (size_t n = 0; n < sizeof(out); ++n)
                check(bytes[n] == 0xa5);
        } else {
            check(!error && out.node.generation == 45 &&
                  out.node.mode == 040755 && out.node.size == 5 &&
                  out.links == 4 && out.atime.nanoseconds == 7);
            check(out.node.object ==
                  (i == 4 && AF07_METADATA_FAULT == 2 ? 35 : 34));
            check(out.mtime.nanoseconds ==
                  (i == 4 && AF07_METADATA_FAULT == 1 ? 1000000000 : 7));
        }
    }
    check(__wrap_aether_zpl_getattr((aether_zpl_view *)&marker, 34, 45, &out) ==
          EIO);
    check(calls == 5 && af07_gets == 5 && af07_fault_error == EIO);
    return 0;
}
