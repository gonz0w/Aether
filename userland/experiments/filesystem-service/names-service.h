/* SPDX-License-Identifier: BSD-2-Clause */
/* Private imported-root readiness; ready result remains greeting completion.
 * The supervisor separately checks exact retained instance live+ready state. */
#ifndef AETHER_FS_NAMES_SERVICE_H
#define AETHER_FS_NAMES_SERVICE_H
#include "native-service.h"
/* Trusted importer: base SPA/endpoint/pointer/serialization obligations apply.
 * Explicit uid/gid<=INT32_MAX are trusted labels. Private AFSRPC05 uses
 * checked cumulative mutation/request counters, never reset/wrapped. Native
 * qualification is exactly9 mutations/96 requests; old profiles stay fixed.
 * Length-checked typed success-only retirements consume old contexts before
 * reopen/next reply. Root aliases refresh, file aliases survive rename; live
 * aliases deny remove. Failed/unknown outcomes retire permanently, never
 * reset/replay. stop0 means explicit disconnect, return0 additionally requires
 * both closes. No operational readiness, public durability, arbitrary staging
 * or restart authorization. */
/* Named requests use complete padded64-byte bodies: components1..255,
 * rename combined<=510. Header inline bytes zero; all bodies before effects.
 * Data<=4096 and every other authority/resource/time/cleanup limit unchanged.
 */
/* Exact private AENBD004/ABI26 primary-only readiness transport required.
 * On EAGAIN wait on the same holder; helpers remain schedulable. Negative
 * wait errors terminate framing without replay; all base limits unchanged. */
int aether_fs_names_run(void *spa, const unsigned char *dataset, size_t length,
                        uint64_t reader, uint64_t writer, uint64_t rights,
                        uint64_t uid, uint64_t gid,
                        struct aether_fs_service_result *result);
#endif
