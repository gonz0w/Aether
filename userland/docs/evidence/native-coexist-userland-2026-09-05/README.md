# UL-047 retained evidence

Six independent ABI 7 coexistence cases and six fresh ABI 5 regressions pass.
See [workload and limits](../../../experiments/native-process/COEXIST.md).

- summary.json: ABI 7 input identities, commands and six outcomes.
- producer/: pinned completed owner summary, suite receipt and 155-file source archive.
- requester/ and source/: independent build receipt, ELFs and consumed local sources.
- Named case directories: retained serial/QEMU logs; ISO/envelope identities in receipts.
- abi5-regression/: separate six-case regression receipt, artifacts and logs.
- rejected-build/: initial opt-level=z linker-bound failure; no native execution.
- SHA256SUMS: inventory of this retained evidence, excluding itself.

Large ISO/envelope and intermediate build files remain under build/. Local documentation
copies in source/ record the pre-completion state consumed by the runner. No shell,
inherited-descriptor, whole-system conformance or performance claim follows.
