# Scoped implementation review

The unchanged large profile already uses a64KiB exception stack; the default uses
16KiB (`protection.zig:kernel_stack`). The before-code note's unqualified16KiB
wording is too broad. At a future16,384-page quota one old slot array would occupy
32KiB, and thread creation keeps both stack and TLS plans live (64KiB before
frames, table plans and other locals). This is prospective stack headroom work,
not evidence of an existing default/large overflow. No stack size is changed.

Compared with the preceding sealed native-backing source snapshot, only Plan
storage/iteration, their map/protect/unmap and thread permission consumers, and
focused tests change. Complete backing/record/table/geometry/permission/context
preflight remains. The IF-clear BSP owner does not schedule or call a service
between constructor and consumption. Free iteration advances before publication;
range lookup uses virtual address, so earlier cleared records cannot change the
next lookup. Protect mutates flags only, detach first leaves metadata intact,
and zero/release clears only each visited record. No anonymous range is silently
shortened or partially accepted. No quota, authority, SDK, grant or launch ABI
changes. Range scanning adds bounded lookup cost; no latency or linear allocator
claim is made.

Plans remain internal trusted descriptors, not persistent snapshots: consuming
one after unrelated metadata mutation is an invariant violation, not a supported
concurrency mode. Current constructors and callers satisfy that obligation.
Independent reader review, general VM/map races and larger backing admission are
unqualified. A future cross-core/dynamic owner must define its own stabilization
and translation/reuse contract before reusing this iteration scheme.

Failures retained: the first nonadvancing cursor control hung on an occupied
record and was stopped by SIGTERM to its two exactly inspected owned processes;
this is not accepted semantic evidence. The skipping cursor instead fails the
exact expected1/found2 TestExpectedEqual oracle. The first suite orchestrator
mistook a separately owned M4 output directory for native memory output. Both
native memory suites actually passed with frozen sources; the retry recovers
those complete receipts and filters output ownership by suite prefix. That runner
also corrects entropy/block prefixes before their execution. Missing-file
`block_native_smoke.py --help` was a discovery typo; the maintained command is
`block_smoke.py --native`, with no runtime or acceptance claim from help.
