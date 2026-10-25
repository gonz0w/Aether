/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_LIBC_H
#define AETHER_FD_LIBC_H
#include "fd-startup.h"
#include <fcntl.h>
/* Private negative-errno helpers; no global state or errno mutation. Valid
 * disjoint C strings/buffers and exclusive context borrowing as before. */
int64_t aefd_libc_open(struct aefd_context *, const char *, int);
int64_t aefd_libc_fcntl(struct aefd_context *, int, int, int);
int64_t aefd_libc_io(struct aefd_context *, uint64_t, uint64_t, uintptr_t,
                     uint64_t);
/* Actual optional shell bindings in fd-libc-bindings.c. Never combine with old
 * runtime exporting the same libc symbols/greeting reader. No copy/rebase. */
int64_t aefd_shell_start(void);
int64_t aefd_shell_role(void);
int64_t aefd_shell_finish(struct aefd_finish *);
int64_t aefd_shell_snapshot(unsigned char *, size_t, int);
struct aefd_redirect_result aefd_shell_redirect(int, int);
long __aether_waitpid(int, int *, int);
_Noreturn void __wrap__exit(int);
long __aether_io(unsigned long, unsigned long, unsigned long, unsigned long);
#endif
