# Contributing

Contributions should improve factual grounding, honest uncertainty, or scope
control without making ordinary tasks unnecessarily slow or restrictive.

## Local setup

Use Python 3.11 or newer. No dependency installation is needed for project tests
or release tooling. From the repository root:

```bash
python3 manage.py check
python3 -m unittest discover -s tests -v
python3 manage.py build
```

Use `python` or `py -3` instead of `python3` where appropriate. The CI definition
targets Python 3.11 and 3.13 on Linux, plus Python 3.13 on Windows and macOS;
configured targets are not evidence of a successful hosted run. Consult
[VERIFICATION.md](VERIFICATION.md) for what has actually been executed.

## Where changes belong

- Policy: edit the canonical `SKILL.md`, review `CHAT.md`, and identify which
  behavioral evaluation cases should improve or remain unchanged.
- Installer: keep file transformations separate from argument parsing and console
  output. Add tests for observable file behavior or a concrete failure mode.
- Compatibility: cite the relevant official client documentation and record the
  client version used for actual runtime validation.
- Releases: update all three plugin manifest versions together and document the
  change in `CHANGELOG.md`. The root portable manifest supplies the build version.

See [ARCHITECTURE.md](ARCHITECTURE.md) before changing boundaries or adding a
dependency. Keep the code, documentation, commit-facing examples, and error
messages in English. The protocol must continue respecting a user's requested
response language.

## Tests and evaluations

Automated tests cover installation, preservation, removal, errors, package
consistency, and release reproducibility. Use temporary directories; do not edit
your personal agent settings or a production project as part of tests.

Use [EVALUATION.md](EVALUATION.md) for model behavior. Record the actual model,
client, tools, prompts, observations, and failures. Avoid claiming effectiveness
from a self-report, one successful example, or packaging tests.

The optional vendor skill-validation helper may require PyYAML in its own
environment. That dependency is not part of this project. Native Claude and
Codex checks require their respective installed clients and, for behavioral
tests, any credentials or service access those clients normally need.

## Reporting a problem

Use the public repository's issue tracker once the project is hosted. Include the
version, OS, Python/client versions, exact command or prompt, minimal sanitized
input, expected behavior, actual behavior, and relevant output. For an installer
issue, retain the backup locally and share only the portion needed to reproduce.
Do not post tokens, private source, full private conversations, or backup files.

For a vulnerability requiring private details, use the repository's private
security reporting channel if the maintainer has enabled it. No dedicated email
address or response-time commitment is claimed by this package.

## Pull requests

Explain the concrete problem and resulting behavior. Include relevant test or
evaluation evidence and compatibility limits. Keep unrelated cleanup separate.
Do not add provider credentials, fabricated badges, generated caches, build
archives, or claims of universal model compliance.

Contributions to the project are submitted under GPL-3.0-only. Preserve existing
license notices. The project does not require a separate contributor license
agreement in this initial version.
