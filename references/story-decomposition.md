# Story decomposition

Apply during `prepare` and `refine`, then check the resulting plan against the issue-body previews before publication. Optimize for completing the EPIC sooner with coherent, verifiable stories. A larger issue count or smaller average story size is not evidence of improvement.

## Choose useful boundaries

For a large story or one that delays other work, identify the concrete output each consumer needs. Split when an earlier verifiable delivery or independent work becomes possible and the benefit outweighs added context, review, and integration costs. Record the reason for consequential splits or for retaining a shared prerequisite in the execution plan.

- Give each resulting story a coherent outcome, explicit scope, and its own acceptance and verification criteria. A technical enabling story is useful when it delivers a needed, testable capability or contract.
- Extract only the shared prerequisite that consumers need; avoid a broad foundations story that remains the bottleneck. Do not create a contract issue when the approved specification already supplies everything consumers need.
- Keep tightly coupled changes together when splitting merely creates a longer serial chain. Do not split by file, technical layer, task count, or arbitrary size targets alone.
- If a shared contract still depends on unresolved domain or implementation questions, expose that uncertainty. Do not promise parallel execution against a contract that cannot yet be stabilized.

Preserve source coverage and implementation rationale when splitting. Reconcile the story list, concepts, index, distribution table, and applicable blocks. All stories remain direct children of the EPIC; decomposition does not introduce another hierarchy level.

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

## Check cycles between deliverables

A cycle in a story-level overview is a signal to inspect the deliverables, not proof that the plan is blocked. Expand the implicated edges into output-availability and consumer-phase milestones, including the internal prerequisites needed to produce each output. Here, a milestone is a delivery event, not a GitHub Milestone resource. Establish whether these events have an executable order from the stated initial conditions. Do not assume an output exists merely because its producer can start.

For example, A can publish a schema before completing, B uses that schema to generate a client, and A then integrates the client. The overview has A → B → A, but the event sequence is `A.schema available → B.client available → A.integration`. Keep that valid sequence visible without forcing a split just to remove the overview cycle. If producing A's schema itself requires B's client, and neither output already exists, the event prerequisites are circular: report the unresolved planning blocker instead of inventing a starting point or available artifact.

Apply the same check when a cycle mixes start, integration, and completion conditions. Resolve real cycles through an evidenced initial artifact or an explicitly proposed design change; changing story names or drawing a different order does not resolve them.

## Review interference and integration

Inspect relevant repository evidence for stories proposed to run concurrently: shared modules and interfaces, schema migrations, generated artifacts, and exclusive test or deployment resources. Record meaningful overlaps and a concrete way to handle them, such as a stable shared contract, separate ownership boundaries, compatible migrations, or a narrow sequencing constraint. Sharing a file warrants review, not an automatic blocking edge. Separate worktrees do not remove integration conflicts.

Include compatibility checks in each affected story and assign the final integrated acceptance check to a named story or explicit EPIC verification activity. Create a separate integration story only when that is a coherent unit of work. Avoid deferring all compatibility discovery to the end.

## Store and present the plan

Keep substantive prerequisite contracts, release conditions, interference decisions, and rationale in operational `SPEC-*` blocks, routed to every affected story and to the EPIC when needed. Story concepts link these blocks and express their implementation and verification work in their existing tasks, acceptance criteria, and quality checklist.

Use the existing EPIC `Dependencies` section to summarize each dependency in the template's table: producer story or external prerequisite, consumer story, required output and when it becomes usable, constrained phase (`start`, `integrate`, or `complete`), release condition, proposed projection (`native` or `documented`), and the blocks that hold the substance. Follow the table with the rationale for each projection; write `None` when there are no inter-story or external dependencies. `validate_epic.py` checks that table's story and block identifiers, phases, projections, routing to the consumer, and cycles among native edges. It cannot tell whether the stated outputs and conditions are true. Use `Execution order` for the dependency graph and decomposition rationale. The graph may be a diagram or a directed edge list; label edges with their phase and output, include independent stories, and identify external prerequisites. These sections summarize the same design rather than maintaining a second specification.

At the coverage checkpoint, show which stories can start once their stated prerequisites hold, which outputs unlock further work, candidate concurrent work, remaining bottlenecks, and unresolved assumptions. Explain apparent story cycles with their executable event sequence, or report real circular prerequisites as unresolved planning blockers. Identify the likely critical path when evidence supports it, and avoid invented duration estimates. Let each story proceed when its own prerequisites hold; presentation groups or waves must not create barriers between otherwise independent stories.

The bundle records durable dependency design, not current readiness, assignees, progress, or satisfied/unsatisfied flags. GitHub remains authoritative for live blocking state, including phase conditions documented in issue bodies.

## Project dependencies into GitHub

Use this conservative workflow policy consistently; it does not claim that GitHub itself prohibits work on a blocked issue:

| Approved constraint                                                                                                     | Projection                                                                                                              |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| The consumer cannot start until a producer issue completes its required delivery, with no usable earlier output.        | Native `consumer blocked by producer` relationship plus the required output and release condition in the consumer body. |
| The consumer can start, but needs the producer to integrate or complete.                                                | Document the phase condition in the consumer body; do not create a native edge for this condition.                      |
| The consumer needs an output available before the producer issue completes.                                             | Document the output and constrained phase in the consumer body; do not make producer closure the gate.                  |
| The prerequisite is external and has no corresponding issue, or is only preferred sequencing or potential interference. | Document the prerequisite or coordination decision; do not invent an issue or native edge.                              |

Evaluate each constraint separately. A later completion condition does not remove a distinct, valid start dependency. The native projection must stay acyclic: a cycle of native edges is a real circular prerequisite, never a publishable plan. Extract an earlier deliverable into a story only when the normal split criteria justify it, not merely to obtain a native edge.

Write every gate, native or documented, in the consumer story as a checkbox in the section for the phase it constrains: a task for a start or integration gate, an acceptance criterion for a completion gate. Name the producer or external prerequisite, the output, and the release evidence. For a documented condition, also state what work may proceed and what must wait; omission from native edges must never imply that the condition is optional. In the issue, that checkbox is the gate's live state: whoever observes the evidence checks it, and the consumer is not complete while one remains open. Publication and `resume` report observed evidence in their previews and check a gate only as an approved body edit.

At coverage review, include each dependency's proposed projection and rationale alongside its specification reference. At the exact-write checkpoint, reconcile that approved design with observed GitHub state and delivery evidence. Preview native edges to add, retain, or remove separately from documented phase conditions; explain omissions and any changed projection. If a prerequisite is already satisfied, do not add or restore an active blocker merely because it remains in the durable design. Changes to existing native edges follow the same exact-write approval and readback rules as other publication writes.

Delivery evidence is a read-only observation of the complete release condition, including availability to the consumer and every named check, not an inference from issue state. Either observation qualifies:

- the output is present on the consumer's base branch and the checks named by the release condition pass there;
- a merged pull request linked to the producer delivers that output to the consumer's base branch, the output remains available there, and the checks named by the release condition pass there. A merge into another branch, a reverted delivery, or missing or failing required checks does not satisfy the gate.

For an external prerequisite, observe whatever its release condition names. Record what was observed and where. Issue closure alone is not evidence: `completed` is a claim, so a closed producer with neither observation is the conflict described below whatever its `stateReason`. An open producer whose output is already observable satisfies a documented condition on that output; leave a native edge to it unchanged. When the observation cannot be made, such as an unreadable branch or check, report unknown satisfaction as explicit uncertainty instead of guessing, and never perform the producer's work to obtain evidence.

If a producer is closed without evidence of the required delivery, treat its disposition as a conflict with the prerequisite, not as a usable blocker or proof of satisfaction. Keep the consumer's documented gate unresolved and preview the missing evidence and required plan correction at the existing checkpoint. Resolve that conflict before applying the affected native dependency actions; do not add an edge to the closed producer as a substitute for resolution, silently reopen it, invent a replacement issue, or waive the output requirement.

A dependency published before this policy, or recorded without a phase and projection, has no approved projection. On `resume`, keep its existing native edges, add none for it, and report it as unclassified at the exact-write checkpoint. Classifying it is a design amendment that needs the coverage checkpoint, not a publication-time guess.

This policy defines publication and resumption behavior, not an ongoing scheduler. During implementation, gate satisfaction belongs in GitHub; do not mirror it into bundle fields or automatically mutate issues as a side effect of reviewing the design.

## Review the result

The semantic review must establish that:

- each split has a useful delivery or unlock benefit relative to its coordination cost;
- each dependency names an output, when the producer makes it usable, and an observable release condition for the affected consumer phase;
- apparent story cycles have an executable event sequence, while real circular prerequisites remain explicit blockers;
- each dependency has a justified native or documented projection, native edges form no cycle, and every gate appears as a checkbox in the consumer's tasks or acceptance criteria;
- candidate concurrent stories have compatible contracts and a plan for meaningful shared-resource interference;
- the graph, routed specification, story tasks, and verification responsibilities agree;
- no unresolved prerequisite or design choice is presented as already available.

Scale the review to the EPIC. A single independent story can state that there are no inter-story dependencies; it does not need invented enabling work. The structural validators do not prove graph correctness or parallel execution safety. If execution evidence later becomes available, evaluate the decomposition using blocked time, EPIC completion time, and integration rework rather than issue count.
