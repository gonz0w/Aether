# Retained static checker correction

The first audit reproduced the accepted ELF exactly, then its zero-undefined-symbol
assumption failed on _DYNAMIC. The accepted original ELF has the same undefined
linker sentinel. The corrected checker requires exact prior/baseline equality,
only _DYNAMIC, no INTERP/DYNAMIC program header and no runtime relocations. It does
not allow arbitrary unresolved imports or newly accept a different runtime image.
The original driver, pins, work root, map, outputs and incomplete report are retained
in initial-attempt/. A fresh build/audit follows; no native rerun is claimed.
