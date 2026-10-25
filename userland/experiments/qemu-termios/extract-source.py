#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Extract pinned QEMU Linux-user build source, excluding unused firmware."""
import json
from pathlib import Path
import sys
import tarfile


def extract(archive, destination):
    excluded = []

    def selected(member, target):
        if member.name == 'qemu-10.0.11/roms' or member.name.startswith('qemu-10.0.11/roms/'):
            excluded.append(member.name)
            return None
        return tarfile.data_filter(member, target)

    with tarfile.open(archive) as source:
        source.extractall(destination, filter=selected)
    return excluded


if __name__ == '__main__':
    omitted = extract(sys.argv[1], '.')
    Path('excluded-firmware.json').write_text(json.dumps(omitted, indent=2) + '\n')
