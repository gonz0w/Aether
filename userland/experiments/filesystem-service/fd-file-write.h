/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_FILE_WRITE_H
#define AETHER_FD_FILE_WRITE_H
#include "fd-client.h"
#ifndef AEFD_WRITE_WIRE
#error "file write receipt requires explicit AEFD_WRITE_WIRE"
#endif
/* Local observations never masquerade as fully decoded remote receipts. */
#define AEFD_WRITE_NOT_SENT 0
#define AEFD_WRITE_REMOTE 1
#define AEFD_WRITE_UNKNOWN 2
struct aefd_write_receipt {
    int64_t status;
    uint64_t count, flags, offset, txg, staged;
    struct aefd_close_result source_cleanup;
    uint64_t error_kind;
    int64_t error_value;
};
struct aefd_write_result {
    int observation;
    int64_t status;
    uint64_t generation, sequence;
    int fd;
    size_t requested;
    struct aefd_write_receipt remote;
    int file_closed;
    struct aefd_close_result file_cleanup;
};
static inline int64_t aefd_write_signed(uint64_t raw)
{
    return raw <= INT64_MAX ? (int64_t)raw
                            : INT64_MIN + (int64_t)(raw - (UINT64_C(1) << 63));
}
static inline int aefd_home_name(unsigned char out[256],
                                 const unsigned char *name, size_t length)
{
    if (!name || !length || length > 255)
        goto invalid;
    if ((length == 1 && name[0] == '.') ||
        (length == 2 && name[0] == '.' && name[1] == '.'))
        goto invalid;
    for (size_t i = 0; i < length; ++i)
        if (!name[i] || name[i] == '/')
            goto invalid;
    memmove(out, name, length);
    memset(out + length, 0, 256 - length);
    return 1;
invalid:
    memset(out, 0, 256);
    return 0;
}
static inline int aefd_write_status(uint64_t kind, int64_t value,
                                    int64_t *status)
{
    if (kind < 1 || kind > 16)
        return 0;
    if (kind == 11) {
        *status = -5;
        return 1;
    }
    if (kind == 12) {
        if (value >= 0 || value < -INT64_C(2147483647))
            return 0;
        *status = value;
        return 1;
    }
    if ((kind != 13 && value) ||
        (kind == 13 && (value < INT32_MIN || value > INT32_MAX)))
        return 0;
    static const int64_t values[17] = {0,   -9, -24, -22, -75, -5, -5,  -22, -5,
                                       -28, -5, -5,  0,   -9,  -9, -16, -9};
    *status = values[kind];
    return 1;
}
/* Pure codec: publish only after complete header and exact64-byte receipt
 * validate. All ranges valid; failed decoding leaves the caller output
 * unchanged. */
static inline int aefd_write_decode(const unsigned char header[64],
                                    const unsigned char *body, size_t length,
                                    uint64_t generation, uint64_t sequence,
                                    size_t requested,
                                    struct aefd_write_receipt *out)
{
    if (!header || !body || !out || length != 64 || !generation || !sequence ||
        sequence == UINT64_MAX || !requested || requested > AEFD_READ_MAX ||
        memcmp(header, AEFD_MAGIC, 8) || aefd_word(header, 2) != generation ||
        aefd_word(header, 3) != sequence || aefd_word(header, 5) != 64 ||
        aefd_word(header, 6) || aefd_word(header, 7))
        return 0;
    struct aefd_write_receipt r = {
        .status = aefd_write_signed(aefd_word(header, 1)),
        .count = aefd_word(header, 4),
        .flags = aefd_word(body, 0),
        .offset = aefd_word(body, 1),
        .txg = aefd_word(body, 2),
        .staged = aefd_word(body, 3),
        .source_cleanup = {aefd_write_signed(aefd_word(body, 4)),
                           aefd_write_signed(aefd_word(body, 5))},
        .error_kind = aefd_word(body, 6),
        .error_value = aefd_write_signed(aefd_word(body, 7))};
    uint64_t tag = r.flags & 7U;
    int has_offset = (r.flags & 8U) != 0, has_cleanup = (r.flags & 16U) != 0;
    if (r.flags & ~UINT64_C(31) || tag == 7 || (!has_offset && r.offset) ||
        (has_offset && r.offset > INT64_MAX) ||
        (!has_cleanup && (r.source_cleanup.input || r.source_cleanup.output)))
        return 0;
    if (tag == 6) {
        if (r.status || r.count != requested || r.flags != 14 || !r.txg ||
            r.staged != requested || r.error_kind || r.error_value ||
            r.offset > (uint64_t)INT64_MAX - requested)
            return 0;
    } else {
        int64_t status;
        if (!aefd_write_status(r.error_kind, r.error_value, &status) ||
            r.status != status || r.count)
            return 0;
        if (tag == 0) {
            if (r.txg || r.staged || (r.error_kind >= 10 && r.error_kind <= 12))
                return 0;
        } else {
            if (!has_offset || !has_cleanup ||
                r.offset > (uint64_t)INT64_MAX - requested)
                return 0;
            if (tag == 5) {
                if ((r.error_kind != 10 && r.error_kind != 11) || r.txg ||
                    r.staged)
                    return 0;
            } else {
                if (r.error_kind != 12)
                    return 0;
                if (tag == 1 && (r.txg || r.staged))
                    return 0;
                if ((tag == 2 || tag == 3) &&
                    (r.staged != 0 && r.staged != requested))
                    return 0;
                if (tag == 3 && !r.txg)
                    return 0;
                if (tag == 4 && (r.error_value != -5 || r.txg || r.staged))
                    return 0;
            }
        }
    }
    *out = r;
    return 1;
}
/* Fresh initialized client, exclusive/disjoint ranges and nonreentrant bounded
 * callbacks. Output always identifies local vs complete remote observation.
 * 1 = validated remote receipt (including errors),0 = invalid/no I/O,-1 = local
 * FILE retirement. Caller retains output through later
 * abort/drop/reconciliation. */
int aefd_client_write(struct aefd_client *, int fd, const unsigned char *,
                      size_t, struct aefd_write_result *);
#endif
