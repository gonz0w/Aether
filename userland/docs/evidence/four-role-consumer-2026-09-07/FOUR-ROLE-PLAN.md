# M3 / UL-059 four-role consumer slice

Consume the privately verified runner return candidate, preserving existing native
consumer bytes. The231 SDK files match the tested consumer pin. New AERIO001
adapter is opt-in and parent-only; child keeps the old two-binding adapter.

Validate the complete160-byte AERIO001 frame before publishing four ordered roles:
stdout1/write512,stderr2/write256,child-input3/read6,child-output4/read-write64.
Validate exact magic,count,generation,refs,rights,capacities and all reserved bytes.
Generation1/2 only for this two-generation experiment. Child refs map via indices2/3;
no native authority inferred from fd/name. Reuse the existing transfer/file logic
with four validated slots, preserving poison,counts,error/close semantics.

Use the actual existing logical-startup decoder/selector and result policy in the
new runner. Close input after admission, consume collection once then verify ECHILD,
check shared-output EOF, close remaining three roles and preserve terminal kind.
Independent backend output/reclaim must still be verified in native execution.
This preparation does not itself claim a native pass or M3 acceptance.

Quality C/CP/TD/TE, Foundations O/I/E and current process/source-review limits apply.
No shared standards or old producer pin change. New source BSD-2-Clause,C17,
pinned Clang21.1.8/strict warnings. Test decoder valid frames for both generations,
each byte mutation,wrong lengths/generation and unchanged destination on rejection;
compile new adapter/runner against verified native SDK. Run format and quality.
Native rebuild/boot with source-built owner/backend and existing child is the next
required gate, including wrong-role/omitted-close controls and six reclaim oracle.
