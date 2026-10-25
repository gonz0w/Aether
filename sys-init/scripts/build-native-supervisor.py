#!/usr/bin/env python3
"""Build a sys-init policy client and bind it with a native C envelope; inert output."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from bounded_tools import run_recorded
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('native',type=Path);p.add_argument('output',type=Path);p.add_argument('--variant',choices=['pass','fault_entry','wrong_detail','io','io-stop','io-stop-wrong-detail','io-retained-stop','io-retained-fault','io-retained-wrong-kind','io-ready-exit','io-ready-fault','io-unready-exit','io-unready-fault','io-unready-stop','io-invent-ready','io-authority','io-authority-allow','io-peer','io-peer-reverse','io-peer-wrong'],default='pass');a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
raw=a.native.read_bytes()
if len(raw)<=40 or raw[:8]!=b'AENATC01':raise SystemExit('native C envelope required')
code=a.output/'supervisor.raw'
io_profile=a.variant.startswith('io')
readiness=a.variant in ('io-ready-exit','io-ready-fault','io-unready-exit','io-unready-fault','io-unready-stop','io-invent-ready')
source='io_peer.rs' if a.variant.startswith('io-peer') else 'io_authority.rs' if a.variant.startswith('io-authority') else 'io_readiness.rs' if readiness else 'io_retained.rs' if a.variant.startswith('io-retained') else 'io_stop.rs' if a.variant.startswith('io-stop') else 'io.rs' if a.variant=='io' else 'main.rs'
command=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-C','opt-level=2','-C','panic=abort','-C','relocation-model=static','-C','link-arg=-T'+str(ROOT/'prototypes/native-supervisor/linker.ld'),'-C','link-arg=--oformat=binary','--check-cfg=cfg(fault_entry)','--check-cfg=cfg(wrong_detail)',str(ROOT/'prototypes/native-supervisor'/source),'-o',str(code)]
if a.variant.startswith('io-stop'):command+=['--check-cfg=cfg(wrong_stop_detail)']
if a.variant=='io-stop-wrong-detail':command+=['--cfg','wrong_stop_detail']
elif a.variant in ('fault_entry','wrong_detail'):command+=['--cfg',a.variant]
if a.variant.startswith('io-retained'):
    command+=['--check-cfg=cfg(fault_first)','--check-cfg=cfg(wrong_kind)']
    if a.variant!='io-retained-stop':command+=['--cfg','fault_first']
    if a.variant=='io-retained-wrong-kind':command+=['--cfg','wrong_kind']
if readiness:
    command+=['--check-cfg=cfg(early_stop)','--check-cfg=cfg(worker_fault)','--check-cfg=cfg(notify_first)','--check-cfg=cfg(invent_ready)']
    if a.variant=='io-unready-stop':command+=['--cfg','early_stop']
    if a.variant.endswith('-fault'):command+=['--cfg','worker_fault']
    if a.variant.startswith('io-ready-'):command+=['--cfg','notify_first']
    if a.variant=='io-invent-ready':command+=['--cfg','invent_ready']
if a.variant.startswith('io-authority'):
    command+=['--check-cfg=cfg(allow_notify)']
    if a.variant=='io-authority-allow':command+=['--cfg','allow_notify']
if a.variant.startswith('io-peer'):
    command+=['--check-cfg=cfg(reverse)','--check-cfg=cfg(peer_ready)']
    if a.variant=='io-peer-reverse':command+=['--cfg','reverse']
    if a.variant=='io-peer-wrong':command+=['--cfg','peer_ready']
run_recorded(command,a.output/'compiler.log',__file__);supervisor=code.read_bytes()
if not 0<len(supervisor)<=4096:raise SystemExit('supervisor image bound')
image=a.output/'supervised.bin';image.write_bytes(struct.pack('<8sII',b'AENFD001' if io_profile else b'AENSUP01',len(raw)-40,len(supervisor))+raw[8:40]+raw[40:]+supervisor)
(a.output/'build.json').write_text(json.dumps({'command':command,'variant':a.variant,'native_sha256':hashlib.sha256(raw).hexdigest(),'supervisor_sha256':hashlib.sha256(supervisor).hexdigest(),'envelope_sha256':hashlib.sha256(image.read_bytes()).hexdigest()},indent=2)+'\n')
print(image)
