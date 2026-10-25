/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include "runner-result.h"
#include <unistd.h>
int runner_main(int argc, char **argv);
long __real_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
long __wrap_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
int __real_native_exchange(unsigned char *, unsigned, unsigned char *);
int __wrap_native_exchange(unsigned char *, unsigned, unsigned char *);
int __real_close(int fd);
int __wrap_close(int fd);
ssize_t __real_read(int fd, void *bytes, size_t count);
ssize_t __wrap_read(int fd, void *bytes, size_t count);
unsigned __wrap_ar_terminal_exit(const struct ar_reply *reply, int complete);
static int active, forbidden;
static unsigned used, injections, input_closes;
static unsigned char *record;
static void guard(void)
{
    if (forbidden)
        _exit(109);
}
long __wrap_channel_raw(unsigned long op, unsigned long grant,
                        unsigned long address, unsigned long size)
{
    guard();
    long result = __real_channel_raw(op, grant, address, size);
    if (active && op == 0x24001 && result > 0 &&
        (unsigned long)result <= size) {
        if (!used)
            record = (unsigned char *)address;
        if ((unsigned char *)address != record + used ||
            (unsigned long)result > 32u - used)
            _exit(110);
        used += (unsigned)result;
        if (used == 32) {
            used = 0;
            if (native_word(record) == 0) {
                if (native_word(record + 4) !=
                        (0x73000000u | native_generation()) ||
                    native_word(record + 8) ||
                    native_word(record + 12) != (UNCERTAIN_OP == 5 ? 1u : 0u))
                    _exit(110);
                for (unsigned i = 16; i < 32; ++i)
                    if (record[i])
                        _exit(110);
                if (injections++)
                    _exit(110);
                forbidden = 1;
#ifdef UNCERTAIN_PADDING
                record[31] = 1;
#elif defined(UNCERTAIN_RECEIPT)
                record[4] ^= 8;
#else
                return 0;
#endif
            }
        }
    }
    return result;
}
int __wrap_native_exchange(unsigned char *q, unsigned size,
                           unsigned char *reply)
{
    guard();
    active = native_word(q) == UNCERTAIN_OP;
    used = 0;
    int result = __real_native_exchange(q, size, reply);
    active = 0;
    return result;
}
int __wrap_close(int fd)
{
    guard();
    if (fd != 3 || input_closes++)
        _exit(110);
    return __real_close(fd);
}
ssize_t __wrap_read(int fd, void *bytes, size_t count)
{
    guard();
    (void)fd;
    (void)bytes;
    (void)count;
    _exit(110);
}
unsigned __wrap_ar_terminal_exit(const struct ar_reply *reply, int complete)
{
    guard();
    (void)reply;
    (void)complete;
    _exit(110);
}
int main(int argc, char **argv)
{
    int result = runner_main(argc, argv);
    if (result != 1 || injections != 1 || used || !forbidden ||
        input_closes != (UNCERTAIN_OP == 5 ? 1u : 0u))
        return 110;
    return UNCERTAIN_OP == 5 ? 102 : 101;
}
