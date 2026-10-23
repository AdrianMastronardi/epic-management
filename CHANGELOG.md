# Changelog

All notable changes to this project are documented in this file.

The format is loosely adapted from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries are grouped by area, in this fixed order. Sections with no entries for a given version are omitted.

- **Skill** covers the agent-facing workflow and invocation interface: `SKILL.md`, `agents/openai.yaml`, and `references/`.
- **Templates** covers files under `assets/` that the skill turns into repository artifacts.
- **Validation** covers deterministic checks under `scripts/`.
- **Documentation** covers human-facing project documentation, including this changelog.
- **Infrastructure** covers formatting rules, editor configuration, and repository plumbing.

Within each section, entries are sorted in case-insensitive alphabetical order by filename.

## [Unreleased]

## [0.5.0] - 2026-10-23

### Skill

- `references/github-publication.md`, `references/github-sub-issues.md`: require complete dependency-graph review before affected publication or resume writes, including documented gates, known cross-EPIC paths, and legacy-plan uncertainty.
- `references/implementation-handoff.md`: checks that a story can close its entire scope and that prerequisite gates agree with the dependency table.
- `references/okf-bundle.md`: documents all-phase dependency validation in both entry points and the semantic-review requirement for prose-only plans.
- `references/story-decomposition.md`: replaces the partial-delivery cycle exception with an acyclic story graph and closable scopes, preserving source coverage, real integration checks, and published identities during scope repair.
- `SKILL.md`: requires complete-graph acyclicity at coverage and publication checkpoints and an approved repair before resuming affected cyclic work.

### Templates

- `assets/epic-concept-template.md`, `assets/story-concept-template.md`: prompt for an acyclic complete graph, explicit prerequisites, and independently closable story scopes.

### Validation

- `scripts/validate_epic.py`: **Breaking:** rejects previously accepted cyclic tables across all internal dependency phases and projections, including completed or cancelled EPICs, with deterministic paths and row, phase, and projection context. Rejects formatted story cells that could hide internal edges.
- `scripts/validate_okf_bundle.py`: shares dependency-table and SPEC-routing checks for each published EPIC without changing unrelated OKF consumer tolerances; missing distribution sections produce diagnostics rather than tracebacks. A historical cycle now blocks validation of the whole bundle.
- `tests/story-decomposition-cases.md`, `tests/story-decomposition-rubric.md`: reverse the schema/client cycle expectation and cover hidden gates, longer cycles, partial publication, cross-EPIC uncertainty, legacy prose, source conflicts, and informational links.
- `tests/story-decomposition-evaluation.md`: records independent isolated planning runs against release 0.4.0 and the candidate across 18 cases, with manual rubric assessment and explicit evaluation limits.
- `tests/test_validators.py`: covers cyclic and acyclic graphs, metadata and routing checks, both layouts and parsers, and CLI failures through both validator entry points.

### Documentation

- `CONTRIBUTING.md`, `README.md`: state the complete-graph invariant and explain the limits of structural dependency validation.

## [0.4.0] - 2026-10-18

### Skill

- `references/github-publication.md`: creates the EPIC index without frontmatter in the embedded layout and links the collection from the enclosing index when that index lists its subdirectories.
- `references/okf-bundle.md`: defines the standalone and embedded layouts of the EPIC collection, keeps `tmp/` outside every bundle, describes the embedded EPIC index and its migration, and states what each validator checks in either layout.
- `SKILL.md`: finds the bundle root at or above `docs/epics/`, recognizes an EPIC collection embedded in a larger bundle without mistaking it for the legacy layout, and drops the index template's frontmatter when publishing into it.

### Validation

- `scripts/okf.py`: infers the published stage for an EPIC directory inside a bundle whose root is its collection or any ancestor, keeps the working stage under `tmp/` even when the repository root is the bundle root, and skips `tmp/` when walking a bundle.
- `scripts/validate_okf_bundle.py`: takes the EPIC collection in both layouts, validates the whole enclosing bundle except `tmp/`, applies the listing and file checks to the collection, and rejects EPIC directories outside the collection and `okf_version` declared below the bundle root.
- `tests/test_validators.py`: covers stage inference and validation in the embedded layout, unlisted EPICs and missing files or indexes, a nested `okf_version`, EPIC directories outside the collection, and a working EPIC under a repository-root bundle.

### Documentation

- `README.md`: describes both layouts and how to validate them.

## [0.3.2] - 2026-10-18

### Skill

- `references/okf-bundle.md`: documents `stale_after` and `sources[].last_modified` as ISO 8601 datetimes with an explicit UTC offset, as the current OKF v0.2 text requires, keeps `started_on` and `completed_on` as calendar days, and converts date-only values from the earlier text to midnight UTC whenever the workflow edits an EPIC.
- `SKILL.md`: writes every OKF timestamp as an ISO 8601 datetime with an explicit UTC offset.

### Templates

- `assets/epic-concept-template.md`: prompts for `sources[].last_modified` as an ISO 8601 UTC datetime.

### Validation

- `scripts/okf.py`: validates `stale_after` and `sources[].last_modified` as ISO 8601 datetimes with an explicit UTC offset, rejects date-only values in the EPIC validator, and names the expected form when a datetime lacks its offset.
- `scripts/validate_okf_bundle.py`: reports date-only `stale_after` and `sources[].last_modified` values written against the earlier OKF v0.2 text as warnings, which `--strict` turns into failures.
- `tests/test_validators.py`: covers UTC-offset datetimes, values without an offset, impossible dates and times, and date-only values for both keys in both validators, and asserts that the EPIC template prompts for a datetime `last_modified`.

### Documentation

- `README.md`: lists date-only timestamps among the tolerances the bundle validator reports as warnings.

## [0.3.1] - 2026-10-18

### Skill

- `references/okf-bundle.md`: states that the optional `stale_after` is omitted unless the source or the user states the re-check date.
- `SKILL.md`: omits `stale_after` during preparation unless a real re-check date is supplied, and forbids inventing one.

### Templates

- `assets/epic-concept-template.md`: drops the `stale_after` placeholder so new EPICs no longer carry a re-check date by default.

### Validation

- `scripts/okf.py`: treats an empty `stale_after` as absent instead of demanding a date.
- `tests/test_validators.py`: covers absent, empty, valid, and invalid `stale_after` values in both validators, and asserts that the EPIC template omits the field.

## [0.3.0] - 2026-10-05

### Skill

- `references/github-publication.md`: preserves dependency phases and integration responsibilities, previews native and documented projections separately, keeps each documented gate as its own checkbox, classifies satisfied and unclassified dependencies, and checks delivery evidence on resume to avoid restoring satisfied blockers or treating closed producers without delivery as usable blockers.
- `references/github-sub-issues.md`: recognizes dependencies proposed during refinement and approved at the coverage checkpoint while preserving the distinction between priority and blocking, and defines the native dependency-edge transport with GitHub CLI and REST commands, bidirectional readback, and the failure rule when no transport exists.
- `references/implementation-handoff.md`: reviews prerequisites for starting, integrating, and completing alongside compatibility with concurrent stories.
- `references/okf-bundle.md`: locates durable dependency design in existing sections and specification blocks without adding live state or changing the artifact schema, and states that the dependency table is validated only when present.
- `references/story-decomposition.md`: adds useful split criteria, output-based dependencies, interference review, deliverable-level cycle analysis, explicit native dependency projection rules, and integrated verification; defines delivery evidence, gates as issue checkboxes, acyclic native projection, identifier stability after a split, the transition from proposed to approved dependencies, and the handling of dependencies published without a projection. Merged pull request evidence must establish delivery on the consumer's base branch and passing release-condition checks, including that the output remains available.
- `SKILL.md`: applies decomposition review during preparation and refinement, itemizes parallel work, bottlenecks, and dependency rationale in the coverage checkpoint, and requires delivery evidence before adding native edges on resume.

### Templates

- `assets/epic-concept-template.md`: replaces the dependency prompt with a table of producer, consumer, output, phase, release condition, projection, and specification block, and prompts for event sequences and decomposition rationale.
- `assets/story-concept-template.md`: adds separate checkbox prompts for start, integration, and completion gates and for contract or integration checks.

### Validation

- `scripts/validate_epic.py`: checks the dependency table when the `Dependencies` section contains it, rejecting undeclared stories, unknown phases or projections, native projections outside start-phase story dependencies, blocks not routed to the consumer, and cycles among native edges; preserves escaped pipes in table cells and validates complete SPEC reference tokens instead of accepting valid prefixes of unknown identifiers. Prose-only sections stay valid.
- `tests/test_validators.py`: covers a valid dependency table with each projection plus regressions for native projection limits, inconsistent references, native cycles, escaped pipes, backslashes before column separators, and malformed SPEC references both alone and alongside valid references.

### Documentation

- `CONTRIBUTING.md`: requires behavioral evaluation of decomposition and dependency-policy changes with an isolated evaluator and a previous-release baseline, distinguishing independent evaluation from manual review.
- `README.md`: explains decomposition for parallel work, links the new review guidance, and describes the dependency-table checks.
- `tests/story-decomposition-cases.md`, `tests/story-decomposition-rubric.md`: separate ten synthetic planning inputs from their behavioral acceptance criteria, covering parallel work, phase gates, apparent and real cycles, cohesive scope, shared-resource interference, external prerequisites, mixed projections, and resumption after delivery or from an older publication, including deliveries on another branch, failed required checks, and reverted deliveries.

## [0.2.3] - 2026-09-24

### Skill

- `references/github-publication.md`: requires issue previews to retain implementation decisions, rationale, and verification details and pass an independent-agent review.
- `references/implementation-handoff.md`: defines how to capture implementation intent from discussion and repository evidence, distinguish decision status, route shared design, and assess readiness without the original conversation.
- `SKILL.md`: requires preparation and refinement to preserve the intended implementation and review each story for independent execution before publication.

### Templates

- `assets/epic-concept-template.md`: prompts for implementation approach, starting points, contracts, rationale, verification, and unresolved decisions within specification blocks.
- `assets/story-concept-template.md`: prompts for ordered implementation steps, scope boundaries, concrete acceptance scenarios, and specific verification checks.

## [0.2.2] - 2026-09-05

Adopts signed, annotated Git tags as the immutable release points behind the changelog. Every released version now has a `vX.Y.Z` tag, version headings link to GitHub comparisons, and ongoing work returns to an empty Unreleased section after each release.

### Documentation

- `CHANGELOG.md`: adds the Unreleased section and tag-backed reference links for every version.
- `CONTRIBUTING.md`: defines the release-cut sequence, including changelog rollover, validation, the release commit, signed tag creation, and publication of the branch and tag together.
- `README.md`: identifies signed release tags and changelog comparisons as the project's version-history interface.

### Infrastructure

- Git tags: marks releases `v0.1.0` through `v0.2.2` with signed, annotated tags that point to their release commits.

## [0.2.1] - 2026-09-05

Makes GitHub's native parent/sub-issue relationship part of the publication contract. Every story issue is now a direct ordered sub-issue of its EPIC; Markdown task lists, issue links, labels, milestones, and dependency edges no longer qualify as substitutes for that relationship.

### Skill

- `references/github-publication.md`: separates native parentage from blocking dependencies, includes current-parent and native-priority state in previews, creates new stories with their parent when possible, and requires bidirectional relationship readback before publication or closure completes.
- `references/github-sub-issues.md`: defines the native relationship model, GitHub CLI, REST, and GraphQL transports, capability and permission preflight, idempotent attachment, transport-specific ID handling, conflict-safe reparenting, priority reconciliation, closure proof, and partial-failure recovery.
- `SKILL.md`: requires every story to be a direct native sub-issue of the EPIC, rejects checklist degradation and implicit reparenting, and adds exact sub-issue set and ordering to completion conditions.

### Documentation

- `CHANGELOG.md`: documents the native Sub-issues release.
- `CONTRIBUTING.md`: adds parentage, priority, dependency separation, conflict handling, and read-only relationship verification to the project invariants.
- `README.md`: explains the native issue hierarchy and routes users to the detailed GitHub Sub-issues protocol.

## [0.2.0] - 2026-08-20

Adopts [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) as the storage format for EPIC knowledge. Published EPICs now live in a conformant knowledge bundle rooted at `docs/epics/`, where one EPIC is one concept directory holding an `epic.md` concept, one `Story` concept per story, and an index. Frontmatter records provenance with `sources`, authorship with `generated`, review with `verified`, document lifecycle with `status`, and execution lifecycle with `epic_status`, so the checkpoint approval this skill already required becomes a recorded human verification event rather than an untracked one.

This release changes artifact paths and adds the `migrate` operation, which converts a legacy `docs/epic-index.md` and flat `docs/epics/EPIC-NNN-name.md` layout into the bundle after an exact-write preview and without touching GitHub. Story concepts link their specification blocks instead of duplicating them, while generated GitHub issue bodies still embed the complete applicable text.

### Skill

- `agents/openai.yaml`: advertises the new `migrate` operation.
- `references/github-publication.md`: publishes into the bundle, assigns the frontmatter that publication owns, updates the bundle index, resolves story block links into complete issue text, and requires both validators before commit.
- `references/okf-bundle.md`: defines the OKF format contract for EPIC artifacts, including bundle layout, concept types, frontmatter families, the actor convention, trust events, source and link policy, the restricted YAML style, index structure, history through git rather than a log file, conformance, and the legacy migration map.
- `SKILL.md`: replaces the single-document artifact model with the OKF concept directory, adds the `migrate` operation and mode, records `generated` and `verified` at the moments they actually occur, separates `status` from `epic_status`, moves per-EPIC metadata out of the index and into the concept, leaves history to git instead of a bundle log, and requires bundle validation before publication completes.

### Templates

- `assets/backlog-concept-template.md`: replaces `assets/epic-backlog-template.md` with an `EPIC Backlog` concept carrying OKF frontmatter.
- `assets/bundle-index-template.md`: provides the bundle-root index, declaring `okf_version` and grouping published EPICs by execution status without linking optional concepts that have not been created.
- `assets/epic-backlog-template.md`: removed in favor of `assets/backlog-concept-template.md`.
- `assets/epic-concept-template.md`: replaces `assets/epic-template.md` with a working `type: EPIC` concept whose title, provenance, lifecycle, and story index live in frontmatter and whose body holds the specification blocks and distribution table; publication-owned resource and human-verification fields remain absent until publication.
- `assets/epic-index-template.md`: becomes the per-EPIC directory index listing the EPIC concept and its story concepts.
- `assets/epic-template.md`: removed in favor of `assets/epic-concept-template.md`.
- `assets/story-concept-template.md`: provides a working `type: Story` concept with `applicable_blocks` frontmatter and an applicable specification section that links its blocks in the EPIC concept, leaving publication-owned resource and human-verification fields absent until publication.

### Validation

- `scripts/okf.py`: adds shared OKF frontmatter parsing and checks, using PyYAML when importable and a strict parser for the documented subset otherwise, keeping both parsers aligned on quoted leading-zero identifiers, and providing reusable actor, calendar date, trust, lifecycle, source, footnote, and hygiene validation.
- `scripts/validate_epic.py`: validates an EPIC concept directory rather than a single file, checking frontmatter families, lifecycle values against the working or published stage, bounded story concept paths, story metadata and resources against the EPIC index, exact specification-link agreement, story numbering and file presence, the directory index, footnote attribution, link targets, and completion requirements.
- `scripts/validate_okf_bundle.py`: adds OKF v0.2 conformance validation for the whole bundle, accepting normalized relative root links, separating hard failures from the tolerances OKF grants consumers, checking any independently maintained `log.md` it finds without requiring one, and offering `--strict`.
- `tests/test_validators.py`: covers valid working and published bundles with PyYAML and the fallback parser plus regressions for concept containment, metadata projection, parser parity, real dates, optional index links, and normalized root links.

### Documentation

- `CHANGELOG.md`: documents the OKF adoption release.
- `CONTRIBUTING.md`: restates the project invariants around the bundle, conformance, evidence-based provenance, the two lifecycle axes, and lossless migration, and requires exercising both validators with and without PyYAML.
- `README.md`: documents the bundle model, the `migrate` operation, the recorded provenance and trust guarantees, git as the bundle's history, both validation commands, and the new package structure.

### Infrastructure

- `.gitignore`: keeps the bytecode cache produced by the shared validator module out of version control.

## [0.1.1] - 2026-08-16

### Skill

- `references/github-publication.md`: requires a new publication to start from the approved working EPIC under `tmp/`, defines native GitHub relationships, and records the separated index and backlog requirements for active and completed EPICs.
- `SKILL.md`: defines the lifecycle boundary, separates published index and future backlog state, requires direct document and story links, controls lifecycle statuses, and bounds completed-EPIC summaries.

### Templates

- `assets/epic-backlog-template.md`: provides an optional separate home for future EPICs without published documents or GitHub issues.
- `assets/epic-index-template.md`: provides a generic published EPIC index with relative document links, controlled status, structured story links, exceptional notes, and bounded completion summaries.

### Validation

- `scripts/validate_epic.py`: makes draft-labelling diagnostics apply accurately to both working and versioned EPIC documents.

### Documentation

- `CONTRIBUTING.md`: adds the temporary-to-versioned publication boundary, index/backlog separation, and complete index-entry requirements to the project invariants.
- `README.md`: documents the artifact lifecycle, index/backlog separation, native GitHub relationships, and active and completed index states.

## [0.1.0] - 2026-08-15

Initial release of Epic Management, a cross-host skill for Codex and Claude Code that transforms a functional and technical specification into one self-contained, versioned EPIC document and a traceable set of GitHub issues without losing source information.

The EPIC document divides the complete specification into stable `SPEC-NNN-SSS` blocks, classifies each block as `context` or `operational`, and maps every operational block to the EPIC issue, one or more story issues, or both. Generated issue bodies include the complete applicable text rather than only summaries, identifiers, or links, so no implementation depends on an ignored temporary file.

The skill provides `help`, `prepare`, `refine`, `publish`, `prepare-and-publish`, `resume`, and `inspect`. Empty invocations show English help without reading the repository or changing state. Publication requires an exact preview and explicit approval, reuses resources by deterministic identity, resumes partial runs without duplication, and leaves documentation pull requests open for human review.

### Skill

- `agents/openai.yaml`: defines Codex discovery metadata, an operation-focused description, and a default prompt that opens the help interface.
- `references/github-publication.md`: defines the approval-gated publication protocol, including repository preconditions, lossless issue-body generation, all-state duplicate detection, exact-write previews, resource-by-resource readback, repository archival, pull-request creation, and post-merge cleanup.
- `SKILL.md`: defines the dual-host invocation contract, explicit operation dispatch, portable resource resolution, single-document invariant, lossless source consumption, block classification and routing, coverage checkpoint, idempotent publication and resumption, formatting requirements, and completion conditions. It prevents remote mutations before approval, temporary-path dependencies, draft-labelled EPIC artifacts, and story implementation during backlog management.

### Templates

- `assets/epic-template.md`: provides the canonical English EPIC structure with functional and technical specification blocks, affected components, dependencies, execution order, global acceptance criteria, a GitHub distribution table, and executable story sections with exact `Applicable blocks` declarations.

### Validation

- `scripts/validate_epic.py`: validates the EPIC title and number, required section order, consecutive and unique specification and story identifiers, distribution-table coverage, contextual and operational routing, story-to-table agreement, required story subsections, unresolved placeholders, forbidden `tmp/` references, and accidental draft labelling.

### Documentation

- `CHANGELOG.md`: documents the complete initial release using fixed, consistently ordered release areas.
- `CONTRIBUTING.md`: defines contribution scope, project invariants, English-language and Markdown requirements, validation and compatibility checks, changelog expectations, and licensing terms.
- `LICENSE`: licenses the project under the MIT License with copyright held by Adrian Mastronardi.
- `README.md`: documents the problem, guarantees, operations, dual-host installation and usage, end-to-end workflow, EPIC document model, validation commands, package structure, license, and contribution entry point.

### Infrastructure

- `.gitattributes`: normalizes supported text formats to LF line endings.
- `.markdownlint-cli2.jsonc`: configures structural Markdown rules while preserving logical prose lines and manually maintained table diffs.
- `.vscode/extensions.json`: recommends the Markdownlint and Prettier editor integrations.
- `.vscode/settings.json`: enables Markdown formatting and lint fixes on save, preserves logical prose lines, normalizes final newlines, and trims trailing whitespace.

[Unreleased]: https://github.com/AdrianMastronardi/epic-management/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/AdrianMastronardi/epic-management/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/AdrianMastronardi/epic-management/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/AdrianMastronardi/epic-management/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/AdrianMastronardi/epic-management/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/AdrianMastronardi/epic-management/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/AdrianMastronardi/epic-management/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/AdrianMastronardi/epic-management/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/AdrianMastronardi/epic-management/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/AdrianMastronardi/epic-management/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/AdrianMastronardi/epic-management/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/AdrianMastronardi/epic-management/releases/tag/v0.1.0
