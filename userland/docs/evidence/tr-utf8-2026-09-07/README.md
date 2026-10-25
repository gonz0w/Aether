# UL-013 / UL-066 tr byte and UTF-8 boundary

Ten characterization cases pass against the pinned GNU9.11 static musl candidate:
a locale probe and four operations under each of C and C.UTF-8. This means the
predeclared byte observations match; it does **not** mean Unicode character
operations pass. [Summary](summary.json), [raw observations](guest.stdout).

| Operation | Input | Observed output in both locales | Character expectation |
| --- | --- | --- | --- |
| Upper to lower class | AZ ÉΣ🙂 | az ÉΣ🙂 | az éσ🙂 |
| Delete alpha class | AéZΩ | éΩ | Empty |
| Delete literal é | éê! | Bytes aa21, invalid UTF-8 | ê! |
| Squeeze literal é | éé | éé | é |

Input/output byte arrays, UTF-8 decoding validity, separate character expectations
and exact process records are retained. The locale probe verifies C=ASCII and
C.UTF-8=UTF-8; changing the locale does not establish character-aware tr behavior.
The non-ASCII deletion removes0xc3 and0xa9 individually, including the leading
byte of ê. All four chosen character expectations fail in each environment.
No broad Unicode, grapheme or locale-wide conclusion beyond these cases is claimed.

The provisional GNU choice remains bounded to tested byte-oriented script needs.
It is not a general UTF-8 text transformer. Native PC-026 status remains unchanged;
UTF-8 terminal display, editing and Zsh support require separate work. No new
provider or libc was selected, and no candidate/source bytes changed.

All ten commands have complete process cleanup; the container is observed absent.
Inputs and sources match their recorded hashes after execution. [Plan](UTF8-PLAN.md),
[syntax](syntax.log), [quality](quality.log). New helpers are BSD-2-Clause;
upstream terms and existing pins are unchanged. New helper review remains pending.

The user stated “reviewed, lets continue” for the preceding provider packet;
[review record](../provider-review-2026-09-07/maintainer-review.json) preserves that
statement and exact packet identity. These new results are an addendum, not an
edit to the reviewed packet or a retrospective approval of this experiment.
Next: carry the byte/character distinction into the supported utility subset;
source trust, native support and later-helper review remain separate gates.
