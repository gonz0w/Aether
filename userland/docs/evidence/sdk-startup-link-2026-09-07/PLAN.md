# UL-005 imported SDK startup link slice

Rebuild the exact previously pinned native-c startup probe and external I/O/memory
adapters against the imported SDK. Verify source hashes against the original SDK
receipt before copying. Preserve sources/style; use C17 in this new experiment
with the prior diagnostic/native assembly options. No runtime or producer adoption.

Positive: explicit crt1/crti/probe/adapter/libc/crtn static link, no undefined
symbols/interpreter/dynamic segment. Negative: omitted crt1 must fail via fatal
missing-entry warning, omitted I/O adapter must fail with __aether_io, a missing
required memory object path must fail, and retained 128-bit division helper must
fail with its compiler-runtime symbol. Do not claim omission of memory adapters
necessarily fails: libc may supply unsupported fallback implementations.

Keep imported package/SDK and adapter/tool/source identities; private output root,
clean env, per-command 30-second process bounds and checked cleanup. Reuse leaf
header/libc controls. Missing tools/pins or changed source block before build.

## Amendment: receipt-pinned io probe

The selected libc receipt (`libc_receipt_sha256` in the stdio evidence.json)
pins `probe_sha256` to io_probe.c, plus io_adapter_sha256 and memory_sources.
Verify that receipt identity first. Compare live io_probe.c, native_io.c,
native_memory.c and memory_probe.c to those hashes before any compile. A
changed-source control must reject. Do not build probe.c for this closure.
Quality and whitespace checks. Host ELF evidence only; full ABI/runtime, static
rebuild SDK-07 and native SDK-08 remain open. No new dependency or sibling write.
