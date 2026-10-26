# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic association protocol controls; real artifact execution is separate.

Opaque synthetic members and receipt text test validation only. PINS is replaced
only inside this fixture; no synthetic compiler/guest is ever executed.
"""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fs_consumer_association as association
import fs_host_dependencies as dependencies
import fs_launch_intake as launch
import fs_metadata_launch as metadata
import openzfs_elapsed as elapsed

PRIVATE=Path('/Users/cam/DEV/Aether')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Association(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='aether-association-')
        self.addCleanup(temporary.cleanup);self.out=Path(temporary.name).resolve()
        self.environment=patch.dict(os.environ,{},clear=False);self.environment.start();self.addCleanup(self.environment.stop)
        for name in (association.ENV_PATH,association.ENV_SHA,dependencies.ENV):os.environ.pop(name,None)
        self.tool=self.out/'zig';self.tool.write_bytes(b'synthetic unexecuted host tool identity\n')
        self.producer={}
        for suffix in ('c','rs','h','o','a'):
            path=self.out/('provider.'+suffix);path.write_bytes(('synthetic '+suffix).encode());self.producer[str(path)]=sha(path)
        self.producer[str(self.tool)]=sha(self.tool)
        for relative in association.PRODUCER_EDITS:
            self.producer[str(PRIVATE/relative)]=sha(PRIVATE/relative)
        self.producer[str(PRIVATE/'kernel/native_elf.zig')]='0'*64
        pins={};artifacts={}
        for kind,(schema,_) in association.PINS.items():
            root=self.out/kind;root.mkdir();(root/'filesystem.elf').write_bytes((kind+' opaque fixture, not executable').encode())
            record=dict(schema=schema,status='pass',executed=False,inputs=self.producer,
                        tools={'fixture':{'resolved_path':str(self.tool),'sha256':sha(self.tool)}},
                        elf_sha256=sha(root/'filesystem.elf'),elf_bytes=(root/'filesystem.elf').stat().st_size,
                        structural_loader='ELF structural pages=synthetic',origins={'main':'fixture.o'},commands=[{'argv':['not-executed'],'exit_code':0}])
            if kind=='af07':
                record.update(owner_manifest_sha256=metadata.OWNER_SEAL,service_manifest_sha256=metadata.metadata.SEAL,
                              origins={k:'/synthetic/'+v for k,v in metadata.REQUIRED.items()},
                              local_frames={n:'fixture\t16\tstatic\n' for n in metadata.FRAME_FILES})
            (root/'build.json').write_text(json.dumps(record))
            for name in ['SOURCE.md','preparation.json','notices/openzfs/LICENSE','notices/openzfs/COPYRIGHT','notices/openzfs/NOTICE','notices/COPYRIGHT.musl','notices/LICENSE',*['fixture-'+str(i) for i in range(21)]]:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic fixture\n')
            members=sorted(p for p in root.rglob('*') if p.is_file());self.assertEqual(len(members),30)
            (root/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(root))+'\n' for p in members));seal=sha(root/'SHA256SUMS');pins[kind]=(schema,seal)
            changes={}
            from source_paths import dependency_input,relocate
            for name,before in self.producer.items():
                after=sha(dependency_input(name,before))
                if after!=before:changes[relocate(name).relative_to(ROOT).as_posix()]={'producer':before,'consumer':after}
            artifacts[kind]=dict(root=str(root),manifest_sha256=seal,build_sha256=sha(root/'build.json'),elf_sha256=sha(root/'filesystem.elf'),changes=changes)
        self.pin_patch=patch.object(association,'PINS',pins);self.pin_patch.start();self.addCleanup(self.pin_patch.stop)
        current={str(ROOT/n):sha(ROOT/n) for n in association.REQUIRED_INPUTS};current[str(self.tool)]=sha(self.tool)
        evidence={}
        for scope,markers in association.MARKERS.items():
            stdout='\n'.join(markers)+'\n';argv=[str(self.tool),'build','kernel-check','-Dnative-fs-owner-stack=true','-Dsmp=false'] if scope=='legacy-kernel' else [str(self.tool),'test','synthetic-source-not-executed','-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')]
            row=dict(argv=argv,cwd=str(ROOT),tool={'path':str(self.tool),'sha256':sha(self.tool)},inputs={str(self.tool):sha(self.tool)},expected_exit=0,exit=0,complete=True,cleanup='complete',failure=None,timeout_seconds=180,stdout=stdout,stderr='',stdout_sha256=hashlib.sha256(stdout.encode()).hexdigest(),stderr_sha256=hashlib.sha256(b'').hexdigest())
            evidence[scope]={'commands':[row],'markers':markers}
        baselines={n:{'path':str(PRIVATE/n),'sha256':sha(PRIVATE/n)} for n in association.PRODUCER_EDITS}
        self.data=dict(format=association.FORMAT,native_executed=False,dependency_root=None,artifacts=artifacts,inputs=current,baselines=baselines,evidence=evidence)
        self.path=self.out/'association.json'

    def select(self,data=None):
        self.path.write_text(json.dumps(data or self.data));os.environ[association.ENV_PATH]=str(self.path);os.environ[association.ENV_SHA]=sha(self.path)

    def unused_make_fixture(self):
        from source_paths import dependency_input, relocate
        roots={
            'af06':{'scripts/fs_launch.py':('recipe','compose','build'),
                    'scripts/service_runtime_smoke.py':('suite','compose_engine'),
                    'scripts/openzfs_elapsed.py':('prepare',), 'scripts/openzfs_volume.py':('build',)},
            'af07':{'scripts/fs_metadata_launch.py':('build','compose'),
                    'scripts/openzfs_fs_metadata_service.py':('prepare_engine',),
                    'scripts/service_runtime_smoke.py':('compose_engine',),
                    'scripts/openzfs_elapsed.py':('prepare',), 'scripts/openzfs_volume.py':('build',),
                    'scripts/openzfs_failure.py':('runtime_archive',)}}
        data=copy.deepcopy(self.data);proof={'current':{'path':'/usr/bin/make','resolved_path':'/usr/bin/make','sha256':sha('/usr/bin/make')},'producers':{}}
        for kind,artifact in data['artifacts'].items():
            directory=Path(artifact['root']);path=directory/'build.json';record=json.loads(path.read_text())
            for relative in roots[kind]:record['inputs'][str(PRIVATE/relative)]=sha(PRIVATE/relative)
            record['tools']['make']={'path':'/usr/bin/make','resolved_path':'/usr/bin/make','sha256':'0'*64,'version':'GNU Make 3.81'}
            path.write_text(json.dumps(record));members={}
            for line in (directory/'SHA256SUMS').read_text().splitlines():
                _,name=line.split('  ',1);members[name]=sha(directory/name)
            (directory/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in members.items()))
            seal=sha(directory/'SHA256SUMS');association.PINS[kind]=(association.PINS[kind][0],seal);artifact.update(manifest_sha256=seal,build_sha256=sha(path))
            recipes={};dispatch={}
            for name,before in record['inputs'].items():
                if not name.endswith('.py'):continue
                relative=relocate(name).relative_to(ROOT).as_posix();historical=PRIVATE/relative
                current=dependencies.retained_input(relocate(name));data['inputs'][str(current)]=sha(current)
                recipes[name]={'historical_path':str(historical),'historical_sha256':before,'current_path':str(current),'current_sha256':sha(current)}
            for relative,functions in roots[kind].items():
                module=ast.parse((PRIVATE/relative).read_text());dispatch[relative]={}
                for name in functions:
                    node=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name==name)
                    dispatch[relative][name]=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
            proof['producers'][kind]={'entry':record['tools']['make'],'command_count':len(record['commands']),'commands_sha256':hashlib.sha256(json.dumps(record['commands'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'recipes':recipes,'dispatch':dispatch}
        data['inputs']['/usr/bin/make']=sha('/usr/bin/make');data['unused_make']=proof
        return data

    def test_explicit_unused_make_requires_complete_recipe_and_command_proof(self):
        data=self.unused_make_fixture();association.validate(data)
        self.select(data)
        accepted=launch.intake(Path(data['artifacts']['af06']['root']),data['artifacts']['af06']['manifest_sha256'])
        self.assertFalse(accepted['native_acceptance']);self.assertFalse(accepted['executed'])
        os.environ.pop(association.ENV_PATH);os.environ.pop(association.ENV_SHA)
        original_read=Path.read_text;live=ROOT/'scripts/fs_launch.py'
        def changed(path,*args,**kwargs):
            text=original_read(path,*args,**kwargs)
            return text.replace('destination = validate_destination(destination)',"destination = Path('/unreviewed')",1) if path==live else text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(ValueError,'producing callgraph changed'):
            association.validate(data)
        for change in ('missing','entry','current','commands','recipe','recipe-path','recipe-shape','extra','dispatch','other-tool'):
            bad=copy.deepcopy(data)
            if change=='missing':bad.pop('unused_make')
            elif change=='entry':bad['unused_make']['producers']['af06']['entry']['path']='/foreign/make'
            elif change=='current':bad['unused_make']['current']['sha256']='1'*64
            elif change=='commands':bad['unused_make']['producers']['af06']['command_count']+=1
            elif change=='recipe':bad['unused_make']['producers']['af07']['recipes'].pop(next(iter(bad['unused_make']['producers']['af07']['recipes'])))
            elif change in ('recipe-path','recipe-shape'):
                source=next(iter(bad['unused_make']['producers']['af07']['recipes'].values()))
                source['current_path' if change=='recipe-path' else 'historical_path']=str(self.out/'foreign-recipe.py') if change=='recipe-path' else None
            elif change=='extra':bad['unused_make']['unexpected']=True
            elif change=='dispatch':bad['unused_make']['producers']['af06']['dispatch']['scripts/fs_launch.py']['compose']='1'*64
            else:self.tool.write_bytes(b'actual compiler drift')
            with self.subTest(change=change),self.assertRaises(ValueError):association.validate(bad)
            if change=='other-tool':self.tool.write_bytes(b'synthetic unexecuted host tool identity\n')

    def test_unused_make_never_admits_executed_tool_or_default_intake(self):
        data=self.unused_make_fixture()
        with self.assertRaises(ValueError):launch.intake(Path(data['artifacts']['af06']['root']),data['artifacts']['af06']['manifest_sha256'])
        for kind in ('af06','af07'):
            bad=copy.deepcopy(data);directory=Path(bad['artifacts'][kind]['root']);path=directory/'build.json';original=path.read_text();record=json.loads(original);record['commands'].append({'argv':['/usr/bin/make','--version'],'exit_code':0});path.write_text(json.dumps(record))
            manifest=directory/'SHA256SUMS';before=manifest.read_text();manifest.write_text(before.replace(hashlib.sha256(original.encode()).hexdigest()+'  build.json',sha(path)+'  build.json'))
            bad['artifacts'][kind].update(build_sha256=sha(path),manifest_sha256=sha(manifest));pin=association.PINS[kind];association.PINS[kind]=(pin[0],sha(manifest))
            bad['unused_make']['producers'][kind].update(command_count=len(record['commands']),commands_sha256=hashlib.sha256(json.dumps(record['commands'],sort_keys=True,separators=(',',':')).encode()).hexdigest())
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'executed make'):association.validate(bad)
            path.write_text(original);manifest.write_text(before);association.PINS[kind]=pin

    def test_default_is_strict_and_explicit_pair_has_no_native_claim(self):
        root=Path(self.data['artifacts']['af06']['root']);seal=self.data['artifacts']['af06']['manifest_sha256']
        with self.assertRaisesRegex(ValueError,'consumed source/input drift'):launch.intake(root,seal)
        association.write(self.path,self.data);os.environ[association.ENV_PATH]=str(self.path);os.environ[association.ENV_SHA]=sha(self.path)
        accepted=launch.intake(root,seal);self.assertFalse(accepted['native_acceptance']);self.assertFalse(accepted['executed'])
        root=Path(self.data['artifacts']['af07']['root']);seal=self.data['artifacts']['af07']['manifest_sha256']
        owner_inputs={str(ROOT/n):sha(ROOT/n) for n in ('scripts/service_runtime_smoke.py','scripts/openzfs_elapsed.py')}
        with patch.object(metadata,'owner_intake',return_value={'inputs':owner_inputs}):
            accepted=metadata.intake(root,seal);self.assertFalse(accepted['native_acceptance'])
        with patch.object(metadata,'owner_intake',return_value={'inputs':{**owner_inputs,str(ROOT/'user/storage/unrecorded.rs'):'0'*64}}):
            with self.assertRaisesRegex(ValueError,'missing consumed closure'):metadata.intake(root,seal)
        os.environ.pop(association.ENV_PATH);os.environ.pop(association.ENV_SHA)
        with self.assertRaisesRegex(ValueError,'consumed source/input drift'):launch.intake(Path(self.data['artifacts']['af06']['root']),self.data['artifacts']['af06']['manifest_sha256'])

    def test_record_hash_duplicate_unknown_field_and_scope_denials(self):
        self.select();os.environ[association.ENV_SHA]='0'*64
        with self.assertRaisesRegex(ValueError,'identity'):association.verify_inputs('af06',Path(self.data['artifacts']['af06']['root']),self.data['artifacts']['af06']['manifest_sha256'],{})
        self.path.write_text('{"format":"duplicate",'+json.dumps(self.data)[1:])
        with self.assertRaisesRegex(ValueError,'duplicate'):association.load(self.path,sha(self.path))
        for change in ({**self.data,'extra':True},{**self.data,'native_executed':True},{**self.data,'dependency_root':'/tmp/unselected'}):
            with self.subTest(change=list(change)),self.assertRaises(ValueError):association.validate(change)
        self.select();os.environ.pop(association.ENV_SHA)
        with self.assertRaisesRegex(ValueError,'path and hash'):association.verify_inputs('af06',Path(self.data['artifacts']['af06']['root']),self.data['artifacts']['af06']['manifest_sha256'],{})

    def test_exact_drift_set_live_sources_and_all_producer_kinds(self):
        for kind in ('af06','af07'):
            for action in ('missing','extra','old-hash','current-hash'):
                data=copy.deepcopy(self.data);changes=data['artifacts'][kind]['changes']
                if action=='missing':changes.pop('kernel/native_elf.zig')
                elif action=='extra':changes['kernel/not-reviewed.zig']={'producer':'0'*64,'consumer':'1'*64}
                elif action=='old-hash':changes['kernel/native_elf.zig']['producer']='1'*64
                else:changes['kernel/native_elf.zig']['consumer']='1'*64
                with self.subTest(kind=kind,action=action),self.assertRaisesRegex(ValueError,'changed-consumer set'):association.validate(data)
        data=copy.deepcopy(self.data);data['inputs'][str(ROOT/'kernel/native_elf.zig')]='0'*64
        with self.assertRaisesRegex(ValueError,'live input changed'):association.validate(data)
        for path in self.producer:
            if Path(path).is_relative_to(self.out) and Path(path)!=self.tool:
                original=Path(path).read_bytes();Path(path).write_bytes(b'drift')
                with self.subTest(path=path),self.assertRaisesRegex(ValueError,'external producer input changed'):association.validate(self.data)
                Path(path).write_bytes(original)
        self.tool.write_bytes(b'tool drift')
        with self.assertRaisesRegex(ValueError,'live input changed'):association.validate(self.data)

    def test_recipe_projection_rejects_any_other_function_import_constant_or_link_change(self):
        for relative in association.PRODUCER_EDITS:
            baseline=(PRIVATE/relative).read_text();current=(ROOT/relative).read_text()
            association.producer_unchanged(relative,baseline,current)
            for addition in ('\nUNREVIEWED_GLOBAL=1\n','\nimport fractions\n','\ndef unreviewed_producer():\n    return "different link flags"\n'):
                with self.subTest(relative=relative,addition=addition),self.assertRaisesRegex(ValueError,'producer logic/import/global drift'):association.producer_unchanged(relative,baseline,current+addition)
        current=(ROOT/'scripts/zpl_pair.py').read_text()
        for before,after in [("retained_root(ROOT / '.deps/native-service-runtime-v3')","retained_root(ROOT / '.deps/foreign')"),("'..' in Path(name).parts","False"),("if not path.resolve().is_relative_to(dependency.resolve()):","if False:")]:
            self.assertEqual(current.count(before),1)
            with self.subTest(pair_change=before),self.assertRaisesRegex(ValueError,'producer logic/import/global drift'):
                association.producer_unchanged('scripts/zpl_pair.py',(PRIVATE/'scripts/zpl_pair.py').read_text(),current.replace(before,after,1))
        current=(ROOT/'scripts/fs_metadata_launch.py').read_text()
        anchor="final[-1]=str(destination/'filesystem.elf')"
        self.assertEqual(current.count(anchor),1)
        with self.assertRaisesRegex(ValueError,'producer logic/import/global drift'):association.producer_unchanged('scripts/fs_metadata_launch.py',(PRIVATE/'scripts/fs_metadata_launch.py').read_text(),current.replace(anchor,"final[-1]=str(destination/'unreviewed.elf')",1))

    def test_evidence_requires_real_shape_inputs_cleanup_outputs_and_all_controls(self):
        for field,value in [('complete',False),('cleanup','unresolved'),('failure','timeout'),('exit',1),('timeout_seconds',181),('stdout_sha256','0'*64),('inputs',{}),('tool',{'path':str(self.tool),'sha256':'0'*64})]:
            data=copy.deepcopy(self.data);data['evidence']['af06-parser']['commands'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):association.validate(data)
        for scope in association.CASES:
            data=copy.deepcopy(self.data);data['evidence'][scope]['markers']=data['evidence'][scope]['markers'][:-1]
            with self.subTest(scope=scope),self.assertRaises(ValueError):association.validate(data)
        data=copy.deepcopy(self.data);row=data['evidence']['af06-parser']['commands'][0];row['stdout']='confounded compiler failure :1:1: error: wrong\n';row['stdout_sha256']=hashlib.sha256(row['stdout'].encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'compile failure'):association.validate(data)
        data=copy.deepcopy(self.data);data['evidence']['legacy-kernel']['commands'][0]['argv'].append('-Dnative-fs-application-profile=true')
        with self.assertRaisesRegex(ValueError,'legacy kernel selection'):association.validate(data)

    def test_real_kernel_row_can_be_separate_from_bound_checked_projection(self):
        data=copy.deepcopy(self.data);group=data['evidence']['legacy-kernel'];kernel=group['commands'][0]
        projection=copy.deepcopy(kernel);tool=self.out/'python3';tool.write_bytes(b'synthetic projection tool, never executed');checker=self.out/'projection.py';checker.write_text('# synthetic checker identity; never executed\n')
        data['inputs'][str(tool)]=sha(tool);data['inputs'][str(checker)]=sha(checker)
        projection.update(argv=[str(tool),str(checker)],tool={'path':str(tool),'sha256':sha(tool)},inputs={str(tool):sha(tool),str(checker):sha(checker)})
        kernel.update(stdout='',stdout_sha256=hashlib.sha256(b'').hexdigest());group['commands'].append(projection)
        association.validate(data)
        group['commands']=[projection]
        with self.assertRaisesRegex(ValueError,'missing actual legacy kernel command'):association.validate(data)
        data=copy.deepcopy(self.data);data['evidence']['legacy-kernel']['commands'][0]['cwd']=str(PRIVATE)
        with self.assertRaisesRegex(ValueError,'legacy kernel selection'):association.validate(data)
        target=ROOT/'kernel/native_elf.zig';original=Path.resolve
        def redirected(path,*args,**kwargs):return PRIVATE/'kernel/native_elf.zig' if path==target else original(path,*args,**kwargs)
        with patch.object(Path,'resolve',redirected),self.assertRaisesRegex(ValueError,'current source path substitution'):association.validate(self.data)

    def test_failed_parser_or_kernel_row_cannot_be_a_positive_witness(self):
        tool=self.out/'python3';tool.write_bytes(b'synthetic projection tool, never executed');checker=self.out/'checked-projection.py';checker.write_text('# synthetic checker identity; never executed\n')
        for scope in ('af06-parser','af07-parser','legacy-kernel'):
            data=copy.deepcopy(self.data);data['inputs'][str(tool)]=sha(tool);data['inputs'][str(checker)]=sha(checker)
            positive=data['evidence'][scope]['commands'][0];projection=copy.deepcopy(positive)
            projection.update(argv=[str(tool),str(checker)],tool={'path':str(tool),'sha256':sha(tool)},inputs={str(tool):sha(tool),str(checker):sha(checker)})
            positive.update(exit=1,expected_exit=1,stdout='',stdout_sha256=hashlib.sha256(b'').hexdigest())
            data['evidence'][scope]['commands'].append(projection)
            with self.subTest(scope=scope),self.assertRaisesRegex(ValueError,'missing .*actual .*command'):association.validate(data)
            positive.update(exit=0,expected_exit=0)
            association.validate(data) # The separate checked projection is allowed.

    def test_current_component_redirects_and_misleading_python_options_reject(self):
        targets=(ROOT/'userland/experiments/filesystem-service/launch-owner.rs',ROOT/'sys-init/prototypes/native-filesystem-session/owner_runtime.rs',ROOT/'sys-init/scripts/owner_compare.py',ROOT/'pkg-mgr/bin/pkg-mgr')
        original=Path.resolve
        with self.assertRaisesRegex(ValueError,'live input changed'):association.mapping({str(ROOT):'0'*64})
        for target in targets:
            self.assertTrue(target.is_file())
            def redirected(path,*args,**kwargs):return PRIVATE/path.relative_to(ROOT) if path==target else original(path,*args,**kwargs)
            with self.subTest(target=target),patch.object(Path,'resolve',redirected):
                with self.assertRaisesRegex(ValueError,'current source path substitution'):association.mapping({str(target):sha(target)})
                with self.assertRaisesRegex(ValueError,'current source path substitution'):association.current_source(target)
        tool=self.out/'python3';tool.write_bytes(b'synthetic Python identity');checker=self.out/'bound-checker.py';checker.write_text('# synthetic checker, never executed\n')
        for args in (['-c','pass','-m','unittest'],['-B','-c','pass',str(checker)]):
            data=copy.deepcopy(self.data);data['inputs'][str(tool)]=sha(tool);data['inputs'][str(checker)]=sha(checker)
            row=copy.deepcopy(data['evidence']['application-models']['commands'][0]);row.update(argv=[str(tool),*args],tool={'path':str(tool),'sha256':sha(tool)},inputs={str(tool):sha(tool),str(checker):sha(checker)})
            data['evidence']['application-models']['commands']=[row]
            with self.subTest(args=args),self.assertRaisesRegex(ValueError,'bound Python checker source'):association.validate(data)
            row['argv']=[str(tool),'-B',str(checker)];association.validate(data)
            row['argv']=[str(tool),'-B','-m','unittest','synthetic-only'];association.validate(data)

    def test_association_mapping_cannot_exempt_retained_prefix_traversal(self):
        traversal=ROOT/'userland/build/session-deliveries/filesystem-abi29-linked-2026-10-21-v1/../../../experiments/filesystem-service/launch-owner.rs'
        data=copy.deepcopy(self.data);data['inputs'][str(traversal)]='0'*64
        with self.assertRaisesRegex(ValueError,'current source parent traversal'):association.validate(data)
        with self.assertRaisesRegex(ValueError,'current source parent traversal'):association.mapping({str(traversal):'0'*64})
        with self.assertRaisesRegex(ValueError,'current source parent traversal'):association.current_source(traversal)
        association.current_source(ROOT/'userland/experiments/filesystem-service/launch-owner.rs')

    def test_selected_copies_mutations_and_extra_members_still_reject(self):
        self.select();root=Path(self.data['artifacts']['af06']['root']);seal=self.data['artifacts']['af06']['manifest_sha256'];copied=self.out/'copy';shutil.copytree(root,copied)
        with self.assertRaisesRegex(ValueError,'copy mismatch'):launch.intake(copied,seal)
        for mode in ('drift','extra','symlink'):
            target=root/'filesystem.elf';original=target.read_bytes()
            if mode=='drift':target.write_bytes(b'wrong')
            elif mode=='extra':(root/'extra').write_text('extra')
            else:target.unlink();target.symlink_to(copied/'filesystem.elf')
            with self.subTest(mode=mode),self.assertRaises(ValueError):launch.intake(root,seal)
            if mode=='symlink':target.unlink()
            target.write_bytes(original);(root/'extra').unlink(missing_ok=True)

    def test_default_stale_kernel_rejects_with_dependency_declaration_selected(self):
        root=Path(self.data['artifacts']['af06']['root']);record=json.loads((root/'build.json').read_text())
        for relative in association.PRODUCER_EDITS:record['inputs'][str(PRIVATE/relative)]=sha(ROOT/relative)
        (root/'build.json').write_text(json.dumps(record))
        members=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
        (root/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(root))+'\n' for p in members))
        with patch.dict(os.environ,{dependencies.ENV:str(PRIVATE)}):
            with self.assertRaisesRegex(ValueError,'consumed source/input drift: .*kernel/native_elf.zig'):launch.intake(root,sha(root/'SHA256SUMS'))

    def test_named_executable_evidence_and_impact_omissions_break_the_oracle(self):
        import importlib.util
        source=(ROOT/'scripts/fs_consumer_association.py').read_text()
        for label,anchor,change in [
                ('evidence','    _evidence(data)\n',lambda data:data['evidence']['af06-parser'].update(markers=[])),
                ('impact',"        require(artifact['changes'] == changes and changes, 'exact changed-consumer set')\n",lambda data:data['artifacts']['af06'].update(changes={}))]:
            self.assertEqual(source.count(anchor),1)
            path=self.out/(label+'.py');path.write_text(source.replace(anchor,'',1))
            spec=importlib.util.spec_from_file_location('synthetic_omitted_'+label,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.PINS=association.PINS
            bad=copy.deepcopy(self.data);change(bad)
            with self.assertRaises(ValueError):association.validate(bad)
            # The compiling omission accepts the forbidden record, so the same
            # rejection oracle detects it. No record is published or executed.
            module.validate(bad)


class Routing(unittest.TestCase):
    def test_actual_path_digest_never_hashes_a_relocated_twin(self):
        with tempfile.TemporaryDirectory(prefix='aether-digest-twins-') as folder:
            root=Path(folder);actual=root/'actual';twin=root/'public-twin';actual.write_bytes(b'actual member');twin.write_bytes(b'different public member')
            with patch.object(launch,'relocate',return_value=twin):
                self.assertEqual(launch.actual_digest(actual),sha(actual));self.assertEqual(launch.digest(actual),sha(twin))

    def test_only_declared_retained_names_route_never_active_source_or_copies(self):
        with patch.dict(os.environ,{dependencies.ENV:str(PRIVATE)}):
            sdk=dependencies.retained_root(ROOT/'.deps/native-current/sdk')
            self.assertEqual(sdk,PRIVATE/'.deps/native-current/sdk')
            for path in (ROOT/'kernel/native_elf.zig',ROOT/'user/storage/service-runtime/filesystem-engine.c',ROOT/'sys-init/prototypes/native-filesystem-session/owner_runtime.rs',ROOT/'pkg-mgr/README.md',Path('/tmp/copy/native-utc-v3')):
                self.assertEqual(dependencies.retained_input(path),path)
                self.assertEqual(dependencies.retained_root(path),path)
            historical=dependencies.retained_root(ROOT/dependencies.HISTORICAL)
            self.assertEqual(historical,PRIVATE/dependencies.HISTORICAL)
        with patch.dict(os.environ,{dependencies.ENV:'/tmp/../not-canonical'}):
            with self.assertRaisesRegex(ValueError,'declaration'):dependencies.retained_root(ROOT/'.deps/native-utc-v3')
        with patch.dict(os.environ,{},clear=False):
            os.environ.pop(dependencies.ENV,None)
            self.assertEqual(dependencies.retained_root(ROOT/'.deps/native-current/sdk'),ROOT/'.deps/native-current/sdk')

    def test_conflicting_alias_capsule_and_changed_availability_stub_reject(self):
        target=ROOT/'.deps/native-current/sdk';original=Path.resolve
        def foreign(path,*args,**kwargs):return PRIVATE/'foreign-capsule' if path==target else original(path,*args,**kwargs)
        def conflicting(path,*args,**kwargs):return path if path==target else original(path,*args,**kwargs)
        with patch.dict(os.environ,{dependencies.ENV:str(PRIVATE)}):
            with patch.object(Path,'resolve',foreign),self.assertRaisesRegex(ValueError,'alias target'):dependencies.retained_root(target)
            with patch.object(Path,'resolve',conflicting),self.assertRaisesRegex(ValueError,'conflicts'):dependencies.retained_root(target)
            stub=ROOT/dependencies.HISTORICAL/'README.md';read=Path.read_bytes
            def changed(path):return b'not the approved availability stub' if path==stub else read(path)
            with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'conflicts'):dependencies.retained_root(ROOT/dependencies.HISTORICAL)
        import source_paths
        self.assertEqual(sha(source_paths.TOOLING/'pins.json'),source_paths.CATALOG_SHA256)

    def test_parent_traversal_cannot_escape_retained_roots(self):
        traversal=ROOT/'.deps/native-current/sdk/../../../kernel/main.zig'
        with patch.dict(os.environ,{dependencies.ENV:str(PRIVATE)}):
            for resolve in (dependencies.retained_input,dependencies.retained_root):
                with self.subTest(resolve=resolve.__name__),self.assertRaisesRegex(ValueError,'parent traversal'):resolve(traversal)
                self.assertEqual(resolve(ROOT/'kernel/main.zig'),ROOT/'kernel/main.zig')
            import source_paths
            with self.assertRaisesRegex(ValueError,'parent traversal'):source_paths.dependency_input(traversal,'0'*64)

    def test_only_three_legacy_recipe_prefixes_change_and_macro_rhs_is_preserved(self):
        for name in ('openzfs-native-delay-2026-10-05','openzfs-native-wait-clocks-2026-10-05','openzfs-native-time-callers-2026-10-05'):
            old='/Users/cam/DEV/Aether/zig-out/'+name
            self.assertEqual(elapsed.route('-I'+old+'/source/header.h'),'-I'+str(elapsed.CURRENT)+'/source/header.h')
            self.assertEqual(elapsed.route('-fmacro-prefix-map='+old+'/source=/historical/__FILE__'),'-fmacro-prefix-map='+str(elapsed.CURRENT)+'/source=/historical/__FILE__')
        old='/Users/cam/DEV/Aether/zig-out/openzfs-native-wait-clocks-2026-10-05/build-attempt-2/kernel.c'
        self.assertEqual(elapsed.route(old),str(elapsed.CURRENT/'previous-build/kernel.c'))
        for text in ('-DNAME=/Users/cam/DEV/Aether/user/unrelated.c','/Users/cam/DEV/Aether/zig-out/unknown-prefix/input.c','/Users/cam/DEV/Aether/zig-out/openzfs-native-delay-2026-10-05-foreign/input.c'):
            self.assertEqual(elapsed.route(text),text)
