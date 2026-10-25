/* SPDX-License-Identifier: BSD-2-Clause */
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
int aefd_cwd_read_probe(int, char **);
int aefd_cwd_read_files(int, char **);
char *aefd_probe_getcwd(char *, size_t);
int aefd_probe_chdir(const char *);
static unsigned mode, path_calls, changes, files;
char *aefd_probe_getcwd(char *out, size_t length)
{
    assert(out && length == 256);
    ++path_calls;
    if ((mode == 1 && path_calls == 1) || (mode == 6 && path_calls == 2))
        return NULL;
    strcpy(out,
           ((mode == 2 && path_calls == 1) || (mode == 7 && path_calls == 2))
               ? "/wrong"
               : "/");
    return out;
}
int aefd_probe_chdir(const char *path)
{
    ++changes;
    if (changes == 1) {
        assert(!strcmp(path, "/./../"));
        return mode == 3 ? -1 : 0;
    }
    assert(changes == 2 && !strcmp(path, "/zstd/.."));
    errno = mode == 5 ? ENOENT : ENOTDIR;
    return mode == 4 ? 0 : -1;
}
int aefd_cwd_read_files(int argc, char **argv)
{
    assert(argc == 2 && !argv && path_calls == 2 && changes == 2);
    ++files;
    return mode == 8 ? 81 : 7;
}
int main(void)
{
    const int expected[] = {7, 91, 91, 92, 93, 93, 94, 94, 81, 80};
    for (mode = 0; mode < 10; ++mode) {
        path_calls = changes = files = 0;
        assert(aefd_cwd_read_probe(mode == 9 ? 1 : 2, NULL) == expected[mode]);
        assert(files == (mode == 0 || mode == 8));
    }
    puts("10 fixed physical CWD probe outcomes pass");
    return 0;
}
