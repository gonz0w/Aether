#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic SDK transport/preservation witnesses; no real SDK qualification."""
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[1]
name = 'aether-musl-sdk'
count = 0
def sha(data):
    return hashlib.sha256(data).hexdigest()
def digest(path):
    return sha(path.read_bytes())
def run(args, status=0, env=None):
    result = subprocess.run([str(a) for a in args], cwd=repo,
                            env=dict(os.environ, **(env or {})), capture_output=True, timeout=60)
    assert result.returncode == status, (args, result.returncode, result.stdout, result.stderr)
    return result

def snapshot(root):
    result = {}
    for path in root.rglob('*'):
        if any(p.startswith('.binary-work.') for p in path.relative_to(root).parts):
            continue  # Killed invocation scratch is retained but never authority.
        info = path.lstat()
        result[path.relative_to(root).as_posix()] = (stat.S_IFMT(info.st_mode),
            stat.S_IMODE(info.st_mode), path.read_bytes() if path.is_file() else None)
    return result

with tempfile.TemporaryDirectory(prefix='.pkg-mgr-sdk-test.', dir=repo) as directory:
    work = Path(directory)
    def init(label):
        root=work/label; root.mkdir(mode=0o700)
        run(['make','-s','-f','mk/pkg.mk',f'ROOT={root}','init-root'])
        run(['sh','mk/state.sh','init',root])
        (root/'sentinel').write_bytes(b'unrelated\n')
        return root
    def source(label, receipt=b'synthetic build\n'):
        root=init(label); stage=root/'stage'/name
        metadata=stage/'usr/local/share/pkg-mgr'/name; metadata.mkdir(parents=True)
        (stage/'payload').write_bytes(b'synthetic SDK data\n')
        (stage/'payload').chmod(0o600)
        (metadata/'sdk-build-receipt').write_bytes(receipt)
        (metadata/'sdk-native-profile').write_bytes(b'synthetic native profile\n')
        target=metadata/'sdk-target.kv'
        target.write_text('format=cross-sdk-target-v1\nrole=build-inputs-only\n'
                          'build_os=FixtureOS\nbuild_arch=fixture64\ncompiler_target=fixture-none\n'
                          f'build_receipt_sha256={digest(metadata/"sdk-build-receipt")}\n'
                          f'native_profile_sha256={digest(metadata/"sdk-native-profile")}\n'
                          'modes=recorded-0000-0777\n')
        evidence=work/(label+'-inputs');evidence.mkdir()
        manifest=evidence/'manifest';run(['sh','mk/verify-metadata.sh','manifest',stage,manifest])
        template=(repo/'fixtures/metadata-boundary/build-input.kv').read_text().splitlines()
        replacements={'package_name':name,'manifest_ref':str(manifest.relative_to(repo))}
        (evidence/'input').write_text('\n'.join(k+'='+replacements.get(k,v) for k,v in
                                    (line.split('=',1) for line in template))+'\n')
        run(['sh','mk/verify-metadata.sh','build-record',evidence/'input',evidence/'build'])
        (evidence/'deps').write_bytes(b'')
        run(['sh','mk/state.sh','register',root,manifest,evidence/'build',evidence/'deps'])
        pin=digest(target)
        result=run(['sh','mk/binary.sh','sdk-export',root,name,pin])
        bundle=root/'binaries'/name
        assert result.stdout==f'sdk-exported\t{name}\t{digest(bundle/"artifact.kv")}\n'.encode()
        return root,bundle,pin
    original,bundle,pin=source('source')
    descriptor=digest(bundle/'artifact.kv')
    def invoke(action,root,selected=bundle,expected=pin,status=0,env=None):
        return run(['sh','mk/binary.sh',action,root,selected,digest(selected/'artifact.kv'),expected],status,env)
    def reject(label,selected=bundle,expected=pin,root=None,action='sdk-import'):
        global count
        root=root or init(label)
        before=snapshot(root)
        result=invoke(action,root,selected,expected,status=1)
        assert result.stdout==b'',(label,result.stdout)
        assert before==snapshot(root),label
        assert not list(root.glob('.binary-work.*')),label
        count+=1
    fresh=init('fresh')
    r=invoke('sdk-import',fresh)
    assert r.stdout==f'sdk-imported\t{name}\t{descriptor}\n'.encode()
    assert snapshot(original/'stage'/name)==snapshot(fresh/'stage'/name)
    assert (original/'state/packages'/f'{name}.tsv').read_bytes()==(fresh/'state/packages'/f'{name}.tsv').read_bytes()
    assert (fresh/'sentinel').read_bytes()==b'unrelated\n'
    count+=1
    reject('already-registered',root=fresh)
    before=snapshot(fresh)
    r=invoke('sdk-recover',fresh)
    assert r.stdout==f'sdk-recovered\t{name}\t{descriptor}\n'.encode()
    assert before==snapshot(fresh);count+=1
    r=run(['sh','mk/binary.sh','export',original,name],status=1)
    assert r.stdout==b'';count+=1
    reject('old-import-sdk',action='import',expected='fixture-none')
    reject('wrong-profile',expected='0'*64)
    occupied=init('occupied');(occupied/'stage'/name).mkdir(parents=True)
    (occupied/'stage'/name/'unrelated').write_bytes(b'keep')
    reject('occupied-stage',root=occupied)
    reject('missing-recovery-stage',action='sdk-recover')
    second,other,other_pin=source('substituted',b'changed synthetic build\n')
    assert other_pin!=pin
    reject('rehashed-substitution',selected=other,expected=pin)
    def mutated(label,change):
        selected=work/label;shutil.copytree(bundle,selected);change(selected)
        fields=(selected/'artifact.kv').read_text().splitlines()
        names={'record_sha256':'package.tsv','target_sha256':'target.kv','modes_sha256':'modes.tsv','dependencies_sha256':'dependencies.tsv'}
        (selected/'artifact.kv').write_text('\n'.join(k+'='+(digest(selected/names[k]) if k in names else v)
                                      for k,v in (line.split('=',1) for line in fields))+'\n')
        return selected
    selected=mutated('outer-target',lambda b:(b/'target.kv').write_bytes((b/'target.kv').read_bytes().replace(b'FixtureOS',b'ChangedOS')))
    reject('bound-target',selected, digest(selected/'target.kv'))
    payload=digest(original/'stage'/name/'payload')
    selected=mutated('corrupt',lambda b:(b/'files'/payload).write_bytes(b'X'*(b/'files'/payload).stat().st_size))
    reject('same-size-corruption',selected)
    selected=mutated('mode-change',lambda b:(b/'modes.tsv').write_text((b/'modes.tsv').read_text().replace('0600','0644')))
    reject('mode-table-mismatch',selected)
    selected=mutated('dependencies',lambda b:(b/'dependencies.tsv').write_text('missing\t'+'a'*64+'\n'))
    reject('nonempty-dependencies',selected)
    selected=mutated('wrong-format',lambda b:None)
    (selected/'artifact.kv').write_text((selected/'artifact.kv').read_text().replace('local-sdk-directory-v1','local-binary-directory-v2'))
    reject('sdk-rejects-v2',selected)
    selected=mutated('link',lambda b:(b/'files'/'link').symlink_to(b/'files'/payload))
    reject('link-payload',selected)
    selected=mutated('fifo',lambda b:os.mkfifo(b/'files'/'fifo'))
    reject('special-payload',selected)
    retained=init('retained');shutil.copytree(original/'stage'/name,retained/'stage'/name)
    (retained/'stage'/name/'payload').chmod(0o644)
    reject('retained-mode',root=retained,action='sdk-recover')
    (retained/'stage'/name/'payload').chmod(0o600)
    reject('retained-pin',root=retained,expected='0'*64,action='sdk-recover')
    before=snapshot(retained/'stage'/name)
    invoke('sdk-recover',retained)
    assert before==snapshot(retained/'stage'/name);count+=1
    # Plausible hash output with a failed status must not admit the SDK profile.
    hash_tools=work/'hash-tools';hash_tools.mkdir()
    wrapper=hash_tools/'sh'
    wrapper.write_text('''#!/bin/sh
if test "$#" -eq 3 && test "${1##*/}" = verify-metadata.sh && test "$2" = hash-file && test "$3" = "$HASH_TARGET"; then
    count=0
    if test -f "$HASH_COUNT"; then read -r count < "$HASH_COUNT"; fi
    count=$((count+1)); printf "%s\\n" "$count" > "$HASH_COUNT"
    "$REAL_SH" "$@" || exit
    if test "$count" -eq 2; then exit 73; fi
    exit 0
fi
exec "$REAL_SH" "$@"
''');wrapper.chmod(0o700)
    root=init('failed-profile-hash');before=snapshot(root)
    r=invoke('sdk-import',root,status=1,env={'PATH':str(hash_tools)+os.pathsep+os.environ['PATH'],
              'REAL_SH':shutil.which('sh'),'HASH_TARGET':str(bundle/'target.kv'),'HASH_COUNT':str(work/'hash-count')})
    assert r.stdout==b'' and snapshot(root)==before
    assert (work/'hash-count').read_text()=='2\n';count+=1
    # Kill the importing shell on a real publication move, before or after it.
    tools=work/'tools';tools.mkdir()
    wrapper=tools/'mv'
    wrapper.write_text('''#!/bin/sh
last=
for argument do last=$argument; done
if test "$last" = "$KILL_DEST"; then
    if test "$KILL_WHEN" = after; then "$REAL_MV" "$@" || exit; fi
    kill -KILL "$PPID"
    exit 73
fi
exec "$REAL_MV" "$@"
''');wrapper.chmod(0o700)
    for phase in ('before-stage','after-stage','after-record'):
        root=init('kill-'+phase)
        destination=root/('state/packages/'+name+'.tsv' if phase=='after-record' else 'stage/'+name)
        env={'PATH':str(tools)+os.pathsep+os.environ['PATH'],'REAL_MV':shutil.which('mv'),
             'KILL_DEST':str(destination),'KILL_WHEN':'before' if phase=='before-stage' else 'after'}
        r=invoke('sdk-import',root,status=-9,env=env)
        assert r.stdout==b''
        if phase=='before-stage':
            assert not (root/'stage'/name).exists()
            invoke('sdk-import',root)
        else:
            assert snapshot(root/'stage'/name)==snapshot(original/'stage'/name)
            invoke('sdk-recover',root)
        assert (root/'state/packages'/f'{name}.tsv').read_bytes()==(original/'state/packages'/f'{name}.tsv').read_bytes()
        assert (root/'sentinel').read_bytes()==b'unrelated\n';count+=1
    # A closed stdout cannot convert a committed operation into reported success.
    root=init('delivery')
    read_fd,write_fd=os.pipe();os.close(read_fd)
    try:
        r=subprocess.run(['sh','mk/binary.sh','sdk-import',str(root),str(bundle),descriptor,pin],
                         cwd=repo,stdout=write_fd,stderr=subprocess.PIPE,timeout=60)
    finally:os.close(write_fd)
    assert r.returncode==1,(r.returncode,r.stderr)
    assert (root/'state/packages'/f'{name}.tsv').read_bytes()==(original/'state/packages'/f'{name}.tsv').read_bytes()
    invoke('sdk-recover',root);count+=1
print(f'PASS: {count} synthetic SDK transport, rejection, recovery and interruption controls')
