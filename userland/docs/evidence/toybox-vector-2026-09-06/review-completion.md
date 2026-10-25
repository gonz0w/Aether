# Scoped technical review

Current-task review checked complete pre-copy validation, bounded16-byte ordered
copy, one-callback/no-retry behavior, zero-progress error, strict result validation,
shared-state poison and re-entry. Unknown count0 is explicitly not no-effect proof.
The callback still owns liveness/rights enforcement. Valid empty input calls it;
invalid trailing vectors are rejected before any read/callback. No pointers are
retained and no allocation, descriptor cleanup or thread safety is implied.

36,992 host scenarios, eight boundary controls and three compiled semantic mutants
pass under UBSan. Strict C17 warnings/format, three CLI controls, Python3.12 grammar
on the actual recorded interpreter and quality gate pass. Minimum-version runtime,
real libc-loop integration, native authority and process-mask implementation remain
open. Same-task technical review only; independent and owner review pending.
