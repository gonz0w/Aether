/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual recovery oracle plus original zpl-read.c, using the existing typed
 * SA/ZAP/DMU/SHA observation fixture. No host crypto or ZFS qualification. */
int aether_home_baseline_main(int, char **);
#define main aether_home_baseline_main
#define kmem_zalloc baseline_kmem_zalloc
#define sa_bulk_lookup baseline_sa_bulk_lookup
#define spa_writeable baseline_spa_writeable
#include "home-recovery-tests.c"
#undef main
#undef kmem_zalloc
#undef sa_bulk_lookup
#undef spa_writeable

void *kmem_zalloc(size_t, int);
int sa_bulk_lookup(sa_handle_t *, sa_bulk_attr_t *, int);
int spa_writeable(spa_t *);
static unsigned fault, probe_loads, eof_seen, spa_queries, allocation_calls;
static unsigned char *scratch;
#define CHECK(value, marker)                                                   \
    do {                                                                       \
        if (!(value)) {                                                        \
            fprintf(stderr, "HOME_EMPTY_%s:%d\n", marker, __LINE__);           \
            exit(1);                                                           \
        }                                                                      \
    } while (0)
void *kmem_zalloc(size_t bytes, int flags)
{
    ++allocation_calls;
    void *result = baseline_kmem_zalloc(bytes, flags);
    if (bytes >= 4096)
        scratch = result;
    return result;
}
int spa_writeable(spa_t *spa)
{
    ++spa_queries;
    return baseline_spa_writeable(spa);
}
int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *attrs, int count)
{
    if (recovered && h->object == probe_object() && count == 6) {
        ++probe_loads;
        if (probe_loads == 2) {
            ++eof_seen;
            /* The prior real xattr read left0x5a in scratch. The actual
             * nonzero-length read clears the requested byte BEFORE SA load.
             * A zero-length read cannot manufacture this observation. */
            CHECK(scratch && scratch[0] == 0, "NONZERO_READ_REQUIRED");
            if (fault == 2)
                return EIO;
            if (fault == 3)
                nodes[10].value[ZPL_SIZE][0] = 1;
            /* EOF later becoming empty cannot excuse an earlier size16. */
            if (fault == 5)
                nodes[10].value[ZPL_SIZE][0] = 0;
            if (fault == 17)
                ++nodes[10].value[ZPL_GEN][0];
        }
    }
    return baseline_sa_bulk_lookup(h, attrs, count);
}
static void prepare(unsigned phase)
{
    initialize(phase);
    probe_loads = eof_seen = spa_queries = allocation_calls = 0;
    scratch = NULL;
    pool.writable = 0;
}
int main(int argc, char **argv)
{
    if (argc != 3)
        return 64;
    fault = (unsigned)strtoul(argv[1], NULL, 10);
    CHECK(fault <= 17, "CLOSED_HOST_CASE");
    reference = malloc(780248);
    FILE *input = fopen(argv[2], "rb");
    CHECK(reference && input && fread(reference, 1, 780248, input) == 780248 &&
              fgetc(input) == EOF,
          "REFERENCE_INPUT");
    fclose(input);
    unsigned char pristine[32], digest[32];
    selected = 0;
    prepare(0);
    CHECK(!aether_home_readback(&pool, 0, 1791290040, 1791290100, pristine) &&
              !owns && !handles && !allocations,
          "PRISTINE_DEFAULT_MODE0");
    selected = fault == 7    ? 34
               : fault == 8  ? 29
               : fault == 11 ? 2
               : fault == 15 ? 18
                             : 0;
    prepare(fault == 10 ? 0 : 1);
    if (fault != 10 && fault != 9 && fault != 5)
        nodes[10].value[ZPL_SIZE][0] = fault == 1 ? 1 : 0;
    if (fault == 6)
        nodes[10].value[ZPL_UID][0] = 0;
    int expectation = fault == 9 || fault == 4     ? 1
                      : fault == 10 || fault == 16 ? 0
                      : fault == 12                ? 3
                      : fault == 13                ? -1
                      : fault == 14                ? INT32_MAX
                                                   : 2;
    memset(digest, 0xa5, sizeof digest);
    int error = aether_home_readback(&pool, expectation, 1791290040, 1791290100,
                                     digest);
    int equal = !memcmp(pristine, digest, sizeof digest);
    int valid = fault == 0 || fault == 9 || fault == 10 || fault == 11;
    CHECK((error == 0 && equal) == valid, "ORACLE_RESULT");
    CHECK(!owns && !handles && !allocations, "ALL_CLEANUP_BALANCED");
    if (fault == 0 || fault == 11)
        CHECK(eof_seen == 1 && probe_loads == 2, "REAL_EMPTY_EOF_OBSERVED");
    if (fault == 2 || fault == 3 || fault == 17)
        CHECK(error && eof_seen == 1, "EOF_ERROR_NONZERO_OR_STALE_DENIED");
    if (fault >= 12 && fault <= 14)
        CHECK(error == EINVAL && !spa_queries && !allocation_calls,
              "UNKNOWN_MODE_BEFORE_EFFECTS");
    if (error)
        for (unsigned i = 0; i < 32; ++i)
            CHECK(!digest[i], "FAILURE_DIGEST_ZERO");
    free(reference);
    printf("home empty case %u passed\n", fault);
    return 0;
}
