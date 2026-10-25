# Selected component-loader and actual reply-write EPIPE controls

2026-10-04 / decision0188/BG-067. Seven fresh consuming VM controls pass expected
rejection: malformed primary/helper/spare ELF magic, zero primary length, reserved
envelope byte,008 profile against the009 kernel, and actual owner reply-write EPIPE.

Loader mutations alter only the named byte/header field of the composed payload;
normal owner bytes stay exact. All other boot modules read back unchanged. Each
requires M1 boot and its exact invalid-launch-ELF/envelope or profile-rejected
panic reason, with no owner boundary, admission, terminal, fallback or halt.
These are selected native parser negatives, not exhaustive loader validation or
artifact authentication. The supported recipe still enforces exact host pins.

The write control stops the first child with an actual accepted stop operation,
observes native signal terminal(2,1,3,143), then actual reply write returns-32.
The existing positive-write guard rejects; unique result/failure/linked-UD2 markers,
exact parent/helper admissions, one fragmented prompt-driven command and no parent
completion/halt are required. Scoped owner15312 bytes/3864 stack fits16384/4088;
raw/ELF parity and immutable builtin inspection pass. No synthetic EPIPE result
or maintained runtime/recovery change is introduced.

rejected/write-admission-expectation/ retains the first actual EPIPE trace and
failed oracle expectation (it expected only parent memory admission; actual child
image admission already occurred before the pending reply). The corrected exact
two-admission oracle was pinned and a fresh same-image native run passed. Other
six loader traces were rechecked without redundant native boots. No failed attempt
is counted as qualification. Tools/input/harness pins and commands are retained;
no SDK/kernel/client source rebuild or sibling mutation occurred.

Bounds: tools180s/4MiB, guest90s/1MiB UART/4MiB stderr, owned live-group teardown and
reaping. Source/ELF inspection is scoped, not formal or SMP proof. Host teardown
is not cleanup of deliberately retained guest authority. Validation and semantic
trace mutations are retained; archives pin actual ISOs/payloads/notices.

The [acceptance matrix](../../SERIAL-SESSION-ACCEPTANCE.md) and
[lifetime handoff](../../SESSION-LIFETIME-HANDOFF.md) separate demonstrated bounded
boot-to-shell behavior from the continuing-use dependency. Full component matrix,
other error schedules, independent assembled review and release authority remain
explicit limits; no full POSIX, renderer, distribution or recovery acceptance.

Full local validation: all ten gates pass in out/checks/run-4fn1ruwp with checked
sources unchanged. Four focused host tests replay all eleven accepted traces and
semantic corruption controls; no omission/skip is counted as success.
