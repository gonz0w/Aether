# Command C17 migration evidence

UL-063 CSR-03, 2026-09-06. All 21 host/control cases and nine native cases pass.
Five client ELFs match the C11 baseline exactly; comparison records retain hashes.
Before/after drivers and the reviewed diff isolate C17 selection and removal of
four unreachable scenario branches. Producer fixture C remains C11. Native
inventory, markers and terminal/cleanup expectations remain unchanged.

`host/`, `clients/` and `native/` retain raw results and process receipts. Large
images and the producer checkout remain under build/native-command-userland-o2itu2ft;
receipt hashes bind the exact images and pinned inputs. No failed attempt occurred
in this slice. Historical C11 evidence remains unchanged. Python 3.10 grammar
parses; execution used the recorded host interpreter, not all supported versions.

Readability migration, independent reviews, UL-058 boundaries and the UL-059 public
contract handoff remain open. This does not complete UL-063 or provide a public CLI.
