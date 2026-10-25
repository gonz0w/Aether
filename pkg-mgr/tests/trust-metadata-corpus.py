#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Bounded deterministic source-record mutations; no network or target writes."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[1]
SEED = 20260906
rng = random.Random(SEED)
root = Path(tempfile.mkdtemp(prefix='pkg-source-corpus-')).resolve()
print(f'source-corpus: seed={SEED} retained_root={root}', flush=True)
target = root / 'target with spaces'
target.write_bytes((REPO / 'fixtures/sources/hello-local/hello.txt').read_bytes())
original = target.read_bytes()
rows = (REPO / 'fixtures/metadata-boundary/source.kv').read_text().splitlines()
cases = [('canonical', rows, None)]
# Each required field must be present once and have a nonempty value.
for index, row in enumerate(rows):
    key = row.split('=', 1)[0]
    cases.extend([
        ('missing-' + key, rows[:index] + rows[index + 1:],
         'missing required key: ' + key),
        ('duplicate-' + key, rows + [row], 'duplicate key: ' + key),
        ('empty-' + key, rows[:index] + [key + '='] + rows[index + 1:],
         'empty value for key: ' + key),
    ])
for index in range(16):
    shuffled = rows.copy()
    rng.shuffle(shuffled)
    cases.append((f'order-{index}', shuffled, None))
for index in range(16):
    key = 'unknown_' + ''.join(rng.choice('abcdef0123456789') for _ in range(12))
    cases.append((f'unknown-{index}', rows + [key + '=inert'], 'unknown key: ' + key))
for value in ('-1', '+105', '0105', '1e2', '105x'):
    cases.append(('size-' + value, [
        'source_size=' + value if r.startswith('source_size=') else r
        for r in rows], 'source_size must be decimal bytes'))
for length in (0, 1, 63, 65, 4096):
    # Empty values have a distinct syntax diagnostic.
    cases.append((f'hash-length-{length}', [
        'source_hash=' + 'a' * length if r.startswith('source_hash=') else r
        for r in rows], 'empty value for key: source_hash' if length == 0 else
        'source_hash must be 64 lowercase hexadecimal characters'))
marker = root / 'must-not-exist'
for index, value in enumerate((f'$(touch {marker})', f'`touch {marker}`',
                               ';touch ' + str(marker), 'x' * 65536)):
    cases.append((f'inert-uri-{index}', [
        'source_uri=' + value if r.startswith('source_uri=') else r
        for r in rows], None))
results = []
try:
    for index, (name, lines, diagnostic) in enumerate(cases):
        record = root / f'{index:03d}.kv'
        record.write_text('\n'.join(lines) + '\n')
        command = ['sh', str(REPO / 'mk/verify-metadata.sh'),
                   'verify-source', str(record), str(target)]
        result = subprocess.run(command, cwd=root, capture_output=True,
                                timeout=5, env=dict(os.environ, LC_ALL='C'))
        (root / f'{index:03d}.stdout').write_bytes(result.stdout)
        (root / f'{index:03d}.stderr').write_bytes(result.stderr)
        results.append({'name': name, 'command': command,
                        'expected_diagnostic': diagnostic,
                        'exit': result.returncode,
                        'input_sha256': hashlib.sha256(record.read_bytes()).hexdigest()})
        if diagnostic is None:
            assert result.returncode == 0, name
            assert result.stdout == f'result=pass label=source-bytes-match target={target}\n'.encode(), name
            assert result.stderr == b'', name
        else:
            assert result.returncode == 1, (name, result.returncode)
            assert result.stderr.decode().strip() == diagnostic, (name, result.stderr)
            assert result.stdout == f'result=fail label=source-metadata-invalid target={record}\n'.encode(), (name, result.stdout)
        assert target.read_bytes() == original, name
        assert not marker.exists(), name
    print(f'PASS: {len(cases)} deterministic source-record cases; seed={SEED}')
finally:
    (root / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
