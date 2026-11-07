# SPDX-License-Identifier: BSD-2-Clause
"""Closed #158 capacity fixtures; bounded actual Zig execution is lead-recorded.

Pure controls: python3 -B -m unittest discover -s tests -p test_zsh_home_redirection_profile.py -v
These helpers execute actual current parser/boot/start/mapping bodies when used
by the bounded host recipe. They build no image and grant no guest authority.
"""
import ast
from pathlib import Path
import unittest

from test_zsh_owner_capacity import (ROOT, envelope, parser_inputs as old_inputs,
    start_preflight_source as old_start, boot_source as old_boot,
    mapping_source as old_mapping)


def parser_inputs():
    return {**old_inputs(), **{str(n)+'.bin': envelope(n) for n in (81920, 81921)}}


def parser_source():
    return r'''const std=@import("std");const Fs=@import("session");
fn check(ok:bool,comptime label:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{label});std.process.exit(91);}}
pub fn main()void{
 const sizes=[_]usize{73728,73729,81920,81921};
 const raws=[_] []const u8{@embedFile("73728.bin"),@embedFile("73729.bin"),@embedFile("81920.bin"),@embedFile("81921.bin")};
 for(raws,sizes)|raw,size|{
  const selected=if(@hasDecl(Fs,"parseHomeRedirectionApplication"))Fs.parseHomeRedirectionApplication(raw)else Fs.parseExternalApplication(raw);
  if(selected)|good|{check(size<=81920 and good.session.supervisor.len==size,"HOME_REDIRECTION_OWNER_BOUND");}
  else |_|{check(size>81920,"HOME_REDIRECTION_OWNER_BOUND");}
  if(Fs.parseExternalApplication(raw))|good|{check(size<=73728 and good.session.supervisor.len==size,"OLD_EXTERNAL_OWNER_BOUND");}
  else |_|{check(size>73728,"OLD_EXTERNAL_OWNER_BOUND");}
  if(Fs.parseApplication(raw))|_|{check(false,"OLD_APPLICATION_NOT_WIDENED");}else |_|{}
 }
 for([_] []const u8{@embedFile("badmagic.bin"),@embedFile("reserved.bin"),@embedFile("truncated.bin"),@embedFile("tail.bin")})|raw|{
  const selected=if(@hasDecl(Fs,"parseHomeRedirectionApplication"))Fs.parseHomeRedirectionApplication(raw)else Fs.parseExternalApplication(raw);
  if(selected)|_|{check(false,"MALFORMED_HOME_REDIRECTION_ACCEPTED");}else |_|{}
 }
 const cap=if(@hasDecl(Fs,"home_redirection_application_envelope_limit"))Fs.home_redirection_application_envelope_limit else Fs.external_application_envelope_limit;
 check(cap==13189280,"HOME_REDIRECTION_DERIVED_OUTER_CAP");
 check(Fs.external_application_envelope_limit==13181088 and Fs.application_envelope_limit==13156512,"OLD_DERIVED_CAPS");
 std.debug.print("HOME_REDIRECTION_PARSER_PASS\n",.{});
}
'''


def start_source():
    source=old_start()
    source=source.replace(' const External=struct{', ' const Home=struct{pub const application=true;pub const native_zsh_external=true;pub const native_zsh_home_redirection=true;};\n const External=struct{',1)
    anchor=' std.debug.print("EARLY_START_PREFLIGHT_PASS'
    checks=""" for([_] []const u8{@embedFile("73729.bin"),@embedFile("81920.bin")})|raw|expect(Home,raw,true,"EARLY_START_HOME_REDIRECTION_BOUND");
 expect(Home,@embedFile("81921.bin"),false,"EARLY_START_HOME_REDIRECTION_ONE_OVER");
 for([_] []const u8{@embedFile("badmagic.bin"),@embedFile("reserved.bin"),@embedFile("truncated.bin"),@embedFile("tail.bin")})|raw|expect(Home,raw,false,"EARLY_START_HOME_REDIRECTION_MALFORMED");
"""
    assert source.count(anchor)==1
    return source.replace(anchor,checks+anchor,1)


def boot_source():
    source=old_boot()
    source=source.replace(' const External=struct{', ' const Home=struct{pub const native_zsh_home_redirection=true;pub const native_zsh_external=true;pub const native_fs_application_profile=true;pub const native_image_large=true;};\n const External=struct{',1)
    anchor=' check(accept(External,13181088)'
    assert source.count(anchor)==1
    return source.replace(anchor,' check(accept(Home,13189280) and !accept(Home,13189281),"HOME_REDIRECTION_BOOT_BOUND");\n'+anchor,1)


def mapping_source():
    return old_mapping(external=True,code_bytes=81920)


def build_cases(directory):
    tree=ast.parse((ROOT/'scripts/fs_session.py').read_text())
    node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FLAGS' for t in n.targets))
    flags=ast.literal_eval(node.func.value).split()+['native-fs-session-init','native-fs-owner-data','native-fs-owner-stack','native-fs-application-profile','native-zsh-terminfo','native-tty-mode-probe','native-tty-signal-probe','native-signal-mask-delivery','native-zsh-external','native-signal-suspend','native-zsh-file-exec','native-zsh-operator']
    image=Path(directory)/'unexecuted.bin';image.write_bytes(b'\0')
    base={'smp':'false','native-c-image':str(image),**dict.fromkeys(flags,'true')}
    selected={**base,'native-zsh-home-redirection':'true'}
    return [('default',{},False),('old-operator',base,False),('home-redirection',selected,False),
        ('missing-operator',{**selected,'native-zsh-operator':'false'},True),
        ('missing-file-exec',{**selected,'native-zsh-file-exec':'false'},True),
        ('release',{**selected,'release-artifact':'true'},True),
        ('standalone',{'native-zsh-home-redirection':'true'},True)]


class HomeRedirectionFixtures(unittest.TestCase):
    def test_extents_and_actual_guard_sources(self):
        inputs=parser_inputs()
        self.assertEqual(len(inputs['81920.bin']),48+4096+112+3*4096+81920)
        self.assertIn('parseHomeRedirectionApplication',parser_source())
        self.assertIn('native_zsh_home_redirection',start_source())
        self.assertIn('native_zsh_home_redirection',boot_source())
        self.assertIn('81920',mapping_source())


if __name__=='__main__':unittest.main()
