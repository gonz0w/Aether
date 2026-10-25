# Current AF07 engine and activation inputs

The legacy AF07 engine/activation selection referred to deliveries made before
accepted AF08 harness changes. Current intake correctly rejected the old recorded
identities of `scripts/fs_af07_inputs.py` and `scripts/fs_metadata_launch.py`.
[Issue55](https://github.com/gonz0w/Aether/issues/55) owns this bounded repair.

## Change

Use the existing offline builder to create separately named engine and activation
dependencies, then select their checked manifests. Preserve the old deliveries and
seals. The engine ELF and activation ELF/raw bytes match the original selected
executables; the new records describe their current source/tool chain. No stale
input exception, runtime implementation change or new authority is introduced.

The selected data is [native-af07-inputs-v1.json](../native-af07-inputs-v1.json).
Its build used unused destinations:

```sh
python3 -B scripts/fs_af07_inputs.py \
  --engine-output .deps/fs-launch-af07-2026-10-25-v3 \
  --activation-output .deps/fs-init-af07-2026-10-25-v3
```

This builds without selecting or preparing a guarded owner. Those paths now hold
active inputs; another build requires new unused names. Selection changed only
after manifest/live-input and exact executable checks, with rollback on failure.
Private SDK/qualification inputs remain required; see the
[public source boundary](../PUBLIC-SOURCE.md). The dependencies are not included
in this source commit.

## Verification and limits

The scoped offline run completed in110.5 seconds under its existing600-second
budget, with180-second test children and bounded diagnostics. All15 methods in
`test_fs_init_af07`, `test_fs_metadata_launch_intake` and `test_fs_af07_inputs`
pass, including actual parser and malformed/drift/foreign-input rejection.
Source/tool checks and all9115 retained AF09 inputs plus six prepared artifacts
match before and after. Owned temporary build outputs were removed; only the
minimal active dependencies remain. QEMU execution was explicitly denied.

Two earlier offline attempts remain failed: one test inherited an insufficient
file cap; the expanded follow-up then found a separate stale guarded fixture.
Both selections rolled back and failed candidate outputs were removed.

The guarded v9/AEFP0002 fixture pins its own engine and does not read this
selection. Its29 changed source identities and failed live-chain check are tracked
in [issue56](https://github.com/gonz0w/Aether/issues/56). Complete AF07-FRESH,
check-init and system coverage remain unavailable where that fixture is required;
this repair neither skips its checks nor qualifies that profile.

The earlier complete host gate remains failed.
[Issue2](https://github.com/gonz0w/Aether/issues/2) still needs a fresh owner
disposition before another900-second run. No guest, native recovery, AF09
integration or release acceptance follows from this dependency refresh.
