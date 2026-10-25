# UL-067 bounded close-policy qualification

All27 local native cases pass. The candidate runs actual Toybox cat_main, then
upstream callbacks/flush and the selected APP_CLOSE_POLICY cleanup. Twenty-three
normal/error outcomes verify exact bytes/status and four reclaims in two generations;
four deliberate mutants require their precise rejection context.

The specific outstanding close-policy requirements now have local evidence:

- Input/output close failures emit exactly `cat: close failed\n` before stderr
  closes. Owner checks both input/output aliases retired before diagnostic writes.
- Diagnostic EIO/EINTR, malformed/cut replies and diagnostic-close failure preserve
  failure and the exact complete message or16-byte prefix. Short writes complete.
- Malformed/cut closes at all three aliases poison the transport; no subsequent
  traps occur, remaining local aliases retire and the owner verifies remote cleanup.
- Re-entry returns120 to the nested hook without effects and latches outer1;
  prior64 stays64. Ignoring the latch rejects1501.
- Actual applet read/write errors and uncertain I/O compose with this cleanup.
  Omitted diagnostics, false success and repeated consumed close reject1505/1501/1504.

[Native receipt](native/results.json) and case logs retain exact expectations,
observations, command records and artifacts. All209 owned commands report complete
cleanup. No failed runtime attempt occurred. [Review](REVIEW.md) records the explicit
diagnostic choice, source/owner review and remaining limits.

## Reproducible inputs

[Intake](intake.json) verifies the completed handoff, all declared dependencies and
archive6b56cc9709e70c416ff3e55a0cf63425ceb6b2945088bbaeffbaffd30750f821.
Only the probe and opt-in owner source changed from the previous finalizer snapshot.
Earlier snapshots and evidence remain unchanged. The producer's existing fresh
baseline recipe removes/rebuilds17 Toybox units and the adapter; the local driver
does not duplicate it. Patched xwrap, real musl callback, probe and owner are rebuilt
per case. SDK libc/CRT remain pinned dependencies. [Backend equality](backend-reuse.json)
checks all27 payloads against the already source-rebuilt local backend; no rebuild
or native reuse is inferred merely from labels.

```
python3 -B experiments/toybox-native/run.py --snapshot build/toybox-close-consumer-q91nkwbt --profile close
```

Original and adapted recipes, driver and process/tool/environment identities are
retained in the execution directory. Each command is bounded at180 seconds; the
pinned guest watchdog remains30 seconds. Outputs/ISOs stay under the recorded build
root. No installation, live sibling edit, network fetch, SDK/shared pin or oracle
change. Original/upstream licenses and machine markers are preserved.

## Acceptance boundary and next roadmap work

The named CAT-06 close-diagnostic, uncertain-close and repeat-hook gaps are locally
qualified for this bounded candidate. This is not arbitrary recursive/signal-safe
xexit or general installed cat. Independent review, the full CAT matrix and
new-revision regression assessment remain open. The locally passed213-case suite
belongs to the previous finalizer revision; the new producer supplies its own213
case result, which is producer evidence rather than a new local run.

Next consolidate the CAT acceptance matrix and review which changed paths require
further local regressions, while advancing the M3 native dash launch/process/FD
integration. Do not expand optional utility tuning. UL-067 and M3 stay active;
public registration, packaging, interactive TTY and general POSIX are not implied.
