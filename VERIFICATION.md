# Verification record

Date: 2026-11-05. This file distinguishes observed local results from intended
compatibility. It should be updated with evidence when further checks run.

| Area | Status | Evidence or limitation |
| --- | --- | --- |
| Automated local suite | Passed | 27 tests passed on Linux with Python 3.13.16, covering installation, errors, preservation, updates, archives, and package contracts |
| Package structure | Passed | `python3 manage.py check` checked manifest agreement, skill fields, marketplace paths, matching GPL files, and relative documentation links |
| Source archive extraction | Passed | The extracted source validated and installed into a fresh temporary project; the complete 27-test suite also passed from the extracted source |
| Reproducible builds | Passed | Tests compared two builds after changing a source file's timestamp and verified identical archive bytes and checksum files |
| Release archive integrity | Passed | Both ZIPs passed CRC checks; SHA-256 checksums and embedded license copies matched the source |
| Codex CLI command forms | Checked | Local `codex-cli 0.166.0` help exposes `plugin marketplace add` and `plugin add` |
| Codex native installation | Not run | Global plugin configuration was not changed; a filtered list returned no installed or available matching plugin and does not establish discovery |
| Claude native validation/runtime | Not run | Claude Code is not installed in this environment |
| Gemini, Cursor, Copilot runtime | Not run | Integration instructions were checked against official documentation, not executed in those clients |
| Model behavior/effectiveness | Not measured | No before/after model evaluation or hallucination-reduction claim |
| Hosted GitHub Actions | Not verified in this record | The workflow is included and can run on GitHub; inspect the repository's Actions page for actual hosted results |
| Optional vendor skill validator | Unavailable | The local helper requires PyYAML; the dependency was absent and could not be retrieved in this environment |

The project provides its own bounded structural validation. That check is not
complete vendor schema validation and cannot replace a native-client test.

## Reproduce the local checks

```bash
python3 manage.py check
python3 -m unittest discover -s tests -v
python3 manage.py build
```

Extract the source ZIP into a fresh directory and run the same checks there.
The artifacts themselves remain source releases with the native-client and
behavioral limitations listed above. Do not treat a configured CI target as a
passing hosted run.
