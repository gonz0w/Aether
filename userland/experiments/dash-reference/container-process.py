# SPDX-License-Identifier: BSD-2-Clause
"""Recorded remote container lifecycle prototype; Python 3.10+."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import uuid

ROOT = Path(__file__).resolve().parents[2]
PROCESS = runpy.run_path(str(ROOT / 'experiments/command-runner/process.py'))
OWNER = 'org.aether.userland.attempt'


class BoundaryError(RuntimeError):
    pass


class Client:
    """Explicit trusted connection; descriptor contains no private-key bytes."""
    def __init__(self, descriptor, work):
        self.descriptor = dict(descriptor)
        self.work = Path(work).resolve()
        self.sequence = 0

    def call(self, args, timeout=20):
        d = self.descriptor
        if hashlib.sha256(Path(d['path']).read_bytes()).hexdigest() != d['sha256']:
            raise BoundaryError('client pin changed')
        self.sequence += 1
        return PROCESS['run'](
            [d['path'], '--url', d['url'], '--identity', d['identity']] + args,
            cwd=self.work, env=PROCESS['clean_env'](self.work), work=self.work,
            label=f'client-{self.sequence}', timeout=timeout,
            file_limit=16 * 1024**2,
        )


def checked(result, exits=(0,)):
    if not result.record['complete'] or result.returncode not in exits:
        raise BoundaryError('client execution incomplete or unexpected status')
    return result


def run_container(client, image, command, work, *, timeout=45, inputs=None,
                  generator_root=None, generator_cwd=None):
    """Run an isolated command; caller checks guest status after complete=True.

    Optional inputs are a read-only private build tree for dash guest tests.
    A trusted daemon and no competing resource mutation are assumed.
    """
    if not re.fullmatch('[0-9a-f]{64}', image):
        raise ValueError('immutable image ID required')
    if not command or not Path(command[0]).is_absolute():
        raise ValueError('absolute entrypoint required')
    options = []
    if (generator_root is None) != (generator_cwd is None):
        raise ValueError('paired generator root/cwd required')
    if generator_root is not None:
        if inputs is not None:
            raise ValueError('exclusive container mount modes required')
        tree = Path(generator_root).resolve(strict=True)
        target = Path(generator_cwd).resolve(strict=True)
        build_root = (ROOT / 'build').resolve()
        if (build_root not in tree.parents or tree not in target.parents
                or not tree.is_dir() or not target.is_dir()
                or any(c in str(tree) + str(target) for c in ',\n\r')):
            raise ValueError('private generator tree and child cwd required')
        options = [
            '--mount', 'type=bind,src=' + str(tree) + ',dst=' + str(tree)
            + ',ro=true',
            '--mount', 'type=bind,src=' + str(target) + ',dst=' + str(target)
            + ',rw=true', '--workdir', str(target),
        ]
    if inputs is not None:
        inputs = Path(inputs).resolve(strict=True)
        build_root = (ROOT / 'build').resolve()
        if (build_root not in inputs.parents or not inputs.is_dir()
                or any(c in str(inputs) for c in ',\n\r')):
            raise ValueError('private build input directory required')
        options = [
            '--tmpfs', '/scratch:rw,noexec,nosuid,size=16m,mode=1777',
            '--mount', 'type=bind,src=' + str(inputs) + ',dst=/inputs,ro=true',
            '--env', 'WITNESS=value', '--env', 'LC_ALL=C',
            '--env', 'PATH=/nonexistent',
        ]
    work = Path(work)
    token = uuid.uuid4().hex
    name = 'aether-ul077-' + token
    state = dict(name=name, token=token, image=image,
                 connection=client.descriptor, container_id=None,
                 create_attempted=False, create_confirmed=False,
                 cleanup='not-started', complete=False, failures=[])
    receipt = work / 'container.json'
    guest = None

    def save():
        receipt.write_text(json.dumps(state, indent=2) + '\n')

    def exists(ref):
        return checked(client.call(['container', 'exists', ref]), (0, 1))

    def inspect_owned():
        result = checked(client.call(['container', 'inspect', name]))
        try:
            rows = json.loads(result.stdout)
            row = rows[0] if len(rows) == 1 else {}
            ident = row.get('Id', '')
            valid = (re.fullmatch('[0-9a-f]{64}', ident)
                     and row.get('Name', '').lstrip('/') == name
                     and row.get('Config', {}).get('Labels', {}).get(OWNER)
                     == token)
            if not valid or (state['container_id'] is not None
                             and state['container_id'] != ident):
                raise BoundaryError('container ownership mismatch')
            return ident
        except (ValueError, TypeError, AttributeError, KeyError) as error:
            raise BoundaryError('invalid container inspection') from error

    save()
    try:
        if exists(name).returncode != 1:
            raise BoundaryError('attempt name already exists')
        state['create_attempted'] = True
        save()
        created = checked(client.call([
            'create', '--name', name, '--label', OWNER + '=' + token,
            '--pull=never', '--network=none', '--read-only', '--cap-drop=all',
            '--security-opt=no-new-privileges', '--user=65534:65534',
            '--memory=512m', '--pids-limit=32',
        ] + options + ['--entrypoint', command[0], image] + list(command[1:])))
        ident = created.stdout.decode('ascii').strip()
        if not re.fullmatch('[0-9a-f]{64}', ident):
            raise BoundaryError('invalid create response')
        state['container_id'] = ident
        state['create_confirmed'] = True
        save()
        inspect_owned()
        guest = client.call(['start', '--attach', ident], timeout=timeout)
        checked(guest, tuple(v for v in range(256)
                             if v not in (125, 126, 127)))
        (work / 'guest.stdout').write_bytes(guest.stdout)
        (work / 'guest.stderr').write_bytes(guest.stderr)
        state['guest_exit'] = guest.returncode
    except (BoundaryError, UnicodeError, OSError) as error:
        state['failures'].append(str(error))
    finally:
        if state['create_attempted']:
            try:
                if exists(name).returncode == 0:
                    ident = inspect_owned()
                    state['cleanup_id'] = ident
                    save()
                    checked(client.call(['rm', '--force', '--time', '1', ident]))
                if exists(name).returncode != 1:
                    raise BoundaryError('container name remains present')
                if (state['container_id'] is not None
                        and exists(state['container_id']).returncode != 1):
                    raise BoundaryError('container ID remains present')
                state['cleanup'] = ('absent' if state['create_confirmed']
                                    else 'unresolved-create')
            except (BoundaryError, UnicodeError, OSError) as error:
                state['cleanup'] = 'unresolved'
                state['failures'].append('cleanup: ' + str(error))
        state['complete'] = (guest is not None
                             and not state['failures']
                             and state['cleanup'] == 'absent')
        save()
    return state


def selected_descriptor(work):
    """Freeze the existing default connection before any container creation."""
    work = Path(work)
    tool = '/opt/homebrew/bin/podman'
    pin = hashlib.sha256(Path(tool).read_bytes()).hexdigest()
    result = PROCESS['run'](
        [tool, 'system', 'connection', 'list', '--format', 'json'],
        cwd=work, env=PROCESS['clean_env'](work), work=work,
        label='connection-selection', timeout=20, file_limit=1024**2,
    )
    checked(result)
    if hashlib.sha256(Path(tool).read_bytes()).hexdigest() != pin:
        raise BoundaryError('client changed during selection')
    rows = json.loads(result.stdout)
    selected = [row for row in rows if row.get('Default') is True]
    if len(selected) != 1:
        raise BoundaryError('one existing default connection required')
    row = selected[0]
    if (not isinstance(row.get('URI'), str)
            or not row['URI'].startswith('ssh://')
            or not isinstance(row.get('Identity'), str)
            or not Path(row['Identity']).is_absolute()):
        raise BoundaryError('explicit SSH connection and identity required')
    descriptor = dict(path=tool, sha256=pin, url=row['URI'],
                      identity=row['Identity'])
    (work / 'container-client.json').write_text(
        json.dumps(descriptor, indent=2) + '\n')
    return descriptor
