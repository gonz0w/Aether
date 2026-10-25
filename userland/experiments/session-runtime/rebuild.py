# SPDX-License-Identifier: BSD-2-Clause
"""Offline receipt-selected experimental rebuild; supports Python 3.10+."""
import hashlib
import json
from pathlib import Path
import types


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def validate_profile(recipe):
    """Validate the selected client compiles before executing a recipe."""
    profile = recipe['profile']
    if profile not in ('AENMX008/ABI23', 'AENMX009/ABI24', 'AENFS003/ABI29'):
        raise ValueError('unsupported bundle profile')
    filesystem = profile == 'AENFS003/ABI29'
    names = {'parent-runtime-compile', 'helper-runtime-compile'}
    if filesystem:
        names |= {'parent-application-compile', 'helper-application-compile'}
    steps = [step for step in recipe['commands'] if step['name'] in names]
    if len(steps) != len(names) or {s['name'] for s in steps} != names:
        raise ValueError('missing or duplicate client compilation')
    waiting = profile != 'AENMX008/ABI23'
    for step in steps:
        argv = step['argv']
        if (('-DSESSION_CHANNEL_WAIT' in argv) != waiting
                or '-DSESSION_SERIAL' not in argv):
            raise ValueError('runtime selection does not match bundle profile')
        if filesystem:
            expected = {'-DSESSION_CHANNEL_WAIT', '-DSESSION_SERIAL',
                        '-DSESSION_FS_ABI29'}
            if step['name'].startswith('helper-'):
                expected.add('-DSESSION_HELPER')
            selected = [arg for arg in argv if arg.startswith(
                ('-DSESSION_', '-USESSION_'))]
            if len(selected) != len(expected) or set(selected) != expected:
                raise ValueError('ABI29 client selector mismatch')
            if '-D' in argv or '-U' in argv:
                raise ValueError('split client selector unsupported')
    if not filesystem and any(
            'SESSION_FS_ABI29' in arg
            for step in recipe['commands'] for arg in step['argv']):
        raise ValueError('filesystem selector in legacy recipe')


def validate_fs_links(recipe, components):
    """Require the receipt to describe each actual linked object/archive."""
    for variant in ('parent', 'helper'):
        entries = recipe['components'][variant]
        required = components.required_components(recipe['profile'], variant)
        if set(entries) != required:
            raise ValueError('ABI29 link component inventory mismatch')
        steps = [s for s in recipe['commands']
                 if s['name'] == variant + '-link']
        if len(steps) != 1:
            raise ValueError('missing or duplicate ABI29 link')
        linked = [arg for arg in steps[0]['argv']
                  if arg.endswith(('.o', '.a'))]
        if (len(linked) != len(entries)
                or len(set(entries.values())) != len(entries)
                or set(linked) != set(entries.values())):
            raise ValueError('ABI29 link inputs do not match components')


def rebuild(bundle, output, expected_seal):
    """Build in a new owned directory; caller selects a reviewed manifest digest."""
    bundle, output = Path(bundle).resolve(), Path(output).resolve()
    if output.exists() or output.is_relative_to(bundle):
        raise ValueError('output must be a new directory outside the input bundle')
    seal = bundle / 'SHA256SUMS'
    if sha(seal) != expected_seal:
        raise ValueError('bundle seal mismatch')
    files = {}
    for line in seal.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = bundle / name
        if name in files or not path.resolve().is_relative_to(bundle) or path.is_symlink() or not path.is_file():
            raise ValueError('invalid bundle member')
        if sha(path) != digest:
            raise ValueError('bundle member mismatch: ' + name)
        files[name] = digest
    members = list(bundle.rglob('*'))
    if any(path.is_symlink() for path in members):
        raise ValueError('symlink in input bundle')
    actual = {str(path.relative_to(bundle)) for path in members if path.is_file() and path != seal}
    if actual != set(files):
        raise ValueError('unlisted or missing bundle input')
    recipe = json.loads((bundle / 'recipe.json').read_text())
    validate_profile(recipe)
    for tool in recipe['tools'].values():
        if sha(Path(tool['path']).resolve()) != tool['sha256']:
            raise ValueError('tool mismatch')
    # Execute the verified files directly. Global module caches/search paths must
    # not substitute an unpinned runner or skip required component admission.
    def load_support(name):
        path = bundle / 'support' / (name + '.py')
        selected = types.ModuleType('aether_session_bundle_' + name)
        selected.__file__ = str(path)
        exec(compile(path.read_bytes(), str(path), 'exec'), selected.__dict__)
        return selected

    process = load_support('process')
    components = load_support('components')
    clean_env, run, validate = process.clean_env, process.run, components.validate
    if recipe['profile'] == 'AENFS003/ABI29':
        validate_fs_links(recipe, components)
    output.mkdir(parents=True)
    (output / 'public-fork').mkdir()
    commands = []
    for step in recipe['commands']:
        argv = [v.replace('@bundle', str(bundle)).replace('@output', str(output)) for v in step['argv']]
        if step['name'].endswith('-link'):
            variant = step['name'].removesuffix('-link')
            receipt = {'schema': 'aether-session-components-v1', 'profile': recipe['profile'], 'components': []}
            if recipe['profile'] == 'AENFS003/ABI29':
                receipt['variant'] = variant
            for name, token in recipe['components'][variant].items():
                path = Path(token.replace('@bundle', str(bundle)).replace('@output', str(output)))
                receipt['components'].append({'name': name, 'path': str(path), 'sha256': sha(path)})
            validate(receipt, recipe['profile'])
            (output / (variant + '-components.json')).write_text(json.dumps(receipt, indent=2) + '\n')
        result = run(argv, cwd=bundle, env=clean_env(output), work=output, label=step['name'],
                     timeout=60, file_limit=16 * 1024**2)
        commands.append(result.record)
        (output / 'results.json').write_text(json.dumps({'status': 'incomplete', 'commands': commands}, indent=2) + '\n')
        if result.returncode or not result.record['complete'] or result.record['cleanup'] != 'complete':
            raise RuntimeError('bundle build failed: ' + step['name'])
    for name, digest in files.items():
        if sha(bundle / name) != digest:
            raise ValueError('bundle changed during build')
    results = {'status': 'pass', 'commands': commands, 'bundle_seal_sha256': expected_seal,
               'files_verified': len(files), 'profile': recipe['profile'], 'native': 'NOT RUN by this builder',
               'parent_sha256': sha(output / 'parent.elf'), 'helper_sha256': sha(output / 'helper.elf')}
    (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    return results
