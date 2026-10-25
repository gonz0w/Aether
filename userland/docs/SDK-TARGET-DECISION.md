# Exact SDK target consumer decision — UL-005

2026-09-07. **Accepted for the first private SDK data-transport experiment.**
This is the current userland task's scoped technical consumer decision under the
user's instruction to continue. It is not independent maintainer sign-off, source
trust approval, production toolchain qualification or native execution acceptance.

Accepted target: [exact target.kv](evidence/sdk-target-review-2026-09-07/target.kv).
SHA-256: `1b9c2fedc9cebba0785c4f4ec5157abaf580e886eae3cb8f809375a70062ab8e`.
The caller pin binds every byte of this target, including its two receipt hashes.
Both receipt hashes match [the prior selection](evidence/sdk-admission-response-2026-09-07/selection.json).
No selected receipt or SDK payload was changed to obtain this decision.

## Why the missing fields are acceptable in this scope

`build_os=unrecorded` and `build_arch=unrecorded` explicitly record absence of
historical observations. They make no host-compatibility or complete-build claim.
For this experiment, admission checks integrity of selected inert data and a
caller-selected profile; it does not execute a compiler or qualify a host.
Consequently the missing observations do not invalidate the scoped transfer
oracle. No fictional OS, wildcard, default profile or general permission to accept
unknown provenance is introduced. This resolves the earlier request to explicitly
revise the representation rather than synthesize historical observations.

The gap remains relevant to later reproducible-build, toolchain and release
claims. SDK-05 must record its actual compiler, host, inputs and flags, including
no host-library/header fallback. It cannot retroactively supply the original
build observations. Recovered historical facts or a fresh SDK build require new
receipt/target bytes, a new pin and a new review; never silently update this pin.

## Evidence and owner next step

Independent read-only checks verify exact target construction, both selected
receipt hashes and every path/hash/mode/type in the 235-file owner stage against
userland's own SDK/notice/receipt inputs. No extra payload files, links or special
files were found. [Verification](evidence/sdk-target-review-2026-09-07/verification.json)
records the identities. Owner transport tests were read, not rerun here.

pkg-mgr may proceed with a fresh complete registered package under its existing
reviewed SDK branches, using this independently selected target pin. Run real
export/import and retained recovery controls, preserving failed attempts and
unrelated state. Return descriptor digest, package records, exact target and
payload manifests, private-root locations, tested source/tool identities and
raw success/denial/recovery evidence. Do not relabel the unregistered candidate
as a completed package or overwrite its retained evidence.

The real-package provenance decision is resolved for this exact experiment.
SDK-01 remains partial until complete registration evidence is returned;
SDK-02–08 are NOT RUN here. Userland's next executable work consumes the returned
imported SDK for SDK-05, followed by static dependency and separately scoped
native gates. UL-005 remains active. No sibling writes or message sending occurred.
