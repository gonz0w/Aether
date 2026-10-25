# User-authorized disk cleanup — UL-007 evidence maintenance

The user explicitly requested cleanup of test/tmp/old-build disk usage on
2026-09-14. Preserve maintained tests, uncommitted source, sealed evidence and
pinned SDK/tool/source inputs. A sibling Aether command-runner is active using
build/native-c-5olokhku; exclude that SDK, all sibling paths and unowned /tmp.

Selection: completed consumer producer/zig-out suites with passing results.json;
archive them under build/retained-artifacts, verify every member byte/hash/type/
mode and unchanged source inventory before removing unpacked copies. Keep original
relative suite paths inside each archive and an explicit old-path/archive index.
Preserve failed inner cases/artifacts if present; only outer completed suite roots
are selected. Do not infer unrelated directories are disposable. The cache scope
is .zig-cache directly under these inactive consumer producer roots; it contains
rebuildable compiler cache, not source pins. Record its measured allocation before
deletion. Never remove the support tool-lock under zig-out/init-capacity.

Foundations E-01–08 and local TD/TC/TE/CP apply. This is storage relocation, not
new native qualification or evidence rewriting. No native tests need rerun because
inputs and outputs are preserved; verify archive readback and run the local quality
gate. Explicit authorization permits removal only after the recorded verification.
Reject symlinked roots, special files, archive collisions and input changes. Keep
all logs, failure receipts and prior seals. Compression uses Python stdlib gzip
level1. Actual execution used the desktop process session with short progress
polls; no automatic1800-second watchdog was installed. The archival script launches
no child process. This differs from the initial planned caller deadline.

Simplicity: one inspected archival script and ordinary tar.gz archives; no new
package manager, service or scheduled cleanup. Restoration is explicit and checks
hashes before use. Independent review is pending; self-review covers path scope,
verification-before-removal and preserved reproduction inputs. No acceptance or
release status changes. Shared /tmp cleanup is deferred without clear attribution.
