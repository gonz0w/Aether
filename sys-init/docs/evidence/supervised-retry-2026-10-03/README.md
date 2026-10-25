# ABI22 bounded pre-effect retry — 2026-10-03

BG-067; decision0180; explicit AENSI001/ABI22/supervised developer composition.
The frozen bytecount workload remains the scope; no arbitrary application or
outside-effect recovery, shared ABI, published pin or sibling mutation is claimed.

Current owner admits at most one replacement after a known failed command before
any dispatched backend read/write, settled references and all three paired-owner
cleanups/reclaims. It resets the request retry budget after a new external run
request. Failure after I/O and exhaustion close admission, permitting halt only
after known cleanup. Unknown cleanup keeps ownership and rejects replay. Backend/
runner errors, partial publication and malformed protocols remain fail-closed;
this is not complete production error recovery. See ../../AETHER-BASELINE.md.

## Fresh evidence and commands

From /Users/cam/DEV/sys-init on the locked macOS arm64 tools:

```sh
python3 scripts/build-aether-baseline.py out/supervised-normal-final \
  --dependencies out/si07-loop/.deps --service-table --supervised --smoke
python3 /tmp/run-supervised-controls-final-2.py
python3 scripts/build-aether-baseline.py out/supervised-baseline-final \
  --dependencies out/si07-loop/.deps
python3 scripts/build-aether-baseline.py out/supervised-table-final \
  --dependencies out/si07-loop/.deps --service-table
python3 -m unittest discover -s tests -p 'test_harness_aether_baseline.py'
```

controls/driver.py retains the private control driver. It verifies the source,
tool and dependency inputs, compiles/inspects each test-only variant, then requires
exact raw/ELF reproduction before building its fresh private image and guest. The
private profile overlays retained candidate bytes and test cfg flags after verified
intake; it does not impersonate a public recipe profile or change its pinned normal
owner. Each result records actual compiler/kernel/QEMU argv and image hashes.

| Case | Actual result and forbidden outcome |
| --- | --- |
| normal-final | One useful bytecount cycle, terminal0/0/17,3reclaims,halt; no startup idle probe. |
| controls/once | Invalid option causes actual command exit64 before backend I/O; runner64/provider17; complete cleanup precedes retry marker. Epoch2 succeeds0/0/17,one completion,6reclaims,halt. |
| controls/exhausted | Two actual command64/runner64/provider17 cohorts; one retry,zero completions,6reclaims. Exhaustion closes admission; another r produces only blocked diagnostic,then h halts. |
| controls/after-read | Owner stops command after an actual6-byte backend read and before write. Observed terminal143/kind3 is explicitly asserted; kernel stop path emits no corresponding UART terminal line. Runner1/provider17,3reclaims; no retry/completion,failed-state halt. |
| controls/unknown | External close of terminal command reader makes actual cleanup returnEACCES13. Owner retains reader/worker ownership, replay is Closed; exact marker precedes fixture failure. No retry/completion/halt or next epoch. This is a deliberate ownership disturbance, not spontaneous ambiguity. |

Five fresh consuming cases use one-core TCG,256MiB,no NIC,private firmware variables,
90-second guest deadline and4MiB serial budget, with owned child-group shutdown.
Normal and control ISOs stay in their named out/ roots; retained result hashes bind
them. Known cleanup is verified by owner resources, stale native handles, paired
close/reclaim outcomes and subsequent fresh epochs. No UART reclaim-per-event
marker or full race/performance proof is invented.

baseline-final and table-final reproduce their prior owner.raw,owner.elf and
envelope exactly using pinned module snapshots. The current maintained source
continues in the explicit supervised profile. The old runtime workloads were not
rerun for identical images. intake/ captures the inspected candidate; its source
predates an inactive test-only stop diagnostic. normal-final reproduces its exact
raw/ELF from final maintained sources, so the scoped inspection can be reused.
Code11,080/16,384; stack2,744/4,088 usable. Controls range10,056–11,224 bytes and
2,728–3,016 stack. indirect-review.json verifies immutable memcpy/memset pointer
values and register-load sites used by the conservative inspector; this is not
formal whole-program/kernel-stack proof or complete tool/library closure.

## Controls, failed attempts and process

Eleven focused tests include ten actual compiler policy cases: default membership,
role/image/order/zero-retry controls plus supervised command<=1 and backend/runner0.
The CLI rejects supervised selection without explicit table selection before output
creation. The aggregate receipt is retained after repository checks.

initial-controls and second-controls preserve native failures. diagnostic-control
adds only a private failure-code print and identifies1403: the older fixture
required both aliases open, whereas this real early-exit payload had closed some.
The final owner accepts only the valid command alias subset at an observed terminal
and retires the remainder. A known early terminal also receives no bootstrap frame;
uncertain publication cannot retry. An intermediate after-read oracle incorrectly
expected a kernel stop UART line; the final control asserts the observed143/kind3
and uses its own scoped marker. Changed source initially failed older image pins;
frozen compatibility module selection restores exact bytes. No failed receipt or
historical seal is overwritten to pass a check. Bulk copied build caches/ISOs were
omitted from this new packet; original out/ attempts and their hashes remain.

The simple counter and conservative I/O flag reuse existing paired ownership and
epoch machinery. Never retrying did not meet the requirement; retrying every
failure could repeat effects. No new dependency graph, parser, backoff service,
journal or generic coordinator is added. Foundations O/I/E, scoped Distribution
service/release and Experience diagnostic/marker rules apply. New diagnostic
strings are fixed plain ASCII and contain no payload or usable grant. Released
pins and sibling sources remain unchanged. Local technical review is not an
independent reviewer sign-off. Remaining protocol schedules, matched environment
composition and assembled v1 acceptance are open.
