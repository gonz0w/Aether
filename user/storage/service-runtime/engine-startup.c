/* SPDX-License-Identifier: BSD-2-Clause */
/* Private engine candidate. The initial thread serializes this lifecycle.
 * Engine/provider failures terminate the owner; supervision/reclaim remain
 * outside this entry point. A failed finish never certifies clean retirement.
 */
#include "runtime.h"
#include "startup-fixture.h"
#if defined(ENGINE_SPA_PHYSICAL) || defined(ENGINE_POOL)
#include <sys/auxv.h>
#endif

extern void kernel_init(int);
extern void kernel_fini(void);
#ifdef ENGINE_ZPL_WRITE
#if !defined(ENGINE_POOL_IMPORT) || !defined(ENGINE_WRITE_MODE)
#error "ZPL writer requires explicit writable import engine"
#endif
extern void aether_zpl_accounting_init(void);
#endif
static _Thread_local volatile unsigned tls_marker = 17;
#ifdef ENGINE_VOLUME
extern int aether_volume_start_probe(void);
extern int aether_volume_engine_probe(int, int);
extern int aether_volume_finish_probe(void);
#ifdef ENGINE_UTC
#include <stdint.h>
extern int aether_engine_utc_start(int, int);
extern int aether_engine_utc_probe(int64_t);
extern int aether_engine_utc_finish(void);
#ifdef ENGINE_POOL
extern int aether_pool_prepare(void);
extern int aether_spa_pool_probe(void);
#ifdef ENGINE_POOL_IMPORT
extern int aether_spa_import_probe(void);
#endif
#endif
#ifdef ENGINE_SPA_PHYSICAL
extern int aether_spa_physical_probe(int, int, int);
#endif
#ifdef ENGINE_SPA_ACTIVE
extern int aether_spa_active_probe(int, int);
#endif
#endif
#ifdef ENGINE_SPA_UTC
extern int aether_volume_spa_utc_probe(int);
#endif
#ifdef ENGINE_VOLUME_WORKERS
extern int aether_volume_workers_probe(int, int);
extern int aether_volume_workers_finish(void);
#endif
#endif
#ifdef ENGINE_NATIVE
#include "engine-observe.inc"
#else
#define engine_observe(phase) ((void)0)
#define engine_finish() aether_runtime_finish()
#endif

#ifdef ENGINE_UTC
void aether_engine_utc_phase(unsigned char phase) { engine_observe(phase); }
#ifdef ENGINE_SPA_PHYSICAL
void aether_physical_io_phase(unsigned char phase) { engine_observe(phase); }
#endif
#endif

#ifdef ENGINE_POOL_INTERRUPT
#if !defined(ENGINE_POOL) || !defined(ENGINE_UTC) || !defined(ENGINE_NATIVE)
#error "pool checkpoint requires the native UTC pool profile"
#endif
#include "pool-checkpoint.inc"
#endif

int main(void)
{
    if (tls_marker != 17)
        return 223;
    if (aether_runtime_init() || aether_runtime_live() != 1 ||
        aether_runtime_admissions() != 1)
        return 222;
    if (aether_zfs_startup_bind(&startup_fixture))
        return 226;
#ifdef ENGINE_VOLUME
    int volume_status = aether_volume_start_probe();
    if (volume_status)
        return volume_status;
#endif
#if defined(ENGINE_SPA_PHYSICAL) || defined(ENGINE_POOL)
    if (getauxval(0xa001) != 0x50000101UL) {
        /* Replacements have no storage authority and start no engine helpers.
         * Actual bind/open denial precedes clean runtime retirement. */
        engine_observe('B');
#ifdef ENGINE_POOL
#ifdef ENGINE_POOL_IMPORT
        int denied = aether_spa_import_probe();
#else
        int denied = aether_spa_pool_probe();
#endif
#else
        int denied = aether_spa_physical_probe(0, 0, 0);
#endif
        if (denied)
            return denied;
        if (engine_finish())
            return 224;
        if (aether_runtime_live() || aether_runtime_admissions() != 1)
            return 225;
        engine_observe('R');
        return tls_marker == 17 ? 0 : 223;
    }
#endif
#ifdef ENGINE_UTC
    int utc_status = aether_engine_utc_start(UTC_POLICY, UTC_DISABLED);
    if (utc_status)
        return utc_status;
#endif
#if defined(ENGINE_POOL) && !defined(ENGINE_POOL_IMPORT)
    if (aether_pool_prepare())
        return 872;
#endif
    engine_observe('B');
#ifdef ENGINE_WRITE_MODE
    kernel_init(
        3); /* Actual SPA_MODE_READ | SPA_MODE_WRITE, separately qualified. */
#else
    kernel_init(1); /* Actual SPA_MODE_READ. */
#endif
#ifdef ENGINE_ZPL_WRITE
    aether_zpl_accounting_init();
    if (aether_pool_prepare())
        return 873;
#endif
    engine_observe('I');
#ifdef ENGINE_VOLUME
#if !defined(ENGINE_SPA_PHYSICAL) && !defined(ENGINE_POOL)
    volume_status = aether_volume_engine_probe(BLOCK_VERIFY, BLOCK_READONLY);
    if (volume_status)
        return volume_status;
#endif
#ifdef ENGINE_VOLUME_WORKERS
    volume_status = aether_volume_workers_probe(BLOCK_READONLY, WORKERS_INLINE);
    if (volume_status)
        return volume_status;
#endif
#endif
#ifdef ENGINE_SPA_UTC
    volume_status = aether_volume_spa_utc_probe(UTC_SKIP_OBSERVER);
    if (volume_status)
        return volume_status;
#endif
#ifdef ENGINE_UTC
    for (unsigned cycle = 0; cycle < UTC_CYCLES; ++cycle) {
        utc_status = aether_engine_utc_probe(UTC_SECONDS);
        if (utc_status)
            return utc_status;
    }
#endif
#ifdef ENGINE_SPA_ACTIVE
    utc_status =
        aether_spa_active_probe(SPA_SKIP_ACTIVATION, SPA_SKIP_CALLBACK);
    if (utc_status)
        return utc_status;
#endif
#ifdef ENGINE_POOL
#ifdef ENGINE_POOL_IMPORT
    utc_status = aether_spa_import_probe();
#else
    utc_status = aether_spa_pool_probe();
#endif
    if (utc_status)
        return utc_status;
#endif
#ifdef ENGINE_SPA_PHYSICAL
    utc_status = aether_spa_physical_probe(
        SPA_PHYSICAL_SMALL, SPA_PHYSICAL_SKIP_CALLBACK, SPA_PHYSICAL_REVOKED);
    if (utc_status)
        return utc_status;
#endif
#ifndef ENGINE_SKIP_FINI
    kernel_fini();
#endif
#if defined(ENGINE_SPA_PHYSICAL)
    if (!SPA_PHYSICAL_REVOKED) {
        /* Keep the healthy provider live until every engine consumer stops. */
        volume_status = aether_volume_finish_probe();
        if (volume_status)
            return volume_status;
    }
#elif defined(ENGINE_VOLUME)
#ifdef ENGINE_VOLUME_WORKERS
    volume_status = aether_volume_workers_finish();
#else
    volume_status = aether_volume_finish_probe();
#endif
    if (volume_status)
        return volume_status;
#endif
#ifdef ENGINE_UTC
    engine_observe('J');
    utc_status = aether_engine_utc_finish();
    if (utc_status)
        return utc_status;
#endif
    engine_observe('F');
#ifndef ENGINE_SKIP_FINISH
    if (engine_finish())
        return 224;
#endif
    if (aether_runtime_live() || !aether_runtime_admissions() ||
        aether_runtime_admissions() > 512)
        return 225;
    engine_observe('R');
    return tls_marker == 17 ? 0 : 223;
}
