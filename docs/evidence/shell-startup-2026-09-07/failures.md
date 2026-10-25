# Failed attempts

Attempt 1 built all clients and completed 60 older target cases, then rejected
the startup ELF before execution: `invalid launch ELF`. Inspection found the
required PT_TLS missing. The new wrapper now supplies and checks a private TLS
cookie, following the existing native loader contract. No loader rule changed.
Original source, full target directory, report and serial log are retained.
The nine new startup cases are ordered first in attempt 2.

The second source also checks no public FD/signal state after malformed
bootstrap and positive F_DUPFD selection/flags. These were identified during
review before the first successful startup execution.
