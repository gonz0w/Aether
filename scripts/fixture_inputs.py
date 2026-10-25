# SPDX-License-Identifier: BSD-2-Clause
"""Read the small versioned consumer fixtures without historical test archives."""
import hashlib
import json
from pathlib import Path, PurePosixPath

from deps import ROOT


def read_inputs(packet, expected):
    if Path(packet).name != packet or packet in ('', '.', '..'):
        raise ValueError('invalid fixture name')
    directory = ROOT / 'tests/fixtures' / packet
    pins = json.loads((directory / 'pin.json').read_text())
    if pins != expected:
        raise RuntimeError('consumer fixture inventory drift')
    result = {}
    for name, digest in pins.items():
        parts = PurePosixPath(name)
        path = directory / name
        if (parts.is_absolute() or '..' in parts.parts
                or not path.resolve().is_relative_to(directory.resolve()) or path.is_symlink()):
            raise ValueError('unsafe fixture path')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise RuntimeError('consumer fixture input drift: ' + name)
        result[Path(name).name] = data
    return result
