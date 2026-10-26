# Filesystem inputs for current host checks

The public checkout contains current source. Some filesystem tests also require
retained private dependencies and historical fixtures. [Issue70](https://github.com/gonz0w/Aether/issues/70)
owns their current host-consumer association; [public availability](PUBLIC-SOURCE.md)
remains explicit. A README stub or old digest does not supply missing bytes.

## Locations and identity

`AETHER_HOST_DEPENDENCY_ROOT` selects one real absolute retained-input root for a
fixed list of dependency capsules. It does not change source `ROOT`. Current
kernel, user, sys-init and package-manager sources remain in this checkout.
Only the named retained dependency and historical-fixture locations in
[`fs_host_dependencies.py`](../scripts/fs_host_dependencies.py) may route.
Unlisted paths, copied test roots and arbitrary source trees do not route.

Declared aliases must resolve to the selected originals. A conflicting alias or
real capsule fails; the documented historical README-only stub is handled as a
missing fixture rather than an available capsule. Existing seal, member, type,
path and real-directory checks still validate the actual retained tree. An alias
is an input location, not enforced filesystem read-only confinement. Keep these
inputs unchanged and verify their hashes before and after qualified work.

Provision only the exact required local inputs. Small sealed deliveries and
compact fixtures may be maintained separately from evidence. Keep SDK-bearing
capsules and historical packets in their retained locations; do not copy SDKs,
recreate archives, overwrite public stubs or publish private input files.

## Historical producer and current consumer

The default AF06/AF07 intake remains strict about live inputs. A historical
receipt cannot qualify changed kernel or loader code. The separately selected
`aether-fs-host-consumer-association-v1` record distinguishes:

- Original immutable artifact, seal, producer inputs, tools, objects and origins.
- The exact reviewed consumer/census changes and current frozen source hashes.
- Fresh current parser, old-profile, application-model and legacy-kernel evidence.

Select both `AETHER_FS_CONSUMER_ASSOCIATION` (a real absolute record path) and
`AETHER_FS_CONSUMER_ASSOCIATION_SHA256` (its exact reviewed SHA256). A partial,
stale, malformed or mismatched selection fails. The reader rejects duplicate or
unknown fields, unlisted producer changes, changed actual compiler/provider
inputs, incomplete processes and missing semantic controls. A producer script
change needs exact proof that its producer logic/imports/constants/flags remain
unchanged after only the named consumer and location-routing transformations.
The existing seven-tool migration catalog and original seals are unchanged.

The legacy pair reader resolves only the declared runtime root before applying
its original member/link/hash checks. Member names must stay relative and inside
that root. Historical AF09 recipe checks use the existing recorded-checkout
prefix map only for identity comparison; current source reads stay under current
`ROOT`, and original generated-input keys and hashes remain unchanged. Retained
live source bytes are checked before generated-source reconstruction, followed by
the complete recipe and input checks. These checks do not qualify a current owner.

The five evidence scopes are `af06-parser`, `af07-parser`, `legacy-models`,
`application-models` and `legacy-kernel`. Their exact process fields and semantic
marker contract live in [`fs_consumer_association.py`](../scripts/fs_consumer_association.py).
A checked projection may summarize retained nested receipts, but it must bind the
actual outputs, generator source, current inputs and real compiler/test commands.
Do not invent commands, replace errors with pass markers or claim disposed test
binaries remain available. `write()` validates and seals data; it does not execute
commands from a receipt.

The record hash is a configuration/review trust anchor. It is not proof of
execution or native capability authority. Current host evidence and separate
source review remain required. Exact record paths, artifact/SDK details and raw
receipts stay local.

## Complete host gate

After provisioning exact inputs and producing the reviewed current association,
run the complete gate from the public repository root. Replace the placeholders:

```sh
AETHER_HOST_DEPENDENCY_ROOT=/absolute/path/to/retained-inputs \
AETHER_FS_CONSUMER_ASSOCIATION=/absolute/path/to/association.json \
AETHER_FS_CONSUMER_ASSOCIATION_SHA256=SHA256_OF_REVIEWED_RECORD \
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Use the owning issue's bounded coordinator, pinned named tools and source freeze.
The aggregate retains its 300-second limit, 180-second auxiliary/leaf bounds and
4 MiB live diagnostic-stream caps. A sparse-fixture or compiler scratch-file
allowance is separate from the stream cap. Track owned root and nested sessions;
confirm cleanup and retain every failed attempt. Do not skip tests, shard the
required gate to evade its budget, reuse a consumed exception or treat a timeout
as a semantic rejection.

Some historical object comparisons also bind diagnostic source locations.
Their regression controls explicitly map the current checkout to the recorded
location before comparing old bytes. Production flags, provider bytes and old
expected hashes remain unchanged. A raw checkout-path difference must not be
reported as either a provider change or proof of byte compatibility.

The owner-approved single extended aggregate in issue69 completed with legacy
regression failures. Its focused corrections and refreshed records do not grant
a full-gate pass or another extended run. Failed attempts and cleanup results
remain local; the default bounds above still apply.

Relevant direct checks are:

```sh
python3 -B -m unittest discover -s tests -p test_fs_consumer_association.py -v
python3 -B -m unittest discover -s tests -p test_fs_application_profile.py -v
```

Fresh host association does not qualify the changed kernel natively. It launches
no guest and grants no operational, persistence, TTY/ZLE or ISO acceptance. The
[bounded application profile](NATIVE-ZSH-APPLICATION.md) and matched native gate
retain their separate acceptance requirements.
