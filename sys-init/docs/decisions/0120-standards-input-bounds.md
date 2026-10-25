# 0120 — Standards wrapper input bounds

BG-056 host verification slice, 2026-09-07. Bound each lock, manifest and payload
read to 1 MiB and release traversal to 2,000 entries including directories.
Require ordinary inputs, reject symlink components below the resolved script
directory, use nonblocking/no-follow opens and verify descriptor identity before
and metadata after reading. Decode lock bytes as ASCII; committed lock layouts
and their LF/CRLF behavior remain supported. No published pin changes.

Keep wrappers self-contained so copying a checker does not add an unrecorded
helper dependency. Apply the same small reader to all three wrappers, with
cross-wrapper tests. Preserve child execution/environment and successful output.
Test special files before open, size/entry limits and controlled replacement;
run focused controls, real pinned checks and the full aggregate. Preserve failed
attempts and native inputs. E-01–08 apply; no native/shared API change is made.

Filesystem I/O deadlines, atomic directory traversal, verify-to-execute identity,
interpreter closure and independent review remain separate BG-056 follow-ups.

Validation: twelve focused tests across three modules pass. All ten gates pass
in out/checks/run-fq54cl5_; three standard stdout streams match decision 0119.
Locks and 24 native inputs are unchanged. Initial input tests also discovered an
imported test class (eight instead of four cases); module import fixes discovery,
and the growth hook now mutates once. Both passing runs are retained. Initial
manual lint warnings were corrected; all twelve final lint/render commands pass.
See ../evidence/standards-input-bounds-2026-09-07/README.md.
