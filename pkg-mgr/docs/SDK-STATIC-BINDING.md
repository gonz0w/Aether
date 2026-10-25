# Static SDK inputs and package records

2026-09-07. A bounded SDK-07 package-record experiment now connects userland's
[local relink evidence](../../userland/docs/evidence/sdk-static-rebuild-2026-09-07/README.md)
to existing package registration, dependency views and exact record hashes.
[Owner evidence](evidence/sdk-static-package-2026-09-07/README.md) retains the
commands, roots, records, data bindings and non-mutating plan. No supported update
command, binding format or automatic rebuild mechanism is introduced here.

## Observed package boundary

A fresh private root imports the accepted real SDK. An observed sdk-static-probe
data package records a direct dependency on aether-musl-sdk and contains three
manifest-bound files: consumer.elf, link-inputs.json and sdk-binding.json. The
last binds the exact installed SDK record, link-input receipt and ELF hashes.
These JSON files are local experiment data, not a production package schema.
The ELF is stored as 0644 data and never executed or admitted as a native program.
An unrelated-data package has no SDK dependency.

Existing state.sh deps/rdeps returns the expected direct edge, excluding the
unrelated package. A plan comparing the bound SDK record with the exact same
record produces no requalification entries. Comparing with a separately observed
candidate SDK record identifies sdk-static-probe for requalification. This plan
is an explicit one-off experiment, not an installed update gate. Package names,
file hashes and graph edges do not grant execution or service authority.

The candidate observation root contains the real userland-modified libc archive;
all other SDK payload files match the baseline. Registration records its changed
manifest and fresh advisory observation. That record's identity can also differ
because observation metadata differs: the policy is conservatively based on the
whole record, not a claim that record hashes isolate only meaningful ABI changes.
No candidate descriptor is exported, no profile is newly approved, and generic
state registration is not SDK/native admission. Historical profile receipts in
that observation are not requalified by copying them alongside changed bytes.

Userland's original and relinked ELF hashes are identical, because the newly added
archive member was unused. Nevertheless its selected input receipt records the
changed archive. Capturing that relink with a new SDK-record/input binding produces
a different consumer package record. A hash-only comparison of the ELF misses the
input revision. Both roots pass ordinary state integrity verification and the
baseline root, SDK and consumer remain byte/mode-identical after the experiment.

## What the current tools do and do not enforce

[Package state](PACKAGE-STATE.md) enforces graph/name consistency and manifest/record
integrity. It does not interpret this experiment's static-input JSON or automatically
compare it with the currently selected SDK record. The experiment performs that
comparison explicitly; state verify succeeding is not static-link requalification.
Existing host bundle dependency fingerprints are a distinct transport contract.
The SDK package itself still has no declared package dependencies.

This witness covers one direct static consumer. It does not supply transitive
rebuild scheduling, option/adapter/toolchain change policies, candidate selection,
missing-binding admission rules, cycles, automatic relink or native compatibility.
The candidate consumer record captures separately retained userland relink evidence;
pkg-mgr did not rerun a compiler or native workload. Independent consumer review
and full SDK-07 update integration remain open. SDK-08's mismatched producer still
needs its own correction and executable acceptance.

[The read-only planner](SDK-REBUILD-PLAN.md) now implements a separate experimental
KV binding, missing/stale rejection, conservative transitive scope and exact
candidate pins. It does not silently adopt the JSON records used in this witness. Any later apply/replacement step needs its
own authority and recovery contract; this experiment does not reopen SDK update,
installed-payload deletion or service activation. Shared cross-project policy
changes remain owned by Aether-standards, with exact package formats owned here.
