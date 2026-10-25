# UTC composition with corrected reaper — 2026-10-06

The maintained UTC builder now explicitly pins the corrected294-member elapsed-v3
seal and rejects obsolete elapsed v2. Provider/calendar/checked-wrapper source
bytes are unchanged; record ownership and native detached retirement come from
[the corrected elapsed runtime](../reaper-fix-2026-10-06/README.md).

Six final native cases pass: normal UTC date, Gregorian leap date, disabled RTC856,
absent source policy855, ordered overlapping detached exits and serial exits.
All use freshly linked exact archives and source-built frozen current kernels,
with app/kernel ISO module readback and complete owned cleanup. The UTC date
cases exercise checked clock/time/gettimeofday, helper establishment/close denial,
busy close and final lifetime. Overlap/serial checks link the full UTC archive;
they specifically check inherited elapsed retirement, without claiming RTC reads
in those ordering cases. Project-formatted witness was rerun in cycle attempt2;
its earlier frozen source/receipts remain separate.

Python3.10.21/3.14.7 reject50 UTC semantic trace corruptions,24 ordered-exit trace
corruptions and eight builder controls each, including rejection of the old base.
Fresh native driver reruns the760-fixture UBSan calendar app; prior3040 Gregorian
comparisons and injected provider/errno/lifetime controls are explicitly reused
only for byte-identical provider/calendar/wrapper sources. [Reuse review](reuse-review.json)
binds the original seal, source hashes and copied historical receipts. Reuse is
invalidated by provider/contract changes, and does not claim fresh native authority.

Private UTC v3: `build/sdk-deliveries/native-utc-2026-10-06-v3`,343 members,
seal `ce420b8ac745287ea057b6c0b8949eb436a63b519e270b7ed7bf164ef342bad3`;
archive `693518d97acafe99f427cae5b42b5cc7aea7f0e8656c17f185fc8c24a0e06150`.
Includes elapsed-v3 base seal
`5adc4f6e9c255df3ead08404fca177d22db00a089429f1c0666fd90dd1812c6d`.
Minimum/current and isolated sealed-source rebuild archives match; final standalone
receipt is outside the immutable seal in [reproducibility.json](reproducibility.json).
Old UTC/elapsed candidates, guarded SDK and default pins remain immutable.

Aether's earlier exact UTC-v2 intake checked actual engine timestamp bodies, but
that archive includes the defective reaper. Corrected-v3 intake and actual engine
helper reuse must precede further storage acceptance. Earlier engine leap timeout
attribution remains open. Explicit unauthenticated q35 RTC-as-UTC remains the only
source policy; no synchronization, accuracy, production identity, persistent pool,
transactions/reboot or wider SESSION acceptance follows. No sibling change or
independent owner/reader approval is claimed.


[Shared final checks/cleanup](../reaper-fix-2026-10-06/checks.json) and
[retention receipt](../reaper-fix-2026-10-06/retention.json) cover this turn's owned
UTC/elapsed builds and VM caches. Sources, process streams, maps and all failed
attempts remain compact; no full-run archive was created.
