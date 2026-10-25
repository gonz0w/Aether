# RL-01–12 producer audit

Disposition is bounded producer coverage, not acceptance of the real userland CLI.
The request and return-package source documents are retained under `review-inputs/`.
Current command receipts supply exact cfg/defines, commands, expected panic context,
artifacts and passed outcomes; sources implement independent backend/lifecycle checks.

| ID | Producer witness / controls | Remaining consumer responsibility or limit |
| --- | --- | --- |
| RL-01 | streams-help/version: exact independent stdout, empty stderr, exit0, zero launch/collection, four reclaims | Actual parser selects sole help/version; proposed version text is not a release assertion |
| RL-02 | streams-usage: exact stderr, empty stdout, exit64 and no child/request | Missing/unknown/extra/empty argument classification belongs to actual userland parser; producer deliberately does not duplicate four equivalent policy inputs |
| RL-03 | streams-denial-name: actual validator ENOENT, exactly one request, no admission, exact text/status2 | Consumer classifies only complete validated error replies |
| RL-04 | streams-denial-rights: actual rights-widening EACCES before admission | Independent consumer decoder and rights interpretation |
| RL-05 | streams-denial-busy: real partial channel reservation EBUSY, restored pair availability after second generation; leak control1342 | Finite three-generation budget; no unbounded reuse claim |
| RL-06 | streams-short/help0; new streams-usage-short/64 and streams-denial-short/2; success-short child output | Positive one-byte writes only; all possible fragmentation schedules unqualified |
| RL-07 | streams-zero/fatal/usage-zero/exhaust and denial-fail cases: exact prefixes/status1, no replay; retry/hide controls | Arbitrary backend crashes and general unknown admission/collection remain unsupported |
| RL-08 | streams-close-error and denial-fail-name-close: confirmed EIO consumption; actual reply-cut close cases distinguish unknown remote result | Owner retirement after terminal/EOF does not retroactively acknowledge a lost close |
| RL-09 | streams-start-* plus rights/role/generation: missing/count/duplicate FD/rights/stale fields reject with startup110, zero publication; AERIO001 fourth-child-role rejection | Missing role represented by declared count; not missing bytes/transport EOF. Exhaustive four-role and truncated combined startup coverage remain unqualified |
| RL-10 | streams-skip/byte/sink; new streams-help-launch rejects op4 at1302; every stream run forbids child slot2 | Actual parser-side unintended launch decision must also be tested by userland |
| RL-11 | skipped output/close, local-premature and stale bootstrap controls; new success-stale-collect rejects generation1 receipt in generation2 at1404/reclaimed3 | Stale retained-result check is a bounded child-collection witness, not general reconciliation |
| RL-12 | Complete command suite preserves finite/startup/mapped/combined profiles; connections and inherited-launch suites; new four-role selected result/startup witnesses | Userland reruns its own prior66/legacy9 tests against its own SDK and selected new pin |

Counts remain distinct: local/denied parent+backend complete four native reclaims;
successful child cases complete six. No local numeric exit proves admission status,
delivery or cleanup by itself. Owner reference validation and kernel channels grant
authority; names, carrier roles and descriptor numbers alone do not.

Independent implementation/reader review is pending. This return candidate supplies
producer evidence and names omissions exactly as requested; it does not waive
missing extended/fuzz coverage, implement general unknown recovery, accept UL-059/067,
or claim an assembled filesystem/package/shell release.
