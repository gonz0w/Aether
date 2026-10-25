/* SPDX-License-Identifier: BSD-2-Clause */
/* Original ZAP/SA own decoding. This bounded walk owns only path composition.
 */
static int context_name(aether_zpl_view *view, const aether_zpl_node *parent,
                        const aether_zpl_node *child, char name[256])
{
    uint64_t count = 0;
    int error = zap_count(view->os, parent->object, &count);
    if (error)
        return error;
    if (count > 4096 || parent->size != count + 2)
        return EIO;
    zap_cursor_t cursor;
    /* Upstream owns the flexible-array layout and its name-capacity field.
     * One standard (256-byte name) record is live per nonrecursive walk. */
    zap_attribute_t *entry = zap_attribute_alloc();
    unsigned found = 0;
    zap_cursor_init(&cursor, view->os, parent->object);
    for (uint64_t i = 0; i < count; ++i) {
        error = zap_cursor_retrieve(&cursor, entry);
        if (error)
            break;
        if (entry->za_integer_length != 8 || entry->za_num_integers != 1 ||
            ((entry->za_first_integer >> 48) & 0xfff)) {
            error = EIO;
            break;
        }
        if (ZFS_DIRENT_OBJ(entry->za_first_integer) == child->object) {
            size_t length = strnlen(entry->za_name, 256);
            if (!length || length > 255 || length == 256 ||
                strchr(entry->za_name, '/') || !strcmp(entry->za_name, ".") ||
                !strcmp(entry->za_name, "..") ||
                ZFS_DIRENT_TYPE(entry->za_first_integer) != IFTODT(S_IFDIR) ||
                ++found != 1) {
                error = EIO;
                break;
            }
            memcpy(name, entry->za_name, length + 1);
        }
        zap_cursor_advance(&cursor);
    }
    if (!error) {
        int end = zap_cursor_retrieve(&cursor, entry);
        if (end != ENOENT)
            error = end ? end : EIO;
    }
    zap_cursor_fini(&cursor);
    zap_attribute_free(entry);
    return error ? error : found == 1 ? 0 : ENOENT;
}

int aether_zpl_context(aether_zpl_view *view, uint64_t root,
                       uint64_t root_generation, uint64_t object,
                       uint64_t generation, unsigned char *path, size_t *length,
                       aether_zpl_node *parent_out)
{
    if (path)
        memset(path, 0, 256);
    if (length)
        *length = 0;
    if (parent_out)
        memset(parent_out, 0, sizeof(*parent_out));
    if (!view || !path || !length || !parent_out || !root || !root_generation ||
        !object || !generation)
        return EINVAL;
    if (view->root.object != root || view->root.generation != root_generation)
        return EACCES;
    aether_zpl_node boundary, current, first_parent = {0};
    uint64_t up = 0;
    int error = aether_zpl_load(view, root, &boundary, &up);
    if (error)
        return error;
    if (boundary.generation != root_generation)
        return ESTALE;
    if (!S_ISDIR(boundary.mode) || up != root)
        return EIO;
    error = aether_zpl_load(view, object, &current, &up);
    if (error)
        return error;
    if (current.generation != generation)
        return ESTALE;
    if (!S_ISDIR(current.mode))
        return ENOTDIR;
    unsigned char result[256] = {0};
    size_t start = 255;
    for (unsigned depth = 0; current.object != root; ++depth) {
        if (depth == 127)
            return ENAMETOOLONG;
        if (!up || up == current.object)
            return EIO;
        aether_zpl_node parent;
        uint64_t next = 0;
        error = aether_zpl_load(view, up, &parent, &next);
        if (error)
            return error;
        if (!S_ISDIR(parent.mode))
            return EIO;
        char component[256];
        error = context_name(view, &parent, &current, component);
        if (error)
            return error;
        size_t bytes = strlen(component);
        if (bytes + 1 > start)
            return ENAMETOOLONG;
        start -= bytes;
        memcpy(result + start, component, bytes);
        result[--start] = '/';
        if (!depth)
            first_parent = parent;
        current = parent;
        up = next;
    }
    if (current.generation != root_generation || up != root)
        return ESTALE;
    if (start == 255) {
        result[--start] = '/';
        first_parent = boundary;
    }
    size_t bytes = 256 - start;
    memcpy(path, result + start, bytes);
    *length = bytes;
    *parent_out = first_parent;
    return 0;
}
