# ISO package test card

For Cam's deferred hands-on testing. Status: **not run; requires a package-ready
Aether ISO and matching persistent disk**. The [SDK document review](evidence/sdk-maintainer-review-2026-09-07/README.md)
is recorded. It does not need another confirmation, and does not substitute for
this target test. This card prepares the existing [bytecount workload](AETHER-RELEASE.md)
and [source-derived prerequisites](NATIVE-PACKAGE-PREREQUISITES.md); it creates no
new package/service interface, native identity or removal authority.

## Entry criteria

A bootable demo ISO alone does not establish these prerequisites. Record missing
items as unavailable and stop dependent steps; do not relabel a host executable
or use the cross-SDK build-input profile as native program admission.

| Supplied input / owner | Required identity and behavior |
| --- | --- |
| Assembled image / Aether and assembly owner | ISO hash, source revisions, selected native profile, boot instructions and serial log capture; actual shell/process/terminal services |
| Persistent disk / storage owner | Disposable disk identity, mount/root mapping, restart procedure and selected persistence/flush contract; the same disk survives reboot |
| Runtime tools / userland | Exact shell, Make and tool builds satisfying NATIVE-PACKAGE-PREREQUISITES, plus filesystem-backed execution, I/O and observable failure behavior |
| Package / pkg-mgr with build owner | Legitimate native bytecount 0.1 bundle, descriptor/target pins, build inputs, license and runtime evidence; admission must actually support that identity |
| Authority / service and execution owners | Caller-owned disposable root, independent filesystem/execute/I/O grants and service startup; a package path or import does not grant execution authority |

No delivered ISO/tool/disk selection or native bundle is invented by this card.
The current host/private-root command witnesses and matched SDK native probe are
supporting evidence only. They do not show bin/pkg-mgr executing on Aether.

## Test sequence and independent oracles

Use the exact init/import/list/files/verify/run command sequence already documented
in AETHER-RELEASE, with the selected native inputs. Record every command, exit
status and stdout/stderr independently. Keep observation logs outside the package
root where the image's granted facilities permit; otherwise document the logging
boundary before interpreting a missing result.

| Step | Required observation / pass criterion |
| --- | --- |
| 1. Boot and identify | Observed ISO/profile, selected tool versions and disk/root mapping match the supplied manifest; boot shell and services expose real failures |
| 2. Establish private test root | Existing caller-owned empty mode-0700 directory, marker/state initialization succeeds; preserve an unrelated sentinel in an agreed separate location |
| 3. Import the pinned native bundle | Exact successful receipt and zero exit; list/files identify bytecount and its expected payload/license; verify succeeds on all recorded bytes/modes |
| 4. Execute with exact input | Write exactly six bytes abcdef, run imported bytecount --decimal through the authorized path; independently read exactly two output bytes: 6 and LF; zero exit |
| 5. Save baseline | Retain record, manifest, payload/license identities, ordinary modes, sentinel identity and raw logs, bound to the ISO and persistent disk identities |
| 6. Reboot the same disk | Follow the agreed storage/boot procedure. Do not initialize a new package root, reimport or repair it. List/files/verify still succeed; saved record/payload/license/modes and sentinel match |
| 7. Repeat execution | The imported program still returns exactly 6 plus LF for the same six-byte input, with zero exit and independently observed output |

A missing result, failed command, changed sentinel or mismatched identity is not a
pass. Stop the dependent sequence and retain evidence. Distinguish ordinary failure,
infrastructure failure, unavailable input and unknown outcome. Do not rerun init or
silently rebuild the disk to conceal a persistence failure. A repeated successful
execution on a fresh root does not satisfy step 6.

This first card covers a positive import/run/reboot slice. Native interruption,
full-storage, corruption/recovery and denial-side reclaim need separately selected
fixtures and owner-defined oracles. Current host fault tests do not certify them
on the ISO. Do not improvise power cuts or destructive faults on an unspecified
storage profile.

## Result record

Record reviewer, UTC time, selected source/ISO/profile/tool/bundle hashes, exact
disk identity, grants, root path, commands and statuses. For each step record pass,
fail, unavailable or unknown, with actual output and retained file references.
Record the before/after comparisons and any deviations/findings. Do not enter
successful values from this card without observing them on the selected system.

A passing card establishes only this pinned positive package workflow and same-disk
reboot slice. It does not approve production security, all native shell behavior,
SDK update/apply or release publication. R1 removal is still a separate explicit
scope conflict: this repository prohibits installed-payload deletion. That gap must
be resolved before R1-05 can close; this test neither implements nor waives it.

Keep results with the selected image's evidence and link them from project STATE.
Until those inputs exist, continue local work against concrete findings and owner
handoffs without repeatedly requesting the already supplied SDK document review.
