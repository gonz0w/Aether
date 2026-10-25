# UL-065 minimal Toybox reference plan

Contributor experiment, 2026-09-06. Source: source.lock.json; Linux x86-64 musl
reference only. Evaluate cat, wc, printf, test (including [), true and false.
No native acceptance or package installation. Upstream source remains unmodified.

Apply Foundations E, Distribution PX and approved CD/CP/TD/TE/DP requirements.
Use the existing pinned Clang/LLD and unmodified musl SDK. Explicitly separate
host generators from target compilation; retain configuration, commands, source,
tool/SDK hashes, ELF inspection and every failure. No source fetch during build.
Reject source/SDK drift, unexpected applets, dynamic linking and host fallback.

Local build deadline: 240 seconds per phase, private build directory, bounded
parallelism. Linux tests: existing pinned Podman image, no network, read-only root,
UID 65534, no capabilities, 512 MiB/32 PIDs, disposable scratch. Explicit candidate
calls under qemu-x86_64; no assumption about binfmt. Test container deadline and
owned-container cleanup must be recorded. Test data and upstream fixture shell
are owned inputs, not user-supplied shell text.

Planned independent cases: exact dispatch inventory; disabled command rejection;
true/false statuses; test true/false/syntax and bracket alias; printf literal,
format/escape and invalid format; cat binary/empty/missing file/full output;
wc byte/line/empty/missing file; deliberately wrong expected output control.
Run applicable upstream test files with direct candidate wrappers and distinguish
shell builtins/helpers. Missing cases/tools or zero discovery cannot pass.
Host sanitizer work is not part of this static Linux-musl cross-build; retain it
as UL-062 coverage, not a native safety claim. No performance comparison planned.

Review inputs, dependency/notice closure and native imports before recommending
admission. Maintain source trust/security-fix review as UL-016. Independent reviewer
pending. Update README, provider matrix, coverage, backlog and STATE with actual
results and remaining work. No manuals/renderer checks apply to this experimental
upstream build; preserve upstream CLI contracts and notices.
