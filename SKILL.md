---
name: epic-management
description: Create, refine, validate, publish, or resume product EPICs from functional and technical specifications without losing source information. Use when the user invokes epic-management or wants to turn a specification into an EPIC, split an EPIC into GitHub stories, create or resume EPIC and story issues, archive an EPIC in a repository, or repair an EPIC-creation workflow. Support the explicit operations help, prepare, refine, publish, prepare-and-publish, resume, and inspect; when invoked without an operation, show usage and take no action. Keep prepared and refined EPIC documents under tmp/; only publication may create GitHub issues, move the approved EPIC to docs/epics/, and update docs/epic-index.md. Map every operational specification block to the EPIC issue, one or more story issues, or both, and prevent implementation dependencies from remaining under tmp/. Do not use for implementing story code, routine issue triage, prioritizing an unrelated backlog, or creating a standalone issue.
---

# Epic Management

Turn a functional and technical specification into one complete EPIC document and a traceable set of executable issues. Preserve knowledge in the EPIC; treat GitHub bodies as operational projections of that document.

## Invocation contract

Use the native explicit-invocation syntax of the active host:

- Codex CLI or IDE: `$epic-management [operation] [input]`
- Claude Code: `/epic-management [operation] [input]`

Accept these operations:

| Operation             | Required input                                                             | Result                                                                                                                                            |
| --------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `help`                | None                                                                       | Show usage, operations, and examples. Make no reads or writes.                                                                                    |
| `prepare`             | Source specification path                                                  | Create or complete one working EPIC under `tmp/`, validate coverage, present the checkpoint, and leave GitHub and versioned EPIC files unchanged. |
| `refine`              | EPIC document path; source path when it cannot be established from context | Refine the working EPIC under `tmp/`, validate coverage, present the checkpoint, and leave GitHub and versioned EPIC files unchanged.             |
| `publish`             | Approved EPIC document path                                                | Validate the working EPIC, preview and approve exact writes, create or reuse GitHub issues, move the EPIC to `docs/epics/`, and update the index. |
| `prepare-and-publish` | Source specification path                                                  | Run `prepare` under `tmp/`, require approval at each checkpoint, and only then cross the publication boundary.                                    |
| `resume`              | EPIC number or document path                                               | Discover an already-started publication, reuse existing resources, preview missing writes, require approval, and continue without duplicates.     |
| `inspect`             | Optional workflow or artifact path                                         | Analyze the EPIC workflow without changing local or remote state.                                                                                 |

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
$epic-management publish tmp/EPIC-020-durable-memory.md
$epic-management prepare-and-publish tmp/functional-technical-spec.md
$epic-management refine tmp/EPIC-020-durable-memory.md tmp/functional-technical-spec.md
$epic-management resume EPIC-020
$epic-management inspect .claude/commands/create-epic.md
```

Claude Code examples:

```text
/epic-management prepare tmp/functional-technical-spec.md
/epic-management publish tmp/EPIC-020-durable-memory.md
/epic-management prepare-and-publish tmp/functional-technical-spec.md
/epic-management refine tmp/EPIC-020-durable-memory.md tmp/functional-technical-spec.md
/epic-management resume EPIC-020
/epic-management inspect .claude/commands/create-epic.md
```

## Resolve bundled resources

Resolve the skill root before reading a bundled file or running a bundled script. Never assume that the current working directory is the skill root.

- In Claude Code, `${CLAUDE_SKILL_DIR}` resolves to the directory containing this `SKILL.md`.
- In Codex, derive the root from the path of the loaded `SKILL.md` shown in the skill catalog.
- Resolve every relative resource link below against that root, following the installation symlink when present.

## Non-negotiable contract

- During `prepare` and `refine`, create or edit exactly one working EPIC at `tmp/EPIC-NNN-name.md`. Do not create, copy, stage, or modify its final `docs/epics/` document, its `docs/epic-index.md` entry, or any GitHub issue.
- Cross the repository publication boundary only in `publish`, after explicit approval of both coverage and exact writes: create or reuse the GitHub issues, move the approved working EPIC from `tmp/` to `docs/epics/EPIC-NNN-name.md`, and update `docs/epic-index.md`. `resume` may finish this sequence only when an approved publication already started.
- After publication, keep exactly one versioned document for an EPIC at `docs/epics/EPIC-NNN-name.md`; the working copy must no longer remain under `tmp/`.
- Keep `docs/epic-index.md` limited to published EPICs. Keep future work without a published document or issue in the repository's backlog authority, such as GitHub Projects or `docs/epic-backlog.md`, never mixed into the index.
- Consume the temporary source specification into the working EPIC, then publish that document. Do not archive the source as a second file under `docs/`.
- Preserve all source information. Never replace the specification with a summary and then discard the source.
- Classify each coherent specification block as `context` or `operational`.
- Route every `operational` block to the EPIC issue, at least one story issue, or both. Copy its substantive text into every mapped issue; a link or identifier alone is insufficient.
- Allow `context` blocks to remain only in the EPIC document, but classify that choice explicitly.
- Keep issue state in GitHub and full context in the EPIC document. When implementation scope changes later, update the issue; when design or rationale changes, amend the EPIC document too.
- Never leave an issue dependent on a path under `tmp/` or another ignored directory.
- Call both the working and versioned artifacts an EPIC document, plan, or snapshot. Do not label either one a draft.
- Format every Markdown file created or edited by the workflow with the repository's Prettier configuration and require both Prettier and markdownlint checks to pass before declaring it complete. This includes the EPIC document and temporary issue-body files.
- Read and obey repository guidance before choosing labels, branches, commit messages, API commands, required checks, or documentation locations.
- Never create or mutate remote issues, branches, or pull requests before an exact user checkpoint.
- Leave pull requests open for human review unless the user explicitly authorizes a merge.
- Do not implement any story while managing the EPIC.

## Infer the mode for natural-language requests

When no explicit operation was supplied, choose one mode from observable state:

1. **Prepare** — a source specification exists, but no complete working `tmp/EPIC-NNN-*.md` exists.
2. **Refine** — a working EPIC exists under `tmp/` but has not passed coverage review.
3. **Publish** — the working EPIC under `tmp/` is approved and validated, and no publication artifact exists yet.
4. **Resume** — an approved publication started and some issues, the versioned document, branch, or PR already exist. Reuse deterministic titles and identifiers; never duplicate them.
5. **Inspect** — the user asks to diagnose or improve an EPIC workflow. Analyze only unless changes are explicitly requested.

If the EPIC number, name, source file, or repository is genuinely ambiguous, ask before writing. Do not infer a consequential identity.

## 1. Load the repository contract and source

Read the applicable repository guidance files, EPIC index, architecture documentation implicated by the source, and any existing EPIC command. Treat repository documentation as validation context, not as permission to add scope.

Read the declared source specification completely. If several files jointly define the specification, require the user to choose whether they form one EPIC; once chosen, consolidate all of them into the single EPIC document.

Record the source paths only in the working notes. Generated issues and the final EPIC must reference `docs/epics/EPIC-NNN-name.md`, never the temporary inputs or working EPIC path.

## 2. Build the single EPIC document

Start from [assets/epic-template.md](assets/epic-template.md). Write the result to `tmp/EPIC-NNN-name.md`; when refining, edit that working document in place. Never place it under `docs/epics/` during this phase. Transform the source itself into the EPIC instead of writing a separate summary:

1. Preserve its problem statement, functional behavior, technical design, constraints, edge cases, alternatives, decisions, open questions, evidence, and examples.
2. Reorganize only when that improves execution clarity and does not erase distinctions.
3. Divide the specification into coherent blocks headed `SPEC-NNN-001`, `SPEC-NNN-002`, and so on.
4. Mark each block in the distribution table as `context` or `operational`.
5. Map every operational block to `EPIC`, one or more `STORY-NNN-SSS` destinations, or both.
6. Give every story an `Applicable blocks` line containing exactly the blocks mapped to it.
7. Put executable work in story descriptions, tasks, acceptance criteria, and quality checks. Keep cross-cutting decisions and invariants at EPIC level as well when every story must respect them.
8. Keep postponed work visible as an explicit open question, exclusion, or future dependency; never omit it because it does not fit the current stories.

Use stable IDs for traceability, not as substitutes for prose. The repository document may reference a block by ID without repeating it inside each story section, but generated GitHub bodies must include the full applicable text.

## 3. Prove coverage and checkpoint

Run the bundled validator with actual resolved paths; never pass an angle-bracket placeholder literally:

- In Claude Code: `python3 "${CLAUDE_SKILL_DIR}/scripts/validate_epic.py" <epic-document>`
- In Codex: `python3 <resolved-skill-root>/scripts/validate_epic.py <epic-document>`

Replace `<epic-document>` and, in Codex, `<resolved-skill-root>` before execution.

The validator proves structure and routing consistency; it cannot prove semantic completeness. Perform a section-by-section comparison against the source and present a checkpoint containing:

- every source section and its destination block;
- every block's `context` or `operational` classification;
- every GitHub destination for operational blocks;
- all exclusions, open decisions, and deferred work;
- any wording that was merged, split, or materially rewritten;
- the proposed EPIC and story titles with labels;
- existing remote resources that will be reused.

Require explicit approval. Do not retire the source specification or make external writes before approval.

Coverage approval makes the working EPIC eligible for publication; it does not publish it. For standalone `prepare` or `refine`, stop with the EPIC under `tmp/` and leave the source at its existing path. Do not create issues, move the EPIC, update `docs/epic-index.md`, or retire the source. `prepare-and-publish` may continue only by entering the publication flow below.

## 4. Publish idempotently

Read [references/github-publication.md](references/github-publication.md) completely before any GitHub or git mutation. Follow the repository's transport and lifecycle rules when they are stricter.

Enter this phase only for `publish`, for the publication half of `prepare-and-publish`, or to `resume` an approved publication that already crossed the boundary. For a new publication, require the approved input to be the working EPIC under `tmp/`. Never pre-stage the final EPIC or index change during preparation.

Generate issue bodies from the approved EPIC:

- Include global operational blocks mapped to `EPIC` in the EPIC body.
- Include every block mapped to a story under that story's applicable specification.
- Preserve requirements, invariants, limits, failure behavior, and exclusions; do not compress away qualifiers.
- Add the versioned EPIC link and issue relationships using the repository's required syntax.
- Use native GitHub parent/sub-issue and dependency relationships when the repository and transport support them; keep GitHub authoritative for live progress and blocking state.
- Rebuild previews after issue numbers become known.

Use deterministic titles for idempotence. Detect existing EPIC, story, branch, and PR resources before creating anything. On partial failure, resume from remote state and verify bodies before patching.

After exact-write approval, create or reuse the GitHub issues and move only the approved EPIC document to `docs/epics/EPIC-NNN-name.md`. Update its issue link and `docs/epic-index.md`; when the index does not exist, create it from [assets/epic-index-template.md](assets/epic-index-template.md), adapt its language to the repository, link the heading to the versioned EPIC with a relative repository path, and resolve or remove every placeholder. Preserve an existing index's language and EPIC ordering; when creating a new one, list published EPICs newest first. Never add future work without a published document or issue to the index. If an existing index embeds future backlog, include a lossless move to the repository's backlog authority in the exact-write preview before removing it from the index. If the repository keeps a Markdown backlog and none exists, create `docs/epic-backlog.md` from [assets/epic-backlog-template.md](assets/epic-backlog-template.md) only when source backlog content exists; never invent deferred scope. Then run the required documentation and repository gates, commit, push, and open the PR. Retire the temporary source only after confirming that the final EPIC contains all of it and the user can recover the approved result; report what was removed and how it is recoverable. Do not claim the stories are implementable from a clean clone until the documentation PR is merged into their base branch.

In every published index entry, use a dedicated `Stories` list to name every story by its stable identifier and title and link its GitHub issue directly. A numeric issue range, EPIC checklist, or link to the EPIC issue does not replace the complete story list. Reserve `Notes` for exceptions or context that does not belong to structured fields. Use the repository's controlled status vocabulary; when none exists, use only `Active`, `Blocked`, `Completed`, or `Cancelled`. While the EPIC remains active, omit the completion-only `Final verification`, `Findings`, and `Exit state` paragraphs from the template.

## 5. Resume and close

In resume mode:

1. Establish the authoritative EPIC document and current remote identifiers.
2. Compare deterministic titles and bodies before deciding what is missing.
3. Reuse existing issues and PRs; patch only stale projections.
4. Refuse ambiguous states such as two local EPIC documents for the same number.
5. Repeat validation and the exact-write checkpoint for any new remote mutation.

After the user confirms the documentation PR was merged, verify the merge, complete the repository's post-merge issue checklist, remove merged branches, and synchronize the base branch. Disclose missing checks or reviews instead of reconstructing evidence retroactively.

Do not treat the documentation PR merge as completion of the EPIC itself. When remote evidence shows that every story and EPIC acceptance criterion is complete, preview the exact index and issue updates and require approval. Then set the index status and completion date, retain the complete linked `Stories` list, and add these evidence-backed paragraphs beneath `Notes`:

- `Final verification` — summarize final acceptance evidence, required checks, and relevant test or review results.
- `Findings` — record material discoveries, deviations, corrections, and follow-up work; write `None` when there were no findings.
- `Exit state` — state what now exists, the boundaries that remain, and deferred or future scope without implying it was delivered.

Keep each completion paragraph to at most three concise paragraphs or bullet points. Put full evidence in the versioned EPIC, GitHub issues, or pull requests and link it rather than duplicating an unbounded closure report in the index.

## Completion conditions

Finish `prepare` or `refine` only when:

- exactly one complete working EPIC exists under `tmp/` and the source remains recoverable at its existing path;
- validation and the section-by-section coverage review completed, and the checkpoint identifies the working EPIC as unpublished;
- no GitHub issue was created or mutated, no EPIC was placed under `docs/epics/`, and `docs/epic-index.md` was not changed.

Finish `publish` or publication `resume` only when:

- exactly one versioned EPIC document contains the complete source specification and execution plan;
- that document is at `docs/epics/EPIC-NNN-name.md`, its `docs/epic-index.md` entry is current, and no working EPIC copy remains under `tmp/`;
- every specification block appears once in the distribution table;
- every operational block reaches at least one GitHub issue;
- story mappings and `Applicable blocks` agree exactly;
- no issue or versioned file depends on `tmp/`;
- all requested issues exist once with correct relationships and labels;
- the documentation PR is open and verified, or post-merge cleanup is complete when the user confirmed a merge;
- validation results and any remaining uncertainty are reported.

When a `resume` operation closes the EPIC itself, additionally require the index entry's `Stories` list to name and link every story, record its completion status and date, and contain `Final verification`, `Findings`, and `Exit state` with no unresolved placeholders.

Finish `help` or `inspect` without local or remote mutations.

## Resources

- [assets/epic-backlog-template.md](assets/epic-backlog-template.md) — copy only when the repository uses a Markdown backlog and source backlog content exists.
- [assets/epic-index-template.md](assets/epic-index-template.md) — copy and adapt only when publication must create a missing EPIC index.
- [assets/epic-template.md](assets/epic-template.md) — copy and fill when preparing the single EPIC document.
- [scripts/validate_epic.py](scripts/validate_epic.py) — validate structure, numbering, routing, and forbidden temporary references.
- [references/github-publication.md](references/github-publication.md) — read before GitHub or git mutations.
