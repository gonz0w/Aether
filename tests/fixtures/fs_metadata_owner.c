/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual importer completion checks against explicit host service/context
 * doubles. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "metadata-service.h"

typedef struct {
    int live;
} aether_zpl_view;
typedef struct {
    int unused;
} spa_t;
typedef struct {
    uint64_t txg, bytes_staged, state;
} aether_zpl_write_result;
#define EIO 5
#define AETHER_FS_SERVICE_LIFETIMES 1
static int mode;
#ifdef AF07_HOST_METADATA_RESULT
static unsigned af07_gets;
static int af07_fault_error;
#endif
#if AETHER_FS_SERVICE_CASE == 3
static unsigned consumed, injected;
static int64_t host_close(uint64_t endpoint)
{
    if (endpoint != 0x10001 || consumed != 10 || injected++) {
        fputs("AF07_OWNER_ORACLE96: close preceded context consumption\n",
              stderr);
        exit(96);
    }
    return mode == 7 ? -5 : 0;
}
#define AETHER_FS_HOST_CLOSE host_close
#endif
unsigned long getauxval(unsigned long key)
{
    return key == 0xa004 ? 0x10001 : key == 0xa005 ? 0x10002 : 0;
}
#include "OWNER"
#if AETHER_FS_SERVICE_CASE == 3
void __real_aether_zpl_close(aether_zpl_view **view)
{
    if (!view || !*view || !(*view)->live)
        exit(96);
    (*view)->live = 0;
    *view = NULL;
    ++consumed;
}
#endif
int aether_fs_metadata_run(void *spa, const unsigned char *dataset,
                           size_t length, uint64_t reader, uint64_t writer,
                           uint64_t rights, uint64_t uid, uint64_t gid,
                           struct aether_fs_service_result *out)
{
    if (!spa || length != 20 || memcmp(dataset, "testpool_zstd/x86_64", 20) ||
        reader != 0x10001 || writer != 0x10002 || rights != 31 || uid != 1000 ||
        gid != 1000)
        exit(96);
    memset(out, 0, sizeof(*out));
    out->ready = 1;
    out->requests = 96;
    out->txg = 796;
    out->state = 2;
    int error = 0;
#if AETHER_FS_SERVICE_CASE == 1
    out->requests = 6;
    out->stop = 2;
    out->error = -32;
    error = 5;
#elif AETHER_FS_SERVICE_CASE == 2
    out->requests = 7;
    out->stop = 1;
    out->error = -5;
    error = 5;
#elif AETHER_FS_SERVICE_CASE == 3
    for (unsigned i = 0; i < 10; ++i) {
        aether_zpl_view value = {1}, *view = &value;
        __wrap_aether_zpl_close(&view);
        if (view || value.live) {
            fputs("AF07_OWNER_ORACLE96: context remained live\n", stderr);
            exit(96);
        }
    }
    out->reader_close = -13;
    out->error = -13;
    error = 5;
#endif
#ifdef AF07_HOST_METADATA_RESULT
    af07_gets = AF07_HOST_METADATA_RESULT == 3 ? 5 : 4;
    out->requests = AF07_HOST_METADATA_RESULT == 3 ? 96 : 38;
    out->stop = AF07_HOST_METADATA_RESULT == 3   ? 0
                : AF07_HOST_METADATA_RESULT == 1 ? 2
                                                 : 5;
    out->error = AF07_HOST_METADATA_RESULT == 3   ? 0
                 : AF07_HOST_METADATA_RESULT == 1 ? -32
                                                  : -5;
    error = AF07_HOST_METADATA_RESULT == 3 ? 0 : 5;
#endif
    switch (mode) {
    case 1:
        ++out->requests;
        break;
    case 2:
        ++out->stop;
        break;
    case 3:
        out->writer_close = -5;
        break;
    case 4:
        out->error = -99;
        break;
    case 5:
        error = error ? 0 : 5;
        break;
    case 6:
        out->ready = 0;
        break;
#ifdef AF07_HOST_METADATA_RESULT
    case 7:
        ++af07_gets;
        break;
    case 8:
        af07_fault_error = EIO;
        break;
#endif
    default:
        break;
    }
    return error;
}
int main(int argc, char **argv)
{
    mode = argc == 2 ? atoi(argv[1]) : 0;
    spa_t spa = {0};
    aether_zpl_write_result result = {0};
    int error = aether_fs_owner_probe(&spa, &result);
    if ((mode ? !error : error != 0) || result.txg != 796 ||
        result.bytes_staged || result.state != 2) {
        fputs(
            "AF07_OWNER_ORACLE96: wrong completion accepted or progress lost\n",
            stderr);
        return 96;
    }
    return 0;
}
