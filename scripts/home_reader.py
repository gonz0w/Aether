# SPDX-License-Identifier: BSD-2-Clause
"""Bounded AF09 read-only reconstruction; no guest execution or old-source edits.

The original startup and fresh recovery importer keep their lifecycle. The
healthy generation buffers its original32 observations, validates completion,
then publishes the independent oracle's entire32-byte metadata digest. Denied
replacement generations retain their B/N/R observations after clean retirement.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / 'user/storage/service-runtime'
VOLUME = ROOT / 'user/storage/openzfs-volume'
UTC_MIN = 1791290040
UTC_MAX = 1791290100
RTC = '2026-10-06T12:34:00,clock=vm'
PHASES = b'BIUVWLP????????OAMT????????SDJFR'


def replace(text, old, new, *, count=1):
    if text.count(old) != count:
        raise ValueError('AF09 reader missing/duplicate source anchor: '+old[:80])
    return text.replace(old, new)


def role(recovered):
    if type(recovered) is not bool:
        raise ValueError('AF09 reader requires explicit pristine/recovery boolean')
    return int(recovered)


def render_observer(original):
    """Buffer the unchanged resource rows; retain the original finish/drain body."""
    start = 'static void engine_observe(unsigned char phase)\n{'
    prefix = '''static unsigned char home_reader_rows[32][8];
static unsigned home_reader_count;
unsigned char aether_home_reader_digest[32];
unsigned aether_home_reader_ready;

'''
    text = replace(original, start, prefix+start)
    begin = '    /* The admitted stdout operation is bounded, and short writes stay explicit.\n'
    end = '\n}\n\n#ifndef ENGINE_SKIP_FINISH'
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError('AF09 reader observer output/finish context changed')
    left = text.index(begin)
    right = text.index(end, left)
    text = text[:left]+'''    if (home_reader_count >= 32)
        _Exit(227);
    for (unsigned i = 0; i < 8; ++i)
        home_reader_rows[home_reader_count][i] = row[i];
    ++home_reader_count;'''+text[right:]
    return text


def render_startup(original, recovered):
    selected = role(recovered)
    text = replace(original, '#include "engine-observe.inc"', '#include "home-reader-observe.inc"')
    text = replace(text, 'int main(void)\n{', 'static int home_reader_run(void)\n{')
    # The wrapper deliberately repeats final checks: no successful lifecycle can
    # expose healthy bytes before TLS/status, phase and oracle checks all pass.
    return text+'''
/* AF09 private late publication. No stdout before every healthy check passes.
 * The existing numeric projection exposes one byte per eight-byte write. */
int main(void)
{
    const int recovered = '''+str(selected)+''';
    (void)recovered; /* Selection also binds the separately compiled importer. */
    int status = home_reader_run();
    if (status)
        return status;
    if (tls_marker != 17)
        return 223;
    if (aether_runtime_live() || !aether_runtime_admissions() ||
        aether_runtime_admissions() > 512)
        return 225;
    static const unsigned char phases[] = "BIUVWLP????????OAMT????????SDJFR";
    int denied = getauxval(0xa001) != 0x50000101UL;
    unsigned expected = denied ? 3 : sizeof(phases) - 1;
    if (home_reader_count != expected)
        return 228;
    for (unsigned i = 0; i < expected; ++i) {
        unsigned char phase = denied ? (unsigned char)"BNR"[i] : phases[i];
        if (phase != '?' && home_reader_rows[i][0] != phase)
            return 228;
    }
    if (!denied && !aether_home_reader_ready)
        return 229;
    if (denied && aether_home_reader_ready)
        return 229;
    for (unsigned i = 0; i < (denied ? 3U : 32U); ++i) {
        unsigned char row[8] = {0};
        if (denied) {
            for (unsigned j = 0; j < 8; ++j)
                row[j] = home_reader_rows[i][j];
        } else
            row[0] = aether_home_reader_digest[i];
        /* One complete bounded write per row, including zero digest bytes.
         * A short/failed write can never certify successful completion. */
        if (write(1, row, sizeof(row)) != (ssize_t)sizeof(row))
            return 227;
    }
    return 0;
}
'''


def render_importer(original, recovered):
    """Use the real fresh read-only import/close/evict path and explicit oracle."""
    selected = role(recovered)
    text = replace(original, 'extern int aether_pool_namespace_recover(spa_t *);',
        '#include "home-recovery-probe.h"\n'
        'extern unsigned char aether_home_reader_digest[32];\n'
        'extern unsigned aether_home_reader_ready;')
    text = replace(text, 'spa->spa_uberblock.ub_txg > 782',
                   'spa->spa_uberblock.ub_txg '+('> 782' if recovered else '== 782'))
    text = replace(text, '        error = aether_pool_namespace_recover(spa);',
        '        error = aether_home_readback(spa, '+str(selected)+',\n'
        '            UINT64_C('+str(UTC_MIN)+'), UINT64_C('+str(UTC_MAX)+'),\n'
        '            aether_home_reader_digest);\n'
        '        if (!error)\n'
        '            aether_home_reader_ready = 1;')
    return text


def render_spa(original, importer):
    """Expand just the prepared import include, preserving real SPA/provider code."""
    return replace(original, '#include "spa-import.inc"', importer)


def _recipe(preparation, name):
    from fs_launch import recipe
    return recipe(preparation, name)


def _compile(preparation, name, source, output, extra=()):
    recipe = _recipe(preparation, name)
    return recipe[:recipe.index('-c')]+list(map(str, extra))+['-c',str(source),'-o',str(output)]


def _relink(argv, replacements, output, mapping=None):
    for old in replacements:
        if argv.count(str(old)) != 1:
            raise ValueError('AF09 reader exact recipe input: '+str(old))
    if argv.count('-o') != 1 or argv.index('-o') != len(argv)-2:
        raise ValueError('AF09 reader exact output recipe')
    if mapping is not None and sum(arg.startswith('-Map=') for arg in argv) > 1:
        raise ValueError('AF09 reader exact map recipe')
    result=[]
    for arg in argv:
        result.append(str(replacements.get(arg, '-Map='+str(mapping)
            if mapping is not None and arg.startswith('-Map=') else arg)))
    result[-1]=str(output)
    if mapping is not None and not any(arg.startswith('-Map=') for arg in argv):
        result.insert(result.index('-o'), '-Map='+str(mapping))
    return result


def compose(base, preparation, work, destination, command, tools, record, recovered):
    """Compile/link actual prepared recovery objects into destination/reader.elf.

    Call only after metadata.prepare_engine(base,...,recovery=True). Caller owns
    fresh work/destination directories, frozen inputs, command recording/limits,
    notice retention, sealing and cleanup. command accepts (argv, log). This
    adapter executes no guest and neither changes old profiles nor copies SDKs.
    """
    selected=role(recovered)
    base=Path(base); work=Path(work); destination=Path(destination)
    port=base/'port'
    if preparation.get('old_service') is not None or preparation.get('recovery_empty') is not False:
        raise ValueError('AF09 reader requires actual normal prepared recovery objects')
    startup=SERVICE/'engine-startup.c'; observe=SERVICE/'engine-observe.inc'
    importer=VOLUME/'spa-zpl-recover.inc'
    source_inputs=(startup,observe,importer,VOLUME/'home-recovery-probe.c',
        VOLUME/'home-recovery-probe.h',VOLUME/'zpl-read.c',VOLUME/'zpl-read.h',
        VOLUME/'namespace-label.inc',VOLUME/'pool-label.c',Path(__file__))
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_inputs}
    record.setdefault('inputs',{}).update(before)
    (work/'home-reader-observe.inc').write_text(render_observer(observe.read_text()))
    (work/'home-reader-startup.c').write_text(render_startup(startup.read_text(),recovered))
    spa_recipe=_recipe(preparation,'spa-active-selected.o')
    spa_source=Path(spa_recipe[spa_recipe.index('-c')+1])
    (work/'home-reader-spa.c').write_text(render_spa(spa_source.read_text(),render_importer(importer.read_text(),recovered)))
    include=['-I'+str(work),'-I'+str(SERVICE),'-I'+str(VOLUME),'-fstack-usage']
    command(_compile(preparation,'engine-startup.o',work/'home-reader-startup.c',work/'home-reader-startup.o',include),work/'reader-startup.log')
    command(_compile(preparation,'spa-active-selected.o',work/'home-reader-spa.c',work/'home-reader-spa.o',include),work/'reader-spa.log')
    command(_compile(preparation,'zpl-mutation.o',VOLUME/'home-recovery-probe.c',work/'home-recovery-probe.o',include+['-std=c17','-Wformat=2']),work/'reader-probe.log')
    replacements={str(port/'spa-active-selected.o'):str(work/'home-reader-spa.o'),
                  str(port/'zpl-mutation.o'):str(work/'home-recovery-probe.o')}
    if not recovered:
        # Prepared recovery labels reject <=782. The pristine reader must use
        # the unchanged original label validator, including its exact782 TXG.
        command(_compile(preparation,'pool-label.o',VOLUME/'pool-label.c',work/'home-reader-label.o',include),work/'reader-label.log')
        replacements[str(port/'pool-label.o')]=str(work/'home-reader-label.o')
    partial=_recipe(preparation,'selected-libzpool.o')
    if any(Path(arg).name in ('zpl-read.o','zpl-recovery.o') for arg in partial):
        raise ValueError('AF09 reader duplicate old read/probe provider')
    command(_relink(partial,replacements,work/'home-reader-libzpool.o',work/'reader-partial.map'),work/'reader-partial.log')
    engine=_recipe(preparation,'selected-engine.o')
    command(_relink(engine,{str(port/'selected-libzpool.o'):str(work/'home-reader-libzpool.o')},work/'home-reader-engine.o'),work/'reader-engine.log')
    elf=destination/'reader.elf'
    command(_relink(_recipe(preparation,'engine.elf'),{
        str(port/'engine-startup.o'):str(work/'home-reader-startup.o'),
        str(port/'selected-engine.o'):str(work/'home-reader-engine.o')},elf,work/'reader.map'),work/'reader-link.log')
    llvm=Path(tools['clang']['path']).parent
    symbols=command([llvm/'llvm-nm','--defined-only',elf],work/'reader-symbols.log')
    required={'main':'home-reader-startup.o','aether_spa_import_probe':'home-reader-engine.o',
              'aether_home_readback':'home-reader-engine.o','spa_import':'home-reader-engine.o',
              'spa_export':'home-reader-engine.o'}
    for name in required:
        rows=[line.split() for line in symbols.splitlines() if line.split()[-1:]==[name]]
        if len(rows)!=1 or len(rows[0])!=3 or rows[0][1]!='T':
            raise ValueError('AF09 reader strong symbol: '+name)
    forbidden={'aether_pool_namespace_recover','aether_fs_home_run','aether_fs_launch_home',
               'aether_zpl_write','aether_pool_namespace_write'}
    if any(line.split()[-1] in forbidden for line in symbols.splitlines() if line.strip()):
        raise ValueError('AF09 reader retained old/writer provider')
    from fs_launch import origins
    final_origins=origins((work/'reader.map').read_text(),required)
    partial_origins=origins((work/'reader-partial.map').read_text(),{
        'aether_home_readback':'home-recovery-probe.o','aether_spa_import_probe':'home-reader-spa.o',
        'spa_import':'home-reader-spa.o','spa_export':'home-reader-spa.o'})
    unresolved=command([llvm/'llvm-nm','-u',elf],work/'reader-imports.log')
    if any(line.split()[-1]!='_DYNAMIC' for line in unresolved.splitlines() if line.strip()):
        raise ValueError('AF09 reader unresolved import')
    if command([llvm/'llvm-readelf','-rW',elf],work/'reader-relocations.log').strip()!='There are no relocations in this file.':
        raise ValueError('AF09 reader runtime relocation')
    # Exact original kernel parser, with the same structural path used by the
    # existing composer. Full admission remains the matched inputs' own gate.
    check=(port/'image-check.zig').read_text()
    (work/'image-check.zig').write_text(replace(check,'@embedFile("engine.elf")','@embedFile("reader.elf")'))
    (work/'reader.elf').write_bytes(elf.read_bytes())
    loader=command(['zig','run','--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
        '-O','ReleaseSafe','--dep','native_elf','-Mroot='+str(work/'image-check.zig'),
        '-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')],work/'reader-loader.log').strip()
    frames={p.name:p.read_text() for p in work.glob('*.su')}
    if not frames or any('dynamic' in value or not value.strip() or any(int(line.split('\t')[1])>8192
        for line in value.splitlines()) for value in frames.values()):
        raise ValueError('AF09 reader local frame bound; not full stack proof')
    for name,expected in before.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:
            raise ValueError('AF09 reader frozen source drift: '+name)
    result=dict(recovered=bool(selected),elf=str(elf),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
        elf_bytes=elf.stat().st_size,origins=final_origins,partial_origins=partial_origins,
        local_frames=frames,structural_loader=loader,healthy_observations=32,healthy_output_bytes=256,
        denied_phases='BNR',utc_min=UTC_MIN,utc_max_exclusive=UTC_MAX,rtc=RTC,
        original_buffered_phases=PHASES.decode('ascii'),clean_export_observed=False,
        generated_sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in work.iterdir()
            if p.suffix in ('.c','.inc')},
        executed=False,native_acceptance=False)
    record['reader']=result
    return result
