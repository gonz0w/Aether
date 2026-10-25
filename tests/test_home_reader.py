# SPDX-License-Identifier: BSD-2-Clause
"""Execute generated AF09 late reader startup with typed host lifecycle substitutes.

These tests qualify lifecycle/output composition, never ZFS/media acceptance.
"""
import hashlib
import importlib.util
import json
import os
import shlex
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import home_reader as reader

spec = importlib.util.spec_from_file_location('home_reader_owned_process', ROOT / 'userland/experiments/command-runner/process.py')
owned = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owned)

CHILDREN = []
HEADER_DEPENDENCIES = {}
HOST_HEADERS = {}
FROZEN = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (
    Path(__file__), ROOT/'scripts/home_reader.py',
    ROOT/'userland/experiments/command-runner/process.py',
    ROOT/'user/storage/service-runtime/engine-startup.c',
    ROOT/'user/storage/service-runtime/engine-observe.inc',
    ROOT/'user/storage/openzfs-volume/spa-zpl-recover.inc',
    ROOT/'.deps/native-current/sdk/tools.lock.json')}
FROZEN['/usr/bin/xcrun'] = hashlib.sha256(Path('/usr/bin/xcrun').read_bytes()).hexdigest()
CLANG_PIN = json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']['clang']
UBSAN = Path(CLANG_PIN['path']).parent.parent/'lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib'
UBSAN_SHA256 = '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
if hashlib.sha256(UBSAN.read_bytes()).hexdigest() != UBSAN_SHA256:
    raise AssertionError('reader UBSan runtime changed')
FROZEN[str(UBSAN)] = UBSAN_SHA256


def run_child(work, argv, label):
    # Discover the exact include closure without compiling/linking or executing
    # the generated source. Freeze that closure before the actual C build.
    if '-MD' in argv and '-M' not in argv:
        discovery=run_child(work,[*argv,'-M'],label+'-dependencies')
        if discovery.returncode:
            raise AssertionError('reader header discovery failed: '+discovery.stderr.decode())
    pin=json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']['clang']
    if str(argv[0]) == pin['path']:
        if hashlib.sha256(Path(argv[0]).read_bytes()).hexdigest() != pin['sha256']:
            raise AssertionError('pinned reader compiler drift before child')
    for name, digest in HOST_HEADERS.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise AssertionError('late reader host header drift before child: '+name)
    for name, digest in FROZEN.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise AssertionError('late reader frozen input drift: '+name)
    result = owned.run(list(map(str, argv)), cwd=str(ROOT), env=owned.clean_env(work),
        work=work, label=label, timeout=180, file_limit=1024*1024)
    generated = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in work.rglob('*') if p.is_file() and p.suffix in ('.c', '.h', '.inc')}
    dependencies = {}
    for dep in work.glob('*.d'):
        for name in shlex.split(dep.read_text().replace('\\\n', ' ').split(':', 1)[1]):
            path = Path(name)
            if path.is_file():
                dependencies[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name, digest in dependencies.items():
        if not Path(name).is_relative_to(work):
            if name in HOST_HEADERS and HOST_HEADERS[name] != digest:
                raise AssertionError('late reader host header drift after child: '+name)
            HOST_HEADERS[name] = digest
    HEADER_DEPENDENCIES.update(dependencies)
    dependency_set=hashlib.sha256(json.dumps(dependencies,sort_keys=True).encode()).hexdigest()
    CHILDREN.append(dict(label=label, process=result.record,
        stdout=result.stdout.decode(errors='replace')[-3000:],
        stderr=result.stderr.decode(errors='replace')[-5000:],
        generated_inputs=generated, header_dependency_set_sha256=dependency_set))
    output = os.environ.get('AETHER_HOME_READER_CHILDREN')
    if output:
        Path(output).write_text(json.dumps(dict(sources=FROZEN, header_dependencies=HEADER_DEPENDENCIES, children=CHILDREN), indent=2)+'\n')
    for name, digest in FROZEN.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise AssertionError('late reader frozen input drift after child: '+name)
    for name, digest in HOST_HEADERS.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise AssertionError('late reader host header drift after child: '+name)
    if str(argv[0]) == pin['path'] and result.record['tool']['sha256'] != pin['sha256']:
        raise AssertionError('pinned reader compiler drift after child')
    if not result.record['complete']:
        raise AssertionError(result.record)
    return result

HEAD = r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <unistd.h>
static int fault, guard, live=1, admissions=1, stopped, utc_closed, drained;
static unsigned calls;
int aether_runtime_init(void);
unsigned aether_runtime_live(void);
unsigned aether_runtime_admissions(void);
int aether_runtime_finish(void);
int aether_zfs_startup_bind(const void *);
uint64_t aether_zfs_granted_pages(void);
uint64_t aether_zfs_free_pages(void);
unsigned long getauxval(unsigned long);
static ssize_t checked_write(int fd, const void *data, size_t count);
#define write checked_write
#define main reader_entry
'''
TAIL = r'''
#undef main
#undef write
int aether_runtime_init(void) { return fault==1; }
unsigned aether_runtime_live(void) { return (fault==14 && stopped) ? 1U : (unsigned)live; }
unsigned aether_runtime_admissions(void) { return fault==15 ? 0U : (unsigned)admissions; }
int aether_zfs_startup_bind(const void *p) { (void)p; return fault==2; }
uint64_t aether_zfs_granted_pages(void) { return fault==12 ? 8191 : 8192; }
uint64_t aether_zfs_free_pages(void) { return fault==13 ? 8193 : 8192; }
unsigned long getauxval(unsigned long x) { (void)x; return guard ? 0UL : 0x50000101UL; }
void kernel_init(int mode) { if(mode!=1) abort(); }
void kernel_fini(void) { drained=1; if(fault==11) tls_marker=18; }
int aether_volume_start_probe(void) { return fault==3; }
int aether_volume_finish_probe(void) { return fault==8; }
int aether_engine_utc_start(int p,int d) { (void)p;(void)d; return fault==4; }
int aether_engine_utc_probe(int64_t s) {
    (void)s;
    if(fault==5) return 1;
    aether_engine_utc_phase('U');
    if(fault!=16) aether_engine_utc_phase('V');
    aether_engine_utc_phase(fault==17 ? 'X' : 'W');
    return 0;
}
int aether_engine_utc_finish(void) { utc_closed=1; return fault==9; }
int aether_runtime_finish(void) {
    if(!guard && (!drained || !utc_closed)) return EIO;
    if(fault==10) return EIO;
    stopped=1;live=0;if(fault==21) tls_marker=18;return 0;
}
int aether_spa_import_probe(void) {
    if(guard) { aether_engine_utc_phase('N'); return fault==18; }
    const unsigned char phases[]="LPabcdefghOAMTabcdefghSD";
    for(size_t i=0;i<sizeof(phases)-1;i++) aether_engine_utc_phase(phases[i]);
    for(unsigned i=0;i<32;i++) aether_home_reader_digest[i]=(unsigned char)(i*17);
    aether_home_reader_ready=fault!=7;
    return fault==6;
}
static ssize_t checked_write(int fd,const void *data,size_t count) {
    if(fd!=1 || count!=8 || !stopped || (!guard && (!drained || !utc_closed))) abort();
    calls++;
    if(fault==19) return 0;
    if(fault==20) return 7;
    return fwrite(data,1,count,stdout)==count ? (ssize_t)count : -1;
}
int main(int argc,char **argv) {
    if(argc>1) fault=atoi(argv[1]);
    if(argc>2) guard=atoi(argv[2]);
    int result=reader_entry();
    if(!result && calls!=(guard?3U:32U)) {
        fputs("late-output-count failure\n",stderr);return 99;
    }
    return result ? 1 : 0;
}
'''


class HomeReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-home-reader-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.clang = json.loads((ROOT / '.deps/native-current/sdk/tools.lock.json').read_text())['tools']['clang']['path']
        cls.original = (ROOT / 'user/storage/service-runtime/engine-startup.c').read_text()
        cls.observe = (ROOT / 'user/storage/service-runtime/engine-observe.inc').read_text()
        (cls.work/'runtime.h').write_text('')
        (cls.work/'startup-fixture.h').write_text('static const int startup_fixture;\n')
        (cls.work/'sys').mkdir()
        (cls.work/'sys/auxv.h').write_text('unsigned long getauxval(unsigned long);\n')
        sdk=cls.run_owned(['/usr/bin/xcrun','--show-sdk-path'],'startup-sdk')
        if sdk.returncode: raise AssertionError(sdk.stderr.decode())
        cls.sdk=sdk.stdout.decode().strip()
        if not Path(cls.sdk).is_dir(): raise AssertionError('missing actual host SDK')
        cls.exe = cls.compile(reader.render_startup(cls.original, True), 'normal')

    @classmethod
    def run_owned(cls, argv, label):
        return run_child(cls.work,argv,label)

    @classmethod
    def compile(cls, startup, label, observer=None):
        (cls.work/'home-reader-observe.inc').write_text(reader.render_observer(cls.observe) if observer is None else observer)
        source = cls.work/(label+'.c'); source.write_text(HEAD+startup+TAIL)
        exe = cls.work/label
        result=cls.run_owned([cls.clang,'--no-default-config','-std=c17','-D_POSIX_C_SOURCE=200809L',
            '-DENGINE_NATIVE','-DENGINE_VOLUME','-DENGINE_UTC','-DENGINE_POOL','-DENGINE_POOL_IMPORT',
            '-DUTC_POLICY=1','-DUTC_DISABLED=0','-DUTC_CYCLES=1','-DUTC_SECONDS=1791290040',
            '-isysroot',cls.sdk,'-MD','-MF',cls.work/(label+'.d'),'-I'+str(cls.work),'-Wall','-Wextra','-Werror','-Wformat=2','-fsanitize=undefined',
            '-fno-sanitize-recover=all',source,'-o',exe],label+'-compile')
        if result.returncode: raise AssertionError(result.stderr.decode())
        return exe

    def test_full_digest_exact_eight_byte_writes_after_all_checks(self):
        result=self.run_owned([self.exe],'healthy')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(result.stdout),256)
        self.assertEqual(result.stdout[::8],bytes((i*17)&255 for i in range(32)))
        self.assertEqual(set(result.stdout[i] for i in range(256) if i%8),{0})

    def test_lifecycle_resource_tls_phase_and_read_failures_never_publish_digest(self):
        for fault in (*range(1,19),21):
            with self.subTest(fault=fault):
                result=self.run_owned([self.exe,str(fault)],'failure-'+str(fault))
                if fault==18: continue # denied import fault belongs to guard below
                self.assertNotEqual(result.returncode,0,'named lifecycle/resource/phase rejection '+str(fault))
                self.assertEqual(result.stdout,b'','failed reader published digest '+str(fault))

    def test_denied_replacement_keeps_bnr_after_clean_retirement(self):
        result=self.run_owned([self.exe,'0','1'],'guard')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout[::8],b'BNR')
        self.assertEqual(len(result.stdout),24)
        for fault in (10,11,12,13,14,15,18,21):
            if fault==11: continue # kernel_fini is correctly absent on denied path
            result=self.run_owned([self.exe,str(fault),'1'],'guard-'+str(fault))
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(result.stdout,b'')

    def test_write_failure_cannot_succeed(self):
        for fault in (19,20):
            result=self.run_owned([self.exe,str(fault)],'write-'+str(fault))
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(result.stdout,b'')

    def test_generated_source_omissions_reject_named_semantics(self):
        text=reader.render_startup(self.original,True)
        for label,old,new,fault in (
            ('final-tls','return tls_marker == 17 ? 0 : 223;','return 0;',11),
            ('phase-order',"engine_observe('F');","engine_observe('X');",0),
            ('missing-fini','    kernel_fini();','    /* omitted fini */',0),
            ('missing-finish','    if (engine_finish())','    if ((void)engine_finish, 0)',0)):
            with self.subTest(control=label):
                self.assertIn(old,text)
                mutated=text.replace(old,new)
                executable=self.compile(mutated,label)
                result=self.run_owned([executable,str(fault)],label+'-run')
                self.assertNotEqual(result.returncode,0,'semantic omission escaped: '+label)
                self.assertEqual(result.stdout,b'','semantic omission emitted: '+label)

    def test_exact_anchor_and_explicit_role_guards_preserve_original(self):
        identity=hashlib.sha256(self.original.encode()).hexdigest()
        for role in (0,1,None,'recovery'):
            with self.assertRaises(ValueError):reader.render_startup(self.original,role)
        for damaged in (self.original.replace('int main(void)','int start(void)'),
                        self.original+self.original):
            with self.assertRaises(ValueError):reader.render_startup(damaged,True)
        self.assertEqual(hashlib.sha256((ROOT/'user/storage/service-runtime/engine-startup.c').read_bytes()).hexdigest(),identity)
        source=(ROOT/'user/storage/openzfs-volume/spa-zpl-recover.inc').read_text()
        pristine=reader.render_importer(source,False)
        recovery=reader.render_importer(source,True)
        self.assertIn('aether_home_readback(spa, 0,',pristine)
        self.assertIn('aether_home_readback(spa, 1,',recovery)
        self.assertIn('spa->spa_uberblock.ub_txg == 782',pristine)
        self.assertIn('spa->spa_uberblock.ub_txg > 782',recovery)
        self.assertNotIn('aether_pool_namespace_recover(spa)',recovery)

IMPORT_HEAD = r'''
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#define FTAG ((void *)0)
#define AETHER_VOLUME_PATH "/dev/fixed"
#define O_RDONLY 0
#define NV_UNIQUE_NAME 1
#define SPA_VERSION_FEATURES 5000
#define SPA_FEATURE_HOLE_BIRTH 1
#define SPA_FEATURE_EMBEDDED_DATA 2
#define SPA_FEATURE_ZSTD_COMPRESS 3
#define DMU_POOL_DIRECTORY_OBJECT 1
#define DMU_POOL_CREATION_VERSION "version"
typedef struct nvlist { int marker; } nvlist_t;
typedef struct zfs_file { int marker; } zfs_file_t;
typedef struct spa { struct { uint64_t ub_txg; } spa_uberblock; void *spa_meta_objset; } spa_t;
static int fault, guard, closed, drained, evicted, oracle_called;
static unsigned phase_count;
static unsigned char phases[32];
static spa_t pool;
static nvlist_t nv;
unsigned char aether_home_reader_digest[32];
unsigned aether_home_reader_ready;
unsigned long getauxval(unsigned long);
int zfs_file_open(const char *,int,int,void *,zfs_file_t **);
void aether_engine_utc_phase(unsigned char);
int aether_pool_label_read(nvlist_t **);
int aether_pool_label_config(nvlist_t *,nvlist_t **);
void nvlist_free(nvlist_t *);
int nvlist_alloc(nvlist_t **,int,int);
int nvlist_add_string(nvlist_t *,const char *,const char *);
int nvlist_add_uint64(nvlist_t *,const char *,uint64_t);
static int aether_pool_config_hash(nvlist_t *,uint64_t *);
int spa_import(const char *,nvlist_t *,nvlist_t *,int);
int spa_open(const char *,spa_t **,void *);
int spa_writeable(spa_t *);
unsigned spa_version(spa_t *);
uint64_t spa_guid(spa_t *);
int spa_feature_is_active(spa_t *,int);
int zap_lookup(void *,uint64_t,const char *,unsigned,unsigned,void *);
void spa_close(spa_t *,void *);
void dmu_buf_user_evict_wait(void);
void spa_namespace_enter(void *);
void spa_namespace_exit(void *);
spa_t *spa_lookup(const char *);
spa_t *spa_next(spa_t *);
int spa_refcount_zero(spa_t *);
void spa_evict_all(void);
int aether_home_readback(spa_t *,int,uint64_t,uint64_t,unsigned char [32]);
'''
IMPORT_TAIL = r'''
unsigned long getauxval(unsigned long n) {(void)n;return guard?0:0x50000101UL;}
int zfs_file_open(const char *s,int f,int m,void *v,zfs_file_t **out) {
    (void)s;(void)f;(void)m;(void)v;*out=NULL;return fault==1?0:ENODEV;
}
void aether_engine_utc_phase(unsigned char p) {if(phase_count>=32)abort();phases[phase_count++]=p;}
int aether_pool_label_read(nvlist_t **out) {*out=&nv;return fault==2;}
int aether_pool_label_config(nvlist_t *in,nvlist_t **out) {(void)in;*out=&nv;return fault==3;}
void nvlist_free(nvlist_t *n) {(void)n;}
int nvlist_alloc(nvlist_t **out,int f,int m) {(void)f;(void)m;*out=&nv;return fault==4;}
int nvlist_add_string(nvlist_t *n,const char *k,const char *v) {(void)n;(void)k;(void)v;return fault==5;}
int nvlist_add_uint64(nvlist_t *n,const char *k,uint64_t v) {(void)n;(void)k;return fault==6 || v!=1;}
static int aether_pool_config_hash(nvlist_t *n,uint64_t *h) {(void)n;*h=123;return fault==7;}
int spa_import(const char *s,nvlist_t *n,nvlist_t *p,int f) {(void)s;(void)n;(void)p;(void)f;return fault==8;}
int spa_open(const char *s,spa_t **out,void *t) {(void)s;(void)t;*out=&pool;return fault==9;}
int spa_writeable(spa_t *p) {(void)p;return fault==10;}
unsigned spa_version(spa_t *p) {(void)p;return fault==11?0:5000;}
uint64_t spa_guid(spa_t *p) {(void)p;return fault==12?0:UINT64_C(4253333510760776491);}
int spa_feature_is_active(spa_t *p,int n) {(void)p;return fault!=13 || n!=3;}
int zap_lookup(void *o,uint64_t d,const char *k,unsigned z,unsigned c,void *v) {
    (void)o;(void)d;(void)k;(void)z;(void)c;*(uint64_t *)v=fault==15?0:5000;return fault==14;
}
void spa_close(spa_t *p,void *t) {(void)p;(void)t;closed=1;}
void dmu_buf_user_evict_wait(void) {if(!closed)abort();drained=1;}
void spa_namespace_enter(void *t) {(void)t;}
void spa_namespace_exit(void *t) {(void)t;}
spa_t *spa_lookup(const char *s) {(void)s;return &pool;}
spa_t *spa_next(spa_t *p) {return (evicted && fault!=18) || p?NULL:&pool;}
int spa_refcount_zero(spa_t *p) {(void)p;return fault!=17;}
void spa_evict_all(void) {if(!closed||!drained)abort();evicted=1;}
int aether_home_readback(spa_t *p,int r,uint64_t min,uint64_t max,unsigned char out[32]) {
    if(p!=&pool || r!=EXPECTED_RECOVERED || min!=1791290040 || max!=1791290100)abort();
    oracle_called=1;
    for(unsigned i=0;i<32;i++)out[i]=(unsigned char)i;
    return fault==16;
}
int main(int argc,char **argv) {
    if(argc>1)fault=atoi(argv[1]);if(argc>2)guard=atoi(argv[2]);
    pool.spa_uberblock.ub_txg=EXPECTED_RECOVERED?783:782;
    if(fault==19)pool.spa_uberblock.ub_txg=EXPECTED_RECOVERED?782:783;
    int status=aether_spa_import_probe();
    if(!status && guard) {
        if(phase_count!=1 || phases[0]!='N' || oracle_called || aether_home_reader_ready || closed) return 98;
    } else if(!status) {
        if(!closed || !drained || !evicted || !oracle_called || !aether_home_reader_ready || phase_count!=24) return 97;
        for(unsigned i=0;i<32;i++)if(aether_home_reader_digest[i]!=i)return 96;
    }
    return status?1:0;
}
'''


class HomeReaderImporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-home-importer-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work=Path(cls.temp.name)
        cls.clang=json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']['clang']['path']
        (cls.work/'sys').mkdir()
        for name in ('dmu.h','zap.h','spa_impl.h'):(cls.work/'sys'/name).write_text('')
        (cls.work/'home-recovery-probe.h').write_text('') # typed five-argument declaration above
        original=(ROOT/'user/storage/openzfs-volume/spa-zpl-recover.inc').read_text()
        sdk=cls.run_owned(['/usr/bin/xcrun','--show-sdk-path'],'importer-sdk')
        if sdk.returncode: raise AssertionError(sdk.stderr.decode())
        cls.sdk=sdk.stdout.decode().strip()
        if not Path(cls.sdk).is_dir(): raise AssertionError('missing actual host SDK')
        cls.executables=[]
        for recovered in (False,True):
            stem='recovered' if recovered else 'pristine'
            source=cls.work/(stem+'.c')
            source.write_text(IMPORT_HEAD+reader.render_importer(original,recovered)+IMPORT_TAIL)
            exe=cls.work/stem
            result=cls.run_owned([cls.clang,'--no-default-config','-std=c17','-isysroot',
                cls.sdk,'-MD','-MF',cls.work/(stem+'.d'),'-I'+str(cls.work),
                '-DEXPECTED_RECOVERED='+str(int(recovered)),'-Wall','-Wextra','-Werror','-Wformat=2',
                '-fsanitize=undefined','-fno-sanitize-recover=all',source,'-o',exe],stem+'-compile')
            if result.returncode:raise AssertionError(result.stderr.decode())
            cls.executables.append(exe)

    @classmethod
    def run_owned(cls,argv,label):
        return run_child(cls.work,argv,label)

    def test_actual_fresh_import_close_drain_retire_and_explicit_oracle_roles(self):
        for exe in self.executables:
            result=self.run_owned([exe],exe.name+'-healthy')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout,b'')

    def test_import_metadata_readback_and_retirement_failures_reject(self):
        for exe in self.executables:
            for fault in range(2,20):
                with self.subTest(role=exe.name,fault=fault):
                    result=self.run_owned([exe,str(fault)],exe.name+'-fault-'+str(fault))
                    self.assertNotEqual(result.returncode,0,'import/read/retire semantic failure '+str(fault))
                    self.assertEqual(result.stdout,b'')

    def test_denied_storage_never_imports_or_reads(self):
        for exe in self.executables:
            result=self.run_owned([exe,'0','1'],exe.name+'-denied')
            self.assertEqual(result.returncode,0,result.stderr)
            result=self.run_owned([exe,'1','1'],exe.name+'-denial-missing')
            self.assertNotEqual(result.returncode,0)

    def test_exact_recipe_replacements_and_map_insertion(self):
        argv=['ld','old.o','-o','old.elf']
        self.assertEqual(reader._relink(argv,{'old.o':'new.o'},'new.elf','new.map'),
                         ['ld','new.o','-Map=new.map','-o','new.elf'])
        for args in (['ld','-o','old.elf'],['ld','old.o','old.o','-o','old.elf'],
                     ['ld','old.o','-Map=a','-Map=b','-o','old.elf'],['ld','old.o','-o','old.elf','tail']):
            with self.assertRaises(ValueError):reader._relink(args,{'old.o':'new.o'},'new.elf','new.map')


if __name__=='__main__':
    unittest.main()
