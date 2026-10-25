/* SPDX-License-Identifier: BSD-2-Clause */
/* Exact context getter body over deterministic upstream-operation doubles.
 * Separate target compilation checks the original OpenZFS header/types. */
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

typedef struct {
    uint64_t object, generation, size, mode;
} aether_zpl_node;
struct item {
    uint64_t parent;
    aether_zpl_node node;
    char name[256];
    int live;
};
struct graph {
    struct item items[132];
    unsigned total, fault;
};
typedef struct {
    struct graph *os;
    aether_zpl_node root;
} aether_zpl_view;
typedef struct {
    struct graph *graph;
    uint64_t directory;
    unsigned index;
} zap_cursor_t;
typedef struct {
    int za_integer_length, za_normalization_conflict;
    uint64_t za_num_integers, za_first_integer;
    uint32_t za_name_len, za_pad;
    char za_name[];
} zap_attribute_t;
static unsigned attribute_live;
static zap_attribute_t *zap_attribute_alloc(void)
{
    assert(attribute_live++ == 0);
    zap_attribute_t *a = calloc(1, sizeof(*a) + 256);
    assert(a);
    a->za_name_len = 256;
    return a;
}
static void zap_attribute_free(zap_attribute_t *a)
{
    assert(attribute_live-- == 1 && a->za_name_len == 256);
    free(a);
}
#define ZFS_DIRENT_OBJ(value) ((value) & ((UINT64_C(1) << 48) - 1))
#define ZFS_DIRENT_TYPE(value) ((value) >> 60)
#define IFTODT(mode) (((mode) & S_IFMT) >> 12)
static unsigned cursor_opens, cursor_closes;
static int aether_zpl_load(aether_zpl_view *view, uint64_t id,
                           aether_zpl_node *node, uint64_t *parent)
{
    if (!id || id > view->os->total || !view->os->items[id - 1].live)
        return ENOENT;
    *node = view->os->items[id - 1].node;
    *parent = view->os->items[id - 1].parent;
    return 0;
}
static unsigned matching(struct graph *g, uint64_t dir)
{
    unsigned n = 0;
    for (unsigned i = 1; i < g->total; ++i)
        if (g->items[i].live && g->items[i].parent == dir)
            ++n;
    return n;
}
static int zap_count(struct graph *g, uint64_t dir, uint64_t *count)
{
    *count = matching(g, dir);
    if (g->fault == 1)
        *count = 4097;
    return 0;
}
static void zap_cursor_init(zap_cursor_t *c, struct graph *g, uint64_t dir)
{
    *c = (zap_cursor_t){g, dir, 1};
    ++cursor_opens;
}
static int zap_cursor_retrieve(zap_cursor_t *c, zap_attribute_t *a)
{
    while (c->index < c->graph->total &&
           (!c->graph->items[c->index].live ||
            c->graph->items[c->index].parent != c->directory))
        ++c->index;
    if (c->index >= c->graph->total)
        return ENOENT;
    const struct item *item = &c->graph->items[c->index];
    assert(a->za_name_len == 256);
    memset(a->za_name, 0, a->za_name_len);
    a->za_integer_length = 8;
    a->za_num_integers = 1;
    a->za_first_integer =
        item->node.object | ((uint64_t)IFTODT(item->node.mode) << 60);
    memcpy(a->za_name, item->name, a->za_name_len);
    switch (c->graph->fault) {
    case 2:
        a->za_integer_length = 4;
        break;
    case 3:
        a->za_num_integers = 2;
        break;
    case 4:
        a->za_first_integer |= UINT64_C(1) << 50;
        break;
    case 5:
        memset(a->za_name, 'a', a->za_name_len);
        break;
    case 6:
        strcpy(a->za_name, "a/b");
        break;
    case 7:
        strcpy(a->za_name, "..");
        break;
    case 8:
        a->za_first_integer =
            (a->za_first_integer & ((UINT64_C(1) << 60) - 1)) |
            (UINT64_C(8) << 60);
        break;
    case 9:
        return EIO;
    default:
        break;
    }
    return 0;
}
static void zap_cursor_advance(zap_cursor_t *c) { ++c->index; }
static void zap_cursor_fini(zap_cursor_t *c)
{
    (void)c;
    ++cursor_closes;
}
#include "../../../user/storage/openzfs-volume/zpl-context.inc"

static struct graph graph;
static aether_zpl_view view;
static void reset(void)
{
    memset(&graph, 0, sizeof(graph));
    graph.total = 4;
    for (unsigned i = 0; i < graph.total; ++i) {
        graph.items[i].live = 1;
        graph.items[i].node =
            (aether_zpl_node){i + 1, 10 + i, 2, S_IFDIR | 0700};
    }
    graph.items[0].parent = 1;
    graph.items[1].parent = 1;
    graph.items[2].parent = 2;
    graph.items[3].parent = 1;
    graph.items[0].node.size = 4;
    graph.items[1].node.size = 3;
    graph.items[3].node.mode = S_IFREG | 0600;
    strcpy(graph.items[1].name, "work");
    strcpy(graph.items[2].name, "nested");
    strcpy(graph.items[3].name, "file");
    view = (aether_zpl_view){&graph, graph.items[0].node};
    cursor_opens = cursor_closes = 0;
}
static int query(uint64_t id, uint64_t generation, const char *expected,
                 int code)
{
    unsigned char out[256];
    memset(out, 0xa5, sizeof(out));
    size_t length = 999;
    aether_zpl_node parent;
    memset(&parent, 0xa5, sizeof(parent));
    int result =
        aether_zpl_context(&view, 1, 10, id, generation, out, &length, &parent);
    assert(result == code);
    assert(cursor_opens == cursor_closes && attribute_live == 0);
    if (!code) {
        assert(length == strlen(expected) + 1 &&
               !memcmp(out, expected, length));
        for (size_t i = length; i < 256; ++i)
            assert(out[i] == 0);
        assert(parent.object == graph.items[id - 1].parent);
    } else {
        assert(length == 0 && parent.object == 0 && parent.generation == 0 &&
               parent.size == 0 && parent.mode == 0);
        for (unsigned i = 0; i < 256; ++i)
            assert(out[i] == 0);
    }
    return result;
}
int main(void)
{
    reset();
    query(1, 10, "/", 0);
    query(2, 11, "/work", 0);
    query(3, 12, "/work/nested", 0);
    strcpy(graph.items[1].name, "renamed");
    query(3, 12, "/renamed/nested", 0);
    reset();
    query(3, 99, 0, ESTALE);
    query(4, 13, 0, ENOTDIR);
    graph.items[2].live = 0;
    query(3, 12, 0, ENOENT);
    for (unsigned fault = 1; fault <= 9; ++fault) {
        reset();
        graph.fault = fault;
        query(3, 12, 0, EIO);
    }
    reset();
    graph.items[1].parent = 2;
    query(2, 11, 0, EIO);
    reset();
    graph.items[0].parent = 2;
    query(3, 12, 0, EIO);
    reset();
    graph.items[1].node.size = 2;
    query(3, 12, 0, EIO);
    reset();
    memset(graph.items[1].name, 'x', 254);
    graph.items[1].name[254] = 0;
    char maximum[256];
    maximum[0] = '/';
    memset(maximum + 1, 'x', 254);
    maximum[255] = 0;
    query(2, 11, maximum, 0);
    graph.items[1].name[254] = 'x';
    graph.items[1].name[255] = 0;
    query(2, 11, 0, ENAMETOOLONG);
    reset();
    graph.items[2].node.object = 2;
    graph.items[2].parent = 1;
    graph.items[1].node.size = 2;
    graph.items[0].node.size = 5;
    query(2, 11, 0, EIO); /* Duplicate directory link. */
    reset();
    graph.items[1].parent = 3;
    graph.items[2].parent = 2;
    graph.items[0].node.size = 3;
    graph.items[1].node.size = 3;
    graph.items[2].node.size = 3;
    query(2, 11, 0,
          ENAMETOOLONG); /* Non-self cycle, bounded without recursion. */
    reset();
    view.root.generation = 99;
    unsigned char out[256];
    size_t length = 99;
    aether_zpl_node parent = {0};
    assert(aether_zpl_context(&view, 1, 10, 3, 12, out, &length, &parent) ==
               EACCES &&
           !length);
    puts("directory-context original body:24 scenarios pass");
    return 0;
}
