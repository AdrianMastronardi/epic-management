# Epic Management

A cross-host skill for turning functional and technical specifications into complete product EPICs with native GitHub sub-issues and an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) knowledge bundle, without losing source information.

Epic Management works with Codex and Claude Code. It prepares and refines one self-contained EPIC concept directory under `tmp/`, then publication projects the relevant portions into executable issues, moves the approved directory into the `docs/epics/` bundle, and updates the bundle index.

## Why it exists

A common EPIC workflow starts with a detailed temporary specification, produces a shorter EPIC plan, and later creates GitHub issues from that plan. Information removed during the first transformation can no longer reach the repository or the issues, leaving implementation dependent on unstated context or an ignored temporary file.

Epic Management prevents that loss by transforming the complete specification into the EPIC concept itself. Stable specification blocks make every routing decision explicit and verifiable, and OKF frontmatter records where the knowledge came from, who generated it, and who verified it.

## Core guarantees

- After publication, exactly one EPIC concept contains the complete functional and technical specification.
- Every specification block is classified as `context` or `operational`.
- Every operational block maps to the EPIC issue, at least one story issue, or both.
- Every generated issue body includes the complete applicable text, not only a summary, identifier, or link.
- No issue or published artifact depends on `tmp/` or another ignored directory.
- A new EPIC does not enter version control during `prepare` or `refine`; both operations keep it under `tmp/` and do not create issues.
- Only approved publication creates GitHub issues, moves the EPIC into `docs/epics/`, and updates the bundle index.
- Publication requires an exact preview and explicit approval, and partial runs resume without duplication.
- Every story issue is a direct native GitHub sub-issue of the EPIC; Markdown task lists and dependency edges never stand in for parentage.
- Native child order follows the ordered `stories` list, while `blocked by` and `blocking` record only explicit execution dependencies.
- Provenance and trust are recorded, never invented: `sources` names the material, `generated` names the agent that wrote it, and `verified` gains a `human:<id>` entry only at a real approval checkpoint.
- Published concepts are never labelled as drafts; `status: draft` marks working concepts under `tmp/` and nothing else.
- The skill manages the backlog but never implements its stories.

## Operations

| Operation             | Required input                                                              | Result                                                                                                              |
| --------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `help`                | None                                                                        | Show usage, operations, and examples without reading or writing anything.                                           |
| `prepare`             | Source specification path                                                   | Create or complete the working EPIC directory under `tmp/`, validate coverage, and stop without publication writes. |
| `refine`              | EPIC directory path; source path when it cannot be established from context | Refine the working EPIC under `tmp/`, validate coverage, and stop without publication writes.                       |
| `publish`             | Approved EPIC directory path                                                | Preview and approve exact writes, create or reuse issues, move the EPIC into the bundle, and update the index.      |
| `prepare-and-publish` | Source specification path                                                   | Prepare the EPIC, require approval at the coverage and write checkpoint, and then publish it.                       |
| `resume`              | EPIC number or directory path                                               | Discover partial local and remote state, reuse existing resources, and continue without duplicates after approval.  |
| `migrate`             | Optional repository or bundle path                                          | Convert a legacy flat EPIC layout into the OKF bundle after an exact-write preview, without touching GitHub.        |
| `inspect`             | Optional workflow or artifact path                                          | Analyze an EPIC workflow and bundle conformance without changing local or remote state.                             |

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
$epic-management publish tmp/EPIC-020-durable-memory
$epic-management resume EPIC-020
```

Claude Code uses a slash command:

```text
/epic-management help
/epic-management prepare tmp/functional-technical-spec.md
/epic-management publish tmp/EPIC-020-durable-memory
/epic-management resume EPIC-020
```

A bare invocation shows help and performs no repository reads, GitHub access, or mutations.

## Workflow

1. Write the complete functional and technical specification in a temporary source file.
2. Run `prepare` to transform that source into one complete working EPIC directory under `tmp/`.
3. Review the coverage checkpoint, including every source section, block classification, issue destination, exclusion, open decision, and the identity that will be recorded as verifier.
4. Approve the checkpoint only when the EPIC preserves the complete source and the proposed issue routing is correct.
5. Run `publish`, or continue `prepare-and-publish`, to preview the exact issues, native parent/sub-issue actions, dependency edges, and repository writes.
6. Approve the writes, then let the skill create or reuse GitHub resources, attach every story as a direct sub-issue, move the directory into `docs/epics/`, update the bundle index, and open the documentation pull request.
7. After a human merges the pull request, run `resume` to verify the merge and complete safe post-merge cleanup.

The skill reads and obeys repository-specific guidance for language, labels, GitHub transport, protected branches, commits, checks, and pull-request lifecycle.

## Bundle model

The published bundle root is `docs/epics/`. One EPIC is one concept directory; one story is one concept inside it.

```text
docs/epics/
├── index.md                                   # bundle listing, declares okf_version
├── backlog.md                                 # optional, type EPIC Backlog
└── EPIC-020-durable-memory/
    ├── index.md                               # listing of this EPIC's concepts
    ├── epic.md                                # type EPIC
    └── STORY-020-001-persist-memory-index.md  # type Story
```

[references/okf-bundle.md](references/okf-bundle.md) is the authoritative format contract: frontmatter families, the actor convention, the trust events this workflow records, link and source policy, the restricted YAML style, index structure, and the legacy migration map.

Each coherent source block receives a stable `SPEC-NNN-SSS` identifier and one row in the distribution table inside `epic.md`. `context` blocks may remain only in the EPIC concept. `operational` blocks must reach the EPIC issue, at least one story issue, or both. Story concepts declare their exact `applicable_blocks` and link those blocks rather than copying them; the validator checks that declaration against the distribution table, and publication resolves each link into complete text when generating issue bodies.

Issue links, dates, story links, notes, and closure evidence live in the EPIC concept's frontmatter and body. The bundle index stays a lightweight listing grouped by `epic_status`, which is what makes it a conformant OKF index rather than a second record of the same facts.

The GitHub issue hierarchy is deliberately shallow:

```text
EPIC-NNN issue
├── STORY-NNN-001 issue  (native sub-issue)
├── STORY-NNN-002 issue  (native sub-issue)
└── STORY-NNN-003 issue  (native sub-issue)
```

Each story remains an independent issue, but the EPIC owns it through GitHub's native parent/sub-issue relation. That relation drives GitHub's progress summary and project hierarchy. It is distinct from a Markdown checkbox and from a dependency: parentage means “part of this EPIC,” while `blocked by` means “cannot proceed until this issue changes.” The skill reads both directions back, reconciles native priority with `epic.md`, and refuses to move a story from another parent without a separate explicit approval. See [references/github-sub-issues.md](references/github-sub-issues.md) for the CLI, REST fallback, conflict, ordering, and recovery protocol.

GitHub remains authoritative for live progress, parentage, and blocking state; the bundle preserves the durable definition, navigation, and historical traceability.

This workflow creates and updates no `log.md`. OKF makes it optional and recommends shipping a bundle as a git repository because git already supplies history, attribution, and diffs, so the repository's history is the bundle's history. Every commit that publishes, closes, deprecates, or migrates an EPIC names its identifier in the subject line. The trade-off is that this history does not travel if the bundle is exported as a tarball; a repository that needs portable history may maintain a `log.md` independently, which the validator checks when it finds one.

Unpublished future work stays outside the index. Repositories that use a Markdown backlog can create `docs/epics/backlog.md` from [assets/backlog-concept-template.md](assets/backlog-concept-template.md); repositories using GitHub Projects keep that system authoritative instead.

## Migrating an existing repository

Repositories created before this format keep `docs/epic-index.md` and flat `docs/epics/EPIC-NNN-name.md` documents. Run `migrate` to convert them: each document becomes a concept directory, each story section becomes a story concept, the old index collapses into `docs/epics/index.md` with its per-EPIC metadata moved into frontmatter, and the completion paragraphs move into the EPIC concept body.

Migration previews every write, never touches GitHub, updates in-repository references to moved paths, and refuses to fabricate provenance for documents that never recorded a source.

## Validation

Validate one EPIC concept directory, working or published:

```sh
python3 scripts/validate_epic.py path/to/EPIC-NNN-name
```

Validate the whole bundle against OKF v0.2:

```sh
python3 scripts/validate_okf_bundle.py docs/epics
```

The EPIC validator checks frontmatter families, the actor convention, lifecycle values, numbering, routing consistency, story paths and resource agreement, applicable specification links, required sections, unresolved placeholders, forbidden temporary references, and draft labelling. The bundle validator checks OKF conformance and reports the tolerances OKF grants consumers, such as broken cross-links, as warnings; `--strict` turns them into failures. Neither proves semantic completeness, which still requires a section-by-section comparison with the source specification.

Both validators use PyYAML when it is importable and fall back to a strict parser for the documented frontmatter subset otherwise, so they run without third-party dependencies.

All project Markdown must pass:

```sh
npx prettier --check "**/*.md"
npx markdownlint-cli2 "**/*.md"
```

Run the deterministic validator tests:

```sh
python3 -m unittest discover -s tests
```

## Files

```text
epic-management/
├── agents/
│   └── openai.yaml  # Codex discovery metadata
├── assets/
│   ├── backlog-concept-template.md  # optional EPIC Backlog concept
│   ├── bundle-index-template.md  # bundle root index
│   ├── epic-concept-template.md  # canonical EPIC concept
│   ├── epic-index-template.md  # per-EPIC directory index
│   └── story-concept-template.md  # canonical Story concept
├── references/
│   ├── github-publication.md  # approval-gated publication protocol
│   ├── github-sub-issues.md  # native parent/sub-issue protocol
│   └── okf-bundle.md  # OKF format contract for EPIC artifacts
├── scripts/
│   ├── okf.py  # shared OKF frontmatter parsing and checks
│   ├── validate_epic.py  # EPIC concept directory validator
│   └── validate_okf_bundle.py  # OKF bundle conformance validator
├── tests/
│   └── test_validators.py  # deterministic validator regression tests
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
