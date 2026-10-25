/* SPDX-License-Identifier: BSD-2-Clause */
/* Typed host substitutions execute the selected original importer/lifecycle.
 * They are observations of call order, not OpenZFS/native execution. */
#include "home-native.h"
#include "home-native-host.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned selected, ordered, exported, closed, stopped, block_closed;
static unsigned utc_closed, runtime_finished, callback;
static objset_t objectset;
static spa_t pool = {{782}, &objectset};
static nvlist_t list;
static struct aether_fs_home_result callback_result;

int aether_pool_label_read(nvlist_t **out)
{
    *out = &list;
    return 0;
}
int aether_pool_label_config(nvlist_t *label, nvlist_t **out)
{
    (void)label;
    *out = &list;
    return 0;
}
void nvlist_free(nvlist_t *value) { (void)value; }
int nvlist_alloc(nvlist_t **out, unsigned flags, int mode)
{
    (void)flags;
    (void)mode;
    *out = &list;
    return 0;
}
int nvlist_add_string(nvlist_t *value, const char *name, const char *text)
{
    (void)value;
    (void)name;
    (void)text;
    return 0;
}
int spa_import(char *name, nvlist_t *config, nvlist_t *props, uint64_t flags)
{
    (void)name;
    (void)config;
    (void)props;
    (void)flags;
    return 0;
}
int spa_open(const char *name, spa_t **out, const void *tag)
{
    (void)name;
    (void)tag;
    *out = &pool;
    return 0;
}
int spa_writeable(spa_t *spa) { return spa == &pool; }
uint64_t spa_version(spa_t *spa)
{
    (void)spa;
    return SPA_VERSION_FEATURES;
}
uint64_t spa_guid(spa_t *spa)
{
    (void)spa;
    return UINT64_C(4253333510760776491);
}
int spa_feature_is_active(spa_t *spa, int feature)
{
    (void)spa;
    (void)feature;
    return 1;
}
int zap_lookup(objset_t *os, uint64_t object, const char *name, uint64_t size,
               uint64_t count, void *out)
{
    (void)os;
    (void)object;
    (void)name;
    (void)size;
    (void)count;
    *(uint64_t *)out = SPA_VERSION_FEATURES;
    return 0;
}
void spa_close(spa_t *spa, const void *tag)
{
    (void)spa;
    (void)tag;
    ++closed;
}
void dmu_buf_user_evict_wait(void) {}
int spa_export(const char *name, nvlist_t **out, int force, int hardforce)
{
    (void)name;
    (void)force;
    (void)hardforce;
    *out = &list;
    ++exported;
    return selected == 20 || selected == 31 ? EBUSY : 0;
}
void spa_namespace_enter(const void *tag) { (void)tag; }
void spa_namespace_exit(const void *tag) { (void)tag; }
spa_t *spa_next(spa_t *previous)
{
    (void)previous;
    return selected == 21 ? &pool : NULL;
}
unsigned aether_pool_hooks_check_ordered(void)
{
    if (!exported || !closed)
        abort();
    ++ordered;
    return selected == 19 || selected == 32;
}
int aether_runtime_init(void) { return 0; }
unsigned aether_runtime_live(void)
{
    return runtime_finished || (selected == 43 && stopped) ? 0 : 1;
}
unsigned aether_runtime_admissions(void) { return 1; }
int aether_runtime_finish(void)
{
    ++runtime_finished;
    return selected == 46 ? EIO : 0;
}
int aether_zfs_startup_bind(const struct aether_zfs_startup *fixture)
{
    (void)fixture;
    return 0;
}
int aether_zfs_volume_bind(uint64_t grant) { return grant ? 0 : EINVAL; }
int aether_utc_establish(unsigned kind)
{
    (void)kind;
    return 0;
}
int aether_utc_close(void)
{
    ++utc_closed;
    return selected == 45 ? EIO : 0;
}
void kernel_init(int mode)
{
    if (mode != 3)
        abort();
}
void kernel_fini(void) { ++stopped; }
void aether_zpl_accounting_init(void) {}
int aether_pool_prepare(void) { return 0; }
uint64_t aether_zfs_granted_pages(void) { return 8192; }
uint64_t aether_zfs_free_pages(void) { return 8192; }
int home_host_block_close(uint64_t grant)
{
    if (!grant || !stopped)
        abort();
    ++block_closed;
    return selected == 44 ? EBUSY : 0;
}

static void success(struct aether_fs_bootstrap_receipt *r)
{
    r->provider = 1;
    r->returned = 1;
    r->returned_txg = r->provider_txg = 800;
    r->returned_state = r->provider_state = 2;
}
static void unassigned(struct aether_fs_bootstrap_receipt *r)
{
    r->provider = 1;
    r->returned = 2;
    r->error_kind = 10;
    r->error_value = EIO;
    r->provider_error = EIO;
}

int aether_fs_home_launch_serve(void *spa,
                                struct aether_fs_home_launch_state *out)
{
    if (spa != &pool)
        abort();
    ++callback;
    struct aether_fs_home_result *h = &out->home;
    h->flags = 4 | 8 | 16 | 32;
    h->phase = 4;
    h->error_kind = 10;
    h->error_value = EIO;
    h->mutation_attempts = 1;
    unassigned(&h->mkdir);
    if (selected) {
        memset(&h->mkdir, 0, sizeof(h->mkdir));
        success(&h->mkdir);
        h->phase = 6;
        h->mutation_attempts = 2;
        h->flags |= 2;
        unassigned(&h->create);
    }
    switch (selected) {
    case 2:
        h->create.provider_state = 2;
        h->create.error_kind = 9;
        h->create.error_value = 0;
        break;
    case 3:
        h->create.error_kind = 15;
        h->create.error_value = 0;
        h->create.returned_error = EIO;
        h->create.provider_state = h->create.returned_state = 1;
        h->create.provider_txg = h->create.returned_txg = 801;
        break;
    case 4:
        memset(&h->create, 0, sizeof(h->create));
        h->create.provider = 2;
        h->create.returned = 2;
        h->create.error_kind = 14;
        break;
    case 5:
        h->create.provider_state = 99;
        break;
    case 6:
        h->flags &= ~UINT64_C(2);
        break;
    case 7:
        h->create.provider = 99;
        break;
    case 8:
        h->create.returned = 0;
        break;
    case 9:
        h->create.error_kind = 99;
        break;
    case 10:
        h->bytes = 72;
        break;
    case 11:
        h->version = 2;
        break;
    case 12:
        h->flags |= 64;
        break;
    case 13:
        h->flags &= ~UINT64_C(4);
        break;
    case 14:
        h->mkdir.provider = 0;
        break;
    case 15:
        h->mutation_attempts = 0;
        break;
    case 16:
        h->create.provider_txg = 900;
        break;
    case 17:
        h->create.error_kind = 15;
        h->create.error_value = 1;
        break;
    case 18:
        h->flags |= 1;
        h->phase = h->error_kind = 0;
        h->error_value = 0;
        memset(&h->create, 0, sizeof(h->create));
        success(&h->create);
        break;
    case 22:
        memset(&h->mkdir, 0, sizeof(h->mkdir));
        memset(&h->create, 0, sizeof(h->create));
        unassigned(&h->mkdir);
        h->phase = 4;
        h->flags &= ~UINT64_C(2);
        h->mutation_attempts = 2; /* Missing receipt for claimed second call. */
        break;
    case 23: /* UTC failed before first provider invocation. */
    case 26: /* Canonical Lost before any reported completion. */
    case 27: /* Canonical unaccepted preflight. */
    case 40: /* Contradictory extra ordered flag after unassigned failure. */
        memset(&h->mkdir, 0, sizeof(h->mkdir));
        memset(&h->create, 0, sizeof(h->create));
        h->phase = 4;
        h->error_kind = 11;
        h->error_value = 0;
        h->mutation_attempts = 0;
        h->flags &= ~UINT64_C(2);
        h->mkdir.returned = 2;
        h->mkdir.error_kind = 11;
        if (selected == 26) {
            h->mkdir.provider = 2;
            h->mkdir.error_kind = h->error_kind = 14;
            h->mutation_attempts = 1;
            h->flags |= 2;
        } else if (selected == 27) {
            memset(&h->mkdir, 0, sizeof(h->mkdir));
            h->phase = 1;
            h->error_kind = 1;
            h->flags = 16 | 32;
        } else if (selected == 40) {
            memset(&h->mkdir, 0, sizeof(h->mkdir));
            unassigned(&h->mkdir);
            h->error_kind = 10;
            h->error_value = EIO;
            h->mutation_attempts = 1;
            h->flags |= 2;
        }
        break;
    case 24: /* Provider success retained despite parent-refresh failure. */
        memset(&h->create, 0, sizeof(h->create));
        h->mkdir.returned = 2;
        h->mkdir.error_kind = 15;
        h->mkdir.returned_error = EIO;
        h->phase = 4;
        h->error_kind = 15;
        h->error_value = 0;
        h->mutation_attempts = 1;
        break;
    case 25: /* UTC failed before second provider invocation. */
        memset(&h->create, 0, sizeof(h->create));
        h->create.returned = 2;
        h->create.error_kind = h->error_kind = 11;
        h->error_value = 0;
        h->mutation_attempts = 1;
        break;
    case 28: /* Bootstrap failure retains actual close errors independently. */
        break;
    case 29: /* Activation's Stop::Provision retains exact Error. */
    case 30: /* Greeting loss retains original reply-loss semantics. */
    case 37: /* Unknown service stop. */
    case 38: /* Malformed ready boolean. */
    case 39: /* Contradictory ordinary-loop header error. */
        memset(&h->create, 0, sizeof(h->create));
        success(&h->create);
        h->flags |= 1;
        h->phase = h->error_kind = 0;
        h->error_value = 0;
        if (selected == 29) {
            h->phase = 9;
            h->error_kind = 11;
            h->service.stop = 4;
            h->service.error = -22;
        } else if (selected == 30) {
            h->service.stop = 2;
            h->service.error = -5;
        } else if (selected == 37) {
            h->service.stop = 99;
        } else if (selected == 38) {
            h->service.ready = 2;
        } else {
            h->error_kind = 11;
        }
        break;
    case 31: /* Protocol invalidity plus export failure. */
    case 32: /* Protocol invalidity plus ordering failure. */
        h->create.provider_state = 99;
        break;
    case 33:
        h->phase = 2;
        break;
    case 34:
        h->phase = 5;
        break;
    case 35:
        h->error_value = INT64_MAX;
        break;
    case 36:
        h->create.error_value = INT64_MAX;
        break;
    case 41:
        h->flags &= ~UINT64_C(32);
        break;
    case 42:
        h->phase = h->error_kind = 0;
        h->error_value = 0;
        break;
    case 47: /* Typed pre-provider Backend is not a provider call. */
    case 48: /* InvalidCompletion contradicts no provider invocation. */
    case 49: /* Only canonical Invalid preflight is an unaccepted result. */
        memset(&h->mkdir, 0, sizeof(h->mkdir));
        memset(&h->create, 0, sizeof(h->create));
        h->mkdir.returned = 2;
        h->mkdir.error_kind = h->error_kind = selected == 48 ? 9 : 10;
        h->mkdir.error_value = h->error_value = selected == 48 ? 0 : -5;
        h->phase = 4;
        h->mutation_attempts = 0;
        h->flags &= ~UINT64_C(2);
        if (selected == 49) {
            memset(&h->mkdir, 0, sizeof(h->mkdir));
            h->phase = 1;
            h->error_kind = 11;
            h->error_value = 0;
            h->flags = 16 | 32;
        }
        break;
    case 50: /* Unknown service completion state. */
    case 51: /* Service staging exceeds the fixed operation bound. */
    case 52: /* Existing service Unknown is a retained failed mutation. */
    case 53: /* Unknown retained through failed reply delivery. */
    case 54: /* Unknown cannot describe a clean loop stop. */
    case 55: /* No loop request can account for a third provider attempt. */
    case 56: /* A loop request cannot precede readiness. */
    case 57: /* Request limit cannot precede the selected 96th request. */
    case 58: /* Exactly 96 requests is the selected loop limit. */
    case 59: /* Unknown does not invent staged bytes. */
    case 60: /* Unknown does not invent an assigned TXG. */
    case 61: /* Unknown cannot clear the failed service status. */
        memset(&h->create, 0, sizeof(h->create));
        success(&h->create);
        h->flags |= 1;
        h->phase = h->error_kind = 0;
        h->error_value = 0;
        if (selected == 50) {
            h->service.state = 99;
        } else if (selected == 51) {
            h->service.bytes_staged = 4097;
        } else if (selected == 55) {
            h->mutation_attempts = 3;
        } else if (selected == 56) {
            h->service.requests = 1;
        } else if (selected == 57 || selected == 58) {
            h->service.ready = 1;
            h->service.requests = selected == 57 ? 95 : 96;
            h->service.stop = 3;
            h->service.error = -28;
        } else {
            h->mutation_attempts = 3;
            h->service.ready = h->service.requests = 1;
            h->service.stop = selected == 53 ? 2 : selected == 54 ? 0 : 5;
            h->service.error = selected == 53 ? -32 : -5;
            h->service.state = 3;
            if (selected == 59)
                h->service.bytes_staged = 1;
            if (selected == 60)
                h->service.txg = 800;
            if (selected == 61)
                h->service.error = 0;
        }
        break;
    case 62: /* State0 cannot retain an assigned TXG. */
    case 63: /* State0 cannot retain staged bytes. */
    case 64: /* Completed state2 requires a TXG. */
    case 65: /* Progress cannot precede readiness and a loop request. */
    case 66: /* Failed committed state1 intentionally retains TXG0. */
    case 67: /* Successful state2 retains the actual completed TXG. */
    case 68: /* Committed state1 cannot describe a clean service stop. */
        memset(&h->create, 0, sizeof(h->create));
        success(&h->create);
        h->flags |= 1;
        h->phase = h->error_kind = 0;
        h->error_value = 0;
        h->mutation_attempts = 3;
        h->service.ready = h->service.requests = 1;
        if (selected == 62)
            h->service.txg = 800;
        else if (selected == 63)
            h->service.bytes_staged = 1;
        else if (selected == 64)
            h->service.state = 2;
        else if (selected == 65) {
            h->service.state = 2;
            h->service.txg = 800;
            h->service.ready = h->service.requests = 0;
            h->mutation_attempts = 2;
        } else if (selected == 66) {
            h->service.state = 1;
            h->service.stop = 5;
            h->service.error = -5;
        } else if (selected == 67) {
            h->service.state = 2;
            h->service.txg = 800;
            h->service.stop = 6;
        } else {
            h->service.state = 1;
            h->service.txg = 800;
        }
        break;
    default:
        break;
    }
    if (selected == 2 || selected == 3 || selected == 4) {
        h->error_kind = h->create.error_kind;
        h->error_value = h->create.error_value;
    }
    if (selected == 18 || selected == 28) {
        h->service.reader_close = -5;
        h->service.writer_close = -6;
    }
    callback_result = *h;
    return EACCES;
}

int main(int argc, char **argv)
{
    if (argc != 2)
        return 64;
    selected = (unsigned)strtoul(argv[1], NULL, 10);
    struct aether_fs_home_launch_state out = {
        .version = 1,
        .bytes = 384,
        .reader = 1,
        .writer = 2,
        .home = {.version = 1, .bytes = 320}};
    int result = aether_fs_home_engine_run(1, &out);
    int protocol = selected == 2 || selected == 22 ||
                   (selected >= 33 && selected <= 42) ||
                   (selected >= 48 && selected <= 51) ||
                   (selected >= 54 && selected <= 57) ||
                   (selected >= 59 && selected <= 65) || selected == 68 ||
                   (selected >= 5 && selected <= 17);
    int failed_order =
        (selected >= 19 && selected <= 21) || selected == 31 || selected == 32;
    if (callback != 1 || closed != 1 || exported != 1 ||
        ordered != (selected == 0 || selected == 20 || selected == 23 ||
                            selected == 27 || selected == 31 || selected == 47
                        ? 0U
                        : 1U)) {
        fprintf(stderr, "HOME_ORDER_ORACLE case=%u ordered=%u exported=%u\n",
                selected, ordered, exported);
        return 1;
    }
    if (failed_order) {
        if (result != (selected == 20 || selected == 31 ? EBUSY : EIO) ||
            (out.phases & AETHER_FS_EXPORTED) || stopped || block_closed)
            return 2;
    } else if (selected >= 43 && selected <= 46) {
        int expected = selected == 44 ? EBUSY : EIO;
        uint64_t missing_phase = selected == 43   ? AETHER_FS_HELPERS_JOINED
                                 : selected == 44 ? AETHER_FS_BLOCK_CLOSED
                                 : selected == 45 ? AETHER_FS_UTC_CLOSED
                                                  : AETHER_FS_RUNTIME_STOPPED;
        if (result != expected || out.engine_error != expected ||
            !(out.phases & AETHER_FS_EXPORTED) ||
            (out.phases & missing_phase) || stopped != 1 ||
            block_closed != (selected == 43 ? 0U : 1U) ||
            utc_closed != (selected <= 44 ? 0U : 1U) ||
            runtime_finished != (selected == 46 ? 1U : 0U))
            return 6;
    } else {
        if (result != (protocol ? EPROTO : EACCES) ||
            out.phases != AETHER_FS_FINISHED || stopped != 1 ||
            block_closed != 1 || utc_closed != 1 || runtime_finished != 1) {
            fprintf(stderr,
                    "HOME_CARRIER_RESULT case=%u actual=%d expected=%d\n",
                    selected, result, protocol ? EPROTO : EACCES);
            return 3;
        }
    }
    /* Import/export/order never normalize or overwrite either observation,
     * bootstrap error, service result or actual endpoint-close result. */
    if (memcmp(&out.home, &callback_result, sizeof(out.home)) ||
        out.engine_error !=
            (failed_order || (selected >= 43 && selected <= 46) ? result : 0))
        return 4;
    struct aether_fs_home_launch_state again = {.version = 1, .bytes = 384};
    if (aether_fs_home_engine_run(1, &again) != EALREADY || callback != 1)
        return 5;
    printf("home C lifecycle case %u passed\n", selected);
    return 0;
}
