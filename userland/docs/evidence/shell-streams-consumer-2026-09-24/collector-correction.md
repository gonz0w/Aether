# Exact corruption-byte correction

Native105 and host110 tests passed first execution. Independent serial collector
attempt1 expected `Pipe data`; the frozen output.rs changes every leading request
byte p to P, and one-byte short transfers expose both p characters. Therefore the
exact corrupted output is `PiPe data`, three times. Positive output remains exact
`pipe data`. The source branch and observed complete raw log agree. This corrects
the consumer's erroneous literal; it does not relax byte matching or lifecycle,
status, prompt, grant, panic or cleanup requirements.

Preserve check-serial-attempt-1.py and serial-check.log. The initial accept.log also
records the dependent acceptor failing because serial-checks.json was absent; no
acceptance was emitted. Retry uses distinct logs and the one corrected literal.
No native/host rerun or producer-source change. Independent review remains pending.
