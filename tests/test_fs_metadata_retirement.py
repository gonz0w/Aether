# SPDX-License-Identifier: BSD-2-Clause
"""Relocated observations preserve actual retirement guards and fixed profiles."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_fs_metadata_failures as prior

ROOT,af07,harness=prior.ROOT,prior.af07,prior.harness


class MetadataRetirement(unittest.TestCase):
    command=prior.MetadataFailures.command

    def test_only_observation_locations_change_and_no_extra_records(self):
        writer=(af07.VOLUME/'spa-zpl-write.inc').read_text()
        startup=(af07.SERVICE/'engine-startup.c').read_text()
        moved,entry=af07.retirement_sources(writer,startup)
        strip=lambda s:re.sub(r"    (?:aether_engine_utc_phase|engine_observe)\('[DJ]'\);\n",'',s)
        self.assertEqual(strip(writer),strip(moved))
        self.assertEqual(strip(startup),strip(entry))
        self.assertEqual(writer.count('aether_engine_utc_phase(')+startup.count('engine_observe('),
                         moved.count('aether_engine_utc_phase(')+entry.count('engine_observe('))
        with self.assertRaisesRegex(ValueError,'source context'):
            af07.retirement_sources(moved,entry)
        self.assertEqual(af07.FAILURE_GROUPS['retirement'],('metadata-nanos',))
        with patch.object(harness.tempfile,'mkdtemp',side_effect=AssertionError('must validate first')):
            with self.assertRaisesRegex(ValueError,'numbered diagnostics'):
                harness.campaign(False,False,'retirement')

    def test_actual_retirement_tail_and_compiling_omissions(self):
        moved,_=af07.retirement_sources((af07.VOLUME/'spa-zpl-write.inc').read_text(),
                                       (af07.SERVICE/'engine-startup.c').read_text())
        tail=moved[moved.index('    spa_close(spa, FTAG);'):].rsplit('}',1)[0].rstrip()
        fixture=(ROOT/'tests/fixtures/fs_metadata_retirement.c').read_text()
        import json
        tools=json.loads((af07.DELIVERY/'inputs.json').read_text())['tools']
        sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        with tempfile.TemporaryDirectory(prefix='aether-af07-retirement-') as temp:
            out=Path(temp);source=out/'tail.c';binary=out/'tail'
            prefix=[tools['clang']['path'],'-isysroot',sdk,'-std=c11','-Wall','-Wextra','-Werror']
            source.write_text(fixture.replace('/* RETIREMENT_TAIL */',tail))
            self.command(prefix+[source,'-o',binary]);self.command([binary])
            for old,new in (
                ('    dmu_buf_user_evict_wait();','    if (mode == 99) dmu_buf_user_evict_wait();'),
                ('    if (error)\n        return 873;','    if (error == 99)\n        return 873;'),
                ('remaining || aether_pool_hooks_check_ordered()',
                 'remaining || (mode == 99 && aether_pool_hooks_check_ordered())')):
                self.assertEqual(tail.count(old),1)
                source.write_text(fixture.replace('/* RETIREMENT_TAIL */',tail.replace(old,new,1)))
                self.command(prefix+[source,'-o',binary])
                self.assertIn('AF07_RETIREMENT_ORACLE96',self.command([binary],96))
