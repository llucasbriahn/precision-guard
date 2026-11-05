# Precision Guard plugin

Evidence-based answers, explicit uncertainty, and strict scope control. This is
an instruction plugin, not a guarantee of factual correctness or a tool-permission
enforcement layer. No measured reduction in hallucinations is claimed.

## Claude Code

Extract the plugin archive and run:

```bash
claude plugin validate /absolute/path/to/precision-guard
claude --plugin-dir /absolute/path/to/precision-guard
```

Then invoke `/precision-guard:precision-guard` followed by your task. A loaded
skill is available for invocation; it is not guaranteed to activate on every turn.

## Codex and project instructions

The plugin contains a portable manifest and a Codex compatibility manifest.
Use the complete source distribution for the local marketplace, installer,
step-by-step integration guide, tests, and evaluation procedures.

For standalone skill discovery, copy `skills/precision-guard` into a supported
skill directory such as a Codex project's `.agents/skills/precision-guard`, then
invoke `$precision-guard` in a new session. For persistent guidance, copy the body
of `skills/precision-guard/SKILL.md` without its YAML metadata into the host's
project instruction file, preserving existing instructions, or use the installer
from the complete source distribution.

## License

GPL-3.0-only. This plugin directory includes the complete `LICENSE` and project
`NOTICE` for both archive and marketplace distribution. The package validator
checks that they match the canonical repository-root copies. No runtime dependency, network
service, API key, or lifecycle hook is required by this plugin.
