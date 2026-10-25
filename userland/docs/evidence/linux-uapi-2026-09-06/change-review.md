# UL-068 reference export review

- Requirement/plan: separate Linux UAPI view for UL-066's missing linux/version.h;
  final plan/source copies in harness, successful builder bytes and earlier plans
  retained per attempt. Scope is Linux reference headers, not native Aether.
- Rules/ownership: E-01–08, CD/CP, TD/TE and DP. Local userland development inputs;
  no shared API/release pin, sibling implementation or package policy changes.
- Dependency/provenance: official Linux 6.18.49 and GNU make 4.4.1 archive pins
  precede extraction; earlier Linux 6.6.156 pin retained. Headers preserve UAPI
  notices/Linux-syscall-note; GNU make and host helpers retain upstream terms.
  Source signer authentication/security maintenance review remains UL-016.
- Host tools: pinned Clang builds make and export helpers; original make bootstraps
  GNU make privately. GNU sed/rsync/sh/awk pinned for the final export. The first
  prototype did not separately pin those helpers; it is rejected/incomplete.
  Actual host SDK, flags, commands and generated helper hashes are retained.
  No claim of complete host OS/transitive-tool hermeticity.
- Filesystem: 6.6 export failed on host relocs headers. The 6.18 macOS-checkout
  export returned zero but lost case-distinct inputs and is rejected. Thirteen
  source collisions were found, eight in exported headers. A private 4 GiB
  case-sensitive APFS image preserves them. Initial unsupported APFSX spelling
  failed; documented Case-sensitive APFS succeeded. All 91,515 extracted regular
  source files match their archives; 1,028 exported headers are separately pinned.
- Lifetimes/authority/bounds: unique owned build directories, 240-second process
  groups with kill on timeout; no real-prefix install. Only the private data image
  was created/mounted; it is retained under build and detached after consumer
  validation. Final image hash and successful detach are in summary. Source and
  export archives preserve filenames without extracting onto the checkout.
- Tests/oracles: case-insensitive work root, empty export, changed header and old
  invalid export reject. Final export archive equals the recorded header inventory.
  Standalone kernel-only guard scan is empty. Five headers retain compound
  __KERNEL__ conditions under unchanged unifdef rules; lexical token absence was
  an overstrict initial oracle and was refined in the plan, not claimed as passing.
  Full semantic header audit remains pending. GNU consumers compile/link and pass
  17 Linux-QEMU tests; musl baseline inventory matches before/after consumption.
- Documentation/evidence: README/reproduction, source locks, coverage, BACKLOG and
  STATE updated; no user-facing renderer or shipped command behavior changed.
  All attempts, helper/source identities, collision findings and controls retained.
- Actual review: source/build boundary inspection and tests by this task;
  independent technical review, reader walkthrough and publication gates remain
  UL-061–063. No invented reviewer sign-off or security/performance claim.
- Decision: UL-068 complete for reference provisioning and GNU consumption.
  UL-066 retains BusyBox/upstream suites; UL-008/012/016 retain native TTY,
  packaging and trust. Any header/tool change requires a new view and consumer
  rerun. The image must be reattached before using the pinned include path.
