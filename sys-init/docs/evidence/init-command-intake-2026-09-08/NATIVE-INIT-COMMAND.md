# BG-067: bounded real-command integration handoff

Producer delivery, 2026-09-08. [Frozen inputs, recipe and evidence](evidence/init-command-handoff-2026-09-08/README.md).
This supplies the selected composition boundary and reference cases needed to
start sys-init's BG-067 adapter. It does not claim that sys-init's owner has been
ported, independently accepted or booted. Userland supplies the real four-role
runner and bytecount; their original frozen sources are rebuilt here.

## Selected ownership and profile

Use the existing AENMX001/ABI9 three-image profile. **Sys-init replaces the reference
supervisor**, rather than supervising an extra broker domain. Its service policy
owns admission, stop, terminal observation and reclaim. The existing command/file
protocol logic remains a separate responsibility in that supervisor address space;
this is not process isolation between those components. The worker roles and wire
contracts remain unchanged. Do not substitute the ABI16 init binary or readiness
writer: the entry registers and transferred connections differ.

| Role | Slot / executable | Owned responsibility |
| --- | --- | --- |
| Runner | 0 / 0xc001 / source-built four-role runner | Decode startup, select bytecount, request launch/collection, close its file references |
| File backend | 1 / 0xc002 / C bridge plus Rust stream service | Seed input, output buffers and open backend handles |
| Command | 2 / 0xc003 / source-built bytecount | Public libc input/output and exit; no image/channel factory authority |
| Supervisor | 3 / raw code tail | Lifecycle authority, connection allocation, file-reference routing, child admission and terminal records |

Supervisor entry: RDI=9, RSI=0xa001 launch factory, RDX=0xc001,
RCX=0xc002, R8=0xd001 channel factory, R9=0xc003. No wait-factory grant is
supplied by this profile. Code must fit 8192 bytes, with a separate 4096-byte stack.
Reference raw images and sizes are in the case receipt; the consumer must measure
its own linked code and stack. This does not extend ABI16's 16 KiB allowance to
ABI9. Three generations per worker/channel remain the existing bounds.

Envelope: 80-byte header/entropy prefix: AENMX001, three ELF byte lengths,
supervisor length, two zero u32 fields, then 48 developer entropy bytes; append
runner, backend, command and raw supervisor in that order. All ELFs are preflighted
before admission. Existing [program](NATIVE-PROGRAM.md), [connections](NATIVE-CONNECTIONS.md),
[launch](NATIVE-LAUNCH.md) and [supervision](NATIVE-SUPERVISION.md) contracts define
exact formats and errors. No new syscall or published standard is introduced.

## Startup, transfers and cleanup

Start backend slot 1 before runner slot 0. Kernel argv is `worker` for the backend
and `client` for the runner, with no environment in this fixture. For each worker,
allocate a request and reply channel: transfer the request reader and reply writer
with 0x23002 only after validating startup. The supervisor retains request writer
and reply reader. Successful transfer denies further caller use of transferred
ends; rejected startup leaves them with the caller for cleanup. Six channels
support the two services plus the command, with 32-byte queues and 16-byte chunks.

Read the backend's fixed handle greeting before publishing runner startup. Send
224-byte AERUN001 with `aether-run`, `bytecount`, `--decimal`, followed by the
160-byte AERIO001 carrier: stdout/write/512, stderr/write/256, child-input/read/6,
child-output/read-write/64. Six is the input capability's bound; the empty case
has zero data without changing that carrier. These are connection-local file
references, not kernel handles. Actual command argv comes from validated runner
forwarding: `bytecount`, `--decimal`; its legacy two-binding carrier supplies input
and output. Do not conflate either carrier with kernel argv or a readiness byte.

The supervisor owns each native connection and instance handle. Runner and command
own their admitted file-reference closures. The backend owns underlying buffers;
it is stopped only after clients are terminal, references retired and readback
complete. Observe with 0x20001; normal exit, fault and controlled stop are distinct
kinds. Reclaim with 0x20002 only after terminal state. 0x20007 is the existing
controlled stop operation; this packet qualifies the fault branch, not a new
stop-recovery policy. Close both retained channel ends and reclaim each client;
then close the backend request writer, observe EOF termination, close its reply
reader and reclaim. Preserve partial cleanup on errors; never replay an unknown
consumption or treat a terminal record as reclamation.

Sys-init's current Service/Pair adapter needs paired request/reply ownership in
place of a single readiness channel, role/image selection and backend EOF ordering.
Its cleanup method currently requires terminal observation before endpoint close;
the backend requires request EOF to terminate. The adapter must explicitly settle
that ordering, retaining per-end close progress, rather than smuggling side effects
into observation. No generic journal or extra service is required by this handoff.

## Producer acceptance and consumer work

The five source-built cases use the unchanged kernel:

- Positive: input `abcdef`, output `6\n`, child/runner/backend exit 0/0/17.
- Empty: empty input, output `0\n`, the same terminal results.
- Fault: injected #UD after command bootstrap, before bytecount; input unchanged,
  no output, command detail134/kind2, runner exit1, backend exit17. Reference owner
  retires the faulted command's file references and completes cleanup.
- Wrong role: invalid AERIO001 startup causes runner110, no command admission,
  owner1401/reclaimed0. Retained failure, not recovered cleanup.
- Omitted stdout close: child0/runner0, owner1403/reclaimed0. Retained failure
  demonstrates the close obligation; it does not qualify recovery.

Positive, empty and fault each require two generations and six reclaims. Backend
readback proves exact output, untouched input, empty runner output, EOF and stale
handle denial. Sys-init must preserve these semantics while supplying its owner,
then independently freeze and run its consuming cases. This packet opens that
adapter work; it does not close BG-067 or confer consumer sign-off.

The native watchdog (<3000 ticks), registration bounds in other profiles, sustained
idle strategy, authorized shutdown source and final action remain later acceptance.
Conformance `finish(100)` is not operator shutdown, filesystem flush or poweroff.
Dash, persistence and package release gates are unchanged.

Reproduce from this checkout with the pinned SDK/tool inputs recorded in the packet:

```sh
python3 docs/evidence/init-command-handoff-2026-09-08/run.py --libc-build /absolute/strict-sdk --tools-lock /absolute/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Use the archived sources for matching-revision reproduction. Builds never follow
mutable sibling code; imported source hashes and the SDK/tool receipts are checked.
The retained SDK archive is `docs/evidence/init-composed-capacity-2026-09-07/sdk-inputs.tar.gz`
(SHA256 `179e9100b6a0a5ee537450cd87d5642e31c00617d545b09bc5c1679e9a997c77`).
Preserve third-party notices and the existing released standards pins.
