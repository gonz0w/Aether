#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Ensure the developer handoff retains required policy and hook documentation."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile


def main():
    spec = importlib.util.spec_from_file_location(
        'snapshot', Path(__file__).with_name('check-source-snapshot.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='pkg-snapshot-policy-') as temporary:
        root = Path(temporary)
        for tree in module.TREES:
            (root / tree).mkdir()
        for name in module.FILES:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fixture\n')
        policy = root / 'SECURITY.md'
        policy.write_bytes(b'Private reporting instructions\n')
        hooks = root / '.githooks'
        hooks.mkdir(exist_ok=True)
        hook_readme = hooks / 'README.md'
        hook_readme.write_bytes(b'Explicit hook setup instructions\n')
        records = module.inventory(root)
        expected = hashlib.sha256(policy.read_bytes()).hexdigest()
        assert records.get('SECURITY.md', {}).get('sha256') == expected
        assert records.get('.githooks/README.md', {}).get('sha256') == hashlib.sha256(
            hook_readme.read_bytes()).hexdigest()
        hook_readme.unlink()
        hooks.rmdir()
        try:
            module.inventory(root)
        except ValueError as error:
            assert str(error) == 'missing or linked source tree: .githooks'
        else:
            raise AssertionError('missing hook tree accepted')
        hooks.mkdir()
        policy.unlink()
        try:
            module.inventory(root)
        except FileNotFoundError as error:
            assert Path(error.filename) == policy
        else:
            raise AssertionError('missing security policy accepted')
    print('PASS: policy and hook documentation bound; missing required inputs reject')


if __name__ == '__main__':
    main()
