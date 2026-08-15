# GitHub publication

Read this file only when the user has approved the EPIC coverage checkpoint and asks to publish or resume publication.

## Publication boundary

For a new publication, the approved EPIC must still be a working document under `tmp/`. Neither `prepare` nor `refine` may create GitHub issues, place the EPIC under `docs/epics/`, or update `docs/epic-index.md`.

Cross that boundary only after the exact-write checkpoint is approved. `resume` may continue publication mutations only when evidence shows that an approved publication already started; otherwise return to the normal `publish` checkpoint.

## Preconditions

- Read the repository's agent guidance, contribution rules, label catalog, protected-branch policy, versioning rules, and required checks.
- Confirm that the EPIC document passes `scripts/validate_epic.py`.
- Confirm that a new publication starts from the single approved `tmp/EPIC-NNN-name.md` working document and that no final copy was pre-created.
- Confirm that the working tree is clean or that every existing change is understood and preserved.
- Confirm that the EPIC number and deterministic titles do not collide with unrelated resources.
- Confirm that no generated body refers to `tmp/`.

Repository rules override the examples below. Use REST, GraphQL, an MCP integration, or another transport only as authorized by the repository and available credentials.

## Build bodies from the distribution table

Construct the EPIC body from:

- description;
- each complete `SPEC-*` block mapped to `EPIC`;
- affected components;
- dependencies;
- execution order;
- global acceptance criteria;
- story checklist with issue numbers after creation.

Construct each story body from:

- the story description;
- an `Applicable specification` section containing the complete text of every mapped `SPEC-*` block;
- tasks;
- story acceptance criteria;
- quality checklist;
- the relation to the EPIC issue;
- a link to the versioned EPIC document.

Do not replace applicable specification text with IDs, summaries, or links. Preserve negations, units, bounds, failure behavior, edge cases, and explicit exclusions.

If a body would exceed the platform limit, stop and redesign the story boundaries or obtain explicit approval for another lossless representation. Never truncate.

## Detect remote state

Search all states, not only open resources:

1. Find an EPIC issue whose title starts with the deterministic `EPIC-NNN:` prefix.
2. Find every story by its deterministic `STORY-NNN-SSS:` prefix.
3. Find the documentation branch and open PR.
4. Compare titles, labels, relationships, bodies, head SHA, and base branch.
5. Classify each resource as absent, current, stale, or conflicting.

Treat a matching deterministic identity with different semantics as a conflict, not a resource to overwrite.

## Exact-write checkpoint

Before the first remote mutation, show:

- EPIC title, labels, and complete body preview;
- every story title, labels, and complete body preview;
- every planned parent/sub-issue and dependency relationship;
- which existing resources will be reused or patched;
- branch name, commit intent, and PR body;
- any temporary interval before the EPIC document reaches the base branch.

Wait for explicit approval. Creating issues is irreversible even when they can later be closed.

## Create or resume

Apply writes one resource at a time and read each one back:

1. Create or reuse the EPIC issue.
2. Create or reuse stories and record their numbers.
3. When supported, make every story a native sub-issue of the EPIC and create native blocking relationships for explicit dependencies.
4. Rebuild and patch the EPIC body with story relationships.
5. Create or reuse the documentation branch from the current protected base.
6. Move the single approved working EPIC to `docs/epics/EPIC-NNN-name.md`; do not copy it or publish the temporary source separately.
7. Add the EPIC issue link to the document and update `docs/epic-index.md` without duplicating entries. If the index does not exist, create it from `assets/epic-index-template.md`, adapt it to the repository language, link the heading to the versioned EPIC with a relative path, resolve or remove every placeholder, and place the published EPIC newest first. If it exists, preserve its language and EPIC ordering and remove any backlog entry promoted into the published EPIC. In either case, populate `Stories` with every story's stable identifier, title, and direct GitHub issue link; an issue range is insufficient. Reserve `Notes` for exceptions or context, use the repository's controlled status vocabulary or `Active`, `Blocked`, `Completed`, and `Cancelled` by default, and omit the completion-only paragraphs while the EPIC is active. Keep unpublished future work in GitHub Projects, the repository's existing backlog authority, or a separate `docs/epic-backlog.md` created from `assets/epic-backlog-template.md` only when source backlog content exists. If the existing index embeds future backlog, preview and perform a lossless migration before removing it from the index.
8. Run format, lint, link, policy, and other repository-required checks.
9. Commit using the repository convention, synchronize with the current base without rewriting reviewed history, push, and create or reuse the PR.
10. Read back issue bodies, native relationships, and PR metadata. Verify exact relationships and SHA.
11. After confirming that the final EPIC contains the complete source and is recoverable, retire the temporary source and report what was removed and how it can be recovered.

Write Markdown bodies through files or another transport that preserves bytes. Avoid inline shell quoting for multiline Markdown.

Do not start story implementation while the documentation exists only on an unmerged branch. State that dependency explicitly in the handoff.

## After merge

Act only after the user confirms the merge:

1. Verify the merged PR and head SHA.
2. Mark only satisfied issue checkboxes.
3. Record material findings that affect subsequent stories.
4. Delete the merged local and remote branch using safe, non-forced operations.
5. Synchronize the protected base and confirm a clean tree.

Never merge on the user's behalf unless they explicitly request it and repository policy permits it.

## After EPIC completion

Do not equate the documentation PR merge with EPIC completion. Act only after remote evidence confirms that every story and EPIC acceptance criterion is complete, then preview and obtain approval for the exact index and issue updates.

Keep every story and its direct GitHub issue link in `Stories`, set the completion status and date, and append beneath `Notes`:

- `Final verification` with final acceptance, checks, tests, and review evidence;
- `Findings` with material discoveries, deviations, corrections, and follow-ups, or `None`;
- `Exit state` with the delivered state, remaining boundaries, and deferred or future scope.

Limit each completion field to three concise paragraphs or bullet points and link to full evidence in the EPIC document, issues, or pull requests.

Read the updated index and issues back. Do not declare the EPIC closed if any story is missing, any link is indirect or unresolved, or any completion paragraph is absent.
