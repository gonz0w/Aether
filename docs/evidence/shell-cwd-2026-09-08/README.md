# Initial scoped directory implementation

Final qualification: 319 command cases and host/pin/workflow checks (98 Python
tests) pass on frozen runtime inputs. AECAT003 adds a staged directory query grant.
The Rust conformance owner enforces the current connection/generation binding and
owns one immutable `/work` directory. The C facade queries it for getcwd and the
three stat fields used by generated dash init; other stat fields are explicitly
unavailable/zero. This is a scoped adaptation, not a general filesystem API.

Actual unchanged generated init handles absent, matching, relative and out-of-scope
PWD without the prior getcwd warning. Raw probes bypass the facade to check denied
foreign/stale references, malformed selectors, unknown operations and reserved
bytes. Caller buffers, exact fit, small/zero sizes, heap allocation/free, errno and
unchanged error outputs are checked. Five malformed grants remain unpublished and
complete four reclaims across two generations. Skipped publication rejects
client106/owner1501. Existing metadata, signal, stream and command controls pass.

Attempt-1 was intentionally interrupted during the 53rd listed case after source
review found a wrong-selector directory request reached the old stream assertion.
No failing target observation had exposed that edge; this is a review-discovered
product defect and an incomplete qualification attempt. The corrected route returns
EINVAL; added raw probes test it and unknown/reserved requests. The interrupted
harness executed its owned QEMU teardown in finally. Partial results, exact sources,
logs and run artifacts are retained; the interrupted case is not counted as passed.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-cwd-2026-09-08/collect.py
```

The collector verifies the previous metadata packet, final input hashes, the
interrupted source archive and simplicity snapshot, then reads back every archived
source/target member. qualification.json names both retained runs; manifest.json
seals the packet recursively. Kernel/build inputs are unchanged; no fresh M4 run.
No sibling, release pin, upstream object or license changed. Sources use the
existing local C style and Rust edition2024 formatting.

See the [pre-code contract and selected qualification scope](../../NATIVE-SHELL-STARTUP.md#directory-implementation-qualification-plan--2026-09-08).
Next: directory reply corruption/truncation and poison teardown; version/truncated
bootstrap, alias grant and mismatched identity/PWD controls. These remain missing
coverage, not exceptions or completed consumer acceptance. Full main/secure-ENV,
exec/wait, general paths/chdir and persistent OpenZFS work remain open.
