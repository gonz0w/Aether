# SPDX-License-Identifier: BSD-2-Clause
"""Pure fixed Zsh home reader rendering; supplied bytes are not native evidence.

Original OpenZFS owns the readonly oracle. The forty-byte result contains its
preserved original-metadata digest and an exact role/version tag, published only
after the original readonly import/close/runtime health checks finish.
"""
import hashlib
from pathlib import Path
import re

import home_reader as legacy

UTC_MIN, UTC_MAX, RTC = legacy.UTC_MIN, legacy.UTC_MAX, legacy.RTC
PHASES = legacy.PHASES
RESULT_FORMAT = 'aether-zsh-home-result-v1'
CONTROLLER_SHA256 = '78b00eca10d2b19bb09a4cac645fb3a136481bd1671bc6acdd64366b2fcd11d5'


def require(ok, message):
    if not ok:
        raise ValueError('Zsh home reader: '+message)


def tag(recovered):
    require(type(recovered) is bool, 'explicit pristine/recovery boolean')
    return b'ZSHWR001' if recovered else b'ZSHPR001'


def render_observer(original):
    text = legacy.render_observer(original)
    text = legacy.replace(text, 'unsigned char aether_home_reader_digest[32];',
                          'unsigned char aether_zsh_home_result[40];')
    return legacy.replace(text, 'unsigned aether_home_reader_ready;',
                          'unsigned aether_zsh_home_ready;')


def render_startup(original, recovered):
    tag(recovered)
    text = legacy.render_startup(original, recovered)
    text = legacy.replace(text, 'aether_home_reader_digest[i]', 'aether_zsh_home_result[i]')
    text = legacy.replace(text, 'aether_home_reader_ready', 'aether_zsh_home_ready', count=2)
    return legacy.replace(text, '(denied ? 3U : 32U)', '(denied ? 3U : 40U)')


def render_importer(original, recovered):
    tag(recovered)
    text = legacy.render_importer(original, recovered)
    text = legacy.replace(text, 'extern unsigned char aether_home_reader_digest[32];',
                          'extern unsigned char aether_zsh_home_result[40];')
    text = legacy.replace(text, 'extern unsigned aether_home_reader_ready;',
                          'extern unsigned aether_zsh_home_ready;')
    text = legacy.replace(text, 'aether_home_readback(spa,', 'aether_home_zsh_readback(spa,')
    text = legacy.replace(text, 'aether_home_reader_digest);', 'aether_zsh_home_result);')
    return legacy.replace(text, 'aether_home_reader_ready = 1;', 'aether_zsh_home_ready = 1;')


def render_spa(original, importer):
    return legacy.render_spa(original, importer)


def render_controller(original):
    require(hashlib.sha256(original.encode()).hexdigest() == CONTROLLER_SHA256,
            'exact maintained readonly controller source')
    require(original.count('256') == 10 and original.count('257') == 1,
            'exact healthy capacity occurrences')
    changes = (
        ('Gen1 validates32 eight-byte digest rows', 'Gen1 validates40 eight-byte result rows'),
        ('all32 opaque digest bytes', 'all40 result bytes (digest32 plus role tag8)'),
        ('for index in 0..32 {', 'for index in 0..40 {'),
    )
    text = original.replace('256', '320').replace('257', '321')
    for before, after in changes:
        text = legacy.replace(text, before, after)
    inverse = text
    for before, after in reversed(changes):
        inverse = legacy.replace(inverse, after, before)
    inverse = inverse.replace('320', '256').replace('321', '257')
    require(inverse == original and text.count('row[5] = 32;') == 1
            and text.count('row[7] = 32;') == 1, 'exact inverse and denied resource rows')
    return text


def reader_recipes(preparation, base, work, destination, recovered, sources):
    """Return bounded source/argv data only; caller owns fit, freeze and execution."""
    tag(recovered)
    base, work, destination = map(Path, (base, work, destination))
    require(all(p.is_absolute() and '..' not in p.parts for p in (base, work, destination)),
            'owned absolute recipe paths')
    require(preparation.get('old_service') is None and preparation.get('recovery_empty') is False,
            'normal readonly recovery provider')
    require(set(sources) == {'startup', 'observer', 'importer', 'spa', 'controller'}
            and all(type(text) is str for text in sources.values()), 'complete source texts')
    generated = {
        str(work/'home-reader-observe.inc'): render_observer(sources['observer']),
        str(work/'home-reader-startup.c'): render_startup(sources['startup'], recovered),
        str(work/'home-reader-spa.c'): render_spa(sources['spa'], render_importer(sources['importer'], recovered)),
        str(work/'zsh-home-readback.rs'): render_controller(sources['controller']),
    }
    include = ['-I'+str(work), '-I'+str(legacy.SERVICE), '-I'+str(legacy.VOLUME), '-fstack-usage']
    rows = []
    for label, old, source, output, extra in (
        ('reader-startup', 'engine-startup.o', work/'home-reader-startup.c', work/'home-reader-startup.o', include),
        ('reader-spa', 'spa-active-selected.o', work/'home-reader-spa.c', work/'home-reader-spa.o', include),
        ('reader-oracle', 'zpl-mutation.o', legacy.VOLUME/'home-recovery-probe.c', work/'home-recovery-probe.o',
         include+['-std=c17', '-Wformat=2']),
    ):
        rows.append(dict(label=label, argv=list(map(str, legacy._compile(preparation, old, source, output, extra)))))
    port = base/'port'
    replacements = {str(port/'spa-active-selected.o'): str(work/'home-reader-spa.o'),
                    str(port/'zpl-mutation.o'): str(work/'home-recovery-probe.o')}
    if not recovered:
        rows.append(dict(label='reader-pristine-label', argv=list(map(str, legacy._compile(preparation,
            'pool-label.o', legacy.VOLUME/'pool-label.c', work/'home-reader-label.o', include)))))
        replacements[str(port/'pool-label.o')] = str(work/'home-reader-label.o')
    partial = legacy._recipe(preparation, 'selected-libzpool.o')
    require(not any(Path(arg).name in ('zpl-read.o', 'zpl-recovery.o') for arg in partial),
            'no duplicate old provider')
    for label, argv in (
        ('reader-partial', legacy._relink(partial, replacements, work/'home-reader-libzpool.o', work/'reader-partial.map')),
        ('reader-engine', legacy._relink(legacy._recipe(preparation, 'selected-engine.o'),
            {str(port/'selected-libzpool.o'): str(work/'home-reader-libzpool.o')}, work/'home-reader-engine.o')),
        ('reader-link', legacy._relink(legacy._recipe(preparation, 'engine.elf'),
            {str(port/'engine-startup.o'): str(work/'home-reader-startup.o'),
             str(port/'selected-engine.o'): str(work/'home-reader-engine.o')}, destination/'reader.elf', work/'reader.map')),
    ):
        rows.append(dict(label=label, argv=list(map(str, argv))))
    return dict(recovered=recovered, generated_sources=generated, commands=rows,
                qualification='Unexecuted recipe; actual loader/stack/lifetime review remains required',
                projected_bytes=40, physical_output_bytes=320, original_buffered_phases=32,
                utc_min=UTC_MIN, utc_max_exclusive=UTC_MAX, rtc=RTC)


def decode_result(raw, recovered):
    expected = tag(recovered)
    require(type(raw) is bytes and len(raw) == 320
            and all(raw[i] == 0 for i in range(320) if i % 8), 'exact forty padded scalar writes')
    digest, observed = raw[::8][:32], raw[::8][32:]
    require(observed == expected, 'exact role/version tag')
    return dict(format=RESULT_FORMAT, recovered=recovered, metadata_sha256=digest.hex(),
                tag_hex=observed.hex(), scope='Supplied result only; no native or persistence acceptance')


def compare_results(pristine, recovered):
    for result, role in ((pristine, False), (recovered, True)):
        require(type(result) is dict and result.get('format') == RESULT_FORMAT
                and result.get('recovered') is role and result.get('tag_hex') == tag(role).hex(),
                'distinct complete pristine and recovery results')
        require(type(result.get('metadata_sha256')) is str
                and re.fullmatch('[0-9a-f]{64}', result['metadata_sha256']), 'full original metadata digest')
    require(pristine['metadata_sha256'] == recovered['metadata_sha256'],
            'preserved original metadata across fresh readonly providers')
    return dict(metadata_sha256=pristine['metadata_sha256'], native_executed=False,
                persistence_verified=False, scope='Result comparison only; exact source/media/lifetime evidence required')
