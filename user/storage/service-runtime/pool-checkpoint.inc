/* SPDX-License-Identifier: BSD-2-Clause */
/* Private after-sync checkpoint. Ordered I/O was checked by the caller;
 * retain engine/provider memory until confirmed host VM teardown. */
int aether_engine_pool_checkpoint(void)
{
    engine_observe('K');
    for (;;) {
        struct timespec pause = {0, 1000000};
        if (nanosleep(&pause, NULL))
            return 872;
    }
}

#ifdef ENGINE_POOL_UNCOMMITTED
int aether_engine_pool_uncommitted(uint64_t candidate)
{
    engine_observe('H');
    for (unsigned i = 0; i < 8; ++i)
        engine_observe((candidate >> (8 * i)) & 255);
    return aether_engine_pool_checkpoint();
}
#endif
