# SDK/package handoff proposal — UL-005

For pkg-mgr and userland maintainers. This proposes the next private-root SDK
transport experiment using existing package machinery. It is not a recipe,
accepted package API, installable base selection or native ABI declaration.

The read-only [inventory](evidence/sdk-package-handoff-2026-09-07/inventory.json)
verifies all 231 SDK inputs against the retained native-stdio-files consumer pin.
Every listed input is a regular file with mode 0644; the current stage contains
no symbolic links. No package staging or runtime test was performed here.

## Candidate and identity

Candidate input is `build/native-c-xhkdw6jv`, the bounded source-rebuilt musl SDK
already consumed by command-runner and reviewed in
[the SDK audit](research/TOYBOX-NATIVE-SDK.md). Use that exact input for a first
transport witness, rather than treating the moving build script as its identity.

| Field | Proposed handoff requirement |
| --- | --- |
| Build machine | Record actual OS/architecture, Python, shell/make, environment and compiler executable hash for each rebuild |
| Compiler host | Pinned Clang/LLVM 21.1.8 executable runs on the provisioned macOS host; host SDK/system dependency closure remains incomplete |
| Compiler target | Existing Linux-musl source/build convention produces x86-64 ELF; it does not identify a Linux-compatible runtime or a production Aether triple |
| Runtime target | Exact kernel-owned bounded native C/memory/command profile, its producer source/artifact digest and build options; broader UL-003 ABI remains unresolved |
| Upstream input | musl 1.2.6 archive SHA-256 `d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a`; hash identity is not UL-016 source-trust approval |
| Static libc | SHA-256 `8f66b2b383eabd08b8f27c4913f36a91071c4cfb6373cedebd2e69cabfaaeecc`, plus exact installed headers/startup objects in the inventory |
| Adaptations | Retain original archive, native transport/scalar-hook transformation, strict metadata-protection patch, before/after hashes and native-libc-patches/build receipts |
| Build flags | Carry exact recorded compiler/linker argv and environment from the SDK build logs; no reconstruction from a target string alone |
| Compiler runtime | This SDK receipt says none linked and 128-bit division deliberately fails; do not import the Linux reference compiler-rt witness as a native dependency |

The SDK headers expose more interfaces than the native profile implements.
Package metadata must not imply successful implementations for unsupported calls.
Its native transport, startup objects and libc must travel together with their
identity and scoped evidence. The SDK inventory is input closure for the existing
consumer, not proof of a complete independently reproducible toolchain.

## Ownership and package-format gap

pkg-mgr already owns [bytecount host packaging](../../pkg-mgr/docs/BYTECOUNT-PACKAGE.md)
and [binary-directory v2](../../pkg-mgr/docs/BINARY-PACKAGE.md). The latter binds a
host OS/architecture, compiler target and manifest-bound host observation. It
supports regular file content and ordinary permissions, but rejects links and
special types. Directory modes, ownership, ACLs/xattrs and timestamps are not
preserved. Its host target validation cannot be relabelled as native SDK admission.

The [native-memory transport](../../pkg-mgr/docs/NATIVE-MEMORY-TRANSPORT.md) is a
separate bounded boot handoff. It does not establish general SDK package records.
Propose that pkg-mgr choose whether to extend its host-tool/data packaging scope
or introduce an explicitly reviewed SDK target record. Do not invent the wire
format here or weaken current target rejection. The initial proposal needs only
regular files; any future link-bearing SDK requires explicit owner support and
rejection/preservation tests. Preserve upstream notices, including musl COPYRIGHT;
verify their inclusion separately from the 231-file consumer input inventory.

Userland supplies sources, scoped ABI requirements, consumer closure and tests.
pkg-mgr chooses recipe layout, source capture, stage paths, package names,
dependency records, export/import and recovery. sys-init retains service policy;
installation or an SDK name grants no launch, filesystem or native authority.
New shared requirements belong in Aether-standards through owner review.

## Static rebuild and update rule proposed for owner review

Record each consuming ELF's exact libc/startup/header identities and applicable
adapter objects, compiler/linker inputs, flags and result hash. Updating libc or
an adapter requires rebuilding and requalifying every affected static consumer;
replacing an archive does not update code already linked into an executable.
Retain old inputs and artifacts for comparison/recovery. Detect stale reverse
consumers before selecting an updated package set. Existing pkg-mgr exact record
fingerprints are useful input, not proof this SDK dependency graph exists.

## Next owner experiment and acceptance

Choose an owner-reviewed package record/profile and capture immutable inputs
before running. Use a fresh private root owned by pkg-mgr, with all outputs under
its permitted build area. No real-prefix install or service activation.

| ID | Required result |
| --- | --- |
| SDK-01 | Stage the selected exact SDK files and required notices; record every path/type/mode/size/hash and compare before/after |
| SDK-02 | Export/import through owner machinery into a second fresh root; dependency records and all file identities/modes match |
| SDK-03 | Reject wrong host/tool/runtime profile, missing dependency, same-size byte corruption and altered ordinary mode before publication; retain unchanged unrelated state evidence |
| SDK-04 | Reject unsupported link/special entry and occupied destination; no following links or replacing another stage |
| SDK-05 | Compile/link a bounded consumer using only imported inputs with recorded argv; missing libc/startup/compiler helper must fail without host fallback |
| SDK-06 | Exercise interrupted publication/recovery using owner-supported semantics; separate acknowledged requests from confirmed publication and preserve owned partial state |
| SDK-07 | Change a static input in an isolated control; demonstrate stale consumer detection and explicit rebuild/retest dependency tracking |
| SDK-08 | Independently execute the exact resulting consumer on its matching native profile with positive/denial/cleanup evidence before any native package claim |

All SDK-01–08 are **NOT RUN for this proposed SDK package**. Existing host package
and native boot evidence inform these gates but do not close them. First owner
response needed: selected record/profile and stage layout, exact notice/dependency
closure, and review of target/rebuild/recovery behavior. This local proposal is
ready for review, not sent or accepted. UL-005 remains active until coordination
and the supported owner staging witness are completed; UL-003/016/012 retain ABI,
source trust and assembled supervised-base acceptance respectively.
