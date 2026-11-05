# Precision Guard

A small instruction plugin for evidence-based answers, explicit uncertainty, and strict scope control. Licensed under **GPL-3.0-only**. The project is written in English; agents should still respond in the user's requested language.

**This is behavioral guidance, not a truth detector or a security boundary.** It cannot guarantee zero hallucinations. No measured reduction in hallucinations is claimed. It asks the agent to verify material claims, distinguish inference from evidence, avoid unnecessary changes, and report only actions and checks that actually occurred.

For maintainers: [Architecture](ARCHITECTURE.md) · [Contributing](CONTRIBUTING.md) · [Releasing](RELEASING.md) · [Changelog](CHANGELOG.md) · [Verification](VERIFICATION.md).

Repository: [llucasbriahn/precision-guard](https://github.com/llucasbriahn/precision-guard).

## Choose how to use it

| Mode | What it does | Best fit |
| --- | --- | --- |
| Project instructions | Adds the protocol to the project's instruction files | Guidance across tasks in that project |
| Native plugin | Makes the skill available through Claude Code or Codex | Explicit invocation and distribution |
| Chat prompt | Supplies instructions in a conversation | Chat products and other agents |

Installing a skill does **not** mean its full instructions run on every turn. Use project instructions for persistent project guidance. Loading remains subject to the client's discovery rules, instruction hierarchy, context limits, and settings. Skills load when selected or invoked. See [OpenAI's skills documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code's plugin overview](https://code.claude.com/docs/en/plugins).

The plugin contains Markdown and JSON only. The optional installer targets Python 3.11+ and uses only its standard library. The installer makes local file changes; it does not call models, access the network, modify tool permissions, or install the native plugin into your account.

## 1. Use persistent instructions in a project

Extract this package, open a terminal in its directory, and replace `/path/to/your/project` with an existing project directory. Commands below use a POSIX shell; on Windows, use your Python launcher (for example `py -3`) and Windows paths, or run the commands in WSL.

Preview the changes:

```bash
python3 install.py --target both --project "/path/to/your/project" --dry-run
```

Apply them:

```bash
python3 install.py --target both --project "/path/to/your/project"
```

Use `--target codex` to edit only `AGENTS.md`, or `--target claude` to edit only `CLAUDE.md`. Start a new agent session from the target project afterward.

The installer inserts the full protocol between managed comment markers, preserves existing content outside that block, and creates a uniquely named `.bak` file before changing an existing file. Repeating an unchanged installation has no effect. Updating the package and rerunning the installer replaces the managed block. Do not edit its markers; keep your own rules outside them. Backups can contain private project instructions, so keep them out of version control.

Codex may prefer an `AGENTS.override.md` over an `AGENTS.md` in the same directory, and more local instructions can take precedence. The installer detects a nonempty adjacent override and asks you to select it explicitly if appropriate. [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

For that explicit choice:

```bash
python3 install.py --file "/path/to/your/project/AGENTS.override.md" --dry-run
python3 install.py --file "/path/to/your/project/AGENTS.override.md"
```

Claude Code supports persistent guidance in `CLAUDE.md`; check `/memory` and the relevant project instruction files if the rules do not load. [Claude Code memory documentation](https://code.claude.com/docs/en/memory).

### Remove project instructions

```bash
python3 install.py --target both --project "/path/to/your/project" --remove
```

Removal deletes only the managed block, preserving text before and after it. An instruction file created by the installer is left empty if it has no other content. Backups remain available. For `--file` installations, use the same `--file` path with `--remove`.

The installer validates all targets before writing, uses atomic replacement for each file, preserves existing file modes, and rejects symlinks and malformed or duplicate blocks. Multi-file installation is not one filesystem transaction: an I/O failure during writing can leave earlier files updated. Use the reported backups if recovery is needed. It is not a sandbox against hostile concurrent filesystem changes.

## 2. Load the native Claude Code plugin

With Claude Code installed, run from this package directory:

```bash
claude plugin validate ./plugins/precision-guard
claude --plugin-dir ./plugins/precision-guard
```

Inside the session, invoke:

```text
/precision-guard:precision-guard Fix the reported bug with the smallest sufficient change. Verify the result and report any checks you could not run.
```

To install from the public repository:

```bash
claude plugin marketplace add llucasbriahn/precision-guard
claude plugin install precision-guard@precision-guard-local
```

For a local checkout instead:

```bash
claude plugin marketplace add /absolute/path/to/precision-guard
claude plugin install precision-guard@precision-guard-local
```

Restart your session and invoke the same skill command. The marketplace path is the **package root**; `--plugin-dir` points to **plugins/precision-guard**. Native plugin installation makes the skill available; use section 1 when you want the rules in project instructions too. These commands follow the official [plugin creation guide](https://code.claude.com/docs/en/plugins/create) and [marketplace guide](https://code.claude.com/docs/en/plugins/create-marketplace). Native installation changes the agent's plugin configuration and is a separate step you run yourself.

## 3. Use it in Codex

### Native plugin

For Codex CLI versions exposing the plugin commands:

```bash
codex plugin marketplace add llucasbriahn/precision-guard
codex plugin add precision-guard@precision-guard-local
```

For a local checkout, replace `llucasbriahn/precision-guard` with the absolute
path to this package's root directory.

Restart your session, select the Precision Guard skill from the available skills, and include your task. Check `codex plugin --help` if your version differs. These command forms were checked against the installed Codex CLI 0.166.0 help; native installation was not executed in this workspace.

The package includes a portable `plugin.json`, a Codex compatibility manifest, and a repository marketplace at `.agents/plugins/marketplace.json`. [OpenAI plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins).

### Standalone skill fallback

If your client does not expose native plugin installation, copy the skill into your project. The following example refuses to overwrite an existing skill directory:

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

source = Path("plugins/precision-guard/skills/precision-guard")
target = Path("/path/to/your/project/.agents/skills/precision-guard")
shutil.copytree(source, target)
print(f"Installed skill: {target}")
PY
```

Start a new Codex session from that project and invoke:

```text
$precision-guard Review this change for unsupported claims and work outside the requested scope.
```

Codex discovers repository skills in `.agents/skills`; select one installation method to avoid duplicate skill entries. [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills). For guidance across the project's tasks, also use section 1.

## 4. Other coding agents

There is no claim that one native plugin format works in every agent. The portable layer is the protocol text. Install it in the instruction mechanism documented for your client.

### Gemini CLI

```bash
python3 install.py --file "/path/to/your/project/GEMINI.md" --dry-run
python3 install.py --file "/path/to/your/project/GEMINI.md"
```

Start a new session and inspect the loaded context with `/memory show`. [Gemini CLI context files](https://geminicli.com/docs/cli/gemini-md/).

### GitHub Copilot

```bash
python3 install.py --file "/path/to/your/project/.github/copilot-instructions.md" --dry-run
python3 install.py --file "/path/to/your/project/.github/copilot-instructions.md"
```

Use a client and feature that support repository custom instructions. Support and precedence vary by surface. [GitHub Copilot custom instructions](https://docs.github.com/en/copilot/concepts/prompting-and-context/custom-instructions).

### Cursor

Use the project's `AGENTS.md` through the installer:

```bash
python3 install.py --file "/path/to/your/project/AGENTS.md" --dry-run
python3 install.py --file "/path/to/your/project/AGENTS.md"
```

Alternatively, create a project rule in Cursor's rule editor, choose **Always Apply**, and paste the protocol exported by `python3 install.py --print`. Cursor documents both `AGENTS.md` and `.mdc` project rules. [Cursor rules](https://cursor.com/docs/rules).

### Another agent or your own application

Run `python3 install.py --print` and place the output in the agent's supported instruction field. If you own an API-based application, include the protocol in the application-controlled instruction layer supported by that API, alongside the task and evidence. Verify the correct parameter and role in that provider's current documentation; this project does not assume a universal API schema.

A filename alone does not activate instructions in an unsupported client. Confirm loading and test behavior in the actual environment.

## 5. Chats

1. Open [CHAT.md](CHAT.md).
2. Copy the text inside its code block into a new conversation, or into a supported custom-instructions field if it fits that field's limits.
3. Replace the final placeholder with your request.
4. For the complete rules, use `python3 install.py --print` instead.
5. Repeat in new conversations unless your product persists those instructions. Do not assume the agent can remember instructions absent from its active context.

No Python runtime or plugin installation is needed when pasting the prompt. In an ordinary chat this is a user instruction, not a privileged system instruction.

## Why the example protocol was adjusted

| Original idea | Precision Guard behavior |
| --- | --- |
| Require 100% certainty | Require adequate evidence and disclose remaining uncertainty |
| Claim something was absent from training data | Describe the evidence available in the current session |
| Always deny real-time access | Inspect actual tools and use authorized sources when available |
| Replace unsupported claims with “users report” | Remove unsupported claims instead of inventing a different authority |
| Always ask a closing question | Ask only when a material information gap remains |
| Avoid all unstated work | Complete necessary work while excluding unrelated additions |

These are design choices for this package, not measured performance claims. The labels are `[INFERENCE]`, `[SPECULATION]`, `[UNVERIFIED]`, and `[GENERALIZATION]`. Requested fiction and reproducible calculations remain possible without unnecessary research.

## Validate and maintain

Run package validation and the automated tests:

```bash
python3 manage.py check
python3 -m unittest discover -s tests -v
python3 manage.py build
```

The build writes a full-source ZIP, a plugin-only ZIP, and `SHA256SUMS` into `dist/`. See [RELEASING.md](RELEASING.md) for archive layouts and publishing steps. The included GitHub Actions workflow is configured to run tests and build artifacts; a successful hosted run is not claimed until one actually occurs.

See [EVALUATION.md](EVALUATION.md) for behavioral checks and a comparison procedure. Automated tests verify file handling and package contracts; they do **not** establish model accuracy or adherence.

The canonical full protocol lives in [SKILL.md](plugins/precision-guard/skills/precision-guard/SKILL.md). The installer reads its body directly. If you change it, rerun installations to update their blocks and review the shortened chat prompt for consistency. Bump plugin manifest versions together before distributing a new release.

This package includes no MCP server, lifecycle hook, response interception, telemetry, or model API integration. Such components are not needed to distribute these instructions. Enforcing tool permissions, filesystem boundaries, or structured output requires controls in the host application; a prompt cannot provide those controls.

Documentation references were consulted on 2026-11-05. Product capabilities and command syntax can change. Only the local verification described in [VERIFICATION.md](VERIFICATION.md) has been performed.

## License

The code, instructions, and documentation are licensed under **GNU GPL version 3 only**, identified as `GPL-3.0-only`. See [LICENSE](LICENSE) and [NOTICE](NOTICE). Release archives include both files. Third-party product names and linked documentation remain the property of their respective owners; this project is independent of those providers.
