# Contributing

Issues and pull requests are welcome.

## Scope

Epic Management is a cross-host skill for turning functional and technical specifications into one complete EPIC document and a traceable GitHub backlog. Contributions should preserve that purpose.

Contributions that fit the project include:

- Workflow improvements that prevent specification loss or ambiguous issue scope.
- Better validation of EPIC structure, routing, and publication preconditions.
- Compatibility fixes for Codex or Claude Code.
- Clearer instructions, examples, templates, and error messages.
- Bug fixes that make preparation, publication, or resumption safer and more idempotent.

Contributions that probably do not fit include:

- Story implementation or project-specific business logic.
- Generic issue triage or backlog prioritization unrelated to EPIC creation.
- Host-specific behavior that breaks the other supported host.
- Additional published files that duplicate the specification already held by the EPIC concept.
- Publication shortcuts that bypass exact previews or explicit approval.

## Before opening a pull request

Open an issue before making anything beyond a typo or small clarification. Describe the problem, the expected behavior, and whether the change affects Codex, Claude Code, the EPIC document schema, GitHub publication, or more than one of those surfaces.

Keep the change focused. If a schema change requires corresponding template, validator, documentation, or compatibility updates, include them in the same pull request so the package never describes mutually incompatible contracts.

## Project invariants

Every change must preserve these invariants:

- One published EPIC has exactly one EPIC concept directory at `docs/epics/EPIC-NNN-name/`.
- The EPIC concept retains the complete functional and technical specification, and story concepts link those blocks instead of copying them.
- Every operational specification block reaches the EPIC issue, at least one story issue, or both.
- GitHub issue bodies include the complete applicable text rather than only identifiers, summaries, or links.
- No published artifact or issue depends on a file under `tmp/` or another ignored directory.
- Preparation and refinement keep the working EPIC directory under `tmp/` without creating issues or writing anything inside `docs/epics/`.
- Publication alone may create issues, move the approved directory into `docs/epics/`, and update the bundle index; resumption may only continue an already-started approved publication.
- Every story issue is a direct native sub-issue of its EPIC issue, and native priority matches the ordered `stories` list. A Markdown task list, link, label, milestone, or dependency edge is not equivalent parentage.
- Parent/sub-issue relationships express EPIC decomposition; `blocked by` and `blocking` express only explicit execution dependencies. A story already parented elsewhere is a conflict and requires a separate approved reparenting preview.
- The bundle stays conformant with OKF v0.2: every concept carries parseable frontmatter with a non-empty `type`, and the reserved filenames `index.md` and `log.md` keep their defined structure and are never concepts.
- This workflow never creates or updates `log.md`: git is its history, and every commit that publishes, closes, deprecates, or migrates an EPIC names that EPIC in its subject line. A repository may maintain an OKF log independently.
- Provenance and trust are recorded from real evidence: `sources` names actual material, `generated` names the acting agent and clock, and a `human:<id>` verifier is added only at a real approval checkpoint.
- OKF `status` records the document lifecycle and `epic_status` records the execution lifecycle; the two are never collapsed.
- Every published index entry links its EPIC concept directory, and per-EPIC issue links, dates, story links, and closure evidence live in the concept rather than the index.
- Future work without a published concept or issue remains outside the EPIC index.
- Completed EPIC concepts include evidence-backed `## Final verification`, `## Findings`, and `## Exit state` sections.
- Published concepts are never labelled as drafts, and `status: draft` marks working concepts under `tmp/` only.
- Migration converts a legacy layout losslessly, updates in-repository references to moved paths, and never touches GitHub.
- Remote mutations require an exact preview and explicit user approval.
- Partial publication can resume without duplicating issues, branches, or pull requests.
- Codex and Claude Code remain supported through their native invocation syntax.

## Writing and formatting

Write skill instructions, documentation, examples, placeholders, and user-facing validation messages in English.

Keep each Markdown paragraph and list item on one logical source line. Every Markdown file must pass both Prettier and markdownlint.

Run:

```sh
npx prettier --check "**/*.md"
npx markdownlint-cli2 "**/*.md"
```

If formatting is required, run Prettier with `--write`, review the resulting diff, and rerun both checks.

## Testing changes

Run the structural skill validator supplied by your Codex installation against the skill directory. Also compile and exercise both bundled validators:

```sh
python3 -m py_compile scripts/okf.py scripts/validate_epic.py scripts/validate_okf_bundle.py
python3 -m unittest discover -s tests
python3 scripts/validate_epic.py path/to/EPIC-NNN-name
python3 scripts/validate_okf_bundle.py path/to/docs/epics
```

Use a complete bundle fixture with an EPIC that covers both `context` and `operational` blocks, `DOCUMENT`, `EPIC`, and story destinations, in both the working and published stages. Add focused invalid fixtures when changing a validation rule and confirm that each one fails for the intended reason.

Exercise the frontmatter parser with and without PyYAML installed, since the validators must agree in both environments.

For invocation changes, verify at minimum:

- `$epic-management help` in Codex.
- `/epic-management help` in Claude Code.
- A bare invocation in each host shows help without reading the repository or changing state.
- Missing and unknown operations fail closed without mutations.

Do not test publication against live GitHub resources unless the test scope, exact writes, and cleanup plan were explicitly approved.

For changes to the native relationship protocol, verify the current `gh issue create`, `gh issue edit`, and `gh issue view` capabilities plus the official REST Sub-issues contract. When an approved live fixture is available, read the parent and child directions back and test idempotent resume after a partial attachment; otherwise keep the verification read-only.

## Changelog

Update [CHANGELOG.md](CHANGELOG.md) for every user-visible change. Record ongoing work under `Unreleased`, and keep entries grouped and ordered according to the rules documented there.

## Cutting a release

A released changelog heading and its reference definition are two parts of the same link, backed by a signed, annotated Git tag named `vX.Y.Z`.

1. Move the contents of `Unreleased` into a new `## [X.Y.Z] - YYYY-MM-DD` section and leave a fresh, empty `Unreleased` section above it.
2. Change the former `Unreleased` reference to `[X.Y.Z]`, pointing it at `compare/vW.V.U...vX.Y.Z`, and add a new `Unreleased` reference pointing at `compare/vX.Y.Z...HEAD`. The oldest release points directly to `releases/tag/vX.Y.Z`.
3. Run the complete validation suite and commit the release on the default branch.
4. Create the release point with `git tag -s vX.Y.Z -m "Release X.Y.Z"`. Never move or replace a published release tag.
5. Publish the branch and its signed tag together with `git push origin main --follow-tags`, then verify that the changelog links resolve.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers this project.
