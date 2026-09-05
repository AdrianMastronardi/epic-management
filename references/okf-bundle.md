# OKF bundle

Read this file before creating, editing, validating, or migrating any EPIC artifact. It defines how this skill maps EPIC management onto [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). `SKILL.md` states the workflow; this file states the format contract the workflow writes into.

## Bundle layout

The published bundle root is `docs/epics/`. One EPIC is one directory inside it, and one story is one concept inside that directory.

```text
docs/epics/                                  # bundle root
├── index.md                                 # reserved: bundle listing, declares okf_version
├── backlog.md                               # concept: type EPIC Backlog (optional)
├── references/                              # optional: external material mirrored as concepts
└── EPIC-020-durable-memory/                 # one directory per EPIC
    ├── index.md                             # reserved: listing of this EPIC's concepts
    ├── epic.md                              # concept: type EPIC
    ├── STORY-020-001-persist-memory-index.md  # concept: type Story
    └── STORY-020-002-expire-stale-entries.md
```

The working copy produced by `prepare` and `refine` is the same directory shape under `tmp/`, so publication is a move rather than a rewrite:

```text
tmp/EPIC-020-durable-memory/
├── index.md
├── epic.md
└── STORY-020-001-persist-memory-index.md
```

Name the EPIC directory `EPIC-NNN-<slug>` and each story concept `STORY-NNN-SSS-<slug>.md`, where `<slug>` is the lowercase kebab-case form of the title. Keeping the slug in the directory name preserves the previous `EPIC-NNN-name` convention and keeps `docs/epics/` readable without opening `index.md`.

## Reserved filenames

`index.md` and `log.md` are reserved at every level and are never concepts. They carry no `type` and, apart from `okf_version` in the bundle-root `index.md`, no frontmatter at all. This skill produces `index.md` files and no `log.md`; see [History](#history).

## Concept types

| `type`         | File                                 | Purpose                                                           |
| -------------- | ------------------------------------ | ----------------------------------------------------------------- |
| `EPIC`         | `EPIC-NNN-<slug>/epic.md`            | The complete functional and technical specification and its plan. |
| `Story`        | `EPIC-NNN-<slug>/STORY-NNN-SSS-*.md` | One executable unit of that EPIC.                                 |
| `EPIC Backlog` | `backlog.md`                         | Future EPICs without a published concept or GitHub issue.         |

The EPIC concept remains the single home of the specification text. Story concepts declare which blocks apply to them and link to those blocks; they never copy the specification into the bundle a second time. GitHub issue bodies still embed the complete applicable text, because an issue lives outside the bundle and cannot follow a bundle link.

## EPIC concept frontmatter

| Key            | Required          | Value                                                                                                             |
| -------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| `type`         | Always            | `EPIC`.                                                                                                           |
| `title`        | Always            | `EPIC-NNN — <name>`, quoted.                                                                                      |
| `description`  | Always            | One sentence naming the outcome.                                                                                  |
| `resource`     | After publication | The canonical GitHub EPIC issue URL. Omit while the EPIC is still under `tmp/`.                                   |
| `tags`         | Recommended       | Flow list of short lowercase strings.                                                                             |
| `status`       | Always            | OKF document lifecycle: `draft` under `tmp/`, `stable` once published, `deprecated` once superseded.              |
| `generated`    | Always            | `{ by: <actor>, at: <ISO 8601 UTC> }` for the last meaningful content change.                                     |
| `verified`     | After approval    | List of `{ by: <actor>, at: <ISO 8601 UTC> }`. The coverage checkpoint adds the human entry.                      |
| `stale_after`  | Optional          | Absolute `YYYY-MM-DD` after which the EPIC's context must be re-checked. Remove when it does not apply.           |
| `sources`      | Always            | The materials the EPIC was built from. See [Sources](#sources).                                                   |
| `epic_number`  | Always            | The three-digit number, quoted so the leading zero survives.                                                      |
| `epic_status`  | Always            | Execution lifecycle: `Active`, `Blocked`, `Completed`, or `Cancelled`, or the repository's controlled vocabulary. |
| `started_on`   | Always            | `YYYY-MM-DD`.                                                                                                     |
| `completed_on` | On completion     | `YYYY-MM-DD`. Omit it or leave it empty while the EPIC is not complete.                                           |
| `stories`      | Always            | Ordered list of `{ id, title, concept, resource }`. See [Stories](#stories).                                      |

`status` and `epic_status` are different axes and must not be collapsed. `status` describes the document: whether this knowledge is reviewed and current. `epic_status` describes the work: whether the EPIC is being executed. A completed EPIC keeps `status: stable` and moves to `epic_status: Completed`; only a superseded or withdrawn EPIC becomes `status: deprecated`.

## Story concept frontmatter

| Key                 | Required          | Value                                                                       |
| ------------------- | ----------------- | --------------------------------------------------------------------------- |
| `type`              | Always            | `Story`.                                                                    |
| `title`             | Always            | `STORY-NNN-SSS — <name>`, quoted.                                           |
| `description`       | Always            | One sentence naming the executable outcome.                                 |
| `resource`          | After publication | The canonical GitHub story issue URL. Omit while the story is under `tmp/`. |
| `tags`              | Recommended       | Flow list of short lowercase strings.                                       |
| `status`            | Always            | Same lifecycle values and transitions as the EPIC concept.                  |
| `generated`         | Always            | `{ by: <actor>, at: <ISO 8601 UTC> }`.                                      |
| `verified`          | After approval    | List of `{ by: <actor>, at: <ISO 8601 UTC> }`.                              |
| `epic`              | Always            | `EPIC-NNN`.                                                                 |
| `epic_concept`      | Always            | Relative path to the EPIC concept, normally `./epic.md`.                    |
| `components`        | Always            | Flow list of the components the story touches.                              |
| `applicable_blocks` | Always            | Flow list of the `SPEC-NNN-SSS` identifiers routed to this story.           |

Story concepts never record progress, assignee, or blocking state. GitHub remains authoritative for live execution state; the concept records the durable definition of the work.

## Stories

Each `stories` entry binds a story identifier to its concept file and its issue:

```yaml
stories:
  - id: STORY-020-001
    title: Persist the memory index
    concept: ./STORY-020-001-persist-the-memory-index.md
    resource: https://github.com/acme/memory/issues/124
```

`concept` must be a relative path that resolves to an existing story file directly inside the EPIC directory. `resource` is added only when the issue exists and must equal the story concept's own `resource`. Story identifiers are consecutive from `001`, unique, and belong to the EPIC named by `epic_number`.

The `stories` list, the EPIC directory's `index.md`, the story files on disk, and the destinations in the EPIC's distribution table describe the same set. Every story's `epic_concept` resolves to the sibling `epic.md`, and its `## Applicable specification` links exactly the blocks in `applicable_blocks`. The validator rejects any disagreement between these projections.

## Sources

`sources` is how this skill keeps its central promise — no information is lost — inside OKF's provenance family:

```yaml
sources:
  - id: durable-memory-spec
    resource: Functional and technical specification supplied for EPIC-020 on 2026-08-18
    title: Durable memory functional and technical specification
    author: human:adrian
    last_modified: 2026-08-18
```

Use a followable `resource` — an absolute URL, or a bundle-relative path into `references/` — whenever the material is durable. When the source was a temporary file that the workflow consumes and retires, OKF permits a scope descriptor instead of a path; name the specification, its EPIC, and its date so the origin stays auditable without archiving a duplicate specification under `docs/`.

Never mirror the consumed specification into the bundle as a second document. The `references/` convention is for genuinely external material the EPIC quotes but does not absorb, such as an RFC, a vendor document, or a design record that keeps living outside this repository.

Attribute individual claims with markdown footnotes whose label is a `sources[].id`:

```markdown
Entries expire after 30 days of inactivity.[^durable-memory-spec]

[^durable-memory-spec]: Durable memory functional and technical specification
```

Every footnote label used in a body must exist in that concept's `sources`.

## Actor convention

Identity fields (`generated.by`, `verified[].by`, `sources[].author`) use one convention:

- `<producer>/<version>` for an agent, using the real host and model, for example `claude-code/opus-5` or `codex/gpt-5`.
- `human:<id>` for a person, for example `human:adrian`.
- `process:<id>` for an automated process, for example `process:ci-nightly`.

Derive the human identifier from the repository's git identity, normally the local part of `git config user.email`, and confirm it at the checkpoint. Never invent an identifier, a model name, or a version.

## Timestamps

`generated.at` and `verified[].at` are ISO 8601 UTC datetimes and must be real. Read the clock instead of estimating:

```sh
date -u +%Y-%m-%dT%H:%M:%SZ
```

`generated.at` changes only when the content changes meaningfully. `verified[].at` records when a human or process confirmed the content and is never back-dated or copied from `generated.at`.

## Trust events in this workflow

| Workflow moment                            | Frontmatter effect                                                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `prepare` or `refine` writes the concept   | Set or update `generated: { by: <agent actor>, at: <now> }`.                                           |
| The user approves the coverage checkpoint  | Append `verified: { by: human:<id>, at: <now> }` to every affected concept.                            |
| Publication moves the EPIC into the bundle | Set `status: stable` and add `resource` to the EPIC and story concepts.                                |
| Closure records the outcome                | Set `epic_status: Completed` and `completed_on`, and append a `verified` entry for the closing review. |

A concept that no human has approved carries no `human:` verifier, which is exactly OKF's unverified or machine-confirmed tier. Do not add one to make a document look reviewed.

## YAML style

Write frontmatter in the restricted style below so the bundled validators parse it without third-party dependencies, and so agent edits produce small diffs:

- One key per line, two-space indentation, no tabs.
- Flow mappings for `generated` and each `verified` entry: `{ by: ..., at: ... }`.
- Flow sequences for `tags`, `components`, and `applicable_blocks`: `[a, b, c]`.
- Block sequences for `sources` and `stories`, one key per line inside each entry.
- Quote any value containing `:`, `#`, `{`, `[`, or a leading zero that must survive, such as `epic_number: "020"`.
- Plain unquoted dates and datetimes, and no inline comments.

The validators prefer PyYAML when it is importable and fall back to a strict parser for this subset otherwise.

## Links

Use relative markdown links between concepts, such as `./epic.md`, `../index.md`, or `./STORY-020-001-persist-memory-index.md`. OKF permits both bundle-relative and relative links and recommends the bundle-relative form; this skill chooses relative links because the bundle lives inside a GitHub repository where a leading `/` resolves against the repository root and breaks in the web renderer for every human reader.

Link a specification block from a story with the block's anchor in the EPIC concept, for example `[SPEC-020-001](./epic.md#spec-020-001-cache-eviction)`. Broken links are tolerated by OKF consumers and may represent knowledge not written yet, but the validators still report unresolved bundle-internal links so nothing rots silently.

## Index files

Every directory in the bundle carries an `index.md` for progressive disclosure. The bundle root declares the format version, which is the only frontmatter any index file may have:

```markdown
---
okf_version: "0.2"
---

# EPIC index

## Active

- [EPIC-020 — Durable memory](EPIC-020-durable-memory/index.md) - Durable cross-session memory for the agent runtime.
```

OKF §8 illustrates sections as level-one headings. This skill uses one level-one title followed by level-two sections so the files pass a default markdownlint configuration in the host repository; the structure a consumer parses — sections of linked, described entries — is unchanged.

Group the bundle-root index by `epic_status`, newest first inside each group, and take each entry's description from the linked concept's `description`. Add a final section linking `backlog.md` when the repository keeps a Markdown backlog. The index lists published EPICs only; future work without a published concept or issue belongs in the backlog authority.

An EPIC directory's `index.md` lists that EPIC's concepts:

```markdown
# EPIC-020 — Durable memory

- [EPIC document](epic.md) - Durable cross-session memory for the agent runtime.

## Stories

- [STORY-020-001 — Persist the memory index](STORY-020-001-persist-the-memory-index.md) - Write the index to durable storage on every commit.
```

## History

OKF makes `log.md` optional and recommends distributing a bundle as a git repository precisely because git already supplies history, attribution, and diffs. This skill takes that option: it never creates or updates `docs/epics/log.md`, and the repository's git history is the bundle's history. A hand-maintained log next to a git history is a second record of the same events that can drift from the first.

That decision places one requirement on commits. The commit that publishes, closes, deprecates, or migrates an EPIC is its history entry, so name the EPIC identifier in the subject line and keep one such event per commit. `git log --follow docs/epics/EPIC-NNN-name/` must be able to answer what a log entry would have answered.

`log.md` stays a reserved filename at every level and must never be used for a concept. A repository may maintain an explicit log independently, and the bundle validator checks its structure when it finds one, but nothing in this workflow writes it.

State the trade-off rather than hiding it: history held in git does not travel when a bundle is exported as a tarball or copied into another repository. A repository that expects that kind of export should maintain a `log.md` outside this workflow.

## Conformance

A bundle conforms to OKF v0.2 when every non-reserved `.md` file has parseable YAML frontmatter with a non-empty `type`, and every reserved file follows the structures above. Consumers must tolerate unknown types, unknown keys, missing optional fields, broken links, and missing index files, so the validators separate hard errors from warnings.

Validate one EPIC directory, working or published:

```sh
python3 scripts/validate_epic.py path/to/EPIC-NNN-name
```

Validate the whole bundle:

```sh
python3 scripts/validate_okf_bundle.py docs/epics
```

Neither validator proves semantic completeness. The section-by-section comparison against the source specification is still required at the coverage checkpoint.

## Legacy layout migration

Repositories created before this format keep a flat layout. The `migrate` operation maps it as follows, without touching GitHub:

| Legacy artifact                    | OKF artifact                                                                                       |
| ---------------------------------- | -------------------------------------------------------------------------------------------------- |
| `docs/epics/EPIC-NNN-name.md`      | `docs/epics/EPIC-NNN-name/epic.md` with frontmatter added.                                         |
| `### STORY-NNN-SSS` sections       | One `STORY-NNN-SSS-<slug>.md` concept each, with `applicable_blocks` taken from the block mapping. |
| `**Applicable blocks**:` lines     | The story concept's `applicable_blocks` frontmatter.                                               |
| `docs/epic-index.md`               | `docs/epics/index.md`, reduced to linked entries grouped by status.                                |
| Index `Issue`, `Status`, and dates | The EPIC concept's `resource`, `epic_status`, `started_on`, `completed_on`.                        |
| Index `Stories` links              | The EPIC concept's `stories[].resource`.                                                           |
| Index `Notes`                      | A `## Notes` section in the EPIC concept.                                                          |
| Index completion paragraphs        | `## Final verification`, `## Findings`, and `## Exit state` in the EPIC concept.                   |
| `docs/epic-backlog.md`             | `docs/epics/backlog.md` with `type: EPIC Backlog` frontmatter.                                     |

Migration is lossless: every sentence in a legacy index entry must land in a named destination above, and any in-repository reference to a moved path must be updated in the same change.
