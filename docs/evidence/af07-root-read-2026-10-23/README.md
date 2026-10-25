# AF07 persistent root-read diagnostic —2026-10-23

The maintainer explicitly approved this one three-guest sequence; it now passes.
All three VMs stopped. [Disposition](disposition.json) and [compact results](results.json)
preserve the exact scope and outcome. No retry or extra guest ran.
[Decision0221](../../../sys-init/docs/decisions/0221-root-path-owner.md),
[host/build results](../../../userland/docs/evidence/filesystem-path-owner-2026-10-23/README.md)
and [exact prepared identity](prepared.json) make this separate diagnostic reviewable.

Actual path-enabled owner40640/49152 code,7504/8192 resident,8000/8184 conservative
stack; initialized TLS shell/helper80/33 pages. AEFP0001 binds matching read-only
Client/ProcessFiles/router/C codec/libc. The separately immutable helper opens
/zstd, reads16 bytes, checks780248-byte EOF twice, closes and emits exactly one
13-byte AF07-READ:ok line before exit7. This qualifies bounded path/read/count/
context/cleanup, not complete content correctness or executing disk bytes.
Independent pristine/recovery readers still verify the full original file/hash,
exact stopped media and canaries. Full Zsh/CWD/public dup2/writable home/packages/
persistent executable loading/ISO and independent acceptance remain open.

Completed fixed sequence: pristine read-only reader → selected writer → fresh
read-only recovery only after strict writer success. Writer60s/6000 ticks,
readers30s/3000,64KiB normalized capture,35MiB/seven domains/twelve channels,
49152 owner code/8192 stack/data and separate9-mutation/96-request qualification
remain fixed. Zero FS mutation requests; import/export may write metadata. Stop
at the first unexpected result; no retry/replacement trial or later reader after
failure. Existing terminal/admission/wait/export/reclaim/media checks stay strict.

Executed once under the recorded fresh disposition, from system root:

```sh
python3 -B sys-init/scripts/qualify-af07-owner.py --run \
  --prepared zig-out/thread-suite-service-runtime-zpl-pair-fs-session-owner31-idtstxiz \
  --prepared-sha256 f691e90ff2c000d2741e28e7c3f0a6458fb719fe7f6e5a919b862acf091bd9da
```

The pristine/recovery readers each verify all780248 original bytes. The writer
observes helper7/parent0/engine0,21 cleanup rows,302 paired waits and halt2020/6000.
Recovery preserves the stopped writer media; canaries match. Zero filesystem mutation
requests; import/export metadata changes remain explicit. Passing transcripts,
reports, images and media are removed after compact readback; current sealed
dependencies remain. This is bounded native path/read/count/cleanup evidence, not
independent persistence/durability acceptance, full content proof from the helper,
consumer sign-off or release readiness. The one-sequence approval is consumed.
