/* SPDX-License-Identifier: BSD-2-Clause */
/* Appended to the pinned CDDL translation unit; does not relicense that unit. */
void aether_taskq_tsd_init(void)
{
    VERIFY0(pthread_key_create(&taskq_tsd, NULL));
}
void aether_taskq_tsd_fini(void)
{
    VERIFY0(pthread_key_delete(taskq_tsd));
}
