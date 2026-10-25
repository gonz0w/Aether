/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include "runner-result.h"
#include <string.h>
#include <unistd.h>
int runner_main(int argc, char **argv);
int __real_native_exchange(unsigned char *, unsigned, unsigned char *);
int __wrap_native_exchange(unsigned char *, unsigned, unsigned char *);
void __real_channel_yield(void);
void __wrap_channel_yield(void);
long __real_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
long __wrap_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
int __real_close(int fd);
int __wrap_close(int fd);
ssize_t __real_read(int fd, void *bytes, size_t count);
ssize_t __wrap_read(int fd, void *bytes, size_t count);
unsigned __real_ar_terminal_exit(const struct ar_reply *, int);
unsigned __wrap_ar_terminal_exit(const struct ar_reply *, int);
static unsigned attempts, yields, launches, input_closes, output_closes, reads,
    policies;
static int synthetic, finished;
static unsigned char collected[32];
static _Noreturn void unexpected(void) { _exit(117); }
long __wrap_channel_raw(unsigned long op, unsigned long grant,
                        unsigned long address, unsigned long size)
{
    if (synthetic && !finished)
        unexpected();
    return __real_channel_raw(op, grant, address, size);
}
void __wrap_channel_yield(void)
{
    if (synthetic && !finished) {
        if (++yields != attempts)
            unexpected();
        return;
    }
    __real_channel_yield();
}
int __wrap_native_exchange(unsigned char *q, unsigned size, unsigned char *r)
{
    if (native_word(q) != 5) {
        if (synthetic &&
            (!finished || (native_word(q) != 1 && native_word(q) != 3)))
            unexpected();
        if (native_word(q) == 4 && ++launches != 1)
            unexpected();
        return __real_native_exchange(q, size, r);
    }
    if (size != 32 || native_word(q + 4) != (0x73000000u | native_generation()))
        unexpected();
    for (unsigned i = 8; i < 32; ++i)
        if (q[i])
            unexpected();
    if (finished || attempts != yields)
        unexpected();
    if (attempts == 100000)
        _exit(115);
    if (!synthetic) {
        for (unsigned turn = 0; turn < 100000; ++turn) {
            struct ar_reply terminal;
            if (!__real_native_exchange(q, size, collected))
                unexpected();
            enum ar_reply_action action =
                ar_collection(collected, 32, native_word(q + 4), &terminal);
            if (action == AR_REPLY_COLLECTED) {
                if (terminal.kind != 1 || terminal.detail != 0 ||
                    terminal.error)
                    unexpected();
                synthetic = 1;
                break;
            }
            if (action != AR_REPLY_PENDING)
                unexpected();
            __real_channel_yield();
        }
        if (!synthetic)
            unexpected();
    }
    ++attempts;
#ifdef BUDGET_LAST
    if (attempts == 100000) {
        memcpy(r, collected, 32);
        finished = 1;
        return 1;
    }
#endif
    memset(r, 0, 32);
    native_put(r, 0xfffffff5u);
    return 1;
}
int __wrap_close(int fd)
{
    if (fd == 3 && !synthetic && ++input_closes == 1)
        return __real_close(fd);
    if (fd == 4 && finished && ++output_closes == 1)
        return __real_close(fd);
    unexpected();
    return -1;
}
ssize_t __wrap_read(int fd, void *bytes, size_t count)
{
    if (fd != 4 || !finished || ++reads != 1)
        unexpected();
    return __real_read(fd, bytes, count);
}
unsigned __wrap_ar_terminal_exit(const struct ar_reply *reply, int complete)
{
    if (!finished || ++policies != 1 || complete != 1 || reply->error ||
        reply->receipt != (0x73000000u | native_generation()) ||
        reply->kind != 1 || reply->detail != 0)
        unexpected();
    return __real_ar_terminal_exit(reply, complete);
}
int main(int argc, char **argv)
{
    int result = runner_main(argc, argv);
    if (!synthetic || launches != 1 || input_closes != 1)
        unexpected();
#ifdef BUDGET_SHORT
    if (result != 1 || attempts != 99999 || yields != 99999 || finished ||
        reads || output_closes || policies)
        unexpected();
    return 116;
#elif defined(BUDGET_LAST)
    if (result != 0 || attempts != 100000 || yields != 99999 || !finished ||
        reads != 1 || output_closes != 1 || policies != 1)
        unexpected();
    return 0;
#else
    if (result != 1 || attempts != 100000 || yields != 100000 || finished ||
        reads || output_closes || policies)
        unexpected();
    return 114;
#endif
}
