/* SPDX-License-Identifier: BSD-2-Clause */
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    static const char bytes[] = "AETHER-ZSH-HOME\n";
    if (argc != 2 || strcmp(argv[0], "/inputs/helper") ||
        strcmp(argv[1], "home-write"))
        return 64;
    int fd = open("/home/probe", O_WRONLY);
    if (fd < 0)
        return 65;
    ssize_t count = write(fd, bytes, sizeof bytes - 1);
    int closed = close(fd);
    return count == 16 && closed == 0 ? 0 : 66;
}
