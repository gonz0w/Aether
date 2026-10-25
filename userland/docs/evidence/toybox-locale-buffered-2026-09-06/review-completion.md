# Scoped technical review

Current-task review checked exact startup trace against main.c's setlocale,
newlocale fallback and uselocale calls. The read observer queries actual codeset
without changing locale. Failure returns set ENOENT/ENOMEM; a failed trace write
exits90. Host UBSan controls independently check routing, allocation counts and
cleanup using host C locales. The real musl locale observations remain separate.
The uninstrumented control ELF reproduces the earlier artifact byte-for-byte;
buffered success and ENOSPC cases run that control, not the locale wrapper.

Eight QEMU Linux cases with exact bytes/status/trace and named cleanup pass.
Two invalid oracle expectations, four UBSan controls, three CLI checks, strict C17
warnings/format, Python3.12 grammar on the recorded actual interpreter and quality
gate pass. No separate minimum-Python execution is claimed. Original source,
objects, pins and retained evidence are unchanged. Same-task technical review only;
independent technical/reader review is pending. No locale resource-exhaustion,
Unicode conformance, target, authority or package acceptance is implied.
