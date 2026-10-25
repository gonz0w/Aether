# Guarded SDK independent intake

Before implementation, 2026-10-04; R1-03. Independently consume userland's sealed
native-error-guards candidate without changing any existing SDK, release pin,
kernel/runtime, sibling source, quota or normal boot image. Verify the producer
packet SHA256SUMS, full retained archive, selected SDK seal/archive and every
member before privately copying selected inputs. Recipes are inert source until
reviewed; no sibling recipe is executed.

Requirement: corrected realtime fallback returns the actual denied provider error
without converting caller data; physical/available-page sysconf returns-1 with
provider errno before reading a failed result. Both remain unsupported natively.
Independently compare libc archive members and staged headers against the old SDK;
only the two reviewed objects may change. No fake time/memory, successful missing
operation, ambient resource discovery or libc-wide promotion is permitted.

Execute one new public-API probe using the existing native memory adapter/driver.
Use copied, verified candidate bytes. Test realtime error/untouched caller buffer,
monotonic public/raw distinction, both page queries and raw resource denial,
identity/entropy/random-device denials. Paired isolated contexts must finish the
unchanged output/yield/terminal contract. Link the same check to the old SDK for
exact clock240 and page241 semantic controls; the latter deliberately repeats the
old unsafe branch only in its disposable isolated negative image. No returned page
count is treated as capacity. No engine or storage executes.

Relink the previously sealed actual startup/partial/adapter objects against the
guarded SDK, inspect imports/relocations and use unchanged actual parser/layout
copies for ordinary/large/W+X/TLS controls. Inspect actual executable instruction
families against the native x87/SSE-only save contract; inventory or CPUID dispatch
is not proof of safe selection. Unsupported CPU-state or providers keep engine
execution unavailable. No AVX/XSAVE feature or resource quota is added here.

Security: native caller buffers remain owned/mapped by the calling instance;
failed queries may not disclose uninitialized data or grant authority. SDK is
trusted user-space code for the service's data, not a smaller kernel TCB claim.
Malformed seals/path/member inventories reject before extraction. Preserve all
attempts/argv/timestamps/binaries, freeze inputs during qualified runs, full host/
pin/workflow and scoped syntax/format/simplicity checks. Archive/read back all new
members before removing only the owned workspace; do not discard older evidence.

Simplicity SE-01–05: consume the existing two direct guards instead of duplicating
them in a new libc shim or adding clock/resource policy to the kernel for this
test. Reuse the real memory fixture and loader, with exact old-library controls.
No compatibility mechanism is removed; cost is a private reproducible intake.
This closes independent consumption only, not real provider/startup qualification.
Update STATE/ROADMAP/FEASIBILITY/COMPANION-PROJECTS/THIRD-PARTY with scope and next
owner action. No new maintained entry point or workflow launch profile is added.

Setup attempt1 rejected an absolute historical Makefile symlink in the producer
retained archive. It was never extracted/followed. Retry reads its inert link
metadata for archive inventory only; selected SDK copy still accepts regular
sealed files exclusively. Preserve the failure and partial receipt.

Setup attempt2 compared the producer regular-file count7310 with all7647 entries
and rejected. Retry verifies7310 regular files plus336 directories/one inert
symlink, all read back under the archive hash. This corrects a local metadata
expectation, not a producer source or accepted payload discrepancy.

Setup attempt3 rejected the SDK file count: producer241 includes the seal itself;
its inventory lists240 payload files. Retry verifies both sets separately and
retains the failed local count expectation. Source member is startup.c in the
prior packet; selected copy uses that exact recorded name.

Native attempt1 rejected duplicate libc archive basenames before compiling. Both
archives legitimately retain1349 object occurrences/1346 distinct names. Retry
compares each ordered occurrence, not a flattened ar extraction that can hide
duplicates. Only the named two objects may change; retain the local preflight.

Native attempt2 links the positive image but rejects musl's local hidden zero
_DYNAMIC sentinel. Retry applies the already source-reviewed sentinel distinction
with actual symbol/relocation records to each fixture image. No external import is
waived. Preserve this failed local audit; it never entered a VM.

The retained fourth setup recipe depended on the failed root existing. Final
recipe permits a fresh owned root while still rejecting existing sdk/prior trees.
A separately recorded fresh replay qualifies it; paths/notices are unchanged.
