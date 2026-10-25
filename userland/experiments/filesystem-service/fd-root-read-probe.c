/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed immutable diagnostic body; not a general shell or executable loader. */
#include <fcntl.h>
#include <unistd.h>
int main(int, char **);
int main(int argc, char **argv)
{
    (void)argv;
    if (argc != 2)
        return 80;
    int fd = open("/zstd", O_RDONLY | O_CLOEXEC);
    if (fd < 0)
        return 81;
#ifdef AEFD_DUP2_WIRE
    int result = 0, alias10 = 0, alias0 = 0;
    if (fcntl(fd, F_GETFD) != FD_CLOEXEC || dup2(fd, fd) != fd ||
        fcntl(fd, F_GETFD) != FD_CLOEXEC)
        result = 87;
    if (!result) {
        if (dup2(fd, 10) != 10)
            result = 88;
        else
            alias10 = 1;
    }
    if (!result && dup2(10, fd) != fd)
        result = 89;
    if (!result && fcntl(fd, F_GETFD) != 0)
        result = 87;
    if (!result) {
        if (dup2(fd, 0) != 0)
            result = 90;
        else
            alias0 = 1;
    }
    unsigned char bytes[16];
    if (!result && read(0, bytes, sizeof bytes) != (ssize_t)sizeof bytes)
        result = 82;
    if (!result && lseek(fd, 0, SEEK_END) != 780248)
        result = 83;
    if (!result &&
        (read(10, bytes, sizeof bytes) != 0 || read(fd, bytes, 1) != 0))
        result = 84;
    if (alias10 && close(10) && !result)
        result = 85;
    if (alias0 && close(0) && !result)
        result = 85;
    if (close(fd) && !result)
        result = 85;
#else
    unsigned char bytes[16];
    int result =
        read(fd, bytes, sizeof bytes) != (ssize_t)sizeof bytes ? 82 : 0;
    if (!result && lseek(fd, 0, SEEK_END) != 780248)
        result = 83;
    if (!result &&
        (read(fd, bytes, sizeof bytes) != 0 || read(fd, bytes, 1) != 0))
        result = 84;
    if (close(fd) && !result)
        result = 85;
#endif
    if (result)
        return result;
    return write(1, "AF07-READ:ok\n", 13) == 13 ? 7 : 86;
}
