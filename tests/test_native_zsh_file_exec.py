# SPDX-License-Identifier: BSD-2-Clause
"""Closed filesystem snapshot exec source/actual-body fixture; no guest.

Run python3 -B -m unittest discover -s tests -p test_native_zsh_file_exec.py -v.
The public unittest checks are stdlib-only. Qualified host capture compiles
checker_source with current kernel modules; this fixture does not depend on
uncommitted host runner APIs.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def block(source, anchor):
    start = source.index(anchor)
    opening = source.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def literal(path, name):
    tree = ast.parse(path.read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


FACADE = '''pub const App=@import("native_app.zig");pub const elf=@import("native_elf.zig");
pub const memory=@import("native_memory.zig");pub const roles=@import("arch/x86_64/native_fs_roles.zig");
pub const launch=@import("native_launch.zig");pub const Pending=@import("arch/x86_64/native_pending.zig");
pub const Channel=@import("native_channel.zig").Channel;'''


def checker_source(native, omission=None):
    scaffold = literal(ROOT / 'tests/test_fs_application_profile.py', 'SCAFFOLD').split('fn launchCase()', 1)[0]
    scaffold = scaffold.replace('const elf=@import("elf");', 'const K=@import("kernel");const App=K.App;const elf=K.elf;const launch=K.launch;')
    scaffold = scaffold.replace('const memory=@import("memory");', 'const memory=K.memory;').replace('const FsRoles=@import("roles");', 'const FsRoles=K.roles;')
    scaffold = scaffold.replace('app_binding:struct{clock:u64=0,fn bound(b:*const @This())bool{return b.clock!=0;}}=.{},',
                                'app_binding:K.App.Binding=.{},tty_signal_owner_generation:?u64=null,signal_actions:K.Pending.State=.{},')
    start = scaffold.index('const Channel=struct{')
    end = scaffold.index('\nvar channels:', start)
    scaffold = scaffold[:start] + 'const Channel=K.Channel;' + scaffold[end:]
    scaffold = scaffold.replace('var channels:[2]Channel', 'var channels:[12]Channel')
    scaffold = scaffold.replace('var third_bytes:[1]u8=.{0};', 'var third_bytes:[4096]u8=@splat(0);')
    scaffold = scaffold.replace(block(scaffold, 'fn ownedChannel('),
        'fn ownedChannel(owner:usize,cap:u64)?*Channel{for(&channels)|*c|if(c.lookup(owner,cap)!=null)return c;return null;}')
    scaffold = scaffold.replace(block(scaffold, 'fn byte('),
        'fn byte(_: *State,address:usize,_:bool)?*u8{if(address>=0x1000 and address-0x1000<args_mapped)return &raw_args[address-0x1000];if(address>=0x3000 and address-0x3000<file_mapped)return &raw_file[address-0x3000];if(address>=0x6000 and address-0x6000<app_raw.len)return &app_raw[address-0x6000];return null;}')
    scaffold = scaffold.replace('fn lookup(value:u64)?usize{return if(value>0 and value<6 and states[value].admitted) @intCast(value) else null;}', 'fn lookup(value:u64)?usize{if(value==100 and states[0].admitted)return 0;return if(value>0 and value<6 and states[value].admitted) @intCast(value) else null;}')
    scaffold = scaffold.replace('fn result(_: *State,value:i64)void{response=value;}',
        'fn result(s:*State,value:i64)void{response=value;s.execution.frame.rax=@bitCast(value);}')
    scaffold = scaffold.replace(block(scaffold, 'fn load('), '''fn load(s:*State,bytes:[]const u8,image:*const elf.Image,_:[]const u8,_:usize)void{
 check((launch.backingPages(image) catch unreachable)<=s.pages.len,"IMAGE_CAPACITY_BEFORE_RESET");
 if(image.entry==0x200180){check(std.mem.allEqual(u8,s.payloadBytes(),0),"OLD_PAYLOAD_ZERO_BEFORE_LOAD");check(std.mem.allEqual(u8,s.recordBytes(),0),"OLD_RECORDS_ZERO_BEFORE_LOAD");}
 loaded_len=bytes.len;loaded_marker=if(bytes.len>384)bytes[384] else 0;loaded_entry=image.entry;mutations+=1;
 s.count=launch.backingPages(image) catch unreachable;s.admitted=true;
}''')
    bodies = '\n'.join(block(native, 'fn ' + name + '(') for name in
        ('imagePreflight', 'fileExecOperation', 'execOperation', 'ordinaryAppEnabled', 'appLaunchOperation', 'launchOperation'))
    aliases = block(native, 'fn aliases(')
    bodies += '\n' + aliases[:aliases.index('    asm volatile')] + '}\n'
    changes = {
        'authority': ('active != supervisorSlot() or !caller.admitted or caller.terminal or f.rdi != 0xa001', 'false'),
        'epoch': ('engine.channel_cap != parent.app_binding.epoch', 'false'),
        'one-shot': (' or s.image_commit.sequence != 0', ''),
        'scratch-clear': ('defer @memset(scratch, 0);', ''),
        'exec-fallback': ('and f.rax == 0x23007)', 'and false)'),
        'app-fallback': ('if (@hasDecl(@import("build_options"), "native_zsh_file_exec") and @import("build_options").native_zsh_file_exec and f.rsi == 0xc003)', 'if (false)'),
        'generic-fallback': ('if (@hasDecl(@import("build_options"), "native_zsh_file_exec") and @import("build_options").native_zsh_file_exec) {', 'if (false) {'),
    }
    if omission:
        old, new = changes[omission]
        assert bodies.count(old) == 1, (omission, bodies.count(old))
        bodies = bodies.replace(old, new)
        if omission == 'app-fallback':
            # Existing external admission is another enforcing guard for C003.
            old = 'if (f.rsi != 0xc002 or f.rdx != 1)'
            assert bodies.count(old) == 1
            bodies = bodies.replace(old, 'if (false)')
    extra = '''
const af09_enabled=false;const af09=struct{const engine_bound=false;};
fn af09Fail(_:usize,_:i64)void{unreachable;}
const combined_init=true;const combined_owner_stack=true;const launch_profile=true;const connections_profile=true;
fn channelCount()usize{return channels.len;}
var app_raw:[320]u8=@splat(0);var raw_file:[4096]u8=@splat(0);var args_mapped:usize=272;var file_mapped:usize=4096;
var loaded_len:usize=0;var loaded_marker:u8=0;var loaded_entry:usize=0;
fn put16(at:usize,value:u16)void{std.mem.writeInt(u16,raw_file[at..][0..2],value,.little);}
fn put32(at:usize,value:u32)void{std.mem.writeInt(u32,raw_file[at..][0..4],value,.little);}
fn put64(at:usize,value:u64)void{std.mem.writeInt(u64,raw_file[at..][0..8],value,.little);}
fn ph(index:usize,kind:u32,flags:u32,offset:u64,address:u64,filesz:u64,memsz:u64)void{
 const at=64+index*56;put32(at,kind);put32(at+4,flags);put64(at+8,offset);put64(at+16,address);put64(at+32,filesz);put64(at+40,memsz);put64(at+48,1);
}
'''
    return scaffold + extra + bodies + CASES


OPTIONS = dict(native_zsh_external=True, native_zsh_terminfo=True, native_tty_mode_probe=True,
               native_tty_signal_probe=True, native_service_lifetime=False, native_process_exec=True,
               native_signal_actions=True, native_exec_token=False, native_exec_early=False)

CASES = r'''
fn setup(length:usize)void{
 reset();args_mapped=272;file_mapped=4096;loaded_len=0;loaded_marker=0;loaded_entry=0;
 for(&channels,0..) |*c,i|{c.identity=i;check(c.createSession(6)>0,"CREATE_OWNED_CHANNEL");}
 const request=channels[10].cap(0);const reply=channels[11].cap(1);
 check(channels[10].transfer(6,request,0) and channels[11].transfer(6,reply,0),"ENGINE_COUNTERPARTS");
 states[0].admitted=true;states[0].channel_cap=request;states[0].channel_reply_cap=reply;
 states[6].admitted=true;states[6].generation=11;
 states[1].admitted=true;states[1].app_binding=K.App.Binding.init(1,7,channels[11].cap(0),channels[10].cap(1),request).?;
 states[1].tty_signal_owner_generation=11;
 states[2].admitted=true;states[2].generation=8;states[2].parent_pid=51;states[2].frozen=true;states[2].freeze_sequence=6;
 states[2].ready=true;states[2].app_binding=K.App.Binding.init(2,8,channels[11].cap(0),channels[10].cap(1),request).?;
 raw_file=@splat(0);@memcpy(raw_file[0..8],"\x7fELF\x02\x01\x01\x00");
 put16(16,2);put16(18,62);put32(20,1);put64(24,0x200180);put64(32,64);put16(52,64);put16(54,56);put16(56,4);
 ph(0,1,5,0,0x200000,length,length);ph(1,6,4,64,0x200040,4*56,4*56);
 ph(2,7,4,320,0x200140,1,1);ph(3,0x6474e551,6,0,0,0,0);raw_file[384]=0x5a;
 app_raw=@splat(0);@memcpy(app_raw[0..8],"AENAP002");std.mem.writeInt(u64,app_raw[8..16],320,.little);app_raw[16]=1;
 std.mem.writeInt(u64,app_raw[288..296],100,.little);std.mem.writeInt(u64,app_raw[296..304],channels[11].cap(0),.little);std.mem.writeInt(u64,app_raw[304..312],channels[10].cap(1),.little);
 third_bytes=@splat(0xa5);
}
fn fileFrame(length:usize)Frame{return .{.rax=0x2300b,.rdi=0xa001,.rsi=2,.rdx=0x3000,.r10=6,.r8=0x1000,.r9=length};}
fn clean()bool{return std.mem.allEqual(u8,&third_bytes,0);}
fn preserved(before:State)bool{return std.meta.eql(before,states[2]) and mutations==0 and storage[2][0][0]==0xa5 and storage[2][639][4095]==0xa5;}
fn success()void{
 for([_]usize{512,4096})|length|{
  setup(length);const old_binding=states[2].app_binding;_=fileExecOperation(&fileFrame(length));
  check(response==0 and loaded_len==length and loaded_marker==0x5a and loaded_entry==0x200180,"COPIED_FILESYSTEM_IMAGE_LOADED");
  check(states[2].image_commit.sequence==6 and states[2].image_commit.image==0xc004 and states[2].image_commit.pending and states[2].frozen and !states[2].ready,"FILESYSTEM_RECEIPT_PENDING");
  check(states[2].generation==8 and std.meta.eql(old_binding,states[2].app_binding) and states[2].tty_signal_owner_generation==null,"LIFETIME_AND_BINDING_RETAINED");
  check(clean() and third_len==1 and third_image.entry==0x200000,"SCRATCH_CLEARED_GLOBAL_METADATA_UNCHANGED");
  _=execOperation(&.{.rax=0x23008,.rdi=0xa001,.rsi=2});
  check(response==6 and states[6].execution.frame.rdx==0xc004 and states[6].execution.frame.r8==1,"C004_QUERY");
  _=execOperation(&.{.rax=0x23009,.rdi=0xa001,.rsi=2,.rdx=5});check(response==-9 and states[2].image_commit.pending,"BAD_PUBLISH_TOKEN_REJECTED");
  _=execOperation(&.{.rax=0x23009,.rdi=0xa001,.rsi=2,.rdx=6});check(response==0 and !states[2].frozen and !states[2].image_commit.pending,"C004_PUBLISHED");
  states[2].frozen=true;states[2].freeze_sequence=7;var again=fileFrame(length);again.r10=7;const before=mutations;
  _=fileExecOperation(&again);check(response==-16 and mutations==before and states[2].image_commit.sequence==6 and clean(),"SECOND_COMMIT_AFTER_PUBLICATION_DENIED");
 }
}
fn authority()void{
 for(0..21)|case|{
  setup(512);var f=fileFrame(512);
  switch(case){0=>active=1,1=>f.rdi=0,2=>states[6].admitted=false,3=>states[6].terminal=true,
   4=>f.rsi=1,5=>states[1].generation+=1,6=>states[6].generation+=1,7=>states[2].generation+=1,
   8=>states[2].parent_pid=0,9=>states[2].tty_signal_owner_generation=11,10=>states[2].app_binding.epoch+=1,
   11=>states[0].terminal=true,12=>states[0].admitted=false,13=>states[0].channel_cap+=256,
   14=>channels[11].owners[1]=5,15=>channels[10].owners[1]=5,16=>channels[10].stream.sealed=true,
   17=>channels[11].stream.reader_closed=true,18=>states[1].terminal=true,19=>states[2].terminal=true,20=>{states[1].app_binding.epoch+=256;states[2].app_binding.epoch+=256;},else=>unreachable,}
  const before=states[2];_=fileExecOperation(&f);check(response==-13 and preserved(before) and clean(),"AUTHORITY_DENIAL_NO_CHILD_EFFECT");
 }
 setup(512);var stale=fileFrame(512);stale.rsi=5;const before=states[2];_=fileExecOperation(&stale);check(response==-9 and preserved(before),"UNKNOWN_CHILD_HANDLE_DENIED");
}
fn precommit()void{
 for(0..14)|case|{
  setup(512);var f=fileFrame(512);var expected:i64=-22;
  switch(case){0=>f.r9=0,1=>f.r9=4097,2=>{f.rdx=std.math.maxInt(u64);expected=-14;},
   3=>{file_mapped=511;expected=-14;},4=>{args_mapped=271;expected=-14;},5=>{f.r8=std.math.maxInt(u64);expected=-14;},
   6=>raw_args[0]=0,7=>{f.r10=5;expected=-9;},8=>{f.r10=0;expected=-9;},
   9=>{states[2].frozen=false;expected=-16;},10=>{states[2].image_commit.pending=true;expected=-16;},
   11=>{states[2].image_commit.sequence=4;expected=-16;},12=>{raw_file[0]=0;expected=-8;},
   13=>{states[2].pages=records[2][0..16];states[2].backing=storage[2][0..16];expected=-12;},else=>unreachable,}
  const before=states[2];_=fileExecOperation(&f);check(response==expected and preserved(before) and clean(),"PRECOMMIT_FAILURE_PRESERVES_OLD_CHILD");
 }
 for(0..6)|case|{
  setup(512);
  switch(case){0=>put32(68,7),1=>put64(64+40,128),2=>put64(24,0x300000),
   3=>put32(64+3*56,1),4=>put64(64+16,0x400000),5=>put32(64+3*56+4,7),else=>unreachable,}
  const before=states[2];_=fileExecOperation(&fileFrame(512));check(response==-8 and preserved(before) and clean(),"ELF_REJECTION_NO_MUTATION");
 }
}
fn fallback()void{
 for(0..2)|after_bad|{
  setup(512);
  if(after_bad!=0){raw_file[0]=0;_=fileExecOperation(&fileFrame(512));check(response==-8 and clean(),"MALFORMED_SNAPSHOT_CLEARED");}
  const before=mutations;
  _=execOperation(&.{.rax=0x23007,.rdi=0xa001,.rsi=2,.rdx=0xc003,.r10=6,.r8=0x1000});
  check(response==-13 and mutations==before and !states[2].image_commit.pending,"BOOT_EXEC_FALLBACK_DENIED");
  _=appLaunchOperation(&.{.rax=0x2300a,.rdi=0xa001,.rsi=0xc003,.rdx=3,.r10=0x6000,.r8=channels[0].cap(0),.r9=channels[1].cap(1)});
  check(response==-13 and mutations==before,"BOOT_APP_FALLBACK_DENIED");
  for([_]u64{0x23000,0x23001,0x23002})|op|{
   _=launchOperation(&.{.rax=op,.rdi=0xa001,.rsi=0xc003,.rdx=3,.r10=0x1000,.r8=if(op==0x23000)0 else channels[0].cap(0),.r9=if(op==0x23002)channels[1].cap(1) else 0});
   check(response==-13 and mutations==before,"GENERIC_LAUNCH_FALLBACK_DENIED");
  }
 }
}
pub fn main()void{
 if(@hasDecl(@import("build_options"),"native_zsh_file_exec") and @import("build_options").native_zsh_file_exec){success();authority();precommit();fallback();}
 else{setup(512);_=fileExecOperation(&fileFrame(512));check(response==-38 and std.mem.allEqual(u8,&third_bytes,0xa5) and mutations==0,"OLD_PROFILE_UNAVAILABLE_CACHE_UNTOUCHED");}
 std.debug.print("ZSH FILE EXEC MODEL PASS\n",.{});
}
'''


class FileExecSelection(unittest.TestCase):
    def test_explicit_default_off_and_dispatch(self):
        build = (ROOT / 'build.zig').read_text()
        self.assertIn('b.option(bool, "native-zsh-file-exec",', build)
        self.assertIn('options.addOption(bool, "native_zsh_file_exec", native_zsh_file_exec);', build)
        self.assertIn('if (native_zsh_file_exec and !native_zsh_external)', build)
        native = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        self.assertIn('frame.rax == 0x2300b) return fileExecOperation(frame);', native)
        self.assertIn('fn fileExecOperation(', native)

    def test_actual_model_and_closed_omission_controls(self):
        native = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        source = checker_source(native)
        self.assertIn('C004_PUBLISHED', source)
        for omission in ('authority', 'epoch', 'one-shot', 'scratch-clear',
                         'exec-fallback', 'app-fallback', 'generic-fallback'):
            self.assertNotEqual(source, checker_source(native, omission))


if __name__ == '__main__':
    unittest.main()
