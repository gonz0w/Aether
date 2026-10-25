/* SPDX-License-Identifier: BSD-2-Clause */
/* Original host-only oracle appended to generated QEMU translation fragments.
 */
int main(void)
{
    const unsigned int target_flags[] = {
        TARGET_CSTOPB, TARGET_CREAD,  TARGET_PARENB,  TARGET_PARODD,
        TARGET_HUPCL,  TARGET_CLOCAL, TARGET_CRTSCTS, MODEL_TARGET_CMSPAR};
    const unsigned int host_flags[] = {
        CSTOPB, CREAD,  PARENB,  PARODD,
        HUPCL,  CLOCAL, CRTSCTS, MODEL_HOST_CMSPAR};
    const unsigned int target_sizes[] = {TARGET_CS5, TARGET_CS6, TARGET_CS7,
                                         TARGET_CS8};
    const unsigned int host_sizes[] = {CS5, CS6, CS7, CS8};
    const size_t count = sizeof(cflag_tbl) / sizeof(cflag_tbl[0]);
    for (unsigned int size = 0; size < 4; ++size) {
        for (unsigned int bits = 0; bits < 256; ++bits) {
            unsigned int target = target_sizes[size];
            unsigned int host = host_sizes[size];
            for (unsigned int bit = 0; bit < 8; ++bit) {
                if ((bits & (1u << bit)) != 0) {
                    target |= target_flags[bit];
                    host |= host_flags[bit];
                }
            }
            unsigned int expected_host = host;
            unsigned int expected_target = target;
            if (!EXPECT_SUPPORT) {
                expected_host &= ~MODEL_HOST_CMSPAR;
                expected_target &= ~MODEL_TARGET_CMSPAR;
            }
            if (target_to_host_bitmask_len(target, cflag_tbl, count) !=
                    expected_host ||
                host_to_target_bitmask_len(host, cflag_tbl, count) !=
                    expected_target) {
                return 20;
            }
        }
    }
    return 0;
}
