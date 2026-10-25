# Linux EHT-01 qualification — 2026-09-07

Decision 0149: eight seeds pass all 54 cases on Linux arm64 (432 executions,
zero skips). The pinned cached image is the same ID/digest used by the earlier
Linux witness. Complete worker records, plan and all corpus/implementation hashes
match the retained macOS campaign and current source files.

`linux-attempt/` retains the exact read-only source snapshot, image inspection,
startup output, container command/status, separate worker logs, campaign report
and named-container cleanup result. `container-driver.py` is the exact orchestration
used (its temporary path locator refers to the original working run). Networking
and image pulls were disabled; resources and privileges were bounded in the
recorded command. No sibling repository or native runtime inputs changed.

The campaign ran on Linux 6.18.10-200.fc43.aarch64, Python 3.13.12 with glibc 2.41.
Its approximately 17.87-second duration is one observation, not a comparative
performance claim. All ten macOS development gates passed in `validation/`;
full current Linux gates were not run by this campaign. `review.json` records
unchanged native inputs/audit output, catalog and three release locks.

Separate command sessions again lost connectivity after startup. Keeping startup,
inspection and execution in one live session succeeded. This suggests execution
session lifetime affects VM availability; it is not a conclusive guest-failure
diagnosis. Earlier failed attempts remain in decision 0148's evidence. No VM
recreation, new image, persistent scheduler or system helper installation occurred.

This qualifies EHT-01 in the recorded container only. Current full Linux gates,
BSD/illumos, independent reader/technical review and hosted scheduling remain
separate work. No native, PID 1, physical hardware or release acceptance is claimed.
