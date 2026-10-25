/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_PRIVATE_VECTOR_WRITE_H
#define AETHER_PRIVATE_VECTOR_WRITE_H
#include <sys/uio.h>
/* Include after transport.h. Private synchronous helper; all borrowed iovec
 * objects and nonempty spans must be readable and stable until return.
 * The existing transport owns authority, liveness and shared poison. This is
 * not a public writev implementation or an arbitrary-pointer validator. */
static long vector_write(int fd, const struct iovec *parts, int count)
{
    if (fd != 1 && fd != 2)
        return -EBADF;
    if (count < 0 || count > 2 || (count && !parts))
        return -EINVAL;
    size_t total = 0;
    for (int i = 0; i < count; i++) {
#ifndef VECTOR_SKIP_NULL
        if (parts[i].iov_len && !parts[i].iov_base)
            return -EFAULT;
#endif
        if (parts[i].iov_len > (size_t)SSIZE_MAX - total)
            return -EINVAL;
        total += parts[i].iov_len;
    }
    unsigned char bytes[16] = {0};
    size_t limit = total < sizeof bytes ? total : sizeof bytes, used = 0;
    for (int i = 0; i < count && used < limit; i++) {
        size_t n =
            parts[i].iov_len < limit - used ? parts[i].iov_len : limit - used;
        if (n)
            memcpy(bytes + used, parts[i].iov_base, n);
        used += n;
    }
#ifdef VECTOR_CORRUPT
    if (limit)
        bytes[0] ^= 1;
#endif
    long result = file_io(1, (unsigned long)fd, (uintptr_t)bytes, limit);
    return result == 0 && limit ? -EIO : result;
}
#endif
