/* SPDX-License-Identifier: BSD-2-Clause */
/* Reuse the actual existing host-only FD boundary fixture, not a second ledger.
 */
#define amk_tty_duplex_probe amk_tty_mode_probe
#define amk_test_tty_duplex_case amk_legacy_duplex_case
#define amk_tty_test_trap amk_legacy_tty_trap
#include "native-duplex-tests.c"
#undef amk_tty_test_trap
#undef amk_test_tty_duplex_case
#undef amk_tty_duplex_probe
#include <termios.h>
int aefd_test_tcgetattr(int, struct termios *);
int aefd_test_tcsetattr(int, int, const struct termios *);
long amk_tty_test_trap(unsigned long op, unsigned long cap, unsigned long a,
                       unsigned long b, unsigned long c)
{
    if ((op != 0x26000 && op != 0x26001 && op != 0x26004) || cap != 0xf001 ||
        a || b || c)
        return -EINVAL;
    ++traps;
    return -EACCES;
}
int amk_test_tty_mode_case(uint32_t kind)
{
    struct aefd_context *ctx = &aefd_shell_external_startup()->context;
    if (kind == 100) {
        errno = 0;
        if (aefd_test_tcgetattr(0, NULL) != -1 || errno != EFAULT)
            return 70;
        errno = 0;
        if (aefd_test_tcsetattr(0, TCSANOW, NULL) != -1 || errno != EFAULT)
            return 71;
        struct termios value;
        errno = 0;
        if (aefd_test_tcgetattr(15, &value) != -1 || errno != EBADF)
            return 72;
        ctx->map.slots[15] = (struct aefd_binding){AEFD_BIND_FILE, 3, 0, 0};
        errno = 0;
        int denied = aefd_test_tcgetattr(15, &value) == -1 && errno == ENOTTY;
        ctx->map.slots[15] = (struct aefd_binding){0};
        if (!denied)
            return 73;
        if (aefd_test_tcgetattr(0, &value))
            return 74;
        uint64_t revision = ctx->mode_revision;
        struct termios changed = value;
        changed.c_lflag |= ECHO;
        errno = 0;
        if (aefd_test_tcsetattr(0, TCSANOW, &changed) != -1 ||
            errno != EOPNOTSUPP)
            return 75;
        changed = value;
        changed.c_cc[VMIN] = 0;
        errno = 0;
        if (aefd_test_tcsetattr(0, TCSADRAIN, &changed) != -1 ||
            errno != EOPNOTSUPP)
            return 76;
        errno = 0;
        if (aefd_test_tcsetattr(0, TCSAFLUSH, &value) != -1 ||
            errno != EOPNOTSUPP)
            return 77;
        return ctx->mode_revision == revision ? 0 : 78;
    }
    if (kind == 101) {
        struct termios value;
        if (aefd_test_tcgetattr(2, &value))
            return 79;
        if (amk_tty_test_close(0))
            return 80;
        errno = 0;
        return aefd_test_tcgetattr(2, &value) == -1 && errno == EBADF ? 0 : 81;
    }
    if (kind == 102) {
        struct termios value;
        if (aefd_test_tcgetattr(0, &value))
            return 82;
        uint64_t revision = ctx->mode_revision;
        value.c_iflag |= ICRNL;
        errno = 0;
        if (aefd_test_tcsetattr(0, TCSANOW, &value) != -1 || errno != EIO ||
            ctx->client.live || ctx->mode_revision != revision)
            return 83;
        unsigned char before[sizeof(value)];
        memcpy(before, &value, sizeof(value));
        errno = 0;
        return aefd_test_tcgetattr(0, &value) == -1 && errno == EIO &&
                       !memcmp(before, &value, sizeof(value))
                   ? 0
                   : 84;
    }
    if (kind == 103) {
        struct termios saved, value;
        if (aefd_test_tcgetattr(0, &saved))
            return 85;
        value = saved;
        value.c_iflag |= ICRNL;
        if (aefd_test_tcsetattr(0, TCSANOW, &value))
            return 86;
        unsigned bits;
        if (aefd_context_mode(ctx, 0, 0x12, 0, 0, &bits) || bits)
            return 87;
        errno = 0;
        if (aefd_test_tcsetattr(0, TCSANOW, &value) != -1 || errno != EBADF)
            return 88;
        return aefd_test_tcgetattr(0, &value) == 0 &&
                       value.c_iflag == saved.c_iflag
                   ? 0
                   : 89;
    }
    if (kind == 104) {
        struct termios value, out;
        if (aefd_test_tcgetattr(0, &value))
            return 94;
        value.c_iflag |= ICRNL;
        if (aefd_test_tcsetattr(0, TCSANOW, &value))
            return 95;
        uint64_t revision = ctx->mode_revision;
        memset(&out, 0xa5, sizeof(out));
        errno = 0;
        if (aefd_test_tcgetattr(0, &out) != -1 || errno != EIO ||
            ctx->client.live || ctx->mode_revision != revision)
            return 96;
        for (unsigned i = 0; i < sizeof(out); ++i)
            if (((unsigned char *)&out)[i] != 0xa5)
                return 97;
        return 0;
    }
    if (kind >= 4)
        return amk_legacy_duplex_case(kind);
    creates = traps = 0;
    char *argv[] = {"mktemp", "-d", "/home/t.XXXXXX", NULL};
    int status = amk_tty_mode_probe(kind == 3 ? 2 : 3, argv);
    if (strcmp(argv[2], "/home/t.XXXXXX"))
        return 90;
    if (kind == 3)
        return status == 1 && !creates && !traps ? 0 : 91;
    if (creates != 1 || traps != 3)
        return 92;
    return status == (kind == 0 ? 0 : 1) ? 0 : 93;
}
