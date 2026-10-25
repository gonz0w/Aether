// SPDX-License-Identifier: BSD-2-Clause
#include "vector.h"
#include <errno.h>
#include <stdint.h>
#include <string.h>

static struct tv_reply error(int value)
{
    return (struct tv_reply){1, 0, -value};
}
static struct tv_reply uncertain(struct tv_state *s)
{
    s->poisoned = 1;
    return (struct tv_reply){0, 0, -EIO};
}
struct tv_reply tv_write(struct tv_state *s, unsigned sink,
                         const struct tv_part *parts, unsigned count,
                         tv_send send, void *context)
{
    if (!s)
        return error(EINVAL);
    if (s->poisoned || s->busy)
        return uncertain(s);
    if (sink > 1)
        return error(EBADF);
    if (count > 2 || (count && !parts) || !send)
        return error(EINVAL);
    size_t total = 0;
    for (unsigned i = 0; i < count; i++) {
        if (parts[i].size > (size_t)PTRDIFF_MAX - total)
            return error(EINVAL);
        if (parts[i].size && !parts[i].data)
            return error(EFAULT);
        total += parts[i].size;
    }
    unsigned char bytes[16] = {0};
    size_t limit = total < sizeof(bytes) ? total : sizeof(bytes), used = 0;
    for (unsigned i = 0; i < count && used < limit; i++) {
        size_t n = parts[i].size < limit - used ? parts[i].size : limit - used;
        if (n)
            memcpy(bytes + used, parts[i].data, n);
        used += n;
    }
    s->busy = 1;
    struct tv_reply result = send(context, sink, bytes, limit);
    s->busy = 0;
    if (s->poisoned || result.known != 1 || result.error > 0 ||
        result.error < -4095 || result.count > limit ||
        (result.error && result.count))
        return uncertain(s);
    if (!result.error && !result.count && limit)
        return error(EIO);
    return result;
}
