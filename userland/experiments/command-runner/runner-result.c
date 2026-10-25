/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-result.h"
static uint32_t word(const unsigned char *p)
{
    uint32_t result = 0;
    for (unsigned i = 0; i < 4; ++i)
        result |= (uint32_t)p[i] << (8 * i);
    return result;
}
static int receipt_valid(uint32_t receipt)
{
#ifdef NATIVE_SUSTAINED_V2
    return (receipt & 0xffff0000u) == 0x7b000000u && (receipt & 0xffffu);
#else
    return receipt == 0x73000001u || receipt == 0x73000002u;
#endif
}
static enum ar_reply_action decode(const unsigned char *record, size_t size,
                                   uint32_t receipt, int collection,
                                   struct ar_reply *output)
{
    if (!record || !output || size != 32 || !receipt_valid(receipt))
        return AR_REPLY_INVALID;
    uint32_t status = word(record);
    struct ar_reply candidate = {0};
    if (status) {
        /* Wire errors are two's-complement -1..-4095, independent of host
         * errno. */
        if (status < UINT32_MAX - 4094u)
            return AR_REPLY_INVALID;
        for (unsigned i = 4; i < 32; ++i)
            if (record[i])
                return AR_REPLY_INVALID;
        candidate.error = -(int32_t)(~status + 1u);
        *output = candidate;
        return collection && candidate.error == -11 ? AR_REPLY_PENDING
                                                    : AR_REPLY_ERROR;
    }
    if (word(record + 4) != receipt)
        return AR_REPLY_INVALID;
    for (unsigned i = collection ? 16u : 8u; i < 32; ++i)
        if (record[i])
            return AR_REPLY_INVALID;
    candidate.receipt = receipt;
    if (collection) {
        candidate.detail = word(record + 8);
        candidate.kind = word(record + 12);
        if (candidate.kind < 1 || candidate.kind > 3)
            return AR_REPLY_INVALID;
    }
    *output = candidate;
    return collection ? AR_REPLY_COLLECTED : AR_REPLY_ADMITTED;
}
enum ar_reply_action ar_admission(const unsigned char *record, size_t size,
                                  uint32_t generation, struct ar_reply *output)
{
#ifdef NATIVE_SUSTAINED_V2
    if (!generation || generation > 65535)
        return AR_REPLY_INVALID;
    return decode(record, size, 0x7b000000u | generation, 0, output);
#else
    if (generation != 1 && generation != 2)
        return AR_REPLY_INVALID;
    return decode(record, size, 0x73000000u | generation, 0, output);
#endif
}
enum ar_reply_action ar_collection(const unsigned char *record, size_t size,
                                   uint32_t receipt, struct ar_reply *output)
{
    return decode(record, size, receipt, 1, output);
}
unsigned ar_terminal_exit(const struct ar_reply *reply, int cleanup_complete)
{
    if (!reply || reply->error || !receipt_valid(reply->receipt) ||
        cleanup_complete != 1 || reply->kind != 1 || reply->detail > 255)
        return 1;
    return reply->detail;
}
