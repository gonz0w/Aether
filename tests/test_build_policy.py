# SPDX-License-Identifier: BSD-2-Clause
"""Require review when the build gains an unclassified boolean option."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    'native-fs-owner-stack',  # Separate approved ABI31 stack/measured code profile; same backing, release rejected.
    'native-fs-owner-data',  # Approved ABI30 private8192-byte owner mapping; same backing, release rejected.
    'native-fs-session-init',  # Explicit16384 immutable owner; same combined quotas; release rejected.
    'native-fs-session',  # Separate fixed seven-domain storage/SESSION closure; release rejected.
    'native-service-lifetime',  # Separate owner27 storage self-park/tick lifetime; old bounds intact, release excluded.
    'native-service-zpl-budget',  # Approved fixed6000-tick diagnostic; no authority/quota bypass; release rejected.
    'native-rtc',  # Read-only bounded raw source; existing live thread authority.
    'native-service-block',  # Explicit region-v2/service backing composition; authority unchanged.
    'native-service-channel',  # Opt-in atomic checked endpoint transfer at worker admission.
    'native-service-channel-wait',  # Private ABI26 primary wait; helpers/authority/quotas preserved; release excluded.
    'native-service-activation',  # Approved separate8KiB supervisor code; private BSP/wait/cleanup only, release excluded.
    'native-clock',  # Opt-in BSP source/absolute wait; existing authority and limits.
    'native-service-workers',  # One larger owner; small companion views and grants preserved.
    'native-service-cleanup-trace',  # Default-off scalar observations; cleanup/authority checks unchanged.
    'native-service-memory',  # One explicit larger owner; small peers and authority preserved.
    'native-backing',  # Explicit bounded physical binding; quotas/rights unchanged.
    'native-thread-origin',  # Same bounded domain grant; exact-ID operations and caller mask.
    'native-thread-reuse',  # Explicit bounded lifetime profile; live quotas and checks preserved.
    'native-entropy',  # Explicit per-domain bounded grant; no enforcement bypass.
    'native-session-lifecycle',  # Separate SESSION clock/park/halt; no quota or authority bypass.
    'native-init-sustained',  # Explicit serial init profile; authority remains enforced.
    'native-pipeline-capacity',  # Separate bounded five-worker profile; old limits preserved.
    'native-exec-denial',  # Exact bounded failed-exec completion, no authority bypass.
    'native-process-exec',  # Frozen same-identity image replacement, publication gated.
    'native-copy-signals',  # Explicit bounded signal-copy experiment.
    'native-process-copy',  # Checked private copy with explicit supervisor authority.
    'native-process-freeze',  # Cooperative parking; creation remains supervisor-owned.
    'native-image-large',
    'native-memory',
    'native-runner-local',
    'native-runner-files',  # Exact six-reclaim composition; no authority bypass.
    'native-parent-identity',  # Bounded direct launcher, no PID authority.
    'native-signal-suspend',  # Opt-in child notification and atomic suspension.
    'native-signal-public',  # Experimental actual-musl action routing.
    'native-signal-mask-delivery',  # Private successful-mask return boundary.
    'native-signal-termination',  # Private owner contract, not legacy consumer adoption.
    'native-signal-actions',  # Opt-in checked copies, not a validation bypass.
    'native-memory-large',
    'native-thread-pair',
    'native-threads',
    'release-artifact',
    'smp',
}
NEGATIVE = {
    'native-clock-ticks',
    'native-clock-skip-wait',
    'native-service-workers-skip-rebind',
    'native-service-skip-image-budget',
    'native-backing-skip-alias-ro',
    'native-entropy-skip-quota',
    'native-exec-copy',
    'native-exec-early',
    'native-exec-token',
    'native-copy-signals-drop',
    'native-copy-signals-pending',
    'native-copy-signals-parent',
    'native-copy-slot-tid',
    'native-copy-fail-stage',
    'native-copy-skip-zero',
    'native-copy-share',
    'native-copy-lose-anonymous',
    'native-freeze-skip-park',
    'native-freeze-ignore-token',
    'native-signal-actions-shared',
    'bad-display-message',
    'bad-ipc-test',
    'bad-lifecycle-abi',
    'bad-smp-ipc-test',
    'bad-stream-generation',
    'bad-user-test',
    'drop-remote-terminal',
    'drop-terminal-test',
    'fail-lifecycle-supervisor',
    'fail-smp-supervisor',
    'native-child-same-id',
    'native-coexist-small-pool',
    'native-init-large-dirty-tail',
    'native-init-skip-deadline',
    'native-mask-skip-inherit',
    'native-memory-deny-protect-once',
    'native-memory-no-grant',
    'native-memory-skip-protect',
    'native-memory-skip-zero',
    'native-no-output',
    'native-requeue-skip-move',
    'native-skip-fp',
    'native-skip-zero',
    'native-threads-skip-pin',
    'native-wait-skip-compare',
    'native-wait-skip-pin',
    'native-wake-unlimited',
    'no-framebuffer-grant',
    'no-timer-test',
    'panic-test',
    'skip-ap-test',
    'skip-ap-timer-test',
    'skip-display-draw',
    'skip-remote-discard',
    'skip-remote-unmap',
    'skip-remote-zero',
    'skip-unmap-test',
    'skip-zero-test',
    'wide-transport-test',
}


class BuildPolicy(unittest.TestCase):
    def test_complete_boolean_classification(self):
        source = (ROOT / 'build.zig').read_text()
        ordinary = set(re.findall(r'b.option\(bool, "([^"\n]+)"', source))
        guarded = set(re.findall(r'negativeOption\(b, release_artifact, "([^"\n]+)"', source))
        self.assertEqual(ALLOWED, ordinary)
        self.assertEqual(NEGATIVE, guarded)
        self.assertFalse(ordinary & guarded)
