/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_PROTOCOL_H
#define AETHER_FD_PROTOCOL_H
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#if defined(AEFD_CWD_WIRE) && !defined(AEFD_DUP2_WIRE)
#error "AEFD_CWD_WIRE requires AEFD_DUP2_WIRE"
#endif
#if defined(AEFD_WRITE_WIRE) &&                                                \
    (!defined(AEFD_PATH_WIRE) || !defined(AEFD_DUP2_WIRE) ||                   \
     defined(AEFD_CWD_WIRE))
#error "AEFD_WRITE_WIRE requires path/dup2 without CWD"
#endif
/* Trusted matching build selection only; never negotiate from peer bytes. */
#ifdef AEFD_DUP2_WIRE
#ifndef AEFD_PATH_WIRE
#error "AEFD_DUP2_WIRE requires AEFD_PATH_WIRE"
#endif
#ifdef AEFD_CWD_WIRE
#define AEFD_MAGIC "AEFP0003"
#else
#ifdef AEFD_WRITE_WIRE
#define AEFD_MAGIC "AEFW0001"
#else
#define AEFD_MAGIC "AEFP0002"
#endif
#endif
#define AEFD_FIRST_FILE 0
#define AEFD_MAP_MAGIC "AEFDT002"
#define AEFD_STARTUP_MAGIC "AEFDB002"
#define AEFD_FORK_MAGIC "AEFORK02"
#define AEFD_EXEC_MAGIC "AEEXEC02"
#else
#define AEFD_FIRST_FILE 3
#define AEFD_MAP_MAGIC "AEFDT001"
#define AEFD_STARTUP_MAGIC "AEFDB001"
#define AEFD_FORK_MAGIC "AEFORK01"
#define AEFD_EXEC_MAGIC "AEEXEC01"
#ifdef AEFD_PATH_WIRE
#define AEFD_MAGIC "AEFP0001"
#else
#define AEFD_MAGIC "AEFD0001"
#endif
#endif
#define AEFD_FRAME 64U
#define AEFD_READ_MAX 4096U

static inline int aefd_file_selector(uint64_t value)
{
    return value - (uint64_t)AEFD_FIRST_FILE < (uint64_t)(16 - AEFD_FIRST_FILE);
}
struct aefd_reply {
    int64_t status;
    uint64_t result;
    size_t body;
};
static inline uint64_t aefd_word(const unsigned char *p, unsigned index)
{
    uint64_t value = 0;
    for (unsigned i = 0; i < 8; ++i)
        value |= (uint64_t)p[index * 8U + i] << (i * 8U);
    return value;
}
static inline void aefd_put(unsigned char *p, unsigned index, uint64_t value)
{
    for (unsigned i = 0; i < 8; ++i)
        p[index * 8U + i] = (unsigned char)(value >> (i * 8U));
}
/* Pure codec only; callers own/authenticate transport and sequence lifetime.
 * All pointer ranges must be valid; this function initializes the whole frame.
 */
static inline int aefd_request(unsigned char out[AEFD_FRAME],
                               uint64_t generation, uint64_t sequence,
                               uint64_t opcode, const uint64_t args[4])
{
    if (!out || !args)
        return 0;
    memset(out, 0, AEFD_FRAME);
    if (!generation || !sequence || sequence == UINT64_MAX)
        return 0;
    memcpy(out, AEFD_MAGIC, 8);
    aefd_put(out, 1, opcode);
    aefd_put(out, 2, generation);
    aefd_put(out, 3, sequence);
    for (unsigned i = 0; i < 4; ++i)
        aefd_put(out, i + 4U, args[i]);
    return 1;
}
/* Full padded component or explicitly selected canonical root path; no CWD. */
static inline int aefd_name(unsigned char out[256], const unsigned char *name,
                            size_t length)
{
    if (!out)
        return 0;
    if (!name || !length || length > 255) {
        memset(out, 0, 256);
        return 0;
    }
#ifdef AEFD_CWD_WIRE
    for (size_t i = 0; i < length; ++i)
        if (!name[i])
            goto invalid_name;
#elif defined(AEFD_PATH_WIRE)
    size_t start = name[0] == '/' ? 1U : 0U;
    /* '/' is a directory; the service supplies EISDIR, not a fabricated file.
     */
    for (size_t i = start; i <= length; ++i) {
        if (i < length && !name[i])
            goto invalid_name;
        if (i == length || name[i] == '/') {
            size_t part = i - start;
            if ((!part && length != 1) || (part == 1 && name[start] == '.') ||
                (part == 2 && name[start] == '.' && name[start + 1] == '.'))
                goto invalid_name;
            start = i + 1;
        }
    }
#else
    if ((length == 1 && name[0] == '.') ||
        (length == 2 && name[0] == '.' && name[1] == '.'))
        goto invalid_name;
    for (size_t i = 0; i < length; ++i)
        if (!name[i] || name[i] == '/')
            goto invalid_name;
#endif
    memmove(out, name, length);
    memset(out + length, 0, 256 - length);
    return 1;
invalid_name:
    memset(out, 0, 256);
    return 0;
}
/* Header validation only. Publish output once all checks pass. Body must still
 * be completely received and validated before a read result can be consumed. */
static inline int aefd_decode(const unsigned char *frame, size_t length,
                              uint64_t generation, uint64_t sequence,
                              uint64_t opcode, size_t requested,
                              struct aefd_reply *out)
{
    if (!frame || !out || length != AEFD_FRAME || !generation || !sequence ||
        sequence == UINT64_MAX || memcmp(frame, AEFD_MAGIC, 8) ||
        aefd_word(frame, 2) != generation || aefd_word(frame, 3) != sequence ||
        aefd_word(frame, 6) || aefd_word(frame, 7))
        return 0;
    uint64_t raw = aefd_word(frame, 1);
    int64_t status = raw <= INT64_MAX
                         ? (int64_t)raw
                         : INT64_MIN + (int64_t)(raw - (UINT64_C(1) << 63));
    uint64_t result = aefd_word(frame, 4), body = aefd_word(frame, 5);
    if (status) {
        if (status > 0 || status < -INT64_C(2147483647) || result || body)
            return 0;
    } else {
        switch (opcode) {
        case 1:
#ifdef AEFD_WRITE_WIRE
        case 10:
#endif
        case 4:
#ifdef AEFD_DUP2_WIRE
        case 7:
#endif
            if (!aefd_file_selector(result) || body)
                return 0;
            break;
        case 2:
            if (requested > AEFD_READ_MAX || result > requested ||
                body != result)
                return 0;
            break;
#ifdef AEFD_CWD_WIRE
        case 9:
            if (result < 2 || result > 256 || body != result)
                return 0;
            break;
#endif
        case 3:
            if (result > INT64_MAX || body)
                return 0;
            break;
        case 5:
        case 6:
#ifdef AEFD_CWD_WIRE
        case 8:
#endif
            if (result || body)
                return 0;
            break;
        default:
            return 0;
        }
    }
    struct aefd_reply value = {status, result, (size_t)body};
    *out = value;
    return 1;
}
/* Caller supplies initialized complete padded input and a valid4096-byte
 * output. Allows overlap. Every rejected body clears the complete output. No
 * I/O/retry. */
static inline int aefd_body(unsigned char out[AEFD_READ_MAX],
                            const unsigned char *body, size_t length,
                            size_t count)
{
    if (!out)
        return 0;
    if (count > AEFD_READ_MAX || length != ((count + 63U) / 64U) * 64U ||
        (length && !body)) {
        memset(out, 0, AEFD_READ_MAX);
        return 0;
    }
    for (size_t i = count; i < length; ++i) {
        if (body[i]) {
            memset(out, 0, AEFD_READ_MAX);
            return 0;
        }
    }
    if (count)
        memmove(out, body, count);
    memset(out + count, 0, AEFD_READ_MAX - count);
    return 1;
}
#endif
