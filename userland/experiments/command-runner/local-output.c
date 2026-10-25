/* SPDX-License-Identifier: BSD-2-Clause */
#include "local-output.h"
static int valid(struct ar_local_io result, size_t bound)
{
    return result.known == 1 && result.error <= 0 && result.error >= -4095 &&
           result.count <= bound && (!result.error || !result.count);
}
unsigned ar_local_deliver(struct ar_local_state *state,
                          const struct ar_local_plan *plan,
                          const struct ar_local_ops *ops, void *context)
{
    if (!state || state->started)
        return 1;
    state->started = 1;
    state->exit_status = 1;
    state->failure = AL_INVALID;
    if (!plan || !ops || !ops->write || !ops->close || !plan->text ||
        !plan->size || plan->size > 512 || plan->kind < AL_HELP ||
        plan->kind > AL_CAPACITY)
        return 1;
    int32_t expected = plan->kind == AL_UNAVAILABLE ? -2
                       : plan->kind == AL_DENIED    ? -13
                       : plan->kind == AL_CAPACITY  ? -16
                                                    : 0;
    state->kind = plan->kind;
    state->admission_error = plan->admission_error;
    state->intended_exit = plan->kind <= AL_VERSION ? 0u
                           : plan->kind == AL_USAGE ? 64u
                                                    : 2u;
    if (plan->admission_error != expected)
        return 1;
    unsigned sink = plan->kind <= AL_VERSION ? 0u : 1u;
    state->failure = AL_NONE;
    while (state->delivered < plan->size) {
        size_t remaining = plan->size - state->delivered;
        struct ar_local_io reply =
            ops->write(context, sink, plan->text + state->delivered, remaining);
        state->write_error = reply.error;
        if (!valid(reply, remaining)) {
            state->failure = AL_UNKNOWN;
            return 1;
        }
        if (reply.error || !reply.count) {
            state->failure = reply.error ? AL_WRITE_ERROR : AL_ZERO;
            break;
        }
        state->delivered += reply.count;
    }
    for (unsigned sink_index = 0; sink_index < 2; ++sink_index) {
        struct ar_local_io reply = ops->close(context, sink_index);
        state->close_error[sink_index] = reply.error;
        if (!valid(reply, 0)) {
            state->closes[sink_index] = AL_CLOSE_UNKNOWN;
            return 1;
        }
        state->closes[sink_index] = reply.error ? AL_CLOSE_FAILED : AL_CLOSED;
    }
    if (state->failure == AL_NONE && state->closes[0] == AL_CLOSED &&
        state->closes[1] == AL_CLOSED)
        state->exit_status = state->intended_exit;
    return state->exit_status;
}
