# SPDX-License-Identifier: BSD-2-Clause
"""Fixed truncate-to-zero recovery oracle; no client policy or generic mutation API."""
from openzfs_fs_bridge import recovery_source

EMPTY_SHA256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'


def recovery(text):
    # The original seed identity and every metadata/ownership predicate are
    # checked by recovery_source before deriving this fixed zero-file variant.
    text = recovery_source(text, writer_60s=True, diagnostic=True)
    start = text.index('    while (!error && offset < 780248) {')
    end = text.index('    SHA2Final(digest, &hash);', start)
    text = text[:start] + text[end:]
    text = text.replace('    uint64_t offset = 0;\n', '', 1)
    start = text.index('    static const unsigned char expected[32] = {')
    end = text.index('};', start) + 2
    values = ', '.join('0x' + EMPTY_SHA256[i:i+2] for i in range(0, 64, 2))
    text = text[:start] + '    static const unsigned char expected[32] = {' + values + '};' + text[end:]
    text = text.replace('780248', '0')
    old = '         count))'
    if text.count(old) != 1:
        raise ValueError('zero recovery EOF context')
    text = text.replace(old, '''         count ||
         aether_zpl_read(view, 2, 47, 780248, buffer, sizeof(buffer), &count) ||
         count))''', 1)
    text = text.replace('Filled only from independent original-zdb extraction plus Python splice.',
                        'Fixed independently known SHA256 of empty content after truncate.')
    return text
