#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Live test-only relay outage with exact owned-container recovery; Python 3.10+."""
import hashlib
import json
import os
import resource
import signal
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODULE = runpy.run_path(str(HERE / 'container-process.py'))
IMAGE = '8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4'


def observer_limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024**2, 16 * 1024**2))


def recover_owned(client, recorded):
    """Record recovery separately; never promote the original attempt."""
    if not recorded['create_attempted']:
        return dict(complete=True, scope='no create request; no recovery action')
    try:
        present = MODULE['checked'](client.call([
            'container', 'exists', recorded['name']]), (0, 1))
        if present.returncode == 1:
            return dict(complete=True, scope='observed absence only')
        found = MODULE['checked'](client.call([
            'container', 'inspect', recorded['name']]))
        item = json.loads(found.stdout)[0]
        if ((recorded['container_id'] is not None
             and item['Id'] != recorded['container_id'])
                or item['Name'].lstrip('/') != recorded['name']
                or item['Config']['Labels'].get(MODULE['OWNER'])
                != recorded['token']):
            raise RuntimeError('recovery ownership mismatch')
        MODULE['checked'](client.call([
            'rm', '--force', '--time', '1', item['Id']]))
        for ref in [recorded['name'], item['Id']]:
            MODULE['checked'](client.call(['container', 'exists', ref]), (1,))
        return dict(complete=True, container_id=item['Id'])
    except (RuntimeError, OSError, ValueError, KeyError, TypeError,
            IndexError, AttributeError) as error:
        return dict(complete=False, error=str(error))


def main(create_loss=False):
    work = Path(tempfile.mkdtemp(prefix='transport-loss-', dir=ROOT / 'build'))
    print(work, flush=True)
    direct = MODULE['selected_descriptor'](work)
    url = urlsplit(direct['url'])
    if url.hostname != '127.0.0.1' or url.port is None:
        raise ValueError('existing loopback SSH endpoint required')
    relay_source = HERE / 'transport-relay.py'
    argv = [sys.executable, '-B', str(relay_source), url.hostname,
            str(url.port), str(work / 'ready.json')]
    fault = work / 'fault'
    if create_loss:
        fault.mkdir()
        argv.append(str(fault))
    relay_record = dict(create_response_loss=create_loss, argv=argv, source_sha256=hashlib.sha256(
        relay_source.read_bytes()).hexdigest(), python=sys.version,
        executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes())
        .hexdigest())
    state = None
    recovery = {'complete': False}
    with (work / 'relay.stdout').open('wb') as stdout:
        with (work / 'relay.stderr').open('wb') as stderr:
            relay = subprocess.Popen(argv, cwd=work,
                                     env=MODULE['PROCESS']['clean_env'](work),
                                     stdin=subprocess.DEVNULL, stdout=stdout,
                                     stderr=stderr)
            relay_record['pid'] = relay.pid

            def stop():
                if relay.poll() is None:
                    relay.terminate()
                    try:
                        relay.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        relay.kill()
                        relay.wait(timeout=3)
                relay_record['exit'] = relay.returncode

            try:
                deadline = time.monotonic() + 5
                while not (work / 'ready.json').exists():
                    if relay.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('relay startup failed')
                    time.sleep(0.01)
                # Relay publishes its ready file atomically.
                port = json.loads((work / 'ready.json').read_text())['port']
                descriptor = dict(direct)
                descriptor['url'] = urlunsplit((url.scheme,
                    url.username + '@127.0.0.1:' + str(port), url.path, '', ''))

                class CutClient(MODULE['Client']):
                    def call(self, args, timeout=20):
                        if create_loss and args[0] == 'create':
                            relay_record['observer_source_sha256'] = hashlib.sha256(
                                (HERE / 'observe-create.py').read_bytes()).hexdigest()
                            config = dict(descriptor=direct,
                                name=args[args.index('--name') + 1],
                                token=args[args.index('--label') + 1].split('=', 1)[1])
                            (fault / 'observer-input.json').write_text(
                                json.dumps(config, indent=2) + '\n')
                            (fault / 'armed').write_text('delay server bytes\n')
                            with (fault / 'observer.stdout').open('wb') as output:
                                with (fault / 'observer.stderr').open('wb') as errors:
                                    watcher = subprocess.Popen([sys.executable, '-B',
                                        str(HERE / 'observe-create.py'), str(fault)],
                                        cwd=work, stdin=subprocess.DEVNULL,
                                        env=MODULE['PROCESS']['clean_env'](work),
                                        stdout=output, stderr=errors,
                                        start_new_session=True, preexec_fn=observer_limits)
                                    try:
                                        result = super().call(args, timeout=timeout)
                                        watcher.wait(timeout=15)
                                        relay_record['observer_exit'] = watcher.returncode
                                        return result
                                    finally:
                                        if MODULE['PROCESS']['alive'](watcher.pid):
                                            try:
                                                os.killpg(watcher.pid, signal.SIGKILL)
                                            except ProcessLookupError:
                                                pass
                                        watcher.wait(timeout=3)
                                        end = time.monotonic() + 5
                                        while (MODULE['PROCESS']['alive'](watcher.pid)
                                               and time.monotonic() < end):
                                            time.sleep(0.01)
                                        relay_record['observer_group_absent'] = not MODULE['PROCESS']['alive'](watcher.pid)
                                        if not relay_record['observer_group_absent']:
                                            raise RuntimeError('observer cleanup unresolved')
                        if not create_loss and args[0] == 'start':
                            stop()
                            relay_record['cut_before'] = list(args)
                        return super().call(args, timeout=timeout)

                attempt = work / 'attempt'
                attempt.mkdir()
                state = MODULE['run_container'](
                    CutClient(descriptor, attempt), IMAGE, ['/bin/true'], attempt)
            finally:
                stop()
                (work / 'relay.json').write_text(json.dumps(relay_record,
                                                           indent=2) + '\n')
                receipt = work / 'attempt/container.json'
                if receipt.exists():
                    recorded = json.loads(receipt.read_text())
                    restore = work / 'recovery'
                    restore.mkdir()
                    client = MODULE['Client'](direct, restore)
                    recovery = recover_owned(client, recorded)
                (work / 'recovery.json').write_text(json.dumps(recovery,
                                                              indent=2) + '\n')
    if (state is None or state['complete'] or state['cleanup'] != 'unresolved'
            or not recovery['complete']):
        raise RuntimeError('wrong transport-loss outcome')
    if create_loss:
        witness = json.loads((fault / 'witness.json').read_text())
        cut = json.loads((fault / 'relay-fault.json').read_text())
        if (not state['create_attempted'] or state['create_confirmed']
                or state['container_id'] is not None
                or recovery.get('container_id') != witness['container_id']
                or relay_record.get('observer_exit') != 0
                or not relay_record.get('observer_group_absent')
                or not cut['cut'] or cut['delayed_bytes'] == 0):
            raise RuntimeError('create response was not lost as required')
    elif not state['create_confirmed'] or 'cut_before' not in relay_record:
        raise RuntimeError('post-create cut was not reached')
    prefix = ('PASS: real create-response loss; ' if create_loss else
              'PASS: real post-create connection loss; ')
    print(prefix + 'unresolved receipt preserved; '
          'owned recovery and absence verified', flush=True)


if __name__ == '__main__':
    if sys.argv[1:] not in ([], ['--create-response']):
        raise ValueError('only --create-response is supported')
    main(create_loss=bool(sys.argv[1:]))
