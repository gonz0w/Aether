# Host-preview content and notice review

HR-01/HR-07 scope for the experimental host preview. This component inventory
separates proposed public content from the larger development snapshot. It does
not approve publication, override upstream terms or qualify optional workflows.
The BSD default and original-work scope come from the maintainer's
[shared licensing policy](../../../Aether-standards/docs/LICENSING.md).

| Component | Origin and license basis | Preview treatment / required notice |
| --- | --- | --- |
| Original bin, mk, host recipes and tests | pkg-mgr original work; root BSD-2-Clause LICENSE | Include host workflows and supporting tests with LICENSE. Native helpers/tests remain labeled development-only if retained for the normal suite. Root licensing covers original files without individual headers. |
| hello-local text and ordinary synthetic fixtures | pkg-mgr authored fixture material | Include inputs needed for the compiler-free workflow; preserve exact pinned fixture bytes. |
| Advisory SPDX fixture | Authored metadata explicitly declares DataLicense: CC0-1.0 | Preserve the declared data license and NOASSERTION fields. Those fields do not license any package payload or establish its provenance. |
| bytecount.c | Aether-userland, imported unchanged at the hash in recipes/bytecount/origin.json; SPDX BSD-2-Clause | Include bytecount.c, source.kv, origin.json and its existing LICENSE. Preserve the source notice and staged share/licenses/bytecount/LICENSE. No sibling checkout is needed to build. |
| zlib/zpipe recipe and local zpipe source | Original recipe/filter code; zlib upstream archive is separate | Retain only as optional development material if needed by fixtures. No bundled zlib archive, compiled zlib library or qualified preview zlib workflow. Recipe licensing does not relicense upstream zlib. |
| Experience, Foundations and Distribution releases | Aether-standards v0.1.0 pins; original Aether content under the shared BSD decision | Retain all pinned files and source snapshots byte-for-byte, with root LICENSE and this scope notice outside immutable releases. Preserve cited origins. External reference links are not bundled dependencies or endorsements. Future imported excerpts need separate terms review. |
| User manuals and active operational references | Original pkg-mgr documentation | Include the three mdoc pages and a closed set of workflow/setup/recovery references. The public documentation edition still needs link and reader review after excluding history. |
| docs/archive, docs/evidence and research guidance | Historical plans, research, captured inputs and tool/boot logs; potentially mixed material | Exclude wholesale from the proposed public source package. Keep locally as development evidence; choose any public evidence separately with origin/notice review. |
| Active planning and agent instructions | Project coordination material | Exclude from the public package; replace navigation that currently depends on these files in the public documentation edition. Preserve them in the development repository. |
| Host tools, SDKs and generated binaries | Separately installed Apple/Unix/development tools; their own terms | Do not bundle. Record installed identities and prerequisites. Root BSD licensing makes no statement about them or linked runtime code. |

The three vendored release manifests are validated by `sh tests/check-standards.sh`.
Bytecount's local source and license must match origin.json before assembly; its
source.kv independently binds build input bytes. The host lifecycle test already
compares the installed license with the recipe copy. Preserve existing notices and
immutable hashes; do not add headers to fixtures or vendored releases.

The dated review evidence records exact inspected active-input paths and hashes,
bytecount/source-license comparisons, three standard manifest pins and selected host
tools. It is an owning-task component review, not exhaustive third-party clearance
or independent approval. No external runtime/archive is inferred to be redistributable
from a hash or a URL.

The [public candidate assembler](PUBLIC-SOURCE.md) now uses release/files.tsv as
an exact allowlist, with a separate README and recorded transformations of omitted
development links. Independent content/reader review and remaining release gates
still apply to the exact candidate bytes. The
existing development tar is intentionally broader and must not be uploaded as the
public package. Security reporting must name a real monitored address or private
reporting URL and a triage owner before publication. No placeholder satisfies that gate.

See [host setup](HOST-SETUP.md) and [release acceptance](HOST-RELEASE.md).
