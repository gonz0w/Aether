/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_USERLAND_CHANNEL_H
#define AETHER_USERLAND_CHANNEL_H
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>
/* One explicitly transferred endpoint; this is not a POSIX descriptor. */
long channel_raw(unsigned long op,unsigned long grant,unsigned long address,unsigned long length);
unsigned long channel_grant(void);
ssize_t channel_read(unsigned long grant,void *buffer,size_t length);
ssize_t channel_write(unsigned long grant,const void *buffer,size_t length);
void channel_yield(void);
#endif
