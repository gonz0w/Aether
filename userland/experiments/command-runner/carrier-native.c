/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include <errno.h>
#include <string.h>
#include <sys/auxv.h>
#include <unistd.h>
long __real_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
long __wrap_channel_raw(unsigned long, unsigned long, unsigned long,
                        unsigned long);
unsigned long __real_getauxval(unsigned long key);
unsigned long __wrap_getauxval(unsigned long key);
static unsigned calls, aux_calls, received, injections;
static unsigned char *record;
static struct ar_startup output, before;
unsigned long __wrap_getauxval(unsigned long key)
{
    ++aux_calls;
    return __real_getauxval(key);
}
long __wrap_channel_raw(unsigned long op, unsigned long grant,
                        unsigned long address, unsigned long size)
{
    ++calls;
    if (memcmp(&output, &before, sizeof output) || native_ref(0) ||
        native_ref(1))
        _exit(112);
#ifdef CARRIER_PREFIX
    if (op == 0x24001) {
        if (received == CARRIER_PREFIX) {
            ++injections;
            return 0;
        }
        if (size > CARRIER_PREFIX - received)
            size = CARRIER_PREFIX - received;
    }
#endif
    long result = __real_channel_raw(op, grant, address, size);
    if (op == 0x24001 && result > 0 && (unsigned long)result <= size) {
        unsigned base = received < AR_CARRIER_SIZE ? 0u : AR_CARRIER_SIZE;
        if (received == base)
            record = (unsigned char *)address;
        if ((unsigned char *)address != record + (received - base) ||
            (unsigned long)result >
                (base ? 32u : AR_CARRIER_SIZE) - (received - base))
            _exit(113);
        received += (unsigned)result;
        if (received == AR_CARRIER_SIZE) {
            struct ar_startup decoded;
            if (!ar_decode(record, AR_CARRIER_SIZE, &decoded))
                _exit(113);
#ifdef CARRIER_FIELD
            if (CARRIER_FIELD < AR_CARRIER_SIZE) {
                record[CARRIER_FIELD] ^= 0x80;
                ++injections;
            }
#endif
        }
        if (received == AR_CARRIER_SIZE + 32) {
            if (native_word(record) || native_word(record + 28))
                _exit(113);
            for (unsigned i = 0; i < 2; ++i) {
                if (native_word(record + 4 + i * 12) !=
                        (0x71000001u | (i << 16)) ||
                    native_word(record + 8 + i * 12) != 3 + i ||
                    native_word(record + 12 + i * 12) != (i ? 3u : 1u))
                    _exit(113);
            }
#ifdef CARRIER_FIELD
            if (CARRIER_FIELD >= AR_CARRIER_SIZE) {
                record[CARRIER_FIELD - AR_CARRIER_SIZE] ^= 0x80;
                ++injections;
            }
#endif
        }
    }
    return result;
}
int main(void)
{
    memset(&output, 0xa5, sizeof output);
    memcpy(&before, &output, sizeof before);
    if (native_runner_bootstrap(&output))
        return 113;
    if (memcmp(&output, &before, sizeof output) || native_ref(0) ||
        native_ref(1))
        return 112;
    if (injections != 1)
        return 113;
    unsigned saved_calls = calls, saved_aux = aux_calls;
    unsigned char byte = 0xa5;
    for (int fd = 0; fd < 5; ++fd) {
        errno = 0;
        if (read(fd, &byte, 1) != -1 || errno != EBADF || byte != 0xa5)
            return 113;
        errno = 0;
        if (write(fd, "X", 1) != -1 || errno != EBADF)
            return 113;
        errno = 0;
        if (close(fd) != -1 || errno != EBADF)
            return 113;
    }
    if (native_runner_bootstrap(&output) || native_bootstrap(0) ||
        native_bootstrap(1))
        return 113;
    unsigned char q[384] = {4}, reply[32];
    if (native_exchange(q, sizeof q, reply) || calls != saved_calls ||
        aux_calls != saved_aux || memcmp(&output, &before, sizeof output))
        return 113;
    return 111;
}
