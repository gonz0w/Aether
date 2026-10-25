# ADP-01-W01 tooling follow-up

The missing-mmdc invocation blocker is resolved. Existing temporary tooling matches
the candidate's dependency package records (root project metadata differs).
No dependency installation, sibling edit or release-pin migration was performed.
`tools.json` records invocation paths, resolved file hashes and dependency versions.

Command (exit 0; complete output in `strict.log`):

```sh
PATH="/private/tmp/aether-docs-render-tools/node_modules/.bin:$PATH" \
PUPPETEER_CACHE_DIR=/private/tmp/aether-docs-browser \
python3 -B docs/standards-review/2026-09-06-rc1-adp01/inputs/tools/check-candidate.py --strict
```

The candidate archive identity remains the one in the committed RC1 review.
The previous missing-tool failure is preserved in that review. This follow-up
passes required host rendering/reference checks, not independent visual/reader
review, complete Aether manuals or runtime compliance. W01 remains partial.
