/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_HOME_NATIVE_H
#define AETHER_FS_HOME_NATIVE_H
#include "native-service.h"
#include "filesystem-engine.h"
#include <stddef.h>
#include <stdint.h>

struct aether_fs_bootstrap_receipt {
    uint64_t provider, returned, error_kind;
    int64_t error_value, returned_error;
    uint64_t returned_txg, returned_staged, returned_state;
    int64_t provider_error;
    uint64_t provider_txg, provider_staged, provider_state;
};
struct aether_fs_home_result {
    uint64_t version, bytes, phase, error_kind;
    int64_t error_value;
    uint64_t flags, mutation_attempts;
    struct aether_fs_bootstrap_receipt mkdir, create;
    struct aether_fs_service_result service;
};
struct aether_fs_home_launch_state {
    uint64_t version, bytes, reader, writer, phases;
    int64_t engine_error;
    struct aether_fs_home_result home;
    int64_t startup_reader_close, startup_writer_close;
};
enum aether_fs_home_flags {
    AETHER_FS_HOME_ACTIVATION = 1,
    AETHER_FS_HOME_ORDER_REQUIRED = 2,
    AETHER_FS_HOME_ENDPOINTS_ACCEPTED = 4,
    AETHER_FS_HOME_CLOSE_ATTEMPTED = 8,
    AETHER_FS_HOME_CALLBACK_ENTERED = 16,
    AETHER_FS_HOME_ENTRY_ENTERED = 32
};
_Static_assert(sizeof(struct aether_fs_bootstrap_receipt) == 96,
               "home receipt");
_Static_assert(_Alignof(struct aether_fs_bootstrap_receipt) == 8,
               "receipt alignment");
_Static_assert(sizeof(struct aether_fs_home_result) == 320, "home result");
_Static_assert(_Alignof(struct aether_fs_home_result) == 8, "result alignment");
_Static_assert(offsetof(struct aether_fs_home_result, mkdir) == 56,
               "mkdir offset");
_Static_assert(offsetof(struct aether_fs_home_result, create) == 152,
               "create offset");
_Static_assert(offsetof(struct aether_fs_home_result, service) == 248,
               "service offset");
_Static_assert(sizeof(struct aether_fs_home_launch_state) == 384,
               "home launch");
_Static_assert(_Alignof(struct aether_fs_home_launch_state) == 8,
               "launch alignment");
_Static_assert(offsetof(struct aether_fs_home_launch_state, home) == 48,
               "home offset");
_Static_assert(offsetof(struct aether_fs_home_launch_state,
                        startup_reader_close) == 368,
               "startup close offset");
int aether_fs_home_run(void *, const unsigned char *, size_t, uint64_t,
                       uint64_t, uint64_t, uint64_t,
                       struct aether_fs_home_result *, size_t);
int aether_fs_home_launch_serve(void *, struct aether_fs_home_launch_state *);
int aether_fs_home_engine_run(uint64_t, struct aether_fs_home_launch_state *);
int aether_fs_home_engine_import(struct aether_fs_home_launch_state *);

/* C independently consumes copied integer diagnostics. No receipt grants
 * authority. A protocol error never selects the no-order path. All borrows
 * follow the selected synchronous SPA/output contract. */
static inline int aether_fs_home_zero_completion(int64_t error, uint64_t txg,
                                                 uint64_t staged,
                                                 uint64_t state)
{
    return !error && !txg && !staged && !state;
}
static inline int
aether_fs_home_receipt_order(const struct aether_fs_bootstrap_receipt *r,
                             int *protocol)
{
    int pzero =
        aether_fs_home_zero_completion(r->provider_error, r->provider_txg,
                                       r->provider_staged, r->provider_state);
    int rzero =
        aether_fs_home_zero_completion(r->returned_error, r->returned_txg,
                                       r->returned_staged, r->returned_state);
    int same = r->provider_error == r->returned_error &&
               r->provider_txg == r->returned_txg &&
               r->provider_staged == r->returned_staged &&
               r->provider_state == r->returned_state;
    int success = !r->provider_error && r->provider_txg &&
                  !r->provider_staged && r->provider_state == 2;
    int unassigned = r->provider_error >= 1 && r->provider_error <= 4095 &&
                     !r->provider_txg && !r->provider_staged &&
                     !r->provider_state;
    int failed =
        r->provider_error >= 1 && r->provider_error <= 4095 &&
        !r->provider_staged &&
        (r->provider_state == 1 || (r->provider_state == 2 && r->provider_txg));
    int valid = r->provider <= 2 && r->returned <= 2 && r->error_kind <= 16 &&
                r->error_value >= INT32_MIN && r->error_value <= INT32_MAX &&
                (r->error_kind == 10 || !r->error_value);
    if (!r->returned) {
        valid = valid && !r->provider && !r->error_kind && !r->error_value &&
                pzero && rzero;
    } else if (r->returned == 1) {
        valid = valid && r->provider == 1 && !r->error_kind &&
                !r->error_value && success && same;
    } else {
        valid = valid && r->error_kind && (r->error_kind == 15 || rzero);
        if (!r->provider) {
            valid = valid && pzero && r->error_kind != 15 &&
                    r->error_kind != 14 && r->error_kind != 9;
        } else if (r->provider == 2) {
            valid = valid && pzero && r->error_kind == 14;
        } else if (r->error_kind == 10) {
            valid = valid && unassigned && r->error_value == r->provider_error;
        } else if (r->error_kind == 15) {
            valid = valid && ((failed && same) ||
                              (success && r->returned_error == 5 &&
                               r->returned_txg == r->provider_txg &&
                               r->returned_staged == r->provider_staged &&
                               r->returned_state == r->provider_state));
        } else {
            /* Malformed original typed completion is retained as diagnostics,
             * but cannot establish a valid C handoff/no-order conclusion. */
            valid = 0;
        }
    }
    if (!valid)
        *protocol = 1;
    return !valid || (r->provider != 0 && !unassigned);
}
static inline int
aether_fs_home_order_required(const struct aether_fs_home_result *h,
                              int *protocol)
{
    int order = aether_fs_home_receipt_order(&h->mkdir, protocol);
    order |= aether_fs_home_receipt_order(&h->create, protocol);
    int active = (h->flags & AETHER_FS_HOME_ACTIVATION) != 0;
    int accepted = (h->flags & AETHER_FS_HOME_ENDPOINTS_ACCEPTED) != 0;
    int close_attempted = (h->flags & AETHER_FS_HOME_CLOSE_ATTEMPTED) != 0;
    int entered = (h->flags & AETHER_FS_HOME_ENTRY_ENTERED) != 0;
    int callback = (h->flags & AETHER_FS_HOME_CALLBACK_ENTERED) != 0;
    unsigned calls = (h->mkdir.provider != 0) + (h->create.provider != 0);
    int valid = h->version == 1 && h->bytes == 320 &&
                !(h->flags & ~UINT64_C(63)) && h->phase <= 9 &&
                h->error_kind <= 16 &&
                (h->error_kind == 10 || !h->error_value) &&
                h->error_value >= INT32_MIN && h->error_value <= INT32_MAX &&
                h->mutation_attempts <= 9 && h->mutation_attempts >= calls &&
                (!close_attempted || accepted) &&
                (!accepted || (entered && close_attempted)) && callback &&
                entered && (h->phase ? h->error_kind != 0 : h->error_kind == 0);
    if (!accepted) {
        valid = valid && !active && !order && !h->mutation_attempts &&
                h->phase == 1 && h->error_kind == 1 && !h->error_value &&
                h->flags == 48 && !close_attempted &&
                !h->service.reader_close && !h->service.writer_close;
    }
    if (h->create.returned || active)
        valid = valid && h->mkdir.returned == 1;
    if (active)
        valid = valid && accepted && h->create.returned == 1 &&
                (h->phase == 0 || h->phase == 9) && h->service.ready <= 1 &&
                h->service.requests <= 96 && h->service.stop <= 6 &&
                h->service.bytes_staged <= 4096 && h->service.state <= 3 &&
                (h->service.ready || !h->service.requests) &&
                h->mutation_attempts <= 2 + h->service.requests &&
                (h->service.stop != 3 || h->service.requests == 96) &&
                (h->phase == 9 ? h->service.stop == 4 : h->service.stop != 4);
    if (h->service.state != 0)
        valid = valid && h->service.ready && h->service.requests;
    else
        valid = valid && !h->service.txg && !h->service.bytes_staged;
    if (h->service.state == 1)
        valid = valid && (h->service.stop == 2 || h->service.stop == 5) &&
                h->service.error;
    if (h->service.state == 2)
        valid = valid && h->service.txg;
    if (h->service.state == 3) {
        valid = valid && active && h->service.ready && h->service.requests &&
                (h->service.stop == 2 || h->service.stop == 5) &&
                h->service.error && !h->service.txg && !h->service.bytes_staged;
    }
    if (accepted) {
        switch (h->phase) {
        case 0:
        case 9:
            valid = valid && active;
            break;
        case 2:
        case 3:
            valid = valid && !h->mkdir.returned && !h->create.returned;
            break;
        case 4:
            valid = valid && h->mkdir.returned == 2 && !h->create.returned;
            break;
        case 5:
            valid = valid && h->mkdir.returned == 1 && !h->create.returned;
            break;
        case 6:
            valid = valid && h->mkdir.returned == 1 && h->create.returned == 2;
            break;
        case 7:
        case 8:
            valid = valid && h->mkdir.returned == 1 && h->create.returned == 1;
            break;
        default:
            valid = 0;
        }
    }
    if (h->phase == 4 || h->phase == 6) {
        const struct aether_fs_bootstrap_receipt *r =
            h->phase == 4 ? &h->mkdir : &h->create;
        valid = valid && r->returned == 2 && h->error_kind == r->error_kind &&
                h->error_value == r->error_value;
    }
    if (!active) {
        const struct aether_fs_service_result *s = &h->service;
        valid = valid && h->mutation_attempts == calls && !s->ready &&
                !s->requests && !s->stop && !s->error && !s->txg &&
                !s->bytes_staged && !s->state;
    }
    order |= active;
    if (!!order != !!(h->flags & AETHER_FS_HOME_ORDER_REQUIRED))
        valid = 0;
    if (!valid)
        *protocol = 1;
    return order || *protocol || (h->flags & AETHER_FS_HOME_ORDER_REQUIRED);
}
#endif
