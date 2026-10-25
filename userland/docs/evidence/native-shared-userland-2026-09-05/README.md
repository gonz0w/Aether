# UL-050 native shared-file evidence

Six native cases pass with independent userland clients. Two successful exit orders
and four exact failure controls consume the pinned shared-files producer on ABI 9.
[Workload and limits](../../../experiments/native-process/SHARED.md).

summary.json records inputs, commands and outcomes. producer/ retains the completed
source archive, summary and suite report. clients/ contains the four built client
variants and inspection evidence. Named case directories retain serial/QEMU logs.
Raw brokers, backend ELF and build logs are retained at this root. source/ records
local inputs before completion documentation updates. Large images remain in build/;
the receipt identifies their hashes. SHA256SUMS inventories all other retained files.
Producer regressions are separate from these six independent outcomes.
