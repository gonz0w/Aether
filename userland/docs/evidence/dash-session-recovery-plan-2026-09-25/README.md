# UL-007 recovery workload preparation

The next consumer-owned workload is ready for Aether owner review and delivery:
[SESSION-RECOVERY](../../../experiments/dash-native/SESSION-RECOVERY.md).
It exercises early-reader EPIPE/pipefail recovery, a subsequent argv/environment
command, a healthy pipeline and final descriptor closure in one unchanged parent.
Three complete parent generations are required. Expected stdout is49 bytes and
stderr20 bytes; the existing helper remains unchanged.

Dash syntax and ShellCheck (--shell=dash) pass through the existing owned process
runner. Both finish with exit0 and complete cleanup, under30-second/16 MiB limits.
`inputs.json` binds script, expected output, helper, contract, manifest, tools,
review, driver and process helper before checks; copies are under `inputs/`.
`checks.json` and raw process logs retain the actual results. No retry was needed.

This is syntax/static preparation. Host execution, Linux reference and native
execution are NOT RUN. RECOVERY-01–06 remains NOT RUN. Expected logical work is
seven copied children and six helper execs per parent; the producer must reconcile
those expectations and freeze its exact phase/slot/generation/admission/wait/reclaim
oracles and resource fit before execution. No slot map, native error number, stack
approval or larger lifetime quota is invented by this handoff.

The current Aether STATE acknowledges completed SESSION acceptance and requests
new userland inputs. This packet supplies the first recovery increment, not failed-
exec/scratch/serial implementation. Existing SESSION-01–06 acceptance remains valid;
its immutable script, helper, proposal, expected streams and sealed evidence are
unchanged. The910-case native regression is prior evidence, not rerun here.

Codex technical preparation review is in `review.md`; independent reader and owner
review remain pending. No sibling implementation, released standard, real prefix
or shared SDK was changed. Full UL-007/M3/R1 and subsequent failed-exec, scratch,
serial, SDK/review, TTY and package/sys-init gates remain open.
