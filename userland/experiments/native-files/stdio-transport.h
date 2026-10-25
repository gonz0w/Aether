/* SPDX-License-Identifier: BSD-2-Clause */
#include <sys/uio.h>
#include <sys/types.h>
ssize_t aether_readv(int,const struct iovec *,int);
ssize_t aether_writev(int,const struct iovec *,int);
off_t aether_stdio_seek(int,off_t,int);
