# Native bootstrap rejection — UL-058 NB-01

Four independently authored native controls pass against the reviewed 293-file
producer bundle. A link-only channel wrapper changes the second reference,
descriptor or rights byte after receiving the real bootstrap. The separately
compiled adapter must reject, expose no references, and let real musl read/write/
close return EBADF with unchanged sentinel. A second bootstrap and launch exchange
must issue no additional adapter channel calls. Completion is child exit 95.

A disposable early-publication adapter is independently caught at child 97.
All four then require the exact finite parent's assertion 53 and broker
970/reclaimed 0, with no CONNECTIONS PASS marker. These are deliberately rejected
native workloads, not successful remote cleanup or recovery. No test-only mutation
is in the normal adapter. The new harness counts adapter channel traps; it does
not claim general trap accounting for unrelated libc/kernel activity.

All nine pre-existing cases pass against the new producer (13 total). A separate
nine-case run passes against the original pin; its default remains unchanged.
All five legacy client ELFs match the prior bootstrap-fix bytes. The four extra
ELFs pass existing static/TLS/NX/WX/undefined/syscall inspections, and link maps
require real musl read/write/close. All 21 host/control cases pass. Every selected
runtime suite passes first attempt, with recorded owned-process cleanup.

--bootstrap-controls explicitly selects the new producer and extra client set;
without it, the old producer pin remains required. No kernel/owner source edit,
shared API change or public runner implementation. NB-02–04, ASan and independent
technical/reader review remain open. New failure evidence does not close UL-058.

Raw source snapshots, diffs, mutants, maps, ELF files, serial logs and receipts
are retained. Large ISOs/checkouts remain under build/native-command-userland-o74uog7q
and build/native-command-userland-igmnafaz with digest-bound receipts. The producer
source archive is retained in docs/evidence/runner-owner-review-2026-09-06.
