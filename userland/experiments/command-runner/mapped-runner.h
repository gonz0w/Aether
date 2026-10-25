/* SPDX-License-Identifier: BSD-2-Clause */
/* Opt-in completed-child path. Unknown outcomes abort this bounded experiment;
 * this function is not an unattended recovery implementation. */
#include "runner-result.h"
static int mapped_run(void)
{
    unsigned char q[384], r[32];
    struct ar_reply admitted, terminal;
    request(q);
    if (!native_exchange(q, sizeof q, r) ||
        ar_admission(r, sizeof r, native_generation(), &admitted) !=
            AR_REPLY_ADMITTED)
        return 1;
    memset(q, 0xa5, sizeof q);
    int input_closed = close(3) == 0;
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
    memset(r, 0xcc, sizeof r);
    char bytes[23];
    int at_eof = read(4, bytes, sizeof bytes) == 0;
    int output_closed = close(4) == 0;
    int cleanup_complete = input_closed && at_eof && output_closed;
#ifdef MAPPED_IGNORE_KIND
    return cleanup_complete ? (int)terminal.detail : 1;
#elif defined(MAPPED_FORCE_ZERO)
    return cleanup_complete ? 0 : 1;
#else
    return (int)ar_terminal_exit(&terminal, cleanup_complete);
#endif
}
