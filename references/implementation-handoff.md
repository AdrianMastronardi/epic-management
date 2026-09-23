# Implementation handoff

An independent agent should be able to take a story issue and the target repository, understand the intended implementation, and begin work without the preparation conversation. Acceptance criteria describe success; they do not replace the approach and reasoning that produced the plan.

## Capture the intended approach

Use the source specification, available preparation and refinement discussion, and relevant repository evidence. For each story, preserve the following where they affect implementation; scale detail to the work rather than filling irrelevant categories:

- **Starting points:** existing paths, symbols, interfaces, and patterns to reuse, with their role in the change. Label proposed files or interfaces as new. Verify existing references against the repository; record unavailable evidence as an uncertainty.
- **Approach and sequence:** the changes to make, how they connect, and their order. Include data or control flow, ownership boundaries, and prerequisite outputs from other stories when relevant.
- **Contracts and failure behavior:** relevant API or schema shapes, invariants, compatibility constraints, errors, retries, concurrency, and migration or rollout requirements. Include concrete examples or pseudocode when prose leaves a consequential ambiguity.
- **Decisions and rationale:** the selected approach and why it was chosen. Preserve rejected alternatives only when their tradeoffs explain a constraint or prevent a likely wrong implementation.
- **Verification:** concrete scenarios, inputs, expected outcomes, and relevant test locations or commands. Tie them to acceptance criteria, including applicable failure cases; “add tests” is insufficient.
- **Boundaries and uncertainty:** exclusions, assumptions, open questions, and choices intentionally left to the implementing agent.

Separate agreed decisions and requirements from proposed approaches and implementation discretion. Never present an agent suggestion as a user-approved decision. If an unresolved choice changes scope, a public contract, or the intended architecture, surface it at refinement and keep the affected work unready until resolved or explicitly delegated with constraints. Routine local choices can remain with the implementer.

Record new or revised decisions during each refinement, including their rationale and affected stories. When discussion contradicts the source, surface the conflict for resolution; do not silently choose a version. Replace superseded guidance in active blocks and preserve the reason for a material change so contradictory instructions do not reach an issue.

## Store once, deliver where needed

Keep the substantive implementation design and rationale in `SPEC-*` blocks in `epic.md`, including design that applies to only one story. Classify implementation guidance as `operational`. Map shared decisions to every affected story, as well as to `EPIC` when relevant; routing a decision only to the parent issue is insufficient when a story implementer needs it.

Story concepts link those blocks in `Applicable specification`. Their `Tasks` give an ordered execution plan referencing the relevant blocks; their acceptance criteria and quality checklist state observable results and checks. Do not copy the design into a second bundle document.

Record discussion-derived decisions in `sources` using a scope descriptor naming the EPIC, topic, and actual discussion date, and attribute them as described in [okf-bundle.md](okf-bundle.md). Preserve the substantive decision in the concept: a conversation reference alone cannot carry implementation context.

When generating GitHub bodies, expand every applicable block into full text, including approach, rationale, constraints, and decision status. Carry over the ordered tasks and specific checks. Durable references provide supporting evidence; the issue itself must contain the decisions necessary to implement it.

## Independent-agent review

Review each story as if the preparation conversation were unavailable. During preparation, assess the story with its resolved specification blocks; before publication, repeat the review against the actual issue-body preview. This is a semantic review, not a requirement to spawn another agent.

Can an implementer determine:

1. What changes, what stays outside scope, and what observable result completes the story?
2. Where to start in the repository, which existing patterns to reuse, and which elements are proposed additions?
3. How the intended solution works, in what order to build it, and which prerequisite contracts or outputs it relies on?
4. Why the consequential decisions were made, which are binding, and which choices remain open to the implementer?
5. How to verify the result, including the relevant edge and failure cases?

If an answer depends on remembering the discussion, “see parent issue,” an unexplained design link, or a task such as “implement the service,” add the missing substance to a routed specification block. A structurally valid document with these gaps is not ready for implementation. Report unresolved blockers at the existing checkpoint; do not invent answers to pass the review.

## Example of useful detail

For an illustrative persistence story, “persist the index and add tests” loses the implementation plan. If refinement actually chose atomic snapshot replacement, preserve that choice: reuse the existing serializer, write a temporary sibling file, replace the current snapshot only after the write succeeds, and retain the previous snapshot on failure. Record that the choice prevents readers from observing a partial snapshot, identify the inspected persistence entry point, and specify success and injected-write-failure checks. Label any unconfirmed durability guarantees as open questions. Do not apply this design to unrelated stories.
