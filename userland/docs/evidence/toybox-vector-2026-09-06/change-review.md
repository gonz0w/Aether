# UL-067 private stdio bridge plan

Specify the private two-vector write bridge and process-mask state; implement only
an independent host C17 vector-gather/callback candidate. No public writev, native
role carrier, musl replacement or umask stub. Validate both vectors and total before
copy/callback; gather at most16 bytes in order, issue one synchronous callback,
return short progress without retries. Zero nonempty progress becomes EIO; unknown,
malformed or recursive transport poisons the shared state and forbids later calls.
Caller owns admitted logical sinks and valid buffers. Model validation is not native
authority. Empty writes still validate the sink via the callback.

Test all split/empty/boundary positions, short counts, errors, malformed replies,
unknown result, no replay and re-entry with independent byte/status/call oracles.
Use pinned Clang21.1.8, strict C17 warnings, UBSan, format and owned60s commands.
Semantic mutants must compile then fail assertions. Retain all attempts and hashes;
quality/docs inventory checks required. O/I/E, CE/CC and TD/TE apply. Original code
BSD-2-Clause. Same-task review only; owner and independent review pending.
Process mask remains a proposal requiring actual process-local state and bootstrap
ownership, never a successful no-op. Native CAT cases stay NOT RUN.
