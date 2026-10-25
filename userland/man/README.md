# Contributor command manuals

For contributors working in this experimental checkout. These mdoc sources
reference actual host tools; they are not installed Aether commands or a complete
base-system manual set. No root authority or network access is required.

| Source | Command described | Status |
| --- | --- | --- |
| [Quality checker](man1/aether-userland-quality.1) | `python3 -B docs/quality/check.py` | Experimental host command; independent reader review and packaged lookup pending |

From the checkout root with mandoc available, read the manual offline:

```sh
mandoc -Tutf8 man/man1/aether-userland-quality.1
```

The name `aether-userland-quality` is a manual label, not an executable alias.
The source is authoritative; rendered copies must record the source digest and
mandoc identity. For contributor validation, keep outputs in an owned directory
under `build/`, run mandoc lint, render ASCII at ordinary and narrow widths and
HTML, then inspect all outputs. See the
[manual validation plan](../docs/evidence/quality-manual-2026-09-06/PLAN.md).

A host rendering pass does not establish target installation paths or section
lookup. UL-061 retains package integration, real reader review and the remaining
command/API/configuration manual inventory. Keep upstream manuals and licenses
intact when packages are selected.
