/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FD_NOTE_CREATE_H
#define AETHER_FD_NOTE_CREATE_H
#include "fd-client.h"
#ifndef AEFD_ZSH_HOME_REDIRECTION_BINDINGS
#error "note creation requires the closed redirection profile"
#endif
/* Remote creation progress, post-create failure and local channel cleanup are
 * independent observations. None grants a descriptor or permission to replay.
 */
struct aefd_note_create_receipt {
    int64_t status;
    uint64_t fd, flags, txg, mutation_kind;
    int64_t mutation_value;
    struct aefd_close_result source_cleanup;
    uint64_t post_kind;
    int64_t post_value;
};
struct aefd_note_create_result {
    int observation;
    int64_t status, installation_status;
    uint64_t generation, sequence;
    struct aefd_note_create_receipt remote;
    int file_closed;
    struct aefd_close_result file_cleanup;
};
/* Pure codec. Failed decoding leaves out unchanged; all fields are checked
 * before the independently successful open can publish its remote selector. */
static inline int aefd_note_create_decode(const unsigned char header[64],
                                          const unsigned char *body,
                                          size_t length, uint64_t generation,
                                          uint64_t sequence,
                                          struct aefd_note_create_receipt *out)
{
    if (!header || !body || !out || length != 64 || !generation || !sequence ||
        sequence == UINT64_MAX || memcmp(header, AEFD_MAGIC, 8) ||
        aefd_word(header, 2) != generation ||
        aefd_word(header, 3) != sequence || aefd_word(header, 5) != 64 ||
        aefd_word(header, 6) || aefd_word(header, 7))
        return 0;
    struct aefd_note_create_receipt r = {
        .status = aefd_write_signed(aefd_word(header, 1)),
        .fd = aefd_word(header, 4),
        .flags = aefd_word(body, 0),
        .txg = aefd_word(body, 1),
        .mutation_kind = aefd_word(body, 2),
        .mutation_value = aefd_write_signed(aefd_word(body, 3)),
        .source_cleanup = {aefd_write_signed(aefd_word(body, 4)),
                           aefd_write_signed(aefd_word(body, 5))},
        .post_kind = aefd_word(body, 6),
        .post_value = aefd_write_signed(aefd_word(body, 7))};
    uint64_t tag = r.flags & 7U;
    int cleanup = (r.flags & 16U) != 0;
    if (r.flags & ~UINT64_C(23) || tag == 7 ||
        (!cleanup && (r.source_cleanup.input || r.source_cleanup.output)))
        return 0;
    if (!r.status) {
        if (r.flags != 6 || !r.txg || !aefd_file_selector(r.fd) ||
            r.mutation_kind || r.mutation_value || r.post_kind || r.post_value)
            return 0;
    } else {
        int64_t status;
        uint64_t kind = tag == 6 ? r.post_kind : r.mutation_kind;
        int64_t value = tag == 6 ? r.post_value : r.mutation_value;
        if (r.fd || !kind || kind > (tag == 0 ? 9U : 12U) ||
            !aefd_write_status(kind, value, &status) || r.status != status)
            return 0;
        if (tag == 0) {
            if (cleanup || r.txg || r.post_kind || r.post_value)
                return 0;
        } else if (tag == 6) {
            if (!cleanup || !r.txg || r.mutation_kind || r.mutation_value)
                return 0;
        } else {
            if (!cleanup || r.post_kind || r.post_value)
                return 0;
            if (tag == 5) {
                if ((kind != 10 && kind != 11) || r.txg)
                    return 0;
            } else {
                if (kind != 12 || (tag == 1 && r.txg) ||
                    ((tag == 2 || tag == 3) && value < -4095) ||
                    (tag == 3 && !r.txg) ||
                    (tag == 4 && (r.txg || value != -5)))
                    return 0;
            }
        }
    }
    *out = r;
    return 1;
}
/* Exclusive/disjoint bounded client contract, identical to typed writes.
 * Preserve output through all later writes, closes and local installation. */
int aefd_client_note_create(struct aefd_client *, const unsigned char *, size_t,
                            int cloexec, unsigned mode,
                            struct aefd_note_create_result *);
#endif
