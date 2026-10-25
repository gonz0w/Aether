#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Consume a pinned native-init producer with sys-init-owned policy; offline QEMU."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import struct
import subprocess
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1]
BUILD_PROFILE = 'retained-sampling-v1'
def compiler_profile(source_dir):
    """Fixed experimental profile; preserve the one-page linker and runtime bounds."""
    return ['-C', 'opt-level=s', '-C', 'panic=abort', '-C', 'relocation-model=static',
            '--remap-path-prefix='+str(source_dir)+'=sys-init/prototypes/native-supervisor']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(root,name):
    path=Path(name)
    if not name or path.is_absolute() or '..' in path.parts:
        raise ValueError('non-relative worker input')
    target=root/path
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('worker input escapes root')
    return target
def validate_service_worker(worker_dir,pin):
    evidence=worker_dir/'evidence.json'
    report=json.loads(evidence.read_text())
    if (not pin or sha(evidence)!=pin
            or report.get('schema')!='sys-init-native-service-worker-v1'
            or report.get('result')!='pass' or report.get('inputs_unchanged') is not True
            or sha(worker_dir/'service-worker.elf')!=report['worker_sha256']):
        raise ValueError('invalid service worker receipt')
    for name,digest in report['inputs'].items():
        if sha(relative(worker_dir,name))!=digest:
            raise ValueError('service worker input mismatch: '+name)
    return report
def validate(producer,pin,large=False,composed=False):
    if large and composed:raise ValueError("select one init profile")
    if sha(producer/'summary.json')!=pin:raise ValueError('producer summary pin mismatch')
    summary=json.loads((producer/'summary.json').read_text())
    if composed and (summary.get('schema')!='sys-init-init-composed-intake-v1' or
                     (summary.get('native_profile'),summary.get('abi'),summary.get('supervisor_limit'),summary.get('stack_bytes'))!=('AENIN003',16,16384,4096)):
        raise ValueError('invalid composed intake profile')
    if sha(producer/'producer-sources.tar.gz')!=summary['source_archive_sha256']:raise ValueError('archive mismatch')
    if sha(producer/'init/results.json')!=summary['suites']['init']['report_sha256']:raise ValueError('producer report mismatch')
    report=json.loads((producer/'init/results.json').read_text())
    if report['status']!='pass' or report['profile']!=('init-composed' if composed else 'init-large' if large else 'init'):raise ValueError('incomplete producer')
    case=next(c for c in report['cases'] if c['name']=='positive')
    raw=(producer/'init/positive/native-c.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=case['envelope_sha256']:raise ValueError('producer envelope mismatch')
    if len(raw)<56:raise ValueError('short init envelope')
    magic,a,b,c,reserved=struct.unpack_from('<8sIIII',raw)
    if (magic!=(b'AENIN003' if composed else b'AENIN002' if large else b'AENIN001') or reserved or not 0<a<=1048576 or not 0<b<=1048576
            or not 0<c<=(16384 if composed else 8192 if large else 4096) or len(raw)!=56+a+b+c):raise ValueError('bounded selected init envelope required')
    for name,body in [('helper1.elf',raw[56:56+a]),('helper2.elf',raw[56+a:56+a+b])]:
        if (producer/'init'/name).read_bytes()!=body:raise ValueError('producer ELF correspondence mismatch')
    return summary,raw[:56+a+b],a,b

def main():
    class Parser(argparse.ArgumentParser):
        def error(self,message):self.exit(64,self.prog+': '+message+'\n')
    p=Parser(description=__doc__)
    p.add_argument('--version',action='version',version='sys-init native init consumer 1')
    profiles=p.add_mutually_exclusive_group()
    profiles.add_argument('--init-composed',action='store_true',help='explicit AENIN003/ABI 16 profile; 16 KiB code, 4 KiB stack')
    profiles.add_argument('--init-large',action='store_true',help='explicit AENIN002/ABI 15 profile; default remains ABI 6')
    p.add_argument('--producer',type=Path,required=True)
    p.add_argument('--summary-pin',required=True)
    p.add_argument('--deps',type=Path,help='required for ABI 6; ABI 15 uses archived pinned boot dependencies')
    p.add_argument('--service-worker',type=Path,
                   help='explicit sys-init service-worker build directory')
    p.add_argument('--service-worker-pin',help='SHA256 of service worker evidence.json')
    p.add_argument('--work',type=Path,required=True,help='new private directory')
    args=p.parse_args();producer=args.producer.resolve();expanded=args.init_large or args.init_composed
    if not expanded and args.deps is None:p.error('--deps is required for ABI 6')
    if expanded and args.deps is not None:p.error('expanded init profiles use archived boot dependencies; omit --deps')
    summary,prefix,first,second=validate(producer,args.summary_pin,args.init_large,args.init_composed)
    service_worker=None
    worker_report=None
    if args.service_worker:
        worker_dir=args.service_worker.resolve()
        worker_report=validate_service_worker(worker_dir,args.service_worker_pin)
        service_worker=worker_dir/'service-worker.elf'
    work=args.work.resolve();work.mkdir(parents=True,exist_ok=False);os.chmod(work,0o700)
    inputs=work/'inputs';inputs.mkdir()
    for name in ['summary.json','producer-sources.tar.gz','init/results.json','init/positive/native-c.bin','init/helper1.elf','init/helper2.elf']:
        target=inputs/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(producer/name,target)
    if service_worker:
        shutil.copyfile(service_worker,inputs/'service-worker.elf')
        shutil.copyfile(service_worker.parent/'evidence.json',inputs/'service-worker-evidence.json')
    validate(inputs,args.summary_pin,args.init_large,args.init_composed)
    kernel=work/'Aether';kernel.mkdir()
    with tarfile.open(inputs/'producer-sources.tar.gz') as archive:archive.extractall(kernel,filter='data')
    for name,pin in summary['inputs'].items():
        if sha(kernel/name)!=pin:raise ValueError('frozen producer source mismatch: '+name)
    if expanded:
        # Expanded profiles' source manifest pins its archived boot dependencies. Never replace them.
        if not (kernel/'.deps').is_dir():raise ValueError('missing pinned boot dependencies')
    else:
        shutil.copytree(args.deps,kernel/'.deps')
    client=work/'sys-init'
    for name in ['prototypes/native-supervisor/init.rs','prototypes/native-supervisor/adapter.rs','prototypes/native-supervisor/service.rs','prototypes/native-supervisor/service_owner.rs','prototypes/native-supervisor/owner_fixture.rs','prototypes/native-supervisor/service_pair.rs','prototypes/native-supervisor/pair_fixture.rs','prototypes/native-supervisor/attempt.rs','prototypes/native-supervisor/binding.rs','prototypes/native-supervisor/terminal.rs','prototypes/native-supervisor/sample_receipts.rs','prototypes/native-supervisor/raw_sampling.rs','prototypes/native-supervisor/pending_history.rs','prototypes/native-supervisor/cut_reservation.rs','prototypes/native-supervisor/init.ld','prototypes/native-supervisor/init-large.ld','prototypes/native-supervisor/init-composed.ld','tests/native-init.py']:
        target=client/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    pins={str(p.relative_to(work)):sha(p) for tree in (kernel,client,inputs) for p in tree.rglob('*') if p.is_file()}
    (work/'sources.json').write_text(json.dumps(pins,indent=2)+'\n')
    report=dict(schema='sys-init-native-init-v1',result='running',summary_sha256=args.summary_pin,cases=[],commands=[],native_profile='AENIN003' if args.init_composed else 'AENIN002' if args.init_large else 'AENIN001',smp=False,build_profile=BUILD_PROFILE+('-abi16' if args.init_composed else '-abi15' if args.init_large else ''))
    if worker_report:
        report.update(service_worker_sha256=worker_report['worker_sha256'],
                      service_worker_receipt_sha256=args.service_worker_pin)
    def save():(work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(argv,label):
        with (work/(label+'.log')).open('wb') as log:
            child=subprocess.Popen(argv,cwd=kernel,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=child.wait(timeout=180)
            except (subprocess.TimeoutExpired,KeyboardInterrupt) as error:
                os.killpg(child.pid,signal.SIGKILL);child.wait()
                report['commands'].append(dict(argv=argv,outcome=type(error).__name__));save();raise
        report['commands'].append(dict(argv=argv,exit=code));save()
        if code:raise RuntimeError('command failed: '+label)
    save()
    try:
        run([sys.executable,'-c','from scripts.deps import verify; verify()'],'dependencies')
        for tool,argv in [('rust',['rustc','+1.98.0','--version']),('zig',['zig','version']),('qemu',['qemu-system-x86_64','--version'])]:run(argv,tool)
        cases=[('policy',None,None,None,None),('adapter-edges','adapter_edges',None,None,None),
               ('adapter-bad-clean','bad_clean',None,'native C profile rejected','NATIVE supervisor result=831 reclaimed=0'),('wrong-deadline','bad_deadline',None,'native C profile rejected','NATIVE supervisor result=821 reclaimed=0'),
               ('late-admission','bad_late',None,'native C profile rejected','NATIVE supervisor result=822 reclaimed=0'),
               ('owner-exit','owner_exit',None,None,None),('owner-fault','owner_fault',None,None,None),
               ('skip-deadline',None,'native-init-skip-deadline','native C profile rejected','NATIVE supervisor result=821 reclaimed=0'),
               ('cleanup-no-zero','owner_exit','native-skip-zero','native init cleanup not zeroed','NATIVE init closing live=1 terminal=1 queued=2 wait=1')]
        cases += [('acquisition-cleanup','acquisition_cleanup',None,None,None),
                  ('acquisition-bad-writer','acquisition_bad_writer',None,'native C profile rejected','NATIVE supervisor result=951 reclaimed=0'),
                  ('acquisition-bad-wait','acquisition_bad_wait',None,'native C profile rejected','NATIVE supervisor result=953 reclaimed=1')]
        cases += [('attempt-retry','attempt_retry',None,None,None),
                  ('attempt-bad-writer','attempt_bad_writer',None,'native C profile rejected','NATIVE supervisor result=961 reclaimed=0'),
                  ('attempt-bad-guard','attempt_bad_guard',None,'native C profile rejected','NATIVE supervisor result=963 reclaimed=0')]
        cases += [('attempt-wait','attempt_wait',None,None,None),
                  ('attempt-wait-forget','attempt_wait_forget',None,'native C profile rejected','NATIVE supervisor result=971 reclaimed=0'),
                  ('attempt-wait-skip-release','attempt_wait_skip_release',None,'native C profile rejected','NATIVE supervisor result=973 reclaimed=1')]
        cases += [('attempt-deadline','attempt_deadline',None,None,None),
                  ('attempt-bad-precedence','attempt_bad_precedence',None,'native C profile rejected','NATIVE supervisor result=980 reclaimed=0'),
                  ('attempt-intent','attempt_intent',None,None,None),
                  ('attempt-bad-intent','attempt_bad_intent',None,'native C profile rejected','NATIVE supervisor result=981 reclaimed=1')]
        cases += [
            ('history-index','history_index',None,None,None),
            ('history-service','history_service',None,None,None),
            ('history-context','history_context',None,None,None),
            ('history-target','history_target',None,None,None),
            ('history-unsealed','history_unsealed',None,None,None),
            ('history-replay','history_replay',None,None,None),
            ('history-identity','history_identity',None,None,None),
            ('history-skip-token','history_skip_token',None,'native C profile rejected','NATIVE supervisor result=1050 reclaimed=0'),
            ('interrupt-empty','interrupt_empty',None,None,None),
            ('interrupt-after-first','interrupt_after_first',None,None,None),
            ('interrupt-after-status','interrupt_after_status',None,None,None),
            ('interrupt-skip-close','interrupt_skip_close',None,'native C profile rejected','NATIVE supervisor result=1046 reclaimed=0'),
            ('interrupt-forget-prefix','interrupt_forget_prefix',None,'native C profile rejected','NATIVE supervisor result=1047 reclaimed=0'),
            ('interrupt-invent-fact','interrupt_invent_fact',None,'native C profile rejected','NATIVE supervisor result=1048 reclaimed=0'),
            ('interrupt-forget-reader','interrupt_forget_reader',None,'native C profile rejected','NATIVE supervisor result=1049 reclaimed=0')]
        cases += [
            ('sample-bad-boolean','sample_bad_boolean',None,None,None),
            ('sample-bad-kind','sample_bad_kind',None,None,None),
            ('sample-bad-result','sample_bad_result',None,None,None),
            ('sample-bad-live','sample_bad_live',None,None,None),
            ('sample-bad-revision','sample_bad_revision',None,None,None),
            ('sample-bad-readiness','sample_bad_readiness',None,None,None),
            ('sample-skip-close','sample_skip_close',None,'native C profile rejected','NATIVE supervisor result=1043 reclaimed=0'),
            ('sample-forget-reader','sample_forget_reader',None,'native C profile rejected','NATIVE supervisor result=1044 reclaimed=0'),
            ('sample-invent-errno','sample_invent_errno',None,'native C profile rejected','NATIVE supervisor result=1045 reclaimed=0')]
        cases += [('raw-terminal','raw_terminal',None,None,None),
                  ('raw-first-stale','raw_first_stale',None,None,None),
                  ('raw-status-stale','raw_status_stale',None,None,None),
                  ('raw-observe-stale','raw_observe_stale',None,None,None),
                  ('raw-forget-prefix','raw_forget_prefix',None,'native C profile rejected','NATIVE supervisor result=1042 reclaimed=1'),
                  ('sampling-preflight','sampling_preflight',None,None,None),
                  ('sampling-target','sampling_target',None,None,None),
                  ('sampling-held','sampling_held',None,None,None),
                  ('sampling-stale','sampling_stale',None,None,None),
                  ('sampling-status-stale','sampling_status_stale',None,None,None),
                  ('sampling-observe-stale','sampling_observe_stale',None,None,None),
                  ('sampling-skip-token','sampling_skip_token',None,'native C profile rejected','NATIVE supervisor result=1040 reclaimed=0'),
                  ('sampling-skip-pending','sampling_skip_pending',None,'native C profile rejected','NATIVE supervisor result=1039 reclaimed=0')]
        cases += [('missing-channel','missing_channel',None,None,None),
                  ('missing-launch','missing_launch',None,None,None),
                  ('missing-skip-close','missing_skip_close',None,'native C profile rejected','NATIVE supervisor result=1033 reclaimed=0'),
                  ('missing-invent-error','missing_invent_error',None,'native C profile rejected','NATIVE supervisor result=1034 reclaimed=0'),
                  ('missing-forget-writer','missing_forget_writer',None,'native C profile rejected','NATIVE supervisor result=1035 reclaimed=0')]
        cases += [('launch-receipt','launch_receipt',None,None,None),
                  ('launch-receipt-close','launch_receipt_close',None,None,None),
                  ('launch-keep-writer','launch_keep_writer',None,'native C profile rejected','NATIVE supervisor result=1030 reclaimed=0'),
                  ('launch-early-generation','launch_early_generation',None,'native C profile rejected','NATIVE supervisor result=1031 reclaimed=0')]
        cases += [('receipt-channel','receipt_channel',None,None,None),
                  ('receipt-identity','receipt_identity',None,None,None),
                  ('receipt-close','receipt_close',None,None,None),
                  ('receipt-skip-phase','receipt_skip_phase',None,'native C profile rejected','NATIVE supervisor result=1025 reclaimed=0'),
                  ('receipt-forget-writer','receipt_forget_writer',None,'native C profile rejected','NATIVE supervisor result=1026 reclaimed=0')]
        cases += [('generation-exhaustion','generation_exhaustion',None,None,None),
                  ('generation-skip-guard','generation_skip_guard',None,'native C profile rejected','NATIVE supervisor result=1023 reclaimed=3'),
                  ('generation-consume-denied','generation_consume_denied',None,'native C profile rejected','NATIVE supervisor result=1024 reclaimed=3')]
        cases += [('expected-target','expected_target',None,None,None),
                  ('target-mismatch','target_mismatch',None,None,None),
                  ('target-wrong-generation','target_wrong_generation',None,None,None),
                  ('target-skip-match','target_skip_match',None,'native C profile rejected','NATIVE supervisor result=1021 reclaimed=0'),
                  ('target-forget-worker','target_forget_worker',None,'native C profile rejected','NATIVE supervisor result=1022 reclaimed=0')]
        cases += [('binding-creation-busy','binding_creation_busy',None,None,None),
                  ('binding-reopen-token','binding_reopen_token',None,'native C profile rejected','NATIVE supervisor result=1018 reclaimed=0'),
                  ('binding-launch-busy','binding_launch_busy',None,None,None),
                  ('binding-busy-forget','binding_busy_forget',None,'native C profile rejected','NATIVE supervisor result=1019 reclaimed=0')]
        cases += [('binding-failure','binding_failure',None,None,None),
                  ('binding-forget-writer','binding_forget_writer',None,'native C profile rejected','NATIVE supervisor result=1017 reclaimed=0')]
        cases += [('binding-preflight','binding_preflight',None,None,None),
                  ('binding-admission','binding_admission',None,None,None),
                  ('binding-skip-token','binding_skip_token',None,'native C profile rejected','NATIVE supervisor result=1014 reclaimed=0'),
                  ('binding-skip-pending','binding_skip_pending',None,'native C profile rejected','NATIVE supervisor result=1015 reclaimed=0')]
        cases += [('routed-partial-cleanup','routed_partial_cleanup',None,None,None),
                  ('route-cleanup-event','route_cleanup_event',None,'native C profile rejected','NATIVE supervisor result=1012 reclaimed=3'),
                  ('route-cleanup-forget','route_cleanup_forget',None,'native C profile rejected','NATIVE supervisor result=1013 reclaimed=3')]
        cases += [('routed-stop-error','routed_stop_error',None,None,None),
                  ('route-error-drop','route_error_drop',None,'native C profile rejected','NATIVE supervisor result=1009 reclaimed=3'),
                  ('route-error-swallow','route_error_swallow',None,'native C profile rejected','NATIVE supervisor result=1010 reclaimed=3')]
        cases += [('routed-live-stop','routed_live_stop',None,None,None),
                  ('route-stop-event','route_stop_event',None,'native C profile rejected','NATIVE supervisor result=1006 reclaimed=0'),
                  ('route-stop-ack','route_stop_ack',None,'native C profile rejected','NATIVE supervisor result=1007 reclaimed=0')]
        cases += [('routed-cancellation','routed_cancellation',None,None,None),
                  ('route-cancel-drop','route_cancel_drop',None,'native C profile rejected','NATIVE supervisor result=1005 reclaimed=0'),
                  ('route-cancel-reset','route_cancel_reset',None,'native C profile rejected','NATIVE supervisor result=1004 reclaimed=0')]
        cases += [('routed-replacement','routed_replacement',None,None,None),
                  ('replacement-events','replacement_events',None,None,None),
                  ('route-skip-delivery','route_skip_delivery',None,'native C profile rejected','NATIVE supervisor result=1001 reclaimed=0'),
                  ('route-old-generation','route_old_generation',None,'native C profile rejected','NATIVE supervisor result=1002 reclaimed=1')]
        cases += [('rejected-events','rejected_events',None,None,None),
                  ('event-wrong-error','event_wrong_error',None,'native C profile rejected','NATIVE supervisor result=997 reclaimed=0'),
                  ('event-failure-early','event_failure_early',None,'native C profile rejected','NATIVE supervisor result=998 reclaimed=0')]
        cases += [('native-events','native_events',None,None,None),
                  ('event-drop-busy','event_drop_busy',None,'native C profile rejected','NATIVE supervisor result=994 reclaimed=0'),
                  ('event-keep-launch','event_keep_launch',None,'native C profile rejected','NATIVE supervisor result=995 reclaimed=0')]
        cases += [('attempt-reader-error','attempt_reader_error',None,None,None),
                  ('attempt-reader-forget','attempt_reader_forget',None,'native C profile rejected','NATIVE supervisor result=992 reclaimed=2'),
                  ('attempt-release-error','attempt_release_error',None,None,None),
                  ('attempt-release-forget','attempt_release_forget',None,'native C profile rejected','NATIVE supervisor result=993 reclaimed=3')]
        cases += [('attempt-partial-cleanup','attempt_partial_cleanup',None,None,None),
                  ('attempt-partial-forget','attempt_partial_forget',None,'native C profile rejected','NATIVE supervisor result=990 reclaimed=0'),
                  ('attempt-stop-error','attempt_stop_error',None,None,None),
                  ('attempt-stop-forget','attempt_stop_forget',None,'native C profile rejected','NATIVE supervisor result=991 reclaimed=3')]
        cases += [('service-lifecycle','service_lifecycle',None,None,None)]
        for suffix, assertion, reclaimed in [('deadline',901,0),('terminal',902,0),('dependency',903,0),('generation',904,2)]:
            cases.append(('service-bad-'+suffix,'service_bad_'+suffix,None,'native C profile rejected',
                          'NATIVE supervisor result='+str(assertion)+' reclaimed='+str(reclaimed)))
        if service_worker:
            cases += [('terminal-fault-collision','terminal_fault_collision',None,None,None),
                      ('terminal-stop-collision','terminal_stop_collision',None,None,None),
                      ('terminal-live','terminal_live',None,None,None),
                      ('terminal-ignore-kind','terminal_ignore_kind',None,'native C profile rejected','NATIVE supervisor result=1036 reclaimed=0')]
            cases += [('service-return','service_return',None,None,None),
                      ('service-return-early','service_return_early',None,'native C profile rejected',
                       'NATIVE supervisor result=912 reclaimed=0'),
                      ('service-return-bad-dependency','service_return_bad_dependency',None,
                       'native C profile rejected','NATIVE supervisor result=915 reclaimed=0'),
                      ('service-silent','service_silent',None,'native C profile rejected',
                       'NATIVE supervisor result=920 reclaimed=0'),
                      ('service-malformed','service_malformed',None,'native C profile rejected',
                       'NATIVE supervisor result=921 reclaimed=0'),
                      ('service-retry-silent','service_retry_silent',None,None,None),
                      ('service-retry-malformed','service_retry_malformed',None,None,None),
                      ('service-retry-bad-cleanup','service_retry_bad_cleanup',None,
                       'native C profile rejected','NATIVE supervisor result=927 reclaimed=1'),
                      ('service-retry-no-fresh','service_retry_no_fresh',None,
                       'native C profile rejected','NATIVE supervisor result=929 reclaimed=1'),
                      ('service-budget-silent','service_budget_silent',None,None,None),
                      ('service-budget-malformed','service_budget_malformed',None,None,None),
                      ('service-budget-extra','service_budget_extra',None,
                       'native C profile rejected','NATIVE supervisor result=931 reclaimed=3'),
                      ('service-budget-short','service_budget_short',None,
                       'native C profile rejected','NATIVE supervisor result=934 reclaimed=2'),
                      ('service-cancel-retry','service_cancel_retry',None,None,None),
                      ('service-cancel-ready','service_cancel_ready',None,None,None),
                      ('service-cancel-bad-retry','service_cancel_bad_retry',None,
                       'native C profile rejected','NATIVE supervisor result=936 reclaimed=1'),
                      ('service-cancel-bad-ready','service_cancel_bad_ready',None,
                       'native C profile rejected','NATIVE supervisor result=937 reclaimed=0'),
                      ('service-loss-stop','service_loss_stop',None,None,None),
                      ('service-loss-return','service_loss_return',None,None,None),
                      ('service-loss-bad-stop','service_loss_bad_stop',None,
                       'native C profile rejected','NATIVE supervisor result=940 reclaimed=0'),
                      ('service-loss-bad-admission','service_loss_bad_admission',None,
                       'native C profile rejected','NATIVE supervisor result=941 reclaimed=0')]
        if expanded:
            cases += [('guard-resources','guard_resources',None,None,None),
                      ('guard-conflict','guard_conflict',None,None,None),
                      ('guard-skip-close','guard_skip_close',None,'native C profile rejected','NATIVE supervisor result=1053 reclaimed=0'),
                      ('guard-forget-reader','guard_forget_reader',None,'native C profile rejected','NATIVE supervisor result=1054 reclaimed=0'),
                      ('conflict-overwrite-primary','conflict_overwrite_primary',None,'native C profile rejected','NATIVE supervisor result=1052 reclaimed=0')]
        if expanded:
            cases += [('guard-denial-unsealed','guard_denial_unsealed',None,None,None),
                      ('guard-denial-occupied','guard_denial_occupied',None,None,None),
                      ('guard-denial-forget-reader','guard_denial_forget_reader',None,'native C profile rejected','NATIVE supervisor result=1055 reclaimed=0'),
                      ('guard-denial-clear-spare','guard_denial_clear_spare',None,'native C profile rejected','NATIVE supervisor result=1056 reclaimed=0'),
                      ('guard-reoffer','guard_reoffer',None,None,None),
                      ('guard-reoffer-produce','guard_reoffer_produce',None,'native C profile rejected','NATIVE supervisor result=1057 reclaimed=0')]
        if expanded:
            cases += [('history-capacity','history_capacity',None,None,None),
                      ('capacity-forget-live','capacity_forget_live',None,'native C profile rejected','NATIVE supervisor result=1058 reclaimed=0'),
                      ('capacity-recycle-primary','capacity_recycle_primary',None,'native C profile rejected','NATIVE supervisor result=1059 reclaimed=0'),
                      ('capacity-recycle-diagnostic','capacity_recycle_diagnostic',None,'native C profile rejected','NATIVE supervisor result=1060 reclaimed=0')]
        if expanded:
            cases += [('seal-live', 'seal_live', None, None, None), ('seal-partial-one', 'seal_partial_one', None, None, None), ('seal-partial-two', 'seal_partial_two', None, None, None), ('seal-failed', 'seal_failed', None, None, None), ('seal-interrupt-one', 'seal_interrupt_one', None, None, None), ('seal-interrupt-two', 'seal_interrupt_two', None, None, None), ('seal-promote', 'seal_promote', None, 'native C profile rejected', 'NATIVE supervisor result=1061 reclaimed=0'), ('seal-forget-sample', 'seal_forget_sample', None, 'native C profile rejected', 'NATIVE supervisor result=1062 reclaimed=0'), ('seal-forget-reader', 'seal_forget_reader', None, 'native C profile rejected', 'NATIVE supervisor result=1063 reclaimed=0')]
        if expanded:
            cases += [('history-errno-first','history_errno_first',None,None,None),
                      ('history-errno-middle','history_errno_middle',None,None,None),
                      ('history-errno-last','history_errno_last',None,None,None),
                      ('history-errno-forget','history_errno_forget',None,'native C profile rejected','NATIVE supervisor result=1065 reclaimed=1'),
                      ('history-errno-error','history_errno_error',None,'native C profile rejected','NATIVE supervisor result=1066 reclaimed=1')]
        if expanded:
            cases += [('history-closed', 'history_closed', None, None, None), ('closed-forget-primary', 'closed_forget_primary', None, 'native C profile rejected', 'NATIVE supervisor result=1067 reclaimed=0'), ('closed-forget-diagnostic', 'closed_forget_diagnostic', None, 'native C profile rejected', 'NATIVE supervisor result=1068 reclaimed=0'), ('closed-reopen', 'closed_reopen', None, 'native C profile rejected', 'NATIVE supervisor result=1069 reclaimed=0'), ('closed-clear-pending', 'closed_clear_pending', None, 'native C profile rejected', 'NATIVE supervisor result=1070 reclaimed=0')]
            cases += [('composed-history', 'composed_history', None, None, None), ('composed-skip-launch', 'composed_skip_launch', None, 'native C profile rejected', 'NATIVE supervisor result=1071 reclaimed=0'), ('composed-keep-writer', 'composed_keep_writer', None, 'native C profile rejected', 'NATIVE supervisor result=1072 reclaimed=0'), ('composed-forget-reader', 'composed_forget_reader', None, 'native C profile rejected', 'NATIVE supervisor result=1073 reclaimed=0'), ('composed-skip-token', 'composed_skip_token', None, 'native C profile rejected', 'NATIVE supervisor result=1074 reclaimed=0')]
            cases += [('bound-reservation', 'bound_reservation', None, None, None), ('bound-skip-owner', 'bound_skip_owner', None, 'native C profile rejected', 'NATIVE supervisor result=1075 reclaimed=0'), ('bound-skip-qualification', 'bound_skip_qualification', None, 'native C profile rejected', 'NATIVE supervisor result=1076 reclaimed=0'), ('bound-skip-token', 'bound_skip_token', None, 'native C profile rejected', 'NATIVE supervisor result=1077 reclaimed=0')]
            cases += [('native-application', 'native_application', None, None, None), ('application-skip-transition', 'application_skip_transition', None, 'native C profile rejected', 'NATIVE supervisor result=1078 reclaimed=0'), ('application-drop-capture', 'application_drop_capture', None, 'native C profile rejected', 'NATIVE supervisor result=1079 reclaimed=0'), ('application-corrupt-capture', 'application_corrupt_capture', None, 'native C profile rejected', 'NATIVE supervisor result=1080 reclaimed=0')]
            cases += [('generated-launch', 'generated_launch', None, None, None), ('effect-skip-token', 'effect_skip_token', None, 'native C profile rejected', 'NATIVE supervisor result=1083 reclaimed=0'), ('effect-early-ack', 'effect_early_ack', None, 'native C profile rejected', 'NATIVE supervisor result=1084 reclaimed=0'), ('effect-keep-writer', 'effect_keep_writer', None, 'native C profile rejected', 'NATIVE supervisor result=1085 reclaimed=0'), ('effect-busy', 'effect_busy', None, 'native C profile rejected', 'NATIVE supervisor result=1086 reclaimed=0')]
            cases += [('dependent-launch', 'dependent_launch', None, None, None), ('retire-skip-retain', 'retire_skip_retain', None, 'native C profile rejected', 'NATIVE supervisor result=1088 reclaimed=0'), ('retire-skip-ack', 'retire_skip_ack', None, 'native C profile rejected', 'NATIVE supervisor result=1089 reclaimed=0'), ('retire-forget-count', 'retire_forget_count', None, 'native C profile rejected', 'NATIVE supervisor result=1090 reclaimed=0'), ('dependent-skip-source', 'dependent_skip_source', None, 'native C profile rejected', 'NATIVE supervisor result=1091 reclaimed=0')]
        if args.init_composed:
            cases += [('native-terminal-application','native_terminal_application',None,None,None)]
            cases += [(name,cfg,None,'native C profile rejected',f'NATIVE supervisor result={status} reclaimed=0') for name,cfg,status in
                      [('native-terminal-owner','terminal_skip_owner',1094),('native-terminal-seal','terminal_skip_seal',1095),
                       ('native-terminal-missing','terminal_drop_capture',1096),('native-terminal-corrupt','terminal_corrupt_capture',1097),
                       ('native-terminal-interrupt','terminal_source_interrupt',1098)]]
        if args.init_composed:
            cases += [('native-issued-reclaim','native_issued_reclaim',None,None,None)]
            cases += [(name,cfg,None,'native C profile rejected',f'NATIVE supervisor result={status} reclaimed={count}') for name,cfg,status,count in [('reclaim-skip-token', 'reclaim_skip_token', 1100, 0), ('reclaim-early-ack', 'reclaim_early_ack', 1101, 0), ('reclaim-keep-reader', 'reclaim_keep_reader', 1102, 0), ('reclaim-keep-worker', 'reclaim_keep_worker', 1103, 1), ('reclaim-close-error', 'reclaim_close_error', 1104, 0), ('reclaim-worker-error', 'reclaim_worker_error', 1105, 1)]]
        if args.init_composed:
            cases += [('native-cleaned','native_cleaned',None,None,None),('cleaned-skip-resources','cleaned_skip_resources',None,'native C profile rejected','NATIVE supervisor result=1108 reclaimed=1'),('cleaned-skip-transition','cleaned_skip_transition',None,'native C profile rejected','NATIVE supervisor result=1109 reclaimed=1')]
        if args.init_composed:
            cases += [('native-pair-teardown','native_pair_teardown',None,None,None)]
            cases += [(n,c,None,'native C profile rejected',f'NATIVE supervisor result={v} reclaimed=1') for n,c,v in [('provider-skip-owner','provider_skip_owner',1111),('provider-skip-seal','provider_skip_seal',1112),('provider-interrupt','provider_interrupt',1113)]]
        if args.init_composed and service_worker:
            cases += [('simple-owner','simple_owner',None,None,None),('owner-launch-denial','owner_launch_denial',None,None,None),('owner-close-error','owner_close_error',None,'native C profile rejected','NATIVE supervisor result=1122 reclaimed=0')]
        if args.init_composed and service_worker:
            cases += [('simple-pair','simple_pair',None,None,None),('pair-provider-loss','pair_provider_loss',None,None,None),('pair-stop-error','pair_stop_error',None,'native C profile rejected','NATIVE supervisor result=1132 reclaimed=1'),('pair-cleanup-error','pair_cleanup_error',None,'native C profile rejected','NATIVE supervisor result=1133 reclaimed=1')]
        for name,cfg,flag,panic,context in cases:
            out=work/'cases'/name;out.mkdir(parents=True)
            argv=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none',*compiler_profile(client/'prototypes/native-supervisor'),
                  '-C','link-arg=-T'+str(client/'prototypes/native-supervisor'/('init-composed.ld' if args.init_composed else 'init-large.ld' if args.init_large else 'init.ld')),'-C','link-arg=--oformat=binary',
                  *['--check-cfg=cfg('+c+')' for c in ['bad_deadline','bad_late','owner_exit','owner_fault','adapter_edges','bad_clean','service_lifecycle','service_bad_deadline','service_bad_terminal','service_bad_dependency','service_bad_generation','service_return','service_return_early','service_return_bad_dependency','service_silent','service_malformed','service_retry_silent','service_retry_malformed','service_retry_bad_cleanup','service_retry_no_fresh']],
                  str(client/'prototypes/native-supervisor/init.rs'),'-o',str(out/'supervisor.raw')]
            argv+=['--check-cfg=cfg('+c+')' for c in ('dependent_launch','retire_skip_retain','retire_skip_ack','retire_forget_count','dependent_skip_source','generated_launch','effect_skip_token','effect_early_ack','effect_keep_writer','effect_busy','native_application','application_skip_transition','application_drop_capture','application_corrupt_capture','bound_reservation','bound_skip_owner','bound_skip_qualification','bound_skip_token','composed_history','composed_skip_launch','composed_keep_writer','composed_forget_reader','composed_skip_token','history_closed','closed_forget_primary','closed_forget_diagnostic','closed_reopen','closed_clear_pending','history_errno_first','history_errno_middle','history_errno_last','history_errno_forget','history_errno_error','seal_live','seal_partial_one','seal_partial_two','seal_failed','seal_interrupt_one','seal_interrupt_two','seal_promote','seal_forget_sample','seal_forget_reader','history_capacity','capacity_forget_live','capacity_recycle_primary','capacity_recycle_diagnostic','guard_denial_unsealed','guard_denial_occupied','guard_denial_forget_reader','guard_denial_clear_spare','guard_reoffer','guard_reoffer_produce','init_large','guard_resources','guard_conflict','guard_skip_close','guard_forget_reader','conflict_overwrite_primary')]
            argv += ['--check-cfg=cfg('+c+')' for c in ('simple_pair','pair_provider_loss','pair_stop_error','pair_cleanup_error','simple_owner','owner_launch_denial','owner_close_error','native_pair_teardown','provider_skip_owner','provider_skip_seal','provider_interrupt','native_cleaned','cleaned_skip_resources','cleaned_skip_transition','native_issued_reclaim', 'reclaim_skip_token', 'reclaim_early_ack', 'reclaim_keep_reader', 'reclaim_keep_worker', 'reclaim_close_error', 'reclaim_worker_error','init_composed','native_terminal_application','terminal_skip_owner','terminal_skip_seal','terminal_drop_capture','terminal_corrupt_capture','terminal_source_interrupt')]
            if args.init_composed:argv+=['--cfg','init_composed']
            if args.init_large:argv+=['--cfg','init_large']
            if cfg:argv+=['--cfg',cfg]
            if cfg in ('native_pair_teardown','provider_skip_owner','provider_skip_seal','provider_interrupt','native_cleaned','cleaned_skip_resources','cleaned_skip_transition'):
                argv += ['-C','lto=fat','-C','codegen-units=1']
            argv += ['--check-cfg=cfg('+c+')' for c in
                     ('history_index','history_service','history_context','history_target','history_unsealed','history_replay','history_identity','history_skip_token','interrupt_empty','interrupt_after_first','interrupt_after_status','interrupt_skip_close','interrupt_forget_prefix','interrupt_invent_fact','interrupt_forget_reader','sample_bad_boolean','sample_bad_kind','sample_bad_result','sample_bad_live','sample_bad_revision','sample_bad_readiness','sample_skip_close','sample_forget_reader','sample_invent_errno','sampling_status_stale','sampling_observe_stale','raw_terminal','raw_first_stale','raw_status_stale','raw_observe_stale','raw_forget_prefix','sampling_preflight','sampling_target','sampling_held','sampling_stale','sampling_skip_token','sampling_skip_pending','terminal_fault_collision','terminal_stop_collision','terminal_live','terminal_ignore_kind','missing_channel','missing_launch','missing_skip_close','missing_invent_error','missing_forget_writer','launch_receipt','launch_receipt_close','launch_keep_writer','launch_early_generation','receipt_channel','receipt_identity','receipt_close','receipt_skip_phase','receipt_forget_writer','generation_exhaustion','generation_skip_guard','generation_consume_denied','expected_target','target_mismatch','target_wrong_generation','target_skip_match','target_forget_worker','binding_creation_busy','binding_reopen_token','binding_launch_busy','binding_busy_forget','binding_failure','binding_forget_writer','binding_preflight','binding_admission','binding_skip_token','binding_skip_pending','routed_partial_cleanup','route_cleanup_event','route_cleanup_forget','routed_stop_error','route_error_drop','route_error_swallow','routed_live_stop','route_stop_event','route_stop_ack','routed_cancellation','route_cancel_drop','route_cancel_reset','routed_replacement','replacement_events','route_skip_delivery','route_old_generation','rejected_events','event_wrong_error','event_failure_early','native_events','event_drop_busy','event_keep_launch','attempt_reader_error','attempt_reader_forget','attempt_release_error','attempt_release_forget','attempt_partial_cleanup','attempt_partial_forget','attempt_stop_error','attempt_stop_forget','attempt_deadline','attempt_bad_precedence','attempt_intent','attempt_bad_intent','attempt_wait','attempt_wait_forget','attempt_wait_skip_release','attempt_retry','attempt_bad_writer','attempt_bad_guard','acquisition_cleanup','acquisition_bad_writer','acquisition_bad_wait','service_budget_silent','service_budget_malformed','service_budget_extra','service_budget_short',
                      'service_cancel_retry','service_cancel_ready','service_cancel_bad_retry','service_cancel_bad_ready',
                      'service_loss_stop','service_loss_return','service_loss_bad_stop','service_loss_bad_admission')]
            run(argv,name+'-client');code=(out/'supervisor.raw').read_bytes()
            if not 0<len(code)<=(16384 if args.init_composed else 8192 if args.init_large else 4096):raise ValueError('supervisor code bound')
            custom_worker=name.startswith(('seal-','history-capacity','capacity-','terminal-','service-return','service-retry','service-budget','service-cancel','service-loss')) or name in ('service-silent','service-malformed','simple-owner','owner-launch-denial','owner-close-error','simple-pair','pair-provider-loss','pair-stop-error','pair-cleanup-error')
            first_image=(inputs/'service-worker.elf').read_bytes() if custom_worker else prefix[56:56+first]
            entropy=prefix[24:56]
            second_image=prefix[56+first:56+first+second]
            (out/'native-c.bin').write_bytes(struct.pack('<8sIIII',b'AENIN003' if args.init_composed else b'AENIN002' if args.init_large else b'AENIN001',len(first_image),second,len(code),0)+entropy+first_image+second_image+code)
            argv=['zig','build','-Dsmp=false','-Dnative-c-image='+str(out/'native-c.bin'),'-p',str(out),'--cache-dir',str(kernel/'.zig-cache'),'--global-cache-dir',str(kernel/'.zig-cache/global')]
            if flag:argv+=['-D'+flag+'=true']
            run(argv,name+'-build')
            marker='AETHER NATIVE INIT CLOSED' if name in ('owner-exit','owner-fault') else 'AETHER NATIVE INIT PASS'
            if args.init_composed:marker=marker.replace('INIT ', 'INIT COMPOSED ')
            elif args.init_large:marker=marker.replace('INIT ', 'INIT LARGE ')
            invocation='import sys; sys.path.insert(0,"scripts"); from native_smoke import run; run('+repr(str(out/'aether.iso'))+',expected_panic='+repr(panic.encode() if panic else None)+',panic_context='+repr((context.encode(),) if context else ())+',marker='+repr(marker.encode())+')'
            run([sys.executable,'-c',invocation],name+'-smoke')
            lines=(out/'native-serial.log').read_text().splitlines()
            if name in ('sampling-status-stale','sampling-observe-stale','raw-terminal','raw-first-stale','raw-status-stale','raw-observe-stale','sampling-preflight','sampling-target','sampling-held','sampling-stale','terminal-fault-collision','terminal-stop-collision','terminal-live','missing-channel','missing-launch','launch-receipt','launch-receipt-close','receipt-channel','receipt-identity','receipt-close','generation-exhaustion','expected-target','target-mismatch','target-wrong-generation','binding-creation-busy','binding-launch-busy','binding-failure','binding-preflight','binding-admission','policy','adapter-edges','acquisition-cleanup','attempt-retry','attempt-wait','attempt-deadline','attempt-intent','attempt-partial-cleanup','attempt-stop-error','attempt-reader-error','attempt-release-error','native-events','rejected-events','routed-replacement','replacement-events','routed-cancellation','routed-live-stop','routed-stop-error','routed-partial-cleanup','service-lifecycle','service-return','service-retry-silent','service-retry-malformed','service-budget-silent','service-budget-malformed','service-cancel-retry','service-cancel-ready') and 'NATIVE supervisor result=100 reclaimed=3' not in lines:raise ValueError('policy completion missing')
            if name in ('native-pair-teardown','simple-owner','owner-launch-denial','simple-pair','pair-provider-loss') and 'NATIVE supervisor result=100 reclaimed=3' not in lines:raise ValueError('pair teardown completion missing')
            if name in ('native-cleaned','native-issued-reclaim','native-terminal-application','dependent-launch','generated-launch','native-application','bound-reservation','composed-history','history-closed','history-errno-first','history-errno-middle','history-errno-last','seal-live','seal-partial-one','seal-partial-two','seal-failed','seal-interrupt-one','seal-interrupt-two','history-capacity','guard-denial-unsealed','guard-denial-occupied','guard-reoffer','guard-resources','guard-conflict','history-index','history-service','history-context','history-target','history-unsealed','history-replay','history-identity','interrupt-empty','interrupt-after-first','interrupt-after-status') and 'NATIVE supervisor result=100 reclaimed=3' not in lines:raise ValueError('interrupted sample completion missing')
            if name.startswith('sample-bad-') and 'NATIVE supervisor result=100 reclaimed=3' not in lines:raise ValueError('malformed sample completion missing')
            if name in ('owner-exit','owner-fault') and 'NATIVE init closing live=1 terminal=1 queued=2 wait=1' not in lines:raise ValueError('shutdown preconditions missing')
            if panic and any(m in lines for m in ('AETHER NATIVE INIT CLOSED','AETHER NATIVE INIT PASS','AETHER NATIVE INIT LARGE CLOSED','AETHER NATIVE INIT LARGE PASS','AETHER NATIVE INIT COMPOSED CLOSED','AETHER NATIVE INIT COMPOSED PASS')):raise ValueError('negative falsely completed')
            report['cases'].append(dict(name=name,result='pass',expected_panic=panic,context=context,marker=marker if not panic else None,
                serial_sha256=sha(out/'native-serial.log'),envelope_sha256=sha(out/'native-c.bin'),supervisor_sha256=sha(out/'supervisor.raw'),iso_sha256=sha(out/'aether.iso')))
            save();print('[OK] '+name,file=sys.stderr,flush=True)
        if any(sha(work/name)!=pin for name,pin in pins.items()):raise ValueError('frozen input changed')
        report.update(result='pass',sources_unchanged=True)
    except BaseException as error:
        report.update(result='interrupted' if isinstance(error,KeyboardInterrupt) else 'fail',error=str(error));raise
    finally:save()
    print(json.dumps(dict(result=report['result'],report=str(work/'results.json'))))
if __name__=='__main__':main()
