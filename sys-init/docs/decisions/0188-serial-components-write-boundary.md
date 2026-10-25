# 0188: Close selected malformed boot and write-EPIPE controls

2026-10-04 / BG-067, before-code scope. Complete the smallest remaining named
boot-to-shell controls: malformed primary/helper/spare ELF; zero primary length;
nonzero reserved envelope bytes;008 profile presented to the pinned009 kernel;
and actual owner reply-write EPIPE after a private confirmed child stop.

Simpler alternative: rely on exact host pins and older producer negatives. Keep
pins as the supported build boundary, but add these selected consuming negatives
to distinguish native rejection from a host guard. No arbitrary component trust,
exhaustive malformed matrix, fallback, recovery API or runtime refactor. Only one
private owner variant is needed for EPIPE; loader cases retain the exact normal
owner bytes. This adds evidence rather than runtime machinery.

Verify repaired normal owner bytes and sealed009 inputs. ELF controls alter one
magic byte of only the selected image; length/reserved/profile cases alter only
the named envelope field. Require full boot readback and exact unchanged prefix/
owner/other-module checks for each mutation. Native loader acceptance needs actual
M1 boot plus exact invalid-launch-ELF/envelope or profile-rejection reason, with
no owner boundary/admission/halt. Timeout or unrelated panic is failure.

Write control: at the first child's pending reply, actual stop0 causes native
signal terminal; the ensuing actual channel write must return-32, then the
unchanged positive-write guard must fail. No invented EPIPE value or cleanup claim.
Private markers prove the result/point. Inspect linked raw/ELF/builtin/stack before
boot; retain16KiB/4088 limits, bounded tool/native execution and owned teardown.
Check identity/semantic mutations, full local checks and immutable evidence.
Maintained runtime, pins, sibling repos and old traces remain untouched.

These are specific native parser and owner-write witnesses, not complete loader
validation, asynchronous recovery, TTY/POSIX or assembled release certification.
The fifteen-lifetime normal SESSION limit remains a product dependency requiring
matching Aether/userland owner decisions and delivery rather than a local quota
bump. Independent reader/assembled review remains separate.
