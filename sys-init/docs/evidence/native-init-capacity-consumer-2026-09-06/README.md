# Native init capacity consumer evidence

2026-09-06; decision 0090.

Decision 0090 accepts the explicit AENIN002 / ABI-15 profile for the existing
151-case sys-init workload. All 151 cases pass in a fresh independent target run
(457 commands, 421 frozen inputs unchanged). Exact old semantic assertions are
preserved; only the producer-defined LARGE PASS/CLOSED markers differ. All 151
ABI-6 images also rebuild byte-for-byte identically under the default profile.
The new profile has an 8192-byte bound; these refreshed images still use at most
4096 bytes. Second-page protection/cleanup evidence comes from the pinned producer;
this consumer run does not yet execute a larger guard image.

SI-05's profile dependency is now available and the compatibility refresh passes.
Next BG-058: integrate the retained conflict guard under the explicit large profile,
run all 151 regressions plus its five proposed cases, then qualify construction
denial and closed reoffer. Guard lifetime/physical capacity and PH-05–07 remain
open; profile acceptance does not accept that guard or close the whole SI-05
consumer handoff. No sibling source or shared standards pin changed.

`upstream/` records the producer packet identity, exact contract and qualification
metadata. All packet files and all 401 source archive members were verified before
normalization. `producer/` preserves original archive, report and envelope bytes
under the existing consumer layout; `producer-pin.json` pins its generated summary.
`prepare-producer.py` records the normalization. Builds consume archived boot
inputs, not a mutable sibling. Installed compiler/tool identities are scoped by
the retained records; complete host-library closure is not claimed.

`witness/` retains all 151 exact outcomes, supervisor/envelope/serial/QEMU artifacts,
commands, source pins, client sources and worker receipts; it is separately sealed
and registered in the offline native catalog. ISO identities remain in the report;
ISO files are reproducible private outputs, not retained in this bundle.
`legacy-build/` retains all 151 byte-identical ABI-6 rebuilds. `capture-attempt-1`
records the packaging-order failure; `capture.py` records the corrected name-based
comparison. It was not a target failure or a change to any semantic oracle.
`validation/` contains full local checks and `adoption/` final documentation/source
records. `sha256.json` seals this new bundle; historical manifests stay unchanged.

Validation: all nine development gates pass in `out/checks/run-x4_z02iw`,
with no skipped gates and unchanged checked inputs. All twelve current consumer
source files match the fresh target snapshot; the legacy linker hash is unchanged.
The offline native audit covers 2360 historical outcomes across 46 bundles.
Full logs, host sample artifacts and final adoption records are retained in
`docs/evidence/native-init-capacity-consumer-2026-09-06/`.
