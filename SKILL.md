---
name: epic-management
description: Create, refine, validate, publish, or resume product EPICs from functional and technical specifications without losing source information. Use when the user invokes epic-management or wants to turn a specification into an EPIC, split an EPIC into GitHub stories, create or resume EPIC and story issues, archive an EPIC in a repository, or repair an EPIC-creation workflow. Support the explicit operations help, prepare, refine, publish, prepare-and-publish, resume, and inspect; when invoked without an operation, show usage and take no action. Produce one self-contained versioned EPIC document, map every operational specification block to the EPIC issue, one or more story issues, or both, and prevent implementation dependencies from remaining under tmp/. Do not use for implementing story code, routine issue triage, prioritizing an unrelated backlog, or creating a standalone issue.
---

# Epic Management

Turn a functional and technical specification into one complete EPIC document and a traceable set of executable issues. Preserve knowledge in the EPIC; treat GitHub bodies as operational projections of that document.

## Invocation contract

Use the native explicit-invocation syntax of the active host:

- Codex CLI or IDE: `$epic-management [operation] [input]`
- Claude Code: `/epic-management [operation] [input]`

Accept these operations:

| Operation             | Required input                                                             | Result                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `help`                | None                                                                       | Show usage, operations, and examples. Make no reads or writes.                                                                                |
| `prepare`             | Source specification path                                                  | Create or complete the single EPIC document, validate coverage, present the checkpoint, and stop before publication.                          |
| `refine`              | EPIC document path; source path when it cannot be established from context | Compare the EPIC with its source, restore missing information, validate coverage, and stop before publication.                                |
| `publish`             | Approved EPIC document path                                                | Validate, preview the exact GitHub and repository writes, require approval, and then publish idempotently.                                    |
| `prepare-and-publish` | Source specification path                                                  | Run `prepare`, require approval at the coverage and write checkpoint, and only then continue with `publish`.                                  |
| `resume`              | EPIC number or document path                                               | Discover partial local and remote state, reuse existing resources, preview missing writes, require approval, and continue without duplicates. |
| `inspect`             | Optional workflow or artifact path                                         | Analyze the EPIC workflow without changing local or remote state.                                                                             |

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

- Keep exactly one versioned document for an EPIC: `docs/epics/EPIC-NNN-name.md` or the repository's equivalent.
- Consume the temporary source specification into that document. Do not archive a second source file elsewhere in `docs/`.
- Preserve all source information. Never replace the specification with a summary and then discard the source.
- Classify each coherent specification block as `context` or `operational`.
- Route every `operational` block to the EPIC issue, at least one story issue, or both. Copy its substantive text into every mapped issue; a link or identifier alone is insufficient.
- Allow `context` blocks to remain only in the EPIC document, but classify that choice explicitly.
- Keep issue state in GitHub and full context in the EPIC document. When implementation scope changes later, update the issue; when design or rationale changes, amend the EPIC document too.
- Never leave an issue dependent on a path under `tmp/` or another ignored directory.
- Call the versioned artifact an EPIC document, plan, or snapshot. Do not label it a draft.
- Format every Markdown file created or edited by the workflow with the repository's Prettier configuration and require both Prettier and markdownlint checks to pass before declaring it complete. This includes the EPIC document and temporary issue-body files.
- Read and obey repository guidance before choosing labels, branches, commit messages, API commands, required checks, or documentation locations.
- Never create or mutate remote issues, branches, or pull requests before an exact user checkpoint.
- Leave pull requests open for human review unless the user explicitly authorizes a merge.
- Do not implement any story while managing the EPIC.

## Infer the mode for natural-language requests

When no explicit operation was supplied, choose one mode from observable state:

1. **Prepare** — a source specification exists, but no complete `EPIC-NNN-*.md` exists.
2. **Refine** — an EPIC document exists locally but has not passed coverage review.
3. **Publish** — the EPIC is approved and validated; GitHub issues or the repository PR are absent.
4. **Resume** — some issues, the archived document, branch, or PR already exist. Reuse deterministic titles and identifiers; never duplicate them.
5. **Inspect** — the user asks to diagnose or improve an EPIC workflow. Analyze only unless changes are explicitly requested.

If the EPIC number, name, source file, or repository is genuinely ambiguous, ask before writing. Do not infer a consequential identity.

## 1. Load the repository contract and source

Read the applicable repository guidance files, EPIC index, architecture documentation implicated by the source, and any existing EPIC command. Treat repository documentation as validation context, not as permission to add scope.

Read the declared source specification completely. If several files jointly define the specification, require the user to choose whether they form one EPIC; once chosen, consolidate all of them into the single EPIC document.

Record the source paths only in the working notes. The final EPIC and its issues must reference the versioned EPIC path, never the temporary inputs.

## 2. Build the single EPIC document

Start from [assets/epic-template.md](assets/epic-template.md). Transform the source itself into the EPIC instead of writing a separate summary:

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

After approval, retire the temporary source only after confirming that the EPIC contains all of it and the user can recover the approved result. Report what was removed and how it is recoverable.

## 4. Publish idempotently

Read [references/github-publication.md](references/github-publication.md) completely before any GitHub or git mutation. Follow the repository's transport and lifecycle rules when they are stricter.

Generate issue bodies from the approved EPIC:

- Include global operational blocks mapped to `EPIC` in the EPIC body.
- Include every block mapped to a story under that story's applicable specification.
- Preserve requirements, invariants, limits, failure behavior, and exclusions; do not compress away qualifiers.
- Add the versioned EPIC link and issue relationships using the repository's required syntax.
- Rebuild previews after issue numbers become known.

Use deterministic titles for idempotence. Detect existing EPIC, story, branch, and PR resources before creating anything. On partial failure, resume from remote state and verify bodies before patching.

Archive only the approved EPIC document in the repository, update its issue link and the EPIC index, run the required documentation and repository gates, then commit, push, and open the PR. Do not claim the stories are implementable from a clean clone until the documentation PR is merged into their base branch.

## 5. Resume and close

In resume mode:

1. Establish the authoritative EPIC document and current remote identifiers.
2. Compare deterministic titles and bodies before deciding what is missing.
3. Reuse existing issues and PRs; patch only stale projections.
4. Refuse ambiguous states such as two local EPIC documents for the same number.
5. Repeat validation and the exact-write checkpoint for any new remote mutation.

After the user confirms the documentation PR was merged, verify the merge, complete the repository's post-merge issue checklist, remove merged branches, and synchronize the base branch. Disclose missing checks or reviews instead of reconstructing evidence retroactively.

## Completion conditions

Finish only when:

- exactly one versioned EPIC document contains the complete source specification and execution plan;
- every specification block appears once in the distribution table;
- every operational block reaches at least one GitHub issue;
- story mappings and `Applicable blocks` agree exactly;
- no issue or versioned file depends on `tmp/`;
- all requested issues exist once with correct relationships and labels;
- the documentation PR is open and verified, or post-merge cleanup is complete when the user confirmed a merge;
- validation results and any remaining uncertainty are reported.

## Resources

- [assets/epic-template.md](assets/epic-template.md) — copy and fill when preparing the single EPIC document.
- [scripts/validate_epic.py](scripts/validate_epic.py) — validate structure, numbering, routing, and forbidden temporary references.
- [references/github-publication.md](references/github-publication.md) — read before GitHub or git mutations.
