/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_HOME_RECOVERY_HOST_H
#define AETHER_HOME_RECOVERY_HOST_H
/* Typed host substitutes, not an OpenZFS implementation or native witness. */
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#define B_FALSE 0
#define B_TRUE 1
#define KM_NOSLEEP 0
#define SA_HDL_PRIVATE 0
#define DMU_READ_NO_PREFETCH 0
#define DMU_OST_ZFS 1
#define MASTER_NODE_OBJ UINT64_C(1)
#define ZPL_VERSION_SA 5
#define ZFS_CASE_SENSITIVE 0
#define ZPL_VERSION_STR "VERSION"
#define ZFS_SA_ATTRS "SA_ATTRS"
#define ZFS_ROOT_OBJ "ROOT"
#define ZFS_UNLINKED_SET "DELETE_QUEUE"
#define ZFS_PROP_NORMALIZE 1
#define ZFS_PROP_CASE 2
#define ZFS_PROP_UTF8ONLY 3
#define ZFS_DIRENT_OBJ(v) ((v) & UINT64_C(0xffffffffffff))
#define ZFS_DIRENT_TYPE(v) ((v) >> 60)
#define IFTODT(v) (((v) & S_IFMT) >> 12)
#define ZFS_ARCHIVE UINT64_C(0x800000000)
#define ZFS_AV_MODIFIED UINT64_C(0x40000000000)
#define ZFS_PROJID UINT64_C(0x800000000000)
#define ZFS_XATTR UINT64_C(1)
#define ZFS_ACL_TRIVIAL UINT64_C(4)
#define ZFS_ACL_PROTECTED UINT64_C(16)
#define ACE_OWNER 0x1000
#define ACE_GROUP 0x2000
#define ACE_IDENTIFIER_GROUP 0x40
#define ACE_EVERYONE 0x4000
#define SHA256 1
#define SHA256_DIGEST_LENGTH 32
enum {
    DMU_OT_SA = 1,
    DMU_OT_DIRECTORY_CONTENTS,
    DMU_OT_PLAIN_FILE_CONTENTS,
    DMU_OT_MASTER_NODE,
    DMU_OT_SA_MASTER_NODE,
    DMU_OT_UNLINKED_SET,
    DMU_OT_SA_ATTR_REGISTRATION,
    DMU_OT_SA_ATTR_LAYOUTS
};
enum {
    ZPL_MODE,
    ZPL_GEN,
    ZPL_SIZE,
    ZPL_LINKS,
    ZPL_PARENT,
    ZPL_FLAGS,
    ZPL_UID,
    ZPL_GID,
    ZPL_ATIME,
    ZPL_MTIME,
    ZPL_CTIME,
    ZPL_CRTIME,
    ZPL_PROJID,
    ZPL_DACL_COUNT,
    ZPL_DACL_ACES,
    ZPL_XATTR,
    ZPL_END
};
typedef struct spa {
    int writable;
} spa_t;
typedef struct {
    int os_encrypted;
    spa_t *spa;
} objset_t;
typedef struct {
    objset_t *os;
    uint64_t object;
    unsigned index;
} zap_cursor_t;
typedef struct {
    uint64_t za_integer_length, za_num_integers, za_first_integer;
    char za_name[256];
} zap_attribute_t;
typedef unsigned sa_attr_type_t;
typedef struct {
    uint64_t object;
} sa_handle_t;
typedef struct {
    unsigned doi_type, doi_bonus_type;
} dmu_object_info_t;
typedef struct {
    unsigned attribute;
    void *data;
    size_t length;
} sa_bulk_attr_t;
typedef struct {
    uint16_t z_type, z_flags;
    uint32_t z_access_mask;
} zfs_ace_hdr_t;
typedef struct {
    size_t bytes;
    uint64_t observed;
    unsigned kind, exact;
} SHA2_CTX;
#define SA_ADD_BULK_ATTR(a, n, t, f, p, z)                                     \
    do {                                                                       \
        (void)(f);                                                             \
        (a)[(n)++] = (sa_bulk_attr_t){(t), (p), (z)};                          \
    } while (0)
extern const void *zfs_attr_table;
void *kmem_zalloc(size_t, int);
void kmem_free(void *, size_t);
int spa_writeable(spa_t *);
int dmu_objset_own(const char *, int, int, int, const void *, objset_t **);
void dmu_objset_disown(objset_t *, int, const void *);
spa_t *dmu_objset_spa(objset_t *);
int dmu_object_info(objset_t *, uint64_t, dmu_object_info_t *);
int dmu_object_next(objset_t *, uint64_t *, int, uint64_t);
int dmu_read(objset_t *, uint64_t, uint64_t, uint64_t, void *, unsigned);
int zap_lookup(objset_t *, uint64_t, const char *, uint64_t, uint64_t, void *);
int zap_count(objset_t *, uint64_t, uint64_t *);
zap_attribute_t *zap_attribute_alloc(void);
void zap_attribute_free(zap_attribute_t *);
void zap_cursor_init(zap_cursor_t *, objset_t *, uint64_t);
void zap_cursor_advance(zap_cursor_t *);
int zap_cursor_retrieve(zap_cursor_t *, zap_attribute_t *);
void zap_cursor_fini(zap_cursor_t *);
int zfs_get_zplprop(objset_t *, int, uint64_t *);
int sa_handle_get(objset_t *, uint64_t, void *, int, sa_handle_t **);
void sa_handle_destroy(sa_handle_t *);
int sa_bulk_lookup(sa_handle_t *, sa_bulk_attr_t *, int);
int sa_lookup(sa_handle_t *, sa_attr_type_t, void *, uint32_t);
int sa_size(sa_handle_t *, sa_attr_type_t, int *);
int sa_setup(objset_t *, uint64_t, const void *, int, sa_attr_type_t **);
void SHA2Init(unsigned, SHA2_CTX *);
void SHA2Update(SHA2_CTX *, const void *, size_t);
void SHA2Final(unsigned char *, SHA2_CTX *);
#endif
