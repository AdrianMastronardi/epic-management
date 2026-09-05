# GitHub Sub-issues

Read this file before creating, attaching, reparenting, ordering, or verifying EPIC story issues. GitHub Sub-issues are a native issue relationship, not a Markdown task list and not a dependency edge.

## Relationship model

- The EPIC issue is the parent.
- Every `STORY-NNN-SSS` issue is a direct native sub-issue of that EPIC.
- A story remains an independent GitHub issue with its own body, state, labels, assignees, and discussion.
- The parent/sub-issue relation expresses decomposition and ownership. `blocked by` and `blocking` express execution constraints. Create dependency edges only when the specification states them; never infer them from story order.
- The native sub-issue order follows the ordered `stories` list in `epic.md`.
- A Markdown checklist or a `## Stories` body section is never evidence of parentage. Do not create a checkbox list to imitate the native relation. GitHub's sub-issue panel and progress summary are authoritative.

This workflow uses one hierarchy level: all story issues are direct children of the EPIC. GitHub currently allows up to 100 sub-issues per parent and up to eight nested levels, but nesting stories beneath other stories would make the bundle's flat `stories` projection ambiguous. If an EPIC needs more than 100 stories or another hierarchy level, stop during coverage review and redesign the issue model explicitly.

## Preflight without mutation

Resolve the GitHub host, repository, authenticated identity, and transport before the exact-write checkpoint.

For a current GitHub CLI, confirm the native flags exist:

```sh
gh issue create --help
gh issue edit --help
gh issue view --help
```

The expected capabilities are:

- `gh issue create --parent` for creating a new story and assigning its EPIC parent in the same command;
- `gh issue edit --add-sub-issue` or `gh issue edit --parent` for attaching an existing story;
- `gh issue view --json parent,subIssues,subIssuesSummary` for readback.

If those flags are unavailable but `gh api` works, use GitHub's REST Sub-issues endpoints. A fine-grained token needs Issues read permission for observation and Issues write permission for mutation. REST permits a child owned by the same repository owner as the parent; keep stories in the EPIC repository unless the approved plan explicitly names a cross-repository child.

When repository policy selects GraphQL or an integration that exposes the same native relation, use that transport without changing the contract. GitHub GraphQL's `addSubIssue` takes the parent `issueId`, either `subIssueId` or `subIssueUrl`, and an optional `replaceParent`; keep replacement false unless separately approved. Its `reprioritizeSubIssue` takes the parent and child node IDs plus exactly one of `afterId` or `beforeId`. GraphQL uses node IDs, unlike the numeric database IDs required by REST.

Do not test write permission by making an unapproved mutation. State the selected transport and any permission uncertainty in the exact-write preview.

## Observe and classify

Before creating or attaching anything, read all issue states, not only open issues:

1. Find the deterministic EPIC and story titles.
2. Read the EPIC's full native sub-issue list in order.
3. Read the current parent of every reused story.
4. Compare the observed children with the ordered `stories` entries in `epic.md`.
5. Classify every intended relationship as `absent`, `current`, `stale`, or `conflicting`.

A relationship is stale when its parent is correct but its native priority differs from the approved story order. It is conflicting when the story belongs to another parent, the EPIC has an undeclared child, or two candidates share one deterministic identity. Never silently detach, replace, or adopt a conflicting issue.

With a current CLI, the readback is:

```sh
gh issue view EPIC_NUMBER --repo OWNER/REPO --json parent,subIssues,subIssuesSummary
gh issue view STORY_NUMBER --repo OWNER/REPO --json parent
```

The REST equivalents are:

```sh
gh api --paginate repos/OWNER/REPO/issues/EPIC_NUMBER/sub_issues
gh api repos/OWNER/REPO/issues/STORY_NUMBER/parent
```

In current GitHub CLI output, `subIssues` is an object with `nodes` and `totalCount`, not a flat array. Compare the node count with `totalCount` before trusting the result. The REST list preserves native sub-issue priority and exposes both the issue `number` and its numeric database `id`. An unparented story returns `parent: null` through the CLI; the REST parent endpoint may return `404`, which means “no parent” only after a separate issue lookup proves that the story exists and is readable.

## Exact-write checkpoint

For each story, preview:

- issue title and whether it will be created or reused;
- expected parent EPIC;
- current parent, if any;
- relationship action: create-with-parent, attach, keep, reorder, reparent, or conflict;
- final native priority;
- dependency edges, listed separately from parentage.

Reparenting is a distinct destructive relationship change. Require explicit approval that names the old parent, new parent, and affected story. Ordinary publication approval does not authorize replacing an existing parent.

If the EPIC body contains a legacy Markdown story checklist, treat its removal or conversion to plain links as a separate body edit in the preview. Preserve user-authored prose; never silently rewrite it merely because native sub-issues now exist.

## Apply idempotently

Create or reuse the EPIC issue first. Then process stories in their `epic.md` order, one at a time.

For a new story with a current CLI, create the issue and assign its parent in the same command:

```sh
gh issue create --repo OWNER/REPO --title "STORY-NNN-SSS: NAME" --body-file STORY_BODY --parent EPIC_NUMBER
```

For an existing unparented story:

```sh
gh issue edit EPIC_NUMBER --repo OWNER/REPO --add-sub-issue STORY_NUMBER
```

The equivalent `gh issue edit STORY_NUMBER --parent EPIC_NUMBER` is valid, but do not use it until readback proves the story has no different parent.

When the CLI flags are unavailable, create or reuse the story, obtain its numeric REST database `id`, and attach it through the parent endpoint:

```sh
gh api repos/OWNER/REPO/issues/STORY_NUMBER --jq .id
gh api --method POST repos/OWNER/REPO/issues/EPIC_NUMBER/sub_issues -F sub_issue_id=STORY_DATABASE_ID
```

`sub_issue_id` is the numeric REST database ID, not the issue number and not the GraphQL node ID returned by `gh issue view --json id`.

GitHub allows only one parent. The REST `replace_parent: true` option or a CLI parent replacement may detach the story from its existing parent. Use it only after the dedicated reparenting approval.

After all children are attached, compare native order with `epic.md`. If it differs, use the REST priority endpoint with exactly one of `after_id` or `before_id` and numeric REST database IDs:

```sh
gh api --method PATCH repos/OWNER/REPO/issues/EPIC_NUMBER/sub_issues/priority -F sub_issue_id=STORY_DATABASE_ID -F after_id=PREVIOUS_STORY_DATABASE_ID
```

Do not encode ordering as blocking dependencies.

## Read back and prove

After every relationship mutation, read both directions back. Before publication completes, prove all of the following:

- the EPIC has exactly the story issues declared by `epic.md`, with no missing or undeclared children;
- every story reports the EPIC as its parent;
- native child order matches the `stories` order;
- dependencies match only the explicit execution constraints;
- `subIssuesSummary.total` equals the number of declared stories;
- issue URLs agree with `epic.md` and the story concepts.

At EPIC closure, also require every declared native sub-issue to be closed and the native completion summary to be complete. A checked Markdown task list does not satisfy this condition.

If any mutation succeeds and a later step fails, stop and report the partial state. `resume` must re-observe both directions, stop again on conflicts, and continue from the first absent or stale relationship without duplicating issues or attachments.

If no authorized transport exposes native sub-issues on the target GitHub host, stop before publication. Do not degrade to task lists, issue-body links, labels, milestones, or dependency edges while claiming that sub-issues were created.

## Authoritative GitHub references

- [Adding sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)
- [REST API endpoints for sub-issues](https://docs.github.com/en/rest/issues/sub-issues)
- [GraphQL issue mutations](https://docs.github.com/en/graphql/reference/issues)
- [`gh issue create`](https://cli.github.com/manual/gh_issue_create)
- [`gh issue edit`](https://cli.github.com/manual/gh_issue_edit)
- [`gh issue view`](https://cli.github.com/manual/gh_issue_view)
