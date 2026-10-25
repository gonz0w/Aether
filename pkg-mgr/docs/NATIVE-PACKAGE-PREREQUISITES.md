# Native bytecount package prerequisites

For pkg-mgr and the Aether/userland/storage owners. Status: **source-reviewed
requirements, no native qualification**. This is the dependency inventory for the
existing local-bundle workload in [AETHER-RELEASE](AETHER-RELEASE.md), not a new
shared API, base-package selection or permission to modify sibling implementations.
Aether is the sole release target. No Apple work is required.

## Selected path and source boundary

The operator supplies a previously reviewed, correctly target-built bytecount v2
directory bundle, its descriptor digest, target identity and an empty caller-owned
0700 root. No fetch, source build, export, replacement or installed-payload removal
is in this first workload. Source-based recipe/build acceptance is a separate path;
this local bundle is a bounded native package-engine probe, not a distribution policy.

1. From the installed source checkout, `make -s -f mk/pkg.mk ROOT="$root" init-root`
   parses [pkg.mk](../mk/pkg.mk), including the default
   [hello-local recipe](../recipes/hello-local/package.mk), and calls
   [check-root](../mk/check-root.sh) in init mode. It does not build hello-local.
2. `sh mk/state.sh init "$root"` calls check-root in state mode and publishes an
   empty state directory. The root must already exist; do not confuse initialization
   with creation of a caller-authorized directory.
3. CLI import calls [binary.sh](../mk/binary.sh), which validates current state,
   bundle records, hashes, dependencies and identities, reconstructs a disposable
   candidate and calls [state.sh](../mk/state.sh) registration/verification.
4. CLI list/files/verify use state.sh, [state-schema.awk](../mk/state-schema.awk)
   and [state-views.awk](../mk/state-views.awk). Plain verify also uses the
   [CLI renderer](../mk/cli-render.awk). CLI scratch and delivery behavior remain
   in [bin/pkg-mgr](../bin/pkg-mgr).
5. The shell runs the imported bytecount with `LC_ALL=C`, stdin redirected from
   six literal bytes and stdout to a separate file. Read back exactly `6\n`.
6. Reboot the same backing image, then repeat list/files/verify/run without init.
   Compare record, manifest, ordinary modes, license and unrelated sentinel bytes.

Import transitively calls [verify-metadata.sh](../mk/verify-metadata.sh) hash-file,
manifest and internal manifest-row helpers plus [file-mode.sh](../mk/file-mode.sh).
Its snapshot/signature/SBOM/source-fetch branches are not consumed by this workload.
The reviewed source identities are retained in
[evidence](evidence/native-prerequisites-2026-09-07/README.md). Re-audit after a
selected source, recipe, helper or tool change; this is not a universal syscall list.

## Executable and shell requirements

| Requirement | Actual use and required behavior |
| --- | --- |
| POSIX sh and script execution | Functions, case/loops, quoted positional arguments, globbing including dot entries, parameter/command substitution, arithmetic, pipelines, `&&`/`||`, subshells and redirected descriptors; preserve spaces and argument order |
| Builtins and process outcomes | `test` including `-e/-f/-d/-L/-r/-w/-s/-n/-z`, `read -r`, `printf`, `command -v`, `cd`, physical `pwd -P`, `export`, `umask`, `set -eu/-C`, traps for exit/HUP/INT/TERM/PIPE, exact child exit status and stdout/stderr separation |
| GNU Make 3.81+ baseline | Include the selected recipe, expand quote/subst/foreach/filter/words and environment assignments, invoke shell with unchanged data; BSD make or an alternative requires its own adaptation witness |
| awk | `-F`, `-v`, `-f`, ENVIRON, associative arrays, field/record handling, regexes and named script exits; `/dev/stderr` diagnostics in schema/view scripts must work |
| sort, sed, tr, wc | C-locale byte sorting including `-t`/`-k`, selected-line/substitution sed operations, whitespace deletion and exact `wc -c` file size; preserve failure status rather than plausible partial output |
| dirname, basename, cat, cmp | Literal pathname manipulation, complete byte delivery and `cmp -s` equality/difference/error distinction; errors cannot become equality or completed publication |
| find | `-type`, `-links +1`, `-name`, `-path`, `-print`, boolean grouping/negation and batched `-exec sh ... {} +`; enumerate dot entries and distinguish failed traversal from an empty tree |
| id, ls, stat | `id -u` and `ls -nd` must agree on root owner; ls exposes mode 0700 and unsupported ACL suffix. File mode helper tries `stat -f '%Lp'`, then `stat -c '%a'`; one form must report exact ordinary bits. These are concrete current compatibility seams |
| mkdir, mktemp, cp, chmod, mv, rm | `mkdir -m 700/-p`; exclusive mktemp file/directory templates including `-d`; ordinary and recursive copy; exact numeric chmod; rename/move and `rm -f/-rf` cleanup with observable errors |
| uname | `uname -s/-m` are consumed by current admission. Owner-supplied identity is required; making these resemble a host does not qualify a native payload |
| SHA-256 provider | Select a pinned working provider: sha256sum, shasum `-a 256`, sha256 (`-q` then named output), or openssl `dgst -sha256`. Detection order matters; failure of a selected provider must reject, not silently fall through. One provider suffices; transitive runtime dependencies belong to its selected build |

PATH, readable HOME distinct from root, current directory, writable private TMPDIR
(or /tmp), LC_ALL=C, and usable /dev/null are required. These environment names
and path strings do not grant capability authority. The CLI may inspect TERM,
NO_COLOR and whether stderr is a terminal; plain mode avoids color selection but
still requires output/error handling. Python and ShellCheck are development tools,
not runtime prerequisites for this selected target sequence. No compiler, tar,
minisign, downloader or network is invoked by its import-only path.

## Filesystem and process contracts to obtain

- Owner-controlled absolute/relative lookup and physical cwd, readable source/helper
  tree and bundle, ordinary files/directories, type/link-count/mode/owner inspection,
  hidden entry enumeration, byte reads/writes and EOF. Current code rejects symlink,
  hardlink and special-file payloads; the adapter must not silently disguise them.
- Exclusive temporary creation, noclobber marker creation and mode 0700 directories;
  redirection create/truncate/append, recursive copy and controlled cleanup. Some
  inspection creates scratch files, so read-only commands still need scratch writes.
- Import candidate staging is under ROOT. Stage and record are published by separate
  moves; this is not one atomic transaction. Same-filesystem rename, partial-copy,
  failure and interruption outcomes must be specified and visible. Cleanup can
  remove invocation-owned scratch or an uncommitted new stage; it does not authorize
  removing an installed package. Read [IMPORT-RECOVERY](IMPORT-RECOVERY.md) before
  adopting any retained stage.
- Flush ordering, dirty data/metadata persistence and reboot recovery must be
  explicitly established by the storage owner and consumed in tests. Current shell
  helpers issue no fsync operation; successful mv/close alone cannot close this gate.
- External program loading from authorized filesystem objects, startup argv/env,
  descriptor inheritance/redirection, wait/exit observation and trap/signal behavior
  must work for shell subprocesses and find's batched sh invocations. A fixed
  boot-image executable grant does not supply this path.

The bytecount payload itself uses [its unchanged C source](../recipes/bytecount/bytecount.c):
main/argv, getenv/strcmp, errno/EINTR, read/write/close and uint64 arithmetic. Its
read buffer is 37 bytes and decimal buffer 21 bytes; partial writes and interrupted
I/O are handled. Startup/libc/compiler-runtime closure and target ABI still belong
to its exact target build. Preserve [its license](../recipes/bytecount/LICENSE).
A shell-looking prompt or a read/write probe does not qualify the full tool closure.

## Known admission blocker and owner handoff

binary.sh currently emits `host-binary-target-v1`, compares uname/compiler target
against target.kv and the bound host.kv observation, and requires runtime `host-only`.
A native bundle therefore needs an agreed native identity/admission change and
matching producer evidence. Do not relabel native execution as host-only, forge
host observations or bypass these checks. The eventual change needs positive and
wrong-runtime/target/record/bundle rejection cases before native acceptance.

Aether's reviewed roadmap still requests actual shell/tools, filesystem and
artifact/publication contracts. Userland's M3 useful-shell milestone and UL-059/067
owner dependencies are not replaced by recent host dash tests. sys-init must start
and grant access to the required services; package import never starts services.
No tool/provider is marked native-ready by this inventory. Owners should return
versioned contracts, exact artifacts and executable success/denial/error/cleanup
receipts for the rows above. pkg-mgr can then select and test the concrete bundle
path without assuming POSIX behavior from similarly named tools.
