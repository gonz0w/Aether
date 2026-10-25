# SPDX-License-Identifier: BSD-2-Clause
"""Host pre-link admission controls, Python3.10+; no native execution."""
import copy
import hashlib
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    path = HERE / (name + '.py')
    module = types.ModuleType('test_selected_' + name)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


components = load('components')
builder = load('rebuild')


def recipe():
    commands = []
    mapping = {}
    for variant in ('parent', 'helper'):
        flags = ['-DSESSION_SERIAL', '-DSESSION_CHANNEL_WAIT',
                 '-DSESSION_FS_ABI29']
        if variant == 'helper':
            flags.append('-DSESSION_HELPER')
        for kind in ('runtime', 'application'):
            commands.append({'name': variant + '-' + kind + '-compile',
                             'argv': ['clang', *flags]})
        names = components.required_components(components.FS_PROFILE, variant)
        mapping[variant] = {name: '@output/' + variant + '-' + name + '.o'
                            for name in sorted(names)}
        commands.append({'name': variant + '-link',
                         'argv': ['clang', *mapping[variant].values(),
                                  '-o', '@output/' + variant + '.elf']})
    return {'profile': components.FS_PROFILE, 'commands': commands,
            'components': mapping}


class BuildAdmission(unittest.TestCase):
    def test_valid_variants_and_legacy(self):
        item = recipe()
        builder.validate_profile(item)
        builder.validate_fs_links(item, components)
        for profile in ('AENMX008/ABI23', 'AENMX009/ABI24'):
            old = copy.deepcopy(item)
            old['profile'] = profile
            for step in old['commands']:
                step['argv'] = [a for a in step['argv']
                                if a != '-DSESSION_FS_ABI29']
                if profile.endswith('ABI23'):
                    step['argv'] = [a for a in step['argv']
                                    if a != '-DSESSION_CHANNEL_WAIT']
            builder.validate_profile(old)

    def test_every_compile_requires_each_selector(self):
        for index in (0, 1, 3, 4):
            for flag in ('-DSESSION_FS_ABI29', '-DSESSION_SERIAL',
                         '-DSESSION_CHANNEL_WAIT'):
                item = recipe()
                item['commands'][index]['argv'].remove(flag)
                with self.subTest(index=index, flag=flag):
                    with self.assertRaises(ValueError):
                        builder.validate_profile(item)

    def test_overrides_helpers_and_duplicate_compiles(self):
        for flag in ('-USESSION_FS_ABI29', '-DSESSION_FS_ABI29=0',
                     '-DSESSION_CHANNEL_WAIT', '-DSESSION_SCRATCH', '-D'):
            item = recipe()
            item['commands'][0]['argv'].append(flag)
            with self.subTest(flag=flag):
                with self.assertRaises(ValueError):
                    builder.validate_profile(item)
        for index in (3, 4):
            item = recipe()
            item['commands'][index]['argv'].remove('-DSESSION_HELPER')
            with self.assertRaises(ValueError):
                builder.validate_profile(item)
        item = recipe()
        item['commands'].append(item['commands'][0])
        with self.assertRaises(ValueError):
            builder.validate_profile(item)

    def test_no_legacy_relabel(self):
        for profile in ('AENMX008/ABI23', 'AENMX009/ABI24', 'ABI29'):
            item = recipe()
            item['profile'] = profile
            with self.assertRaises(ValueError):
                builder.validate_profile(item)

    def test_link_inventory_is_actual_and_complete(self):
        for variant in ('parent', 'helper'):
            for name in components.required_components(
                    components.FS_PROFILE, variant):
                item = recipe()
                del item['components'][variant][name]
                with self.subTest(variant=variant, name=name):
                    with self.assertRaises(ValueError):
                        builder.validate_fs_links(item, components)
            for change in ('missing', 'extra', 'duplicate', 'substitution'):
                item = recipe()
                args = next(s['argv'] for s in item['commands']
                            if s['name'] == variant + '-link')
                if change == 'missing':
                    del args[1]
                elif change == 'extra':
                    args.append('@output/unlisted.o')
                elif change == 'duplicate':
                    args.append(args[1])
                else:
                    args[1] = '@output/foreign.o'
                with self.subTest(variant=variant, change=change):
                    with self.assertRaises(ValueError):
                        builder.validate_fs_links(item, components)

    def test_component_content_and_variant(self):
        root = HERE.parents[1] / 'build'
        with tempfile.TemporaryDirectory(prefix='fs-component-test-',
                                         dir=root) as directory:
            for variant in ('parent', 'helper'):
                entries = []
                for name in sorted(components.required_components(
                        components.FS_PROFILE, variant)):
                    path = Path(directory) / (variant + '-' + name)
                    path.write_bytes((variant + name).encode())
                    entries.append({'name': name, 'path': str(path),
                                    'sha256': hashlib.sha256(
                                        path.read_bytes()).hexdigest()})
                item = {'schema': 'aether-session-components-v1',
                        'profile': components.FS_PROFILE, 'variant': variant,
                        'components': entries}
                components.validate(item, components.FS_PROFILE)
                for failure in ('wrong-variant', 'duplicate', 'stale', 'alias'):
                    bad = copy.deepcopy(item)
                    if failure == 'wrong-variant':
                        bad['variant'] = 'unknown'
                    elif failure == 'duplicate':
                        bad['components'][-1] = bad['components'][0]
                    elif failure == 'stale':
                        bad['components'][0]['sha256'] = '0' * 64
                    else:
                        bad['components'][0]['path'] = entries[1]['path']
                        bad['components'][0]['sha256'] = entries[1]['sha256']
                    with self.subTest(variant=variant, failure=failure):
                        with self.assertRaises(ValueError):
                            components.validate(bad, components.FS_PROFILE)


if __name__ == '__main__':
    unittest.main()
