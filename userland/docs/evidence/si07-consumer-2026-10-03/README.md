# SI-07 matched native consumer checkpoint — 2026-10-03

**Nine fresh independent Aether/QEMU replays pass.** The missing matched-input
and generation3 blocker is closed for this private AENSI001/ABI22 profile. This
accepts the bounded replay checkpoint; it does not close all SI-07/SUSTAIN gates,
implement sys-init policy or publish a supported SDK.

[Before-code plan](review.md), [technical findings](technical-findings.md),
[intake and artifact pins](preparation.json), [native results](native-results.json),
[independent trace controls](oracle-results.json), [owner inspection](inspection.json).
The producer seal809a1912dd46657001282146cdc22ff593935b822e2fe8623d1208c842107a6a
verifies382 packet members. All3600 indexed archive members and244 final source
members are verified; archived symlinks are checked as metadata and never followed.
Each ISO's actual kernel and native payload are extracted and compared to the
indexed artifacts before boot. The envelope binds exact userland parent/bytecount,
backend and owner images; each VM uses fresh local firmware variables.

The positive run completes five actual cycles at1–5 with3044 total/3004 idle ticks,
ordered0/0/17 terminals,15 reclaims and fresh-input authorized halt. Separate seeded
255/256/65534/65535 cohorts each execute a real command and halt with three reclaims;
65535 rejects the next65536 before admission. These are boundary witnesses, not
65535 sequential commands or a runtime reseeding API.

Both parent profile mismatch directions reject with110/17 terminals, no child
admission or successful completion, two reclaims and authorized halt. The full-width
cohort-divergence case confirms owner stop/terminal/endpoint/reclaim/stale assertions
with no worker admission trace. Initial65536 rejects before any command/worker.
Those two rejection fixtures end with an explicit failure marker, so the independent
oracle requires their specific proof and ordering rather than accepting generic
failure. Seven successful halt traces account for31 reclaims; divergence has a
separate owner cleanup assertion, not an independently exposed reclaim counter.

Nine independent trace comparisons reject242 deliberate corruptions, including
lost, duplicated and reordered events, wrong generations/status/resource facts and
extra worker/admission evidence. Native replay passes on the first attempt. Host
inspection initially used the production stack field name for boundary records;
its KeyError, source and partial receipts are retained. The corrected reader
explicitly handles the two declared model fields; native artifacts were unchanged.

All nine raw/ELF owner identities match the producer's scoped audit records.
ELF inspections pass; code maximum10000/16384, estimated stack3832/4088. These
reuse producer stack models and immutable-builtin assumptions, not independent
all-path stack proof. Backend6\n bytes are asserted inside the inspected owner
before command-complete; UART exposes those assertions/terminal facts rather than
a second direct backend-byte channel. See technical findings for exact limitations.

Commands: `python3 -B docs/evidence/si07-consumer-2026-10-03/run.py prepare`, then
`.../run.py replay`, `.../check-oracle.py` and `.../inspect.py`. Preparation/replay
reject reuse to preserve attempts; restore the retained work archive or select a
new dated packet for a new run. Exact executable hashes, argv, environment,90sec
inner/120sec outer bounds, inputs, serial/error logs and process-group cleanup
receipts are retained. No sibling writes/messages, standards pin or runtime source
changes. Original harness BSD-2-Clause; upstream and owner notices remain intact.

Next implementation: sys-init BG-067 consumes the matched ABI22 closure and defines
settlement of outstanding work before interruption/shutdown. Remaining Aether-native
child-bootstrap profile mismatch, malformed/stale/foreign schedules and partial/
poisoned-close cleanup need explicit owner fixtures and independent consumption.
Userland host decoder/transport controls do not fill those native gaps. Reader
approval, supported SDK disposition, persistence/packages and full M3/R1 remain open.

All839 files in the completed consumer work root (including fresh VM variables,
artifacts and failed host receipts) were archived and individually read back with
hash/size/mode/namespace verification before redundant output removal.
[Retention record](retention.json) identifies the recoverable archive/index under
build/retained-artifacts. Net reclaimed97,452,032 allocated build bytes. Selected
source, metadata, serial logs and cleanup receipts remain directly in this packet.
The producer's175MB archive and all earlier evidence remain untouched.
