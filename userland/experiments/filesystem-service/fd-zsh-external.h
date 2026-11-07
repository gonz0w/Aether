/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_ZSH_EXTERNAL_H
#define AETHER_FD_ZSH_EXTERNAL_H
#ifdef AEFD_ZSH_PROCESS_BINDINGS
#include "fd-protocol.h"
#endif
#include <sys/types.h>
#include <sys/uio.h>
/* Private current-Zsh entry/scoped stdio adapter. At most two readable iovecs;
 * returns libc -1/errno or at most16 accepted source bytes. */
long aether_zsh_vector_write(int, const struct iovec *, int);
/* Scoped pinned-musl consumers, not a public readv implementation. Read one
 * prefix of the first nonempty iovec, at most4096 bytes; validate both spans
 * before effects. All spans must be outside the stable descriptor context.
 * These four calls return libc -1/errno; successful calls preserve errno. */
int aether_zsh_open(const char *, int, mode_t);
#ifdef AEFD_ZSH_HOME_REDIRECTION_BINDINGS
mode_t aether_zsh_umask(mode_t);
#endif
long aether_zsh_vector_read(int, const struct iovec *, int);
long aether_zsh_read(int, void *, size_t);
off_t aether_zsh_seek(int, off_t, int);
/* fopen's internal cleanup/status calls require raw negative errno and must
 * not change libc errno (including a failed fdopen allocation's errno). */
long aether_zsh_raw_fcntl(int, int, int);
long aether_zsh_raw_close(int);
#ifdef AEFD_ZSH_FILESYSTEM_BINDINGS
struct aether_tinfo_directory_view;
int aether_zsh_directory_probe(const char *,
                               struct aether_tinfo_directory_view *);
uid_t __wrap_getuid(void);
uid_t __wrap_geteuid(void);
gid_t __wrap_getgid(void);
gid_t __wrap_getegid(void);
int __wrap_access(const char *, int);
char *__wrap_getcwd(char *, size_t);
#ifdef AEFD_ZSH_HOME_CWD_BINDINGS
int __wrap_chdir(const char *);
#endif
#endif
#ifdef AEFD_ZSH_DIAGNOSTIC
#ifndef AEFD_ZSH_FILESYSTEM_BINDINGS
#error "Zsh diagnostic requires the closed filesystem selection"
#endif
/* Diagnostic observation only: real tgetent and actual active TTY input.
 * Preserve delegated results. Qualify only requested zero exit status. */
int __wrap_tgetent(char *, const char *);
int aether_zsh_diagnostic_status(int);
#endif
#ifdef AEFD_ZSH_PROCESS_BINDINGS
/* Single selected aggregate supplies parent, copied child and fresh helper. */
int64_t aefd_zsh_admit(void);
int aefd_zsh_tls_valid(void);
#endif
int __wrap_main(int, char **);
#endif
