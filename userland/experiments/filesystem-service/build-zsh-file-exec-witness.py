# SPDX-License-Identifier: BSD-2-Clause
"""Build/check the fixed #148 startup/READY witness, never an image or guest.

From the system root, run this script with explicit installed pinned tool paths,
--work NEW_DIRECTORY and --report JSON. The work directory retains the needed ELF
and inspection inputs until the lead disposes them; the report is compact evidence.
Uses the existing bounded_capture worker (300s aggregate,180s child,4MiB capture).
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('rustc', 'lld', 'objcopy', 'objdump', 'readelf', 'zig', 'work', 'report'):
        parser.add_argument('--'+name, required=True, type=Path)
    parser.add_argument('--reuse-host-report', type=Path)
    args = parser.parse_args()
    work, report_path = args.work.resolve(), args.report.resolve()
    work.mkdir(parents=True, exist_ok=False)
    (work/'tmp').mkdir()
    spec = importlib.util.spec_from_file_location('witness_capture', ROOT/'sys-init/scripts/bounded_capture.py')
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)
    sources = [Path(__file__).resolve(), HERE/'zsh-file-exec-witness.rs',
        HERE/'zsh-file-exec-witness.ld', ROOT/'sys-init/scripts/bounded_capture.py',
        ROOT/'sys-init/prototypes/native-filesystem-session/startup.rs',
        ROOT/'sys-init/prototypes/native-filesystem-session/zsh_process_frames.rs',
        ROOT/'kernel/native_elf.zig']
    before = {str(path): digest(path) for path in sources}
    started = time.monotonic()
    deadline = started + 300
    report = dict(issue=148, work=str(work), status='building', commands=[],
        native_executed=False, sources_before=before,
        limits=dict(aggregate_seconds=300, child_seconds=180, capture_bytes=4194304,
                    file_bytes=16777216, complete_elf_bytes=4096))
    environment = dict(PATH='/usr/bin:/bin', LC_ALL='C', TMPDIR=str(work/'tmp'))

    def save():
        report['elapsed_seconds'] = time.monotonic() - started
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2)+'\n')

    def run(label, command):
        remaining = deadline - time.monotonic()
        require(remaining > 10, 'aggregate deadline before '+label)
        row = dict(label=label, argv=list(map(str, command)))
        report['commands'].append(row)
        save()
        with capture.OwnedTemporaryDirectory(prefix='capture-', dir=work/'tmp') as owner:
            result = capture.run_capture_bytes(row['argv'], cwd=work, env=environment,
                timeout=min(180, remaining-10), deadline=deadline, limit=4194304,
                file_limit=16777216, owner=owner, record_path=owner.name+'/child.process.json')
            row.update(exit=result.returncode, process=result.record,
                stdout_tail=result.stdout.decode(errors='replace')[-1500:],
                stderr_tail=result.stderr.decode(errors='replace')[-2500:])
            save()
            require(result.record.get('cleanup') == 'complete'
                and result.record.get('group_absent') and result.record.get('stdout_eof')
                and result.record.get('stderr_eof'), label+': unknown cleanup')
            require(result.returncode == 0, label+': '+row['stderr_tail'])
            return result.stdout

    try:
        report['tools'] = {name: dict(path=str(getattr(args,name).resolve()),
            sha256=digest(getattr(args,name).resolve()))
            for name in ('rustc','lld','objcopy','objdump','readelf','zig')}
        report['rust_version'] = run('rust-version', [args.rustc,'--version']).decode().strip()
        common = ['--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn']
        source = HERE/'zsh-file-exec-witness.rs'
        # Compile the reused codec without cfg(test), so this witness's focused
        # tests do not pull the codec's separate producer-test dependency graph.
        host_frames = work/'host-frames.rs'
        startup = ROOT/'sys-init/prototypes/native-filesystem-session/startup.rs'
        frames = ROOT/'sys-init/prototypes/native-filesystem-session/zsh_process_frames.rs'
        host_frames.write_text('#![no_std]\nextern crate self as abi29_dispatch_core;\n'
            +'#[path='+json.dumps(str(startup))+'] pub mod startup;\n'
            +'#[allow(dead_code)] #[path='+json.dumps(str(frames))+'] mod implementation;\n'
            +'pub use implementation::{snapshot,Expected};\n')
        report['host_fixture_sha256'] = digest(host_frames)
        if args.reuse_host_report is not None:
            old = json.loads(args.reuse_host_report.read_text())
            for path in (source,startup,frames):
                require(old['sources_before'][str(path)] == digest(path)
                    and str(path) not in old['source_drift'], 'host reuse input agreement')
            require(old['tools']['rustc'] == report['tools']['rustc'], 'host compiler unchanged')
            rows = {row['label']:row for row in old['commands']}
            require(all(rows[name]['exit']==0 and rows[name]['process']['cleanup']=='complete'
                for name in ('host-codec-build','host-test-build','host-tests')), 'actual passing host cohort')
            report['reused_host_checks'] = dict(report=str(args.reuse_host_report.resolve()),
                sha256=digest(args.reuse_host_report), labels=['host-codec-build','host-test-build','host-tests'])
        else:
            run('host-codec-build', [args.rustc,*common,'--crate-type=rlib',
                '--crate-name=file_exec_frames',host_frames,'-o',work/'libfile_exec_frames.rlib'])
            run('host-test-build', [args.rustc,*common,'--test',source,
                '--extern','file_exec_frames='+str(work/'libfile_exec_frames.rlib'),
                '-o',work/'witness-tests'])
            run('host-tests', [work/'witness-tests'])
        run('target-build', [args.rustc,*common,'--target=x86_64-unknown-none',
            '-Cpanic=abort','-Copt-level=z','-Crelocation-model=static',
            '-Ccodegen-units=1','-Cjump-tables=no','-Clto=fat','-Cembed-bitcode=yes',
            '-Clinker='+str(args.lld),
            '-Clink-arg=-T'+str(HERE/'zsh-file-exec-witness.ld'),
            '-Clink-arg=--gc-sections','-Clink-arg=--build-id=none',
            '-Clink-arg=-Map='+str(work/'witness.map'),
            '--emit=link='+str(work/'witness.symbols.elf')+',asm='+str(work/'witness.s')
            +',dep-info='+str(work/'witness.d'),source])
        # This standard ELF strip retains all program/loaded bytes and removes
        # section-table metadata. The resulting complete ELF, not a flat image,
        # is the exact file provisioned and parsed by the kernel.
        run('strip-sections', [args.objcopy,'--strip-sections',
            work/'witness.symbols.elf',work/'witness.elf'])
        raw = (work/'witness.elf').read_bytes()
        original = (work/'witness.symbols.elf').read_bytes()
        require(64 <= len(raw) <= 4096, 'complete witness ELF<=4096')
        phoff = struct.unpack_from('<Q',raw,32)[0]
        phnum = struct.unpack_from('<H',raw,56)[0]
        headers = [struct.unpack_from('<IIQQQQQQ',raw,phoff+i*56) for i in range(phnum)]
        require(phnum == 4 and [h[0] for h in headers] == [6,1,7,0x6474e551], 'exact PHDR/LOAD/TLS/NX-stack')
        require(raw[phoff:phoff+phnum*56] == original[phoff:phoff+phnum*56], 'strip preserves program headers')
        load, tls = headers[1:3]
        require(load[1] == 5 and load[3] == 0x200000 and load[2] == 0
            and load[5] == load[6] and load[5] <= len(raw), 'one immutable load')
        # Header section metadata may change; all runtime instruction/data bytes
        # from the end of the program table through the load remain identical.
        bound = phoff+phnum*56
        require(raw[bound:load[5]] == original[bound:load[5]], 'strip preserves loaded code/data')
        require(tls[1] == 4 and tls[5:7] == (4,4)
            and raw[tls[2]:tls[2]+4] == b'\x01\x00\x00\x00', 'initialized readonly TLS')
        report['elf'] = dict(path=str(work/'witness.elf'),sha256=digest(work/'witness.elf'),
            file_bytes=len(raw),entry=struct.unpack_from('<Q',raw,24)[0],
            programs=headers,application_backing_pages=17,initialized_tls_hex='01000000',
            symbols_path=str(work/'witness.symbols.elf'),symbols_sha256=digest(work/'witness.symbols.elf'))
        assembly = run('disassembly', [args.objdump,'-d','--no-show-raw-insn',
            '--x86-asm-syntax=intel',work/'witness.symbols.elf'])
        (work/'witness.disassembly').write_bytes(assembly)
        run('elf-observation', [args.readelf,'-h','-l','-S',work/'witness.elf'])
        (work/'parser-test.zig').write_text('const e=@import("elf"); test "actual filesystem witness" { const raw=@embedFile("witness.elf"); _=try e.parseApplication(raw); }\n')
        run('actual-kernel-parser', [args.zig,'test','--dep','elf',
            '-Mroot='+str(work/'parser-test.zig'),'-Melf='+str(ROOT/'kernel/native_elf.zig'),
            '--cache-dir',work/'zig-cache','--global-cache-dir',work/'zig-global'])
        report['status'] = 'built-runtime-unqualified'
    except BaseException as error:
        report.update(status='failed', error=type(error).__name__+': '+str(error))
        if hasattr(error,'record'):
            report['failed_process'] = error.record
    finally:
        report['source_drift'] = [p for p,h in before.items() if not Path(p).is_file() or digest(p)!=h]
        if report['source_drift']:
            report.update(status='failed',error='frozen source drift')
        save()
    print(json.dumps(dict(status=report['status'],work=str(work),report=str(report_path),
        error=report.get('error'))))
    return 0 if report['status']=='built-runtime-unqualified' else 1


if __name__ == '__main__':
    raise SystemExit(main())
