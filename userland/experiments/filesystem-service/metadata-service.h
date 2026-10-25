/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_METADATA_SERVICE_H
#define AETHER_FS_METADATA_SERVICE_H
#include "native-service.h"
/* Separate AF07 entry; same trusted nine arguments and72-byte result. Adds
 * METADATA16 authority and opcode12 on a retained token. Success word5=112 then
 * two zero-padded64-byte frames, explicit LE raw labels/signed-second values;
 * never C object/generation/parent identities, credentials or POSIX authority.
 * The original metadata engine replaces the directory provider; do not link
 * both. All SPA/UTC/import/endpoint/drain/export obligations remain unchanged.
 */
int aether_fs_metadata_run(void *, const unsigned char *, size_t, uint64_t,
                           uint64_t, uint64_t, uint64_t, uint64_t,
                           struct aether_fs_service_result *);
#endif
