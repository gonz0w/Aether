/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_DIRECTORIES_SERVICE_H
#define AETHER_FS_DIRECTORIES_SERVICE_H
#include "native-service.h"
/* Private AF06 selected entry, same nine arguments/72-byte result and ABI26.
 * AF05 whole names/data framing and failure/ownership rules apply. Additional
 * named operations10 mkdir0700 and11 empty-rmdir use delegated parent tokens;
 * LOOKUP|MUTATE_DIR and trusted uid/gid/UTC, never raw client object
 * identities. All current resources/time/workload limits remain. Service
 * context/endpoints close on return; importer still owes ordered
 * drain/export/block quiescence. No fixture expected-error conversion,
 * automatic restart/replay or durability acknowledgment is authorized. This
 * header is not an operational executable.
 */
int aether_fs_directories_run(void *, const unsigned char *, size_t, uint64_t,
                              uint64_t, uint64_t, uint64_t, uint64_t,
                              struct aether_fs_service_result *);
#endif
