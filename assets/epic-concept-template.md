---
type: EPIC
title: "EPIC-{{NNN}} — {{NAME}}"
description: "{{ONE_SENTENCE_OUTCOME}}"
tags: [epic, "{{TAG}}"]
status: draft
generated: { by: "{{HOST}}/{{MODEL}}", at: "{{ISO_8601_UTC}}" }
sources:
  - id: "{{SOURCE_ID}}"
    resource: "{{URL_BUNDLE_PATH_OR_SCOPE_DESCRIPTOR}}"
    title: "{{SOURCE_TITLE}}"
    author: "{{ACTOR}}"
    last_modified: "{{YYYY-MM-DD}}"
epic_number: "{{NNN}}"
epic_status: Active
started_on: "{{YYYY-MM-DD}}"
completed_on:
stories:
  - id: "STORY-{{NNN}}-001"
    title: "{{STORY_TITLE}}"
    concept: "./STORY-{{NNN}}-001-{{STORY_SLUG}}.md"
---

## Description

{{PROBLEM_GOALS_AND_OUTCOME}}

## Functional and technical specification

### SPEC-{{NNN}}-001: {{BLOCK_NAME}}

{{COMPLETE_SPECIFICATION_CONTENT_WITH_INTENDED_APPROACH_REPOSITORY_STARTING_POINTS_CONTRACTS_AND_FAILURE_BEHAVIOR}}

**Decisions and rationale:** {{AGREED_DECISIONS_AND_REASONS_PROPOSALS_AND_IMPLEMENTER_DISCRETION}}

**Verification:** {{CONCRETE_SCENARIOS_AND_EXPECTED_RESULTS}}

**Open questions:** {{UNRESOLVED_IMPLEMENTATION_DECISIONS_OR_NONE}}

### SPEC-{{NNN}}-002: {{BLOCK_NAME}}

{{COMPLETE_SPECIFICATION_CONTENT}}

## Affected components

- {{COMPONENT}}

## Dependencies

| Producer                                       | Consumer          | Output                                                    | Phase                           | Release condition                              | Projection               | Spec             |
| ---------------------------------------------- | ----------------- | --------------------------------------------------------- | ------------------------------- | ---------------------------------------------- | ------------------------ | ---------------- |
| {{PRODUCER_STORY_ID_OR_EXTERNAL_PREREQUISITE}} | STORY-{{NNN}}-001 | {{REQUIRED_OUTPUT_AND_WHEN_THE_PRODUCER_MAKES_IT_USABLE}} | {{start_integrate_OR_complete}} | {{OBSERVABLE_EVIDENCE_THAT_RELEASES_THE_GATE}} | {{native_OR_documented}} | SPEC-{{NNN}}-001 |

{{PROJECTION_RATIONALE_FOR_EACH_DEPENDENCY_OR_REPLACE_THE_TABLE_AND_THIS_LINE_WITH_NONE}}

## Execution order

{{DEPENDENCY_GRAPH_OR_DIRECTED_EDGE_LIST_WITH_PHASE_AND_OUTPUT_LABELS_INDEPENDENT_STORIES_AND_EXTERNAL_PREREQUISITES_OR_SINGLE_STORY_PLAN}}

{{EXECUTABLE_EVENT_SEQUENCE_FOR_APPARENT_STORY_CYCLES_OR_REAL_CYCLE_BLOCKERS_OR_REMOVE}}

{{SPLIT_RATIONALE_CANDIDATE_CONCURRENT_WORK_BOTTLENECKS_AND_UNRESOLVED_ASSUMPTIONS_WITH_SPEC_LINKS_AS_NEEDED}}

## Acceptance criteria

- [ ] {{GLOBAL_CRITERION}}

## GitHub distribution

| Block            | Class       | Destination             |
| ---------------- | ----------- | ----------------------- |
| SPEC-{{NNN}}-001 | operational | EPIC, STORY-{{NNN}}-001 |
| SPEC-{{NNN}}-002 | context     | DOCUMENT                |
