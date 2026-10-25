# Candidate qualification after intent fix — 2026-09-06

Local unpublished 187-file candidate, including checked replacement intent digest
assignments and ten prepare/finish hash-failure controls. No tag, signature, upload,
independent review or publication approval is implied.

Archive SHA-256: `28d7b300bf8e9f68b101ae2805cdca5fb3cde098e1211c2e50f0765da0124428`.
Retained archive:
`/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-release.c7yws0w2/pkg-mgr-0.1.0-candidate.tar`.
Size: 1,013,760 bytes. Repeated assembly yields identical bytes; host tar extraction
matches the selected file bytes/modes. artifact.json identifies the assembly root;
input-files.json binds the exact original dirty-tree inputs, SOURCE-MANIFEST.json
binds the public edition, and documentation-edits.json records omitted references.

Six selected input files changed since the previous qualified candidate: the
replacement helper, its binary fixture, replacement contract, development inventory,
host setup and release plan. No files entered or left the allowlist. See
changes-since-previous.json. The setup documentation now records missing original
Apple installation inputs and the requirements for qualifying a captured builder.

Selected checks run from the extracted archive: host preflight, the normal
sixteen-fixture suite with its 600-second process-group watchdog, and required
manual rendering/lookup plus the compiler-dependent bytecount example. The latter
workflow has a separate 600-second invocation deadline. These independent private
root checks overlap; timings are not comparative performance measurements.

Host preflight and all required manual/bytecount checks pass. Host-result and
manuals/result records identify tools and exact inputs; logs and rendered pages
are retained. Installed-tool observation does not establish reproducible tool
acquisition, a clean independent builder or complete SDK byte closure.

Full-suite outcome and post-test integrity verification are recorded separately.
The two extra transaction repetitions on the previous archive do not count as
repetitions of this archive. No unexecuted checks are carried forward.

Remaining release gates include captured builder setup and an independent witness,
broader boundary/failure qualification, independent content/reader review, a
monitored security contact and publication approval. This does not establish
physical full-storage or power-loss durability, native execution, concurrency
safety or Linux/BSD support. No live prefix or sibling repository was changed.

All sixteen fixtures, three pinned standards gates and whole-shell lint pass from
this archive, including the ten intent hash failures and normal/recovery cases.
The source corpus and live minisign fixture verification also pass. suite-result.txt
records the measured run and deadline. Post-test verification confirms all 187
selected file bytes/modes, the manifest and retained archive digest are unchanged.
This is one transaction-fixture run on this candidate, not a soak test.
