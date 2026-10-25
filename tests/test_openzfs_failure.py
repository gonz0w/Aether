# SPDX-License-Identifier: BSD-2-Clause
"""Execute selected allocation guards; diagnostics never certify cleanup."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_failure import instrument, instrument_backend, decode_site, assertion_symbol, FAMILIES
from openzfs_elapsed import CURRENT, patch_alloc_header, patch_kernel, patch_entropy
from openzfs_elapsed import patch_tpool, OWNED
from openzfs_elapsed import function
from test_openzfs_alloc import PREFIX, MAIN


class PoolFailure(unittest.TestCase):
    def test_actual_runtime_wake_wait_failures_preserve_fatal_effects(self):
        original = (CURRENT.parent/'native-utc-v3/base/source/experiments/native-service-runtime/backend.c').read_text()
        marked, _ = instrument_backend(original)
        fatal = marked[marked.index('static _Noreturn void fatal('):marked.index('static void yield(void)')]
        source = '''#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#define SYS_exit_group 231
#define wait private_wait
static unsigned long thread_cap=7;
static int broken;
static unsigned site, expected;
static long answer;
void aether_pool_failure_site(unsigned id) {if(broken!=EIO) exit(94);site=id;}
static long memtrap(unsigned long op,unsigned long cap,unsigned long a,unsigned long b,unsigned long c) {
    (void)a;(void)b;(void)c;
    if(op==0x10000+SYS_exit_group) {
        if(cap!=125 || broken!=EIO || site!=expected) exit(90);
        exit(125);
    }
    if(cap!=7) exit(91);
    return answer;
}
''' + fatal + function(marked,'wake') + function(marked,'wait') + '''
int main(int argc,char **argv) {
    if(argc!=2) return 92;
    unsigned word=0;
    int mode=atoi(argv[1]);
    if(mode==0) wake(&word);
    if(mode==1) {answer=-EIO;expected=96;wake(&word);return 93;}
    if(mode==2) {answer=-EAGAIN;wait(&word,0);}
    if(mode==3) {answer=-EIO;expected=97;wait(&word,0);return 93;}
    if(mode==4) wait(&word,0);
    return site || broken;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-pool-fatal-') as temporary:
            folder=Path(temporary);(folder/'probe.c').write_text(source)
            result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                   '-std=c11','-Wall','-Wextra','-Werror',str(folder/'probe.c'),
                                   '-o',str(folder/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            for mode in range(5):
                self.assertEqual(subprocess.run([str(folder/'probe'),str(mode)],timeout=5).returncode,
                                 125 if mode in (1,3) else 0)

    def test_actual_emitter_payload_preserves_full_request_bits(self):
        body = function((OWNED.parent/'openzfs-volume/pool-failure.c').read_text(),
                        'aether_pool_failure_allocation')
        source = '''#include <stdint.h>
static unsigned char rows[13];
static unsigned count;
void aether_pool_failure_site(unsigned x) { if(count<13) rows[count++]=x; }
''' + body + '''
int main(void) {
    aether_pool_failure_allocation(2, UINT64_C(0x0102030405060708), 0x090a0b0c);
    unsigned char expected[13]={2,8,7,6,5,4,3,2,1,12,11,10,9};
    if(count!=13) return 90;
    for(unsigned i=0;i<13;++i) if(rows[i]!=expected[i]) return 91;
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-pool-payload-') as temporary:
            folder=Path(temporary); (folder/'probe.c').write_text(source)
            result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                   '-std=c11','-Wall','-Wextra','-Werror',str(folder/'probe.c'),
                                   '-o',str(folder/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(subprocess.run([str(folder/'probe')],timeout=5).returncode,0)

    def test_actual_assertion_and_inline_time_guards(self):
        assertion, _ = instrument((CURRENT/'engine/assert-native.c').read_text(), 'assertion')
        # Execute the original native branches, with rejected stderr and observed
        # bounded diagnostic sink. The real _Exit still determines each outcome.
        first = assertion.index('void\nlibspl_set_assert_ok(')
        last = assertion.index('\nstatic pthread_mutex_t assert_lock', first)
        setter = assertion[first:last]
        first = assertion.index('void\nlibspl_assertf(')
        last = assertion.index('#else', first)
        failure = assertion[first:last] + '#endif\n}\n'
        time, _ = instrument((CURRENT/'build-attempt-5/guarded-include/sys/time.h').read_text(), 'time')
        first = time.index('static inline void\ngethrestime(')
        time = time[first:time.index('#endif /* _LIBSPL_SYS_TIME_H */', first)]
        record = function(assertion, 'aether_pool_assertion_record')
        source = r'''#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <time.h>
#define AETHER_NATIVE_PROFILE 1
#define STDERR_FILENO 2
#define NANOSEC 1000000000LL
#define NSEC_PER_USEC 1000LL
typedef int boolean_t;
typedef long long hrtime_t;
typedef struct timespec inode_timespec_t;
static boolean_t libspl_assert_ok;
static unsigned site, expected, writes, want_writes;
static unsigned assertion_line;
static unsigned long long caller;
static int error;
unsigned aether_pool_failure_tid(void) {return 123;}
void aether_pool_failure_pthread(unsigned long long value,unsigned tid) {
 if(value!=11 || tid!=123) _Exit(96);site=66;
}
static struct timespec clock_value={2,123456789};
static int fake_clock(int clock,struct timespec *out) {(void)clock;*out=clock_value;return error;}
#define clock_gettime fake_clock
static long denied_write(int fd,const void *p,unsigned long bytes) {
 (void)p;(void)bytes;if(fd!=2) _Exit(90);++writes;return -1;
}
#define write denied_write
void aether_pool_failure_site(unsigned value) {site=value;}
void aether_pool_failure_assertion(unsigned line,unsigned long long pc) {site=65;assertion_line=line;caller=pc;}
static _Noreturn void checked_exit(int status) {
 if(status!=125 || site!=expected || writes!=want_writes) _Exit(91);
 if(site==65 && (assertion_line!=1234 || !caller)) _Exit(92);
 _Exit(125);
}
#define _Exit checked_exit
''' + record + setter + failure + time + r'''
int main(int argc,char **argv) {
 if(argc!=2) return 93;
 int mode=atoi(argv[1]);inode_timespec_t at;
 if(mode==0) {libspl_set_assert_ok(0);gethrestime(&at);if(at.tv_nsec!=123456000 ||
  gethrestime_sec()!=2 || getlrtime()!=2123456000LL || gethrtime()!=2123456789LL) {return 94;}
  return site || writes;}
 if(mode==1) {expected=64;libspl_set_assert_ok(1);}
 if(mode==2) {expected=65;want_writes=1;libspl_assertf("private", "test",1234,"denied");}
 if(mode==3) {expected=112;error=-1;gethrestime(&at);}
 if(mode==4) {expected=113;clock_value.tv_sec=-1;(void)gethrestime_sec();}
 if(mode==5) {expected=114;clock_value.tv_nsec=NANOSEC;(void)getlrtime();}
 if(mode==6) {expected=115;clock_value.tv_sec=LLONG_MAX/NANOSEC+1;(void)getlrtime();}
 if(mode==7) {expected=116;clock_value.tv_nsec=-1;(void)gethrtime();}
 if(mode==8) {expected=117;clock_value.tv_sec=LLONG_MAX/NANOSEC+1;(void)gethrtime();}
 if(mode==9) {expected=66;want_writes=1;libspl_assertf("private", "zk_thread_create",1234,
   "VERIFY0(%s) failed (%lld)","pthread_create(&tid, &attr, zk_thread_wrapper, ztw)",11ULL);}
 if(mode==10) {expected=65;want_writes=1;libspl_assertf("private", "zk_thread_create",1234,
   "VERIFY0(%s) failed (%lld)","other_expression",11ULL);}
 if(mode==11) {expected=65;want_writes=1;libspl_assertf("private", "other_function",1234,
   "VERIFY0(%s) failed (%lld)");}
 return 95;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-pool-assert-time-') as temporary:
            folder=Path(temporary);(folder/'probe.c').write_text(source)
            result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                   '-std=gnu11','-O2','-Wall','-Wextra','-Werror',str(folder/'probe.c'),
                                   '-o',str(folder/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            for mode in range(12):
                self.assertEqual(subprocess.run([str(folder/'probe'),str(mode)],timeout=5).returncode,
                                 0 if mode==0 else 125,mode)

    def test_actual_assertion_payload_and_symbol_bounds(self):
        body = function((OWNED.parent/'openzfs-volume/pool-failure.c').read_text(),
                        'aether_pool_failure_assertion')
        source = '''#include <stdint.h>
static unsigned char rows[13];
static unsigned count;
void aether_pool_failure_site(unsigned x) { if(count<13) rows[count++]=x; }
''' + body + '''
int main(void) {
    aether_pool_failure_assertion(0x01020304, UINT64_C(0x05060708090a0b0c));
    unsigned char expected[13]={65,4,3,2,1,12,11,10,9,8,7,6,5};
    if(count!=13) return 90;
    for(unsigned i=0;i<13;++i) if(rows[i]!=expected[i]) return 91;
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-pool-assert-payload-') as temporary:
            folder=Path(temporary); (folder/'probe.c').write_text(source)
            result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                   '-std=c11','-Wall','-Wextra','-Werror',str(folder/'probe.c'),
                                   '-o',str(folder/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(subprocess.run([str(folder/'probe')],timeout=5).returncode,0)
        symbols='1000 0020 T actual_caller\n1020 0040 t next\n1000 0020 D data\n'
        self.assertEqual(assertion_symbol(symbols,0x1020)['symbol'],'actual_caller')
        for text,pc in ((symbols,0),(symbols,-1),(symbols,1<<64),(symbols,0x1000),
                        ('1000 0000 T unknown\n',0x1001),
                        (symbols+'1000 0020 T duplicate\n',0x1010)):
            with self.assertRaises(ValueError): assertion_symbol(text,pc)

    def test_actual_allocation_guards_keep_exit_and_side_effects(self):
        original = (CURRENT / 'build-attempt-5/guarded-include/umem.h').read_text()
        selected, _ = instrument(patch_alloc_header(original)[0], 'allocation')
        prefix = PREFIX.replace('static unsigned calls,', '''static unsigned seen, expected_site, expected_error;
static unsigned long long observed_size, expected_size=64;
void aether_pool_failure_site(unsigned site) { seen=site; }
void aether_pool_failure_allocation(unsigned site, unsigned long long size, unsigned error) {
    seen=site; observed_size=size;
    if (size!=expected_size || error!=expected_error) exit(93);
}
static unsigned calls,''')
        prefix = prefix.replace('if (status!=125 || calls!=expected_calls',
                                'if (seen!=expected_site || status!=125 || calls!=expected_calls')
        main = MAIN.replace('int mode=atoi(argv[1]);', '''int mode=atoi(argv[1]);
    if (mode==1 || mode==2 || mode==7 || mode==16) {expected_site=1;expected_error=ENOMEM;}
    if (mode==3 || mode==4 || mode==5) {expected_site=2;expected_error=mode==4?EINVAL:mode==5?EIO:ENOMEM;}
    if (mode==6 || mode==12) expected_site=3;
    if (mode==7) expected_size=sizeof(umem_cache_t);''')
        main = main.replace('    return 0;\n}', '    CHECK(!seen);\n    return 0;\n}')
        with tempfile.TemporaryDirectory(prefix='aether-pool-failure-host-') as temporary:
            out = Path(temporary)
            (out / 'sys').mkdir()
            (out / 'sys/debug.h').write_bytes((CURRENT/'build-attempt-5/guarded-include/sys/debug.h').read_bytes())
            (out / 'umem.h').write_text(selected)
            source = out / 'guards.c'
            source.write_text(prefix + main)
            sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
            result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                     '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                                     '-isysroot', sdk, '-I'+str(out), str(source), '-o', str(out/'guards')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            failures = (1, 2, 3, 4, 5, 6, 7, 12, 16)
            for mode in range(18):
                self.assertEqual(subprocess.run([str(out/'guards'), str(mode)]).returncode,
                                 125 if mode in failures else 0, mode)

    def test_actual_thread_admission_and_clone_denials(self):
        original = (CURRENT.parent/'native-utc-v3/base/source/experiments/native-service-runtime/backend.c').read_text()
        marked, _ = instrument_backend(original)
        admission = function(marked, 'aether_pthread_admit')
        clone = function(marked, '__clone').replace('int __clone(', 'int private_clone(', 1)
        helpers = marked[marked.index('static long thread_denial('):marked.index('int aether_pthread_admit(')]
        # The selected private functions, tested with controlled TLS/attributes,
        # records and native return. Not a reimplementation of their guards.
        source = r'''#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#define pthread_t test_pthread_t
#define pthread_attr_t test_pthread_attr_t
#define pthread_attr_init test_attr_init
struct test_thread {int tid;void *map_base;unsigned long guard_size,map_size;int detach_state;};
typedef struct test_thread *pthread_t;
typedef struct {unsigned _a_stacksize,_a_guardsize,_a_detach,extra;} pthread_attr_t;
#define __ATTRP_C11_THREAD ((void *)(uintptr_t)-1)
#define DT_DETACHED 1
#define CLONE_VM 1
#define CLONE_FS 2
#define CLONE_FILES 4
#define CLONE_SIGHAND 8
#define CLONE_THREAD 16
#define CLONE_SYSVSEM 32
#define CLONE_SETTLS 64
#define CLONE_PARENT_SETTID 128
#define CLONE_CHILD_CLEARTID 256
#define CLONE_DETACHED 512
static struct test_thread self={.tid=73};
static pthread_t __pthread_self(void) {return &self;}
unsigned aether_pool_failure_tid(void) {return (unsigned)self.tid;}
static int pthread_attr_init(pthread_attr_t *a) {memset(a,0,sizeof *a);return 0;}
static unsigned initialized,closing,admissions,live,capacity=82;
static int broken;
static volatile int __thread_list_lock=73;
static unsigned calls,seen_stage,seen_value,seen_tid;
static long seen_error,answer;
static unsigned long thread_cap=7;
void aether_pool_failure_denial(unsigned stage,long error,unsigned value,unsigned tid) {
 if(seen_stage) exit(90);
 seen_stage=stage;seen_error=error;seen_value=value;seen_tid=tid;
}
''' + original[original.index('struct record {'):original.index('static _Noreturn void fatal(')] + r'''
static void trampoline(unsigned long value) {(void)value;}
static int worker(void *value) {(void)value;return 0;}
static long memtrap(unsigned long op,unsigned long cap,unsigned long a,unsigned long b,unsigned long c) {
 ++calls;if(op!=0x28006 || cap!=7 || b || c) exit(91);
 struct descriptor *d=(void *)a;
 if(d->version!=1 || d->size!=96 || d->reserved || d->base!=0x11000 || d->bytes!=0x3f000) exit(92);
 return answer;
}
''' + helpers.replace('static long thread_result(', 'long thread_result(') + admission + clone + r'''
int main(int argc,char **argv) {
 if(argc!=2) return 93;
 int mode=atoi(argv[1]);initialized=1;
 pthread_attr_t attr={262144,4096,0,0};const void *given=&attr;
 int expected=0;unsigned stage=0,value=0;long result;
 if(mode<=12) {
  if(mode==1) {initialized=0;expected=ENOSYS;stage=1;}
  if(mode==2) {broken=EIO;expected=EIO;stage=1;}
  if(mode==3) {closing=1;admissions=512;live=82;expected=EAGAIN;stage=2;value=1;}
  if(mode==4) {admissions=512;live=82;expected=EAGAIN;stage=3;value=512;}
  if(mode==5) {live=82;expected=EAGAIN;stage=4;value=82;}
  if(mode==6) {given=__ATTRP_C11_THREAD;expected=ENOTSUP;stage=5;}
  if(mode==7) {attr._a_stacksize=16383;expected=ENOTSUP;stage=6;}
  if(mode==8) {attr._a_stacksize=262145;expected=ENOTSUP;stage=6;}
  if(mode==9) {attr._a_guardsize=4097;expected=ENOTSUP;stage=6;}
  if(mode==10) {attr.extra=1;expected=ENOTSUP;stage=7;}
  if(mode==11) given=0;
  if(mode==12) {attr._a_detach=1;attr._a_guardsize=8192;}
  result=aether_pthread_admit(given);
  if(calls) return 94;
 } else {
  struct test_thread td={.tid=74,.map_base=(void *)0x10000,.guard_size=4096,.map_size=262144};
  int flags=1023,parent=0;void *stack=(void *)0x50000;answer=5;
  if(mode==14) {flags=0;expected=-ENOTSUP;stage=8;}
  if(mode==15) {__thread_list_lock=0;expected=-ENOTSUP;stage=8;}
  if(mode==16) {closing=1;expected=-EAGAIN;stage=9;}
  if(mode==17) {broken=EIO;expected=-EIO;stage=9;}
  if(mode==18) {admissions=512;expected=-EAGAIN;stage=9;}
  if(mode==19) {for(unsigned i=0;i<82;++i) records[i].thread=&self;expected=-EAGAIN;stage=10;value=82;}
  if(mode==20) {td.map_base=0;expected=-EINVAL;stage=11;}
  if(mode==21) {stack=(void *)0x11000;expected=-EINVAL;stage=12;}
  if(mode==22) {answer=-ENOMEM;expected=-ENOMEM;stage=13;}
  if(mode==13) expected=5;
  result=private_clone(worker,stack,flags,&self,&parent,&td,&__thread_list_lock);
  if(calls!=(unsigned)(mode==13 || mode==22)) return 95;
  if(mode==13) {
   if(live!=1 || admissions!=1 || records[0].thread!=&td || !records[0].published ||
     records[0].id!=5 || records[0].base!=0x10000 || records[0].bytes!=262144) return 96;
  } else if(live || records[0].published || (mode!=18 && admissions)) return 97;
 }
 if(result!=expected || seen_stage!=stage || (stage && (seen_error!=expected ||
   seen_value!=value || seen_tid!=73))) return 98;
 return 0;
}
'''
        self.compile_probe(source, range(23), 'thread-branches')

    def test_actual_mapping_and_mask_returns_are_not_retried(self):
        original=(CURRENT.parent/'native-utc-v3/base/source/experiments/native-service-runtime/backend.c').read_text()
        marked,_=instrument_backend(original)
        body=marked[marked.index('long aether_wait_syscall('):marked.index('long __aether_io(')]
        # Run the exact selected memory/mask prefix on this ARM host; unrelated
        # x86 futex inline assembly remains covered by the existing native profile.
        body=body[:body.index('    if (n == SYS_futex')]+'    return -ENOSYS;\n}\n'
        helpers=marked[marked.index('static long thread_denial('):marked.index('int aether_pthread_admit(')]
        calls=sorted(set(re.findall(r'\bSYS_\w+',body)))
        source=r'''#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#define FUTEX_WAIT 0
#define FUTEX_WAKE 1
#define FUTEX_REQUEUE 3
#define FUTEX_PRIVATE 128
#define MAP_PRIVATE 2
#define MAP_ANONYMOUS 32
static unsigned long thread_cap=7,memory_cap=8;
unsigned aether_pool_failure_tid(void) {return 73;}
static unsigned calls,stage,value,actor;
static long answer,seen_error;
void aether_pool_failure_denial(unsigned s,long error,unsigned v,unsigned tid) {stage=s;seen_error=error;value=v;actor=tid;}
static long aether_sleep_syscall(long n,long a,long b,long c,long d) {(void)n;(void)a;(void)b;(void)c;(void)d;exit(91);}
static long memtrap(unsigned long op,unsigned long cap,unsigned long a,unsigned long b,unsigned long c) {
 (void)a;(void)b;(void)c;
 if((op==0x28009 && cap!=7) || (op!=0x28009 && cap!=8)) exit(92);
 ++calls;return answer;
}
''' + ''.join(f'#define {name} {i+100}\n' for i,name in enumerate(calls)) + helpers + body + r'''
int main(int argc,char **argv) {
 if(argc!=2) return 93;int mode=atoi(argv[1]);int kind=mode/3;
 answer=mode%3==0?-ENOMEM:mode%3==1?0:4096;
 long result;
 if(kind==0) result=aether_wait_syscall(SYS_rt_sigprocmask,0,0,0,8,0,0);
 else if(kind==1) result=aether_wait_syscall(SYS_mmap,0,4096,3,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 else if(kind==2) result=aether_wait_syscall(SYS_mprotect,4096,4096,3,0,0,0);
 else result=aether_wait_syscall(SYS_munmap,4096,4096,0,0,0,0);
 if(result!=answer || calls!=1) return 94;
 if(answer<0) {if(stage!=14+(unsigned)kind || seen_error!=answer || value || actor!=73) return 95;}
 else if(stage) return 96;
 return 0;
}
'''
        self.compile_probe(source,range(12),'mapping-returns')

    def compile_probe(self, source, modes, label):
        with tempfile.TemporaryDirectory(prefix='aether-pool-'+label+'-') as temporary:
            folder=Path(temporary);(folder/'probe.c').write_text(source)
            result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                   '-std=gnu11','-O2','-Wall','-Wextra','-Werror',str(folder/'probe.c'),
                                   '-o',str(folder/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            for mode in modes:
                self.assertEqual(subprocess.run([str(folder/'probe'),str(mode)],timeout=5).returncode,0,mode)

    def test_actual_thread_payload_bounds(self):
        source_text=(OWNED.parent/'openzfs-volume/pool-failure.c').read_text()
        source=r'''#include <stdlib.h>
#include <stdint.h>
static unsigned char rows[17];static unsigned count;
void aether_pool_failure_site(unsigned value) {if(count>=17) exit(90);rows[count++]=value;}
''' + function(source_text,'aether_pool_failure_denial') + function(source_text,'aether_pool_failure_pthread') + r'''
int main(int argc,char **argv) {
 if(argc!=2) return 91;int mode=atoi(argv[1]);
 long error=mode==0?-12:mode==1?32768:mode==2?-32768:mode==3?0:-12;
 unsigned value=mode==4?65536:82,tid=mode==5?0:0x12345678;
 aether_pool_failure_denial(13,error,value,tid);
 aether_pool_failure_pthread(mode==6?65547:mode==7?UINT64_MAX:11,tid);
 if(count!=17 || rows[0]!=120 || rows[10]!=66) return 92;
 if(mode==0) {
  unsigned char expected[17]={120,13,244,255,82,0,120,86,52,18,66,11,0,120,86,52,18};
  for(unsigned i=0;i<17;++i) if(rows[i]!=expected[i]) return 93;
 }
 if(mode>=1 && mode<=5 && (rows[1] || rows[2] || rows[3])) return 94;
 if((mode==6 || mode==7) && (rows[11] || rows[12])) return 95;
 return 0;
}
'''
        self.compile_probe(source, range(8), 'thread-payload')

    def test_thread_decoder_requires_matched_original_error(self):
        catalogue=[{'site':66,'family':'pthread-assertion'},{'site':120,'family':'thread-denial'}]
        def trace(stage=4,error=11,value=82,tid=73,pthread=11,actor=73,denial=True):
            data=b'BIUVWP'+bytes(range(8))+b'C'
            if denial:
                data+=bytes([120,stage])+error.to_bytes(2,'little',signed=True)+value.to_bytes(2,'little')+tid.to_bytes(4,'little')
            data+=bytes([66])+pthread.to_bytes(2,'little')+actor.to_bytes(4,'little')
            return ''.join(f'NATIVE observation slot=0 generation=1 offset={i*8} byte={b}\n'
                           for i,b in enumerate(data))+'NATIVE terminal slot=0 generation=1 kind=1 detail=125\nNATIVE supervisor result=401 reclaimed=0\n'
        result=decode_site(trace(),catalogue)
        self.assertEqual(result['denial']['branch'],'admission-live-limit')
        self.assertEqual(result['denial']['compared_value'],82)
        self.assertEqual(result['pthread_error'],11)
        self.assertFalse(result['denial']['joint_resource_snapshot'])
        self.assertIsNone(decode_site(trace(denial=False),catalogue)['denial'])
        for stage,error,pthread in ((13,-12,11),(15,-12,11),(16,-22,11),(14,-5,5),(5,95,95)):
            self.assertEqual(decode_site(trace(stage,error,0,pthread=pthread),catalogue)['pthread_error'],pthread)
        for change in ({'tid':74},{'actor':0},{'pthread':0},{'pthread':32768},{'pthread':12},
                       {'stage':0},{'stage':255},{'error':0},{'error':-32768},{'value':81},
                       {'stage':3,'value':511},{'stage':2,'value':0},
                       {'stage':10,'error':-11,'value':81},
                       {'stage':13,'error':12,'value':0},
                       {'stage':13,'error':-12,'value':0,'pthread':12},
                       {'stage':17,'error':-12,'value':0}):
            with self.subTest(change=change),self.assertRaises(ValueError): decode_site(trace(**change),catalogue)
        good=trace()
        for bad in (good.replace('offset=200 byte=66','offset=200 byte=120'),
                    good.replace('generation=1','generation=2',1),
                    good.replace('detail=125','detail=0'),
                    good.replace('reclaimed=0','reclaimed=1'),
                    good.replace('offset=248','offset=240'),
                    good[:good.index('NATIVE observation slot=0 generation=1 offset=248')]+
                    good[good.index('NATIVE terminal '):]):
            with self.assertRaises(ValueError): decode_site(bad,catalogue)

    def test_source_catalogue_and_drift(self):
        kernel = (CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        text = patch_entropy(patch_kernel(kernel)[0])[0]
        sources = {'kernel': text,
                   'tpool': patch_tpool((CURRENT/'previous-build/source/thread_pool.c').read_text())[0],
                   'allocation': patch_alloc_header((CURRENT/'build-attempt-5/guarded-include/umem.h').read_text())[0],
                   'resources': (OWNED/'resources.c').read_text(),
                   'startup': (OWNED/'startup.c').read_text(),
                   'arc': (OWNED/'arc-functions.c').read_text(),
                   'assertion': (CURRENT/'engine/assert-native.c').read_text(),
                   'time': (CURRENT/'build-attempt-5/guarded-include/sys/time.h').read_text()}
        all_sites = []
        for family, text in sources.items():
            marked, rows = instrument(text, family)
            self.assertEqual(len(rows), FAMILIES[family][1] + (family == 'assertion'))
            self.assertEqual(marked.count('_Exit(125);'), 0)
            all_sites += [r['site'] for r in rows]
            for changed in (text.replace('_Exit(125);', '', 1), text + '_Exit(125);'):
                with self.assertRaises(ValueError):
                    instrument(changed, family)
        backend = (CURRENT.parent/'native-utc-v3/base/source/experiments/native-service-runtime/backend.c').read_text()
        marked, rows = instrument_backend(backend)
        self.assertEqual(len(rows), 10)
        self.assertIn('broken = EIO;', marked)
        self.assertIn('memtrap(0x10000 + SYS_exit_group, 125, 0, 0, 0)', marked)
        with self.assertRaises(ValueError):
            instrument_backend(backend.replace('fatal();', '', 1))
        for old,new in (('live >= capacity','live > capacity'),
                        ('return memtrap(0x22001, memory_cap, b, c, 0);','return -12;')):
            with self.assertRaises(ValueError): instrument_backend(backend.replace(old,new,1))
        all_sites += [r['site'] for r in rows] + [80]
        self.assertEqual(len(all_sites), len(set(all_sites)))
        self.assertEqual(len(all_sites), 46)

    def test_decoder_requires_exact_failure_not_cleanup(self):
        def trace(site, payload=b''):
            data = b'BIUVWP' + bytes(range(8)) + b'C' + bytes([site]) + payload
            return ''.join(f'NATIVE observation slot=0 generation=1 offset={i*8} byte={b}\n'
                           for i, b in enumerate(data)) + (
                'NATIVE terminal slot=0 generation=1 kind=1 detail=125\n'
                'NATIVE supervisor result=401 reclaimed=0\n')
        catalogue = [{'site': 1, 'family': 'allocation'}, {'site': 96, 'family': 'runtime'},
                     {'site':65,'family':'assertion'}]
        good = trace(1, (1048576).to_bytes(8,'little') + (12).to_bytes(4,'little'))
        result = decode_site(good, catalogue)
        self.assertEqual((result['requested_bytes'], result['error_bits']), (1048576,12))
        self.assertEqual(decode_site(trace(96), catalogue)['family'], 'runtime')
        assertion=trace(65,(1234).to_bytes(4,'little')+(0x12345678).to_bytes(8,'little'))
        self.assertEqual(decode_site(assertion,catalogue)['assertion_line'],1234)
        self.assertEqual(decode_site(assertion,catalogue)['caller_return_address'],0x12345678)
        for bad in (trace(1), trace(255), good.replace('generation=1', 'generation=2',1),
                    good.replace('detail=125','detail=0'), good.replace('reclaimed=0','reclaimed=3'),
                    trace(96,b'\0'*12), trace(65), assertion.replace('byte=67','byte=66'),
                    good.replace('offset=120','offset=112')):
            with self.assertRaises(ValueError):
                decode_site(bad, catalogue)
        with self.assertRaises(ValueError):
            decode_site(good, catalogue+catalogue)
