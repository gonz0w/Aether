# Directory-anchored path foundation —2026-10-23

[Requirement, authority/ownership/cleanup and simplicity review](../../proposals/FS-ROOT-PATHS.md#directory-anchored-walk-foundation-2026-10-23).
Existing fs_paths now supplies open_file_from and open_directory_from over an
explicit retained live directory. A walk never closes its borrowed base or falls
back to system root. New APIs require canonical nonempty relative paths; existing
open_root_path retains absolute/root behavior. Directory results retain LOOKUP|
READ3, files READ2; no writes, CWD string, fake getcwd, field, allocation, unsafe,
protocol, authority, quota or native selection. This is a necessary CWD foundation,
not actual per-process CWD inheritance or a writable home.

Run from userland:

```
python3 -B experiments/filesystem-service/check-paths.py
python3 -B experiments/filesystem-service/check-fd-protocol.py --paths --dup2
```

[All attempts](host-results.json) bind source/dependency/tool/checker hashes,
principal commands, per-child command/output hashes, exits, cleanup and failures.
Pinned Rust1.98/Rustfmt/Clippy, no unsafe, strict warnings, host and
x86_64-unknown-none no_std libraries pass. Selected/default client30/13, selected/
default Remote9/8 and eight compiling semantic controls pass. Controls reject
base substitution, wrong base type/result kind/rights, root escape, skipped
preflight and leaked temporary directory. Client/Descriptors680/1128 bytes,
alignment8 both: layouts identical to the default, no handle capacity change.
Actual C/Rust/C selected FILE consumer15 cases/10 compiling controls,12 replies/
96 malformed-header/three padding denials, C17/UBSan and target libraries pass.

Two harness failures remain failed. First, the skipped-preflight control triggered
the intended side-effect assertion, but the new assertion held a MutexGuard while
panicking; fixture destructor then hit a poisoned mutex and aborted(-6), which is
not the required ordinary Rust semantic-failure result101. Snapshot the observation
before asserting, preserving the same expected value and production check. Second,
Rustfmt expanded the new rights expression, so the old single-line mutation anchor
was missing. Bind the precise formatted branch and require every anchor unique.
No production behavior or safety check changed to admit either failure. The final
run compiles all eight controls and gets ordinary assertion failures101.

Existing root/wire defaults and sealed native inputs/pins remain unchanged. This
host/target build does not update the prior native frozen-source witness, select
the new libraries in an owner, prove process CWD/public chdir/getcwd, qualify home
mutation authority or make the persistent Zsh ISO ready. Future composition needs
actual complete-owner code/resident/guarded-stack fit before fresh scoped native
disposition. No extra VM ran. Current Python3.14.7 only; minimum3.10/independent
review remain missing coverage. Implementation-agent review only. Generated build
outputs removed after compact readback; active dependencies retained. Root STATE
owns next integration; no sibling-repository wait.
