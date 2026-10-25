#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check local coverage inventory and reviewed draft identity, offline."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate field: {key}")
        result[key] = value
    return result


def read_json(path):
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('inventory exceeds 1 MiB')
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def local(root, name):
    path = Path(name)
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError(f"unsafe inventory path: {name}")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink in inventory path: {name}")
    if not current.is_file():
        raise ValueError(f"missing inventory file: {name}")
    return current


def check(root):
    inventory = read_json(local(root, 'docs/workflow.json'))
    if inventory['status'] != 'local-process-pilot':
        raise ValueError('draft process must not claim released conformance')
    snapshot = local(root, inventory['review_manifest'])
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    if digest != inventory['review_manifest_sha256']:
        raise ValueError('review manifest changed without explicit re-review')
    review = read_json(snapshot)
    if review['status'] != 'unreleased-review-snapshot' or not review['files']:
        raise ValueError('missing or misclassified draft review')
    actual = {str(p.relative_to(snapshot.parent))
              for p in snapshot.parent.rglob('*') if p.is_file()}
    if actual != set(review['files']) | {'manifest.json'}:
        raise ValueError('review snapshot inventory mismatch')
    for name, expected in review['files'].items():
        data = local(snapshot.parent, name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'reviewed draft changed: {name}')
    approval = read_json(local(snapshot.parent, review['approval']))
    if approval['decision'] != 'approved-standards-content':
        raise ValueError('missing standards content approval')
    if not approval['files']:
        raise ValueError('empty approval inventory')
    for entry in approval['files']:
        if review['files'].get(entry['path']) != entry['sha256']:
            raise ValueError('approval and review content mismatch')
    references = {str(p.relative_to(root))
                  for p in (root / 'docs').glob('NATIVE-*.md')}
    if not references or references != set(inventory['interfaces']):
        raise ValueError('native reference coverage drift')
    tools = {str(p.relative_to(root)) for p in (root / 'scripts').glob('*.py')
             if '__main__' in p.read_text()}
    if not tools or tools != set(inventory['tools']):
        raise ValueError('developer CLI/build-tool coverage drift')
    for name, entry in inventory['interfaces'].items():
        local(root, name)
        if entry['status'] not in ('experimental-reference', 'proposal'):
            raise ValueError(f'unsupported reference status: {name}')
        if not entry['gap'] or not entry['validation']:
            raise ValueError(f'missing reference disposition: {name}')
    for name, entry in inventory['tools'].items():
        local(root, name)
        local(root, entry['reference'])
        if entry['manual'] not in ('blocked-not-written', 'excluded-internal'):
            raise ValueError(f'unreviewed manual state: {name}')
        if not entry['reason']:
            raise ValueError(f'missing manual disposition: {name}')
    tree = ast.parse(local(root, 'scripts/launch_smoke.py').read_text())
    profiles = {node.args[0].value for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == 'profiles'
                and node.func.attr == 'add_argument' and node.args
                and isinstance(node.args[0], ast.Constant)}
    if profiles != set(inventory['launch_profiles']):
        raise ValueError('native profile test-selection drift')
    for reference in inventory['launch_profiles'].values():
        if reference not in inventory['interfaces']:
            raise ValueError('profile lacks inventoried reference')
    ids = set()
    if not inventory['test_groups']:
        raise ValueError('empty test inventory')
    for group in inventory['test_groups']:
        if group['id'] in ids:
            raise ValueError('duplicate test ID')
        ids.add(group['id'])
        for field in ('invariants', 'command', 'oracle', 'gaps', 'owner'):
            if not group[field]:
                raise ValueError(f'missing test-group {field}')
        local(root, group['reference'])
        budget = group['budget_seconds']
        if type(budget) is not int or budget <= 0:
            raise ValueError('invalid test budget')
    return len(references), len(tools), len(ids)


if __name__ == '__main__':
    if sys.argv[1:] == ['--help']:
        print(__doc__ + '\nUsage: python3 scripts/check_workflow.py'
              '\nExits: 0/pass, 1/fail, 64/usage. See docs/DEVELOPMENT.md.')
        raise SystemExit(0)
    if sys.argv[1:] == ['--version']:
        print('aether-workflow-check 1')
        raise SystemExit(0)
    if len(sys.argv) != 1:
        print('usage: python3 scripts/check_workflow.py', file=sys.stderr)
        raise SystemExit(64)
    try:
        counts = check(ROOT)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        print(f'[FAIL] workflow: {error}', file=sys.stderr)
        raise SystemExit(1)
    print('[PASS] workflow: %d references, %d tools, %d test groups; '
          'approved content; release/runtime gates remain open' % counts)
