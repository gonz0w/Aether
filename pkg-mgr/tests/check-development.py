#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline syntax/coverage checks; explicit changed-file ShellCheck gate."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_cases(root, inventory):
    """Check declared coverage locations, never infer executed outcomes."""
    cases = inventory.get('coverage_cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('empty critical-case inventory')
    surfaces = {item['id']: item for item in inventory['surfaces']}
    seen = set()
    for case in cases:
        required = ('id', 'surface', 'owner', 'family', 'stage', 'layer',
                    'test', 'anchor', 'oracle', 'forbidden', 'limits')
        if not isinstance(case, dict) or any(
                not isinstance(case.get(k), str) or not case[k].strip()
                for k in required):
            raise ValueError('incomplete critical case')
        if case['id'] in seen:
            raise ValueError('duplicate critical case: ' + case['id'])
        seen.add(case['id'])
        if case['surface'] not in surfaces:
            raise ValueError('unknown case surface: ' + case['id'])
        if case['stage'] not in ('before-merge', 'opt-in', 'release'):
            raise ValueError('unknown case stage: ' + case['id'])
        if case['layer'] not in ('host', 'model', 'target'):
            raise ValueError('unknown case layer: ' + case['id'])
        clauses = case.get('clauses')
        if not isinstance(clauses, list) or not clauses or any(
                not isinstance(c, str) or not c.strip() for c in clauses):
            raise ValueError('missing case requirements: ' + case['id'])
        path = (root / case['test']).resolve()
        if (not path.is_relative_to(root.resolve()) or not path.is_file()
                or case['test'] not in surfaces[case['surface']]['tests']):
            raise ValueError('unowned case test: ' + case['id'])
        if path.read_text().count(case['anchor']) != 1:
            raise ValueError('missing or ambiguous case anchor: ' + case['id'])
    return len(cases)


def check():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lint', nargs='+', metavar='PATH')
    parser.add_argument('--standards-source', type=Path, metavar='DIRECTORY',
                        help='read-only comparison with reviewed source hashes')
    parser.add_argument('--lint-all', action='store_true',
                        help='require lint for all active shell files')
    args = parser.parse_args()
    if args.standards_source is not None:
        review = json.loads((ROOT / 'docs/standards-review.json').read_text())
        for name, digest in review['files'].items():
            observed = hashlib.sha256(
                (args.standards_source / name).read_bytes()).hexdigest()
            if observed != digest:
                raise ValueError('REVIEW REQUIRED: standards changed: ' + name)
        print('PASS: reviewed standards source hashes match; no code executed')
    inventory = json.loads(
        (ROOT / 'docs/development-inventory.json').read_text())
    if inventory.get('schema') != 'pkg-mgr-development-inventory-v1':
        raise ValueError('unsupported development inventory')
    surfaces = inventory['surfaces']
    if not surfaces or len({s['id'] for s in surfaces}) != len(surfaces):
        raise ValueError('empty or duplicate surface inventory')
    case_count = check_cases(ROOT, inventory)
    covered = set()
    for surface in surfaces:
        for field in ('oracle', 'gap'):
            if not surface[field]:
                raise ValueError('missing scope: ' + surface['id'])
        for pattern in surface['sources']:
            matches = list(ROOT.glob(pattern))
            if not matches:
                raise ValueError('unmatched source pattern: ' + pattern)
            covered.update(matches)
        for field in ('references', 'tests'):
            if not surface[field]:
                raise ValueError('empty ' + field)
            for name in surface[field]:
                if not (ROOT / name).is_file():
                    raise ValueError('missing inventory destination: ' + name)
    sources = {ROOT / 'bin/pkg-mgr'}
    for directory in ('mk', 'recipes', 'tests'):
        sources.update(p for p in (ROOT / directory).rglob('*')
                       if p.suffix in ('.sh', '.py', '.awk', '.mk', '.c'))
    sources.update((ROOT / 'docs').glob('check-*.py'))
    if sources - covered:
        raise ValueError('uninventoried source: ' + ', '.join(
            str(p.relative_to(ROOT)) for p in sorted(sources - covered)))
    shell = []
    python = []
    for path in sorted(sources):
        if path.suffix == '.sh' or path == ROOT / 'bin/pkg-mgr':
            subprocess.run(['sh', '-n', str(path)], check=True, timeout=60)
            shell.append(path)
        elif path.suffix == '.py':
            ast.parse(path.read_text(), filename=str(path))
            python.append(path)
    # Active narrative only; historical/vendor/evidence bytes are immutable.
    documents = list((ROOT / 'docs').glob('*.md'))
    documents += [ROOT / 'README.md', ROOT / 'CONTRIBUTING.md',
                  ROOT / 'SECURITY.md']
    links = 0
    for path in documents:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            destination = (path.parent / target.split('#')[0]).resolve()
            if not destination.is_relative_to(ROOT):
                continue  # Sibling navigation is never a build dependency.
            if not destination.exists():
                raise ValueError(f'broken local link in {path.name}: {target}')
            links += 1
    print(f'PASS: {len(surfaces)} subsystem mappings, {len(shell)} sh and '
          f'{len(python)} Python syntax checks, {links} local file links',
          flush=True)
    print(f'PASS: {case_count} critical-case locations; execution is separate')
    if args.lint_all:
        args.lint = [str(p.relative_to(ROOT)) for p in shell]
    if args.lint:
        tool = shutil.which('shellcheck')
        if tool is None:
            raise ValueError('BLOCKED: ShellCheck 0.11.0 is required')
        version = subprocess.run([tool, '--version'], check=True,
                                 capture_output=True, text=True, timeout=60)
        if 'version: 0.11.0\n' not in version.stdout:
            raise ValueError('BLOCKED: reviewed ShellCheck version is 0.11.0')
        for name in args.lint:
            path = (ROOT / name).resolve()
            if path not in shell:
                raise ValueError('lint target outside active shell scope: '
                                 + name)
            subprocess.run([tool, '--norc', '--shell=sh', str(path)],
                           cwd=ROOT, check=True, timeout=60)
        print(f'PASS: ShellCheck 0.11.0 on {len(args.lint)} requested files')
    else:
        print('NOT RUN: ShellCheck; use --lint PATH ... for changed shell files')
    print('Scope: syntax and file references; no runtime/release certification')


if __name__ == '__main__':
    try:
        check()
    except (ValueError, KeyError, OSError, SyntaxError,
            subprocess.SubprocessError) as error:
        sys.exit(str(error))
