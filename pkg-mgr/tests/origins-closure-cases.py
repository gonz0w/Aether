#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic producer-side records and independent OC-H3 consumer oracles."""
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
RUN = Path(tempfile.mkdtemp(prefix='.pkg-mgr-live-origins-closure-', dir=REPO)).resolve()
INSPECTOR = REPO / 'tests/origins_closure.py'
RESULTS = []
print('origins-closure: retained_root=' + str(RUN), flush=True)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + chr(10)).encode('ascii')


def check(condition, message):
    if not condition:
        raise ValueError(message)


def build(name):
    root = RUN / name
    root.mkdir(mode=0o700)
    objects = root / 'objects'
    objects.mkdir(mode=0o700)
    inventory = {}

    def put(value):
        raw = value if isinstance(value, bytes) else encode(value)
        digest = hashlib.sha256(raw).hexdigest()
        path = objects / digest
        if not path.exists():
            path.write_bytes(raw)
        inventory[digest] = len(raw)
        return {'sha256':digest, 'size':len(raw)}

    profile = {'schema':'pkg-origins-review-profile-v1','purpose':'synthetic-host-fixture',
               'name':'oc-h3-fixture','build':'oc-h3-fixture','host':'oc-h3-fixture','target':'oc-h3-fixture'}
    if name == 'unsupported-profile':
        profile['purpose'] = 'native-aether'
    profile_ref = put(profile)
    tool = put(b'x'*16777216 if name == 'read-budget' else b'Synthetic SDK input; not a usable compiler.')
    sdk = {'schema':'pkg-origins-review-sdk-v1','purpose':'synthetic-host-fixture',
           'profile':profile_ref,'inputs':[{'name':'compiler','object':tool}]}
    if name == 'read-budget':
        sdk['inputs']=[{'name':'a','object':tool},{'name':'b','object':tool}]
    if name == 'sdk-profile-mismatch':
        sdk['profile'] = {'sha256':'0'*64,'size':0}
    if name == 'sdk-unknown-field':
        sdk['execute'] = 'forbidden'
    if name == 'object-limit':
        sdk['inputs'][0]['object'] = {'sha256':'1'*64,'size':16777217}
    if name == 'aggregate-limit':
        sdk['inputs'] = [{'name':'a','object':put(b'a'*16777216)},
                         {'name':'b','object':put(b'b'*16777216)}]
    sdk_ref = put(sdk)
    license_ref = put(b'Synthetic license text, not a redistribution approval.')
    review_blob = put(b'Synthetic observation, not an owner review.')
    evidence = {'schema':'pkg-origins-review-evidence-v1','kind':'synthetic','objects':[review_blob]}
    if name == 'claimed-approval':
        evidence['kind'] = 'approved'
    evidence_ref = put(evidence)
    extra_evidence = []
    if name == 'object-count-limit':
        for batch in range(9):
            refs = [put(('evidence-leaf-'+str(batch)+'-'+str(n)).encode()) for n in range(32)]
            extra_evidence.append(put({'schema':'pkg-origins-review-evidence-v1','kind':'synthetic','objects':sorted(refs,key=lambda r:r['sha256'])}))
    marker = root / 'must-not-exist'
    recipe = put(('$(shell touch ' + str(marker) + ')').encode())
    app_source = put(b'app source fixture')
    leaf_source = put(b'leaf source fixture')
    base = json.loads((REPO/'fixtures/origins-records/source.json').read_text())
    base.update(sdk=sdk_ref,build='oc-h3-fixture',host='oc-h3-fixture',target='oc-h3-fixture',
                licenses=[{'expression':'BSD-2-Clause','text':license_ref}],evidence=[evidence_ref])
    if extra_evidence:
        base['evidence'] = sorted(extra_evidence, key=lambda r:r['sha256'])
    base['inputs'][0]['object'] = recipe
    leaf_name = 'other/leaf' if name == 'explicit-namespace' else 'aether/leaf'
    leaf = copy.deepcopy(base)
    leaf.update(package=leaf_name)
    leaf['inputs'][1]['object'] = leaf_source
    if name == 'cyclic-graph':
        leaf['dependencies']=[{'package':'aether/app','record':{'sha256':'2'*64,'size':1},'role':'target'}]
    if name == 'target-mismatch':
        leaf['target']='other-target'
    leaf_ref=put(leaf)
    app=copy.deepcopy(base)
    app.update(package='aether/app',dependencies=[{'package':leaf_name,'record':leaf_ref,'role':'target'}])
    app['inputs'][1]['object']=app_source
    if name == 'map-conflict':
        app['dependencies'][0]['record']= {'sha256':'3'*64,'size':1}
    if name == 'build-dependency':
        app['dependencies'][0]['role']='build'
    if name == 'record-package-mismatch':
        app['package']='aether/wrong'
    if name == 'dual-role':
        app['dependencies'].append(dict(app['dependencies'][0],role='build'))
    catalog=[{'package':'aether/app','record':put(app)},{'package':leaf_name,'record':leaf_ref}]
    if name in ('cached-depth', 'edge-limit'):
        catalog=[]
        for n in range(34 if name == 'edge-limit' else 17):
            record=copy.deepcopy(base)
            record['inputs'][1]['object']=app_source
            record['package']='aether/p'+str(n).zfill(2)
            if name == 'cached-depth':
                prior=catalog
            elif n < 17:
                prior=[]
            elif n < 33:
                prior=catalog[:17]
            else:
                prior=catalog[17:33]
            record['dependencies']=[{'package':d['package'],'record':d['record'],'role':'target'} for d in prior]
            catalog.append({'package':record['package'],'record':put(record)})
    if name == 'deep-chain':
        catalog=[]
        dep=None
        for n in reversed(range(17)):
            record=copy.deepcopy(base)
            record['inputs'][1]['object']=app_source
            record['package']='aether/p'+str(n).zfill(2)
            record['dependencies']=[] if dep is None else [{'package':dep['package'],'record':dep['record'],'role':'target'}]
            dep={'package':record['package'],'record':put(record)}
            catalog.append(dep)
        catalog.sort(key=lambda item:item['package'])
    if name == 'unselected-package':
        catalog.append({'package':'aether/unselected','record':{'sha256':'5'*64,'size':1}})
    if name == 'missing-package':
        catalog=catalog[:1]
    if name == 'duplicate-package':
        catalog.append(catalog[0])
    if name == 'package-count-limit':
        catalog=[{'package':'aether/p'+str(n).zfill(2),'record':leaf_ref} for n in range(65)]
    release={'schema':'pkg-origins-review-release-v1','repository':'a'*64,
             'profile':profile_ref,'packages':catalog}
    if name == 'unknown-release-schema':
        release['schema']='origins-production-release-v1'
    release_ref=put(release)
    mapping=[{'package':'aether/app','local_name':'app'}, {'package':leaf_name,'local_name':'leaf'}]
    roots=['aether/app',leaf_name] if name == 'multiple-roots' else ['aether/app']
    if name in ('deep-chain','cached-depth','edge-limit'):
        mapping=[{'package':item['package'],'local_name':item['package'].split('/')[1]} for item in catalog]
        roots=['aether/p00' if name == 'deep-chain' else catalog[-1]['package']]
    if name == 'mapping-collision':
        mapping[1]['local_name']='app'
    if name == 'missing-mapping':
        mapping=mapping[:1]
    if name == 'extra-mapping':
        mapping.append({'package':'aether/unused','local_name':'unused'})
    if name == 'invalid-local-name':
        mapping[1]['local_name']='namespace/leaf'
    selection={'schema':'pkg-origins-review-selection-v1','release':release_ref,'roots':roots,'mapping':mapping}
    if name == 'wrong-selected-release':
        selection['release']={'sha256':'4'*64,'size':1}
    if name == 'empty-roots':
        selection['roots']=[]
    if name == 'unknown-selection-field':
        selection['start_services']=True
    raw=encode(selection)
    if name == 'duplicate-selection-key':
        raw=b'{"schema":"pkg-origins-review-selection-v1",'+raw[1:]
    selection_path=root/'selection.json'
    selection_path.write_bytes(raw)
    pin=hashlib.sha256(raw).hexdigest()
    if name == 'wrong-selection-pin':
        pin='0'*64
    (root/'selection.sha256').write_text(pin+chr(10))
    for kind, reference in [('source',app_source),('recipe',recipe),('sdk',tool),
                             ('license',license_ref),('evidence',review_blob),('profile',profile_ref)]:
        if name=='missing-'+kind:
            (objects/reference['sha256']).unlink()
    if name=='corrupt-source':
        p=objects/app_source['sha256'];data=p.read_bytes();p.write_bytes(bytes([data[0]^1])+data[1:])
    if name=='symlink-object':
        p=objects/app_source['sha256'];p.unlink();p.symlink_to(root/'selection.json')
    if name=='fifo-object':
        p=objects/app_source['sha256'];p.unlink();os.mkfifo(p,0o600)
    if name=='unsafe-root':
        objects.chmod(0o755)
    (root/'package-state-sentinel').write_bytes(b'no mutation')
    expected={'schema':'pkg-origins-closure-report-v1','status':'declared-closure-only',
              'selection_sha256':pin,'release_sha256':release_ref['sha256'],
              'packages':mapping,'dependency_edges':1,'object_count':len(inventory),
              'object_bytes':sum(inventory.values()),'sdk_count':1,'eligibility':'not-evaluated',
              'sdk_completeness':'not-proven','base_admission':'not-evaluated'}
    return root,objects,selection_path,pin,expected


def snapshot(root):
    import stat
    rows={}
    for p in sorted(root.rglob('*')):
        if p.name in ('stdout','stderr'):
            continue
        mode=p.lstat().st_mode
        value={'mode':mode}
        if stat.S_ISREG(mode):
            value['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        elif stat.S_ISLNK(mode):
            value['link']=os.readlink(p)
        rows[str(p.relative_to(root))]=value
    return rows


def main():
    cases=[('complete',None),('build-dependency',None),('explicit-namespace',None),
           ('multiple-roots',None),('unselected-package',None),
           ('map-conflict','release-map-conflict'),('missing-package','package-missing'),
           ('record-package-mismatch','package-conflict'),('dual-role','order-or-duplicate'),
           ('cyclic-graph','dependency-cycle'),('deep-chain','depth-limit'),
           ('cached-depth','depth-limit'),('edge-limit','edge-limit'),
           ('mapping-collision','mapping-collision'),('missing-mapping','mapping-incomplete'),
           ('extra-mapping','mapping-incomplete'),('invalid-local-name','format-invalid'),
           ('target-mismatch','profile-mismatch'),('unsupported-profile','profile-unsupported'),
           ('sdk-profile-mismatch','sdk-profile-mismatch'),('sdk-unknown-field','format-invalid'),
           ('claimed-approval','evidence-unsupported'),('object-limit','object-limit'),
           ('aggregate-limit','closure-limit'),('object-count-limit','closure-limit'),('read-budget','read-limit'),('duplicate-package','order-or-duplicate'),
           ('package-count-limit','format-invalid'),('unknown-release-schema','unsupported-schema'),
           ('wrong-selected-release','object-missing'),('empty-roots','format-invalid'),
           ('unknown-selection-field','format-invalid'),('duplicate-selection-key','duplicate-key'),
           ('wrong-selection-pin','identity-mismatch'),('corrupt-source','identity-mismatch'),
           ('fifo-object','file-type-invalid'),('symlink-object','IO-ERROR'),('unsafe-root','root-invalid')]
    cases += [('missing-'+name,'object-missing') for name in ('source','recipe','sdk','license','evidence','profile')]
    for name,code in cases:
        root,objects,selection,pin,expected=build(name)
        before=snapshot(root)
        argv=[sys.executable,'-B',str(INSPECTOR),str(objects),str(selection),pin]
        r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10,
                         env=dict(os.environ,LC_ALL='C',PYTHONDONTWRITEBYTECODE='1'),cwd=root)
        (root/'stdout').write_bytes(r.stdout);(root/'stderr').write_bytes(r.stderr)
        if code:
            status=1 if code=='IO-ERROR' else 2
            ok=r.returncode==status and not r.stdout and ('PKG-ORIGINS-CLOSURE-'+code.upper()+':').encode() in r.stderr
        else:
            ok=r.returncode==0 and not r.stderr and r.stdout==encode(expected)
        unchanged=snapshot(root)==before
        RESULTS.append({'case':name,'result':'pass' if ok and unchanged else 'fail',
                        'expected':code or expected,'exit':r.returncode,'command':argv,'unchanged':unchanged})
        check(ok and unchanged,'case failed: '+name)
    for option in ('--help','--version'):
        r=subprocess.run([sys.executable,'-B',str(INSPECTOR),option],capture_output=True,timeout=5)
        check(r.returncode==0 and r.stdout and not r.stderr,'help/version')
    r=subprocess.run([sys.executable,'-B',str(INSPECTOR)],capture_output=True,timeout=5)
    check(r.returncode==64 and not r.stdout and b'PKG-ORIGINS-CLOSURE-USAGE:' in r.stderr,'usage')
    print('PASS: '+str(len(RESULTS))+' declared-closure cases; no execution, trust or admission')


if __name__=='__main__':
    status=1
    try:
        main();status=0
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print('FAIL: '+str(error),file=sys.stderr)
    finally:
        paths=[INSPECTOR,REPO/'tests/origins_source_record.py',Path(__file__).resolve(),REPO/'fixtures/origins-records/source.json']
        (RUN/'result.json').write_text(json.dumps({'exit':status,'cases':RESULTS,'platform':platform.platform(),
            'python':sys.version,'inputs':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},indent=2))
    sys.exit(status)
