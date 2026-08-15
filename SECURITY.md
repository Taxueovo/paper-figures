# Security Policy

## Supported version

Security fixes target the latest commit on `main`.

## Reporting a vulnerability

Please use GitHub's **Security → Report a vulnerability** flow for this repository. Do not include credentials, private datasets, or exploit details in a public issue.

Expect an acknowledgement within seven days. Reports should include affected versions, reproduction steps, impact, and any proposed mitigation.

## Execution boundary

`paper-figures render` and `paper-figures batch` execute user-selected Python source in a subprocess. They enforce time and output contracts but do not provide an operating-system sandbox. Only run trusted figure code and use an isolated environment for third-party sources.
