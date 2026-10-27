# Pinned passive policy-selection checker

Source: [Agent Temper tools/check_policy.py](https://github.com/gonz0w/agent-temper/blob/781a4b9f71d002b93bc4ad26669d01a3b37c482e/tools/check_policy.py)
at immutable revision `781a4b9f71d002b93bc4ad26669d01a3b37c482e`.
The helper is copied unchanged outside the immutable method bundle.
SHA-256: `e61f9bac92fc5296c3f12182f6490ed957006da36cba9f2900213af864cd2d9c`.
The unchanged upstream [BSD-3-Clause license](LICENSE) retains its copyright,
conditions and disclaimer; its SHA-256 is `1bc9ce76b659a58c7b8edb88304880f36fd2a005f7b7f3349d1efc860d8deb87`.
The repository's original-work license does not relicense this imported helper.

With an existing Python 3.11+ interpreter, from the repository root run:

```sh
python3 -B tools/temper/check_policy.py --root "$PWD" --manifest policy.toml --as-of 2026-10-27
```

Choose the actual explicit assessment date for later checks. The helper reads
selected Markdown files and bounded TOML as inert data. Exit 0 means no declared
mechanical selection errors; exit 1 reports such errors as JSON. It performs no
candidate import, document command, network access, tool installation or CI wiring.
Its selection authority, execution authority and policy conformance fields remain
`unverified`. Approval, policy meaning, undeclared conflicts, event expiry and
actual check applicability need the existing source/reader review. The manual
command grants no product, host/native, integration or consequential authority.

Updates require the existing bounded work and review process: compare the exact
upstream helper and license, record the replacement revision/hashes, run meaningful
allowed source/fixture checks and preserve local policy and required gates.
