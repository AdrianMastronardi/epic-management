# Epic Management

A cross-host skill for turning functional and technical specifications into complete product EPICs and traceable GitHub stories without losing source information.

Epic Management works with Codex and Claude Code. It prepares and refines one self-contained EPIC under `tmp/`, then publication projects the relevant portions into executable issues, moves the approved EPIC to `docs/epics/`, and updates `docs/epic-index.md`.

## Why it exists

A common EPIC workflow starts with a detailed temporary specification, produces a shorter EPIC plan, and later creates GitHub issues from that plan. Information removed during the first transformation can no longer reach the repository or the issues, leaving implementation dependent on unstated context or an ignored temporary file.

Epic Management prevents that loss by transforming the complete specification into the EPIC document itself. Stable specification blocks make every routing decision explicit and verifiable.

## Core guarantees

- After publication, exactly one versioned EPIC document contains the complete functional and technical specification.
- Every specification block is classified as `context` or `operational`.
- Every operational block maps to the EPIC issue, at least one story issue, or both.
- Every generated issue body includes the complete applicable text, not only a summary, identifier, or link.
- No issue or versioned artifact depends on `tmp/` or another ignored directory.
- A new EPIC does not enter version control during `prepare` or `refine`; both operations keep it under `tmp/` and do not create issues.
- Only approved publication creates GitHub issues, moves the EPIC to `docs/epics/`, and updates `docs/epic-index.md`.
- Publication requires an exact preview and explicit approval, and partial runs resume without duplication.
- Versioned EPIC artifacts are never labelled as drafts.
- The skill manages the backlog but never implements its stories.

## Operations

| Operation             | Required input                                                             | Result                                                                                                             |
| --------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `help`                | None                                                                       | Show usage, operations, and examples without reading or writing anything.                                          |
| `prepare`             | Source specification path                                                  | Create or complete the working EPIC under `tmp/`, validate coverage, and stop without publication writes.          |
| `refine`              | EPIC document path; source path when it cannot be established from context | Refine the working EPIC under `tmp/`, validate coverage, and stop without publication writes.                      |
| `publish`             | Approved EPIC document path                                                | Preview and approve exact writes, create or reuse issues, move the EPIC to `docs/epics/`, and update the index.    |
| `prepare-and-publish` | Source specification path                                                  | Prepare the EPIC, require approval at the coverage and write checkpoint, and then publish it.                      |
| `resume`              | EPIC number or document path                                               | Discover partial local and remote state, reuse existing resources, and continue without duplicates after approval. |
| `inspect`             | Optional workflow or artifact path                                         | Analyze an EPIC workflow without changing local or remote state.                                                   |

## Installation

Keep one local checkout and symlink it into either or both host skill directories.

For Codex:

```sh
mkdir -p "$HOME/.agents/skills"
ln -s /absolute/path/to/epic-management "$HOME/.agents/skills/epic-management"
```

For Claude Code:

```sh
mkdir -p "$HOME/.claude/skills"
ln -s /absolute/path/to/epic-management "$HOME/.claude/skills/epic-management"
```

Replace `/absolute/path/to/epic-management` with the actual checkout path. If the destination already exists, inspect it before changing anything; do not overwrite it blindly.

## Usage

Codex uses a skill mention:

```text
$epic-management help
$epic-management prepare tmp/functional-technical-spec.md
$epic-management publish tmp/EPIC-020-durable-memory.md
$epic-management resume EPIC-020
```

Claude Code uses a slash command:

```text
/epic-management help
/epic-management prepare tmp/functional-technical-spec.md
/epic-management publish tmp/EPIC-020-durable-memory.md
/epic-management resume EPIC-020
```

A bare invocation shows help and performs no repository reads, GitHub access, or mutations.

## Workflow

1. Write the complete functional and technical specification in a temporary source file.
2. Run `prepare` to transform that source into one complete working EPIC under `tmp/`.
3. Review the coverage checkpoint, including every source section, block classification, issue destination, exclusion, and open decision.
4. Approve the checkpoint only when the EPIC preserves the complete source and the proposed issue routing is correct.
5. Run `publish`, or continue `prepare-and-publish`, to preview the exact issues and repository writes.
6. Approve the writes, then let the skill create or reuse GitHub resources, move the EPIC to `docs/epics/`, update `docs/epic-index.md`, and open the documentation pull request.
7. After a human merges the pull request, run `resume` to verify the merge and complete safe post-merge cleanup.

The skill reads and obeys repository-specific guidance for language, labels, GitHub transport, protected branches, commits, checks, and pull-request lifecycle.

## EPIC document model

The canonical template is [assets/epic-template.md](assets/epic-template.md). Each coherent source block receives a stable `SPEC-NNN-SSS` identifier and one row in the GitHub distribution table.

When publication must create a missing `docs/epic-index.md`, it starts from [assets/epic-index-template.md](assets/epic-index-template.md). Each heading links to its versioned EPIC document with a relative path. Existing indexes keep their repository-specific structure and ordering.

Every index entry names and directly links all GitHub story issues in a dedicated `Stories` list, reserves `Notes` for exceptional context, and uses a controlled lifecycle status. Completed EPICs additionally record concise `Final verification`, `Findings`, and `Exit state` summaries; these completion paragraphs remain absent while an EPIC is active.

When supported, the EPIC issue is the native parent of its story sub-issues and explicit blocking relationships use GitHub dependencies. GitHub remains authoritative for live progress and blocking state; the versioned index preserves navigation and historical traceability.

Unpublished future work stays outside the index. Repositories that use a Markdown backlog can create `docs/epic-backlog.md` from [assets/epic-backlog-template.md](assets/epic-backlog-template.md); repositories using GitHub Projects keep that system authoritative instead.

`context` blocks may remain only in the EPIC document. `operational` blocks must reach the EPIC issue, at least one story issue, or both. Story sections declare their exact `Applicable blocks`, and the validator checks that declaration against the distribution table.

Stable identifiers provide traceability, but GitHub issue bodies still receive the complete applicable specification text.

## Validation

Validate a completed EPIC document with:

```sh
python3 scripts/validate_epic.py path/to/EPIC-NNN-name.md
```

The validator checks structure, numbering, routing consistency, required story sections, unresolved placeholders, forbidden temporary references, and draft labelling. Semantic completeness still requires a section-by-section comparison with the source specification.

All project Markdown must pass:

```sh
npx prettier --check "**/*.md"
npx markdownlint-cli2 "**/*.md"
```

## Files

```text
epic-management/
├── agents/
│   └── openai.yaml  # Codex discovery metadata
├── assets/
│   ├── epic-backlog-template.md  # optional unpublished EPIC backlog template
│   ├── epic-index-template.md  # published EPIC index template
│   └── epic-template.md  # canonical EPIC document template
├── references/
│   └── github-publication.md  # approval-gated publication protocol
├── scripts/
│   └── validate_epic.py  # deterministic EPIC structural validator
├── CHANGELOG.md  # version history
├── CONTRIBUTING.md  # contribution guidelines
├── LICENSE  # MIT License
├── README.md  # project overview and usage
└── SKILL.md  # agent-facing workflow and contract
```

## License and contributions

Licensed under the [MIT License](LICENSE).

Issues and pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before making anything beyond a typo or small clarification.

See [CHANGELOG.md](CHANGELOG.md) for version history.
