# Writable shell descriptor intake — 2026-09-14

Documentation and source review only. No writable-shell runtime result is claimed.
The [selected owner review](../../NATIVE-SHELL-STARTUP.md#writable-shell-descriptor-owner-review--2026-09-14)
records requirements, compatibility, bounds, cleanup, test selection and simplicity.

The unchanged userland manifest, three scripts and exact expected stdout are
captured in inputs, together with the helper and current consumer guidance.
Every script/output/helper digest matches the manifest. Expected shell exits are
22 for the deliberate leak control, 0 for redirection and 0 for denied redirection.
The helper source confirms that a live descriptor3–63 produces95. Reviewed source
copies show the current file/stream backend and descriptor integration boundary.
These copies are inert evidence, not build inputs or a second implementation.

Workflow and host checks pass; check logs and commands are retained. Host includes
all three offline standards checks. The simplicity manifest and four members verify.
All267 source hashes from the latest failed-exec qualification remain unchanged;
see runtime-identity.json. No runtime change, target run, new dependency, SDK
installation, sibling modification, released-pin update or independent acceptance.
No failed test attempt occurred. Initial discovery used a nonexistent helper path
and a shell glob with no matches; the manifest resolved the actual helper path
before intake. Neither discovery error was a runtime test or a qualification result.

Next implement the exact opt-in scratch records and bounded backend integration,
then root/rights/alias/lifetime controls before unchanged dash workloads. General
filesystem, persistence and R1 assembly remain open. No generated target trees
were created for this intake.
