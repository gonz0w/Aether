# Legacy work routing

This is the initial migration index, not a live backlog. After the verified
cutover in [PROJECT](../PROJECT.md#public-onboarding-cutover), GitHub Issues own
status, priority, dependencies, ownership and continuation. The onboarding issue
tracks the bootstrap while that cutover is pending. Existing UL/BG/root
identifiers remain references to their durable contracts. New work does not need
a duplicate entry here.

Completed historical work was not reopened. The source audit reconciled all83
userland rows (62 completed) and all38 active/captured sys-init records; superseded
scope and sibling implementation queues are excluded. Capability gates remain
in the roadmap; old planning status fields are historical.

| Planning key | Canonical issue | Legacy identifiers |
| --- | --- | --- |
| AF09-HOST | [#2](https://github.com/gonz0w/Aether/issues/2) | AT-HOST |
| AF09-NATIVE | [#4](https://github.com/gonz0w/Aether/issues/4) | AF09, userland:UL-082 |
| AT-003 | [#1](https://github.com/gonz0w/Aether/issues/1) | AT-003 |
| FS-EXEC-CONTRACT | [#12](https://github.com/gonz0w/Aether/issues/12) | R1-04, VM-01:file-backed-loading, VM-02:file-backed-loading |
| FS-HOME-PREP | [#3](https://github.com/gonz0w/Aether/issues/3) | FS-HOME-PREP, userland:UL-082 |
| FS-LIFETIME | [#9](https://github.com/gonz0w/Aether/issues/9) | userland:UL-082, R1-03, R1-06 |
| FS-MUTATIONS | [#10](https://github.com/gonz0w/Aether/issues/10) | userland:UL-082, R1-03, UP-06:filesystem-slice |
| HO-01 | [#51](https://github.com/gonz0w/Aether/issues/51) | HO-01 |
| LATER-RESEARCH | [#52](https://github.com/gonz0w/Aether/issues/52) | root:later-research |
| M4 | [#40](https://github.com/gonz0w/Aether/issues/40) | M4 |
| M5 | [#49](https://github.com/gonz0w/Aether/issues/49) | M5 |
| M6 | [#50](https://github.com/gonz0w/Aether/issues/50) | M6 |
| PKG-BUILDS | [#47](https://github.com/gonz0w/Aether/issues/47) | pkg-mgr:BG-012, pkg-mgr:BG-013, pkg-mgr:BG-014, pkg-mgr:BG-015, pkg-mgr:BG-026, pkg-mgr:BG-027, pkg-mgr:BG-028, pkg-mgr:BG-030 |
| PKG-BUNDLE-NATIVE | [#18](https://github.com/gonz0w/Aether/issues/18) | R1-05:bytecount-native |
| PKG-DURABILITY | [#48](https://github.com/gonz0w/Aether/issues/48) | pkg-mgr:BG-009, pkg-mgr:BG-031, R1-03:post-R1-rollback |
| PKG-NATIVE-IDENTITY | [#14](https://github.com/gonz0w/Aether/issues/14) | R1-05:target-admission |
| PKG-REMOVE-CONTRACT | [#15](https://github.com/gonz0w/Aether/issues/15) | R1-05:remove |
| PKG-TRUST | [#46](https://github.com/gonz0w/Aether/issues/46) | pkg-mgr:BG-011, pkg-mgr:BG-029, pkg-mgr:BG-043 |
| POST-IDENTITY | [#41](https://github.com/gonz0w/Aether/issues/41) | userland:UL-010, UP-06:post-R1 |
| QUALITY-CODE | [#27](https://github.com/gonz0w/Aether/issues/27) | userland:UL-063, sys-init:BG-056:code |
| QUALITY-DOCS | [#25](https://github.com/gonz0w/Aether/issues/25) | userland:UL-061, userland:UL-071, sys-init:BG-056:documentation, pkg-mgr:reader-review, R1-07:documentation |
| QUALITY-EXTENDED | [#26](https://github.com/gonz0w/Aether/issues/26) | userland:UL-013, userland:UL-062, sys-init:BG-054:local-harness, sys-init:BG-056:extended, pkg-mgr:release-testing |
| R1 | [#5](https://github.com/gonz0w/Aether/issues/5) | R1 |
| R1-01 | [#6](https://github.com/gonz0w/Aether/issues/6) | R1-01, userland:UL-008, UP-07 |
| R1-02 | [#8](https://github.com/gonz0w/Aether/issues/8) | R1-02, UP-02, userland:UL-003, userland:UL-007, userland:UL-015 |
| R1-03 | [#11](https://github.com/gonz0w/Aether/issues/11) | R1-03, userland:UL-082 |
| R1-04 | [#13](https://github.com/gonz0w/Aether/issues/13) | R1-04, userland:UL-059 |
| R1-05 | [#19](https://github.com/gonz0w/Aether/issues/19) | R1-05 |
| R1-06 | [#16](https://github.com/gonz0w/Aether/issues/16) | R1-06, userland:UL-012, sys-init:BG-067, sys-init:BG-020, sys-init:BG-021, sys-init:BG-028, sys-init:BG-032, sys-init:BG-035, sys-init:BG-038, sys-init:BG-039, sys-init:BG-040, sys-init:BG-042, sys-init:BG-043, sys-init:BG-044, sys-init:BG-045, sys-init:BG-046, sys-init:BG-050:v1 |
| R1-07 | [#29](https://github.com/gonz0w/Aether/issues/29) | R1-07 |
| SDK-SESSION-PACKAGE | [#24](https://github.com/gonz0w/Aether/issues/24) | pkg-mgr:session-runtime-intake, userland:UL-007:SDK-consumption |
| SI-01 | [#33](https://github.com/gonz0w/Aether/issues/33) | SI-01 |
| SI07-REMAINDERS | [#21](https://github.com/gonz0w/Aether/issues/21) | sys-init:BG-067:SUSTAIN, userland:UL-007:SUSTAIN |
| SYS-ACTIVATION | [#45](https://github.com/gonz0w/Aether/issues/45) | sys-init:BG-041, sys-init:BG-048, sys-init:BG-049, sys-init:BG-050:extensions |
| SYS-HISTORY | [#43](https://github.com/gonz0w/Aether/issues/43) | sys-init:BG-057:extensions, sys-init:BG-058:extensions, sys-init:BG-060, sys-init:BG-062, sys-init:BG-047 |
| SYS-PUBLISH | [#44](https://github.com/gonz0w/Aether/issues/44) | sys-init:BG-036, sys-init:BG-037, sys-init:BG-029 |
| SYS-RECOVERY | [#42](https://github.com/gonz0w/Aether/issues/42) | SI-03:broader, sys-init:BG-031, sys-init:BG-033, sys-init:BG-051, sys-init:BG-030:recovery-payload |
| UL-009-PREFLIGHT | [#7](https://github.com/gonz0w/Aether/issues/7) | userland:UL-009 |
| UL-011-TOOLS | [#17](https://github.com/gonz0w/Aether/issues/17) | userland:UL-011, userland:UL-066 |
| UL-016-TRUST | [#28](https://github.com/gonz0w/Aether/issues/28) | userland:UL-016 |
| UL-058-BOOTSTRAP | [#20](https://github.com/gonz0w/Aether/issues/20) | userland:UL-058 |
| UL-067-ACCEPT | [#30](https://github.com/gonz0w/Aether/issues/30) | userland:UL-067 |
| UL-078-SDK | [#22](https://github.com/gonz0w/Aether/issues/22) | userland:UL-078 |
| UL-079-SDK-RECLAIM | [#23](https://github.com/gonz0w/Aether/issues/23) | userland:UL-079 |
| UP-01 | [#34](https://github.com/gonz0w/Aether/issues/34) | UP-01 |
| UP-03 | [#35](https://github.com/gonz0w/Aether/issues/35) | UP-03 |
| UP-04 | [#36](https://github.com/gonz0w/Aether/issues/36) | UP-04 |
| UP-05 | [#37](https://github.com/gonz0w/Aether/issues/37) | UP-05 |
| UP-06 | [#38](https://github.com/gonz0w/Aether/issues/38) | UP-06 |
| UP-08 | [#39](https://github.com/gonz0w/Aether/issues/39) | UP-08 |
| VM-01 | [#31](https://github.com/gonz0w/Aether/issues/31) | VM-01 |
| VM-02 | [#32](https://github.com/gonz0w/Aether/issues/32) | VM-02 |


## Absorbed and superseded sys-init records

These five records were reconciled without inventing duplicate implementation
work or claiming fresh acceptance:

| Legacy record | Disposition and remaining route |
| --- | --- |
| BG-069 | The agreed serialized fork staging/framing foundation supersedes its old missing-seam notes; no duplicate staging issue. |
| BG-070 | The bounded AF07/AF08 owner transaction has native evidence. Wider product/schedule scope remains in [R1-02 #8](https://github.com/gonz0w/Aether/issues/8), [R1-06 #16](https://github.com/gonz0w/Aether/issues/16) and [consumer remainder #21](https://github.com/gonz0w/Aether/issues/21). |
| BG-072 | ABI30 mapping and later complete-owner offline fit supersede the missing-placement item; native peak/assembly acceptance remains separate. |
| BG-073 | In-place construction and whole-owner fit supersede the old16384-byte initialization blocker. AF09 integration remains in [#3](https://github.com/gonz0w/Aether/issues/3); no fit or guest gate is waived. |
| BG-019 | The old research-intake coordination queue is superseded by accepted v1 scope and its specific records. Remaining work routes to [#16](https://github.com/gonz0w/Aether/issues/16) and deferred [#42](https://github.com/gonz0w/Aether/issues/42), [#43](https://github.com/gonz0w/Aether/issues/43), [#44](https://github.com/gonz0w/Aether/issues/44), [#45](https://github.com/gonz0w/Aether/issues/45). |
