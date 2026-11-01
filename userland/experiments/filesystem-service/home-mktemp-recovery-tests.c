/* SPDX-License-Identifier: BSD-2-Clause */
/* Executes actual home-recovery-probe.c and zpl-read.c validation. Reuse the
 * pinned original-data/SA providers; host SHA is stream instrumentation only,
 * not cryptographic or native OpenZFS qualification. Each case is one process.
 */
#define AETHER_HOME_MKTEMP_FIXTURE 1
#define main aether_home_recovery_baseline_main
#define kmem_zalloc baseline_kmem_zalloc
#define spa_writeable baseline_spa_writeable
#define zap_lookup baseline_zap_lookup
#define zap_count baseline_zap_count
#define sa_bulk_lookup baseline_sa_bulk_lookup
#define sa_handle_get baseline_sa_handle_get
int aether_home_recovery_baseline_main(int, char **);
#include "home-recovery-tests.c"
#undef main
#undef kmem_zalloc
#undef spa_writeable
#undef zap_lookup
#undef zap_count
#undef sa_bulk_lookup
#undef sa_handle_get

void *kmem_zalloc(size_t, int);
int spa_writeable(spa_t *);
int zap_lookup(objset_t *, uint64_t, const char *, uint64_t, uint64_t, void *);
int zap_count(objset_t *, uint64_t, uint64_t *);
int sa_bulk_lookup(sa_handle_t *, sa_bulk_attr_t *, int);
int sa_handle_get(objset_t *, uint64_t, void *, int, sa_handle_t **);

/* Numeric case identity is closed so the reviewed runner can enumerate every
 * case without an unreviewed filter. Metadata cases80..115 are three objects
 * (home/probe/generated) times the12 attributes selected below. */
enum {
    SUCCESS,
    REVERSED_ENTRIES,
    EQUAL_LOWER_TIMES,
    ALPHABET_BOUNDARIES,
    DIFFERENT_OBJECT_IDS,
    PRISTINE,
    RECOVERY_AS_PRISTINE,
    PRISTINE_AS_RECOVERY,
    NULL_SPA,
    NULL_OUTPUT,
    UNKNOWN_RECOVERED,
    NEGATIVE_RECOVERED,
    EMPTY_WINDOW,
    WIDE_WINDOW,
    OVERFLOW_WINDOW,
    WRITABLE_SPA,
    SCRATCH_ALLOCATION,
    VIEW_ALLOCATION,
    ATTRIBUTE_ALLOCATION,
    FIRST_RETRIEVE,
    SECOND_RETRIEVE,
    END_RETRIEVE,
    MISSING_FIRST,
    MISSING_SECOND,
    EXTRA_ENTRY,
    DUPLICATE_PROBE,
    DUPLICATE_DIRECTORY,
    WRONG_PROBE_KIND,
    WRONG_DIRECTORY_KIND,
    UNKNOWN_NAME,
    WRONG_PREFIX,
    SHORT_NAME,
    LONG_NAME,
    EMBEDDED_NUL,
    SLASH_NAME,
    ALPHABET_AT,
    ALPHABET_Q,
    ALPHABET_BACKTICK,
    ALPHABET_q,
    ALPHABET_DIGIT,
    ALPHABET_HIGH,
    INTEGER_WIDTH,
    INTEGER_COUNT,
    RESERVED_DIRENT,
    ZERO_OBJECT,
    PROBE_BINDING,
    DIRECTORY_BINDING,
    PROBE_LOOKUP,
    DIRECTORY_LOOKUP,
    HOME_COUNT,
    DIRECTORY_NONEMPTY,
    HIDDEN_OBJECT,
    MISSING_ORIGINAL_OBJECT,
    REPEATED_OBJECT,
    ORIGINAL_PAYLOAD,
    ORIGINAL_METADATA_DIGEST,
    HANDLE_ACQUISITION,
    STALE_METADATA_GENERATION,
    EOF_ERROR,
    EOF_NONEMPTY,
    EOF_STALE,
    ACL_OVERSIZE,
    HOME_BIRTH,
    PROBE_MTIME,
    DIRECTORY_MTIME,
    HOME_FINAL_TIME,
    PROBE_BEFORE_HOME,
    DIRECTORY_BEFORE_PROBE,
    TIME_LOWER,
    TIME_UPPER,
    TIME_NANOS,
    TIME_CTIME,
    TIME_ATIME,
    ROOT_CTIME,
    ROOT_MTIME,
    ROOT_LINKS,
    ROOT_MODE,
    ROOT_COUNT,
    ROOT_SIZE,
    LOOKUP_LOAD_ERROR,
    META_FIRST,
    CASE_COUNT = META_FIRST + 36
};
static unsigned fault, cursor_live, attribute_live, cursor_calls;
static unsigned advances, finishes, attribute_frees, spa_queries, kmem_calls;
static unsigned probe_loads, eof_observed, metadata_staled;
static unsigned char *workspace;
static zap_attribute_t entries[3];
static char generated_name[9];
static uint64_t generated_object(void) { return nodes[11].object; }
#define CHECK(value, marker)                                                   \
    do {                                                                       \
        if (!(value)) {                                                        \
            fprintf(stderr, "HOME_MKTEMP_%s case=%u line=%d\n", marker, fault, \
                    __LINE__);                                                 \
            exit(1);                                                           \
        }                                                                      \
    } while (0)

void *kmem_zalloc(size_t bytes, int flags)
{
    ++kmem_calls;
    if ((fault == SCRATCH_ALLOCATION && kmem_calls == 1) ||
        (fault == VIEW_ALLOCATION && kmem_calls == 2))
        return NULL;
    void *out = baseline_kmem_zalloc(bytes, flags);
    if (bytes >= 4096)
        workspace = out;
    return out;
}
int spa_writeable(spa_t *spa)
{
    ++spa_queries;
    return baseline_spa_writeable(spa);
}
int zap_lookup(objset_t *os, uint64_t object, const char *name, uint64_t width,
               uint64_t count, void *out)
{
    if (recovered && object == home_object()) {
        if (fault == PROBE_LOOKUP && !strcmp(name, "probe"))
            return EIO;
        if (!strcmp(name, generated_name)) {
            if (fault == DIRECTORY_LOOKUP)
                return EIO;
            uint64_t value = (UINT64_C(4) << 60) | generated_object();
            CHECK(width == 8 && count == 1, "LOOKUP_GEOMETRY");
            memcpy(out, &value, 8);
            return 0;
        }
    }
    return baseline_zap_lookup(os, object, name, width, count, out);
}
int zap_count(objset_t *os, uint64_t object, uint64_t *out)
{
    if (recovered && object == home_object()) {
        *out = fault == HOME_COUNT ? 1 : 2;
        return 0;
    }
    if (recovered && object == generated_object()) {
        *out = fault == DIRECTORY_NONEMPTY ? 1 : 0;
        return 0;
    }
    int error = baseline_zap_count(os, object, out);
    if (recovered && fault == ROOT_COUNT && object == 34)
        ++*out;
    return error;
}
int sa_handle_get(objset_t *os, uint64_t object, void *user, int kind,
                  sa_handle_t **out)
{
    if (recovered && fault == HANDLE_ACQUISITION &&
        object == generated_object())
        return EIO;
    return baseline_sa_handle_get(os, object, user, kind, out);
}
int sa_bulk_lookup(sa_handle_t *h, sa_bulk_attr_t *attrs, int count)
{
    if (recovered && h->object == probe_object() && count == 6) {
        ++probe_loads;
        if (probe_loads == 2) {
            ++eof_observed;
            CHECK(workspace && workspace[0] == 0, "NONZERO_EOF_READ");
            if (fault == EOF_ERROR)
                return EIO;
            if (fault == EOF_NONEMPTY)
                nodes[10].value[ZPL_SIZE][0] = 1;
            if (fault == EOF_STALE)
                ++nodes[10].value[ZPL_GEN][0];
        }
    }
    if (recovered && h->object == generated_object()) {
        if (fault == LOOKUP_LOAD_ERROR && count == 6)
            return EIO;
        if (fault == STALE_METADATA_GENERATION && count == 14 &&
            !metadata_staled) {
            ++nodes[11].value[ZPL_GEN][0];
            ++metadata_staled;
        }
    }
    return baseline_sa_bulk_lookup(h, attrs, count);
}
zap_attribute_t *zap_attribute_alloc(void)
{
    if (fault == ATTRIBUTE_ALLOCATION)
        return NULL;
    zap_attribute_t *out = calloc(1, sizeof(*out));
    if (out)
        ++attribute_live;
    return out;
}
void zap_attribute_free(zap_attribute_t *entry)
{
    CHECK(attribute_live == 1 && !cursor_live, "ATTRIBUTE_RELEASE");
    --attribute_live;
    ++attribute_frees;
    free(entry);
}
void zap_cursor_init(zap_cursor_t *cursor, objset_t *os, uint64_t object)
{
    CHECK(!cursor_live && attribute_live == 1 && owns == 1 &&
              object == home_object(),
          "CURSOR_ACQUIRE");
    *cursor = (zap_cursor_t){os, object, 0};
    ++cursor_live;
}
void zap_cursor_advance(zap_cursor_t *cursor)
{
    CHECK(cursor_live == 1 && cursor->index < 2, "CURSOR_ADVANCE_BOUND");
    ++cursor->index;
    ++advances;
}
int zap_cursor_retrieve(zap_cursor_t *cursor, zap_attribute_t *entry)
{
    CHECK(cursor_live == 1 && cursor->os == &dataset &&
              cursor->object == home_object() && cursor_calls < 3,
          "CURSOR_RETRIEVE_BOUND");
    ++cursor_calls;
    if ((fault == FIRST_RETRIEVE && cursor->index == 0) ||
        (fault == SECOND_RETRIEVE && cursor->index == 1) ||
        (fault == END_RETRIEVE && cursor->index == 2))
        return EIO;
    if ((fault == MISSING_FIRST && cursor->index == 0) ||
        (fault == MISSING_SECOND && cursor->index == 1))
        return ENOENT;
    if (cursor->index == 2 && fault != EXTRA_ENTRY)
        return ENOENT;
    *entry = entries[cursor->index];
    return 0;
}
void zap_cursor_fini(zap_cursor_t *cursor)
{
    CHECK(cursor_live == 1 && cursor->os == &dataset, "CURSOR_FINISH");
    --cursor_live;
    ++finishes;
    memset(cursor, 0, sizeof(*cursor));
}

static void entry(zap_attribute_t *out, const char *name, uint64_t object,
                  unsigned kind)
{
    memset(out, 0, sizeof(*out));
    out->za_integer_length = 8;
    out->za_num_integers = 1;
    out->za_first_integer = ((uint64_t)kind << 60) | object;
    memcpy(out->za_name, name, strlen(name) + 1);
}
static void prepare(unsigned phase)
{
    selected = fault == DIFFERENT_OBJECT_IDS ? 2 : 0;
    initialize(phase);
    spa_queries = kmem_calls = cursor_calls = advances = finishes = 0;
    attribute_frees = probe_loads = eof_observed = metadata_staled = 0;
    workspace = NULL;
    pool.writable = 0;
    memcpy(generated_name,
           fault == ALPHABET_BOUNDARIES ? "t.APapPA" : "t.ABCdef", 9);
    if (!phase)
        return;
    fixture_objects = 12;
    nodes[11] = nodes[9];
    nodes[11].object = fault == DIFFERENT_OBJECT_IDS ? 212 : 112;
    nodes[11].value[ZPL_GEN][0] = 52;
    nodes[11].value[ZPL_PARENT][0] = home_object();
    nodes[11].value[ZPL_SIZE][0] = 2;
    nodes[11].value[ZPL_LINKS][0] = 2;
    nodes[9].value[ZPL_SIZE][0] = 4;
    nodes[9].value[ZPL_LINKS][0] = 3;
    nodes[10].value[ZPL_SIZE][0] = 0;
    for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t) {
        stamp(&nodes[10], t, 1791290042, 100);
        stamp(&nodes[11], t, 1791290043, 100);
    }
    stamp(&nodes[9], ZPL_MTIME, 1791290043, 100);
    stamp(&nodes[9], ZPL_CTIME, 1791290043, 100);
    if (fault == EQUAL_LOWER_TIMES) {
        stamp(&nodes[6], ZPL_MTIME, 1791290040, 0);
        stamp(&nodes[6], ZPL_CTIME, 1791290040, 0);
        for (unsigned i = 9; i < 12; ++i)
            for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t)
                stamp(&nodes[i], t, 1791290040, 0);
    }
    entry(&entries[0], "probe", probe_object(), 8);
    entry(&entries[1], generated_name, generated_object(), 4);
    entry(&entries[2], "extra", 999, 4);
    if (fault == REVERSED_ENTRIES) {
        zap_attribute_t temporary = entries[0];
        entries[0] = entries[1];
        entries[1] = temporary;
    }
    switch (fault) {
    case WRITABLE_SPA:
        pool.writable = 1;
        break;
    case DUPLICATE_PROBE:
        entries[1] = entries[0];
        break;
    case DUPLICATE_DIRECTORY:
        entries[0] = entries[1];
        break;
    case WRONG_PROBE_KIND:
        entries[0].za_first_integer ^= UINT64_C(12) << 60;
        break;
    case WRONG_DIRECTORY_KIND:
        entries[1].za_first_integer ^= UINT64_C(12) << 60;
        break;
    case UNKNOWN_NAME:
        memcpy(entries[0].za_name, "other", 6);
        break;
    case WRONG_PREFIX:
        entries[1].za_name[0] = 'u';
        break;
    case SHORT_NAME:
        entries[1].za_name[7] = 0;
        break;
    case LONG_NAME:
        entries[1].za_name[8] = 'A';
        break;
    case EMBEDDED_NUL:
        entries[1].za_name[4] = 0;
        break;
    case SLASH_NAME:
        entries[1].za_name[4] = '/';
        break;
    case ALPHABET_AT:
        entries[1].za_name[4] = '@';
        break;
    case ALPHABET_Q:
        entries[1].za_name[4] = 'Q';
        break;
    case ALPHABET_BACKTICK:
        entries[1].za_name[4] = '`';
        break;
    case ALPHABET_q:
        entries[1].za_name[4] = 'q';
        break;
    case ALPHABET_DIGIT:
        entries[1].za_name[4] = '0';
        break;
    case ALPHABET_HIGH:
        entries[1].za_name[4] = (char)0x80;
        break;
    case INTEGER_WIDTH:
        entries[1].za_integer_length = 4;
        break;
    case INTEGER_COUNT:
        entries[0].za_num_integers = 2;
        break;
    case RESERVED_DIRENT:
        entries[1].za_first_integer |= UINT64_C(1) << 48;
        break;
    case ZERO_OBJECT:
        entries[1].za_first_integer = UINT64_C(4) << 60;
        break;
    case PROBE_BINDING:
        entries[0].za_first_integer = (UINT64_C(8) << 60) | 2;
        break;
    case DIRECTORY_BINDING:
        entries[1].za_first_integer = (UINT64_C(4) << 60) | 34;
        break;
    case HIDDEN_OBJECT:
        selected = 25;
        break;
    case MISSING_ORIGINAL_OBJECT:
        selected = 24;
        break;
    case REPEATED_OBJECT:
        selected = 26;
        break;
    case ORIGINAL_PAYLOAD:
        selected = 22;
        break;
    case ORIGINAL_METADATA_DIGEST:
        selected = 18;
        stamp(&nodes[1], ZPL_CRTIME, 1620802862, 124);
        break;
    case ACL_OVERSIZE:
        selected = 33;
        break;
    case HOME_BIRTH:
        stamp(&nodes[9], ZPL_CRTIME, 1791290041, 99);
        stamp(&nodes[9], ZPL_ATIME, 1791290041, 99);
        break;
    case PROBE_MTIME:
        stamp(&nodes[10], ZPL_MTIME, 1791290042, 101);
        stamp(&nodes[10], ZPL_CTIME, 1791290042, 101);
        break;
    case DIRECTORY_MTIME:
        stamp(&nodes[11], ZPL_MTIME, 1791290043, 101);
        stamp(&nodes[11], ZPL_CTIME, 1791290043, 101);
        break;
    case HOME_FINAL_TIME:
        stamp(&nodes[9], ZPL_MTIME, 1791290044, 100);
        stamp(&nodes[9], ZPL_CTIME, 1791290044, 100);
        break;
    case PROBE_BEFORE_HOME:
        for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t)
            stamp(&nodes[10], t, 1791290040, 100);
        break;
    case DIRECTORY_BEFORE_PROBE:
        for (unsigned t = ZPL_ATIME; t <= ZPL_CRTIME; ++t)
            stamp(&nodes[11], t, 1791290041, 100);
        stamp(&nodes[9], ZPL_MTIME, 1791290041, 100);
        stamp(&nodes[9], ZPL_CTIME, 1791290041, 100);
        break;
    case TIME_LOWER:
        stamp(&nodes[11], ZPL_ATIME, 1791290039, 100);
        break;
    case TIME_UPPER:
        stamp(&nodes[11], ZPL_MTIME, 1791290100, 100);
        break;
    case TIME_NANOS:
        stamp(&nodes[11], ZPL_ATIME, 1791290043, 1000000000);
        break;
    case TIME_CTIME:
        stamp(&nodes[11], ZPL_CTIME, 1791290043, 99);
        break;
    case TIME_ATIME:
        stamp(&nodes[11], ZPL_ATIME, 1791290043, 99);
        break;
    case ROOT_CTIME:
        stamp(&nodes[6], ZPL_CTIME, 1791290041, 99);
        break;
    case ROOT_MTIME:
        stamp(&nodes[6], ZPL_MTIME, 1791290039, 100);
        break;
    case ROOT_LINKS:
        nodes[6].value[ZPL_LINKS][0] = 2;
        break;
    case ROOT_MODE:
        nodes[6].value[ZPL_MODE][0] = 040700;
        break;
    case ROOT_SIZE:
        nodes[6].value[ZPL_SIZE][0] = 3;
        break;
    default:
        break;
    }
    if (fault >= META_FIRST) {
        unsigned which = (fault - META_FIRST) / 12;
        unsigned field = (fault - META_FIRST) % 12;
        struct fixture_node *n = &nodes[9 + which];
        static const unsigned scalar[] = {ZPL_MODE,   ZPL_UID,    ZPL_GID,
                                          ZPL_PARENT, ZPL_LINKS,  ZPL_SIZE,
                                          ZPL_FLAGS,  ZPL_PROJID, ZPL_XATTR};
        if (field < 9)
            n->value[scalar[field]][0] ^= 1;
        else if (field == 9)
            n->acl[2].z_access_mask ^= 1;
        else if (field == 10)
            n->value[ZPL_DACL_COUNT][0] = 2;
        else
            n->value[ZPL_GEN][0] = 0;
    }
}

int main(int argc, char **argv)
{
    if (argc != 3)
        return 64;
    char *end = NULL;
    unsigned long parsed = strtoul(argv[1], &end, 10);
    if (!argv[1][0] || !end || *end || parsed >= CASE_COUNT)
        return 64;
    fault = (unsigned)parsed;
    reference = malloc(780248);
    FILE *input = fopen(argv[2], "rb");
    CHECK(reference && input && fread(reference, 1, 780248, input) == 780248 &&
              fgetc(input) == EOF,
          "REFERENCE_INPUT");
    fclose(input);
    unsigned saved_fault = fault;
    fault = SUCCESS;
    prepare(0);
    unsigned char pristine[40], result[40];
    memset(pristine, 0xa5, sizeof(pristine));
    CHECK(!aether_home_mktemp_readback(&pool, 0, 1791290040, 1791290100,
                                       pristine),
          "PRISTINE_RESULT");
    CHECK(!owns && !handles && !allocations && !cursor_live &&
              !attribute_live && !cursor_calls && object_calls == 10,
          "PRISTINE_CLEANUP_INVENTORY");
    for (unsigned i = 32; i < 40; ++i)
        CHECK(!pristine[i], "PRISTINE_ZERO_LEAF");
    fault = saved_fault;
    prepare(fault == PRISTINE || fault == PRISTINE_AS_RECOVERY ? 0 : 1);
    int expectation = fault == PRISTINE || fault == RECOVERY_AS_PRISTINE ? 0
                      : fault == UNKNOWN_RECOVERED                       ? 2
                      : fault == NEGATIVE_RECOVERED                      ? -1
                                                                         : 1;
    uint64_t minimum = 1791290040;
    uint64_t maximum = fault == EMPTY_WINDOW      ? minimum
                       : fault == WIDE_WINDOW     ? minimum + 61
                       : fault == OVERFLOW_WINDOW ? UINT64_MAX
                                                  : 1791290100;
    memset(result, 0xa5, sizeof(result));
    int error = aether_home_mktemp_readback(
        fault == NULL_SPA ? NULL : &pool, expectation, minimum, maximum,
        fault == NULL_OUTPUT ? NULL : result);
    int valid = fault <= PRISTINE || fault == ORIGINAL_METADATA_DIGEST;
    CHECK((error == 0) == valid, "READER_STATUS");
    if (!valid) {
        int expected =
            fault >= NULL_SPA && fault <= OVERFLOW_WINDOW ? EINVAL
            : fault == WRITABLE_SPA                       ? EROFS
            : fault >= SCRATCH_ALLOCATION && fault <= ATTRIBUTE_ALLOCATION
                ? ENOMEM
            : fault == MISSING_FIRST || fault == MISSING_SECOND ||
                    (fault >= META_FIRST && (fault - META_FIRST) / 12 == 1 &&
                     (fault - META_FIRST) % 12 == 4)
                ? ENOENT
            : fault == EOF_STALE                                    ? ESTALE
            : fault >= META_FIRST && (fault - META_FIRST) % 12 == 6 ? ENOTSUP
                                                                    : EIO;
        CHECK(error == expected, "EXACT_ERROR_IDENTITY");
    }
    if (valid) {
        CHECK((memcmp(pristine, result, 32) == 0) ==
                  (fault != ORIGINAL_METADATA_DIGEST),
              "PRESERVED_DIGEST");
        if (fault == PRISTINE)
            CHECK(!memcmp(pristine + 32, result + 32, 8), "PRISTINE_SENTINEL");
        else {
            CHECK(!memcmp(result + 32, generated_name, 8), "ACTUAL_LEAF");
            CHECK(cursor_calls == 3 && advances == 2 && finishes == 1 &&
                      attribute_frees == 1 && eof_observed == 1 &&
                      object_calls == 13,
                  "BOUNDED_COMPLETE_OBSERVATIONS");
        }
    } else if (fault != NULL_OUTPUT)
        for (unsigned i = 0; i < 40; ++i)
            CHECK(!result[i], "FAILURE_ALL40_ZERO");
    CHECK(!owns && !handles && !allocations && !cursor_live && !attribute_live,
          "ALL_OWNERSHIP_BALANCED");
    CHECK(finishes == attribute_frees && cursor_calls <= 3 && advances <= 2,
          "CURSOR_BALANCED_BOUNDED");
    if (fault >= NULL_SPA && fault <= OVERFLOW_WINDOW)
        CHECK(error == EINVAL && !spa_queries && !kmem_calls && !cursor_calls,
              "INVALID_BEFORE_IO");
    if (fault == ATTRIBUTE_ALLOCATION)
        CHECK(error == ENOMEM && !cursor_calls && !finishes,
              "ATTRIBUTE_FAILURE_NO_CURSOR");
    if (fault >= FIRST_RETRIEVE && fault <= EXTRA_ENTRY)
        CHECK(finishes == 1 && attribute_frees == 1 &&
                  cursor_calls ==
                      (fault == FIRST_RETRIEVE || fault == MISSING_FIRST ? 1U
                       : fault == SECOND_RETRIEVE || fault == MISSING_SECOND
                           ? 2U
                           : 3U),
              "CURSOR_ERROR_CLEANUP");
    if (fault >= EOF_ERROR && fault <= EOF_STALE)
        CHECK(eof_observed == 1 && probe_loads == 2, "ACTUAL_EOF_DENIAL");
    if (fault == STALE_METADATA_GENERATION)
        CHECK(metadata_staled == 1, "ACTUAL_METADATA_GENERATION_DENIAL");
    free(reference);
    printf("home mktemp case %u passed\n", fault);
    return 0;
}
