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
- Additional versioned specification files that duplicate the EPIC document.
- Publication shortcuts that bypass exact previews or explicit approval.

## Before opening a pull request

Open an issue before making anything beyond a typo or small clarification. Describe the problem, the expected behavior, and whether the change affects Codex, Claude Code, the EPIC document schema, GitHub publication, or more than one of those surfaces.

Keep the change focused. If a schema change requires corresponding template, validator, documentation, or compatibility updates, include them in the same pull request so the package never describes mutually incompatible contracts.

## Project invariants

Every change must preserve these invariants:

- One published EPIC has exactly one versioned EPIC document.
- The EPIC document retains the complete functional and technical specification.
- Every operational specification block reaches the EPIC issue, at least one story issue, or both.
- GitHub issue bodies include the complete applicable text rather than only identifiers, summaries, or links.
- No published artifact or issue depends on a file under `tmp/` or another ignored directory.
- Preparation and refinement keep the working EPIC under `tmp/` without creating issues or modifying `docs/epics/` or `docs/epic-index.md`.
- Publication alone may create issues, move the approved EPIC to `docs/epics/`, and update `docs/epic-index.md`; resumption may only continue an already-started approved publication.
- Every published index entry links its versioned EPIC document and names and directly links every story issue in a dedicated `Stories` list.
- Future work without a published document or issue remains outside the EPIC index.
- Completed index entries include evidence-backed `Final verification`, `Findings`, and `Exit state` paragraphs.
- Versioned EPIC artifacts are never labelled as drafts.
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

Run the structural skill validator supplied by your Codex installation against the skill directory. Also compile and exercise the bundled EPIC validator:

```sh
python3 -m py_compile scripts/validate_epic.py
python3 scripts/validate_epic.py path/to/EPIC-NNN-name.md
```

Use a complete EPIC fixture that covers both `context` and `operational` blocks, `DOCUMENT`, `EPIC`, and story destinations. Add focused invalid fixtures when changing a validation rule and confirm that each one fails for the intended reason.

For invocation changes, verify at minimum:

- `$epic-management help` in Codex.
- `/epic-management help` in Claude Code.
- A bare invocation in each host shows help without reading the repository or changing state.
- Missing and unknown operations fail closed without mutations.

Do not test publication against live GitHub resources unless the test scope, exact writes, and cleanup plan were explicitly approved.

## Changelog

Update [CHANGELOG.md](CHANGELOG.md) for every user-visible change. Add the new version at the top and keep entries grouped and ordered according to the rules documented there.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers this project.
