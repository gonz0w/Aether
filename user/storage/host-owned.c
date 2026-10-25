/* SPDX-License-Identifier: BSD-2-Clause */
/* Linux-only libzpool fixture. Never accepts a device or imported
 * configuration. */
#include <sys/zfs_context.h>
#include <sys/spa.h>
#include <sys/dmu.h>
#include <sys/dmu_objset.h>
#include <sys/txg.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char pool[] = "owned";
static const char dataset[] = "owned/data";
static const char path[] = "/work/owned/vdev.raw";
static char tag;
static void require(int ok, const char *reason)
{
    if (!ok) {
        fprintf(stderr, "OWNED FAIL: %s\n", reason);
        exit(1);
    }
}
static objset_t *own(void)
{
    objset_t *os = NULL;
    require(dmu_objset_own(dataset, DMU_OST_OTHER, B_FALSE, B_FALSE, &tag,
                           &os) == 0,
            "objset own");
    return os;
}
static void pattern(unsigned char *data, unsigned int version)
{
    for (size_t i = 0; i < 4096; ++i)
        data[i] = (unsigned char)(i * 17 + version * 53);
}
static void write_data(uint64_t *object, unsigned int version)
{
    objset_t *os = own();
    static unsigned char data[4096];
    pattern(data, version);
    dmu_tx_t *tx = dmu_tx_create(os);
    dmu_tx_hold_write(tx, *object ? *object : DMU_NEW_OBJECT, 0, sizeof(data));
    require(dmu_tx_assign(tx, DMU_TX_WAIT) == 0, "transaction assign");
    if (!*object)
        *object =
            dmu_object_alloc(os, DMU_OT_PLAIN_OTHER, 4096, DMU_OT_NONE, 0, tx);
    dmu_write(os, *object, 0, sizeof(data), data, tx, 0);
    dmu_tx_commit(tx);
    txg_wait_synced(dmu_objset_pool(os), 0);
    dmu_objset_disown(os, B_FALSE, &tag);
}
static void verify_data(uint64_t object, unsigned int version)
{
    objset_t *os = own();
    static unsigned char data[4096], expected[4096];
    pattern(expected, version);
#ifdef WRONG_EXPECTED
    expected[123] ^= 1;
#endif
    require(dmu_read(os, object, 0, sizeof(data), data, 0) == 0, "object read");
    require(memcmp(data, expected, sizeof(data)) == 0, "payload mismatch");
    dmu_objset_disown(os, B_FALSE, &tag);
}
static nvlist_t *restart(void)
{
    nvlist_t *config = NULL;
    char *packed = NULL;
    size_t size = 0;
    require(spa_export(pool, &config, B_FALSE, B_FALSE) == 0, "export");
    require(nvlist_pack(config, &packed, &size, NV_ENCODE_XDR, 0) == 0,
            "pack exported configuration");
    nvlist_free(config);
    /* packed is host malloc storage; no engine object survives shutdown. */
    kernel_fini();
    kernel_init(SPA_MODE_READ | SPA_MODE_WRITE);
    config = NULL;
    require(nvlist_unpack(packed, size, &config, 0) == 0,
            "unpack own configuration");
    free(packed);
    require(spa_import(pool, config, NULL, 0) == 0, "writable import");
    require(spa_import(pool, config, NULL, 0) == EEXIST,
            "duplicate import denial");
    return config;
}
int main(void)
{
    int fd =
        open(path, O_RDWR | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    require(fd >= 0, "new private file required");
    struct stat st;
    require(fstat(fd, &st) == 0 && S_ISREG(st.st_mode) && st.st_nlink == 1,
            "regular private file");
    require(flock(fd, LOCK_EX | LOCK_NB) == 0, "exclusive file lock");
    int other = open(path, O_RDWR | O_NOFOLLOW | O_CLOEXEC);
    require(other >= 0, "independent lock witness");
    require(flock(other, LOCK_EX | LOCK_NB) == -1 && errno == EWOULDBLOCK,
            "second lock denied");
    require(close(other) == 0, "close lock witness");
    require(ftruncate(fd, 256ULL << 20) == 0, "size new vdev");
    kernel_init(SPA_MODE_READ | SPA_MODE_WRITE);
    nvlist_t *leaf = fnvlist_alloc(), *root = fnvlist_alloc(),
             *props = fnvlist_alloc();
    fnvlist_add_string(leaf, ZPOOL_CONFIG_TYPE, VDEV_TYPE_FILE);
    fnvlist_add_string(leaf, ZPOOL_CONFIG_PATH, path);
    fnvlist_add_string(root, ZPOOL_CONFIG_TYPE, VDEV_TYPE_ROOT);
    const nvlist_t *children[] = {leaf};
    fnvlist_add_nvlist_array(root, ZPOOL_CONFIG_CHILDREN, children, 1);
    fnvlist_add_string(props, "cachefile", "none");
    require(spa_create(pool, root, props, NULL, NULL) == 0, "pool create");
    nvlist_free(leaf);
    nvlist_free(root);
    nvlist_free(props);
    require(dmu_objset_create(dataset, DMU_OST_OTHER, 0, NULL, NULL, NULL) == 0,
            "objset create");
    uint64_t object = 0;
    write_data(&object, 1);
    nvlist_t *config = restart();
    nvlist_free(config);
    verify_data(object, 1);
    write_data(&object, 2);
    config = restart();
    nvlist_free(config);
    verify_data(object, 2);
    require(spa_export(pool, &config, B_FALSE, B_FALSE) == 0, "final export");
    nvlist_free(config);
    kernel_fini();
    require(fsync(fd) == 0 && close(fd) == 0, "close owned file");
    puts("OWNED PASS: two writable imports, two verified payloads");
    return 0;
}
