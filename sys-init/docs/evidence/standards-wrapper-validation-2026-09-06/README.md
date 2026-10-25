# Standard wrapper verification evidence

Decision 0103 closes two local findings without modifying pinned releases.
Experience now validates exact pins, symlink roots/files, manifest paths and
complete inventory before executing the checker. Experience and Distribution
explicitly set PYTHONOPTIMIZE=0 for the child while preserving other environment
values. Parent flags/environment are not altered. Successful output and ignored
argument behavior remain unchanged; malformed Experience inputs now use the
stricter local rejection paths documented in its manual.

Four required harness tests cover 45 parameterized scenarios: nine malformed
locks, twelve manifest/inventory failures, four symlink configurations and twenty
positive/required-assertion cases across both wrappers and five optimization
configurations. Invalid fixtures must reject before their execution marker can
be written. Deliberately failing assertions cannot become a successful checker
when the parent or inherited environment is optimized. Fixtures are synthetic
private trees; no real release was edited to create negative inputs.

All ten aggregate gates pass in out/checks/run-5aqgn48h, retained in validation/.
Six runs of the actual pinned releases preserve their original stdout across
normal/inherited/parent optimization settings. compatibility.json retains those
commands; before/ preserves the original wrappers and baseline streams.
pins-before.json was verified after runs: every lock and vendor file is unchanged.

Updated manuals render at 78/60 columns and HTML; terminal text was inspected.
Lint retains only the exact experimental-OS STYLE notice from decision 0099.
HTML visual and independent reader review remain pending. Source snapshots
include final code, tests, inventory and documentation; the final STANDARDS
adoption note was appended after the aggregate run and changes no checked code.

No native behavior, source, ABI, sibling repository or shared pin changed.
The check is not confinement against concurrent filesystem mutation. Standalone
subprocess bounds, full tool closure, remaining eight command manuals, detailed
API coverage and independent/target review remain open.
