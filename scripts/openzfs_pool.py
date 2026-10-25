# SPDX-License-Identifier: BSD-2-Clause
"""Private pool observers for host checks and the opt-in native checkpoint."""
import hashlib
from pathlib import Path
from openzfs_elapsed import function

LABEL_BODY_PINS = {
    'label_offset': '7f61d0d6948eadb90507898d7496bd915e34a0151d1972636176ef00f6fccd8c',
    'zpool_read_label_slow': '58dc5dbb8403eb37f34f7a9c92b83edbbf7c216beaab2a949b0e57814d109c9e',
}
LABEL_SOURCE_SHA256 = '0215a118d9ee4f00e0d5e7f4fb1a48fe28720752154645439e0665d84f5de515'


def trusted_write_hooks(text):
    """Select first trusted writable leaf; never rearm a retired witness."""
    anchor = '''    pool_problem();
    return;
  }
  unsigned phase =
      atomic_load_explicit(&pool_publication, memory_order_acquire);
  if (phase == POOL_READY && vd->vdev_reopening'''
    if text.count('static void aether_pool_hook_open(vdev_t *vd) {') != 1 or text.count(anchor) != 1:
        raise ValueError('trusted writer hook context changed')
    return text.replace(anchor, anchor.replace('  unsigned phase =',
        '  /* Import replaces its provisional read tree before trusted writes. */\n'
        '  if (!spa_writeable(vd->vdev_spa))\n'
        '    return;\n'
        '  unsigned phase =', 1), 1)


def pool_label_bodies(text):
    """Original synchronous reader only; no libzutil scanning/AIO closure."""
    if hashlib.sha256(text.encode()).hexdigest() != LABEL_SOURCE_SHA256:
        raise RuntimeError('pool original label source changed')
    bodies = []
    for name, digest in LABEL_BODY_PINS.items():
        body = function(text, name)
        if hashlib.sha256(body.encode()).hexdigest() != digest:
            raise RuntimeError('pool original label body changed: ' + name)
        bodies.append(body)
    old = 'zpool_read_label_slow(int fd, nvlist_t **config, int *num_labels)'
    if bodies[1].count(old) != 1:
        raise RuntimeError('pool label descriptor context changed')
    bodies[1] = bodies[1].replace(old, 'zpool_read_label_slow(struct aether_label_reader *fd, nvlist_t **config, int *num_labels)')
    for old, new in (
        ('struct stat64 statbuf;', 'struct aether_label_size statbuf;'),
        ('fstat64_blk(fd, &statbuf)', 'aether_label_stat(fd, &statbuf)'),
        ('pread64(fd, label, sizeof (vdev_phys_t),', 'aether_label_pread(fd, label, sizeof (vdev_phys_t),'),
    ):
        if bodies[1].count(old) != 1:
            raise RuntimeError('pool label I/O context changed')
        bodies[1] = bodies[1].replace(old, new, 1)
    notice_end = '\n#ifdef HAVE_AIO_H\n#include <aio.h>\n#endif'
    if text.count(notice_end) != 1:
        raise RuntimeError('pool label notice/include context changed')
    return text[:text.index(notice_end)] + '\n' + '\n\n'.join(bodies) + '\n'

# Exact original 2.4.4 bodies, commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1.
BODY_PINS = {
    'vdev_file_open': '67fda53f7fd73312a47203beb1124309c20be8b11cf704f7890ac36d6bbb42ee',
    'vdev_file_close': 'd5531f284df0cf993b3bd367eddd9edded5559a50bd65b169c16ea8fcd27796a',
    'vdev_file_io_strategy': 'f0ffe67a2eff6c9810a136578df869ceb325ae293e442e00b4a2c682cadc1673',
    'vdev_file_io_fsync': '2532bfd90e7078e26b9fc41d534fd64e9eafd5361c171c975a446f9539b88f3b',
    'vdev_file_io_start': '96d3f9389b705d600c3bc272b1c17d204db970a66f84e3e169794fb4f6ed67ee',
}


def pool_open_mode_body(text):
    # The existing audited extractor does not accept mode_t return types.
    start = 'static mode_t\nvdev_file_open_mode('
    end = '\n\nstatic int\nvdev_file_open('
    if text.count(start) != 1 or text.count(end) != 1:
        raise RuntimeError('pool open-mode context changed')
    body = text[text.index(start):text.index(end, text.index(start))]
    if hashlib.sha256(body.encode()).hexdigest() != '4f89aff2fe6d8d941164318edd0465e305fa665da9ebc9dc592112cb2533c162':
        raise RuntimeError('pool original open-mode body changed')
    return body

TRANSACTION_BODY_PINS = {
    'dmu_tx_get_txg': 'c7e3a3891d4f2c2587e7be4c7ccb032f779991fda65da6d77f74e705d508410d',
    'dmu_tx_pool': '956659b7cd7064d68ad4478f1f1427b1c47b7d32ca58496ba268029f7de79a6c',
    'spa_get_dsl': '6050acf21b8038e4610eba6059b0b1657777af3c8f42e16705cbe258abfde749',
}


def pool_transaction_body(text, name):
    if name == 'dmu_tx_get_txg':
        body = function(text, name)
    else:
        # These two pinned pointer-return getters have one simple body each;
        # avoid widening the shared native selector's accepted return types.
        start = 'dsl_pool_t *\n' + name + '('
        if text.count(start) != 1:
            raise RuntimeError('pool transaction getter context changed: ' + name)
        begin = text.index(start)
        body = text[begin:text.index('\n}', begin) + 2]
    if hashlib.sha256(body.encode()).hexdigest() != TRANSACTION_BODY_PINS[name]:
        raise RuntimeError('pool transaction getter body changed: ' + name)
    return body


SYNC_BODY_PINS = {
    'txg_wait_synced_flags': '29083861ed8b45a5d72358a5b6c4949409171e21c3777edca78ce762be05614f',
    'vdev_config_sync': '2e9cb1790375e5716cd522e6998b379066a684b2ac8f5ee5314e10ef56b4dffd',
    'vdev_uberblock_sync_list': 'ba72814446e594d822ef2cb56a766e842088029c9ddfe21158cd6dbd961c1bfb',
    'vdev_label_sync_list': 'efe2760a3ee9cbb9795725ba81c7102e6ca6e6bba9dc7c0894291184fbfcf75b',
    'vdev_label_sync_top_done': 'ff590ee27d481b173fcc852dd30d3cbc14ac01e41e98ab0811302d31a6ed72eb',
    'vdev_label_sync_ignore_done': 'e33041d8d3f7e271ebac6eb1b5141b27a0a81521bf7686df3fb2c8115eb03266',
}


def sync_body(text, name):
    original = function(text, name)
    if hashlib.sha256(original.encode()).hexdigest() != SYNC_BODY_PINS[name]:
        raise RuntimeError('pool original sync body changed: ' + name)
    return original


def patch_pool_txg(text):
    if 'aether_pool_txg_observe' in text or 'pool-sync-witness.h' in text:
        raise RuntimeError('pool TXG observation already selected')
    original = sync_body(text, 'txg_wait_synced_flags')
    anchor = '\tmutex_exit(&tx->tx_sync_lock);'
    if original.count(anchor) != 1:
        raise RuntimeError('pool TXG unlock context changed')
    call = '\taether_pool_txg_observe(dp, txg, tx->tx_synced_txg, error);\n'
    changed = '#include "pool-sync-witness.h"\n' + original.replace(anchor, call + anchor)
    return text.replace(original, changed, 1)


def patch_pool_labels(text):
    if 'aether_pool_sync_observe' in text or 'pool-sync-witness.h' in text:
        raise RuntimeError('pool sync observation already selected')
    # Also pin the unchanged label-list/callback bodies used by host selection.
    for name in ('vdev_label_sync_list', 'vdev_label_sync_top_done', 'vdev_label_sync_ignore_done'):
        sync_body(text, name)
    original = sync_body(text, 'vdev_uberblock_sync_list')
    anchor = '\t(void) zio_wait(zio);'
    if original.count(anchor) != 2:
        raise RuntimeError('pool uberblock wait context changed')
    chunks = original.split(anchor)
    changed = chunks[0] + anchor + '\n\taether_pool_sync_observe(spa, ub->ub_txg, AETHER_POOL_UB_WRITES_RETURNED, good_writes >= 1 ? 0 : EIO);'
    changed += chunks[1] + anchor + '\n\taether_pool_sync_observe(spa, ub->ub_txg, AETHER_POOL_UB_FLUSH_RETURNED, 0);' + chunks[2]
    text = text.replace(original, '#include "pool-sync-witness.h"\n' + changed, 1)
    original = sync_body(text, 'vdev_config_sync')
    patches = (
        ('retry:\n', '\taether_pool_sync_observe(spa, txg, AETHER_POOL_CONFIG_ATTEMPT, error);\n'),
        ('\t(void) zio_wait(zio);', '\n\taether_pool_sync_observe(spa, txg, AETHER_POOL_BLOCK_FLUSH_RETURNED, 0);'),
    )
    changed = original
    for anchor, addition in patches:
        if changed.count(anchor) != 1:
            raise RuntimeError('pool config context changed')
        changed = changed.replace(anchor, anchor + addition, 1)
    anchor = '\tif ((error = vdev_uberblock_sync_list(svd, svdcount, ub, flags)) != 0) {'
    if changed.count(anchor) != 1:
        raise RuntimeError('pool even-label context changed')
    changed = changed.replace(anchor, '\taether_pool_sync_observe(spa, txg, AETHER_POOL_EVEN_LABELS_RETURNED, 0);\n' + anchor)
    anchor = '\n\treturn (0);\n}'
    if changed.count(anchor) != 1:
        raise RuntimeError('pool config completion context changed')
    changed = changed.replace(anchor, '\n\taether_pool_sync_observe(spa, txg, AETHER_POOL_CONFIG_COMPLETE, 0);' + anchor)
    text = text.replace(original, changed, 1)
    roots = {
        'vdev_config_sync': [
            ('\tzio_t *zio = zio_root(spa, NULL, NULL, flags);',
             '\n\tunsigned aether_pool_phase = aether_pool_root_begin(zio, spa, txg, AETHER_POOL_BLOCK_ROOT, 1);'),
            ('\t(void) zio_wait(zio);', '\n\taether_pool_root_end(aether_pool_phase, 0);')],
        'vdev_uberblock_sync_list': [
            ('\tzio = zio_root(spa, NULL, NULL, flags);',
             '\n\tunsigned aether_pool_phase = aether_pool_root_begin(zio, spa, ub->ub_txg, AETHER_POOL_UB_WRITE_ROOT, 1);'),
            ('\t(void) zio_wait(zio);',
             '\n\taether_pool_root_end(aether_pool_phase, good_writes >= 1 ? 0 : EIO);'),
            ('\tzio = zio_root(spa, NULL, NULL, flags);',
             '\n\taether_pool_phase = aether_pool_root_begin(zio, spa, ub->ub_txg, AETHER_POOL_UB_FLUSH_ROOT, 1);'),
            ('\t(void) zio_wait(zio);', '\n\taether_pool_root_end(aether_pool_phase, 0);')],
        'vdev_label_sync_list': [
            ('\tzio = zio_root(spa, NULL, NULL, flags);',
             '\n\tunsigned aether_pool_phase = aether_pool_root_begin(zio, spa, txg, l ? AETHER_POOL_ODD_WRITE_ROOT : AETHER_POOL_EVEN_WRITE_ROOT, !list_is_empty(dl));'),
            ('\terror = zio_wait(zio);', '\n\taether_pool_root_end(aether_pool_phase, error);'),
            ('\tzio = zio_root(spa, NULL, NULL, flags);',
             '\n\taether_pool_phase = aether_pool_root_begin(zio, spa, txg, l ? AETHER_POOL_ODD_FLUSH_ROOT : AETHER_POOL_EVEN_FLUSH_ROOT, !list_is_empty(dl));'),
            ('\t(void) zio_wait(zio);', '\n\taether_pool_root_end(aether_pool_phase, 0);')],
    }
    for name, patches in roots.items():
        body = function(text, name)
        # Insert in original occurrence order, not by a second global replace
        # that could accidentally select the first root or wait again.
        cursor = 0
        for anchor, call in patches:
            begin = body.find(anchor, cursor)
            if begin < 0:
                raise RuntimeError('pool root context changed: ' + name)
            finish = begin + len(anchor)
            body = body[:finish] + call + body[finish:]
            cursor = finish + len(call)
        text = text.replace(function(text, name), body, 1)
    anchor = '#include "pool-sync-witness.h"'
    if text.count(anchor) != 1:
        raise RuntimeError('pool root include context changed')
    return text.replace(anchor, anchor + '\n#include "pool-flow-witness.h"', 1)


GRAPH_BODY_PINS = {
    'zio_add_child_impl': '4a6e8740d849fa85fc03aabdefcc960af4037008e638fa6e322484da02eb99c2',
    'zio_destroy': '41108976dfdda563c9c5bde06d5c61512cdbe685e43ea7681d3521b727b86d12',
    'zio_flush': 'a19dd07e924a385399a29ef2f9680c76dd1fba3cede1db3044ee2779727704b2',
    'zio_write_phys': '5e91059b1b044079578788b9d1f9783e645b0e6fa68c06a717073e19b8776675',
}


def graph_body(text, name, checked=True):
    if name == 'zio_write_phys':
        start = 'zio_t *\nzio_write_phys('
        if text.count(start) != 1:
            raise RuntimeError('pool physical-write context changed')
        begin = text.index(start)
        body = text[begin:text.index('\n}', begin) + 2]
    else:
        body = function(text, name)
    if checked and hashlib.sha256(body.encode()).hexdigest() != GRAPH_BODY_PINS[name]:
        raise RuntimeError('pool original graph body changed: ' + name)
    return body


def patch_pool_graph(text):
    if 'aether_pool_' in text or 'pool-flow-witness.h' in text:
        raise RuntimeError('pool graph observation already selected')
    additions = {
        'zio_add_child_impl': ('\tlist_insert_head(&cio->io_parent_list, zl);',
                               '\n\taether_pool_zio_child(pio, cio);'),
        'zio_destroy': ('\n{', '\n\taether_pool_zio_retire(zio);'),
        'zio_flush': ('\n{', '\n\taether_pool_flush_requested(pio, vd);'),
        'zio_write_phys': ('\treturn (zio);',
                           '\taether_pool_write_requested(pio, zio);\n'),
    }
    for name, (anchor, call) in additions.items():
        original = graph_body(text, name)
        if original.count(anchor) != 1:
            raise RuntimeError('pool graph hook context changed: ' + name)
        changed = original.replace(anchor, call + anchor if name == 'zio_write_phys' else anchor + call, 1)
        if name == 'zio_add_child_impl':
            changed = '#include "pool-flow-witness.h"\n' + changed
        text = text.replace(original, changed, 1)
    return text


def patch_pool_vdev(text):
    """Add observations around original calls; reject drift and repeated intake."""
    if 'aether_pool_hook_' in text or 'pool-vdev-hooks.inc' in text:
        raise RuntimeError('pool observation already selected')
    pool_open_mode_body(text)
    # Each anchor belongs to one audited original body, not the whole file.
    additions = {
        'vdev_file_open': (
            ('\treturn (0);', '\taether_pool_hook_open(vd);\n'),
        ),
        'vdev_file_close': (
            ('\tif (vf->vf_file != NULL) {', '\taether_pool_hook_close(vd);\n'),
        ),
        'vdev_file_io_strategy': (
            ('\tzio_t *zio = (zio_t *)arg;\n',
             '\tstruct pool_observation observation = aether_pool_hook_take(zio);\n'),
            ('\t\t    vd->vdev_ashift, &resid);\n',
             '\t\taether_pool_hook_provider(&observation, vf->vf_file, err, resid);\n'),
            ('\tzio_delay_interrupt(zio);',
             '\taether_pool_hook_finish(&observation, zio);\n'),
        ),
        'vdev_file_io_fsync': (
            ('\tzio_t *zio = (zio_t *)arg;\n',
             '\tstruct pool_observation observation = aether_pool_hook_take(zio);\n'),
            ('\tzio->io_error = zfs_file_fsync(vf->vf_file, O_SYNC | O_DSYNC);\n',
             '\taether_pool_hook_provider(&observation, vf->vf_file, zio->io_error, 0);\n'),
            ('\tzio_interrupt(zio);',
             '\taether_pool_hook_finish(&observation, zio);\n'),
        ),
        'vdev_file_io_start': (
            ('\n{\n', '\taether_pool_hook_admit(zio);\n'),
        ),
    }
    for name, patches in additions.items():
        original = function(text, name)
        if hashlib.sha256(original.encode()).hexdigest() != BODY_PINS[name]:
            raise RuntimeError('pool original body changed: ' + name)
        changed = original
        for anchor, addition in patches:
            if changed.count(anchor) != 1:
                raise RuntimeError('pool hook context changed: ' + name)
            # Interrupt observations precede a call that can free the request.
            if 'interrupt(zio);' in anchor or name in ('vdev_file_open', 'vdev_file_close'):
                changed = changed.replace(anchor, addition + anchor, 1)
            else:
                changed = changed.replace(anchor, anchor + addition, 1)
        if name == 'vdev_file_io_start':
            anchor = '\t\t\tzio_interrupt(zio);'
            if changed.count(anchor) != 2:
                raise RuntimeError('pool direct completion context changed')
            changed = changed.replace(anchor, '\t\t\taether_pool_hook_direct(zio);\n' + anchor)
        if name == 'vdev_file_open':
            changed = '#include <sys/dmu_tx.h>\n#include <sys/dsl_pool.h>\n#include "pool-vdev-hooks.inc"\n' + changed
        text = text.replace(original, changed, 1)
    return text


def build_pool_objects(output, base, receipt, command, active_labels=False, namespace=False, namespace_recovery=False, worker_stages=False, sync_stages=False):
    """Reconstruct each original slot before selecting private observations."""
    if namespace_recovery and (not namespace or active_labels):
        raise ValueError('ZPL recovery labels require exported namespace selection')
    if sync_stages and not worker_stages:
        raise ValueError('sync stages require worker profile')
    from openzfs_elapsed import route
    owned = Path(__file__).resolve().parents[1] / 'user/storage/openzfs-volume'
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    records = []
    selections = [(98, 'txg', patch_worker_txg if worker_stages and not sync_stages else patch_pool_txg),
                  (109, 'labels', patch_pool_labels), (138, 'graph', patch_pool_graph)]
    if sync_stages:
        selections += [(162, 'dsl-sync', patch_sync_dsl)]
    for slot, name, patch in selections:
        recipe = next(c['argv'] for c in receipt['commands']
                      if c['name'] == 'input-' + str(slot) + '-checked')
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        prefix[1:1] = ['-I' + str(output / 'resources'),
                       '-I' + str(output / 'allocation'), '-I' + str(owned)]
        prefix += ['-isystem', str(Path(prefix[0]).parents[1] / 'lib/clang/21/include')]
        source = Path(route(recipe[recipe.index('-c') + 1]))
        original = output / ('pool-' + name + '-original.o')
        command(prefix + ['-c', source, '-o', original],
                output / ('pool-' + name + '-original.log'))
        if sha(original) != sha(base[slot]):
            raise RuntimeError('pool original slot bytes changed: ' + name)
        selected_source = output / ('pool-' + name + '.c')
        selected_source.write_text(patch(source.read_text()))
        # Preserve original diagnostic __FILE__ paths, not temporary root names.
        historical = str(source)
        for arg in prefix:
            if arg.startswith('-fmacro-prefix-map='):
                left, right = arg.removeprefix('-fmacro-prefix-map=').split('=', 1)
                if str(source).startswith(left):
                    historical = right + str(source)[len(left):]
                    break
        selected = output / ('pool-' + name + '.o')
        command(prefix + ['-fmacro-prefix-map=' + str(selected_source) + '=' + historical,
                          '-c', selected_source, '-o', selected],
                output / ('pool-' + name + '.log'))
        base[slot] = str(selected)
        records.append({'slot': slot, 'original_sha256': sha(original),
                        'selected_source_sha256': sha(selected_source),
                        'selected_sha256': sha(selected)})
    ledger = output / 'pool-witness.o'
    command(prefix + ['-Wall', '-Wextra', '-Werror', '-c', owned / 'pool-witness.c',
                      '-o', ledger], output / 'pool-witness.log')
    base.append(str(ledger))
    from openzfs_elapsed import CURRENT
    label_source = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libzutil/zutil_import.c'
    excerpt = output / 'pool-label-original.inc'
    excerpt.write_text(pool_label_bodies(label_source.read_text()))
    intake = output / 'pool-label.o'
    intake_source = owned / 'pool-label.c'
    if namespace_recovery:
        from openzfs_namespace import recovery_label_source
        (output / 'namespace-recovery-label.inc').write_text(
            recovery_label_source((owned / 'namespace-label.inc').read_text()))
        anchor = '#include "namespace-label.inc"'
        text = intake_source.read_text()
        if text.count(anchor) != 1:
            raise ValueError('ZPL recovery label include context changed')
        intake_source = output / 'pool-recovery-label.c'
        intake_source.write_text(text.replace(anchor, '#include "namespace-recovery-label.inc"', 1))
    command(prefix + ['-I' + str(output), '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                      *(['-DAETHER_POOL_ACTIVE_LABELS=1'] if active_labels else []),
                      *(['-DAETHER_POOL_NAMESPACE=1'] if namespace else []),
                      *(['-DAETHER_POOL_ZPL_RECOVER=1'] if namespace_recovery else []),
                      '-ffunction-sections', '-fdata-sections', '-c', intake_source,
                      '-o', intake], output / 'pool-label.log')
    base.append(str(intake))
    return {'slots': records, 'ledger_sha256': sha(ledger),
            'label_intake': {'source_sha256': sha(label_source),
                            'original_body_sha256': LABEL_BODY_PINS,
                            'excerpt_sha256': sha(excerpt), 'object_sha256': sha(intake),
                            'adapter_sha256': sha(owned / 'pool-label.c'),
                            'expected_state': 'ACTIVE' if active_labels else 'EXPORTED'}}


def repeated_write_hooks(text):
    """Two append-only TXG observations; canonical single-write hooks stay fixed."""
    text = trusted_write_hooks(text)
    replacements = (
        ('#include "pool-flow.inc"', '#include "pool-repeat.inc"'),
        ('sizeof(pool_nodes) + sizeof(pool_phases) +\n                       sizeof(pool_step) + sizeof(pool_synced)',
         'sizeof(pool_nodes) + sizeof(pool_repeat_records) +\n                       sizeof(pool_repeat_count) + sizeof(pool_synced)'),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise ValueError('repeated writer hook context changed')
        text = text.replace(old, new, 1)
    start = text.index('  unsigned unbound = POOL_TX_UNBOUND;',
                       text.index('int aether_pool_hooks_bind_transaction('))
    end = text.index('\n}\n', start)
    expected = '''  unsigned unbound = POOL_TX_UNBOUND;
  if (!atomic_compare_exchange_strong_explicit(
          &pool_transaction, &unbound, POOL_TX_BINDING, memory_order_acquire,
          memory_order_relaxed)) {
    pool_problem();
    return EALREADY;
  }
  int error = aether_pool_witness_bind_txg(pool_observer, dmu_tx_get_txg(tx));
  if (error) {
    pool_problem();
    return error; /* BINDING remains incomplete, never reset/retry. */
  }
  pool_dp = dp;
  atomic_store_explicit(&pool_transaction, POOL_TX_BOUND, memory_order_release);
  return 0;'''
    if text[start:end] != expected:
        raise ValueError('repeated writer transaction context changed')
    return text[:start] + '  return pool_repeat_bind(dp, dmu_tx_get_txg(tx));' + text[end:]


def eight_write_hooks(text):
    """Approved fixed eight-record/10KiB private observer; defaults stay exact."""
    selected = repeated_write_hooks(text)
    from deps import ROOT
    flow = (ROOT / 'user/storage/openzfs-volume/pool-repeat.inc').read_text()
    if flow.count('#define POOL_REPEAT_LIMIT 2') != 1:
        raise ValueError('eight-write record limit context changed')
    flow = flow.replace('#define POOL_REPEAT_LIMIT 2', '#define POOL_REPEAT_LIMIT 8', 1)
    old = '#include "pool-repeat.inc"'
    bound = '<=\n                   8192,'
    if selected.count(old) != 1 or selected.count(bound) != 1:
        raise ValueError('eight-write observer budget context changed')
    return selected.replace(old, flow, 1).replace(bound, '<=\n                   10240,', 1)


def lifetime_write_hooks(text):
    """One explicitly retired TXG record; existing append-only paths stay exact."""
    selected = repeated_write_hooks(text)
    old = ('sizeof(pool_repeat_records) +\n'
           '                       sizeof(pool_repeat_count) + sizeof(pool_synced)')
    new = ('sizeof(pool_record) + sizeof(pool_epoch) + sizeof(pool_gate) +\n'
           '                       sizeof(pool_retired_txg) + sizeof(pool_completed) + sizeof(pool_synced)')
    if selected.count(old) != 1 or selected.count('#include "pool-repeat.inc"') != 1:
        raise ValueError('write lifetime observer context changed')
    return selected.replace(old,new,1).replace('#include "pool-repeat.inc"','#include "pool-lifetime.inc"',1)


def repeated_write_probe(text):
    """Two adjacent eight-byte writes retain the existing independent oracle."""
    old = '''        unsigned char bytes[ZPL_PROBE_LENGTH];
        for (size_t i = 0; i < sizeof(bytes); ++i)
            bytes[i] = replacement(i);
        error =
            aether_zpl_write(view, 2, 47, ZPL_PROBE_OFFSET, bytes,
                             sizeof(bytes), utc.tv_sec, utc.tv_nsec, &result);'''
    new = '''        uint64_t previous = 0;
        for (unsigned part = 0; part < 2 && !error; ++part) {
            unsigned char bytes[ZPL_PROBE_LENGTH / 2];
            for (size_t i = 0; i < sizeof(bytes); ++i)
                bytes[i] = replacement(part * sizeof(bytes) + i);
            error = aether_zpl_write(view, 2, 47,
                                     ZPL_PROBE_OFFSET + part * sizeof(bytes),
                                     bytes, sizeof(bytes), utc.tv_sec,
                                     utc.tv_nsec, &result);
            if (!error && (result.txg <= previous ||
                           result.bytes_staged != sizeof(bytes) ||
                           result.state != AETHER_ZPL_SYNCED))
                error = EIO;
            previous = result.txg;
        }'''
    check = 'result.bytes_staged != ZPL_PROBE_LENGTH ||'
    if text.count(old) != 1 or text.count(check) != 1:
        raise ValueError('repeated writer probe context changed')
    return text.replace(old, new, 1).replace(check,
        'result.bytes_staged != ZPL_PROBE_LENGTH / 2 ||', 1)


def transaction_write_probe(text):
    """Worker experiment after a separately qualified pristine readonly VM.

    Fixed expected data comes from original-zdb extraction plus Python splice,
    independently of this writer. Keep its full post-write stream and EOF check.
    The paired coordinator must qualify unchanged pristine media before entry.
    """
    text = repeated_write_probe(text)
    start = text.index('    unsigned char original[32]')
    end = text.index('    struct timespec utc;', start)
    if hashlib.sha256(text[start:end].encode()).hexdigest() != 'ff43cefc15ebe85770685f1dd8501fca9333e946c6df5cb9051ac617a919dcda':
        raise ValueError('transaction writer baseline context changed')
    expected = bytes.fromhex('9ae4ab7a896f9d760334d1f322996043e1e132f4b131ccc3f2b7b2c577d2afb0')
    oracle = ('    unsigned char actual[32];\n'
              '    static const unsigned char predicted[32] = {\n        ' +
              ', '.join(f'0x{byte:02x}' for byte in expected) + '};\n')
    return text[:start] + oracle + text[end:]


def staged_import_probe(text):
    """Keep original config validation; reuse its eight exported hash slots."""
    old = '''        for (unsigned i = 0; i < 8; ++i)
            aether_engine_utc_phase((hash >> (8 * i)) & 255);'''
    if text.count(old) != 1 or text.count('int aether_spa_import_probe(void)') != 1:
        raise ValueError('stage diagnostic import context changed')
    return text.replace(old, '        /* Stage profile keeps validation but does not export the XDR hash. */', 1)


def staged_write_probe(text):
    """Only scalar markers; preserve every original operation/error/close."""
    text = repeated_write_probe(text)
    changes = (
        ('    int error = aether_zpl_open_write(',
         "    aether_engine_utc_phase('o');\n    int error = aether_zpl_open_write("),
        ('    unsigned char stage = 2;',
         "    aether_engine_utc_phase('r');\n    unsigned char stage = 2;"),
        ('        stage = 4;\n        error = stream_hash',
         "        stage = 4;\n        aether_engine_utc_phase('h');\n        error = stream_hash"),
        ('        stage = 5;\n        if (clock_gettime',
         "        stage = 5;\n        aether_engine_utc_phase('c');\n        if (clock_gettime"),
        ('            error = aether_zpl_write(view, 2, 47,',
         "            aether_engine_utc_phase(part ? '2' : '1');\n            error = aether_zpl_write(view, 2, 47,"),
        ('        stage = 8;\n        error = aether_zpl_lookup',
         "        stage = 8;\n        aether_engine_utc_phase('v');\n        error = aether_zpl_lookup"),
        ('    if (!error)\n        *assigned = result.txg;',
         "    if (!error) {\n        aether_engine_utc_phase('x');\n        *assigned = result.txg;\n    }"),
    )
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('stage diagnostic probe context changed')
        text = text.replace(old, new, 1)
    return text


def first_write_provider(text):
    """Explicit first-call wrapper; original/default entry has no observations."""
    signature = '''int aether_zpl_write(aether_zpl_view *view, uint64_t object,
                     uint64_t generation, uint64_t offset, const void *buffer,
                     size_t length, uint64_t seconds, uint64_t nanoseconds,
                     aether_zpl_write_result *out)'''
    changes = (
        (signature, signature.replace('int aether_zpl_write(', 'static int write_profile(').replace(
            'aether_zpl_write_result *out)', 'aether_zpl_write_result *out, int diagnostic)')),
        ('    error = dmu_tx_assign(tx, DMU_TX_WAIT);',
         "    if (diagnostic) aether_engine_utc_phase('a');\n    error = dmu_tx_assign(tx, DMU_TX_WAIT);\n    if (diagnostic) aether_engine_utc_phase('b');"),
        ('    dmu_tx_commit(tx);', "    if (diagnostic) aether_engine_utc_phase('c');\n    dmu_tx_commit(tx);"),
        ('    out->state = AETHER_ZPL_COMMITTED;',
         "    out->state = AETHER_ZPL_COMMITTED;\n    if (diagnostic) aether_engine_utc_phase('d');"),
        ('''    if (!error)
        error =
            txg_wait_synced_flags(spa_get_dsl(spa), out->txg, TXG_WAIT_SUSPEND);''',
         '''    if (!error) {
        if (diagnostic) aether_engine_utc_phase('w');
        error =
            txg_wait_synced_flags(spa_get_dsl(spa), out->txg, TXG_WAIT_SUSPEND);
        if (diagnostic) aether_engine_utc_phase('s');
    }'''),
    )
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('first-write provider context changed')
        text = text.replace(old, new, 1)
    text = 'extern void aether_engine_utc_phase(unsigned char);\n' + text
    for name, diagnostic in (('aether_zpl_write', False), ('aether_zpl_write_diagnostic', True)):
        text += '\n' + signature.replace('aether_zpl_write(', name + '(') + '\n{\n'
        if diagnostic:
            text += "    aether_engine_utc_phase('e');\n    int error = "
        else:
            text += '    return '
        text += ('write_profile(view, object, generation, offset, buffer, length,\n'
                 '                         seconds, nanoseconds, out, ' + str(int(diagnostic)) + ');\n')
        if diagnostic:
            text += "    aether_engine_utc_phase('f');\n    return error;\n"
        text += '}\n'
    return text


def first_write_probe(text):
    """Observe first helper only, preserving original error/close/readback flow."""
    text = repeated_write_probe(text)
    old = '            error = aether_zpl_write(view, 2, 47,'
    if text.count(old) != 1 or text.count('#define ZPL_PROBE_BYTES') != 1:
        raise ValueError('first-write probe context changed')
    text = text.replace(old, '            error = (part ? aether_zpl_write : aether_zpl_write_diagnostic)(view, 2, 47,', 1)
    return text.replace('#define ZPL_PROBE_BYTES', '''extern int aether_zpl_write_diagnostic(aether_zpl_view *, uint64_t,
    uint64_t, uint64_t, const void *, size_t, uint64_t, uint64_t,
    aether_zpl_write_result *);

#define ZPL_PROBE_BYTES''', 1)


WORKER_BODY_PINS = {
    'txg_sync_thread': 'fed72787e526e17b30dfb87194608470b261887abc02a84a1b112df083fd075e',
    'txg_quiesce_thread': '72e42138dccf837bb0a1d31db76376f191bc4f1d7b4173d10149c60017b23866',
}


def worker_body(text, name, checked=True):
    start = 'static __attribute__((noreturn)) void\n' + name + '(void *arg)\n{'
    if name not in WORKER_BODY_PINS or text.count(start) != 1:
        raise ValueError('TXG worker function context changed')
    begin = text.index(start)
    body = text[begin:text.index('\n}', begin) + 2]
    if checked and hashlib.sha256(body.encode()).hexdigest() != WORKER_BODY_PINS[name]:
        raise ValueError('TXG worker original body changed')
    return body


def patch_worker_txg(text):
    """Observe original workers only at points outside tx_sync_lock."""
    originals = {name: worker_body(text, name) for name in WORKER_BODY_PINS}
    text = patch_pool_txg(text)
    for name, original in originals.items():
        changes = (
            ("\t\ttxg_quiesce(dp, txg);", "\t\taether_pool_worker_progress(dp, txg, 'q');"),
        ) if name == 'txg_quiesce_thread' else (
            ('\t\tmutex_exit(&tx->tx_sync_lock);', "\t\taether_pool_worker_progress(dp, txg, 's');"),
            ('\t\tspa_sync(spa, txg);', "\t\taether_pool_worker_progress(dp, txg, 'd');"),
        )
        selected = original
        for anchor, call in changes:
            if selected.count(anchor) != 1:
                raise ValueError('TXG worker observation anchor changed')
            selected = selected.replace(anchor, anchor + '\n' + call, 1)
        text = text.replace(original, selected, 1)
    anchor = worker_body(text, 'txg_sync_thread', checked=False)
    return text.replace(anchor, 'extern void aether_pool_worker_progress(const void *, uint64_t, unsigned char);\n' + anchor, 1)


def worker_flow(text):
    """No new mutable state: select the immutable first published TXG."""
    anchor = 'static void pool_flow_prepare(void)'
    callback = '''extern void aether_pool_worker_phase(unsigned char) __attribute__((weak));
void aether_pool_worker_progress(const void *dp, uint64_t target, unsigned char event)
{
    if (!pool_observer ||
        atomic_load_explicit(&pool_publication, memory_order_acquire) != POOL_READY ||
        atomic_load_explicit(&pool_transaction, memory_order_acquire) != POOL_TX_BOUND ||
        !atomic_load_explicit(&pool_repeat_count, memory_order_acquire) ||
        dp != pool_dp || target != atomic_load(&pool_repeat_records[0].txg))
        return;
    if (aether_pool_worker_phase) aether_pool_worker_phase(event);
}

'''
    bound = '''    atomic_store_explicit(&pool_transaction, POOL_TX_BOUND,
                          memory_order_release);
    return 0;'''
    ended = '''    if (!atomic_compare_exchange_strong_explicit(&record->step, &active, local,
                                                 memory_order_release,
                                                 memory_order_relaxed))
        pool_problem();'''
    replacements = (
        (anchor, callback + anchor),
        (bound, bound.replace('    return 0;', "    if (!n) aether_pool_worker_progress(dp, target, 'b');\n    return 0;")),
        (ended, ended + '''
    else if (!index && (local == 1 || local == 4 || local == 7))
        aether_pool_worker_progress(pool_dp, atomic_load(&record->txg),
                                   local == 1 ? 'l' : local == 4 ? 'u' : 'o');'''),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise ValueError('TXG worker flow context changed')
        text = text.replace(old, new, 1)
    return text


def worker_write_provider(text):
    anchor = '#include <sys/txg.h>'
    old = '''    if (!error)
        error =
            txg_wait_synced_flags(spa_get_dsl(spa), out->txg, TXG_WAIT_SUSPEND);'''
    new = '''    if (!error) {
        error =
            txg_wait_synced_flags(spa_get_dsl(spa), out->txg, TXG_WAIT_SUSPEND);
        aether_pool_worker_progress(spa_get_dsl(spa), out->txg, 'w');
    }'''
    if text.count(anchor) != 1 or text.count(old) != 1:
        raise ValueError('TXG worker provider context changed')
    return text.replace(anchor, anchor + '\nextern void aether_pool_worker_progress(const void *, uint64_t, unsigned char);', 1).replace(old, new, 1)


def worker_publisher(text):
    anchor = 'void aether_engine_utc_phase(unsigned char phase) { engine_observe(phase); }'
    if text.count(anchor) != 1:
        raise ValueError('TXG worker publisher context changed')
    return text.replace(anchor, anchor + '\nvoid aether_pool_worker_phase(unsigned char phase) { aether_engine_utc_phase(phase); }', 1)


SYNC_STAGE_PINS = {
    'spa_sync': 'e2aed369025419e8fe98299e103b99efd7bf27c096b919fa2d575b5d43fb2863',
    'dsl_pool_sync': '53b47e59d62421c03447a9e5ec1aff1cde8e46e895d8bdb9b9e7ed57c4a13525',
}


def sync_stage_body(text, name):
    original = function(text, name)
    if hashlib.sha256(original.encode()).hexdigest() != SYNC_STAGE_PINS[name]:
        raise ValueError('original sync-stage body changed: ' + name)
    return original


def patch_sync_spa(text):
    original = sync_stage_body(text, 'spa_sync')
    selected = original
    points = (
        ('\tvdev_t *vd = NULL;', 'e'),
        ('\t(void) zio_wait(spa->spa_txg_zio[txg & TXG_MASK]);', 'i'),
        ('\tspa_config_exit(spa, SCL_STATE, FTAG);', 'c'),
        ('\tspa_sync_iterate_to_convergence(spa, tx);', 'r'),
    )
    for anchor, event in points:
        if selected.count(anchor) != 1:
            raise ValueError('sync-stage SPA context changed')
        selected = selected.replace(anchor, anchor + '\n\taether_pool_worker_progress(spa->spa_dsl_pool, txg, \'' + event + "');", 1)
    declaration = 'extern void aether_pool_worker_progress(const void *, uint64_t, unsigned char);\n'
    return text.replace(original, declaration + selected, 1)


def patch_sync_dsl(text):
    original = sync_stage_body(text, 'dsl_pool_sync')
    selected = original
    for anchor, event in (('\ttx = dmu_tx_create_assigned(dp, txg);', 'p'),
                          ('\tVERIFY0(zio_wait(rio));', 'v')):
        # The first dataset wait is distinct from later MOS/accounting waits.
        if anchor not in selected:
            raise ValueError('sync-stage DSL context changed')
        selected = selected.replace(anchor, anchor + '\n\tif (spa_sync_pass(dp->dp_spa) == 1) aether_pool_worker_progress(dp, txg, \'' + event + "');", 1)
    declaration = 'extern void aether_pool_worker_progress(const void *, uint64_t, unsigned char);\n'
    return text.replace(original, declaration + selected, 1)


def sync_stage_flow(text):
    """Keep first-target binding/gating; ordinary roots retain their witness."""
    text = worker_flow(text)
    removed = '''    else if (!index && (local == 1 || local == 4 || local == 7))
        aether_pool_worker_progress(pool_dp, atomic_load(&record->txg),
                                   local == 1 ? 'l' : local == 4 ? 'u' : 'o');'''
    if text.count(removed) != 1:
        raise ValueError('sync-stage flow context changed')
    return text.replace(removed, '', 1)
