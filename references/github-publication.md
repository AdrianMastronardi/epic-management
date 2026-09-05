# GitHub publication

Read this file only when the user has approved the EPIC coverage checkpoint and asks to publish or resume publication. Read [okf-bundle.md](okf-bundle.md) first; it defines the artifacts this protocol writes. Read [github-sub-issues.md](github-sub-issues.md) before inspecting or mutating parent/sub-issue relationships.

## Publication boundary

For a new publication, the approved EPIC must still be a working concept directory under `tmp/`. Neither `prepare` nor `refine` may create GitHub issues or write anything inside `docs/epics/`.

Cross that boundary only after the exact-write checkpoint is approved. `resume` may continue publication mutations only when evidence shows that an approved publication already started; otherwise return to the normal `publish` checkpoint.

## Preconditions

- Read the repository's agent guidance, contribution rules, label catalog, protected-branch policy, versioning rules, and required checks.
- Confirm that `scripts/validate_epic.py` passes for the working directory.
- Confirm that a new publication starts from the single approved `tmp/EPIC-NNN-name/` directory and that nothing was pre-created inside `docs/epics/`.
- Confirm that every concept carries a human `verified` entry recorded at the coverage checkpoint.
- Confirm that the working tree is clean or that every existing change is understood and preserved.
- Confirm that the EPIC number and deterministic titles do not collide with unrelated resources.
- Confirm that no generated body refers to `tmp/`.
- Confirm that a native sub-issue transport is available and record which CLI or API path publication will use. Do not probe write permission with an unapproved mutation.
- Detect the layout. When the repository still uses the legacy flat layout, migrate it first under the `migrate` protocol in `SKILL.md`, or fold the migration into this exact-write preview with the user's approval.

Repository rules override the examples below. Use REST, GraphQL, an MCP integration, or another transport only as authorized by the repository and available credentials.

## Build bodies from the distribution table

Construct the EPIC body from:

- the EPIC concept's description;
- each complete `SPEC-*` block mapped to `EPIC`;
- affected components;
- dependencies;
- execution order;
- global acceptance criteria;
- an optional plain-linked story summary when repository conventions require body navigation. Never use Markdown checkboxes to represent parentage or progress already owned by native sub-issues.

Construct each story body from:

- the story concept's description;
- an `Applicable specification` section containing the complete text of every block named in the story's `applicable_blocks`;
- tasks;
- story acceptance criteria;
- quality checklist;
- the relation to the EPIC issue;
- a link to the published EPIC concept.

The story concept links its blocks instead of copying them, which is correct inside the bundle and wrong in an issue. Resolve every such link into full text when generating a body. Do not replace applicable specification text with IDs, summaries, or links. Preserve negations, units, bounds, failure behavior, edge cases, and explicit exclusions.

If a body would exceed the platform limit, stop and redesign the story boundaries or obtain explicit approval for another lossless representation. Never truncate.

## Detect remote state

Search all states, not only open resources:

1. Find an EPIC issue whose title starts with the deterministic `EPIC-NNN:` prefix.
2. Find every story by its deterministic `STORY-NNN-SSS:` prefix.
3. Read the EPIC's native sub-issues in priority order and the current parent of every reused story.
4. Find the documentation branch and open PR.
5. Compare titles, labels, parentage, native child order, dependencies, bodies, head SHA, and base branch.
6. Classify each resource and relationship as absent, current, stale, or conflicting.

Treat a matching deterministic identity with different semantics as a conflict, not a resource to overwrite.

## Exact-write checkpoint

Before the first remote mutation, show:

- EPIC title, labels, and complete body preview;
- every story title, labels, and complete body preview;
- every planned native parent/sub-issue action, current parent, final child priority, and dependency edge, keeping parentage and dependencies separate;
- which existing resources will be reused or patched;
- every file created, moved, or modified inside `docs/epics/`, including the index entry;
- branch name, commit intent, and PR body;
- any temporary interval before the published concepts reach the base branch.

Wait for explicit approval. Creating issues is irreversible even when they can later be closed.

## Create or resume

Apply writes one resource at a time and read each one back:

1. Create or reuse the EPIC issue.
2. Create new stories with the EPIC parent in the same command when the transport supports it. For reused stories, verify they have no conflicting parent before attaching them.
3. Read every relationship back in both directions, reconcile native priority with the ordered `stories` list, and create blocking relationships only for explicit dependencies.
4. Rebuild and patch the EPIC body if repository conventions require a plain-linked story summary. Do not duplicate native progress as a Markdown checklist.
5. Create or reuse the documentation branch from the current protected base.
6. Move the single approved working directory to `docs/epics/EPIC-NNN-name/`; do not copy it and do not publish the temporary source separately.
7. Update the frontmatter that publication owns: set `status: stable` on every concept, set the EPIC's `resource` to its issue URL, set each `stories[].resource` and each story concept's `resource`, and refresh `generated.at` on every concept you changed.
8. Update `docs/epics/index.md`: add one linked entry under the group matching `epic_status`, newest first, taking its description from the concept's `description`. Create the file from `assets/bundle-index-template.md` when it does not exist, adapt its language to the repository, and resolve or remove every placeholder. Preserve an existing index's language and ordering, and never add future work without a published concept or issue.
9. Keep unpublished future work in GitHub Projects, the repository's existing backlog authority, or `docs/epics/backlog.md` created from `assets/backlog-concept-template.md` only when source backlog content exists. If the existing index embeds future backlog, preview and perform a lossless migration before removing it from the index.
10. Run `scripts/validate_epic.py` against the published directory and `scripts/validate_okf_bundle.py` against `docs/epics`, then run format, lint, link, policy, and other repository-required checks.
11. Commit using the repository convention, naming the EPIC identifier in the subject line because this commit is the bundle's history entry, then synchronize with the current base without rewriting reviewed history, push, and create or reuse the PR.
12. Read back issue bodies, every story's parent, the EPIC's complete ordered sub-issue set and summary, dependency edges, and PR metadata. Verify exact relationships and SHA.
13. After confirming that the published concepts contain the complete source and are recoverable, retire the temporary source and report what was removed and how it can be recovered.

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

Do not equate the documentation PR merge with EPIC completion. Act only after remote evidence confirms that every story and EPIC acceptance criterion is complete, then preview and obtain approval for the exact concept, index, and issue updates.

In `epic.md`, set `epic_status: Completed` and `completed_on`, append a `verified` entry for the closing review, and add:

- `## Final verification` with final acceptance, checks, tests, and review evidence;
- `## Findings` with material discoveries, deviations, corrections, and follow-ups, or `None`;
- `## Exit state` with the delivered state, remaining boundaries, and deferred or future scope.

Limit each completion section to three concise paragraphs or bullet points and link to full evidence in the issues or pull requests. Move the index entry into the completed group, and name the EPIC identifier in the closing commit subject so the git history records the completion.

A completed EPIC keeps `status: stable`. Use `status: deprecated` only for an EPIC that was superseded or withdrawn, and name the superseding concept in the same change.

Read the updated concepts, index, and issues back. Do not declare the EPIC closed if any declared story is missing from the native sub-issue set, has another parent, remains open, is out of order, any link is indirect or unresolved, any completion section is absent, or either validator fails.
