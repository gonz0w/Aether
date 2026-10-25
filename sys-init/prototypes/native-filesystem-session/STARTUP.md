# Proposed AEFDB001 startup producer

Decision0200 prepares fd_startup.rs as a separate no_std crate, consuming the
unchanged ABI29 startup core. No accepted owner, linked shell, old32/64-byte
startup path, SDK or released pin is changed. Userland startup56 candidate seal
`709a2c0f33b3cbf8dbecc3143d2976d5dd9093120cb4460eb41f697805147094`
is the exact proposal/consumer input, not a released cross-project ABI.

`encode(&Plan, &mut [u8;304]) -> Result<(),i32>` first validates identity through
existing greeting, then file generation, all16 bindings/seven source records and
retained pipe history. Failure leaves output unchanged; success initializes all
304 bytes, including reserved zeros. The small temporary identity frame is32 bytes;
no304-byte automatic frame,4096 workspace, allocator or writable static is added.
No I/O, send loop, replay, another context/ledger or second AF07 Owner/SPA.

Binding kinds0/1/2/3 are empty/console/pipe/file; selectors and flags follow exact
candidate bounds. FILE selector3 and PIPE selector3 are independent; duplicate
FILE selectors reject while stream aliases are allowed. Every stream selector
must have one matching nonzero source and every nonzero source must be referenced.
Source references are unique; selector, read/write rights and16-byte bounds match
source position. Pipe references encode exact object/generation/end and must match
retained histories0..9. Histories remain even when no local endpoint exists.
Console references and nonzero file generation are opaque owner-issued labels.
Role factory is0x76050001 for shell1 and0 for copied children2..4. Existing genuine
boot parent7 and copied parent/shell-generation checks remain unchanged.

The trusted caller must own actual admitted instance/process/channel and source/
factory rights. Shape validation supplies no native authority, authentication or
endpoint transfer. Emit only on that exact instance's authenticated channel and
only to the new selected sole consumer; never send this proposal to the old linked
shell. Full single-consumer delivery, partial-send failure, endpoint retirement,
readiness and native cleanup are future full dispatcher responsibilities. There
is no fallback, reconnect or implicit grant acquisition in this function.

Wire layout: AEFDB001/version1/length304 at0..16; unchanged AEFSH001 identity at16;
AEFDT001 map at48; seven16-byte source records at176; histories at288/292; role
factory at296; zero reserved at300. Map includes generation at56/count16 at64,
reserved zeros72..112 and16 four-byte records at112..176. All integers little-endian.

[Evidence](../../docs/evidence/descriptor-startup-producer-2026-10-22/README.md)
records three host Rust tests, three compiling omissions,138 real Rust-generated
frames consumed by exact C startup/context/native code and1518 corruptions. C
native calls are host-injected; short reads/EAGAIN, full/early length, mask/query
arguments, publication, scratch clearing/readmission and raw local close results
are observed. No native traps execute. Generic no_std library builds only; neither
native executable, actual startup observations, shell entry nor complete fit.

Compile core lib.rs as abi29_dispatch_core, then fd_startup.rs as fd_startup with
that extern. Exact bounded commands/tool/native-library/header/runtime/source pins
and inert reproduction runner are retained in evidence. All16 selected closures/
494 members verify. Do not rerun into sealed evidence; choose fresh private roots.

Next userland wires this sole consumer/context into libc/shell and replaces old
64-byte table/process snapshot/copy/exec framing explicitly. Child rebind/TLS,
source/file/channel generation and immutable image/failed-or-unknown-exec parent/
FD preservation and actual off-stack placement/full resource fit remain required.
Then sys-init composes full matched dispatcher/readiness/shutdown and Aether
qualifies fresh native commands/errors/cleanup/readback. Native/context helper
code now exists; authenticated linked runtime selection is still absent.
