# Native I/O explicit-stop evidence — 2026-09-05

Decision 0008; BG-032/BG-040. All work was confined to sys-init and private test directories. The kernel and musl descriptor probe were taken unchanged from BG-055's archived snapshot/SDK. Shared pins and companion working trees were not edited. Native memory and SMP were explicitly disabled.

[Results](results.json) retain four exact semantic outcomes: new stop client, deliberately wrong terminal-detail client, skipped backing zeroing, and the original I/O client. The wrong-detail log includes `NATIVE supervisor result=244 reclaimed=0`, proving rejection at its intended assertion. The stop positive and original positive have the exact I/O pass marker; negatives have the exact expected panic and no pass marker. No command timed out. Build/image/client/serial hashes were checked; ISO bytes remain in the recorded work directory.

The first generation is stopped while live and historically ready, before input arrives. Repeated stop retains detail 143/kind 3; both empty outputs become EOF; producer submission/seal reject. After reclaim, status, stop, input, both outputs and reclaim reject the old handle. A distinct second generation starts with open output streams and completes the unchanged input/backpressure/seal/stdout/stderr/EOF transaction, then reclaims successfully.

This does not witness nonempty output retention across stop, actual worker fault closure, POSIX signals, recovery or production init. Those remain separate BG-032/BG-040 work. The native completion marker retains its existing two-reclaim meaning; individual checks live in the pinned policy client.

## Reproduction

Use BG-055's [source archive and SDK](../native-refresh-2026-09-05/README.md), apply the three original source files retained under `source/` to the sys-init checkout, and invoke the new harness with the matching kernel and I/O SDK:

```sh
python3 tests/native-io-stop.py --aether AETHER_SNAPSHOT --sdk IO_SDK --receipt-pin RECEIPT_SHA256 --work NEW_PRIVATE_DIRECTORY
```

`--receipt-pin` is the externally retained SHA-256 of the SDK's evidence.json. The harness checks profile, envelope and ELF identity before allocating its output, freezes kernel/client/input copies and checks frozen source hashes after execution. It does not authenticate a publisher or claim its lightweight input test establishes a bootable ELF. Each command uses an owned process group and a 120-second watchdog; the existing emulator runner supplies its independent 30-second watchdog. Existing work directories reject. Help/version exit 0; invalid usage exits 64, operational errors 1, and SIGINT caught during a child wait exits 130. stdout returns a result/report object; progress and failures use stderr.

[Original invocation](invocation.json) and [commands/results](results.json) record exact arguments. Existing supervision variants pass, wrong_detail and fault_entry rebuilt byte-for-byte identical to BG-055 ([compatibility checks](legacy-compatibility.json)); the original I/O variant also ran on the target in this suite. Functional validation passes all standards checks, 34 model cases/three mutation controls, 38 host cases and 14 harness tests. The new input test checks wrong receipt pins, changed payloads and wrong SDK profiles using an explicitly inert format fixture.

Sources, source hashes, SDK receipt, rebuilt client envelopes, serial and build logs are retained here. SDK ELF, pinned tools, source archive and notices remain in the linked BG-055 evidence; first-party and musl notices are also retained here. SHA256SUMS.json fingerprints this evidence set. This is an internal experiment witness, not a release or third-party licensing audit.
