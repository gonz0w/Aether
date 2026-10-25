# UL-076 — local dash helper-build ownership

The host compilation stage previously shared test.py's direct-child wrapper with
remote Podman calls. It now uses host-build.py, a small adapter over the unchanged
command-runner helper. PLAN.md records the clauses, ownership assumptions, limits,
validation and remaining remote work. No sibling or release input changed.

Six controls in three methods pass on Python 3.10.21 and 3.14.7: separate byte
streams with explicit cwd/environment, nonzero status, timeout with descendant,
successful leader exit with a surviving child, output exhaustion and missing tool.
Every started group is absent after cleanup; missing execution is incomplete.
Logs, fixture programs and process receipts are retained in this packet.

The retained compile.py verifies the old build wrapper inputs, tool executable
pins and full SDK inventory before invoking the new adapter with actual helper.c.
The fresh helper exactly matches the previous helper digest. compilation.json binds
argv, original evidence, tool lock, platform and runtime. This is a host compile
and byte comparison, not guest or native execution. The twelve guest cases and
markers are unchanged, but their full runner integration has not been rerun.

Commands from the repository root:

```
python3 -B experiments/dash-reference/test-host-build.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-host-build.py
python3 -B build/dash-host-review/compile.py
python3 -B docs/quality/check.py
```

The test runner keeps command fields and stdout/trace paths; successful aggregate
evidence adds host_build_sha256 and process_helper_sha256. It now stops on unresolved
local compiler cleanup even if a leader exits zero. Existing 16 MiB limits also
bound compiler-created files; the tested small artifact fits. Failed attempts keep
receipts even when no aggregate evidence.json is produced.

Source inspection found build.py's generated compiler wrappers and make can invoke
remote target generators; test.py similarly runs anonymous --rm containers through
Podman. Their direct-child waits do not prove remote reclamation. UL-077 requires
unique recorded attempt identity, ownership validation, bounded cleanup and absence
witnesses, including service-loss/ambiguous-create controls. No Podman lifecycle
mutation or new remote-cleanup implementation was attempted here.

sources.json records revised test.py, new adapter/tests and unchanged helper/build
script identities. These supersede affected UL-074 census entries without rewriting
that dated snapshot. Independent review remains pending; UL-076 stays active. The
new code has author controls, not inherited approval from UL-072 or full UL-063
acceptance. Whole-suite bounds, hostile detach/owner SIGKILL and filesystem races
remain outside this scoped local ownership contract.
