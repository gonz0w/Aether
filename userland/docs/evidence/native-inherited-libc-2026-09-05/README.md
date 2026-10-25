# UL-053 bounded inherited musl read/close evidence

Fourteen native outcomes pass: the nine admission/collection cases through libc
clients plus five adapter controls. [Workload and limits](../../../experiments/native-process/INHERITED-LIBC.md).

summary.json records the final input identities, commands and outcomes. producer/
retains the pinned 170-file archive, summary and suite report. clients/ retains
11 ELF variants, separate probe objects, link maps and inspections. Named case
directories contain serial/QEMU logs. Raw brokers, backend ELF and command logs
are at this root. source/ records final local runtime inputs before completion
documentation updates. ISO/envelope hashes identify large images left in build/.
SHA256SUMS inventories all other retained files.

superseded/ records the initial 14-case run before the connection-wide guard and
wire-counter checks were added. It is not the final acceptance set or 14 additional
claims. All 14 cases were rerun after that change. Negative fault cases prove
explicit refusal/no replay and expected workload rejection, not remote recovery.
