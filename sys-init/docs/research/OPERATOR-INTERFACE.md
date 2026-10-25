# Operator interface research

Observed 2026-09-05. BG-016 complete as research. The candidate interface is consolidated in the [runtime draft](../specs/RUNTIME-V0.md); no command below is installed or implemented.

| Interface | Observed convention | Lesson |
| --- | --- | --- |
| [systemctl](https://raw.githubusercontent.com/systemd/systemd/main/man/systemctl.xml) | Enable/disable and start/stop are distinct; --now combines them | Separate persistent intent from current activation in our basic vocabulary |
| [FreeBSD service](https://man.freebsd.org/cgi/man.cgi?query=service&sektion=8&format=html) | Familiar script/action invocation under a restricted boot-like environment | Predictable environment and short verbs help; script success still needs a lifecycle contract |
| [OpenRC rc-service](https://raw.githubusercontent.com/OpenRC/openrc/master/man/rc-service.8) | Resolves and invokes named service scripts and offers discovery options | Use stable service names; keep lookup failures explicit |
| [runit sv](https://smarden.org/runit/sv.8) | Up/down express supervision intent; start/stop can wait; sent-command success differs from waited success | Receipt, completion and client timeout must be distinct results |
| [s6-rc](https://skarnet.org/software/s6-rc/s6-rc.html) | Named selection drives graph transitions; exposes partial failure and timeout; dry-run is available | Make scope and plan inspectable, and never imply graph-wide rollback from a failed operation |
| [illumos svcadm](https://smartos.org/man/8/svcadm) | Enable, disable, restart and maintenance administration use service instances | Stable identity and explicit recovery actions are preferable to process-name manipulation |
| [historical launchctl](https://raw.githubusercontent.com/apple-oss-distributions/launchd/main/man/launchctl.1) | Start/stop address labels; stop can be followed by policy-driven restart | Define whether stop changes intent. Do not surprise operators with immediate automatic resurrection |

These primary manuals were read, not executed. Upstream branch content is not pinned release behavior; Apple's source is historical and is not guidance for current macOS commands. This survey supports vocabulary, not cross-platform command compatibility.

Propose `list`, `status`, `explain`, `start`, `stop`, `restart`, `operation` and `wait` for the first live prototype, plus offline `check` and `plan`. Keep enable/disable for the later persistent-profile contract. A client wait timeout must say the operation may still be running and provide its ID. Unknown runtime state is not equivalent to stopped. Do not overload `status` exit failure to mean every unhealthy service: status retrieval and state predicates need distinct contracts.

Human status should answer what was requested, what is observed, why it differs, and which action is pending. Machine output requires versioned fields and stable reason codes; avoid forcing scripts to parse prose. Debugging should start with explanation and bounded logs rather than an unscoped shell running with supervisor authority.

BG-050 captures exact command grammar, exit statuses, request deduplication and authorization; BG-045 retains status/error/boot-failure fixtures. BG-051 captures bounded recovery workflows and the no-shell/no-console cases. The draft makes these boundaries explicit before implementation. No production CLI or rescue promise follows from research completion.
