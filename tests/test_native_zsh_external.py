# SPDX-License-Identifier: BSD-2-Clause
"""Closed parent/helper source checks and actual-body host fixture; no guest.

Run python3 -B -m unittest discover -s tests -p test_native_zsh_external.py -v.
Public checks use only stdlib and launch no process. Private qualified capture
compiles checker_source with the actual kernel modules; no public dependency on
uncommitted bounded_capture APIs is introduced.
"""
import ast
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]


def block(source,anchor):
    start=source.index(anchor);opening=source.index('{',start);depth=1;end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]


def literal(path,name):
    tree=ast.parse(path.read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))


FACADE='''pub const App=@import("native_app.zig");pub const elf=@import("native_elf.zig");
pub const memory=@import("native_memory.zig");pub const roles=@import("arch/x86_64/native_fs_roles.zig");
pub const launch=@import("native_launch.zig");pub const Pending=@import("arch/x86_64/native_pending.zig");'''


def checker_source(native,omission=None):
    scaffold=literal(ROOT/'tests/test_fs_application_profile.py','SCAFFOLD').split('fn launchCase()',1)[0]
    scaffold=scaffold.replace('const elf=@import("elf");','const K=@import("kernel");const elf=K.elf;const launch=K.launch;')
    scaffold=scaffold.replace('const memory=@import("memory");','const memory=K.memory;').replace('const FsRoles=@import("roles");','const FsRoles=K.roles;')
    scaffold=scaffold.replace('app_binding:struct{clock:u64=0,fn bound(b:*const @This())bool{return b.clock!=0;}}=.{},',
        'app_binding:K.App.Binding=.{},tty_signal_owner_generation:?u64=null,signal_actions:K.Pending.State=.{},')
    scaffold=scaffold.replace('fn payloadBytes(s:*State)', 'fn context(s:*State)*Execution{return &s.execution;}\n fn payloadBytes(s:*State)')
    scaffold=scaffold.replace('fn result(_: *State,value:i64)void{response=value;}', 'fn result(s:*State,value:i64)void{response=value;s.execution.frame.rax=@bitCast(value);}')
    scaffold=scaffold.replace('s.admitted=false;s.execution=.{};', 's.admitted=false;s.ready=false;s.freeze_sequence=0;s.image_commit=.{};s.app_binding=.{};s.tty_signal_owner_generation=null;s.signal_actions=.{};s.execution=.{};')
    bodies='\n'.join(block(native,'fn '+name+'(') for name in ('imagePreflight','copyPreflight','freezeOperation','copyOperation','execOperation','notifyParent'))
    aliases=block(native,'fn aliases(');bodies+='\n'+aliases[:aliases.index('    asm volatile')]+'}\n'
    if omission=='clock':
        old='child.app_binding = child_binding;';assert bodies.count(old)==1;bodies=bodies.replace(old,'child.app_binding = source.app_binding;')
    elif omission=='tty':
        old='child.tty_signal_owner_generation = null;';assert bodies.count(old)==1;bodies=bodies.replace(old,'child.tty_signal_owner_generation = source.tty_signal_owner_generation;')
    elif omission=='exec-image':
        old='if (f.rax == 0x23007 and f.rdx != 0xc003)';assert bodies.count(old)==1;bodies=bodies.replace(old,'if (false)')
    elif omission is not None:raise ValueError('closed omission')
    extra='''
const af09_enabled=false;const af09=struct{const engine_bound=false;};
fn af09Bind(_:usize,_:usize)void{unreachable;}fn af09Fail(_:usize,_:i64)void{unreachable;}
const session_lifecycle=true;fn rotate()void{}
'''
    return scaffold+extra+bodies+CASES


OPTIONS=dict(native_process_exec=True,native_exec_copy=False,native_signal_actions=True,
 native_copy_signals=True,native_copy_signals_drop=False,native_copy_signals_pending=False,native_copy_signals_parent=False,
 native_copy_lose_anonymous=False,native_copy_share=False,native_copy_fail_stage=False,native_copy_skip_zero=False,
 native_freeze_skip_park=False,native_freeze_ignore_token=False,native_exec_token=False,native_exec_early=False,
 native_signal_suspend=True,native_tty_signal_probe=True)

CASES=r'''
fn setup()void{
 reset();copySource();states[6].admitted=true;states[6].generation=0;
 states[1].app_binding=K.App.Binding.init(1,7,33,44,55).?;states[1].tty_signal_owner_generation=0;
 states[1].signal_actions.records[16]=.{.entry=0x200010,.restorer=0x200020};
 states[1].signal_actions.pending=2;
}
fn copyFrame()Frame{return .{.rax=0x23006,.rdi=0xa001,.rsi=1,.rdx=2,.r10=5,.r8=10,.r9=11};}
fn execFrame()Frame{return .{.rax=0x23007,.rdi=0xa001,.rsi=2,.rdx=0xc003,.r10=6,.r8=0x1000};}
fn copied()void{
 setup();_=copyOperation(&copyFrame());check(response==2 and states[2].admitted,"SELECTED_CHILD_ADMITTED");
 const child=&states[2];const binding=child.app_binding;
 check(child.generation==8 and binding.valid(2,8,true,false,binding.clock),"CHILD_CLOCK_GENERATION");
 check(binding.clock!=states[1].app_binding.clock and !binding.valid(1,7,true,false,binding.clock),"CHILD_CLOCK_NOT_PARENT");
 check(binding.reader==33 and binding.writer==44 and binding.epoch==55,"CHILD_INTERNAL_PROVENANCE");
 check(child.tty_signal_owner_generation==null,"CHILD_NO_TTY_OWNER_INCLUDING_ZERO");
 check(channels[0].owners[0]==2 and channels[1].owners[1]==2 and child.channel_cap==10 and child.channel_reply_cap==11,"CHILD_PROCESS_ENDPOINTS_ONLY");
 check(child.parent_pid==51 and states[1].execution.frame.rax==59 and child.execution.frame.rax==0,"ACTUAL_PARENT_CHILD_IDENTITIES");
 check(child.signal_actions.pending==0 and states[1].signal_actions.pending==2 and child.signal_actions.records[16].entry==0x200010,"CHILD_PENDING_EMPTY_DISPOSITION_INHERITED");
 check(!binding.valid(2,7,true,false,binding.clock) and !binding.valid(2,8,false,false,binding.clock) and !binding.valid(2,8,true,true,binding.clock),"CHILD_CLOCK_STALE_DENIALS");
}
fn copyDenied()void{
 for(0..10)|case|{
  setup();var f=copyFrame();
  switch(case){0=>f.rdi=0,1=>active=1,2=>f.rdx=3,3=>f.r10=4,4=>states[2].admitted=true,
   5=>states[1].tty_signal_owner_generation=null,6=>states[1].generation=8,7=>states[6].generation=1,
   8=>states[1].terminal=true,9=>states[1].app_binding.clock=0,else=>unreachable,}
  const child=states[2];_=copyOperation(&f);
  check(response<0 and std.meta.eql(child,states[2]) and mutations==0 and channels[0].owners[0]==6,"COPY_DENIAL_NO_EFFECT");
 }
 setup();states[2].generation=15;_=copyOperation(&copyFrame());check(response==-28 and !states[2].admitted,"CHILD_LIFETIME_CAP");
}
fn freezeCases()void{
 setup();states[1].frozen=false;active=1;_=freezeOperation(&.{.rax=0x23003});check(response==-11 and states[1].frozen,"PARENT_COOPERATIVE_FREEZE");
 copied();active=2;_=freezeOperation(&.{.rax=0x23003});check(response==-11 and states[2].frozen and states[2].freeze_sequence==1,"CHILD_COOPERATIVE_EXEC_FREEZE");
 states[2].frozen=false;states[2].tty_signal_owner_generation=0;_=freezeOperation(&.{.rax=0x23003});check(response==-95 and !states[2].frozen,"CHILD_SOME_ZERO_NOT_NULL");
}
fn execCases()void{
 copied();const before=states[2].app_binding;const before_mutations=mutations;states[2].frozen=true;states[2].freeze_sequence=6;
 for([_]u64{0xc001,0xc002})|image|{var f=execFrame();f.rdx=image;_=execOperation(&f);check(response==-13 and mutations==before_mutations and !states[2].image_commit.pending,"CHILD_EXEC_C003_ONLY");}
 var f=execFrame();f.rsi=1;_=execOperation(&f);check(response==-95,"PARENT_EXEC_DENIED");
 f=execFrame();f.r10=5;_=execOperation(&f);check(response==-9 and std.meta.eql(before,states[2].app_binding),"EXEC_STALE_TOKEN_NO_CHANGE");
 f=execFrame();_=execOperation(&f);check(response==0 and states[2].image_commit.pending and states[2].frozen and !states[2].ready,"CHILD_EXEC_PENDING");
 check(states[2].generation==8 and std.meta.eql(before,states[2].app_binding) and states[2].tty_signal_owner_generation==null,"EXEC_PRESERVES_CHILD_LIFETIME");
 _=execOperation(&.{.rax=0x23008,.rdi=0xa001,.rsi=2});check(response==6 and states[6].execution.frame.rdx==0xc003 and states[6].execution.frame.r8==1,"EXACT_EXEC_RECEIPT");
 _=execOperation(&.{.rax=0x23009,.rdi=0xa001,.rsi=2,.rdx=5});check(response==-9 and states[2].image_commit.pending,"STALE_PUBLISH_DENIED");
 _=execOperation(&.{.rax=0x23009,.rdi=0xa001,.rsi=2,.rdx=6});check(response==0 and !states[2].frozen and !states[2].image_commit.pending,"CHECKED_EXEC_PUBLICATION");
}
fn execDenied()void{
 for(0..8)|case|{
  copied();states[2].frozen=true;states[2].freeze_sequence=6;
  switch(case){0=>states[1].generation+=1,1=>states[6].generation=1,2=>states[2].generation+=1,
   3=>states[2].tty_signal_owner_generation=0,4=>states[2].app_binding.epoch+=1,
   5=>states[1].terminal=true,6=>states[2].parent_pid=0,7=>states[2].terminal=true,else=>unreachable,}
  const binding=states[2].app_binding;const before=mutations;_=execOperation(&execFrame());
  check(response<0 and mutations==before and std.meta.eql(binding,states[2].app_binding) and !states[2].image_commit.pending,"EXEC_STALE_RELATIONSHIP_NO_EFFECT");
 }
 copied();states[2].frozen=true;states[2].freeze_sequence=6;third_image.segments[0].memsz=640*4096;
 const before=mutations;_=execOperation(&execFrame());check(response==-12 and mutations==before and states[2].frozen and !states[2].image_commit.pending,"FAILED_EXEC_OLD_IMAGE_RETAINED");
 setup();states[2].generation=14;_=copyOperation(&copyFrame());check(response==2 and states[2].generation==15 and states[2].app_binding.valid(2,15,true,false,states[2].app_binding.clock),"REUSED_CHILD_ACTUAL_NEXT_GENERATION");
}
fn rollbackCase()void{
 setup();_=copyOperation(&copyFrame());
 check(response==-12 and !states[2].admitted and states[2].generation==7 and states[1].frozen and !states[2].app_binding.bound() and states[2].tty_signal_owner_generation==null,"FAILED_COPY_UNPUBLISHED_NO_BINDING");
 check(channels[0].owners[0]==6 and channels[1].owners[1]==6 and std.mem.allEqual(u8,states[2].payloadBytes(),0),"FAILED_COPY_ZERO_NO_ENDPOINT_TRANSFER");
}
fn notifyCases()void{
 copied();active=2;notifyParent(&states[2]);check(states[1].signal_actions.pending==65538,"EXACT_SIGCHLD17");
 states[1].signal_actions.pending=0;states[1].generation+=1;notifyParent(&states[2]);check(states[1].signal_actions.pending==0,"STALE_PARENT_NO_SIGCHLD");
}
pub fn main()void{
 const selected=@hasDecl(@import("build_options"),"native_zsh_external") and @import("build_options").native_zsh_external;
 if(@import("build_options").native_copy_fail_stage){rollbackCase();}
 else if(selected){copied();copyDenied();freezeCases();execCases();execDenied();notifyCases();}
 else{setup();_=copyOperation(&copyFrame());check(response==-95 and !states[2].admitted,"OLD_BOUND_COPY_DENIAL");active=1;states[1].frozen=false;_=freezeOperation(&.{.rax=0x23003});check(response==-95 and !states[1].frozen,"OLD_BOUND_FREEZE_DENIAL");}
 std.debug.print("ZSH EXTERNAL MODEL PASS\n",.{});
}
'''


class ZshExternalSource(unittest.TestCase):
    def test_actual_model_and_closed_binding_sites(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        self.assertIn('child.app_binding = child_binding;',native)
        self.assertIn('child.tty_signal_owner_generation = null;',native)
        self.assertIn('if (f.rax == 0x23007 and f.rdx != 0xc003)',native)
        self.assertIn('s.app_binding.bound() and !(@hasDecl(@import("build_options"), "native_zsh_terminfo")',native)
        self.assertIn('ZSH EXTERNAL MODEL PASS',checker_source(native))
        for omission in ('clock','tty','exec-image'):
            self.assertNotEqual(checker_source(native),checker_source(native,omission))

    def test_build_selection_remains_explicit_default_off(self):
        source=(ROOT/'build.zig').read_text()
        self.assertIn('b.option(bool, "native-zsh-external",',source)
        self.assertIn('const native_zsh_external = ',source)
        self.assertIn('options.addOption(bool, "native_zsh_external", native_zsh_external);',source)
        guard=next(line for line in source.splitlines() if 'if (native_zsh_external and' in line)
        for dependency in ('native_zsh_terminfo','native_process_copy','native_process_exec','native_copy_signals','native_signal_actions','native_signal_public','native_signal_suspend','native_parent_identity'):
            self.assertIn('!'+dependency,guard)


if __name__=='__main__':unittest.main()
