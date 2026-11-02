# SPDX-License-Identifier: BSD-2-Clause
"""Closed #137 build/admission custody checks. Host substitutions; no guest."""
import ast
from pathlib import Path
import unittest

import test_native_app as native_app

ROOT = native_app.ROOT
from test_native_cleanup import block

CASES = r'''
fn prepare()void{
 reset();combined_application_profile=true;
 @memcpy(states[6].backing[0][0..8],"AENAP002");
}
fn selectedCase()void{
 prepare();for(0..32)|i|_=channels[11].stream.push(@intCast(i));
 channels[11].write_started=true;const namespace=channels[10..12].*;
 const f=launchFrame();_=appLaunchOperation(&f);
 check(response==@as(i64,@intCast(handle(1))),"SELECTED_HANDLE");
 check(states[1].admitted and !states[1].ready,"ADMITTED_NOT_READY");
 check(channels[0].owners[0]==1 and channels[0].owners[1]==6 and channels[1].owners[1]==1 and channels[1].owners[0]==6,"PROCESS_ONLY_TRANSFER");
 check(std.meta.eql(namespace,channels[10..12].*),"RETAINED_NAMESPACE_UNCHANGED");
 check(states[1].app_binding.bound() and states[1].tty_signal_owner_generation==states[6].generation,"EXACT_OWNER_BINDING");
 check(states[1].app_binding.epoch==states[0].channel_cap,"EXACT_ENGINE_EPOCH");
 check(@sizeOf(App.Binding)==32,"UNCHANGED_BINDING_GEOMETRY");
 check(transfer(1,11,true,1)==-13 and transfer(1,10,false,1)==-13,"APP_HAS_NO_NAMESPACE_AUTHORITY");
 check(std.meta.eql(namespace,channels[10..12].*),"APP_NAMESPACE_DENIAL_NO_EFFECT");
 active=1;_=freezeOperation(&.{.rax=0x23003});check(response==-95 and !states[1].frozen,"SELECTED_FREEZE_DENIED");
 active=6;_=copyPrefix(&.{.rax=0x23006,.rdi=0xa001,.rsi=handle(1),.rdx=2});
 check(response==-95 and effects==0 and !states[2].admitted,"SELECTED_COPY_DENIED");
 for([_]u64{0x23007,0x23009})|op|{_=execPrefix(&.{.rax=op,.rdi=0xa001,.rsi=handle(1)});check(response==-95 and effects==0,"SELECTED_EXEC_DENIED");}
 const s=&states[1];const base:usize=0x0800c000;const strings:usize=0x0800e100;
 const expected=[_]u64{4,strings,strings+32,strings+64,strings+96,0,strings+128,strings+160,strings+192,strings+224,0,
 3,0x200040,4,56,5,1,6,4096,9,0x200000,11,1000,12,1000,13,1000,14,1000,23,0,25,0x0800e080,31,strings,
 0xa000,s.memory_cap,0xa001,s.channel_cap,0xa002,s.channel_reply_cap,0,0};
 check(expected.len==43,"MAXIMUM43_WORDS");
 for(expected,0..)|v,i|check(readStackWord(s,base+i*8)==v,"PROCESS_ONLY_AUXV");
 for(0..64)|i|check(byte(s,App.startup_address+i,false).?.*==0,"NO_NAMESPACE_STARTUP");
 for(0..16)|i|check(byte(s,0x0800e080+i,false).?.*==0x6d,"ENTROPY_PRESERVED");
 for(0..8)|i|check(byte(s,strings+i*32,false).?.*=='a'+i,"ARGUMENT_BANK_PRESERVED");
 _=states[1].signal_actions.install(2,.{.handler=.{.entry=0x200010,.restorer=0x200020,.mask=0}}) catch unreachable;
 const sig=Frame{.rax=0x29003,.rdi=handle(1),.rsi=2,.rdx=0};
 _=ttySignalOperation(&sig);check(response==1 and states[1].signal_actions.pending==0,"PREFLIGHT_NO_PENDING");
 var post=sig;post.rdx=1;_=ttySignalOperation(&post);check(response==1,"EXACT_OWNER_POST");
 const pending=states[1].signal_actions.pending;states[6].generation+=1;
 _=ttySignalOperation(&post);check(response==-13 and states[1].signal_actions.pending==pending,"STALE_OWNER_NO_EFFECT");
 states[6].generation-=1;post.rdi^=0x100;_=ttySignalOperation(&post);check(response==-3 and states[1].signal_actions.pending==pending,"STALE_APP_NO_EFFECT");
 active=6;_=stopEntry(&.{.rax=0x20007});
 check(!states[1].app_binding.bound() and states[1].tty_signal_owner_generation==null,"STOP_REVOKES_RELATIONSHIP");
 check(std.meta.eql(namespace,channels[10..12].*),"STOP_RETAINS_OWNER_NAMESPACE");
 check(transfer(6,11,true,1)==1 and channels[11].read_started,"OWNER_NAMESPACE_AVAILABLE_AFTER_STOP");
}
fn deniedCase()void{
 prepare();@memcpy(states[6].backing[0][0..8],"AENAP001");deny(launchFrame(),-22);
 for([_]usize{0,8,16,24,312})|offset|{prepare();put(offset,255);deny(launchFrame(),-22);}
 for([_]usize{288,296,304})|offset|{prepare();put(offset,0);deny(launchFrame(),-13);}
 prepare();channels[11].read_started=true;deny(launchFrame(),-13);
 prepare();channels[10].write_started=true;deny(launchFrame(),-13);
 prepare();channels[11].owners[1]=5;deny(launchFrame(),-13);
 prepare();channels[10].owners[0]=5;deny(launchFrame(),-13);
 prepare();var f=launchFrame();f.r9=channels[0].cap(1);deny(f,-13);
 prepare();states[0].terminal=true;deny(launchFrame(),-13);
 prepare();states[1].generation=15;deny(launchFrame(),-28);
 prepare();states[1].admitted=true;deny(launchFrame(),-16);
 prepare();combined_init=false;deny(launchFrame(),-38);
 prepare();combined_profile=false;deny(launchFrame(),-38);
 prepare();combined_owner_stack=false;deny(launchFrame(),-38);
 prepare();launch_profile=false;deny(launchFrame(),-38);
 prepare();connections_profile=false;deny(launchFrame(),-38);
 prepare();second_image.segments[0].memsz=640*4096;f=launchFrame();f.rsi=0xc002;deny(f,-12);
}
pub fn main()void{
 if(@import("build_options").native_zsh_terminfo){selectedCase();deniedCase();}
 else {positive();denials();stackCase();revocation();mutation();
 reset();@memcpy(states[6].backing[0][0..8],"AENAP002");deny(launchFrame(),-22);}
 std.debug.print("ZSH TERMINFO PROFILE PASS\n",.{});
}
'''


class ZshTerminfo(unittest.TestCase):
    setUpClass = classmethod(native_app.NativeApp.setUpClass.__func__)
    finalize = classmethod(native_app.NativeApp.finalize.__func__)
    capture = native_app.NativeApp.capture

    def source(self, omission=None):
        source = native_app.NativeApp.actual_source(self)
        source = source[:source.index('pub fn main(')]
        source = source.replace('app_binding:App.Binding=.{},channel_cap:u64=0',
            'app_binding:App.Binding=.{},ready:bool=false,tty_signal_owner_generation:?u64=null,signal_actions:K.Pending.State=.{},channel_cap:u64=0')
        source += block((ROOT/'kernel/arch/x86_64/native_c.zig').read_text(), 'fn ttySignalOperation(') + CASES
        if omission == 'profile':
            old = '(terminfo and combined_profile'
            self.assertEqual(source.count(old), 1)
            source = source.replace(old, '(terminfo and !combined_profile')
        if omission == 'custody':
            old = 'if (!retained_namespace) {'
            self.assertEqual(source.count(old), 1)
            source = source.replace(old, 'if (true) {')
        if omission == 'auxv':
            old = 's.app_binding.bound() and !(@hasDecl(@import("build_options"), "native_zsh_terminfo") and @import("build_options").native_zsh_terminfo)'
            self.assertEqual(source.count(old), 1)
            source = source.replace(old, 's.app_binding.bound()')
        return source

    def build(self, selected=True, mode='Debug', omission=None):
        label = mode+'-'+str(selected)+'-'+str(omission)
        source = self.out/(label+'.zig');source.write_text(self.source(omission))
        options = dict(native_zsh_terminfo=selected,native_tty_mode_probe=True,native_tty_signal_probe=True,
            native_memory=True,native_clock=True,native_clock_ticks=False,native_service_lifetime=False,
            native_signal_suspend=False,native_signal_actions=False,native_service_channel_wait=False,
            native_skip_zero=False,native_process_exec=True,native_exec_copy=False,native_copy_signals=False,
            native_freeze_skip_park=False,native_freeze_ignore_token=False,native_exec_token=False)
        options_file=self.out/'options.zig'
        options_file.write_text('\n'.join('pub const '+k+'='+str(v).lower()+';' for k,v in options.items()))
        binary=self.out/label
        with self.temporary.named_file(mode='w',prefix='.zsh-host-imports-',suffix='.zig',dir=ROOT/'kernel') as facade:
            with self.temporary.named_file(mode='w',prefix='.zsh-host-core-',suffix='.zig',dir=ROOT/'kernel') as core:
                selected_core='native_app.zig'
                if omission == 'history':
                    text=(ROOT/'kernel/native_app.zig').read_text()
                    old='if (nr.read_started or nw.write_started) return null;'
                    self.assertEqual(text.count(old),1)
                    core.write(text.replace(old,''));core.flush();selected_core=Path(core.name).name
                facade.write('pub const App=@import("'+selected_core+'");'+
                    'pub const C=@import("native_channel.zig");pub const launch=@import("native_launch.zig");'+
                    'pub const elf=@import("native_elf.zig");pub const memory=@import("native_memory.zig");'+
                    'pub const E=@import("arch/x86_64/native_execution.zig");'+
                    'pub const Frame=@import("arch/x86_64/context.zig").Frame;'+
                    'pub const FsRoles=@import("arch/x86_64/native_fs_roles.zig");'+
                    'pub const Pending=@import("arch/x86_64/native_pending.zig");'+
                    'pub const Sustained=@import("native_sustained.zig");'+
                    'pub const Clock=@import("native_clock.zig");pub const Af09=@import("native_af09_drain.zig");')
                facade.flush()
                result=self.capture(['zig','build-exe','-O'+mode,'-fstrip','--cache-dir',self.out/'cache',
                    '--global-cache-dir',self.out/'global','--dep','kernel','--dep','build_options',
                    '-Mroot='+str(source),'-Mkernel='+facade.name,'-Mbuild_options='+str(options_file),
                    '-femit-bin='+str(binary)],60)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return binary

    def test_actual_selected_and_ordinary_custody_startup_signal_and_denials(self):
        for selected in (False,True):
            for mode in ('Debug','ReleaseSafe'):
                with self.subTest(selected=selected,mode=mode):
                    result=self.capture([self.build(selected,mode)],10)
                    self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                    self.assertIn('ZSH TERMINFO PROFILE PASS',result.stderr)

    def test_compiling_semantic_custody_auxv_and_history_omissions(self):
        for omission,marker in (('profile','SELECTED_HANDLE'),('custody','RETAINED_NAMESPACE_UNCHANGED'),
                                ('auxv','PROCESS_ONLY_AUXV'),('history','DENIAL_STATUS')):
            with self.subTest(omission=omission):
                result=self.capture([self.build(omission=omission)],10)
                self.assertEqual(result.returncode,91,result.stdout+result.stderr)
                self.assertIn(marker,result.stderr)

    def test_actual_build_selection_and_closed_prerequisites(self):
        tree=ast.parse((ROOT/'scripts/fs_session.py').read_text())
        value=next(n.value for n in tree.body if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='FLAGS' for t in n.targets))
        flags=ast.literal_eval(value.func.value).split()
        flags += ['native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']
        image=self.out/'unexecuted.bin';image.write_bytes(b'\0')
        base={'smp':'false','native-c-image':str(image),**dict.fromkeys(flags,'true')}
        selected={**base,**dict.fromkeys(('native-zsh-terminfo','native-fs-application-profile',
            'native-tty-mode-probe','native-tty-signal-probe','native-signal-mask-delivery'),'true')}
        def invoke(options,bad=False,marker=None):
            result=self.capture(['zig','build','--help','--cache-dir',self.out/'cache',
                '--global-cache-dir',self.out/'global',*['-D'+k+'='+v for k,v in options.items()]],60)
            self.assertEqual(result.returncode != 0,bad,result.stdout+result.stderr)
            if marker:self.assertIn(marker,result.stdout+result.stderr)
        invoke({});invoke(base);invoke(selected)
        for name in ('native-zsh-terminfo','native-fs-application-profile','native-tty-mode-probe',
                     'native-tty-signal-probe','native-signal-mask-delivery','native-fs-owner-stack',
                     'native-fs-session-init','native-process-copy','native-process-exec'):
            with self.subTest(missing=name):invoke({**selected,name:'false'},True)
        for name in ('smp','release-artifact','native-mktemp-reader','native-service-lifetime'):
            with self.subTest(forbidden=name):invoke({**selected,name:'true'},True)
        invoke({**selected,'native-af09-drain':'file_prefix'},True)
        invoke({'native-zsh-terminfo':'true'},True)


if __name__ == '__main__':
    unittest.main()
