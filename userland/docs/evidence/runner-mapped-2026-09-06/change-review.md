# UL-059 native collected-result plan

Before code: opt-in runner uses tested admission and collection decoders. Send
one launch, validate receipt before use, consume collection only until a validated
terminal reply (repeat only explicit pending). Unknown transport, malformed reply,
owner error or exhausted observation budget returns1 without replay. This does
not resolve recovery ownership or qualify zero-admission outcomes. Keep child
receipt/kind/full detail separate from cleanup and final CLI status.

After known admission, close parent input once; after collection observe output
EOF and close output once. Failed cleanup returns1 without erasing raw terminal.
Do not confuse shared-position EOF with independent backend byte verification.
The pinned owner enables runner_startup and mapped_results only for new cases.
Normal0/1/2/64/125/126/127/134/255 must map exactly; actual fault134/kind2 maps1.
Link-only child wrappers terminate after real bytecount output and before close,
leaving aliases for owner cleanup. Native mutations ignoring kind and forcing
nonzero to zero require exact child/parent/broker970 records. A local close-error
control performs the real close, then reports EIO; a policy-call wrapper verifies
raw child0/kind1/receipt and cleanup=false survive. Parent1/broker970 is deliberate
rejection, not accepted remote cleanup failure or recovery.

New functions use C17/strict new-source diagnostics; Python3.10+ standard library
and existing pinned tools/SDK, clean environments, owned native180s commands,
guest30s watchdog/no NIC and original file limits. Freeze sources before tests.
Run all existing34 combined native plus13 mapped cases, nine original-pin cases,
result/parser host controls and21 command regressions; compare prior28 client
ELFs. Default pin and finite parent29 behavior must remain unchanged. Retain every
attempt, source/tool/flags/ABI identities, raw serial/output and cleanup receipts.
Run C formatting, Python grammar and quality/standards checks. Foundations O/I/E,
Experience exit policy and approved CE/CC/CP, TD/TC/TE apply; no standards/sibling
change, new package or authority. Technical review by current task; independent
technical/reader review and full owner/public CLI acceptance remain open.
