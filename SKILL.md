---
name: epic-management
description: Create, refine, validate, publish, migrate, inspect, or resume product EPICs as Open Knowledge Format bundles with traceable GitHub stories. Use when a user invokes epic-management; wants to turn a functional and technical specification into an EPIC; wants to create, publish, migrate, inspect, or resume an EPIC and its story issues; or needs to repair an EPIC workflow. Preparation stays under tmp/ and only approved publication may create GitHub issues or write the docs/epics bundle. Preserve all source information, route every operational specification block to the EPIC or stories, and never implement story code.
---

# Epic Management

Turn a functional and technical specification into one complete EPIC concept and a traceable set of executable issues. Preserve knowledge in an Open Knowledge Format bundle under `docs/epics/`; treat GitHub bodies as operational projections of that bundle.

## Invocation contract

Use the native explicit-invocation syntax of the active host:

- Codex CLI or IDE: `$epic-management [operation] [input]`
- Claude Code: `/epic-management [operation] [input]`

Accept these operations:

| Operation             | Required input                                                              | Result                                                                                                                                                          |
| --------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `help`                | None                                                                        | Show usage, operations, and examples. Make no reads or writes.                                                                                                  |
| `prepare`             | Source specification path                                                   | Create or complete one working EPIC concept directory under `tmp/`, validate coverage, present the checkpoint, and leave GitHub and the bundle unchanged.       |
| `refine`              | EPIC directory path; source path when it cannot be established from context | Refine the working EPIC directory under `tmp/`, validate coverage, present the checkpoint, and leave GitHub and the bundle unchanged.                           |
| `publish`             | Approved EPIC directory path                                                | Validate the working EPIC, preview and approve exact writes, create or reuse GitHub issues, move the directory into `docs/epics/`, and update the bundle index. |
| `prepare-and-publish` | Source specification path                                                   | Run `prepare` under `tmp/`, require approval at each checkpoint, and only then cross the publication boundary.                                                  |
| `resume`              | EPIC number or directory path                                               | Discover an already-started publication, reuse existing resources, preview missing writes, require approval, and continue without duplicates.                   |
| `migrate`             | Optional repository or bundle path                                          | Convert a legacy flat EPIC layout into the OKF bundle after an exact-write preview. Never touch GitHub.                                                         |
| `inspect`             | Optional workflow or artifact path                                          | Analyze the EPIC workflow and bundle conformance without changing local or remote state.                                                                        |

Apply these dispatch rules before reading the repository or taking any other action:

1. Normalize the actionable input from the current user request. In Codex, use the text after the `$epic-management` mention. In Claude Code, use the text after `/epic-management`; Claude Code may expose non-empty text as a final `ARGUMENTS: <value>` record, in which case use only `<value>` as the invocation input. For implicit invocation, use the natural-language request.
2. If the normalized input is empty, or its operation is `help`, `-h`, or `--help`, respond in English with both host syntaxes, the operation table, and at least one `prepare` and one `publish` example. Do not inspect the repository, access GitHub, or modify anything.
3. If the first token is a known operation, obey it. An explicit operation overrides mode inference from repository state.
4. If an explicit operation lacks required input, show that operation's syntax in the active host and request only the missing value. Do not start another operation.
5. If the first token looks like an operation but is unknown, identify it as unknown and show help. Do not guess or mutate state.
6. If the prompt is a natural-language task without an explicit operation, infer the operation from the request and observable state using the mode rules below.
7. Treat text after the operation as either its direct input or additional natural-language constraints. Accept absolute and repository-relative paths.

Codex examples:

```text
$epic-management prepare tmp/functional-technical-spec.md
$epic-management publish tmp/EPIC-020-durable-memory
$epic-management prepare-and-publish tmp/functional-technical-spec.md
$epic-management refine tmp/EPIC-020-durable-memory tmp/functional-technical-spec.md
$epic-management resume EPIC-020
$epic-management migrate docs/epics
$epic-management inspect .claude/commands/create-epic.md
```

Claude Code examples:

```text
/epic-management prepare tmp/functional-technical-spec.md
/epic-management publish tmp/EPIC-020-durable-memory
/epic-management prepare-and-publish tmp/functional-technical-spec.md
/epic-management refine tmp/EPIC-020-durable-memory tmp/functional-technical-spec.md
/epic-management resume EPIC-020
/epic-management migrate docs/epics
/epic-management inspect .claude/commands/create-epic.md
```

## Resolve bundled resources

Resolve the skill root before reading a bundled file or running a bundled script. Never assume that the current working directory is the skill root.

- In Claude Code, `${CLAUDE_SKILL_DIR}` resolves to the directory containing this `SKILL.md`.
- In Codex, derive the root from the path of the loaded `SKILL.md` shown in the skill catalog.
- Resolve every relative resource link below against that root, following the installation symlink when present.

## Artifact model

Read [references/okf-bundle.md](references/okf-bundle.md) before creating, editing, validating, or migrating any EPIC artifact. It is the authoritative format contract; this file states only the workflow that writes into it.

One EPIC is one OKF concept directory. Preparation builds it under `tmp/` and publication moves it into the bundle:

```text
tmp/EPIC-NNN-name/                     docs/epics/
├── index.md                           ├── index.md
├── epic.md                            ├── backlog.md
└── STORY-NNN-001-slug.md              └── EPIC-NNN-name/
                                           ├── index.md
                                           ├── epic.md
                                           └── STORY-NNN-001-slug.md
```

`epic.md` is a `type: EPIC` concept holding the complete specification. Each story is a `type: Story` concept declaring its `applicable_blocks` and linking the blocks in `epic.md`; story concepts never copy the specification into the bundle a second time. GitHub issue bodies still carry the complete applicable text, because an issue cannot follow a bundle link.

## Non-negotiable contract

- During `prepare` and `refine`, create or edit exactly one working EPIC directory at `tmp/EPIC-NNN-name/` containing `epic.md`, one concept per story, and `index.md`. Do not create, copy, stage, or modify anything inside `docs/epics/` or any GitHub issue.
- Cross the repository publication boundary only in `publish`, after explicit approval of both coverage and exact writes: create or reuse the GitHub issues, move the approved directory from `tmp/` to `docs/epics/EPIC-NNN-name/`, and update `docs/epics/index.md`. `resume` may finish this sequence only when an approved publication already started.
- After publication, keep exactly one EPIC directory for an EPIC at `docs/epics/EPIC-NNN-name/`; the working copy must no longer remain under `tmp/`.
- Do not create or update `docs/epics/log.md`. The repository's git history is the bundle's history for this workflow, so name the EPIC identifier in the subject of every commit that publishes, closes, deprecates, or migrates an EPIC, and keep one such event per commit.
- Keep `docs/epics/index.md` limited to published EPICs. Keep future work without a published concept or issue in the repository's backlog authority, such as GitHub Projects or `docs/epics/backlog.md`, never mixed into the index.
- Consume the temporary source specification into the EPIC concept and record it in `sources`. Do not archive the source as a second document under `docs/`.
- Preserve all source information. Never replace the specification with a summary and then discard the source.
- Classify each coherent specification block as `context` or `operational`.
- Route every `operational` block to the EPIC issue, at least one story issue, or both. Copy its substantive text into every mapped issue; a link or identifier alone is insufficient.
- Allow `context` blocks to remain only in the EPIC concept, but classify that choice explicitly.
- Keep issue state in GitHub and full context in the bundle. Story concepts record the durable definition of the work and never mirror progress, assignee, or blocking state. When implementation scope changes later, update the issue; when design or rationale changes, amend the concept too.
- Write real frontmatter. Take timestamps from the clock, derive actors from the active host and the repository git identity, and never invent a model name, a human identifier, or a verification event.
- Add a `human:<id>` entry to `verified` only when the user has actually approved that content at a checkpoint.
- Use OKF `status` for the document lifecycle and `epic_status` for the execution lifecycle, and never collapse them. A published concept is `status: stable`; only `tmp/` carries `status: draft`.
- Never label an EPIC or story a draft in prose, titles, or issue bodies. The `status: draft` frontmatter value is the OKF lifecycle marker for a working concept and is not a label.
- Never leave an issue dependent on a path under `tmp/` or another ignored directory.
- Format every Markdown file created or edited by the workflow with the repository's Prettier configuration and require both Prettier and markdownlint checks to pass before declaring it complete. This includes every concept, index, and temporary issue-body file.
- Read and obey repository guidance before choosing labels, branches, commit messages, API commands, required checks, or documentation locations.
- Never create or mutate remote issues, branches, or pull requests before an exact user checkpoint.
- Leave pull requests open for human review unless the user explicitly authorizes a merge.
- Do not implement any story while managing the EPIC.

## Infer the mode for natural-language requests

When no explicit operation was supplied, choose one mode from observable state:

1. **Prepare** — a source specification exists, but no complete working `tmp/EPIC-NNN-*/` directory exists.
2. **Refine** — a working EPIC directory exists under `tmp/` but has not passed coverage review.
3. **Publish** — the working EPIC under `tmp/` is approved and validated, and no publication artifact exists yet.
4. **Resume** — an approved publication started and some issues, the published directory, branch, or PR already exist. Reuse deterministic titles and identifiers; never duplicate them.
5. **Migrate** — the repository keeps EPICs in the legacy flat layout, such as `docs/epic-index.md` or `docs/epics/EPIC-NNN-name.md` files without frontmatter, and the user asks to adopt OKF or to publish into a bundle that does not exist yet.
6. **Inspect** — the user asks to diagnose or improve an EPIC workflow. Analyze only unless changes are explicitly requested.

If the EPIC number, name, source file, or repository is genuinely ambiguous, ask before writing. Do not infer a consequential identity.

## 1. Load the repository contract and source

Read the applicable repository guidance files, the EPIC bundle, architecture documentation implicated by the source, and any existing EPIC command. Treat repository documentation as validation context, not as permission to add scope.

Detect the layout before writing anything. When `docs/epics/index.md` declares `okf_version`, the bundle exists. When only `docs/epic-index.md` or frontmatter-less `docs/epics/*.md` files exist, the repository is on the legacy layout and needs `migrate` before or during publication.

Read the declared source specification completely. If several files jointly define the specification, require the user to choose whether they form one EPIC; once chosen, consolidate all of them into the single EPIC concept.

Record the source paths only in the working notes. Published concepts and generated issues must reference `docs/epics/EPIC-NNN-name/`, never the temporary inputs or the working path.

## 2. Build the EPIC concept directory

Start from [assets/epic-concept-template.md](assets/epic-concept-template.md), [assets/story-concept-template.md](assets/story-concept-template.md), and [assets/epic-index-template.md](assets/epic-index-template.md). Write the result to `tmp/EPIC-NNN-name/`; when refining, edit that working directory in place. Never write inside `docs/epics/` during this phase. Transform the source itself into the EPIC instead of writing a separate summary:

1. Preserve its problem statement, functional behavior, technical design, constraints, edge cases, alternatives, decisions, open questions, evidence, and examples.
2. Reorganize only when that improves execution clarity and does not erase distinctions.
3. Divide the specification into coherent blocks headed `### SPEC-NNN-001`, `### SPEC-NNN-002`, and so on inside `epic.md`.
4. Mark each block in the distribution table as `context` or `operational`.
5. Map every operational block to `EPIC`, one or more `STORY-NNN-SSS` destinations, or both.
6. Give every story concept an `applicable_blocks` list containing exactly the blocks mapped to it, and an `## Applicable specification` section linking those blocks in `epic.md`.
7. Put executable work in story descriptions, tasks, acceptance criteria, and quality checks. Keep cross-cutting decisions and invariants at EPIC level as well when every story must respect them.
8. Keep postponed work visible as an explicit open question, exclusion, or future dependency; never omit it because it does not fit the current stories.
9. Record the specification in `sources`, using a followable resource for durable material and a scope descriptor for a temporary file the workflow will retire. Attribute individual claims with footnotes keyed to `sources[].id`.
10. Set `generated` from the active host, model, and current clock on every concept you write or meaningfully change. Leave `verified`, `resource`, and the published `status` for later phases.

Use stable IDs for traceability, not as substitutes for prose. A story concept may reference a block by ID and link, but generated GitHub bodies must include the full applicable text.

## 3. Prove coverage and checkpoint

Run the bundled validator with actual resolved paths; never pass an angle-bracket placeholder literally:

- In Claude Code: `python3 "${CLAUDE_SKILL_DIR}/scripts/validate_epic.py" <epic-directory>`
- In Codex: `python3 <resolved-skill-root>/scripts/validate_epic.py <epic-directory>`

Replace `<epic-directory>` and, in Codex, `<resolved-skill-root>` before execution.

The validator proves structure, frontmatter, and routing consistency; it cannot prove semantic completeness. Perform a section-by-section comparison against the source and present a checkpoint containing:

- every source section and its destination block;
- every block's `context` or `operational` classification;
- every GitHub destination for operational blocks;
- all exclusions, open decisions, and deferred work;
- any wording that was merged, split, or materially rewritten;
- the proposed EPIC and story titles with labels;
- the `sources` entries and the human identifier that will be recorded as the verifier;
- existing remote resources that will be reused.

Require explicit approval. Do not retire the source specification or make external writes before approval.

On approval, append `verified: { by: human:<id>, at: <now> }` to `epic.md` and to every story concept the user approved, using the real clock and the confirmed identifier. Coverage approval makes the working EPIC eligible for publication; it does not publish it. For standalone `prepare` or `refine`, stop with the directory under `tmp/` and leave the source at its existing path. Do not create issues, move the directory, update the bundle index, or retire the source. `prepare-and-publish` may continue only by entering the publication flow below.

## 4. Publish idempotently

Read [references/github-publication.md](references/github-publication.md) completely before any GitHub or git mutation. Follow the repository's transport and lifecycle rules when they are stricter.

Enter this phase only for `publish`, for the publication half of `prepare-and-publish`, or to `resume` an approved publication that already crossed the boundary. For a new publication, require the approved input to be the working directory under `tmp/`. Never pre-stage anything inside `docs/epics/` during preparation.

Generate issue bodies from the approved concepts:

- Include global operational blocks mapped to `EPIC` in the EPIC body.
- Include every block mapped to a story under that story's applicable specification, resolving the link into the complete block text.
- Preserve requirements, invariants, limits, failure behavior, and exclusions; do not compress away qualifiers.
- Add the published concept link and issue relationships using the repository's required syntax.
- Use native GitHub parent/sub-issue and dependency relationships when the repository and transport support them; keep GitHub authoritative for live progress and blocking state.
- Rebuild previews after issue numbers become known.

Use deterministic titles for idempotence. Detect existing EPIC, story, branch, and PR resources before creating anything. On partial failure, resume from remote state and verify bodies before patching.

After exact-write approval, create or reuse the GitHub issues and move the approved directory to `docs/epics/EPIC-NNN-name/`. Then set `status: stable` on every concept, write each issue URL into the EPIC's `resource`, each `stories[].resource`, and each story concept's `resource`, and update the bundle. When `docs/epics/index.md` does not exist, create it from [assets/bundle-index-template.md](assets/bundle-index-template.md), adapt its language to the repository, and resolve or remove every placeholder. Add the EPIC to the index group matching its `epic_status`, newest first. Preserve an existing index's language and ordering. Never add future work without a published concept or issue to the index. If an existing index embeds future backlog, include a lossless move to the repository's backlog authority in the exact-write preview before removing it from the index. If the repository keeps a Markdown backlog and none exists, create `docs/epics/backlog.md` from [assets/backlog-concept-template.md](assets/backlog-concept-template.md) only when source backlog content exists; never invent deferred scope. Then run the required documentation and repository gates, commit, push, and open the PR. Retire the temporary source only after confirming that the published concept contains all of it and the user can recover the approved result; report what was removed and how it is recoverable. Do not claim the stories are implementable from a clean clone until the documentation PR is merged into their base branch.

Validate the bundle before committing:

```sh
python3 <resolved-skill-root>/scripts/validate_okf_bundle.py docs/epics
```

Every published EPIC appears in `docs/epics/index.md` as a linked entry under its status group. Issue links, dates, story links, notes, and closure evidence live in the EPIC concept, not in the index. Use the repository's controlled status vocabulary for `epic_status`; when none exists, use only `Active`, `Blocked`, `Completed`, or `Cancelled`. While the EPIC remains active, omit the completion-only `## Final verification`, `## Findings`, and `## Exit state` sections.

## 5. Resume and close

In resume mode:

1. Establish the authoritative EPIC directory and current remote identifiers.
2. Compare deterministic titles and bodies before deciding what is missing.
3. Reuse existing issues and PRs; patch only stale projections.
4. Refuse ambiguous states such as two EPIC directories for the same number.
5. Repeat validation and the exact-write checkpoint for any new remote mutation.

After the user confirms the documentation PR was merged, verify the merge, complete the repository's post-merge issue checklist, remove merged branches, and synchronize the base branch. Disclose missing checks or reviews instead of reconstructing evidence retroactively.

Do not treat the documentation PR merge as completion of the EPIC itself. When remote evidence shows that every story and EPIC acceptance criterion is complete, preview the exact concept, index, and issue updates and require approval. Then set `epic_status: Completed` and `completed_on`, move the index entry to the completed group, append a `verified` entry for the closing review, and add these evidence-backed sections to `epic.md`:

- `## Final verification` — summarize final acceptance evidence, required checks, and relevant test or review results.
- `## Findings` — record material discoveries, deviations, corrections, and follow-up work; write `None` when there were no findings.
- `## Exit state` — state what now exists, the boundaries that remain, and deferred or future scope without implying it was delivered.

Keep each completion section to at most three concise paragraphs or bullet points. Link full evidence in the GitHub issues or pull requests rather than duplicating an unbounded closure report.

Set `status: deprecated` only when the EPIC is superseded or withdrawn, and record the superseding concept in the same change. A completed EPIC stays `status: stable`.

## 6. Migrate a legacy layout

Enter this mode only for `migrate`, or when publication finds a legacy layout and the user approves converting it first. Migration never creates, mutates, or closes a GitHub issue.

1. Inventory the legacy artifacts: `docs/epic-index.md`, every `docs/epics/EPIC-NNN-name.md`, `docs/epic-backlog.md`, and every in-repository reference to those paths.
2. Map each artifact to its OKF destination using the migration table in [references/okf-bundle.md](references/okf-bundle.md).
3. Build the exact-write preview: every file created, moved, or deleted; every story section that becomes a concept; every index sentence and its destination; every reference that must be updated.
4. Require explicit approval. State plainly that every sentence of the legacy index lands in a named destination, and name anything you cannot place instead of dropping it.
5. Apply the writes with git moves where possible so history survives, set `generated` on every concept you author, and carry forward existing issue URLs into `resource` and `stories[].resource`.
6. Run both validators over every migrated EPIC and over the bundle, then run the repository's documentation gates, commit with a subject that names the migration, push, and open the PR.

Do not fabricate provenance during migration. When a legacy document records no source, write a `sources` entry whose `resource` is a scope descriptor naming the legacy document and its history, and do not add a `verified` entry for a review that never happened.

## Completion conditions

Finish `prepare` or `refine` only when:

- exactly one complete working EPIC directory exists under `tmp/` and the source remains recoverable at its existing path;
- `validate_epic.py` passes and the section-by-section coverage review completed, and the checkpoint identifies the working EPIC as unpublished;
- no GitHub issue was created or mutated and nothing under `docs/epics/` was changed.

Finish `publish` or publication `resume` only when:

- exactly one EPIC directory contains the complete source specification and execution plan;
- that directory is at `docs/epics/EPIC-NNN-name/`, its entry in `docs/epics/index.md` is current, and no working copy remains under `tmp/`;
- `validate_epic.py` passes for the published directory and `validate_okf_bundle.py` passes for `docs/epics`;
- every specification block appears once in the distribution table;
- every operational block reaches at least one GitHub issue;
- story mappings and `applicable_blocks` agree exactly;
- every published concept carries `status: stable`, a `resource` issue URL, and a human `verified` entry;
- no issue or published file depends on `tmp/`;
- all requested issues exist once with correct relationships and labels;
- the documentation PR is open and verified, or post-merge cleanup is complete when the user confirmed a merge;
- validation results and any remaining uncertainty are reported.

When a `resume` operation closes the EPIC itself, additionally require `epic_status: Completed`, `completed_on`, the index entry moved to the completed group, and `## Final verification`, `## Findings`, and `## Exit state` with no unresolved placeholders.

Finish `migrate` only when both validators pass, every legacy artifact reached a named destination, every in-repository reference to a moved path is updated, and no GitHub resource was touched.

Finish `help` or `inspect` without local or remote mutations.

## Resources

- [assets/backlog-concept-template.md](assets/backlog-concept-template.md) — copy only when the repository uses a Markdown backlog and source backlog content exists.
- [assets/bundle-index-template.md](assets/bundle-index-template.md) — copy and adapt only when publication or migration must create a missing bundle index.
- [assets/epic-concept-template.md](assets/epic-concept-template.md) — copy and fill when preparing the EPIC concept.
- [assets/epic-index-template.md](assets/epic-index-template.md) — copy and fill for each EPIC directory's index.
- [assets/story-concept-template.md](assets/story-concept-template.md) — copy and fill for each story concept.
- [references/okf-bundle.md](references/okf-bundle.md) — read before creating, editing, validating, or migrating any EPIC artifact.
- [references/github-publication.md](references/github-publication.md) — read before GitHub or git mutations.
- [scripts/validate_epic.py](scripts/validate_epic.py) — validate one EPIC concept directory, working or published.
- [scripts/validate_okf_bundle.py](scripts/validate_okf_bundle.py) — validate the whole bundle against OKF v0.2.
