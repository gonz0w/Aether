# 0021 — Silent and malformed native readiness

Accepted 2026-09-05 as the next bounded BG-040 extension. Reuse decision 0020's
independently built worker and ABI-6 channel path. Add two explicit worker modes:
`silent` yields without writing or notifying; `malformed` writes byte 41 and then
notifies. The accepted one-byte fixture frame remains exactly 42.

Neither case may launch a dependent. Silent readiness must reach the policy's
absolute interrupt deadline and reject at assertion 920. Malformed readiness must
reject the first byte at assertion 921 before liveness or dependent admission
can promote it. The QEMU watchdog remains an independent harness failure and
cannot satisfy the silent deadline result. Both cases retain zero reclaims at the
assertion, localizing rejection before cleanup. These cases terminate at rejection;
they do not establish resource cleanup or successful retry. EOF (922), iteration
budget exhaustion (924), unexpected valid readiness (919), and adapter errors
(909) cannot satisfy either expected result. Successful admission and these
negative cases use the same readiness polling helper.

The worker mode is fixed supervisor startup data, not service-controlled authority
or a production descriptor. Byte 41/42 are bounded test frames, not a selected
wire format. The 10-tick deadline is delivered-interrupt time and has no implicit
millisecond meaning. Existing worker-return and prior adapter/service cases must
retain their expected outcomes. Rebuild and pin the worker because its source and
ELF change; do not rewrite decision 0020's retained evidence.

Acceptance requires exact target assertions, worker SDK/tool/source provenance,
unchanged frozen inputs, offline evidence audit and full development checks. This
does not cover multi-byte partial frames, flooding, helpers, production parsing,
health checks or worker exceptions. Exact lifecycle policy remains sys-init-owned;
no shared standard, ABI or Distribution descriptor changes.

## Result

[Retained target evidence](../evidence/native-readiness-failures-2026-09-05/README.md)
passes all 19 cases, including exact results 920/921. All seventeen prior raw
supervisors are unchanged despite the shared polling refactor. The two added
clients are 656 bytes each; all 178 frozen consumer inputs remain stable.
BG-040 remains partial: next specify rejection cleanup, replacement and fresh
evidence before dependent admission. No kernel extension is required for that
bounded follow-on; broader production timing and recovery remain contract-gated.
