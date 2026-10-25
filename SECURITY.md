# Reporting a vulnerability

Please use [GitHub private vulnerability reporting](https://github.com/gonz0w/Aether/security/advisories/new).
On the repository's **Security** tab, choose **Report a vulnerability**.

Do not put exploit details, credentials or affected private data in a public issue
or discussion. A private report lets the maintainer investigate before disclosure.
If the private reporting button is unavailable, ask in Discussions for a private
reporting route without including vulnerability details.

## What to include

Include the affected source revision, relevant component, required access or
capabilities, a minimal reproduction, expected behavior and observed impact.
Explain any uncertainty. Small logs or a proof of concept are useful; remove
secrets and unrelated personal data.

Keep destructive or resource-intensive demonstrations out of public automation.
The maintainer can agree on a bounded reproduction and disclosure plan privately.

## Scope and response

Aether is an experimental hobby OS. No release with a supported security
maintenance window has been declared. Reports about the kernel, userland,
sys-init, pkg-mgr and repository tooling are welcome. Host test results and
bounded native fixtures are not a whole-system security assurance claim.

Responses are best effort; there is no promised response time or support SLA.
A report's receipt is not confirmation that it is valid or fixed. The maintainer
will distinguish investigation, a verified fix and any later release action.

For ordinary bugs or build questions, use the public issue forms or Discussions.
