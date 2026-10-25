# UL-056 bytecount preparation evidence

Ten host-libc cases and eleven injected command-logic controls pass. Native output
is an x86-64 musl object only, with public libc imports; no native executable,
bootstrap, TLS image or command-runner execution is claimed. summary.json records
source/tool identities and commands. source/ retains command and reviewed candidate
bytes; candidate-review.json identifies read-only owner inputs. The host uses its
platform libc/SDK. Large or production-package readiness is not inferred.
[Program and tests](../../../experiments/command-runner/README.md).
SHA256SUMS inventories all other retained files. Standards checks pass.
