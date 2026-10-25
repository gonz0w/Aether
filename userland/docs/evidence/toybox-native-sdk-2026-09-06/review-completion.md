# Scoped technical review

Current-task review followed actual SDK source rather than assuming scalar write
covers FILE callbacks. Verified installed inventory/receipt and original archive
source correspondence plus exact native-header transformation. Built-in locale
selection is distinguished from injected return failure and separate xmalloc.
The existing UL-044 bridge is identified as a different descriptor fixture, not
silently adopted. Proposed termination seam preserves callbacks/flush/rebound
ordering and keeps global musl exit semantics untouched. Full indirect/signal
reachability remains an explicit pre-patch gate; no native execution was performed.

Initial audit attempted the wrong archive path and stopped with FileNotFoundError
before source consumption. The original script is retained; corrected path comes
from experiments/native-c/build.py. The final audit verifies18 upstream sources
and231 installed SDK files. A subsequent source addition retained __stdio_exit
for the shutdown finding. Quality and local link checks pass. Independent review,
native closure/build/runtime and owner acceptance remain pending.
