/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed root-CWD check before the existing full-file/dup2 diagnostic. */
#include <errno.h>
#include <string.h>
#include <unistd.h>
#ifdef AEFD_CWD_PROBE_HOST_TEST
int aefd_cwd_read_files(int, char **);
#else
#define main aefd_cwd_read_files
#include "fd-root-read-probe.c"
#undef main
#endif
int main(int, char **);
int main(int argc, char **argv)
{
    if (argc != 2)
        return 80;
    char path[256];
    if (getcwd(path, sizeof(path)) != path || strcmp(path, "/"))
        return 91;
    if (chdir("/./../"))
        return 92;
    errno = 0;
    if (chdir("/zstd/..") != -1 || errno != ENOTDIR)
        return 93;
    if (getcwd(path, sizeof(path)) != path || strcmp(path, "/"))
        return 94;
    return aefd_cwd_read_files(argc, argv);
}
