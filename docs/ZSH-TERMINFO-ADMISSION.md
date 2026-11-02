# Retained-namespace Zsh admission

Issue [137](https://github.com/gonz0w/Aether/issues/137) selects the default-off
`-Dnative-zsh-terminfo=true` boolean with the complete existing private BSP ABI31
filesystem owner-stack, application, MODE and exact-generation SIGINT flags.
The kernel exports `native_zsh_terminfo`; the matched Rust Owner selects its
`native_zsh_filesystem` cfg. Neither selection changes resource limits.
Incomplete selections, release artifacts, SMP, AF09 diagnostics, mktemp-reader
and storage-lifetime compositions reject. Large application plus MODE remains
rejected unless this closed selection is present.

## Authority and commit

Use the existing int81 `0x2300a` operands and exact320-byte
[ordinary launch layout](NATIVE-LAUNCH.md#ordinary-one-app-namespace-launch), with
magic `AENAP002`. The selected parser rejects `AENAP001`; ordinary admission
rejects `AENAP002`. All other fields, reserved bytes, argument bounds, error
precedence and image/backing/leaf preflight remain unchanged.

Before effects, the same preflight validates the exact current engine instance,
all four distinct open endpoints, Owner6 custody, engine counterparts/directions,
empty process channels and untouched namespace response-read/request-write
history. An already queued engine greeting is allowed and preserved. Under the
existing IF=0 gate, commit transfers only the process reader and writer to the
app. Both namespace endpoints and their queued bytes remain in the Rust Owner.
The app receives its existing memory and process auxv entries; it receives no
`0xa003` entry or namespace startup bytes. The fixed32-byte internal binding
still constrains copy/exec and identifies the precise app lifetime. No namespace
authority is forwarded through that binding.

Admission returns a live app handle while the app awaits its FD greeting.
It does not mark the app ready. The Owner provisions and verifies terminfo after
admission, then publishes checked FD startup under its own service contract.
Provisioning failure still permits the existing exact app stop/reclaim path;
Owner namespace custody remains available for healthy or fatal cleanup.

The admitted target records the actual Owner generation, including real boot
generation0. Existing int81 `0x29003` validates that relationship and the exact
current app binding/handle before PREFLIGHT or POST. Stops, faults, reclaim and
shutdown revoke it. Existing MODE delegation, holder checks and post-stop cleanup
are unchanged; no syscall, endpoint, grant, queue or global registry is added.

## Focused checks

From the repository root with Zig0.16.0:

```sh
python3 -B -m unittest discover -s tests -p test_zsh_terminfo_profile.py -v
python3 -B -m unittest discover -s tests -p test_build_policy.py -v
```

The new suite compiles extracted production admission, startup, channel and
SIGINT bodies over actual model types and host-owned backing. It checks selected
and ordinary custody, exact wire/startup compatibility, pre-effect denials,
stale Owner/app signal targets, app namespace/copy/exec denials, stop revocation
and retained namespace access after containment.
Compiling selection, custody, auxv and history omissions must fail their semantic oracles.
`zig build --help` evaluates actual profile guards without producing an image.
The inherited focused runner bounds are300 seconds aggregate,60 seconds per
compiler child,10 seconds per executable,4MiB output and16MiB compiler files.
Generated sources, caches and executables are owned temporary outputs.

Host substitutions cover MMU loading, scheduling and device access. These checks
do not establish whole Owner/Zsh fit, hardware enforcement, UART timing, native
handler delivery, ZLE or release acceptance. Matching artifact/geometry review
and the existing finite no-network disposable-media execution gate remain.
