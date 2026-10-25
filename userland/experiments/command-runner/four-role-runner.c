/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
#include "runner-result.h"
#include "../native-channel/channel.h"
#include <errno.h>
#include <string.h>
#include <unistd.h>
int main(int argc, char **argv)
{
    struct ar_startup startup;
    struct ar_invocation invocation;
    struct ar_reply admitted, terminal;
    unsigned char q[384] = {0}, r[32];
    if (argc != 1 || strcmp(argv[0], "client") ||
        !native_runner_bootstrap(&startup) ||
        ar_select(&startup, &invocation) != AR_LAUNCH)
        return 110;
    memset(&startup, 0xa5, sizeof startup);
    native_put(q, 4);
    native_put(q + 4, 1);
    native_put(q + 8, invocation.count);
    native_put(q + 12, 1);
    native_put(q + 16, 2);
    memcpy(q + 32, invocation.args[0], 32);
    for (unsigned i = 0; i < 2; ++i) {
        unsigned at = 64 + i * 32;
        native_put(q + at, native_ref(i));
        native_put(q + at + 4, i + 3);
        native_put(q + at + 8, i);
        native_put(q + at + 12, i ? 2 : 1);
    }
    for (unsigned i = 0; i < invocation.count; ++i)
        memcpy(q + 128 + i * 32, invocation.args[i], 32);
    memcpy(q + 128 + invocation.count * 32, invocation.environment, 32);
    if (!native_exchange(q, sizeof q, r) ||
        ar_admission(r, sizeof r, native_generation(), &admitted) !=
            AR_REPLY_ADMITTED)
        return 1;
    memset(q, 0xa5, sizeof q);
    int complete = close(3) == 0;
    enum ar_reply_action action = AR_REPLY_PENDING;
    for (unsigned turn = 0; turn < 100000 && action == AR_REPLY_PENDING;
         ++turn) {
        memset(q, 0, 32);
        native_put(q, 5);
        native_put(q + 4, admitted.receipt);
        if (!native_exchange(q, 32, r))
            return 1;
        action = ar_collection(r, sizeof r, admitted.receipt, &terminal);
        if (action == AR_REPLY_PENDING)
            channel_yield();
    }
    if (action != AR_REPLY_COLLECTED)
        return 1;
    memset(q, 0, 32);
    native_put(q, 5);
    native_put(q + 4, admitted.receipt);
    if (!native_exchange(q, 32, r) || (int)native_word(r) != -ECHILD)
        return 1;
    for (unsigned i = 4; i < 32; ++i)
        if (r[i])
            return 1;
    char byte;
    if (read(4, &byte, 1) != 0)
        complete = 0;
    for (int fd = 4; fd >= 1; --fd)
        if (fd != 3 && close(fd))
            complete = 0;
    return (int)ar_terminal_exit(&terminal, complete);
}
