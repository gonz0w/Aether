# UL-077 — dash guest-test integration

Integrate the existing lifecycle adapter into twelve dash guest cases. Preserve
scripts, expected exits/output, trace names, image and isolation limits. Add only
the existing read-only /inputs bind, bounded /scratch tmpfs and fixed guest env.
Validate mount source as a trusted private build descendant and reject delimiter
injection before client calls. No writable generator support in this slice.

Snapshot the existing default Podman connection through an owned local query,
pin client bytes before querying and freeze explicit URL/identity for all cases.
Do not silently follow later default changes, start a VM, pull or alter siblings.
Record config selection, client and adapter identities; no secret bytes copied.
CP-01–03, O-03/04, E-01–08 and local UL-063 apply. Current Experience migration
exception covers existing internal progress/exception style; no new public CLI.

Run lifecycle models including mount construction/invalid path denial on 3.10.21
and 3.14.7. Run all twelve real guest cases with retained pinned dash/LLVM/SDK and
verify semantic oracles plus each container's absence. Existing UL-076 host adapter
is exercised in the complete runner. Preserve all attempts and compare script/output
identities to original evidence. Run quality and whitespace checks. Independent
review, writable generators and live creation/service-loss ambiguity remain open.
