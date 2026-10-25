# UL-013 / UL-066 tr UTF-8 boundary

Characterize the pinned GNU tr candidate under C and C.UTF-8 without promoting
byte operations to Unicode support. Reuse the verified locale probe and runtime
closure. Each locale gets the probe plus four cases: ASCII case conversion with
non-ASCII input, alpha deletion, literal multibyte deletion and squeezing repeated
multibyte text. Ten executions. Pin exact input/expected output bytes before run.

For literal deletion, deleting UTF-8 é from éê! under byte semantics removes both
0xc3 and0xa9, leaving0xaa21 (invalid UTF-8). Character semantics would yield ê!.
For squeeze, byte semantics leave éé unchanged; character semantics would yield é.
Require those contrasts to remain visible. A passing characterization is not a
passing Unicode operation. No source, locale or candidate mutation.

Follow LOCALE-PLAN's SDK/owned-helper identity, isolation, licenses, bounds and
quality CP/TD/TE requirements. Ten10-second children inside120-second offline
container,512 MiB,32 PIDs,uid65534,no capabilities,private scratch,read-only inputs.
Capture command and cleanup receipts, UTF-8 decoding validity and separate
character expectations. Run syntax, ten actual cases and quality gate. New review
pending. Update coverage, provider packet follow-up, compatibility inventory notes,
BACKLOG and STATE. Native/Unicode-wide/POSIX support remains unclaimed.
