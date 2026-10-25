/* SPDX-License-Identifier: BSD-2-Clause */
#include "local-frontend.h"
/* Generated in the private host build from verified proposal fixtures. */
#include "local-text.h"
enum ar_front_action ar_front_run(struct ar_front_state *state,
                                  const unsigned char *carrier, size_t size,
                                  uint32_t generation,
                                  const struct ar_front_ops *ops, void *context)
{
    if (!state || state->started)
        return AF_FAILED;
    state->started = 1;
    state->selection = AR_INVALID_STARTUP;
    if (!ops || !ops->admit || !ops->output.write || !ops->output.close ||
        (generation != 1 && generation != 2))
        return AF_FAILED;
    struct ar_startup startup;
    if (!ar_decode(carrier, size, &startup))
        return AF_FAILED;
    state->selection = ar_select(&startup, &state->invocation);
    enum ar_local_kind kind;
    int32_t error = 0;
    if (state->selection == AR_HELP)
        kind = AL_HELP;
    else if (state->selection == AR_VERSION)
        kind = AL_VERSION;
    else if (state->selection == AR_USAGE)
        kind = AL_USAGE;
    else if (state->selection == AR_LAUNCH) {
        unsigned char reply[32] = {0};
        size_t reply_size = 0;
        if (ops->admit(context, &state->invocation, reply, &reply_size) != 1)
            return AF_FAILED;
        state->admission_action =
            ar_admission(reply, reply_size, generation, &state->admission);
        if (state->admission_action == AR_REPLY_ADMITTED) {
            state->action = AF_ADMITTED;
            return state->action;
        }
        if (state->admission_action != AR_REPLY_ERROR)
            return AF_FAILED;
        error = state->admission.error;
        if (error == -2)
            kind = AL_UNAVAILABLE;
        else if (error == -13)
            kind = AL_DENIED;
        else if (error == -16)
            kind = AL_CAPACITY;
        else
            return AF_FAILED;
    } else
        return AF_FAILED;
    struct ar_local_plan plan = {kind, local_text[kind].bytes,
                                 local_text[kind].size, error};
    (void)ar_local_deliver(&state->delivery, &plan, &ops->output, context);
    state->action = AF_LOCAL;
    return state->action;
}
