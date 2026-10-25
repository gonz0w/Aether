# Native reply uncertainty review — 2026-09-06

Read-only pkg-mgr review of Aether-userland UL-058 NB-02. [Exact identities](review.json)
verify 1,284 owner manifest files, 26 ISO/serial pairs (17 combined cases and nine
old-pin regressions), four negative marker sets and the unchanged NB-01 adapter.
Copied receipts and owner reports preserve their bytes. No sibling code was run.

The retained reply-native.c wrapper receives the complete real service reply,
then simulates lost read, malformed read metadata or lost close acknowledgement.
The first two require EIO and an untouched destination. Lost close requires EIO
and subsequent EBADF on the consumed descriptor. Subsequent file/launch/collection
attempts must cause no adapter transport call. Three controls end at child 84;
the private disabled-poison mutant ends at child 94. All four require parent 53,
broker 970/reclaimed 0 and absence of CONNECTIONS PASS. The mutant wrapper stops
the forbidden call before it reaches the service. This does not prove remote
recovery, successful reclamation or all possible lost-reply schedules.

The owner reports 21 host regressions and nine prior client ELFs unchanged; their
reports/artifacts are included in the verified manifest. This review checks
retained evidence and source assertions, not independent re-execution or release
approval. NB-03/04, UL-059 public parser/carrier, ASan and Cam reviews remain open.
Native shell/make and package storage acceptance are separate release gates.

No package runtime, selector, pin, frozen archive or sibling implementation changed.
The initial inspection tried a nonexistent replies-native.c filename; discovery
located reply-native.c. This was a read-path typo, not a test or runtime failure.
Validation commands and documentation hashes are retained in validation.json.
