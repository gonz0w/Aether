# Control authority review — 2026-09-06

Selected source/document review, not a new native run or full-source build pin.
reviewed/ contains 12 Aether files and three central standards files captured from
mutable sibling checkouts. reviewed-files.json records hashes, verified against
source immediately after capture. Git HEAD is context only; file hashes identify
reviewed bytes. Neither sibling was modified. Existing consumer pins are unchanged.

The review finds owner-bound private channels and broker namespaces useful for a
single-client control experiment, but no accepted sys-init reconnect/revocation/
effect-acknowledgment composition in the reviewed contracts. Current command
producer reports remain their owners' evidence, not additional sys-init outcomes.
The central release registry still lists the existing three v0.1.0 consumer pins.

`python3 scripts/check-all.py` passes in this checkout: 99 model tests/nine
controls, 48 host, 37 harness and all offline gates. validation/ retains exact
reports and raw logs. Native audit checks 215 historical outcomes; no new target
execution is claimed. New review/specification/decision links were checked for
local existence; `git diff --check` passed for tracked changes.

source/ retains the final review, requirements, follow-on planning and relevant
existing facade/delivery code. OQ-021/022 and BG-050/BG-032/BG-033 keep unanswered
binding and driver-recovery work visible. No runtime code changed and no new test
coverage is claimed. Result-only Markdown notes were added after full checks;
quality inventory matches the run. SHA256SUMS.json binds all files except itself.

A01–A03 trusted policy tests are next. Native endpoint enforcement is distinct
from service scope or human authentication, and an authorized request cannot
justify disclosing an out-of-scope conflict snapshot. Revocation must stop future
progress without erasing already-owned work. No independent owner sign-off,
shared ABI acceptance or new kernel interface request is implied.
