# Collected runner result evidence — 2026-09-06

Pass: 51 command cases, 9 inherited-launch cases, 6 connection cases, kernel host
checks, 73 Python tests, three release-pin checks and workflow validation. One
attempt per runtime suite, no runtime failure or timeout. A Rust format issue was
corrected before qualification; initial note and final pinned format checks are
retained. The mapped broker is 7064 bytes (8192 limit).

Nine normal statuses (0, 1, 2, 64, 125, 126, 127, 134, 255) are preserved. Actual
#UD kind 2/detail 134 maps to parent 1 with raw child identity retained. Every
accepted case requires ordered child/parent/backend terminal records in both
generations, independent file verification and broker 100/reclaimed 6. Two broken
parents (fault reported as normal 134; normal 64 reported as 0) require their exact
child/parent records then broker 970/reclaimed 0. Generic failure cannot pass.

[Contract](../../NATIVE-COMMAND-IO.md#collected-runner-result-mapping).
Direct C policy checks include out-of-range detail, unknown kind and cleanup-false
inputs. They are not native out-of-range or failed-cleanup evidence: native launch
currently masks normal exits to eight bits. No ABI/authority/quota or sibling pin
changed. Legacy exit-29 cases remain intact. Carrier and mapped-result modes are
separately tested; full public parser/error/help/recovery integration remains open.

`results.json` binds reports and source archive. Profile directories retain serial,
build and static-analysis logs, payloads, client/kernel ELFs, broker images,
startup records and maps under 2 MiB. Rebuildable ISOs are omitted; complete output
paths remain recorded. Source, tests, contracts, UL-059 proposal snapshot and
approved standards snapshot are archived. External SDK/tools are bound separately
by suite receipts/digests. Commands and exact UTC start/end/status are captured in
`*-attempt.json`; pinned format checks in `format-attempts.json`. This is scoped
producer/QEMU qualification, not independent consumer or release acceptance.
