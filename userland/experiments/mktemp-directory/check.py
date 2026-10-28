# SPDX-License-Identifier: BSD-2-Clause
"""Source-only producer library for issue97; no selected default execution route.

The separately reviewed private entry supplies the unchanged qualified process
owner, fixed aggregate clock and exact input freeze. Importing this file starts
nothing. This library never imports the legacy process.py helper.
"""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
USERLAND = HERE.parents[1]
ROOT = USERLAND.parent
HOOKS = ('-Dmkdtemp=amk_checked_mkdtemp', '-Dumask=amk_target_umask',
         '-D_exit=amk_target_terminal_exit')



def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def standalone_config(text):
    """Retain the existing cat recipe's exact hidden-TOYBOX correction."""
    require(text.count('CONFIG_TOYBOX=y') == 1 and text.splitlines().count('CONFIG_TOYBOX=y') == 1, 'standalone TOYBOX anchor changed')
    return text.replace('CONFIG_TOYBOX=y', '# CONFIG_TOYBOX is not set')


def effective_selection(config, expanded_table):
    require(config.count('CONFIG_MKTEMP=y') == 1 and config.splitlines().count('CONFIG_MKTEMP=y') == 1, 'MKTEMP must be enabled once')
    require('# CONFIG_TOYBOX is not set' in config and 'CONFIG_TOYBOX=y' not in config,
            'multiplexer must be disabled')
    active = set(re.findall(r'^CONFIG_([A-Z0-9_]+)=y$', config, re.M))
    require(all(name == 'MKTEMP' or name.startswith(('TOYBOX_', 'IS_')) for name in active),
            'another applet or unreviewed hidden selection is enabled')
    require(not {'TOYBOX_SUID', 'TOYBOX_HELP', 'TOYBOX_ZHELP'} & active,
            'unselected startup/help feature')
    require(re.fullmatch(r'\s*AMK_APPLET\s*\(\s*mktemp\s*\)\s*', expanded_table) is not None,
            'effective preprocessed applet table must contain exactly mktemp')
    return sorted(active)


def header_map(headers, inputs):
    """Closed host include roots; no SDK copy or claimed dylib closure."""
    require(isinstance(headers, dict) and headers, 'discovered header closure required')
    roots = (Path(inputs['host']['sdk']).resolve(),
             Path(inputs['tools']['clang']['path']).resolve().parents[1]/'lib/clang/21/include')
    for name in headers:
        path = Path(name)
        require(path == path.resolve() and any(path.is_relative_to(root) for root in roots),
                'header outside selected SDK/compiler roots')
    return headers


def generation_tools(inputs):
    selected = {name: inputs['tools'][name] for name in ('clang', 'gsed', 'bash', 'darwin-ld')}
    for item in selected.values():
        require(str(Path(item['path']).resolve()) == item['resolved_path'], 'generator tool alias target changed')
    return {item['resolved_path']: item['sha256'] for item in selected.values()}


def clean_env(work, rustc=None):
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work)}
    if rustc is not None:
        env['DYLD_LIBRARY_PATH'] = str(Path(rustc).parent.parent/'lib')
    return env


def generation_env(inputs, work, miniconfig):
    clang = inputs['tools']['clang']['path']
    sdk = inputs['host']['sdk']
    # CC must be one executable for portability.sh's command -v. HOSTCC is
    # expanded as words by upstream brun; all fixed paths have no whitespace.
    require(not any(c.isspace() for c in clang+sdk), 'fixed tool/SDK paths required')
    flags = '--no-default-config --target=arm64-apple-macos -isysroot '+sdk
    return dict(clean_env(work), CC=clang, HOSTCC=clang+' '+flags+' -MD -fuse-ld='+inputs['tools']['darwin-ld']['path'],
                CFLAGS=flags+' -O2 -fstack-protector-strong',
                CPUS='2', SED=inputs['tools']['gsed']['path'], VERSION='0.8.14',
                NOSTRIP='1', NOBUILD='1', LDOPTIMIZE='-Wl,-dead_strip',
                LDFLAGS='-fuse-ld='+inputs['tools']['darwin-ld']['path'],
                UNSTRIPPED=str(Path(work)/'generators'),
                KCONFIG_ALLCONFIG=str(miniconfig), KCONFIG_CONFIG='.config',
                GENDIR='generated', OUTNAME=str(Path(work)/'not-built'))


def generate(run, clock, tree, work, inputs):
    """Input preparation only, after a separately reviewed concrete entry GO."""
    env = generation_env(inputs, work, HERE/'miniconfig')
    bash = inputs['tools']['bash']['path']
    run('generate-config', [bash, 'scripts/genconfig.sh', '-n'], cwd=tree, env=env)
    clock.check_execution()
    config = Path(tree)/'.config'
    config.write_text(standalone_config(config.read_text()))
    run('generate-headers', [bash, 'scripts/make.sh'], cwd=tree, env=env)
    clock.check_execution()


def c_flags(inputs, tree=None):
    flags = ['--no-default-config', '--target=arm64-apple-macos', '-isysroot',
             inputs['host']['sdk'], '-O2', '-fstack-protector-strong']
    if tree is not None:
        flags += ['-I'+str(tree), '-funsigned-char', '-ffunction-sections',
                  '-fdata-sections', '-fno-asynchronous-unwind-tables',
                  '-fno-strict-aliasing', '-Werror=implicit-function-declaration',
                  '-Wno-deprecated-declarations', '-Wno-pointer-sign',
                  '-Wno-string-plus-int', '-Wno-invalid-source-encoding', *HOOKS]
    else:
        flags += ['-std=c17', '-Wall', '-Wextra', '-Werror', '-I'+str(HERE)]
    return flags


def depfile_paths(text, cwd):
    """Fixed whitespace-free host roots; reject unsupported escaped syntax."""
    logical = text.replace('\\\n', ' ')
    require(':' in logical, 'compiler dependency rule missing')
    _, body = logical.split(':', 1)
    require('\\' not in body and '$' not in body, 'unsupported dependency path encoding')
    paths = body.split()
    require(paths, 'nonempty compiler dependencies required')
    return {str((Path(cwd)/name).resolve()) for name in paths}


if __name__ == '__main__':
    raise SystemExit('mktemp-directory producer is not selected as a direct CLI; see README.md')
