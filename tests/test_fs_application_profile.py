# SPDX-License-Identifier: BSD-2-Clause
"""Execute selected native bodies over owned host storage; no MMU/guest claim."""
from pathlib import Path
import tempfile
import unittest

from test_fs_owner_data import ROOT, run as run_original
from test_native_cleanup import block, af09_prelude, af09_command

def run(command, *args, **kwargs):
    return run_original(af09_command(command), *args, **kwargs)


SCAFFOLD = r'''
const std=@import("std");
const elf=@import("elf");
const memory=@import("memory");
const FsRoles=@import("roles");
const Frame=struct{rax:u64=0,rdi:u64=0,rsi:u64=0,rdx:u64=0,rcx:u64=0,r10:u64=0,r8:u64=0,r9:u64=0,rip:u64=0,rsp:u64=0};
const Execution=struct{
 frame:Frame=.{},fp:[512]u8=@splat(0),fs:u64=0,tls_base:u64=0,tls_bytes:usize=0,signal_mask:u64=0,clear_tid:usize=0,
 fn forImage(_: *const Execution, entry:usize, stack:usize) Execution{return .{.frame=.{.rip=entry,.rsp=stack}};}
};
const State=struct{
 app_binding:struct{clock:u64=0,fn bound(b:*const @This())bool{return b.clock!=0;}}=.{},
 pages:[]memory.Page=undefined,backing:[]align(4096) [4096]u8=undefined,
 root:[1]u64=.{0},pdpt:[1]u64=.{0},pd:[512]u64=@splat(0),pts:[32][512]u64=@splat(@splat(0)),pt_index:[32]usize=@splat(0),pt_count:usize=0,count:usize=0,
 execution:Execution=.{},generation:u64=7,terminal:bool=false,frozen:bool=false,freeze_sequence:u64=5,admitted:bool=false,ready:bool=false,parent_pid:u64=0,memory_cap:u64=0,channel_cap:u64=0,channel_reply_cap:u64=0,
 image_commit:struct{sequence:u64=0,image:u64=0,pending:bool=false}=.{},
 fn payloadBytes(s:*State)[]u8{return std.mem.sliceAsBytes(s.backing);}
 fn recordBytes(s:*State)[]u8{return std.mem.sliceAsBytes(s.pages);}
 fn payload(s:*State)[]align(4096) [4096]u8{return s.backing;}
};
var states:[7]State=@splat(.{});
var records:[7][640]memory.Page=@splat(@splat(.{}));
var storage:[7][640][4096]u8 align(4096)=@splat(@splat(@splat(0)));
var alias_write:[7][640]bool=@splat(@splat(true));
var active:usize=6;var response:i64=99;var mutations:usize=0;var published:usize=0;var context:Frame=.{};
const combined_profile=true;const combined_application_profile=true;const program_profile=true;
const nx:u64=1<<63;
var service_image:elf.Image=undefined;var second_image:elf.Image=undefined;var third_image:elf.Image=undefined;
var service_bytes:[1]u8=.{0};var second_bytes:[1]u8=.{0};var third_bytes:[1]u8=.{0};
const service_len=1;const second_len=1;const third_len=1;const bootstrap=[_]u8{0}**80;
var raw_args:[272]u8=@splat(0);
const Channel=struct{
 owners:[2]usize=.{6,6},stream:struct{count:usize=0,sealed:bool=false,reader_closed:bool=false}=.{},
 fn lookup(_: *const Channel,_:usize,cap:u64)?usize{return if(cap==10) 0 else if(cap==11) 1 else null;}
 fn transfer(c:*Channel,owner:usize,cap:u64,destination:usize)bool{const side=c.lookup(owner,cap) orelse return false;if(c.owners[side]!=owner)return false;c.owners[side]=destination;return true;}
};
var channels:[2]Channel=@splat(.{});
fn check(ok:bool,comptime message:[]const u8)void{if(!ok){std.debug.print("{s}\\n",.{message});std.process.exit(91);}}
fn require(ok:bool)void{check(ok,"PRODUCTION_INVARIANT");}
fn supervisorSlot()usize{return 6;}
fn workerCount()usize{return 6;}
fn lifetimeLimit()u64{return 100;}
fn processSlot(slot:usize)bool{return FsRoles.process(slot);}
fn threadedSlot(slot:usize)bool{return FsRoles.threaded(slot);}
fn backingOwner(s:*const State)usize{for(&states,0..) |*candidate,i|if(candidate==s)return i;unreachable;}
fn ownedChannel(_:usize,cap:u64)?*Channel{return if(cap==10)&channels[0] else if(cap==11)&channels[1] else null;}
fn lookup(value:u64)?usize{return if(value>0 and value<6 and states[value].admitted) @intCast(value) else null;}
fn result(_: *State,value:i64)void{response=value;}
fn select()*const Frame{return &context;}
fn handle(slot:usize)u64{return slot;}
fn byte(_: *State,address:usize,_:bool)?*u8{return if(address>=0x1000 and address-0x1000<raw_args.len)&raw_args[address-0x1000] else null;}
fn phys(p:anytype)u64{return @intFromPtr(p);}
fn backingFrame(s:*const State,i:usize)u64{return @intFromPtr(&s.backing[i]);}
fn mapKernel(_: *State)void{mutations+=1;}
fn setBackingAlias(_: *State,owner:*State,index:usize,writable:bool)void{alias_write[backingOwner(owner)][index]=writable;}
fn resetState(s:*State)void{mutations+=1;s.count=0;s.pt_count=0;s.admitted=false;s.execution=.{};@memset(s.pages,.{});}
fn addPage(s:*State,address:usize,flags:u64)void{check(s.count<s.pages.len,"COPY_CAPACITY_BEFORE_RESET");s.pages[s.count]=.{.address=address,.flags=flags};s.count+=1;}
fn publishSustained()void{published+=1;}
fn launchStack(_: *State,_:*const launch.Arguments,_:*const elf.Image)void{}
fn load(s:*State,_:[]const u8,image:*const elf.Image,_:[]const u8,_:usize)void{
 check((launch.backingPages(image) catch unreachable)<=s.pages.len,"IMAGE_CAPACITY_BEFORE_RESET");mutations+=1;s.count=launch.backingPages(image) catch unreachable;s.admitted=true;
}
fn reset()void{
 for(&states,0..) |*s,i|{s.*=.{};s.pages=&records[i];s.backing=&storage[i];@memset(s.pages,.{});@memset(s.payloadBytes(),0xa5);}
 channels=@splat(.{});alias_write=@splat(@splat(true));mutations=0;published=0;response=99;active=6;
 raw_args=@splat(0);raw_args[0]=1;
 service_image=.{.entry=0x200000,.phdr=0x200040,.phnum=0,.count=1,.segments=undefined};
 service_image.segments[0]=.{.flags=5,.address=0x200000,.offset=0,.filesz=1,.memsz=184*4096};second_image=service_image;third_image=service_image;
}
fn copySource()void{
 states[1].admitted=true;states[1].frozen=true;states[1].count=640;states[1].pt_count=4;
 states[1].execution=.{.fs=memory.base+64,.tls_base=memory.base,.tls_bytes=4096,.clear_tid=memory.base+16,.signal_mask=42};
 for(states[1].pages,0..) |*p,i|p.*=.{.address=if(i==0) 0x200000 else memory.base+(i-1)*4096,.flags=if(i==0) 5|nx else 7|nx,.anonymous=i!=0};
 storage[1][0][0]=0x11;storage[1][639][4095]=0x66;
}
fn launchCase()void{
 reset();states[1].pages=records[1][0..128];states[1].backing=storage[1][0..128];
 const f=Frame{.rax=0x23000,.rdi=0xa001,.rsi=0xc001,.rdx=1,.r10=0x1000};_=launchOperation(&f);
 check(response==-12 and mutations==0 and states[1].generation==7 and !states[1].admitted and published==0,"LAUNCH_PREFLIGHT_NO_EFFECT");
 for([_]u64{0xc001,0xc002,0xc003}) |selector|{reset();var good=f;good.rsi=selector;_=launchOperation(&good);check(response==1 and states[1].generation==8 and states[1].admitted and published==1,"LAUNCH_SELECTED_IMAGES");}
}
fn execCase()void{
 reset();states[1].pages=records[1][0..128];states[1].backing=storage[1][0..128];states[1].admitted=true;states[1].frozen=true;
 const f=Frame{.rax=0x23007,.rdi=0xa001,.rsi=1,.rdx=0xc001,.r10=5,.r8=0x1000};_=execOperation(&f);
 check(response==-12 and mutations==0 and states[1].frozen and !states[1].image_commit.pending and states[1].generation==7,"EXEC_PREFLIGHT_NO_EFFECT");
 reset();states[1].admitted=true;states[1].frozen=true;states[1].ready=true;_=execOperation(&f);
 check(response==0 and states[1].image_commit.pending and states[1].frozen and !states[1].ready and states[1].generation==7 and states[1].execution.frame.rip==service_image.entry,"EXEC_PENDING_PUBLICATION");
 check(std.mem.allEqual(u8,states[1].payloadBytes(),0),"EXEC_OLD_PAYLOAD_ZERO");
}
fn copyCase()void{
 reset();copySource();states[2].pages=records[2][0..639];states[2].backing=storage[2][0..639];
 const f=Frame{.rax=0x23006,.rdi=0xa001,.rsi=1,.rdx=2,.r10=5,.r8=10,.r9=11};_=copyOperation(&f);
 check(response==-12 and mutations==0 and states[1].frozen and !states[2].admitted and states[2].generation==7 and channels[0].owners[0]==6,"COPY_PREFLIGHT_NO_EFFECT");
 reset();copySource();states[1].pt_count=33;_=copyOperation(&f);check(response==-12 and mutations==0,"COPY_TABLE_PREFLIGHT_NO_EFFECT");
 reset();copySource();_=copyOperation(&f);
 if(@import("build_options").native_copy_fail_stage){
  check(response==-12 and !states[2].admitted and states[2].generation==7 and states[1].frozen and channels[0].owners[0]==6,"COPY_ROLLBACK_UNPUBLISHED");
  check(std.mem.allEqual(u8,states[2].payloadBytes(),0),"COPY_ROLLBACK_ALL_640_ZERO");
 }else{
  check(response==2 and states[2].admitted and states[2].count==640 and !states[1].frozen,"COPY_PUBLICATION");
  check(storage[2][0][0]==0x11 and storage[2][639][4095]==0x66 and states[2].pages[639].anonymous,"COPY_ALL_640_PRIVATE");
  check(!alias_write[2][0] and alias_write[2][639],"COPY_IMMUTABLE_ALIAS");
  storage[2][639][4095]=0x55;check(storage[1][639][4095]==0x66,"COPY_INDEPENDENT_WRITES");
  check(states[2].execution.fs==memory.base+64 and states[2].execution.tls_base==memory.base and states[2].execution.clear_tid==0 and states[2].execution.signal_mask==42,"COPY_TLS_PIN_STATE");
  check(states[2].memory_cap!=states[1].memory_cap and states[2].execution.frame.rdi==states[2].memory_cap and channels[0].owners[0]==2 and channels[1].owners[1]==2,"COPY_REBIND_PUBLICATION");
 }
 reset();copySource();var denied=f;denied.rdx=0;_=copyOperation(&denied);check(response==-95 and mutations==0,"COPY_ENGINE_DENIED");
 denied.rdx=6;_=copyOperation(&denied);check(response==-22 and mutations==0,"COPY_OWNER_DENIED");
 denied=f;denied.r10=99;_=copyOperation(&denied);check(response==-9 and mutations==0,"COPY_STALE_TOKEN_DENIED");
}
pub fn main()void{launchCase();execCase();copyCase();std.debug.print("APPLICATION ACTUAL PATHS PASS\\n",.{});}
'''


BINDING_SCAFFOLD = r'''
const std=@import("std");const memory=@import("memory");const Page=memory.Page;const FsRoles=@import("roles");
const service_memory=true;const service_workers=false;const external_backing=true;const combined_profile=true;const combined_application_profile=true;
const Reset=struct{value:usize=9,fn reset(s:*@This())void{s.value=0;}};
const State=struct{
 app_binding:struct{clock:u64=0}=.{},
 pages:[]Page=undefined,backing:[]align(4096) [4096]u8=undefined,root:[1]u64=.{7},generation:u64=5,count:usize=0,admitted:bool=true,terminal:bool=true,execution:Reset=.{},children:[0]Reset=.{},
 fn records(s:*State)[]Page{return s.pages;}
 fn payload(s:*State)[]align(4096) [4096]u8{return s.backing;}
 fn childRecords(s:*State)[]Reset{return &s.children;}
};
var states:[7]State=@splat(.{});
var payload_storage:[11520][4096]u8 align(4096)=@splat(@splat(0));
const Partition=struct{first:usize,count:usize,fn alias(p:@This())usize{return @intFromPtr(&payload_storage[p.first]);}};
var backing_partitions:[7]Partition=undefined;var backing_boot_views=false;var response:i64=99;var reclaimed:usize=0;var detached:usize=0;var published:usize=0;
const Frame=struct{};var frame:Frame=.{};
fn check(ok:bool,comptime message:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{message});std.process.exit(91);}}
fn require(ok:bool)void{check(ok,"PRODUCTION_INVARIANT");}
fn backingOwner(s:*const State)usize{for(&states,0..) |*candidate,i|if(candidate==s)return i;unreachable;}
fn bindChildren(_: *State)void{unreachable;}
fn aliases(s:*State,writable:bool)void{check(writable and s.root[0]==0 and s.terminal and s.admitted,"RECLAIM_DETACH_BEFORE_CLEAR");detached+=1;}
fn nativeCleanupTrace(_:usize,_:usize)void{}
fn publishSustained()void{published+=1;}
fn result(_: *State,value:i64)void{response=value;}
fn select()*const Frame{return &frame;}
'''
BINDING_CASES = r'''
pub fn main()void{
 @memset(std.mem.sliceAsBytes(&payload_storage),0xa5);
 for(&states,0..) |*s,i|{
  const expected=FsRoles.applicationPages(i) catch unreachable;
  backing_partitions[i]=.{.first=FsRoles.applicationFirstPage(i) catch unreachable,.count=expected};
  bindRecords(s);bindPayload(s,backing_partitions[i].alias());
  check(s.pages.len==expected and s.backing.len==expected,"ROLE_INITIAL_BINDING");
  s.pages[0].address=0x55;s.pages[expected-1].address=0x66;
  resetState(s);
  check(s.pages.len==expected and s.backing.len==expected and s.generation==0,"ROLE_RESET_BINDING");
  check(s.pages[0].address==0 and s.pages[expected-1].address==0,"ROLE_RESET_ALL_RECORDS");
  check(s.backing[expected-1][4095]==0xa5,"ROLE_RESET_RETAINS_OWNED_PAYLOAD");
 }
 const s=&states[1];s.admitted=true;s.terminal=false;s.root[0]=7;s.count=640;
 _=reclaim();check(response==-16 and detached==0 and reclaimed==0 and s.backing[639][4095]==0xa5,"LIVE_RECLAIM_DENIED");
 s.terminal=true;_=reclaim();
 check(response==0 and reclaimed==1 and published==1 and detached==1 and !s.admitted and s.count==0,"RECLAIM_PUBLICATION");
 check(std.mem.allEqual(u8,std.mem.sliceAsBytes(s.payload()),0),"RECLAIM_ALL_640_PAGES_ZERO");
 check(states[0].backing[8191][4095]==0xa5 and states[2].backing[0][0]==0xa5 and states[6].backing[127][4095]==0xa5,"RECLAIM_OTHER_ROLES_UNCHANGED");
 std.debug.print("APPLICATION BIND RESET RECLAIM PASS\n",.{});
}
'''


class ApplicationProfile(unittest.TestCase):
    def exercise(self, mode, omission=None, rollback=False):
        native = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        launch = (ROOT / 'kernel/native_launch.zig').read_text()
        api = ('const launch=struct{pub const record_size=272;'
               'pub const Arguments=struct{argc:usize,envc:usize,strings:[8][32]u8};'
               'pub const Error=error{InvalidLaunch};')
        api += '\n'.join(block(launch, 'pub fn ' + name + '(').replace('result', 'parsed') if name == 'arguments' else block(launch, 'pub fn ' + name + '(')
                         for name in ('arguments', 'backingPages', 'layout')) + '};\n'
        bodies = '\n'.join(block(native, 'fn ' + name + '(')
                           for name in ('imagePreflight', 'copyPreflight')
                           if 'fn ' + name + '(' in native)
        for name in ('launchOperation', 'execOperation', 'copyOperation'):
            body = block(native, 'fn ' + name + '(')
            if omission == name:
                anchor = '    if (!' + ('copyPreflight' if name == 'copyOperation' else 'imagePreflight')
                check = block(body, anchor)
                body = body.replace(check, '')
            bodies += '\n' + body
        aliases = block(native, 'fn aliases(')
        # Execute actual alias decisions; privileged CR3 reload is outside host coverage.
        aliases = aliases[:aliases.index('    asm volatile')] + '}\n'
        if omission == 'aliases':
            aliases = aliases.replace('writable or page.flags & 2 != 0', 'true')
            aliases = aliases.replace('fn aliases(owner: *State, writable: bool)', 'fn aliases(owner: *State, _: bool)')
        with tempfile.TemporaryDirectory(prefix='aether-application-host-') as folder:
            out = Path(folder)
            (out / 'main.zig').write_text(SCAFFOLD + af09_prelude(native) + api + bodies + aliases)
            values = dict(native_process_exec=True,native_exec_copy=False,native_signal_actions=False,
                          native_copy_signals=False,native_copy_lose_anonymous=False,native_copy_share=False,
                          native_copy_fail_stage=rollback,native_copy_skip_zero=mode == 'skip-zero',
                          native_exec_token=False,native_exec_early=False)
            (out / 'options.zig').write_text('\n'.join('pub const ' + n + '=' + str(v).lower() + ';' for n,v in values.items()))
            binary = out / 'actual'
            run(['zig','build-exe','-OReleaseSafe','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                 '--dep','build_options','--dep','elf','--dep','memory','--dep','roles','-Mroot='+str(out/'main.zig'),
                 '-Mbuild_options='+str(out/'options.zig'),'-Melf='+str(ROOT/'kernel/native_elf.zig'),
                 '-Mmemory='+str(ROOT/'kernel/native_memory.zig'),'-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),
                 '-femit-bin='+str(binary)],out)
            text=run([binary],out,-6 if mode=='skip-zero' else 91 if omission else 0)
            if omission == 'aliases':self.assertIn('COPY_IMMUTABLE_ALIAS',text)
            elif omission == 'copyOperation':self.assertIn('COPY_CAPACITY_BEFORE_RESET',text)
            elif omission:self.assertIn('IMAGE_CAPACITY_BEFORE_RESET',text)
            elif mode == 'skip-zero':self.assertIn('panic: native copy rollback not zeroed',text)
            else:self.assertIn('APPLICATION ACTUAL PATHS PASS',text)

    def test_actual_launch_exec_copy_preflight_and_private_copy(self):
        self.exercise('actual')

    def test_named_compiling_preflight_and_alias_omissions(self):
        for name in ('launchOperation','execOperation','copyOperation','aliases'):
            with self.subTest(omission=name):self.exercise(name, name)

    def test_actual_unpublished_copy_rollback_and_zero_omission(self):
        self.exercise('rollback',rollback=True)
        self.exercise('skip-zero',rollback=True)

    def test_actual_selected_record_binding_reset_and_full_partition_reclaim(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        declarations='\n'.join(line for line in native.splitlines() if line.startswith(('var service_records:', 'var small_records:', 'var application_records:')))
        binding='\n'.join(block(native,'fn '+name+'(') for name in ('bindRecords','bindPayload','resetState'))
        reclaim=block(native,'        0x20002 => {')
        wrapper='fn reclaim()*const Frame{const slot:usize=1;const s=&states[slot];const caller=&states[6];switch(@as(u64,0x20002)){'+reclaim+',else=>unreachable,}return select();}\n'
        for mode in ('actual','omit-reset-binding','omit-last-page-clear'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory(prefix='aether-application-binding-') as folder:
                out=Path(folder);text=binding;operation=wrapper
                if mode=='omit-reset-binding':
                    reset=block(text,'fn resetState(')
                    text=text.replace(reset,reset.replace('bindRecords(state);',''))
                if mode=='omit-last-page-clear':
                    operation=operation.replace('for (s.payload()) |*page| {','for (s.payload()[0..s.payload().len-1]) |*page| {')
                (out/'main.zig').write_text(BINDING_SCAFFOLD+af09_prelude(native)+declarations+text+operation+BINDING_CASES)
                (out/'options.zig').write_text('pub const native_service_workers_skip_rebind=false;pub const native_skip_zero=false;pub const native_signal_actions=false;')
                binary=out/'actual'
                run(['zig','build-exe','-OReleaseSafe','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                     '--dep','build_options','--dep','memory','--dep','roles','-Mroot='+str(out/'main.zig'),
                     '-Mbuild_options='+str(out/'options.zig'),'-Mmemory='+str(ROOT/'kernel/native_memory.zig'),
                     '-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),'-femit-bin='+str(binary)],out)
                output=run([binary],out,0 if mode=='actual' else 91)
                self.assertIn('APPLICATION BIND RESET RECLAIM PASS' if mode=='actual' else 'ROLE_RESET_BINDING' if mode=='omit-reset-binding' else 'PRODUCTION_INVARIANT',output)

    def test_explicit_private_build_selection_and_unchanged_old_profile(self):
        import ast
        tree=ast.parse((ROOT/'scripts/fs_session.py').read_text())
        values=[n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FLAGS' for t in n.targets)]
        self.assertEqual(len(values),1)
        base=ast.literal_eval(values[0].func.value).split()
        base += ['native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']
        with tempfile.TemporaryDirectory(prefix='aether-application-build-') as folder:
            out=Path(folder);image=out/'unexecuted-envelope.bin';image.write_bytes(bytes(1))
            command=['zig','build','--help','--cache-dir',out/'cache','--global-cache-dir',out/'global']
            selected=['-Dsmp=false','-Dnative-c-image='+str(image),*['-D'+name+'=true' for name in base]]
            log=run([*command,'-Dnative-fs-application-profile=true'],out,1)
            self.assertIn('filesystem application profile requires its private ABI31 owner-stack profile',log)
            self.assertNotRegex(log,r':\d+:\d+: error:')
            log=run([*command,*selected,'-Dnative-fs-application-profile=true','-Drelease-artifact=true'],out,1)
            self.assertIn('filesystem application profile requires its private ABI31 owner-stack profile',log)
            for application in (False,True):
                log=run([*command,*selected,'-Dnative-fs-application-profile='+str(application).lower()],out)
                self.assertIn('native-fs-application-profile',log)
            no_exec=[flag for flag in selected if flag!='-Dnative-process-exec=true']
            log=run([*command,*no_exec,'-Dnative-fs-application-profile=true'],out,1)
            self.assertIn('SESSION lifecycle requires capacity, copy, exec',log)
            self.assertNotRegex(log,r':\d+:\d+: error:')

    def test_actual_start_rejects_selected_input_before_reservation_and_devices(self):
        import re
        from test_fs_session import envelope,small_elf
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        start=block(native,'pub fn start(')
        start=start[:start.index('    @import("protection.zig").tables();')]
        start=start.replace('pub fn start(', 'fn start(').replace('@import("../../limine.zig").MemoryResponse','Map').replace(') noreturn {',') void {',1)
        start=start.replace('asm volatile ("cli" ::: .{ .memory = true });','effects+=1;')
        for name,value in [('controls','0'),('protection','1<<16'),('efer','1<<11')]:
            start,count=re.subn('const '+name+r' = asm volatile \(.*?\);','const '+name+':u64='+value+';',start,flags=re.S)
            self.assertEqual(count,1)
        start=start.replace('@import("entropy.zig")','Entropy').replace('@import("block.zig")','Block').replace('@import("clock.zig")','Clock')
        start=start.replace('@panic("invalid filesystem application envelope")','rejected()')
        start+='    _=bytes;\n}\n'
        scaffold=r'''
const std=@import("std");const FsSession=@import("composition");const Map=struct{};
const combined_profile=true;const combined_application_profile=true;const combined_owner_stack=true;const combined_owner_data=true;const combined_init=true;
const service_memory=true;const external_backing=true;const pipeline_capacity=true;
var effects:usize=0;var physical:u64=0;var virtual:u64=0;var block_base:u64=0;var block_count:u64=0;
var session_lifecycle=false;var sustained=false;var block_regions=false;var block_profile=false;var pipeline_session=false;var pipeline_console=false;var connections_console=false;var console_relay=false;var console_handoff=false;var console_profile=false;var io_profile=false;var connections_large=false;var connections_profile=false;var program_profile=false;var coexist_profile=false;var init_composed=false;var init_large=false;var init_profile=false;var file_profile=false;var channel_profile=false;var launch_profile=false;var supervised=false;
var channels:[1]struct{sustained:bool=false}=@splat(.{});var service_bytes:[1536*1024]u8=undefined;
fn check(ok:bool,comptime message:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{message});std.process.exit(91);}}
fn require(ok:bool)void{check(ok,"START_INVARIANT");}
fn rejected()noreturn{check(effects==0 and physical==0 and virtual==0,"START_REJECT_HAS_EFFECTS");std.debug.print("EARLY_APPLICATION_REJECT zero-effects\n",.{});std.process.exit(92);}
fn storageMagic()[]const u8{return "AENSUP01";}
fn prepareBacking(_:u64,_:*const Map)void{effects+=1;}
const Entropy=struct{fn initialize(_:u64,_:u64)void{effects+=1;}};
const Block=struct{fn initialize(_:u64,_:u64)void{effects+=1;}fn sectorCount()u64{return 2097160;}};
const Clock=struct{fn initialize(_:u64,_:u64,_:u64,_:*const Map)!void{effects+=1;}};
pub fn main()void{start(0x100000,0xffffffff80000000,@embedFile("envelope.bin"),0,&.{});check(@import("build_options").valid and effects==5,"START_PREFLIGHT_REQUIRED");std.debug.print("START VALID SETUP PASS\n",.{});}
'''
        raw=bytearray(envelope(small_elf()));raw[:8]=b'AENFS006';raw[48+4096:48+4096+8]=b'AENMX011'
        wrong=bytearray(raw);wrong[48+4096:48+4096+8]=b'AENMX010'
        cases=[('valid',raw,True,False,0),('wrong-nested',wrong,False,False,92),('truncated',raw[:-1],False,False,92),('omitted-preflight',wrong,False,True,91)]
        for name,data,valid,omit,expected in cases:
            with self.subTest(case=name),tempfile.TemporaryDirectory(prefix='aether-application-start-') as folder:
                out=Path(folder);body=start
                if omit:body=body.replace(block(body,'    if (combined_application_profile)'),'')
                (out/'main.zig').write_text(scaffold+body);(out/'envelope.bin').write_bytes(data)
                values=dict(native_service_block=True,native_service_channel=True,native_coexist_small_pool=False,native_exec_denial=False,native_thread_pair=True,native_threads=True,native_memory=True,native_session_lifecycle=True,native_init_sustained=False,native_process_copy=True,native_process_exec=True,native_image_large=True,native_entropy=True,native_clock=True,valid=valid)
                (out/'options.zig').write_text('\n'.join('pub const '+k+'='+str(v).lower()+';' for k,v in values.items()))
                binary=out/'actual'
                run(['zig','build-exe','-OReleaseSafe','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                     '--dep','build_options','--dep','composition','-Mroot='+str(out/'main.zig'),
                     '-Mbuild_options='+str(out/'options.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig'),
                     '-femit-bin='+str(binary)],out)
                log=run([binary],out,expected)
                self.assertIn('START VALID SETUP PASS' if valid else 'START_PREFLIGHT_REQUIRED' if omit else 'EARLY_APPLICATION_REJECT zero-effects',log)
