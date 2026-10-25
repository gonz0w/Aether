# Time caller review and limits

Pinned OpenZFS2.4.4 commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1;
exact source/header/SDK and all prior packet manifests are retained and verified.
The queue selections remain four scalar expressions in the same three original
files. Only the libspl time header changes behavior in this packet. CDDL attribution
and style remain; full source, public dependency headers and compiler flags are
available in the archive. No Linux comparison configuration becomes native probing.

gethrtime checks CLOCK_MONOTONIC; the three wall helpers check CLOCK_REALTIME.
The current SDK denies both with an error. gettimeofday is unsuitable here: its
musl body ignores clock_gettime failure and returns success. Native attempt2
actually returns245 from wall-inode instead of expected125. Final wall helpers
bypass that body, preserving original successful microsecond truncation rather
than silently changing timestamp precision. Native attempt3 binds the identical
final header to all four denial cases. No SDK fix or UTC source is claimed.

Each checked read rejects nonzero status before examining output, negative seconds
or fractional values outside [0,1e9). No uninitialized value is used after a failed
call. Inode output is assigned only after validation. hrtime_t conversions reject
values beyond LLONG_MAX before multiplication/addition; wall nanoseconds truncate
to whole microseconds. Inode/seconds helpers can return nonnegative signed time_t
seconds beyond the hrtime_t nanosecond range because they do not convert to that
range. Pre-epoch wall times are explicitly unsupported by this experimental port.
_Exit125 avoids retry/error suppression; it aborts the service, which later needs
supervision and real terminal/recovery evidence. It is not an error-return API.

Actual289-object population is inventoried from original compiler/link receipts.
272 OpenZFS/generated inputs reproduce byte-identically;17 fixed zlib/libtirpc
inputs have no libspl wrapper include chain. Of234 header consumers,37 optimized
objects change;197 unchanged bodies are nevertheless rebuilt. Final guarded
-M scans bind the actual new header and exclude the old one. Generated kernel.c
and abd_os.c are existing prior adaptation inputs, not new edits. Four unchanged
startup support inputs are also inventoried. Original archive links are verified
as metadata and never followed/extracted. Compile paths normalize only historical
__FILE__ macros and original byte equality verifies equivalence with pinned Clang.
The preserved queue baseline ELF is03de1e4cbad1bbe3f20cce5963ad31de39fbe299b4bc9d67b685da4b704571d7;
final ELF is01e3be1ad6782b765348d703d8c459fd734935a7cdaa0a3cef47604ea79737f0.

Scope still excludes direct wait-clock callers. A scan of all272 rebuilt source
inputs finds three other direct clock calls: generated libzpool kernel.c373/413
(cv_timedwait/cv_timedwait_hires) verify gettimeofday status but inherit its false
success; lib/libtpool/thread_pool.c156 ignores CLOCK_REALTIME status before adding
linger. Signed deadline arithmetic and actual timed-wait progress need separate
qualification. Keep full engine entry unavailable until these paths are adapted
and required providers are real. This scan is source review, not an exhaustive
indirect-call/assembly/tunable or whole-engine security audit. The kernel SDK's
clock grants, UTC establishment, cross-core calibration and timer ownership remain
in the accepted CLOCKS-TIMERS direction. Existing virtual ticks are not a substitute.

Native helper admission uses the existing small memory profile and two primary
contexts; it does not place the full4.38-MB engine in that profile. Loader models
prove image geometry and semantic W+X/TLS denials only. Native service8192-page/
82-child limits, helper occupancy, actual heap/ARC/TLS and281 lifetime creates
remain unqualified for the engine. Selected counts do not mean four engine threads.
No scheduler/resource/quota changes or public ABI/SDK/owner acceptance occurs.

Failures are retained: build1 missing linker package path before commands; build2
missing two selected generated inputs after successful prior objects; build3 missing
gzip public header after265 inputs; build4 repeats that selection failure after
adding guarded dependency proof. Header-selection1 chose a wrong prefix and selected
nothing. Final5 includes only byte-verified required headers/sources and succeeds.
Host1 is an unrelated Linux-string/macOS-fortify compile conflict; host2 isolates
the exact time header, host3 adds the direct realtime port and host4 checks actual
sub-microsecond truncation. Native1 is compile-path routing error, native2 contains
one passing monotonic case and the real wall failure, native3 passes all four.
No earlier failure is relabeled passing. Optional process-list inspection was denied
by the sandbox; no escalation/process mutation occurred. All raw redirected logs,
recipes, artifacts, receipts and the selection error recorded from tool output remain.
