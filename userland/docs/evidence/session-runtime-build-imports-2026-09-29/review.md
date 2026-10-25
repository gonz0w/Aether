# UL-007 bundle dependency import review

Requirement: a receipt-selected builder must execute its pinned support modules,
even when embedded in a Python process that already imported modules with the same
names. Existing plain imports use sys.modules and can select unpinned validation
or process helpers. Reproduce the issue before fixing it. Original runtime/native
sources, owned command helper, recipes and frozen evidence remain unchanged.

Scope: explicitly load the verified support/process.py and support/components.py
from the selected bundle; preserve results/exit/cleanup contracts. No kernel/ABI,
C runtime or UL-058 behavior change; independent reader review remains pending.
Foundations E-01–06 and Coding explicit-dependency/control rules apply. Python3.14
host, pinned Clang/LLD and existing SDK bundle. Inputs and driver/plan hashes selected
before execution. Fresh private build directories;60-second/16MiB owned commands.

Tests: the old builder with a cached validator can admit an omitted memory
component and link its libc fallback. The corrected builder must reject that
closure before linking despite cached validator/process modules. A valid bundle
must rebuild with poisoned cached names without invoking them, preserve sys.path
and cached modules, and reproduce native-qualified whole parent/helper ELFs.
Also exercise two distinct bundles in one interpreter to exclude cross-bundle
module reuse. Pin/source/seal checks, Python syntax, quality and whitespace gates.
No new native run is needed if corrected build outputs equal prior qualified bytes;
this does not qualify concurrent hostile Python mutation or source-trust policy.

Simpler alternative: delete conflicting sys.modules entries and use normal imports.
That mutates caller state and can still select another search path. Load two exact
verified files into local module objects instead; avoid a plugin/import framework.
Remove dependence on global import name/search-path selection. No broader module
sandbox, concurrent-input confinement or general package machinery is added.

Author technical findings recorded in this packet; external/reader review pending.
UL-007/SSDK promotion and separate SI-07 runtime delivery remain open.
