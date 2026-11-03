# SPDX-License-Identifier: BSD-2-Clause
"""Closed #143 capacity fixtures; no compiler/VM is launched by this module.

Run pure controls: python3 -B -m unittest discover -s tests -p test_zsh_owner_capacity.py -v
The lead's bounded private capture compiles parser_source, boot_source and
mapping_source against actual current Zig bodies; exact invocations/results are
recorded separately. This file needs no uncommitted capture API.
"""
import importlib.util
from pathlib import Path
import re
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]


def block(source, needle):
    start = source.index(needle)
    end = source.index('{', start)
    depth = 1
    end += 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def small_elf():
    raw = bytearray(4096)
    raw[:8] = b'\x7fELF\x02\x01\x01\0'
    struct.pack_into('<HHIQQQIHHHHHH', raw, 16, 2, 62, 1, 0x200200, 64, 0, 0, 64, 56, 4, 0, 0, 0)
    rows = ((6, 4, 64, 0x200040, 0x200040, 224, 224, 8),
            (1, 5, 0, 0x200000, 0x200000, 4096, 4096, 4096),
            (7, 4, 768, 0x200300, 0x200300, 4, 4, 4),
            (0x6474e551, 6, 0, 0, 0, 0, 0, 16))
    for i, row in enumerate(rows):
        struct.pack_into('<IIQQQQQQ', raw, 64 + 56*i, *row)
    return bytes(raw)


def envelope(owner_bytes):
    image = small_elf()
    nested = (struct.pack('<8sIIIIQ', b'AENMX011', 4096, 4096, 4096, owner_bytes, 0)
              + bytes(range(80)) + image*3 + bytes(owner_bytes))
    return struct.pack('<8sII', b'AENFS006', 4096, len(nested)) + bytes(range(32)) + image + nested


def parser_source():
    return r'''const std=@import("std");const Fs=@import("session");
fn check(ok:bool,comptime label:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{label});std.process.exit(91);}}
pub fn main()void{
    const sizes=[_]usize{49152,49153,67704,73728,73729};
    const raws=[_] []const u8{@embedFile("49152.bin"),@embedFile("49153.bin"),@embedFile("67704.bin"),@embedFile("73728.bin"),@embedFile("73729.bin")};
    for(raws,sizes)|raw,size|{
        const selected=if(@hasDecl(Fs,"parseExternalApplication")) Fs.parseExternalApplication(raw) else Fs.parseApplication(raw);
        if(selected)|good|{check(size<=73728 and good.session.supervisor.len==size,"EXTERNAL_OWNER_BOUND");}
        else |_|{check(size>73728,"EXTERNAL_OWNER_BOUND");}
        if(Fs.parseApplication(raw))|good|{check(size<=49152 and good.session.supervisor.len==size,"OLD_APPLICATION_OWNER_BOUND");}
        else |_|{check(size>49152,"OLD_APPLICATION_OWNER_BOUND");}
        if(Fs.parseOwnerStack(raw))|_|{check(false,"MAGIC_NOT_PROFILE_AUTHORITY");}else |_|{}
    }
    // This is the real old wire and old entry, not just a foreign-magic denial.
    const old_sizes=[_]usize{49152,49153,67704};
    const old_raws=[_] []const u8{@embedFile("old-49152.bin"),@embedFile("old-49153.bin"),@embedFile("old-67704.bin")};
    for(old_raws,old_sizes)|raw,size|{
        if(Fs.parseOwnerStack(raw))|good|{check(size<=49152 and good.session.supervisor.len==size,"OLD_OWNER_STACK_BOUND");}
        else |_|{check(size>49152,"OLD_OWNER_STACK_BOUND");}
    }
    for([_] []const u8{@embedFile("badmagic.bin"),@embedFile("reserved.bin"),@embedFile("truncated.bin"),@embedFile("tail.bin")})|raw|{
        const bad=if(@hasDecl(Fs,"parseExternalApplication")) Fs.parseExternalApplication(raw) else Fs.parseApplication(raw);
        if(bad)|_|{check(false,"MALFORMED_SELECTED_ACCEPTED");}else |_|{}
    }
    check(Fs.application_envelope_limit==13156512,"OLD_DERIVED_OUTER_CAP");
    const external_cap=if(@hasDecl(Fs,"external_application_envelope_limit"))Fs.external_application_envelope_limit else Fs.application_envelope_limit;
    check(external_cap==13181088,"EXTERNAL_DERIVED_OUTER_CAP");
    std.debug.print("PARSER_CAPACITY_PASS\n",.{});
}
'''


def parser_inputs():
    inputs = {str(n)+'.bin': envelope(n) for n in (49152, 49153, 67704, 73728, 73729)}
    raw = inputs['73728.bin']
    changed = bytearray(raw)
    changed[:8] = b'AENFS005'
    inputs['badmagic.bin'] = bytes(changed)
    changed = bytearray(raw)
    changed[4144+24] = 1
    inputs['reserved.bin'] = bytes(changed)
    inputs['truncated.bin'] = raw[:-1]
    inputs['tail.bin'] = raw+b'\0'
    for size in (49152, 49153, 67704):
        old = bytearray(envelope(size))
        old[:8] = b'AENFS005'
        old[4144:4152] = b'AENMX010'
        inputs['old-'+str(size)+'.bin'] = bytes(old)
    return inputs


def boot_source():
    source = (ROOT/'kernel/main.zig').read_text()
    gate = next(line.strip() for line in source.splitlines() if '@panic("native envelope oversized")' in line)
    gate = gate.replace('@import("build_options")', 'O').replace('@import("native_fs_session.zig")', 'Fs')
    gate = gate.replace('@panic("native envelope oversized")', 'return false')
    return r'''const std=@import("std");const Fs=@import("session");
fn check(ok:bool,comptime label:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{label});std.process.exit(91);}}
fn accept(comptime O:type,size:u64)bool{const native=struct{size:u64}{.size=size};
''' + gate + r'''
return true;}
pub fn main()void{
 const External=struct{pub const native_zsh_external=true;pub const native_fs_application_profile=true;pub const native_image_large=true;};
 const Old=struct{pub const native_fs_application_profile=true;pub const native_image_large=true;};
 const Large=struct{pub const native_fs_application_profile=false;pub const native_image_large=true;};
 const Ordinary=struct{pub const native_fs_application_profile=false;pub const native_image_large=false;};
 check(accept(External,13181088) and !accept(External,13181089),"EXTERNAL_BOOT_BOUND");
 check(accept(Old,13156512) and !accept(Old,13156513) and !accept(Old,13181088),"OLD_BOOT_BOUND");
 check(accept(Large,8392752) and !accept(Large,8392753) and !accept(Large,9081744),"LARGE_BOOT_BOUND");
 check(accept(Ordinary,3154000) and !accept(Ordinary,3154001),"ORDINARY_BOOT_BOUND");
 std.debug.print("BOOT_CAPACITY_PASS\n",.{});
}
'''


MAPPING = r'''
const std=@import("std");const FsRoles=@import("roles");const O=@import("build_options");
const combined_profile=true;const combined_init=true;const combined_owner_data=true;
const combined_owner_stack=O.stack;const combined_application_profile=true;const nx:u64=1<<63;
const Page=struct{address:usize=0,flags:u64=0};
const Frame=struct{rsp:u64=0x801000-8,rdi:u64=29,rsi:u64=0xa001,rdx:u64=0xf101,rcx:u64=0xc002,r8:u64=0xd001,r9:u64=0xc003,r10:u64=0,r11:u64=0};
const Context=struct{frame:Frame=.{}};
const State=struct{pages:[128]Page=@splat(.{}),backing:[128][4096]u8=@splat(@splat(0xa5)),count:usize=0,
 pt_index:[32]usize=@splat(0),pt_count:usize=0,pts:[32][512]u64=@splat(@splat(0)),pd:[512]u64=@splat(0),memory_cap:u64=0,execution:Context=.{},
 fn context(s:*State)*Context{return &s.execution;}};
var states:[7]State=@splat(.{});
fn supervisorSlot()usize{return 6;}
fn check(ok:bool,comptime label:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{label});std.process.exit(91);}}
fn require(ok:bool)void{check(ok,"PRODUCTION_INVARIANT");}
fn phys(p:anytype)u64{return @intFromPtr(p)&~@as(u64,4095);}
fn backingFrame(s:*State,i:usize)u64{return 0x10000000+((@intFromPtr(s)-@intFromPtr(&states[0]))/@sizeOf(State)*128+i)*4096;}
fn pte(s:*State,address:usize)u64{for(s.pt_index[0..s.pt_count],0..)|n,i|if(n==address/(2*1024*1024))return s.pts[i][address/4096%512];return 0;}
'''


def mapping_source(*, external, owner_stack=True, omission=None):
    native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
    bodies = '\n'.join(block(native, name) for name in (
        'fn addPage(', 'fn byte(', 'fn mapOwnerStack(', 'fn mapOwnerData(', 'fn ownerDataStartup(', 'fn auditOwnerStack('))
    if omission is not None:
        before, after = omission
        if before not in bodies:
            raise ValueError('omission must match actual production body')
        bodies = bodies.replace(before, after, 1)
    rx = next(line.strip() for line in native.splitlines() if line.strip().startswith('for (0..(supervisor_code.len + 4095) / 4096)'))
    pages = 18 if external else 12 if owner_stack else 2
    count = 3 if external else 2 if owner_stack else 1
    base = 0x7ff000 if external else 0x800000
    cases = r'''
pub fn main()void{
 const s=&states[6];const supervisor_code=[_]u8{0}**CODE_BYTES;
 RX_LOOP
 mapOwnerStack(s);mapOwnerData(s);ownerDataStartup(&s.context().frame);
 check(s.count==CODE_PAGES+STACK_PAGES+2,"STACK_PAGE_COUNT");
 for(0..CODE_PAGES)|i|{check(pte(s,0x400000+i*4096)==backingFrame(s,i)|5,"RX_FLAGS");}
 for(0..STACK_PAGES)|i|{
  check(pte(s,STACK_BASE+i*4096)==backingFrame(s,CODE_PAGES+i)|7|nx,"STACK_RW_NX");
  for(s.backing[CODE_PAGES+i])|v|check(v==STACK_BYTE,"STACK_ZERO");
 }
 check(pte(s,STACK_BASE-4096)==0 and pte(s,STACK_BASE+STACK_PAGES*4096)==0,"STACK_GUARDS");
 check(s.execution.frame.rsp==STACK_TOP-8 and s.execution.frame.rdi==ABI,"ENTRY_UNCHANGED");
 check(s.execution.frame.r10==0x900000 and s.execution.frame.r11==8192,"DATA_ENTRY_UNCHANGED");
 for(0..2)|i|{check(pte(s,0x900000+i*4096)==backingFrame(s,CODE_PAGES+STACK_PAGES+i)|7|nx,"DATA_RW_NX");}
 for(states[0..6])|*peer|check(peer.count==0,"OWNER_ONLY_MAPPING");
 check(s.count<=try_pages() and FsRoles.application_backing_pages==11520,"UNCHANGED_BACKING");
 check(s.memory_cap==0 and s.pt_count<=32,"NO_ALLOCATOR_GRANT");
 auditOwnerStack(s,CODE_PAGES);std.debug.print("MAPPING_CAPACITY_PASS\n",.{});
}
fn try_pages()usize{return FsRoles.applicationPages(6) catch unreachable;}
'''
    values = dict(CODE_BYTES=pages*4096, CODE_PAGES=pages, STACK_PAGES=count,
                  STACK_BASE=hex(base), STACK_TOP=hex(base+count*4096), STACK_BYTE=0 if owner_stack else 0xa5, ABI=31 if owner_stack else 30)
    cases = cases.replace('RX_LOOP', rx)
    for key in sorted(values, key=len, reverse=True):
        cases = re.sub(r'\b'+key+r'\b', str(values[key]), cases)
    return MAPPING+bodies+cases


def inspector():
    spec = importlib.util.spec_from_file_location('actual_owner_stack', ROOT/'scripts/owner_stack.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OwnerCapacity(unittest.TestCase):
    def test_explicit_three_page_inspector_and_old_capacity_refusal(self):
        s = inspector()
        assembly = '0000000000400000 <_start>:\n400000: sub rsp, 9280\n400007: ret\n'
        self.assertEqual(s.inspect(assembly, stack_bytes=12288)['entry_stack_bytes'], 9408)
        for capacity in (4096, 8192):
            with self.assertRaises(s.StackLimit):
                s.inspect(assembly, stack_bytes=capacity)

    def test_stack_inspector_default_and_unsupported_profiles(self):
        s = inspector()
        assembly = '0000000000400000 <_start>:\n400000: ret\n'
        self.assertEqual(s.inspect(assembly)['usable_stack_bytes'], 4088)
        self.assertEqual(s.inspect(assembly, stack_bytes=8192)['usable_stack_bytes'], 8184)
        for capacity in (True, 0, 8193, 16384):
            with self.assertRaises(ValueError):
                s.inspect(assembly, stack_bytes=capacity)

    def test_selected_inspector_keeps_dynamic_recursive_unknown_edge_denials(self):
        s = inspector()
        for instruction in ('sub rsp, rax', 'xchg rsp, rax', 'call 400000 <_start>', 'call rax'):
            with self.subTest(instruction=instruction), self.assertRaises(ValueError):
                s.inspect('0000000000400000 <_start>:\n400000: '+instruction+'\n', stack_bytes=12288)

    def test_fixtures_use_actual_sources_and_closed_extents(self):
        raw = envelope(73728)
        self.assertEqual(len(raw), 48+4096+112+3*4096+73728)
        self.assertEqual(struct.unpack_from('<I', raw, 4144+20)[0], 73728)
        for size in (49152, 49153, 67704):
            old = parser_inputs()['old-'+str(size)+'.bin']
            self.assertEqual(old[:8], b'AENFS005')
            self.assertEqual(old[4144:4152], b'AENMX010')
            self.assertEqual(struct.unpack_from('<I', old, 4144+20)[0], size)
        self.assertIn('Fs.parseApplication(raw)', parser_source())
        self.assertIn('native envelope oversized', (ROOT/'kernel/main.zig').read_text())
        self.assertIn('native.size >', boot_source())
        dispatch = block((ROOT/'kernel/arch/x86_64/native_c.zig').read_text(), 'fn startSupervised(')
        self.assertIn('native_zsh_external) FsSession.parseExternalApplication(envelope) else if (combined_application_profile) FsSession.parseApplication(envelope)', dispatch)
        for external in (False, True):
            self.assertIn(block((ROOT/'kernel/arch/x86_64/native_c.zig').read_text(), 'fn auditOwnerStack('), mapping_source(external=external))


if __name__ == '__main__':
    unittest.main()
