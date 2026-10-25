# Session bundle Python3.10 qualification — 2026-10-03

The old builder and component validator failed on Python3.10 because they used
hashlib.file_digest. Both failures are reproduced on pinned3.10.21 before changes.
The two maintained hashing paths now stream SHA256 in1MiB chunks with APIs
available on3.10. No C/runtime, ABI, compiler recipe, SDK, owned helper or native
input changed. Previous candidates and evidence remain immutable.

Pinned Python3.10.21 and3.14.7 each pass ten controls, including valid empty/
multichunk inputs, missing/stale/duplicate/profile/symlink denial, wrong seal,
corrupt member and missing-memory rejection before linking despite cached fake
support modules. Fresh valid builds under both interpreters preserve cached
module/search-path state and reproduce exactly:

- Parent ELF:860b24b16e28e6fcaeb013a71d60c584750e99e240bd75bf7278b4a500591147
- Helper ELF:6b09427a7f35a06959b049f7373da72ad9ac4d52ee8a1b31a331dabcb96e5cf1

The prior49 native executions retain their exact-artifact scope; no fresh native
run or wider interpreter qualification is claimed. Independent reader/technical
promotion and full SSDK-01–06 remain pending. A new candidate.tar.gz with
candidate-SHA256SUMS supplies the corrected standalone build inputs. Select seal
`7d8689e797181750b28b900e1d4b86541da876cdfe8fdc59984dc770ceb485a4`
for new builds. Only support/rebuild.py, support/components.py and README differ
from the previous sealed candidate. All upstream/notices remain unchanged.

An initial intake rejected legitimate archive directory entries before any build;
the failed source and partial root are retained. The corrected intake admits
safe directory names, still rejects links/special entries, then verifies the full
external seal and exact file namespace before consumption. Native runs were not
repeated. Every build/negative/gate receipt, source snapshot and recovery archive
is retained. See [review](review.md), [before](before-results.json),
[3.10 results](after-310-results.json), [3.14 results](after-314-results.json),
[inputs](inputs.json), gates.json and retention.json. SHA256SUMS seals all packet
files except itself. No published release pin or sibling implementation changed.

Quality, syntax and whitespace checks pass. Both newly created work roots were
fully archived and read back (3754files total) before removal,
reclaiming32624640allocated build bytes. Native runtime, application and owned
helper hashes remain unchanged. To replay retained drivers, restore the named
work archive to its original build path; the standalone candidate archive is
delivered directly alongside this packet and does not require that work tree.
