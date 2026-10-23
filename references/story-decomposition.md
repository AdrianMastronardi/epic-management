# Story decomposition

Apply during `prepare` and `refine`, then check the resulting plan against the issue-body previews before publication. Optimize for completing the EPIC sooner with coherent, verifiable stories. A larger issue count or smaller average story size is not evidence of improvement.

## Choose useful boundaries

For a large story or one that delays other work, identify the concrete output each consumer needs. Split when an earlier verifiable delivery or independent work becomes possible and the benefit outweighs added context, review, and integration costs. Record the reason for consequential splits or for retaining a shared prerequisite in the execution plan.

- Give each resulting story a coherent outcome, explicit scope, and its own acceptance and verification criteria. Once its declared prerequisites hold, it must be able to implement, verify, and close its entire scope without waiting on a story that depends on it. A technical enabling story is useful when it delivers a needed, testable capability or contract.
- Extract only the shared prerequisite that consumers need; avoid a broad foundations story that remains the bottleneck. Do not create a contract issue when the approved specification already supplies everything consumers need.
- Keep tightly coupled changes together when splitting merely creates a longer serial chain. Do not split by file, technical layer, task count, or arbitrary size targets alone.
- If a shared contract still depends on unresolved domain or implementation questions, expose that uncertainty. Do not promise parallel execution against a contract that cannot yet be stabilized.

Preserve source coverage and implementation rationale when splitting. Reconcile operational specification blocks, the story list, concepts, tasks, acceptance criteria, index, distribution table, applicable blocks, and projected issue bodies. Preserve real integration checks; passing against a double cannot replace acceptance against the required provider. All stories remain direct children of the EPIC; decomposition does not introduce another hierarchy level.

Story identifiers stay consecutive in `stories` order, so renumber freely only while no story issue exists. Once any story issue exists, its identifier and deterministic title are its identity: append stories created by a later split with the next identifiers, patch the narrowed story's body as a stale projection, and treat renumbering or retitling an existing issue as a conflict to preview.

## Explain dependencies through outputs

For each proposed dependency, record the producer story or external prerequisite, consumer story, required output, why it is needed, and its release condition: the observable evidence that makes the output usable and releases the gate, unrelated to a software release. Say whether that output becomes usable before the producer completes or requires its completed delivery. Distinguish the consumer phase it constrains:

| Phase     | Required explanation                                                                  |
| --------- | ------------------------------------------------------------------------------------- |
| Start     | What must be available before meaningful implementation can begin?                    |
| Integrate | What must be available before the change can be merged or connected to its consumers? |
| Complete  | What must be available before acceptance and verification can finish?                 |

For example, a consumer may start against an approved API schema and compatible test double, while its integrated acceptance check requires the real provider. State how that double will be checked against the shared contract. Do not turn the later verification requirement into a blanket prohibition on starting.

Separate hard prerequisites from preferred sequencing and potential interference. Story numbers, native priority, and shared components do not establish dependencies. Mark dependencies discovered during refinement as proposals, preserve their evidence and rationale, and include them in the existing coverage checkpoint. Approval makes them explicit specification constraints; it does not authorize publication outside the existing exact-write checkpoint. In the same edit that records the `verified` entry, restate each approved dependency as an agreed constraint in its block so no issue body publishes it as a proposal; a dependency the user did not approve stays labeled as a proposal or is removed.

## Require an acyclic story dependency graph

Build the complete logical graph with `consumer → producer` edges for every execution prerequisite, including documented gates for integration and completion. The graph must be a directed acyclic graph (DAG), and self-dependencies are invalid. Phase, projection, partial output availability, and an executable sequence of milestones do not exempt an edge. Parentage, reciprocal informational links, preferred sequencing, and shared-resource interference do not establish execution prerequisites.

For example, A owns a schema and its eventual integration, while B generates a client from that schema. The sequence `A.schema → B.client → A.integration` is executable but leaves a cycle between issues. Propose three closable scopes: a contract story publishing and verifying the schema, a client story depending on the contract, and an integration story depending on the preceding outputs. Delivery and closure then follow `Contract → Client → Integration`. Equivalent decompositions are valid when they preserve all requirements and remove the cycle.

During analysis, diagnose any cycle with its closed story path and implicated phases and projections. Keep the plan unready until an approved scope split or design correction removes it. If the source asks to retain cyclic scopes, surface the contradiction at the coverage checkpoint rather than declaring the plan publishable. Do not hide a prerequisite by omitting it, relabeling it as documented or as a milestone, or removing acceptance criteria. An existing artifact removes a prerequisite only when the revised scope demonstrably no longer requires that producer; merely satisfying a gate does not remove it from the durable design.

When publication has already started, preserve existing issue identities and append identifiers for new stories. Preview changes to scope, bodies, and relationships through the existing coverage and exact-write checkpoints. Never silently renumber, close, reopen, or reparent issues to repair a cycle.

## Review interference and integration

Inspect relevant repository evidence for stories proposed to run concurrently: shared modules and interfaces, schema migrations, generated artifacts, and exclusive test or deployment resources. Record meaningful overlaps and a concrete way to handle them, such as a stable shared contract, separate ownership boundaries, compatible migrations, or a narrow sequencing constraint. Sharing a file warrants review, not an automatic blocking edge. Separate worktrees do not remove integration conflicts.

Include compatibility checks in each affected story and assign the final integrated acceptance check to a named story or explicit EPIC verification activity. Create a separate integration story only when that is a coherent unit of work. Avoid deferring all compatibility discovery to the end.

## Store and present the plan

Keep substantive prerequisite contracts, release conditions, interference decisions, and rationale in operational `SPEC-*` blocks, routed to every affected story and to the EPIC when needed. Story concepts link these blocks and express their implementation and verification work in their existing tasks, acceptance criteria, and quality checklist.

Use bare local `STORY-NNN-SSS` identifiers in story cells; do not wrap them in backticks or Markdown links. For a producer issue in another EPIC, use its canonical issue URL in `Producer`, with its identity, required output, and release condition in the referenced operational block. This remains an issue dependency that semantic review must follow, not an opaque external exemption; the offline validators cannot inspect its return paths.

Use the existing EPIC `Dependencies` section to summarize every dependency in the template's table: producer story or external prerequisite, consumer story, required output and when it becomes usable, constrained phase (`start`, `integrate`, or `complete`), release condition, proposed projection (`native` or `documented`), and the blocks that hold the substance. New and refined plans must include every execution prerequisite in this checkable representation; never leave a return edge only in prose, tasks, acceptance criteria, or a diagram while the table says `None` or lists only native projections. Follow the table with the rationale for each projection; write `None` only when there are no inter-story or external dependencies. Both validators check that table's story and block identifiers, phases, projections, routing to the consumer, and cycles across all internal rows. They cannot tell whether outputs and conditions are true or whether the table omits a real dependency. Use `Execution order` to present the same design and decomposition rationale, with phase and output labels, independent stories, and external prerequisites; do not maintain a second authoritative graph.

At the coverage checkpoint, show which stories can start once their stated prerequisites hold, which outputs unlock further work, candidate concurrent work, remaining bottlenecks, and unresolved assumptions. Require the complete story graph to be acyclic before presenting the plan as ready; show unresolved cycle paths with a proposed scope or design repair. Identify the likely critical path when evidence supports it, and avoid invented duration estimates. Let each story proceed when its own prerequisites hold; presentation groups or waves must not create barriers between otherwise independent stories.

Before the first affected mutation in `publish` or `resume`, reconcile the approved dependency table with all routed specification blocks, tasks, acceptance gates, issue-body previews, and known existing dependencies. Follow known prerequisites into other EPICs or issues far enough to check for a return path; do not relabel a known issue as opaque external text. If the necessary graph cannot be inspected, report that uncertainty and resolve it before affected writes. The local validators remain offline and check only declared internal rows. For legacy prose-only dependencies, `inspect` and `resume` must disclose that structural success does not establish acyclicity and require normalization or semantic plan review before affected dependency or issue-body writes.

For a new publication or its partial resume, every publication write is affected: issue creation or body edits, parentage or dependency changes, published bundle files, documentation branches and commits, and PRs carrying the plan. Complete graph review and validation of any existing bundle must precede those writes, including branch creation. Other resume operations must review the implicated plan before changing its issue bodies, relationships, or durable files. Repair preparation under `tmp/` may proceed while publication remains blocked. Include the reconciliation result and any inspected or unknown cross-EPIC paths in the exact-write preview.

This validation change also applies to historical `Completed` and `Cancelled` EPICs. A cyclic table in any EPIC blocks bundle validation and therefore later publication, even for another EPIC. First establish whether the rows incorrectly describe the historical prerequisites: an evidence-backed correction requires the existing approval checkpoints and must retain original requirements, decisions, and closure evidence in operational blocks. If a real historical cycle cannot be truthfully reconciled into an acyclic scope or design, report the blocked bundle and required design decision. Do not invent a decomposition that was never delivered, delete true prerequisites, or reopen, close, or reparent historical issues just to make validation pass; status and already-satisfied gates provide no exemption.

The bundle records durable dependency design, not current readiness, assignees, progress, or satisfied/unsatisfied flags. GitHub remains authoritative for live blocking state, including phase conditions documented in issue bodies.

## Project dependencies into GitHub

Use this conservative workflow policy consistently; it does not claim that GitHub itself prohibits work on a blocked issue:

| Approved constraint                                                                                                     | Projection                                                                                                              |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| The consumer cannot start until a producer issue completes its required delivery, with no usable earlier output.        | Native `consumer blocked by producer` relationship plus the required output and release condition in the consumer body. |
| The consumer can start, but needs the producer to integrate or complete.                                                | Document the phase condition in the consumer body; do not create a native edge for this condition.                      |
| The consumer needs an output available before the producer issue completes.                                             | Document the output and constrained phase in the consumer body; do not make producer closure the gate.                  |
| The prerequisite is external and has no corresponding issue, or is only preferred sequencing or potential interference. | Document the prerequisite or coordination decision; do not invent an issue or native edge.                              |

Evaluate each constraint separately. A later completion condition does not remove a distinct, valid start dependency. Require the complete logical graph to be acyclic before selecting native actions; an acyclic native subgraph cannot justify a cyclic plan. A split that produces coherent, closable scopes can repair a cycle; do not split merely to obtain a native edge.

Write every gate, native or documented, in the consumer story as a checkbox in the section for the phase it constrains: a task for a start or integration gate, an acceptance criterion for a completion gate. Name the producer or external prerequisite, the output, and the release evidence. For a documented condition, also state what work may proceed and what must wait; omission from native edges must never imply that the condition is optional. In the issue, that checkbox is the gate's live state: whoever observes the evidence checks it, and the consumer is not complete while one remains open. Publication and `resume` report observed evidence in their previews and check a gate only as an approved body edit.

At coverage review, include each dependency's proposed projection and rationale alongside its specification reference. At the exact-write checkpoint, reconcile that approved design with observed GitHub state and delivery evidence. Preview native edges to add, retain, or remove separately from documented phase conditions; explain omissions and any changed projection. If a prerequisite is already satisfied, do not add or restore an active blocker merely because it remains in the durable design. Changes to existing native edges follow the same exact-write approval and readback rules as other publication writes.

Delivery evidence is a read-only observation of the complete release condition, including availability to the consumer and every named check, not an inference from issue state. Either observation qualifies:

- the output is present on the consumer's base branch and the checks named by the release condition pass there;
- a merged pull request linked to the producer delivers that output to the consumer's base branch, the output remains available there, and the checks named by the release condition pass there. A merge into another branch, a reverted delivery, or missing or failing required checks does not satisfy the gate.

For an external prerequisite, observe whatever its release condition names. Record what was observed and where. Issue closure alone is not evidence: `completed` is a claim, so a closed producer with neither observation is the conflict described below whatever its `stateReason`. An open producer whose output is already observable satisfies a documented condition on that output; leave a native edge to it unchanged. When the observation cannot be made, such as an unreadable branch or check, report unknown satisfaction as explicit uncertainty instead of guessing, and never perform the producer's work to obtain evidence.

If a producer is closed without evidence of the required delivery, treat its disposition as a conflict with the prerequisite, not as a usable blocker or proof of satisfaction. Keep the consumer's documented gate unresolved and preview the missing evidence and required plan correction at the existing checkpoint. Resolve that conflict before applying the affected native dependency actions; do not add an edge to the closed producer as a substitute for resolution, silently reopen it, invent a replacement issue, or waive the output requirement.

A dependency published before this policy, or recorded without a phase and projection, has no approved projection. On `resume`, leave its existing native edges untouched, add none for it, and report it as unclassified at the exact-write checkpoint. Require normalization or semantic plan review before affected dependency or issue-body writes. Classifying it is a design amendment that needs the coverage checkpoint, not a publication-time guess. A discovered cycle blocks affected writes even when some resources already exist; obtain an approved plan correction and reuse their identities rather than duplicating them.

This policy defines publication and resumption behavior, not an ongoing scheduler. During implementation, gate satisfaction belongs in GitHub; do not mirror it into bundle fields or automatically mutate issues as a side effect of reviewing the design.

## Review the result

The semantic review must establish that:

- each split has a useful delivery or unlock benefit relative to its coordination cost;
- each dependency names an output, when the producer makes it usable, and an observable release condition for the affected consumer phase;
- the complete story dependency graph is acyclic across all phases and projections, and each story can close its full scope once its prerequisites hold;
- each dependency has a justified native or documented projection, and every gate appears both in the dependency table and as a checkbox in the consumer's tasks or acceptance criteria;
- candidate concurrent stories have compatible contracts and a plan for meaningful shared-resource interference;
- the graph, routed specification, story tasks, and verification responsibilities agree;
- no unresolved prerequisite or design choice is presented as already available.

Scale the review to the EPIC. A single independent story can state that there are no inter-story dependencies; it does not need invented enabling work. The structural validators do not prove graph correctness or parallel execution safety. If execution evidence later becomes available, evaluate the decomposition using blocked time, EPIC completion time, and integration rework rather than issue count.
