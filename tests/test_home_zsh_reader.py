# SPDX-License-Identifier: BSD-2-Clause
"""Pure fixed Zsh home reader controls, never runtime or durability evidence."""
import ast
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import home_zsh_reader as reader


def projection(recovered=False, digest=bytes(range(32))):
    return b''.join(bytes((value,))+bytes(7) for value in digest+reader.tag(recovered))


class HomeZshReader(unittest.TestCase):
    def test_distinct_full_projection_and_explicit_role(self):
        for recovered in (False, True):
            result = reader.decode_result(projection(recovered), recovered)
            self.assertEqual(result['metadata_sha256'], bytes(range(32)).hex())
            self.assertEqual(result['tag_hex'], reader.tag(recovered).hex())
        with self.assertRaises(ValueError):
            reader.decode_result(projection(True), False)
        for bad in (1, None, 'recovery'):
            with self.assertRaises(ValueError): reader.tag(bad)

    def test_exact_extent_padding_and_tag(self):
        raw = projection(True)
        for changed in (raw[:-1], raw+bytes(8), raw[:1]+b'X'+raw[2:],
                        raw[:32*8]+bytes(8*8)):
            with self.assertRaises(ValueError): reader.decode_result(changed, True)

    def test_pristine_and_recovery_original_metadata_must_match(self):
        before = reader.decode_result(projection(), False)
        after = reader.decode_result(projection(True), True)
        result = reader.compare_results(before, after)
        self.assertEqual(result['metadata_sha256'], before['metadata_sha256'])
        self.assertFalse(result['native_executed'] or result['persistence_verified'])
        changed = dict(after, metadata_sha256='f'*64)
        with self.assertRaises(ValueError): reader.compare_results(before, changed)
        with self.assertRaises(ValueError): reader.compare_results(after, before)

    def test_controller_keeps_readonly_denied_rows_and_bounded_extent(self):
        original = (ROOT/'user/storage/session/home-readback.rs').read_text()
        rendered = reader.render_controller(original)
        self.assertIn('bytes.len() == 320', rendered)
        self.assertIn('let length = if generation == 1 { 320 } else { 24 };', rendered)
        self.assertIn('row[5] = 32;', rendered)
        self.assertIn('row[7] = 32;', rendered)
        self.assertIn('let region = [8u64, 2097152, 1];', rendered)
        with self.assertRaises(ValueError): reader.render_controller(original+' ')

    def test_actual_importer_uses_new_oracle_and_old_readonly_lifetime(self):
        source = (ROOT/'user/storage/openzfs-volume/spa-zpl-recover.inc').read_text()
        for recovered in (False, True):
            text = reader.render_importer(source, recovered)
            self.assertIn('aether_home_zsh_readback(spa,', text)
            self.assertIn('aether_zsh_home_result', text)
            self.assertIn('spa_import', text)
            self.assertNotIn('aether_home_mktemp_readback', text)
        self.assertNotIn('subprocess', (ROOT/'scripts/home_zsh_reader.py').read_text())



def namespace_fixture():
    """Actual new C namespace/inventory bodies over an explicit typed provider model.

    The SHA stub models the fixed-asset provider boundary; it is not crypto,
    OpenZFS decoding, namespace persistence, or actual reader execution evidence.
    Original OpenZFS/SA/ACL and shutdown checks still require target qualification.
    """
    text = (ROOT/'user/storage/openzfs-volume/home-recovery-probe.c').read_text()
    def body(name):
        at = text.index(name)
        opening = text.index('{', at)
        depth = 0
        for i in range(opening, len(text)):
            depth += (text[i] == '{') - (text[i] == '}')
            if not depth:
                return text[at:i+1]
        raise ValueError('unterminated actual reader function')
    functions = '\n'.join(body(name) for name in (
        'static int home_time_before(', 'static int home_inventory(',
        'static int home_zsh_namespace('))
    head = r"""
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define EIO 5
#define EINVAL 22
#define ESRCH 3
#define B_FALSE 0
#define S_IFDIR 0040000U
#define S_IFREG 0100000U
#define SHA256 1
#define MODE_DIR (S_IFDIR|0700U)
#define MODE_FILE (S_IFREG|0600U)
typedef struct {uint64_t object,generation,mode,size;} aether_zpl_node;
typedef struct {void *os;aether_zpl_node root;} aether_zpl_view;
struct home_metadata {uint64_t birthtime[2],mtime[2];};
struct home_workspace {unsigned char buffer[4096];struct home_metadata metadata;};
typedef struct {int valid;} SHA2_CTX;
static int fault;
static aether_zpl_node home={71,3,MODE_DIR,4},probe={101,7,MODE_FILE,16},
    term={157,11,MODE_DIR,3},dir={229,13,MODE_DIR,3},asset={307,17,MODE_FILE,1268};
static const unsigned char expected_hash[32]={
    0x51,0x29,0x24,0xdc,0x4f,0x0c,0x9d,0x70,0xe6,0x62,0x8d,0x63,0x61,0x58,0x84,0xaa,
    0x93,0xfa,0xd7,0xd7,0xfc,0x7a,0x9f,0x62,0xba,0x35,0x36,0xdb,0x24,0x70,0x2d,0xc1};
static void SHA2Init(int which,SHA2_CTX *c){c->valid=which==SHA256;}
static void SHA2Update(SHA2_CTX *c,const void *p,size_t n){
    const unsigned char *b=p;if(n!=1268)c->valid=0;
    for(size_t i=0;i<n;i++)if(b[i]!='V')c->valid=0;
}
static void SHA2Final(unsigned char out[32],SHA2_CTX *c){
    if(c->valid)memcpy(out,expected_hash,32);else memset(out,0,32);
}
static int home_count(aether_zpl_view *v,uint64_t id,uint64_t n){
    (void)v;
    if(id==home.object)return n==2?0:EIO;
    if(id==term.object)return n==1&&fault!=8?0:EIO;
    if(id==dir.object)return n==1?0:EIO;
    return EIO;
}
static int home_new_metadata(aether_zpl_view *v,aether_zpl_node n,uint64_t parent,
        uint64_t links,uint64_t lo,uint64_t hi,struct home_metadata *m){
    (void)v;if(lo!=49||hi!=60||fault==16)return EIO;
    uint64_t birth=0,modified=0;
    if(n.object==home.object&&parent==9&&links==3){birth=50;modified=52;}
    else if(n.object==probe.object&&parent==home.object&&links==1){birth=51;modified=fault==15?54:56;}
    else if(n.object==term.object&&parent==home.object&&links==3){birth=fault==9?51:52;modified=53;}
    else if(n.object==dir.object&&parent==term.object&&links==2&&fault!=10){birth=53;modified=54;}
    else if(n.object==asset.object&&parent==dir.object&&links==1){birth=54;modified=55;}
    else return EIO;
    m->birthtime[0]=birth;m->birthtime[1]=0;m->mtime[0]=modified;m->mtime[1]=0;return 0;
}
static int aether_zpl_lookup(aether_zpl_view *v,uint64_t parent,uint64_t gen,
        const unsigned char *name,size_t length,aether_zpl_node *out){
    (void)v;
    if(parent==home.object&&gen==home.generation&&length==5&&!memcmp(name,"probe",5))*out=probe;
    else if(parent==home.object&&gen==home.generation&&length==9&&!memcmp(name,".terminfo",9)&&fault!=7)*out=term;
    else if(parent==term.object&&gen==term.generation&&length==1&&name[0]=='v')*out=dir;
    else if(parent==dir.object&&gen==dir.generation&&length==5&&!memcmp(name,"vt100",5))*out=asset;
    else return EIO;
    return 0;
}
static int aether_zpl_read(aether_zpl_view *v,uint64_t id,uint64_t gen,uint64_t offset,
        void *out,size_t length,size_t *count){
    (void)v;if(offset)return EIO;
    if(id==probe.object&&gen==probe.generation&&length==16){
        memcpy(out,"AETHER-ZSH-HOME\n",16);if(fault==4)((unsigned char*)out)[3]^=1;
        *count=fault==5?15:16;return 0;
    }
    if(id==asset.object&&gen==asset.generation&&length==1268){
        memset(out,'V',1268);if(fault==12)((unsigned char*)out)[500]^=1;
        *count=fault==14?1267:1268;return 0;
    }
    return EIO;
}
static int home_eof(aether_zpl_view *v,aether_zpl_node node,uint64_t offset,unsigned char *out){
    (void)v;(void)out;
    if(node.object==probe.object)return offset==16&&fault!=6?0:EIO;
    if(node.object==asset.object)return offset==1268&&fault!=13?0:EIO;
    return EIO;
}
static int dmu_object_next(void *os,uint64_t *value,int holes,uint64_t txg){
    (void)os;(void)holes;(void)txg;
    static const uint64_t ids[]={1,2,3,4,5,6,7,8,9,71,101,157,229,307,409};
    unsigned count=fault==17?15:fault==19?13:14;
    for(unsigned i=0;i<count;i++)if(ids[i]>*value){*value=ids[i];return 0;}
    return ESRCH;
}
"""
    tail = r"""
int main(int argc,char **argv){
    if(argc!=2)return 90;fault=atoi(argv[1]);
    if(fault==1)home.size=3;
    if(fault==2)probe.mode=MODE_DIR;
    if(fault==3)probe.size=15;
    if(fault==11)asset.size=1267;
    aether_zpl_view view={0};view.root.object=9;
    struct home_workspace w={0};uint64_t extra[5]={0},root_time[2]={50,0};
    aether_zpl_node observed={0};
    int error=home_zsh_namespace(&view,home,root_time,49,60,&observed,extra,&w);
    if(!error){
        static const uint64_t original[9]={1,2,3,4,5,6,9,7,8};
        if(fault==18)extra[4]=extra[1];
        error=home_inventory(&view,original,extra,fault==20?6:5);
    }
    if(!fault){
        const uint64_t expected[5]={71,101,157,229,307};
        if(error||memcmp(extra,expected,sizeof(expected))){fputs("HEALTHY_ORACLE_REJECT\n",stderr);return 91;}
    }else if(error!=(fault==20?EINVAL:EIO)){
        fprintf(stderr,"ORACLE_BAD_CASE_ACCEPTED_%d\n",fault);return 92;
    }
    return 0;
}
"""
    return head+functions+tail


if __name__ == '__main__': unittest.main()
