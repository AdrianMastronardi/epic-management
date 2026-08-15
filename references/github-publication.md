# GitHub publication

Read this file only when the user has approved the EPIC coverage checkpoint and asks to publish or resume publication.

## Preconditions

- Read the repository's agent guidance, contribution rules, label catalog, protected-branch policy, versioning rules, and required checks.
- Confirm that the EPIC document passes `scripts/validate_epic.py`.
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
- which existing resources will be reused or patched;
- branch name, commit intent, and PR body;
- any temporary interval before the EPIC document reaches the base branch.

Wait for explicit approval. Creating issues is irreversible even when they can later be closed.

## Create or resume

Apply writes one resource at a time and read each one back:

1. Create or reuse the EPIC issue.
2. Create or reuse stories and record their numbers.
3. Rebuild and patch the EPIC body with story relationships.
4. Create or reuse the documentation branch from the current protected base.
5. Move the single approved EPIC document to the repository's EPIC directory; do not publish the temporary source separately.
6. Add the EPIC issue link to the document and update the EPIC index without duplicating entries.
7. Run format, lint, link, policy, and other repository-required checks.
8. Commit using the repository convention, synchronize with the current base without rewriting reviewed history, push, and create or reuse the PR.
9. Read back issue bodies and PR metadata. Verify exact relationships and SHA.

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
