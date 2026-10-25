/* SPDX-License-Identifier: BSD-2-Clause */
/* No native transport, fixture data, or shell parsing in the command itself. */
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static int finish(int status)
{
    /* Each descriptor is closed once. Never retry an uncertain close. */
    if (close(STDIN_FILENO) < 0 && !status)
        status = 1;
    if (close(STDOUT_FILENO) < 0 && !status)
        status = 1;
    if (status == 1) {
        const char message[] = "bytecount: I/O failure\n";
        (void)write(STDERR_FILENO, message, sizeof message - 1);
    }
    return status;
}
static int emit(const char *bytes, size_t count)
{
    while (count) {
        ssize_t n = write(STDOUT_FILENO, bytes, count);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0 || (size_t)n > count)
            return 1;
        bytes += n;
        count -= (size_t)n;
    }
    return 0;
}
int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "--help")) {
        const char help[] =
            "Count bytes from standard input.\nUsage: bytecount "
            "--decimal\nOptions: --decimal, --help, --version\nExample: "
            "bytecount --decimal < input\nCounting requires LC_ALL=C and "
            "readable stdin/writable stdout.\n";
        return finish(emit(help, sizeof help - 1));
    }
    if (argc == 2 && !strcmp(argv[1], "--version"))
        return finish(emit("bytecount 0.1\n", 14));
    const char *locale = getenv("LC_ALL");
    if (argc != 2 || strcmp(argv[1], "--decimal") || !locale ||
        strcmp(locale, "C")) {
        const char message[] = "bytecount: expected --decimal and LC_ALL=C\n";
        (void)write(STDERR_FILENO, message, sizeof message - 1);
        return finish(64);
    }
    uint64_t total = 0;
    unsigned char input[37];
    for (;;) {
        ssize_t n = read(STDIN_FILENO, input, sizeof input);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return finish(1);
        }
        if (!n)
            break;
        if ((size_t)n > sizeof input || (uint64_t)n > UINT64_MAX - total)
            return finish(1);
        total += (uint64_t)n;
    }
    char output[21];
    unsigned start = sizeof output;
    output[--start] = '\n';
    do {
        output[--start] = (char)('0' + total % 10);
        total /= 10;
    } while (total);
    while (start < sizeof output) {
        size_t remaining = sizeof output - start;
        ssize_t n = write(STDOUT_FILENO, output + start, remaining);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0 || (size_t)n > remaining)
            return finish(1);
        start += (unsigned)n;
    }
    return finish(0);
}
