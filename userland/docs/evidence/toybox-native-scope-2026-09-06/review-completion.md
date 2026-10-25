# Scoped technical review

Current-task review traced bootstrap publication, bounded read/write/close and
bytecount finish against the existing Toybox startup/exit findings. The proposal
keeps unsupported arguments explicit, requires diagnostic authority before normal
startup, and puts finalization after callbacks/flush but before terminal exit.
It distinguishes consumed local bindings, remote acknowledgements and native
reclaim; no unknown close is retried. It preserves command errors and requires
nonzero status for failed cleanup. Fault/stop reclamation remains owner-supervised.

Current owner identities are compared separately in summary.json. Reference
manifests are fully verified and reused only as reference evidence; no runtime
was rerun for prose changes. Proposal links and the quality gate pass. All eight
native cases remain NOT RUN; owner and independent review remain pending. No
shared standard, runtime source, pin, package or sibling project was changed.
The stdin-only candidate is not proposed for general /bin/cat installation.
