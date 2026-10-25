#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Record the installed macOS arm64 preview tools; never install or approve them."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

REQUIRED = ('sh', 'make', 'python3', 'shellcheck', 'cc', 'mandoc', 'man', 'tar',
            'awk', 'cat', 'chmod', 'cmp', 'cp', 'cut', 'date', 'dd', 'dirname',
            'env', 'find', 'grep', 'head', 'mkdir', 'mktemp', 'mv', 'od', 'pwd',
            'rm', 'sed', 'sort', 'tail', 'tee', 'tr', 'uname', 'wc',
            'xcrun', 'xcode-select', 'sw_vers')


def identity(path):
    resolved = Path(path).resolve(strict=True)
    return {'path': str(path), 'resolved': str(resolved),
            'sha256': hashlib.sha256(resolved.read_bytes()).hexdigest()}


def main():
    root = Path(tempfile.mkdtemp(prefix='pkg-host-setup-')).resolve()
    print(f'retained_root={root}', flush=True)
    report = {'status': 'incomplete', 'platform': platform.platform(), 'tools': {},
              'commands': [], 'environment': {k: os.environ.get(k) for k in
                                            ('DEVELOPER_DIR', 'SDKROOT', 'CC')},
              'scope': 'installed host observations; not pinned installation or release approval'}

    def run(command):
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        report['commands'].append({'argv': command, 'exit': result.returncode,
                                   'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise ValueError('required probe failed: ' + command[0])
        return result.stdout.strip()

    try:
        if platform.system() != 'Darwin' or platform.machine() != 'arm64':
            raise ValueError('this setup profile requires macOS arm64')
        if sys.version_info < (3, 10):
            raise ValueError('Python 3.10+ required')
        for name in REQUIRED:
            path = shutil.which(name)
            if path is None:
                raise ValueError('missing required tool: ' + name)
            report['tools'][name] = identity(path)
        hash_tool = next((shutil.which(n) for n in ('sha256sum', 'shasum', 'sha256', 'openssl') if shutil.which(n)), None)
        if hash_tool is None:
            raise ValueError('missing SHA-256 tool')
        report['hash_tool'] = identity(hash_tool)
        signer = shutil.which('minisign')
        report['minisign'] = identity(signer) if signer else 'NOT RUN: optional live signature fixture'
        version = run(['make', '--version'])
        match = re.search(r'GNU Make (\d+)\.(\d+)', version)
        if not match or tuple(map(int, match.groups())) < (3, 81):
            raise ValueError('GNU Make 3.81+ required')
        if 'version: 0.11.0' not in run(['shellcheck', '--version']).splitlines():
            raise ValueError('ShellCheck 0.11.0 required')
        run(['python3', '--version'])
        run(['cc', '--version'])
        run(['cc', '-dumpmachine'])
        run(['tar', '--version'])
        run(['sw_vers'])
        report['developer_directory'] = run(['xcode-select', '-p'])
        # Apple /usr/bin wrappers share bytes; also identify selected implementations.
        report['selected_tools'] = {name: identity(run(['xcrun', '--find', name]))
                                    for name in ('cc', 'make')}
        report['sdk_path'] = run(['xcrun', '--show-sdk-path'])
        report['sdk_version'] = run(['xcrun', '--show-sdk-version'])
        report['sdk_settings'] = identity(Path(report['sdk_path']) / 'SDKSettings.json')
        report['status'] = 'pass'
    except Exception as error:
        report['status'] = 'blocked'
        report['reason'] = str(error)
        raise
    finally:
        (root / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: required host tools observed, including selected Apple tools and SDK metadata')
    print('NOT RUN: tool installation reproducibility, complete SDK byte closure and independent review')


if __name__ == '__main__':
    main()
