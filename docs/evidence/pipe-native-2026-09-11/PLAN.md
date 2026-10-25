# Native pipe wiring review

Requirement: connect the safe Rust core to authenticated native connections and a
private C descriptor adapter, using actual musl fork/copy and EOF before wait.
This bounded producer experiment does not install public pipe() or qualify SIGPIPE.

Use the existing two-lifetime inheritance harness: parent, backend and copied child
in slots0/1/2, repeated once after all three reclaims. Each lifetime owns a new pipe
object; process generations1/2 are independent of the pipe's generation1. The fixed
factory value remains valid only on that lifetime's authenticated parent route;
old routes are reclaimed before the next lifetime. No extra workers, channels,
generation quota, new kernel API or dummy-reclaim processes are added. The first
probe uses existing AENMX002 transport rather than serial AENMX003: both have the
required local connection/copy mechanisms, and no UART grant is requested here.
The later serial dash profile still uses AENMX003.

Send unchanged AECAT003 then AEPIPE01. The private adapter reserves two FD slots
under the existing mask, validates the complete reply before publishing either,
and poisons unknown responses without retry. Fork-plan v2 carries five bindings;
copy receipt validates all five references before rebinding. Keep old profiles v1
and unchanged. Reject STARTUP_FILES combined with the pipe profile.

Native probe: preserve CLOEXEC FD10; create endpoints at3/4, alias the reader to11
and close3; copy the actual process; child closes reader, writes320 patterned bytes
in16-byte calls, then exits0 without closing its writer. Parent closes writer;
a private op83 scheduling witness holds its read until the child has a full-buffer
pending write. Then parent drains exact FIFO bytes through EOF before waitpid,
checks real child exit0, closes remaining descriptors and exits0. Backend closes
only after the final stdio holder; two full lifetimes produce six real reclaims.
Op83 is a fixture witness only, not a public pipe operation.

Forbidden: unauthenticated wire identity, servicing staged child traffic, fake
exec or exit72, EOF while a writer lives, partial/repeated enqueue, reclaim before
wait acknowledgment, terminal release from a mere stop request, and caller retry
after unknown reply. The owner retains partial/pending32-byte frames per caller;
completed replies are sent once and transport failure contains the fixture.
Exact frame, bound, generation and close checks precede effects. Current finite
watchdogs remain failures, never successful pipe completion.

Selection before code: positive target workload and named premature-EOF/retained-
writer controls, complete matching connections suite and affected launch/console
regressions; host tests, Python harness checks, Rust/C formatting and standards
pins. Freeze and retain each attempt. Negative tests must fail with specific owner
or client status and reclaim context. Measure owner bytes against16KiB. Existing
mask/copy assembly remains unchanged; new unsafe operations are only existing
native transport calls on owned stack buffers. C output must be a valid writable
two-int span; arbitrary pointer recovery remains unqualified.

Simplicity: extend the existing opt-in fork adapter and use a focused pipe request
loop beside the exec-specific dispatcher; do not force pipes through fake exec or
add filesystem/service abstractions. Future dash integration will reuse these
boundaries; the narrow probe remains its regression. Existing SE-01–05/O/I/E/PX
clauses apply. No sibling, released pin or kernel change is planned. New C header
uses the pinned clang-format21.1.8 style; existing C remains scoped formatting.

Review addendum before errno fix: validate signed negative create replies against
the three allowed errno values before negation, so INT32_MIN never triggers signed
overflow. Add a zero-tailed INT32_MIN reply control. The client must report EIO,
poison transport, leave output/FD bindings unpublished and terminate with the
specific witness92. The owner observes that terminal and an empty request route,
retires the possibly created pipe only then, and aborts the deliberately corrupt
fixture with2167 and zero reclaims. This proves neither automatic caller recovery
nor continued service availability after unknown outcomes. Preserve the previous
full run as superseded review evidence, and rerun affected tests on final sources.
