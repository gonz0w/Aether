# UL-049 native connections evidence

Six independent AENMX001 / ABI 9 cases pass. Both client ELFs are rebuilt from
userland's own source against the tested strict-musl SDK. The pinned producer
provides the kernel, broker and file-service bridge/implementation.

See [workload, reproduction and limits](../../../experiments/native-process/CONNECTIONS.md).
summary.json records exact sources, commands and outcomes; producer/ retains the
165-file source archive, pinned summary and producer report. clients/ retains
build evidence, ELF inspections and binaries. Named case directories contain
serial/QEMU logs. source/ contains the local inputs captured before completion
documentation was updated. Raw brokers and backend ELF are retained at this root.
ISO/envelope hashes are in the receipt; large images remain in build/.
SHA256SUMS inventories retained files except itself. Earlier producer regressions
are separate evidence, not additional runs by this consumer.
