# Command-protocol stop candidate: capacity blocked

Date: 2026-09-08. No new native acceptance is claimed.

The candidate selects `success_stop` in the existing ABI9 command witness. It
consumes a complete first command read before backend dispatch or a reply. It
checks the exact request and zero file positions, asks the paired owner to stop,
then requires actual terminal143/kind3, EOF with no partial request, retirement of
both command file aliases, runner status1, one collection followed by ECHILD,
unchanged input, empty output, backend EOF/status17 and six reclaims over two
generations. A selected skip-retirement control is prepared but has not run.
This is a proposed bounded policy for a request with no backend effect; it does
not resolve interruption after an effect, graceful shutdown or operator input.

All four enforced stop links fail the original8192-byte assertion before native
execution. Attempt1 uses ordinary size optimization and direct field assertions;
attempt2 tries opt-level=z; attempt3 a separate stop helper; attempt4 compares the
exact32-byte request. A private non-inlined native observation experiment also
fails and was reverted. No old evidence, released pin, kernel or userland input
was changed. Three ordinary variants build byte-identically to the prior accepted
positive/empty/fault scalar images in each attempt. Existing wrong-role/skip-close
cases use that same positive supervisor.

Measurement-only links for attempt1 and the final candidate are8336 bytes,144
above the limit. These raw sizing files are not valid executable profile inputs
and were never booted. The retained sizing linker removes only the code-size
assertion for measurement. Final sizing.json records its command and result.
The ordinary enforced linker remains authoritative. The final staged lifecycle
module was restored after the observation experiment.

Source/ contains the maintained candidate and its local owner modules. Earlier
candidate success.rs files accompany attempts1–3. The final driver records intended
native cases but stops on the rejected link; it is not evidence of passing runtime
checks. Frozen producer sources/artifacts and tool identities are those linked in
../init-command-intake-2026-09-08 and ../simple-service-pair-2026-09-07. Compiler
memcmp signature warnings remain the previously recorded compatible declaration
warning. Native-source changes add no unsafe sites or machine-output contract.

SE review: the requirement is bounded cancellation during actual file exchange.
The simpler alternative is the existing isolated stop probe, but it cannot prove
file-reference retirement or runner collection. Reuse the current state and
abnormal-terminal cleanup; no new manager or protocol is added. No production
path is removed. Rejected helper/optimization experiments do not remain in the
maintained candidate. Resolve the small code-capacity gap without dropping
ownership, protocol or terminal checks before attempting native execution.

BG-067 remains blocked at this enforced link, not on an inferred kernel defect.
A scoped code-layout review is next; a profile increase would require an explicit
producer handoff, not silently borrowing another profile. No sibling request was
sent. Independent review, sustained boot and operator shutdown remain open.

Full local checks are recorded after this snapshot. They cannot establish native
stop behavior. sha256.json seals retained files, excluding only itself.

Final local validation: all ten gates pass in run-2_nk5bb8, with checked sources
unchanged. Final staged/source copies and all three released lock hashes match.
`git diff --check` passes. No native cancellation acceptance follows from this.
