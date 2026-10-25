# Private supervisor code capacity — 2026-09-23

AENMX005 adds a bounded24-KiB supervisor code envelope to the already opt-in
five-worker capacity fixture. AENMX004 remains16 KiB; all ordinary bundle limits
and entry ABI19 remain unchanged. The new header keeps112 bytes, three image sizes,
supervisor size, reserved zero and80 entropy bytes. It does not add authority,
workers, channels, writable code, dynamic allocation or another service.

The prior full exec state-machine trial needed17200–17392 bytes. Repeated compiler
layout tuning impeded implementation. Six code pages provide bounded room for that
measured implementation and remaining dispatch integration. This is a test-owner
budget change, not a larger kernel privilege boundary or completed exec feature.
Old fixtures keep their linker and004 payloads; actual larger source owners still
need an appropriately bounded linker when their implementation is introduced.

## Security and resource scope

The existing supervisor loader maps the actual code pages user RX and the separate
stack page RW/NX. It removes writable kernel aliases in all native domain page
tables, verifies each mapping and checks zero tail. At the new maximum, six code
pages plus one stack page consume the existing fixed backing; no reserved backing
pool or worker quota changes. Normal bundle parsing and disabled capacity builds
reject005. A malicious envelope cannot use the version to bypass length checks.

Host tests cover004/005 bounds, zero length, truncation, trailing data, reserved
bytes and rejection by the normal parser. Native positive witnesses admit16385,
20481 and24576 code bytes and complete the existing three-generation/fifteen-reclaim
lifecycle. Negative witnesses reject24577 bytes, truncation, disabled005 and oversized
004. Four hostile supervisor programs provide exact exception oracles:

- Sixth-page write: user page fault at40000a, error7.
- Sixth-page execution: reaches intentional UD2 at405000, vector6/error0.
- Stack execution: user page fault at800000, error15 (hex, present/user/fetch).
- Beyond-code execution: user page fault at406000, error14 (hex, absent/user/fetch).

Each protection case then reports `native supervisor terminated`. These expected
faults do not establish supervisor recovery; production supervisor recovery and
kernel compromise containment remain outside this witness.

## Reproduction and evidence

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

The existing54 cases run alongside11 new boundary/protection cases. Runtime sources
are frozen; raw logs, commands and artifacts are retained. finalize.py verifies
archives against every generated file before removing only this run's owned output
directory. SHA256SUMS seals the packet. Previous evidence and standards pins are
unchanged. The implementation review is in NATIVE-SHELL-STARTUP; workflow coverage
and the envelope contract remain in their existing references.

This is private producer evidence. Full matching connections/runner suites and
independent SDK/consumer acceptance remain separate gates. Retained snapshot,
freeze/admission/publication, grant/readiness progression and actual exec/I/O overlap
remain next. No full dash, persistent filesystem, package or release acceptance is
claimed by this capacity extension.

Final result: all65 native cases pass in197.261 recorded case seconds on280 frozen inputs. Host suite passes105 Python tests plus Zig/Rust checks. All81 prior ELF/raw images are identical. Kernel mapping span remains8007680 bytes; it is not a kernel-code or whole-system TCB measurement. One native attempt, no runtime failures in this slice.

Archive collection attempt1 failed integrity verification because Finder changed
.DS_Store during archiving; no output was deleted. Its script, inventory, archive
and diagnosis remain as collector-attempt-1 artifacts. Collection was retried with
only Finder metadata excluded, matching the source inventory policy. Actual build,
image, serial and result bytes still require exact archive/live hash agreement.
This collector failure does not change the completed native qualification.
