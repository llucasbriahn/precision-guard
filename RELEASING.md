# Releasing

The source repository is [llucasbriahn/precision-guard](https://github.com/llucasbriahn/precision-guard).
Hosting source does not imply an official marketplace listing or a tagged release.
The local build creates artifacts; publishing them is a separate action.

## Prepare a release

1. Review the policy changes and compatibility claims. Record actual evaluation
   evidence or explicitly state that behavior has not been evaluated.
2. Update the version in all three `plugins/precision-guard/**/plugin.json`
   manifests, using `major.minor.patch`. Keep the license `GPL-3.0-only`.
   If project notices change, synchronize the plugin directory's `LICENSE` and
   `NOTICE` with the root copies so marketplace installs carry the same terms.
3. Update `CHANGELOG.md` and `VERIFICATION.md` with observed results. Do not mark
   hosted CI or a native client as passing until it actually ran successfully.
4. Run the following commands from the repository root:

```bash
python3 manage.py check
python3 -m unittest discover -s tests -v
python3 manage.py build
```

5. Inspect the archive member lists and extract each archive into a fresh
   temporary directory. Run the source archive's checks and installer tests.
   For Claude Code, run `claude plugin validate` on the extracted plugin folder
   and load it with `--plugin-dir`. For Codex, test a local marketplace and confirm
   the skill is discoverable. Record the exact client versions and outcome.
6. Run representative cases from `EVALUATION.md` in each client for which you
   intend to claim runtime support. Do not advertise untested clients as tested.

## Build outputs

```text
dist/
  precision-guard-0.1.0-source.zip
  precision-guard-0.1.0-plugin.zip
  SHA256SUMS
```

Versioned filenames follow the portable manifest's version. The source ZIP includes
the local marketplace and complete project. The plugin ZIP includes the native
plugin source, README, license, and notice. Rebuilding the same content overwrites
these versioned outputs with the same bytes. Use `--output /path/to/artifacts` to
choose a different output directory.

To check downloaded archives in a POSIX shell, run `sha256sum -c SHA256SUMS` from
their directory. A checksum does not authenticate the publisher; distribute it
through a channel your users trust.

## Publish the repository and release

Create the repository under your own account and push the reviewed source using
your normal Git workflow. Keep hidden directories such as `.agents`,
`.claude-plugin`, and `.github`; they are part of the package. Do not commit `dist`
or private backup files.

The included CI runs on pushes, pull requests, and manual dispatch. It has
read-only repository permissions, pins external actions to commit IDs, runs the
test matrix, and produces downloadable build artifacts after tests pass. It
does not create tags, publish releases, install plugins globally, or access model
credentials. Review action updates through normal dependency maintenance.

After reviewing CI and client test results, create a `vX.Y.Z` Git tag and a release
for that exact source revision. Attach both ZIPs and `SHA256SUMS`, and describe the
changes, verification, and known limitations. Review those files before publishing.

Once a public repository URL exists, users can register its marketplace through
their client's documented Git repository installation flow. Replace example paths
in public installation announcements with the actual repository URL. Do not invent
a repository URL or claim an official marketplace listing before it exists.

## License and source distribution

GPL version 3 only was selected for this project. Preserve `LICENSE`, `NOTICE`,
and applicable source notices in distributions. Publish the matching complete
source alongside releases; these releases already contain source text rather than
compiled proprietary components. Modified distributions must preserve applicable
notices and identify modifications as required by the license. Read the actual
[GPL text](LICENSE) for the terms; this guide is not a substitute for it.

The license text's FSF copyright refers to the license document. The project
notice identifies the project's license separately. If you add individual
copyright notices, use the actual rightsholders rather than template names.
