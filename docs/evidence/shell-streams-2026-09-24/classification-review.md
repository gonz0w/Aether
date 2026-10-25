# Host rejection classification

Attempt2 passes all105 cases. Its serial-byte tuple still carries the old2743
guest-panic annotation, although the serial driver correctly rejects host output
after successful guest cleanup. Remove that unused panic expectation: the final
harness must also perform ordinary positive admission, terminal and mapping checks
for this control, and record the expected host rejection explicitly in results.
Runtime/ELF bytes are unchanged; attempt3 reruns the full suite on final harness
bytes. Attempt2 remains retained as successful earlier-harness evidence.
