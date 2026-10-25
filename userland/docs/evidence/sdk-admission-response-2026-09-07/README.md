# UL-005 admission review and receipt selection

Read-only independent verification passes for 232 staged payload files and 4557
captured kernel source files. verification.json records current owner document
hashes and results. sdk-native-profile preserves the original libc evidence bytes;
its libc_receipt_sha256 matches the selected SDK receipt. sdk-build-receipt captures
original build/configuration/patch records with hashes and labels incomplete host
provenance and later tool observations. selection.json identifies both exact files.
No native execution, package admission or source-trust claim follows.

Review: ../../SDK-ADMISSION-RESPONSE.md. Plan: PLAN.md. Current-task technical
review checked native versus host identity, target versus native-receipt pin,
manifest binding, recovery and output-delivery semantics. Independent technical,
maintainer and native producer acceptance remain separate. First verification
attempt passed; no production code, sibling or immutable input changed.

Unresolved: original build-host provenance for canonical target construction,
owner parser/transport implementation and real package controls, imported-SDK
consumer adapter closure, static rebuild and native execution. No new exception
or fabricated host observation is introduced. UL-005 remains active.
