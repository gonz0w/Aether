# POC test evidence retention

On 2026-10-05 the maintainer requested disposal of bulky test archives and generated
outputs. Compact reports, small diagnostics, test recipes and fixed regression
inputs remain; the storage and workflow policy is in
[DEVELOPMENT](../DEVELOPMENT.md#evidence-and-failures).

Historical packet manifests, archive inventories, README commands and hashes record
what was executed at the time. They may refer to deliberately removed files. Their
old archive verification/replay commands are retired, and their original result
claims have not been rewritten into fresh tests or full standards compliance.
Do not recreate those archives for subsequent work.

The five maintained shell/session fixtures now live in `tests/fixtures` and are
checked against their original pins. One verified copy of current private OpenZFS/
SDK build inputs lives in `.deps/native-current`; the pinned upstream source archive
is in `.deps/sources`. These are build inputs, not stored test data or release proof.

Cleanup requirement: delete test archives, generated binary/image data, inactive
build output and workspace caches; preserve source, released standards, reviewed
snapshots, current input bytes/pins and small regression fixtures. No sibling repo
or runtime ABI changes are authorized by this cleanup. Select full host/pin checks,
fixture identity, cleanup path/ownership checks and a focused actual wait smoke.
