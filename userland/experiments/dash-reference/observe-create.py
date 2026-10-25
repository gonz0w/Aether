#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Test-only real-create observer; asks the owned relay to cut, never starts guests."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
MODULE = runpy.run_path(str(HERE / 'container-process.py'))


def main():
    work = Path(sys.argv[1])
    config = json.loads((work / 'observer-input.json').read_text())
    class ObserverClient:
        # The fixture owns our inherited process group, including CLI descendants.
        sequence = 0

        def call(self, args, timeout=2):
            d = config['descriptor']
            if hashlib.sha256(Path(d['path']).read_bytes()).hexdigest() != d['sha256']:
                raise RuntimeError('observer client pin changed')
            self.sequence += 1
            label = 'query-' + str(self.sequence)
            argv = [d['path'], '--url', d['url'], '--identity', d['identity']] + args
            record = dict(argv=argv, timeout=timeout, scope='leader wait; '
                          'fixture owns enclosing process group', exit=None)
            try:
                with (work / (label + '.stdout')).open('wb') as output:
                    with (work / (label + '.stderr')).open('wb') as errors:
                        result = subprocess.run(argv, cwd=work,
                            env=MODULE['PROCESS']['clean_env'](work),
                            stdin=subprocess.DEVNULL, stdout=output,
                            stderr=errors, timeout=timeout)
                record['exit'] = result.returncode
                result.stdout = (work / (label + '.stdout')).read_bytes()
                result.record = {'complete': True}
                return result
            finally:
                (work / (label + '.json')).write_text(
                    json.dumps(record, indent=2) + '\n')

    client = ObserverClient()
    deadline = time.monotonic() + 12
    for _ in range(40):
        if time.monotonic() >= deadline:
            break
        result = MODULE['checked'](client.call([
            'container', 'exists', config['name']], timeout=2), (0, 1))
        if result.returncode == 0:
            found = MODULE['checked'](client.call([
                'container', 'inspect', config['name']], timeout=2))
            item = json.loads(found.stdout)[0]
            if (item['Name'].lstrip('/') != config['name']
                    or item['Config']['Labels'].get(MODULE['OWNER'])
                    != config['token']):
                raise RuntimeError('observer ownership mismatch')
            (work / 'witness.json').write_text(json.dumps(dict(
                name=config['name'], container_id=item['Id'],
                state=item['State']), indent=2) + '\n')
            (work / 'cut').write_text('created container observed\n')
            return
        time.sleep(0.05)
    raise RuntimeError('create effect not observed before deadline')


if __name__ == '__main__':
    main()
