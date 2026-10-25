#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare matching AF08/FILE03 inputs from checked outputs; no default pin or VM."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from fs_context_launch import build
from fs_af07_inputs import guarded


def main():
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            self.print_usage(sys.stderr)
            self.exit(64,'[ERROR] '+ascii(message)[1:-1]+'\n')
    parser=Parser(description=__doc__,epilog='Consume owned producer/provider/owner checks; write unused .deps/fs-launch-af08-* and fs-owner-af08-* candidates. No guest, default pin update or release acceptance.')
    parser.add_argument('--version',action='version',version='aether-fs-context-inputs 1')
    parser.add_argument('--producer',required=True,type=Path)
    parser.add_argument('--provider',required=True,type=Path)
    parser.add_argument('--owner',required=True,type=Path)
    parser.add_argument('--engine-output',required=True,type=Path)
    parser.add_argument('--guarded-output',required=True,type=Path)
    args=parser.parse_args()
    engine=build(args.engine_output,args.producer)
    owner=guarded(args.guarded_output,Path(engine['elf']).parent,
        engine['manifest_sha256'],paths=True,dup2=True,cwd=True,
        checked=dict(producer=args.producer,provider=args.provider,owner=args.owner))
    print(json.dumps(dict(schema='aether-fs-context-inputs-result-v1',status='prepared',engine=engine,owner=owner,native_executed=False)))


if __name__=='__main__':
    try: main()
    except ValueError as error:
        print('[BLOCKED] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(2)
    except (OSError,RuntimeError,subprocess.SubprocessError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(1)
