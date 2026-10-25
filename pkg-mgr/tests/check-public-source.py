#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Assemble an explicitly listed, unpublished host-preview source candidate."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = ('docs/archive/', 'docs/evidence/', '.planning/', '.git/', '.jj/',
            'work/', 'stage/', 'logs/', 'distfiles/')
OMITTED = {'AGENTS.md', 'docs/PM-PRD-Initial-Research-Guidance.md',
           'docs/REVIEW-2026-09-05.md', 'docs/INTEGRATION-REVIEW-2026-09-05.md'}


def excluded(name):
    return name in OMITTED or name.startswith(EXCLUDED)


def file_record(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_mode & 0o7000:
        raise ValueError('non-ordinary source file: ' + str(path))
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'size': info.st_size, 'mode': f'{stat.S_IMODE(info.st_mode):04o}'}


def main():
    run = Path(tempfile.mkdtemp(prefix='pkg-public-source-')).resolve()
    print(f'retained_root={run}', flush=True)
    mappings = {}
    for row in (ROOT / 'release/files.tsv').read_text().splitlines():
        dest, source = row.split('\t')
        for name in (dest, source):
            if not re.fullmatch(r'[A-Za-z0-9_.+/-]+', name) or any(p in ('', '.', '..') for p in name.split('/')) or excluded(name):
                raise ValueError('unsafe or excluded allowlist path: ' + name)
        if dest in mappings:
            raise ValueError('duplicate allowlist destination: ' + dest)
        mappings[dest] = source
    if list(mappings) != sorted(mappings) or not mappings:
        raise ValueError('allowlist must be nonempty and sorted')
    sources = {}
    for name in set(mappings.values()):
        path = ROOT / name
        if any(parent.is_symlink() for parent in path.parents if parent != ROOT.parent):
            raise ValueError('source parent link: ' + name)
        sources[name] = file_record(path)
    (run / 'input-files.json').write_text(json.dumps(sources, indent=2, sort_keys=True) + '\n')
    stage = run / 'stage'
    stage.mkdir()
    edits = []
    available = set(mappings)
    available.update(str(p) for n in mappings for p in Path(n).parents)
    for name, source in mappings.items():
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = (ROOT / source).read_bytes()
        if name.endswith('.md') and not name.startswith('docs/vendor/'):
            def link(match):
                label, target = match.groups()
                if '://' in target or target.startswith('#'):
                    return match.group(0)
                destination = (path.parent / target.split('#')[0]).resolve()
                relative = str(destination.relative_to(stage)) if destination.is_relative_to(stage) else None
                if relative in available:
                    return match.group(0)
                if relative is not None and not excluded(relative):
                    raise ValueError(f'unresolved public document link: {name}: {target}')
                edits.append({'document': name, 'target': target, 'label': label})
                return label + ' (development reference omitted from this package)'
            text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, data.decode())
            if name.startswith('docs/'):
                text = '> Public candidate edition: development references may be omitted. Historical observations are not candidate acceptance evidence.\n\n' + text
            data = text.encode()
        path.write_bytes(data)
        path.chmod(int(sources[source]['mode'], 8))
    records = {n: file_record(stage / n) for n in sorted(mappings)}
    (run / 'documentation-edits.json').write_text(json.dumps(edits, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('snapshot', ROOT / 'tests/check-source-snapshot.py')
    snapshot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(snapshot)
    for name in ('source.tar', 'repeat.tar'):
        snapshot.assemble(stage, run / name, records)
    digest = hashlib.sha256((run / 'source.tar').read_bytes()).hexdigest()
    if hashlib.sha256((run / 'repeat.tar').read_bytes()).hexdigest() != digest:
        raise ValueError('public source archive repeat differs')
    extracted = run / 'extracted'
    extracted.mkdir()
    subprocess.run(['tar', '-xpf', str(run / 'source.tar'), '-C', str(extracted)], check=True, timeout=60)
    snapshot.verify(extracted / 'pkg-mgr', records)
    if any(file_record(ROOT / n) != value for n, value in sources.items()):
        raise ValueError('source changed during assembly')
    (run / 'result.json').write_text(json.dumps({'status': 'pass', 'files': len(records),
        'archive_sha256': digest, 'extracted_root': str(extracted / 'pkg-mgr'),
        'omitted_links': len(edits), 'scope': 'unpublished candidate; independent review and release gates pending'}, indent=2) + '\n')
    print(f'PASS: {len(records)} explicitly listed files; repeated archive and extracted bytes/modes match')


if __name__ == '__main__':
    main()
