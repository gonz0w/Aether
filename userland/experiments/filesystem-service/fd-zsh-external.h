/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_ZSH_EXTERNAL_H
#define AETHER_FD_ZSH_EXTERNAL_H
#include <sys/uio.h>
/* Private current-Zsh entry/scoped stdio adapter. At most two readable iovecs;
 * returns libc -1/errno or at most16 accepted source bytes. */
long aether_zsh_vector_write(int, const struct iovec *, int);
int __wrap_main(int, char **);
#endif
