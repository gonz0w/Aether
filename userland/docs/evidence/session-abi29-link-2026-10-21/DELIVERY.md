# Private ABI29 linked client candidate

Profile AENFS003/ABI29, AEFSH001 client greeting, shell1/children2–4.
This is a source/CRT/libc/component/link candidate, not a native-qualified shell,
published SDK, package, boot image or release. Matching dispatch and filesystem
FD/path/immutable executable translation are still required. No new native
authority, lifetime reset, allocation quota or owner policy is supplied.

The sealed recipe builds runtime/application, memory, public musl fork/wait/rebind
and the existing serial helper. Prebuilt pinned dash/CRT/libc inputs and their
notices are retained. Parent admission lists all45 actual link inputs, including
all32 dash objects; helper lists its actual eight inputs. The existing memory
component remains mandatory even where libc could satisfy an omitted adapter.
Every new runtime/application compile explicitly selects ABI29/serial/waiting;
mixed ABI24 application/runtime links fail on the distinct startup symbol.

Choose the externally reviewed SHA256SUMS digest before calling
`support/rebuild.py`'s `rebuild(bundle, new_output, expected_seal)` with
Python3.10+. Output must be a new owned directory outside this bundle. The builder
verifies exact members, tools, component/link selection and post-build hashes,
using the unchanged owned runner with60s/16MiB command bounds. No network,
installation, QEMU, native admission or SDK promotion occurs in this function.

Host-built static ELF identity and initial kernel parser/backing fit are recorded
separately from execution. The retained libc's zero-valued LOCAL HIDDEN UND
`_DYNAMIC` symbol is a static-link sentinel, not a dynamic segment or global
import. No relocations, interpreter, writable-executable segment or unexpected
undefined symbol is admitted by the inspection.

One selected future workload is the existing serial helper's `argv`, `status`,
`copy`, `closed`, `one` and `pump` modes under the retained application path
`/inputs/helper`. Those are bounded client inputs, not evidence of a filesystem
loader. A matched owner must bind real authorized persistent image bytes through
loader admission before that path can satisfy persistent-command acceptance.
UID1000/PWD and numeric descriptor/PID labels grant no native authority.

Initial backing includes the16-page main stack. Static headroom is not peak
stack/heap use or TTY/Zsh resource acceptance. Full native copy/exec/wait/FD,
error/unknown-outcome handling, clean disconnect/export/reclaim/halt and fresh-
boot state, independent technical/reader reviews and M3/R1 remain open.
