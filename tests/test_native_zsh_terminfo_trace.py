# SPDX-License-Identifier: BSD-2-Clause
"""Actual emission bodies with tiny host scaffolding; this is not a VM.

Run python3 -B -m unittest discover -s tests -p test_native_zsh_terminfo_trace.py -v.
Public checks launch no process and use only the standard library. The returned
Zig fixture is compiled with the private qualified capture entry for issue137;
committed public bounded_capture.py does not supply that private execution API.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SELECTED='(@hasDecl(@import("build_options"), "native_zsh_terminfo") and @import("build_options").native_zsh_terminfo)'


def body(source,anchor):
    if source.count(anchor)!=1:raise ValueError('one actual source anchor required')
    start=source.index(anchor);opening=source.index('{',start);depth=0
    for at in range(opening,len(source)):
        if source[at]=='{':depth+=1
        elif source[at]=='}':
            depth-=1
            if depth==0:return source[start:at+1]
    raise ValueError('unterminated actual body')


def emissions(source):
    complete=body(source,'fn completeWait(')
    channel=body(source,'fn traceStorageChannelWait(')
    after=source.split('const status = s.context().wait.parkAbsolute(',1)
    if len(after)!=2:raise ValueError('one absolute clock park required')
    park=body(after[1].split('} else if ((f.rax',1)[0],'if (status == 0) {')
    return complete,channel,park


def checker_source(source,omission=None):
    complete,channel,park=emissions(source)
    if omission=='channel':channel=channel.replace('    if ('+SELECTED+' and status == 0) return;\n','')
    elif omission=='timeout':complete=complete.replace(' and !'+SELECTED,'')
    elif omission=='park':park=park.replace('if (!'+SELECTED+') {','if (true) {')
    elif omission is not None:raise ValueError('closed guard omission')
    actual='\n'.join((complete,channel,'fn clockPark(status:i64) *Frame { const s=&state; const f=&frame; const now:u64=8;'+park+'\nreturn select();\n}'))
    actual=actual.replace('@import("build_options")','options')
    return r'''
const std=@import("std");
const options=struct{var native_zsh_terminfo=false;const native_service_channel_wait=true;var native_clock_skip_wait=false;};
const Frame=struct{rax:u64=0,rdx:u64=0,r10:u64=99};
const Done=struct{status:i64,elapsed:u64};
const Wait=struct{monotonic:bool=true,done:?Done=null,
 fn completeAt(self:*Wait,key:usize,ticks:u64,now:?u64)?Done{_ = key;_ = ticks;_ = now;const d=self.done;self.done=null;return d;}};
const Execution=struct{wait:Wait=.{},frame:Frame=.{}};
const State=struct{generation:u64=1,execution:Execution=.{},fn context(self:*@This())*Execution{return &self.execution;}};
const serial=struct{var bytes:[1024]u8=undefined;var used:usize=0;fn write(s:[]const u8)void{@memcpy(bytes[used..][0..s.len],s);used+=s.len;}};
var states:[7]State=@splat(.{});const combined_owner_stack=true;const total_ticks:u64=5;
var state:State=.{};var frame:Frame=.{};var rotations:usize=0;const active:usize=1;
fn result(s:*State,status:i64)void{s.execution.frame.rax=@bitCast(status);}
fn rotate()void{rotations+=1;}
fn select()*Frame{return &frame;}
ACTUAL

test "actual channel row selection retains every nonzero completion" {
 for([_]bool{false,true})|quiet|{
  options.native_zsh_terminfo=quiet;
  for([_]i64{0,-4,-13,-38,-5,1})|status|{
   for([_][]const u8{"park","wake"})|phase|{
    serial.used=0;traceStorageChannelWait(1,phase,status);
    if(quiet and status==0){try std.testing.expectEqual(@as(usize,0),serial.used);}
    else{var expected:[128]u8=undefined;const row=try std.fmt.bufPrint(&expected,"\nNATIVE STORAGE WAIT slot=1 generation=1 phase={s} status={d}\n",.{phase,status});try std.testing.expectEqualSlices(u8,row,serial.bytes[0..serial.used]);}
   }
  }
 }
}
test "actual timeout returns elapsed and status despite selected quiet" {
 for([_]bool{false,true})|quiet|{for([_]i64{-110,0,-4})|status|{
  options.native_zsh_terminfo=quiet;serial.used=0;
  var context=Execution{.wait=.{.done=.{.status=status,.elapsed=7}}};
  completeWait(&context,1,0,8);
  try std.testing.expectEqual(@as(u64,@bitCast(status)),context.frame.rax);
  try std.testing.expectEqual(@as(u64,7),context.frame.rdx);
  try std.testing.expect(context.wait.done==null);
  if(status == -110 and !quiet)try std.testing.expectEqualStrings("NATIVE CLOCK timeout task=1 now=8 elapsed=7\n",serial.bytes[0..serial.used])
  else try std.testing.expectEqual(@as(usize,0),serial.used);
 }}
}
test "actual clock park scheduling and skip result remain unchanged" {
 for([_]bool{false,true})|quiet|{for([_]bool{false,true})|skip|{
  options.native_zsh_terminfo=quiet;options.native_clock_skip_wait=skip;serial.used=0;rotations=0;state=.{};
  _=clockPark(0);
  try std.testing.expectEqual(@as(usize,@intFromBool(!skip)),rotations);
  try std.testing.expectEqual(@as(u64,if(skip) @bitCast(@as(i64,-110)) else 0),state.execution.frame.rax);
  if(quiet)try std.testing.expectEqual(@as(usize,0),serial.used)
  else try std.testing.expectEqualStrings("NATIVE CLOCK park task=1 start=8 deadline=99\n",serial.bytes[0..serial.used]);
 }}
}
'''.replace('ACTUAL',actual)


class ZshTerminfoTraceSource(unittest.TestCase):
    def test_actual_guards_scope_only_emission_and_keep_scheduler_assignments(self):
        source=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        complete,channel,park=emissions(source)
        self.assertIn('if ('+SELECTED+' and status == 0) return;',channel)
        self.assertIn('clock_wait and done.status == -110 and !'+SELECTED,complete)
        self.assertIn('context.frame.rax = @bitCast(done.status);',complete)
        self.assertIn('context.frame.rdx = done.elapsed;',complete)
        self.assertIn('if (!'+SELECTED+') {',park)
        self.assertIn('} else rotate();',park)
        self.assertIn('result(s, -110);',park)
        self.assertEqual(source.count('"NATIVE CLOCK park task='),1)
        self.assertEqual(source.count('"NATIVE CLOCK timeout task='),1)
        self.assertEqual(source.count('"NATIVE STORAGE WAIT slot='),1)

    def test_fixture_extracts_actual_functions_and_rejects_unknown_omission(self):
        source=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        self.assertIn('fn completeWait(',checker_source(source))
        for omission in ('channel','timeout','park'):
            self.assertNotEqual(checker_source(source),checker_source(source,omission))
        with self.assertRaises(ValueError):checker_source(source,'unknown')
        with self.assertRaises(ValueError):emissions(source.replace('fn completeWait(','fn noCompleteWait('))


if __name__=='__main__':unittest.main()
