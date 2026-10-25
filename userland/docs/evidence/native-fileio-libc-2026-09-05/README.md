# UL-055 shared-position musl file I/O evidence

Ten final native outcomes pass. [Results and limits](../../../experiments/native-process/FILEIO-LIBC.md).
summary.json identifies the final inputs, commands and outcomes. producer/ retains
the 172-file completed archive, summary and file-io report. clients/ retains seven
ELF variants, separate probe objects and inspection/link evidence. Named directories
contain serial/QEMU logs; brokers, backend ELF and build logs are at this root.
source/ captures runtime inputs before completion documentation updates. Large
images remain in build/, identified by receipt hashes. SHA256SUMS inventories all
other retained files. No new runs of older profiles are implied.

rejected-injection/ records the first attempt: nine cases passed, but dropping a
close before required writes triggered broker 985 before a reply existed. This is
not a passing dropped-reply control. The injection moved after the completed write
workload and all ten cases were rerun. Only the final set is acceptance.
