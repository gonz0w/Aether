# SPDX-License-Identifier: BSD-2-Clause
"""Execute actual channel syscall/copy bodies; no host timing claim."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from test_native_cleanup import block

SCAFFOLD = r'''
const std = @import("std");
const C = @import("channel");
const Page = struct { address: usize = 0, flags: u64 = 0 };
const Frame = struct {rax:u64=0,rdi:u64=0,rsi:u64=0,rdx:u64=0,r10:u64=0,r8:u64=0,r9:u64=0};
const State = struct {
 pages:[3]Page=@splat(.{}),count:usize=3,backing:[3][4096]u8=@splat(@splat(0xa5)),
 channel_wait:C.Wait=.{},on_child:bool=false,
};
var states:[1]State=@splat(.{});
var channels:[1]C.Channel=@splat(.{});
var active:usize=0;
var response:i64=99;
var lookups:usize=0;
var published:usize=0;
var returned:Frame=.{};
fn channelCount() usize {return channels.len;}
fn channelInterrupted(_: *State) bool {return false;}
fn traceStorageChannelWait(_:usize,_:[]const u8,_:i64) void {}
fn rotate() void {}
fn select() *const Frame {return &returned;}
fn result(_: *State, value:i64) void {response=value;}
fn require(ok:bool) void {if(!ok) @panic("CHANNEL_STREAM");}
fn publishSustained() void {published+=1;}
fn check(ok:bool, comptime message:[]const u8) void {if(!ok) @panic(message);}
fn reset() void {
 states=@splat(.{});channels=@splat(.{});lookups=0;published=0;response=99;
 // Virtual neighbors use noncontiguous/reversed backing records.
 states[0].pages=.{.{.address=0x2000,.flags=7},.{.address=0x9000,.flags=7},.{.address=0x1000,.flags=7}};
 _=channels[0].create(0);
}
fn invoke(reading:bool,address:usize,length:usize) void {
 const f=Frame{.rax=if(reading) 0x24001 else 0x24002,.rdi=channels[0].cap(if(reading) 0 else 1),.rsi=address,.rdx=length};
 _=transfer(&f);
}
fn fill(count:usize) void {for(0..count) |i| require(channels[0].stream.push(@intCast(i))==0);}
fn put(address:usize,value:u8) void {
 const index:usize=if(address<0x2000) 2 else 0;
 states[0].backing[index][address%4096]=value;
}
fn get(address:usize) u8 {const index:usize=if(address<0x2000) 2 else 0;return states[0].backing[index][address%4096];}
'''
CASES = r'''
test "all chunk/page boundaries and noncontiguous backing use one lookup per page" {
 for([_]bool{false,true}) |reading| for(0..16) |edge| for(1..17) |length| {
  reset();const address=0x2000-edge;
  if(reading) fill(length) else for(0..length) |i| put(address+i,@intCast(i));
  invoke(reading,address,length);
  check(response==length,"CHANNEL_COUNT");
  check(lookups==(if(edge==0 or length<=edge) @as(usize,1) else 2),"CHANNEL_LOOKUP_BOUND");
  for(0..length) |i| {
   const value=if(reading) get(address+i) else channels[0].stream.pop();
   check(value==i,"CHANNEL_BYTES");
  }
  check(get(address-1)==0xa5 and get(address+length)==0xa5,"CHANNEL_GUARDS");
 };
}
test "entire requested chunk validates before any short empty closed or full result" {
 for([_]bool{false,true}) |reading| for(0..4) |mode| for([_]u64{0,1,3,4}) |flags| {
  reset();states[0].pages[0].flags=flags;
  if(mode==0) fill(3);
  if(mode==1) channels[0].stream.sealed=true;
  if(mode==2) channels[0].stream.reader_closed=true;
  if(mode==3) fill(32);
  const stream=channels[0].stream;const before=states[0].backing;
  invoke(reading,0x1ff8,16);
  check(response==-14,"CHANNEL_PREFLIGHT");
  check(std.meta.eql(stream,channels[0].stream),"CHANNEL_QUEUE_UNCHANGED");
  check(std.meta.eql(before,states[0].backing),"CHANNEL_BUFFER_UNCHANGED");
  check(published==0,"CHANNEL_NO_PUBLICATION");
 };
 reset();states[0].pages[0].address=0;fill(3);invoke(true,0x1ff8,16);
 check(response==-14 and channels[0].stream.count==3,"CHANNEL_HOLE");
 reset();states[0].pages[0].flags=5;fill(3);invoke(true,0x1ff8,16);
 check(response==-14 and channels[0].stream.count==3,"CHANNEL_READONLY_SECOND");
 reset();states[0].pages[0].flags=5;invoke(false,0x1ff8,16);
 check(response==16,"CHANNEL_READABLE_SOURCE");
}
test "authority reserved direction zero and overflow retain precedence" {
 reset();var f=Frame{.rax=0x24001,.rdi=channels[0].cap(0)+99,.rsi=0,.rdx=16};
 _=transfer(&f);check(response==-13 and lookups==0,"CHANNEL_AUTHORITY");
 f.rdi=channels[0].cap(1);_=transfer(&f);check(response==-9 and lookups==0,"CHANNEL_DIRECTION");
 f.rdi=channels[0].cap(0);f.rdx=257;_=transfer(&f);check(response==-22 and lookups==0,"CHANNEL_LENGTH");
 f.rdx=16;f.r10=1;_=transfer(&f);check(response==-22 and lookups==0,"CHANNEL_RESERVED");
 reset();invoke(true,std.math.maxInt(usize),1);check(response==-14 and lookups==0,"CHANNEL_OVERFLOW");
 reset();invoke(true,std.math.maxInt(usize),0);check(response==0 and lookups==0,"CHANNEL_ZERO");
 reset();invoke(true,0,1);check(response==-14,"CHANNEL_NULL");
 reset();channels[0].closeOwner(0);invoke(true,0x1000,16);check(response==-13 and lookups==0,"CHANNEL_STALE");
}
test "queue short results and closure are unchanged" {
 reset();fill(3);invoke(true,0x1ff8,16);check(response==3 and channels[0].stream.count==0,"CHANNEL_SHORT_READ");
 check(get(0x1ffb)==0xa5,"CHANNEL_SHORT_GUARD");
 reset();fill(30);invoke(false,0x1ff8,16);check(response==2 and channels[0].stream.count==32,"CHANNEL_SHORT_WRITE");
 reset();invoke(true,0x1000,16);check(response==-11,"CHANNEL_EMPTY");
 channels[0].stream.sealed=true;invoke(true,0x1000,16);check(response==0,"CHANNEL_EOF");
 reset();fill(32);invoke(false,0x1000,16);check(response==-11,"CHANNEL_FULL");
 reset();channels[0].stream.reader_closed=true;invoke(false,0x1000,16);check(response==-32,"CHANNEL_EPIPE");
 reset();invoke(false,0x1000,256);check(response==16,"CHANNEL_CAPPED_CHUNK");
}
'''


class ChannelCopy(unittest.TestCase):
    def test_actual_transfer_boundaries_and_compiling_semantic_omissions(self):
        source = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        helper = block(source, 'const ChannelBuffer = struct') + ';\n' + block(source, 'fn channelBuffer(')
        lookup = block(source, 'fn byte(').replace('    for (s.pages', '    lookups += 1;\n    for (s.pages', 1)
        operation = block(source, 'fn channelOperation(')
        tail = operation[operation.index('    const selected = ownedChannel'):]
        owned = block(source, 'fn ownedChannel(').replace('@import("../../native_channel.zig")', 'C')
        function = 'fn transfer(f:*const Frame) *const Frame {const s=&states[active];\n' + tail
        variants = [
            ('actual', helper, function, None),
            ('second-write-right', helper.replace('byte(s, address + length, write)', 'byte(s, address + length, false)'), function, 'CHANNEL_READONLY_SECOND'),
            ('contiguous-backing', helper.replace('second = next[0 .. count - length];', '_ = next; second = first[length..count];'), function, 'CHANNEL_BYTES'),
            ('early-effect', helper, function.replace('    const buffer = channelBuffer', '    if (reading and selected.stream.count > 0) { const p = byte(s, @intCast(f.rsi), true) orelse unreachable; p.* = @intCast(selected.stream.pop()); }\n    const buffer = channelBuffer'), 'CHANNEL_QUEUE_UNCHANGED'),
            ('repeated-lookup', helper, function.replace('const p = if (i < buffer.first.len) &buffer.first[i] else &buffer.second[i - buffer.first.len];', '_ = buffer; const p = byte(s, @intCast(f.rsi + i), reading).?;'), 'CHANNEL_LOOKUP_BOUND'),
        ]
        with tempfile.TemporaryDirectory(prefix='aether-channel-copy-') as directory:
            out = Path(directory)
            options = out / 'options.zig'
            options.write_text('pub const native_service_channel_wait=false;')
            for name, view, transfer, oracle in variants:
                path = out / (name + '.zig')
                path.write_text(SCAFFOLD + lookup + '\n' + view + '\n' + owned + '\n' + transfer + CASES)
                command = ['zig', 'test', '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global'),
                           '--dep', 'channel', '--dep', 'build_options', '-Mroot=' + str(path),
                           '-Mchannel=' + str(ROOT / 'kernel/native_channel.zig'), '-Mbuild_options=' + str(options)]
                if name == 'early-effect':
                    command += ['--test-filter', 'entire requested chunk']
                run = subprocess.run(command, capture_output=True, text=True, timeout=120)
                if oracle:
                    self.assertNotEqual(run.returncode, 0, name)
                    self.assertNotRegex(run.stderr, r':\d+:\d+: error:', name + run.stderr)
                    self.assertIn(oracle, run.stderr, name + run.stderr)
                else:
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
