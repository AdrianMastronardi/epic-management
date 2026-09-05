---
type: EPIC
title: "EPIC-{{NNN}} — {{NAME}}"
description: "{{ONE_SENTENCE_OUTCOME}}"
tags: [epic, "{{TAG}}"]
status: draft
generated: { by: "{{HOST}}/{{MODEL}}", at: "{{ISO_8601_UTC}}" }
stale_after: "{{YYYY-MM-DD_OR_REMOVE}}"
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

{{COMPLETE_SPECIFICATION_CONTENT}}

### SPEC-{{NNN}}-002: {{BLOCK_NAME}}

{{COMPLETE_SPECIFICATION_CONTENT}}

## Affected components

- {{COMPONENT}}

## Dependencies

{{DEPENDENCIES_OR_NONE}}

## Execution order

{{ORDER_AND_RATIONALE}}

## Acceptance criteria

- [ ] {{GLOBAL_CRITERION}}

## GitHub distribution

| Block            | Class       | Destination             |
| ---------------- | ----------- | ----------------------- |
| SPEC-{{NNN}}-001 | operational | EPIC, STORY-{{NNN}}-001 |
| SPEC-{{NNN}}-002 | context     | DOCUMENT                |
