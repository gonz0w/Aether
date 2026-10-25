# V4 file-description and descriptor boundaries

Final qualification passes387 command cases and98 Python host tests, including
offline pin/workflow checks. The failed first attempt is retained below.

This packet records the existing command suite's bounded descriptor client,
separate from the unchanged actual dash script-execution case. Final counts and
source identities are in qualification.json. Queued-body and ambiguous-reply
recovery remain outside this qualification.

The client opens hello.sh twice and rejects a third simultaneous description.
It duplicates the first descriptor to10 with CLOEXEC, compares successive four-byte
reads through original and alias, and independently reads the first four bytes
through the second open. Public write returns EACCES with no transport call.
Ten additional stream aliases fill the16-descriptor table; open must return
EMFILE without traffic. Closing these aliases and the original file descriptor
must also cause no remote close. The remaining file alias reads the nine-byte
suffix including the final newline, reaches EOF and closes the description.

After both descriptions close, a reopened file has a new reference. Direct old-
reference and wrong-binding reads return EBADF with zero payload. CWD-root and
write-rights substitution return EACCES; a missing basename returns ENOENT. The
new file still reads its first four bytes, demonstrating unchanged offset after
those rejections. Three more open/read/close cycles start at offset0 and consume
the six-open limit; another open returns EMFILE without poisoning the client.

Normal completion requires client0, empty streams, exactly six successful opens
and nine reads, no live file records, and client0/stream17/file17 terminal order
across two generations with six reclaims. The final wrapper checks one file
CLOEXEC duplication at or above10. FD exhaustion and nonfinal close use the
existing test-only transport counter, enabled for this fixture.

Two deliberately broken owner selections must each fail client114/owner1501:
omitted offset advancement returns repeated bytes through the alias; ignored
reference matching lets an old reference reach the reopened description. Neither
claims native recovery or reclaims. Outer VM teardown remains separate. The
unchanged real-dash test and all prior command profiles remain in the full suite.

## Retained attempt

command-runner-suite-aaus5pse passed11 cases, then the new positive descriptor
case exited114 and the owner rejected1501 with zero reclaims. Source review found
the test expected an eight-byte suffix, omitting the script's final newline:
the17-byte script has nine bytes remaining after its first eight. The failed run
and sources were retained before correcting the expected count and comparison.
This was a test-expectation defect, not a passing negative control. The final
run uses corrected frozen sources; attempt.log, attempt-results.json and
attempt-sources.tar.gz preserve the failed qualification. Its artifacts are
included in target-artifacts.tar.gz. The passing preflight host log is retained.

## Scope and reproduction

This adds a conformance client and optional owner mutations/counter selection,
not a new production descriptor service, shared protocol or resource quota.
No kernel API, sibling, SDK default, upstream object, service engine or release
pin change. Compact C conventions remain under DEVELOPMENT's migration exception;
Rust uses edition2024 formatting. No fresh M4 run: the counter is test-only and
shared kernel/transport behavior is unchanged outside this native fixture.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 scripts/check_workflow.py
python3 docs/evidence/shell-file-descriptions-2026-09-09/collect.py
```

The collector verifies final runtime sources, the prior sealed admission packet
and simplicity snapshot, and reads back archives. The recursive manifest seals
all evidence. Independent consumer acceptance, V4 queued-body cases, malformed/
lost replies and confirmed service-stop recovery, actual-main ENV, persistent
OpenZFS and assembled serial-shell release work remain open.
